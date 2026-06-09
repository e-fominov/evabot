#!/usr/bin/env python3
"""Debug: scan CAN bus for motors and dump settings."""
import can
import time


def crc(data):
    return sum(data) & 0xFF


def send_and_recv(bus, can_id, cmd_data, timeout=0.3):
    """Send command and collect all responses."""
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
    return ' '.join(f'{b:02X}' for b in data)


def scan_motors(bus, max_id=10):
    """Find all motors that respond to encoder read."""
    found = []
    for can_id in range(1, max_id + 1):
        responses = send_and_recv(bus, can_id, [0x30], timeout=0.15)
        if responses:
            found.append(can_id)
            print(f"  CAN ID {can_id}: FOUND ({len(responses)} response(s))")
        else:
            print(f"  CAN ID {can_id}: no response")
    return found


def read_param(bus, can_id, cmd, name, parser=None):
    """Read a parameter and print raw response."""
    responses = send_and_recv(bus, can_id, [cmd])
    if responses:
        for r in responses:
            extra = ""
            if parser:
                extra = "  -> " + parser(r.data)
            print(f"    {name:30s} (0x{cmd:02X}): [{hex_dump(r.data)}]{extra}")
        return responses
    else:
        print(f"    {name:30s} (0x{cmd:02X}): no response")
        return None


def read_config_param(bus, can_id, param_code, name, parser=None):
    """Read a config parameter via 0x00 command."""
    responses = send_and_recv(bus, can_id, [0x00, param_code])
    if responses:
        for r in responses:
            extra = ""
            if parser:
                extra = "  -> " + parser(r.data)
            print(f"    {name:30s} (0x00,0x{param_code:02X}): [{hex_dump(r.data)}]{extra}")
        return responses
    else:
        print(f"    {name:30s} (0x00,0x{param_code:02X}): no response")
        return None


def parse_encoder(data):
    if len(data) >= 7 and data[0] == 0x30:
        carry = int.from_bytes(data[1:5], 'big', signed=True)
        value = int.from_bytes(data[5:7], 'big', signed=False)
        pos = carry * 3200 + int(value * 3200 / 16384)
        return f"carry={carry}, value={value}, pos={pos} pulses"
    return "?"


def parse_version(data):
    if len(data) >= 5 and data[0] == 0x40:
        cal_hw = data[1]
        cal = (cal_hw >> 7) & 1
        hw = cal_hw & 0x7F
        hw_names = {1: 'S42D_485', 2: 'S42D_CAN', 3: 'S57D_485', 4: 'S57D_CAN',
                    5: 'S28D_485', 6: 'S28D_CAN', 7: 'S35D_485', 8: 'S35D_CAN'}
        fw = f"V{data[2]}.{data[3]}.{data[4]}"
        return f"hw={hw_names.get(hw, hw)}, fw={fw}, calibrated={'yes' if cal else 'NO'}"
    return "?"


def parse_speed(data):
    if len(data) >= 3 and data[0] == 0x32:
        rpm = int.from_bytes(data[1:3], 'big', signed=True)
        return f"{rpm} RPM"
    return "?"


def parse_enable(data):
    if len(data) >= 2 and data[0] == 0x3A:
        return "ENABLED" if data[1] == 1 else "DISABLED"
    return "?"


def parse_error(data):
    if len(data) >= 5 and data[0] == 0x39:
        err = int.from_bytes(data[1:5], 'big', signed=True)
        degrees = err * 360.0 / 51200
        return f"{err} ({degrees:.1f} deg)"
    return "?"


MODE_NAMES = {0: 'CR_OPEN', 1: 'CR_CLOSE', 2: 'CR_vFOC', 3: 'SR_OPEN', 4: 'SR_CLOSE', 5: 'SR_vFOC'}


def parse_mode(data):
    if len(data) >= 2:
        mode = data[1]
        return MODE_NAMES.get(mode, f"unknown({mode})")
    return "?"


def parse_direction(data):
    if len(data) >= 2:
        return "CW" if data[1] == 0 else "CCW"
    return "?"


