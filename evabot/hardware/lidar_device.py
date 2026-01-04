"""
RPLidar hardware singleton.
Manages physical lidar device shared across all robots.
"""

import atexit
import logging
import threading
import time
from typing import Optional, Dict
from rplidar import RPLidar, RPLidarException


logger = logging.getLogger(__name__)


class LidarDevice:
    """
    Singleton manager for physical RPLidar device.

    Multiple robot instances can share the same physical lidar.
    The lidar continuously scans and provides the latest scan data to all consumers.
    """

    _instance: Optional['LidarDevice'] = None
    _lock = threading.Lock()

    def __init__(self, port: str, baudrate: int):
        """
        Initialize lidar device.

        Args:
            port: Serial port (e.g., '/dev/ttyUSB0')
            baudrate: Baud rate (e.g., 460800 for C1)
        """
        self.port = port
        self.baudrate = baudrate
        self._lidar: Optional[RPLidar] = None
        self._scan_thread: Optional[threading.Thread] = None
        self._running = False
        self._scan_lock = threading.RLock()

        # Latest complete 360° scan data
        # Format: {angle_deg: (distance_m, quality)}
        self._latest_scan: Dict[int, tuple] = {}

        # Connection state
        self._connected = False

        logger.info(f"LidarDevice created for {port} @ {baudrate} baud")

    @classmethod
    def get_default(cls, port='/dev/ttyUSB0', baudrate=460800) -> 'LidarDevice':
        """
        Get or create the default lidar device (singleton).

        Args:
            port: Serial port for lidar
            baudrate: Baud rate (460800 for RPLidar C1)

        Returns:
            Shared LidarDevice instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(port, baudrate)
            return cls._instance

    @classmethod
    def cleanup_all(cls):
        """Cleanup all lidar devices."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance.stop()
                cls._instance = None

    def start(self):
        """Start lidar scanning."""
        if self._running:
            logger.warning("Lidar already running")
            return

        try:
            # Connect to lidar
            logger.info(f"Connecting to lidar at {self.port} @ {self.baudrate} baud")
            self._lidar = RPLidar(self.port, baudrate=self.baudrate, timeout=1)

            # Clear any leftover data in buffer
            logger.debug("Clearing serial buffer...")
            self._lidar._serial.reset_input_buffer()
            self._lidar._serial.reset_output_buffer()
            time.sleep(0.1)

            # Send stop command first to reset lidar state
            logger.debug("Resetting lidar state...")
            self._lidar._serial.write(b'\xA5\x25')  # Stop scan
            time.sleep(0.2)
            self._lidar._serial.reset_input_buffer()  # Clear response

            # Get device info
            info = self._lidar.get_info()
            logger.info(f"Lidar info: model={info['model']}, "
                       f"firmware={info['firmware']}, hardware={info['hardware']}")

            # Check health
            health, error_code = self._lidar.get_health()
            logger.info(f"Lidar health: {health} (error_code={error_code})")

            if health == 'Error':
                raise RPLidarException(f"Lidar in error state: {error_code}")

            self._connected = True

            # Start scanning thread
            self._running = True
            self._scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
            self._scan_thread.start()

            logger.info("Lidar scanning started")

        except Exception as e:
            logger.error(f"Failed to start lidar: {e}")
            self.stop()
            raise

    def stop(self):
        """Stop lidar scanning."""
        logger.info("Stopping lidar...")
        self._running = False

        if self._scan_thread is not None:
            self._scan_thread.join(timeout=2)
            self._scan_thread = None

        if self._lidar is not None:
            try:
                # Stop scan command already sent by scan loop
                self._lidar.disconnect()
            except Exception as e:
                logger.warning(f"Error stopping lidar: {e}")
            finally:
                self._lidar = None
                self._connected = False

        logger.info("Lidar stopped")

    def _scan_loop(self):
        """Background thread that continuously reads scans using raw serial."""
        logger.info("Scan loop started")

        try:
            # Get direct serial port access
            ser = self._lidar._serial

            # Send start scan command (0xA5 0x20 for normal scan)
            logger.info("Sending start scan command...")
            ser.write(b'\xA5\x20')
            time.sleep(0.1)

            # Read and verify descriptor
            desc = ser.read(7)
            if len(desc) == 7 and desc[0] == 0xA5 and desc[1] == 0x5A:
                logger.info("Scan started successfully")
            else:
                raise RPLidarException("Failed to start scan - invalid descriptor")

            # Continuously read scan points
            scan_data = {}
            last_angle = None

            while self._running:
                # Read one scan point (5 bytes)
                data = ser.read(5)
                if len(data) != 5:
                    continue

                # Parse scan point
                # Byte 0: S[1] | S[0] | Quality[6]
                # Byte 1: C[1] | Angle[7]
                # Byte 2: Angle[8]
                # Byte 3: Distance[8]
                # Byte 4: Distance[8]

                new_scan = data[0] & 0x01
                quality = (data[0] >> 2)
                check_bit = data[1] & 0x01

                if check_bit != 1:
                    continue  # Invalid data

                angle = ((data[1] >> 1) | (data[2] << 7)) / 64.0
                distance = (data[3] | (data[4] << 8)) / 4.0  # mm

                # Check for new scan (360° wrap)
                if new_scan and last_angle is not None:
                    # We completed a full 360° rotation
                    # Update the shared scan data
                    with self._scan_lock:
                        self._latest_scan = scan_data.copy()
                    scan_data = {}  # Start new scan

                last_angle = angle

                # Add point to current scan
                if distance > 0 and quality > 0:
                    angle_deg = int(round(angle)) % 360
                    distance_m = distance / 1000.0
                    scan_data[angle_deg] = (distance_m, quality)

        except Exception as e:
            if self._running:
                logger.error(f"Scan loop error: {e}")
            else:
                logger.debug("Scan loop stopped (expected)")
        finally:
            # Send stop scan command
            try:
                self._lidar._serial.write(b'\xA5\x25')
            except Exception:
                pass
            logger.info("Scan loop ended")

    def get_latest_scan(self) -> Dict[int, tuple]:
        """
        Get the latest complete 360° scan.

        Returns:
            Dictionary mapping angle (0-359 degrees) to (distance_m, quality)
        """
        with self._scan_lock:
            return self._latest_scan.copy()

    def get_distance_at_angle(self, angle_deg: float) -> Optional[float]:
        """
        Get distance reading at specific angle.

        Args:
            angle_deg: Angle in degrees (0-360)

        Returns:
            Distance in meters, or None if no reading at that angle
        """
        angle_int = int(round(angle_deg)) % 360
        with self._scan_lock:
            if angle_int in self._latest_scan:
                return self._latest_scan[angle_int][0]
            return None

    @property
    def is_connected(self) -> bool:
        """Check if lidar is connected."""
        return self._connected

    @property
    def is_running(self) -> bool:
        """Check if lidar is scanning."""
        return self._running


# Register cleanup on program exit
atexit.register(LidarDevice.cleanup_all)
