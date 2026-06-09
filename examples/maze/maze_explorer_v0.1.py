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
WALL_THRESHOLD = 0.25   # >25cm = open
CENTER_DIST = 0.125     # 12.5cm from wall
SAFE_DIST = 0.09        # 9cm emergency stop (robot is 8.5cm from center to edge)

# Movement
MOVE_SPEED = 0.12
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

    Monitors the wall AHEAD (in movement direction) and stops at CENTER_DIST.
    Also checks ALL walls for safety every cycle.
    """
    opp = OPPOSITE[direction]

    # Measure starting distances
    ahead_dist = measure_wall(robot, direction)
    behind_dist = measure_wall(robot, opp)

    # Movement in robot frame
    move_map = {FRONT: (1, 0), BACK: (-1, 0), LEFT: (0, 1), RIGHT: (0, -1)}
    dx_dir, dy_dir = move_map[direction]

    # Set target: exactly one cell
    dx = dx_dir * CELL_SIZE
    dy = dy_dir * CELL_SIZE

    # Pick best perpendicular wall to align to during movement (closest, best quality)
    perp_dirs = [d for d in ALL_DIRS if d != direction and d != opp]
    align_wall = None
    best_quality = 0
    for d in perp_dirs:
        dist_d, angle_d, q_d = robot.lidar.check_wall(d)
        if dist_d is not None and q_d is not None and q_d > best_quality and dist_d < WALL_THRESHOLD:
            best_quality = q_d
            align_wall = d

    print(f"  Moving {DIR_NAMES[direction]}...")
    if ahead_dist:
        print(f"    Ahead: {ahead_dist*100:.1f}cm")
    if align_wall is not None:
        print(f"    Aligning to: {DIR_NAMES[align_wall]} wall")

    robot.drive.set_target_position(dx=dx, dy=dy, speed=MOVE_SPEED, acceleration=50)

    start_time = time.time()
    while time.time() - start_time < MOVE_TIMEOUT:
        # Check wall ahead
        d_ahead, angle_ahead, q_ahead = robot.lidar.check_wall(direction)

        if d_ahead is not None:
            # Emergency stop
            if d_ahead < SAFE_DIST:
                robot.drive.halt()
                print(f"    SAFETY STOP: {DIR_NAMES[direction]} wall at {d_ahead*100:.1f}cm")
                return

            # Reached center of new cell (wall ahead at ~15cm)
            if d_ahead <= CENTER_DIST + 0.01:
                robot.drive.halt()
                print(f"    Stopped: {d_ahead*100:.1f}cm from {DIR_NAMES[direction]} wall")
                return

        # Get heading correction from chosen alignment wall
        # Scale down to avoid overcorrection (K_angular in lookahead amplifies this)
        dtheta_deg = 0.0
        if align_wall is not None:
            _, angle_err, q_wall = robot.lidar.check_wall(align_wall)
            if angle_err is not None and q_wall is not None and q_wall > 0.5:
                dtheta_deg = max(-3.0, min(3.0, angle_err * 0.3))
        # Fallback to ahead wall
        if dtheta_deg == 0.0 and angle_ahead is not None and q_ahead is not None and q_ahead > 0.5:
            dtheta_deg = max(-3.0, min(3.0, angle_ahead * 0.3))

        # Update target with heading correction (like phase6g)
        remaining_ahead = d_ahead - CENTER_DIST if d_ahead is not None else CELL_SIZE * 0.5
        remaining = max(remaining_ahead, 0.01)
        new_dx = dx_dir * remaining
        new_dy = dy_dir * remaining
        robot.drive.set_target_position(dx=new_dx, dy=new_dy, dtheta_deg=dtheta_deg,
                                        speed=MOVE_SPEED, acceleration=50)

        # Check perpendicular walls for safety
        for perp_dir in perp_dirs:
            d_perp, _, _ = robot.lidar.check_wall(perp_dir)
            if d_perp is not None and d_perp < SAFE_DIST:
                robot.drive.halt()
                print(f"    SAFETY STOP: {DIR_NAMES[perp_dir]} wall at {d_perp*100:.1f}cm")
                return

        # Position control finished (moved full distance)
        if not robot.drive.is_position_control_active():
            robot.drive.halt()
            print(f"    Position control complete")
            return

        time.sleep(0.02)

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

    try:
        for step in range(100):
            print()
            print("=" * 50)
            print(f"CELL ({cell_x}, {cell_y}) - Step {step + 1}")
            print("=" * 50)

            # Scan
            wall_scan = scan_walls(robot)
            for d in ALL_DIRS:
                dist, has_wall = wall_scan[d]
                status = f"{dist*100:.1f}cm WALL" if has_wall else "OPEN"
                print(f"  {DIR_NAMES[d]:6s}: {status}")

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
            move_to_cell(robot, direction)
            cell_x, cell_y = nx, ny
            time.sleep(0.3)

        print()
        print("=" * 50)
        print(f"DONE - visited {len(maze.visited)} cells")
        print("=" * 50)
        maze.print_map(cell_x, cell_y)

    except KeyboardInterrupt:
        print("\nInterrupted!")
        maze.print_map(cell_x, cell_y)

    robot.drive.halt()
    time.sleep(0.3)
    robot.stop()


if __name__ == "__main__":
    main()
