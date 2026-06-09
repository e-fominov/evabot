from evabot import Servo42D
import time

MOTORS = [1, 2, 3, 4]
for i in MOTORS:
    motor = Servo42D(i)
    motor.start()  # Wake it up
    motor.run(30)  # Spin at 30 RPM
    time.sleep(3)  # Wait 3 seconds
    motor.stop()  # Stop and unlock
