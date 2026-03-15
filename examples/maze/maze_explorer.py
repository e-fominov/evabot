#!/usr/bin/env python3
"""
Simple maze explorer with lidar-feedback movement.

No alignment or centering - just scan walls, pick direction, move with lidar feedback.
set_target_position + continuous wall monitoring provides all the safety needed.

Usage:
    robot run examples/maze/maze_explorer.py
"""

import time
import math
from evabot import Robot, MecanumDrive, RPLidarC1

# Maze parameters
CELL_SIZE = 0.30
WALL_THRESHOLD = 0.25  # >25cm = open
CENTER_DIST = 0.125  # 12.5cm from wall
SAFE_DIST = 0.09  # 9cm emergency stop (robot is 8.5cm from center to edge)

# Movement
MOVE_SPEED = 0.8
MOVE_TIMEOUT = 10.0

# Directions
FRONT = 0
RIGHT = 90
BACK = 180
LEFT = 270

ALL_DIRS = [FRONT, RIGHT, BACK, LEFT]
DIR_NAMES = {FRONT: "Front", RIGHT: "Right", BACK: "Back", LEFT: "Left"}
DIR_DELTA = {FRONT: (1, 0), RIGHT: (0, -1), BACK: (-1, 0), LEFT: (0, 1)}
OPPOSITE = {FRONT: BACK, BACK: FRONT, LEFT: RIGHT, RIGHT: LEFT}
EXPLORE_PRIORITY = [LEFT, BACK, RIGHT, FRONT]


class MazeMap:
    def __init__(self):
        self.visited = set()
        self.walls = {}

    def visit(self, x, y):
        self.visited.add((x, y))

    def set_wall(self, x, y, direction, has_wall):
        self.walls[(x, y, direction)] = has_wall
        dx, dy = DIR_DELTA[direction]
        self.walls[(x + dx, y + dy, OPPOSITE[direction])] = has_wall

    def has_wall(self, x, y, direction):
        return self.walls.get((x, y, direction), None)

    def is_visited(self, x, y):
        return (x, y) in self.visited

    def get_unvisited_neighbors(self, x, y):
        neighbors = []
        for d in EXPLORE_PRIORITY:
            dx, dy = DIR_DELTA[d]
            nx, ny = x + dx, y + dy
            if self.has_wall(x, y, d) is False and not self.is_visited(nx, ny):
                neighbors.append((d, nx, ny))
        return neighbors

    def print_map(self, robot_x, robot_y):
        xs = [x for x, y in self.visited]
        ys = [y for x, y in self.visited]
        if not xs:
            return
        min_x, max_x = min(xs) - 1, max(xs) + 1
        min_y, max_y = min(ys) - 1, max(ys) + 1

        print()
        for y in range(max_y, min_y - 1, -1):
            row_top = ""
            row_mid = ""
            for x in range(min_x, max_x + 1):
                top = self.has_wall(x, y, FRONT)
                row_top += "+"
                row_top += "---" if top is True else "   " if top is False else " . "

                if x == robot_x and y == robot_y:
                    cell = " R "
                elif (x, y) in self.visited:
                    cell = " . "
                else:
                    cell = "   "

                left = self.has_wall(x, y, LEFT)
                row_mid += "|" if left is True else " " if left is False else ":"
                row_mid += cell

            row_top += "+"
            right = self.has_wall(max_x, y, RIGHT)
            row_mid += "|" if right is True else " " if right is False else ":"
            print(row_top)
            print(row_mid)

        row_bot = ""
        for x in range(min_x, max_x + 1):
            bot = self.has_wall(x, min_y, BACK)
            row_bot += "+"
            row_bot += "---" if bot is True else "   " if bot is False else " . "
        row_bot += "+"
        print(row_bot)
        print()


def measure_wall(robot, angle):
    """Single wall measurement."""
    d, a, q = robot.lidar.check_wall(angle)
    if d is not None and q is not None and q > 0.3:
        return d
    return None


def scan_walls(robot):
    """Scan all 4 walls - fast, single reading each."""
    results = {}
    for d in ALL_DIRS:
        dist = measure_wall(robot, d)
        if dist is not None and dist < WALL_THRESHOLD:
            results[d] = (dist, True)
        else:
            results[d] = (dist, False)
    return results


