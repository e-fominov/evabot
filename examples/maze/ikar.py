#!/usr/bin/env python3
# maze robot by ikar, age 10
# robot goes through maze, drops ball on blue, stops on red

import time
from evabot import Robot, MecanumDrive, RPLidarC1, Servo42D
from evabot.components.sensors import Camera

# my maze has 30cm cells
WALL_DIST = 0.25  # if wall closer than 25cm its a wall
STOP_DIST = 0.145  # stop 14.5cm from wall

# directions for lidar
FRONT = 0
RIGHT = 90
BACK = 180
LEFT = 270

opposite = {FRONT: BACK, BACK: FRONT, LEFT: RIGHT, RIGHT: LEFT}
delta = {FRONT: (1, 0), RIGHT: (0, -1), BACK: (-1, 0), LEFT: (0, 1)}
names = {FRONT: "front", RIGHT: "right", BACK: "back", LEFT: "left"}

# i try left first, then back, then right, then front
priority = [LEFT, BACK, RIGHT, FRONT]

# map - which cells i visited and where walls are
visited = set()
walls = {}


def add_wall(x, y, d, has_wall):
    walls[(x, y, d)] = has_wall
    # neighbor sees same wall from other side
    dx, dy = delta[d]
    walls[(x + dx, y + dy, opposite[d])] = has_wall


def check_walls(robot):
    """look around and see which walls exist"""
    result = {}
    for d in [FRONT, RIGHT, BACK, LEFT]:
        dist, _, quality = robot.lidar.check_wall(d)
        if dist is not None and quality is not None and quality > 0.3 and dist < WALL_DIST:
            result[d] = True
        else:
            result[d] = False
    return result


def find_next(x, y):
    """find a neighbor i haven't been to yet"""
    for d in priority:
        dx, dy = delta[d]
        nx, ny = x + dx, y + dy
        if walls.get((x, y, d)) == False and (nx, ny) not in visited:
            return d, nx, ny
    return None


# setup robot
robot = Robot()
robot.drive = MecanumDrive()
robot.lidar = RPLidarC1(max_range=1.0)
robot.start()

camera = Camera()
camera.start()

# motor 5 is the ball dropper
dropper = Servo42D(5)
dropper.start()

dropped = False
finished = False

time.sleep(3)
print("3...")
time.sleep(1)
print("2...")
time.sleep(1)
print("1...")
time.sleep(1)
print("GO!!!")

# start at cell 0,0
x, y = 0, 0
path = []  # remember where i came from so i can go back

try:
    for step in range(200):
        print(f"\n=== cell ({x},{y}) step {step+1} ===")

        # look around
        visited.add((x, y))
        w = check_walls(robot)
        for d in [FRONT, RIGHT, BACK, LEFT]:
            add_wall(x, y, d, w[d])
            if w[d]:
                print(f"  {names[d]}: wall")
            else:
                print(f"  {names[d]}: open!")

        # where to go?
        nxt = find_next(x, y)

        if nxt:
            # go to unvisited cell
            d, nx, ny = nxt
            print(f"  going {names[d]} to ({nx},{ny})")
            path.append((x, y, d))
            robot.move_to_wall(d, stop_distance=STOP_DIST, speed=0.2)
            x, y = nx, ny

        elif path:
            # dead end! go back
            print(f"  dead end! going back...")
            while path:
                px, py, came_from = path.pop()
                back = opposite[came_from]
                print(f"  back {names[back]} to ({px},{py})")
                robot.move_to_wall(back, stop_distance=STOP_DIST, speed=0.2)
                x, y = px, py
                time.sleep(0.2)

                # maybe i found red?
                if camera.match_color("red") > 0.05:
                    print("RED!!! FINISH!!!")
                    finished = True
                    break

                # maybe theres somewhere new to go
                if find_next(x, y):
                    print(f"  found new path!")
                    break
            else:
                print("explored everything!")
                break
            if finished:
                break
            continue

        else:
            print("explored everything!")
            break

        # check colors after each move
        # red = finish line
        if camera.match_color("red") > 0.05:
            print("RED!!! FINISH!!!")
            break

        # blue = drop the ball
        if not dropped:
            if camera.match_color("blue") > 0.05:
                print("BLUE! dropping ball...")
                dropper.run(30)
                time.sleep(1)
                dropper.run(0)
                dropped = True
                print("ball dropped!")

    print(f"\ndone! visited {len(visited)} cells")

except KeyboardInterrupt:
    print("\nstopped")

robot.drive.halt()
dropper.stop()
camera.stop()
time.sleep(0.3)
robot.stop()
