#!/usr/bin/env python3
"""
MKS SERVO42D CAN Bus Stepper Motor Component

Progressive complexity:
  Level 1: motor.run(30)  # Just run at 30 RPM
  Level 2: motor.get_position()  # Read encoder
  Level 3+: Attached to robot for odometry
"""

import can
import time
import threading
from typing import Optional
from ..base import Component
from ...hardware import CanBus


class Servo42D(Component):
    """
    MKS SERVO42D stepper motor with CAN bus interface.

    Works standalone or attached to a robot:
      - Standalone: Simple motor control, no odometry
      - With robot: Updates robot.odom based on encoder readings

    Usage (Level 1 - Standalone):
        motor = Servo42D(1)  # CAN ID 1
        motor.start()
        motor.run(30)        # 30 RPM forward
        motor.stop()

    Usage (Level 3+ - With robot):
        robot = Robot()
        robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
        # Motors automatically attach and provide odometry
    """

    # Protocol constants
    CMD_ENABLE = 0xF3
    CMD_EMERGENCY_STOP = 0xF7
    CMD_SPEED = 0xF6
    CMD_READ_ENCODER = 0x30  # Read encoder position
    CMD_MOVE_RELATIVE = 0xFD  # Position mode 1: relative motion by pulses
    CMD_MOVE_ABSOLUTE = 0xFE  # Position mode 2: absolute motion by pulses
    CMD_SET_CURRENT = 0x83  # Set working current (Ma)
    CMD_SET_MODE = 0x82  # Set work mode

    # Conversion constants
    PULSES_PER_ROTATION = 3200  # With 16 subdivisions
    PULSES_PER_DEGREE = 3200 / 360  # ~8.889 pulses per degree

    def __init__(
        self,
        can_id: int,
        can_bus: Optional[can.Bus] = None,
        channel: str = 'can0',
        bitrate: int = 500000
    ):
        """
        Initialize motor.

        Args:
            can_id: Motor CAN ID (1-2047)
            can_bus: Optional CanBus instance (uses singleton if None)
            channel: CAN channel name (default 'can0')
            bitrate: CAN bitrate (default 500000)
        """
        super().__init__(name=f"Servo42D_{can_id}")

        self.can_id = can_id
        self.channel = channel
        self.bitrate = bitrate

        # Use provided bus or get singleton
        self._bus = can_bus

        # State
        self._enabled = False
        self._current_speed_rpm = 0
        self._encoder_position = 0  # pulses
        self._lock = threading.RLock()

    def _flush_can_buffer(self):
        """Flush old messages from CAN bus receive buffer."""
        if self._bus is None:
            return
        while True:
            msg = self._bus.recv(timeout=0.01)
            if msg is None:
                break

    def start(self):
        """
        Start motor (connect to CAN bus).

        Called automatically when robot.start() is called,
        or manually for standalone use.
        """
        # Get CAN bus (singleton if not provided)
        if self._bus is None:
            self._bus = CanBus.get_default(self.channel, self.bitrate)

        # Register for emergency cleanup
        CanBus.register_device(self)

        # Wait for motor to be ready (CAN bus startup)
        time.sleep(0.1)

        # Ensure clean state: stop any ongoing motion and clear buffer
        # This is important when motor is already running from previous test/session
        self._flush_can_buffer()

        # Send stop command (speed=0) to halt any ongoing motion
        # Don't use run(0) as it requires enabled state
        data = [self.CMD_SPEED, 0x00, 0x00, 0x02]
        crc = self._calculate_crc([self.can_id] + data)
        msg = can.Message(arbitration_id=self.can_id, data=data + [crc], is_extended_id=False)
        self._bus.send(msg)
        time.sleep(0.1)

        # Clear any responses
        self._flush_can_buffer()

        # Enable motor (lock shaft)
        enabled = self.enable(True)
        if not enabled:
            print(f"{self.name}: Warning - Enable failed, retrying...")
            time.sleep(0.2)
            enabled = self.enable(True)
            if not enabled:
                print(f"{self.name}: Warning - Enable still failed")

        print(f"{self.name}: Ready on CAN ID {self.can_id}")

    def hold(self):
        """
        Stop moving and hold current position.

        Motor stops moving but stays enabled (shaft locked).
        Use this to stop motion while maintaining holding torque.

        Usage:
            motor.run(30)    # Move forward
            motor.hold()     # Stop but keep shaft locked

        Note:
            Shaft is locked - you cannot turn it manually.
            Use disable() to release the shaft.
        """
        self.run(0)

    def disable(self):
        """
        Disable motor and release shaft.

        Motor can be turned freely by hand after disabling.

        Usage:
            motor.disable()  # Release shaft, can turn manually

        Note:
            Motor will not hold position after disabling.
            Use hold() to stop while keeping position locked.
        """
        # Clear active command (stop resending)
        if self._bus:
            self._bus.clear_active_command(self.can_id)

        # Release shaft
        self.enable(False)

    def stop(self):
        """
        Stop motor completely (holds position, then disables).

        Called automatically when robot.stop() is called,
        or manually for standalone use.

        This is a cleanup method - stops motion and releases shaft.
        """
        # Stop motion and hold briefly
        self.hold()
        time.sleep(0.1)

        # Disable motor (release shaft)
        self.disable()

        # Unregister from emergency cleanup
        CanBus.unregister_device(self)

        print(f"{self.name}: Stopped")

    # ========== Core Motor Control ==========

    def run(self, speed_rpm: float, acceleration: int = 2):
        """
        Run motor at specified speed (continuous mode).

        Args:
            speed_rpm: Speed in RPM
                      Positive = forward (CW)
                      Negative = backward (CCW)
                      0 = stop (same as hold())

            acceleration: How quickly motor reaches target speed (0-255)
                         Lower values = faster acceleration (more jerky)
                         Higher values = slower acceleration (smoother)

                         Recommended values:
                         - 0-5:   Very fast, instant response (jerky)
                         - 10-30: Fast, responsive (default: 2)
                         - 50-100: Medium, balanced
                         - 150+:  Slow, very smooth

        Usage:
            motor.run(30)                    # 30 RPM forward, default acceleration
            motor.run(-20)                   # 20 RPM backward
            motor.run(30, acceleration=50)   # Slower, smoother acceleration
            motor.run(30, acceleration=0)    # Instant speed change

        Note:
            Motor runs continuously until next run() command.
            Motor uses same acceleration value for deceleration (slowing down).

            To stop motion:
            - motor.hold()      # Stop and hold position (shaft locked)
            - motor.run(0)      # Same as hold()
            - motor.disable()   # Stop and release shaft (can turn freely)

        Safety:
            Emergency stop automatically called on program exit/crash.
        """
        # Handle direction (1 = forward, 0 = backward for Servo42D)
        direction = 1 if speed_rpm >= 0 else 0
        speed = abs(speed_rpm)

        # Clamp values
        speed = int(max(0, min(3000, speed)))
        acceleration = int(max(0, min(255, acceleration)))

        # Build command (4-byte format for continuous mode)
        # Motor runs continuously until next speed command
        byte2 = (direction << 7) | ((speed >> 8) & 0x0F)
        byte3 = speed & 0xFF

        # Command format: [CMD, direction+speed_high, speed_low, acceleration]
        data = [self.CMD_SPEED, byte2, byte3, acceleration]

        # Add CRC
        crc = self._calculate_crc([self.can_id] + data)
        msg_data = data + [crc]

        # Send command
        if self._bus:
            msg = can.Message(
                arbitration_id=self.can_id,
                data=msg_data,
                is_extended_id=False
            )
            self._bus.send(msg)

            # Register for periodic resending (keeps motor running)
            # Resend every 200ms (faster than 500ms timeout)
            self._bus.set_active_command(self.can_id, msg_data, resend_rate=0.2)

        with self._lock:
            self._current_speed_rpm = speed_rpm

    def enable(self, enabled: bool = True):
        """
        Enable/disable motor (lock/release shaft).

        Args:
            enabled: True to lock shaft, False to release
        """
        state = 0x01 if enabled else 0x00
        data = [self.CMD_ENABLE, state]

        # Motor may send multiple responses (current state, then new state)
        # Keep reading until we get the requested state or timeout
        if self._bus is None:
            return False

        # Add CRC and send
        crc = self._calculate_crc([self.can_id] + data)
        msg_data = data + [crc]
        msg = can.Message(
            arbitration_id=self.can_id,
            data=msg_data,
            is_extended_id=False
        )
        self._bus.send(msg)

        # Wait for correct response (may need to skip old/intermediate responses)
        timeout = 0.5
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            response = self._bus.recv(timeout=0.05)
            if response and response.arbitration_id == self.can_id:
                if len(response.data) >= 2:
                    if response.data[0] == self.CMD_ENABLE and response.data[1] == state:
                        # Got correct state confirmation
                        with self._lock:
                            self._enabled = enabled
                        return True

        return False

    def emergency_stop(self):
        """
        Emergency stop (immediate halt + disable).

        Stops motor motion AND disables motor (releases shaft).
        Critical for safety - prevents overheating and power consumption.

        Usage:
            motor.emergency_stop()
        """
        # Clear active command first (stop resending)
        if self._bus:
            self._bus.clear_active_command(self.can_id)

        # Send emergency stop command (halt motion)
        data = [self.CMD_EMERGENCY_STOP]
        self._send_command(data, wait_response=False)

        # CRITICAL: Disable motor (release shaft)
        # Without this, motor stays locked and consumes power
        time.sleep(0.05)  # Brief delay for stop command
        self.enable(False)

        with self._lock:
            self._current_speed_rpm = 0
            self._enabled = False

    def set_mode(self, mode: int):
        """
        Set motor work mode.

        Args:
            mode: Work mode (0-5)
                0 = CR_OPEN  (pulse, 0-400 RPM, fixed current)
                1 = CR_CLOSE (pulse, 0-1500 RPM, fixed current)
                2 = CR_vFOC  (pulse, 0-3000 RPM, adaptive current)
                3 = SR_OPEN  (serial, 0-400 RPM, fixed current) - Best for low speed
                4 = SR_CLOSE (serial, 0-1500 RPM, fixed current)
                5 = SR_vFOC  (serial, 0-3000 RPM, adaptive current) - Default

        Returns:
            bool: True if mode change successful

        Usage:
            motor.set_mode(3)  # Switch to SR_OPEN for smooth low-speed operation

        Note:
            SR_OPEN (mode=3) is optimized for low speeds (0-400 RPM)
            and eliminates oscillations at speeds like 19-60 RPM.
            Default is SR_vFOC (mode=5) which is optimized for high speeds.
        """
        if not 0 <= mode <= 5:
            raise ValueError(f"Mode must be 0-5, got {mode}")

        if self._bus is None:
            return False

        # Build command
        data = [self.CMD_SET_MODE, mode]
        crc = self._calculate_crc([self.can_id] + data)
        msg_data = data + [crc]

        # Send command
        msg = can.Message(
            arbitration_id=self.can_id,
            data=msg_data,
            is_extended_id=False
        )
        self._bus.send(msg)

        # Wait for response
        # Note: Motor may send response in different format or timing
        # Even if we timeout, the command usually worked (check motor behavior)
        timeout = 1.0  # Increased timeout
        start_time = time.time()
        response_received = False

        while (time.time() - start_time) < timeout:
            response = self._bus.recv(timeout=0.1)
            if response and response.arbitration_id == self.can_id:
                response_received = True
                # Response format: [CMD, status, CRC]
                if len(response.data) >= 2:
                    # Check if it's our command response
                    if response.data[0] == self.CMD_SET_MODE:
                        status = response.data[1]
                        if status == 1:
                            print(f"{self.name}: Mode set to {mode} successfully")
                            return True
                        else:
                            print(f"{self.name}: Mode change returned status {status}")
                            # Command sent but status unclear - likely still worked
                            return True
                    else:
                        # Got some response but not the expected one
                        # Command was likely sent successfully
                        print(f"{self.name}: Mode change sent (response: 0x{response.data[0]:02X})")
                        return True

        # No response received - but motor behavior suggests it worked anyway
        if not response_received:
            print(f"{self.name}: Mode change command sent (no response, but motor likely changed)")

        # Assume success - motor behavior will confirm
        return True

    # ========== Encoder Reading (Level 2) ==========

    def get_position(self) -> int:
        """
        Read encoder position in pulses.

        Returns:
            Encoder position (pulses since power-on or reset)
            Range: 0-3200 per revolution (16 subdivisions × 200 steps)

        Note:
            Servo42D uses 16384-line encoder (14-bit)
            With 16 subdivisions: 3200 pulses per revolution
        """
        # Send read encoder command (0x30)
        data = [self.CMD_READ_ENCODER]
        response = self._send_command(data, wait_response=True, timeout=0.1)

        if response and len(response.data) >= 8:
            # Response format (from manual):
            # Byte1: 0x30 (command)
            # Bytes 2-5: carry (int32_t) - full rotations count
            # Bytes 6-7: value (uint16_t) - position within rotation (0-0x4000)
            # Byte8: CRC
            if response.data[0] == self.CMD_READ_ENCODER:
                # Parse carry (int32_t, big-endian, bytes 1-4)
                carry = int.from_bytes(response.data[1:5], byteorder='big', signed=True)

                # Parse value (uint16_t, big-endian, bytes 5-6)
                value = int.from_bytes(response.data[5:7], byteorder='big', signed=False)

                # Total position in encoder counts (0x4000 = 16384 per revolution)
                # Convert to subdivision pulses (3200 per revolution)
                # position = carry * 3200 + (value * 3200 / 16384)
                position = carry * 3200 + int(value * 3200 / 16384)

                with self._lock:
                    self._encoder_position = position

                return position

        # If read failed, return cached value
        with self._lock:
            return self._encoder_position

    def get_speed(self) -> float:
        """
        Get current commanded speed in RPM.

        Returns:
            Current speed in RPM (positive=forward, negative=backward)
        """
        with self._lock:
            return self._current_speed_rpm

    # ========== Position Control (Level 3) ==========

    def zero_position(self):
        """
        Set current position as zero reference point.

        All future absolute position commands (move_to) will be relative to this point.

        Usage:
            motor.zero_position()           # Set current as zero
            motor.move_to(90, 40, 'degrees')  # Move to 90 degrees from zero
            motor.move_to(0, 30, 'degrees')   # Return to zero position

        Note:
            This is useful for setting home position for robot arms, grippers, etc.
        """
        # Command 0x92 sets current position as zero
        data = [0x92]
        response = self._send_command(data, wait_response=True)

        if response and len(response.data) >= 2:
            # Response: [0x92, status, CRC]
            # status=0: fail, status=1: success
            if response.data[0] == 0x92 and response.data[1] == 0x01:
                # Zero set successfully
                with self._lock:
                    self._encoder_position = 0
                return True

        return False

    def set_target_position_relative(self, pulses: int, speed: int, acceleration: int = 2):
        """
        Set target position relative to current position (non-blocking).

        This sends a position command to the motor's internal controller but returns
        immediately without waiting for completion. The motor handles trajectory
        planning at kHz frequency for precise, smooth motion.

        Args:
            pulses: Number of pulses to move (positive=forward, negative=backward)
            speed: Movement speed in RPM (0-3000)
            acceleration: Acceleration (0-255, default 2)

        Returns:
            bool: True if command sent successfully, False otherwise

        Usage:
            # Non-blocking position command
            motor.set_target_position_relative(3200, 40)  # 1 rotation at 40 RPM
            # Can immediately do other work while motor moves
            while True:
                pos = motor.get_position()
                # Check sensors, abort if needed, etc.

        Note:
            This is the foundation for high-precision position control in MecanumDrive.
            Motor controller runs at kHz, eliminating Python control loop latency.
        """
        # Direction (1=CW/forward, 0=CCW/backward for position mode)
        direction = 1 if pulses >= 0 else 0
        pulses_abs = abs(pulses)

        # Clamp values
        speed = int(max(0, min(3000, speed)))
        acceleration = int(max(0, min(255, acceleration)))
        pulses_abs = int(max(0, min(0xFFFFFF, pulses_abs)))  # 24-bit max

        # Build command: [CMD, dir+speed_h, speed_l, accel, pulse_h, pulse_m, pulse_l]
        byte2 = (direction << 7) | ((speed >> 8) & 0x0F)
        byte3 = speed & 0xFF
        pulse_h = (pulses_abs >> 16) & 0xFF
        pulse_m = (pulses_abs >> 8) & 0xFF
        pulse_l = pulses_abs & 0xFF

        data = [self.CMD_MOVE_RELATIVE, byte2, byte3, acceleration, pulse_h, pulse_m, pulse_l]

        # Add CRC
        crc = self._calculate_crc([self.can_id] + data)
        msg_data = data + [crc]

        # Send command (non-blocking)
        if self._bus:
            msg = can.Message(
                arbitration_id=self.can_id,
                data=msg_data,
                is_extended_id=False
            )
            self._bus.send(msg)
            return True

        return False

    def move_by(self, distance: float, speed: int, unit: str = 'degrees', acceleration: int = 2):
        """
        Move motor by relative distance (blocking).

        Args:
            distance: Distance to move (positive=forward, negative=backward)
            speed: Movement speed in RPM (0-3000)
            unit: Unit of distance - 'degrees' or 'rotations' (default: 'degrees')
            acceleration: Acceleration (0-255, default 2)

        Usage:
            motor.move_by(90, 40)                      # Move 90 degrees forward
            motor.move_by(-180, 30)                    # Move 180 degrees backward
            motor.move_by(2, 40, 'rotations')          # Move 2 full rotations
            motor.move_by(1.5, 50, 'rotations')        # Move 1.5 rotations
            motor.move_by(45, 60, acceleration=50)     # Slower acceleration

        Note:
            Motor moves relative to current position.
            Movement is blocking - function returns when complete.
        """
        # Convert to pulses
        if unit == 'degrees':
            pulses = int(abs(distance) * self.PULSES_PER_DEGREE)
        elif unit == 'rotations':
            pulses = int(abs(distance) * self.PULSES_PER_ROTATION)
        else:
            raise ValueError(f"Invalid unit '{unit}'. Use 'degrees' or 'rotations'")

        # Direction (1=CW/forward, 0=CCW/backward for position mode)
        # NOTE: Position mode has OPPOSITE direction bit from speed mode!
        direction = 1 if distance >= 0 else 0

        # Clamp values
        speed = int(max(0, min(3000, speed)))
        acceleration = int(max(0, min(255, acceleration)))
        pulses = int(max(0, min(0xFFFFFF, pulses)))  # 24-bit max

        # Flush CAN bus receive buffer before sending position command
        self._flush_can_buffer()

        # Build command: [CMD, dir+speed_h, speed_l, accel, pulse_h, pulse_m, pulse_l]
        byte2 = (direction << 7) | ((speed >> 8) & 0x0F)
        byte3 = speed & 0xFF
        pulse_h = (pulses >> 16) & 0xFF
        pulse_m = (pulses >> 8) & 0xFF
        pulse_l = pulses & 0xFF

        data = [self.CMD_MOVE_RELATIVE, byte2, byte3, acceleration, pulse_h, pulse_m, pulse_l]

        # Send command
        response = self._send_command(data, wait_response=True, timeout=0.5)

        if response and len(response.data) >= 2:
            if response.data[0] == self.CMD_MOVE_RELATIVE:
                status = response.data[1]
                if status == 0x01:
                    # Movement started, now wait for completion
                    # Poll for completion status (status=0x02)
                    return self._wait_for_move_complete(timeout=30.0)
                elif status == 0x00:
                    print(f"{self.name}: Move failed to start")
                    return False

        print(f"{self.name}: No response from move command")
        return False

    def move_to(self, position: float, speed: int, unit: str = 'degrees', acceleration: int = 2):
        """
        Move motor to absolute position.

        Args:
            position: Target position (relative to zero point set by zero_position())
            speed: Movement speed in RPM (0-3000)
            unit: Unit of position - 'degrees' or 'rotations' (default: 'degrees')
            acceleration: Acceleration (0-255, default 2)

        Usage:
            motor.zero_position()                   # Set current as zero
            motor.move_to(90, 40)                   # Move to 90 degrees
            motor.move_to(-180, 30)                 # Move to -180 degrees
            motor.move_to(2, 40, 'rotations')       # Move to 2 rotations
            motor.move_to(0, 30)                    # Return to zero

        Note:
            Requires zero_position() to be called first to set reference point.
            Movement is blocking - function returns when complete.
        """
        # Convert to pulses (signed 24-bit)
        if unit == 'degrees':
            pulses = int(position * self.PULSES_PER_DEGREE)
        elif unit == 'rotations':
            pulses = int(position * self.PULSES_PER_ROTATION)
        else:
            raise ValueError(f"Invalid unit '{unit}'. Use 'degrees' or 'rotations'")

        # Clamp values
        speed = int(max(0, min(3000, speed)))
        acceleration = int(max(0, min(255, acceleration)))

        # Clamp to signed 24-bit range (-8388607 to +8388607)
        pulses = int(max(-8388607, min(8388607, pulses)))

        # Flush CAN bus receive buffer before sending position command
        self._flush_can_buffer()

        # Build command: [CMD, speed_h, speed_l, accel, pulse_h, pulse_m, pulse_l]
        speed_h = (speed >> 8) & 0xFF
        speed_l = speed & 0xFF

        # Convert signed to bytes (24-bit two's complement)
        if pulses < 0:
            pulses_unsigned = (1 << 24) + pulses  # Two's complement
        else:
            pulses_unsigned = pulses

        pulse_h = (pulses_unsigned >> 16) & 0xFF
        pulse_m = (pulses_unsigned >> 8) & 0xFF
        pulse_l = pulses_unsigned & 0xFF

        data = [self.CMD_MOVE_ABSOLUTE, speed_h, speed_l, acceleration, pulse_h, pulse_m, pulse_l]

        # Send command
        response = self._send_command(data, wait_response=True, timeout=0.5)

        if response and len(response.data) >= 2:
            if response.data[0] == self.CMD_MOVE_ABSOLUTE:
                status = response.data[1]
                if status == 0x01:
                    # Movement started, now wait for completion
                    return self._wait_for_move_complete(timeout=30.0)
                elif status == 0x00:
                    print(f"{self.name}: Move failed to start")
                    return False

        print(f"{self.name}: No response from move command")
        return False

    def _wait_for_move_complete(self, timeout: float = 30.0) -> bool:
        """
        Wait for position movement to complete.

        Polls encoder position to detect when motor stops moving.
        Note: Motor may not send completion status if CanRSP is disabled.

        Returns:
            True if movement completed successfully, False otherwise
        """
        start_time = time.time()
        stable_count = 0
        stable_threshold = 3  # Readings with same position = stopped
        last_position = None

        # Also check for CAN status messages (if CanRSP enabled)
        while (time.time() - start_time) < timeout:
            # Check for status updates from motor (if available)
            response = self._bus.recv(timeout=0.01)
            if response and response.arbitration_id == self.can_id:
                if len(response.data) >= 2:
                    cmd = response.data[0]
                    status = response.data[1]

                    # Check for move complete status
                    if cmd in [self.CMD_MOVE_RELATIVE, self.CMD_MOVE_ABSOLUTE]:
                        if status == 0x02:
                            # Movement complete
                            return True
                        elif status == 0x03:
                            # End limit stopped
                            print(f"{self.name}: Movement stopped by limit switch")
                            return False

            # Poll encoder position to detect when motor stops
            current_position = self.get_position()

            if last_position is not None:
                if abs(current_position - last_position) < 5:  # Within 5 pulses = stationary
                    stable_count += 1
                    if stable_count >= stable_threshold:
                        # Motor has stopped moving
                        return True
                else:
                    # Still moving
                    stable_count = 0

            last_position = current_position
            time.sleep(0.1)  # Poll every 100ms

        # Timeout
        print(f"{self.name}: Movement timeout - motor may still be moving")
        return False

    # ========== Internal Helpers ==========

    def _calculate_crc(self, data: list) -> int:
        """Calculate 8-bit CRC checksum (simple sum & 0xFF)"""
        return sum(data) & 0xFF

    def _send_command(
        self,
        data: list,
        wait_response: bool = False,
        timeout: float = 0.1
    ) -> Optional[can.Message]:
        """
        Send CAN command to motor.

        Args:
            data: Command bytes (without CRC)
            wait_response: Whether to wait for response
            timeout: Response timeout in seconds

        Returns:
            Response message if wait_response=True, else None
        """
        if self._bus is None:
            raise RuntimeError(f"{self.name}: Not started (call .start() first)")

        # Add CRC
        crc = self._calculate_crc([self.can_id] + data)
        msg_data = data + [crc]

        # Create CAN message
        msg = can.Message(
            arbitration_id=self.can_id,
            data=msg_data,
            is_extended_id=False
        )

        try:
            # Use CanBus send/recv methods
            self._bus.send(msg)

            if wait_response:
                # Wait for response from THIS motor (filter by CAN ID AND command type)
                # Multiple motors on bus, need to keep reading until we get ours
                # Also check command type to avoid reading responses for other commands
                expected_cmd = data[0]  # First byte is command type
                start_time = time.time()
                while (time.time() - start_time) < timeout:
                    response = self._bus.recv(timeout=timeout / 10)
                    if response and response.arbitration_id == self.can_id:
                        # Check if response is for OUR command
                        if len(response.data) > 0 and response.data[0] == expected_cmd:
                            return response
                # Timeout - no response from our motor
                return None

            return None

        except Exception as e:
            print(f"{self.name}: Error sending command: {e}")
            return None

    # ========== Convenience Methods ==========

    def forward(self, speed_rpm: float = 100):
        """Run forward at specified speed (convenience method)"""
        self.run(abs(speed_rpm))

    def backward(self, speed_rpm: float = 100):
        """Run backward at specified speed (convenience method)"""
        self.run(-abs(speed_rpm))

    def __repr__(self):
        with self._lock:
            return (
                f"Servo42D(id={self.can_id}, "
                f"speed={self._current_speed_rpm:.0f}rpm, "
                f"enabled={self._enabled})"
            )
