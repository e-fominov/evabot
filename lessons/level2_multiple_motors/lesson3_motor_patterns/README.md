# Lesson 2.3: Motor Patterns

**Level**: 2 - Multiple Motors
**Time**: 60-90 minutes
**Difficulty**: ⭐⭐⭐ Intermediate+

## What You'll Learn

- Create sequential patterns
- Time-based coordination
- Creative motor choreography
- Loop-based control

## Hardware Needed

- 4× Servo42D motors (connected to CAN bus)
- CAN interface (can0)
- Motors: FL=4, FR=2, BL=3, BR=1

## Concepts

- Sequential activation
- Timing and synchronization
- Pattern loops
- Creative programming

## Instructions

1. **Open the template**: Start with `template.py`
2. **Fill in the code**: Follow the comments
3. **Run it**: `python template.py`
4. **Watch the mesmerizing patterns!**

## What Should Happen

1. **Wave Pattern**: Motors start one by one (FL → FR → BR → BL)
2. **Pulse Pattern**: All motors speed up and slow down together
3. **Spin Pattern**: Motors rotate in a spinning pattern
4. **Custom Pattern**: Create your own!

## Success Criteria

- ✅ Wave pattern flows smoothly around
- ✅ Pulse pattern synchronized
- ✅ Spin pattern creates rotation effect
- ✅ Motors coordinate beautifully
- ✅ No crashes or errors

## Pattern Ideas

**Wave** (Sequential):
```
Time  FL  FR  BR  BL
0.0s  ON  -   -   -
0.5s  ON  ON  -   -
1.0s  -   ON  ON  -
1.5s  -   -   ON  ON
2.0s  ON  -   -   ON
```

**Pulse** (All together):
```
All motors: 20 → 40 → 60 → 40 → 20 RPM
Like heartbeat!
```

**Diagonal**:
```
FL+BR: Forward
FR+BL: Backward
Creates X-pattern
```

## Common Mistakes

**Problem**: "Pattern looks choppy"
**Fix**: Reduce time.sleep() delays for smoother transitions

**Problem**: "Motors out of sync"
**Fix**: Ensure equal timing between commands

**Problem**: "One motor behaves differently"
**Fix**: Motors may have slight differences, adjust speeds to compensate

## Try These Challenges

After completing the basic lesson:

1. **Circle Wave**: Make wave go in circles continuously (FL→FR→BR→BL→FL→...)
2. **Acceleration Wave**: Each motor faster than previous
3. **Music Pattern**: Create a "melody" with motor speeds
4. **Random Pattern**: Generate random but interesting patterns
5. **Your Idea**: Be creative! What pattern can you invent?

## Creative Ideas

- **Traffic Light**: All red (slow), yellow (medium), green (fast)
- **Police Siren**: Alternate left/right sides rapidly
- **Spinning Top**: Gradually speed up, then slow down
- **Breathing**: Slow pulse in and out

## Next Lesson

**Level 3**: Mecanum Drive - Use the Robot class to actually drive!

---

**Need help?** Check `solution.py` to see how it's done!
