# Lesson 1.5: Move Exact Distance

**Level**: 1 - Single Motor
**Time**: 45-60 minutes
**Difficulty**: ⭐⭐ Beginner+

## What You'll Learn

- Set zero position (home position)
- Move by exact degrees or rotations
- Move to absolute positions
- Understand position control vs speed control

## Hardware Needed

- 1× Servo42D motor (connected to CAN bus)
- CAN interface (can0)
- Motor should be CAN ID 1
- Free space for motor to spin

## Concepts

- **Position control** - Move exact distance, then stop
- **Speed control** - Run continuously at set speed
- **Zero position** - Reference point for absolute moves
- **Relative motion** - Move from current position
- **Absolute motion** - Move to target position

## Instructions

1. **Open the template**: Start with `template.py`
2. **Fill in the code**: Follow the comments
3. **Run it**: `python template.py`
4. **Watch the motor move precisely!**

## What Should Happen

1. Motor sets current position as zero
2. Motor moves exactly 90 degrees forward
3. Waits 1 second
4. Motor returns to zero position
5. Waits 1 second
6. Motor moves 1 full rotation forward
7. Motor returns to zero again

## Success Criteria

- ✅ Motor moves exactly 90 degrees (quarter turn)
- ✅ Motor returns to zero position accurately
- ✅ Motor completes full rotation (360 degrees)
- ✅ Movements are smooth (not jerky)
- ✅ No errors in terminal

## Important Concepts

**Position Control Functions:**

1. **motor.zero_position()** - Set current as zero
   - Sets reference point for absolute moves
   - Use this at startup or home position
   - Example: `motor.zero_position()`

2. **motor.move_by(distance, speed, unit)** - Relative move
   - Move by distance from current position
   - Units: 'degrees' or 'rotations'
   - Blocking: waits until complete
   - Example: `motor.move_by(90, 40, 'degrees')`

3. **motor.move_to(position, speed, unit)** - Absolute move
   - Move to exact position from zero
   - Returns to previous positions accurately
   - Example: `motor.move_to(0, 30, 'degrees')`

**Parameters:**
- `distance/position`: How far to move (degrees or rotations)
- `speed`: Motor speed in RPM (0-3000)
- `unit`: 'degrees' or 'rotations'
- `acceleration`: How fast to speed up (default: 2)

**Units:**
- **Degrees**: 0-360 for one rotation
  - 90 degrees = quarter turn
  - 180 degrees = half turn
  - 360 degrees = full rotation
- **Rotations**: Whole rotations
  - 1.0 = one full turn
  - 0.5 = half turn
  - 2.5 = two and a half turns

## Common Mistakes

**Problem**: "Motor doesn't move"
**Fix**: Make sure you called `motor.start()` first!

**Problem**: "Motor moves wrong direction"
**Fix**: Use negative values to reverse: `motor.move_by(-90, 40, 'degrees')`

**Problem**: "Motor doesn't return to zero exactly"
**Fix**: Normal! Small error (±5 degrees) is okay. Use lower speeds for better accuracy.

**Problem**: "Program hangs after move command"
**Fix**: Motor is moving - wait for it to complete! Position moves are blocking.

## Speed vs Position Control

**Speed Control (run)**:
- Runs continuously until stopped
- Good for: Continuous motion, unknown distance
- Example: `motor.run(30)`

**Position Control (move_by/move_to)**:
- Moves exact distance, then stops
- Good for: Precise movements, returning to positions
- Example: `motor.move_by(90, 40, 'degrees')`

## Try These Challenges

After completing the basic lesson:

1. **Square Pattern**: Move 90° four times with pauses
2. **Pendulum**: Swing between -45° and +45°
3. **Spiral**: Gradually increase rotation amount
4. **Precision Test**: Move to 0°, 90°, 180°, 270°, check accuracy
5. **Custom Units**: Create function to move in wheel rotations

## Math Challenge

If your motor has a wheel with radius = 50mm:
- 1 rotation = 2πr = 2 × 3.14159 × 50 = 314.2mm
- To move 1 meter, need: 1000mm / 314.2mm = 3.18 rotations

Can you make the motor move exactly 1 meter?

## Next Lesson

**Level 2**: Multiple Motors - Control several motors together!

---

**Need help?** Check `solution.py` to see how it's done!
