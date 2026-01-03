# Integration Tests

Integration tests that verify **real hardware communication** with the EvaBot robotics library.

Unlike unit tests, these tests require actual hardware and verify:
- CAN bus communication
- Motor responses
- Encoder updates
- State changes
- Safety features

## Requirements

### Hardware
- Servo42D motors connected to CAN bus
- CAN interface configured (`can0`)
- Motors free to move (not mechanically constrained)

### Software
- EvaBot library installed (`pip install -e .`)
- CAN bus up and configured
- Python 3.7+

## Setup CAN Bus

Before running tests:

```bash
# Check if CAN interface exists
ip link show can0

# If not up, configure it:
sudo ip link set can0 type can bitrate 500000
sudo ip link set can0 up

# Verify status
ip -s link show can0
```

## Running Tests

### Single Motor Test

Tests basic motor functionality with one Servo42D motor at CAN ID 1:

```bash
cd /home/fm/work/evabot
python tests/integration/test_single_motor.py
```

**What it tests:**
1. Motor initialization and CAN communication
2. Encoder updates when running forward
3. Encoder updates when running backward
4. Speed control (different RPMs)
5. Motor stop releases shaft
6. Runtime timeout safety feature

**Expected output:**
```
============================================================
INTEGRATION TEST: Single Motor (Servo42D)
============================================================

Ready to start tests? (y/n): y

TEST: Motor Initialization and CAN Communication
------------------------------------------------------------
✓ PASS: Motor object created
✓ PASS: Motor started (CAN communication established)
✓ PASS: Encoder read successful: 1234 pulses
...

TEST SUMMARY
============================================================
  PASS  Motor Initialization
  PASS  Encoder Updates (Forward)
  PASS  Encoder Updates (Reverse)
  PASS  Speed Control
  PASS  Stop Releases Shaft
  PASS  Runtime Timeout

Result: 6/6 tests passed
✓ ALL TESTS PASSED
```

## Test Details

### Test 1: Motor Initialization
- Creates motor object
- Starts motor (enables CAN communication)
- Reads encoder (verifies communication working)
- Checks encoder value is reasonable

### Test 2: Encoder Updates (Forward)
- Runs motor forward at 40 RPM for 3 seconds
- Samples encoder every 0.5 seconds
- Verifies encoder increases (forward direction)
- Checks encoder change is significant
- Verifies monotonic increase (consistent motion)
- Compares actual vs expected pulse count

### Test 3: Encoder Updates (Reverse)
- Runs motor backward at -40 RPM for 3 seconds
- Samples encoder every 0.5 seconds
- Verifies encoder decreases (reverse direction)
- Checks encoder change is significant
- Verifies monotonic decrease

### Test 4: Speed Control
- Tests 3 different speeds: 20, 40, 60 RPM
- Verifies higher speeds produce more encoder change
- Checks proportionality (60 RPM ≈ 3× of 20 RPM)

### Test 5: Stop Releases Shaft
- Starts motor (shaft locks)
- User manually verifies shaft is hard to turn
- Stops motor (shaft releases)
- User manually verifies shaft is free to turn

### Test 6: Runtime Timeout
- Runs motor with 1000ms timeout
- Monitors encoder for 3 seconds
- Verifies motor stops after ~1 second
- Checks position stabilizes after timeout

## Troubleshooting

### CAN Bus Errors

**Problem**: `Failed to open CAN bus`
```bash
# Check interface is up
ip link show can0

# Restart interface
sudo ip link set can0 down
sudo ip link set can0 type can bitrate 500000
sudo ip link set can0 up
```

### Motor Not Responding

**Problem**: `Encoder read failed` or `No response from motor`

- Check motor is powered
- Verify CAN ID is correct (default: 1)
- Check CAN wiring (CANH, CANL, GND)
- Verify termination resistors (120Ω at each end)

### Encoder Not Changing

**Problem**: Encoder value doesn't change when motor runs

- Motor might be mechanically stuck
- Check motor is free to spin
- Verify motor shaft can rotate
- Check motor is actually receiving power

### Test Failures

**Problem**: Tests fail due to encoder drift or timing

- Normal - some variation expected
- Tests have tolerances built in
- Retry test to confirm consistent failure
- Check for mechanical issues (friction, load)

## Adding New Tests

When adding integration tests:

1. **Test real hardware behavior** - Not just API calls
2. **Verify state changes** - Encoder updates, motor responses
3. **Check timing** - Motion should happen in expected timeframes
4. **Test safety features** - Timeouts, emergency stops
5. **Make tests observable** - Print intermediate values
6. **Use tolerances** - Hardware isn't perfect, allow reasonable variance

Example test structure:

```python
def test_my_feature():
    """Test description"""
    print_test("Feature Name")

    try:
        motor = Servo42D(can_id=1)
        motor.start()

        # Get initial state
        initial_state = motor.get_state()

        # Perform action
        motor.do_something()

        # Verify state changed
        new_state = motor.get_state()

        success = assert_true(
            new_state != initial_state,
            "State changed after action",
            "State didn't change"
        )

        motor.stop()
        return success

    except Exception as e:
        print_fail(f"Test failed: {e}")
        return False
```

## Future Tests

Planned integration tests:

- **Multiple Motors**: Test 4 motors running together
- **Mecanum Drive**: Test omnidirectional movement
- **Odometry**: Verify position tracking accuracy
- **CAN Bus Load**: Test with many motors on same bus
- **Error Recovery**: Test handling of CAN errors, motor faults
- **Safety Systems**: Test emergency stop, timeout edge cases

## CI/CD

These tests require real hardware and **cannot run in CI/CD**. They must be run manually on actual robot hardware.

For CI/CD, use unit tests that mock hardware interfaces.
