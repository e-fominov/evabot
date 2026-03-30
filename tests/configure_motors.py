#!/usr/bin/env python3
"""Configure all 4 motors to identical settings."""
import can
import time

# Target configuration
TARGET = {
    "mode": (0x82, 3, "SR_OPEN"),  # Work mode (smooth at low speed)
    "current": (0x83, 800, "mA"),  # Working current (uint16)
    "subdivisions": (0x84, 16, "microsteps"),  # Subdivisions
    "en_pin": (0x85, 0, "active low"),  # EN pin active level
    "direction": (0x86, 0, "CW"),  # Motor direction
    "screen_off": (0x87, 0, "disabled"),  # Auto screen off
    "interpolation": (0x89, 1, "enabled"),  # Subdivision interpolation
    "can_bitrate": (0x8A, 2, "500K"),  # CAN bitrate
    "response": (0x8C, [1, 0], "respond, passive"),  # Response method
    "key_lock": (0x8F, 0, "unlocked"),  # Key lock
    "holding_pct": (0x9B, 4, "50%"),  # Holding current %
}

MOTOR_IDS = [5]
# MOTOR_IDS = [1, 2, 3, 4]


def crc(data):
    return sum(data) & 0xFF


def send_and_recv(bus, can_id, cmd_data, timeout=0.3):
    while bus.recv(timeout=0.01):
        pass
    data = cmd_data[:]
    data.append(crc([can_id] + data))
    msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=False)
    bus.send(msg)

    responses = []
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = bus.recv(timeout=0.05)
        if r and r.arbitration_id == can_id:
            responses.append(r)
    return responses


def hex_dump(data):
    return " ".join(f"{b:02X}" for b in data)


def read_config(bus, can_id, param_code):
    """Read a config parameter via 0x00."""
    return send_and_recv(bus, can_id, [0x00, param_code])


def write_param(bus, can_id, param_code, value):
    """Write a config parameter. Value can be int or list of bytes."""
    if isinstance(value, list):
        cmd = [param_code] + value
    elif value > 255:
        # uint16
        cmd = [param_code, (value >> 8) & 0xFF, value & 0xFF]
    else:
        cmd = [param_code, value]
    return send_and_recv(bus, can_id, cmd)


def configure_motor(bus, can_id):
    """Configure a single motor to target settings."""
    print(f"\n{'='*60}")
    print(f"CONFIGURING MOTOR CAN ID {can_id}")
    print(f"{'='*60}")

    changes = 0

    for name, (param_code, target_val, label) in TARGET.items():
        # Read current value
        current = read_config(bus, can_id, param_code)

        # Extract current value from response
        current_bytes = None
        if current and len(current[0].data) >= 2:
            current_bytes = list(current[0].data)

        # Build expected value bytes for comparison
        if isinstance(target_val, list):
            expected = target_val
        elif target_val > 255:
            expected = [(target_val >> 8) & 0xFF, target_val & 0xFF]
        else:
            expected = [target_val]

        # Check if current matches target
        needs_change = True
        if current_bytes:
            # Response format: [param_code, value_bytes..., crc]
            resp_values = current_bytes[1:-1]  # strip cmd and crc
            if resp_values == expected:
                needs_change = False

        if needs_change:
            print(f"  {name:20s}: CHANGING to {target_val} ({label})")
            if current_bytes:
                print(f"    was: [{hex_dump(current[0].data)}]")

            result = write_param(bus, can_id, param_code, target_val)
            if result:
                status = result[0].data[1] if len(result[0].data) >= 2 else "?"
                ok = "OK" if status == 1 else f"status={status}"
                print(f"    result: [{hex_dump(result[0].data)}]  {ok}")
            else:
                print(f"    result: no response")
            changes += 1
            time.sleep(0.1)
        else:
            print(f"  {name:20s}: OK ({label})")

    if changes == 0:
        print(f"\n  All settings already correct!")
    else:
        print(f"\n  Applied {changes} change(s)")

    return changes


