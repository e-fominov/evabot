#!/usr/bin/env python3
"""
Standalone Remote Run Script (no installation required)

Simple wrapper to run scripts on the robot without installing evabot package.
Just needs Python 3 and standard library.

Usage:
    python3 run_remote.py <script.py>
    python3 run_remote.py lessons/level1_single_motor/lesson1_make_it_spin/solution.py

Requires .env file with ROBOT_HOST configured.
"""

import sys
from pathlib import Path

# Add evabot to path
sys.path.insert(0, str(Path(__file__).parent))

from evabot.tools.remote_run import main

if __name__ == '__main__':
    sys.exit(main())
