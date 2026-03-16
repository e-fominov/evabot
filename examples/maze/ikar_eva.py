#!/usr/bin/env python3
# робот-лабиринт от Икара, 10 лет
# робот едет по лабиринту, бросает шарик на синем, останавливается на красном

import time
from evabot import Robot, MecanumDrive, RPLidarC1, Servo42D
from evabot.components.sensors import Camera

# мой лабиринт с ячейками 30 см
WALL_DIST = 0.25  # если стена ближе 25см - это стена
STOP_DIST = 0.145  # останавливаемся в 14.5см от стены

# направления для лидара
FRONT = 0
RIGHT = 90
BACK = 180
LEFT = 270

opposite = {FRONT: BACK, BACK: FRONT, LEFT: RIGHT, RIGHT: LEFT}
delta = {FRONT: (1, 0), RIGHT: (0, -1), BACK: (-1, 0), LEFT: (0, 1)}
names = {FRONT: "перед", RIGHT: "право", BACK: "зад", LEFT: "лево"}

# сначала налево, потом назад, потом направо, потом вперед
priority = [LEFT, BACK, RIGHT, FRONT]

# карта - где был и где стены
visited = set()
walls = {}


def add_wall(x, y, d, has_wall):
    walls[(x, y, d)] = has_wall
    # сосед видит эту же стену с другой стороны
    dx, dy = delta[d]
    walls[(x + dx, y + dy, opposite[d])] = has_wall


def check_walls(robot):
    """смотрим вокруг - где стены"""
    result = {}
    for d in [FRONT, RIGHT, BACK, LEFT]:
        dist, _, quality = robot.lidar.check_wall(d)
        if dist is not None and quality is not None and quality > 0.3 and dist < WALL_DIST:
            result[d] = True
        else:
            result[d] = False
    return result


def find_next(x, y):
    """ищем соседа где ещё не были"""
    for d in priority:
        dx, dy = delta[d]
        nx, ny = x + dx, y + dy
        if walls.get((x, y, d)) == False and (nx, ny) not in visited:
            return d, nx, ny
    return None


# настраиваем робота
robot = Robot()
robot.drive = MecanumDrive()
robot.lidar = RPLidarC1(max_range=1.0)
robot.start()

camera = Camera()
camera.start()

# мотор 5 - это сбрасыватель шарика
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
print("ПОЕХАЛИ!!!")

# начинаем в ячейке 0,0
x, y = 0, 0
path = []  # запоминаем откуда пришли чтобы вернуться

try:
    for step in range(200):
        print(f"\n=== ячейка ({x},{y}) шаг {step+1} ===")

        # осматриваемся
        visited.add((x, y))
        w = check_walls(robot)
        for d in [FRONT, RIGHT, BACK, LEFT]:
            add_wall(x, y, d, w[d])
            if w[d]:
                print(f"  {names[d]}: стена")
            else:
                print(f"  {names[d]}: проход!")

        # куда ехать?
        nxt = find_next(x, y)

        if nxt:
            # едем в новую ячейку
            d, nx, ny = nxt
            print(f"  еду {names[d]} в ({nx},{ny})")
            path.append((x, y, d))
            robot.move_to_wall(d, stop_distance=STOP_DIST, speed=0.2)
            x, y = nx, ny

        elif path:
            # тупик! едем назад
            print(f"  тупик! возвращаюсь...")
            while path:
                px, py, came_from = path.pop()
                back = opposite[came_from]
                print(f"  назад {names[back]} в ({px},{py})")
                robot.move_to_wall(back, stop_distance=STOP_DIST, speed=0.2)
                x, y = px, py
                time.sleep(0.2)

                # может нашли красное?
                if camera.match_color("red") > 0.05:
                    print("КРАСНОЕ!!! ФИНИШ!!!")
                    finished = True
                    break

                # может есть куда поехать
                if find_next(x, y):
                    print(f"  нашёл новый путь!")
                    break
            else:
                print("всё объехал!")
                break
            if finished:
                break
            continue

        else:
            print("всё объехал!")
            break

        # проверяем цвета после каждого хода
        # красный = финиш
        if camera.match_color("red") > 0.05:
            print("КРАСНОЕ!!! ФИНИШ!!!")
            break

        # синий = бросаем шарик
        if not dropped:
            if camera.match_color("blue") > 0.05:
                print("СИНЕЕ! бросаю шарик...")
                dropper.run(30)
                time.sleep(1)
                dropper.run(0)
                dropped = True
                print("шарик сброшен!")

    print(f"\nготово! объехал {len(visited)} ячеек")

except KeyboardInterrupt:
    print("\nстоп")

robot.drive.halt()
dropper.stop()
camera.stop()
time.sleep(0.3)
robot.stop()
