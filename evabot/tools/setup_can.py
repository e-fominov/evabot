#!/usr/bin/env python3
"""
Setup CAN bus interface on robot.

Automatically detects and configures CAN interface (can0) with proper settings.
"""

import subprocess
import sys


def check_can_interface(interface='can0'):
    """Check if CAN interface exists"""
    try:
        result = subprocess.run(
            ['ip', 'link', 'show', interface],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def is_can_up(interface='can0'):
    """Check if CAN interface is UP"""
    try:
        result = subprocess.run(
            ['ip', 'link', 'show', interface],
            capture_output=True,
            text=True
        )
        return 'UP' in result.stdout
    except Exception:
        return False


def setup_can(interface='can0', bitrate=500000):
    """
    Bring up CAN interface with specified bitrate.

    Args:
        interface: CAN interface name (default: can0)
        bitrate: Bitrate in bps (default: 500000)

    Returns:
        True if successful, False otherwise
    """
    if not check_can_interface(interface):
        print(f"✗ Error: CAN interface '{interface}' not found")
        print(f"  Make sure your CAN hardware is connected")
        return False

    if is_can_up(interface):
        print(f"✓ CAN interface '{interface}' already UP")
        return True

    print(f"→ Bringing up {interface} @ {bitrate}bps...")

    # Try to bring up interface
    try:
        # Set down first (in case it's in error state)
        subprocess.run(
            ['sudo', 'ip', 'link', 'set', interface, 'down'],
            check=False,
            capture_output=True
        )

        # Configure and bring up
        subprocess.run(
            ['sudo', 'ip', 'link', 'set', interface, 'type', 'can', 'bitrate', str(bitrate)],
            check=True,
            capture_output=True
        )

        subprocess.run(
            ['sudo', 'ip', 'link', 'set', interface, 'up'],
            check=True,
            capture_output=True
        )

        print(f"✓ CAN interface '{interface}' is UP @ {bitrate}bps")
        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to bring up CAN interface: {e}")
        print(f"  You may need to configure CAN manually or check permissions")
        return False


def main():
    """Main entry point"""
    print("=" * 60)
    print("EvaBot CAN Bus Setup")
    print("=" * 60)
    print()

    success = setup_can()

    print()
    if success:
        print("✓ CAN bus ready!")
        return 0
    else:
        print("✗ CAN bus setup failed")
        print("\nManual setup:")
        print("  sudo ip link set can0 up type can bitrate 500000")
        return 1


if __name__ == '__main__':
    sys.exit(main())
