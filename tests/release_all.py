#!/usr/bin/env python3
"""Test each motor one by one: forward then reverse."""
import time
from evabot.components.motors import Servo42D

SPEED = 40  # RPM
DURATION = 2  # seconds per direction
MOTOR_IDS = {'BR': 1, 'FR': 2, 'BL': 3, 'FL': 4}

motors = {}
for name, can_id in MOTOR_IDS.items():
    m = Servo42D(can_id=can_id)
    m.start()
    motors[name] = m

for name, motor in motors.items():
    print(f"\n--- {name} (CAN {motor.can_id}) ---")

    print(f"  Forward {SPEED} RPM...")
    motor.run(SPEED)
    time.sleep(DURATION)
    motor.run(0)
    time.sleep(0.5)

    print(f"  Reverse {SPEED} RPM...")
    motor.run(-SPEED)
    time.sleep(DURATION)
    motor.run(0)
    time.sleep(0.5)

    print(f"  Done.")

print("\nReleasing all motors...")
for motor in motors.values():
    motor.stop()
print("All motors released.")
