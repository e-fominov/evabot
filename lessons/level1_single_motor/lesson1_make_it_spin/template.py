#!/usr/bin/env python3
"""
Lesson 1.1: Make It Spin
========================

Your first robot program! Make a motor spin.

Instructions:
1. Import the Servo42D motor class
2. Create a motor object with CAN ID 1
3. Start the motor
4. Make it run at 30 RPM
5. Wait 3 seconds
6. Stop the motor

Fill in the blanks marked with # TODO
"""

import time

# TODO: Import Servo42D from evabot.components.motors
# Hint: from evabot.components.motors import ???


def main():
    print("=" * 60)
    print("Lesson 1.1: Make It Spin!")
    print("=" * 60)
    print()

    # TODO: Create a motor with CAN ID 1
    # Hint: motor = Servo42D(???)


    # TODO: Start the motor (connects to CAN bus)
    # Hint: motor.???()


    print("Starting motor at 30 RPM...")

    # TODO: Make the motor run at 30 RPM
    # Hint: motor.run(???)


    print("Motor is spinning!")
    print("Waiting 3 seconds...")

    # TODO: Wait for 3 seconds
    # Hint: time.sleep(???)


    print("Stopping motor...")

    # TODO: Stop the motor
    # Hint: motor.???()


    print()
    print("=" * 60)
    print("Great job! The motor spun and stopped safely.")
    print("=" * 60)


if __name__ == "__main__":
    main()
