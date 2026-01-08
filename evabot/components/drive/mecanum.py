#!/usr/bin/env python3
r"""
Mecanum drive system with odometry.

Mecanum wheels allow omnidirectional movement:
  - Forward/backward
  - Strafe left/right
  - Rotate in place
  - Move in any direction while rotating

Motor layout (top view):
    FRONT
  FL ╱╲ FR     FL/BR: forward-left (/) rollers
    ╱  ╲       FR/BL: forward-right (\) rollers
   ╱    ╲
  BL ╲╱ BR
    BACK
"""

import threading
import time
import math
from typing import Optional
from ..base import Component
from ..motors import Servo42D


class MecanumDrive(Component):
    """
    Mecanum drive system with 4 motors and odometry.

    Supports two wheel patterns:
    - 'X': X-pattern (FL\\ FR/ BL/ BR\\)
    - 'diamond': Diamond/rhombic pattern (FL/ FR\\ BL\\ BR/)

    Automatically creates Servo42D motors and manages odometry.

    Usage (Level 3):
        robot = Robot()
        robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1, pattern='X')
        robot.start()

        # Simple movement
        robot.drive.forward(0.3)   # 0.3 m/s forward
        robot.drive.strafe(0.2)    # 0.2 m/s left
        robot.drive.rotate(0.5)    # 0.5 rad/s CCW

        # Omnidirectional (all at once!)
        robot.drive.move(vx=0.3, vy=0.1, vtheta=0.2)

        # Check position
        print(f"Position: {robot.odom.pose}")
    """

    def __init__(
        self,
        fl: int,
        fr: int,
        bl: int,
        br: int,
        wheel_radius: float = 0.04,  # meters (50mm)
        wheel_base: float = 0.20,  # meters (200mm, front-back)
        track_width: float = 0.20,  # meters (200mm, left-right)
        pulses_per_rev: int = 3200,  # Servo42D: 200 steps × 16 subdivisions
        channel: str = "can0",
        bitrate: int = 500000,
        pattern: str = "X",  # 'X' or 'diamond'
        acceleration: int = 50,  # Motor acceleration (0-255, higher=smoother)
    ):
        """
        Initialize mecanum drive.

        Args:
            fl, fr, bl, br: CAN IDs for motors (front-left, front-right, back-left, back-right)
            wheel_radius: Wheel radius in meters (default 50mm)
            wheel_base: Distance front-to-back in meters (default 200mm)
            track_width: Distance left-to-right in meters (default 200mm)
            pulses_per_rev: Encoder pulses per wheel revolution (default 3200)
            channel: CAN channel (default 'can0')
            bitrate: CAN bitrate (default 500000)
            pattern: Wheel pattern - 'X' or 'diamond' (default 'X')
                    'X': FL\\ FR/ BL/ BR\\ (most common)
                    'diamond': FL/ FR\\ BL\\ BR/ (alternative)
            acceleration: Motor acceleration (0-255, default 50)
                         Higher values = smoother but slower acceleration
                         Lower values = faster but jerkier acceleration
                         Recommended: 50-100 for smooth motion under load
        """
        super().__init__(name="MecanumDrive")

        # Robot geometry
        self.wheel_radius = wheel_radius
        self.wheel_base = wheel_base
        self.track_width = track_width
        self.pulses_per_rev = pulses_per_rev
        self.pattern = pattern.lower()
        self.acceleration = acceleration

        # Validate pattern
        if self.pattern not in ["x", "diamond"]:
            raise ValueError(f"Invalid pattern '{pattern}'. Use 'X' or 'diamond'")

        # Create motors
        self.fl = Servo42D(fl, channel=channel, bitrate=bitrate)
        self.fr = Servo42D(fr, channel=channel, bitrate=bitrate)
        self.bl = Servo42D(bl, channel=channel, bitrate=bitrate)
        self.br = Servo42D(br, channel=channel, bitrate=bitrate)

        self._motors = [self.fl, self.fr, self.bl, self.br]

        # Odometry state
        self._odom_thread: Optional[threading.Thread] = None
        self._running = False
        self._last_encoder = [0, 0, 0, 0]  # Last encoder readings

        # Target position control (non-blocking position mode)
        self._position_control_active = False
        self._target_dx = 0.0  # Target displacement in robot frame (meters)
        self._target_dy = 0.0
        self._target_dtheta = 0.0
        self._target_speed = 0.2  # m/s
        self._position_start_x = 0.0  # Odometry position when target was set
        self._position_start_y = 0.0
        self._position_start_theta = 0.0
        self._position_control_lock = threading.RLock()

    def start(self):
        """
        Start drive system (enable motors, start odometry).

        Called automatically when robot.start() is called.
        """
        # Start all motors
        for motor in self._motors:
            motor.start()

        # Start odometry thread if attached to robot
        if self._robot is not None:
            self._running = True
            self._odom_thread = threading.Thread(
                target=self._odometry_loop, daemon=True, name="odometry"
            )
            self._odom_thread.start()
            print(f"{self.name}: Odometry started")

        print(f"{self.name}: Ready (4 motors)")

    def stop(self):
        """
        Stop drive system (stop motors, stop odometry).

        Called automatically when robot.stop() is called.
        """
        # Stop odometry thread
        self._running = False
        if self._odom_thread:
            self._odom_thread.join(timeout=1.0)

        # Stop all motors
        for motor in self._motors:
            motor.stop()

        print(f"{self.name}: Stopped")

    # ========== Movement API (Level 3) ==========

    def move(self, vx: float = 0, vy: float = 0, vtheta: float = 0):
        """
        Omnidirectional movement.

        Args:
            vx: Forward velocity in m/s (positive = forward)
            vy: Left velocity in m/s (positive = left)
            vtheta: Rotation velocity in rad/s (positive = CCW)

        Usage:
            drive.move(vx=0.3)              # Forward only
            drive.move(vy=0.2)              # Strafe left only
            drive.move(vtheta=0.5)          # Rotate only
            drive.move(vx=0.3, vy=0.1)      # Diagonal
            drive.move(vx=0.3, vtheta=0.2)  # Arc
        """
        # Mecanum inverse kinematics
        # Convert desired velocities to wheel speeds
        # Reference: https://robohub.org/drive-kinematics-mecanum-wheels/

        # Calculate wheel velocities (m/s)
        lx = (self.wheel_base + self.track_width) / 2  # half diagonal

        if self.pattern == "x":
            # X pattern: FL\\ FR/ BL/ BR\\
            vfl = vx - vy - vtheta * lx
            vfr = vx + vy + vtheta * lx
            vbl = vx + vy - vtheta * lx
            vbr = vx - vy + vtheta * lx
        else:  # diamond
            # Diamond pattern: FL/ FR\\ BL\\ BR/
            vfl = vx + vy - vtheta * lx
            vfr = vx - vy + vtheta * lx
            vbl = vx - vy - vtheta * lx
            vbr = vx + vy + vtheta * lx

        # Convert linear velocity to RPM
        # v = ω × r  →  ω = v / r  (rad/s)
        # RPM = ω × (60 / 2π) = v / r × 60 / 2π
        def vel_to_rpm(v):
            omega = v / self.wheel_radius  # rad/s
            return omega * (60.0 / (2.0 * math.pi))

        # Set motor speeds
        # Right side motors (FR, BR) are physically mirrored, so negate their speeds
        self.fl.run(vel_to_rpm(vfl), acceleration=self.acceleration)
        self.fr.run(vel_to_rpm(-vfr), acceleration=self.acceleration)
        self.bl.run(vel_to_rpm(vbl), acceleration=self.acceleration)
        self.br.run(vel_to_rpm(-vbr), acceleration=self.acceleration)

    def forward(self, speed: float):
        """Move forward at speed (m/s)"""
        self.move(vx=speed)

    def backward(self, speed: float):
        """Move backward at speed (m/s)"""
        self.move(vx=-speed)

    def strafe_left(self, speed: float):
        """Strafe left at speed (m/s)"""
        self.move(vy=speed)

    def strafe_right(self, speed: float):
        """Strafe right at speed (m/s)"""
        self.move(vy=-speed)

    def rotate_ccw(self, speed: float):
        """Rotate counter-clockwise at speed (rad/s)"""
        self.move(vtheta=speed)

    def rotate_cw(self, speed: float):
        """Rotate clockwise at speed (rad/s)"""
        self.move(vtheta=-speed)

    def halt(self):
        """Stop all motion (convenience method)"""
        # Cancel any active position control
        with self._position_control_lock:
            self._position_control_active = False

        # Stop velocity control
        self.move(0, 0, 0)

    # ========== Non-blocking Position Control ==========

    def set_target_position(
        self,
        dx: float = 0,
        dy: float = 0,
        dtheta_deg: float = 0,
        speed: float = 0.2,
        acceleration: int = 50
    ):
        """
        Set target position for non-blocking position control (motor-based trajectory planning).

        This method leverages the Servo42D's internal trajectory planner running at kHz
        frequency for precise motion. Unlike velocity control with lidar feedback, this
        eliminates Python control loop latency.

        The odometry loop continuously updates motor target positions based on remaining
        distance, allowing real-time monitoring and abortion via lidar/sensors.

        Args:
            dx: Forward displacement in meters (positive = forward, negative = backward)
            dy: Left displacement in meters (positive = left, negative = right)
            dtheta_deg: Rotation angle in DEGREES (positive = CCW, negative = CW)
            speed: Maximum linear speed in m/s (default 0.2)
            acceleration: Motor acceleration (0-255, default 50)

        Returns:
            None (non-blocking)

        Usage:
            # Set target and continue execution
            robot.drive.set_target_position(dx=0.30, speed=0.16)

            # Rotate 90 degrees while moving forward
            robot.drive.set_target_position(dx=0.20, dtheta_deg=90, speed=0.16)

            # Monitor lidar while motors handle precise motion
            while robot.drive.is_position_control_active():
                distance, _, _ = robot.lidar.check_wall(0)
                if distance < 0.13:  # Safety stop
                    robot.drive.halt()
                    break
                time.sleep(0.02)

        Advantages over velocity control:
            - Motor controller runs at kHz (vs 10-50Hz Python loop)
            - Sub-millimeter precision even at high speeds
            - Can abort immediately if needed
            - Eliminates control loop latency

        Note:
            Requires robot attachment for odometry feedback.
            Target position is continuously updated in odometry loop based on remaining distance.
        """
        if self._robot is None:
            raise RuntimeError(
                "MecanumDrive must be attached to Robot to use set_target_position()"
            )

        # Get current odometry position
        current_pose = self._robot.odom.pose

        # Convert degrees to radians internally
        import math
        dtheta_rad = math.radians(dtheta_deg)

        with self._position_control_lock:
            self._target_dx = dx
            self._target_dy = dy
            self._target_dtheta = dtheta_rad  # Store as radians internally
            self._target_speed = speed
            self.acceleration = acceleration  # Update motor acceleration

            # Save starting position
            self._position_start_x = current_pose.x
            self._position_start_y = current_pose.y
            self._position_start_theta = current_pose.theta

            # Activate position control
            self._position_control_active = True

    def is_position_control_active(self) -> bool:
        """Check if position control is currently active."""
        with self._position_control_lock:
            return self._position_control_active

    def cancel_position_control(self):
        """Cancel active position control (same as halt())."""
        self.halt()

    # ========== Blocking Movements ==========

    def move_for(
        self, duration: float, vx: float = 0, vy: float = 0, vtheta: float = 0
    ):
        """
        Move at specified velocities for a duration (blocks until complete).

        This is time-based control - moves for a set time regardless of distance traveled.
        Useful for simple timed movements when exact distance is not critical.

        Args:
            duration: Time to move in seconds
            vx: Forward velocity in m/s (positive = forward)
            vy: Left velocity in m/s (positive = left)
            vtheta: Rotation velocity in rad/s (positive = CCW)

        Usage:
            robot.drive.move_for(5.0, vx=0.2)                    # Forward 5 sec
            robot.drive.move_for(3.0, vtheta=0.5)                # Rotate 3 sec
            robot.drive.move_for(4.0, vx=0.2, vy=0.1)            # Diagonal 4 sec
            robot.drive.move_for(2.0, vx=0.2, vtheta=0.3)        # Arc 2 sec
        """
        if duration <= 0:
            return

        try:
            self.move(vx=vx, vy=vy, vtheta=vtheta)
            time.sleep(duration)
        except KeyboardInterrupt:
            self.halt()
            raise
        finally:
            self.halt()

    def move_by(
        self,
        dx: float = 0,
        dy: float = 0,
        dtheta: float = 0,
        speed: float = 0.2,
        timeout: float = 30.0,
    ):
        """
        Move by specified displacements (blocks until complete).

        Uses odometry feedback to move exactly the specified distances.
        This is a blocking call - returns when movement is complete or timeout reached.

        Args:
            dx: Forward distance in meters (positive = forward, negative = backward)
            dy: Left distance in meters (positive = left, negative = right)
            dtheta: Rotation angle in radians (positive = CCW, negative = CW)
            speed: Maximum linear speed in m/s (default 0.2)
            timeout: Maximum time to wait in seconds (default 30.0)

        Returns:
            bool: True if target reached, False if timeout

        Raises:
            RuntimeError: If robot not attached or odometry not available

        Usage:
            robot.drive.move_by(dx=1.0)              # Forward 1m
            robot.drive.move_by(dy=0.5)              # Strafe left 0.5m
            robot.drive.move_by(dtheta=math.pi/2)    # Rotate 90° CCW
            robot.drive.move_by(dx=1.0, dy=0.5)      # Diagonal
            robot.drive.move_by(dx=1.0, dtheta=0.5)  # Forward + rotate
        """
        # Check if robot attached
        if self._robot is None:
            raise RuntimeError(
                "MecanumDrive must be attached to Robot to use move_by()"
            )

        # If all zeros, nothing to do
        if dx == 0 and dy == 0 and dtheta == 0:
            return True

        # Get starting pose
        start_pose = self._robot.odom.pose
        start_x = start_pose.x
        start_y = start_pose.y
        start_theta = start_pose.theta

        # Calculate target pose (in odometry frame)
        # Note: dx, dy are in robot frame, need to convert to odometry frame
        cos_theta = math.cos(start_theta)
        sin_theta = math.sin(start_theta)

        target_x = start_x + dx * cos_theta - dy * sin_theta
        target_y = start_y + dx * sin_theta + dy * cos_theta
        target_theta = start_theta + dtheta

        # Calculate total distance for speed scaling
        linear_dist = math.sqrt(dx**2 + dy**2)
        angular_dist = abs(dtheta)

        # Determine movement duration (use longer of linear/angular)
        if linear_dist > 0:
            linear_time = linear_dist / speed
        else:
            linear_time = 0

        if angular_dist > 0:
            # Use reasonable rotation speed (e.g., 0.5 rad/s per 0.2 m/s)
            rot_speed = speed * 2.5  # Scale rotation speed with linear speed
            angular_time = angular_dist / rot_speed
        else:
            angular_time = 0

        duration = max(linear_time, angular_time)

        if duration == 0:
            return True

        # Calculate velocities in robot frame
        vx = dx / duration
        vy = dy / duration
        vtheta = dtheta / duration

        # Thresholds for "close enough"
        pos_threshold = 0.01  # 1cm
        angle_threshold = 0.05  # ~3 degrees

        # Start movement
        start_time = time.time()
        self.move(vx=vx, vy=vy, vtheta=vtheta)

        try:
            # Control loop
            rate = 50  # Hz
            period = 1.0 / rate

            while True:
                # Check timeout
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    self.halt()
                    return False

                # Get current pose
                current_pose = self._robot.odom.pose

                # Calculate errors (in odometry frame)
                error_x = target_x - current_pose.x
                error_y = target_y - current_pose.y
                error_theta = target_theta - current_pose.theta

                # Normalize angle error to [-pi, pi]
                while error_theta > math.pi:
                    error_theta -= 2 * math.pi
                while error_theta < -math.pi:
                    error_theta += 2 * math.pi

                # Calculate distance to target
                pos_error = math.sqrt(error_x**2 + error_y**2)
                angle_error = abs(error_theta)

                # Check if reached target
                if pos_error < pos_threshold and angle_error < angle_threshold:
                    self.halt()
                    return True

                # Proportional control with distance remaining
                # Slow down as we approach target
                remaining_fraction = pos_error / (
                    linear_dist + 0.001
                )  # Avoid division by zero
                remaining_fraction = max(
                    0.1, min(1.0, remaining_fraction)
                )  # Clamp to [0.1, 1.0]

                # Update velocities (transform errors back to robot frame for control)
                cos_current = math.cos(current_pose.theta)
                sin_current = math.sin(current_pose.theta)

                error_x_robot = error_x * cos_current + error_y * sin_current
                error_y_robot = -error_x * sin_current + error_y * cos_current

                # Scale velocities based on remaining distance
                new_vx = (error_x_robot / duration) * remaining_fraction
                new_vy = (error_y_robot / duration) * remaining_fraction
                new_vtheta = error_theta / duration

                # Limit speeds
                speed_limit = speed * 1.2  # Allow slight overshoot for faster response
                new_vx = max(-speed_limit, min(speed_limit, new_vx))
                new_vy = max(-speed_limit, min(speed_limit, new_vy))

                rot_limit = speed * 3.0
                new_vtheta = max(-rot_limit, min(rot_limit, new_vtheta))

                self.move(vx=new_vx, vy=new_vy, vtheta=new_vtheta)

                time.sleep(period)

        except KeyboardInterrupt:
            self.halt()
            raise

    # ========== Utility Methods ==========

    def zero_position(self):
        """
        Reset odometry to (0, 0, 0).

        Sets the current position as the origin. Useful for:
        - Starting navigation from a known point
        - Resetting after manual repositioning
        - Beginning a new task or mission

        Raises:
            RuntimeError: If robot not attached

        Usage:
            # Mark current location as origin
            robot.drive.zero_position()

            # Now move relative to this new origin
            robot.drive.move_by(dx=1.0)
            print(robot.odom.pose.x)  # Will be ~1.0

            # Move back to origin
            robot.drive.move_by(dx=-1.0)
            print(robot.odom.pose.x)  # Will be ~0.0
        """
        if self._robot is None:
            raise RuntimeError(
                "MecanumDrive must be attached to Robot to use zero_position()"
            )

        self._robot._state.odom.set_pose(0, 0, 0)
        self._robot._state.odom.set_velocity(0, 0, 0)

    # ========== Odometry (Internal) ==========

    def _odometry_loop(self):
        """
        Odometry loop - runs in background thread.

        Reads encoder positions, computes motion, updates robot.odom.
        """
        rate = 50  # Hz
        period = 1.0 / rate
        next_time = time.time()

        # Initialize encoder readings
        for i, motor in enumerate(self._motors):
            self._last_encoder[i] = motor.get_position()

        while self._running:
            try:
                # Read current encoder positions
                encoder = [motor.get_position() for motor in self._motors]

                # Compute deltas (pulses)
                delta_fl = encoder[0] - self._last_encoder[0]
                delta_fr = encoder[1] - self._last_encoder[1]
                delta_bl = encoder[2] - self._last_encoder[2]
                delta_br = encoder[3] - self._last_encoder[3]

                # Convert pulses to wheel displacement (meters)
                # distance = (pulses / pulses_per_rev) × (2π × radius)
                meters_per_pulse = (
                    2 * math.pi * self.wheel_radius
                ) / self.pulses_per_rev

                dfl = delta_fl * meters_per_pulse
                dfr = delta_fr * meters_per_pulse
                dbl = delta_bl * meters_per_pulse
                dbr = delta_br * meters_per_pulse

                # Mecanum forward kinematics
                # Convert wheel displacements to robot motion
                lx = (self.wheel_base + self.track_width) / 2

                if self.pattern == "x":
                    # X pattern kinematics
                    dx = (dfl + dfr + dbl + dbr) / 4.0
                    dy = (-dfl + dfr + dbl - dbr) / 4.0
                    dtheta = (-dfl + dfr - dbl + dbr) / (4.0 * lx)
                else:  # diamond
                    # Diamond pattern kinematics
                    dx = (dfl + dfr + dbl + dbr) / 4.0
                    dy = (dfl - dfr - dbl + dbr) / 4.0
                    dtheta = (-dfl + dfr - dbl + dbr) / (4.0 * lx)

                # Update robot odometry (in odometry frame)
                if self._robot is not None:
                    # Get current pose
                    current = self._robot.odom.pose

                    # Integrate motion (odometry frame = fixed)
                    # For now, simple integration (assumes small dt)
                    # TODO: Consider robot orientation for better accuracy
                    cos_theta = math.cos(current.theta)
                    sin_theta = math.sin(current.theta)

                    # Transform motion to odometry frame
                    dx_odom = dx * cos_theta - dy * sin_theta
                    dy_odom = dx * sin_theta + dy * cos_theta

                    # Update pose
                    new_x = current.x + dx_odom
                    new_y = current.y + dy_odom
                    new_theta = current.theta + dtheta

                    self._robot._state.odom.set_pose(new_x, new_y, new_theta)

                    # Update velocity (v = delta / dt)
                    vx = dx / period
                    vy = dy / period
                    vtheta = dtheta / period
                    self._robot._state.odom.set_velocity(vx, vy, vtheta)

                    # ========== Position Control Logic ==========
                    # If position control active, calculate and send motor position commands
                    with self._position_control_lock:
                        if self._position_control_active:
                            # Calculate displacement traveled so far (in odometry frame)
                            traveled_x_odom = current.x - self._position_start_x
                            traveled_y_odom = current.y - self._position_start_y
                            traveled_theta = current.theta - self._position_start_theta

                            # Normalize angle
                            while traveled_theta > math.pi:
                                traveled_theta -= 2 * math.pi
                            while traveled_theta < -math.pi:
                                traveled_theta += 2 * math.pi

                            # Calculate target in odometry frame
                            cos_start = math.cos(self._position_start_theta)
                            sin_start = math.sin(self._position_start_theta)

                            target_x_odom = self._position_start_x + self._target_dx * cos_start - self._target_dy * sin_start
                            target_y_odom = self._position_start_y + self._target_dx * sin_start + self._target_dy * cos_start
                            target_theta = self._position_start_theta + self._target_dtheta

                            # Calculate remaining distance (in odometry frame)
                            remaining_x_odom = target_x_odom - current.x
                            remaining_y_odom = target_y_odom - current.y
                            remaining_theta = target_theta - current.theta

                            # Normalize angle
                            while remaining_theta > math.pi:
                                remaining_theta -= 2 * math.pi
                            while remaining_theta < -math.pi:
                                remaining_theta += 2 * math.pi

                            # Convert remaining distance to robot frame
                            cos_current = math.cos(current.theta)
                            sin_current = math.sin(current.theta)

                            remaining_dx_robot = remaining_x_odom * cos_current + remaining_y_odom * sin_current
                            remaining_dy_robot = -remaining_x_odom * sin_current + remaining_y_odom * cos_current

                            # Check if reached target
                            pos_error = math.sqrt(remaining_dx_robot**2 + remaining_dy_robot**2)
                            angle_error = abs(remaining_theta)

                            if pos_error < 0.005 and angle_error < 0.02:  # 5mm, ~1 degree
                                # Target reached, deactivate position control
                                self._position_control_active = False
                                # Stop motors
                                for motor in self._motors:
                                    motor.run(0, acceleration=self.acceleration)
                            else:
                                # Calculate required wheel displacements (mecanum inverse kinematics)
                                lx = (self.wheel_base + self.track_width) / 2

                                if self.pattern == "x":
                                    # X pattern: FL\\ FR/ BL/ BR\\
                                    dfl_wheel = remaining_dx_robot - remaining_dy_robot - remaining_theta * lx
                                    dfr_wheel = remaining_dx_robot + remaining_dy_robot + remaining_theta * lx
                                    dbl_wheel = remaining_dx_robot + remaining_dy_robot - remaining_theta * lx
                                    dbr_wheel = remaining_dx_robot - remaining_dy_robot + remaining_theta * lx
                                else:  # diamond
                                    # Diamond pattern: FL/ FR\\ BL\\ BR/
                                    dfl_wheel = remaining_dx_robot + remaining_dy_robot - remaining_theta * lx
                                    dfr_wheel = remaining_dx_robot - remaining_dy_robot + remaining_theta * lx
                                    dbl_wheel = remaining_dx_robot - remaining_dy_robot - remaining_theta * lx
                                    dbr_wheel = remaining_dx_robot + remaining_dy_robot + remaining_theta * lx

                                # Convert wheel linear displacement to pulses
                                pulses_per_meter = self.pulses_per_rev / (2 * math.pi * self.wheel_radius)

                                pulses_fl = int(dfl_wheel * pulses_per_meter)
                                pulses_fr = int(dfr_wheel * pulses_per_meter)
                                pulses_bl = int(dbl_wheel * pulses_per_meter)
                                pulses_br = int(dbr_wheel * pulses_per_meter)

                                # Convert linear speed to RPM
                                omega = self._target_speed / self.wheel_radius  # rad/s
                                speed_rpm = int(omega * (60.0 / (2.0 * math.pi)))

                                # Send non-blocking position commands to motors
                                # Right side motors (FR, BR) are mirrored, so negate
                                self.fl.set_target_position_relative(pulses_fl, speed_rpm, self.acceleration)
                                self.fr.set_target_position_relative(-pulses_fr, speed_rpm, self.acceleration)
                                self.bl.set_target_position_relative(pulses_bl, speed_rpm, self.acceleration)
                                self.br.set_target_position_relative(-pulses_br, speed_rpm, self.acceleration)

                # Save encoder values
                self._last_encoder = encoder

                # Sleep until next iteration
                next_time += period
                sleep_time = next_time - time.time()
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    next_time = time.time()

            except Exception as e:
                print(f"{self.name}: Odometry error: {e}")
                time.sleep(period)

    def __repr__(self):
        return (
            f"MecanumDrive("
            f"fl={self.fl.can_id}, fr={self.fr.can_id}, "
            f"bl={self.bl.can_id}, br={self.br.can_id})"
        )
