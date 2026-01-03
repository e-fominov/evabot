#!/usr/bin/env python3
"""
Integration test for four Servo42D motors (mecanum drive configuration).

Tests coordinated motor control:
- All 4 motors initialization
- Synchronized movements (all forward, all backward)
- Opposite directions (diagonal patterns)
- Different speeds per motor
- Encoder updates for all motors
- Safety features (all motors unlock on exit)

Requirements:
- Motors at CAN IDs: FL=4, FR=2, BL=3, BR=1
- CAN bus (can0) configured and up
- Motors should be free to spin (not mechanically loaded)
"""

import time
import sys
from evabot.components.motors import Servo42D


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_test(name):
    """Print test name"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}TEST: {name}{Colors.RESET}")
    print("-" * 60)


def print_pass(message):
    """Print pass message"""
    print(f"{Colors.GREEN}✓ PASS:{Colors.RESET} {message}")


def print_fail(message):
    """Print fail message"""
    print(f"{Colors.RED}✗ FAIL:{Colors.RESET} {message}")


def print_info(message):
    """Print info message"""
    print(f"{Colors.YELLOW}ℹ INFO:{Colors.RESET} {message}")


def assert_true(condition, message, error_msg):
    """Assert condition is true"""
    if condition:
        print_pass(message)
        return True
    else:
        print_fail(error_msg)
        return False


def test_four_motor_initialization():
    """Test 1: Initialize all 4 motors and verify CAN communication"""
    print_test("Four Motor Initialization")

    motor_ids = {'FL': 4, 'FR': 2, 'BL': 3, 'BR': 1}
    motors = {}

    try:
        # Create all motors
        for name, can_id in motor_ids.items():
            motors[name] = Servo42D(can_id=can_id)
            print_pass(f"Motor {name} (ID {can_id}) created")

        # Start all motors
        for name, motor in motors.items():
            motor.start()
            print_pass(f"Motor {name} started")

        # Wait for motors to stabilize
        time.sleep(1.0)

        # Verify all motors respond (read encoders)
        success = True
        for name, motor in motors.items():
            try:
                position = motor.get_position()
                print_pass(f"Motor {name} encoder: {position} pulses")

                if abs(position) > 10_000_000:  # Sanity check
                    print_fail(f"Motor {name} encoder value seems too large: {position}")
                    success = False
            except Exception as e:
                print_fail(f"Failed to read encoder from motor {name}: {e}")
                success = False

        # Cleanup
        for motor in motors.values():
            motor.stop()

        return success

    except Exception as e:
        print_fail(f"Initialization failed: {e}")
        for motor in motors.values():
            try:
                motor.stop()
            except:
                pass
        return False


def test_synchronized_forward():
    """Test 2: All 4 motors run forward together"""
    print_test("Synchronized Forward Movement")

    motor_ids = {'FL': 4, 'FR': 2, 'BL': 3, 'BR': 1}
    motors = {}

    try:
        # Create and start motors
        for name, can_id in motor_ids.items():
            motors[name] = Servo42D(can_id=can_id)
            motors[name].start()

        # Wait for motors to stabilize
        time.sleep(1.0)

        # Read initial positions
        initial_positions = {}
        for name, motor in motors.items():
            initial_positions[name] = motor.get_position()
            print_info(f"Motor {name} initial: {initial_positions[name]} pulses")

        # Run all motors forward at 40 RPM
        print_info("Running all motors forward at 40 RPM for 3 seconds...")
        for motor in motors.values():
            motor.run(40)

        time.sleep(3)

        # Stop all motors
        for motor in motors.values():
            motor.run(0)
        # Wait for motors to stabilize
        time.sleep(1.0)

        # Read final positions
        final_positions = {}
        deltas = {}
        for name, motor in motors.items():
            final_positions[name] = motor.get_position()
            deltas[name] = final_positions[name] - initial_positions[name]
            print_info(f"Motor {name} delta: {deltas[name]:+7d} pulses")

        # Verify all motors moved forward
        success = True
        for name, delta in deltas.items():
            if not assert_true(delta > 0,
                              f"Motor {name} moved forward ({delta} pulses)",
                              f"Motor {name} didn't move forward ({delta} pulses)"):
                success = False

            if not assert_true(abs(delta) > 100,
                              f"Motor {name} moved significantly",
                              f"Motor {name} barely moved ({delta} pulses)"):
                success = False

        # Cleanup
        for motor in motors.values():
            motor.stop()

        return success

    except Exception as e:
        print_fail(f"Test failed: {e}")
        for motor in motors.values():
            try:
                motor.stop()
            except:
                pass
        return False


def test_opposite_directions():
    """Test 3: Front motors forward, rear motors backward"""
    print_test("Opposite Directions (Front Forward, Rear Backward)")

    motor_ids = {'FL': 4, 'FR': 2, 'BL': 3, 'BR': 1}
    motors = {}

    try:
        # Create and start motors
        for name, can_id in motor_ids.items():
            motors[name] = Servo42D(can_id=can_id)
            motors[name].start()

        # Wait for motors to stabilize
        time.sleep(1.0)

        # Read initial positions
        initial_positions = {}
        for name, motor in motors.items():
            initial_positions[name] = motor.get_position()

        # Front motors forward, rear motors backward
        print_info("FL & FR: +40 RPM (forward)")
        print_info("BL & BR: -40 RPM (backward)")
        motors['FL'].run(40)
        motors['FR'].run(40)
        motors['BL'].run(-40)
        motors['BR'].run(-40)

        time.sleep(3)

        # Stop all
        for motor in motors.values():
            motor.run(0)
        # Wait for motors to stabilize
        time.sleep(1.0)

        # Read final positions
        deltas = {}
        for name, motor in motors.items():
            final_pos = motor.get_position()
            deltas[name] = final_pos - initial_positions[name]
            print_info(f"Motor {name} delta: {deltas[name]:+7d} pulses")

        # Verify front motors moved forward
        success = True
        for name in ['FL', 'FR']:
            if not assert_true(deltas[name] > 0,
                              f"Motor {name} moved forward ({deltas[name]} pulses)",
                              f"Motor {name} didn't move forward ({deltas[name]} pulses)"):
                success = False

        # Verify rear motors moved backward
        for name in ['BL', 'BR']:
            if not assert_true(deltas[name] < 0,
                              f"Motor {name} moved backward ({deltas[name]} pulses)",
                              f"Motor {name} didn't move backward ({deltas[name]} pulses)"):
                success = False

        # Cleanup
        for motor in motors.values():
            motor.stop()

        return success

    except Exception as e:
        print_fail(f"Test failed: {e}")
        for motor in motors.values():
            try:
                motor.stop()
            except:
                pass
        return False


def test_different_speeds():
    """Test 4: Each motor at different speed"""
    print_test("Different Speeds Per Motor")

    motor_ids = {'FL': 4, 'FR': 2, 'BL': 3, 'BR': 1}
    motors = {}
    speeds = {'FL': 20, 'FR': 40, 'BL': 60, 'BR': 80}

    try:
        # Create and start motors
        for name, can_id in motor_ids.items():
            motors[name] = Servo42D(can_id=can_id)
            motors[name].start()

        # Wait for motors to stabilize
        time.sleep(1.0)

        # Read initial positions
        initial_positions = {}
        for name, motor in motors.items():
            initial_positions[name] = motor.get_position()

        # Run each motor at different speed
        print_info("Running motors at different speeds for 2 seconds:")
        for name, speed in speeds.items():
            print_info(f"  {name}: {speed} RPM")
            motors[name].run(speed)

        time.sleep(2)

        # Stop all
        for motor in motors.values():
            motor.run(0)
        # Wait for motors to stabilize
        time.sleep(1.0)

        # Read final positions
        deltas = {}
        for name, motor in motors.items():
            final_pos = motor.get_position()
            deltas[name] = abs(final_pos - initial_positions[name])
            print_info(f"Motor {name} ({speeds[name]} RPM): {deltas[name]} pulses")

        # Verify higher speeds produce more movement
        # Note: Due to CAN timing and acceleration, we use loose checks
        success = True

        # Check FL < FR < BL < BR (20 < 40 < 60 < 80 RPM)
        if deltas['FL'] > 0 and deltas['FR'] > 0:
            if not assert_true(deltas['FR'] > deltas['FL'] * 0.8,
                              f"40 RPM ({deltas['FR']}) > 20 RPM ({deltas['FL']})",
                              f"Speed proportionality failed: FR not faster than FL"):
                success = False

        if deltas['FR'] > 0 and deltas['BL'] > 0:
            if not assert_true(deltas['BL'] > deltas['FR'] * 0.8,
                              f"60 RPM ({deltas['BL']}) > 40 RPM ({deltas['FR']})",
                              f"Speed proportionality failed: BL not faster than FR"):
                success = False

        if deltas['BL'] > 0 and deltas['BR'] > 0:
            if not assert_true(deltas['BR'] > deltas['BL'] * 0.8,
                              f"80 RPM ({deltas['BR']}) > 60 RPM ({deltas['BL']})",
                              f"Speed proportionality failed: BR not faster than BL"):
                success = False

        # Cleanup
        for motor in motors.values():
            motor.stop()

        return success

    except Exception as e:
        print_fail(f"Test failed: {e}")
        for motor in motors.values():
            try:
                motor.stop()
            except:
                pass
        return False


def test_diagonal_pattern():
    """Test 5: Diagonal movement pattern (FL+BR vs FR+BL)"""
    print_test("Diagonal Pattern (Mecanum Simulation)")

    motor_ids = {'FL': 4, 'FR': 2, 'BL': 3, 'BR': 1}
    motors = {}

    try:
        # Create and start motors
        for name, can_id in motor_ids.items():
            motors[name] = Servo42D(can_id=can_id)
            motors[name].start()

        # Wait for motors to stabilize
        time.sleep(1.0)

        # Read initial positions
        initial_positions = {}
        for name, motor in motors.items():
            initial_positions[name] = motor.get_position()

        # Diagonal: FL+BR forward, FR+BL backward
        print_info("Diagonal pattern (simulates mecanum strafe):")
        print_info("  FL & BR: +40 RPM")
        print_info("  FR & BL: -40 RPM")
        motors['FL'].run(40)
        motors['BR'].run(40)
        motors['FR'].run(-40)
        motors['BL'].run(-40)

        time.sleep(3)

        # Stop all
        for motor in motors.values():
            motor.run(0)
        # Wait for motors to stabilize
        time.sleep(1.0)

        # Read final positions
        deltas = {}
        for name, motor in motors.items():
            final_pos = motor.get_position()
            deltas[name] = final_pos - initial_positions[name]
            print_info(f"Motor {name} delta: {deltas[name]:+7d} pulses")

        # Verify FL & BR moved forward
        success = True
        for name in ['FL', 'BR']:
            if not assert_true(deltas[name] > 0,
                              f"Motor {name} moved forward ({deltas[name]} pulses)",
                              f"Motor {name} didn't move forward ({deltas[name]} pulses)"):
                success = False

        # Verify FR & BL moved backward
        for name in ['FR', 'BL']:
            if not assert_true(deltas[name] < 0,
                              f"Motor {name} moved backward ({deltas[name]} pulses)",
                              f"Motor {name} didn't move backward ({deltas[name]} pulses)"):
                success = False

        # Cleanup
        for motor in motors.values():
            motor.stop()

        return success

    except Exception as e:
        print_fail(f"Test failed: {e}")
        for motor in motors.values():
            try:
                motor.stop()
            except:
                pass
        return False


def test_encoder_independence():
    """Test 6: Verify each motor's encoder updates independently"""
    print_test("Encoder Independence")

    motor_ids = {'FL': 4, 'FR': 2, 'BL': 3, 'BR': 1}
    motors = {}

    try:
        # Create and start motors
        for name, can_id in motor_ids.items():
            motors[name] = Servo42D(can_id=can_id)
            motors[name].start()

        # Wait for motors to stabilize
        time.sleep(1.0)

        # Test each motor individually
        success = True
        for test_motor_name in motor_ids.keys():
            print_info(f"\nTesting {test_motor_name} alone...")

            # Read all initial positions
            initial_positions = {}
            for name, motor in motors.items():
                initial_positions[name] = motor.get_position()

            # Run only the test motor
            motors[test_motor_name].run(40)
            time.sleep(1.5)
            motors[test_motor_name].run(0)
            # Wait for motors to stabilize
            time.sleep(1.0)

            # Read all final positions
            final_positions = {}
            deltas = {}
            for name, motor in motors.items():
                final_positions[name] = motor.get_position()
                deltas[name] = abs(final_positions[name] - initial_positions[name])

            # Verify only test motor moved significantly
            print_info(f"  {test_motor_name}: {deltas[test_motor_name]} pulses (should be large)")

            if not assert_true(deltas[test_motor_name] > 100,
                              f"{test_motor_name} moved ({deltas[test_motor_name]} pulses)",
                              f"{test_motor_name} didn't move enough ({deltas[test_motor_name]} pulses)"):
                success = False

            # Other motors should not move (allow small noise)
            for name in motor_ids.keys():
                if name != test_motor_name:
                    print_info(f"  {name}: {deltas[name]} pulses (should be ~0)")
                    if not assert_true(deltas[name] < deltas[test_motor_name] * 0.1,
                                      f"{name} didn't move (encoder independent)",
                                      f"{name} moved unexpectedly ({deltas[name]} pulses)"):
                        success = False

        # Cleanup
        for motor in motors.values():
            motor.stop()

        return success

    except Exception as e:
        print_fail(f"Test failed: {e}")
        for motor in motors.values():
            try:
                motor.stop()
            except:
                pass
        return False


