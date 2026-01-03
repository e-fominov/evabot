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
