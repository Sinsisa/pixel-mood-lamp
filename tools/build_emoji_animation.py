"""Generate shared 15x15 emoji frames and flash-resident Arduino animation data.

The browser and Arduino consume these same palette-indexed frames. All art is
drawn on the actual 225-pixel grid; no platform emoji fonts are involved.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIDTH = HEIGHT = 15
PALETTE = [
    [0, 0, 0], [76, 20, 0], [255, 99, 0], [255, 166, 0],
    [255, 209, 20], [255, 244, 172], [255, 43, 77], [150, 10, 5],
    [25, 180, 255], [154, 241, 255], [60, 140, 10], [130, 224, 20],
    [255, 58, 0], [255, 125, 6], [255, 190, 35], [140, 43, 0],
]
SCENES = [
    {"name": "Pac-Man", "startMs": 0, "endMs": 4000},
    {"name": "Laugh out loud", "startMs": 4000, "endMs": 7500},
    {"name": "Happy little moment", "startMs": 7500, "endMs": 10500},
    {"name": "Too cool", "startMs": 10500, "endMs": 14000},
    {"name": "Pumpkin after dark", "startMs": 14000, "endMs": 18000},
]


class Canvas:
    def __init__(self):
        self.pixels = [0] * 225

    def dot(self, x, y, colour):
        x, y = int(x), int(y)
        if 0 <= x < 15 and 0 <= y < 15:
            self.pixels[y * 15 + x] = colour

    def line(self, x1, y1, x2, y2, colour):
        steps = max(abs(x2 - x1), abs(y2 - y1))
        if steps == 0:
            self.dot(x1, y1, colour)
            return
        for i in range(steps + 1):
            self.dot(round(x1 + (x2 - x1) * i / steps),
                     round(y1 + (y2 - y1) * i / steps), colour)

    def rect(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.dot(xx, yy, colour)

    def shifted(self, dx=0, dy=0):
        result = Canvas()
        for y in range(15):
            for x in range(15):
                if self.pixels[y * 15 + x]:
                    result.dot(x + dx, y + dy, self.pixels[y * 15 + x])
        return result


def face():
    c = Canvas()
    for y in range(1, 14):
        for x in range(1, 14):
            d = (x - 7) ** 2 + (y - 7) ** 2
            if d <= 41:
                c.dot(x, y, 2 if d >= 34 else (3 if y >= 10 else 4))
    c.line(4, 3, 6, 2, 5)
    return c


def happy(blink=False, wink=False, cheeks=False):
    c = face()
    if blink:
        c.line(4, 6, 5, 6, 0)
        c.line(9, 6, 10, 6, 0)
    else:
        c.rect(4, 5, 2, 2, 0)
        if wink:
            c.line(9, 6, 11, 6, 0)
        else:
            c.rect(9, 5, 2, 2, 0)
    for x, y in [(4, 9), (5, 10), (6, 11), (7, 11), (8, 11), (9, 10), (10, 9)]:
        c.dot(x, y, 0)
    if cheeks:
        c.line(3, 8, 4, 8, 6)
        c.line(10, 8, 11, 8, 6)
    return c


def laughing(beat, tears):
    c = face()
    for x in (4, 10):
        c.dot(x - 1, 6, 0)
        c.dot(x, 5, 0)
        c.dot(x + 1, 6, 0)
    c.rect(4, 8, 7, 3, 0)
    c.rect(5, 11, 5, 1, 0)
    c.line(4, 8, 10, 8, 5)
    c.line(6, 11, 8, 11, 6)
    if beat % 2:
        c.line(5, 11, 9, 11, 0)
        c.line(6, 10, 8, 10, 6)
    c = c.shifted(dy=-1 if beat % 3 == 1 else 0)
    if tears:
        y = 7 + tears % 3
        c.dot(1, y, 8)
        c.dot(1, y + 1, 9)
        c.dot(13, y + 1, 8)
        c.dot(13, y + 2, 9)
    return c


def glasses(drop=0, glint=-1, grin=False):
    c = happy()
    y = 4 + drop
    c.line(1, y, 13, y, 0)
    c.rect(2, y, 5, 3, 0)
    c.rect(8, y, 5, 3, 0)
    c.line(3, y + 3, 5, y + 3, 0)
    c.line(9, y + 3, 11, y + 3, 0)
    c.dot(3, y, 8)
    c.dot(9, y, 8)
    if glint >= 0:
        for dx in (0, 6):
            c.dot(2 + glint + dx, y + 1, 9)
            c.dot(3 + glint + dx, y, 5)
    if grin:
        c.rect(5, 9, 5, 2, 0)
        c.line(5, 9, 9, 9, 5)
    return c


def pumpkin(glow=0, wink=False):
    c = Canvas()
    for y in range(3, 14):
        for x in range(1, 14):
            if ((x - 7) / 6.4) ** 2 + ((y - 8) / 5.5) ** 2 <= 1:
                c.dot(x, y, 13 if x in (4, 7, 10) else 12)
                if x in (1, 13) or y == 13:
                    c.dot(x, y, 15)
    c.line(7, 1, 7, 3, 10)
    c.dot(8, 1, 11)
    c.dot(9, 2, 10)
    light = (14, 5, 3)[glow % 3]
    for x in (4, 10):
        c.dot(x, 5, 0)
        c.line(x - 1, 6, x + 1, 6, 0)
        c.line(x - 1, 7, x + 1, 7, 0)
        c.dot(x, 6, light)
    if wink:
        c.rect(9, 5, 3, 3, 12)
        c.line(9, 6, 11, 6, 0)
    c.dot(7, 8, 0)
    c.line(6, 9, 8, 9, 0)
    c.line(3, 9, 4, 11, 0)
    c.rect(4, 10, 7, 3, 0)
    c.line(10, 11, 11, 9, 0)
    c.dot(5, 10, 13)
    c.dot(9, 10, 13)
    c.dot(7, 12, 13)
    for x in (5, 6, 8, 9):
        c.dot(x, 11, light)
    return c


def pacman(step, entrance=False, exit=False):
    c = Canvas()
    # Pac-Man stays readable while pellets travel into the opening.
    centre = 5
    if entrance:
        centre = (-4, -1, 2, 4, 5)[min(step, 4)]
    elif exit:
        centre = (5, 7, 9, 12, 16, 20)[min(step, 5)]
    for x in (10 - step % 4, 14 - step % 4):
        if x > centre + 3:
            c.dot(x, 7, 5)
    opening = (0.06, 0.38, 0.8, 1.05, 0.8, 0.38)[step % 6]
    for y in range(2, 13):
        for x in range(15):
            dx, dy = x - centre, y - 7
            if dx * dx + dy * dy <= 27:
                if dx >= 0 and abs(math.atan2(dy, dx)) < opening:
                    continue
                c.dot(x, y, 3 if y >= 11 else 4)
    c.dot(centre, 4, 0)
    c.dot(centre - 2, 3, 5)
    return c


def wipe(a, b, column):
    c = Canvas()
    for y in range(15):
        for x in range(15):
            c.dot(x, y, b.pixels[y * 15 + x] if x <= column else a.pixels[y * 15 + x])
    return c


def create_show():
    frames = []
    frame_ids = {}
    timeline = []

    def add(canvas, duration, scene):
        key = tuple(canvas.pixels)
        if key not in frame_ids:
            frame_ids[key] = len(frames)
            frames.append(canvas.pixels)
        index = frame_ids[key]
        if timeline and timeline[-1]["frame"] == index and timeline[-1]["scene"] == scene:
            timeline[-1]["duration"] += duration
        else:
            timeline.append({"frame": index, "duration": duration, "scene": scene})

    # 0-4 s: enter, chomp pellets in a steady arcade rhythm, then exit.
    for i in range(5):
        add(pacman(i, entrance=True), 100, 0)
    for i in range(29):
        add(pacman(i), 100, 0)
    for i in range(6):
        add(pacman(i, exit=True), 100, 0)

    # 4-7.5 s: anticipation, a bouncing laugh and little rolling tears.
    add(happy(), 200, 1)
    for i in range(18):
        add(laughing(i, 1 + (i // 2) % 3), 150, 1)
    add(laughing(0, 0), 300, 1)
    add(happy(blink=True, cheeks=True), 150, 1)
    add(happy(cheeks=True), 150, 1)

    # 7.5-10.5 s: a relaxed smile with a quick double blink and a wink.
    for canvas, duration in [
        (happy(cheeks=True), 650), (happy(blink=True, cheeks=True), 100),
        (happy(cheeks=True), 180), (happy(blink=True, cheeks=True), 100),
        (happy(cheeks=True), 700), (happy(wink=True, cheeks=True), 220),
        (happy(cheeks=True).shifted(dy=-1), 150), (happy(cheeks=True), 900),
    ]:
        add(canvas, duration, 2)

    # 10.5-14 s: glasses drop, settle and catch a short travelling glint.
    add(glasses(-3), 100, 3)
    add(glasses(-2), 100, 3)
    add(glasses(-1), 100, 3)
    add(glasses(0), 150, 3)
    add(glasses(1), 100, 3)
    add(glasses(0), 650, 3)
    for i in range(3):
        add(glasses(0, i, True), 100, 3)
    add(glasses(0, -1, True), 900, 3)
    add(glasses(0), 800, 3)
    add(glasses(0, -1, True), 300, 3)

    # 14-18 s: pumpkin sweeps across the face and gently flickers like a candle.
    previous = glasses(0, -1, True)
    for column in (2, 5, 8, 11, 14):
        add(wipe(previous, pumpkin(), column), 100, 4)
    for glow, duration in [(0, 500), (1, 160), (0, 360), (2, 150),
                           (0, 430), (1, 170), (0, 430)]:
        add(pumpkin(glow), duration, 4)
    add(pumpkin(0, True), 180, 4)
    add(pumpkin(0), 520, 4)
    # Closing iris leaves black on the final frame, ready for Pac-Man's entry.
    full = pumpkin(0)
    for radius in (6, 4, 2, 0):
        closed = Canvas()
        for y in range(15):
            for x in range(15):
                if radius and (x - 7) ** 2 + (y - 7) ** 2 <= radius * radius:
                    closed.dot(x, y, full.pixels[y * 15 + x])
        add(closed, 150, 4)

    assert sum(t["duration"] for t in timeline) == 18000
    for scene, definition in enumerate(SCENES):
        assert sum(t["duration"] for t in timeline if t["scene"] == scene) == definition["endMs"] - definition["startMs"]
    assert len(frames) < 256
    return {"width": 15, "height": 15, "totalMs": 18000, "palette": PALETTE,
            "frames": frames, "timeline": timeline, "scenes": SCENES,
            "defaultBrightness": 8}


def write_header(data):
    packed = []
    for frame in data["frames"]:
        packed.append([(frame[i] << 4) | (frame[i + 1] if i + 1 < 225 else 0)
                       for i in range(0, 225, 2)])
    lines = ["// Generated by tools/build_emoji_animation.py. Do not edit frame bytes by hand.",
             "#pragma once", "#include <Arduino.h>",
             "#if defined(ARDUINO_ARCH_AVR)", "#include <avr/pgmspace.h>", "#endif", "",
             f"constexpr uint16_t SHOW_DURATION_MS = {data['totalMs']};",
             f"constexpr uint16_t TIMELINE_COUNT = {len(data['timeline'])};",
             f"constexpr uint16_t FRAME_COUNT = {len(packed)};",
             "constexpr uint8_t FRAME_BYTES = 113;", "",
             "const uint8_t EMOJI_PALETTE[16][3] PROGMEM = {"]
    lines += ["  {" + ",".join(map(str, c)) + "}," for c in PALETTE]
    lines += ["};", "", "const uint8_t EMOJI_FRAMES[FRAME_COUNT][FRAME_BYTES] PROGMEM = {"]
    lines += ["  {" + ",".join(f"0x{x:02x}" for x in frame) + "}," for frame in packed]
    lines += ["};", "", "struct TimelineStep { uint8_t frame; uint16_t duration; };",
              "const TimelineStep EMOJI_TIMELINE[TIMELINE_COUNT] PROGMEM = {"]
    lines += [f"  {{{t['frame']}, {t['duration']}}}," for t in data["timeline"]]
    lines += ["};", ""]
    target = ROOT / "firmware/PanelEmojiShow/EmojiShowData.h"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")


def main():
    data = create_show()
    target = ROOT / "visualizations/emoji-show-data.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8")
    write_header(data)
    byte_size = len(data["frames"]) * 113 + len(data["timeline"]) * 3 + 48
    print(f"{len(data['frames'])} unique frames; {len(data['timeline'])} timeline steps; "
          f"18000 ms; AVR animation data {byte_size} bytes")


if __name__ == "__main__":
    main()
