#!/usr/bin/env python3
"""
Lesson 1.5: Move Exact Distance - SOLUTION
===========================================

This is the complete working solution.
Try to complete template.py yourself first!
"""

import time
from evabot.components.motors import Servo42D


def main():
    print("=" * 60)
    print("Lesson 1.5: Move Exact Distance!")
    print("=" * 60)
    print()

    # Create a motor with CAN ID 1
    motor = Servo42D(can_id=1)

    # Start the motor
    print("Starting motor...")
    motor.start()

    # Step 1: Set current position as zero
    print("\n--- Step 1: Setting Zero Position ---")
    print("Setting current position as zero (home position)...")
    motor.zero_position()
    print("✓ Zero position set!")
    time.sleep(1)

    # Step 2: Move 90 degrees forward (quarter turn)
    print("\n--- Step 2: Move 90 Degrees Forward ---")
    print("Moving 90 degrees (quarter turn) at 40 RPM...")
    motor.move_by(90, speed=40, unit='degrees')
    print("✓ Moved 90 degrees!")

    # Read position to verify
    position = motor.get_position()
    print(f"Current position: {position} pulses (should be ~800)")
    time.sleep(1)

    # Step 3: Return to zero
    print("\n--- Step 3: Return to Zero ---")
    print("Moving back to zero position at 30 RPM...")
    motor.move_to(0, speed=30, unit='degrees')
    print("✓ Returned to zero!")

    # Read position to verify
    position = motor.get_position()
    print(f"Current position: {position} pulses (should be ~0)")
    time.sleep(1)

    # Step 4: Move 1 full rotation
    print("\n--- Step 4: Full Rotation ---")
    print("Moving 1 full rotation (360 degrees) at 50 RPM...")
    motor.move_by(1, speed=50, unit='rotations')
    print("✓ Completed full rotation!")

    # Read position to verify
    position = motor.get_position()
    print(f"Current position: {position} pulses (should be ~3200)")
    time.sleep(1)

    # Step 5: Return to zero again
    print("\n--- Step 5: Final Return to Zero ---")
    print("Returning to zero position at 40 RPM...")
    motor.move_to(0, speed=40, unit='degrees')
    print("✓ Back at zero!")

    # Read position to verify
    position = motor.get_position()
    print(f"Final position: {position} pulses (should be ~0)")

    # Stop motor
    print("\nStopping motor...")
    motor.stop()

    print()
    print("=" * 60)
    print("Great! You can now move motors to exact positions!")
    print("=" * 60)
    print()
    print("Key Takeaways:")
    print("  • zero_position() sets reference point")
    print("  • move_by() moves relative to current position")
    print("  • move_to() moves to absolute position from zero")
    print("  • Use 'degrees' or 'rotations' as units")
    print("  • Position control is perfect for precise movements!")
    print()


if __name__ == "__main__":
    main()
