# Lesson 1.4: Read Position

**Level**: 1 - Single Motor
**Time**: 45-60 minutes
**Difficulty**: ⭐⭐ Beginner+

## What You'll Learn

- Read encoder position
- Understand encoder pulses
- Calculate distance traveled
- Track motor rotation

## Hardware Needed

- 1× Servo42D motor (connected to CAN bus)
- CAN interface (can0)
- Motor should be CAN ID 1

## Concepts

- Encoder pulses (position feedback)
- Pulses per revolution (3200 for Servo42D)
- Converting pulses to rotations
- Position tracking

## Instructions

1. **Open the template**: Start with `template.py`
2. **Fill in the code**: Follow the comments
3. **Run it**: `python template.py`
4. **Watch the encoder count increase!**

## What Should Happen

1. Program shows starting position (encoder = 0)
2. Motor runs at 30 RPM
3. Program shows position every 0.5 seconds
4. After 5 seconds, motor stops
5. Program shows total distance traveled

## Success Criteria

- ✅ Encoder position increases while motor runs
- ✅ Position values make sense (thousands of pulses)
- ✅ Total rotations calculated correctly
- ✅ No errors in terminal

## Understanding Encoders

**What is an encoder?**
- Counts motor shaft rotation
- Like an odometer for your motor
- Measured in "pulses" or "steps"

**Servo42D specs**:
- 3200 pulses per revolution
- 1 full rotation = 3200 pulses
- 0.5 rotations = 1600 pulses
- 10 rotations = 32000 pulses

**Math**:
```
rotations = pulses / 3200
pulses = rotations × 3200
```

## Common Mistakes

**Problem**: "Position is always 0"
**Fix**: Motor might not be moving. Check motor is running.

**Problem**: "Position is negative"
**Fix**: Normal! Motor can run backward. Negative = reverse direction.

**Problem**: "Huge position values"
**Fix**: Normal! Encoders accumulate. 32000 pulses = only 10 rotations.

## Try These Challenges

After completing the basic lesson:

1. **Exact Rotations**: Make motor spin exactly 5 rotations (5 × 3200 = 16000 pulses)
2. **Distance Tracking**: If wheel radius is 50mm, calculate distance in meters
3. **Reverse Check**: Run backward, verify position decreases
4. **Speed Verification**: Does higher RPM give more pulses per second?

## Math Challenge

If your motor has a wheel with radius = 50mm (0.05m):
- Circumference = 2 × π × r = 2 × 3.14159 × 0.05 = 0.314 meters
- 1 rotation = 0.314 meters traveled
- 3200 pulses = 0.314 meters
- 1 pulse = 0.0000981 meters (0.098mm)

Can you modify the solution to show distance in meters?

## Next Lesson

**Lesson 1.5**: Move Exact Distance - Learn position control with move_by() and move_to()!

---

**Need help?** Check `solution.py` to see how it's done!
