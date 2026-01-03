# Lesson 3.3: Rotation

**Level**: 3 - Mecanum Drive
**Time**: 45-60 minutes
**Difficulty**: ⭐⭐ Intermediate

## What You'll Learn

- Rotate robot in place
- Understand angular velocity (rad/s)
- Clockwise vs counter-clockwise
- Arc movement (rotation + linear motion)

## Hardware Needed

- 4× Servo42D motors with mecanum wheels
- CAN interface (can0)
- Motors: FL=4, FR=2, BL=3, BR=1

## Concepts

- In-place rotation
- Angular velocity (radians per second)
- CCW (counter-clockwise) vs CW (clockwise)
- Combined rotation and translation

## Instructions

1. **Open the template**: Start with `template.py`
2. **Fill in the code**: Follow the comments
3. **Run it**: `python template.py`
4. **Watch your robot spin!**

## What Should Happen

1. Robot rotates counter-clockwise (CCW) at 0.5 rad/s
2. Robot stops
3. Robot rotates clockwise (CW) at 0.5 rad/s
4. Robot stops
5. Robot moves in an arc (forward while rotating)

## Success Criteria

- ✅ Robot spins in place (no translation)
- ✅ Robot rotates both directions
- ✅ Robot can combine rotation with movement
- ✅ Smooth arc motion
- ✅ No errors

## Important Concepts

**Angular Velocity**:
- Measured in radians per second (rad/s)
- 2π radians = 360° = 1 full rotation
- π radians = 180° = half rotation
- 0.5 rad/s ≈ 28°/second (safe speed)

**Conversions**:
```
1 rad/s = 57.3°/s
0.5 rad/s ≈ 29°/s
π rad/s = 180°/s (very fast!)
2π rad/s = 360°/s (one rotation per second!)
```

**Directions**:
- Positive = Counter-Clockwise (CCW) - left turn
- Negative = Clockwise (CW) - right turn
- Same as math convention!

**Arc Motion**:
- Combine linear + rotational
- Like a car turning while driving
- Very smooth and natural

## Common Mistakes

**Problem**: "Robot translates while rotating"
**Fix**: Normal if wheels slightly misaligned. Should be minimal.

**Problem**: "Robot rotates very slowly"
**Fix**: Try higher angular velocity (0.8 or 1.0 rad/s)

**Problem**: "Robot vibrates during rotation"
**Fix**: Surface friction or wheel issues. Try smoother surface.

## Try These Challenges

After completing the basic lesson:

1. **Full Turn**: Rotate exactly 360° (2π radians). How long at 0.5 rad/s?
2. **Half Turn**: Rotate exactly 180° (π radians)
3. **Spiral**: Move forward while slowly rotating (makes a spiral!)
4. **Spin Fast**: How fast can your robot spin safely?

## Math Challenges

**Challenge 1**: At 0.5 rad/s, how long for 360° rotation?
- 360° = 2π radians = 6.28 radians
- Time = 6.28 / 0.5 = 12.56 seconds

**Challenge 2**: To rotate 90° in 2 seconds, what angular velocity?
- 90° = π/2 radians = 1.57 radians
- Velocity = 1.57 / 2 = 0.785 rad/s

**Challenge 3**: Arc with radius 1 meter at 0.3 m/s forward?
- Angular velocity = linear velocity / radius
- ω = 0.3 / 1.0 = 0.3 rad/s

## Next Lesson

**Lesson 3.4**: Combine Movements - Do everything at once!

---

**Need help?** Check `solution.py` to see how it's done!
