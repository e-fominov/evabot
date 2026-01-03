# Lesson 3.2: Strafe (Sideways)

**Level**: 3 - Mecanum Drive
**Time**: 45-60 minutes
**Difficulty**: ⭐⭐ Intermediate

## What You'll Learn

- Move sideways (strafe) without turning
- Understand mecanum wheel magic
- Combine forward and sideways motion
- Move diagonally

## Hardware Needed

- 4× Servo42D motors with mecanum wheels
- CAN interface (can0)
- Motors: FL=4, FR=2, BL=3, BR=1

## Concepts

- Strafing (sideways movement)
- Mecanum wheel kinematics
- Omnidirectional movement
- Diagonal motion

## What Makes Mecanum Special?

**Normal wheels**: Can only go forward/backward
**Mecanum wheels**: Can move in ANY direction!

```
    Forward
       ↑
       |
Left ← + → Right
       |
       ↓
   Backward
```

The robot can move in ANY of these directions WITHOUT turning!

## Instructions

1. **Open the template**: Start with `template.py`
2. **Fill in the code**: Follow the comments
3. **Run it**: `python template.py`
4. **Watch your robot slide sideways!**

## What Should Happen

1. Robot strafes LEFT at 0.2 m/s
2. Robot stops
3. Robot strafes RIGHT at 0.2 m/s
4. Robot stops
5. Robot moves diagonally (forward + right)

## Success Criteria

- ✅ Robot moves left without turning
- ✅ Robot moves right without turning
- ✅ Robot moves diagonally
- ✅ No forward/backward rotation during strafe
- ✅ Smooth omnidirectional motion

## Important Concepts

**Strafing**:
- Moving sideways
- Orientation stays the same
- Front stays front!
- Like crab walking

**How It Works**:
- Mecanum wheels have angled rollers
- Different wheel patterns create sideways force
- All 4 wheels work together
- Magic of kinematics!

**Diagonal Motion**:
- Combine forward + strafe
- Can move at any angle
- Still no rotation!

## Common Mistakes

**Problem**: "Robot rotates while strafing"
**Fix**: Check wheel pattern setting ('X' or 'diamond'). Default is 'X'.

**Problem**: "Robot moves forward instead of sideways"
**Fix**: Wheels might be installed incorrectly. Check mecanum orientation.

**Problem**: "Diagonal doesn't work"
**Fix**: Make sure you're using `move(vx=..., vy=...)` not separate commands

## Try These Challenges

After completing the basic lesson:

1. **Square Strafe**: Left → Forward → Right → Backward (makes a square!)
2. **Circle Strafe**: Move around a point while facing forward
3. **Figure-8**: Create smooth figure-8 pattern with diagonal motion
4. **Angle Test**: Try different diagonal angles (more forward vs more sideways)

## Math Challenge

If robot moves at:
- Forward: 0.3 m/s
- Right: 0.4 m/s

What's the total speed and angle?
- Speed = √(0.3² + 0.4²) = 0.5 m/s
- Angle = arctan(0.4/0.3) ≈ 53° to the right

## Next Lesson

**Lesson 3.3**: Rotation - Spin in place!

---

**Need help?** Check `solution.py` to see how it's done!
