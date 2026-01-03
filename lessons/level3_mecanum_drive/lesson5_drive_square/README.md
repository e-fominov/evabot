# Lesson 3.5: Drive a Square

**Level**: 3 - Mecanum Drive
**Time**: 60-90 minutes
**Difficulty**: ⭐⭐⭐ Advanced

## What You'll Learn

- Execute precise timed movements
- Calculate distance from velocity and time
- Create geometric patterns
- Chain multiple movements together

## Hardware Needed

- 4× Servo42D motors with mecanum wheels
- CAN interface (can0)
- Motors: FL=4, FR=2, BL=3, BR=1
- Open floor space (at least 2m × 2m)

## Concepts

- Distance = velocity × time
- Geometric path planning
- Sequential movements
- Precision control

## Goal

Make your robot drive in a perfect 1m × 1m square using:
- Forward movement
- Strafe movement (sideways)
- NO rotation (robot always faces same direction!)

This is the magic of mecanum wheels!

## Instructions

1. **Open the template**: Start with `template.py`
2. **Fill in the code**: Follow the comments
3. **Run it**: `python template.py`
4. **Measure the square on the floor!**

## What Should Happen

```
    START
    ↓
1m  →→→→→ (forward)
    ↓
    ↓ (strafe left)
    ↓
    ←←←←← (backward)
    ↓
    ↑ (strafe right)
    ↑
    END (back at start!)
```

All without rotating! Robot faces forward the whole time.

## Success Criteria

- ✅ Robot completes square path
- ✅ Robot returns to start position (within ~10cm)
- ✅ Robot never rotates (always faces same direction)
- ✅ Each side approximately 1 meter
- ✅ Smooth transitions between sides

## Important Concepts

**Distance Calculation**:
```
distance = velocity × time

Example:
velocity = 0.2 m/s
time = 5 seconds
distance = 0.2 × 5 = 1.0 meter
```

**Square Path**:
1. Forward 1m
2. Strafe left 1m
3. Backward 1m
4. Strafe right 1m

**Precision Factors**:
- Wheel slip on floor
- Acceleration/deceleration
- Odometry drift
- Surface friction

## Common Mistakes

**Problem**: "Square not closing (doesn't return to start)"
**Fix**: Normal! Odometry drift and wheel slip. Try adjusting times.

**Problem**: "Sides not equal length"
**Fix**: Different directions may have different friction. Adjust individual times.

**Problem**: "Robot rotates slightly"
**Fix**: Wheels not perfectly aligned. Small rotation is normal.

## Try These Challenges

After completing the basic lesson:

1. **Bigger Square**: 2m × 2m square
2. **Rectangle**: 1m × 2m rectangle
3. **Triangle**: Use diagonal movements for triangle
4. **Octagon**: 8-sided shape using angles
5. **Spiral Square**: Square that gets bigger each loop

## Advanced: Calibration

If your square doesn't close:
1. Measure actual distance traveled
2. Calculate correction factor
3. Adjust time or velocity

Example:
- Expected: 1.0m in 5s at 0.2 m/s
- Actual: 0.9m traveled
- Factor: 1.0 / 0.9 = 1.11
- New time: 5 × 1.11 = 5.55 seconds

## Math Exercise

**Problem**: Create a 0.5m × 1.5m rectangle at 0.3 m/s

Solution:
- Short side: time = 0.5 / 0.3 = 1.67 seconds
- Long side: time = 1.5 / 0.3 = 5.0 seconds

Path:
1. Forward 5.0s (1.5m)
2. Strafe left 1.67s (0.5m)
3. Backward 5.0s (1.5m)
4. Strafe right 1.67s (0.5m)

## Next Lesson

**Lesson 3.6**: Track Position - Use odometry to measure where you are!

---

**Need help?** Check `solution.py` to see how it's done!
