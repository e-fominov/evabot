#!/usr/bin/env python3
"""
Simple maze explorer with lidar-feedback movement.

No alignment or centering - just scan walls, pick direction, move with lidar feedback.
set_target_position + continuous wall monitoring provides all the safety needed.

Usage:
    robot run examples/maze/maze_explorer.py
"""

import time
from evabot import Robot, MecanumDrive, RPLidarC1

# Maze parameters
CELL_SIZE = 0.30
WALL_THRESHOLD = 0.25  # >25cm = open
CENTER_DIST = 0.125  # 12.5cm from wall = stop distance
MIN_DIST = 0.10  # 10cm = start pushing away from wall
SAFE_DIST = 0.09  # 9cm = emergency stop

# Movement
MOVE_SPEED = 0.3
MOVE_TIMEOUT = 10.0

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

# Map state (globals)
visited = set()  # set of (x, y)
walls = {}  # (x, y, direction) -> bool


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
    """Scan all 4 walls, return {direction: (distance, has_wall)}."""
    results = {}
    for d in ALL_DIRS:
        dist, _, q = robot.lidar.check_wall(d)
        if dist is not None and q is not None and q > 0.3 and dist < WALL_THRESHOLD:
            results[d] = (dist, True)
        else:
            results[d] = (dist, False)
    return results


def move_to_cell(robot, direction):
    """
    Move one cell using set_target_position + lidar monitoring.

    Every cycle reads all visible walls and:
    - Moves toward direction, stops at CENTER_DIST from ahead wall
    - Pushes away from ANY wall closer than MIN_DIST
    - Aligns theta using angle_error from all visible walls
    - Emergency stops if any wall < SAFE_DIST in movement direction
    """
    opp = OPPOSITE[direction]
    dx_dir, dy_dir = DIR_DELTA[direction]

    ahead_dist, _, _ = robot.lidar.check_wall(direction)
    print(f"  Moving {DIR_NAMES[direction]}...", end="")
    if ahead_dist:
        print(f" (ahead: {ahead_dist*100:.1f}cm)", end="")
    print()

    cycle = 0
    start_time = time.time()

    while time.time() - start_time < MOVE_TIMEOUT:
        cycle += 1

        # --- Read ahead wall every cycle ---
        d_ahead, a_ahead, q_ahead = robot.lidar.check_wall(direction)

        # --- Safety: emergency stop if too close ahead ---
        if d_ahead is not None and d_ahead < SAFE_DIST:
            robot.drive.halt()
            print(f"    SAFETY STOP: {DIR_NAMES[direction]} at {d_ahead*100:.1f}cm")
            return

        # --- Arrived? ---
        if d_ahead is not None and d_ahead <= CENTER_DIST + 0.01:
            robot.drive.halt()
            print(f"    Stopped: {d_ahead*100:.1f}cm from {DIR_NAMES[direction]} wall")
            return

        # --- Forward target ---
        if d_ahead is not None:
            remaining = max(d_ahead - CENTER_DIST, 0.01)
        else:
            remaining = CELL_SIZE * 0.5
        target_dx = dx_dir * remaining
        target_dy = dy_dir * remaining

        # --- Read side walls (every 3rd cycle) and collect theta samples ---
        angle_samples = []
        if a_ahead is not None and q_ahead is not None and q_ahead > 0.5:
            angle_samples.append(a_ahead)

        for wall_dir in ALL_DIRS:
            if wall_dir == direction:
                continue  # already read above
            d_w, a_w, q_w = robot.lidar.check_wall(wall_dir)
            if d_w is None:
                continue

            # Theta alignment from any visible wall
            if a_w is not None and q_w is not None and q_w > 0.5:
                angle_samples.append(a_w)

            # Push away if too close (any wall, any direction except behind)
            if wall_dir != opp and d_w < CENTER_DIST and q_w is not None and q_w > 0.3:
                push = (CENTER_DIST - d_w) * 1.0
                wx, wy = DIR_DELTA[wall_dir]
                target_dx -= wx * push
                target_dy -= wy * push

        # --- Theta correction ---
        dtheta_deg = 0.0
        if angle_samples:
            avg_angle = sum(angle_samples) / len(angle_samples)
            dtheta_deg = max(-15.0, min(15.0, avg_angle))

        # --- Send target ---
        robot.drive.set_target_position(
            dx=target_dx, dy=target_dy, dtheta_deg=dtheta_deg,
            speed=MOVE_SPEED, acceleration=50,
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

            # Move
            t_move = time.time()
            move_to_cell(robot, direction)
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
