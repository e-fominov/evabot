#!/usr/bin/env python3
"""
CAN Bus hardware singleton.

Manages shared CAN bus access across multiple components/robots.
Prevents multiple components from opening the same CAN interface.

Features:
- Background thread for command resending (handles motor timeout + bus errors)
- Emergency stop on program exit
"""

import atexit
import subprocess
import threading
import time
from typing import Dict, Tuple, Optional, List
import can


class CanBus:
    """
    Singleton CAN bus manager.

    Ensures only one connection per (channel, bitrate) pair exists.
    Multiple components/robots share the same physical bus.

    Usage:
        # Get default CAN bus (can0 @ 500kbps)
        bus = CanBus.get_default()

        # Get specific bus
        bus = CanBus.get_default(channel='can1', bitrate=1000000)

        # All components share the same instance
        bus1 = CanBus.get_default('can0')
        bus2 = CanBus.get_default('can0')
        assert bus1 is bus2  # Same instance!
    """

    # Class-level storage for singleton instances
    _instances: Dict[Tuple[str, int], 'CanBus'] = {}
    _lock = threading.Lock()

    # Track active devices for cleanup
    _all_devices: list = []  # List of all Servo42D instances

    def __init__(self, channel: str, bitrate: int):
        """
        Initialize CAN bus with background thread.

        Args:
            channel: CAN interface (e.g., 'can0')
            bitrate: Bus bitrate in bps
        """
        self.channel = channel
        self.bitrate = bitrate

        # Open CAN bus
        try:
            self.bus = can.Bus(
                channel=channel,
                interface='socketcan',
                bitrate=bitrate
            )
            print(f"CanBus: Opened {channel} @ {bitrate}bps")
        except Exception as e:
            raise RuntimeError(
                f"Failed to open CAN bus {channel} @ {bitrate}bps: {e}"
            ) from e

        # Active commands to resend: {can_id: (data, last_sent_time, resend_rate)}
        self._active_commands: Dict[int, Tuple[List[int], float, float]] = {}
        self._active_lock = threading.Lock()

        # Background thread
        self._running = False
        self._thread = None
        self._start_thread()

    def _start_thread(self):
        """Start background thread for command resending"""
        self._running = True
        self._thread = threading.Thread(
            target=self._can_loop,
            daemon=True,
            name=f"can_{self.channel}"
        )
        self._thread.start()

    def _can_loop(self):
        """
        Background thread - resends active commands.

        Jobs:
        1. Resend motor commands every 200ms (keeps motors running with 500ms timeout)
        2. Handles bus errors (command loss)
        """
        while self._running:
            current_time = time.time()

            with self._active_lock:
                for can_id, (data, last_sent, resend_rate) in list(self._active_commands.items()):
                    # Time to resend?
                    if current_time - last_sent >= resend_rate:
                        try:
                            msg = can.Message(
                                arbitration_id=can_id,
                                data=data,
                                is_extended_id=False
                            )
                            self.bus.send(msg)

                            # Update last sent time
                            self._active_commands[can_id] = (data, current_time, resend_rate)

                        except Exception as e:
                            print(f"CanBus: Error resending to ID {can_id}: {e}")

            # Sleep to prevent CPU spin
            time.sleep(0.05)  # 20Hz check rate

    def set_active_command(self, can_id: int, data: List[int], resend_rate: float = 0.2):
        """
        Set active command for periodic resending.

        Args:
            can_id: CAN device ID
            data: Command bytes (including CRC)
            resend_rate: Resend interval in seconds (default 200ms)

        Usage:
            # Motor sets speed - will be resent every 200ms
            can_bus.set_active_command(can_id=1, data=[0xF6, ...])
        """
        with self._active_lock:
            self._active_commands[can_id] = (data, 0.0, resend_rate)

    def clear_active_command(self, can_id: int):
        """
        Clear active command (stop resending).

        Args:
            can_id: CAN device ID
        """
        with self._active_lock:
            if can_id in self._active_commands:
                del self._active_commands[can_id]

    def send(self, msg: can.Message):
        """Send CAN message directly (for immediate commands)"""
        self.bus.send(msg)

    def recv(self, timeout: float = None):
        """Receive CAN message"""
        return self.bus.recv(timeout=timeout)

    @classmethod
    def get_default(cls, channel: str = 'can0', bitrate: int = 500000) -> 'CanBus':
        """
        Get or create CAN bus instance (singleton).

        Args:
            channel: CAN interface name (e.g., 'can0', 'can1')
            bitrate: Bus bitrate in bits/second (default 500kbps)

        Returns:
            Shared CanBus instance for this (channel, bitrate) pair

        Note:
            The first call creates the bus + background thread.
            Subsequent calls return the same instance.
            Automatic cleanup on program exit.
        """
        key = (channel, bitrate)

        with cls._lock:
            if key not in cls._instances:
                cls._instances[key] = CanBus(channel, bitrate)

            return cls._instances[key]

    @classmethod
    def register_device(cls, device):
        """
        Register device for emergency cleanup.

        Called by devices (motors) when they start.
        """
        with cls._lock:
            if device not in cls._all_devices:
                cls._all_devices.append(device)

    @classmethod
    def unregister_device(cls, device):
        """
        Unregister device from emergency cleanup.

        Called by devices (motors) when they stop.
        """
        with cls._lock:
            if device in cls._all_devices:
                cls._all_devices.remove(device)

    @classmethod
    def cleanup_all(cls):
        """
        Cleanup all open CAN buses and stop all motors.

        Called automatically on program exit via atexit.
        Sends emergency stop to all motors before closing buses.
        """
        with cls._lock:
            # Emergency stop all motors
            print("CanBus: Emergency stopping all motors...")
            for device in cls._all_devices:
                try:
                    # Send emergency stop command
                    device.emergency_stop()
                except Exception as e:
                    print(f"CanBus: Error stopping {device.name}: {e}")

            # CRITICAL: Wait for disable commands to be sent
            # Each motor needs time to receive disable command
            if cls._all_devices:
                time.sleep(0.2)
                print(f"CanBus: Disabled {len(cls._all_devices)} motors")

            # Stop and close CAN buses
            for (channel, bitrate), can_bus_instance in cls._instances.items():
                try:
                    # Stop background thread
                    can_bus_instance._running = False
                    if can_bus_instance._thread:
                        can_bus_instance._thread.join(timeout=1.0)

                    # Close bus
                    can_bus_instance.bus.shutdown()
                    print(f"CanBus: Closed {channel} @ {bitrate}bps")
                except Exception as e:
                    print(f"CanBus: Error closing {channel}: {e}")

            cls._all_devices.clear()
            cls._instances.clear()

    @classmethod
    def reset_for_testing(cls):
        """
        Reset singleton state (for testing only).

        WARNING: Only use in tests! Closes all buses without cleanup.
        """
        with cls._lock:
            cls._instances.clear()


# Register cleanup on program exit
atexit.register(CanBus.cleanup_all)
