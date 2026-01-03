# Lesson 3.1: Forward and Backward

**Level**: 3 - Mecanum Drive
**Time**: 45-60 minutes
**Difficulty**: ⭐⭐ Intermediate

## What You'll Learn

- Use the Robot class
- Create a MecanumDrive
- Drive forward and backward
- Understand velocity (m/s)

## Hardware Needed

- 4× Servo42D motors (connected to CAN bus)
- Mecanum wheels attached to motors
- CAN interface (can0)
- Motors: FL=4, FR=2, BL=3, BR=1

## Concepts

- Robot abstraction
- Mecanum drive system
- Linear velocity (meters per second)
- Coordinated 4-wheel control

## Instructions

1. **Open the template**: Start with `template.py`
2. **Fill in the code**: Follow the comments
3. **Run it**: `python template.py`
4. **Watch your robot drive!**

## What Should Happen

1. Robot initializes with 4 motors
2. Robot drives forward at 0.2 m/s for 3 seconds
3. Robot stops briefly
4. Robot drives backward at 0.2 m/s for 3 seconds
5. Robot stops

## Success Criteria

- ✅ Robot moves forward in a straight line
- ✅ Robot stops between movements
- ✅ Robot moves backward in a straight line
- ✅ All 4 wheels work together
- ✅ No errors in terminal

## Important Concepts

**Robot Class**:
- High-level control
- Manages components (drive, sensors, etc.)
- Cleaner code than individual motors

**MecanumDrive**:
- Controls 4 motors as one system
- Handles wheel coordination
- Uses velocity (m/s) not RPM

**Velocity**:
- Speed in meters per second (m/s)
- 0.2 m/s = 20 cm/s (slow, safe speed)
- 0.5 m/s = 50 cm/s (medium speed)
- Negative = backward

## Common Mistakes

**Problem**: "Robot doesn't move straight"
**Fix**: Check wheel alignment. Motors may need slight speed adjustment.

**Problem**: "ImportError: cannot import name 'Robot'"
**Fix**: Run `pip install -e .` from /home/fm/work/evabot

**Problem**: "Robot moves but wrong direction"
**Fix**: Check motor IDs match physical layout (FL=4, FR=2, BL=3, BR=1)

**Problem**: "Motors fight each other"
**Fix**: Ensure mecanum wheels installed correctly (check pattern)

## Try These Challenges

After completing the basic lesson:

1. **Speed Test**: Try different speeds (0.1, 0.3, 0.5 m/s)
2. **Longer Distance**: Calculate time needed to travel 1 meter at 0.2 m/s
3. **Back and Forth**: Go forward, backward, forward, backward (4 times)
4. **Acceleration**: Gradually increase from 0.1 to 0.5 m/s

## Math Challenge

If robot moves at 0.2 m/s:
- In 1 second: 0.2 meters (20 cm)
- In 3 seconds: 0.6 meters (60 cm)
- In 5 seconds: 1.0 meters (100 cm)

How long to travel 2 meters? (Answer: 10 seconds)

## Next Lesson

**Lesson 3.2**: Strafe (Sideways) - Move left and right without turning!

---

**Need help?** Check `solution.py` to see how it's done!
