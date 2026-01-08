from evabot import Servo42D

for i in range(6):
    m = Servo42D(i)
    m.start()
    m.stop()