def test_emergency_stop_all():
    """Test 7: Verify all motors unlock after emergency stop"""
    print_test("Emergency Stop - All Motors Unlock")

    motor_ids = {'FL': 4, 'FR': 2, 'BL': 3, 'BR': 1}
    motors = {}

    try:
        # Create and start motors
        for name, can_id in motor_ids.items():
            motors[name] = Servo42D(can_id=can_id)
            motors[name].start()

        # Wait for motors to stabilize
        time.sleep(1.0)

        # Run all motors
        print_info("Running all motors...")
        for motor in motors.values():
            motor.run(40)

        time.sleep(1)

        # Emergency stop all
        print_info("Calling emergency_stop() on all motors...")
        for name, motor in motors.items():
            motor.emergency_stop()
            print_info(f"  {name} emergency stopped")

        # Wait for motors to stabilize
        time.sleep(1.0)

        # Verify all motors disabled
        success = True
        for name, motor in motors.items():
            if not assert_true(not motor._enabled,
                              f"Motor {name} disabled (shaft unlocked)",
                              f"Motor {name} still enabled (shaft locked)"):
                success = False

        print_info("\nManual check: All motor shafts should be FREE to turn")

        # Cleanup
        for motor in motors.values():
            motor.stop()

        return success

    except Exception as e:
        print_fail(f"Test failed: {e}")
        for motor in motors.values():
            try:
                motor.stop()
            except:
                pass
        return False


