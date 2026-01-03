#!/usr/bin/env python3
"""
Lesson 1.4: Read Position - SOLUTION
====================================

This is the complete working solution.
Try to complete template.py yourself first!
"""

import time
from evabot.components.motors import Servo42D

# Servo42D has 3200 pulses per revolution
PULSES_PER_REV = 3200


def main():
    print("=" * 60)
    print("Lesson 1.4: Read Position!")
    print("=" * 60)
    print()

    # Create a motor with CAN ID 1
    motor = Servo42D(can_id=1)

    # Start the motor
    motor.start()

    # Read the starting position
    start_position = motor.get_position()
    print(f"Starting position: {start_position} pulses")
    print()

    print("Running motor at 30 RPM for 5 seconds...")
    print("Watching encoder position...")
    print()

    # Run the motor at 30 RPM
    motor.run(30)

    # Read position every 0.5 seconds for 5 seconds
    for i in range(10):
        time.sleep(0.5)

        # Read current position
        current_position = motor.get_position()

        # Calculate pulses traveled
        pulses_traveled = current_position - start_position

        print(f"  {i*0.5+0.5:.1f}s: position = {current_position:6d} pulses "
              f"(+{pulses_traveled:6d} since start)")

    print()
    print("Stopping motor...")

    # Stop the motor
    motor.stop()

    # Read final position
    final_position = motor.get_position()

    # Calculate total distance
    total_pulses = final_position - start_position
    total_rotations = total_pulses / PULSES_PER_REV

    print()
    print("=" * 60)
    print(f"Total pulses:    {total_pulses}")
    print(f"Total rotations: {total_rotations:.2f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
