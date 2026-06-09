from evabot import Robot, MecanumDrive
import time

robot = Robot()
robot.drive = MecanumDrive(fl=3, fr=4, bl=1, br=2, pattern="X")
robot.start()
robot.drive.zero_position()
robot.drive.move_by(dx=0.0, dy=0.0, dtheta=0.5, speed=0.05, timeout=10)
time.sleep(0.5)
robot.stop()
