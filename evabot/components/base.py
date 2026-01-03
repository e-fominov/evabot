#!/usr/bin/env python3
"""
Base component class for all robot components.
All hardware components (motors, sensors, actuators) inherit from this.
"""

import threading
from typing import Optional


class Component:
    """
    Base class for all robot components.

    Components can be motors, sensors, actuators, or drive systems.
    They handle their own initialization, background threads, and cleanup.
    """

    def __init__(self, name: Optional[str] = None):
        """
        Initialize component.

        Args:
            name: Optional name for this component (e.g., "front_left_motor")
        """
        self.name = name or self.__class__.__name__
        self._robot = None
        self._thread = None
        self._running = False

    def _attach_to_robot(self, robot):
        """
        Called when component is assigned to a robot.
        This is internal - users don't call this.

        Args:
            robot: The Robot instance this component belongs to
        """
        self._robot = robot

    def start(self):
        """
        Start the component (e.g., begin sensor readings, enable motors).
        Override this in subclasses if needed.
        """
        pass

    def stop(self):
        """
        Stop the component gracefully.
        Override this in subclasses if needed.
        """
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"
