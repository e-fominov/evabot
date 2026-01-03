# Lesson 3.4: Combine Movements

**Level**: 3 - Mecanum Drive
**Time**: 60 minutes
**Difficulty**: ⭐⭐⭐ Advanced

## What You'll Learn

- Combine all 3 motion types simultaneously
- Create complex omnidirectional paths
- Understand true omnidirectional control
- Coordinate vx, vy, and vtheta together

## Hardware Needed

- 4× Servo42D motors with mecanum wheels
- CAN interface (can0)
- Motors: FL=4, FR=2, BL=3, BR=1

## Concepts

- Omnidirectional motion
- 3-DOF control (3 degrees of freedom)
- Vector addition
- Complex path planning

## What is 3-DOF Control?

Your robot can control 3 things at once:
1. **vx**: Forward/backward velocity (m/s)
2. **vy**: Left/right velocity (m/s)
3. **vtheta**: Rotation velocity (rad/s)

ALL THREE can be non-zero simultaneously!

Example: Move forward + strafe right + rotate CCW = complex diagonal curve

## Instructions

1. **Open the template**: Start with `template.py`
2. **Fill in the code**: Follow the comments
3. **Run it**: `python template.py`
4. **Watch complex omnidirectional motion!**

## What Should Happen

1. Forward + Strafe left (diagonal)
2. Forward + Rotate CCW (arc)
3. Strafe right + Rotate CW (sideways arc)
4. Forward + Strafe + Rotate (ALL THREE!)

## Success Criteria

- ✅ Robot moves diagonally smoothly
- ✅ Robot creates forward arc
- ✅ Robot creates sideways arc
- ✅ Robot combines all 3 motions
- ✅ Movement is controlled and predictable

## Important Concepts

**Omnidirectional**:
- Can move in ANY direction
- Can face ANY direction while moving
- Like ice skating or hovercrafts!
- Unique to mecanum/omni wheels

**Motion Vectors**:
```
vx = 0.2, vy = 0.1, vtheta = 0.3
↓
Robot moves:
- Forward at 0.2 m/s
- Left at 0.1 m/s
- Rotating CCW at 0.3 rad/s
ALL AT THE SAME TIME!
```

**Vector Magnitude**:
- Linear speed = √(vx² + vy²)
- Example: vx=0.3, vy=0.4 → speed = 0.5 m/s

## Common Mistakes

**Problem**: "Motion seems chaotic"
**Fix**: Start with small velocities. Complex motion needs practice!

**Problem**: "Robot doesn't follow expected path"
**Fix**: Odometry drift, surface friction. This is normal - later lessons address this.

**Problem**: "Wheels slip"
**Fix**: Reduce velocity. Complex motion requires good traction.

## Try These Challenges

After completing the basic lesson:

1. **Circle**: Move in perfect circle while facing forward
2. **Spiral**: Combine forward arc that curves inward
3. **Figure-8**: Create figure-8 pattern with combined motion
4. **Dance**: Create a "dance" routine with changing velocities!

## Advanced Challenge: Perfect Circle

To drive in a circle while facing forward:
- Radius r = 1 meter
- Linear speed v = 0.3 m/s
- Angular velocity ω = v/r = 0.3 rad/s

```python
# Circle to the left
robot.drive.move(vx=0.3, vy=0, vtheta=0.3)
# Robot faces forward, moves in circle!
```

## Math Exercise

**Problem**: Move diagonally forward-right at 0.2 m/s, 45° angle
- 45° means vx = vy
- Speed = √(vx² + vy²) = 0.2
- √(vx² + vx²) = 0.2
- vx = vy = 0.141 m/s

```python
robot.drive.move(vx=0.141, vy=-0.141)  # vy negative = right
```

## Next Lesson

**Lesson 3.5**: Drive a Square - Precise motion control!

---

**Need help?** Check `solution.py` to see how it's done!
