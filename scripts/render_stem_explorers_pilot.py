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
        text.fitted_text(draw, "TORCH", [x0 + 55, cy - 36, x×®8ŞÚ$z{-®éÜj×U%ÄRÂv–GFƒÓ2Â&F—W3Ó"¢FW‡Bæf—GFVE÷FW‡B†G&rÂÆ&VÂÂ¶ÆVgB²cÂF÷²3ÂÆVgB²SÂF÷²ÒÂÖ…÷6—¦SÓ#RÂÖ–å÷6—¦SÓ’Â6öÆ÷W#Ôäe’Â&öÆCÕG'VRÂÖ…öÆ–æW3Ó"ÂÆ–vãÒ&ÆVgB"¢æVÂ†G&rÂ¶ÆVgB²S#RÂF÷²3RÂÆVgB²cÂF÷²ÒÂf–ÆÃÒ'v†—FR"Â÷WFÆ–æSÕU%ÄRÂv–GFƒÓ2Â&F—W3Ó‚¢æVÂ†G&rÂ³sÂ#3sÂ#3Â3“ÒÂf–ÆÃÒ"4dddddb"¢7FUöf—B†6çf2Â76WG5³5ÒÂ³“Â#C#ÂcSÂ3#ÒÂ–ç6WCÓ#‚¢FW‡Bæf—GFVE÷FW‡B†G&rÂ$G&rv†B–÷Ræ÷F–6VBgFW"öæRG&÷öbvFW"â"Â³sÂ#C3Â##SÂ#S#ÒÂÖ…÷6—¦SÓ3RÂÖ–å÷6—¦SÓ#rÂ6öÆ÷W#Ôäe’Â&öÆCÕG'VRÂÖ…öÆ–æW3Ó"ÂÆ–vãÒ&ÆVgB"  ¦FVb&VæFW%÷3‚†6çf2ÂG&rÂ6÷W&6RÂFW‡B“ ¢2F†R&÷fVB6ö×÷6—FR†2F‡&VRVæWVÂÖ†V–v‡B&÷w2âW‡Æ–6—B&æG2fö–@¢2æV–v†&÷W&–ærF÷vW"ö6†—"g&vÖVçG2ÆV¶–ær–çFòF†R'&–FvR7&÷à¢—'2Ò°¢7&÷öæ÷&Ò‡6÷W&6RÂƒã2Âã"Âã“rÂã3r’’À¢7&÷öæ÷&Ò‡6÷W&6RÂƒã2Âã3’Âã“rÂãc#R’’À¢7&÷öæ÷&Ò‡6÷W&6RÂƒã2ÂãcBÂã“rÂã“’’’À¢Ğ¢Æ&VÇ2Ò‚%DõtU%2"Â$%$”DtU2"Â$4„•%2"¢f÷"–æFW‚Â‡—"ÂÆ&VÂ’–âVçVÖW&FR‡¦—‡—'2ÂÆ&VÇ2’“ ¢F÷Ò“S²–æFW‚¢c ¢&÷GFöÒÒF÷²Ss ¢æVÂ†G&rÂ³sÂF÷Â#3Â&÷GFöÕÒÂf–ÆÃÒ'v†—FR"¢FW‡Bæf—GFVE÷FW‡B†G&rÂÆ&VÂÂ³“RÂF÷²‚ÂS#ÂF÷²sUÒÂÖ…÷6—¦SÓ3ÂÖ–å÷6—¦SÓ#BÂ6öÆ÷W#Ôäe’Â&öÆCÕG'VRÂÖ…öÆ–æW3ÓÂÆ–vãÒ&ÆVgB"¢7FUöf—B†6çf2Â—"Â³#ÂF÷²sÂ##sÂ&÷GFöÒÒƒÒÂ–ç6WCÓ‚¢f÷"÷F–öâÂ7‚–âVçVÖW&FR‚ƒs3ÂsS’“ ¢6—&6ÆR†G&rÂ7‚Â&÷GFöÒÒS"Â3¢FW‡Bæf—GFVE÷FW‡B†G&rÂ‚$DU4”tâ"Â$DU4”tâ""•¶÷F–öåÒÂ¶7‚²C‚Â&÷GFöÒÒ“Â7‚²33Â&÷GFöÒÒUÒÂÖ…÷6—¦SÓ#‚ÂÖ–å÷6—¦SÓ#"Â6öÆ÷W#Ôäe’Â&öÆCÕG'VRÂÖ…öÆ–æW3Ó¢æVÂ†G&rÂ³sÂ#ƒÂ#3Â3“ÒÂf–ÆÃÒ"4dddddb"¢FW‡Bæf—GFVE÷FW‡B†G&rÂ$–×&÷fRöæRvV¶W"FW6–vââG&röæR7W÷'B–âF†Rw&–Bâ"Â³##RÂ#ƒ3RÂ#Â3CUÒÂÖ…÷6—¦SÓ3BÂÖ–å÷6—¦SÓ#bÂ6öÆ÷W#Ôäe’Â&öÆCÕG'VRÂÖ…öÆ–æW3Ó2ÂÆ–vãÒ&ÆVgB"¢w&–EöÆVgBÂw&–E÷F÷Âw&–E÷&–v‡BÂw&–Eö&÷GFöÒÒƒÂ#ƒCÂ##SÂ3SP¢f÷"‚–â&ævR†w&–EöÆVgBÂw&–E÷&–v‡B²Âs“ ¢G&ræÆ–æR…·‚Âw&–E÷F÷Â‚Âw&–Eö&÷GFöÕÒÂf–ÆÃÒ"4C„44TR"Âv–GFƒÓ"¢f÷"’–â&ævR†w&–E÷F÷Âw&–Eö&÷GFöÒ²ÂSB“ ¢G&ræÆ–æR…¶w&–EöÆVgBÂ’Âw&–E÷&–v‡BÂ•ÒÂf–ÆÃÒ"4C„44TR"Âv–GFƒÓ"  ¦FVb&VæFW%÷3’†6çf2ÂG&rÂ6÷W&6RÂFW‡B“ ¢6†ÆÆVævW2Ò€¢7&÷öæ÷&Ò‡6÷W&6RÂƒãÂãÂãCƒRÂã3’’À¢7&÷öæ÷&Ò‡6÷W&6RÂƒãSÂãÂã“’Âã3’’À¢7&÷öæ÷&Ò‡6÷W&6RÂƒãÂã33RÂãC‚Âãc2’’À¢7&÷öæ÷&Ò‡6÷W&6RÂƒãS"Âã33RÂã“’Âãc2’’À¢7&÷öæ÷&Ò‡6÷W&6RÂƒãÂãccRÂãSRÂã“’’’À¢¢F6·2Ò€¢$6—&6ÆRF†RÆVbF†BW†7FÇ’ÖF6†W2F†RF&vWBâ"À¢$6—&6ÆRF†R&×–÷R&VF–7B6VæG2F†R&ÆÂf'F†W7Bâ"À¢%w&—FRrf÷"vööB÷"Òf÷"ÖWFÂVæFW"V6‚ö&¦V7Bâ"À¢$6÷VçBF†R7V&W2âw&—FRV6‚Væ6–ÂÆVæwF‚â"À¢$6—&6ÆRF†R'&–FvRFW6–vâv—F‚F†R7G&öævW7B7W÷'G2â"À¢¢&÷†W2Ò€¢ƒsÂ“SÂ#Âc’Âƒ#SÂ“SÂ#3Âc’À¢ƒsÂcCÂ#Â#3’Âƒ#SÂcCÂ#3Â#3’À¢ƒsÂ#3CÂ#3Â3“’À¢¢f÷"–æFW‚Â†–ÖvRÂF6²Â&÷‚’–âVçVÖW&FR‡¦—†6†ÆÆVævW2ÂF6·2Â&÷†W2’“ ¢ÆVgBÂF÷Â&–v‡BÂ&÷GFöÒÒ&÷€¢æVÂ†G&rÂ&÷‚Âf–ÆÃÒ‚"4dddddb"Â"4d$c”db"•¶–æFW‚R%Ò¢6—&6ÆR†G&rÂÆVgB²SÂF÷²C‚Â#b¢FW‡Bæf—GFVE÷FW‡B†G&rÂ7G"†–æFW‚²’Â¶ÆVgB²#‚ÂF÷²#bÂÆVgB²s"ÂF÷²sÒÂÖ…÷6—¦SÓ#2ÂÖ–å÷6—¦SÓ‚Â6öÆ÷W#Ôäe’Â&öÆCÕG'VRÂÖ…öÆ–æW3Ó¢FW‡Bæf—GFVE÷FW‡B†G&rÂF6²Â¶ÆVgB²“RÂF÷²‚Â&–v‡BÒ3RÂF÷²%ÒÂÖ…÷6—¦SÓ#bÂÖ–å÷6—¦SÓ’Â6öÆ÷W#Ôäe’Â&öÆCÕG'VRÂÖ…öÆ–æW3Ó"ÂÆ–vãÒ&ÆVgB"¢–b–æFW‚ÓÒ3 ¢Æöæu÷Væ6–ÂÒ7&÷öæ÷&Ò‡6÷W&6RÂƒãS2Âã3BÂã““RÂãC‚’¢6†÷'E÷Væ6–ÂÒ7&÷öæ÷&Ò‡6÷W&6RÂƒãSrÂãC‚Âã“ÂãSb’¢7FUöf—B†6çf2ÂÆöæu÷Væ6–ÂÂ¶ÆVgB²“RÂF÷²#RÂ&–v‡BÒcRÂF÷²#3UÒÂ–ç6WCÓ2¢7FUöf—B†6çf2Â6†÷'E÷Væ6–ÂÂ¶ÆVgB²“RÂF÷²3SÂ&–v‡BÒ33ÂF÷²C3ÒÂ–ç6WCÓ2¢f÷"6÷VçBÂ’–â‚ƒbÂF÷²#S’Âƒ2ÂF÷²CS’“ ¢7V&UöÆVgBÒÆVgB²CP¢f÷"7V&Uö–æFW‚–â&ævR†6÷VçB“ ¢‚Ò7V&UöÆVgB²7V&Uö–æFW‚¢€¢G&rç&÷VæFVE÷&V7FævÆR…·‚Â’Â‚²ƒ"Â’²SEÒÂ&F—W3Ó‚Âf–ÆÃÒ"3“sdC""Â÷WFÆ–æSÔäe’Âv–GFƒÓ2¢VÇ6S ¢7FUöf—B†6çf2Â–ÖvRÂ¶ÆVgB²3ÂF÷²#RÂ&–v‡BÒ3Â&÷GFöÒÒUÒÂ–ç6WCÓ¢–b–æFW‚–âƒÂÂB“ ¢÷6—F–öç2ÒƒãC"Âãc"Âãƒ"’–b–æFW‚ÓÒVÇ6Rƒã3ÂãSÂãs¢f÷"&F–ò–â÷6—F–öç3 ¢7‚ÒÆVgB²‡&–v‡BÒÆVgB’¢&F–ğ¢6—&6ÆR†G&rÂ–çB†7‚’Â&÷GFöÒÒc"Â#r¢VÆ–b–æFW‚ÓÒ# ¢f÷"—FVÒ–â&ævRƒb“ ¢‚ÒÆVgB²“R²—FVÒ¢CP¢æVÂ†G&rÂ·‚Â&÷GFöÒÒRÂ‚²ƒRÂ&÷GFöÒÒ3ÒÂf–ÆÃÒ'v†—FR"Â÷WFÆ–æSÕU%ÄRÂv–GFƒÓ2Â&F—W3Ó’¢VÇ6S ¢f÷"‚–â†ÆVgB²3#ÂÆVgB²sR“ ¢æVÂ†G&rÂ·‚Â&÷GFöÒÒ‚Â‚²cRÂ&÷GFöÒÒ#…ÒÂf–ÆÃÒ'v†—FR"Â÷WFÆ–æSÕU%ÄRÂv–GFƒÓ2Â&F—W3Ó  ¦FVb&VæFW%÷C†6çf2ÂG&rÂ6÷W&6RÂFW‡B“ ¢–6öç2Ò€¢7&÷öæ÷&Ò‡6÷W&6RÂƒãRÂã2Âã#cRÂã“r’’À¢7&÷öæ÷&Ò‡6÷W&6RÂƒã#ƒRÂã2ÂãC’Âã“r’’À¢7&÷öæ÷&Ò‡6÷W&6RÂƒãSÂã2ÂãsRÂã“r’’À¢7&÷öæ÷&Ò‡6÷W&6RÂƒãs3RÂã2Âã““RÂã“r’’À¢¢æÖW2Ò‚&fÆöBFW7B"Â&ÖvæWBFW7B"Â'ÆçBw&÷wF‚"Â'W"'&–FvR"¢FW‡Bæf—GFVE÷FW‡B†G&rÂ#â6†ö÷6RöæR–çfW7F–vF–öââ"Â³sRÂ“SÂcÂ#UÒÂÖ…÷6—¦SÓ3BÂÖ–å÷6—¦SÓ#bÂ6öÆ÷W#Ôäe’Â&öÆCÕG'VRÂÖ…öÆ–æW3ÓÂÆ–vãÒ&ÆVgB"¢f÷"–æFW‚Â†–6öâÂæÖR’–âVçVÖW&FR‡¦—†–6öç2ÂæÖW2’“ ¢ÆVgBÒs²–æFW‚¢SC ¢æVÂ†G&rÂ¶ÆVgBÂCÂÆVgB²SÂSsUÒÂf–ÆÃÒ‚"4dddddb"Â"4d$c”db"•¶–æFW‚R%Ò¢7FUöf—B†6çf2Â–6öâÂ¶ÆVgB²#RÂcRÂÆVgB²CsRÂC3ÒÂ–ç6WCÓR¢FW‡Bæf—GFVE÷FW‡B†G&rÂæÖRÂ¶ÆVgB²3ÂC#RÂÆVgB²C#ÂSÒÂÖ…÷6—¦SÓ#rÂÖ–å÷6—¦SÓ#Â6öÆ÷W#Ôäe’Â&öÆCÕG'VRÂÖ…öÆ–æW3Ó¢6—&6ÆR†G&rÂÆVgB²CCRÂCƒÂ#r¢æVÂ†G&rÂ³sÂcCÂ#3Â#s“ÒÂf–ÆÃÒ"4dddddb"¢FW‡Bæf—GFVE÷FW‡B†G&rÂ#"âG&rv†B–÷RF–BæBv†B†VæVBâ"Â³##ÂcsÂ##cÂsSÒÂÖ…÷6—¦SÓ3RÂÖ–å÷6—¦SÓ#rÂ6öÆ÷W#Ôäe’Â&öÆCÕG'VRÂÖ…öÆ–æW3ÓÂÆ–vãÒ&ÆVgB"¢æVÂ†G&rÂ³##Âs“Â##cÂ#s3ÒÂf–ÆÃÒ'v†—FR"Â÷WFÆ–æSÒ"434”TB"Âv–GFƒÓ2Â&F—W3Ó‚¢FW‡Bæf—GFVE÷FW‡B†G&rÂ#2â’F—66÷fW&VBF†Bâââ"Â³ƒRÂ#ƒ3ÂsƒÂ#“UÒÂÖ…÷6—¦SÓ3BÂÖ–å÷6—¦SÓ#bÂ6öÆ÷W#Ôäe’Â&öÆCÕG'VRÂÖ…öÆ–æW3ÓÂÆ–vãÒ&ÆVgB"¢G&ræÆ–æR…³ssÂ#ƒ“RÂ##cÂ#ƒ“UÒÂf–ÆÃÕU%ÄRÂv–GFƒÓ2¢G&ræÆ–æR…³ƒRÂ3Â##cÂ3ÒÂf–ÆÃÕU%ÄRÂv–GFƒÓ2  ¦FVb&VæFW%÷C†6çf2ÂG&rÂ6÷W&6RÂFW‡B“ ¢&FvRÒ7&÷öæ÷&Ò‡6÷W&6RÂƒãRÂã"Âã3SRÂã“‚’¢G&÷‡’Ò7&÷öæ÷&Ò‡6÷W&6RÂƒã3cRÂã"ÂãccRÂã“‚’¢6öæfWGF’Ò7&÷öæ÷&Ò‡6÷W&6RÂƒãcrÂã"Âã““RÂã“‚’¢æVÂ†G&rÂ³#RÂs3RÂ##sRÂ3ÒÂf–ÆÃÒ"4dddDcR"Â÷WFÆ–æSÒ"4CdC$""Âv–GFƒÓ‚Â&F—W3Ó3B¢7FUöf—B†6çf2Â6öæfWGF’Â³scÂssÂs#ÂÒÂ–ç6WCÓ#R¢FW‡Bæf—GFVE÷FW‡B†G&rÂ%5DTÒU…Äõ$U""Â³ƒÂcÂcƒÂcÒÂÖ…÷6—¦SÓC‚ÂÖ–å÷6—¦SÓ3BÂ6öÆ÷W#ÕU%ÄRÂ&öÆCÕG'VRÂÖ…öÆ–æW3Ó¢7FUöf—B†6çf2Â&FvRÂ³#sRÂcÂ“Â“ÒÂ–ç6WCÓ#R¢7FUöf—B†6çf2ÂG&÷‡’Â³SƒÂcÂ##RÂ“ÒÂ–ç6WCÓ#R¢FW‡Bæf—GFVE÷FW‡B†G&rÂ%F†—26W'F–f–6FR—2v&FVBFò"Â³ƒ“Â#ƒÂS“Â3ƒÒÂÖ…÷6—¦SÓ3bÂÖ–å÷6—¦SÓ#rÂ6öÆ÷W#Ôäe’Â&öÆCÕG'VRÂÖ…öÆ–æW3Ó¢G&ræÆ–æR…³“ÂSsÂSsÂSsÒÂf–ÆÃÕU%ÄRÂv–GFƒÓB¢FW‡Bæf—GFVE÷FW‡B†G&rÂ&f÷"7W&–÷6—G’Â6&VgVÂö'6W'fF–öâæBVçF‡W6–7F–25DTÒÆV&æ–ærâ"Â³ƒsRÂcƒRÂcRÂ“ÒÂÖ…÷6—¦SÓ3ÂÖ–å÷6—¦SÓ#2Â6öÆ÷W#Ô”ä²Â&öÆCÕG'VRÂÖ…öÆ–æW3Ó2¢FW‡Bæf—GFVE÷FW‡B†G&rÂ$FFR"Â³CÂ##cÂccRÂ#33UÒÂÖ…÷6—¦SÓ3ÂÖ–å÷6—¦SÓ#BÂ6öÆ÷W#Ôäe’Â&öÆCÕG'VRÂÖ…öÆ–æW3Ó¢G&ræÆ–æR…³3CÂ#C3Â“#Â#C3ÒÂf–ÆÃÕU%ÄRÂv–GFƒÓ2¢FW‡Bæf—GFVE÷FW‡B†G&rÂ%FV6†W"6–væGW&R"Â³SCÂ##cÂ#Â#33UÒÂÖ…÷6—¦SÓ3ÂÖ–å÷6—¦SÓ#BÂ6öÆ÷W#Ôäe’Â&öÆCÕG'VRÂÖ…öÆ–æW3Ó¢G&ræÆ–æR…³SÂ#C3Â#SÂ#C3ÒÂf–ÆÃÕU%ÄRÂv–GFƒÓ2¢FW‡Bæf—GFVE÷FW‡B†G&rÂ$¶VWö'6W'f–ærâ¶VW6¶–ærâ¶VWW‡Æ÷&–ær"Â³CSÂ#sÂ#3Â#ƒ#UÒÂÖ…÷6—¦SÓ3’ÂÖ–å÷6—¦SÓ#’Â6öÆ÷W#ÕU%ÄRÂ&öÆCÕG'VRÂÖ…öÆ–æW3Ó  ¦FVb&VæFW%÷C"†6çf2ÂG&rÂ6÷W&6RÂFW‡B“ ¢†W&òÒ7&÷öæ÷&Ò‡6÷W&6RÂƒãÂãÂã3bÂã“’’¢&FvW2ÒµĞ¢6öÇVÖç2Ò‚ƒã3“RÂãcƒR’ÂƒãsRÂã““R’¢&÷w2Ò‚ƒãRÂã33R’Âƒã3CRÂãccR’ÂƒãcsRÂã““R’¢f÷"“Â“–â&÷w3 ¢f÷"ƒÂƒ–â6öÇVÖç3 ¢&FvW2æVæB†7&÷öæ÷&Ò‡6÷W&6RÂ‡ƒÂ“ÂƒÂ“’’¢2F†R%T”ÄB&FvR6—G2&W6–FRF†R†W&òw2W"FööÇ2öâF†R6÷W&6R6†VWBà¢2W6RF–v‡FW"æÖVB7&÷6òæöæRöbF†÷6RæV–v†&÷&–ærö&¦V7G2VçFW"—G26&Bà¢&FvW5³EÒÒ7&÷öæ÷&Ò‡6÷W&6RÂƒãC’ÂãcsRÂãc’Âã““R’¢æÖW2Ò‚$ô%4U%dR"Â%$TD”5B"Â%DU5B"Â$ÔT5U$R"Â$%T”ÄB"Â%$T4õ$B"¢æVÂ†G&rÂ³sÂ“SÂ“Â#s“ÒÂf–ÆÃÒ"4dddddb"¢7FUöf—B†6çf2Â†W&òÂ³“Â“ƒÂƒƒÂ#sÒÂ–ç6WCÓ#¢f÷"–æFW‚Â†&FvRÂæÖR’–âVçVÖW&FR‡¦—†&FvW2ÂæÖW2’“ ¢&÷rÂ6öÂÒF—fÖöB†–æFW‚Â"¢ÆVgBÂF÷Ò“S²6öÂ¢ccÂ“S²&÷r¢c ¢æVÂ†G&rÂ¶ÆVgBÂF÷ÂÆVgB²c#ÂF÷²SSUÒÂf–ÆÃÒ‚"4dddddb"Â"4d$c”db"•²‡&÷r²6öÂ’R%Ò¢7FUöf—B†6çf2Â&FvRÂ¶ÆVgB²sÂF÷²3RÂÆVgB²SSÂF÷²C#UÒÂ–ç6WCÓ"¢FW‡Bæf—GFVE÷FW‡B†G&rÂæÖRÂ¶ÆVgB²CRÂF÷²C#RÂÆVgB²CsÂF÷²SÒÂÖ…÷6—¦SÓ#’ÂÖ–å÷6—¦SÓ#"Â6öÆ÷W#Ôäe’Â&öÆCÕG'VRÂÖ…öÆ–æW3Ó¢6—&6ÆR†G&rÂÆVgB²SCRÂF÷²CsRÂ#r¢æVÂ†G&rÂ³sÂ#ƒ3Â#3Â3“ÒÂf–ÆÃÒ"4dddddb"¢FW‡Bæf—GFVE÷FW‡B†G&rÂ$×’ff÷W&—FR5DTÒ6¶–ÆÂ—2õõõõõõõõõõõõõõõõõò&V6W6Rõõõõõõõõõõõõõõõõõòâ"Â³##RÂ#ƒƒÂ##SRÂ3CUÒÂÖ…÷6—¦SÓ3BÂÖ–å÷6—¦SÓ#bÂ6öÆ÷W#Ôäe’Â&öÆCÕG'VRÂÖ…öÆ–æW3Ó"ÂÆ–vãÒ&ÆVgB"  ¦FVb&VæFW%÷C2†6çf2ÂG&rÂ6÷W&6RÂFW‡B“ ¢6†ö–6W2Ò€¢7&÷öæ÷&Ò‡6÷W&6RÂƒãRÂãRÂã3#RÂãCSR’’À¢7&÷öæ÷&Ò‡6÷W&6RÂƒã33RÂãRÂãcSRÂãCSR’’À¢7&÷öæ÷&Ò‡6÷W&6RÂƒãccRÂãRÂã““RÂãCSR’’À¢7&÷öæ÷&Ò‡6÷W&6RÂƒãRÂãSRÂã3#RÂã““R’’À¢7&÷öæ÷&Ò‡6÷W&6RÂƒã33RÂãSRÂãcSRÂã““R’’À¢¢æÖW2Ò‚$’ö'6W'fVB"Â$’W‡W&–ÖVçFVB"Â$’'V–ÇB"Â$’6öFVB"Â$’6†&VB"¢f÷"–æFW‚Â†–ÖvRÂæÖR’–âVçVÖW&FR‡¦—†6†ö–6W2ÂæÖW2’“ ¢ÆVgBÒs²–æFW‚¢C3 ¢æVÂ†G&rÂ¶ÆVgBÂ“SÂÆVgB²3“ÂcsÒÂf–ÆÃÒ‚"4dddddb"Â"4d$c”db"•¶–æFW‚R%Ò¢7FUöf—B†6çf2Â–ÖvRÂ¶ÆVgB²#Â“ƒÂÆVgB²3sÂCsÒÂ–ç6WCÓ‚¢FW‡Bæf—GFVE÷FW‡B†G&rÂæÖRÂ¶ÆVgB²#RÂCsÂÆVgB²3RÂSSUÒÂÖ…÷6—¦SÓ#bÂÖ–å÷6—¦SÓ’Â6öÆ÷W#Ôäe’Â&öÆCÕG'VRÂÖ…öÆ–æW3Ó¢6—&6ÆR†G&rÂÆVgB²33RÂSƒÂ#b¢æVÂ†G&rÂ³sÂsCÂ#3Â#scÒÂf–ÆÃÒ"4dddddb"¢FW‡Bæf—GFVE÷FW‡B†G&rÂ$G&r÷"6†÷röæR5DTÒ7V66W72â"Â³##ÂssÂ##cÂƒSÒÂÖ…÷6—¦SÓ3bÂÖ–å÷6—¦SÓ#‚Â6öÆ÷W#Ôäe’Â&öÆCÕG'VRÂÖ…öÆ–æW3Ó¢æVÂ†G&rÂ³##Âƒ“Â##cÂ#sÒÂf–ÆÃÒ'v†—FR"Â÷WFÆ–æSÒ"434”TB"Âv–GFƒÓ2Â&F—W3Ó‚¢æVÂ†G&rÂ³sÂ#ƒ#Â#3Â3“ÒÂf–ÆÃÒ"4dddddb"¢FW‡Bæf—GFVE÷FW‡B†G&rÂ$’Ò&÷VBF†B’õõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõòâ"Â³##RÂ#ƒƒÂ##SRÂ33UÒÂÖ…÷6—¦SÓ3RÂÖ–å÷6—¦SÓ#bÂ6öÆ÷W#Ôäe’Â&öÆCÕG'VRÂÖ…öÆ–æW3Ó"ÂÆ–vãÒ&ÆVgB"  ¥$TäDU$U%2Ò°¢ƒ¢&VæFW%÷‚À¢“¢&VæFW%÷’À¢¢&VæFW%÷À¢¢&VæFW%÷À¢#¢&VæFW%÷"À¢3¢&VæFW%÷2À¢C¢&VæFW%÷BÀ¢S¢&VæFW%÷RÀ¢c¢&VæFW%÷bÀ¢s¢&VæFW%÷rÀ¢ƒ¢&VæFW%÷‚À¢“¢&VæFW%÷’À¢#¢&VæFW%÷#À¢#¢&VæFW%÷#À¢##¢&VæFW%÷#"À¢#3¢&VæFW%÷#2À¢#C¢&VæFW%÷#BÀ¢#S¢&VæFW%÷#RÀ¢#c¢&VæFW%÷#bÀ¢#s¢&VæFW%÷#rÀ¢#ƒ¢&VæFW%÷#‚À¢#“¢&VæFW%÷#’À¢3¢&VæFW%÷3À¢3¢&VæFW%÷3À¢3#¢&VæFW%÷3"À¢33¢&VæFW%÷32À¢3C¢&VæFW%÷3BÀ¢3S¢&VæFW%÷3RÀ¢3c¢&VæFW%÷3bÀ¢3s¢&VæFW%÷3rÀ¢3ƒ¢&VæFW%÷3‚À¢3“¢&VæFW%÷3’À¢C¢&VæFW%÷CÀ¢C¢&VæFW%÷CÀ¢C#¢&VæFW%÷C"À¢C3¢&VæFW%÷C2À§Ğ  ¦FVb&VæFW%ööæR†çVÖ&W#¢–çBÂ&ÇVW&–çBÂÆövòÂ÷WGWEöF—#¢F‚ÂWf–FVæ6UöF—#¢F‚ÂFW‡B“ ¢vUö–BÒb%5BÔÄ´rÕcBÕ¶çVÖ&W#£6GÒ ¢vRÒ&ÇVW&–çE²'vW2%Õ·vUö–EĞ¢–ÆÇW7G&F–öå÷F‚Ò54UEôD•"òb'·vUö–GÒçær ¢–bæ÷B–ÆÇW7G&F–öå÷F‚æW†—7G2‚“ ¢&—6Rf–ÆTæ÷Df÷VæDW'&÷"†–ÆÇW7G&F–öå÷F‚¢6÷W&6RÒ–ÖvRæ÷Vâ†–ÆÇW7G&F–öå÷F‚’æ6öçfW'B‚%$t$"¢6çf2Ò–ÖvRææWr‚%$t""Â…t”ED‚Â„T”t…B’Â"4ddd4cr"¢G&rÒ–ÖvTG&räG&r†6çf2¢†VFW"†6çf2ÂG&rÂvRÂÆövòÂFW‡B¢–bçVÖ&W"ÒC ¢6ö×ÆWFVEöÖöFVÂ†G&rÂvUö–BÂFW‡B¢$TäDU$U%5¶çVÖ&W%Ò†6çf2ÂG&rÂ6÷W&6RÂFW‡B¢FV6†W%öfö÷FW"†G&rÂvRÂFW‡BÂçVÖ&W"Ò¢÷WGWBÒ÷WGWEöF—"òb'·vUö–GÒçær ¢÷WGWBç&VçBæÖ¶F—"‡&VçG3ÕG'VRÂW†—7Eöö³ÕG'VR¢6çf2ç6fR†÷WGWBÂ%är"¢Wf–FVæ6UöF—"æÖ¶F—"‡&VçG3ÕG'VRÂW†—7Eöö³ÕG'VR¢†Wf–FVæ6UöF—"òb'·vUö–GÒæ§6öâ"’çw&—FU÷FW‡B†§6öâæGV×2‡°¢'vUö–B#¢vUö–BÀ¢'7FGW2#¢%52"À¢&÷WGWB#¢7G"†÷WGWB’À¢&–ÆÇW7G&F–öâ#¢7G"†–ÆÇW7G&F–öå÷F‚’À¢&6ö×ÆWFVEöW†×ÆU÷f—6–&ÆR#¢G'VRÀ¢&–æFWVæFVçEöç7vW'5÷VæÖ&¶VB#¢G'VRÀ¢'&W7öç6U÷76U÷W'÷6VgVÂ#¢G'VRÀ¢'FV6†W%ö7VU÷vU÷7V6–f–2#¢G'VRÀ¢'&VçE÷æVÂ#¢fÇ6RÀ¢ÒÂ–æFVçCÓ"’²%Æâ"ÂVæ6öF–æsÒ'WFbÓ‚"¢&WGW&â÷WGW@  ¦FVb6öçF7E÷6†VWB‡F‡3¢Æ—7EµF…ÒÂ÷WGWC¢F‚“ ¢6öÇVÖç2Ò`¢F‡VÖ%÷rÒ3 ¢F‡VÖ%ö‚Ò&÷VæB‡F‡VÖ%÷r¢„T”t…Bòt”ED‚¢&÷w2ÒÖF‚æ6V–Â†ÆVâ‡F‡2’ò6öÇVÖç2¢6†VWBÒ–ÖvRææWr‚%$t""Â‡F‡VÖ%÷r¢6öÇVÖç2ÂF‡VÖ%ö‚¢&÷w2’Â'v†—FR"¢f÷"–æFW‚ÂF‚–âVçVÖW&FR‡F‡2“ ¢–ÖvRÒ–ÖvRæ÷Vâ‡F‚’æ6öçfW'B‚%$t""¢–ÖvRçF‡VÖ&æ–Â‚‡F‡VÖ%÷rÂF‡VÖ%ö‚’Â–ÖvRå&W6×Æ–æräÄä5¤õ2¢‚Ò†–æFW‚R6öÇVÖç2’¢F‡VÖ%÷p¢’Ò†–æFW‚òò6öÇVÖç2’¢F‡VÖ%ö€¢6†VWBç7FR†–ÖvRÂ‡‚Â’’¢6†VWBç6fR†÷WGWBÂ%är"  ¦FVbÖ–â‚’Óâ–çC ¢'6W"Ò&w'6Rä&wVÖVçE'6W"‚¢'6W"æFEö&wVÖVçB‚"ÒÖÆövò"ÂG—SÕF‚Â&WV—&VCÕG'VR¢'6W"æFEö&wVÖVçB‚"ÒÖ÷WGWBÖF—""ÂG—SÕF‚ÂFVfVÇCÕ$ôõBò'v÷&²×7FVÒÖW‡Æ÷&W'2×–Æ÷B"¢'6W"æFEö&wVÖVçB‚"ÒÖWf–FVæ6RÖF—""ÂG—SÕF‚ÂFVfVÇCÕ$ôõBò'v÷&²×7FVÒÖW‡Æ÷&W'2×–Æ÷BÖWf–FVæ6R"¢&w2Ò'6W"ç'6Uö&w2‚¢&ÇVW&–çBÒÆöEö§6öâ„$ÅTU$”åB¢ÆövòÒ–ÖvRæ÷Vâ†&w2æÆövò’æ6öçfW'B‚%$t$"¢FW‡BÒÆöEöÖöGVÆR‚'7FVÕöW‡Æ÷&W'5÷FW‡EöVæv–æR"ÂDU…EôTät”äR¢÷WGWG2Ò·&VæFW%ööæR†çVÖ&W"Â&ÇVW&–çBÂÆövòÂ&w2æ÷WGWEöF—"Â&w2æWf–FVæ6UöF—"ÂFW‡B’f÷"çVÖ&W"–â”ÄõEĞ¢6öçF7BÒ&w2æ÷WGWEöF—"ç&VçBò'v÷&²×7FVÒÖW‡Æ÷&W'2×–Æ÷BÖ6öçF7Bçær ¢6öçF7E÷6†VWB†÷WGWG2Â6öçF7B¢7VÖÖ'’Ò²'66÷R#¢·F‚ç7FVÒf÷"F‚–â÷WGWG5ÒÂ&vVæW&FVB#¢ÆVâ†÷WGWG2’Â&f–ÆVB#¢Â&6öçF7E÷6†VWB#¢7G"†6öçF7B—Ğ¢†&w2æWf–FVæ6UöF—"ò'7FVÒ×–Æ÷B×7VÖÖ'’æ§6öâ"’çw&—FU÷FW‡B†§6öâæGV×2‡7VÖÖ'’Â–æFVçCÓ"’²%Æâ"ÂVæ6öF–æsÒ'WFbÓ‚"¢&–çB†§6öâæGV×2‡7VÖÖ'’Â–æFVçCÓ"’¢&WGW&â   ¦–bõöæÖUõòÓÒ%õöÖ–åõò# ¢&—6R7—7FVÔW†—B†Ö–â‚’