def verify_motor(bus, can_id):
    """Verify motor responds to speed commands after config."""
    print(f"\n  Verification spin test (CAN ID {can_id}):")

    # Enable
    r = send_and_recv(bus, can_id, [0xF3, 0x01], timeout=0.3)
    if r and len(r[0].data) >= 2 and r[0].data[1] == 1:
        print(f"    Enable: OK")
    else:
        print(f"    Enable: FAILED")
        return False

    time.sleep(0.1)

    # Read encoder before
    r = send_and_recv(bus, can_id, [0x30], timeout=0.15)
    pos_before = None
    if r and len(r[0].data) >= 7:
        carry = int.from_bytes(r[0].data[1:5], "big", signed=True)
        value = int.from_bytes(r[0].data[5:7], "big", signed=False)
        pos_before = carry * 3200 + int(value * 3200 / 16384)

    # Spin forward briefly
    speed = 30
    byte2 = (1 << 7) | ((speed >> 8) & 0x0F)
    byte3 = speed & 0xFF
    cmd = [0xF6, byte2, byte3, 0x02]
    cmd.append(crc([can_id] + cmd))
    bus.send(can.Message(arbitration_id=can_id, data=cmd, is_extended_id=False))
    time.sleep(1.0)

    # Stop
    cmd = [0xF6, 0x00, 0x00, 0x02]
    cmd.append(crc([can_id] + cmd))
    bus.send(can.Message(arbitration_id=can_id, data=cmd, is_extended_id=False))
    time.sleep(0.3)

    # Read encoder after
    r = send_and_recv(bus, can_id, [0x30], timeout=0.15)
    pos_after = None
    if r and len(r[0].data) >= 7:
        carry = int.from_bytes(r[0].data[1:5], "big", signed=True)
        value = int.from_bytes(r[0].data[5:7], "big", signed=False)
        pos_after = carry * 3200 + int(value * 3200 / 16384)

    # Disable
    send_and_recv(bus, can_id, [0xF3, 0x00], timeout=0.2)

    if pos_before is not None and pos_after is not None:
        delta = pos_after - pos_before
        if abs(delta) > 50:
            print(f"    Spin: PASS (delta={delta:+d} pulses)")
            return True
        else:
            print(f"    Spin: FAIL - motor did not move (delta={delta:+d})")
            return False
    else:
        print(f"    Spin: FAIL - encoder read error")
        return False


def main():
    print("=" * 60)
    print("EVABOT MOTOR CONFIGURATION")
    print("=" * 60)
    print(f"\nTarget settings:")
    for name, (param_code, val, label) in TARGET.items():
        print(f"  {name:20s}: {val} ({label})")

    bus = can.Bus(channel="can0", interface="socketcan", bitrate=500000)
    while bus.recv(timeout=0.05):
        pass

    total_changes = 0
    results = {}

    for can_id in MOTOR_IDS:
        changes = configure_motor(bus, can_id)
        total_changes += changes
        ok = verify_motor(bus, can_id)
        results[can_id] = ok

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for can_id in MOTOR_IDS:
        status = "PASS" if results[can_id] else "FAIL"
        print(f"  Motor CAN ID {can_id}: {status}")
    print(f"\n  Total config changes: {total_changes}")

    passed = sum(1 for v in results.values() if v)
    if passed == len(MOTOR_IDS):
        print(f"\n  ALL {len(MOTOR_IDS)} MOTORS OK!")
    else:
        print(f"\n  {passed}/{len(MOTOR_IDS)} motors working - check failures above")

    # Cleanup
    for can_id in MOTOR_IDS:
        send_and_recv(bus, can_id, [0xF7], timeout=0.1)
        send_and_recv(bus, can_id, [0xF3, 0x00], timeout=0.1)

    bus.shutdown()
    print("Done.")


if __name__ == "__main__":
    main()
