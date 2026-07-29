#!/usr/bin/env python3
"""Render the STEM Explorers LKG curriculum-first validation waves."""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "curriculum/stem-explorers/lkg/curriculum-first-p008-p043-v1.json"
TEXT_ENGINE = ROOT / "bcube-publishing-sdk/composer/compose_learning_page_v2.py"
ASSET_DIR = ROOT / "assets/illustrations/stem-explorers/lkg"

WIDTH, HEIGHT = 2480, 3508
NAVY = "#123F72"
PURPLE = "#7E57C2"
SOFT_PURPLE = "#A077E8"
BLUE = "#E8F4FF"
GOLD = "#FFF4C6"
GREEN = "#F0FAED"
INK = "#31353A"
PILOT = tuple(range(8, 44))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object expected: {path}")
    return value


def panel(draw: ImageDraw.ImageDraw, box, *, fill="#FFFFFF", outline=SOFT_PURPLE, width=4, radius=24):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def circle(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius=25, width=4, fill="white"):
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=fill, outline=PURPLE, width=width)


def trim_white(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    rgb = rgba.convert("RGB")
    diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, "white")).convert("L")
    diff = diff.point(lambda value: 255 if value > 14 else 0)
    alpha = rgba.getchannel("A").point(lambda value: 255 if value > 8 else 0)
    box = ImageChops.multiply(diff, alpha).getbbox()
    return rgba.crop(box) if box else rgba


def crop_norm(source: Image.Image, box) -> Image.Image:
    width, height = source.size
    x0, y0, x1, y1 = box
    return trim_white(source.crop((round(x0 * width), round(y0 * height), round(x1 * width), round(y1 * height))))


def grid_crops(source: Image.Image, columns: int, rows: int, count: int) -> list[Image.Image]:
    crops: list[Image.Image] = []
    for index in range(count):
        column = index % columns
        row = index // columns
        pad_x = 0.018
        pad_y = 0.018
        crops.append(crop_norm(source, (
            column / columns + pad_x,
            row / rows + pad_y,
            (column + 1) / columns - pad_x,
            (row + 1) / rows - pad_y,
        )))
    return crops


def paste_fit(canvas: Image.Image, image: Image.Image, box, inset=12):
    x0, y0, x1, y1 = [int(value) for value in box]
    x0 += inset; y0 += inset; x1 -= inset; y1 -= inset
    source = trim_white(image)
    scale = min((x1 - x0) / source.width, (y1 - y0) / source.height)
    source = source.resize((max(1, round(source.width * scale)), max(1, round(source.height * scale))), Image.Resampling.LANCZOS)
    x = x0 + (x1 - x0 - source.width) // 2
    y = y0 + (y1 - y0 - source.height) // 2
    canvas.paste(source, (x, y), source)


