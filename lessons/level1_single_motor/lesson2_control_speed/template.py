#!/usr/bin/env python3
"""
Lesson 1.2: Control Speed
=========================

Learn to change motor speed while it's running!

Instructions:
1. Import the Servo42D motor class
2. Create and start a motor
3. Change speed multiple times while running
4. Try running in reverse (negative speed)
5. Stop the motor

Fill in the blanks marked with # TODO
"""

import time

# TODO: Import Servo42D from evabot.components.motors
# Hint: from evabot.components.motors import ???


def main():
    print("=" * 60)
    print("Lesson 1.2: Control Speed!")
    print("=" * 60)
    print()

    # TODO: Create a motor with CAN ID 1
    # Hint: motor = Servo42D(???)


    # TODO: Start the motor
    # Hint: motor.???()


    print("Starting slow: 20 RPM")
    # TODO: Run at 20 RPM
    # Hint: motor.run(???)

    time.sleep(2)

    print("Speeding up: 60 RPM")
    # TODO: Change speed to 60 RPM (just call run again!)
    # Hint: motor.run(???)

    time.sleep(2)

    print("Slowing down: 30 RPM")
    # TODO: Change speed to 30 RPM


    time.sleep(2)

    print("Reversing: -40 RPM")
    # TODO: Run backward at -40 RPM
    # Hint: Use negative number


    time.sleep(2)

    print("Stopping motor...")
    # TODO: Stop the motor


    print()
    print("=" * 60)
    print("Great! You controlled the speed in real-time!")
    print("=" * 60)


if __name__ == "__main__":
    main()
