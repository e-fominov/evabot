#!/usr/bin/env python3
"""
Lesson 1.5: Move Exact Distance - TEMPLATE
===========================================

Fill in the blanks to make the motor move to exact positions!
Look for TODO comments and replace ??? with the correct code.
"""

import time
from evabot.components.motors import Servo42D


def main():
    print("=" * 60)
    print("Lesson 1.5: Move Exact Distance!")
    print("=" * 60)
    print()

    # TODO: Create a motor with CAN ID 1
    motor = ???

    # TODO: Start the motor
    print("Starting motor...")
    motor.???()

    # Step 1: Set current position as zero
    print("\n--- Step 1: Setting Zero Position ---")
    print("Setting current position as zero (home position)...")

    # TODO: Set zero position (hint: use zero_position method)
    motor.???()

    print("✓ Zero position set!")
    time.sleep(1)

    # Step 2: Move 90 degrees forward
    print("\n--- Step 2: Move 90 Degrees Forward ---")
    print("Moving 90 degrees (quarter turn) at 40 RPM...")

    # TODO: Move by 90 degrees at speed 40
    # Hint: motor.move_by(distance, speed, unit='degrees')
    motor.move_by(???, speed=???, unit='degrees')

    print("✓ Moved 90 degrees!")

    # Read position to verify
    position = motor.get_position()
    print(f"Current position: {position} pulses (should be ~800)")
    time.sleep(1)

    # Step 3: Return to zero
    print("\n--- Step 3: Return to Zero ---")
    print("Moving back to zero position at 30 RPM...")

    # TODO: Move to absolute position 0 at speed 30
    # Hint: motor.move_to(position, speed, unit='degrees')
    motor.move_to(???, speed=???, unit='degrees')

    print("✓ Returned to zero!")

    # Read position to verify
    position = motor.get_position()
    print(f"Current position: {position} pulses (should be ~0)")
    time.sleep(1)

    # Step 4: Move 1 full rotation
    print("\n--- Step 4: Full Rotation ---")
    print("Moving 1 full rotation (360 degrees) at 50 RPM...")

    # TODO: Move by 1 rotation at speed 50
    # Hint: Use unit='rotations' this time!
    motor.move_by(???, speed=???, unit='rotations')

    print("✓ Completed full rotation!")

    # Read position to verify
    position = motor.get_position()
    print(f"Current position: {position} pulses (should be ~3200)")
    time.sleep(1)

    # Step 5: Return to zero again
    print("\n--- Step 5: Final Return to Zero ---")
    print("Returning to zero position at 40 RPM...")

    # TODO: Move to position 0 at speed 40
    motor.move_to(???, speed=???, unit='degrees')

    print("✓ Back at zero!")

    # Read position to verify
    position = motor.get_position()
    print(f"Final position: {position} pulses (should be ~0)")

    # TODO: Stop motor when done
    print("\nStopping motor...")
    motor.???()

    print()
    print("=" * 60)
    print("Great! You can now move motors to exact positions!")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
