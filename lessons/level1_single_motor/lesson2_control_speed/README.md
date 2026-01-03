# Lesson 1.2: Control Speed

**Level**: 1 - Single Motor
**Time**: 30-60 minutes
**Difficulty**: ⭐ Beginner

## What You'll Learn

- Change motor speed while it's running
- Run motors in reverse (negative speed)
- Understand RPM (rotations per minute)
- Smooth speed transitions

## Hardware Needed

- 1× Servo42D motor (connected to CAN bus)
- CAN interface (can0)
- Motor should be CAN ID 1

## Concepts

- Dynamic speed control
- Positive vs negative RPM
- Motor direction
- Real-time speed changes

## Instructions

1. **Open the template**: Start with `template.py`
2. **Fill in the code**: Follow the comments
3. **Run it**: `python template.py`
4. **Watch the motor change speeds!**

## What Should Happen

1. Motor starts at 20 RPM (slow)
2. Speeds up to 60 RPM (faster)
3. Slows down to 30 RPM (medium)
4. Reverses to -40 RPM (backward)
5. Stops

## Success Criteria

- ✅ Motor changes speed smoothly
- ✅ You can hear the speed changes
- ✅ Motor runs backward (reverses direction)
- ✅ No errors in terminal

## Common Mistakes

**Problem**: Motor jerks or vibrates when changing speed
**Fix**: Normal - motor adjusts to new speed. Try slower transitions.

**Problem**: Motor doesn't reverse
**Fix**: Check that you're using negative speed (e.g., -40)

**Problem**: Motor seems to lag behind
**Fix**: Normal - motor acceleration takes time. This is controlled by acceleration parameter.

## Try These Challenges

After completing the basic lesson:

1. **Speed Ramp**: Gradually increase from 10 to 100 RPM in steps of 10
2. **Oscillate**: Go back and forth between 50 and -50 RPM
3. **Fast Reverse**: How quickly can you reverse from +100 to -100?
4. **Find Limits**: What's the maximum speed your motor can handle?

## Next Lesson

**Lesson 1.3**: Start and Stop - Learn to enable/disable motor and emergency stop

---

**Need help?** Check `solution.py` to see how it's done!