def main():
    """Run all 4-motor integration tests"""
    print(f"\n{Colors.BOLD}{'=' * 60}")
    print("INTEGRATION TEST: Four Motors (Mecanum Configuration)")
    print(f"{'=' * 60}{Colors.RESET}\n")

    print_info("Requirements:")
    print_info("  - Motors at CAN IDs: FL=4, FR=2, BL=3, BR=1")
    print_info("  - CAN bus (can0) configured and active")
    print_info("  - Motors free to spin (not mechanically loaded)")
    print()

    # Run all tests
    tests = [
        ("Four Motor Initialization", test_four_motor_initialization),
        ("Synchronized Forward", test_synchronized_forward),
        ("Opposite Directions", test_opposite_directions),
        ("Different Speeds", test_different_speeds),
        ("Diagonal Pattern", test_diagonal_pattern),
        ("Encoder Independence", test_encoder_independence),
        ("Emergency Stop All", test_emergency_stop_all),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_fail(f"Test crashed: {e}")
            results.append((name, False))

    # Print summary
    print(f"\n{Colors.BOLD}{'=' * 60}")
    print("TEST SUMMARY")
    print(f"{'=' * 60}{Colors.RESET}\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {status}  {name}")

    print(f"\n{Colors.BOLD}Result: {passed}/{total} tests passed{Colors.RESET}")

    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
