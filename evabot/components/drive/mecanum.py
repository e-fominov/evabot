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
        wheel_radius: float = 0.05,     # meters (50mm)
        wheel_base: float = 0.20,        # meters (200mm, front-back)
        track_width: float = 0.20,       # meters (200mm, left-right)
        pulses_per_rev: int = 3200,      # Servo42D: 200 steps × 16 subdivisions
        channel: str = 'can0',
        bitrate: int = 500000,
        pattern: str = 'X'               # 'X' or 'diamond'
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
        """
        super().__init__(name="MecanumDrive")

        # Robot geometry
        self.wheel_radius = wheel_radius
        self.wheel_base = wheel_base
        self.track_width = track_width
        self.pulses_per_rev = pulses_per_rev
        self.pattern = pattern.lower()

        # Validate pattern
        if self.pattern not in ['x', 'diamond']:
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
                target=self._odometry_loop,
                daemon=True,
                name="odometry"
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

        if self.pattern == 'x':
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
        self.fl.run(vel_to_rpm(vfl))
        self.fr.run(vel_to_rpm(vfr))
        self.bl.run(vel_to_rpm(vbl))
        self.br.run(vel_to_rpm(vbr))

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
        self.move(0, 0, 0)

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
                meters_per_pulse = (2 * math.pi * self.wheel_radius) / self.pulses_per_rev

                dfl = delta_fl * meters_per_pulse
                dfr = delta_fr * meters_per_pulse
                dbl = delta_bl * meters_per_pulse
                dbr = delta_br * meters_per_pulse

                # Mecanum forward kinematics
                # Convert wheel displacements to robot motion
                lx = (self.wheel_base + self.track_width) / 2

                if self.pattern == 'x':
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
