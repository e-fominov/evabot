# Lesson 1.3: Start and Stop

**Level**: 1 - Single Motor
**Time**: 30-60 minutes
**Difficulty**: ⭐ Beginner

## What You'll Learn

- Understand three stop methods: hold(), disable(), stop()
- Feel the difference between locked and free shaft
- Know when to use each method
- Understand motor shaft locking

## Hardware Needed

- 1× Servo42D motor (connected to CAN bus)
- CAN interface (can0)
- Motor should be CAN ID 1

## Concepts

- **hold()** - Stop moving, shaft stays locked
- **disable()** - Release shaft (can turn freely)
- **stop()** - Cleanup method (hold + disable)
- Motor enable state (shaft locks)
- Motor disable state (shaft free)

## Instructions

1. **Open the template**: Start with `template.py`
2. **Fill in the code**: Follow the comments
3. **Run it**: `python template.py`
4. **Try to turn the motor shaft by hand between steps!**

## What Should Happen

1. Motor enables (shaft locks - try to turn it!)
2. Motor runs at 40 RPM
3. Motor uses `hold()` (shaft still locked, but not moving)
4. Wait 2 seconds (shaft still locked)
5. Motor uses `disable()` (shaft free - you can turn it easily!)
6. Motor uses `stop()` for cleanup (holds briefly, then disables)

## Success Criteria

- ✅ Motor shaft locks when enabled
- ✅ You can't turn the shaft by hand when locked
- ✅ `hold()` stops motion but keeps shaft locked
- ✅ `disable()` releases shaft (can turn freely)
- ✅ `stop()` does both (hold + disable)
- ✅ No errors in terminal

## Important Concepts

**Three Ways to Stop:**

1. **motor.hold()** - Stop moving, keep locked
   - Shaft stays hard to turn
   - Motor still uses power
   - Good for: Pausing before next move
   - Example: `motor.run(30); motor.hold()`

2. **motor.disable()** - Release shaft
   - Shaft turns freely
   - Motor saves power
   - Good for: Manual positioning, power saving
   - Example: `motor.disable()`

3. **motor.stop()** - Complete shutdown
   - Holds briefly, then disables
   - Good for: End of program cleanup
   - Example: `motor.stop()`

**Enabled (Locked) State**:
- Motor holds position with force
- Shaft is hard to turn
- Motor ready to move
- Uses power to hold

**Disabled (Free) State**:
- Motor releases shaft
- Shaft turns freely
- Motor won't respond to commands
- Saves power

## Common Mistakes

**Problem**: "Motor doesn't lock when enabled"
**Fix**: Check motor is connected and responding

**Problem**: "Shaft still free after start()"
**Fix**: start() enables the motor - try turning shaft harder, it should resist

**Problem**: "Motor gets warm even when not moving"
**Fix**: Normal - enabled motors use power to hold position. Call stop() when done!

## Try These Challenges

After completing the basic lesson:

1. **Hold Position**: Enable motor, manually try to rotate shaft. Feel the resistance!
2. **Power Save**: Create a program that only enables when needed, disables after
3. **Multiple Cycles**: Enable, run, disable. Repeat 5 times.

## Next Lesson

**Lesson 1.4**: Read Position - Learn to read encoder and measure distance

---

**Need help?** Check `solution.py` to see how it's done!
