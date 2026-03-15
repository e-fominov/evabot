#!/usr/bin/env python3
"""
Simple maze explorer with lidar-feedback movement.

Uses robot.move_to_wall() for safe cell-to-cell navigation.

Usage:
    robot run examples/maze/maze_explorer.py
"""

import time
from evabot import Robot, MecanumDrive, RPLidarC1

# Maze parameters
CELL_SIZE = 0.30
WALL_THRESHOLD = 0.25  # >25cm = open
CENTER_DIST = 0.125

# Movement
MOVE_SPEED = 0.3

# Directions (lidar angles)
FRONT = 0
RIGHT = 90
BACK = 180
LEFT = 270

ALL_DIRS = [FRONT, RIGHT, BACK, LEFT]
DIR_NAMES = {FRONT: "Front", RIGHT: "Right", BACK: "Back", LEFT: "Left"}
DIR_DELTA = {FRONT: (1, 0), RIGHT: (0, -1), BACK: (-1, 0), LEFT: (0, 1)}
OPPOSITE = {FRONT: BACK, BACK: FRONT, LEFT: RIGHT, RIGHT: LEFT}
EXPLORE_PRIORITY = [LEFT, BACK, RIGHT, FRONT]

# Map state
visited = set()
walls = {}


def set_wall(x, y, direction, has_wall):
    walls[(x, y, direction)] = has_wall
    dx, dy = DIR_DELTA[direction]
    walls[(x + dx, y + dy, OPPOSITE[direction])] = has_wall


def get_unvisited_neighbors(x, y):
    neighbors = []
    for d in EXPLORE_PRIORITY:
        dx, dy = DIR_DELTA[d]
        nx, ny = x + dx, y + dy
        if walls.get((x, y, d)) is False and (nx, ny) not in visited:
            neighbors.append((d, nx, ny))
    return neighbors


def scan_walls(robot):
    results = {}
    for d in ALL_DIRS:
        dist, _, q = robot.lidar.check_wall(d)
        if dist is not None and q is not None and q > 0.3 and dist < WALL_THRESHOLD:
            results[d] = (dist, True)
        else:
            results[d] = (dist, False)
    return results


def main():
    print("=" * 50)
    print("Maze Explorer")
    print("=" * 50)

    robot = Robot()
    robot.drive = MecanumDrive()
    robot.lidar = RPLidarC1(max_range=1.0)
    robot.start()
    time.sleep(3)

    cell_x, cell_y = 0, 0
    move_times = []

    try:
        t_total_start = time.time()

        for step in range(100):
            t_step_start = time.time()
            print()
            print(f"--- CELL ({cell_x}, {cell_y}) - Step {step + 1} ---")

            # Scan
            t_scan = time.time()
            wall_scan = scan_walls(robot)
            t_scan = time.time() - t_scan
            for d in ALL_DIRS:
                dist, has_wall = wall_scan[d]
                status = f"{dist*100:.1f}cm WALL" if has_wall else "OPEN"
                print(f"  {DIR_NAMES[d]:6s}: {status}")

            # Update map
            visited.add((cell_x, cell_y))
            for d in ALL_DIRS:
                _, has_wall = wall_scan[d]
                set_wall(cell_x, cell_y, d, has_wall)

            # Find next
            neighbors = get_unvisited_neighbors(cell_x, cell_y)
            if not neighbors:
                print("  No unvisited neighbors - done!")
                break

            direction, nx, ny = neighbors[0]
            print(f"  Next: {DIR_NAMES[direction]} -> ({nx}, {ny})")

            # Move using robot.move_to_wall()
            t_move = time.time()
            robot.move_to_wall(direction, stop_distance=CENTER_DIST, speed=MOVE_SPEED)
            t_move = time.time() - t_move
            move_times.append(t_move)
            cell_x, cell_y = nx, ny

            t_step = time.time() - t_step_start
            print(f"  Step: {t_step:.2f}s (move: {t_move:.2f}s, scan: {t_scan*1000:.0f}ms)")

        t_total = time.time() - t_total_start

        print()
        print("=" * 50)
        print(f"DONE - {len(visited)} cells in {t_total:.1f}s")
        print("=" * 50)
        if move_times:
            print(f"  Avg move: {sum(move_times)/len(move_times):.2f}s")
            print(f"  Total:    {sum(move_times):.1f}s move + {t_total - sum(move_times):.1f}s overhead")

    except KeyboardInterrupt:
        t_total = time.time() - t_total_start
        print(f"\nInterrupted after {t_total:.1f}s, {len(visited)} cells")

    robot.drive.halt()
    time.sleep(0.3)
    robot.stop()


if __name__ == "__main__":
    main()
