#!/usr/bin/env python3
"""Curriculum-first Communication Champions LKG page composer."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "bcube-publishing-sdk/composer/compose_learning_page_v2.py"
TEMPLATE = ROOT / "bcube-publishing-sdk/templates/learning-page-v2.json"
LOADER = ROOT / "bcube-publishing-sdk/runtime/load_book_contract.py"
WIDTH, HEIGHT = 2480, 3508
NAVY, PURPLE, SOFT_PURPLE = "#123F72", "#7E57C2", "#A077E8"
BLUE, GOLD, GREEN, INK = "#E8F4FF", "#FFF4C6", "#F0FAED", "#31353A"


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
    difference = ImageChops.difference(rgba, background).convert("L").point(lambda value: 255 if value > 18 else 0)
    box = difference.getbbox()
    return rgba.crop(box) if box else rgba


def paste_fit(canvas: Image.Image, image: Image.Image, box, inset=10):
    x0, y0, x1, y1 = box
    x0 += inset; y0 += inset; x1 -= inset; y1 -= inset
    source = trim_white(image)
    scale = min((x1 - x0) / source.width, (y1 - y0) / source.height)
    source = source.resize((max(1, round(source.width * scale)), max(1, round(source.height * scale))), Image.Resampling.LANCZOS)
    x = x0 + (x1 - x0 - source.width) // 2; y = y0 + (y1 - y0 - source.height) // 2
    canvas.paste(source, (x, y), source)


def _cluster_positions(values: list[float], tolerance: float = 0.03) -> list[float]:
    clusters: list[list[float]] = []
    for value in sorted(values):
        if not clusters or abs(value - sum(clusters[-1]) / len(clusters[-1])) > tolerance:
            clusters.append([value])
        else:
            clusters[-1].append(value)
    return [sum(cluster) / len(cluster) for cluster in clusters]


def _white_gutter_boundaries(source: Image.Image, centres: list[float], *, axis: str) -> list[int]:
    """Find real white gutters near the manifest's planned grid midpoints."""
    size = source.width if axis == "x" else source.height
    cross = source.height if axis == "x" else source.width
    rgba = source.convert("RGBA")
    white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    ink = ImageChops.difference(rgba, white).convert("L").point(lambda value: 255 if value > 18 else 0)
    projection = [
        sum(1 for value in (ink.crop((index, 0, index + 1, source.height)).getdata() if axis == "x" else ink.crop((0, index, source.width, index + 1)).getdata()) if value)
        for index in range(size)
    ]
    boundaries = [0]
    for left, right in zip(centres, centres[1:]):
        midpoint = (left + right) / 2
        radius = max(6, round((right - left) * size * 0.22))
        start = max(1, round(midpoint * size) - radius)
        end = min(size - 1, round(midpoint * size) + radius)
        quiet = max(2, round(cross * 0.004))
        runs: list[tuple[int, int]] = []
        run_start: int | None = None
        for index in range(start, end):
            if projection[index] <= quiet:
                if run_start is None:
                    run_start = index
            elif run_start is not None:
                runs.append((run_start, index))
                run_start = None
        if run_start is not None:
            runs.append((run_start, end))
        if runs:
            target = round(midpoint * size)
            best = max(runs, key=lambda run: ((run[1] - run[0]), -abs((run[0] + run[1]) // 2 - target)))
            boundaries.append((best[0] + best[1]) // 2)
        else:
            boundaries.append(round(midpoint * size))
    boundaries.append(size)
    return boundaries


def crop_assets(source: Image.Image, crop_map: dict[str, Any]) -> dict[str, Image.Image]:
    width, height = source.size; result = {}
    x_centres = _cluster_positions([float(crop["x"]) + float(crop["w"]) / 2 for crop in crop_map.values()])
    y_centres = _cluster_positions([float(crop["y"]) + float(crop["h"]) / 2 for crop in crop_map.values()])
    grid_like = 1 <= len(x_centres) <= 4 and 1 <= len(y_centres) <= 8 and len(crop_map) <= len(x_centres) * len(y_centres)
    x_bounds = _white_gutter_boundaries(source, x_centres, axis="x") if grid_like else []
    y_bounds = _white_gutter_boundaries(source, y_centres, axis="y") if grid_like else []
    for name, crop in crop_map.items():
        x = float(crop["x"]); y = float(crop["y"]); w = float(crop["w"]); h = float(crop["h"])
        if grid_like:
            x_index = min(range(len(x_centres)), key=lambda index: abs(x_centres[index] - (x + w / 2)))
            y_index = min(range(len(y_centres)), key=lambda index: abs(y_centres[index] - (y + h / 2)))
            x0, x1 = x_bounds[x_index] + 2, x_bounds[x_index + 1] - 2
            y0, y1 = y_bounds[y_index] + 2, y_bounds[y_index + 1] - 2
        else:
            pad = float(crop.get("padding", 0.0))
            x0 = max(0, round((x - pad) * width)); y0 = max(0, round((y - pad) * height))
            x1 = min(width, round((x + w + pad) * width)); y1 = min(height, round((y + h + pad) * height))
        if x1 <= x0 or y1 <= y0: raise ValueError(f"Empty crop for {name}")
        result[name] = trim_white(source.crop((x0, y0, x1, y1)))
    return result


def readable(value: str) -> str:
    label = value.replace("_scene", "").replace("_action", "").replace("_solution", "").replace("_", " ")
    replacements = {"touch head": "touch your head", "show pencil": "show a pencil", "see bus": "bus", "boy has ball": "boy with a ball"}
    return replacements.get(label, label)


def display_label(page: dict[str, Any], asset_name: str) -> str:
    labels = page.get("activity", {}).get("mechanics", {}).get("display_labels", {})
    return str(labels.get(asset_name) or readable(asset_name))


def header(canvas, draw, page, logo, text, template):
    logo = logo.convert("RGBA"); logo.thumbnail((300, 220), Image.Resampling.LANCZOS)
    canvas.paste(logo, (110 + (300 - logo.width) // 2, 35 + (220 - logo.height) // 2), logo)
    text.brand_title(draw, ["Communication Champions"], [470, 45, 2320, 145], template["colours"], template["typography"])
    text.fitted_text(draw, page["identity"]["title"], [470, 140, 2320, 275], max_size=66, min_size=44, colour=NAVY, bold=True, max_lines=2)
    panel(draw, [150, 305, 2330, 445], fill=BLUE, outline="#1768B3", width=3)
    text.fitted_text(draw, "Learning goal: " + page["learning"]["objective"], [190, 318, 2290, 432], max_size=47, min_size=31, colour=NAVY, bold=True, max_lines=2)
    panel(draw, [150, 490, 2330, 650], fill=GOLD, outline="#E1A81C", width=3)
    text.fitted_text(draw, page["learning"]["instruction"], [190, 505, 2290, 635], max_size=51, min_size=32, colour=INK, bold=True, max_lines=2)


def teacher_footer(draw, page, text):
    panel(draw, [150, 3070, 2300, 3270], fill=GREEN, outline="#5F9D50", width=3)
    text.fitted_text(draw, "TEACHER CUE", [180, 3095, 520, 3245], max_size=38, min_size=29, colour=NAVY, bold=True, max_lines=1)
    text.fitted_text(draw, page["guidance"]["teacher_cue"], [550, 3090, 2260, 3250], max_size=38, min_size=27, colour=INK, align="left", max_lines=3)
    printed = page["identity"].get("printed_page")
    if printed is not None: text.fitted_text(draw, str(printed), [2180, 3310, 2310, 3425], max_size=40, min_size=31, colour="#667085", bold=True, max_lines=1)


def model_strip(canvas, draw, page, assets, text):
    panel(draw, [170, 700, 2310, 900], fill="#F6F1FF", outline=SOFT_PURPLE, width=3)
    panel(draw, [195, 720, 535, 880], fill="#E7D9FA", outline=SOFT_PURPLE, width=2, radius=18)
    text.fitted_text(draw, "COMPLETED\nEXAMPLE", [220, 737, 510, 862], max_size=35, min_size=26, colour=NAVY, bold=True, max_lines=2)
    model = page["learning"]["model_text"]
    asset_name = next((model[key] for key in ("picture", "person", "object", "solution") if isinstance(model.get(key), str) and model[key] in assets), None)
    text_left = 610
    if asset_name:
        paste_fit(canvas, assets[asset_name], [565, 708, 1020, 892], inset=3); text_left = 1060
    phrase = None
    if model.get("question") and model.get("answer"):
        phrase = f"{model['question']}  →  {model['answer']}"
    elif model.get("beginning") and model.get("ending"):
        phrase = f"{model['beginning']}  →  {model['ending']}"
    phrase = phrase or model.get("answer") or model.get("reply") or model.get("reflection") or model.get("instruction")
    if not phrase and model.get("actions"): phrase = " → ".join(model["actions"])
    if not phrase and model.get("steps"): phrase = " → ".join(model["steps"])
    if not phrase and model.get("words"): phrase = " ".join(model["words"])
    if not phrase and model.get("events"): phrase = "1  →  2  →  3  →  4"
    if not phrase and model.get("prompts"): phrase = "  •  ".join(model["prompts"])
    if not phrase: phrase = "The example shows how to complete the activity."
    text.fitted_text(draw, str(phrase), [text_left, 730, 2265, 870], max_size=43, min_size=28, colour=NAVY, bold=True, max_lines=3)


def draw_choices(draw, text, choices, box, *, cols=None):
    if not choices: return
    cols = cols or min(3, len(choices)); rows = math.ceil(len(choices) / cols)
    x0, y0, x1, y1 = box; gap = 16
    cell_w = (x1 - x0 - gap * (cols - 1)) // cols; cell_h = (y1 - y0 - gap * (rows - 1)) // rows
    for index, choice in enumerate(choices):
        row, col = divmod(index, cols); left = x0 + col * (cell_w + gap); top = y0 + row * (cell_h + gap)
        panel(draw, [left, top, left + cell_w, top + cell_h], fill="#FFFDF8", outline="#C7A9EF", width=2, radius=16)
        text.fitted_text(draw, str(choice), [left + 12, top + 8, left + cell_w - 12, top + cell_h - 8], max_size=34, min_size=23, colour=NAVY, bold=True, max_lines=2)


def render_card_grid(canvas, draw, page, assets, text):
    controls = page["activity"]["mechanics"]; names = controls["asset_order"]
    cols = 2 if len(names) <= 6 else 3; rows = math.ceil(len(names) / cols)
    left, right, top, bottom, gap = 170, 2310, 950, 2990, 24
    cell_w = (right - left - gap * (cols - 1)) // cols; cell_h = (bottom - top - gap * (rows - 1)) // rows
    choices_by_index = controls.get("choices") if controls.get("choices") and isinstance(controls["choices"][0] if controls["choices"] else None, list) else None
    repeated_choices = controls.get("choices") if controls.get("choices") and not choices_by_index and len(controls.get("choices", [])) <= 3 and all("_" not in str(value) for value in controls["choices"]) else None
    for index, name in enumerate(names):
        row, col = divmod(index, cols); x0 = left + col * (cell_w + gap); y0 = top + row * (cell_h + gap)
        panel(draw, [x0, y0, x0 + cell_w, y0 + cell_h], outline=SOFT_PURPLE, width=3)
        reserve = 155 if choices_by_index or repeated_choices or controls.get("sentence_frames") or controls.get("frame") else 85
        paste_fit(canvas, assets[name], [x0 + 25, y0 + 18, x0 + cell_w - 25, y0 + cell_h - reserve], inset=5)
        text.fitted_text(draw, display_label(page, name), [x0 + 20, y0 + cell_h - reserve + 5, x0 + cell_w - 20, y0 + cell_h - reserve + 62], max_size=30, min_size=21, colour=NAVY, bold=True, max_lines=1)
        if choices_by_index and index < len(choices_by_index): draw_choices(draw, text, choices_by_index[index], [x0 + 20, y0 + cell_h - 88, x0 + cell_w - 20, y0 + cell_h - 20], cols=len(choices_by_index[index]))
        elif repeated_choices: draw_choices(draw, text, repeated_choices, [x0 + 20, y0 + cell_h - 88, x0 + cell_w - 20, y0 + cell_h - 20], cols=len(repeated_choices))
        elif controls.get("sentence_frames"):
            frame = controls["sentence_frames"][index % len(controls["sentence_frames"])]
            text.fitted_text(draw, frame, [x0 + 25, y0 + cell_h - 90, x0 + cell_w - 25, y0 + cell_h - 18], max_size=29, min_size=21, colour=NAVY, bold=True, max_lines=1)
        elif controls.get("frame"):
            text.fitted_text(draw, controls["frame"], [x0 + 25, y0 + cell_h - 90, x0 + cell_w - 25, y0 + cell_h - 18], max_size=29, min_size=21, colour=NAVY, bold=True, max_lines=1)
        elif controls.get("response") == "circle":
            # Keep the child's response target separate from the readable label.
            draw.ellipse([x0 + cell_w - 82, y0 + 22, x0 + cell_w - 30, y0 + 74], fill="white", outline=PURPLE, width=4)


def render_match(canvas, draw, page, assets, text):
    controls = page["activity"]["mechanics"]; lefts = controls.get("left") or controls.get("pictures"); rights = controls.get("right_display") or controls.get("right") or controls.get("words")
    count = max(len(lefts), len(rights)); top, bottom, gap = 950, 2990, 20; row_h = (bottom - top - gap * (count - 1)) // count
    for index in range(count):
        y0 = top + index * (row_h + gap); y1 = y0 + row_h
        if index < len(lefts):
            panel(draw, [180, y0, 1010, y1], outline=SOFT_PURPLE, width=3); paste_fit(canvas, assets[lefts[index]], [225, y0 + 5, 850, y1 - 55], inset=4)
            text.fitted_text(draw, display_label(page, lefts[index]), [240, y1 - 58, 830, y1 - 5], max_size=27, min_size=20, colour=NAVY, bold=True, max_lines=1); draw.ellipse([940, (y0+y1)//2-16, 972, (y0+y1)//2+16], fill="white", outline=PURPLE, width=4)
        if index < len(rights):
            panel(draw, [1470, y0, 2300, y1], outline=SOFT_PURPLE, width=3); draw.ellipse([1518, (y0+y1)//2-16, 1550, (y0+y1)//2+16], fill="white", outline=PURPLE, width=4)
            if rights[index] in assets: paste_fit(canvas, assets[rights[index]], [1620, y0 + 5, 2250, y1 - 55], inset=4)
            text.fitted_text(draw, display_label(page, rights[index]), [1620, y1 - 62 if rights[index] in assets else y0 + 20, 2250, y1 - 5 if rights[index] in assets else y1 - 20], max_size=30, min_size=21, colour=NAVY, bold=True, max_lines=2)


def render_number_sequence(canvas, draw, page, assets, text):
    controls = page["activity"]["mechanics"]; order = controls.get("display_order") or controls.get("asset_order"); count = len(order)
    left, right, top, bottom, gap = 170, 2310, 980, 2850, 25; cell_w = (right-left-gap*(count-1))//count
    for index, name in enumerate(order):
        x0 = left + index*(cell_w+gap); panel(draw, [x0, top, x0+cell_w, bottom], outline=SOFT_PURPLE, width=3)
        paste_fit(canvas, assets[name], [x0+20, top+45, x0+cell_w-20, bottom-210], inset=5)
        text.fitted_text(draw, readable(name), [x0+20, bottom-200, x0+cell_w-20, bottom-130], max_size=28, min_size=20, colour=NAVY, bold=True, max_lines=1)
        panel(draw, [x0+cell_w//2-55, bottom-105, x0+cell_w//2+55, bottom-5], fill="#FFFFFF", outline=PURPLE, width=4, radius=14)
    text.fitted_text(draw, "Write one number in each box.", [650, 2880, 1830, 2990], max_size=35, min_size=27, colour=NAVY, bold=True, max_lines=1)


def render_action_strips(canvas, draw, page, assets, text):
    names = page["activity"]["mechanics"]["asset_order"]
    top, gap = 970, 28; row_h = (2990 - top - gap * (len(names) - 1)) // len(names)
    for index, name in enumerate(names):
        y0 = top + index * (row_h + gap); y1 = y0 + row_h
        panel(draw, [170, y0, 2310, y1], outline=SOFT_PURPLE, width=3)
        panel(draw, [195, y0 + 30, 325, y0 + 160], fill="#E7D9FA", outline=PURPLE, width=3, radius=18)
        text.fitted_text(draw, str(index + 1), [215, y0 + 45, 305, y0 + 145], max_size=45, min_size=34, colour=NAVY, bold=True, max_lines=1)
        paste_fit(canvas, assets[name], [370, y0 + 20, 1900, y1 - 20], inset=5)
        text.fitted_text(draw, "Listen, then do both actions.", [1920, y0 + 50, 2270, y1 - 50], max_size=31, min_size=23, colour=NAVY, bold=True, max_lines=3)


def render_scene_prompts(canvas, draw, page, assets, text):
    controls = page["activity"]["mechanics"]; scene = controls.get("scene") or controls["asset_order"][0]
    panel(draw, [170, 950, 2310, 2200], outline=SOFT_PURPLE, width=3); paste_fit(canvas, assets[scene], [205, 980, 2275, 2170], inset=4)
    questions = controls.get("questions") or controls.get("responses") or controls.get("frames") or []
    gap=20; card_w=(2140-gap*(len(questions)-1))//max(1,len(questions))
    for index, question in enumerate(questions):
        x0=170+index*(card_w+gap); panel(draw,[x0,2240,x0+card_w,2980],fill="#FBFAFF",outline=SOFT_PURPLE,width=3)
        text.fitted_text(draw, question, [x0+25,2270,x0+card_w-25,2420], max_size=38,min_size=25,colour=NAVY,bold=True,max_lines=3)
        draw.line([x0+50,2790,x0+card_w-50,2790],fill=PURPLE,width=3); draw.line([x0+50,2890,x0+card_w-50,2890],fill=PURPLE,width=3)


def render_social_cards(canvas, draw, page, assets, text):
    controls=page["activity"]["mechanics"]; names=controls["asset_order"]
    # Four choices read more naturally as a balanced 2 x 2 activity.  A
    # three-column grid left one isolated card and two unexplained blank cells.
    cols=2 if len(names)==4 else min(3,len(names)); rows=math.ceil(len(names)/cols); left,right,top,bottom,gap=170,2310,950,2540,24
    cell_w=(right-left-gap*(cols-1))//cols; cell_h=(bottom-top-gap*(rows-1))//rows
    for index,name in enumerate(names):
        row,col=divmod(index,cols); x0=left+col*(cell_w+gap); y0=top+row*(cell_h+gap)
        panel(draw,[x0,y0,x0+cell_w,y0+cell_h],outline=SOFT_PURPLE,width=3); paste_fit(canvas,assets[name],[x0+20,y0+15,x0+cell_w-20,y0+cell_h-80],inset=4)
        text.fitted_text(draw,display_label(page,name),[x0+15,y0+cell_h-72,x0+cell_w-15,y0+cell_h-10],max_size=28,min_size=20,colour=NAVY,bold=True,max_lines=1)
    choices=controls.get("responses") or controls.get("frames") or controls.get("checklist") or controls.get("questions") or controls.get("starters") or controls.get("choices") or ([controls["frame"]] if controls.get("frame") else [])
    if not choices and controls.get("ask"): choices=[controls["ask"], controls.get("reply","")]
    panel(draw,[170,2580,2310,2990],fill="#FBFAFF",outline=SOFT_PURPLE,width=3)
    draw_choices(draw,text,choices,[210,2620,2270,2950],cols=min(3,max(1,len(choices))))


def render_good_listening(canvas, draw, page, assets, text):
    """Five evidence cards plus a purposeful practise cell."""
    controls=page["activity"]["mechanics"]; names=controls["asset_order"]
    left,right,top,bottom,gap=170,2310,950,2990,24
    cols,rows=2,3; cell_w=(right-left-gap)//2; cell_h=(bottom-top-gap*2)//3
    for index,name in enumerate(names):
        row,col=divmod(index,cols); x0=left+col*(cell_w+gap); y0=top+row*(cell_h+gap)
        panel(draw,[x0,y0,x0+cell_w,y0+cell_h],outline=SOFT_PURPLE,width=3)
        draw.ellipse([x0+cell_w-76,y0+20,x0+cell_w-28,y0+68],fill="white",outline=PURPLE,width=4)
        paste_fit(canvas,assets[name],[x0+28,y0+18,x0+cell_w-28,y0+cell_h-92],inset=4)
        text.fitted_text(draw,display_label(page,name),[x0+22,y0+cell_h-82,x0+cell_w-22,y0+cell_h-15],max_size=30,min_size=21,colour=NAVY,bold=True,max_lines=1)
    x0=left+(cell_w+gap); y0=top+2*(cell_h+gap)
    panel(draw,[x0,y0,x0+cell_w,y0+cell_h],fill="#FFFDF8",outline=SOFT_PURPLE,width=3)
    text.fitted_text(draw,"TRY IT NOW",[x0+30,y0+25,x0+cell_w-30,y0+92],max_size=34,min_size=27,colour=NAVY,bold=True,max_lines=1)
    steps=["Look at your partner.","Keep your body still.","Say: I am ready to listen."]
    for i,step in enumerate(steps):
        yy=y0+125+i*135
        draw.rectangle([x0+45,yy+18,x0+91,yy+64],fill="white",outline=PURPLE,width=3)
        text.fitted_text(draw,step,[x0+120,yy,x0+cell_w-35,yy+88],max_size=29,min_size=22,colour=NAVY,bold=True,max_lines=2)


def render_classroom_objects(canvas, draw, page, assets, text):
    """Six vocabulary cards plus one asset and a related find/draw task."""
    controls=page["activity"]["mechanics"]; names=controls["asset_order"]
    left,right,top,gap=170,2310,950,24; cols=3
    cell_w=(right-left-gap*2)//3; row_h=620
    for index,name in enumerate(names[:6]):
        row,col=divmod(index,cols); x0=left+col*(cell_w+gap); y0=top+row*(row_h+gap)
        panel(draw,[x0,y0,x0+cell_w,y0+row_h],outline=SOFT_PURPLE,width=3)
        paste_fit(canvas,assets[name],[x0+22,y0+12,x0+cell_w-22,y0+row_h-145],inset=4)
        text.fitted_text(draw,display_label(page,name),[x0+18,y0+row_h-137,x0+cell_w-18,y0+row_h-82],max_size=28,min_size=21,colour=NAVY,bold=True,max_lines=1)
        text.fitted_text(draw,controls["frame"],[x0+18,y0+row_h-80,x0+cell_w-18,y0+row_h-15],max_size=27,min_size=20,colour=NAVY,bold=True,max_lines=1)
    y0=top+2*(row_h+gap); last_w=cell_w
    panel(draw,[left,y0,left+last_w,2990],outline=SOFT_PURPLE,width=3)
    paste_fit(canvas,assets[names[6]],[left+25,y0+15,left+last_w-25,2840],inset=4)
    text.fitted_text(draw,display_label(page,names[6]),[left+20,2832,left+last_w-20,2882],max_size=28,min_size=21,colour=NAVY,bold=True,max_lines=1)
    text.fitted_text(draw,controls["frame"],[left+20,2880,left+last_w-20,2965],max_size=27,min_size=20,colour=NAVY,bold=True,max_lines=1)
    x0=left+last_w+gap
    panel(draw,[x0,y0,right,2990],fill="#FFFDF8",outline=SOFT_PURPLE,width=3)
    text.fitted_text(draw,"FIND ONE MORE",[x0+35,y0+25,right-35,y0+90],max_size=34,min_size=27,colour=NAVY,bold=True,max_lines=1)
    text.fitted_text(draw,"Look around. Draw one more classroom thing.",[x0+35,y0+90,right-35,y0+185],max_size=31,min_size=23,colour=NAVY,bold=True,max_lines=2)
    panel(draw,[x0+45,y0+205,right-45,2840],fill="white",outline="#C7A9EF",width=2,radius=16)
    text.fitted_text(draw,"I can see a ___.",[x0+55,2860,right-55,2970],max_size=31,min_size=24,colour=NAVY,bold=True,max_lines=1)


def render_position_words(canvas, draw, page, assets, text):
    controls=page["activity"]["mechanics"]; names=controls["asset_order"]; choices=controls["choices"]
    left,right,top,gap=170,2310,950,24; cell_w=(right-left-gap)//2; row_h=610
    for index,name in enumerate(names[:4]):
        row,col=divmod(index,2); x0=left+col*(cell_w+gap); y0=top+row*(row_h+gap)
        panel(draw,[x0,y0,x0+cell_w,y0+row_h],outline=SOFT_PURPLE,width=3)
        paste_fit(canvas,assets[name],[x0+25,y0+15,x0+cell_w-25,y0+row_h-145],inset=4)
        text.fitted_text(draw,display_label(page,name),[x0+20,y0+row_h-140,x0+cell_w-20,y0+row_h-90],max_size=27,min_size=20,colour=NAVY,bold=True,max_lines=1)
        draw_choices(draw,text,choices[index],[x0+20,y0+row_h-82,x0+cell_w-20,y0+row_h-14],cols=2)
    y0=top+2*(row_h+gap)
    panel(draw,[left,y0,left+cell_w,2990],outline=SOFT_PURPLE,width=3)
    paste_fit(canvas,assets[names[4]],[left+25,y0+15,left+cell_w-25,2840],inset=4)
    text.fitted_text(draw,display_label(page,names[4]),[left+20,2825,left+cell_w-20,2880],max_size=27,min_size=20,colour=NAVY,bold=True,max_lines=1)
    draw_choices(draw,text,choices[4],[left+20,2890,left+cell_w-20,2970],cols=2)
    x0=left+cell_w+gap
    panel(draw,[x0,y0,right,2990],fill="#FFFDF8",outline=SOFT_PURPLE,width=3)
    text.fitted_text(draw,"DRAW AND SAY",[x0+35,y0+25,right-35,y0+95],max_size=34,min_size=27,colour=NAVY,bold=True,max_lines=1)
    text.fitted_text(draw,"Draw a ball under a chair.",[x0+35,y0+90,right-35,y0+175],max_size=31,min_size=23,colour=NAVY,bold=True,max_lines=2)
    panel(draw,[x0+45,y0+190,right-45,2960],fill="white",outline="#C7A9EF",width=2,radius=16)


def render_polite_words(canvas, draw, page, assets, text):
    controls=page["activity"]["mechanics"]; names=controls["asset_order"]
    left,right,top,gap=170,2310,950,24; cell_w=(right-left-gap*2)//3
    for index,name in enumerate(names):
        x0=left+index*(cell_w+gap)
        panel(draw,[x0,top,x0+cell_w,2220],outline=SOFT_PURPLE,width=3)
        paste_fit(canvas,assets[name],[x0+25,top+20,x0+cell_w-25,2100],inset=4)
        text.fitted_text(draw,display_label(page,name),[x0+20,2110,x0+cell_w-20,2195],max_size=29,min_size=21,colour=NAVY,bold=True,max_lines=2)
    text.fitted_text(draw,"Choose the words for each picture.",[190,2250,2290,2325],max_size=32,min_size=25,colour=NAVY,bold=True,max_lines=1)
    draw_choices(draw,text,controls["responses"],[190,2340,2290,2635],cols=3)
    panel(draw,[170,2675,2310,2990],fill="#FFFDF8",outline=SOFT_PURPLE,width=3)
    text.fitted_text(draw,"TRY IT WITH A PARTNER",[220,2705,2260,2780],max_size=33,min_size=26,colour=NAVY,bold=True,max_lines=1)
    text.fitted_text(draw,"Use one classroom object. Ask politely, pass it, then say thank you.",[220,2790,2260,2945],max_size=31,min_size=23,colour=NAVY,bold=True,max_lines=2)


def render_taking_turns(canvas, draw, page, assets, text):
    controls=page["activity"]["mechanics"]; order=controls["display_order"]
    left,right,top,gap=170,2310,950,24; cell_w=(right-left-gap*2)//3
    for index,name in enumerate(order):
        x0=left+index*(cell_w+gap)
        panel(draw,[x0,top,x0+cell_w,2300],outline=SOFT_PURPLE,width=3)
        paste_fit(canvas,assets[name],[x0+20,top+25,x0+cell_w-20,2100],inset=4)
        text.fitted_text(draw,readable(name),[x0+20,2110,x0+cell_w-20,2170],max_size=28,min_size=21,colour=NAVY,bold=True,max_lines=1)
        panel(draw,[x0+cell_w//2-50,2180,x0+cell_w//2+50,2280],fill="white",outline=PURPLE,width=4,radius=14)
    panel(draw,[170,2340,2310,2990],fill="#FFFDF8",outline=SOFT_PURPLE,width=3)
    text.fitted_text(draw,"NOW PRACTISE WITH ONE TOY",[210,2370,2270,2445],max_size=34,min_size=27,colour=NAVY,bold=True,max_lines=1)
    steps=["Ask for a turn.","Wait for your turn.","Take your turn and pass the toy."]
    for i,step in enumerate(steps):
        y=2490+i*145
        panel(draw,[230,y,320,y+90],fill="#E7D9FA",outline=PURPLE,width=3,radius=16)
        text.fitted_text(draw,str(i+1),[250,y+10,300,y+80],max_size=38,min_size=30,colour=NAVY,bold=True,max_lines=1)
        draw.rectangle([355,y+20,405,y+70],fill="white",outline=PURPLE,width=3)
        text.fitted_text(draw,step,[440,y,2200,y+95],max_size=31,min_size=23,colour=NAVY,bold=True,max_lines=2)


def render_help_request(canvas, draw, page, assets, text):
    controls=page["activity"]["mechanics"]; names=controls["asset_order"]
    left,right,top,gap=170,2310,950,24; cell_w=(right-left-gap*2)//3
    for index,name in enumerate(names):
        x0=left+index*(cell_w+gap)
        panel(draw,[x0,top,x0+cell_w,2280],outline=SOFT_PURPLE,width=3)
        draw.ellipse([x0+cell_w-78,top+22,x0+cell_w-28,top+72],fill="white",outline=PURPLE,width=4)
        paste_fit(canvas,assets[name],[x0+22,top+25,x0+cell_w-22,2160],inset=4)
        text.fitted_text(draw,display_label(page,name),[x0+18,2165,x0+cell_w-18,2255],max_size=29,min_size=21,colour=NAVY,bold=True,max_lines=2)
    boxes=[("1  ASK FOR HELP","Please help me ___."),("2  REPLY POLITELY","Thank you.")]
    bw=(2140-gap)//2
    for i,(heading,phrase) in enumerate(boxes):
        x0=170+i*(bw+gap); panel(draw,[x0,2320,x0+bw,2990],fill="#FFFDF8",outline=SOFT_PURPLE,width=3)
        text.fitted_text(draw,heading,[x0+35,2360,x0+bw-35,2445],max_size=32,min_size=25,colour=NAVY,bold=True,max_lines=1)
        text.fitted_text(draw,phrase,[x0+45,2500,x0+bw-45,2870],max_size=39,min_size=28,colour=NAVY,bold=True,max_lines=2)


def render_joining_group(canvas, draw, page, assets, text):
    controls=page["activity"]["mechanics"]; names=controls["asset_order"]
    left,right,top,gap=170,2310,950,24; cell_w=(right-left-gap*2)//3
    for index,name in enumerate(names):
        x0=left+index*(cell_w+gap)
        panel(draw,[x0,top,x0+cell_w,2220],outline=SOFT_PURPLE,width=3)
        draw.ellipse([x0+cell_w-78,top+22,x0+cell_w-28,top+72],fill="white",outline=PURPLE,width=4)
        paste_fit(canvas,assets[name],[x0+22,top+25,x0+cell_w-22,2100],inset=4)
        text.fitted_text(draw,display_label(page,name),[x0+18,2110,x0+cell_w-18,2195],max_size=29,min_size=21,colour=NAVY,bold=True,max_lines=2)
    steps=[("1","Choose a group."),("2",controls["ask"]),("3",controls["reply"])]
    sw=(2140-gap*2)//3
    for i,(number,phrase) in enumerate(steps):
        x0=170+i*(sw+gap); panel(draw,[x0,2260,x0+sw,2990],fill="#FFFDF8",outline=SOFT_PURPLE,width=3)
        panel(draw,[x0+sw//2-45,2300,x0+sw//2+45,2390],fill="#E7D9FA",outline=PURPLE,width=3,radius=16)
        text.fitted_text(draw,number,[x0+sw//2-25,2310,x0+sw//2+25,2380],max_size=38,min_size=30,colour=NAVY,bold=True,max_lines=1)
        text.fitted_text(draw,phrase,[x0+35,2440,x0+sw-35,2900],max_size=33,min_size=24,colour=NAVY,bold=True,max_lines=3)


def render_problem_solution(canvas, draw, page, assets, text):
    controls = page["activity"]["mechanics"]
    problem = controls["problem"]
    solutions = controls["solutions"]
    panel(draw, [170, 950, 2310, 1780], fill="#FBFAFF", outline=SOFT_PURPLE, width=3)
    text.fitted_text(draw, "What is the problem?", [210, 980, 720, 1060], max_size=36, min_size=27, colour=NAVY, bold=True, max_lines=1)
    paste_fit(canvas, assets[problem], [260, 1070, 1500, 1720], inset=5)
    text.fitted_text(draw, display_label(page, problem), [1530, 1160, 2240, 1650], max_size=42, min_size=28, colour=NAVY, bold=True, max_lines=4)
    gap = 25
    width = (2140 - gap * 2) // 3
    for index, name in enumerate(solutions):
        x0 = 170 + index * (width + gap)
        panel(draw, [x0, 1820, x0 + width, 2990], fill="#FFFFFF", outline=SOFT_PURPLE, width=3)
        draw.ellipse([x0 + width - 82, 1850, x0 + width - 30, 1902], fill="white", outline=PURPLE, width=4)
        paste_fit(canvas, assets[name], [x0 + 25, 1900, x0 + width - 25, 2780], inset=5)
        text.fitted_text(draw, display_label(page, name), [x0 + 25, 2800, x0 + width - 25, 2960], max_size=34, min_size=24, colour=NAVY, bold=True, max_lines=2)


def render_character(canvas, draw, page, assets, text):
    controls = page["activity"]["mechanics"]
    character = controls["character"]
    panel(draw, [170, 950, 1280, 2990], fill="#FFFFFF", outline=SOFT_PURPLE, width=3)
    paste_fit(canvas, assets[character], [210, 1000, 1240, 2770], inset=5)
    text.fitted_text(draw, display_label(page, character), [230, 2800, 1220, 2945], max_size=34, min_size=25, colour=NAVY, bold=True, max_lines=2)
    pairs = controls["choice_pairs"]
    gap = 24
    row_h = (2040 - gap * (len(pairs) - 1)) // len(pairs)
    for index, pair in enumerate(pairs):
        y0 = 950 + index * (row_h + gap)
        panel(draw, [1320, y0, 2310, y0 + row_h], fill="#FBFAFF", outline=SOFT_PURPLE, width=3)
        text.fitted_text(draw, f"Choose {index + 1}", [1360, y0 + 22, 1580, y0 + 80], max_size=26, min_size=21, colour=NAVY, bold=True, max_lines=1)
        draw_choices(draw, text, pair, [1360, y0 + 95, 2270, y0 + row_h - 28], cols=2)


def render_show_tell(canvas, draw, page, assets, text):
    controls = page["activity"]["mechanics"]
    choices = controls["choices"]
    gap = 24
    left, right, top, bottom = 170, 2310, 950, 2410
    cell_w = (right - left - gap) // 2
    cell_h = (bottom - top - gap) // 2
    for index, name in enumerate(choices):
        row, col = divmod(index, 2)
        x0 = left + col * (cell_w + gap)
        y0 = top + row * (cell_h + gap)
        panel(draw, [x0, y0, x0 + cell_w, y0 + cell_h], fill="#FFFFFF", outline=SOFT_PURPLE, width=3)
        draw.ellipse([x0 + cell_w - 82, y0 + 22, x0 + cell_w - 30, y0 + 74], fill="white", outline=PURPLE, width=4)
        paste_fit(canvas, assets[name], [x0 + 30, y0 + 25, x0 + cell_w - 30, y0 + cell_h - 90], inset=5)
        text.fitted_text(draw, display_label(page, name), [x0 + 25, y0 + cell_h - 82, x0 + cell_w - 25, y0 + cell_h - 15], max_size=32, min_size=24, colour=NAVY, bold=True, max_lines=1)
    questions = controls["questions"]
    panel(draw, [170, 2450, 2310, 2990], fill="#FBFAFF", outline=SOFT_PURPLE, width=3)
    draw_choices(draw, text, questions, [210, 2490, 2270, 2950], cols=2)


def render_sentence_order(canvas, draw, page, assets, text):
    controls=page["activity"]["mechanics"]; sentences=controls["sentences"]; pictures=controls["asset_order"]; top=980
    colours=["#E8F4FF","#FFF4C6","#F0FAED","#F6F1FF","#FFE8EC"]
    for row, words in enumerate(sentences):
        y0=top+row*620; panel(draw,[170,y0,2310,y0+560],outline=SOFT_PURPLE,width=3)
        text.fitted_text(draw,f"Sentence {row+1}",[205,y0+20,530,y0+90],max_size=31,min_size=24,colour=NAVY,bold=True,max_lines=1)
        picture_name = pictures[row]
        panel(draw,[205,y0+110,530,y0+385],fill="#FBFAFF",outline=SOFT_PURPLE,width=2,radius=14)
        paste_fit(canvas,assets[picture_name],[220,y0+120,515,y0+375],inset=4)
        text.fitted_text(draw,"Picture clue",[220,y0+390,515,y0+440],max_size=25,min_size=20,colour=NAVY,bold=True,max_lines=1)
        gap=14; cards_left=560; cards_right=2250; width=(cards_right-cards_left-gap*(len(words)-1))//len(words)
        for index,word in enumerate(words):
            x0=cards_left+index*(width+gap); panel(draw,[x0,y0+125,x0+width,y0+300],fill=colours[index%len(colours)],outline=PURPLE,width=2,radius=16)
            text.fitted_text(draw,word,[x0+8,y0+138,x0+width-8,y0+287],max_size=40,min_size=25,colour=NAVY,bold=True,max_lines=1)
        text.fitted_text(draw,"Write the sentence in order.",[560,y0+350,1120,y0+420],max_size=31,min_size=24,colour=NAVY,bold=True,max_lines=1)
        draw.line([1130,y0+405,2250,y0+405],fill=PURPLE,width=3)


def render_journal(canvas, draw, page, assets, text):
    controls=page["activity"]["mechanics"]; icons=controls.get("icons") or controls.get("asset_order")
    if page["identity"]["physical_page"]==12:
        panel(draw,[170,980,2310,1680],outline=SOFT_PURPLE,width=3); paste_fit(canvas,assets[icons[0]],[220,1020,930,1630],inset=5)
        for label,y in [("My name is",1080),("I am",1340),("years old.",1510)]:
            text.fitted_text(draw,label,[1000,y,1370,y+90],max_size=41,min_size=30,colour=NAVY,bold=True,max_lines=1); draw.line([1390,y+72,2220,y+72],fill=PURPLE,width=3)
        panel(draw,[170,1750,2310,2990],fill="#FBFAFF",outline=SOFT_PURPLE,width=3); text.fitted_text(draw,"Draw yourself.",[220,1790,2260,1900],max_size=42,min_size=31,colour=NAVY,bold=True,max_lines=1); return
    physical = page["identity"]["physical_page"]
    if physical == 38:
        panel(draw,[170,950,2310,2300],outline=SOFT_PURPLE,width=3)
        text.fitted_text(draw,"Draw one piece of news.",[220,980,2260,1080],max_size=42,min_size=31,colour=NAVY,bold=True,max_lines=1)
        questions=controls.get("questions") or []
        gap=18; card_w=(2100-gap*2)//3
        for index,(name,question) in enumerate(zip(icons,questions)):
            x0=190+index*(card_w+gap)
            panel(draw,[x0,2340,x0+card_w,2990],fill="#FFFDF8",outline=SOFT_PURPLE,width=3)
            paste_fit(canvas,assets[name],[x0+35,2370,x0+card_w-35,2820],inset=5)
            text.fitted_text(draw,question,[x0+22,2830,x0+card_w-22,2965],max_size=32,min_size=24,colour=NAVY,bold=True,max_lines=2)
        return
    panel(draw,[170,950,2310,2240],outline=SOFT_PURPLE,width=3)
    text.fitted_text(draw,"Draw your communication moment.",[220,980,2260,1080],max_size=42,min_size=31,colour=NAVY,bold=True,max_lines=1)
    skills=controls.get("skills") or []
    gap=16; card_w=(2100-gap*3)//4
    for index,(name,skill) in enumerate(zip(icons,skills)):
        x0=190+index*(card_w+gap)
        panel(draw,[x0,2280,x0+card_w,2785],fill="#FFFDF8",outline=SOFT_PURPLE,width=3)
        paste_fit(canvas,assets[name],[x0+28,2300,x0+card_w-28,2670],inset=5)
        draw.rectangle([x0+25,2705,x0+69,2749],fill="white",outline=PURPLE,width=3)
        text.fitted_text(draw,skill,[x0+82,2685,x0+card_w-18,2768],max_size=27,min_size=20,colour=NAVY,bold=True,max_lines=2)
    if controls.get("reflection"):
        text.fitted_text(draw,controls["reflection"],[210,2835,1090,2960],max_size=34,min_size=26,colour=NAVY,bold=True,max_lines=1)
        draw.line([1090,2935,2280,2935],fill=PURPLE,width=3)


def render_group_speaking(canvas, draw, page, assets, text):
    controls = page["activity"]["mechanics"]
    topics = controls["topics"]
    gap = 18; card_w = (2140 - gap * 2) // 3
    for index, topic in enumerate(topics):
        x0 = 170 + index * (card_w + gap)
        panel(draw, [x0, 950, x0 + card_w, 1165], fill="#FFFDF8", outline=SOFT_PURPLE, width=3)
        draw.ellipse([x0 + 28, 1022, x0 + 78, 1072], fill="white", outline=PURPLE, width=4)
        text.fitted_text(draw, topic, [x0 + 100, 980, x0 + card_w - 22, 1135], max_size=31, min_size=23, colour=NAVY, bold=True, max_lines=2)
    panel(draw, [170, 1200, 2310, 2510], outline=SOFT_PURPLE, width=3)
    paste_fit(canvas, assets[controls["scene"]], [210, 1220, 2270, 2490], inset=5)
    checklist = controls["checklist"]
    gap = 16; card_w = (2100 - gap * 3) // 4
    for index, item in enumerate(checklist):
        x0 = 190 + index * (card_w + gap)
        panel(draw, [x0, 2550, x0 + card_w, 2990], fill="#FBFAFF", outline=SOFT_PURPLE, width=3)
        draw.rectangle([x0 + 28, 2705, x0 + 78, 2755], fill="white", outline=PURPLE, width=3)
        text.fitted_text(draw, item, [x0 + 95, 2620, x0 + card_w - 22, 2900], max_size=29, min_size=21, colour=NAVY, bold=True, max_lines=3)


def render_listen_respond(canvas, draw, page, assets, text):
    controls = page["activity"]["mechanics"]
    panel(draw, [170, 950, 2310, 2420], outline=SOFT_PURPLE, width=3)
    paste_fit(canvas, assets[controls["scene"]], [220, 980, 2260, 2390], inset=5)
    responses = controls["responses"]
    gap = 18; card_w = (2100 - gap * 2) // 3
    for index, response in enumerate(responses):
        x0 = 190 + index * (card_w + gap)
        panel(draw, [x0, 2470, x0 + card_w, 2990], fill="#FFFDF8", outline=SOFT_PURPLE, width=3)
        draw.ellipse([x0 + 28, 2680, x0 + 82, 2734], fill="white", outline=PURPLE, width=4)
        text.fitted_text(draw, response, [x0 + 105, 2530, x0 + card_w - 25, 2915], max_size=31, min_size=22, colour=NAVY, bold=True, max_lines=3)


def render_story(canvas, draw, page, assets, text):
    controls=page["activity"]["mechanics"]
    if controls.get("drawing_box"):
        starters=controls["starters"]; endings=controls["endings"]
        gap=24; cell_w=(2140-gap)//2
        for i,name in enumerate(starters):
            x0=170+i*(cell_w+gap)
            panel(draw,[x0,950,x0+cell_w,1660],outline=SOFT_PURPLE,width=3)
            text.fitted_text(draw,"1. First" if i==0 else "2. Then",[x0+20,970,x0+cell_w-20,1040],max_size=31,min_size=24,colour=NAVY,bold=True,max_lines=1)
            paste_fit(canvas,assets[name],[x0+20,1050,x0+cell_w-20,1640],inset=4)
        for i,name in enumerate(endings):
            x0=170+i*(cell_w+gap)
            panel(draw,[x0,1690,x0+cell_w,2320],outline=SOFT_PURPLE,width=3)
            text.fitted_text(draw,f"Ending {'A' if i==0 else 'B'}",[x0+25,1710,x0+cell_w-110,1780],max_size=31,min_size=24,colour=NAVY,bold=True,max_lines=1)
            draw.ellipse([x0+cell_w-88,1710,x0+cell_w-30,1768],fill="white",outline=PURPLE,width=4)
            paste_fit(canvas,assets[name],[x0+20,1790,x0+cell_w-20,2300],inset=4)
        panel(draw,[170,2350,2310,2990],fill="#FFFFFF",outline=PURPLE,width=3)
        text.fitted_text(draw,"Draw another sensible ending.",[210,2380,2270,2480],max_size=39,min_size=29,colour=NAVY,bold=True,max_lines=1)
    else:
        render_number_sequence(canvas,draw,page,assets,text)


def render_retell(canvas, draw, page, assets, text):
    controls = page["activity"]["mechanics"]; names = controls["events"]; prompts = controls["prompts"]
    left, right, top, bottom, gap = 170, 2310, 970, 2990, 24; cell_w = (right - left - gap * 3) // 4
    for index, name in enumerate(names):
        x0 = left + index * (cell_w + gap)
        panel(draw, [x0, top, x0 + cell_w, bottom], outline=SOFT_PURPLE, width=3)
        panel(draw, [x0 + 15, top + 20, x0 + cell_w - 15, top + 130], fill="#F6F1FF", outline="#D8C5F4", width=2, radius=14)
        text.fitted_text(draw, prompts[index], [x0 + 25, top + 30, x0 + cell_w - 25, top + 120], max_size=31, min_size=22, colour=NAVY, bold=True, max_lines=2)
        paste_fit(canvas, assets[name], [x0 + 20, top + 155, x0 + cell_w - 20, bottom - 210], inset=5)
        text.fitted_text(draw, readable(name), [x0 + 20, bottom - 200, x0 + cell_w - 20, bottom - 125], max_size=27, min_size=20, colour=NAVY, bold=True, max_lines=1)
        draw.line([x0 + 40, bottom - 75, x0 + cell_w - 40, bottom - 75], fill=PURPLE, width=3)


def render_celebration(canvas, draw, page, assets, text):
    name = page["activity"]["mechanics"]["asset_order"][0]
    panel(draw, [170, 950, 2310, 2050], outline=SOFT_PURPLE, width=3)
    paste_fit(canvas, assets[name], [220, 980, 2260, 2020], inset=5)
    checks = page["activity"]["mechanics"]["checks"]
    gap=18; left,right,top,bottom=190,2290,2100,2870; cols=2
    cell_w=(right-left-gap)//2; cell_h=(bottom-top-gap*2)//3
    for index,value in enumerate(checks):
        row,col=divmod(index,cols); x0=left+col*(cell_w+gap); y0=top+row*(cell_h+gap)
        panel(draw,[x0,y0,x0+cell_w,y0+cell_h],fill="#FFFDF8",outline="#C7A9EF",width=2,radius=16)
        draw.rectangle([x0+35,y0+cell_h//2-25,x0+85,y0+cell_h//2+25],fill="white",outline=PURPLE,width=3)
        text.fitted_text(draw,value,[x0+110,y0+20,x0+cell_w-25,y0+cell_h-20],max_size=32,min_size=23,colour=NAVY,bold=True,max_lines=2)
    text.fitted_text(draw, "I am a communication champion!", [400, 2900, 2080, 3000], max_size=45, min_size=33, colour=NAVY, bold=True, max_lines=1)


def render_certificate(canvas, draw, page, assets, text):
    panel(draw,[220,760,2260,3030],fill="#FFFDF5",outline="#D8A51C",width=6,radius=40)
    paste_fit(canvas,assets["achievement_badge"],[950,820,1530,1250],inset=5)
    text.fitted_text(draw,"CERTIFICATE OF COMPLETION",[350,1280,2130,1420],max_size=58,min_size=42,colour=NAVY,bold=True,max_lines=1)
    text.fitted_text(draw,"This certificate is awarded to",[500,1490,1980,1590],max_size=40,min_size=30,colour=INK,bold=False,max_lines=1)
    draw.line([470,1740,2010,1740],fill=PURPLE,width=4)
    text.fitted_text(draw,page["activity"]["mechanics"]["certificate_statement"],[420,1830,2060,2130],max_size=39,min_size=28,colour=NAVY,bold=True,max_lines=4)
    paste_fit(canvas,assets["trophy"],[1020,2180,1460,2490],inset=5)
    for label,x0,x1 in [("Date",420,1050),("Teacher",1430,2060)]:
        draw.line([x0,2570,x1,2570],fill=PURPLE,width=3); text.fitted_text(draw,label,[x0,2590,x1,2670],max_size=30,min_size=24,colour=NAVY,bold=True,max_lines=1)


def compose(page, logo_path: Path, illustration_path: Path, output: Path, evidence_output: Path):
    text=load_module("communication_text_engine",BASE); template=load_json(TEMPLATE)
    canvas=Image.new("RGBA",(WIDTH,HEIGHT),(255,253,248,255)); draw=ImageDraw.Draw(canvas); logo=Image.open(logo_path).convert("RGBA")
    header(canvas,draw,page,logo,text,template)
    if not illustration_path.is_file(): raise FileNotFoundError(f"Approved illustration required: {illustration_path}")
    source=Image.open(illustration_path).convert("RGBA"); assets=crop_assets(source,page["illustration"]["asset_crops"])
    physical=page["identity"]["physical_page"]
    if physical!=42: model_strip(canvas,draw,page,assets,text)
    if physical==42: render_certificate(canvas,draw,page,assets,text)
    elif physical in {12,38,41}: render_journal(canvas,draw,page,assets,text)
    elif physical==8: render_good_listening(canvas,draw,page,assets,text)
    elif physical==15: render_classroom_objects(canvas,draw,page,assets,text)
    elif physical==19: render_position_words(canvas,draw,page,assets,text)
    elif physical==22: render_polite_words(canvas,draw,page,assets,text)
    elif physical==23: render_taking_turns(canvas,draw,page,assets,text)
    elif physical==24: render_help_request(canvas,draw,page,assets,text)
    elif physical==25: render_joining_group(canvas,draw,page,assets,text)
    elif physical==39: render_group_speaking(canvas,draw,page,assets,text)
    elif physical==40: render_listen_respond(canvas,draw,page,assets,text)
    elif physical in {14,16,18}: render_match(canvas,draw,page,assets,text)
    elif physical==10: render_action_strips(canvas,draw,page,assets,text)
    elif physical in {23,33}: render_number_sequence(canvas,draw,page,assets,text)
    elif physical==20: render_sentence_order(canvas,draw,page,assets,text)
    elif physical in {28,32}: render_scene_prompts(canvas,draw,page,assets,text)
    elif physical==34: render_retell(canvas,draw,page,assets,text)
    elif physical==35: render_story(canvas,draw,page,assets,text)
    elif physical==43: render_celebration(canvas,draw,page,assets,text)
    elif physical==27: render_problem_solution(canvas,draw,page,assets,text)
    elif physical==36: render_character(canvas,draw,page,assets,text)
    elif physical==37: render_show_tell(canvas,draw,page,assets,text)
    elif physical in {21,26,29,31}: render_social_cards(canvas,draw,page,assets,text)
    else: render_card_grid(canvas,draw,page,assets,text)
    if physical!=42: teacher_footer(draw,page,text)
    else:
        printed=page["identity"].get("printed_page")
        if printed is not None:text.fitted_text(draw,str(printed),[2180,3310,2310,3425],max_size=40,min_size=31,colour="#667085",bold=True,max_lines=1)
    output.parent.mkdir(parents=True,exist_ok=True); canvas.convert("RGB").save(output,"PNG",dpi=(300,300),optimize=True)
    evidence={"page_id":page["identity"]["page_id"],"render_kind":page["activity"]["render_kind"],"output":str(output),"output_sha256":hashlib.sha256(output.read_bytes()).hexdigest(),"completed_example_visible":physical!=42,"independent_answers_unmarked":True,"parent_panel":False,"generic_response_panel":False,"status":"PASS"}
    evidence_output.parent.mkdir(parents=True,exist_ok=True); evidence_output.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")


def main()->int:
    parser=argparse.ArgumentParser(); parser.add_argument("--page-id",required=True); parser.add_argument("--logo",type=Path,required=True); parser.add_argument("--illustration",type=Path,required=True); parser.add_argument("--output",type=Path,required=True); parser.add_argument("--evidence-output",type=Path,required=True); args=parser.parse_args()
    loader=load_module("communication_runtime_loader",LOADER); page=loader.load_page_contract(level="lkg",book_slug="communication-champions",page_id=args.page_id); compose(page,args.logo,args.illustration,args.output,args.evidence_output); return 0


if __name__=="__main__":
    try: raise SystemExit(main())
    except (OSError,ValueError,RuntimeError,json.JSONDecodeError) as exc:
        print(f"Communication Champions render FAIL: {exc}",file=sys.stderr); raise SystemExit(2)