def move_to_cell(robot, direction):
    """
    Move one cell using set_target_position + lidar monitoring.

    Monitors 3 walls (ahead + 2 sides) while moving:
    - Stops at CENTER_DIST from ahead wall
    - Corrects lateral drift to maintain CENTER_DIST from side walls
    - Aligns theta using all visible walls
    """
    opp = OPPOSITE[direction]
    perp_dirs = [d for d in ALL_DIRS if d != direction and d != opp]

    # Movement axes in robot frame
    # main_axis: direction of travel (dx_dir, dy_dir)
    # side_axis: perpendicular correction direction for each side wall
    move_map = {FRONT: (1, 0), BACK: (-1, 0), LEFT: (0, 1), RIGHT: (0, -1)}
    dx_dir, dy_dir = move_map[direction]

    # For side wall corrections: which robot-frame axis to adjust
    # If side wall is too close, move away from it
    side_correction = {}
    for side_dir in perp_dirs:
        sx, sy = move_map[side_dir]
        # Correction is AWAY from the wall (opposite direction)
        side_correction[side_dir] = (-sx, -sy)

    ahead_dist = measure_wall(robot, direction)
    print(f"  Moving {DIR_NAMES[direction]}...")
    if ahead_dist:
        print(f"    Ahead: {ahead_dist*100:.1f}cm")

    start_time = time.time()
    log_interval = 0.2
    last_log = 0
    cycle = 0
    side_data = {}

    while time.time() - start_time < MOVE_TIMEOUT:
        cycle += 1
        t_now = time.time() - start_time

        # --- Read walls: ahead every cycle, sides every 3rd ---
        d_ahead, a_ahead, q_ahead = robot.lidar.check_wall(direction)

        if cycle % 3 == 1 or not side_data:
            side_data = {}
            for sd in perp_dirs:
                d_s, a_s, q_s = robot.lidar.check_wall(sd)
                side_data[sd] = (d_s, a_s, q_s)

        # --- Safety check: only ahead wall gets emergency stop ---
        if d_ahead is not None and d_ahead < SAFE_DIST:
            robot.drive.halt()
            print(f"    SAFETY STOP: {DIR_NAMES[direction]} at {d_ahead*100:.1f}cm")
            return

        # --- Arrived? ---
        if d_ahead is not None and d_ahead <= CENTER_DIST + 0.01:
            robot.drive.halt()
            print(f"    Stopped: {d_ahead*100:.1f}cm from {DIR_NAMES[direction]} wall")
            return

        # --- Calculate forward target (main axis) ---
        if d_ahead is not None:
            remaining = max(d_ahead - CENTER_DIST, 0.01)
        else:
            remaining = CELL_SIZE * 0.5
        target_dx = dx_dir * remaining
        target_dy = dy_dir * remaining

        # --- Lateral correction (side walls) ---
        lat_corrections = {}
        for sd in perp_dirs:
            d_s, _, q_s = side_data[sd]
            if d_s is not None and d_s < CENTER_DIST and q_s is not None and q_s > 0.3:
                correction = (CENTER_DIST - d_s) * 0.5
                cx, cy = side_correction[sd]
                target_dx += cx * correction
                target_dy += cy * correction
                lat_corrections[sd] = correction

        # --- Theta correction from all visible walls ---
        dtheta_deg = 0.0
        angle_samples = {}
        for sd in perp_dirs:
            _, a_s, q_s = side_data[sd]
            if a_s is not None and q_s is not None and q_s > 0.5:
                angle_samples[sd] = a_s
        if a_ahead is not None and q_ahead is not None and q_ahead > 0.5:
            angle_samples[direction] = a_ahead
        if angle_samples:
            avg_angle = sum(angle_samples.values()) / len(angle_samples)
            dtheta_deg = max(-15.0, min(15.0, avg_angle))

        # --- Log ---
        if t_now - last_log >= log_interval:
            last_log = t_now
            parts = [f"ahead={d_ahead*100:.0f}cm" if d_ahead else "ahead=?"]
            for sd in perp_dirs:
                d_s, a_s, q_s = side_data[sd]
                if d_s is not None:
                    parts.append(
                        f"{DIR_NAMES[sd]}={d_s*100:.0f}cm/a={a_s:+.1f}"
                        if a_s is not None
                        else f"{DIR_NAMES[sd]}={d_s*100:.0f}cm"
                    )
            if lat_corrections:
                parts.append(
                    f"lat={','.join(f'{DIR_NAMES[k]}:{v*100:+.1f}cm' for k,v in lat_corrections.items())}"
                )
            parts.append(f"dtheta={dtheta_deg:+.1f}")
            parts.append(f"target=({target_dx*100:.1f},{target_dy*100:.1f})")
            print(f"    [{t_now:.1f}s] {' | '.join(parts)}")

        # --- Send target ---
        robot.drive.set_target_position(
            dx=target_dx,
            dy=target_dy,
            dtheta_deg=dtheta_deg,
            speed=MOVE_SPEED,
            acceleration=50,
        )

        # --- Position control finished ---
        if not robot.drive.is_position_control_active():
            robot.drive.halt()
            print(f"    Position control complete")
            return

        time.sleep(0.01)

    robot.drive.halt()
    print(f"    Timeout!")


