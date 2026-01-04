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
- RPLidar C1 connected to `/dev/ttyUSB0` (for lidar tests)

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

### RPLidar C1 Test

Tests lidar scanning and coordinate system alignment:

```bash
cd /home/fm/work/evabot
python tests/integration/test_lidar.py
```

**What it tests:**
1. Lidar initialization and connection
2. 360° scan data acquisition
3. Directional readings (front, right, back, left)
4. Coordinate system (CW rotation: 0°=front, 90°=right, 180°=back, 270°=left)
5. Angular range queries
6. Obstacle detection logic
7. Real-time continuous scanning

**Expected output:**
```
============================================================
RPLidar C1 Standalone Test
============================================================

Creating RPLidarC1...
Starting lidar...

Basic Distance Readings:
  Coordinate System: CW rotation (0°=front, 90°=right, 180°=back, 270°=left)

  Front (0°):   0.65m
  Right (90°):  0.53m
  Back (180°):  0.59m
  Left (270°):  0.84m

Full Scan Statistics:
  Total points: 282
  Min distance: 0.30m
  Max distance: 4.58m
  Coverage:     78.3%

✓ Test Complete!
```

### Four Motors Test

Tests multiple motors coordination (coming soon):

```bash
cd /home/fm/work/evabot
python tests/integration/test_four_motors.py
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

### Lidar Not Responding

**Problem**: `Failed to connect to lidar` or `No such file or directory: /dev/ttyUSB0`

- Check lidar is connected via USB
- Verify USB device appears:
  ```bash
  ls -l /dev/ttyUSB*
  ```
- Check permissions:
  ```bash
  sudo chmod 666 /dev/ttyUSB0
  # Or add user to dialout group:
  sudo usermod -a -G dialout $USER
  # Then logout and login
  ```
- Verify baud rate is 460800 (RPLidar C1)

**Problem**: "Incorrect descriptor starting bytes"

- Already fixed with automatic buffer clearing
- If still occurs, manually cleanup:
  ```python
  from evabot.hardware import LidarDevice
  LidarDevice.cleanup_all()
  ```

**Problem**: No scan data or sparse coverage

- Wait 2-3 seconds for first full scan to complete
- RPLidar C1 typically provides 75-80% coverage (normal)
- Use averaged readings (`.front`, `.right`, etc.) for robustness

### Orbbec Camera Test

Tests RGB and Depth camera capture:

```bash
cd /home/fm/work/evabot
python tests/integration/test_camera.py
```

**What it tests:**
1. Camera initialization and connection
2. RGB frame capture (640x480)
3. Depth frame capture (640x480)
4. Depth at specific pixel coordinates
5. Atomic RGB+Depth frame retrieval
6. Continuous capture monitoring
7. OpenCV visualization (optional)

**Expected output:**
```
============================================================
Orbbec Camera Standalone Test
============================================================

Creating OrbbecCamera...
Starting camera...

Basic Frame Retrieval:
  ✅ RGB image: (480, 640, 3) dtype=uint8
     Range: 0-255
  ✅ Depth image: (480, 640) dtype=uint16
     Range: 0-4500 mm
  ✅ Depth (meters): (480, 640) dtype=float32
     Range: 0.30-4.50 m
     Mean:  1.25 m

Depth at Specific Points:
  center   (320, 240): 1.25 m
  left     (160, 240): 1.45 m
  right    (480, 240): 1.10 m
  top      (320, 120): 1.30 m
  bottom   (320, 360): 1.20 m

✅ Test Complete!
```

### Camera Not Responding

**Problem**: `No Orbbec devices found` or `Failed to start camera`

- Check camera is connected via USB
- Verify USB device appears:
  ```bash
  lsusb | grep -i orbbec
  ```
- Install udev rules (Linux):
  ```bash
  # Download udev rules from pyorbbecsdk
  sudo wget https://raw.githubusercontent.com/orbbec/pyorbbecsdk/main/misc/99-obsensor-libusb.rules -O /etc/udev/rules.d/99-obsensor-libusb.rules
  sudo udevadm control --reload-rules && sudo udevadm trigger
  ```
- Check permissions (add user to video group):
  ```bash
  sudo usermod -a -G video $USER
  # Then logout and login
  ```

**Problem**: `ModuleNotFoundError: No module named 'pyorbbecsdk'`

- Install PyOrbbecSDK:
  ```bash
  pip install pyorbbecsdk2
  ```
- Note: Package name is `pyorbbecsdk2` but import is `pyorbbecsdk`

**Problem**: No RGB or depth frames

- Wait 1-2 seconds after start() for first frames
- Check camera supports both RGB and Depth (some models depth-only)
- Verify camera is not in use by another process

## Future Tests

Planned integration tests:

- **Multiple Motors**: Test 4 motors running together
- **Mecanum Drive**: Test omnidirectional movement
- **Odometry**: Verify position tracking accuracy
- **Orbbec Camera**: Test RGB + Depth capture
- **CAN Bus Load**: Test with many motors on same bus
- **Error Recovery**: Test handling of CAN errors, motor faults
- **Safety Systems**: Test emergency stop, timeout edge cases

## CI/CD

These tests require real hardware and **cannot run in CI/CD**. They must be run manually on actual robot hardware.

For CI/CD, use unit tests that mock hardware interfaces.
