#!/usr/bin/env python3
"""
Lesson 1.4: Read Position
=========================

Learn to read encoder and track motor position!

Instructions:
1. Create and start a motor
2. Read the starting position
3. Run the motor
4. Read position periodically while running
5. Calculate total rotations

Fill in the blanks marked with # TODO
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

    # TODO: Create a motor with CAN ID 1


    # TODO: Start the motor


    # TODO: Read the starting position
    # Hint: start_position = motor.get_position()

    print(f"Starting position: {start_position} pulses")
    print()

    print("Running motor at 30 RPM for 5 seconds...")
    print("Watching encoder position...")
    print()

    # TODO: Run the motor at 30 RPM


    # Read position every 0.5 seconds for 5 seconds
    for i in range(10):
        time.sleep(0.5)

        # TODO: Read current position
        # Hint: current_position = motor.get_position()


        # Calculate pulses traveled
        pulses_traveled = current_position - start_position

        print(f"  {i*0.5:.1f}s: position = {current_position:6d} pulses "
              f"(+{pulses_traveled:6d} since start)")

    print()
    print("Stopping motor...")

    # TODO: Stop the motor


    # TODO: Read final position


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
