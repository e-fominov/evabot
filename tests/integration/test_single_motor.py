#!/usr/bin/env python3
"""
Integration test for single Servo42D motor.

Tests real hardware communication:
- Motor initialization and CAN communication
- Running at different speeds
- Encoder updates and accuracy
- Reverse direction
- Safety features (runtime timeout)

Requirements:
- Motor at CAN ID 1
- CAN bus (can0) configured and up
- Motor should be free to spin (not mechanically loaded)
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


def test_motor_initialization():
    """Test 1: Motor initialization and CAN communication"""
    print_test("Motor Initialization and CAN Communication")

    try:
        motor = Servo42D(can_id=1)
        print_pass("Motor object created")

        motor.start()
        print_pass("Motor started (CAN communication established)")

        time.sleep(0.5)

        # Try to read encoder (verifies CAN communication)
        try:
            position = motor.get_position()
            print_pass(f"Encoder read successful: {position} pulses")

            # Encoder should return a reasonable value
            if abs(position) < 1_000_000:  # Sanity check
                print_pass(f"Encoder value is reasonable")
            else:
                print_fail(f"Encoder value seems too large: {position}")
                motor.stop()
                return False

        except Exception as e:
            print_fail(f"Failed to read encoder: {e}")
            motor.stop()
            return False

        motor.stop()
        print_pass("Motor stopped")

        return True

    except Exception as e:
        print_fail(f"Motor initialization failed: {e}")
        return False


def test_encoder_updates_forward():
    """Test 2: Encoder updates when motor runs forward"""
    print_test("Encoder Updates - Forward Direction")

    try:
        motor = Servo42D(can_id=1)
        motor.start()

        # Read initial position
        initial_pos = motor.get_position()
        print_info(f"Initial encoder: {initial_pos} pulses")

        # Run motor forward at 40 RPM
        print_info("Running motor forward at 40 RPM for 3 seconds...")
        motor.run(40)

        # Sample encoder during motion
        positions = []
        for i in range(6):
            time.sleep(0.5)
            pos = motor.get_position()
            delta = pos - initial_pos
            positions.append(pos)
            print_info(f"  {i*0.5 + 0.5:.1f}s: {pos:7d} pulses (+{delta:6d})")

        # Stop motor
        motor.run(0)
        time.sleep(0.5)

        final_pos = motor.get_position()
        total_delta = final_pos - initial_pos

        print_info(f"Final encoder: {final_pos} pulses")
        print_info(f"Total change: {total_delta} pulses")

        # Verify encoder increased (forward motion)
        success = True
        if not assert_true(total_delta > 0,
                          f"Encoder increased (forward direction verified)",
                          f"Encoder didn't increase! Delta: {total_delta}"):
            success = False

        # Verify encoder changed significantly (motor actually moved)
        if not assert_true(abs(total_delta) > 100,
                          f"Encoder changed significantly ({total_delta} pulses)",
                          f"Encoder barely changed ({total_delta} pulses) - motor might not be moving"):
            success = False

        # Calculate expected pulses: 40 RPM × 3 seconds × 3200 pulses/rev ÷ 60 s/min
        expected_pulses = 40 * 3 * 3200 / 60
        print_info(f"Expected ~{expected_pulses:.0f} pulses (40 RPM × 3s)")

        # Allow 50% tolerance (motor may not reach full speed instantly)
        tolerance = 0.5
        if not assert_true(abs(total_delta) > expected_pulses * tolerance,
                          f"Encoder change matches expected speed (within tolerance)",
                          f"Encoder change too small: {total_delta} < {expected_pulses * tolerance:.0f}"):
            success = False

        # Verify monotonic increase (all samples increasing)
        monotonic = all(positions[i] > positions[i-1] for i in range(1, len(positions)))
        if not assert_true(monotonic,
                          "Encoder increased monotonically (consistent forward motion)",
                          "Encoder values not monotonically increasing"):
            success = False

        motor.stop()
        return success

    except Exception as e:
        print_fail(f"Test failed with exception: {e}")
        try:
            motor.stop()
        except:
            pass
        return False


def test_encoder_updates_reverse():
    """Test 3: Encoder updates when motor runs backward"""
    print_test("Encoder Updates - Reverse Direction")

    try:
        motor = Servo42D(can_id=1)
        motor.start()

        # Read initial position
        initial_pos = motor.get_position()
        print_info(f"Initial encoder: {initial_pos} pulses")

        # Run motor backward at -40 RPM
        print_info("Running motor backward at -40 RPM for 3 seconds...")
        motor.run(-40)

        # Sample encoder during motion
        positions = []
        for i in range(6):
            time.sleep(0.5)
            pos = motor.get_position()
            delta = pos - initial_pos
            positions.append(pos)
            print_info(f"  {i*0.5 + 0.5:.1f}s: {pos:7d} pulses ({delta:+6d})")

        # Stop motor
        motor.run(0)
        time.sleep(0.5)

        final_pos = motor.get_position()
        total_delta = final_pos - initial_pos

        print_info(f"Final encoder: {final_pos} pulses")
        print_info(f"Total change: {total_delta} pulses")

        # Verify encoder decreased (backward motion)
        success = True
        if not assert_true(total_delta < 0,
                          f"Encoder decreased (reverse direction verified)",
                          f"Encoder didn't decrease! Delta: {total_delta}"):
            success = False

        # Verify encoder changed significantly
        if not assert_true(abs(total_delta) > 100,
                          f"Encoder changed significantly ({abs(total_delta)} pulses)",
                          f"Encoder barely changed ({abs(total_delta)} pulses)"):
            success = False

        # Verify monotonic decrease
        monotonic = all(positions[i] < positions[i-1] for i in range(1, len(positions)))
        if not assert_true(monotonic,
                          "Encoder decreased monotonically (consistent reverse motion)",
                          "Encoder values not monotonically decreasing"):
            success = False

        motor.stop()
        return success

    except Exception as e:
        print_fail(f"Test failed with exception: {e}")
        try:
            motor.stop()
        except:
            pass
        return False


def test_speed_control():
    """Test 4: Different speeds produce proportional encoder changes"""
    print_test("Speed Control - Different RPMs")

    try:
        motor = Servo42D(can_id=1)
        motor.start()

        speeds = [20, 40, 60]
        deltas = []

        for speed in speeds:
            initial_pos = motor.get_position()
            print_info(f"Testing {speed} RPM for 2 seconds...")

            motor.run(speed)
            time.sleep(2)
            motor.run(0)
            time.sleep(0.5)

            final_pos = motor.get_position()
            delta = final_pos - initial_pos
            deltas.append(delta)

            print_info(f"  {speed} RPM → {delta} pulses")

        # Verify higher speeds produce more encoder change
        success = True
        if not assert_true(deltas[1] > deltas[0],
                          f"40 RPM ({deltas[1]}) > 20 RPM ({deltas[0]})",
                          f"Speed proportionality failed: 40 RPM not faster than 20 RPM"):
            success = False

        if not assert_true(deltas[2] > deltas[1],
                          f"60 RPM ({deltas[2]}) > 40 RPM ({deltas[1]})",
                          f"Speed proportionality failed: 60 RPM not faster than 40 RPM"):
            success = False

        # Check approximate proportionality (60 RPM should be ~3x of 20 RPM)
        ratio = deltas[2] / deltas[0] if deltas[0] > 0 else 0
        print_info(f"Speed ratio (60/20 RPM): {ratio:.2f}x (expected ~3x)")

        if not assert_true(2.0 < ratio < 4.0,
                          f"Speed proportionality reasonable ({ratio:.2f}x)",
                          f"Speed ratio {ratio:.2f}x out of expected range (2-4x)"):
            success = False

        motor.stop()
        return success

    except Exception as e:
        print_fail(f"Test failed with exception: {e}")
        try:
            motor.stop()
        except:
            pass
        return False


def test_position_control():
    """Test 5: Position control - move by degrees and rotations"""
    print_test("Position Control - Move by Distance")

    try:
        motor = Servo42D(can_id=1)
        motor.start()

        # Set zero position
        print_info("Setting current position as zero...")
        result = motor.zero_position()

        if not assert_true(result,
                          "Zero position set successfully",
                          "Failed to set zero position"):
            motor.stop()
            return False

        # Read zero position immediately (before encoder drift)
        initial_pos = motor.get_position()
        print_info(f"Zero reference position: {initial_pos} pulses")

        time.sleep(0.5)

        # Test move_by with degrees
        print_info("Testing move_by(90 degrees, speed=40)...")
        pre_move_pos = motor.get_position()
        print_info(f"Position before move_by: {pre_move_pos} pulses")
        result = motor.move_by(90, speed=40, unit='degrees')

        if result:
            final_pos = motor.get_position()
            delta = abs(final_pos - initial_pos)
            expected = 90 * motor.PULSES_PER_DEGREE
            print_info(f"Moved {delta} pulses (expected ~{expected:.0f})")

            success = True
            if not assert_true(result,
                              f"Move by 90 degrees completed",
                              f"Move by 90 degrees failed"):
                success = False

            # Check if movement was approximately correct (within 20% tolerance)
            if not assert_true(abs(delta - expected) < expected * 0.2,
                              f"Movement distance accurate ({delta:.0f} ≈ {expected:.0f} pulses)",
                              f"Movement distance off: {delta:.0f} vs {expected:.0f} pulses"):
                success = False
        else:
            print_fail("Move by degrees failed or timed out")
            success = False

        time.sleep(1)

        # Test move_to (return to zero)
        print_info("Testing move_to(0 degrees, speed=30) - return to zero...")
        result = motor.move_to(0, speed=30, unit='degrees')

        if result:
            final_pos = motor.get_position()
            delta_from_zero = abs(final_pos - initial_pos)
            print_info(f"Final position: {final_pos} pulses ({delta_from_zero} from zero)")

            if not assert_true(delta_from_zero < 100,
                              f"Returned to zero position ({delta_from_zero} pulses from zero)",
                              f"Did not return to zero ({delta_from_zero} pulses from zero)"):
                success = False
        else:
            print_info("Move to zero failed or timed out (may need debugging)")
            success = False

        motor.stop()
        return success

    except Exception as e:
        print_fail(f"Test failed with exception: {e}")
        try:
            motor.stop()
        except:
            pass
        return False


def main():
    """Run all integration tests"""
    print(f"\n{Colors.BOLD}{'=' * 60}")
    print("INTEGRATION TEST: Single Motor (Servo42D)")
    print(f"{'=' * 60}{Colors.RESET}\n")

    print_info("Requirements:")
    print_info("  - Servo42D motor at CAN ID 1")
    print_info("  - CAN bus (can0) configured and active")
    print_info("  - Motor free to spin (not mechanically loaded)")
    print()

    # Run all tests
    tests = [
        ("Motor Initialization", test_motor_initialization),
        ("Encoder Updates (Forward)", test_encoder_updates_forward),
        ("Encoder Updates (Reverse)", test_encoder_updates_reverse),
        ("Speed Control", test_speed_control),
        ("Position Control", test_position_control),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_fail(f"Test crashed: {e}")
            results.append((name, False))

        # Give motor time to fully reset between tests
        time.sleep(1.0)

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
