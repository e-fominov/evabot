# Lesson 2.2: Four Motors

**Level**: 2 - Multiple Motors
**Time**: 60 minutes
**Difficulty**: ⭐⭐ Intermediate

## What You'll Learn

- Control four motors simultaneously
- Create motor groups (left, right, all)
- Coordinate complex movements
- Prepare for mecanum drive

## Hardware Needed

- 4× Servo42D motors (connected to CAN bus)
- CAN interface (can0)
- Motors should be CAN ID 1, 2, 3, 4

## Motor Layout

Think of motors as robot base corners:
```
    FRONT
  FL    FR     FL = Front Left  (ID 4)
              FR = Front Right (ID 2)
  BL    BR     BL = Back Left   (ID 3)
    BACK       BR = Back Right  (ID 1)
```

## Concepts

- Managing multiple motors
- Left/right side coordination
- All motors together
- Motor groups

## Instructions

1. **Open the template**: Start with `template.py`
2. **Fill in the code**: Follow the comments
3. **Run it**: `python template.py`
4. **Watch all four motors coordinate!**

## What Should Happen

1. All 4 motors run forward at 30 RPM
2. Left side (FL, BL) and right side (FR, BR) run at different speeds
3. Front (FL, FR) and back (BL, BR) run opposite directions
4. All motors stop together

## Success Criteria

- ✅ All 4 motors start successfully
- ✅ Can control all motors together
- ✅ Can control left/right sides separately
- ✅ Can control front/back separately
- ✅ All motors stop cleanly
- ✅ No errors in terminal

## Important Concepts

**Motor Groups**:
- Left side: FL + BL
- Right side: FR + BR
- Front: FL + FR
- Back: BL + BR
- All: FL + FR + BL + BR

**Why Groups?**:
- Easier to coordinate
- Fewer lines of code
- Clearer logic
- Prepares for robot driving

## Common Mistakes

**Problem**: "Wrong motor responding"
**Fix**: Double-check CAN IDs match physical motors

**Problem**: "One motor doesn't start"
**Fix**: Check all 4 CAN connections. Use `ip -s link show can0` to check bus.

**Problem**: "Motors respond slowly"
**Fix**: Normal with 4 motors. CAN bus handles commands quickly but sequentially.

## Try These Challenges

After completing the basic lesson:

1. **Wave Pattern**: Start motors one by one (FL → FR → BR → BL)
2. **Diagonal**: FL+BR forward, FR+BL backward
3. **Speed Test**: All motors 10→20→30→40→50 RPM in steps
4. **Random Chaos**: Each motor different random speed!

## Next Lesson

**Lesson 2.3**: Motor Patterns - Create interesting motion patterns!

---

**Need help?** Check `solution.py` to see how it's done!
