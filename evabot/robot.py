#!/usr/bin/env python3
"""
Main Robot class - container for all components.
Kids interact with this to build their robot.
"""

import threading
import time
import signal
import sys
from typing import Optional, Callable, List
from .state import RobotState
from .components.base import Component


class Robot:
    """
    Main robot container.

    This is the primary interface kids use to build and control their robot.

    Usage:
        robot = Robot()
        robot.drive = MecanumDrive(fl=4, fr=2, bl=3, br=1)
        robot.lidar = RPLidarC1()

        # Access data through components (not generic .state!)
        robot.odom.x         # meters (odometry frame)
        robot.lidar.front    # meters
        robot.camera.image   # RGB image

        robot.start()
    """

    def __init__(self):
        """Initialize empty robot."""
        # Internal state (thread-safe, not exposed directly)
        self._state = RobotState()

        # Component registry
        self._components: List[Component] = []

        # Components (None until assigned)
        # These ARE the API - accessed directly by users
        self._odom = None       # Odometry component (provides .x, .y, .theta)
        self._drive = None      # Drive system
        self._lidar = None      # Lidar sensor
        self._camera = None     # Camera sensor
        self._actuator = None   # Gripper/arm

        # Control loops
        self._loops: List[tuple] = []  # [(function, rate), ...]
        self._running = False
        self._loop_threads: List[threading.Thread] = []

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\nShutting down robot...")
        self.stop()
        sys.exit(0)

    def _register_component(self, component: Component):
        """
        Register a component with the robot.
        Internal - called automatically when components are assigned.
        """
        if component not in self._components:
            self._components.append(component)
            component._attach_to_robot(self)

    # ========== Odometry ==========

    @property
    def odom(self):
        """
        Access odometry data (position in odometry frame).

        Usage:
            robot.odom.x        # meters
            robot.odom.y        # meters
            robot.odom.theta    # radians
            robot.odom.pose     # Pose object
            robot.odom.velocity # Velocity object
        """
        # Return internal state's odom - components will populate this
        return self._state.odom

    # Future: robot.map for SLAM (Phase 7)

    # ========== Drive System ==========

    @property
    def drive(self):
        """Access drive system (e.g., MecanumDrive)"""
        return self._drive

    @drive.setter
    def drive(self, drive_component):
        """Assign drive system"""
        self._drive = drive_component
        self._register_component(drive_component)

    # ========== Sensors ==========

    @property
    def lidar(self):
        """
        Access lidar sensor.

        Usage:
            robot.lidar.front   # meters
            robot.lidar.back    # meters
            robot.lidar.left    # meters
            robot.lidar.right   # meters
            robot.lidar.scan    # Full 360° scan
        """
        return self._lidar

    @lidar.setter
    def lidar(self, lidar_component):
        """Assign lidar"""
        self._lidar = lidar_component
        self._register_component(lidar_component)

    @property
    def camera(self):
        """
        Access camera.

        Usage:
            robot.camera.image            # RGB image
            robot.camera.depth            # Depth image
            robot.camera.depth_at(x, y)   # Depth at pixel
        """
        return self._camera

    @camera.setter
    def camera(self, camera_component):
        """Assign camera"""
        self._camera = camera_component
        self._register_component(camera_component)

    # ========== Actuators ==========

    @property
    def actuator(self):
        """Access actuator (gripper, arm, etc.)"""
        return self._actuator

    @actuator.setter
    def actuator(self, actuator_component):
        """Assign actuator"""
        self._actuator = actuator_component
        self._register_component(actuator_component)

    # ========== Navigation ==========

    def move_to_wall(
        self,
        direction: int,
        stop_distance: float = 0.125,
        speed: float = 0.3,
        acceleration: int = 50,
        timeout: float = 10.0,
        safe_distance: float = 0.09,
        max_travel: float = None,
        debug: bool = False,
    ):
        """
        Move toward a wall using lidar feedback.

        Drives in the given direction while:
        - Stopping at stop_distance from the ahead wall
        - Pushing away from any side wall closer than stop_distance
        - Aligning theta using all visible walls
        - Emergency stopping if ahead wall < safe_distance
        - Stopping after max_travel distance (for cell-by-cell movement)

        Args:
            direction: Lidar angle to move toward (0=front, 90=right, 180=back, 270=left)
            stop_distance: Distance from wall to stop at (meters, default 0.125)
            speed: Movement speed (m/s, default 0.3)
            acceleration: Motor acceleration (0-255, default 50)
            timeout: Maximum time to move (seconds, default 10)
            safe_distance: Emergency stop distance (meters, default 0.09)
            max_travel: Maximum distance to travel (meters, default None = no limit)
            debug: Print wall readings each cycle (default False)

        Returns:
            True if stopped at wall, False if timeout or safety stop

        Usage:
            robot.move_to_wall(0)           # move forward to wall
            robot.move_to_wall(270)         # move left to wall
            robot.move_to_wall(90, speed=0.5, debug=True)  # debug mode

        Requires:
            robot.drive and robot.lidar must be set up
        """
        if self._drive is None or self._lidar is None:
            raise RuntimeError("move_to_wall requires both drive and lidar")

        # Direction constants
        dir_names = {0: "F", 90: "R", 180: "B", 270: "L"}
        dir_delta = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}
        opposite = {0: 180, 180: 0, 90: 270, 270: 90}

        dx_dir, dy_dir = dir_delta[direction]
        opp = opposite[direction]

        # Quick pre-align if badly misaligned (>8 degrees)
        for _ in range(20):
            _, a, q = self._lidar.check_wall(direction)
            if a is None or q is None or q < 0.3 or abs(a) < 8:
                break
            correction = max(-10.0, min(10.0, a))
            if debug:
                print(f"    Pre-align: {a:+.1f}° -> correction {correction:+.1f}°")
            self._drive.set_target_position(dtheta_deg=correction, speed=0.1, acceleration=50)
            time.sleep(0.15)
        self._drive.halt()

        # Record starting ahead distance for max_travel tracking
        start_ahead, _, _ = self._lidar.check_wall(direction)

        start_time = time.time()
        log_time = 0

        while time.time() - start_time < timeout:
            t_now = time.time() - start_time

            # Read ahead wall
            d_ahead, a_ahead, q_ahead = self._lidar.check_wall(direction)

            # Emergency stop
            if d_ahead is not None and d_ahead < safe_distance:
                self._drive.halt()
                if debug:
                    print(f"    [{t_now:.1f}s] SAFETY STOP: ahead={d_ahead*100:.1f}cm")
                return False

            # Arrived at wall
            if d_ahead is not None and d_ahead <= stop_distance + 0.01:
                self._drive.halt()
                if debug:
                    print(f"    [{t_now:.1f}s] ARRIVED: ahead={d_ahead*100:.1f}cm")
                return True

            # Traveled max distance (one cell)
            if max_travel is not None and start_ahead is not None and d_ahead is not None:
                traveled = start_ahead - d_ahead
                if traveled >= max_travel:
                    self._drive.halt()
                    if debug:
                        print(f"    [{t_now:.1f}s] MAX TRAVEL: {traveled*100:.1f}cm")
                    return True

            # Forward target
            if d_ahead is not None:
                remaining = max(d_ahead - stop_distance, 0.01)
            else:
                remaining = 0.15  # half cell default
            if max_travel is not None:
                remaining = min(remaining, max_travel)
            target_dx = dx_dir * remaining
            target_dy = dy_dir * remaining

            # Read all other walls: theta alignment + push away
            angle_samples = []
            if a_ahead is not None and q_ahead is not None and q_ahead > 0.5:
                angle_samples.append(a_ahead)

            debug_walls = {}
            if debug:
                debug_walls[direction] = (d_ahead, a_ahead)

            for wall_dir in [0, 90, 180, 270]:
                if wall_dir == direction:
                    continue
                d_w, a_w, q_w = self._lidar.check_wall(wall_dir)
                if d_w is None:
                    continue
                if debug:
                    debug_walls[wall_dir] = (d_w, a_w)
                if a_w is not None and q_w is not None and q_w > 0.5:
                    angle_samples.append(a_w)
                if wall_dir != opp and d_w < stop_distance and q_w is not None and q_w > 0.3:
                    push = (stop_distance - d_w) * 1.0
                    wx, wy = dir_delta[wall_dir]
                    target_dx -= wx * push
                    target_dy -= wy * push

            # Theta correction
            dtheta_deg = 0.0
            if angle_samples:
                avg = sum(angle_samples) / len(angle_samples)
                dtheta_deg = max(-15.0, min(15.0, avg))

            # Debug output every 200ms
            if debug and t_now - log_time >= 0.2:
                log_time = t_now
                parts = []
                for wd in [0, 90, 180, 270]:
                    if wd in debug_walls:
                        d, a = debug_walls[wd]
                        if d is None:
                            continue
                        s = f"{dir_names[wd]}={d*100:.0f}cm"
                        if a is not None:
                            s += f"/{a:+.1f}°"
                        parts.append(s)
                parts.append(f"theta={dtheta_deg:+.1f}°")
                parts.append(f"target=({target_dx*100:.1f},{target_dy*100:.1f})")
                print(f"    [{t_now:.1f}s] {' | '.join(parts)}")

            # Send target
            self._drive.set_target_position(
                dx=target_dx, dy=target_dy, dtheta_deg=dtheta_deg,
                speed=speed, acceleration=acceleration,
            )

            # Position control finished (no wall ahead, moved full distance)
            if not self._drive.is_position_control_active():
                self._drive.halt()
                if debug:
                    print(f"    [{t_now:.1f}s] Position control complete")
                return True

            time.sleep(0.01)

        self._drive.halt()
        if debug:
            print(f"    Timeout!")
        return False

    # ========== Control Loops ==========

    def loop(self, rate: float = 10):
        """
        Decorator for control loops.

        Args:
            rate: Loop frequency in Hz (default 10)

        Usage:
            @robot.loop(rate=10)
            def navigate(robot):  # Gets robot, not state!
                if robot.lidar.front < 0.3:  # 30cm = 0.3m
                    robot.drive.stop()
                else:
                    robot.drive.forward(0.3)

            robot.start()  # Runs loop forever
        """
        def decorator(func: Callable):
            self._loops.append((func, rate))
            return func
        return decorator

    def _run_loop(self, func: Callable, rate: float):
        """Run a single control loop at specified rate"""
        period = 1.0 / rate
        next_time = time.time()

        while self._running:
            try:
                # Call user function with robot (not state!)
                func(self)

                # Sleep until next iteration
                next_time += period
                sleep_time = next_time - time.time()
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    # We're running behind schedule
                    next_time = time.time()

            except Exception as e:
                print(f"Error in loop {func.__name__}: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(period)

    # ========== Lifecycle ==========

    def start(self):
        """
        Start all components and run control loops.

        If there are no loops, this returns immediately after starting components.
        If there are loops, this blocks forever (until Ctrl+C).
        """
        print("Starting robot...")

        # Start all components
        for component in self._components:
            print(f"  Starting {component.name}...")
            component.start()

        print("Robot ready!")

        # If we have loops, run them
        if self._loops:
            self._running = True

            # Start each loop in its own thread
            for func, rate in self._loops:
                thread = threading.Thread(
                    target=self._run_loop,
                    args=(func, rate),
                    daemon=True,
                    name=f"loop_{func.__name__}"
                )
                thread.start()
                self._loop_threads.append(thread)

            print(f"Running {len(self._loops)} control loop(s)...")
            print("Press Ctrl+C to stop")

            # Block forever (or until signal)
            try:
                while self._running:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\nStopping...")
                self.stop()

    def stop(self):
        """Stop all components and loops"""
        print("Stopping robot...")

        # Stop loops
        self._running = False
        for thread in self._loop_threads:
            thread.join(timeout=1.0)
        self._loop_threads.clear()

        # Stop all components
        for component in self._components:
            try:
                component.stop()
            except Exception as e:
                print(f"Error stopping {component.name}: {e}")

        print("Robot stopped")

    def __repr__(self):
        components = [c.name for c in self._components]
        return f"Robot(components={components})"
