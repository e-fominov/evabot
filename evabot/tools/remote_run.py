#!/usr/bin/env python3
"""
Remote Run Tool for EvaBot

Copies and executes Python scripts on the robot (Raspberry Pi) via SSH/SCP.
Uses .env file for configuration.

Usage:
    evabot-remote run <script.py>              # Run script on robot
    evabot-remote run <script.py> --args "arg1 arg2"  # With arguments
    evabot-remote copy <file>                  # Just copy file
    evabot-remote shell                        # Open SSH shell
    evabot-remote install                      # Install evabot on robot

Configuration (.env file):
    ROBOT_HOST=192.168.1.100    # Robot IP or hostname
    ROBOT_USER=pi               # SSH username (default: pi)
    ROBOT_PASS=raspberry        # SSH password (optional if using keys)
    ROBOT_DIR=/home/pi/evabot   # Remote directory (default: ~/evabot)
"""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path
from typing import Optional


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def load_env():
    """Load configuration from .env file or shared config"""
    # Check for local .env first (project-specific override)
    env_file = Path.cwd() / '.env'

    # Fall back to shared config
    if not env_file.exists():
        env_file = Path.home() / '.evabot_config'

    if not env_file.exists():
        print(f"{Colors.RED}✗ Error: Robot configuration not found{Colors.RESET}")
        print(f"\nRun setup first:")
        print(f"  {Colors.BOLD}robot setup{Colors.RESET}")
        print(f"\nThis will configure your robot connection settings.")
        sys.exit(1)

    # Load config file
    env_vars = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()

    # Extract configuration
    config = {
        'host': env_vars.get('ROBOT_HOST'),
        'user': env_vars.get('ROBOT_USER', 'pi'),
        'password': env_vars.get('ROBOT_PASS'),
        'remote_dir': env_vars.get('ROBOT_DIR', '/home/pi/evabot'),
    }

    if not config['host']:
        print(f"{Colors.RED}✗ Error: ROBOT_HOST not set in .env{Colors.RESET}")
        sys.exit(1)

    return config


