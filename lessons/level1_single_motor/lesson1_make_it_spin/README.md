# Lesson 1.1: Make It Spin

**Level**: 1 - Single Motor
**Time**: 30-60 minutes
**Difficulty**: ⭐ Beginner

## What You'll Learn

- Connect to a motor using Python
- Make the motor spin
- Control the speed
- Stop the motor

## Hardware Needed

- 1× Servo42D motor (connected to CAN bus)
- CAN interface (can0)
- Motor should be CAN ID 1

## Concepts

- Import libraries
- Create objects
- Call methods
- Basic motor control

## Instructions

1. **Open the template**: Start with `template.py`
2. **Fill in the code**: Follow the comments
3. **Run it**: `python template.py`
4. **Watch the motor spin!**

## What Should Happen

1. Motor enables (shaft locks)
2. Motor spins at 30 RPM for 3 seconds
3. Motor stops
4. Program exits safely

## Success Criteria

- ✅ Motor spins when program runs
- ✅ You can see/hear the motor running
- ✅ Motor stops after 3 seconds
- ✅ No errors in terminal

## Common Mistakes

**Problem**: "ImportError: No module named 'evabot'"
**Fix**: Run `pip install -e .` from /home/fm/work/evabot

**Problem**: "Failed to open CAN bus"
**Fix**: Check CAN interface is up: `ip link show can0`

**Problem**: Motor doesn't move
**Fix**: Check CAN ID matches your motor (default is 1)

## Try These Challenges

After completing the basic lesson:

1. **Slower**: Make it spin at 10 RPM instead of 30
2. **Faster**: Try 100 RPM (careful!)
3. **Longer**: Run for 5 seconds instead of 3
4. **Backward**: Can you make it spin the other direction? (Hint: negative speed)

## Next Lesson

**Lesson 1.2**: Control Speed - Learn to change speed while motor is running

---

**Need help?** Check `solution.py` to see how it's done!