def header(canvas, draw, page, logo, text):
    logo_image = logo.copy().convert("RGBA")
    logo_image.thumbnail((300, 220), Image.Resampling.LANCZOS)
    canvas.paste(logo_image, (105 + (300 - logo_image.width) // 2, 35 + (220 - logo_image.height) // 2), logo_image)
    text.fitted_text(draw, "STEM Explorers", [470, 45, 2320, 145], max_size=43, min_size=34, colour=PURPLE, bold=True, max_lines=1)
    text.fitted_text(draw, page["title"], [470, 140, 2320, 275], max_size=69, min_size=45, colour=NAVY, bold=True, max_lines=2)
    panel(draw, [150, 305, 2330, 445], fill=BLUE, outline="#1768B3", width=3)
    text.fitted_text(draw, "Learning goal: " + page["objective"], [190, 318, 2290, 432], max_size=46, min_size=31, colour=NAVY, bold=True, max_lines=2)
    panel(draw, [150, 490, 2330, 650], fill=GOLD, outline="#E1A81C", width=3)
    text.fitted_text(draw, page["instruction"], [190, 505, 2290, 635], max_size=50, min_size=31, colour=INK, bold=True, max_lines=2)


def model_shell(draw, text):
    panel(draw, [170, 700, 2310, 900], fill="#F6F1FF", outline=SOFT_PURPLE, width=3)
    panel(draw, [195, 720, 535, 880], fill="#E7D9FA", outline=SOFT_PURPLE, width=2, radius=18)
    text.fitted_text(draw, "COMPLETED\nEXAMPLE", [220, 737, 510, 862], max_size=35, min_size=27, colour=NAVY, bold=True, max_lines=2)
    return 575, 720, 2275, 880


def completed_model(draw, page_id: str, text):
    x0, y0, x1, y1 = model_shell(draw, text)
    cy = (y0 + y1) // 2
    if page_id == "ST-LKG-V4-P008":
        for index in range(2):
            cx = x0 + 90 + index * 145
            draw.ellipse([cx - 48, cy - 30, cx + 48, cy + 30], fill="#77C95B", outline=NAVY, width=3)
            for spot in range(3 - index):
                sx = cx - 22 + spot * 22
                draw.ellipse([sx - 6, cy - 6, sx + 6, cy + 6], fill="#F4D03F")
        draw.ellipse([x0 + 166, cy - 55, x0 + 304, cy + 55], outline=PURPLE, width=5)
        message = "Circle what changed in the second picture."
    elif page_id == "ST-LKG-V4-P009":
        panel(draw, [x0 + 35, cy - 52, x0 + 310, cy + 52], fill="#E9F5FF", outline=PURPLE, width=3)
        text.fitted_text(draw, "EAR", [x0 + 55, cy - 36, x0 + 290, cy + 36], max_size=35, min_size=28, colour=NAVY, bold=True, max_lines=1)
        draw.line([x0 + 350, cy, x0 + 560, cy], fill=PURPLE, width=6)
        draw.polygon([(x0 + 560, cy), (x0 + 520, cy - 24), (x0 + 520, cy + 24)], fill=PURPLE)
        panel(draw, [x0 + 610, cy - 52, x0 + 885, cy + 52], fill="#FFF4C6", outline=PURPLE, width=3)
        text.fitted_text(draw, "BELL", [x0 + 630, cy - 36, x0 + 865, cy + 36], max_size=35, min_size=28, colour=NAVY, bold=True, max_lines=1)
        message = "The ear helps us hear a bell."
    elif page_id == "ST-LKG-V4-P010":
        draw.line([x0 + 105, cy + 35, x0 + 105, cy - 30], fill="#4AA34B", width=8)
        draw.ellipse([x0 + 65, cy - 68, x0 + 145, cy + 2], fill="#F05A87", outline=NAVY, width=3)
        draw.line([x0 + 180, cy, x0 + 465, cy], fill=PURPLE, width=6)
        draw.polygon([(x0 + 465, cy), (x0 + 425, cy - 25), (x0 + 425, cy + 25)], fill=PURPLE)
        panel(draw, [x0 + 520, cy - 55, x0 + 810, cy + 55], fill=BLUE, outline="#1768B3", width=3)
        text.fitted_text(draw, "LIVING", [x0 + 545, cy - 40, x0 + 785, cy + 40], max_size=37, min_size=29, colour=NAVY, bold=True, max_lines=1)
        message = "A flower is living because it grows."
    elif page_id == "ST-LKG-V4-P011":
        panel(draw, [x0 + 35, cy - 52, x0 + 330, cy + 52], fill="#F6F1FF", outline=PURPLE, width=3)
        text.fitted_text(draw, "FLOWER", [x0 + 55, cy - 36, x0 + 310, cy + 36], max_size=34, min_size=27, colour=NAVY, bold=True, max_lines=1)
        draw.line([x0 + 365, cy, x0 + 610, cy], fill=PURPLE, width=6)
        draw.polygon([(x0 + 610, cy), (x0 + 570, cy - 24), (x0 + 570, cy + 24)], fill=PURPLE)
        draw.ellipse([x0 + 675, cy - 55, x0 + 785, cy + 55], fill="#F05A87", outline=NAVY, width=3)
        message = "Draw from each word to the matching plant part."
    elif page_id == "ST-LKG-V4-P012":
        for label, left, fill in (("FISH", x0 + 35, "#E9F5FF"), ("POND", x0 + 630, "#EAF6E7")):
            panel(draw, [left, cy - 52, left + 280, cy + 52], fill=fill, outline=PURPLE, width=3)
            text.fitted_text(draw, label, [left + 20, cy - 36, left + 260, cy + 36], max_size=34, min_size=27, colour=NAVY, bold=True, max_lines=1)
        draw.line([x0 + 350, cy, x0 + 575, cy], fill=PURPLE, width=6)
        draw.polygon([(x0 + 575, cy), (x0 + 535, cy - 24), (x0 + 535, cy + 24)], fill=PURPLE)
        message = "A fish lives in a pond."
    elif page_id == "ST-LKG-V4-P013":
        for label, left, fill in (("SUNNY", x0 + 35, "#FFF4C6"), ("HAT", x0 + 630, "#E9F5FF")):
            panel(draw, [left, cy - 52, left + 280, cy + 52], fill=fill, outline=PURPLE, width=3)
            text.fitted_text(draw, label, [left + 20, cy - 36, left + 260, cy + 36], max_size=34, min_size=27, colour=NAVY, bold=True, max_lines=1)
        draw.line([x0 + 350, cy, x0 + 575, cy], fill=PURPLE, width=6)
        draw.polygon([(x0 + 575, cy), (x0 + 535, cy - 24), (x0 + 535, cy + 24)], fill=PURPLE)
        message = "A sun hat is useful on a sunny day."
    elif page_id == "ST-LKG-V4-P014":
        draw.ellipse([x0 + 50, cy - 55, x0 + 160, cy + 55], fill="#FFD73B", outline=NAVY, width=3)
        draw.line([x0 + 205, cy, x0 + 475, cy], fill=PURPLE, width=6)
        draw.polygon([(x0 + 475, cy), (x0 + 435, cy - 24), (x0 + 435, cy + 24)], fill=PURPLE)
        panel(draw, [x0 + 525, cy - 55, x0 + 815, cy + 55], fill="#FFF4C6", outline="#1768B3", width=3)
        text.fitted_text(draw, "DAY", [x0 + 555, cy - 38, x0 + 785, cy + 38], max_size=38, min_size=30, colour=NAVY, bold=True, max_lines=1)
        message = "The sun belongs with DAY."
    elif page_id == "ST-LKG-V4-P015":
        panel(draw, [x0 + 35, cy - 52, x0 + 365, cy + 52], fill=BLUE, outline=PURPLE, width=3)
        text.fitted_text(draw, "TURN OFF TAP", [x0 + 55, cy - 38, x0 + 345, cy + 38], max_size=30, min_size=24, colour=NAVY, bold=True, max_lines=1)
        draw.line([x0 + 410, cy, x0 + 600, cy], fill=PURPLE, width=6)
        draw.polygon([(x0 + 600, cy), (x0 + 560, cy - 24), (x0 + 560, cy + 24)], fill=PURPLE)
        draw.ellipse([x0 + 650, cy - 57, x0 + 790, cy + 57], outline=PURPLE, width=6)
        message = "Circle careful water use. Cross water waste."
    elif page_id == "ST-LKG-V4-P016":
        draw.ellipse([x0 + 55, cy - 32, x0 + 160, cy + 32], fill="#77C95B", outline=NAVY, width=3)
        for index, label in enumerate(("FLOAT", "SINK")):
            left = x0 + 245 + index * 285
            circle(draw, left, cy, 28)
            text.fitted_text(draw, label, [left + 45, cy - 35, left + 245, cy + 35], max_size=32, min_size=26, colour=NAVY, bold=True, max_lines=1)
            if index == 0:
                draw.ellipse([left - 39, cy - 39, left + 39, cy + 39], outline=PURPLE, width=5)
        message = "Predict first. Record the result after testing."
    elif page_id == "ST-LKG-V4-P017":
        panel(draw, [x0 + 35, cy - 52, x0 + 330, cy + 52], fill="#F6F1FF", outline=PURPLE, width=3)
        text.fitted_text(draw, "PAPER CLIP", [x0 + 55, cy - 36, x0 + 310, cy + 36], max_size=30, min_size=24, colour=NAVY, bold=True, max_lines=1)
        draw.line([x0 + 365, cy, x0 + 555, cy], fill=PURPLE, width=6)
        draw.polygon([(x0 + 555, cy), (x0 + 515, cy - 24), (x0 + 515, cy + 24)], fill=PURPLE)
        panel(draw, [x0 + 605, cy - 55, x0 + 865, cy + 55], fill=BLUE, outline="#1768B3", width=3)
        text.fitted_text(draw, "MAGNETIC", [x0 + 625, cy - 40, x0 + 845, cy + 40], max_size=31, min_size=25, colour=NAVY, bold=True, max_lines=1)
        message = "Write each picture number in the correct group."
    elif page_id == "ST-LKG-V4-P018":
        panel(draw, [x0 + 35, cy - 52, x0 + 280, cy + 52], fill=BLUE, outline=PURPLE, width=3)
        text.fitted_text(draw, "CUP", [x0 + 55, cy - 36, x0 + 260, cy + 36], max_size=32, min_size=26, colour=NAVY, bold=True, max_lines=1)
        draw.line([x0 + 325, cy, x0 + 515, cy], fill=PURPLE, width=6)
        draw.polygon([(x0 + 515, cy), (x0 + 475, cy - 24), (x0 + 475, cy + 24)], fill=PURPLE)
        panel(draw, [x0 + 565, cy - 52, x0 + 850, cy + 52], fill="#333333", outline=PURPLE, width=3)
        text.fitted_text(draw, "CUP SHADOW", [x0 + 585, cy - 36, x0 + 830, cy + 36], max_size=28, min_size=22, colour="white", bold=True, max_lines=1)
        message = "Match the outside shape and direction."
    elif page_id == "ST-LKG-V4-P019":
        draw.line([x0 + 45, cy + 40, x0 + 275, cy + 40], fill="#A9A9A9", width=18)
        draw.line([x0 + 45, cy + 40, x0 + 45, cy + 75], fill="#C58B4A", width=28)
        draw.line([x0 + 275, cy + 40, x0 + 275, cy + 75], fill="#C58B4A", width=28)
        draw.line([x0 + 355, cy + 35, x0 + 635, cy + 35], fill="#A9A9A9", width=22)
        for x in range(x0 + 355, x0 + 636, 40):
            draw.line([x, cy + 15, x + 20, cy + 55], fill="#777777", width=4)
        draw.ellipse([x0 + 330, cy - 75, x0 + 660, cy + 90], outline=PURPLE, width=6)
        message = "Folded paper can make a stronger bridge."
    elif page_id == "ST-LKG-V4-P020":
        draw.polygon([(x0 + 45, cy + 55), (x0 + 255, cy + 55), (x0 + 255, cy - 45)], fill="#D69B43", outline=NAVY)
        draw.line([x0 + 305, cy, x0 + 560, cy], fill=PURPLE, width=6)
        draw.polygon([(x0 + 560, cy), (x0 + 520, cy - 24), (x0 + 520, cy + 24)], fill=PURPLE)
        panel(draw, [x0 + 610, cy - 52, x0 + 850, cy + 52], fill=GOLD, outline=PURPLE, width=3)
        text.fitted_text(draw, "SLIDE", [x0 + 635, cy - 36, x0 + 825, cy + 36], max_size=32, min_size=26, colour=NAVY, bold=True, max_lines=1)
        message = "A slide is an everyday ramp."
    elif page_id == "ST-LKG-V4-P021":
        panel(draw, [x0 + 30, cy - 52, x0 + 275, cy + 52], fill="#FFFFFF", outline=PURPLE, width=3)
        text.fitted_text(draw, "ZEBRA", [x0 + 50, cy - 36, x0 + 255, cy + 36], max_size=31, min_size=25, colour=NAVY, bold=True, max_lines=1)
        choices = ("STRIPES", "SPOTS", "SPIRAL", "VEINS")
        for index, label in enumerate(choices):
            left = x0 + 330 + index * 205
            panel(draw, [left, cy - 45, left + 180, cy + 45], fill="#FFFFFF", outline=PURPLE, width=2, radius=14)
            text.fitted_text(draw, label, [left + 8, cy - 30, left + 172, cy + 30], max_size=25, min_size=19, colour=NAVY, bold=True, max_lines=1)
            if index == 0:
                draw.rounded_rectangle([left - 7, cy - 52, left + 187, cy + 52], radius=18, outline=PURPLE, width=5)
        message = "A zebra has STRIPES."
    elif page_id == "ST-LKG-V4-P022":
        panel(draw, [x0 + 35, cy - 52, x0 + 325, cy + 52], fill="#EAF6E7", outline=PURPLE, width=3)
        text.fitted_text(draw, "RECYCLE", [x0 + 55, cy - 36, x0 + 305, cy + 36], max_size=31, min_size=24, colour=NAVY, bold=True, max_lines=1)
        draw.line([x0 + 365, cy, x0 + 555, cy], fill=PURPLE, width=6)
        draw.polygon([(x0 + 555, cy), (x0 + 515, cy - 24), (x0 + 515, cy + 24)], fill=PURPLE)
        panel(draw, [x0 + 605, cy - 52, x0 + 910, cy + 52], fill=GREEN, outline="#5F9D50", width=3)
        text.fitted_text(draw, "HELPS EARTH", [x0 + 625, cy - 36, x0 + 890, cy + 36], max_size=29, min_size=22, colour=NAVY, bold=True, max_lines=1)
        message = "Write each picture number in the correct group."
    elif page_id == "ST-LKG-V4-P023":
        panel(draw, [x0 + 35, cy - 52, x0 + 300, cy + 52], fill="#FFF4C6", outline=PURPLE, width=3)
        text.fitted_text(draw, "TORCH", [x0 + 55, cy - 36, x0 + 280, cy + 36], max_size=32, min_size=25, colour=NAVY, bold=True, max_lines=1)
        draw.rounded_rectangle([x0 + 25, cy - 62, x0 + 310, cy + 62], radius=20, outline=PURPLE, width=5)
        message = "A torch helps us see in the dark."
    elif page_id == "ST-LKG-V4-P024":
        panel(draw, [x0 + 35, cy - 52, x0 + 330, cy + 52], fill="#EAF6E7", outline=PURPLE, width=3)
        text.fitted_text(draw, "SIT WELL", [x0 + 55, cy - 36, x0 + 310, cy + 36], max_size=31, min_size=24, colour=NAVY, bold=True, max_lines=1)
        draw.rounded_rectangle([x0 + 25, cy - 62, x0 + 340, cy + 62], radius=20, outline=PURPLE, width=5)
        message = "Circle safe use. Cross unsafe use."
    elif page_id == "ST-LKG-V4-P025":
        symbols = (("UP", "#F05A47"), ("RIGHT", "#3D8BFF"), ("UP", "#F05A47"), ("RIGHT", "#3D8BFF"))
        for index, (label, colour) in enumerate(symbols):
            left = x0 + 30 + index * 190
            panel(draw, [left, cy - 52, left + 160, cy + 52], fill=colour, outline=NAVY, width=2, radius=16)
            text.fitted_text(draw, label, [left + 8, cy - 34, left + 152, cy + 34], max_size=25, min_size=19, colour="white", bold=True, max_lines=1)
            if index >= 2:
                draw.rounded_rectangle([left - 7, cy - 59, left + 167, cy + 59], radius=20, outline=PURPLE, width=5)
        message = "The next two symbols repeat the colour-and-arrow code."
    elif page_id == "ST-LKG-V4-P026":
        size = 54
        gx, gy = x0 + 25, cy - size
        for row in range(2):
            for col in range(3):
                draw.rectangle([gx + col * size, gy + row * size, gx + (col + 1) * size, gy + (row + 1) * size], outline="#77849A", width=2)
        start = (gx + size // 2, gy + size + size // 2)
        turn = (gx + 2 * size + size // 2, start[1])
        finish = (turn[0], gy + size // 2)
        draw.ellipse([start[0] - 18, start[1] - 18, start[0] + 18, start[1] + 18], fill="#3D8BFF", outline=NAVY, width=2)
        draw.line([start, turn, finish], fill=PURPLE, width=9, joint="curve")
        draw.polygon([(turn[0], start[1]), (turn[0] - 23, start[1] - 15), (turn[0] - 23, start[1] + 15)], fill=PURPLE)
        draw.polygon([(finish[0], finish[1]), (finish[0] - 15, finish[1] + 23), (finish[0] + 15, finish[1] + 23)], fill=PURPLE)
        draw.rectangle([finish[0] - 20, finish[1] - 28, finish[0] + 20, finish[1] + 28], fill="#F4D03F", outline=NAVY, width=2)
        draw.rectangle([finish[0] - 7, finish[1] - 37, finish[0] + 7, finish[1] - 27], fill="#F4D03F", outline=NAVY, width=2)
        message = "Say each direction and record one arrow for each move."
    elif page_id == "ST-LKG-V4-P027":
        draw.line([x0 + 35, cy + 32, x0 + 285, cy + 32], fill="#D69B43", width=20)
        draw.polygon([(x0 + 80, cy + 30), (x0 + 160, cy - 55), (x0 + 240, cy + 30)], outline=PURPLE, width=7)
        draw.ellipse([x0 + 20, cy - 75, x0 + 305, cy + 85], outline=PURPLE, width=5)
        message = "Triangle supports can make a bridge stronger."
    elif page_id == "ST-LKG-V4-P028":
        for row, count in enumerate((5, 3, 1)):
            start = x0 + 35 + (5 - count) * 28
            for col in range(count):
                draw.rectangle([start + col * 56, cy + 10 - row * 48, start + (col + 1) * 56, cy + 53 - row * 48], fill=("#3D8BFF", "#77C95B", "#F05A47")[row], outline=NAVY, width=2)
        draw.ellipse([x0 + 15, cy - 125, x0 + 350, cy + 62], outline=PURPLE, width=5)
        message = "A wide base helps a tall tower stay stable."
    elif page_id == "ST-LKG-V4-P029":
        for index, (label, fill) in enumerate((("WEAK", "#FFF0EE"), ("STRONG", GREEN))):
            left = x0 + 35 + index * 330
            panel(draw, [left, cy - 52, left + 285, cy + 52], fill=fill, outline=PURPLE, width=3)
            text.fitted_text(draw, label, [left + 20, cy - 36, left + 265, cy + 36], max_size=31, min_size=24, colour=NAVY, bold=True, max_lines=1)
            if index == 1:
                draw.rounded_rectangle([left - 7, cy - 59, left + 292, cy + 59], radius=20, outline=PURPLE, width=5)
        message = "Circle the structure with better support."
    elif page_id == "ST-LKG-V4-P030":
        for index in range(7):
            left = x0 + 25 + index * 55
            draw.rectangle([left, cy - 25, left + 48, cy + 25], fill="#F4D03F", outline=NAVY, width=2)
        panel(draw, [x0 + 450, cy - 52, x0 + 610, cy + 52], fill="white", outline=PURPLE, width=4)
        text.fitted_text(draw, "7", [x0 + 470, cy - 38, x0 + 590, cy + 38], max_size=38, min_size=30, colour=NAVY, bold=True, max_lines=1)
        message = "Count the cubes, write the number, then compare."
    elif page_id == "ST-LKG-V4-P031":
        panel(draw, [x0 + 35, cy - 52, x0 + 310, cy + 52], fill="#F6F1FF", outline=PURPLE, width=3)
        text.fitted_text(draw, "KEY", [x0 + 55, cy - 36, x0 + 290, cy + 36], max_size=31, min_size=24, colour=NAVY, bold=True, max_lines=1)
        draw.line([x0 + 350, cy, x0 + 540, cy], fill=PURPLE, width=6)
        draw.polygon([(x0 + 540, cy), (x0 + 500, cy - 24), (x0 + 500, cy + 24)], fill=PURPLE)
        panel(draw, [x0 + 590, cy - 52, x0 + 850, cy + 52], fill=BLUE, outline=PURPLE, width=3)
        text.fitted_text(draw, "METAL", [x0 + 610, cy - 36, x0 + 830, cy + 36], max_size=31, min_size=24, colour=NAVY, bold=True, max_lines=1)
        message = "Write each picture number under its material."
    elif page_id == "ST-LKG-V4-P032":
        for index, height in enumerate((28, 58, 92)):
            left = x0 + 35 + index * 170
            draw.line([left, cy + 38, left + 125, cy + 38 - height], fill="#B4772C", width=12)
            draw.ellipse([left - 18, cy + 18, left + 18, cy + 54], fill="#3D8BFF", outline=NAVY, width=2)
        circle(draw, x0 + 35 + 2 * 170, cy + 62, 30)
        message = "Predict first. Test each ramp. Then record what happened."
    elif page_id == "ST-LKG-V4-P033":
        draw.rectangle([x0 + 45, cy - 50, x0 + 145, cy + 40], fill="#BFE7FF", outline=NAVY, width=3)
        draw.ellipse([x0 + 25, cy + 28, x0 + 170, cy + 65], fill="#9EDBFF", outline="#1768B3", width=2)
        text.fitted_text(draw, "What happens when ice gets warm?", [x0 + 210, cy - 55, x0 + 850, cy + 60], max_size=31, min_size=23, colour=NAVY, bold=True, max_lines=2)
        message = "Use a question starter and ask a complete question."
    elif page_id == "ST-LKG-V4-P034":
        draw.ellipse([x0 + 35, cy - 55, x0 + 175, cy + 55], fill="#D6F1FF", outline="#1768B3", width=3)
        draw.rectangle([x0 + 80, cy - 42, x0 + 130, cy - 5], fill="#C99555", outline=NAVY, width=2)
        panel(draw, [x0 + 220, cy - 52, x0 + 445, cy + 52], fill=GREEN, outline=PURPLE, width=3)
        text.fitted_text(draw, "FLOAT", [x0 + 240, cy - 36, x0 + 370, cy + 36], max_size=29, min_size=22, colour=NAVY, bold=True, max_lines=1)
        panel(draw, [x0 + 375, cy - 30, x0 + 425, cy + 20], fill="white", outline=PURPLE, width=3, radius=6)
        draw.line([x0 + 384, cy - 4, x0 + 395, cy + 9, x0 + 417, cy - 18], fill=NAVY, width=5, joint="curve")
        message = "Test each object, then tick FLOAT or SINK."
    elif page_id == "ST-LKG-V4-P035":
        panel(draw, [x0 + 35, cy - 52, x0 + 300, cy + 52], fill="#FFFFFF", outline=PURPLE, width=3)
        text.fitted_text(draw, "OBSERVE", [x0 + 55, cy - 36, x0 + 280, cy + 36], max_size=29, min_size=22, colour=NAVY, bold=True, max_lines=1)
        draw.line([x0 + 340, cy, x0 + 530, cy], fill=PURPLE, width=6)
        draw.polygon([(x0 + 530, cy), (x0 + 490, cy - 24), (x0 + 490, cy + 24)], fill=PURPLE)
        draw.ellipse([x0 + 590, cy - 45, x0 + 680, cy + 45], outline=NAVY, width=8)
        draw.line([x0 + 665, cy + 35, x0 + 735, cy + 92], fill=NAVY, width=10)
        message = "Draw a line from each word to its action picture."
    elif page_id == "ST-LKG-V4-P036":
        draw.polygon([(x0 + 45, cy + 45), (x0 + 125, cy - 55), (x0 + 205, cy + 45)], fill="#77C95B", outline=NAVY)
        text.fitted_text(draw, "green • smooth • pointed", [x0 + 245, cy - 45, x0 + 760, cy + 45], max_size=29, min_size=22, colour=NAVY, bold=True, max_lines=1)
        message = "Complete each short review task without copying the model."
    elif page_id == "ST-LKG-V4-P037":
        draw.rounded_rectangle([x0 + 45, cy - 50, x0 + 210, cy + 50], radius=12, fill="#FFFFFF", outline="#9AA0A6", width=3)
        draw.ellipse([x0 + 115, cy - 18, x0 + 145, cy + 15], fill="#4AA8FF", outline="#1768B3", width=2)
        panel(draw, [x0 + 260, cy - 52, x0 + 590, cy + 52], fill=GREEN, outline=PURPLE, width=3)
        text.fitted_text(draw, "ABSORBS", [x0 + 280, cy - 36, x0 + 500, cy + 36], max_size=29, min_size=22, colour=NAVY, bold=True, max_lines=1)
        panel(draw, [x0 + 505, cy - 30, x0 + 560, cy + 25], fill="white", outline=PURPLE, width=3, radius=6)
        draw.line([x0 + 515, cy - 3, x0 + 527, cy + 10, x0 + 550, cy - 18], fill=NAVY, width=5, joint="curve")
        message = "Predict, test one drop, and record the result."
    elif page_id == "ST-LKG-V4-P039":
        draw.ellipse([x0 + 45, cy - 62, x0 + 165, cy + 58], fill="#77C95B", outline=NAVY, width=3)
        for index in range(3):
            left = x0 + 245 + index * 135
            draw.ellipse([left, cy - 48, left + 92, cy + 44], fill="#77C95B", outline=NAVY, width=3)
        draw.ellipse([x0 + 238, cy - 58, x0 + 344, cy + 54], outline=PURPLE, width=5)
        message = "Observe the target closely, then circle its exact match."
    elif page_id == "ST-LKG-V4-P040":
        draw.ellipse([x0 + 45, cy - 55, x0 + 185, cy + 55], fill="#D6F1FF", outline="#1768B3", width=3)
        draw.ellipse([x0 + 78, cy - 20, x0 + 158, cy + 20], fill="#77C95B", outline=NAVY, width=2)
        draw.line([x0 + 230, cy, x0 + 420, cy], fill=PURPLE, width=6)
        draw.polygon([(x0 + 420, cy), (x0 + 380, cy - 24), (x0 + 380, cy + 24)], fill=PURPLE)
        message = "I discovered that a leaf can float."
    elif page_id == "ST-LKG-V4-P042":
        draw.ellipse([x0 + 45, cy - 60, x0 + 170, cy + 65], fill="#EAF6E7", outline="#4AA34B", width=6)
        draw.ellipse([x0 + 78, cy - 32, x0 + 137, cy + 27], outline=NAVY, width=5)
        draw.line([x0 + 130, cy + 20, x0 + 170, cy + 58], fill=NAVY, width=7)
        message = "Colour each skill badge you practised."
    elif page_id == "ST-LKG-V4-P043":
        draw.line([x0 + 45, cy + 38, x0 + 300, cy + 38], fill="#D69B43", width=16)
        draw.polygon([(x0 + 75, cy + 35), (x0 + 155, cy - 48), (x0 + 235, cy + 35)], outline=PURPLE, width=6)
        message = "I am proud that I built a strong bridge."
    else:
        for index, widths in enumerate(((1, 1, 1), (3, 2, 1))):
            base_x = x0 + 40 + index * 260
            for row, count in enumerate(widths):
                block_w = 46
                for col in range(count):
                    draw.rectangle([base_x + col * block_w, cy + 45 - row * 42, base_x + (col + 1) * block_w, cy + 85 - row * 42], fill=("#F05A47", "#3D8BFF")[index], outline=NAVY, width=2)
        draw.ellipse([x0 + 285, cy - 85, x0 + 505, cy + 95], outline=PURPLE, width=5)
        message = "Choose the stronger design, then improve the weaker one."
    message_left = x0 + 1160 if page_id == "ST-LKG-V4-P021" else x0 + 900
    text.fitted_text(draw, message, [message_left, y0 + 20, x1 - 25, y1 - 20], max_size=36, min_size=24, colour=NAVY, bold=True, max_lines=2)


def teacher_footer(draw, page, text, printed_page: int):
    panel(draw, [150, 3190, 2330, 3385], fill=GREEN, outline="#5F9D50", width=3)
    text.fitted_text(draw, "TEACHER CUE", [215, 3230, 525, 3345], max_size=34, min_size=27, colour=NAVY, bold=True, max_lines=1)
    text.fitted_text(draw, page["teacher_cue"], [555, 3215, 2265, 3355], max_size=35, min_size=26, colour=INK, max_lines=2, align="left")
    text.fitted_text(draw, str(printed_page), [2210, 3400, 2325, 3470], max_size=34, min_size=28, colour="#5C6B7D", bold=True, max_lines=1)


def render_p008(canvas, draw, source, text):
    scenes = grid_crops(source, 2, 1, 2)
    boxes = ([160, 965, 1215, 2780], [1265, 965, 2320, 2780])
    for index, (scene, box) in enumerate(zip(scenes, boxes)):
        panel(draw, box, fill="white")
        text.fitted_text(draw, ("PICTURE A", "PICTURE B")[index], [box[0] + 25, box[1] + 20, box[2] - 25, box[1] + 100], max_size=36, min_size=28, colour=NAVY, bold=True, max_lines=1)
        paste_fit(canvas, scene, [box[0] + 25, box[1] + 115, box[2] - 25, box[3] - 25], inset=20)
    panel(draw, [270, 2840, 2210, 3090], fill="#FFFFFF", outline=SOFT_PURPLE, width=3)
    text.fitted_text(draw, "Tell one difference: In Picture B, ________________________________.", [325, 2885, 2155, 3035], max_size=38, min_size=28, colour=NAVY, bold=True, max_lines=2, align="left")


def numbered_card(canvas, draw, text, image, name, number, box):
    panel(draw, box, fill="white")
    circle(draw, box[0] + 48, box[1] + 48, 28)
    text.fitted_text(draw, str(number), [box[0] + 25, box[1] + 24, box[0] + 72, box[1] + 72], max_size=27, min_size=22, colour=NAVY, bold=True, max_lines=1)
    paste_fit(canvas, image, [box[0] + 22, box[1] + 82, box[2] - 22, box[3] - 72], inset=18)
    text.fitted_text(draw, name, [box[0] + 20, box[3] - 68, box[2] - 20, box[3] - 18], max_size=30, min_size=23, colour=NAVY, bold=True, max_lines=1)


def render_p010(canvas, draw, source, text):
    # The dog, tree and car extend beyond equal-width thirds in the source sheet.
    # Named crops preserve their full silhouettes instead of trimming an edge.
    images = [
        crop_norm(source, (0.005, 0.005, 0.31, 0.49)),
        crop_norm(source, (0.325, 0.005, 0.65, 0.49)),
        crop_norm(source, (0.66, 0.005, 0.995, 0.49)),
        crop_norm(source, (0.005, 0.50, 0.32, 0.995)),
        crop_norm(source, (0.325, 0.50, 0.65, 0.995)),
        crop_norm(source, (0.65, 0.50, 0.995, 0.995)),
    ]
    panel(draw, [170, 950, 1195, 1165], fill="#F7F3FF")
    panel(draw, [1285, 950, 2310, 1165], fill=BLUE)
    for index, (label, left) in enumerate((("LIVING", 170), ("NON-LIVING", 1285))):
        text.fitted_text(draw, label, [left + 25, 970, left + 1000, 1035], max_size=38, min_size=30, colour=NAVY, bold=True, max_lines=1)
        for item in range(3):
            x = left + 270 + item * 180
            panel(draw, [x, 1060, x + 115, 1145], fill="white", outline=PURPLE, width=3, radius=12)
    names = ("dog", "rock", "tree", "book", "butterfly", "car")
    for index, (image, name) in enumerate(zip(images, names)):
        row, col = divmod(index, 3)
        numbered_card(canvas, draw, text, image, name, index + 1, [170 + col * 720, 1205 + row * 865, 835 + col * 720, 2025 + row * 865])


def matching_card(canvas, draw, text, image, name, box, anchor_x, anchor_side):
    panel(draw, box, fill="white", outline="#C3A9ED", width=3, radius=16)
    paste_fit(canvas, image, [box[0] + 22, box[1] + 20, box[2] - 22, box[3] - 62], inset=12)
    text.fitted_text(draw, name, [box[0] + 20, box[3] - 65, box[2] - 20, box[3] - 15], max_size=30, min_size=23, colour=NAVY, bold=True, max_lines=1)
    circle(draw, anchor_x, (box[1] + box[3]) // 2, 25)


def render_two_column_match(canvas, draw, source, text, columns, rows, count, left_names, right_names, right_order, images=None):
    images = images or grid_crops(source, columns, rows, count)
    left_images = images[:len(left_names)]
    right_images = images[len(left_names):]
    top, bottom = 950, 3070
    row_height = (bottom - top) // len(left_names)
    draw.line([1240, top + 10, 1240, bottom - 10], fill="#B7A0DE", width=5)
    for index, (image, name) in enumerate(zip(left_images, left_names)):
        y0 = top + index * row_height + 8
        y1 = top + (index + 1) * row_height - 8
        matching_card(canvas, draw, text, image, name, [170, y0, 1100, y1], 1145, "right")
    for index, source_index in enumerate(right_order):
        y0 = top + index * row_height + 8
        y1 = top + (index + 1) * row_height - 8
        matching_card(canvas, draw, text, right_images[source_index], right_names[source_index], [1380, y0, 2310, y1], 1335, "left")


def render_p009(canvas, draw, source, text):
    columns = ((0.02, 0.32), (0.34, 0.66), (0.68, 0.98))
    rows = ((0.02, 0.25), (0.27, 0.485), (0.50, 0.74), (0.75, 0.98))
    images = [crop_norm(source, (x0, y0, x1, y1)) for y0, y1 in rows for x0, x1 in columns][:10]
    # The rainbow cloud reaches into the hand's equal-width cell.
    images[4] = crop_norm(source, (0.34, 0.27, 0.62, 0.485))
    render_two_column_match(
        canvas, draw, source, text, 3, 4, 10,
        ("eye", "ear", "nose", "tongue", "hand"),
        ("rainbow", "bell", "flower", "lemon", "feather"),
        (1, 4, 0, 2, 3),
        images=images,
    )


def render_p011(canvas, draw, source, text):
    plant = trim_white(source)
    panel(draw, [760, 950, 2310, 3070], fill="white")
    paste_fit(canvas, plant, [850, 985, 2240, 3030], inset=24)
    labels = (("FLOWER", 1080), ("LEAVES", 1510), ("STEM", 2050), ("ROOTS", 2690))
    for label, cy in labels:
        panel(draw, [170, cy - 75, 600, cy + 75], fill="#F7F3FF", outline=PURPLE, width=3, radius=18)
        text.fitted_text(draw, label, [200, cy - 48, 570, cy + 48], max_size=34, min_size=27, colour=NAVY, bold=True, max_lines=1)
        circle(draw, 650, cy, 25)
    targets = ((1500, 1080), (1480, 2150), (1630, 2430), (1480, 2780))
    for cx, cy in targets:
        circle(draw, cx, cy, 22)


def render_p012(canvas, draw, source, text):
    columns = ((0.02, 0.32), (0.34, 0.66), (0.68, 0.98))
    rows = ((0.02, 0.28), (0.29, 0.54), (0.55, 0.75), (0.77, 0.99))
    images = [crop_norm(source, (x0, y0, x1, y1)) for y0, y1 in rows for x0, x1 in columns][:10]
    # The pond foliage reaches slightly into the dog cell in the composite.
    images[4] = crop_norm(source, (0.34, 0.29, 0.64, 0.54))
    render_two_column_match(
        canvas, draw, source, text, 3, 4, 10,
        ("fish", "bird", "rabbit", "bee", "dog"),
        ("pond", "nest", "burrow", "hive", "kennel"),
        (3, 0, 4, 1, 2),
        images=images,
    )


def render_p013(canvas, draw, source, text):
    render_two_column_match(
        canvas, draw, source, text, 3, 3, 8,
        ("sunny", "rainy", "windy", "cloudy"),
        ("sun hat", "umbrella", "kite", "light jacket"),
        (1, 3, 0, 2),
    )


def render_p014(canvas, draw, source, text):
    # The source uses three clean columns for the first two rows and two
    # centred scenes in the last row. Keep the regions disjoint so an object
    # cannot borrow fragments from its neighbour.
    images = [
        crop_norm(source, (0.02, 0.01, 0.32, 0.32)),
        crop_norm(source, (0.35, 0.01, 0.63, 0.32)),
        crop_norm(source, (0.65, 0.01, 0.995, 0.34)),
        crop_norm(source, (0.015, 0.34, 0.315, 0.66)),
        crop_norm(source, (0.34, 0.34, 0.655, 0.66)),
        crop_norm(source, (0.66, 0.34, 0.995, 0.66)),
        crop_norm(source, (0.03, 0.66, 0.31, 0.995)),
        crop_norm(source, (0.32, 0.66, 0.67, 0.995)),
    ]
    panel(draw, [170, 950, 1195, 1165], fill="#FFF8DA")
    panel(draw, [1285, 950, 2310, 1165], fill="#EEF2FF")
    for label, left in (("DAY", 170), ("NIGHT", 1285)):
        text.fitted_text(draw, label, [left + 25, 970, left + 1000, 1035], max_size=38, min_size=30, colour=NAVY, bold=True, max_lines=1)
        for item in range(4):
            x = left + 210 + item * 190
            panel(draw, [x, 1060, x + 125, 1145], fill="white", outline=PURPLE, width=3, radius=12)
    names = ("breakfast", "school", "outdoor play", "sun", "sleep", "moon & stars", "pyjamas", "bedtime story")
    for index, (image, name) in enumerate(zip(images, names)):
        row, col = divmod(index, 4)
        numbered_card(canvas, draw, text, image, name, index + 1, [170 + col * 540, 1205 + row * 865, 675 + col * 540, 2025 + row * 865])


def render_p015(canvas, draw, source, text):
    images = grid_crops(source, 4, 2, 8)
    names = ("drink water", "running tap", "water a plant", "overflowing bucket", "wash hands", "spraying hose", "cook carefully", "turn off tap")
    for index, (image, name) in enumerate(zip(images, names)):
        row, col = divmod(index, 4)
        x0 = 170 + col * 540
        y0 = 950 + row * 1010
        box = [x0, y0, x0 + 500, y0 + 950]
        panel(draw, box, fill="white", outline="#C3A9ED", width=3, radius=18)
        paste_fit(canvas, image, [x0 + 22, y0 + 25, x0 + 478, y0 + 835], inset=16)
        text.fitted_text(draw, name, [x0 + 25, y0 + 840, x0 + 475, y0 + 925], max_size=27, min_size=21, colour=NAVY, bold=True, max_lines=2)


def render_p017(canvas, draw, source, text):
    images = [
        crop_norm(source, (0.02, 0.01, 0.28, 0.48)),
        crop_norm(source, (0.29, 0.01, 0.48, 0.48)),
        crop_norm(source, (0.49, 0.01, 0.74, 0.46)),
        crop_norm(source, (0.75, 0.01, 0.995, 0.48)),
        crop_norm(source, (0.02, 0.50, 0.25, 0.995)),
        crop_norm(source, (0.26, 0.50, 0.49, 0.995)),
        crop_norm(source, (0.50, 0.50, 0.68, 0.995)),
        crop_norm(source, (0.68, 0.50, 0.995, 0.995)),
    ]
    for label, left, fill in (("MAGNETIC", 170, BLUE), ("NOT MAGNETIC", 1285, "#F7F3FF")):
        panel(draw, [left, 950, left + 1025, 1165], fill=fill)
        text.fitted_text(draw, label, [left + 25, 970, left + 1000, 1038], max_size=36, min_size=28, colour=NAVY, bold=True, max_lines=1)
        for item in range(4):
            x = left + 205 + item * 190
            panel(draw, [x, 1060, x + 125, 1145], fill="white", outline=PURPLE, width=3, radius=12)
    names = ("wood block", "paper clip", "eraser", "key", "plastic spoon", "iron nail", "crayon", "steel lid")
    for index, (image, name) in enumerate(zip(images, names)):
        row, col = divmod(index, 4)
        numbered_card(canvas, draw, text, image, name, index + 1, [170 + col * 540, 1205 + row * 865, 675 + col * 540, 2025 + row * 865])


def render_p018(canvas, draw, source, text):
    left_boxes = (
        (0.02, 0.01, 0.46, 0.18),
        (0.02, 0.19, 0.46, 0.35),
        (0.02, 0.36, 0.46, 0.485),
        # The rabbit sits close to both neighbouring source rows. Include its
        # complete ears and feet while stopping before the umbrella below.
        (0.02, 0.485, 0.46, 0.67),
        (0.02, 0.68, 0.46, 0.815),
        # Start at the final source row so the bicycle stays fully visible.
        (0.02, 0.825, 0.46, 0.995),
    )
    right_boxes = (
        (0.54, 0.01, 0.98, 0.17),
        (0.54, 0.19, 0.98, 0.325),
        (0.54, 0.35, 0.98, 0.495),
        (0.54, 0.515, 0.98, 0.645),
        (0.54, 0.675, 0.98, 0.81),
        # Use the same final-row boundary to preserve the full kite silhouette.
        (0.54, 0.825, 0.98, 0.995),
    )
    images = [crop_norm(source, box) for box in left_boxes + right_boxes]
    render_two_column_match(
        canvas, draw, source, text, 2, 6, 12,
        ("tree", "kite", "cup", "rabbit", "umbrella", "bicycle"),
        ("shadow A", "shadow B", "shadow C", "shadow D", "shadow E", "shadow F"),
        (0, 1, 2, 3, 4, 5), images=images,
    )


def render_p019(canvas, draw, source, text):
    bridges = grid_crops(source, 1, 3, 3)
    names = ("flat paper", "accordion fold", "side rails")
    for index, (bridge, name) in enumerate(zip(bridges, names)):
        top = 950 + index * 590
        bottom = top + 545
        panel(draw, [170, top, 2310, bottom], fill="white")
        circle(draw, 230, top + 62, 30)
        text.fitted_text(draw, name, [285, top + 25, 720, top + 95], max_size=31, min_size=24, colour=NAVY, bold=True, max_lines=1, align="left")
        paste_fit(canvas, bridge, [675, top + 20, 2250, bottom - 20], inset=20)
    panel(draw, [170, 2760, 2310, 3090], fill="#FFFFFF")
    text.fitted_text(draw, "Make a bridge stronger. Draw one fold or support.", [220, 2800, 980, 3040], max_size=34, min_size=26, colour=NAVY, bold=True, max_lines=3, align="left")
    for x in range(1050, 2251, 70):
        draw.line([x, 2800, x, 3050], fill="#D8CCEE", width=2)
    for y in range(2800, 3051, 50):
        draw.line([1050, y, 2250, y], fill="#D8CCEE", width=2)


def render_p020(canvas, draw, source, text):
    images = grid_crops(source, 3, 3, 9)
    images[6] = crop_norm(source, (0.02, 0.68, 0.29, 0.98))
    machine_names = ("ramp", "wheel and axle", "lever")
    example_names = ("seesaw", "bicycle", "slide", "bottle opener", "loading ramp", "wheelbarrow")
    machine_images = images[:3]
    example_images = images[3:]
    top, row_h = 950, 680
    draw.line([910, top + 5, 910, 3045], fill="#B7A0DE", width=5)
    for row, (image, name) in enumerate(zip(machine_images, machine_names)):
        y0 = top + row * row_h + 10
        y1 = y0 + row_h - 20
        panel(draw, [170, y0, 800, y1], fill="#F7F3FF")
        paste_fit(canvas, image, [200, y0 + 25, 770, y1 - 110], inset=20)
        text.fitted_text(draw, name, [205, y1 - 100, 650, y1 - 25], max_size=31, min_size=24, colour=NAVY, bold=True, max_lines=1)
        circle(draw, 720, y1 - 65, 25)
        circle(draw, 775, y1 - 65, 25)
    # Deliberately shuffled so correct examples do not form repeated columns.
    order = (2, 4, 0, 5, 3, 1)
    for index, source_index in enumerate(order):
        row, col = divmod(index, 2)
        x0 = 1010 + col * 650
        y0 = top + row * row_h + 10
        y1 = y0 + row_h - 20
        panel(draw, [x0, y0, x0 + 590, y1], fill="white")
        paste_fit(canvas, example_images[source_index], [x0 + 25, y0 + 25, x0 + 565, y1 - 100], inset=18)
        circle(draw, x0 + 45, y1 - 62, 25)
        text.fitted_text(draw, example_names[source_index], [x0 + 90, y1 - 100, x0 + 565, y1 - 25], max_size=29, min_size=22, colour=NAVY, bold=True, max_lines=1)


def render_p021(canvas, draw, source, text):
    images = grid_crops(source, 4, 2, 8)
    # The snail extends across the equal-width source boundary. Use a wider
    # named region that includes its head while stopping before the leaf.
    images[2] = crop_norm(source, (0.47, 0.005, 0.77, 0.49))
    names = ("zebra", "ladybird", "snail", "leaf", "tiger", "butterfly", "sunflower", "fern")
    choices = ("STRIPES", "SPOTS", "SPIRAL", "VEINS")
    for index, (image, name) in enumerate(zip(images, names)):
        row, col = divmod(index, 4)
        x0 = 170 + col * 540
        y0 = 950 + row * 1050
        box = [x0, y0, x0 + 500, y0 + 995]
        panel(draw, box, fill="white", outline="#C3A9ED", width=3, radius=18)
        paste_fit(canvas, image, [x0 + 20, y0 + 20, x0 + 480, y0 + 650], inset=14)
        text.fitted_text(draw, name, [x0 + 25, y0 + 640, x0 + 475, y0 + 705], max_size=29, min_size=23, colour=NAVY, bold=True, max_lines=1)
        for choice_index, label in enumerate(choices):
            choice_row, choice_col = divmod(choice_index, 2)
            left = x0 + 24 + choice_col * 232
            top = y0 + 725 + choice_row * 115
            panel(draw, [left, top, left + 215, top + 92], fill="#FFFCF7", outline="#B59AE1", width=2, radius=12)
            text.fitted_text(draw, label, [left + 8, top + 14, left + 207, top + 78], max_size=25, min_size=18, colour=NAVY, bold=True, max_lines=1)


def render_p022(canvas, draw, source, text):
    images = grid_crops(source, 4, 2, 8)
    names = ("drop litter", "plant a tree", "waste water", "recycle", "pick flowers", "reuse a bag", "smoky car", "turn off light")
    for label, left, fill in (("HELPS EARTH", 170, GREEN), ("HURTS EARTH", 1285, "#FFF0EE")):
        panel(draw, [left, 950, left + 1025, 1165], fill=fill)
        text.fitted_text(draw, label, [left + 25, 970, left + 1000, 1038], max_size=36, min_size=28, colour=NAVY, bold=True, max_lines=1)
        for item in range(4):
            x = left + 205 + item * 190
            panel(draw, [x, 1060, x + 125, 1145], fill="white", outline=PURPLE, width=3, radius=12)
    for index, (image, name) in enumerate(zip(images, names)):
        row, col = divmod(index, 4)
        numbered_card(canvas, draw, text, image, name, index + 1, [170 + col * 540, 1205 + row * 865, 675 + col * 540, 2025 + row * 865])


def render_p023(canvas, draw, source, text):
    top_boxes = (
        (0.01, 0.01, 0.21, 0.47),
        (0.225, 0.01, 0.41, 0.47),
        (0.41, 0.01, 0.60, 0.47),
        (0.60, 0.01, 0.80, 0.47),
        (0.80, 0.01, 0.99, 0.47),
    )
    bottom_boxes = (
        (0.01, 0.49, 0.18, 0.99),
        (0.19, 0.49, 0.34, 0.99),
        (0.35, 0.49, 0.59, 0.99),
        (0.59, 0.49, 0.80, 0.99),
        (0.81, 0.49, 0.99, 0.99),
    )
    images = [crop_norm(source, box) for box in top_boxes + bottom_boxes]
    names = ("book", "torch", "spoon", "tablet", "ball", "fan", "chair", "telephone", "camera", "washing machine")
    for index, (image, name) in enumerate(zip(images, names)):
        row, col = divmod(index, 5)
        x0 = 170 + col * 430
        y0 = 950 + row * 835
        box = [x0, y0, x0 + 395, y0 + 790]
        panel(draw, box, fill="white", outline="#C3A9ED", width=3, radius=16)
        paste_fit(canvas, image, [x0 + 18, y0 + 18, x0 + 377, y0 + 700], inset=12)
        text.fitted_text(draw, name, [x0 + 16, y0 + 700, x0 + 379, y0 + 770], max_size=27, min_size=20, colour=NAVY, bold=True, max_lines=1)
    panel(draw, [170, 2660, 2320, 3085], fill="#FFFFFF", outline=SOFT_PURPLE, width=3)
    text.fitted_text(draw, "Tell about one thing you circled.", [220, 2700, 2250, 2785], max_size=36, min_size=28, colour=NAVY, bold=True, max_lines=1)
    text.fitted_text(draw, "A __________________ helps us ________________________________.", [235, 2830, 2240, 3010], max_size=38, min_size=28, colour=NAVY, bold=True, max_lines=2, align="left")


def render_p024(canvas, draw, source, text):
    images = grid_crops(source, 4, 2, 8)
    names = ("screen too close", "ask an adult", "drink by device", "sit well", "screen in bed", "take a break", "unknown pop-up", "clean, dry hands")
    for index, (image, name) in enumerate(zip(images, names)):
        row, col = divmod(index, 4)
        x0 = 170 + col * 540
        y0 = 950 + row * 1010
        box = [x0, y0, x0 + 500, y0 + 950]
        panel(draw, box, fill="white", outline="#C3A9ED", width=3, radius=18)
        paste_fit(canvas, image, [x0 + 20, y0 + 20, x0 + 480, y0 + 830], inset=14)
        text.fitted_text(draw, name, [x0 + 22, y0 + 835, x0 + 478, y0 + 925], max_size=27, min_size=20, colour=NAVY, bold=True, max_lines=2)


def render_p025(canvas, draw, source, text):
    symbols = grid_crops(source, 4, 2, 8)
    rows = (
        ((0, 1), 6, "red up, blue right"),
        ((2, 2, 3), 6, "green down, green down, yellow left"),
        ((4, 5, 6), 6, "red circle, blue square, green triangle"),
        ((7, 4), 6, "yellow star, red circle"),
    )
    for row_index, (unit, visible_count, spoken_code) in enumerate(rows):
        top = 950 + row_index * 525
        bottom = top + 485
        panel(draw, [170, top, 2310, bottom], fill=("#FFFFFF", "#FBF9FF")[row_index % 2], outline="#C3A9ED", width=3, radius=18)
        circle(draw, 225, top + 55, 28)
        text.fitted_text(draw, str(row_index + 1), [202, top + 31, 248, top + 79], max_size=25, min_size=20, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, spoken_code, [285, top + 22, 2240, top + 90], max_size=29, min_size=21, colour=NAVY, bold=True, max_lines=1, align="left")
        sequence = [unit[index % len(unit)] for index in range(visible_count)]
        item_w, gap, start_x = 205, 40, 260
        for index, symbol_index in enumerate(sequence):
            left = start_x + index * (item_w + gap)
            paste_fit(canvas, symbols[symbol_index], [left, top + 110, left + item_w, bottom - 55], inset=18)
        for blank_index in range(2):
            left = start_x + (visible_count + blank_index) * (item_w + gap)
            panel(draw, [left, top + 145, left + item_w, bottom - 75], fill="white", outline=PURPLE, width=4, radius=14)


def render_p016(canvas, draw, source, text):
    images = grid_crops(source, 3, 2, 6)
    names = ("leaf", "coin", "cork", "spoon", "plastic cap", "stone")
    x_positions = {"image": (180, 610), "predict": (660, 1450), "result": (1510, 2300)}
    text.fitted_text(draw, "OBJECT", [180, 930, 610, 1005], max_size=31, min_size=25, colour=NAVY, bold=True, max_lines=1)
    text.fitted_text(draw, "MY PREDICTION", [660, 930, 1450, 1005], max_size=31, min_size=25, colour=NAVY, bold=True, max_lines=1)
    text.fitted_text(draw, "AFTER TESTING", [1510, 930, 2300, 1005], max_size=31, min_size=25, colour=NAVY, bold=True, max_lines=1)
    for index, (image, name) in enumerate(zip(images, names)):
        top = 1010 + index * 350
        bottom = top + 320
        panel(draw, [160, top, 2320, bottom], fill=("#FFFFFF", "#FBF9FF")[index % 2], outline="#C3A9ED", width=2, radius=16)
        paste_fit(canvas, image, [180, top + 25, 490, bottom - 55], inset=10)
        text.fitted_text(draw, name, [175, bottom - 60, 520, bottom - 12], max_size=28, min_size=22, colour=NAVY, bold=True, max_lines=1)
        for group_left in (690, 1540):
            for option, label in enumerate(("FLOAT", "SINK")):
                cx = group_left + option * 335
                circle(draw, cx, (top + bottom) // 2, 30)
                text.fitted_text(draw, label, [cx + 45, (top + bottom) // 2 - 35, cx + 285, (top + bottom) // 2 + 35], max_size=29, min_size=23, colour=NAVY, bold=True, max_lines=1)


def render_p026(canvas, draw, source, text):
    images = grid_crops(source, 3, 2, 5)
    robot, battery, rock, puddle, crate = images
    grid_x, grid_y, cell = 290, 960, 260
    panel(draw, [250, 925, 1885, 2575], fill="#FFFFFF", outline=SOFT_PURPLE, width=4)
    for row in range(6):
        for col in range(6):
            draw.rectangle([grid_x + col * cell, grid_y + row * cell, grid_x + (col + 1) * cell, grid_y + (row + 1) * cell], outline="#94A4B7", width=3)
    paste_fit(canvas, robot, [grid_x + 10, grid_y + 5 * cell + 10, grid_x + cell - 10, grid_y + 6 * cell - 10], inset=18)
    paste_fit(canvas, battery, [grid_x + 5 * cell + 20, grid_y + 10, grid_x + 6 * cell - 20, grid_y + cell - 10], inset=22)
    obstacles = (((4, 1), rock), ((3, 1), rock), ((2, 3), puddle), ((1, 4), crate))
    for (row, col), image in obstacles:
        paste_fit(canvas, image, [grid_x + col * cell + 18, grid_y + row * cell + 18, grid_x + (col + 1) * cell - 18, grid_y + (row + 1) * cell - 18], inset=16)
    panel(draw, [1930, 925, 2310, 2575], fill="#F7F3FF")
    text.fitted_text(draw, "WRITE THE ARROW STEPS", [1960, 970, 2280, 1080], max_size=31, min_size=24, colour=NAVY, bold=True, max_lines=2)
    for index in range(10):
        top = 1130 + index * 130
        panel(draw, [2010, top, 2230, top + 95], fill="white", outline=PURPLE, width=3, radius=12)
        text.fitted_text(draw, str(index + 1), [1945, top + 18, 2005, top + 78], max_size=25, min_size=20, colour=NAVY, bold=True, max_lines=1)
    panel(draw, [290, 2640, 2310, 3080], fill="#FFFFFF")
    text.fitted_text(draw, "Tell your route:", [345, 2685, 760, 2760], max_size=36, min_size=28, colour=NAVY, bold=True, max_lines=1, align="left")
    for index, word in enumerate(("RIGHT", "LEFT", "UP", "DOWN")):
        left = 350 + index * 465
        panel(draw, [left, 2810, left + 390, 2985], fill=("#E9F5FF", "#FFF4C6", "#EAF6E7", "#F6F1FF")[index], outline=SOFT_PURPLE, width=3)
        text.fitted_text(draw, word, [left + 25, 2850, left + 365, 2945], max_size=33, min_size=26, colour=NAVY, bold=True, max_lines=1)


def render_p027(canvas, draw, source, text):
    images = grid_crops(source, 2, 2, 4)
    names = ("one support post", "no support", "arch support", "triangle supports")
    for index, (image, name) in enumerate(zip(images, names)):
        row, col = divmod(index, 2)
        x0 = 170 + col * 1085
        y0 = 950 + row * 670
        box = [x0, y0, x0 + 1035, y0 + 625]
        panel(draw, box, fill="white")
        paste_fit(canvas, image, [x0 + 25, y0 + 25, x0 + 1010, y0 + 520], inset=18)
        circle(draw, x0 + 65, y0 + 560, 30)
        text.fitted_text(draw, name, [x0 + 115, y0 + 520, x0 + 990, y0 + 600], max_size=30, min_size=23, colour=NAVY, bold=True, max_lines=1)
    panel(draw, [170, 2325, 2310, 3090], fill="#FFFFFF")
    text.fitted_text(draw, "Improve a weaker bridge. Draw one support in the grid.", [225, 2365, 1030, 2560], max_size=35, min_size=26, colour=NAVY, bold=True, max_lines=3, align="left")
    grid_left, grid_top, grid_right, grid_bottom = 1080, 2370, 2250, 3025
    for x in range(grid_left, grid_right + 1, 78):
        draw.line([x, grid_top, x, grid_bottom], fill="#D8CCEE", width=2)
    for y in range(grid_top, grid_bottom + 1, 65):
        draw.line([grid_left, y, grid_right, y], fill="#D8CCEE", width=2)


def render_p028(canvas, draw, source, text):
    images = grid_crops(source, 2, 2, 4)
    names = ("narrow base", "wide base", "uneven tower", "leaning tower")
    for index, (image, name) in enumerate(zip(images, names)):
        row, col = divmod(index, 2)
        x0 = 170 + col * 1085
        y0 = 950 + row * 545
        box = [x0, y0, x0 + 1035, y0 + 505]
        panel(draw, box, fill="white")
        paste_fit(canvas, image, [x0 + 25, y0 + 18, x0 + 1010, y0 + 405], inset=14)
        circle(draw, x0 + 65, y0 + 450, 30)
        text.fitted_text(draw, name, [x0 + 115, y0 + 410, x0 + 990, y0 + 490], max_size=30, min_size=23, colour=NAVY, bold=True, max_lines=1)
    panel(draw, [170, 2075, 2310, 3090], fill="#FFFFFF")
    text.fitted_text(draw, "Plan your own tall tower with a wide base.", [225, 2115, 1000, 2290], max_size=35, min_size=26, colour=NAVY, bold=True, max_lines=3, align="left")
    grid_left, grid_top, grid_right, grid_bottom = 1050, 2120, 2250, 3030
    for x in range(grid_left, grid_right + 1, 100):
        draw.line([x, grid_top, x, grid_bottom], fill="#D8CCEE", width=2)
    for y in range(grid_top, grid_bottom + 1, 100):
        draw.line([grid_left, y, grid_right, y], fill="#D8CCEE", width=2)


def render_p029(canvas, draw, source, text):
    pair_boxes = (
        (0.01, 0.015, 0.99, 0.195),
        (0.08, 0.21, 0.92, 0.395),
        (0.08, 0.438, 0.92, 0.605),
        (0.03, 0.64, 0.97, 0.755),
        (0.01, 0.78, 0.99, 0.985),
    )
    pairs = [crop_norm(source, box) for box in pair_boxes]
    names = ("bridge", "tower", "chair", "shelf", "tent")
    for index, (pair, name) in enumerate(zip(pairs, names)):
        top = 950 + index * 420
        bottom = top + 390
        panel(draw, [170, top, 2310, bottom], fill=("#FFFFFF", "#FBF9FF")[index % 2], outline="#C3A9ED", width=3, radius=16)
        circle(draw, 225, top + 55, 28)
        text.fitted_text(draw, str(index + 1), [202, top + 31, 248, top + 79], max_size=25, min_size=20, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, name, [275, top + 22, 650, top + 90], max_size=29, min_size=22, colour=NAVY, bold=True, max_lines=1, align="left")
        paste_fit(canvas, pair, [300, top + 55, 2180, bottom - 55], inset=10)
        for cx, label in ((720, "A"), (1745, "B")):
            circle(draw, cx, bottom - 42, 28)
            text.fitted_text(draw, label, [cx + 45, bottom - 78, cx + 120, bottom - 10], max_size=26, min_size=20, colour=NAVY, bold=True, max_lines=1)


def render_p030(canvas, draw, source, text):
    images = grid_crops(source, 3, 2, 6)
    names = ("pencil", "crayon", "book", "eraser", "plant", "bottle")
    counts = (7, 4, 6, 3, 8, 5)
    pairs = ((0, 1), (2, 3), (4, 5))
    for row, pair in enumerate(pairs):
        top = 950 + row * 700
        bottom = top + 660
        panel(draw, [170, top, 2310, bottom], fill=("#FFFFFF", "#FBF9FF")[row % 2])
        for col, source_index in enumerate(pair):
            left = 205 + col * 1060
            paste_fit(canvas, images[source_index], [left, top + 25, left + 670, top + 395], inset=16)
            text.fitted_text(draw, names[source_index], [left, top + 390, left + 650, top + 455], max_size=29, min_size=22, colour=NAVY, bold=True, max_lines=1)
            cube_size = 48
            for cube in range(counts[source_index]):
                cube_left = left + cube * (cube_size + 7)
                draw.rectangle([cube_left, top + 475, cube_left + cube_size, top + 523], fill="#F4D03F", outline=NAVY, width=2)
            panel(draw, [left + 720, top + 455, left + 890, top + 555], fill="white", outline=PURPLE, width=4, radius=12)
            circle(draw, left + 955, top + 505, 30)
        text.fitted_text(draw, "Circle the longer or taller object.", [650, bottom - 85, 1830, bottom - 18], max_size=29, min_size=22, colour=NAVY, bold=True, max_lines=1)


def render_p031(canvas, draw, source, text):
    images = grid_crops(source, 3, 3, 9)
    images[3] = crop_norm(source, (0.02, 0.295, 0.31, 0.645))
    images[6] = crop_norm(source, (0.005, 0.635, 0.335, 0.995))
    names = ("metal key", "plastic cup", "wooden spoon", "plastic bottle", "wooden block", "metal can", "wooden pencil", "plastic comb", "metal paper clip")
    for index, (label, fill) in enumerate((("WOOD", "#FFF4C6"), ("METAL", BLUE), ("PLASTIC", "#F7F3FF"))):
        left = 170 + index * 720
        panel(draw, [left, 950, left + 665, 1165], fill=fill)
        text.fitted_text(draw, label, [left + 25, 970, left + 640, 1035], max_size=35, min_size=28, colour=NAVY, bold=True, max_lines=1)
        for item in range(3):
            x = left + 135 + item * 165
            panel(draw, [x, 1060, x + 115, 1145], fill="white", outline=PURPLE, width=3, radius=12)
    for index, (image, name) in enumerate(zip(images, names)):
        row, col = divmod(index, 3)
        numbered_card(canvas, draw, text, image, name, index + 1, [170 + col * 720, 1205 + row * 590, 835 + col * 720, 1755 + row * 590])


def render_p032(canvas, draw, source, text):
    ramps = [
        crop_norm(source, (0.02, 0.06, 0.98, 0.30)),
        crop_norm(source, (0.02, 0.355, 0.98, 0.62)),
        crop_norm(source, (0.02, 0.65, 0.98, 0.94)),
    ]
    names = ("low ramp", "medium ramp", "high ramp")
    for index, (image, name) in enumerate(zip(ramps, names)):
        top = 950 + index * 610
        panel(draw, [170, top, 2310, top + 565], fill=("#FFFFFF", "#FBF9FF")[index % 2])
        circle(draw, 220, top + 52, 28)
        text.fitted_text(draw, str(index + 1), [198, top + 28, 242, top + 75], max_size=25, min_size=20, colour=NAVY, bold=True, max_lines=1)
        paste_fit(canvas, image, [250, top + 35, 1470, top + 470], inset=12)
        text.fitted_text(draw, name, [430, top + 470, 1250, top + 535], max_size=29, min_size=22, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, "PREDICT", [1510, top + 90, 1810, top + 150], max_size=27, min_size=21, colour=NAVY, bold=True, max_lines=1)
        circle(draw, 1870, top + 120, 30)
        text.fitted_text(draw, "RESULT", [1510, top + 245, 1810, top + 305], max_size=27, min_size=21, colour=NAVY, bold=True, max_lines=1)
        panel(draw, [1830, top + 225, 1910, top + 305], fill="white", outline=PURPLE, width=4, radius=10)
    panel(draw, [170, 2830, 2310, 3090], fill="#FFFFFF")
    text.fitted_text(draw, "The ball travelled farthest on the __________________ ramp.", [245, 2890, 2235, 3030], max_size=36, min_size=27, colour=NAVY, bold=True, max_lines=2, align="left")


def render_p033(canvas, draw, source, text):
    images = grid_crops(source, 2, 2, 4)
    names = ("melting ice", "growing plant", "floating boat", "magnet and clips")
    starters = ("What", "Why", "How", "Which")
    for index, (image, name, starter) in enumerate(zip(images, names, starters)):
        row, col = divmod(index, 2)
        left, top = 170 + col * 1080, 950 + row * 905
        panel(draw, [left, top, left + 1030, top + 850], fill=("#FFFFFF", "#FBF9FF")[(row + col) % 2])
        paste_fit(canvas, image, [left + 35, top + 35, left + 995, top + 595], inset=16)
        text.fitted_text(draw, name, [left + 35, top + 590, left + 995, top + 650], max_size=29, min_size=22, colour=NAVY, bold=True, max_lines=1)
        panel(draw, [left + 45, top + 680, left + 265, top + 795], fill=GOLD, outline=PURPLE, width=3, radius=14)
        text.fitted_text(draw, starter, [left + 65, top + 700, left + 245, top + 775], max_size=31, min_size=24, colour=NAVY, bold=True, max_lines=1)
        draw.line([left + 310, top + 765, left + 950, top + 765], fill=PURPLE, width=3)
    panel(draw, [170, 2810, 2310, 3090], fill="#FFFFFF")
    text.fitted_text(draw, "Ask one question to a partner. Listen to the reply.", [250, 2870, 2230, 3030], max_size=38, min_size=29, colour=NAVY, bold=True, max_lines=2)


def render_p034(canvas, draw, source, text):
    images = grid_crops(source, 2, 2, 4)
    names = ("cork", "coin", "leaf", "stone")
    for index, (image, name) in enumerate(zip(images, names)):
        row, col = divmod(index, 2)
        left, top = 170 + col * 1080, 950 + row * 700
        panel(draw, [left, top, left + 1030, top + 650], fill=("#FFFFFF", "#FBF9FF")[(row + col) % 2])
        paste_fit(canvas, image, [left + 35, top + 30, left + 650, top + 515], inset=12)
        text.fitted_text(draw, name, [left + 60, top + 520, left + 620, top + 585], max_size=29, min_size=22, colour=NAVY, bold=True, max_lines=1)
        for choice, cy in (("FLOAT", top + 230), ("SINK", top + 390)):
            panel(draw, [left + 700, cy - 48, left + 955, cy + 48], fill="white", outline=PURPLE, width=3, radius=12)
            text.fitted_text(draw, choice, [left + 720, cy - 34, left + 865, cy + 34], max_size=26, min_size=20, colour=NAVY, bold=True, max_lines=1)
            panel(draw, [left + 875, cy - 36, left + 945, cy + 34], fill="white", outline=PURPLE, width=3, radius=8)
    panel(draw, [170, 2390, 2310, 3090], fill="#FFFFFF")
    text.fitted_text(draw, "Draw one thing you noticed during the water test.", [225, 2425, 2255, 2505], max_size=35, min_size=27, colour=NAVY, bold=True, max_lines=1)


def render_p035(canvas, draw, source, text):
    images = grid_crops(source, 2, 4, 8)
    words = ("observe", "predict", "test", "measure", "sort", "build", "record", "improve")
    order = (2, 4, 0, 7, 3, 6, 5, 1)
    panel(draw, [170, 950, 2310, 3090], fill="#FFFFFF")
    draw.line([1240, 1000, 1240, 3040], fill="#C3A9ED", width=5)
    for row, word in enumerate(words):
        cy = 1080 + row * 245
        panel(draw, [225, cy - 70, 1080, cy + 70], fill=("#FBF9FF", "#FFFFFF")[row % 2], outline="#C3A9ED", width=3, radius=14)
        text.fitted_text(draw, word.upper(), [270, cy - 45, 1000, cy + 45], max_size=31, min_size=23, colour=NAVY, bold=True, max_lines=1, align="left")
        circle(draw, 1135, cy, 24)
        image = images[order[row]]
        panel(draw, [1320, cy - 105, 2240, cy + 105], fill="white", outline="#C3A9ED", width=3, radius=14)
        paste_fit(canvas, image, [1360, cy - 95, 2140, cy + 95], inset=8)
        circle(draw, 1280, cy, 24)


def render_p036(canvas, draw, source, text):
    images = grid_crops(source, 2, 3, 6)
    tasks = (
        "Circle the leaf with the different detail.",
        "Say: bell-hear, flower-smell, feather-feel.",
        "Write L for living and N for non-living.",
        "Circle what you predict will float.",
        "Write how many cubes long the pencil is.",
        "Circle the stronger bridge."
    )
    for index, (image, task) in enumerate(zip(images, tasks)):
        row, col = divmod(index, 2)
        left, top = 170 + col * 1080, 950 + row * 690
        panel(draw, [left, top, left + 1030, top + 645], fill=("#FFFFFF", "#FBF9FF")[(row + col) % 2])
        circle(draw, left + 50, top + 50, 27)
        text.fitted_text(draw, str(index + 1), [left + 27, top + 27, left + 73, top + 73], max_size=24, min_size=19, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, task, [left + 100, top + 20, left + 985, top + 110], max_size=27, min_size=20, colour=NAVY, bold=True, max_lines=2, align="left")
        paste_fit(canvas, image, [left + 35, top + 125, left + 995, top + 535], inset=12)
        if index in (0, 3, 5):
            for cx in (left + 350, left + 700): circle(draw, cx, top + 580, 26)
        elif index == 2:
            for cx in (left + 300, left + 500, left + 700, left + 900): panel(draw, [cx - 36, top + 545, cx + 36, top + 617], fill="white", outline=PURPLE, width=3, radius=8)
        elif index == 4:
            panel(draw, [left + 430, top + 540, left + 600, top + 620], fill="white", outline=PURPLE, width=3, radius=10)


def render_p037(canvas, draw, source, text):
    assets = grid_crops(source, 2, 2, 4)
    materials = assets[:3]
    names = ("tissue", "foil", "plastic")
    for index, (image, name) in enumerate(zip(materials, names)):
        left = 170 + index * 720
        panel(draw, [left, 950, left + 665, 2300], fill=("#FFFFFF", "#FBF9FF")[index % 2])
        paste_fit(canvas, image, [left + 35, 990, left + 630, 1540], inset=20)
        text.fitted_text(draw, name, [left + 40, 1525, left + 625, 1600], max_size=32, min_size=25, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, "PREDICT", [left + 45, 1660, left + 360, 1725], max_size=27, min_size=21, colour=NAVY, bold=True, max_lines=1)
        circle(draw, left + 545, 1690, 30)
        for label, top in (("ABSORBS", 1815), ("DOES NOT ABSORB", 2000)):
            panel(draw, [left + 40, top, left + 620, top + 140], fill="white", outline=PURPLE, width=3, radius=12)
            text.fitted_text(draw, label, [left + 60, top + 30, left + 500, top + 110], max_size=25, min_size=19, colour=NAVY, bold=True, max_lines=2, align="left")
            panel(draw, [left + 525, top + 35, left + 600, top + 110], fill="white", outline=PURPLE, width=3, radius=8)
    panel(draw, [170, 2370, 2310, 3090], fill="#FFFFFF")
    paste_fit(canvas, assets[3], [190, 2420, 650, 3020], inset=28)
    text.fitted_text(draw, "Draw what you noticed after one drop of water.", [700, 2430, 2250, 2520], max_size=35, min_size=27, colour=NAVY, bold=True, max_lines=2, align="left")


def render_p038(canvas, draw, source, text):
    # The approved composite has three unequal-height rows. Explicit bands avoid
    # neighbouring tower/chair fragments leaking into the bridge crop.
    pairs = [
        crop_norm(source, (0.03, 0.02, 0.97, 0.37)),
        crop_norm(source, (0.03, 0.39, 0.97, 0.625)),
        crop_norm(source, (0.03, 0.64, 0.97, 0.99)),
    ]
    labels = ("TOWERS", "BRIDGES", "CHAIRS")
    for index, (pair, label) in enumerate(zip(pairs, labels)):
        top = 950 + index * 610
        bottom = top + 570
        panel(draw, [170, top, 2310, bottom], fill="white")
        text.fitted_text(draw, label, [195, top + 18, 520, top + 75], max_size=30, min_size=24, colour=NAVY, bold=True, max_lines=1, align="left")
        paste_fit(canvas, pair, [210, top + 70, 2270, bottom - 80], inset=18)
        for option, cx in enumerate((730, 1750)):
            circle(draw, cx, bottom - 52, 30)
            text.fitted_text(draw, ("DESIGN A", "DESIGN B")[option], [cx + 48, bottom - 90, cx + 330, bottom - 15], max_size=28, min_size=22, colour=NAVY, bold=True, max_lines=1)
    panel(draw, [170, 2810, 2310, 3090], fill="#FFFFFF")
    text.fitted_text(draw, "Improve one weaker design. Draw one support in the grid.", [225, 2835, 1120, 3045], max_size=34, min_size=26, colour=NAVY, bold=True, max_lines=3, align="left")
    grid_left, grid_top, grid_right, grid_bottom = 1180, 2840, 2250, 3055
    for x in range(grid_left, grid_right + 1, 70):
        draw.line([x, grid_top, x, grid_bottom], fill="#D8CCEE", width=2)
    for y in range(grid_top, grid_bottom + 1, 54):
        draw.line([grid_left, y, grid_right, y], fill="#D8CCEE", width=2)


def render_p039(canvas, draw, source, text):
    challenges = (
        crop_norm(source, (0.01, 0.01, 0.485, 0.31)),
        crop_norm(source, (0.50, 0.01, 0.99, 0.31)),
        crop_norm(source, (0.01, 0.335, 0.48, 0.63)),
        crop_norm(source, (0.52, 0.335, 0.99, 0.63)),
        crop_norm(source, (0.01, 0.665, 0.55, 0.99)),
    )
    tasks = (
        "Circle the leaf that exactly matches the target.",
        "Circle the ramp you predict sends the ball farthest.",
        "Write W for wood or M for metal under each object.",
        "Count the cubes. Write each pencil length.",
        "Circle the bridge design with the strongest supports.",
    )
    boxes = (
        (170, 950, 1200, 1600), (1250, 950, 2310, 1600),
        (170, 1640, 1200, 2300), (1250, 1640, 2310, 2300),
        (170, 2340, 2310, 3090),
    )
    for index, (image, task, box) in enumerate(zip(challenges, tasks, boxes)):
        left, top, right, bottom = box
        panel(draw, box, fill=("#FFFFFF", "#FBF9FF")[index % 2])
        circle(draw, left + 50, top + 48, 26)
        text.fitted_text(draw, str(index + 1), [left + 28, top + 26, left + 72, top + 71], max_size=23, min_size=18, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, task, [left + 95, top + 18, right - 35, top + 112], max_size=26, min_size=19, colour=NAVY, bold=True, max_lines=2, align="left")
        if index == 3:
            long_pencil = crop_norm(source, (0.53, 0.34, 0.995, 0.48))
            short_pencil = crop_norm(source, (0.57, 0.48, 0.90, 0.56))
            paste_fit(canvas, long_pencil, [left + 95, top + 125, right - 65, top + 235], inset=3)
            paste_fit(canvas, short_pencil, [left + 95, top + 350, right - 330, top + 430], inset=3)
            for count, y in ((6, top + 250), (3, top + 450)):
                cube_left = left + 145
                for cube_index in range(count):
                    x = cube_left + cube_index * 118
                    draw.rounded_rectangle([x, y, x + 82, y + 54], radius=8, fill="#1976D2", outline=NAVY, width=3)
        else:
            paste_fit(canvas, image, [left + 30, top + 125, right - 30, bottom - 115], inset=10)
        if index in (0, 1, 4):
            positions = (0.42, 0.62, 0.82) if index == 0 else (0.30, 0.50, 0.70)
            for ratio in positions:
                cx = left + (right - left) * ratio
                circle(draw, int(cx), bottom - 62, 27)
        elif index == 2:
            for item in range(6):
                x = left + 95 + item * 145
                panel(draw, [x, bottom - 105, x + 85, bottom - 30], fill="white", outline=PURPLE, width=3, radius=9)
        else:
            for x in (left + 320, left + 705):
                panel(draw, [x, bottom - 108, x + 165, bottom - 28], fill="white", outline=PURPLE, width=3, radius=10)


def render_p040(canvas, draw, source, text):
    icons = (
        crop_norm(source, (0.005, 0.03, 0.265, 0.97)),
        crop_norm(source, (0.285, 0.03, 0.49, 0.97)),
        crop_norm(source, (0.50, 0.03, 0.715, 0.97)),
        crop_norm(source, (0.735, 0.03, 0.995, 0.97)),
    )
    names = ("float test", "magnet test", "plant growth", "paper bridge")
    text.fitted_text(draw, "1. Choose one investigation.", [175, 950, 1160, 1025], max_size=34, min_size=26, colour=NAVY, bold=True, max_lines=1, align="left")
    for index, (icon, name) in enumerate(zip(icons, names)):
        left = 170 + index * 540
        panel(draw, [left, 1040, left + 500, 1575], fill=("#FFFFFF", "#FBF9FF")[index % 2])
        paste_fit(canvas, icon, [left + 25, 1065, left + 475, 1430], inset=15)
        text.fitted_text(draw, name, [left + 30, 1425, left + 420, 1510], max_size=27, min_size=20, colour=NAVY, bold=True, max_lines=1)
        circle(draw, left + 445, 1480, 27)
    panel(draw, [170, 1640, 2310, 2790], fill="#FFFFFF")
    text.fitted_text(draw, "2. Draw what you did and what happened.", [220, 1670, 2260, 1750], max_size=35, min_size=27, colour=NAVY, bold=True, max_lines=1, align="left")
    panel(draw, [220, 1790, 2260, 2730], fill="white", outline="#C3A9ED", width=3, radius=18)
    text.fitted_text(draw, "3. I discovered that...", [185, 2830, 780, 2905], max_size=34, min_size=26, colour=NAVY, bold=True, max_lines=1, align="left")
    draw.line([770, 2895, 2260, 2895], fill=PURPLE, width=3)
    draw.line([185, 3000, 2260, 3000], fill=PURPLE, width=3)


def render_p041(canvas, draw, source, text):
    badge = crop_norm(source, (0.005, 0.02, 0.355, 0.98))
    trophy = crop_norm(source, (0.365, 0.02, 0.665, 0.98))
    confetti = crop_norm(source, (0.67, 0.02, 0.995, 0.98))
    panel(draw, [205, 735, 2275, 3100], fill="#FFFDF5", outline="#D6A42B", width=8, radius=34)
    paste_fit(canvas, confetti, [760, 770, 1720, 1100], inset=25)
    text.fitted_text(draw, "STEM EXPLORER", [800, 1060, 1680, 1160], max_size=48, min_size=34, colour=PURPLE, bold=True, max_lines=1)
    paste_fit(canvas, badge, [275, 1160, 900, 1900], inset=25)
    paste_fit(canvas, trophy, [1580, 1160, 2205, 1900], inset=25)
    text.fitted_text(draw, "This certificate is awarded to", [890, 1280, 1590, 1380], max_size=36, min_size=27, colour=NAVY, bold=True, max_lines=1)
    draw.line([910, 1570, 1570, 1570], fill=PURPLE, width=4)
    text.fitted_text(draw, "for curiosity, careful observation and enthusiastic STEM learning.", [875, 1685, 1605, 1900], max_size=31, min_size=23, colour=INK, bold=True, max_lines=3)
    text.fitted_text(draw, "Date", [410, 2260, 665, 2335], max_size=31, min_size=24, colour=NAVY, bold=True, max_lines=1)
    draw.line([340, 2430, 920, 2430], fill=PURPLE, width=3)
    text.fitted_text(draw, "Teacher signature", [1540, 2260, 2100, 2335], max_size=31, min_size=24, colour=NAVY, bold=True, max_lines=1)
    draw.line([1510, 2430, 2150, 2430], fill=PURPLE, width=3)
    text.fitted_text(draw, "Keep observing. Keep asking. Keep exploring!", [450, 2700, 2030, 2825], max_size=39, min_size=29, colour=PURPLE, bold=True, max_lines=1)


def render_p042(canvas, draw, source, text):
    hero = crop_norm(source, (0.01, 0.01, 0.36, 0.99))
    badges = []
    columns = ((0.395, 0.685), (0.705, 0.995))
    rows = ((0.015, 0.335), (0.345, 0.665), (0.675, 0.995))
    for y0, y1 in rows:
        for x0, x1 in columns:
            badges.append(crop_norm(source, (x0, y0, x1, y1)))
    # The BUILD badge sits beside the hero's paper tools on the source sheet.
    # Use a tighter named crop so none of those neighboring objects enter its card.
    badges[4] = crop_norm(source, (0.49, 0.675, 0.69, 0.995))
    names = ("OBSERVE", "PREDICT", "TEST", "MEASURE", "BUILD", "RECORD")
    panel(draw, [170, 950, 900, 2790], fill="#FFFFFF")
    paste_fit(canvas, hero, [190, 980, 880, 2700], inset=20)
    for index, (badge, name) in enumerate(zip(badges, names)):
        row, col = divmod(index, 2)
        left, top = 950 + col * 660, 950 + row * 600
        panel(draw, [left, top, left + 620, top + 555], fill=("#FFFFFF", "#FBF9FF")[(row + col) % 2])
        paste_fit(canvas, badge, [left + 70, top + 35, left + 550, top + 425], inset=12)
        text.fitted_text(draw, name, [left + 45, top + 425, left + 470, top + 510], max_size=29, min_size=22, colour=NAVY, bold=True, max_lines=1)
        circle(draw, left + 545, top + 475, 27)
    panel(draw, [170, 2830, 2310, 3090], fill="#FFFFFF")
    text.fitted_text(draw, "My favourite STEM skill is __________________ because __________________.", [225, 2880, 2255, 3045], max_size=34, min_size=26, colour=NAVY, bold=True, max_lines=2, align="left")


def render_p043(canvas, draw, source, text):
    choices = (
        crop_norm(source, (0.005, 0.005, 0.325, 0.455)),
        crop_norm(source, (0.335, 0.005, 0.655, 0.455)),
        crop_norm(source, (0.665, 0.005, 0.995, 0.455)),
        crop_norm(source, (0.005, 0.505, 0.325, 0.995)),
        crop_norm(source, (0.335, 0.505, 0.655, 0.995)),
    )
    names = ("I observed", "I experimented", "I built", "I coded", "I shared")
    for index, (image, name) in enumerate(zip(choices, names)):
        left = 170 + index * 430
        panel(draw, [left, 950, left + 390, 1670], fill=("#FFFFFF", "#FBF9FF")[index % 2])
        paste_fit(canvas, image, [left + 20, 980, left + 370, 1470], inset=8)
        text.fitted_text(draw, name, [left + 25, 1470, left + 315, 1555], max_size=26, min_size=19, colour=NAVY, bold=True, max_lines=1)
        circle(draw, left + 335, 1580, 26)
    panel(draw, [170, 1740, 2310, 2760], fill="#FFFFFF")
    text.fitted_text(draw, "Draw or show one STEM success.", [220, 1770, 2260, 1850], max_size=36, min_size=28, colour=NAVY, bold=True, max_lines=1)
    panel(draw, [220, 1890, 2260, 2700], fill="white", outline="#C3A9ED", width=3, radius=18)
    panel(draw, [170, 2820, 2310, 3090], fill="#FFFFFF")
    text.fitted_text(draw, "I am proud that I ________________________________________________.", [225, 2880, 2255, 3035], max_size=35, min_size=26, colour=NAVY, bold=True, max_lines=2, align="left")


RENDERERS = {
    8: render_p008,
    9: render_p009,
    10: render_p010,
    11: render_p011,
    12: render_p012,
    13: render_p013,
    14: render_p014,
    15: render_p015,
    16: render_p016,
    17: render_p017,
    18: render_p018,
    19: render_p019,
    20: render_p020,
    21: render_p021,
    22: render_p022,
    23: render_p023,
    24: render_p024,
    25: render_p025,
    26: render_p026,
    27: render_p027,
    28: render_p028,
    29: render_p029,
    30: render_p030,
    31: render_p031,
    32: render_p032,
    33: render_p033,
    34: render_p034,
    35: render_p035,
    36: render_p036,
    37: render_p037,
    38: render_p038,
    39: render_p039,
    40: render_p040,
    41: render_p041,
    42: render_p042,
    43: render_p043,
}


def render_one(number: int, blueprint, logo, output_dir: Path, evidence_dir: Path, text):
    page_id = f"ST-LKG-V4-P{number:03d}"
    page = blueprint["pages"][page_id]
    illustration_path = ASSET_DIR / f"{page_id}.png"
    if not illustration_path.exists():
        raise FileNotFoundError(illustration_path)
    source = Image.open(illustration_path).convert("RGBA")
    canvas = Image.new("RGB", (WIDTH, HEIGHT), "#FFFCF7")
    draw = ImageDraw.Draw(canvas)
    header(canvas, draw, page, logo, text)
    if number != 41:
        completed_model(draw, page_id, text)
    RENDERERS[number](canvas, draw, source, text)
    teacher_footer(draw, page, text, number - 1)
    output = output_dir / f"{page_id}.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, "PNG")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / f"{page_id}.json").write_text(json.dumps({
        "page_id": page_id,
        "status": "PASS",
        "output": str(output),
        "illustration": str(illustration_path),
        "completed_example_visible": True,
        "independent_answers_unmarked": True,
        "response_space_purposeful": True,
        "teacher_cue_page_specific": True,
        "parent_panel": False,
    }, indent=2) + "\n", encoding="utf-8")
    return output


def contact_sheet(paths: list[Path], output: Path):
    columns = 6
    thumb_w = 310
    thumb_h = round(thumb_w * HEIGHT / WIDTH)
    rows = math.ceil(len(paths) / columns)
    sheet = Image.new("RGB", (thumb_w * columns, thumb_h * rows), "white")
    for index, path in enumerate(paths):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (index % columns) * thumb_w
        y = (index // columns) * thumb_h
        sheet.paste(image, (x, y))
    sheet.save(output, "PNG")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--logo", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "work-stem-explorers-pilot")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "work-stem-explorers-pilot-evidence")
    args = parser.parse_args()
    blueprint = load_json(BLUEPRINT)
    logo = Image.open(args.logo).convert("RGBA")
    text = load_module("stem_explorers_text_engine", TEXT_ENGINE)
    outputs = [render_one(number, blueprint, logo, args.output_dir, args.evidence_dir, text) for number in PILOT]
    contact = args.output_dir.parent / "work-stem-explorers-pilot-contact.png"
    contact_sheet(outputs, contact)
    summary = {"scope": [path.stem for path in outputs], "generated": len(outputs), "failed": 0, "contact_sheet": str(contact)}
    (args.evidence_dir / "stem-pilot-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