def test_spin(bus, can_id, speed=30, duration=1.5):
    """Try to spin motor forward then reverse."""
    # Enable
    send_and_recv(bus, can_id, [0xF3, 0x01], timeout=0.2)
    time.sleep(0.1)

    # Read initial encoder
    r = send_and_recv(bus, can_id, [0x30], timeout=0.15)
    pos_before = None
    if r and len(r[0].data) >= 7:
        carry = int.from_bytes(r[0].data[1:5], 'big', signed=True)
        value = int.from_bytes(r[0].data[5:7], 'big', signed=False)
        pos_before = carry * 3200 + int(value * 3200 / 16384)

    # Forward
    byte2 = (1 << 7) | ((speed >> 8) & 0x0F)
    byte3 = speed & 0xFF
    cmd = [0xF6, byte2, byte3, 0x02]
    cmd.append(crc([can_id] + cmd))
    bus.send(can.Message(arbitration_id=can_id, data=cmd, is_extended_id=False))
    print(f"    Forward {speed} RPM for {duration}s...")
    time.sleep(duration)

    # Stop
    cmd = [0xF6, 0x00, 0x00, 0x02]
    cmd.append(crc([can_id] + cmd))
    bus.send(can.Message(arbitration_id=can_id, data=cmd, is_extended_id=False))
    time.sleep(0.5)

    # Read encoder after forward
    r = send_and_recv(bus, can_id, [0x30], timeout=0.15)
    pos_after_fwd = None
    if r and len(r[0].data) >= 7:
        carry = int.from_bytes(r[0].data[1:5], 'big', signed=True)
        value = int.from_bytes(r[0].data[5:7], 'big', signed=False)
        pos_after_fwd = carry * 3200 + int(value * 3200 / 16384)

    if pos_before is not None and pos_after_fwd is not None:
        delta = pos_after_fwd - pos_before
        moved = "YES" if abs(delta) > 50 else "NO"
        print(f"    Forward result: delta={delta:+d} pulses  MOVED={moved}")
    else:
        print(f"    Forward result: encoder read failed")

    # Reverse
    byte2 = (0 << 7) | ((speed >> 8) & 0x0F)
    byte3 = speed & 0xFF
    cmd = [0xF6, byte2, byte3, 0x02]
    cmd.append(crc([can_id] + cmd))
    bus.send(can.Message(arbitration_id=can_id, data=cmd, is_extended_id=False))
    print(f"    Reverse {speed} RPM for {duration}s...")
    time.sleep(duration)

    # Stop
    cmd = [0xF6, 0x00, 0x00, 0x02]
    cmd.append(crc([can_id] + cmd))
    bus.send(can.Message(arbitration_id=can_id, data=cmd, is_extended_id=False))
    time.sleep(0.5)

    # Read encoder after reverse
    r = send_and_recv(bus, can_id, [0x30], timeout=0.15)
    pos_after_rev = None
    if r and len(r[0].data) >= 7:
        carry = int.from_bytes(r[0].data[1:5], 'big', signed=True)
        value = int.from_bytes(r[0].data[5:7], 'big', signed=False)
        pos_after_rev = carry * 3200 + int(value * 3200 / 16384)

    if pos_after_fwd is not None and pos_after_rev is not None:
        delta = pos_after_rev - pos_after_fwd
        moved = "YES" if abs(delta) > 50 else "NO"
        print(f"    Reverse result: delta={delta:+d} pulses  MOVED={moved}")
    else:
        print(f"    Reverse result: encoder read failed")

    # Disable
    send_and_recv(bus, can_id, [0xF3, 0x00], timeout=0.2)


def dump_motor(bus, can_id):
    """Dump all readable info from a motor."""
    print(f"\n{'='*60}")
    print(f"MOTOR CAN ID {can_id}")
    print(f"{'='*60}")

    # Version info
    print(f"  Identity:")
    read_param(bus, can_id, 0x40, "Version", parse_version)

    # Status
    print(f"  Status:")
    read_param(bus, can_id, 0x30, "Encoder", parse_encoder)
    read_param(bus, can_id, 0x32, "Real-time speed", parse_speed)
    read_param(bus, can_id, 0x39, "Position angle error", parse_error)
    read_param(bus, can_id, 0x3A, "Enable status", parse_enable)
    read_param(bus, can_id, 0x3B, "Return-to-zero status")
    read_param(bus, can_id, 0x33, "Pulses received")

    # Configuration (read via 0x00 command)
    print(f"  Configuration (via 0x00 read):")
    read_config_param(bus, can_id, 0x82, "Work mode", parse_mode)
    read_config_param(bus, can_id, 0x83, "Working current")
    read_config_param(bus, can_id, 0x84, "Subdivisions")
    read_config_param(bus, can_id, 0x85, "EN pin active level")
    read_config_param(bus, can_id, 0x86, "Motor direction", parse_direction)
    read_config_param(bus, can_id, 0x87, "Auto screen off")
    read_config_param(bus, can_id, 0x89, "Subdivision interpolation")
    read_config_param(bus, can_id, 0x8A, "CAN bitrate")
    read_config_param(bus, can_id, 0x8B, "CAN slave ID")
    read_config_param(bus, can_id, 0x8C, "Response method")
    read_config_param(bus, can_id, 0x8D, "Group CAN ID")
    read_config_param(bus, can_id, 0x8F, "Key lock")
    read_config_param(bus, can_id, 0x95, "Position arrival threshold")
    read_config_param(bus, can_id, 0x98, "Heartbeat protection time")
    read_config_param(bus, can_id, 0x9B, "Holding current %")

    # Spin test
    print(f"  Spin test:")
    test_spin(bus, can_id)


def main():
    print("=" * 60)
    print("EVABOT MOTOR DEBUG - CAN Bus Scanner")
    print("=" * 60)

    bus = can.Bus(channel='can0', interface='socketcan', bitrate=500000)

    while bus.recv(timeout=0.05):
        pass

    print("\nScanning CAN IDs 1-10...")
    found = scan_motors(bus, max_id=10)
    print(f"\nFound {len(found)} motor(s): {found}")

    for can_id in found:
        dump_motor(bus, can_id)

    # Cleanup
    print(f"\n{'='*60}")
    print("Releasing all motors...")
    for can_id in found:
        send_and_recv(bus, can_id, [0xF7], timeout=0.1)
        send_and_recv(bus, can_id, [0xF3, 0x00], timeout=0.1)

    bus.shutdown()
    print("Done.")


if __name__ == '__main__':
    main()