def run_ssh_command(config: dict, command: str, interactive: bool = False) -> int:
    """Run command on robot via SSH"""
    ssh_cmd = [
        'ssh',
        '-o', 'StrictHostKeyChecking=no',
        '-o', 'UserKnownHostsFile=/dev/null',
        '-o', 'LogLevel=ERROR',
        f"{config['user']}@{config['host']}",
        command
    ]

    if interactive:
        # Interactive shell
        ssh_cmd = [
            'ssh',
            '-o', 'StrictHostKeyChecking=no',
            '-t',
            f"{config['user']}@{config['host']}",
        ]
        return subprocess.call(ssh_cmd)
    else:
        # Run command and stream output
        process = subprocess.Popen(
            ssh_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # Stream output line by line
        for line in iter(process.stdout.readline, ''):
            if line:
                print(line, end='')

        process.wait()
        return process.returncode


def copy_file(config: dict, local_path: Path, remote_path: Optional[str] = None) -> bool:
    """Copy file to robot via SCP"""
    if not local_path.exists():
        print(f"{Colors.RED}✗ Error: File not found: {local_path}{Colors.RESET}")
        return False

    if remote_path is None:
        remote_path = f"{config['remote_dir']}/{local_path.name}"

    scp_cmd = [
        'scp',
        '-o', 'StrictHostKeyChecking=no',
        '-o', 'UserKnownHostsFile=/dev/null',
        '-o', 'LogLevel=ERROR',
        str(local_path),
        f"{config['user']}@{config['host']}:{remote_path}"
    ]

    print(f"{Colors.BLUE}→ Copying {local_path.name} to robot...{Colors.RESET}")
    result = subprocess.call(scp_cmd)

    if result == 0:
        print(f"{Colors.GREEN}✓ File copied to {remote_path}{Colors.RESET}")
        return True
    else:
        print(f"{Colors.RED}✗ Copy failed{Colors.RESET}")
        return False


def ensure_remote_dir(config: dict):
    """Ensure remote directory exists"""
    cmd = f"mkdir -p {config['remote_dir']}"
    run_ssh_command(config, cmd)


def setup_can_on_robot(config: dict):
    """Setup CAN bus on robot before running scripts"""
    print(f"{Colors.BLUE}→ Setting up CAN bus...{Colors.RESET}")
    # Try venv first, fallback to system python
    # Use -u flag for unbuffered output (real-time display)
    cmd = f"cd {config['remote_dir']} && (./venv/bin/python -u -m evabot.tools.setup_can || python3 -u -m evabot.tools.setup_can)"
    returncode = run_ssh_command(config, cmd)
    print()
    return returncode == 0


def run_script(config: dict, script_path: Path, args: str = ""):
    """Copy and run Python script on robot"""
    print(f"{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}EvaBot Remote Runner{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"Robot: {config['user']}@{config['host']}")
    print(f"Script: {script_path}")
    print(f"{'=' * 60}\n")

    # Ensure remote directory exists
    ensure_remote_dir(config)

    # Setup CAN bus
    setup_can_on_robot(config)

    # Copy script to robot
    remote_script = f"{config['remote_dir']}/{script_path.name}"
    if not copy_file(config, script_path, remote_script):
        return 1

    print()

    # Run script on robot
    print(f"{Colors.BLUE}→ Running script on robot...{Colors.RESET}")
    print(f"{Colors.YELLOW}{'=' * 60}{Colors.RESET}\n")

    # Build python command (use venv if available, fallback to system python)
    # Use -u flag for unbuffered output (real-time display)
    python_cmd = f"cd {config['remote_dir']} && (./venv/bin/python -u {script_path.name} {args} || python3 -u {script_path.name} {args})"

    returncode = run_ssh_command(config, python_cmd)

    print(f"\n{Colors.YELLOW}{'=' * 60}{Colors.RESET}")

    if returncode == 0:
        print(f"{Colors.GREEN}✓ Script completed successfully{Colors.RESET}")
    else:
        print(f"{Colors.RED}✗ Script exited with code {returncode}{Colors.RESET}")

    return returncode


def install_evabot(config: dict):
    """Install evabot library on robot"""
    print(f"{Colors.BOLD}Installing EvaBot on robot...{Colors.RESET}\n")

    # Ensure remote directory exists
    ensure_remote_dir(config)

    # Get project root
    project_root = Path(__file__).parent.parent.parent

    # First, copy setup_can.py for initial CAN configuration
    print(f"{Colors.BLUE}→ Copying CAN setup script...{Colors.RESET}")
    setup_can_script = project_root / 'evabot' / 'tools' / 'setup_can.py'
    if setup_can_script.exists():
        copy_file(config, setup_can_script, f"{config['remote_dir']}/setup_can.py")
    print()

    # Copy entire evabot package
    print(f"{Colors.BLUE}→ Copying evabot package...{Colors.RESET}")

    rsync_cmd = [
        'rsync',
        '-avz',
        '--exclude', '__pycache__',
        '--exclude', '*.pyc',
        '--exclude', '.git',
        '--exclude', 'tests',
        '--exclude', 'lessons',
        '-e', 'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR',
        str(project_root / 'evabot') + '/',
        f"{config['user']}@{config['host']}:{config['remote_dir']}/evabot/"
    ]

    result = subprocess.call(rsync_cmd)

    if result != 0:
        print(f"{Colors.RED}✗ Failed to copy package{Colors.RESET}")
        return 1

    print(f"{Colors.GREEN}✓ Package copied{Colors.RESET}\n")

    # Copy setup files
    print(f"{Colors.BLUE}→ Copying setup files...{Colors.RESET}")
    for file in ['pyproject.toml', 'setup.py']:
        file_path = project_root / file
        if file_path.exists():
            copy_file(config, file_path, f"{config['remote_dir']}/{file}")

    print()

    # Create virtual environment
    print(f"{Colors.BLUE}→ Creating virtual environment...{Colors.RESET}")
    venv_cmd = f"cd {config['remote_dir']} && python3 -m venv venv"
    returncode = run_ssh_command(config, venv_cmd)

    if returncode != 0:
        print(f"\n{Colors.RED}✗ Failed to create venv{Colors.RESET}")
        return returncode

    print(f"{Colors.GREEN}✓ Virtual environment created{Colors.RESET}\n")

    # Install on robot (in venv)
    print(f"{Colors.BLUE}→ Installing package in venv...{Colors.RESET}")
    install_cmd = f"cd {config['remote_dir']} && ./venv/bin/pip install -e ."

    returncode = run_ssh_command(config, install_cmd)

    if returncode != 0:
        print(f"\n{Colors.RED}✗ Installation failed{Colors.RESET}")
        return returncode

    print(f"\n{Colors.GREEN}✓ EvaBot installed successfully in venv{Colors.RESET}\n")

    # Setup CAN bus
    print(f"{Colors.BLUE}→ Setting up CAN bus...{Colors.RESET}")
    setup_can_on_robot(config)

    print(f"{Colors.GREEN}✓ Robot ready!{Colors.RESET}")
    return 0


def setup_config():
    """Interactive setup for robot configuration"""
    config_file = Path.home() / '.evabot_config'

    print(f"{Colors.BOLD}EvaBot Robot Setup{Colors.RESET}")
    print(f"{'=' * 60}\n")

    # Check if config already exists
    if config_file.exists():
        print(f"{Colors.YELLOW}Configuration already exists:{Colors.RESET}")
        with open(config_file) as f:
            print(f.read())
        print()
        response = input(f"Overwrite existing configuration? [y/N]: ")
        if response.lower() != 'y':
            print(f"{Colors.BLUE}Setup cancelled{Colors.RESET}")
            return 0

    # Prompt for configuration
    print(f"Enter your robot connection settings:\n")

    robot_host = input(f"Robot hostname or IP [default: rpi]: ").strip()
    if not robot_host:
        robot_host = "rpi"

    robot_user = input(f"SSH username [default: pi]: ").strip()
    if not robot_user:
        robot_user = "pi"

    robot_dir = input(f"Remote directory [default: /home/pi/evabot]: ").strip()
    if not robot_dir:
        robot_dir = "/home/pi/evabot"

    # Write configuration
    config_content = f"""# EvaBot Robot Configuration
# Created by robot setup command

ROBOT_HOST={robot_host}
ROBOT_USER={robot_user}
ROBOT_DIR={robot_dir}
"""

    with open(config_file, 'w') as f:
        f.write(config_content)

    print(f"\n{Colors.GREEN}✓ Configuration saved to {config_file}{Colors.RESET}\n")
    print(f"Configuration:")
    print(f"  Host: {robot_host}")
    print(f"  User: {robot_user}")
    print(f"  Directory: {robot_dir}")
    print(f"\nNext steps:")
    print(f"  {Colors.BOLD}robot install{Colors.RESET}     # Install evabot on robot")
    print(f"  {Colors.BOLD}robot lesson 1.1{Colors.RESET}  # Start first lesson")

    return 0


def create_lesson(lesson_num: str, include_solution: bool = False):
    """
    Create lesson directory from template.

    Args:
        lesson_num: Lesson number (e.g., '1.2', '1.5')
        include_solution: Whether to include solution.py
    """
    # Parse lesson number
    parts = lesson_num.split('.')
    if len(parts) != 2:
        print(f"{Colors.RED}✗ Error: Lesson number must be in format 'X.Y' (e.g., '1.2'){Colors.RESET}")
        return 1

    level, lesson = parts
    lesson_dir_name = f"lesson{level}_{lesson}"

    # Find evabot package location
    try:
        import evabot
        evabot_path = Path(evabot.__file__).parent.parent
    except ImportError:
        print(f"{Colors.RED}✗ Error: evabot package not installed{Colors.RESET}")
        print(f"  Run: pip install -e /path/to/evabot")
        return 1

    # Find source lesson directory
    source_base = evabot_path / 'lessons' / f'level{level}_single_motor' / f'lesson{lesson}_*'

    # Find matching lesson directory
    import glob
    matches = glob.glob(str(source_base))

    if not matches:
        print(f"{Colors.RED}✗ Error: Lesson {lesson_num} not found{Colors.RESET}")
        print(f"  Searched: {source_base}")
        return 1

    source_lesson = Path(matches[0])

    # Create destination directory
    dest_lesson = Path.cwd() / lesson_dir_name

    if dest_lesson.exists():
        print(f"{Colors.YELLOW}! Warning: {lesson_dir_name}/ already exists{Colors.RESET}")
        response = input("Overwrite? [y/N]: ")
        if response.lower() != 'y':
            print(f"{Colors.BLUE}Cancelled{Colors.RESET}")
            return 0
        shutil.rmtree(dest_lesson)

    dest_lesson.mkdir(parents=True)

    print(f"{Colors.BOLD}Creating Lesson {lesson_num}{Colors.RESET}")
    print(f"Source: {source_lesson.name}")
    print(f"Destination: {dest_lesson}\n")

    # Copy README.md
    readme_src = source_lesson / 'README.md'
    if readme_src.exists():
        shutil.copy2(readme_src, dest_lesson / 'README.md')
        print(f"{Colors.GREEN}✓ Copied README.md{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}! Warning: README.md not found{Colors.RESET}")

    # Copy template.py
    template_src = source_lesson / 'template.py'
    if template_src.exists():
        shutil.copy2(template_src, dest_lesson / 'template.py')
        print(f"{Colors.GREEN}✓ Copied template.py{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}! Warning: template.py not found{Colors.RESET}")

    # Copy solution.py if requested
    if include_solution:
        solution_src = source_lesson / 'solution.py'
        if solution_src.exists():
            shutil.copy2(solution_src, dest_lesson / 'solution.py')
            print(f"{Colors.GREEN}✓ Copied solution.py{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}! Warning: solution.py not found{Colors.RESET}")

    print(f"\n{Colors.GREEN}✓ Lesson created: {lesson_dir_name}/{Colors.RESET}")
    print(f"\nNext steps:")
    print(f"  cd {lesson_dir_name}")
    print(f"  cat README.md          # Read lesson instructions")
    print(f"  nano template.py       # Write your solution")
    print(f"  robot run template.py  # Run on robot")

    return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='EvaBot Robot Control - Run scripts and manage lessons',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Setup command
    subparsers.add_parser('setup', help='Configure robot connection settings')

    # Lesson command
    lesson_parser = subparsers.add_parser('lesson', help='Create lesson from template')
    lesson_parser.add_argument('number', type=str, help='Lesson number (e.g., 1.2, 1.5)')
    lesson_parser.add_argument('--solution', action='store_true', help='Include solution.py')

    # Run command
    run_parser = subparsers.add_parser('run', help='Run script on robot')
    run_parser.add_argument('script', type=str, help='Python script to run')
    run_parser.add_argument('script_args', nargs='*', help='Arguments to pass to script (use -- separator)')
    run_parser.add_argument('--args', type=str, default='', help='(Deprecated) Use positional args instead')

    # Copy command
    copy_parser = subparsers.add_parser('copy', help='Copy file to robot')
    copy_parser.add_argument('file', type=str, help='File to copy')

    # Shell command
    subparsers.add_parser('shell', help='Open SSH shell to robot')

    # Install command
    subparsers.add_parser('install', help='Install evabot package on robot')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    if args.command == 'setup':
        return setup_config()

    if args.command == 'lesson':
        return create_lesson(args.number, args.solution)

    # Load configuration (not needed for setup/lesson commands)
    config = load_env()

    if args.command == 'run':
        script_path = Path(args.script)
        # Use script_args if provided, fallback to deprecated --args
        script_args_str = ' '.join(args.script_args) if args.script_args else args.args
        return run_script(config, script_path, script_args_str)

    elif args.command == 'copy':
        file_path = Path(args.file)
        return 0 if copy_file(config, file_path) else 1

    elif args.command == 'shell':
        print(f"{Colors.BLUE}→ Opening SSH shell to {config['user']}@{config['host']}...{Colors.RESET}\n")
        return run_ssh_command(config, '', interactive=True)

    elif args.command == 'install':
        return install_evabot(config)

    return 0


if __name__ == '__main__':
    sys.exit(main())
