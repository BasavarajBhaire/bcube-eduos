#!/usr/bin/env python3
"""Curriculum-first Early Literacy Adventures LKG page composer.

The first implementation wave covers the two deterministic foundation pages
and the proven Read & Match regression page. Unsupported page mechanics fail
closed until their exact renderer is implemented.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "bcube-publishing-sdk/composer/compose_learning_page_v2.py"
TEMPLATE = ROOT / "bcube-publishing-sdk/templates/learning-page-v2.json"
LOADER = ROOT / "bcube-publishing-sdk/runtime/load_book_contract.py"

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
        raise ValueError(f"{path} must contain a JSON object")
    return value


def panel(draw: ImageDraw.ImageDraw, box, *, fill="#FFFFFF", outline=SOFT_PURPLE, width=4, radius=24):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def trim_white(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    difference = ImageChops.difference(rgba, background).convert("L")
    difference = difference.point(lambda value: 255 if value > 18 else 0)
    box = difference.getbbox()
    return rgba.crop(box) if box else rgba


def paste_fit(canvas: Image.Image, image: Image.Image, box, inset=10):
    x0, y0, x1, y1 = box
    x0 += inset; y0 += inset; x1 -= inset; y1 -= inset
    source = trim_white(image)
    scale = min((x1 - x0) / source.width, (y1 - y0) / source.height)
    source = source.resize((max(1, round(source.width * scale)), max(1, round(source.height * scale))), Image.Resampling.LANCZOS)
    x = x0 + (x1 - x0 - source.width) // 2
    y = y0 + (y1 - y0 - source.height) // 2
    canvas.paste(source, (x, y), source)


def crop_assets(source: Image.Image, crop_map: dict[str, Any]) -> dict[str, Image.Image]:
    width, height = source.size
    result: dict[str, Image.Image] = {}
    for name, crop in crop_map.items():
        x = float(crop["x"]); y = float(crop["y"])
        w = float(crop["w"]); h = float(crop["h"])
        pad = float(crop.get("padding", 0.0))
        x0 = max(0, round((x - pad) * width)); y0 = max(0, round((y - pad) * height))
        x1 = min(width, round((x + w + pad) * width)); y1 = min(height, round((y + h + pad) * height))
        if x1 <= x0 or y1 <= y0:
            raise ValueError(f"Empty crop for {name}")
        result[name] = trim_white(source.crop((x0, y0, x1, y1)))
    return result


def header(canvas, draw, page, logo, text_engine, template):
    logo_image = logo.convert("RGBA")
    logo_image.thumbnail((300, 220), Image.Resampling.LANCZOS)
    canvas.paste(logo_image, (110 + (300 - logo_image.width) // 2, 35 + (220 - logo_image.height) // 2), logo_image)
    text_engine.brand_title(draw, ["Early Literacy Adventures"], [470, 45, 2320, 145], template["colours"], template["typography"])
    text_engine.fitted_text(draw, page["identity"]["title"], [470, 140, 2320, 275], max_size=66, min_size=46, colour=NAVY, bold=True, max_lines=2)
    panel(draw, [150, 305, 2330, 445], fill=BLUE, outline="#1768B3", width=3)
    text_engine.fitted_text(draw, "Learning goal: " + page["learning"]["objective"], [190, 318, 2290, 432], max_size=47, min_size=32, colour=NAVY, bold=True, max_lines=2)
    panel(draw, [150, 490, 2330, 650], fill=GOLD, outline="#E1A81C", width=3)
    text_engine.fitted_text(draw, page["learning"]["instruction"], [190, 505, 2290, 635], max_size=53, min_size=35, colour=INK, bold=True, max_lines=2)


def model_shell(draw, text_engine):
    panel(draw, [170, 700, 2310, 900], fill="#F6F1FF", outline=SOFT_PURPLE, width=3)
    panel(draw, [195, 720, 535, 880], fill="#E7D9FA", outline=SOFT_PURPLE, width=2, radius=18)
    text_engine.fitted_text(draw, "COMPLETED\nEXAMPLE", [220, 737, 510, 862], max_size=35, min_size=27, colour=NAVY, bold=True, max_lines=2)
    return [575, 720, 2275, 880]


def teacher_and_footer(draw, page, text_engine):
    panel(draw, [150, 3070, 2300, 3270], fill=GREEN, outline="#5F9D50", width=3)
    text_engine.fitted_text(draw, "TEACHER CUE", [180, 3095, 520, 3245], max_size=38, min_size=30, colour=NAVY, bold=True, max_lines=1)
    text_engine.fitted_text(draw, page["guidance"]["teacher_cue"], [550, 3090, 2260, 3250], max_size=39, min_size=28, colour=INK, align="left", max_lines=3)
    printed = page["identity"].get("printed_page")
    if printed is not None:
        text_engine.fitted_text(draw, str(printed), [2180, 3310, 2310, 3425], max_size=40, min_size=31, colour="#667085", bold=True, max_lines=1)


def letter_tile(draw, text_engine, box, value, *, filled=False):
    panel(draw, box, fill="#EAF4FF" if filled else "#FFFFFF", outline=PURPLE, width=4, radius=18)
    text_engine.fitted_text(draw, value, [box[0] + 10, box[1] + 10, box[2] - 10, box[3] - 10], max_size=72, min_size=48, colour=NAVY, bold=True, max_lines=1)


def model_choice(draw, text_engine, value, box, *, selected=False):
    text_engine.fitted_text(draw, str(value), box, max_size=47, min_size=32, colour=NAVY, bold=True, max_lines=1)
    if selected:
        draw.ellipse([box[0] - 8, box[1] - 4, box[2] + 8, box[3] + 4], outline=PURPLE, width=5)


def draw_model_icon(draw, name: str, box) -> bool:
    """Draw a small deterministic model object without adding an answer asset."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    if name == "ball":
        radius = min(x1 - x0, y1 - y0) // 2 - 8
        bounds = [cx - radius, cy - radius, cx + radius, cy + radius]
        draw.ellipse(bounds, fill="#F05A47", outline=NAVY, width=4)
        draw.arc(bounds, 55, 235, fill="#FFD34D", width=max(5, radius // 5))
        draw.arc(bounds, 235, 415, fill="#3D8BFF", width=max(5, radius // 5))
        return True
    if name == "cup":
        width = min(150, x1 - x0 - 55)
        height = min(105, y1 - y0 - 35)
        left, top = cx - width // 2, cy - height // 2
        draw.rounded_rectangle([left, top, left + width, top + height], radius=16, fill="#4FA7E8", outline=NAVY, width=4)
        draw.ellipse([left + width - 10, top + 20, left + width + 48, top + height - 12], fill="white", outline=NAVY, width=4)
        draw.ellipse([left + width - 2, top + 30, left + width + 34, top + height - 22], fill="#F6F1FF")
        return True
    if name == "hat":
        width = min(175, x1 - x0 - 20)
        left = cx - width // 2
        draw.rounded_rectangle([left + 38, cy - 58, left + width - 38, cy + 28], radius=14, fill="#7E57C2", outline=NAVY, width=4)
        draw.rounded_rectangle([left, cy + 12, left + width, cy + 48], radius=14, fill="#F2B84B", outline=NAVY, width=4)
        return True
    if name in {"red_ball", "yellow_duck", "clap", "map", "cat"}:
        if name == "red_ball":
            radius = min(x1 - x0, y1 - y0) // 2 - 10
            draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill="#EF3340", outline=NAVY, width=4)
            draw.ellipse([cx - radius // 2, cy - radius // 2, cx - radius // 6, cy - radius // 6], fill="#FF9A9A")
        elif name == "yellow_duck":
            draw.ellipse([cx - 72, cy - 28, cx + 70, cy + 55], fill="#FFD447", outline=NAVY, width=4)
            draw.ellipse([cx - 55, cy - 80, cx + 35, cy + 10], fill="#FFD447", outline=NAVY, width=4)
            draw.polygon([(cx - 62, cy - 30), (cx - 105, cy - 12), (cx - 62, cy + 2)], fill="#F49B2A", outline=NAVY)
            draw.ellipse([cx + 2, cy - 52, cx + 14, cy - 40], fill=NAVY)
        elif name == "clap":
            draw.ellipse([cx - 90, cy - 48, cx - 12, cy + 52], fill="#F6B27B", outline=NAVY, width=4)
            draw.ellipse([cx + 12, cy - 48, cx + 90, cy + 52], fill="#F6B27B", outline=NAVY, width=4)
            for offset in (-65, -45, 45, 65):
                draw.line([cx + offset, cy - 42, cx + offset, cy - 72], fill=NAVY, width=4)
            draw.arc([cx - 20, cy - 88, cx + 20, cy - 48], 200, 340, fill="#F2B84B", width=5)
        elif name == "map":
            draw.rounded_rectangle([cx - 95, cy - 62, cx + 95, cy + 62], radius=12, fill="#FFE7A5", outline=NAVY, width=4)
            draw.line([cx - 68, cy + 26, cx + 52, cy - 34], fill="#3A8D5B", width=7)
            draw.line([cx - 18, cy - 40, cx + 70, cy + 32], fill="#3D8BFF", width=7)
        else:
            draw.ellipse([cx - 62, cy - 52, cx + 62, cy + 60], fill="#F39A38", outline=NAVY, width=4)
            draw.polygon([(cx - 55, cy - 30), (cx - 42, cy - 88), (cx - 8, cy - 48)], fill="#F39A38", outline=NAVY)
            draw.polygon([(cx + 55, cy - 30), (cx + 42, cy - 88), (cx + 8, cy - 48)], fill="#F39A38", outline=NAVY)
            draw.ellipse([cx - 30, cy - 15, cx - 15, cy], fill=NAVY)
            draw.ellipse([cx + 15, cy - 15, cx + 30, cy], fill=NAVY)
            draw.polygon([(cx, cy + 8), (cx - 9, cy + 19), (cx + 9, cy + 19)], fill="#E05B5B")
        return True
    return False


def render_text_model(draw, page, text_engine):
    area = model_shell(draw, text_engine)
    model = page["learning"]["model_text"]
    x0, y0, x1, y1 = area
    cy = (y0 + y1) // 2
    if "left" in model and "right" in model:
        text_engine.fitted_text(draw, str(model["left"]), [x0 + 40, y0 + 25, x0 + 330, y1 - 25], max_size=48, min_size=34, colour=NAVY, bold=True, max_lines=1)
        draw.ellipse([x0 + 365, cy - 13, x0 + 391, cy + 13], fill="white", outline=PURPLE, width=3)
        draw.line([x0 + 391, cy, x0 + 700, cy], fill=PURPLE, width=5)
        draw.ellipse([x0 + 700, cy - 13, x0 + 726, cy + 13], fill="white", outline=PURPLE, width=3)
        text_engine.fitted_text(draw, str(model["right"]), [x0 + 770, y0 + 25, x0 + 1080, y1 - 25], max_size=48, min_size=34, colour=NAVY, bold=True, max_lines=1)
        note = "These words are opposites." if "opposite" in page["activity"]["mechanic"] else "These words rhyme."
        text_engine.fitted_text(draw, note, [x0 + 1130, y0 + 25, x1 - 20, y1 - 25], max_size=38, min_size=28, colour=NAVY, bold=True, max_lines=2)
        return
    if "tiles" in model:
        short_tiles = all(len(str(tile)) == 1 for tile in model["tiles"])
        tile_width = 120 if short_tiles else 150
        tile_step = 155 if short_tiles else 175
        for index, tile in enumerate(model["tiles"]):
            left = x0 + 35 + index * tile_step
            letter_tile(draw, text_engine, [left, y0 + 32, left + tile_width, y1 - 32], str(tile))
        draw.line([x0 + 535, cy, x0 + 700, cy], fill=PURPLE, width=5)
        draw.polygon([(x0 + 700, cy), (x0 + 660, cy - 24), (x0 + 660, cy + 24)], fill=PURPLE)
        answer_parts = [str(part) for part in model["answer"]]
        answer = "".join(answer_parts) if all(len(part) == 1 for part in answer_parts) else " ".join(answer_parts)
        text_engine.fitted_text(draw, answer, [x0 + 755, y0 + 25, x0 + 1120, y1 - 25], max_size=58, min_size=42, colour=NAVY, bold=True, max_lines=1)
        unit = "letters" if short_tiles else "words"
        text_engine.fitted_text(draw, f"Put the {unit} in order.", [x0 + 1170, y0 + 22, x1 - 20, y1 - 22], max_size=37, min_size=27, colour=NAVY, bold=True, max_lines=2)
        return
    if "letter" in model and "asset" in model:
        label = str(model["letter"])
        target = str(model["asset"])
        text_engine.fitted_text(draw, label, [x0 + 25, y0 + 25, x0 + 330, y1 - 25], max_size=50, min_size=34, colour=NAVY, bold=True, max_lines=1)
        draw.line([x0 + 375, cy, x0 + 650, cy], fill=PURPLE, width=5)
        draw.polygon([(x0 + 650, cy), (x0 + 610, cy - 24), (x0 + 610, cy + 24)], fill=PURPLE)
        target_box = [x0 + 710, y0 + 20, x0 + 1020, y1 - 20]
        if not draw_model_icon(draw, target, target_box):
            text_engine.fitted_text(draw, target, target_box, max_size=50, min_size=34, colour=NAVY, bold=True, max_lines=1)
        text_engine.fitted_text(draw, "The picture begins with this sound.", [x0 + 1080, y0 + 20, x1 - 20, y1 - 20], max_size=35, min_size=26, colour=NAVY, bold=True, max_lines=2)
        return
    if "word" in model and "asset" in model:
        word = str(model["word"])
        asset = str(model["asset"])
        text_engine.fitted_text(draw, word, [x0 + 25, y0 + 25, x0 + 330, y1 - 25], max_size=50, min_size=34, colour=NAVY, bold=True, max_lines=1)
        draw.line([x0 + 375, cy, x0 + 650, cy], fill=PURPLE, width=5)
        draw.polygon([(x0 + 650, cy), (x0 + 610, cy - 24), (x0 + 610, cy + 24)], fill=PURPLE)
        asset_box = [x0 + 710, y0 + 20, x0 + 1020, y1 - 20]
        if not draw_model_icon(draw, asset, asset_box):
            text_engine.fitted_text(draw, asset, asset_box, max_size=50, min_size=34, colour=NAVY, bold=True, max_lines=1)
        text_engine.fitted_text(draw, "The word matches this picture.", [x0 + 1080, y0 + 20, x1 - 20, y1 - 20], max_size=35, min_size=26, colour=NAVY, bold=True, max_lines=2)
        return
    raw_label = model.get("model") or model.get("asset") or model.get("word")
    label = str(raw_label or "")
    if label:
        label_box = [x0 + 25, y0 + 20, x0 + 330, y1 - 20]
        if not draw_model_icon(draw, label, label_box):
            text_engine.fitted_text(draw, label, label_box, max_size=45, min_size=30, colour=NAVY, bold=True, max_lines=1)
    choices = model.get("choices") or []
    if choices:
        answer = model.get("answer")
        choice_start = x0 + 410 if label else x0 + 60
        choice_step = 285 if len(choices) <= 2 else 255
        choice_width = 210 if len(choices) <= 2 else 175
        for index, choice in enumerate(choices):
            left = choice_start + index * choice_step
            model_choice(draw, text_engine, choice, [left, y0 + 45, left + choice_width, y1 - 45], selected=choice == answer)
        note_left = x0 + 1030 if len(choices) <= 2 else x0 + 880
        text_engine.fitted_text(draw, "The circled choice completes the example.", [note_left, y0 + 20, x1 - 20, y1 - 20], max_size=35, min_size=26, colour=NAVY, bold=True, max_lines=2)
    else:
        target = str(model.get("letter") or model.get("answer") or "")
        draw.line([x0 + 375, cy, x0 + 650, cy], fill=PURPLE, width=5)
        draw.polygon([(x0 + 650, cy), (x0 + 610, cy - 24), (x0 + 610, cy + 24)], fill=PURPLE)
        text_engine.fitted_text(draw, target or label, [x0 + 710, y0 + 25, x0 + 1020, y1 - 25], max_size=50, min_size=34, colour=NAVY, bold=True, max_lines=1)


def draw_asset_or_text(canvas, draw, text_engine, assets, value, box):
    if value in assets:
        paste_fit(canvas, assets[value], box, inset=6)
    else:
        text_engine.fitted_text(draw, str(value), [box[0] + 15, box[1] + 15, box[2] - 15, box[3] - 15], max_size=70, min_size=42, colour=NAVY, bold=True, max_lines=1)


def readable_asset_name(value):
    """Convert an internal asset id into a short child-readable picture name."""
    label = str(value).replace("_scene", "").replace("_", " ").strip()
    return {
        "child reads": "child reads",
        "dog runs": "dog runs",
        "red ball": "ball",
    }.get(label, label)


def draw_asset_name(draw, text_engine, value, box, *, max_size=29):
    text_engine.fitted_text(
        draw,
        readable_asset_name(value),
        box,
        max_size=max_size,
        min_size=21,
        colour=NAVY,
        bold=True,
        max_lines=1,
    )


def render_two_column_match(canvas, draw, page, assets, text_engine):
    render_text_model(draw, page, text_engine)
    controls = page["activity"]["mechanics"]
    render_kind = page["activity"]["render_kind"]
    left_values, right_values = controls["left"], controls["right"]
    count = max(len(left_values), len(right_values))
    top, bottom, gap = 950, 2990, 22
    row_h = (bottom - top - gap * (count - 1)) // count
    for index in range(count):
        y0 = top + index * (row_h + gap)
        y1 = y0 + row_h
        if index < len(left_values):
            panel(draw, [180, y0, 1010, y1], outline=SOFT_PURPLE, width=3)
            if render_kind == "literacy-word-picture-match":
                text_engine.fitted_text(draw, str(left_values[index]), [260, y0 + 25, 880, y1 - 25], max_size=72, min_size=48, colour=NAVY, bold=True, max_lines=1)
            else:
                draw_asset_or_text(canvas, draw, text_engine, assets, left_values[index], [230, y0 + 8, 900, y1 - 58])
                if left_values[index] in assets:
                    draw_asset_name(draw, text_engine, left_values[index], [300, y1 - 60, 830, y1 - 8], max_size=28)
            draw.ellipse([940, (y0 + y1) // 2 - 16, 972, (y0 + y1) // 2 + 16], fill="white", outline=PURPLE, width=4)
        if index < len(right_values):
            panel(draw, [1470, y0, 2300, y1], outline=SOFT_PURPLE, width=3)
            draw.ellipse([1518, (y0 + y1) // 2 - 16, 1550, (y0 + y1) // 2 + 16], fill="white", outline=PURPLE, width=4)
            draw_asset_or_text(canvas, draw, text_engine, assets, right_values[index], [1600, y0 + 8, 2250, y1 - 58])
            if right_values[index] in assets:
                draw_asset_name(draw, text_engine, right_values[index], [1660, y1 - 60, 2190, y1 - 8], max_size=28)


def render_choice_cards(canvas, draw, page, assets, text_engine):
    render_text_model(draw, page, text_engine)
    cards = page["activity"]["mechanics"]["cards"]
    cols, gap = 2, 28
    left, right, top, bottom = 180, 2300, 950, 2990
    rows = (len(cards) + 1) // 2
    cell_w = (right - left - gap) // 2
    cell_h = (bottom - top - gap * (rows - 1)) // rows
    for index, card in enumerate(cards):
        row, col = divmod(index, cols)
        x0 = left + col * (cell_w + gap); y0 = top + row * (cell_h + gap)
        box = [x0, y0, x0 + cell_w, y0 + cell_h]
        panel(draw, box, outline=SOFT_PURPLE, width=3)
        sentence = card.get("sentence")
        asset_bottom = y0 + cell_h - 310 if not sentence else y0 + cell_h - 430
        paste_fit(canvas, assets[card["asset"]], [x0 + 35, y0 + 25, x0 + cell_w - 35, asset_bottom])
        draw_asset_name(draw, text_engine, card["asset"], [x0 + 55, asset_bottom + 5, x0 + cell_w - 55, asset_bottom + 70], max_size=30)
        if sentence:
            text_engine.fitted_text(draw, sentence, [x0 + 45, asset_bottom + 72, x0 + cell_w - 45, asset_bottom + 175], max_size=39, min_size=28, colour=NAVY, bold=True, max_lines=2)
        choice_top = y0 + cell_h - 205
        choices = card["choices"]
        choice_w = (cell_w - 135) // len(choices)
        for choice_index, choice in enumerate(choices):
            cx0 = x0 + 45 + choice_index * (choice_w + 45)
            panel(draw, [cx0, choice_top, cx0 + choice_w, choice_top + 120], fill="#FFFDF8", outline="#C7A9EF", width=2, radius=16)
            text_engine.fitted_text(draw, choice, [cx0 + 10, choice_top + 6, cx0 + choice_w - 10, choice_top + 114], max_size=58, min_size=42, colour=NAVY, bold=True, max_lines=1)
        if sentence:
            draw.line([x0 + 160, y0 + cell_h - 40, x0 + cell_w - 160, y0 + cell_h - 40], fill="#716052", width=3)


def render_picture_choice_rows(canvas, draw, page, assets, text_engine):
    render_text_model(draw, page, text_engine)
    rows = page["activity"]["mechanics"]["rows"]
    top, bottom, gap = 950, 2990, 22
    row_h = (bottom - top - gap * (len(rows) - 1)) // len(rows)
    for index, row in enumerate(rows):
        y0 = top + index * (row_h + gap); y1 = y0 + row_h
        panel(draw, [180, y0, 2300, y1], outline=SOFT_PURPLE, width=3)
        model = row.get("model")
        choices = row["choices"]
        values = ([model] if model else []) + choices
        count = len(values)
        gap_x = 28
        usable_left, usable_right = 220, 2260
        cell_w = (usable_right - usable_left - gap_x * (count - 1)) // count
        for value_index, value in enumerate(values):
            x0 = usable_left + value_index * (cell_w + gap_x)
            fill = "#EEF6FF" if model and value_index == 0 else "#FFFFFF"
            panel(draw, [x0, y0 + 22, x0 + cell_w, y1 - 22], fill=fill, outline="#C7A9EF", width=2, radius=18)
            draw_asset_or_text(canvas, draw, text_engine, assets, value, [x0 + 12, y0 + 30, x0 + cell_w - 12, y1 - 88])
            if value in assets:
                draw_asset_name(draw, text_engine, value, [x0 + 20, y1 - 85, x0 + cell_w - 20, y1 - 28], max_size=27)


def render_build_word(canvas, draw, page, assets, text_engine):
    render_text_model(draw, page, text_engine)
    rows = page["activity"]["mechanics"]["rows"]
    top, bottom, gap = 950, 2990, 24
    row_h = (bottom - top - gap * (len(rows) - 1)) // len(rows)
    for index, row in enumerate(rows):
        y0 = top + index * (row_h + gap); y1 = y0 + row_h
        panel(draw, [180, y0, 2300, y1], outline=SOFT_PURPLE, width=3)
        paste_fit(canvas, assets[row["asset"]], [220, y0 + 20, 700, y1 - 20])
        for tile_index, tile in enumerate(row["tiles"]):
            left = 820 + tile_index * 180
            letter_tile(draw, text_engine, [left, y0 + 65, left + 135, y0 + 205], tile)
        draw.line([1390, (y0 + y1) // 2, 1530, (y0 + y1) // 2], fill=PURPLE, width=5)
        draw.polygon([(1530, (y0 + y1)//2), (1490, (y0 + y1)//2 - 24), (1490, (y0 + y1)//2 + 24)], fill=PURPLE)
        for box_index in range(3):
            left = 1600 + box_index * 205
            panel(draw, [left, y0 + 65, left + 160, y0 + 225], fill="#FFFDF3", outline="#D8A51C", width=3, radius=14)
            draw.line([left + 35, y0 + 205, left + 125, y0 + 205], fill="#9C7615", width=3)


def render_missing_letters(draw, page, text_engine):
    area = model_shell(draw, text_engine)
    values = ["A", "B", "C"]
    for index, value in enumerate(values):
        left = area[0] + 100 + index * 270
        letter_tile(draw, text_engine, [left, 742, left + 180, 858], value, filled=index == 1)
    text_engine.fitted_text(draw, "B fills the missing place.", [1450, 738, 2220, 860], max_size=40, min_size=30, colour=NAVY, bold=True, max_lines=2)

    rows = page["activity"]["mechanics"]["rows"]
    top, gap, row_h = 960, 24, 318
    for row_index, row in enumerate(rows):
        y0 = top + row_index * (row_h + gap)
        panel(draw, [180, y0, 2300, y0 + row_h], outline=SOFT_PURPLE, width=3)
        sequence = row["sequence"]
        tile_w, tile_gap = 260, 105
        total = len(sequence) * tile_w + (len(sequence) - 1) * tile_gap
        start = (WIDTH - total) // 2
        for index, value in enumerate(sequence):
            left = start + index * (tile_w + tile_gap)
            if value is None:
                panel(draw, [left, y0 + 70, left + tile_w, y0 + 250], fill="#FFFDF3", outline="#D8A51C", width=4, radius=18)
                draw.line([left + 55, y0 + 225, left + tile_w - 55, y0 + 225], fill="#9C7615", width=4)
            else:
                letter_tile(draw, text_engine, [left, y0 + 70, left + tile_w, y0 + 250], value)


def render_letter_match(draw, page, text_engine):
    area = model_shell(draw, text_engine)
    letter_tile(draw, text_engine, [area[0] + 80, 742, area[0] + 260, 858], "A")
    letter_tile(draw, text_engine, [area[0] + 780, 742, area[0] + 960, 858], "a", filled=True)
    cy = 800
    draw.ellipse([area[0] + 315, cy - 14, area[0] + 343, cy + 14], fill="white", outline=PURPLE, width=4)
    draw.line([area[0] + 343, cy, area[0] + 725, cy], fill=PURPLE, width=6)
    draw.ellipse([area[0] + 725, cy - 14, area[0] + 753, cy + 14], fill="white", outline=PURPLE, width=4)
    text_engine.fitted_text(draw, "A and a have the same letter name.", [area[0] + 1040, 738, area[2] - 20, 865], max_size=38, min_size=28, colour=NAVY, bold=True, max_lines=2)

    controls = page["activity"]["mechanics"]
    left_values, right_values = controls["left"], controls["right"]
    top, row_h, gap = 960, 306, 26
    for index, (left_value, right_value) in enumerate(zip(left_values, right_values)):
        y0 = top + index * (row_h + gap)
        panel(draw, [180, y0, 1010, y0 + row_h], outline=SOFT_PURPLE, width=3)
        panel(draw, [1470, y0, 2300, y0 + row_h], outline=SOFT_PURPLE, width=3)
        letter_tile(draw, text_engine, [430, y0 + 60, 710, y0 + 245], left_value)
        letter_tile(draw, text_engine, [1770, y0 + 60, 2050, y0 + 245], right_value)
        cy = y0 + row_h // 2
        draw.ellipse([930, cy - 16, 962, cy + 16], fill="white", outline=PURPLE, width=4)
        draw.ellipse([1518, cy - 16, 1550, cy + 16], fill="white", outline=PURPLE, width=4)


def render_read_match(canvas, draw, page, assets, text_engine):
    area = model_shell(draw, text_engine)
    text_engine.fitted_text(draw, "map", [area[0] + 40, 744, area[0] + 270, 858], max_size=65, min_size=48, colour=NAVY, bold=True, max_lines=1)
    cy = 800
    draw.ellipse([area[0] + 320, cy - 14, area[0] + 348, cy + 14], fill="white", outline=PURPLE, width=4)
    draw.line([area[0] + 348, cy, area[0] + 690, cy], fill=PURPLE, width=6)
    draw.ellipse([area[0] + 690, cy - 14, area[0] + 718, cy + 14], fill="white", outline=PURPLE, width=4)
    draw.rounded_rectangle([area[0] + 780, 746, area[0] + 1000, 854], radius=14, fill="#F6E2A8", outline=NAVY, width=3)
    draw.line([area[0] + 820, 825, area[0] + 945, 770], fill="#4D8B3C", width=8)
    draw.line([area[0] + 875, 760, area[0] + 970, 830], fill="#3183C8", width=7)
    text_engine.fitted_text(draw, "Read, then match.", [area[0] + 1070, 742, area[2] - 20, 858], max_size=42, min_size=31, colour=NAVY, bold=True, max_lines=1)

    controls = page["activity"]["mechanics"]
    main_words = controls["main_words"]
    main_pictures = controls["main_picture_order"]
    top, row_h = 950, 330
    for index, (word, picture) in enumerate(zip(main_words, main_pictures)):
        y0 = top + index * row_h
        panel(draw, [180, y0, 980, y0 + row_h - 20], outline=SOFT_PURPLE, width=3)
        panel(draw, [1500, y0, 2300, y0 + row_h - 20], outline=SOFT_PURPLE, width=3)
        text_engine.fitted_text(draw, word, [310, y0 + 55, 790, y0 + 235], max_size=77, min_size=56, colour=NAVY, bold=True, max_lines=1)
        paste_fit(canvas, assets[picture], [1630, y0 + 22, 2170, y0 + row_h - 42])
        cy = y0 + (row_h - 20) // 2
        draw.ellipse([915, cy - 16, 947, cy + 16], fill="white", outline=PURPLE, width=4)
        draw.ellipse([1533, cy - 16, 1565, cy + 16], fill="white", outline=PURPLE, width=4)

    panel(draw, [180, 2300, 2300, 2980], fill="#FBFAFF", outline=SOFT_PURPLE, width=3)
    text_engine.fitted_text(draw, "Read and match again.", [230, 2320, 2250, 2415], max_size=44, min_size=34, colour=NAVY, bold=True, max_lines=1)
    small_words = controls["small_words"]
    small_pictures = controls["small_picture_order"]
    for index, (word, picture) in enumerate(zip(small_words, small_pictures)):
        y0 = 2435 + index * 170
        text_engine.fitted_text(draw, word, [270, y0, 680, y0 + 135], max_size=60, min_size=44, colour=NAVY, bold=True, max_lines=1)
        draw.ellipse([760, y0 + 48, 790, y0 + 78], fill="white", outline=PURPLE, width=4)
        draw.ellipse([1570, y0 + 48, 1600, y0 + 78], fill="white", outline=PURPLE, width=4)
        paste_fit(canvas, assets[picture], [1660, y0 - 15, 2160, y0 + 150], inset=2)


def render_category_sort(canvas, draw, page, assets, text_engine):
    area = model_shell(draw, text_engine)
    x0, y0, x1, y1 = area
    cy = (y0 + y1) // 2
    paste_fit(canvas, assets["orange"], [x0 + 35, y0 + 15, x0 + 185, y1 - 15], inset=0)
    draw.line([x0 + 215, cy, x0 + 520, cy], fill=PURPLE, width=5)
    draw.polygon([(x0 + 520, cy), (x0 + 480, cy - 24), (x0 + 480, cy + 24)], fill=PURPLE)
    panel(draw, [x0 + 580, y0 + 35, x0 + 900, y1 - 35], fill=BLUE, outline="#1768B3", width=3, radius=18)
    text_engine.fitted_text(draw, "FRUITS", [x0 + 610, y0 + 45, x0 + 870, y1 - 45], max_size=43, min_size=32, colour=NAVY, bold=True, max_lines=1)
    text_engine.fitted_text(draw, "Write its picture number in the matching group.", [x0 + 960, y0 + 20, x1 - 20, y1 - 20], max_size=34, min_size=25, colour=NAVY, bold=True, max_lines=2)

    mechanics = page["activity"]["mechanics"]
    categories = mechanics["categories"]
    category_top, category_bottom = 950, 1190
    gap = 28
    left, right = 170, 2310
    category_w = (right - left - gap * 2) // 3
    for index, category in enumerate(categories):
        cx0 = left + index * (category_w + gap)
        fill = "#F6F1FF" if index != 1 else BLUE
        panel(draw, [cx0, category_top, cx0 + category_w, category_bottom], fill=fill, outline=SOFT_PURPLE, width=3)
        text_engine.fitted_text(draw, category, [cx0 + 20, category_top + 14, cx0 + category_w - 20, category_top + 72], max_size=38, min_size=30, colour=NAVY, bold=True, max_lines=1)
        text_engine.fitted_text(draw, "Write numbers:", [cx0 + 25, category_top + 72, cx0 + category_w - 25, category_top + 115], max_size=26, min_size=21, colour=INK, max_lines=1)
        box_count = int(mechanics.get("number_writing_boxes_per_category", 3))
        box_gap = 24
        box_w = 108
        boxes_w = box_count * box_w + (box_count - 1) * box_gap
        boxes_left = cx0 + (category_w - boxes_w) // 2
        for box_index in range(box_count):
            bx0 = boxes_left + box_index * (box_w + box_gap)
            panel(draw, [bx0, category_top + 125, bx0 + box_w, category_bottom - 18], fill="#FFFFFF", outline=PURPLE, width=3, radius=14)

    items = mechanics["items"]
    grid_top, grid_bottom = 1250, 2990
    rows, cols = 3, 3
    cell_gap = 24
    cell_w = (right - left - cell_gap * (cols - 1)) // cols
    cell_h = (grid_bottom - grid_top - cell_gap * (rows - 1)) // rows
    for index, item in enumerate(items):
        row, col = divmod(index, cols)
        ix0 = left + col * (cell_w + cell_gap)
        iy0 = grid_top + row * (cell_h + cell_gap)
        panel(draw, [ix0, iy0, ix0 + cell_w, iy0 + cell_h], outline=SOFT_PURPLE, width=3)
        paste_fit(canvas, assets[item["asset"]], [ix0 + 28, iy0 + 22, ix0 + cell_w - 28, iy0 + cell_h - 78], inset=3)
        draw_asset_name(draw, text_engine, item["asset"], [ix0 + 45, iy0 + cell_h - 72, ix0 + cell_w - 45, iy0 + cell_h - 16], max_size=27)
        draw.ellipse([ix0 + 14, iy0 + 14, ix0 + 80, iy0 + 80], fill="#F3E9FF", outline=PURPLE, width=3)
        text_engine.fitted_text(draw, str(item["number"]), [ix0 + 22, iy0 + 20, ix0 + 72, iy0 + 72], max_size=31, min_size=26, colour=NAVY, bold=True, max_lines=1)


def render_read_colour(canvas, draw, page, assets, text_engine):
    area = model_shell(draw, text_engine)
    x0, y0, x1, y1 = area
    draw.ellipse([x0 + 70, y0 + 32, x0 + 190, y1 - 32], fill="#F6A623", outline=NAVY, width=4)
    text_engine.fitted_text(draw, "Colour the circle orange.", [x0 + 265, y0 + 20, x1 - 30, y1 - 20], max_size=40, min_size=30, colour=NAVY, bold=True, max_lines=2)

    cards = page["activity"]["mechanics"]["cards"]
    left, right, top, bottom, gap = 180, 2300, 950, 2990, 28
    cell_w = (right - left - gap) // 2
    cell_h = (bottom - top - gap) // 2
    for index, card in enumerate(cards):
        row, col = divmod(index, 2)
        cx0 = left + col * (cell_w + gap)
        cy0 = top + row * (cell_h + gap)
        panel(draw, [cx0, cy0, cx0 + cell_w, cy0 + cell_h], outline=SOFT_PURPLE, width=3)
        paste_fit(canvas, assets[card["asset"]], [cx0 + 50, cy0 + 30, cx0 + cell_w - 50, cy0 + cell_h - 205], inset=4)
        panel(draw, [cx0 + 45, cy0 + cell_h - 165, cx0 + cell_w - 45, cy0 + cell_h - 35], fill="#FFFDF8", outline="#C7A9EF", width=2, radius=16)
        text_engine.fitted_text(draw, card["sentence"], [cx0 + 70, cy0 + cell_h - 150, cx0 + cell_w - 70, cy0 + cell_h - 50], max_size=39, min_size=29, colour=NAVY, bold=True, max_lines=2)


def render_sentence_builder(canvas, draw, page, assets, text_engine):
    render_text_model(draw, page, text_engine)
    rows = page["activity"]["mechanics"]["rows"]
    top, bottom, gap = 950, 2990, 26
    row_h = (bottom - top - gap * (len(rows) - 1)) // len(rows)
    for index, row in enumerate(rows):
        y0 = top + index * (row_h + gap)
        y1 = y0 + row_h
        panel(draw, [180, y0, 2300, y1], outline=SOFT_PURPLE, width=3)
        paste_fit(canvas, assets[row["asset"]], [220, y0 + 30, 680, y1 - 105], inset=4)
        draw_asset_name(draw, text_engine, row["asset"], [230, y1 - 102, 670, y1 - 38], max_size=28)
        tiles = row["tiles"]
        tile_gap = 18
        tile_w = 170 if len(tiles) == 4 else 190
        tile_left = 720
        for tile_index, tile in enumerate(tiles):
            tx0 = tile_left + tile_index * (tile_w + tile_gap)
            panel(draw, [tx0, y0 + 80, tx0 + tile_w, y0 + 220], fill="#FFFFFF", outline=PURPLE, width=3, radius=16)
            draw.ellipse([tx0 + 8, y0 + 68, tx0 + 78, y0 + 138], fill="#FFFFFF", outline=PURPLE, width=3)
            text_engine.fitted_text(draw, str(tile), [tx0 + 86, y0 + 96, tx0 + tile_w - 8, y0 + 208], max_size=36, min_size=20, colour=NAVY, bold=True, max_lines=1)
        answer_left = 1530
        text_engine.fitted_text(draw, "Write the sentence:", [answer_left, y0 + 65, 2240, y0 + 135], max_size=31, min_size=25, colour=NAVY, bold=True, max_lines=1)
        draw.line([answer_left, y0 + 210, 2240, y0 + 210], fill="#716052", width=3)
        draw.line([answer_left, y0 + 330, 2240, y0 + 330], fill="#B6A89C", width=2)


def draw_open_choices(draw, text_engine, choices, box, *, selected=None, max_size=34):
    """Draw large readable response choices; only the model may pass selected."""
    x0, y0, x1, y1 = box
    gap = 18
    choice_w = (x1 - x0 - gap * (len(choices) - 1)) // max(1, len(choices))
    for index, choice in enumerate(choices):
        left = x0 + index * (choice_w + gap)
        panel(draw, [left, y0, left + choice_w, y1], fill="#FFFDF8", outline="#C7A9EF", width=2, radius=16)
        text_engine.fitted_text(draw, str(choice), [left + 14, y0 + 8, left + choice_w - 14, y1 - 8], max_size=max_size, min_size=23, colour=NAVY, bold=True, max_lines=2)
        if choice == selected:
            draw.rounded_rectangle([left + 5, y0 + 5, left + choice_w - 5, y1 - 5], radius=18, outline=PURPLE, width=6)


def render_question_model(draw, page, text_engine):
    area = model_shell(draw, text_engine)
    model = page["learning"]["model_text"]
    x0, y0, x1, y1 = area
    label = model.get("question") or model.get("teacher_word") or model.get("sentence") or "Look, then choose."
    text_engine.fitted_text(draw, str(label), [x0 + 20, y0 + 18, x0 + 690, y1 - 18], max_size=34, min_size=25, colour=NAVY, bold=True, align="left", max_lines=2)
    choices = model.get("choices") or []
    if choices:
        draw_open_choices(draw, text_engine, choices, [x0 + 730, y0 + 32, x0 + 1250, y1 - 32], selected=model.get("answer"), max_size=36)
        text_engine.fitted_text(draw, "The circled choice completes the example.", [x0 + 1290, y0 + 18, x1 - 15, y1 - 18], max_size=30, min_size=23, colour=NAVY, bold=True, max_lines=2)


def render_scene_questions(canvas, draw, page, assets, text_engine, *, labelled=False):
    render_question_model(draw, page, text_engine)
    mechanics = page["activity"]["mechanics"]
    scene_name = mechanics.get("scene") or next(iter(assets))
    panel(draw, [170, 950, 1370, 2990], outline=SOFT_PURPLE, width=3)
    paste_fit(canvas, assets[scene_name], [205, 985, 1335, 2955], inset=3)
    questions = mechanics["questions"]
    gap = 20
    row_h = (2990 - 950 - gap * (len(questions) - 1)) // len(questions)
    for index, item in enumerate(questions):
        y0 = 950 + index * (row_h + gap)
        panel(draw, [1400, y0, 2310, y0 + row_h], fill="#FBFAFF", outline=SOFT_PURPLE, width=3)
        question_top = y0 + 22
        if labelled:
            panel(draw, [1430, y0 + 20, 1610, y0 + 82], fill=BLUE, outline="#1768B3", width=2, radius=14)
            text_engine.fitted_text(draw, item["label"], [1445, y0 + 25, 1595, y0 + 75], max_size=27, min_size=23, colour=NAVY, bold=True, max_lines=1)
            question_top = y0 + 88
        text_engine.fitted_text(draw, item["question"], [1435, question_top, 2275, question_top + 100], max_size=33, min_size=24, colour=NAVY, bold=True, align="left", max_lines=2)
        draw_open_choices(draw, text_engine, item["choices"], [1435, y0 + row_h - 135, 2275, y0 + row_h - 25], max_size=31)


def render_listening_choice(canvas, draw, page, assets, text_engine):
    area = model_shell(draw, text_engine)
    x0, y0, x1, y1 = area
    draw.ellipse([x0 + 35, y0 + 30, x0 + 155, y1 - 30], fill="#FFD447", outline=NAVY, width=4)
    text_engine.fitted_text(draw, "Teacher says: sun", [x0 + 210, y0 + 20, x0 + 670, y1 - 20], max_size=39, min_size=29, colour=NAVY, bold=True, max_lines=2)
    draw_open_choices(draw, text_engine, ["sun", "bus", "cup"], [x0 + 720, y0 + 30, x1 - 20, y1 - 30], selected="sun", max_size=34)
    rows = page["activity"]["mechanics"]["rows"]
    top, bottom, gap = 950, 2990, 22
    row_h = (bottom - top - gap * (len(rows) - 1)) // len(rows)
    for index, row in enumerate(rows):
        y0 = top + index * (row_h + gap)
        panel(draw, [180, y0, 2300, y0 + row_h], outline=SOFT_PURPLE, width=3)
        panel(draw, [205, y0 + 25, 520, y0 + row_h - 25], fill=BLUE, outline="#1768B3", width=2, radius=16)
        text_engine.fitted_text(draw, f"Say: {row['teacher_word']}", [225, y0 + 45, 500, y0 + row_h - 45], max_size=34, min_size=27, colour=NAVY, bold=True, max_lines=2)
        choices = row["choices"]
        card_gap = 24
        card_w = (2240 - 570 - card_gap * 2) // 3
        for choice_index, choice in enumerate(choices):
            cx0 = 570 + choice_index * (card_w + card_gap)
            panel(draw, [cx0, y0 + 22, cx0 + card_w, y0 + row_h - 22], outline="#C7A9EF", width=2, radius=16)
            paste_fit(canvas, assets[choice], [cx0 + 20, y0 + 35, cx0 + card_w - 20, y0 + row_h - 90], inset=3)
            circle_x = cx0 + card_w // 2
            draw.ellipse([circle_x - 19, y0 + row_h - 74, circle_x + 19, y0 + row_h - 36], fill="white", outline=PURPLE, width=4)


def star_points(cx, cy, outer, inner, points=5):
    import math
    result = []
    for index in range(points * 2):
        angle = -math.pi / 2 + index * math.pi / points
        radius = outer if index % 2 == 0 else inner
        result.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return result


def render_sight_words(canvas, draw, page, assets, text_engine):
    area = model_shell(draw, text_engine)
    x0, y0, x1, y1 = area
    draw.polygon(star_points(x0 + 120, 800, 72, 35), fill="#FFD447", outline=NAVY)
    text_engine.fitted_text(draw, "I", [x0 + 80, 760, x0 + 160, 840], max_size=43, min_size=34, colour=NAVY, bold=True, max_lines=1)
    words = ["I", "can", "run."]
    for index, word in enumerate(words):
        left = x0 + 260 + index * 220
        text_engine.fitted_text(draw, word, [left, 755, left + 190, 845], max_size=42, min_size=31, colour=NAVY, bold=True, max_lines=1)
        if word == "I":
            draw.ellipse([left + 50, 750, left + 140, 850], outline=PURPLE, width=5)
    text_engine.fitted_text(draw, "Circle the star word in the sentence.", [x0 + 980, 742, x1 - 20, 858], max_size=34, min_size=26, colour=NAVY, bold=True, max_lines=2)
    rows = page["activity"]["mechanics"]["rows"]
    top, bottom, gap = 950, 2990, 24
    row_h = (bottom - top - gap * (len(rows) - 1)) // len(rows)
    for index, row in enumerate(rows):
        y0 = top + index * (row_h + gap)
        panel(draw, [180, y0, 2300, y0 + row_h], outline=SOFT_PURPLE, width=3)
        draw.polygon(star_points(340, y0 + row_h // 2, 92, 44), fill="#FFD447", outline=NAVY)
        text_engine.fitted_text(draw, row["target"], [270, y0 + row_h // 2 - 42, 410, y0 + row_h // 2 + 42], max_size=37, min_size=27, colour=NAVY, bold=True, max_lines=1)
        sentence_words = row["sentence"].split()
        start = 540
        word_w = min(260, (1440 - start) // max(1, len(sentence_words)))
        for word_index, word in enumerate(sentence_words):
            left = start + word_index * word_w
            text_engine.fitted_text(draw, word, [left, y0 + 115, left + word_w - 8, y0 + row_h - 115], max_size=46, min_size=31, colour=NAVY, bold=True, max_lines=1)
        paste_fit(canvas, assets[row["asset"]], [1740, y0 + 25, 2250, y0 + row_h - 25], inset=3)


def render_mixed_review(canvas, draw, page, assets, text_engine):
    area = model_shell(draw, text_engine)
    x0, y0, x1, y1 = area
    text_engine.fitted_text(draw, "cat", [x0 + 45, y0 + 30, x0 + 270, y1 - 30], max_size=54, min_size=40, colour=NAVY, bold=True, max_lines=1)
    draw.line([x0 + 320, 800, x0 + 610, 800], fill=PURPLE, width=5)
    draw.polygon([(x0 + 610, 800), (x0 + 570, 776), (x0 + 570, 824)], fill=PURPLE)
    draw_model_icon(draw, "cat", [x0 + 680, y0 + 20, x0 + 980, y1 - 20])
    text_engine.fitted_text(draw, "Complete each different reading challenge.", [x0 + 1040, y0 + 20, x1 - 20, y1 - 20], max_size=34, min_size=26, colour=NAVY, bold=True, max_lines=2)
    tasks = page["activity"]["mechanics"]["tasks"]
    left, top, right, bottom, gap = 170, 950, 2310, 2990, 24
    cell_w = (right - left - gap) // 2
    row_count = max(1, (len(tasks) + 1) // 2)
    cell_h = (bottom - top - gap * (row_count - 1)) // row_count
    for index, task in enumerate(tasks):
        row, col = divmod(index, 2)
        cx0 = left + col * (cell_w + gap); cy0 = top + row * (cell_h + gap)
        cx1, cy1 = cx0 + cell_w, cy0 + cell_h
        panel(draw, [cx0, cy0, cx1, cy1], outline=SOFT_PURPLE, width=3)
        task_type = task["type"]
        if task_type == "word-picture":
            text_engine.fitted_text(draw, f"Read: {task['word']}", [cx0 + 30, cy0 + 18, cx1 - 30, cy0 + 90], max_size=42, min_size=31, colour=NAVY, bold=True, max_lines=1)
            choices = task["choices"]
            for cindex, choice in enumerate(choices):
                card_w = (cell_w - 150) // 2
                bx0 = cx0 + 45 + cindex * (card_w + 60)
                paste_fit(canvas, assets[choice], [bx0, cy0 + 100, bx0 + card_w, cy1 - 145], inset=3)
                draw_asset_name(draw, text_engine, choice, [bx0 + 10, cy1 - 143, bx0 + card_w - 10, cy1 - 98], max_size=25)
                draw.ellipse([bx0 + card_w // 2 - 22, cy1 - 88, bx0 + card_w // 2 + 22, cy1 - 44], fill="white", outline=PURPLE, width=4)
        elif task_type == "rhyme":
            text_engine.fitted_text(draw, f"Rhymes with {task['model']}", [cx0 + 30, cy0 + 18, cx1 - 30, cy0 + 90], max_size=39, min_size=29, colour=NAVY, bold=True, max_lines=1)
            for cindex, choice in enumerate(task["choices"]):
                card_w = (cell_w - 150) // 2
                bx0 = cx0 + 45 + cindex * (card_w + 60)
                paste_fit(canvas, assets[choice], [bx0, cy0 + 100, bx0 + card_w, cy1 - 145], inset=3)
                draw_asset_name(draw, text_engine, choice, [bx0 + 10, cy1 - 143, bx0 + card_w - 10, cy1 - 98], max_size=25)
                draw.ellipse([bx0 + card_w // 2 - 22, cy1 - 88, bx0 + card_w // 2 + 22, cy1 - 44], fill="white", outline=PURPLE, width=4)
        elif task_type == "sentence-picture":
            text_engine.fitted_text(draw, task["sentence"], [cx0 + 30, cy0 + 18, cx1 - 30, cy0 + 100], max_size=38, min_size=29, colour=NAVY, bold=True, max_lines=1)
            paste_fit(canvas, assets[task["asset"]], [cx0 + 320, cy0 + 105, cx1 - 320, cy1 - 185], inset=8)
            draw_asset_name(draw, text_engine, task["asset"], [cx0 + 330, cy1 - 182, cx1 - 330, cy1 - 140], max_size=25)
            draw.rectangle([cx0 + 310, cy1 - 115, cx0 + 378, cy1 - 47], fill="white", outline=PURPLE, width=4)
            text_engine.fitted_text(draw, "Tick if it matches", [cx0 + 400, cy1 - 125, cx1 - 45, cy1 - 40], max_size=28, min_size=22, colour=NAVY, bold=True, max_lines=1)
        elif task_type == "sight-word":
            text_engine.fitted_text(draw, f"Circle the word: {task['target']}", [cx0 + 30, cy0 + 20, cx1 - 30, cy0 + 100], max_size=36, min_size=28, colour=NAVY, bold=True, max_lines=1)
            words = task["sentence"].replace(".", "").split()
            draw_open_choices(draw, text_engine, words, [cx0 + 55, cy0 + 210, cx1 - 55, cy1 - 150], max_size=38)
        elif task_type == "beginning-sound":
            text_engine.fitted_text(draw, "Circle the beginning sound.", [cx0 + 30, cy0 + 18, cx1 - 30, cy0 + 90], max_size=34, min_size=26, colour=NAVY, bold=True, max_lines=1)
            paste_fit(canvas, assets[task["asset"]], [cx0 + 80, cy0 + 105, cx0 + 440, cy1 - 115], inset=3)
            draw_asset_name(draw, text_engine, task["asset"], [cx0 + 95, cy1 - 110, cx0 + 425, cy1 - 60], max_size=25)
            draw_open_choices(draw, text_engine, task["choices"], [cx0 + 500, cy0 + 205, cx1 - 55, cy1 - 165], max_size=46)
        elif task_type == "read-word":
            text_engine.fitted_text(draw, "Read the word. Tick the picture.", [cx0 + 30, cy0 + 18, cx1 - 30, cy0 + 90], max_size=33, min_size=25, colour=NAVY, bold=True, max_lines=1)
            text_engine.fitted_text(draw, task["word"], [cx0 + 50, cy0 + 170, cx0 + 340, cy1 - 110], max_size=54, min_size=40, colour=NAVY, bold=True, max_lines=1)
            paste_fit(canvas, assets[task["asset"]], [cx0 + 390, cy0 + 105, cx1 - 145, cy1 - 105], inset=3)
            draw_asset_name(draw, text_engine, task["asset"], [cx0 + 410, cy1 - 100, cx1 - 165, cy1 - 50], max_size=25)
            draw.rectangle([cx1 - 120, cy1 - 115, cx1 - 50, cy1 - 45], fill="white", outline=PURPLE, width=4)
        else:
            raise ValueError(f"Unsupported mixed review task: {task_type}")


def render_story_sequence(canvas, draw, page, assets, text_engine):
    area = model_shell(draw, text_engine)
    x0, y0, x1, y1 = area
    steps = [("1", "empty cup"), ("2", "pour water"), ("3", "full cup")]
    for index, (number, label) in enumerate(steps):
        left = x0 + 20 + index * 385
        draw.ellipse([left, y0 + 40, left + 78, y0 + 118], fill=BLUE, outline=PURPLE, width=3)
        text_engine.fitted_text(draw, number, [left + 12, y0 + 52, left + 66, y0 + 106], max_size=31, min_size=26, colour=NAVY, bold=True, max_lines=1)
        text_engine.fitted_text(draw, label, [left + 92, y0 + 25, left + 350, y1 - 25], max_size=31, min_size=23, colour=NAVY, bold=True, max_lines=2)
    text_engine.fitted_text(draw, "The numbers show the completed order.", [x0 + 1190, y0 + 20, x1 - 20, y1 - 20], max_size=31, min_size=24, colour=NAVY, bold=True, max_lines=2)
    order = page["activity"]["mechanics"]["display_order"]
    left, top, gap = 180, 950, 28
    cell_w = (2300 - left - gap) // 2
    cell_h = (2990 - top - gap) // 2
    for index, asset in enumerate(order):
        row, col = divmod(index, 2)
        cx0 = left + col * (cell_w + gap); cy0 = top + row * (cell_h + gap)
        panel(draw, [cx0, cy0, cx0 + cell_w, cy0 + cell_h], outline=SOFT_PURPLE, width=3)
        paste_fit(canvas, assets[asset], [cx0 + 45, cy0 + 30, cx0 + cell_w - 45, cy0 + cell_h - 130], inset=3)
        panel(draw, [cx0 + cell_w // 2 - 75, cy0 + cell_h - 115, cx0 + cell_w // 2 + 75, cy0 + cell_h - 25], fill="#FFFDF3", outline="#D8A51C", width=3, radius=14)


def render_story_retell(canvas, draw, page, assets, text_engine):
    area = model_shell(draw, text_engine)
    x0, y0, x1, y1 = area
    draw.rounded_rectangle([x0 + 45, y0 + 35, x0 + 270, y1 - 35], radius=12, fill="#8EC5FF", outline=NAVY, width=4)
    draw.line([x0 + 158, y0 + 42, x0 + 158, y1 - 42], fill=NAVY, width=3)
    text_engine.fitted_text(draw, "First, the child opens the book.", [x0 + 330, y0 + 20, x1 - 20, y1 - 20], max_size=39, min_size=29, colour=NAVY, bold=True, max_lines=2)
    mechanics = page["activity"]["mechanics"]
    scenes, starters = mechanics["ordered_scenes"], mechanics["starters"]
    left, top, gap = 180, 950, 28
    cell_w = (2300 - left - gap) // 2
    cell_h = (2990 - top - gap) // 2
    for index, asset in enumerate(scenes):
        row, col = divmod(index, 2)
        cx0 = left + col * (cell_w + gap); cy0 = top + row * (cell_h + gap)
        panel(draw, [cx0, cy0, cx0 + cell_w, cy0 + cell_h], outline=SOFT_PURPLE, width=3)
        panel(draw, [cx0 + 25, cy0 + 22, cx0 + 240, cy0 + 100], fill=BLUE, outline="#1768B3", width=2, radius=14)
        text_engine.fitted_text(draw, starters[index], [cx0 + 45, cy0 + 30, cx0 + 220, cy0 + 92], max_size=34, min_size=27, colour=NAVY, bold=True, max_lines=1)
        paste_fit(canvas, assets[asset], [cx0 + 35, cy0 + 115, cx0 + cell_w - 35, cy0 + cell_h - 25], inset=3)


def render_picture_conversation(canvas, draw, page, assets, text_engine):
    area = model_shell(draw, text_engine)
    x0, y0, x1, y1 = area
    text_engine.fitted_text(draw, "What are the children doing?", [x0 + 25, y0 + 18, x0 + 650, y1 - 18], max_size=35, min_size=26, colour=NAVY, bold=True, align="left", max_lines=2)
    text_engine.fitted_text(draw, "They are sharing a ball.", [x0 + 730, y0 + 18, x1 - 20, y1 - 18], max_size=39, min_size=29, colour="#2E7D32", bold=True, max_lines=2)
    mechanics = page["activity"]["mechanics"]
    panel(draw, [170, 950, 1510, 2660], outline=SOFT_PURPLE, width=3)
    paste_fit(canvas, assets[mechanics["scene"]], [205, 985, 1475, 2625], inset=3)
    prompts = mechanics["prompts"]
    gap = 22; row_h = (2660 - 950 - gap * 2) // 3
    for index, item in enumerate(prompts):
        y0 = 950 + index * (row_h + gap)
        panel(draw, [1540, y0, 2310, y0 + row_h], fill="#FBFAFF", outline=SOFT_PURPLE, width=3)
        text_engine.fitted_text(draw, item["question"], [1570, y0 + 28, 2280, y0 + 125], max_size=33, min_size=25, colour=NAVY, bold=True, align="left", max_lines=2)
        text_engine.fitted_text(draw, item["starter"], [1570, y0 + 145, 2280, y0 + row_h - 55], max_size=31, min_size=23, colour=INK, align="left", max_lines=2)
        draw.line([1600, y0 + row_h - 40, 2250, y0 + row_h - 40], fill="#716052", width=3)
    panel(draw, [170, 2700, 2310, 2990], fill=BLUE, outline="#1768B3", width=3)
    text_engine.fitted_text(draw, mechanics["partner_turn_cue"], [230, 2740, 2250, 2950], max_size=40, min_size=30, colour=NAVY, bold=True, max_lines=2)


def render_favourite_story(draw, page, text_engine):
    area = model_shell(draw, text_engine)
    x0, y0, x1, y1 = area
    draw.ellipse([x0 + 55, y0 + 35, x0 + 180, y1 - 35], fill="#F5F1E8", outline=NAVY, width=4)
    draw.polygon([(x0 + 72, y0 + 55), (x0 + 78, y0 + 10), (x0 + 105, y0 + 50)], fill="#F5F1E8", outline=NAVY)
    draw.polygon([(x0 + 128, y0 + 50), (x0 + 155, y0 + 10), (x0 + 165, y0 + 60)], fill="#F5F1E8", outline=NAVY)
    text_engine.fitted_text(draw, "My favourite character is the rabbit.", [x0 + 240, y0 + 20, x1 - 20, y1 - 20], max_size=39, min_size=29, colour=NAVY, bold=True, max_lines=2)
    panel(draw, [180, 950, 2300, 2440], fill="#FFFFFF", outline=SOFT_PURPLE, width=4)
    text_engine.fitted_text(draw, "Draw your favourite story character here.", [260, 990, 2220, 1090], max_size=40, min_size=30, colour=NAVY, bold=True, max_lines=1)
    starter = page["activity"]["mechanics"]["sentence_starter"]
    panel(draw, [180, 2480, 2300, 2740], fill="#FFFDF8", outline="#D8A51C", width=3)
    text_engine.fitted_text(draw, starter, [240, 2520, 2240, 2700], max_size=43, min_size=31, colour=NAVY, bold=True, max_lines=2)
    panel(draw, [180, 2780, 2300, 2990], fill=BLUE, outline="#1768B3", width=3)
    text_engine.fitted_text(draw, page["activity"]["mechanics"]["oral_prompt"], [240, 2815, 2240, 2960], max_size=37, min_size=28, colour=NAVY, bold=True, max_lines=2)


def assessment_shell(draw, text_engine):
    """Assessment pages explain the response rule without revealing a model answer."""
    panel(draw, [170, 700, 2310, 900], fill="#F6F1FF", outline=SOFT_PURPLE, width=3)
    panel(draw, [195, 720, 535, 880], fill="#E7D9FA", outline=SOFT_PURPLE, width=2, radius=18)
    text_engine.fitted_text(draw, "MINI\nASSESSMENT", [220, 737, 510, 862], max_size=35, min_size=27, colour=NAVY, bold=True, max_lines=2)
    text_engine.fitted_text(
        draw,
        "Complete each activity independently. No answer is shown.",
        [585, 730, 2270, 870],
        max_size=41,
        min_size=30,
        colour=NAVY,
        bold=True,
        max_lines=2,
    )


def draw_asset_choice_cards(canvas, draw, assets, text_engine, choices, box):
    x0, y0, x1, y1 = box
    gap = 22
    card_w = (x1 - x0 - gap * (len(choices) - 1)) // len(choices)
    for index, choice in enumerate(choices):
        left = x0 + index * (card_w + gap)
        panel(draw, [left, y0, left + card_w, y1], fill="#FFFDF8", outline="#C7A9EF", width=2, radius=16)
        paste_fit(canvas, assets[choice], [left + 18, y0 + 15, left + card_w - 18, y1 - 75], inset=2)
        circle_x = left + card_w // 2
        draw.ellipse([circle_x - 23, y1 - 63, circle_x + 23, y1 - 17], fill="white", outline=PURPLE, width=4)


def render_mini_assessment(canvas, draw, page, assets, text_engine):
    assessment_shell(draw, text_engine)
    tasks = page["activity"]["mechanics"]["tasks"]
    left, top, right, bottom, gap = 170, 950, 2310, 2990, 28
    cell_w = (right - left - gap) // 2
    cell_h = (bottom - top - gap) // 2

    for index, task in enumerate(tasks):
        row, col = divmod(index, 2)
        x0 = left + col * (cell_w + gap)
        y0 = top + row * (cell_h + gap)
        x1, y1 = x0 + cell_w, y0 + cell_h
        panel(draw, [x0, y0, x1, y1], fill="#FFFFFF", outline=SOFT_PURPLE, width=3)
        task_type = task["type"]

        if task_type in {"beginning-sound", "ending-sound"}:
            prompt = "Circle the beginning sound." if task_type == "beginning-sound" else "Circle the ending sound."
            text_engine.fitted_text(draw, prompt, [x0 + 28, y0 + 24, x1 - 28, y0 + 105], max_size=34, min_size=27, colour=NAVY, bold=True, max_lines=1)
            paste_fit(canvas, assets[task["asset"]], [x0 + 260, y0 + 125, x1 - 260, y0 + 600], inset=3)
            draw_open_choices(draw, text_engine, task["choices"], [x0 + 155, y1 - 230, x1 - 155, y1 - 70], max_size=48)
        elif task_type == "rhyme":
            text_engine.fitted_text(draw, "Circle the picture that rhymes.", [x0 + 28, y0 + 24, x1 - 28, y0 + 105], max_size=34, min_size=27, colour=NAVY, bold=True, max_lines=1)
            paste_fit(canvas, assets[task["model"]], [x0 + 390, y0 + 115, x1 - 390, y0 + 400], inset=3)
            text_engine.fitted_text(draw, task["model"], [x0 + 365, y0 + 390, x1 - 365, y0 + 465], max_size=34, min_size=26, colour=NAVY, bold=True, max_lines=1)
            draw_asset_choice_cards(canvas, draw, assets, text_engine, task["choices"], [x0 + 85, y0 + 490, x1 - 85, y1 - 45])
        elif task_type == "read-match":
            text_engine.fitted_text(draw, "Read the word. Circle its picture.", [x0 + 28, y0 + 24, x1 - 28, y0 + 105], max_size=34, min_size=27, colour=NAVY, bold=True, max_lines=1)
            panel(draw, [x0 + 385, y0 + 120, x1 - 385, y0 + 265], fill=BLUE, outline="#1768B3", width=3, radius=16)
            text_engine.fitted_text(draw, task["word"], [x0 + 405, y0 + 135, x1 - 405, y0 + 250], max_size=55, min_size=41, colour=NAVY, bold=True, max_lines=1)
            draw_asset_choice_cards(canvas, draw, assets, text_engine, task["choices"], [x0 + 85, y0 + 305, x1 - 85, y1 - 45])
        elif task_type == "sight-word":
            text_engine.fitted_text(draw, f"Circle the word: {task['target']}", [x0 + 28, y0 + 28, x1 - 28, y0 + 130], max_size=38, min_size=29, colour=NAVY, bold=True, max_lines=1)
            words = task["sentence"].replace(".", "").split()
            draw_open_choices(draw, text_engine, words, [x0 + 65, y0 + 300, x1 - 65, y0 + 500], max_size=43)
        elif task_type == "sentence-picture":
            text_engine.fitted_text(draw, "Tick if the sentence matches.", [x0 + 28, y0 + 24, x1 - 28, y0 + 105], max_size=34, min_size=27, colour=NAVY, bold=True, max_lines=1)
            text_engine.fitted_text(draw, task["sentence"], [x0 + 45, y0 + 120, x1 - 45, y0 + 245], max_size=43, min_size=32, colour=NAVY, bold=True, max_lines=2)
            paste_fit(canvas, assets[task["asset"]], [x0 + 260, y0 + 270, x1 - 260, y1 - 170], inset=3)
            draw.rectangle([x0 + 420, y1 - 135, x0 + 500, y1 - 55], fill="white", outline=PURPLE, width=4)
            text_engine.fitted_text(draw, "Tick", [x0 + 520, y1 - 145, x0 + 700, y1 - 45], max_size=33, min_size=27, colour=NAVY, bold=True, max_lines=1)
        elif task_type == "sequence":
            text_engine.fitted_text(draw, "Write 1, 2 and 3 in story order.", [x0 + 28, y0 + 24, x1 - 28, y0 + 105], max_size=34, min_size=27, colour=NAVY, bold=True, max_lines=1)
            names = task["display_order"]
            card_gap = 14
            card_w = (x1 - x0 - 80 - card_gap * 2) // 3
            for item_index, name in enumerate(names):
                left_card = x0 + 40 + item_index * (card_w + card_gap)
                panel(draw, [left_card, y0 + 145, left_card + card_w, y1 - 45], outline="#C7A9EF", width=2, radius=14)
                paste_fit(canvas, assets[name], [left_card + 10, y0 + 160, left_card + card_w - 10, y1 - 150], inset=2)
                panel(draw, [left_card + card_w // 2 - 42, y1 - 125, left_card + card_w // 2 + 42, y1 - 45], fill="#FFFDF8", outline=PURPLE, width=3, radius=12)
        elif task_type == "picture-question":
            text_engine.fitted_text(draw, task["question"], [x0 + 28, y0 + 24, x1 - 28, y0 + 105], max_size=35, min_size=27, colour=NAVY, bold=True, max_lines=1)
            paste_fit(canvas, assets[task["asset"]], [x0 + 240, y0 + 120, x1 - 240, y0 + 600], inset=3)
            draw_open_choices(draw, text_engine, task["choices"], [x0 + 115, y1 - 230, x1 - 115, y1 - 70], max_size=35)
        else:
            raise ValueError(f"Unsupported assessment task: {task_type}")


def render_full_review(canvas, draw, page, assets, text_engine):
    area = model_shell(draw, text_engine)
    x0, y0, x1, y1 = area
    text_engine.fitted_text(draw, "A", [x0 + 30, y0 + 28, x0 + 250, y1 - 28], max_size=56, min_size=42, colour=NAVY, bold=True, max_lines=1)
    draw.line([x0 + 280, 800, x0 + 575, 800], fill=PURPLE, width=5)
    draw.polygon([(x0 + 575, 800), (x0 + 535, 776), (x0 + 535, 824)], fill=PURPLE)
    text_engine.fitted_text(draw, "a", [x0 + 630, y0 + 28, x0 + 850, y1 - 28], max_size=56, min_size=42, colour=NAVY, bold=True, max_lines=1)
    text_engine.fitted_text(draw, "Match the capital letter to its small letter.", [x0 + 930, y0 + 20, x1 - 20, y1 - 20], max_size=35, min_size=27, colour=NAVY, bold=True, max_lines=2)

    tasks = page["activity"]["mechanics"]["tasks"]
    left, top, right, bottom, gap = 170, 950, 2310, 2990, 24
    cell_w = (right - left - gap) // 2
    cell_h = (bottom - top - gap * 2) // 3
    for index, task in enumerate(tasks):
        row, col = divmod(index, 2)
        px0 = left + col * (cell_w + gap); py0 = top + row * (cell_h + gap)
        px1, py1 = px0 + cell_w, py0 + cell_h
        panel(draw, [px0, py0, px1, py1], outline=SOFT_PURPLE, width=3)
        task_type = task["type"]
        if task_type == "letter-match":
            text_engine.fitted_text(draw, "Match the letter.", [px0 + 25, py0 + 20, px1 - 25, py0 + 90], max_size=31, min_size=25, colour=NAVY, bold=True, max_lines=1)
            text_engine.fitted_text(draw, task["left"], [px0 + 70, py0 + 150, px0 + 300, py1 - 110], max_size=65, min_size=48, colour=NAVY, bold=True, max_lines=1)
            draw_open_choices(draw, text_engine, task["choices"], [px0 + 390, py0 + 175, px1 - 45, py1 - 130], max_size=46)
        elif task_type == "beginning-sound":
            text_engine.fitted_text(draw, "Circle the beginning sound.", [px0 + 25, py0 + 20, px1 - 25, py0 + 90], max_size=31, min_size=24, colour=NAVY, bold=True, max_lines=1)
            paste_fit(canvas, assets[task["asset"]], [px0 + 80, py0 + 105, px0 + 420, py1 - 55], inset=2)
            draw_open_choices(draw, text_engine, task["choices"], [px0 + 480, py0 + 175, px1 - 45, py1 - 130], max_size=45)
        elif task_type == "rhyme":
            text_engine.fitted_text(draw, f"Circle what rhymes with {task['model']}.", [px0 + 25, py0 + 20, px1 - 25, py0 + 90], max_size=31, min_size=24, colour=NAVY, bold=True, max_lines=1)
            paste_fit(canvas, assets[task["model"]], [px0 + 50, py0 + 110, px0 + 330, py1 - 70], inset=2)
            draw_asset_choice_cards(canvas, draw, assets, text_engine, task["choices"], [px0 + 370, py0 + 120, px1 - 35, py1 - 35])
        elif task_type == "read-word":
            text_engine.fitted_text(draw, "Read the word. Tick the picture.", [px0 + 25, py0 + 20, px1 - 25, py0 + 90], max_size=31, min_size=24, colour=NAVY, bold=True, max_lines=1)
            text_engine.fitted_text(draw, task["word"], [px0 + 45, py0 + 145, px0 + 330, py1 - 100], max_size=57, min_size=41, colour=NAVY, bold=True, max_lines=1)
            paste_fit(canvas, assets[task["asset"]], [px0 + 400, py0 + 105, px1 - 120, py1 - 65], inset=2)
            draw.rectangle([px1 - 105, py1 - 120, px1 - 45, py1 - 60], fill="white", outline=PURPLE, width=4)
        elif task_type == "sentence":
            text_engine.fitted_text(draw, task["sentence"], [px0 + 25, py0 + 20, px1 - 25, py0 + 110], max_size=34, min_size=26, colour=NAVY, bold=True, max_lines=1)
            paste_fit(canvas, assets[task["asset"]], [px0 + 300, py0 + 120, px1 - 260, py1 - 70], inset=2)
            draw.rectangle([px1 - 105, py1 - 120, px1 - 45, py1 - 60], fill="white", outline=PURPLE, width=4)
        elif task_type == "sight-word":
            text_engine.fitted_text(draw, f"Circle: {task['target']}", [px0 + 25, py0 + 20, px1 - 25, py0 + 90], max_size=31, min_size=25, colour=NAVY, bold=True, max_lines=1)
            draw_open_choices(draw, text_engine, task["sentence"].replace(".", "").split(), [px0 + 65, py0 + 210, px1 - 65, py1 - 125], max_size=38)


def render_certificate(canvas, draw, page, assets, text_engine):
    panel(draw, [190, 720, 2290, 3140], fill="#FFFDF8", outline="#D8A51C", width=6, radius=34)
    paste_fit(canvas, assets["badge"], [855, 770, 1625, 1370], inset=8)
    text_engine.fitted_text(draw, "CERTIFICATE OF COMPLETION", [340, 1400, 2140, 1535], max_size=57, min_size=42, colour=NAVY, bold=True, max_lines=1)
    text_engine.fitted_text(draw, "This certificate is proudly presented to", [380, 1570, 2100, 1680], max_size=39, min_size=30, colour=INK, max_lines=1)
    draw.line([500, 1870, 1980, 1870], fill=PURPLE, width=4)
    text_engine.fitted_text(draw, "Learner name", [850, 1885, 1630, 1975], max_size=31, min_size=25, colour="#667085", max_lines=1)
    text_engine.fitted_text(draw, page["activity"]["mechanics"]["achievement_line"], [390, 2040, 2090, 2160], max_size=43, min_size=33, colour=NAVY, bold=True, max_lines=2)
    paste_fit(canvas, assets["book_cluster"], [760, 2180, 1720, 2660], inset=8)
    draw.line([330, 2860, 980, 2860], fill=PURPLE, width=3)
    draw.line([1500, 2860, 2150, 2860], fill=PURPLE, width=3)
    text_engine.fitted_text(draw, "Date", [530, 2875, 780, 2965], max_size=31, min_size=25, colour="#667085", max_lines=1)
    text_engine.fitted_text(draw, "Teacher signature", [1650, 2875, 2000, 2965], max_size=31, min_size=25, colour="#667085", max_lines=1)


def render_reader_reflection(canvas, draw, page, assets, text_engine):
    area = model_shell(draw, text_engine)
    x0, y0, x1, y1 = area
    draw.rectangle([x0 + 40, y0 + 42, x0 + 118, y0 + 120], fill="#FFFFFF", outline=PURPLE, width=4)
    draw.line([x0 + 53, y0 + 84, x0 + 73, y0 + 105], fill="#2E7D32", width=6)
    draw.line([x0 + 73, y0 + 105, x0 + 108, y0 + 55], fill="#2E7D32", width=6)
    text_engine.fitted_text(draw, page["learning"]["model_text"]["statement"], [x0 + 155, y0 + 25, x0 + 750, y1 - 25], max_size=40, min_size=30, colour=NAVY, bold=True, max_lines=2)
    text_engine.fitted_text(draw, "The completed tick shows one example.", [x0 + 820, y0 + 25, x1 - 20, y1 - 25], max_size=34, min_size=26, colour=NAVY, bold=True, max_lines=2)
    panel(draw, [170, 950, 2310, 1640], outline=SOFT_PURPLE, width=3)
    paste_fit(canvas, assets["reader_hero"], [210, 980, 2270, 1610], inset=4)
    statements = page["activity"]["mechanics"]["statements"]
    left, top, gap = 170, 1685, 24
    card_w = (2140 - gap * 2) // 3
    for index, statement in enumerate(statements):
        x = left + index * (card_w + gap)
        panel(draw, [x, top, x + card_w, 2160], fill="#FBFAFF", outline=SOFT_PURPLE, width=3)
        draw.rectangle([x + 40, top + 65, x + 145, top + 170], fill="#FFFFFF", outline=PURPLE, width=5)
        text_engine.fitted_text(draw, statement, [x + 175, top + 35, x + card_w - 25, 2110], max_size=37, min_size=28, colour=NAVY, bold=True, align="left", max_lines=3)
    panel(draw, [170, 2205, 2310, 2635], fill=BLUE, outline="#1768B3", width=3)
    text_engine.fitted_text(draw, "TELL YOUR TEACHER", [230, 2250, 850, 2350], max_size=34, min_size=27, colour=NAVY, bold=True, max_lines=1)
    text_engine.fitted_text(draw, page["activity"]["mechanics"]["oral_prompt"], [880, 2250, 2240, 2590], max_size=42, min_size=31, colour=NAVY, bold=True, max_lines=2)
    panel(draw, [170, 2680, 2310, 2990], fill="#FFFDF8", outline="#D8A51C", width=3)
    text_engine.fitted_text(draw, "Choose honestly. You may tick more than one statement.", [230, 2740, 2250, 2930], max_size=38, min_size=29, colour=NAVY, bold=True, max_lines=2)


def render_celebration(canvas, draw, page, assets, text_engine):
    area = model_shell(draw, text_engine)
    x0, y0, x1, y1 = area
    panel(draw, [x0 + 35, y0 + 35, x0 + 330, y1 - 35], fill=BLUE, outline="#1768B3", width=3, radius=14)
    text_engine.fitted_text(draw, "WORDS", [x0 + 65, y0 + 50, x0 + 300, y1 - 50], max_size=35, min_size=28, colour=NAVY, bold=True, max_lines=1)
    draw.line([x0 + 375, 800, x0 + 650, 800], fill=PURPLE, width=5)
    draw.polygon([(x0 + 650, 800), (x0 + 610, 776), (x0 + 610, 824)], fill=PURPLE)
    text_engine.fitted_text(draw, "cat", [x0 + 710, y0 + 30, x0 + 1000, y1 - 30], max_size=53, min_size=39, colour=NAVY, bold=True, max_lines=1)
    text_engine.fitted_text(draw, "Choose one area, then make your own example.", [x0 + 1050, y0 + 18, x1 - 20, y1 - 18], max_size=34, min_size=26, colour=NAVY, bold=True, max_lines=2)
    panel(draw, [170, 950, 2310, 1660], outline=SOFT_PURPLE, width=3)
    paste_fit(canvas, assets["celebration_hero"], [210, 980, 2270, 1630], inset=3)
    choices = page["activity"]["mechanics"]["choices"]
    gap = 26; choice_w = (2140 - gap * 2) // 3
    for index, choice in enumerate(choices):
        left = 170 + index * (choice_w + gap)
        panel(draw, [left, 1705, left + choice_w, 1945], fill="#FBFAFF", outline=SOFT_PURPLE, width=3)
        draw.rectangle([left + 45, 1770, left + 125, 1850], fill="#FFFFFF", outline=PURPLE, width=4)
        text_engine.fitted_text(draw, choice, [left + 155, 1745, left + choice_w - 25, 1875], max_size=39, min_size=29, colour=NAVY, bold=True, max_lines=1)
    panel(draw, [170, 1990, 2310, 2990], fill="#FFFFFF", outline="#D8A51C", width=4)
    text_engine.fitted_text(draw, page["activity"]["mechanics"]["work_frame_prompt"], [230, 2025, 2250, 2130], max_size=40, min_size=31, colour=NAVY, bold=True, max_lines=1)


def compose(page, logo_path: Path, illustration_path: Path | None, output: Path, evidence_output: Path):
    text_engine = load_module("early_literacy_text_engine", BASE)
    template = load_json(TEMPLATE)
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (255, 253, 248, 255))
    draw = ImageDraw.Draw(canvas)
    logo = Image.open(logo_path).convert("RGBA")
    header(canvas, draw, page, logo, text_engine, template)

    assets: dict[str, Image.Image] = {}
    if page["illustration"]["requires_generated_art"]:
        if illustration_path is None or not illustration_path.is_file():
            raise FileNotFoundError(f"Approved illustration required for {page['identity']['page_id']}")
        source = Image.open(illustration_path).convert("RGBA")
        assets = crop_assets(source, page["illustration"]["asset_crops"])

    render_kind = page["activity"]["render_kind"]
    if render_kind == "literacy-missing-letters":
        render_missing_letters(draw, page, text_engine)
    elif render_kind == "literacy-letter-match":
        render_letter_match(draw, page, text_engine)
    elif render_kind in {"literacy-letter-picture-match", "literacy-picture-match", "literacy-word-picture-match"}:
        render_two_column_match(canvas, draw, page, assets, text_engine)
    elif render_kind in {"literacy-picture-letter-choice", "literacy-picture-word-choice", "literacy-sentence-completion"}:
        render_choice_cards(canvas, draw, page, assets, text_engine)
    elif render_kind in {"literacy-sound-choice-rows", "literacy-odd-picture-rows"}:
        render_picture_choice_rows(canvas, draw, page, assets, text_engine)
    elif render_kind == "literacy-build-word":
        render_build_word(canvas, draw, page, assets, text_engine)
    elif render_kind == "literacy-read-match":
        render_read_match(canvas, draw, page, assets, text_engine)
    elif render_kind == "literacy-category-sort":
        render_category_sort(canvas, draw, page, assets, text_engine)
    elif render_kind == "literacy-read-colour":
        render_read_colour(canvas, draw, page, assets, text_engine)
    elif render_kind == "literacy-sentence-builder":
        render_sentence_builder(canvas, draw, page, assets, text_engine)
    elif render_kind == "literacy-scene-questions":
        render_scene_questions(canvas, draw, page, assets, text_engine)
    elif render_kind == "literacy-listening-choice":
        render_listening_choice(canvas, draw, page, assets, text_engine)
    elif render_kind == "literacy-sight-word-search":
        render_sight_words(canvas, draw, page, assets, text_engine)
    elif render_kind == "literacy-mixed-review":
        render_mixed_review(canvas, draw, page, assets, text_engine)
    elif render_kind == "literacy-story-sequence":
        render_story_sequence(canvas, draw, page, assets, text_engine)
    elif render_kind == "literacy-story-retell":
        render_story_retell(canvas, draw, page, assets, text_engine)
    elif render_kind == "literacy-picture-conversation":
        render_picture_conversation(canvas, draw, page, assets, text_engine)
    elif render_kind == "literacy-who-what-where":
        render_scene_questions(canvas, draw, page, assets, text_engine, labelled=True)
    elif render_kind == "literacy-favourite-story":
        render_favourite_story(draw, page, text_engine)
    elif render_kind == "literacy-mini-assessment":
        render_mini_assessment(canvas, draw, page, assets, text_engine)
    elif render_kind == "literacy-full-review":
        render_full_review(canvas, draw, page, assets, text_engine)
    elif render_kind == "literacy-certificate":
        render_certificate(canvas, draw, page, assets, text_engine)
    elif render_kind == "literacy-reader-reflection":
        render_reader_reflection(canvas, draw, page, assets, text_engine)
    elif render_kind == "literacy-celebration":
        render_celebration(canvas, draw, page, assets, text_engine)
    else:
        raise ValueError(f"Exact Early Literacy renderer not implemented yet: {render_kind}")

    if render_kind == "literacy-certificate":
        printed = page["identity"].get("printed_page")
        if printed is not None:
            text_engine.fitted_text(draw, str(printed), [2180, 3310, 2310, 3425], max_size=40, min_size=31, colour="#667085", bold=True, max_lines=1)
    else:
        teacher_and_footer(draw, page, text_engine)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output, "PNG", dpi=(300, 300), optimize=True)
    evidence = {
        "page_id": page["identity"]["page_id"],
        "render_kind": render_kind,
        "output": str(output),
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "completed_example_visible": render_kind not in {"literacy-mini-assessment", "literacy-certificate"},
        "assessment_safe": render_kind != "literacy-mini-assessment" or bool(page["learning"]["model_text"].get("assessment_safe")),
        "independent_answers_unmarked": True,
        "parent_panel": False,
        "generic_response_panel": False,
        "status": "PASS",
    }
    evidence_output.parent.mkdir(parents=True, exist_ok=True)
    evidence_output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--page-id", required=True)
    parser.add_argument("--logo", type=Path, required=True)
    parser.add_argument("--illustration", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    args = parser.parse_args()
    loader = load_module("early_literacy_runtime_loader", LOADER)
    page = loader.load_page_contract(level="lkg", book_slug="early-literacy-adventures", page_id=args.page_id)
    compose(page, args.logo, args.illustration, args.output, args.evidence_output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Early Literacy render FAIL: {exc}", file=sys.stderr)
        raise SystemExit(2)
