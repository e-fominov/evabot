"""
RPLidar C1 sensor component.
Provides easy access to lidar scan data for robots.
"""

import logging
from typing import Optional, Dict
from evabot.components.base import Component
from evabot.hardware import LidarDevice


logger = logging.getLogger(__name__)


class RPLidarC1(Component):
    """
    RPLidar C1 laser scanner component.

    Provides easy access to 360° lidar scan data:
    - Front/back/left/right distance readings
    - Full 360° scan data
    - Works standalone or attached to Robot

    Example (standalone):
        >>> lidar = RPLidarC1()
        >>> lidar.start()
        >>> print(f"Front: {lidar.front}m")
        >>> lidar.stop()

    Example (with robot):
        >>> robot = Robot()
        >>> robot.lidar = RPLidarC1()
        >>> robot.start()
        >>> print(f"Front: {robot.lidar.front}m")
    """

    def __init__(self, device: Optional[LidarDevice] = None,
                 port='/dev/ttyUSB0', baudrate=460800):
        """
        Initialize RPLidar C1 component.

        Args:
            device: Optional LidarDevice instance (uses singleton if None)
            port: Serial port for lidar (default /dev/ttyUSB0)
            baudrate: Baud rate (default 460800 for C1)
        """
        super().__init__()

        # Get or use lidar device (singleton)
        if device is None:
            self._device = LidarDevice.get_default(port=port, baudrate=baudrate)
        else:
            self._device = device

        logger.info("RPLidarC1 component created")

    def start(self):
        """Start lidar scanning."""
        logger.info("Starting RPLidarC1...")
        self._device.start()
        self._running = True
        logger.info("RPLidarC1 started")

    def stop(self):
        """Stop lidar scanning."""
        logger.info("Stopping RPLidarC1...")
        self._running = False
        # Note: Don't stop the device - other components might be using it
        # The device will be stopped by cleanup_all() on exit
        logger.info("RPLidarC1 stopped")

    @property
    def scan(self) -> Dict[int, float]:
        """
        Get full 360° scan.

        Returns:
            Dictionary mapping angle (0-359 degrees) to distance (meters)
            Example: {0: 1.5, 1: 1.52, 2: 1.48, ...}
        """
        scan_data = self._device.get_latest_scan()
        # Convert from {angle: (distance, quality)} to {angle: distance}
        return {angle: dist for angle, (dist, _) in scan_data.items()}

    @property
    def front(self) -> Optional[float]:
        """
        Get distance in front of robot (0°, X axis).

        Returns:
            Distance in meters, or None if no reading

        Note:
            Takes average of readings around 0° (±5°) for robustness
            Coordinate system: CW rotation when viewed top-down
        """
        return self._get_averaged_distance(0, spread=5)

    @property
    def back(self) -> Optional[float]:
        """
        Get distance behind robot (180°).

        Returns:
            Distance in meters, or None if no reading
        """
        return self._get_averaged_distance(180, spread=5)

    @property
    def right(self) -> Optional[float]:
        """
        Get distance to the right of robot (90°).

        Returns:
            Distance in meters, or None if no reading

        Note:
            Using CW rotation: 0°=front, 90°=right, 180°=back, 270°=left
        """
        return self._get_averaged_distance(90, spread=5)

    @property
    def left(self) -> Optional[float]:
        """
        Get distance to the left of robot (270°).

        Returns:
            Distance in meters, or None if no reading

        Note:
            Using CW rotation: 0°=front, 90°=right, 180°=back, 270°=left
        """
        return self._get_averaged_distance(270, spread=5)

    def get_distance_at(self, angle_deg: float) -> Optional[float]:
        """
        Get distance at specific angle.

        Args:
            angle_deg: Angle in degrees (0° = front, 90° = left,
                                        180° = back, 270° = right)

        Returns:
            Distance in meters, or None if no reading
        """
        return self._device.get_distance_at_angle(angle_deg)

    def get_min_distance_in_range(self, start_angle: float, end_angle: float) -> Optional[float]:
        """
        Get minimum distance in an angular range.

        Args:
            start_angle: Start angle in degrees
            end_angle: End angle in degrees

        Returns:
            Minimum distance in meters, or None if no readings in range

        Example:
            >>> # Check for obstacles in front-left quadrant
            >>> min_dist = lidar.get_min_distance_in_range(315, 45)
        """
        scan = self.scan
        if not scan:
            return None

        # Normalize angles
        start = int(round(start_angle)) % 360
        end = int(round(end_angle)) % 360

        # Collect distances in range
        distances = []

        if start <= end:
            # Normal range (e.g., 45° to 135°)
            for angle in range(start, end + 1):
                if angle in scan:
                    distances.append(scan[angle])
        else:
            # Wrap-around range (e.g., 315° to 45°)
            for angle in range(start, 360):
                if angle in scan:
                    distances.append(scan[angle])
            for angle in range(0, end + 1):
                if angle in scan:
                    distances.append(scan[angle])

        return min(distances) if distances else None

    def _get_averaged_distance(self, center_angle: float, spread: int = 5) -> Optional[float]:
        """
        Get averaged distance around a center angle for robustness.

        Args:
            center_angle: Center angle in degrees
            spread: Number of degrees to average on each side

        Returns:
            Average distance in meters, or None if no readings
        """
        scan = self.scan
        if not scan:
            return None

        # Collect distances within range
        distances = []
        center = int(round(center_angle))

        for offset in range(-spread, spread + 1):
            angle = (center + offset) % 360
            if angle in scan:
                distances.append(scan[angle])

        return sum(distances) / len(distances) if distances else None

    @property
    def is_connected(self) -> bool:
        """Check if lidar is connected."""
        return self._device.is_connected

    @property
    def scan_quality(self) -> Dict[int, int]:
        """
        Get full scan with quality values.

        Returns:
            Dictionary mapping angle to quality (0-15, higher is better)
        """
        scan_data = self._device.get_latest_scan()
        return {angle: quality for angle, (_, quality) in scan_data.items()}
