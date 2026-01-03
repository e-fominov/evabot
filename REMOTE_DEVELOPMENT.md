# Remote Development Guide

Run Python scripts on your robot (Raspberry Pi) from your development machine.

## Quick Start

### 1. Configure Your Robot Connection

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your robot's details:

```bash
ROBOT_HOST=192.168.1.100    # Your robot's IP or hostname
ROBOT_USER=pi               # SSH username (default: pi)
ROBOT_DIR=/home/pi/evabot   # Remote directory
```

### 2. Install EvaBot on Robot (One Time)

First, install the package on your robot:

```bash
# Using installed command (after pip install -e .)
evabot-remote install

# OR using standalone script
python3 run_remote.py install
```

This will:
- Copy the evabot package to the robot
- Install dependencies
- Make it available for import

### 3. Run Scripts Remotely

Run any Python script on your robot:

```bash
# Run a lesson
evabot-remote run lessons/level1_single_motor/lesson1_make_it_spin/solution.py

# Run integration test
evabot-remote run tests/integration/test_single_motor.py

# Run with arguments
evabot-remote run my_script.py --args "--speed 40 --time 5"

# Using standalone script (no installation)
python3 run_remote.py lessons/level1_single_motor/lesson1_make_it_spin/solution.py
```

## Commands

### Run Script

```bash
evabot-remote run <script.py>
```

Copies the script to robot and executes it. Output is streamed to your terminal in real-time.

**Options:**
- `--args "arg1 arg2"` - Pass arguments to the script

**Example:**
```bash
evabot-remote run tests/integration/test_single_motor.py
```

### Copy File

```bash
evabot-remote copy <file>
```

Just copies a file to the robot without running it.

**Example:**
```bash
evabot-remote copy my_config.json
```

### Open SSH Shell

```bash
evabot-remote shell
```

Opens an interactive SSH session to your robot.

### Install/Update Package

```bash
evabot-remote install
```

Copies the entire evabot package to robot and installs it. Run this:
- First time setup
- After making changes to the library code
- To update the robot with latest version

## Typical Workflow

### For Running Lessons

Students can run lessons directly on the robot:

```bash
# Copy .env.example to .env and configure
cp .env.example .env
nano .env

# Run a lesson
python3 run_remote.py lessons/level1_single_motor/lesson1_make_it_spin/solution.py
```

### For Development

When developing new features:

```bash
# 1. Make code changes locally
nano evabot/components/motors/servo42d.py

# 2. Update robot with new code
evabot-remote install

# 3. Run tests on robot
evabot-remote run tests/integration/test_single_motor.py
```

### For Quick Testing

Test a script without installing:

```bash
# Edit script
nano test_my_feature.py

# Run directly (script is copied, not installed)
evabot-remote run test_my_feature.py
```

## Configuration Options

### .env File

```bash
# Required
ROBOT_HOST=192.168.1.100           # Robot IP or hostname

# Optional (defaults shown)
ROBOT_USER=pi                      # SSH username
ROBOT_DIR=/home/pi/evabot          # Remote directory
ROBOT_PASS=raspberry               # Password (if not using SSH keys)
```

### Finding Your Robot's IP

**On the robot:**
```bash
hostname -I
```

**From your computer:**
```bash
# If using hostname
ping raspberrypi.local

# Scan network
nmap -sn 192.168.1.0/24 | grep -i raspberry
```

## SSH Key Setup (Recommended)

For passwordless access, set up SSH keys:

```bash
# Generate key (if you don't have one)
ssh-keygen -t ed25519

# Copy to robot
ssh-copy-id pi@192.168.1.100

# Test
ssh pi@192.168.1.100
```

Then you can omit `ROBOT_PASS` from `.env`.

## Troubleshooting

### "Connection refused"

**Problem:** Can't connect to robot

**Solutions:**
- Verify robot IP: `ping <ROBOT_HOST>`
- Check SSH is enabled on robot
- Verify firewall settings

### "Permission denied"

**Problem:** SSH authentication fails

**Solutions:**
- Check username in .env
- Verify password or SSH key
- Try: `ssh pi@<ROBOT_HOST>` to test manually

### "No such file or directory"

**Problem:** Script not found

**Solutions:**
- Check script path is correct
- Use relative path from project root
- Verify file exists: `ls <script.py>`

### "Module not found"

**Problem:** Import errors when running on robot

**Solutions:**
- Run `evabot-remote install` to install package on robot
- Check dependencies are installed on robot
- Verify robot has python3-can: `ssh pi@<ROBOT_HOST> 'pip3 list | grep can'`

## Examples

### Run Lesson 1

```bash
# Configure robot
echo "ROBOT_HOST=192.168.1.100" > .env

# Install on robot (first time)
python3 run_remote.py install

# Run the lesson
python3 run_remote.py lessons/level1_single_motor/lesson1_make_it_spin/solution.py
```

### Run Integration Tests

```bash
# Single motor test
evabot-remote run tests/integration/test_single_motor.py

# Four motor test
evabot-remote run tests/integration/test_four_motors.py
```

### Debug on Robot

```bash
# Open shell
evabot-remote shell

# On robot, run manually
cd /home/pi/evabot
python3 tests/integration/test_single_motor.py
```

## Robot Setup Requirements

Your robot needs:

1. **SSH Server**
   ```bash
   sudo systemctl enable ssh
   sudo systemctl start ssh
   ```

2. **Python 3**
   ```bash
   python3 --version  # Should be 3.8+
   ```

3. **CAN Bus Tools**
   ```bash
   sudo apt-get install can-utils
   ```

4. **Python CAN Library**
   ```bash
   pip3 install python-can
   ```

5. **CAN Interface Configured**
   ```bash
   # Add to /etc/network/interfaces
   auto can0
   iface can0 inet manual
       pre-up /sbin/ip link set can0 type can bitrate 500000
       up /sbin/ifconfig can0 up
       down /sbin/ifconfig can0 down
   ```

## Advanced Usage

### Run with Custom Python

```bash
evabot-remote run my_script.py --args "--python python3.11"
```

### Copy Multiple Files

```bash
for file in *.json; do
    evabot-remote copy "$file"
done
```

### Monitor Robot Logs

```bash
evabot-remote shell
# On robot:
tail -f /var/log/syslog | grep python
```

## See Also

- [README.md](README.md) - Main project documentation
- [LEARNING_PLAN.md](LEARNING_PLAN.md) - Lesson structure
- [lessons/](lessons/) - Tutorial lessons
