#!/usr/bin/env python3
"""Generate deterministic preschool maths assets for the curriculum-first proof set.

This intentionally replaces image-model generation for pages where exact counts,
clean shapes, and strict isolation matter more than painterly illustration.

Generated pages:
- P009 Count & Match
- P018 Number Line character markers
- P021 2D Shapes

P013 remains fully deterministic in the page renderer and needs no assets.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw

CANVAS = 1024
BG = (255, 255, 255, 0)
OUTLINE = (55, 55, 75, 255)


def image() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = Image.new("RGBA", (CANVAS, CANVAS), BG)
    return im, ImageDraw.Draw(im)


def save_asset(path: Path, painter: Callable[[ImageDraw.ImageDraw], None]) -> None:
    im, draw = image()
    painter(draw)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "PNG")


def positions(count: int) -> list[tuple[int, int]]:
    if count == 1:
        return [(512, 512)]
    cols = 2 if count <= 4 else 3 if count <= 6 else 4
    rows = (count + cols - 1) // cols
    gap_x = 560 // max(1, cols - 1) if cols > 1 else 0
    gap_y = 420 // max(1, rows - 1) if rows > 1 else 0
    x0 = 512 - gap_x * (cols - 1) // 2
    y0 = 512 - gap_y * (rows - 1) // 2
    pts = []
    for i in range(count):
        r, c = divmod(i, cols)
        pts.append((x0 + c * gap_x, y0 + r * gap_y))
    return pts


def kite(draw: ImageDraw.ImageDraw, x: int, y: int, colour: tuple[int, int, int, int]) -> None:
    s = 95
    draw.polygon([(x, y-s), (x+s, y), (x, y+s), (x-s, y)], fill=colour, outline=OUTLINE)
    draw.line([(x, y+s), (x+20, y+s+70), (x-15, y+s+135)], fill=OUTLINE, width=8)
    draw.polygon([(x+15, y+s+55), (x+55, y+s+75), (x+20, y+s+100)], fill=(255, 215, 80, 255), outline=OUTLINE)


def duck(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.ellipse([x-90, y-40, x+90, y+80], fill=(255, 219, 70, 255), outline=OUTLINE, width=6)
    draw.ellipse([x+30, y-110, x+120, y-20], fill=(255, 219, 70, 255), outline=OUTLINE, width=6)
    draw.polygon([(x+115, y-65), (x+165, y-45), (x+115, y-25)], fill=(255, 145, 45, 255), outline=OUTLINE)
    draw.ellipse([x+85, y-75, x+98, y-62], fill=OUTLINE)


def cupcake(draw: ImageDraw.ImageDraw, x: int, y: int, icing: tuple[int, int, int, int]) -> None:
    draw.polygon([(x-75, y+10), (x+75, y+10), (x+55, y+120), (x-55, y+120)], fill=(245, 185, 95, 255), outline=OUTLINE)
    draw.ellipse([x-95, y-85, x+95, y+45], fill=icing, outline=OUTLINE, width=6)
    draw.ellipse([x-12, y-105, x+12, y-81], fill=(220, 55, 70, 255), outline=OUTLINE)


def ball(draw: ImageDraw.ImageDraw, x: int, y: int, colour: tuple[int, int, int, int]) -> None:
    draw.ellipse([x-70, y-70, x+70, y+70], fill=colour, outline=OUTLINE, width=6)
    draw.arc([x-55, y-55, x+55, y+55], 20, 160, fill=(255, 255, 255, 220), width=8)


def animal_frog(draw: ImageDraw.ImageDraw) -> None:
    draw.ellipse([300, 340, 724, 760], fill=(92, 194, 92, 255), outline=OUTLINE, width=8)
    for cx in (380, 644):
        draw.ellipse([cx-70, 250, cx+70, 390], fill=(92, 194, 92, 255), outline=OUTLINE, width=8)
        draw.ellipse([cx-24, 292, cx+24, 340], fill=(255,255,255,255), outline=OUTLINE, width=5)
        draw.ellipse([cx-8, 306, cx+8, 322], fill=OUTLINE)
    draw.arc([390, 460, 635, 650], 20, 160, fill=OUTLINE, width=8)


def animal_rabbit(draw: ImageDraw.ImageDraw) -> None:
    draw.ellipse([330, 320, 700, 780], fill=(242, 235, 226, 255), outline=OUTLINE, width=8)
    draw.ellipse([360, 90, 475, 420], fill=(242,235,226,255), outline=OUTLINE, width=8)
    draw.ellipse([555, 90, 670, 420], fill=(242,235,226,255), outline=OUTLINE, width=8)
    draw.ellipse([430, 450, 475, 495], fill=OUTLINE)
    draw.ellipse([555, 450, 600, 495], fill=OUTLINE)
    draw.polygon([(515, 520), (550, 545), (515, 565), (480,545)], fill=(238,132,145,255), outline=OUTLINE)


def animal_bee(draw: ImageDraw.ImageDraw) -> None:
    draw.ellipse([290, 360, 740, 700], fill=(255, 207, 55, 255), outline=OUTLINE, width=8)
    for x in (400, 510, 620):
        draw.rectangle([x-20, 375, x+20, 685], fill=(45,45,55,255))
    draw.ellipse([240, 280, 430, 470], fill=(220,245,255,220), outline=OUTLINE, width=6)
    draw.ellipse([600, 280, 790, 470], fill=(220,245,255,220), outline=OUTLINE, width=6)
    draw.ellipse([390, 470, 430, 510], fill=OUTLINE)
    draw.ellipse([600, 470, 640, 510], fill=OUTLINE)


def shape_circle(draw: ImageDraw.ImageDraw) -> None:
    draw.ellipse([240, 240, 784, 784], fill=(240, 88, 88, 255), outline=OUTLINE, width=10)


def shape_square(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle([240, 240, 784, 784], fill=(92, 154, 230, 255), outline=OUTLINE, width=10)


def shape_triangle(draw: ImageDraw.ImageDraw) -> None:
    draw.polygon([(512, 200), (820, 790), (204, 790)], fill=(92, 190, 112, 255), outline=OUTLINE)


def shape_rectangle(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle([180, 300, 844, 724], fill=(255, 214, 78, 255), outline=OUTLINE, width=10)


def object_clock(draw: ImageDraw.ImageDraw) -> None:
    draw.ellipse([225, 225, 799, 799], fill=(255,255,255,255), outline=OUTLINE, width=14)
    draw.line([(512,512),(512,350)], fill=OUTLINE, width=14)
    draw.line([(512,512),(640,590)], fill=OUTLINE, width=14)
    draw.ellipse([492,492,532,532], fill=OUTLINE)


def object_window(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle([245,245,779,779], fill=(205,235,255,255), outline=OUTLINE, width=14)
    draw.line([(512,245),(512,779)], fill=OUTLINE, width=12)
    draw.line([(245,512),(779,512)], fill=OUTLINE, width=12)


def object_flag(draw: ImageDraw.ImageDraw) -> None:
    draw.line([(330,180),(330,840)], fill=OUTLINE, width=16)
    draw.polygon([(345,220),(790,390),(345,560)], fill=(92,190,112,255), outline=OUTLINE)


def object_door(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle([305,160,719,850], fill=(193,126,76,255), outline=OUTLINE, width=14)
    draw.ellipse([630,500,670,540], fill=(255,215,80,255), outline=OUTLINE, width=5)


def generate(output_dir: Path) -> dict[str, list[str]]:
    report: dict[str, list[str]] = {}

    p9 = output_dir / "EM-LKG-V4-P009"
    specs = [
        ("group_2_kites.png", lambda d: [kite(d,x,y,c) for (x,y),c in zip(positions(2),[(225,90,90,255),(80,155,230,255)])]),
        ("group_4_ducks.png", lambda d: [duck(d,x,y) for x,y in positions(4)]),
        ("group_6_cupcakes.png", lambda d: [cupcake(d,x,y,c) for (x,y),c in zip(positions(6),[(245,120,145,255),(120,180,245,255),(255,210,80,255),(160,120,220,255),(100,200,165,255),(245,150,90,255)])]),
        ("group_8_balls.png", lambda d: [ball(d,x,y,c) for (x,y),c in zip(positions(8),[(235,80,80,255),(80,150,230,255),(255,205,65,255),(90,185,115,255)]*2)]),
    ]
    report["EM-LKG-V4-P009"] = []
    for name, painter in specs:
        save_asset(p9/name, painter); report["EM-LKG-V4-P009"].append(str(p9/name))

    p18 = output_dir / "EM-LKG-V4-P018"
    for name, painter in [("frog.png", animal_frog), ("rabbit.png", animal_rabbit), ("bee.png", animal_bee)]:
        save_asset(p18/name, painter)
    report["EM-LKG-V4-P018"] = [str(p18/n) for n in ("frog.png","rabbit.png","bee.png")]

    p21 = output_dir / "EM-LKG-V4-P021"
    shape_specs = [
        ("shape_circle.png", shape_circle), ("shape_square.png", shape_square),
        ("shape_triangle.png", shape_triangle), ("shape_rectangle.png", shape_rectangle),
        ("object_clock.png", object_clock), ("object_window.png", object_window),
        ("object_flag.png", object_flag), ("object_door.png", object_door),
    ]
    for name, painter in shape_specs:
        save_asset(p21/name, painter)
    report["EM-LKG-V4-P021"] = [str(p21/n) for n,_ in shape_specs]

    report["EM-LKG-V4-P013"] = ["DETERMINISTIC_PAGE_NO_ASSETS"]
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic Early Maths proof assets")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = generate(output)
    report_path = output / "deterministic-assets-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Generated deterministic proof assets in {output}")
    print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
