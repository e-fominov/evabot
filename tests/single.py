from evabot import Servo42D
import time

m = Servo42D(3)
m.start()
m.run(100)
time.sleep(30)
m.stop()
