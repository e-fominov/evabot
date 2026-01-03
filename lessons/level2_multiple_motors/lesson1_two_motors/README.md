# Lesson 2.1: Two Motors Together

**Level**: 2 - Multiple Motors
**Time**: 45-60 minutes
**Difficulty**: ⭐⭐ Intermediate

## What You'll Learn

- Control two motors at once
- Synchronized movement
- Independent motor control
- Coordinate multiple motors

## Hardware Needed

- 2× Servo42D motors (connected to CAN bus)
- CAN interface (can0)
- Motors should be CAN ID 1 and 2

## Concepts

- Multiple motor objects
- Same vs different speeds
- Same vs opposite directions
- Motor coordination

## Instructions

1. **Open the template**: Start with `template.py`
2. **Fill in the code**: Follow the comments
3. **Run it**: `python template.py`
4. **Watch both motors work together!**

## What Should Happen

1. Both motors run forward at 30 RPM (synchronized)
2. Both motors run at different speeds (40 and 20 RPM)
3. Motors run in opposite directions (+30 and -30 RPM)
4. Both motors stop

## Success Criteria

- ✅ Both motors start and run
- ✅ Motors can run at same speed
- ✅ Motors can run at different speeds
- ✅ Motors can run in opposite directions
- ✅ Both motors stop cleanly
- ✅ No errors in terminal

## Important Concepts

**Synchronized Motion**:
- Both motors same speed → move together
- Like two wheels on same axle
- Useful for parallel motion

**Independent Motion**:
- Different speeds → different rates
- Opposite directions → opposing motion
- More control, more complex

**CAN Bus**:
- All motors share one bus
- Each has unique ID (1, 2, 3, 4...)
- Can control many motors!

## Common Mistakes

**Problem**: "Second motor doesn't respond"
**Fix**: Check CAN ID is correct (should be 2, not 1)

**Problem**: "Motors fight each other"
**Fix**: If mechanically connected, ensure compatible speeds/directions

**Problem**: "One motor much faster than other"
**Fix**: Motors may have slight variations. Try adjusting speeds to match.

## Try These Challenges

After completing the basic lesson:

1. **Speed Ramp**: Both motors accelerate from 0 to 60 RPM together
2. **Chase**: Motor 1 at 40 RPM, Motor 2 at 20 RPM - one "chases" the other
3. **Wave**: Alternate - Motor 1 runs, stops, then Motor 2 runs, stops
4. **Mirror**: Whatever Motor 1 does, Motor 2 does opposite

## Next Lesson

**Lesson 2.2**: Four Motors - Control all motors for a robot base!

---

**Need help?** Check `solution.py` to see how it's done!
