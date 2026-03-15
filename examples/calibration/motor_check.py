#!/usr/bin/env python3
"""
Motor check: spin each motor one at a time to identify which is which.
NO driving - just single motor pulses so you can see which wheel moves.
"""

import time
from evabot import Robot, MecanumDrive, RPLidarC1


def main():
    print("=" * 50)
    print("Motor Identity Check")
    print("=" * 50)
    print()
    print("Will spin each motor INDIVIDUALLY for 0.5s at low speed.")
    print("Watch which wheel moves and which direction.")
    print()
    print("Expected layout (top view, lidar = front):")
    print("    FRONT (lidar)")
    print("  FL=3       FR=4")
    print("  BL=1       BR=2")
    print("     BACK")
    print()
    print("Starting in 3 seconds...")
    time.sleep(3)

    robot = Robot()
    robot.drive = MecanumDrive(
        fl=3, fr=4, bl=1, br=2,
        wheel_radius=0.03,
        pattern="X",
        acceleration=50,
    )
    robot.lidar = RPLidarC1(max_range=1.0)
    robot.start()
    time.sleep(2)

    # Print initial wall distances for reference
    print()
    print("Wall distances:")
    for name, angle in [('Front', 0), ('Right', 90), ('Back', 180), ('Left', 270)]:
        d, a, q = robot.lidar.check_wall(angle)
        if d and d < 0.5:
            print(f"  {name:6s}: {d*100:.1f} cm")
        else:
            print(f"  {name:6s}: open/far")
    print()

    motors = [
        ("FL (CAN ID 3)", robot.drive.fl),
        ("FR (CAN ID 4)", robot.drive.fr),
        ("BL (CAN ID 1)", robot.drive.bl),
        ("BR (CAN ID 2)", robot.drive.br),
    ]

    try:
        for name, motor in motors:
            print(f"--- Spinning {name} FORWARD at 30 RPM for 0.5s ---")
            print(f"    Watch which wheel moves!")
            motor.run(30, acceleration=50)
            time.sleep(0.5)
            motor.run(0, acceleration=50)
            time.sleep(1.5)

            print(f"--- Spinning {name} REVERSE at 30 RPM for 0.5s ---")
            motor.run(-30, acceleration=50)
            time.sleep(0.5)
            motor.run(0, acceleration=50)
            time.sleep(1.5)
            print()

        print("All motors tested.")
        print()
        print("If a motor spun in the wrong position, the CAN IDs need remapping.")
        print("Current mapping: fl=3, fr=4, bl=1, br=2")

    except KeyboardInterrupt:
        print("\nInterrupted!")

    robot.drive.halt()
    time.sleep(0.3)
    robot.stop()
    print("Done.")


if __name__ == "__main__":
    main()