def main():
    print("=" * 50)
    print("Maze Explorer")
    print("=" * 50)
    print(f"Cell: {CELL_SIZE*100:.0f}cm | Safe: {SAFE_DIST*100:.0f}cm")
    print(f"Priority: left, back, right, front")
    print()
    print("Starting in 3 seconds...")
    time.sleep(3)

    robot = Robot()
    robot.drive = MecanumDrive()
    robot.lidar = RPLidarC1(max_range=1.0)
    robot.start()
    time.sleep(3)

    maze = MazeMap()
    cell_x, cell_y = 0, 0
    move_times = []

    try:
        t_total_start = time.time()

        for step in range(100):
            t_step_start = time.time()
            print()
            print("=" * 50)
            print(f"CELL ({cell_x}, {cell_y}) - Step {step + 1}")
            print("=" * 50)

            # Scan
            t_scan = time.time()
            wall_scan = scan_walls(robot)
            t_scan = time.time() - t_scan
            for d in ALL_DIRS:
                dist, has_wall = wall_scan[d]
                status = f"{dist*100:.1f}cm WALL" if has_wall else "OPEN"
                print(f"  {DIR_NAMES[d]:6s}: {status}")
            print(f"  (scan: {t_scan*1000:.0f}ms)")

            # Update map
            maze.visit(cell_x, cell_y)
            for d in ALL_DIRS:
                _, has_wall = wall_scan[d]
                maze.set_wall(cell_x, cell_y, d, has_wall)

            maze.print_map(cell_x, cell_y)

            # Find next
            neighbors = maze.get_unvisited_neighbors(cell_x, cell_y)
            if not neighbors:
                print("  No unvisited neighbors - done!")
                break

            direction, nx, ny = neighbors[0]
            print(f"  Next: {DIR_NAMES[direction]} -> ({nx}, {ny})")

            # Move
            t_move = time.time()
            move_to_cell(robot, direction)
            t_move = time.time() - t_move
            move_times.append(t_move)
            cell_x, cell_y = nx, ny

            t_step = time.time() - t_step_start
            print(
                f"  Step time: {t_step:.2f}s (move: {t_move:.2f}s, scan: {t_scan*1000:.0f}ms)"
            )
            time.sleep(0.3)

        t_total = time.time() - t_total_start

        print()
        print("=" * 50)
        print(f"DONE - visited {len(maze.visited)} cells in {t_total:.1f}s")
        print("=" * 50)
        if move_times:
            print(f"  Move times: {', '.join(f'{t:.2f}s' for t in move_times)}")
            print(f"  Avg move:   {sum(move_times)/len(move_times):.2f}s")
            print(f"  Total move: {sum(move_times):.1f}s")
            print(f"  Overhead:   {t_total - sum(move_times):.1f}s")
        maze.print_map(cell_x, cell_y)

    except KeyboardInterrupt:
        t_total = time.time() - t_total_start
        print(f"\nInterrupted after {t_total:.1f}s, visited {len(maze.visited)} cells")
        maze.print_map(cell_x, cell_y)

    robot.drive.halt()
    time.sleep(0.3)
    robot.stop()


if __name__ == "__main__":
    main()
