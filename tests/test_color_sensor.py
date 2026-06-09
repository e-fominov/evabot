#!/usr/bin/env python3
"""Live color sensor test — prints HSV and color confidences in a loop."""

import time
from evabot.components.sensors import Camera

cam = Camera()
cam.start()

COLORS = ["red", "yellow", "green", "blue", "white", "black"]

try:
    while True:
        hsv = cam.get_color()
        if hsv is None:
            print("No frame")
            time.sleep(0.5)
            continue

        scores = {c: cam.match_color(c) for c in COLORS}
        best = max(scores, key=scores.get)

        parts = [f"HSV({hsv[0]:3d},{hsv[1]:3d},{hsv[2]:3d})"]
        for c in COLORS:
            s = scores[c]
            marker = " <" if c == best and s > 0.05 else ""
            parts.append(f"{c[:3]}:{s:.2f}{marker}")

        print("  ".join(parts))
        time.sleep(0.3)
except KeyboardInterrupt:
    pass
finally:
    cam.stop()
