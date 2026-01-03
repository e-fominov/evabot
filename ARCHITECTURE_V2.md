# EvaBot Architecture V2 - Generic CAN Bus with Callbacks

## Core Principle

**CAN Bus = Generic Communication Layer**
- Doesn't know about motors, sensors, or any specific devices
- Only knows: CAN IDs, messages, callbacks
- Devices register themselves for periodic reads
- Supports both async (queued) and blocking calls

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Application Layer (User Code)                          │
│  robot.drive.forward(0.3)                               │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Component Layer (Servo42D, RPLidar, etc)              │
│  - Register periodic reads with CanBus                  │
│  - Send async commands (speed, etc)                     │
│  - Send blocking commands (config, calibrate)           │
│  - Receive callbacks with data                          │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Hardware Layer (CanBus)                                │
│  - Generic CAN communication                            │
│  - Periodic read scheduler (10Hz default)               │
│  - Callback routing by CAN ID                           │
│  - Blocking send/receive                                │
│  - Thread manages all CAN I/O                           │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Physical CAN Bus (can0)                                │
│  - Multiple CAN devices (motors, sensors, etc)          │
└─────────────────────────────────────────────────────────┘
```

## CanBus Implementation (Generic)

```python
class CanBus:
    """
    Generic CAN bus manager with background thread.

    Doesn't know about motors, sensors, or specific devices.
    Just routes CAN messages to/from registered callbacks.
    """

    def __init__(self, channel, bitrate):
        self.bus = can.Bus(channel, bitrate=bitrate)

        # Periodic reads: [(can_id, command_data, callback, rate, last_read_time)]
        self._periodic_reads = []
        self._periodic_lock = threading.Lock()

        # Response callbacks: {can_id: callback}
        self._callbacks = {}
        self._callback_lock = threading.Lock()

        # Background thread
        self._running = False
        self._thread = None

    def start(self):
        """Start CAN bus background thread"""
        self._running = True
        self._thread = threading.Thread(
            target=self._can_loop,
            daemon=True,
            name="can_bus"
        )
        self._thread.start()

    def _can_loop(self):
        """
        Background thread - handles periodic reads and incoming messages.

        Jobs:
        1. Send periodic read commands (e.g., encoder reads @ 10Hz)
        2. Listen for responses
        3. Route responses to callbacks
        """
        while self._running:
            current_time = time.time()

            # 1. Handle periodic reads
            with self._periodic_lock:
                for item in self._periodic_reads:
                    can_id, cmd_data, callback, rate, last_time = item

                    # Time to read?
                    if current_time - last_time >= (1.0 / rate):
                        # Send read command
                        msg = can.Message(
                            arbitration_id=can_id,
                            data=cmd_data,
                            is_extended_id=False
                        )
                        self.bus.send(msg)

                        # Update last read time
                        item[4] = current_time

            # 2. Listen for incoming messages (non-blocking)
            msg = self.bus.recv(timeout=0.01)
            if msg:
                # Route to callback
                with self._callback_lock:
                    if msg.arbitration_id in self._callbacks:
                        callback = self._callbacks[msg.arbitration_id]
                        callback(msg)

            # Small sleep to prevent CPU spin
            time.sleep(0.001)

    # === Device Registration ===

    def register_periodic_read(
        self,
        can_id: int,
        command_data: list,
        callback: callable,
        rate: float = 10.0
    ):
        """
        Register a device for periodic reading.

        Args:
            can_id: CAN device ID
            command_data: Command bytes to send (e.g., [0x30] for encoder)
            callback: Function called with response msg
            rate: Read frequency in Hz

        Usage:
            # Motor registers for encoder updates
            can_bus.register_periodic_read(
                can_id=1,
                command_data=[0x30],  # Read encoder command
                callback=self._on_encoder_update,
                rate=10.0
            )
        """
        with self._periodic_lock:
            self._periodic_reads.append([
                can_id,
                command_data,
                callback,
                rate,
                0.0  # last_read_time
            ])

        # Also register for responses
        self.register_callback(can_id, callback)

    def register_callback(self, can_id: int, callback: callable):
        """
        Register callback for CAN ID responses.

        Args:
            can_id: CAN device ID
            callback: Function(msg) called when message received
        """
        with self._callback_lock:
            self._callbacks[can_id] = callback

    # === Async Send ===

    def send_async(self, can_id: int, data: list):
        """
        Send command asynchronously (non-blocking).

        Args:
            can_id: CAN device ID
            data: Command bytes (including CRC)

        Usage:
            # Motor sets speed
            can_bus.send_async(can_id=1, data=[0xF6, 0x00, 0x64, 0x02, 0xCRC])
        """
        msg = can.Message(
            arbitration_id=can_id,
            data=data,
            is_extended_id=False
        )
        self.bus.send(msg)

    # === Blocking Send ===

    def send_blocking(
        self,
        can_id: int,
        data: list,
        timeout: float = 1.0
    ) -> can.Message:
        """
        Send command and wait for response (blocking).

        Args:
            can_id: CAN device ID
            data: Command bytes
            timeout: Max wait time in seconds

        Returns:
            Response message or None

        Usage:
            # Configure motor PID
            response = can_bus.send_blocking(
                can_id=1,
                data=[0x83, 0x0A, 0x05, 0x01, CRC],
                timeout=1.0
            )
        """
        # Send message
        msg = can.Message(
            arbitration_id=can_id,
            data=data,
            is_extended_id=False
        )
        self.bus.send(msg)

        # Wait for response
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = self.bus.recv(timeout=0.1)
            if response and response.arbitration_id == can_id:
                return response

        return None  # Timeout

    def stop(self):
        """Stop CAN bus thread"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
```

## Device Example: Servo42D

```python
class Servo42D(Component):
    """
    Servo42D motor - CAN device.

    Uses CanBus generically:
    - Registers for periodic encoder reads (10Hz)
    - Async speed commands
    - Blocking config commands
    """

    def __init__(self, can_id: int):
        super().__init__(name=f"Servo42D_{can_id}")
        self.can_id = can_id

        # Cached state (updated by CAN thread callback)
        self._encoder_position = 0
        self._lock = threading.RLock()

    def start(self):
        """Start motor - register with CAN bus"""
        bus = CanBus.get_default('can0')

        # Register for periodic encoder reads @ 10Hz
        bus.register_periodic_read(
            can_id=self.can_id,
            command_data=[0x30],  # Read encoder command
            callback=self._on_encoder_update,
            rate=10.0
        )

        # Enable motor
        self.enable(True)

    def _on_encoder_update(self, msg: can.Message):
        """
        Callback from CAN thread with encoder data.

        Called at 10Hz by CanBus background thread.
        """
        if len(msg.data) >= 8 and msg.data[0] == 0x30:
            # Parse encoder
            carry = int.from_bytes(msg.data[1:5], byteorder='big', signed=True)
            value = int.from_bytes(msg.data[5:7], byteorder='big', signed=False)
            position = carry * 3200 + int(value * 3200 / 16384)

            # Update cache
            with self._lock:
                self._encoder_position = position

    def get_position(self) -> int:
        """Get cached encoder position (no CAN traffic)"""
        with self._lock:
            return self._encoder_position

    # === Async Commands (real-time) ===

    def run(self, speed_rpm: float):
        """Set motor speed (async, non-blocking)"""
        direction = 1 if speed_rpm >= 0 else 0
        speed = int(abs(speed_rpm))

        byte2 = (direction << 7) | ((speed >> 8) & 0x0F)
        byte3 = speed & 0xFF
        data = [0xF6, byte2, byte3, 2]  # acceleration=2

        # Add CRC
        crc = self._calculate_crc([self.can_id] + data)
        data.append(crc)

        # Send async (queued by CAN thread)
        CanBus.get_default('can0').send_async(self.can_id, data)

    # === Blocking Commands (configuration) ===

    def enable(self, enabled: bool) -> bool:
        """Enable/disable motor (blocking until confirmed)"""
        state = 0x01 if enabled else 0x00
        data = [0xF3, state]

        # Add CRC
        crc = self._calculate_crc([self.can_id] + data)
        data.append(crc)

        # Send blocking
        response = CanBus.get_default('can0').send_blocking(
            self.can_id,
            data,
            timeout=1.0
        )

        if response and len(response.data) >= 2:
            return response.data[0] == 0xF3 and response.data[1] == 0x01

        return False

    def set_pid_params(self, kp: int, ki: int, kd: int) -> bool:
        """Set PID parameters (blocking)"""
        data = [0x83, kp, ki, kd]
        crc = self._calculate_crc([self.can_id] + data)
        data.append(crc)

        response = CanBus.get_default('can0').send_blocking(
            self.can_id,
            data,
            timeout=2.0
        )

        return response is not None

    def calibrate_encoder(self) -> bool:
        """Calibrate encoder (blocking, may take 10+ seconds)"""
        data = [0x80]  # Calibrate command
        crc = self._calculate_crc([self.can_id] + data)
        data.append(crc)

        response = CanBus.get_default('can0').send_blocking(
            self.can_id,
            data,
            timeout=15.0  # Long timeout for calibration
        )

        return response is not None

    # === Motor Built-in Position Control ===

    def move_to_position(self, target_pulses: int, speed: int = 100):
        """
        Move to absolute position using motor's controller.

        Motor handles the motion internally with its PID controller.
        """
        # Command format from manual (absolute position move)
        # TODO: Implement based on Servo42D protocol
        pass
```

## Device Example: CAN Sensor (hypothetical)

```python
class CanDistanceSensor(Component):
    """
    Hypothetical CAN distance sensor.

    Shows how ANY CAN device can use the same architecture.
    """

    def __init__(self, can_id: int):
        self.can_id = can_id
        self._distance_m = 0.0
        self._lock = threading.RLock()

    def start(self):
        """Register for distance readings @ 20Hz"""
        bus = CanBus.get_default('can0')

        bus.register_periodic_read(
            can_id=self.can_id,
            command_data=[0x01],  # Read distance command
            callback=self._on_distance_update,
            rate=20.0  # 20Hz updates
        )

    def _on_distance_update(self, msg: can.Message):
        """Callback with distance data"""
        if msg.data[0] == 0x01:
            # Parse distance (example)
            distance_mm = int.from_bytes(msg.data[1:3], byteorder='big')

            with self._lock:
                self._distance_m = distance_mm / 1000.0

    def get_distance(self) -> float:
        """Get cached distance (no CAN traffic)"""
        with self._lock:
            return self._distance_m
```

## Benefits

✅ **Generic** - Works for any CAN device (motors, sensors, displays)
✅ **Clean separation** - CanBus doesn't know device types
✅ **Flexible rates** - Each device chooses update rate (10Hz, 20Hz, etc)
✅ **Both patterns** - Async for real-time, blocking for config
✅ **Efficient** - Single CAN thread handles all devices
✅ **Scalable** - Easy to add new CAN devices

## CAN Traffic Example

```
CAN Bus Thread (running @ ~100Hz check rate):

  t=0ms:    Send encoder read to motor 1 (10Hz)
  t=10ms:   Receive response → callback to motor 1
  t=50ms:   Send distance read to sensor (20Hz)
  t=60ms:   Receive response → callback to sensor
  t=100ms:  Send encoder read to motor 2 (10Hz)
  ...

Main Thread:
  motor.run(100)  → CanBus.send_async() → queued, non-blocking
  motor.enable()  → CanBus.send_blocking() → waits for response
```

## Migration Path

1. Implement generic CanBus with callbacks
2. Update Servo42D to use new CanBus API
3. MecanumDrive odometry uses cached encoder values
4. Add more Servo42D features (PID, position control)
5. Easy to add new CAN devices later

**Want me to implement this?**
