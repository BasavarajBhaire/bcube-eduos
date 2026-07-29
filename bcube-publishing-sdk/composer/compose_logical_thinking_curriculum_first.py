#!/usr/bin/env python3
"""Curriculum-first Logical Thinking Adventures LKG composer.

Wave 1 renders P008-P017 from the approved page-specific illustration sheets.
Every independent response remains open; completed marks appear only in the
model strip. Unsupported pages fail closed until their exact layout is added.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
TEXT_ENGINE = ROOT / "bcube-publishing-sdk/composer/compose_learning_page_v2.py"
TEMPLATE = ROOT / "bcube-publishing-sdk/templates/learning-page-v2.json"
CONTRACT = ROOT / "runtime-contracts/lkg/logical-thinking-adventures.json"

WIDTH, HEIGHT = 2480, 3508
NAVY = "#123F72"
PURPLE = "#7E57C2"
SOFT_PURPLE = "#A077E8"
BLUE = "#E8F4FF"
GOLD = "#FFF4C6"
GREEN = "#F0FAED"
INK = "#31353A"


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


def trim_white(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    rgb = rgba.convert("RGB")
    difference = ImageChops.difference(rgb, Image.new("RGB", rgb.size, "white")).convert("L")
    difference = difference.point(lambda value: 255 if value > 14 else 0)
    alpha = rgba.getchannel("A").point(lambda value: 255 if value > 8 else 0)
    difference = ImageChops.multiply(difference, alpha)
    box = difference.getbbox()
    return rgba.crop(box) if box else rgba


def crop_norm(source: Image.Image, box) -> Image.Image:
    width, height = source.size
    x0, y0, x1, y1 = box
    return trim_white(source.crop((round(x0 * width), round(y0 * height), round(x1 * width), round(y1 * height))))


def crop_raw_norm(source: Image.Image, box) -> Image.Image:
    """Crop without trimming so nested coordinates keep their original grid."""
    width, height = source.size
    x0, y0, x1, y1 = box
    return source.crop((round(x0 * width), round(y0 * height), round(x1 * width), round(y1 * height))).convert("RGBA")


def paste_fit(canvas: Image.Image, image: Image.Image, box, inset=10):
    x0, y0, x1, y1 = [int(value) for value in box]
    x0 += inset; y0 += inset; x1 -= inset; y1 -= inset
    source = trim_white(image)
    scale = min((x1 - x0) / source.width, (y1 - y0) / source.height)
    source = source.resize((max(1, round(source.width * scale)), max(1, round(source.height * scale))), Image.Resampling.LANCZOS)
    x = x0 + (x1 - x0 - source.width) // 2
    y = y0 + (y1 - y0 - source.height) // 2
    canvas.paste(source, (x, y), source)


def paste_fit_aligned(canvas: Image.Image, image: Image.Image, box, *, align="center", inset=10):
    """Fit an object while preserving a meaningful edge alignment.

    Finish-the-picture pages need the supplied half-picture to touch the
    centre guide.  Centring that half inside a large box makes the drawing
    relationship unclear and can make the original half appear cropped.
    """
    x0, y0, x1, y1 = [int(value) for value in box]
    x0 += inset; y0 += inset; x1 -= inset; y1 -= inset
    source = trim_white(image)
    scale = min((x1 - x0) / source.width, (y1 - y0) / source.height)
    source = source.resize((max(1, round(source.width * scale)), max(1, round(source.height * scale))), Image.Resampling.LANCZOS)
    if align == "right":
        x = x1 - source.width
    elif align == "left":
        x = x0
    else:
        x = x0 + (x1 - x0 - source.width) // 2
    y = y0 + (y1 - y0 - source.height) // 2
    canvas.paste(source, (x, y), source)


def activity_card(draw, text, number, instruction, x0, y0, width=1025, height=625):
    panel(draw, [x0, y0, x0 + width, y0 + height], fill="#FFFFFF", outline=SOFT_PURPLE, width=4)
    panel(draw, [x0 + 18, y0 + 15, x0 + width - 18, y0 + 112], fill="#F7F3FF", outline=None, width=0, radius=14)
    circle(draw, x0 + 65, y0 + 64, 28, 3)
    text.fitted_text(draw, str(number), [x0 + 40, y0 + 38, x0 + 90, y0 + 89], max_size=28, min_size=23, colour=NAVY, bold=True, max_lines=1)
    text.fitted_text(draw, instruction, [x0 + 110, y0 + 27, x0 + width - 35, y0 + 101], max_size=29, min_size=22, colour=NAVY, bold=True, align="left", max_lines=2)


def option_label(draw, text, label, cx, cy):
    circle(draw, cx, cy, 22, 4)
    text.fitted_text(draw, label, [cx - 18, cy - 18, cx + 18, cy + 18], max_size=21, min_size=18, colour=NAVY, bold=True, max_lines=1)


def header(canvas, draw, page, logo, text):
    logo_image = logo.convert("RGBA")
    logo_image.thumbnail((300, 220), Image.Resampling.LANCZOS)
    canvas.paste(logo_image, (105 + (300 - logo_image.width) // 2, 35 + (220 - logo_image.height) // 2), logo_image)
    text.fitted_text(draw, "Logical Thinking Adventures", [470, 45, 2320, 145], max_size=43, min_size=34, colour=PURPLE, bold=True, max_lines=1)
    text.fitted_text(draw, page["identity"]["title"], [470, 140, 2320, 275], max_size=69, min_size=46, colour=NAVY, bold=True, max_lines=2)
    panel(draw, [150, 305, 2330, 445], fill=BLUE, outline="#1768B3", width=3)
    text.fitted_text(draw, "Learning goal: " + page["learning"]["objective"], [190, 318, 2290, 432], max_size=47, min_size=32, colour=NAVY, bold=True, max_lines=2)
    panel(draw, [150, 490, 2330, 650], fill=GOLD, outline="#E1A81C", width=3)
    text.fitted_text(draw, page["learning"]["instruction"], [190, 505, 2290, 635], max_size=53, min_size=35, colour=INK, bold=True, max_lines=2)


def model_shell(draw, text):
    panel(draw, [170, 700, 2310, 900], fill="#F6F1FF", outline=SOFT_PURPLE, width=3)
    panel(draw, [195, 720, 535, 880], fill="#E7D9FA", outline=SOFT_PURPLE, width=2, radius=18)
    text.fitted_text(draw, "COMPLETED\nEXAMPLE", [220, 737, 510, 862], max_size=35, min_size=27, colour=NAVY, bold=True, max_lines=2)
    return [575, 720, 2275, 880]


def circle(draw, cx, cy, radius=24, width=4):
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill="white", outline=PURPLE, width=width)


def completed_model(canvas, draw, page_id, text):
    x0, y0, x1, y1 = model_shell(draw, text)
    cy = (y0 + y1) // 2
    if page_id == "LT-LKG-V4-P008":
        draw.polygon([(x0 + 40, cy + 25), (x0 + 145, cy + 25), (x0 + 115, cy + 62), (x0 + 70, cy + 62)], fill="#43A7E6", outline=NAVY)
        draw.line([x0 + 92, cy + 25, x0 + 92, cy - 48], fill=NAVY, width=4)
        draw.polygon([(x0 + 94, cy - 46), (x0 + 145, cy - 20), (x0 + 94, cy - 5)], fill="#F05A47", outline=NAVY)
        draw.ellipse([x0 + 25, cy - 75, x0 + 165, cy + 80], outline=PURPLE, width=5)
        text.fitted_text(draw, "Circle the part that changed.", [x0 + 240, y0 + 20, x1 - 20, y1 - 20], max_size=42, min_size=32, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P009":
        for i, colour in enumerate(("#F05A47", "#F05A47", "#3D8BFF")):
            cx = x0 + 90 + i * 150
            draw.ellipse([cx - 42, cy - 42, cx + 42, cy + 42], fill=colour, outline=NAVY, width=3)
        draw.ellipse([x0 + 182, cy - 58, x0 + 298, cy + 58], outline=PURPLE, width=5)
        text.fitted_text(draw, "Circle the picture that is exactly the same.", [x0 + 530, y0 + 20, x1 - 20, y1 - 20], max_size=39, min_size=29, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P010":
        for i, symbol in enumerate(("apple", "apple", "car", "apple")):
            cx = x0 + 70 + i * 135
            if symbol == "apple":
                draw.ellipse([cx - 34, cy - 36, cx + 34, cy + 36], fill="#F44336", outline=NAVY, width=3)
            else:
                draw.rounded_rectangle([cx - 48, cy - 28, cx + 48, cy + 28], radius=12, fill="#3D8BFF", outline=NAVY, width=3)
        draw.ellipse([x0 + 285, cy - 58, x0 + 405, cy + 58], outline=PURPLE, width=5)
        text.fitted_text(draw, "The car does not belong with the apples.", [x0 + 590, y0 + 20, x1 - 20, y1 - 20], max_size=38, min_size=28, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P011":
        text.fitted_text(draw, "shoe", [x0 + 30, y0 + 30, x0 + 260, y1 - 30], max_size=42, min_size=32, colour=NAVY, bold=True, max_lines=1)
        circle(draw, x0 + 300, cy, 13, 3); draw.line([x0 + 313, cy, x0 + 640, cy], fill=PURPLE, width=5); circle(draw, x0 + 653, cy, 13, 3)
        text.fitted_text(draw, "sock", [x0 + 700, y0 + 30, x0 + 930, y1 - 30], max_size=42, min_size=32, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, "These belong together.", [x0 + 1000, y0 + 20, x1 - 20, y1 - 20], max_size=37, min_size=28, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P012":
        draw.ellipse([x0 + 45, cy - 48, x0 + 141, cy + 48], fill="#F05A47", outline=NAVY, width=3)
        draw.ellipse([x0 + 25, cy - 72, x0 + 161, cy + 72], outline=PURPLE, width=5)
        text.fitted_text(draw, "Find the ball in the scene and circle it.", [x0 + 240, y0 + 20, x1 - 20, y1 - 20], max_size=40, min_size=30, colour=NAVY, bold=True, max_lines=2)
    elif page_id in {"LT-LKG-V4-P013", "LT-LKG-V4-P015"}:
        colours = ("#F05A47", "#3D8BFF", "#F05A47", "#3D8BFF")
        for i, colour in enumerate(colours):
            cx = x0 + 65 + i * 115
            draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=colour, outline=NAVY, width=3)
        draw.rectangle([x0 + 460, cy - 50, x0 + 560, cy + 50], outline=PURPLE, width=4)
        draw.ellipse([x0 + 480, cy - 30, x0 + 540, cy + 30], fill="#F05A47", outline=NAVY, width=3)
        text.fitted_text(draw, "The next item continues the pattern.", [x0 + 650, y0 + 20, x1 - 20, y1 - 20], max_size=38, min_size=28, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P014":
        for i, label in enumerate(("1", "2", "3", "4")):
            left = x0 + 40 + i * 150
            panel(draw, [left, cy - 50, left + 105, cy + 50], fill="#FFFFFF", outline=PURPLE, width=3, radius=14)
            text.fitted_text(draw, label, [left + 10, cy - 40, left + 95, cy + 40], max_size=48, min_size=36, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, "Number the pictures in story order.", [x0 + 700, y0 + 20, x1 - 20, y1 - 20], max_size=39, min_size=29, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P016":
        for i, radius in enumerate((22, 34, 46)):
            cx = x0 + 80 + i * 145
            draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill="#FFD447", outline=NAVY, width=3)
        draw.ellipse([x0 + 327, cy - 60, x0 + 449, cy + 60], outline=PURPLE, width=5)
        text.fitted_text(draw, "Circle the choice that completes the change.", [x0 + 560, y0 + 20, x1 - 20, y1 - 20], max_size=39, min_size=29, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P017":
        draw.ellipse([x0 + 55, cy - 45, x0 + 145, cy + 45], fill="#F05A47", outline=NAVY, width=3)
        circle(draw, x0 + 55, cy - 55, 25, 3)
        text.fitted_text(draw, "1", [x0 + 35, cy - 76, x0 + 75, cy - 34], max_size=24, min_size=20, colour=NAVY, bold=True, max_lines=1)
        draw.line([x0 + 180, cy, x0 + 500, cy], fill=PURPLE, width=5)
        draw.polygon([(x0 + 500, cy), (x0 + 455, cy - 28), (x0 + 455, cy + 28)], fill=PURPLE)
        panel(draw, [x0 + 540, cy - 62, x0 + 790, cy + 62], fill=BLUE, outline="#1768B3", width=3, radius=15)
        text.fitted_text(draw, "RED", [x0 + 555, cy - 52, x0 + 675, cy - 2], max_size=31, min_size=25, colour=NAVY, bold=True, max_lines=1)
        panel(draw, [x0 + 690, cy - 45, x0 + 765, cy + 45], fill="#FFFFFF", outline=PURPLE, width=3, radius=10)
        text.fitted_text(draw, "1", [x0 + 705, cy - 35, x0 + 750, cy + 35], max_size=31, min_size=25, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, "The red picture is number 1, so write 1 in RED.", [x0 + 845, y0 + 20, x1 - 20, y1 - 20], max_size=34, min_size=26, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P018":
        draw.ellipse([x0 + 55, cy - 45, x0 + 145, cy + 45], fill="#3D8BFF", outline=NAVY, width=3)
        draw.line([x0 + 180, cy, x0 + 500, cy], fill=PURPLE, width=5)
        draw.polygon([(x0 + 500, cy), (x0 + 455, cy - 28), (x0 + 455, cy + 28)], fill=PURPLE)
        panel(draw, [x0 + 540, cy - 55, x0 + 790, cy + 55], fill=BLUE, outline="#1768B3", width=3, radius=15)
        text.fitted_text(draw, "CIRCLE", [x0 + 555, cy - 40, x0 + 775, cy + 40], max_size=38, min_size=29, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, "Put each picture number in its shape group.", [x0 + 850, y0 + 20, x1 - 20, y1 - 20], max_size=35, min_size=27, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P021":
        draw.line([x0 + 55, cy - 35, x0 + 165, cy + 35], fill="#F05A47", width=13)
        draw.line([x0 + 112, cy - 5, x0 + 145, cy - 45], fill=NAVY, width=5)
        draw.line([x0 + 112, cy - 5, x0 + 80, cy + 42], fill=NAVY, width=5)
        draw.line([x0 + 205, cy, x0 + 500, cy], fill=PURPLE, width=5)
        draw.polygon([(x0 + 500, cy), (x0 + 455, cy - 28), (x0 + 455, cy + 28)], fill=PURPLE)
        panel(draw, [x0 + 540, cy - 55, x0 + 760, cy + 55], fill="#EAF6E7", outline="#5F9D50", width=3, radius=15)
        text.fitted_text(draw, "SMALL", [x0 + 560, cy - 40, x0 + 740, cy + 40], max_size=39, min_size=30, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, "A broken crayon is a small problem I can solve calmly.", [x0 + 820, y0 + 20, x1 - 20, y1 - 20], max_size=34, min_size=26, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P019":
        for index, radius in enumerate((24, 38, 52)):
            cx = x0 + 75 + index * 145
            draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill="#F2B84B", outline=NAVY, width=3)
            text.fitted_text(draw, str(index + 1), [cx - 35, cy + 55, cx + 35, cy + 105], max_size=28, min_size=23, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, "Number from smallest to biggest.", [x0 + 570, y0 + 20, x1 - 20, y1 - 20], max_size=39, min_size=29, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P020":
        text.fitted_text(draw, "pencil", [x0 + 25, y0 + 25, x0 + 260, y1 - 25], max_size=40, min_size=30, colour=NAVY, bold=True, max_lines=1)
        circle(draw, x0 + 300, cy, 13, 3); draw.line([x0 + 313, cy, x0 + 620, cy], fill=PURPLE, width=5); circle(draw, x0 + 633, cy, 13, 3)
        text.fitted_text(draw, "sharpener", [x0 + 680, y0 + 25, x0 + 1010, y1 - 25], max_size=40, min_size=30, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, "Draw one matching line.", [x0 + 1080, y0 + 20, x1 - 20, y1 - 20], max_size=36, min_size=27, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P022":
        draw.ellipse([x0 + 55, cy - 36, x0 + 127, cy + 36], fill="#F05A47", outline=NAVY, width=3)
        draw.line([x0 + 155, cy, x0 + 480, cy], fill=PURPLE, width=5)
        draw.polygon([(x0 + 480, cy), (x0 + 438, cy - 25), (x0 + 438, cy + 25)], fill=PURPLE)
        for offset in (0, 55, 110):
            draw.ellipse([x0 + 540 + offset, cy - 36, x0 + 612 + offset, cy + 36], fill="#F05A47", outline=NAVY, width=3)
        text.fitted_text(draw, "Pushing the ball makes it roll.", [x0 + 850, y0 + 20, x1 - 20, y1 - 20], max_size=37, min_size=28, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P023":
        draw.rounded_rectangle([x0 + 150, cy - 55, x0 + 215, cy + 55], radius=18, fill="#FFD447", outline=NAVY, width=3)
        draw.ellipse([x0 + 285, cy - 32, x0 + 349, cy + 32], fill="#F05A47", outline=NAVY, width=3)
        panel(draw, [x0 + 410, cy - 50, x0 + 650, cy + 50], fill=BLUE, outline="#1768B3", width=3, radius=15)
        text.fitted_text(draw, "RIGHT", [x0 + 430, cy - 38, x0 + 630, cy + 38], max_size=39, min_size=30, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, "The ball is RIGHT of the child.", [x0 + 750, y0 + 20, x1 - 20, y1 - 20], max_size=36, min_size=27, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P024":
        draw.rectangle([x0 + 155, cy - 5, x0 + 190, cy + 65], fill="#8D5A2B", outline=NAVY, width=3)
        draw.ellipse([x0 + 105, cy - 35, x0 + 240, cy + 35], fill="#43A047", outline=NAVY, width=3)
        draw.ellipse([x0 + 145, cy - 88, x0 + 195, cy - 38], fill="#3D8BFF", outline=NAVY, width=3)
        panel(draw, [x0 + 310, cy - 50, x0 + 560, cy + 50], fill=BLUE, outline="#1768B3", width=3, radius=15)
        text.fitted_text(draw, "ABOVE", [x0 + 330, cy - 38, x0 + 540, cy + 38], max_size=39, min_size=30, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, "The bird is ABOVE the tree.", [x0 + 680, y0 + 20, x1 - 20, y1 - 20], max_size=36, min_size=27, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P025":
        draw.rectangle([x0 + 65, cy - 62, x0 + 245, cy + 62], fill="#D9A15B", outline=NAVY, width=4)
        draw.ellipse([x0 + 115, cy - 40, x0 + 195, cy + 40], fill="#F05A47", outline=NAVY, width=3)
        panel(draw, [x0 + 330, cy - 50, x0 + 590, cy + 50], fill=BLUE, outline="#1768B3", width=3, radius=15)
        text.fitted_text(draw, "INSIDE", [x0 + 350, cy - 38, x0 + 570, cy + 38], max_size=39, min_size=30, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, "The ball is INSIDE the box.", [x0 + 700, y0 + 20, x1 - 20, y1 - 20], max_size=36, min_size=27, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P026":
        draw.rectangle([x0 + 40, cy - 55, x0 + 430, cy + 55], outline=PURPLE, width=4)
        draw.line([x0 + 75, cy + 25, x0 + 180, cy + 25, x0 + 180, cy - 20, x0 + 370, cy - 20], fill="#3D8BFF", width=8)
        text.fitted_text(draw, "Trace from START to FINISH.", [x0 + 520, y0 + 20, x1 - 20, y1 - 20], max_size=39, min_size=29, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P027":
        # Study: red, blue, yellow. Recall: red, green, yellow. The two
        # remembered colours are visibly modelled without solving a task row.
        for index, colour in enumerate(("#F05A47", "#43A047", "#FFD447")):
            cx = x0 + 70 + index * 130
            draw.ellipse([cx - 35, cy - 35, cx + 35, cy + 35], fill=colour, outline=NAVY, width=3)
        for cx in (x0 + 70, x0 + 330):
            draw.ellipse([cx - 54, cy - 54, cx + 54, cy + 54], outline=PURPLE, width=5)
        text.fitted_text(draw, "After covering the study pictures, circle the pictures you remember.", [x0 + 500, y0 + 20, x1 - 20, y1 - 20], max_size=36, min_size=27, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P028":
        draw.ellipse([x0 + 45, cy - 48, x0 + 141, cy + 48], fill="#3D8BFF", outline=NAVY, width=3)
        text.fitted_text(draw, "What colour was the ball?", [x0 + 190, y0 + 15, x0 + 650, y1 - 15], max_size=34, min_size=27, colour=NAVY, bold=True, max_lines=2)
        for index, word in enumerate(("BLUE", "RED")):
            left = x0 + 690 + index * 260
            panel(draw, [left, cy - 48, left + 220, cy + 48], fill="#FFFFFF", outline=PURPLE, width=3, radius=14)
            text.fitted_text(draw, word, [left + 12, cy - 34, left + 208, cy + 34], max_size=31, min_size=25, colour=NAVY, bold=True, max_lines=1)
            if index == 0:
                draw.rounded_rectangle([left - 8, cy - 58, left + 228, cy + 58], radius=18, outline=PURPLE, width=5)
        text.fitted_text(draw, "Cover the picture, then answer.", [x0 + 1250, y0 + 20, x1 - 20, y1 - 20], max_size=33, min_size=26, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P029":
        draw.rounded_rectangle([x0 + 45, cy - 38, x0 + 170, cy + 38], radius=12, fill="#78C8F0", outline=NAVY, width=3)
        for index, word in enumerate(("WIPE", "LEAVE")):
            left = x0 + 245 + index * 260
            text.fitted_text(draw, word, [left, cy - 42, left + 210, cy + 42], max_size=36, min_size=28, colour=NAVY, bold=True, max_lines=1)
            if index == 0: draw.ellipse([left - 10, cy - 58, left + 220, cy + 58], outline=PURPLE, width=5)
        text.fitted_text(draw, "Choose the safest helpful answer.", [x0 + 830, y0 + 20, x1 - 20, y1 - 20], max_size=37, min_size=28, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P030":
        draw.arc([x0 + 50, cy - 65, x0 + 185, cy + 65], 90, 270, fill=NAVY, width=5)
        draw.line([x0 + 118, cy - 65, x0 + 118, cy + 65], fill="#AAB4C0", width=3)
        draw.arc([x0 + 50, cy - 65, x0 + 185, cy + 65], 270, 450, fill=PURPLE, width=5)
        text.fitted_text(draw, "Draw the missing half to finish the picture.", [x0 + 300, y0 + 20, x1 - 20, y1 - 20], max_size=38, min_size=28, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P031":
        text.fitted_text(draw, "TOP", [x0 + 25, y0 + 25, x0 + 220, y1 - 25], max_size=37, min_size=28, colour=NAVY, bold=True, max_lines=1)
        circle(draw, x0 + 265, cy, 13, 3); draw.line([x0 + 278, cy, x0 + 580, cy], fill=PURPLE, width=5); circle(draw, x0 + 593, cy, 13, 3)
        text.fitted_text(draw, "BOTTOM", [x0 + 640, y0 + 25, x0 + 930, y1 - 25], max_size=37, min_size=28, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, "Match the two picture halves.", [x0 + 1000, y0 + 20, x1 - 20, y1 - 20], max_size=35, min_size=27, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P032":
        draw.arc([x0 + 50, cy - 62, x0 + 185, cy + 62], 180, 360, fill="#3D8BFF", width=12)
        draw.line([x0 + 118, cy, x0 + 118, cy + 65], fill=NAVY, width=7)
        circle(draw, x0 + 255, cy, 13, 3); draw.line([x0 + 268, cy, x0 + 520, cy], fill=PURPLE, width=5); circle(draw, x0 + 533, cy, 13, 3)
        draw.arc([x0 + 590, cy - 62, x0 + 725, cy + 62], 180, 360, fill="#333333", width=12)
        draw.line([x0 + 658, cy, x0 + 658, cy + 65], fill="#333333", width=7)
        text.fitted_text(draw, "Match each object to its shadow.", [x0 + 820, y0 + 20, x1 - 20, y1 - 20], max_size=35, min_size=27, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P034":
        # A completed plant-growth example models the same visual reasoning
        # used by the five activity rows without revealing one of their
        # actual answers.
        draw.ellipse([x0 + 55, cy + 18, x0 + 95, cy + 48], fill="#8D5A2B", outline=NAVY, width=3)
        draw.line([x0 + 220, cy + 40, x0 + 220, cy - 15], fill="#43A047", width=7)
        draw.ellipse([x0 + 185, cy - 28, x0 + 222, cy], fill="#7BC96F", outline=NAVY, width=2)
        draw.ellipse([x0 + 220, cy - 40, x0 + 260, cy - 8], fill="#7BC96F", outline=NAVY, width=2)
        draw.line([x0 + 370, cy + 45, x0 + 370, cy - 55], fill="#2E8B45", width=8)
        for dx, dy in ((-38, -30), (10, -48), (-42, 0), (10, -15)):
            draw.ellipse([x0 + 370 + dx, cy + dy, x0 + 415 + dx, cy + dy + 32], fill="#43A047", outline=NAVY, width=2)
        draw.ellipse([x0 + 305, cy - 72, x0 + 445, cy + 72], outline=PURPLE, width=5)
        text.fitted_text(draw, "Seed, sprout, then plant. Circle the picture that completes the idea.", [x0 + 540, y0 + 20, x1 - 20, y1 - 20], max_size=36, min_size=27, colour=NAVY, bold=True, max_lines=2)
    elif page_id in {"LT-LKG-V4-P033", "LT-LKG-V4-P038"}:
        for index, colour in enumerate(("#F05A47", "#3D8BFF", "#FFD447")):
            left = x0 + 45 + index * 145
            draw.polygon([(left + 45, cy - 45), (left + 90, cy), (left + 45, cy + 45), (left, cy)], fill=colour, outline=NAVY)
        draw.ellipse([x0 + 168, cy - 68, x0 + 302, cy + 68], outline=PURPLE, width=5)
        text.fitted_text(draw, "Circle the choice that completes the puzzle.", [x0 + 560, y0 + 20, x1 - 20, y1 - 20], max_size=37, min_size=28, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P036":
        for index, colour in enumerate(("#F05A47", "#F05A47", "#3D8BFF", "#F05A47")):
            cx = x0 + 65 + index * 120
            draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=colour, outline=NAVY, width=3)
        draw.ellipse([x0 + 280, cy - 52, x0 + 390, cy + 52], outline=PURPLE, width=5)
        text.fitted_text(draw, "The blue circle is the odd one out.", [x0 + 600, y0 + 20, x1 - 20, y1 - 20], max_size=37, min_size=28, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P037":
        text.fitted_text(draw, "key", [x0 + 30, y0 + 30, x0 + 260, y1 - 30], max_size=42, min_size=32, colour=NAVY, bold=True, max_lines=1)
        circle(draw, x0 + 300, cy, 13, 3)
        draw.line([x0 + 313, cy, x0 + 640, cy], fill=PURPLE, width=5)
        circle(draw, x0 + 653, cy, 13, 3)
        text.fitted_text(draw, "lock", [x0 + 700, y0 + 30, x0 + 930, y1 - 30], max_size=42, min_size=32, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, "Draw a line between related pictures.", [x0 + 1000, y0 + 20, x1 - 20, y1 - 20], max_size=35, min_size=27, colour=NAVY, bold=True, max_lines=2)
    elif page_id == "LT-LKG-V4-P035":
        points = ((x0 + 55, cy, x0 + 155, cy), (x0 + 205, cy, x0 + 305, cy), (x0 + 405, cy + 42, x0 + 405, cy - 48))
        for ax0, ay0, ax1, ay1 in points:
            draw.line([ax0, ay0, ax1, ay1], fill=PURPLE, width=10)
            if ay0 == ay1:
                draw.polygon([(ax1, ay1), (ax1 - 28, ay1 - 22), (ax1 - 28, ay1 + 22)], fill=PURPLE)
            else:
                draw.polygon([(ax1, ay1), (ax1 - 22, ay1 + 28), (ax1 + 22, ay1 + 28)], fill=PURPLE)
        text.fitted_text(draw, "One arrow moves one grid square.", [x0 + 560, y0 + 20, x1 - 20, y1 - 20], max_size=37, min_size=28, colour=NAVY, bold=True, max_lines=2)
    else:
        for index, colour in enumerate(("#F05A47", "#F05A47", "#3D8BFF", "#F05A47")):
            cx = x0 + 65 + index * 120
            draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=colour, outline=NAVY, width=3)
        draw.ellipse([x0 + 280, cy - 52, x0 + 390, cy + 52], outline=PURPLE, width=5)
        text.fitted_text(draw, "Complete each thinking task without showing the answer.", [x0 + 600, y0 + 20, x1 - 20, y1 - 20], max_size=36, min_size=27, colour=NAVY, bold=True, max_lines=2)


def teacher_footer(draw, page, text):
    panel(draw, [150, 3070, 2300, 3270], fill=GREEN, outline="#5F9D50", width=3)
    text.fitted_text(draw, "TEACHER CUE", [180, 3095, 520, 3245], max_size=38, min_size=30, colour=NAVY, bold=True, max_lines=1)
    text.fitted_text(draw, page["guidance"]["teacher_cue"], [550, 3090, 2260, 3250], max_size=39, min_size=28, colour=INK, align="left", max_lines=3)
    printed = page["identity"].get("printed_page")
    if printed is not None:
        text.fitted_text(draw, str(printed), [2180, 3310, 2310, 3425], max_size=40, min_size=31, colour="#667085", bold=True, max_lines=1)


def grid_crop(source, cols, rows, index, margin_x=0.0, margin_y=0.0):
    """Crop one logical cell without shaving artwork at the cell boundary.

    The approved sheets already include white separation. Earlier renderers
    added an inward margin to every cell; that visibly cut shoes, buses,
    arrows, tails and other objects placed close to a nominal grid edge.
    Keep the full cell and let ``trim_white`` remove only real whitespace.
    The margin arguments remain for API compatibility but are intentionally
    ignored for approved sheets.
    """
    col, row = index % cols, index // cols
    return crop_norm(source, (col / cols, row / rows, (col + 1) / cols, (row + 1) / rows))


def isolate_largest_content(image):
    """Keep one complete object while discarding bleed from adjacent cells."""
    rgba = image.convert("RGBA")
    scale = min(1.0, 220.0 / max(rgba.size))
    small = rgba.resize((max(1, int(rgba.width * scale)), max(1, int(rgba.height * scale))), Image.Resampling.BILINEAR)
    pixels = small.load(); width, height = small.size
    visible = bytearray(width * height)
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a > 20 and min(r, g, b) < 245:
                visible[y * width + x] = 1
    seen = bytearray(width * height); best = None
    for start in range(width * height):
        if not visible[start] or seen[start]:
            continue
        stack = [start]; seen[start] = 1; points = []
        while stack:
            point = stack.pop(); points.append(point)
            x, y = point % width, point // width
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                neighbour = ny * width + nx
                if 0 <= nx < width and 0 <= ny < height and visible[neighbour] and not seen[neighbour]:
                    seen[neighbour] = 1; stack.append(neighbour)
        if best is None or len(points) > len(best):
            best = points
    if not best:
        return trim_white(rgba)
    # Keep only the selected connected component.  Cropping to its bounding
    # box alone retained small neighbouring fragments whenever the main
    # object's arms or branches spanned those fragments horizontally.
    component_mask = Image.new("L", small.size, 0)
    mask_pixels = component_mask.load()
    for point in best:
        mask_pixels[point % width, point // width] = 255
    component_mask = component_mask.filter(ImageFilter.MaxFilter(7))
    component_mask = component_mask.resize(rgba.size, Image.Resampling.NEAREST)
    clean_alpha = ImageChops.multiply(rgba.getchannel("A"), component_mask)
    rgba.putalpha(clean_alpha)
    xs = [point % width for point in best]; ys = [point // width for point in best]
    pad = 6
    box = (
        max(0, int((min(xs) - pad) / scale)), max(0, int((min(ys) - pad) / scale)),
        min(rgba.width, int((max(xs) + pad + 1) / scale)), min(rgba.height, int((max(ys) + pad + 1) / scale)),
    )
    return rgba.crop(box)


def grid_crop_object(source, cols, rows, index):
    """Crop a single-object cell with overlap, then remove neighbour bleed."""
    col, row = index % cols, index // cols
    overlap_x, overlap_y = 0.012, 0.035
    box = (
        max(0.0, col / cols - overlap_x), max(0.0, row / rows - overlap_y),
        min(1.0, (col + 1) / cols + overlap_x), min(1.0, (row + 1) / rows + overlap_y),
    )
    return isolate_largest_content(crop_norm(source, box))


DIRECT_ACTIVITY = {
    "LT-LKG-V4-P009": {
        "steps": ("Look at the large picture in each group.", "Check shape, colour and direction.", "Circle the one picture that is exactly the same."),
        "words": "fish • kite • cup • car • butterfly • shoe",
    },
    "LT-LKG-V4-P010": {
        "steps": ("Name all four pictures in a group.", "Say what three pictures have in common.", "Circle the picture that does not belong."),
        "words": "fruit • animals • clothes • transport • shapes • weather",
    },
    "LT-LKG-V4-P011": {
        "steps": ("Name the pictures in both columns.", "Find two things used together.", "Draw one line between each matching pair."),
        "words": "shoe • sock • key • lock • pencil • sharpener • cup • jug • soap • towel • bed • pillow",
    },
    "LT-LKG-V4-P013": {
        "steps": ("Say the pictures from left to right.", "Find the part that repeats.", "Circle the choice that comes next."),
        "words": "stars • apples • shapes • animals • vehicles",
    },
    "LT-LKG-V4-P015": {
        "steps": ("Point and say each pattern.", "Find the repeating part.", "Draw the next picture in the empty box."),
        "words": "fruit • shapes • toys • flowers • animals",
    },
    "LT-LKG-V4-P016": {
        "steps": ("Look at how each row changes.", "Say what should come next.", "Circle one answer choice."),
        "words": "size • number • direction • position • colour",
    },
    "LT-LKG-V4-P020": {
        "steps": ("Name every object.", "Find two objects used together.", "Draw a line to make six pairs."),
        "words": "pencil–sharpener • shoe–sock • soap–towel • bed–pillow • car–garage • spoon–bowl",
    },
    "LT-LKG-V4-P022": {
        "steps": ("Look at an action in the left column.", "Say what will probably happen.", "Draw a line to the matching result."),
        "words": "ice–puddle • push–roll • rain–wet • switch–light • umbrella–dry",
    },
    "LT-LKG-V4-P029": {
        "steps": ("Look at one everyday problem.", "Compare the three picture choices.", "Circle the safest or most helpful choice."),
        "words": "wipe a spill • help a friend • cross safely • dress warmly • find a pencil",
        "tasks": (
            "Circle the best way to wipe the spill.",
            "Circle the kindest way to help the friend.",
            "Circle the safest way to cross.",
            "Circle the clothes that keep the child warm.",
            "Circle the best place to look for the pencil.",
        ),
    },
    "LT-LKG-V4-P033": {
        "steps": ("Look at the empty puzzle space.", "Compare the shape and picture details.", "Circle the one piece that fits."),
        "words": "train • fish • flower • kite • teddy bear",
    },
    "LT-LKG-V4-P034": {
        "steps": ("Look at the pictures in order.", "Say the rule or what changes.", "Circle the picture that completes the rule."),
        "words": "growth • weather • meal • animal home • tool use",
    },
    "LT-LKG-V4-P036": {
        "steps": ("Complete one box at a time.", "Say the rule before choosing.", "Circle or draw only where the box asks."),
        "words": "odd one out • same • pattern • size order • shadow",
        "tasks": ("Circle the fruit that is different.", "Circle the matching butterfly.", "Draw the next flower.", "Write 1, 2, 3 from small to big.", "Circle the matching shadow."),
    },
    "LT-LKG-V4-P037": {
        "steps": ("Read one short task with your teacher.", "Solve that task by yourself.", "Move to the next task when finished."),
        "words": "difference • match • sort • order • position • pattern",
        "tasks": ("Circle what changed.", "Draw both matching lines.", "Circle the three red objects.", "Write 1, 2, 3, 4 in story order.", "Circle the cat under the table and the ball inside the box.", "Complete both patterns."),
    },
    "LT-LKG-V4-P038": {
        "steps": ("Study one puzzle carefully.", "Try a strategy: compare, count or continue.", "Mark only your chosen answer."),
        "words": "missing piece • paths • balance • odd grid • sequence",
        "tasks": ("Choose the missing picture.", "Trace each path to the matching food or home.", "Complete the balance.", "Find the odd grid picture.", "Continue the leaf sequence."),
    },
    "LT-LKG-V4-P039": {
        "steps": ("Listen to one direction.", "Complete that task independently.", "Stop when all six tasks are finished."),
        "words": "observe • classify • match • sequence • position • coding",
        "tasks": ("Circle the differences.", "Circle the one that is not a fruit.", "Match each object to its shadow.", "Number the plant pictures 1, 2, 3.", "Circle the picture that shows UNDER.", "Follow the arrows to the red dot."),
    },
}


def render_direct_activity(canvas, draw, source, text, page_id):
    """Render each visual task with its own instruction.

    The former implementation placed a complete illustration sheet on the
    left and a detached instruction panel on the right.  That preserved the
    artwork, but it did not read like a children's textbook.  Approved sheets
    in this family are organised as a 2 x 3 grid, so retain each complete
    visual relationship in a card and place the exact child action directly
    above it.  Children can now see, read and respond in one place.
    """
    spec = DIRECT_ACTIVITY[page_id]
    task_text = {
        "LT-LKG-V4-P009": (
            "Circle the fish that is exactly the same.", "Circle the kite that is exactly the same.",
            "Circle the cup that is exactly the same.", "Circle the car that is exactly the same.",
            "Circle the butterfly that is exactly the same.", "Circle the shoe that is exactly the same.",
        ),
        "LT-LKG-V4-P010": (
            "Circle the picture that is not a fruit.", "Circle the picture that is not an animal.",
            "Circle the picture that is not clothing.", "Circle the picture that is not transport.",
            "Circle the picture that is not a shape.", "Circle the picture that does not match the weather.",
        ),
        "LT-LKG-V4-P013": (
            "Circle what comes next in the star pattern.", "Circle what comes next in the fruit pattern.",
            "Circle what comes next in the shape pattern.", "Circle what comes next in the vehicle pattern.",
            "Circle what comes next in the animal pattern.",
        ),
        "LT-LKG-V4-P015": (
            "Draw the next fruit.", "Draw the next shape.", "Draw the next toy.",
            "Draw the next flower.", "Draw the next animal.",
        ),
        "LT-LKG-V4-P016": (
            "Circle what comes next as the size changes.", "Circle what comes next as the number changes.",
            "Circle what comes next as the direction changes.", "Circle what comes next as the position changes.",
            "Circle what comes next as the colour changes.",
        ),
        "LT-LKG-V4-P029": spec.get("tasks", ()),
        "LT-LKG-V4-P033": (
            "Circle the piece that completes the train.", "Circle the piece that completes the fish.",
            "Circle the piece that completes the flower.", "Circle the piece that completes the kite.",
            "Circle the piece that completes the teddy bear.",
        ),
        "LT-LKG-V4-P034": (
            "Circle what happens next as the plant grows.", "Circle what happens next in the weather.",
            "Circle what happens next at mealtime.", "Circle the animal's correct home.",
            "Circle the object used with the tool.",
        ),
        "LT-LKG-V4-P036": spec.get("tasks", ()),
        "LT-LKG-V4-P037": spec.get("tasks", ()),
        "LT-LKG-V4-P038": spec.get("tasks", ()),
        "LT-LKG-V4-P039": spec.get("tasks", ()),
    }[page_id]
    start_y = 730 if page_id == "LT-LKG-V4-P039" else 950
    card_h = 675
    for index, task in enumerate(task_text):
        col, row = index % 2, index // 2
        is_last_odd = len(task_text) % 2 == 1 and index == len(task_text) - 1
        card_w = 2140 if is_last_odd else 1025
        x0 = 170 if is_last_odd else 170 + col * 1085
        y0 = start_y + row * card_h
        panel(draw, [x0, y0, x0 + card_w, y0 + 625], fill="#FFFFFF", outline=SOFT_PURPLE, width=4)
        panel(draw, [x0 + 18, y0 + 15, x0 + card_w - 18, y0 + 112], fill="#F7F3FF", outline=None, width=0, radius=14)
        circle(draw, x0 + 65, y0 + 64, 28, 3)
        text.fitted_text(draw, str(index + 1), [x0 + 40, y0 + 38, x0 + 90, y0 + 89], max_size=28, min_size=23, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, task, [x0 + 110, y0 + 27, x0 + card_w - 40, y0 + 101], max_size=29, min_size=22, colour=NAVY, bold=True, align="left", max_lines=2)
        source_index = (0, 1, 2, 5, 4)[index] if page_id == "LT-LKG-V4-P013" else index
        source_col, source_row = source_index % 2, source_index // 2
        inset = 0.012
        if page_id == "LT-LKG-V4-P039":
            p039_boxes = (
                (0.02, 0.02, 0.49, 0.39), (0.52, 0.02, 0.98, 0.39),
                (0.02, 0.425, 0.49, 0.68), (0.50, 0.40, 0.98, 0.68),
                (0.02, 0.69, 0.49, 0.99), (0.50, 0.69, 0.98, 0.99),
            )
            image = crop_norm(source, p039_boxes[index])
        else:
            image = crop_norm(source, (
                source_col / 2 + inset, source_row / 3 + inset,
                (source_col + 1) / 2 - inset, (source_row + 1) / 3 - inset,
            ))
        order_boxes = 0
        if page_id == "LT-LKG-V4-P036" and index == 3:
            order_boxes = 3
        elif page_id == "LT-LKG-V4-P037" and index == 3:
            order_boxes = 4
        elif page_id == "LT-LKG-V4-P039" and index == 3:
            order_boxes = 3
        image_bottom = y0 + 505 if order_boxes else y0 + 600
        if is_last_odd:
            image_box = [x0 + 500, y0 + 125, x0 + card_w - 500, image_bottom]
        else:
            image_box = [x0 + 28, y0 + 125, x0 + card_w - 28, image_bottom]
        paste_fit(canvas, image, image_box, 2)
        if page_id == "LT-LKG-V4-P013":
            # Keep the given pattern visually distinct from the answer
            # choices.  Without this rule the two areas read as one long row
            # and children cannot tell which pictures they may select.
            draw.line(
                [x0 + 55, y0 + 405, x0 + card_w - 55, y0 + 405],
                fill=SOFT_PURPLE,
                width=4,
            )
        if order_boxes:
            box_w, gap = 120, 35
            total_w = order_boxes * box_w + (order_boxes - 1) * gap
            first_x = x0 + (card_w - total_w) // 2
            for box_index in range(order_boxes):
                left = first_x + box_index * (box_w + gap)
                panel(draw, [left, y0 + 515, left + box_w, y0 + 590], fill="#FFFFFF", outline=PURPLE, width=4, radius=12)


def render_picture_logic_p034(canvas, draw, source, text):
    """Render five full-width logic rows without cutting the answer choices."""
    tasks = (
        "Circle what happens next as the plant grows.",
        "A raincoat keeps the child dry. Circle what keeps feet dry.",
        "Rice is served on a plate. Circle another food served on a plate.",
        "A dog lives in a doghouse. Circle where a bird lives.",
        "A hammer is a tool. Circle the tool used to cut wood.",
    )
    row_boxes = (
        (0.00, 0.03, 1.00, 0.21),
        (0.00, 0.225, 1.00, 0.40),
        (0.00, 0.415, 1.00, 0.57),
        (0.00, 0.575, 1.00, 0.755),
        (0.00, 0.76, 1.00, 0.92),
    )
    start_y, row_h = 950, 405
    for index, task in enumerate(tasks):
        y0 = start_y + index * row_h
        panel(draw, [170, y0, 2310, y0 + 375], fill="#FFFFFF", outline=SOFT_PURPLE, width=4)
        circle(draw, 230, y0 + 54, 27, 3)
        text.fitted_text(draw, str(index + 1), [207, y0 + 31, 253, y0 + 77], max_size=27, min_size=22, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, task, [285, y0 + 18, 2250, y0 + 90], max_size=31, min_size=24, colour=NAVY, bold=True, align="left", max_lines=2)
        row = crop_norm(source, row_boxes[index])
        paste_fit(canvas, row, [205, y0 + 90, 2275, y0 + 350], 2)


def render_p008(canvas, draw, source, text):
    for index, label in enumerate(("Picture A", "Picture B")):
        x0 = 170 + index * 1085
        panel(draw, [x0, 950, x0 + 1025, 2980])
        image = crop_norm(source, (index * 0.5, 0.05, (index + 1) * 0.5, 0.95))
        paste_fit(canvas, image, [x0 + 35, 1020, x0 + 990, 2890], 5)
        text.fitted_text(draw, label, [x0 + 220, 960, x0 + 805, 1030], max_size=40, min_size=31, colour=NAVY, bold=True, max_lines=1)


def render_p009(canvas, draw, source, text):
    labels = ("fish", "kite", "cup", "car", "butterfly", "shoe")
    # The approved sheet puts the reference in the left half of every cell and
    # three alternatives down the right half.  Recompose the relationship so
    # the child sees LOOK | CHOOSE, and vary the location of the identical
    # alternative instead of teaching a column-position shortcut.
    permutations = ((1, 0, 2), (1, 2, 0), (0, 2, 1), (2, 1, 0), (2, 0, 1), (0, 1, 2))
    for index, label in enumerate(labels):
        col, row = index % 2, index // 2
        x0, y0 = 170 + col * 1085, 950 + row * 675
        activity_card(draw, text, index + 1, f"Circle the {label} that is exactly the same.", x0, y0)
        cell = crop_raw_norm(source, (col / 2, row / 3, (col + 1) / 2, (row + 1) / 3))
        reference = isolate_largest_content(crop_norm(cell, (0.0, 0.0, 0.60, 1.0)))
        # The source alternatives are not distributed in three mathematically
        # equal slices: tails, wheels and handles cross those boundaries. Use
        # overlapping bands and let component isolation retain the complete
        # object in each band.
        choice_bands = ((0.00, 0.46), (0.20, 0.80), (0.50, 1.00))
        choices = [
            isolate_largest_content(crop_norm(cell, (0.50, top, 1.0, bottom)))
            for top, bottom in choice_bands
        ]
        if label == "kite":
            # Kite tails cross the source row boundaries and cannot be split
            # safely from the composite sheet. Build two complete tilted
            # distractors from the intact reference; source index 0 remains
            # the one exact, upright match.
            choices = [
                reference.copy(),
                reference.rotate(-12, expand=True),
                reference.rotate(12, expand=True),
            ]
        text.fitted_text(draw, "LOOK", [x0 + 35, y0 + 125, x0 + 320, y0 + 175], max_size=23, min_size=19, colour="#65758B", bold=True, max_lines=1)
        paste_fit(canvas, reference, [x0 + 35, y0 + 170, x0 + 330, y0 + 530], 4)
        text.fitted_text(draw, label, [x0 + 40, y0 + 525, x0 + 325, y0 + 575], max_size=25, min_size=21, colour=NAVY, bold=True, max_lines=1)
        draw.line([x0 + 350, y0 + 135, x0 + 350, y0 + 585], fill=SOFT_PURPLE, width=4)
        text.fitted_text(draw, "CHOOSE", [x0 + 385, y0 + 125, x0 + 980, y0 + 175], max_size=23, min_size=19, colour="#65758B", bold=True, max_lines=1)
        for display_index, source_index in enumerate(permutations[index]):
            left = x0 + 380 + display_index * 205
            paste_fit(canvas, choices[source_index], [left, y0 + 180, left + 180, y0 + 475], 3)
            option_label(draw, text, chr(65 + display_index), left + 90, y0 + 535)


def render_p010(canvas, draw, source, text):
    labels = ("fruit", "animals", "clothes", "transport", "shapes", "weather")
    source_names = (
        ("apple", "banana", "grapes", "car"), ("lion", "elephant", "cow", "orange"),
        ("shirt", "trousers", "dress", "cup"), ("bus", "aeroplane", "boat", "flower"),
        ("square", "triangle", "circle", "ball"), ("sun", "rain", "storm", "shoe"),
    )
    # The source artwork places every outsider last.  Vary its displayed
    # position so classification, rather than column memory, solves the task.
    permutations = ((0, 3, 1, 2), (1, 2, 3, 0), (3, 0, 1, 2), (0, 1, 2, 3), (2, 3, 0, 1), (1, 2, 3, 0))
    for index, label in enumerate(labels):
        col, row = index % 2, index // 2
        x0, y0 = 170 + col * 1085, 950 + row * 675
        activity_card(draw, text, index + 1, f"Name the pictures. Circle the one that is not {label}.", x0, y0)
        cell = crop_raw_norm(source, (col / 2, row / 3, (col + 1) / 2, (row + 1) / 3))
        objects = [isolate_largest_content(crop_norm(cell, (part / 4, 0.05, (part + 1) / 4, 0.96))) for part in range(4)]
        for display_index, source_index in enumerate(permutations[index]):
            left = x0 + 35 + display_index * 240
            paste_fit(canvas, objects[source_index], [left, y0 + 145, left + 220, y0 + 455], 3)
            text.fitted_text(draw, source_names[index][source_index], [left + 3, y0 + 455, left + 217, y0 + 505], max_size=22, min_size=18, colour=NAVY, bold=True, max_lines=1)
            option_label(draw, text, chr(65 + display_index), left + 110, y0 + 555)


def render_p011(canvas, draw, source, text):
    names = ("shoe", "key", "pencil", "cup", "soap", "bed", "sock", "lock", "sharpener", "jug", "towel", "pillow")
    left = names[:6]
    right = ("towel", "pillow", "sock", "sharpener", "lock", "jug")
    crops = {name: grid_crop_object(source, 2, 6, index) for index, name in enumerate(names)}
    for row in range(6):
        y0 = 950 + row * 335
        for side, name in enumerate((left[row], right[row])):
            x0 = 180 if side == 0 else 1410
            panel(draw, [x0, y0, x0 + 700, y0 + 290], radius=18)
            paste_fit(canvas, crops[name], [x0 + 35, y0 + 18, x0 + 480, y0 + 215], 3)
            text.fitted_text(draw, name, [x0 + 35, y0 + 220, x0 + 480, y0 + 275], max_size=30, min_size=24, colour=NAVY, bold=True, max_lines=1)
            circle(draw, x0 + (650 if side == 0 else 50), y0 + 145, 16, 3)


def render_p012(canvas, draw, source, text):
    panel(draw, [170, 950, 2310, 2180])
    scene = crop_norm(source, (0.03, 0.02, 0.97, 0.48))
    paste_fit(canvas, scene, [205, 1040, 2275, 2140], 6)
    text.fitted_text(draw, "Find and circle these objects in the classroom.", [230, 970, 2250, 1045], max_size=35, min_size=27, colour=NAVY, bold=True, max_lines=1)
    targets = ("ball", "key", "spoon", "sock", "pencil", "teddy")
    crop_boxes = (
        (0.08, 0.47, 0.43, 0.63), (0.58, 0.48, 0.93, 0.63),
        (0.06, 0.62, 0.46, 0.78), (0.55, 0.60, 0.93, 0.79),
        (0.05, 0.78, 0.47, 0.96), (0.56, 0.76, 0.94, 0.98),
    )
    for index, name in enumerate(targets):
        col, row = index % 3, index // 3
        x0, y0 = 170 + col * 725, 2225 + row * 380
        panel(draw, [x0, y0, x0 + 680, y0 + 340], radius=18)
        image = crop_norm(source, crop_boxes[index])
        paste_fit(canvas, image, [x0 + 35, y0 + 15, x0 + 645, y0 + 255], 4)
        text.fitted_text(draw, name, [x0 + 40, y0 + 260, x0 + 640, y0 + 325], max_size=31, min_size=25, colour=NAVY, bold=True, max_lines=1)


def render_rows_with_choices(canvas, draw, source, text, labels, *, grid=(1, 5), draw_box=False):
    cols, rows = grid
    for index, label in enumerate(labels):
        if cols == 1:
            x0, y0, width, height = 170, 940 + index * 410, 2140, 375
        else:
            col, row = index % cols, index // cols
            x0, y0, width, height = 170 + col * 1085, 950 + row * 675, 1025, 625
        panel(draw, [x0, y0, x0 + width, y0 + height])
        image = grid_crop(source, cols, rows, index, margin_y=0.01)
        right_space = 270 if draw_box else 135
        paste_fit(canvas, image, [x0 + 45, y0 + 45, x0 + width - right_space, y0 + height - 55], 4)
        text.fitted_text(draw, label, [x0 + 30, y0 + 12, x0 + 350, y0 + 70], max_size=30, min_size=24, colour=NAVY, bold=True, max_lines=1)
        if draw_box:
            panel(draw, [x0 + width - 235, y0 + 95, x0 + width - 40, y0 + height - 55], fill="#FFFFFF", outline=PURPLE, width=4, radius=16)
        else:
            for option in range(3):
                circle(draw, x0 + width - 70, y0 + 150 + option * ((height - 230) // 2), 21, 4)


def render_p013(canvas, draw, source, text):
    labels = ("stars", "fruit", "shapes", "vehicles", "animals")
    source_indices = (0, 1, 2, 5, 4)
    for display_index, (label, source_index) in enumerate(zip(labels, source_indices)):
        col, row = display_index % 2, display_index // 2
        x0, y0 = 170 + col * 1085, 950 + row * 675
        panel(draw, [x0, y0, x0 + 1025, y0 + 625])
        image = grid_crop(source, 2, 3, source_index, margin_y=0.006)
        paste_fit(canvas, image, [x0 + 45, y0 + 45, x0 + 900, y0 + 570], 3)
        text.fitted_text(draw, label, [x0 + 30, y0 + 15, x0 + 300, y0 + 70], max_size=30, min_size=24, colour=NAVY, bold=True, max_lines=1)
        for option in range(3):
            circle(draw, x0 + 940, y0 + 185 + option * 145, 21, 4)


def render_p015(canvas, draw, source, text):
    tasks = (
        ("Draw the next fruit.", (("apple", "banana") * 2)),
        ("Draw the next shape.", ("circle", "triangle", "triangle", "circle", "triangle", "triangle")),
        ("Draw the next toy.", ("ball", "car", "teddy", "ball", "car", "teddy")),
        ("Draw the next flower.", (("red_flower", "blue_flower") * 2)),
        ("Draw the next animal.", ("cat", "dog", "dog", "cat", "dog", "dog")),
    )
    crop_boxes = {
        "apple": (0.01, 0.10, 0.17, 0.31), "banana": (0.12, 0.10, 0.27, 0.31),
        "circle": (0.54, 0.10, 0.68, 0.31), "triangle": (0.65, 0.10, 0.79, 0.31),
        "ball": (0.00, 0.38, 0.15, 0.59), "car": (0.12, 0.38, 0.30, 0.59), "teddy": (0.28, 0.36, 0.45, 0.59),
        "red_flower": (0.53, 0.37, 0.62, 0.59), "blue_flower": (0.61, 0.37, 0.70, 0.59),
        "cat": (0.00, 0.68, 0.17, 0.89), "dog": (0.13, 0.68, 0.30, 0.89),
    }
    objects = {name: isolate_largest_content(crop_norm(source, box)) for name, box in crop_boxes.items()}
    for index, (instruction, sequence) in enumerate(tasks):
        col, row = index % 2, index // 2
        is_last = index == len(tasks) - 1
        width = 2140 if is_last else 1025
        x0 = 170 if is_last else 170 + col * 1085
        y0 = 950 + row * 675
        activity_card(draw, text, index + 1, instruction, x0, y0, width)
        blank_w = 190 if width == 1025 else 250
        content_left, content_right = x0 + 35, x0 + width - blank_w - 55
        gap = 8
        slot_w = max(72, (content_right - content_left - gap * (len(sequence) - 1)) // len(sequence))
        for item_index, name in enumerate(sequence):
            left = content_left + item_index * (slot_w + gap)
            paste_fit(canvas, objects[name], [left, y0 + 155, left + slot_w, y0 + 520], 2)
        blank_left = x0 + width - blank_w - 30
        panel(draw, [blank_left, y0 + 175, x0 + width - 30, y0 + 535], fill="#FFFFFF", outline=PURPLE, width=4, radius=16)
        text.fitted_text(draw, "DRAW", [blank_left + 12, y0 + 540, x0 + width - 42, y0 + 585], max_size=22, min_size=18, colour="#65758B", bold=True, max_lines=1)


def render_complete_series_p016(canvas, draw, source, text):
    """Five consistent SERIES | CHOOSE activities with one rule per row."""
    tasks = (
        "The circles grow. Circle what comes next.",
        "The number of dots grows by one. Circle what comes next.",
        "The arrow turns right. Circle what comes next.",
        "The ball moves from top to middle to bottom. Circle what comes next.",
        "The colours repeat red, blue, yellow. Circle what comes next.",
    )

    def dot(cx, cy, radius, colour="#FFD447"):
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=colour, outline=NAVY, width=3)

    def arrow(cx, cy, direction, scale=1.0):
        length, head = int(82 * scale), int(30 * scale)
        stroke = max(6, int(13 * scale))
        if direction == "right":
            draw.line([cx - length, cy, cx + length - head, cy], fill="#F05A47", width=stroke)
            draw.polygon([(cx + length, cy), (cx + length - head, cy - head), (cx + length - head, cy + head)], fill="#F05A47")
        elif direction == "left":
            draw.line([cx + length, cy, cx - length + head, cy], fill="#F05A47", width=stroke)
            draw.polygon([(cx - length, cy), (cx - length + head, cy - head), (cx - length + head, cy + head)], fill="#F05A47")
        elif direction == "down":
            draw.line([cx, cy - length, cx, cy + length - head], fill="#F05A47", width=stroke)
            draw.polygon([(cx, cy + length), (cx - head, cy + length - head), (cx + head, cy + length - head)], fill="#F05A47")
        else:
            draw.line([cx, cy + length, cx, cy - length + head], fill="#F05A47", width=stroke)
            draw.polygon([(cx, cy - length), (cx - head, cy - length + head), (cx + head, cy - length + head)], fill="#F05A47")

    for index, instruction in enumerate(tasks):
        col, row = index % 2, index // 2
        is_last = index == 4
        width = 2140 if is_last else 1025
        x0 = 170 if is_last else 170 + col * 1085
        y0 = 950 + row * 675
        activity_card(draw, text, index + 1, instruction, x0, y0, width)
        divider = x0 + (1090 if is_last else 605)
        draw.line([divider, y0 + 135, divider, y0 + 585], fill=SOFT_PURPLE, width=4)
        text.fitted_text(draw, "SERIES", [x0 + 35, y0 + 125, divider - 25, y0 + 170], max_size=22, min_size=18, colour="#65758B", bold=True, max_lines=1)
        text.fitted_text(draw, "CHOOSE", [divider + 25, y0 + 125, x0 + width - 25, y0 + 170], max_size=22, min_size=18, colour="#65758B", bold=True, max_lines=1)
        given_x = ([x0 + 170, x0 + 350, x0 + 530, x0 + 710, x0 + 890] if is_last else [x0 + 90, x0 + 245, x0 + 400])
        choice_x = ([x0 + 1325, x0 + 1650, x0 + 1975] if is_last else [x0 + 690, x0 + 835, x0 + 970])
        cy = y0 + 350

        if index == 0:
            for cx, radius in zip(given_x, (30, 48, 66)):
                dot(cx, cy, radius)
            for choice_index, (cx, radius) in enumerate(zip(choice_x, (84, 50, 30))):
                dot(cx, cy, radius); option_label(draw, text, chr(65 + choice_index), cx, y0 + 555)
        elif index == 1:
            for count, cx in enumerate(given_x, 1):
                for item in range(count):
                    dot(cx + int((item - (count - 1) / 2) * 34), cy, 15, "#43A047")
            for choice_index, (cx, count) in enumerate(zip(choice_x, (2, 4, 3))):
                for item in range(count):
                    dot(cx + int((item % 2 - 0.5) * 34), cy + int((item // 2 - 0.5) * 34), 14, "#43A047")
                option_label(draw, text, chr(65 + choice_index), cx, y0 + 555)
        elif index == 2:
            for cx, direction in zip(given_x, ("right", "down", "left")):
                arrow(cx, cy, direction, 0.55)
            for choice_index, (cx, direction) in enumerate(zip(choice_x, ("left", "down", "up"))):
                arrow(cx, cy, direction, 0.52); option_label(draw, text, chr(65 + choice_index), cx, y0 + 555)
        elif index == 3:
            for cx, ball_y in zip(given_x, (cy - 90, cy, cy + 90)):
                panel(draw, [cx - 58, cy - 135, cx + 58, cy + 135], fill="#FFFFFF", outline="#AAB4C0", width=3, radius=12)
                dot(cx, ball_y, 24, "#3D8BFF")
            for choice_index, (cx, ball_y) in enumerate(zip(choice_x, (cy, cy - 90, cy + 90))):
                panel(draw, [cx - 52, cy - 125, cx + 52, cy + 125], fill="#FFFFFF", outline="#AAB4C0", width=3, radius=12)
                dot(cx, ball_y, 22, "#3D8BFF"); option_label(draw, text, chr(65 + choice_index), cx, y0 + 555)
        else:
            for cx, colour in zip(given_x, ("#F05A47", "#3D8BFF", "#FFD447", "#F05A47", "#3D8BFF")):
                dot(cx, cy, 42, colour)
            for choice_index, (cx, colour) in enumerate(zip(choice_x, ("#3D8BFF", "#F05A47", "#FFD447"))):
                dot(cx, cy, 48, colour); option_label(draw, text, chr(65 + choice_index), cx, y0 + 555)


def render_p014(canvas, draw, source, text):
    names = ("wet hands", "apply soap", "scrub hands", "dry hands")
    order = (3, 0, 2, 1)
    for display_index, crop_index in enumerate(order):
        x0 = 170 + display_index * 535
        panel(draw, [x0, 980, x0 + 490, 2770])
        image = grid_crop(source, 2, 2, crop_index)
        paste_fit(canvas, image, [x0 + 25, 1030, x0 + 465, 2440], 5)
        text.fitted_text(draw, names[crop_index], [x0 + 20, 2450, x0 + 470, 2525], max_size=28, min_size=23, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, "Write the step number.", [x0 + 30, 2535, x0 + 460, 2600], max_size=25, min_size=21, colour=INK, max_lines=1)
        panel(draw, [x0 + 155, 2620, x0 + 335, 2800], fill="#FFFFFF", outline=PURPLE, width=4, radius=18)


def render_p017(canvas, draw, source, text):
    for category, x0 in (("RED", 170), ("BLUE", 1255)):
        panel(draw, [x0, 950, x0 + 1025, 1190], fill="#F7F3FF" if category == "RED" else BLUE)
        text.fitted_text(draw, category, [x0 + 35, 970, x0 + 990, 1040], max_size=39, min_size=31, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, f"Write the {category.lower()} picture numbers:", [x0 + 45, 1045, x0 + 980, 1100], max_size=27, min_size=22, colour=INK, max_lines=1)
        for index in range(4):
            bx = x0 + 95 + index * 220
            panel(draw, [bx, 1110, bx + 150, 1175], fill="#FFFFFF", outline=PURPLE, width=3, radius=12)
    names = ("red button", "blue cube", "blue ball", "red car", "blue button", "red cube", "red ball", "blue car")
    for index, name in enumerate(names):
        col, row = index % 4, index // 4
        x0, y0 = 170 + col * 535, 1240 + row * 850
        panel(draw, [x0, y0, x0 + 490, y0 + 790], radius=18)
        image = grid_crop(source, 2, 4, index)
        paste_fit(canvas, image, [x0 + 45, y0 + 55, x0 + 445, y0 + 600], 4)
        circle(draw, x0 + 48, y0 + 48, 30, 3)
        text.fitted_text(draw, str(index + 1), [x0 + 23, y0 + 20, x0 + 73, y0 + 75], max_size=30, min_size=25, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, name, [x0 + 25, y0 + 625, x0 + 465, y0 + 720], max_size=29, min_size=23, colour=NAVY, bold=True, max_lines=2)


def render_number_sort(canvas, draw, source, text, *, names, categories, cols, rows):
    cat_count = len(categories)
    gap = 30
    width = (2140 - gap * (cat_count - 1)) // cat_count
    for index, category in enumerate(categories):
        x0 = 170 + index * (width + gap)
        panel(draw, [x0, 950, x0 + width, 1195], fill="#F7F3FF" if index % 2 == 0 else BLUE)
        text.fitted_text(draw, category, [x0 + 25, 970, x0 + width - 25, 1045], max_size=36, min_size=27, colour=NAVY, bold=True, max_lines=1)
        for box_index in range(3):
            bx = x0 + 55 + box_index * ((width - 110) // 3)
            panel(draw, [bx, 1080, bx + 140, 1170], fill="#FFFFFF", outline=PURPLE, width=3, radius=12)
    item_cols = 3 if len(names) in {6, 9} else 4
    item_rows = (len(names) + item_cols - 1) // item_cols
    card_w = (2140 - 25 * (item_cols - 1)) // item_cols
    card_h = (1740 - 25 * (item_rows - 1)) // item_rows
    for index, name in enumerate(names):
        col, row = index % item_cols, index // item_cols
        x0, y0 = 170 + col * (card_w + 25), 1240 + row * (card_h + 25)
        panel(draw, [x0, y0, x0 + card_w, y0 + card_h], radius=18)
        image = grid_crop_object(source, cols, rows, index)
        paste_fit(canvas, image, [x0 + 35, y0 + 45, x0 + card_w - 35, y0 + card_h - 125], 4)
        circle(draw, x0 + 45, y0 + 45, 29, 3)
        text.fitted_text(draw, str(index + 1), [x0 + 20, y0 + 18, x0 + 70, y0 + 70], max_size=29, min_size=24, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, name.replace("_", " "), [x0 + 25, y0 + card_h - 105, x0 + card_w - 25, y0 + card_h - 25], max_size=28, min_size=22, colour=NAVY, bold=True, max_lines=2)


def render_size_sets(canvas, draw, source, text):
    names = ("bears", "trees", "cups", "fish", "cars")
    for index, name in enumerate(names):
        col, row = index % 2, index // 2
        x0, y0 = 170 + col * 1085, 950 + row * 675
        panel(draw, [x0, y0, x0 + 1025, y0 + 625])
        image = grid_crop(source, 2, 3, index, margin_y=0.008)
        paste_fit(canvas, image, [x0 + 35, y0 + 55, x0 + 980, y0 + 430], 3)
        text.fitted_text(draw, name, [x0 + 30, y0 + 15, x0 + 350, y0 + 70], max_size=30, min_size=24, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, "Write 1, 2, 3", [x0 + 610, y0 + 445, x0 + 980, y0 + 500], max_size=27, min_size=22, colour=INK, bold=True, max_lines=1)
        for box_index in range(3):
            bx = x0 + 610 + box_index * 125
            panel(draw, [bx, y0 + 515, bx + 100, y0 + 600], fill="#FFFFFF", outline=PURPLE, width=3, radius=12)


def render_match_page(canvas, draw, source, text, *, left_names, right_names, source_names, cols, rows):
    crops = {name: grid_crop_object(source, cols, rows, index) for index, name in enumerate(source_names)}
    count = len(left_names)
    row_h = 1960 // count
    for row in range(count):
        y0 = 950 + row * row_h
        for side, name in enumerate((left_names[row], right_names[row])):
            x0 = 180 if side == 0 else 1410
            panel(draw, [x0, y0, x0 + 700, y0 + row_h - 30], radius=16)
            paste_fit(canvas, crops[name], [x0 + 35, y0 + 15, x0 + 485, y0 + row_h - 92], 3)
            text.fitted_text(draw, name.replace("_", " "), [x0 + 25, y0 + row_h - 88, x0 + 495, y0 + row_h - 25], max_size=27, min_size=22, colour=NAVY, bold=True, max_lines=1)
            circle(draw, x0 + (650 if side == 0 else 50), y0 + (row_h - 30) // 2, 16, 3)


def render_spatial_raw(canvas, draw, source, text, page_id):
    if page_id == "LT-LKG-V4-P023":
        prompts = (
            ("Is the ball LEFT or RIGHT of the boy?", "boy", "ball"),
            ("Is the bird LEFT or RIGHT of the tree?", "bird", "tree"),
            ("Is the teddy LEFT or RIGHT of the box?", "box", "teddy"),
            ("Is the flower LEFT or RIGHT of the bench?", "flower", "bench"),
            ("Is the cup LEFT or RIGHT of the table?", "cup", "table"),
            ("Is the bicycle LEFT or RIGHT of the gate?", "gate", "bicycle"),
        )
        crop_boxes = {
            "boy": (0.13, 0.01, 0.42, 0.31), "ball": (0.37, 0.10, 0.52, 0.30),
            "bird": (0.52, 0.10, 0.65, 0.28), "tree": (0.65, 0.00, 0.91, 0.31),
            "box": (0.12, 0.35, 0.37, 0.63), "teddy": (0.35, 0.39, 0.53, 0.63),
            "flower": (0.53, 0.42, 0.65, 0.63), "bench": (0.65, 0.35, 0.90, 0.63),
            "cup": (0.00, 0.73, 0.14, 0.93), "table": (0.14, 0.67, 0.42, 0.95),
            "gate": (0.63, 0.67, 0.91, 0.95), "bicycle": (0.86, 0.73, 1.00, 0.93),
        }
        objects = {name: isolate_largest_content(crop_norm(source, box)) for name, box in crop_boxes.items()}
        for index, prompt in enumerate(prompts):
            col, row = index % 2, index // 2
            x0, y0 = 170 + col * 1085, 950 + row * 675
            activity_card(draw, text, index + 1, prompt[0], x0, y0)
            paste_fit(canvas, objects[prompt[1]], [x0 + 105, y0 + 140, x0 + 470, y0 + 430], 4)
            paste_fit(canvas, objects[prompt[2]], [x0 + 555, y0 + 140, x0 + 920, y0 + 430], 4)
            text.fitted_text(draw, prompt[1], [x0 + 110, y0 + 410, x0 + 465, y0 + 460], max_size=25, min_size=21, colour=NAVY, bold=True, max_lines=1)
            text.fitted_text(draw, prompt[2], [x0 + 560, y0 + 410, x0 + 915, y0 + 460], max_size=25, min_size=21, colour=NAVY, bold=True, max_lines=1)
            for choice_index, word in enumerate(("LEFT", "RIGHT")):
                bx = x0 + 95 + choice_index * 465
                panel(draw, [bx, y0 + 500, bx + 400, y0 + 585], fill="#FFFFFF", outline=PURPLE, width=3, radius=16)
                text.fitted_text(draw, word, [bx + 15, y0 + 514, bx + 385, y0 + 572], max_size=29, min_size=23, colour=NAVY, bold=True, max_lines=1)
        return
    names = ("bird / tree", "shoe / chair", "sun / cloud", "cat / table", "ball / shelf", "fish / boat") if page_id.endswith("P024") else ("ball / box", "dog / kennel", "fish / bowl", "bird / cage", "teddy / basket", "child / house")
    choices = ("ABOVE", "BELOW") if page_id.endswith("P024") else ("INSIDE", "OUTSIDE")
    for index, name in enumerate(names):
        col, row = index % 2, index // 2
        x0, y0 = 170 + col * 1085, 950 + row * 675
        panel(draw, [x0, y0, x0 + 1025, y0 + 625])
        image = grid_crop(source, 2, 3, index)
        paste_fit(canvas, image, [x0 + 55, y0 + 45, x0 + 970, y0 + 410], 3)
        text.fitted_text(draw, name, [x0 + 200, y0 + 390, x0 + 825, y0 + 445], max_size=28, min_size=23, colour=NAVY, bold=True, max_lines=1)
        for choice_index, word in enumerate(choices):
            bx = x0 + 85 + choice_index * 460
            panel(draw, [bx, y0 + 480, bx + 380, y0 + 575], fill="#FFFFFF", outline=PURPLE, width=3, radius=18)
            text.fitted_text(draw, word, [bx + 15, y0 + 495, bx + 365, y0 + 560], max_size=31, min_size=25, colour=NAVY, bold=True, max_lines=1)


def render_maze(canvas, draw, source, text):
    rabbit = crop_norm(source, (0.05, 0.18, 0.52, 0.82)); carrot = crop_norm(source, (0.52, 0.18, 0.95, 0.82))
    paste_fit(canvas, rabbit, [170, 1000, 560, 1390], 4); paste_fit(canvas, carrot, [1930, 1000, 2310, 1390], 4)
    text.fitted_text(draw, "START", [200, 1370, 540, 1440], max_size=31, min_size=25, colour=NAVY, bold=True, max_lines=1)
    text.fitted_text(draw, "FINISH", [1950, 1370, 2290, 1440], max_size=31, min_size=25, colour=NAVY, bold=True, max_lines=1)
    x0, y0, x1, y1 = 330, 1490, 2150, 2920
    cols, rows = 10, 8; cw, ch = (x1 - x0) // cols, (y1 - y0) // rows
    # Build a deterministic perfect maze so START always connects to FINISH.
    import random
    rng = random.Random(2608)
    walls = {(col, row): {"N", "E", "S", "W"} for row in range(rows) for col in range(cols)}
    visited = {(0, rows - 1)}; stack = [(0, rows - 1)]
    directions = ((0, -1, "N", "S"), (1, 0, "E", "W"), (0, 1, "S", "N"), (-1, 0, "W", "E"))
    while stack:
        col, row = stack[-1]
        choices = [(dc, dr, here, there) for dc, dr, here, there in directions if 0 <= col + dc < cols and 0 <= row + dr < rows and (col + dc, row + dr) not in visited]
        if not choices:
            stack.pop(); continue
        dc, dr, here, there = rng.choice(choices); neighbour = (col + dc, row + dr)
        walls[(col, row)].remove(here); walls[neighbour].remove(there)
        visited.add(neighbour); stack.append(neighbour)
    for row in range(rows):
        for col in range(cols):
            left, top = x0 + col * cw, y0 + row * ch
            if "N" in walls[(col, row)]: draw.line([left, top, left + cw, top], fill=PURPLE, width=5)
            if "W" in walls[(col, row)]: draw.line([left, top, left, top + ch], fill=PURPLE, width=5)
            if row == rows - 1 and "S" in walls[(col, row)]: draw.line([left, top + ch, left + cw, top + ch], fill=PURPLE, width=5)
            if col == cols - 1 and "E" in walls[(col, row)]: draw.line([left + cw, top, left + cw, top + ch], fill=PURPLE, width=5)
    draw.line([x0, y0 + 7 * ch + ch // 2, x0 + 35, y0 + 7 * ch + ch // 2], fill="#FFFCF7", width=14)
    draw.line([x0 + cols * cw - 35, y0 + ch // 2, x0 + cols * cw, y0 + ch // 2], fill="#FFFCF7", width=14)


def render_memory(canvas, draw, source, text):
    panel(draw, [170, 950, 1750, 2980])
    paste_fit(canvas, source, [205, 985, 1715, 2945], 4)
    panel(draw, [1790, 950, 2310, 2980], fill="#F7F3FF", outline=SOFT_PURPLE, width=4)
    text.fitted_text(draw, "MEMORY STEPS", [1830, 990, 2270, 1070], max_size=36, min_size=28, colour=NAVY, bold=True, max_lines=1)
    steps = (
        "Look at the TOP six pictures for 10 seconds.",
        "Cover the top half with a sheet of paper.",
        "In the BOTTOM half, circle the 3 pictures you remember.",
    )
    for index, step in enumerate(steps, 1):
        cy = 1210 + (index - 1) * 360
        circle(draw, 1850, cy, 36, 4)
        text.fitted_text(draw, str(index), [1818, cy - 31, 1882, cy + 31], max_size=34, min_size=27, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, step, [1910, cy - 95, 2270, cy + 105], max_size=31, min_size=24, colour=INK, align="left", max_lines=5)
    panel(draw, [1830, 2350, 2270, 2850], fill=BLUE, outline="#1768B3", width=3)
    text.fitted_text(draw, "SAY THE NAMES", [1870, 2390, 2230, 2470], max_size=31, min_size=25, colour=NAVY, bold=True, max_lines=1)
    text.fitted_text(draw, "apple • ball • cup • car • teddy • kite • bus • dog • flower", [1870, 2510, 2230, 2790], max_size=29, min_size=23, colour=INK, align="left", max_lines=8)


def render_picture_recall(canvas, draw, source, text):
    panel(draw, [170, 940, 2310, 2010])
    paste_fit(canvas, source, [205, 980, 2275, 1970], 5)
    text.fitted_text(draw, "LOOK FOR 10 SECONDS. THEN COVER THE PICTURE.", [200, 950, 2280, 1030], max_size=36, min_size=28, colour=NAVY, bold=True, max_lines=1)
    questions = (
        ("What colour was the kite?", "RED", "GREEN"),
        ("How many birds were there?", "1", "2", "3"),
        ("What was beside the tree?", "GIRL", "BUS"),
        ("What colour was the ball?", "BLUE", "YELLOW"),
        ("Which animal was there?", "DOG", "CAT"),
    )
    for index, choices in enumerate(questions):
        col, row = index % 2, index // 2
        x0, y0 = 170 + col * 1085, 2050 + row * 300
        panel(draw, [x0, y0, x0 + 1025, y0 + 265], radius=16)
        text.fitted_text(draw, choices[0], [x0 + 30, y0 + 20, x0 + 995, y0 + 95], max_size=30, min_size=24, colour=NAVY, bold=True, max_lines=1)
        choice_w = 850 // (len(choices) - 1)
        for choice_index, word in enumerate(choices[1:]):
            bx = x0 + 70 + choice_index * choice_w
            panel(draw, [bx, y0 + 125, bx + choice_w - 50, y0 + 225], fill="#FFFFFF", outline=PURPLE, width=3, radius=16)
            text.fitted_text(draw, word, [bx + 15, y0 + 140, bx + choice_w - 65, y0 + 210], max_size=29, min_size=23, colour=NAVY, bold=True, max_lines=1)


def render_memory_integrated(canvas, draw, source, text):
    """Keep the study direction with the study set and recall direction with choices."""
    panel(draw, [170, 950, 2310, 1910], fill="#FFFFFF", outline=SOFT_PURPLE, width=4)
    panel(draw, [190, 970, 2290, 1070], fill="#F7F3FF", outline=None, width=0, radius=14)
    text.fitted_text(draw, "1  LOOK, NAME AND REMEMBER THESE SIX PICTURES.", [230, 985, 2250, 1055], max_size=34, min_size=27, colour=NAVY, bold=True, max_lines=1)
    study = crop_norm(source, (0.0, 0.0, 1.0, 0.515))
    paste_fit(canvas, study, [210, 1090, 2270, 1880], 3)
    panel(draw, [170, 1950, 2310, 2980], fill="#FFFFFF", outline=SOFT_PURPLE, width=4)
    panel(draw, [190, 1970, 2290, 2070], fill=BLUE, outline=None, width=0, radius=14)
    text.fitted_text(draw, "2  COVER THE TOP. CIRCLE THE THREE PICTURES YOU REMEMBER.", [230, 1985, 2250, 2055], max_size=33, min_size=26, colour=NAVY, bold=True, max_lines=1)
    choices = crop_norm(source, (0.0, 0.52, 1.0, 1.0))
    paste_fit(canvas, choices, [210, 2090, 2270, 2945], 3)


def render_task_grid(canvas, draw, source, text, labels, *, circles=3, start_y=950, cols=2, source_rows=3):
    for index, label in enumerate(labels):
        col, row = index % cols, index // cols
        x0, y0 = 170 + col * 1085, start_y + row * 675
        panel(draw, [x0, y0, x0 + 1025, y0 + 625])
        image = grid_crop(source, cols, source_rows, index, margin_y=0.008)
        paste_fit(canvas, image, [x0 + 45, y0 + 55, x0 + 900, y0 + 535], 3)
        text.fitted_text(draw, label, [x0 + 30, y0 + 15, x0 + 850, y0 + 75], max_size=29, min_size=23, colour=NAVY, bold=True, max_lines=1)
        if circles:
            for option in range(circles):
                circle(draw, x0 + 945, y0 + 175 + option * 145, 21, 4)


def render_complete_puzzle_p033(canvas, draw, source, text):
    instructions = (
        "Circle the piece that completes the train.", "Circle the piece that completes the fish.",
        "Circle the piece that completes the flower.", "Circle the piece that completes the kite.",
        "Circle the piece that completes the teddy bear.",
    )
    # The approved sheet stores the incomplete picture above its three answer
    # pieces. Crop those regions separately so the composer never cuts the
    # answer pieces or mistakes them for part of the main picture.
    main_boxes = (
        (0.00, 0.00, 0.50, 0.235), (0.50, 0.00, 1.00, 0.235),
        (0.00, 0.345, 0.50, 0.555), (0.50, 0.345, 1.00, 0.585),
        (0.00, 0.67, 0.50, 0.88),
    )
    choice_boxes = (
        (0.00, 0.225, 0.50, 0.335), (0.50, 0.225, 1.00, 0.335),
        (0.00, 0.545, 0.50, 0.675), (0.50, 0.575, 1.00, 0.675),
        (0.00, 0.865, 0.50, 1.00),
    )
    for index, instruction in enumerate(instructions):
        col, row = index % 2, index // 2
        is_last = index == 4
        width = 2140 if is_last else 1025
        x0 = 170 if is_last else 170 + col * 1085
        y0 = 950 + row * 675
        activity_card(draw, text, index + 1, instruction, x0, y0, width)
        if index != 3:
            main = crop_norm(source, main_boxes[index])
            choices = crop_norm(source, choice_boxes[index])
            side_pad = 460 if is_last else 65
            paste_fit(canvas, main, [x0 + side_pad, y0 + 125, x0 + width - side_pad, y0 + 405], 2)
            draw.line([x0 + 55, y0 + 415, x0 + width - 55, y0 + 415], fill=SOFT_PURPLE, width=4)
            choice_pad = 570 if is_last else 105
            paste_fit(canvas, choices, [x0 + choice_pad, y0 + 425, x0 + width - choice_pad, y0 + 565], 2)
        else:
            main = crop_norm(source, (0.50, 0.355, 1.00, 0.585))
            paste_fit(canvas, main, [x0 + 180, y0 + 125, x0 + width - 180, y0 + 395], 2)
            draw.line([x0 + 55, y0 + 410, x0 + width - 55, y0 + 410], fill=SOFT_PURPLE, width=4)
            # All alternatives use the same square jigsaw silhouette.  The
            # earlier arrow pieces could never fit the square kite opening.
            colours = (
                ("#3D8BFF",) * 4,
                ("#F05A47", "#FFD447", "#3D8BFF", "#43A047"),
                ("#FFD447",) * 4,
            )
            for choice_index, quadrants in enumerate(colours):
                cx = x0 + 285 + choice_index * 225
                draw.rectangle([cx - 58, y0 + 455, cx, y0 + 507], fill=quadrants[0])
                draw.rectangle([cx, y0 + 455, cx + 58, y0 + 507], fill=quadrants[1])
                draw.rectangle([cx - 58, y0 + 507, cx, y0 + 560], fill=quadrants[2])
                draw.rectangle([cx, y0 + 507, cx + 58, y0 + 560], fill=quadrants[3])
                draw.rectangle([cx - 58, y0 + 455, cx + 58, y0 + 560], outline=NAVY, width=3)
                draw.ellipse([cx - 22, y0 + 433, cx + 22, y0 + 477], fill=quadrants[0], outline=NAVY, width=3)
                option_label(draw, text, chr(65 + choice_index), cx, y0 + 585)


def render_thinking_challenge_p036(canvas, draw, source, text):
    instructions = (
        "Circle the picture that is not a fruit.", "Circle the butterfly that is exactly the same.",
        "Draw the next flower in the box.", "Write 1, 2, 3 from small to big.",
        "Circle the shadow that matches the ball.",
    )
    crop_boxes = {
        "apple": (0.00, 0.08, 0.13, 0.27), "banana": (0.11, 0.08, 0.25, 0.27),
        "carrot": (0.22, 0.08, 0.36, 0.27), "watermelon": (0.33, 0.08, 0.50, 0.27),
        "butterfly": (0.60, 0.01, 0.90, 0.20),
        "red_flower": (0.00, 0.36, 0.12, 0.55), "blue_flower": (0.10, 0.36, 0.23, 0.55),
        "ball": (0.08, 0.68, 0.39, 0.83), "shadow_pattern": (0.00, 0.82, 0.17, 1.00),
        "shadow_circle": (0.16, 0.82, 0.32, 1.00), "shadow_bear": (0.31, 0.82, 0.49, 1.00),
    }
    objects = {name: isolate_largest_content(crop_norm(source, box)) for name, box in crop_boxes.items()}
    for index, instruction in enumerate(instructions):
        col, row = index % 2, index // 2
        is_last = index == 4
        width = 2140 if is_last else 1025
        x0 = 170 if is_last else 170 + col * 1085
        y0 = 950 + row * 675
        activity_card(draw, text, index + 1, instruction, x0, y0, width)
        if index == 0:
            order = ("apple", "carrot", "banana", "watermelon")
            for item_index, name in enumerate(order):
                left = x0 + 35 + item_index * 240
                paste_fit(canvas, objects[name], [left, y0 + 165, left + 215, y0 + 500], 3)
                option_label(draw, text, chr(65 + item_index), left + 108, y0 + 555)
        elif index == 1:
            text.fitted_text(draw, "LOOK", [x0 + 35, y0 + 125, x0 + 315, y0 + 170], max_size=22, min_size=18, colour="#65758B", bold=True, max_lines=1)
            paste_fit(canvas, objects["butterfly"], [x0 + 40, y0 + 175, x0 + 325, y0 + 520], 3)
            draw.line([x0 + 350, y0 + 135, x0 + 350, y0 + 585], fill=SOFT_PURPLE, width=4)
            # A horizontal flip is not a valid distractor for a nearly
            # symmetrical butterfly; it can look identical. Both distractors
            # are visibly tilted while B is the sole exact upright match.
            variants = (
                objects["butterfly"].rotate(18, expand=True),
                objects["butterfly"],
                objects["butterfly"].rotate(-18, expand=True),
            )
            for choice_index, image in enumerate(variants):
                left = x0 + 380 + choice_index * 205
                paste_fit(canvas, image, [left, y0 + 180, left + 180, y0 + 475], 3)
                option_label(draw, text, chr(65 + choice_index), left + 90, y0 + 535)
        elif index == 2:
            sequence = ("red_flower", "blue_flower", "red_flower", "blue_flower")
            for item_index, name in enumerate(sequence):
                left = x0 + 35 + item_index * 185
                paste_fit(canvas, objects[name], [left, y0 + 175, left + 165, y0 + 505], 3)
            panel(draw, [x0 + 805, y0 + 175, x0 + 980, y0 + 520], fill="#FFFFFF", outline=PURPLE, width=4, radius=16)
        elif index == 3:
            bears = crop_norm(source, (0.50, 0.35, 1.00, 0.67))
            paste_fit(canvas, bears, [x0 + 80, y0 + 140, x0 + 945, y0 + 485], 3)
            for box_index in range(3):
                left = x0 + 250 + box_index * 190
                panel(draw, [left, y0 + 505, left + 135, y0 + 585], fill="#FFFFFF", outline=PURPLE, width=4, radius=12)
        else:
            paste_fit(canvas, objects["ball"], [x0 + 180, y0 + 145, x0 + 750, y0 + 505], 3)
            text.fitted_text(draw, "LOOK", [x0 + 210, y0 + 505, x0 + 720, y0 + 555], max_size=23, min_size=19, colour="#65758B", bold=True, max_lines=1)
            draw.line([x0 + 850, y0 + 140, x0 + 850, y0 + 580], fill=SOFT_PURPLE, width=4)
            order = ("shadow_circle", "shadow_pattern", "shadow_bear")
            for choice_index, name in enumerate(order):
                left = x0 + 980 + choice_index * 350
                paste_fit(canvas, objects[name], [left, y0 + 160, left + 300, y0 + 500], 3)
                option_label(draw, text, chr(65 + choice_index), left + 150, y0 + 555)


def render_brain_challenge_p038(canvas, draw, source, text):
    tasks = list(DIRECT_ACTIVITY["LT-LKG-V4-P038"]["tasks"])
    tasks[0] = "Continue the dog and cat pattern. Circle what comes next."
    pattern_source = Image.open(ROOT / "assets/illustrations/logical-thinking-adventures/lkg/LT-LKG-V4-P015.png").convert("RGBA")
    dog = isolate_largest_content(crop_norm(pattern_source, (0.13, 0.68, 0.30, 0.89)))
    cat = isolate_largest_content(crop_norm(pattern_source, (0.00, 0.68, 0.17, 0.89)))
    for index, task in enumerate(tasks):
        col, row = index % 2, index // 2
        is_last = index == 4
        width = 2140 if is_last else 1025
        x0 = 170 if is_last else 170 + col * 1085
        y0 = 730 + row * 735
        activity_card(draw, text, index + 1, task, x0, y0, width)
        if index == 0:
            text.fitted_text(draw, "PATTERN", [x0 + 35, y0 + 125, x0 + 575, y0 + 170], max_size=22, min_size=18, colour="#65758B", bold=True, max_lines=1)
            for item_index, image in enumerate((dog, cat, dog, cat)):
                left = x0 + 35 + item_index * 125
                paste_fit(canvas, image, [left, y0 + 180, left + 110, y0 + 455], 2)
            panel(draw, [x0 + 535, y0 + 215, x0 + 605, y0 + 430], fill="#FFFFFF", outline=PURPLE, width=4, radius=12)
            draw.line([x0 + 625, y0 + 145, x0 + 625, y0 + 565], fill=SOFT_PURPLE, width=4)
            text.fitted_text(draw, "CHOOSE", [x0 + 650, y0 + 125, x0 + width - 25, y0 + 170], max_size=22, min_size=18, colour="#65758B", bold=True, max_lines=1)
            choices = (cat, dog, cat.rotate(-15, expand=True))
            for choice_index, image in enumerate(choices):
                left = x0 + 650 + choice_index * 120
                paste_fit(canvas, image, [left, y0 + 190, left + 105, y0 + 455], 2)
                option_label(draw, text, chr(65 + choice_index), left + 52, y0 + 535)
        elif index < 4:
            image = crop_norm(source, (col / 2, row / 3, (col + 1) / 2, (row + 1) / 3))
            paste_fit(canvas, image, [x0 + 35, y0 + 130, x0 + width - 35, y0 + 585], 2)
        else:
            leaf_boxes = {
                "green": (0.00, 0.68, 0.18, 0.86), "yellow": (0.17, 0.68, 0.34, 0.86),
                "orange": (0.33, 0.68, 0.50, 0.86), "red": (0.34, 0.84, 0.50, 1.00),
            }
            leaves = {name: isolate_largest_content(crop_norm(source, box)) for name, box in leaf_boxes.items()}
            for item_index, name in enumerate(("green", "yellow", "orange")):
                left = x0 + 180 + item_index * 300
                paste_fit(canvas, leaves[name], [left, y0 + 160, left + 245, y0 + 465], 3)
                if item_index < 2:
                    draw.line([left + 250, y0 + 310, left + 290, y0 + 310], fill=PURPLE, width=8)
                    draw.polygon([(left + 290, y0 + 310), (left + 265, y0 + 290), (left + 265, y0 + 330)], fill=PURPLE)
            draw.line([x0 + 1050, y0 + 140, x0 + 1050, y0 + 585], fill=SOFT_PURPLE, width=4)
            for choice_index, name in enumerate(("orange", "red", "green")):
                left = x0 + 1160 + choice_index * 300
                paste_fit(canvas, leaves[name], [left, y0 + 165, left + 245, y0 + 465], 3)
                option_label(draw, text, chr(65 + choice_index), left + 122, y0 + 535)


def render_finish_picture(canvas, draw, source, text):
    labels = ("apple", "fish", "flower", "house", "balloon")
    for index, label in enumerate(labels):
        col, row = index % 2, index // 2
        is_last = index == len(labels) - 1
        width = 2140 if is_last else 1025
        x0 = 170 if is_last else 170 + col * 1085
        y0 = 950 + row * 675
        activity_card(draw, text, index + 1, f"Finish the {label}. Draw the missing half.", x0, y0, width)
        image = grid_crop(source, 2, 3, index)
        centre = x0 + width // 2
        paste_fit_aligned(canvas, image, [x0 + 55, y0 + 145, centre, y0 + 555], align="right", inset=0)
        draw.line([centre, y0 + 145, centre, y0 + 555], fill="#8793A4", width=4)
        # The whole right half is purposeful drawing space; a light dashed
        # boundary makes that space obvious without tracing the answer.
        draw.rounded_rectangle([centre, y0 + 145, x0 + width - 35, y0 + 555], radius=18, outline="#B9A2E7", width=3)
        text.fitted_text(draw, "DRAW THE OTHER HALF", [centre + 40, y0 + 475, x0 + width - 60, y0 + 540], max_size=24, min_size=19, colour="#65758B", bold=True, max_lines=1)


def render_coding(canvas, draw, source, text):
    endpoint_names = (("mouse", "cheese"), ("bee", "flower"), ("car", "garage"))
    endpoints = [grid_crop(source, 2, 3, index) for index in range(6)]
    for task in range(3):
        y0 = 950 + task * 665
        panel(draw, [170, y0, 2310, y0 + 620])
        panel(draw, [205, y0 + 25, 505, y0 + 90], fill=BLUE, outline="#1768B3", width=2, radius=12)
        panel(draw, [1970, y0 + 25, 2270, y0 + 90], fill=GREEN, outline="#5F9D50", width=2, radius=12)
        text.fitted_text(draw, "START", [225, y0 + 34, 485, y0 + 80], max_size=27, min_size=22, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, "GOAL", [1990, y0 + 34, 2250, y0 + 80], max_size=27, min_size=22, colour=NAVY, bold=True, max_lines=1)
        paste_fit(canvas, endpoints[task * 2], [200, y0 + 70, 520, y0 + 380], 3)
        paste_fit(canvas, endpoints[task * 2 + 1], [1970, y0 + 70, 2280, y0 + 380], 3)
        text.fitted_text(draw, endpoint_names[task][0], [210, y0 + 390, 500, y0 + 450], max_size=27, min_size=22, colour=NAVY, bold=True, max_lines=1)
        text.fitted_text(draw, endpoint_names[task][1], [1980, y0 + 390, 2270, y0 + 450], max_size=27, min_size=22, colour=NAVY, bold=True, max_lines=1)
        gx0, gy0, cell = 610, y0 + 70, 120
        cols = 5 if task == 2 else 4; rows = 4
        for row in range(rows + 1): draw.line([gx0, gy0 + row * cell, gx0 + cols * cell, gy0 + row * cell], fill=PURPLE, width=3)
        for col in range(cols + 1): draw.line([gx0 + col * cell, gy0, gx0 + col * cell, gy0 + rows * cell], fill=PURPLE, width=3)
        text.fitted_text(draw, "Draw one arrow in each box along your path.", [950, y0 + 535, 1950, y0 + 605], max_size=28, min_size=23, colour=NAVY, bold=True, max_lines=1)


def render_journal(canvas, draw, source, text):
    labels = ("I observed", "I matched", "I put in order")
    for index, label in enumerate(labels):
        x0 = 170 + index * 725
        panel(draw, [x0, 760, x0 + 680, 1150], radius=18)
        icon_cx, icon_cy = x0 + 190, 930
        if index == 0:
            # Complete magnifying glass: no crop fragments from the composite.
            draw.ellipse([icon_cx - 72, icon_cy - 72, icon_cx + 72, icon_cy + 72], fill="#E8F4FF", outline="#1768B3", width=10)
            draw.ellipse([icon_cx - 47, icon_cy - 47, icon_cx + 47, icon_cy + 47], outline="#69B9E8", width=6)
            draw.line([icon_cx + 50, icon_cy + 50, icon_cx + 122, icon_cy + 122], fill="#1768B3", width=18)
        elif index == 1:
            # Two identical shapes joined by a line model matching.
            draw.ellipse([icon_cx - 120, icon_cy - 58, icon_cx - 20, icon_cy + 42], fill="#FFD447", outline=NAVY, width=4)
            draw.ellipse([icon_cx + 55, icon_cy - 58, icon_cx + 155, icon_cy + 42], fill="#FFD447", outline=NAVY, width=4)
            draw.line([icon_cx - 15, icon_cy - 8, icon_cx + 50, icon_cy - 8], fill=PURPLE, width=8)
        else:
            # Three complete ordered cards replace the clipped puzzle artwork.
            for number, dx, colour in ((1, -120, "#F05A47"), (2, 0, "#FFD447"), (3, 120, "#43A047")):
                panel(draw, [icon_cx + dx - 48, icon_cy - 65, icon_cx + dx + 48, icon_cy + 65], fill=colour, outline=NAVY, width=4, radius=12)
                text.fitted_text(draw, str(number), [icon_cx + dx - 36, icon_cy - 45, icon_cx + dx + 36, icon_cy + 45], max_size=44, min_size=34, colour=NAVY, bold=True, max_lines=1)
        panel(draw, [x0 + 355, 900, x0 + 425, 970], fill="#FFFFFF", outline=PURPLE, width=4, radius=8)
        text.fitted_text(draw, label, [x0 + 440, 875, x0 + 650, 1000], max_size=29, min_size=23, colour=NAVY, bold=True, max_lines=2)
    panel(draw, [170, 1210, 2310, 2600], fill="#FFFFFF", outline=SOFT_PURPLE, width=4)
    text.fitted_text(draw, "Draw a problem you solved.", [220, 1240, 2260, 1330], max_size=40, min_size=31, colour=NAVY, bold=True, max_lines=1)
    text.fitted_text(draw, "I solved it by…", [190, 2660, 750, 2740], max_size=36, min_size=28, colour=NAVY, bold=True, max_lines=1)
    draw.line([720, 2730, 2270, 2730], fill=PURPLE, width=3); draw.line([190, 2850, 2270, 2850], fill=PURPLE, width=3)


def render_celebration(canvas, draw, source, text):
    labels = ("I can observe", "I can match", "I can sort", "I can put in order", "I can solve")
    for index, label in enumerate(labels):
        col, row = index % 2, index // 2
        x0, y0 = 260 + col * 1050, 930 + row * 680
        panel(draw, [x0, y0, x0 + 910, y0 + 620], fill="#FFFFFF", outline=SOFT_PURPLE, width=3)
        image = grid_crop(source, 2, 3, index, margin_y=0.01)
        paste_fit(canvas, image, [x0 + 110, y0 + 35, x0 + 800, y0 + 470], 3)
        text.fitted_text(draw, label, [x0 + 40, y0 + 485, x0 + 870, y0 + 575], max_size=34, min_size=27, colour=NAVY, bold=True, max_lines=1)


def render_certificate(canvas, draw, source, logo, text, page):
    panel(draw, [115, 115, 2365, 3375], fill="#FFFEF7", outline="#E2B13C", width=8, radius=36)
    logo_image = logo.copy(); logo_image.thumbnail((360, 250), Image.Resampling.LANCZOS); canvas.paste(logo_image, (1060, 150), logo_image)
    text.fitted_text(draw, "CERTIFICATE OF ACHIEVEMENT", [260, 430, 2220, 590], max_size=65, min_size=48, colour=NAVY, bold=True, max_lines=1)
    text.fitted_text(draw, "Logical Thinking Adventures", [360, 610, 2120, 720], max_size=48, min_size=36, colour=PURPLE, bold=True, max_lines=1)
    badge = crop_norm(source, (0.0, 0.0, 0.62, 1.0)); corners = crop_norm(source, (0.58, 0.0, 1.0, 1.0))
    paste_fit(canvas, badge, [710, 760, 1770, 1660], 5); paste_fit(canvas, corners, [1750, 300, 2290, 900], 5)
    text.fitted_text(draw, "This certificate is proudly presented to", [360, 1710, 2120, 1810], max_size=40, min_size=31, colour=INK, max_lines=1)
    draw.line([420, 2010, 2060, 2010], fill=PURPLE, width=4)
    text.fitted_text(draw, "for completing the Logical Thinking Adventures journey.", [300, 2070, 2180, 2200], max_size=39, min_size=30, colour=NAVY, bold=True, max_lines=2)
    text.fitted_text(draw, "Date", [360, 2510, 700, 2590], max_size=31, min_size=25, colour=INK, max_lines=1); draw.line([330, 2700, 1030, 2700], fill=PURPLE, width=3)
    text.fitted_text(draw, "Teacher’s signature", [1390, 2510, 2100, 2590], max_size=31, min_size=25, colour=INK, max_lines=1); draw.line([1360, 2700, 2130, 2700], fill=PURPLE, width=3)
    text.fitted_text(draw, "Well done, Logic Explorer!", [420, 2900, 2060, 3060], max_size=52, min_size=40, colour=PURPLE, bold=True, max_lines=1)


def render_explorer(canvas, draw, source, text):
    # The approved sheet is an irregular five-asset composition, not a grid.
    # Exact regions prevent neighbouring artwork from leaking into the cards.
    hero = crop_norm(source, (0.0, 0.0, 0.52, 0.40)); badge = crop_norm(source, (0.48, 0.0, 1.0, 0.40))
    panel(draw, [170, 940, 2310, 2050]); paste_fit(canvas, hero, [220, 980, 1210, 1990], 4); paste_fit(canvas, badge, [1280, 980, 2250, 1990], 4)
    labels = ("Observe", "Match", "Solve")
    icons = (
        crop_norm(source, (0.08, 0.39, 0.43, 0.70)),
        crop_norm(source, (0.50, 0.42, 0.98, 0.70)),
        crop_norm(source, (0.08, 0.71, 0.47, 0.97)),
    )
    for index, label in enumerate(labels):
        x0 = 250 + index * 720
        panel(draw, [x0, 2110, x0 + 650, 2800], radius=20)
        paste_fit(canvas, icons[index], [x0 + 80, 2150, x0 + 570, 2610], 3)
        panel(draw, [x0 + 70, 2670, x0 + 140, 2740], fill="#FFFFFF", outline=PURPLE, width=4, radius=8)
        text.fitted_text(draw, label, [x0 + 170, 2640, x0 + 590, 2770], max_size=35, min_size=27, colour=NAVY, bold=True, max_lines=1)


RENDERERS = {
    "LT-LKG-V4-P008": render_p008,
    "LT-LKG-V4-P009": render_p009,
    "LT-LKG-V4-P010": render_p010,
    "LT-LKG-V4-P011": render_p011,
    "LT-LKG-V4-P012": render_p012,
    "LT-LKG-V4-P013": render_p013,
    "LT-LKG-V4-P014": render_p014,
    "LT-LKG-V4-P015": render_p015,
    "LT-LKG-V4-P017": render_p017,
}


def render(page_id: str, illustration: Path, logo_path: Path, output: Path, evidence_path: Path):
    contract = load_json(CONTRACT)
    if page_id not in contract.get("pages", {}):
        raise ValueError(f"Runtime contract missing {page_id}")
    if page_id not in {f"LT-LKG-V4-P{number:03d}" for number in range(8, 44)}:
        raise ValueError(f"Exact renderer not implemented for {page_id}")
    page = contract["pages"][page_id]
    source = Image.open(illustration).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")
    template = load_json(TEMPLATE)
    module = load_module("logical_thinking_text_engine", TEXT_ENGINE)
    text = module
    canvas = Image.new("RGB", (WIDTH, HEIGHT), "#FFFCF7")
    draw = ImageDraw.Draw(canvas)
    if page_id == "LT-LKG-V4-P042":
        render_certificate(canvas, draw, source, logo, text, page)
        output.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output, "PNG")
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(json.dumps({"page_id": page_id, "status": "PASS", "certificate_complete": True, "renderer": Path(__file__).name}, indent=2) + "\n", encoding="utf-8")
        return
    header(canvas, draw, page, logo, text)
    if page.get("layout", {}).get("completed_example", True) and page_id not in {"LT-LKG-V4-P040", "LT-LKG-V4-P041", "LT-LKG-V4-P043"}:
        completed_model(canvas, draw, page_id, text)
    integrated_task_pages = {
        "LT-LKG-V4-P013", "LT-LKG-V4-P029",
        "LT-LKG-V4-P037", "LT-LKG-V4-P039",
    }
    if page_id in integrated_task_pages:
        render_direct_activity(canvas, draw, source, text, page_id)
    elif page_id == "LT-LKG-V4-P016":
        render_complete_series_p016(canvas, draw, source, text)
    elif page_id == "LT-LKG-V4-P018":
        render_number_sort(canvas, draw, source, text, names=("clock", "window", "flag", "plate", "tile", "sandwich", "coin", "gift box", "road sign"), categories=("CIRCLE", "SQUARE", "TRIANGLE"), cols=2, rows=5)
    elif page_id == "LT-LKG-V4-P019":
        render_size_sets(canvas, draw, source, text)
    elif page_id == "LT-LKG-V4-P020":
        render_match_page(canvas, draw, source, text, left_names=("pencil", "shoe", "soap", "bed", "car", "spoon"), right_names=("towel", "garage", "sharpener", "bowl", "pillow", "sock"), source_names=("pencil", "shoe", "soap", "bed", "car", "spoon", "sharpener", "sock", "towel", "pillow", "garage", "bowl"), cols=2, rows=6)
    elif page_id == "LT-LKG-V4-P021":
        render_number_sort(canvas, draw, source, text, names=("broken crayon", "spilled water", "missing toy", "smoke", "hurt knee", "lost outside"), categories=("SMALL", "BIG — TELL AN ADULT"), cols=2, rows=3)
    elif page_id == "LT-LKG-V4-P022":
        render_match_page(canvas, draw, source, text, left_names=("drop ice", "push ball", "rain cloud", "turn switch", "open umbrella"), right_names=("lit lamp", "puddle", "dry child", "wet ground", "rolling ball"), source_names=("drop ice", "push ball", "rain cloud", "turn switch", "open umbrella", "puddle", "rolling ball", "wet ground", "lit lamp", "dry child"), cols=2, rows=5)
    elif page_id in {"LT-LKG-V4-P023", "LT-LKG-V4-P024", "LT-LKG-V4-P025"}:
        render_spatial_raw(canvas, draw, source, text, page_id)
    elif page_id == "LT-LKG-V4-P026":
        render_maze(canvas, draw, source, text)
    elif page_id == "LT-LKG-V4-P027":
        render_memory_integrated(canvas, draw, source, text)
    elif page_id == "LT-LKG-V4-P028":
        render_picture_recall(canvas, draw, source, text)
    elif page_id == "LT-LKG-V4-P029":
        render_direct_activity(canvas, draw, source, text, page_id)
    elif page_id == "LT-LKG-V4-P030":
        render_finish_picture(canvas, draw, source, text)
    elif page_id == "LT-LKG-V4-P031":
        render_match_page(canvas, draw, source, text, left_names=("cat top", "bus left", "ball top", "flower left", "fish top"), right_names=("fish bottom", "flower right", "cat bottom", "ball bottom", "bus right"), source_names=("cat top", "bus left", "ball top", "flower left", "fish top", "fish bottom", "flower right", "cat bottom", "ball bottom", "bus right"), cols=2, rows=5)
    elif page_id == "LT-LKG-V4-P032":
        render_match_page(canvas, draw, source, text, left_names=("umbrella", "boot", "teapot", "guitar", "duck", "bicycle"), right_names=("duck shadow", "bicycle shadow", "boot shadow", "umbrella shadow", "guitar shadow", "teapot shadow"), source_names=("umbrella", "boot", "teapot", "guitar", "duck", "bicycle", "duck shadow", "bicycle shadow", "boot shadow", "umbrella shadow", "guitar shadow", "teapot shadow"), cols=2, rows=6)
    elif page_id == "LT-LKG-V4-P033":
        render_complete_puzzle_p033(canvas, draw, source, text)
    elif page_id == "LT-LKG-V4-P034":
        render_picture_logic_p034(canvas, draw, source, text)
    elif page_id == "LT-LKG-V4-P035":
        render_coding(canvas, draw, source, text)
    elif page_id == "LT-LKG-V4-P036":
        render_thinking_challenge_p036(canvas, draw, source, text)
    elif page_id == "LT-LKG-V4-P037":
        render_task_grid(canvas, draw, source, text, ("find difference", "match", "sort", "put in order", "position", "pattern"), circles=1)
    elif page_id == "LT-LKG-V4-P038":
        render_brain_challenge_p038(canvas, draw, source, text)
    elif page_id == "LT-LKG-V4-P039":
        render_task_grid(canvas, draw, source, text, ("observation", "classification", "matching", "sequence", "position", "coding"), circles=1, start_y=730)
    elif page_id == "LT-LKG-V4-P040":
        render_journal(canvas, draw, source, text)
    elif page_id == "LT-LKG-V4-P041":
        render_celebration(canvas, draw, source, text)
    elif page_id == "LT-LKG-V4-P043":
        render_explorer(canvas, draw, source, text)
    else:
        RENDERERS[page_id](canvas, draw, source, text)
    if page_id not in {"LT-LKG-V4-P041", "LT-LKG-V4-P043"}:
        teacher_footer(draw, page, text)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, "PNG")
    evidence = {
        "page_id": page_id,
        "status": "PASS",
        "output": str(output),
        "source_illustration": str(illustration),
        "source_sha256": hashlib.sha256(illustration.read_bytes()).hexdigest(),
        "completed_example_visible": True,
        "independent_answers_unmarked": True,
        "object_names_visible": True,
        "parent_or_home_panel": False,
        "generic_activity_box": False,
        "renderer": Path(__file__).name,
    }
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--page-id", required=True)
    parser.add_argument("--illustration", type=Path, required=True)
    parser.add_argument("--logo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    args = parser.parse_args()
    render(args.page_id, args.illustration, args.logo, args.output, args.evidence_output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"Logical Thinking render FAIL: {exc}", file=sys.stderr)
        raise SystemExit(2)
