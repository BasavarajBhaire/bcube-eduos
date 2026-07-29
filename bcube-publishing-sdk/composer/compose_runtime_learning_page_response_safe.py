#!/usr/bin/env python3
"""Full-book Early Maths composer with response-safe choice rendering.

Use this entry point for P022 onward. Any independent choice with visible text is
rendered without an enclosing answer circle. Blank connector dots and writing
boxes remain available for mechanics that genuinely require them.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
BASE_COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_runtime_learning_page.py"
POLICY_PATH = ROOT / "bcube-publishing-sdk/composer/early_maths_response_policy.py"
TEXT_ENGINE_PATH = ROOT / "bcube-publishing-sdk/composer/compose_learning_page_v2.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


base = load_module("early_maths_full_book_base", BASE_COMPOSER)
policy = load_module("early_maths_response_policy_full", POLICY_PATH)
text_engine = load_module("early_maths_full_book_text", TEXT_ENGINE_PATH)
original_circle = base.circle


def response_safe_circle(draw, text_base, template, cx, cy, text=""):
    """Text choices stay plain; empty connector/response markers stay circular."""
    if text not in (None, ""):
        policy.draw_plain_choice_with_base(
            text_base,
            draw,
            template,
            text,
            [cx - 72, cy - 64, cx + 72, cy + 64],
            size=42,
        )
        return
    original_circle(draw, text_base, template, cx, cy, text)


base.circle = response_safe_circle


# P022-P044 are not generic asset grids.  Each page below renders the exact
# response mechanic described by its contract.  The shared helpers also trim
# opaque white padding from the approved Work Mode assets before placement.
NAVY = "#183E67"
PURPLE = "#7140A0"
SOFT_PURPLE = "#8E5AC7"
GOLD = "#FFF1B8"
BLUE = "#E8F4FF"
GREEN = "#EFF9EA"
INK = "#333333"
TASK_TOP = 930
TASK_BOTTOM = 2990


def trim_visible(image: Image.Image) -> Image.Image:
    source = image.convert("RGBA")
    rgb = source.convert("RGB")
    difference = ImageChops.difference(rgb, Image.new("RGB", rgb.size, "white")).convert("L")
    visible = difference.point(lambda value: 255 if value > 7 else 0)
    alpha = source.getchannel("A").point(lambda value: 255 if value > 8 else 0)
    visible = ImageChops.multiply(visible, alpha)
    box = visible.getbbox()
    return source.crop(box) if box else source


def late_paste_fit(canvas, image, box, inset=12):
    x0, y0, x1, y1 = [int(value) for value in box]
    x0 += inset; y0 += inset; x1 -= inset; y1 -= inset
    if x1 <= x0 or y1 <= y0:
        return
    source = trim_visible(image)
    scale = min((x1 - x0) / source.width, (y1 - y0) / source.height)
    source = source.resize(
        (max(1, round(source.width * scale)), max(1, round(source.height * scale))),
        Image.Resampling.LANCZOS,
    )
    x = x0 + (x1 - x0 - source.width) // 2
    y = y0 + (y1 - y0 - source.height) // 2
    canvas.paste(source, (x, y), source)


OBJECT_NAME_OVERRIDES = {
    "pattern_stars": "red star - blue star",
    "pattern_shapes": "yellow circle - green square",
    "pattern_leaf_flower": "leaf - flower - flower",
    "row_apples_bananas": "apple - banana",
    "row_circle_triangles": "circle - triangle - triangle",
    "row_coloured_cubes": "red cube - blue cube - green cube",
    "row_small_big_stars": "small star - big star",
    "mouse_to_cheese": "mouse to cheese",
    "bee_to_flower": "bee to flower",
    "car_to_garage": "car to garage",
    "dog_next_to_boy": "dog beside boy",
    "morning_wake_up": "morning",
    "afternoon_play": "afternoon",
    "night_sleep": "night",
    "problem_missing_ball": "children and balls",
    "problem_share_apples": "children and apples",
    "problem_bus_seats": "bus seats",
}


def object_name(asset_name: str) -> str:
    """Turn a semantic asset identifier into a simple child-facing label."""
    if asset_name in OBJECT_NAME_OVERRIDES:
        return OBJECT_NAME_OVERRIDES[asset_name]
    parts = asset_name.split("_")
    if parts and parts[-1].isdigit():
        parts = parts[:-1]
    for prefix in ("shape", "object", "graph", "review", "solid"):
        if parts and parts[0] == prefix:
            parts = parts[1:]
            break
    return " ".join(parts).replace("tin can", "can").strip()


def object_label(draw, text_base, asset_name: str, box, *, value: str | None = None, size: int = 29):
    text_base.fitted_text(
        draw,
        value or object_name(asset_name),
        box,
        max_size=size,
        min_size=max(21, size - 7),
        colour=NAVY,
        bold=True,
        max_lines=1,
    )


def route_endpoint_crops(asset_name: str, image: Image.Image) -> tuple[Image.Image, Image.Image]:
    """Extract complete route endpoints while discarding the generated route."""
    source = image.convert("RGBA")
    width, height = source.size
    settings = {
        "mouse_to_cheese": (0.22, 0.81, 0.19, 0.83),
        "bee_to_flower": (0.19, 0.815, None, None),
        "car_to_garage": (0.25, 0.753, None, None),
    }
    left_end, right_start, clear_left_from, clear_right_to = settings[asset_name]
    left = source.crop((0, 0, round(width * left_end), height))
    right = source.crop((round(width * right_start), 0, width, height))
    route_y = height // 2
    half_band = max(18, round(height * 0.035))
    if clear_left_from is not None:
        ImageDraw.Draw(left).rectangle(
            [round(width * clear_left_from), route_y - half_band, left.width, route_y + half_band],
            fill="white",
        )
    if clear_right_to is not None:
        ImageDraw.Draw(right).rectangle(
            [0, route_y - half_band, round(width * (clear_right_to - right_start)), route_y + half_band],
            fill="white",
        )
    return left, right


base.paste_fit = late_paste_fit


def late_header(canvas, draw, page, book_title, logo, text_base, template):
    colours = template["colours"]
    typography = template["typography"]
    logo = logo.convert("RGBA")
    logo.thumbnail((290, 205), Image.Resampling.LANCZOS)
    canvas.paste(logo, (105 + (290 - logo.width) // 2, 35 + (205 - logo.height) // 2), logo)
    text_base.brand_title(draw, [book_title], [450, 42, 2320, 142], colours, typography)
    text_base.fitted_text(
        draw, page["identity"]["title"], [440, 140, 2320, 292],
        max_size=78, min_size=52, colour=colours["navy"], bold=True, max_lines=2,
    )
    base.panel(draw, [150, 320, 2330, 465], fill=BLUE, outline="#1768B3", width=3)
    text_base.fitted_text(
        draw, "Learning goal: " + page["learning"]["objective"], [190, 334, 2290, 451],
        max_size=49, min_size=34, colour=colours["navy"], bold=True, max_lines=2,
    )
    base.panel(draw, [150, 500, 2330, 665], fill=GOLD, outline="#E1A81C", width=3)
    text_base.fitted_text(
        draw, page["learning"]["instruction"], [190, 515, 2290, 650],
        max_size=55, min_size=37, colour=colours["line"], bold=True, max_lines=2,
    )


def late_teacher(draw, page, text_base, template):
    if page["identity"].get("page_type") in {"back_cover", "certificate"} or page["identity"].get("title") == "Certificate":
        return
    base.panel(draw, [150, 3070, 2300, 3270], fill=GREEN, outline="#5F9D50", width=3)
    text_base.fitted_text(draw, "TEACHER CUE", [180, 3092, 520, 3248], max_size=38, min_size=31,
                          colour=NAVY, bold=True, max_lines=1)
    text_base.fitted_text(draw, page["guidance"]["teacher_cue"], [550, 3090, 2260, 3250],
                          max_size=40, min_size=29, colour=INK, align="left", max_lines=3)


base.header = late_header
base.teacher = late_teacher


def model_panel(draw, text_base, template):
    base.panel(draw, [170, 700, 2310, 890], fill="#F5F1FF", outline=SOFT_PURPLE, width=3, radius=22)
    base.panel(draw, [195, 720, 535, 870], fill="#E7D9FA", outline=SOFT_PURPLE, width=2, radius=18)
    text_base.fitted_text(draw, "COMPLETED\nEXAMPLE", [220, 735, 510, 855], max_size=35, min_size=27,
                          colour=NAVY, bold=True, max_lines=2)
    return [565, 715, 2280, 875]


def draw_choice_words(draw, text_base, words, box, correct=None):
    x0, y0, x1, y1 = box
    gap = 34
    width = (x1 - x0 - gap * (len(words) - 1)) // len(words)
    for index, word in enumerate(words):
        left = x0 + index * (width + gap)
        target = [left, y0, left + width, y1]
        text_base.fitted_text(draw, word, target, max_size=42, min_size=31, colour=NAVY, bold=True, max_lines=1)
        if correct == word:
            draw.ellipse([left - 8, y0 - 2, left + width + 8, y1 + 2], outline=PURPLE, width=5)


def draw_simple_model(canvas, draw, page, assets, text_base, template):
    area = model_panel(draw, text_base, template)
    page_id = page["identity"]["prompt_id"] if "prompt_id" in page["identity"] else page.get("page_id", "")
    mechanic = page["activity"]["mechanic"]
    x0, y0, x1, y1 = area
    cy = (y0 + y1) // 2
    if mechanic == "match-3d-solid-to-object":
        # Use an external cuboid-to-book example so no independent pair is solved.
        draw.polygon([(x0 + 45, cy - 45), (x0 + 155, cy - 45), (x0 + 205, cy - 75),
                      (x0 + 95, cy - 75)], fill="#8E62CF", outline=NAVY)
        draw.polygon([(x0 + 45, cy - 45), (x0 + 155, cy - 45), (x0 + 155, cy + 50),
                      (x0 + 45, cy + 50)], fill="#7140A0", outline=NAVY)
        draw.polygon([(x0 + 155, cy - 45), (x0 + 205, cy - 75), (x0 + 205, cy + 20),
                      (x0 + 155, cy + 50)], fill="#A987DE", outline=NAVY)
        draw.ellipse([x0 + 240, cy - 13, x0 + 266, cy + 13], fill="white", outline=PURPLE, width=3)
        draw.line([x0 + 266, cy, x0 + 500, cy], fill=PURPLE, width=5)
        draw.ellipse([x0 + 500, cy - 13, x0 + 526, cy + 13], fill="white", outline=PURPLE, width=3)
        draw.rounded_rectangle([x0 + 555, cy - 62, x0 + 750, cy + 62], radius=12,
                               fill="#F25E5E", outline=NAVY, width=3)
        draw.line([x0 + 585, cy - 55, x0 + 585, cy + 55], fill="#FFD778", width=10)
        text_base.fitted_text(draw, "same solid shape", [x0 + 800, y0 + 25, x1 - 20, y1 - 25],
                              max_size=40, min_size=30, colour=NAVY, bold=True, max_lines=1)
    elif mechanic == "shape-hunt-scene":
        draw.ellipse([x0 + 45, cy - 45, x0 + 135, cy + 45], fill="#FFD522", outline=NAVY, width=3)
        draw.rectangle([x0 + 175, cy - 45, x0 + 265, cy + 45], fill="#2381F2", outline=NAVY, width=3)
        draw.polygon([(x0 + 350, cy - 50), (x0 + 295, cy + 45), (x0 + 405, cy + 45)],
                     fill="#49B83D", outline=NAVY)
        draw.ellipse([x0 + 155, cy - 65, x0 + 285, cy + 65], outline=PURPLE, width=5)
        text_base.fitted_text(draw, "Find and circle the blue square.", [x0 + 500, y0 + 25, x1 - 30, y1 - 25],
                              max_size=44, min_size=32, colour=NAVY, bold=True, max_lines=1)
    elif mechanic == "identify-repeating-pattern":
        colours = ["#F12B2B", "#2381F2", "#F12B2B", "#2381F2"]
        for i, colour in enumerate(colours):
            draw.ellipse([x0 + 75 + i * 130, cy - 42, x0 + 159 + i * 130, cy + 42], fill=colour, outline=NAVY, width=2)
        draw.rounded_rectangle([x0 + 55, cy - 62, x0 + 310, cy + 62], radius=18, outline="#D48B00", width=5)
        text_base.fitted_text(draw, "The red-blue unit repeats.", [x0 + 650, y0 + 25, x1 - 30, y1 - 25],
                              max_size=42, min_size=31, colour=NAVY, bold=True, max_lines=1)
    elif mechanic == "complete-repeating-pattern":
        colours = ["#F12B2B", "#2381F2", "#F12B2B", "#2381F2"]
        for i, colour in enumerate(colours):
            draw.ellipse([x0 + 55 + i * 115, cy - 38, x0 + 131 + i * 115, cy + 38], fill=colour, outline=NAVY, width=2)
        draw.line([x0 + 545, cy, x0 + 690, cy], fill=PURPLE, width=5)
        draw.polygon([(x0 + 690, cy), (x0 + 650, cy - 25), (x0 + 650, cy + 25)], fill=PURPLE)
        draw.ellipse([x0 + 745, cy - 45, x0 + 835, cy + 45], fill="#F12B2B", outline=PURPLE, width=5)
        text_base.fitted_text(draw, "red comes next", [x0 + 885, y0 + 25, x1 - 25, y1 - 25],
                              max_size=42, min_size=31, colour=NAVY, bold=True, max_lines=1)
    elif mechanic == "position-word-choice":
        draw.rectangle([x0 + 70, cy, x0 + 300, cy + 50], fill="#B9773E", outline=NAVY, width=3)
        draw.line([x0 + 100, cy + 50, x0 + 100, cy + 72], fill=NAVY, width=6)
        draw.line([x0 + 270, cy + 50, x0 + 270, cy + 72], fill=NAVY, width=6)
        draw.ellipse([x0 + 145, cy - 70, x0 + 225, cy + 10], fill="#F12B2B", outline=NAVY, width=3)
        draw_choice_words(draw, text_base, ["on", "under", "in"], [x0 + 380, y0 + 45, x1 - 35, y1 - 45], correct="on")
    elif mechanic == "follow-direction-path":
        draw.ellipse([x0 + 75, cy - 32, x0 + 139, cy + 32], fill="#F5A623", outline=NAVY, width=2)
        for i in range(6):
            px = x0 + 210 + i * 105
            draw.ellipse([px - 8, cy - 8, px + 8, cy + 8], fill=PURPLE)
        draw.polygon([(x0 + 880, cy), (x0 + 820, cy - 35), (x0 + 820, cy + 35)], fill=PURPLE)
        text_base.fitted_text(draw, "Trace from start to finish.", [x0 + 960, y0 + 25, x1 - 25, y1 - 25],
                              max_size=40, min_size=29, colour=NAVY, bold=True, max_lines=1)
    elif mechanic == "direction-word-choice":
        draw.line([x0 + 120, cy + 55, x0 + 120, cy - 55], fill="#2381F2", width=18)
        draw.polygon([(x0 + 120, cy - 75), (x0 + 80, cy - 25), (x0 + 160, cy - 25)], fill="#2381F2")
        draw.line([x0 + 260, cy - 55, x0 + 260, cy + 55], fill="#F12B2B", width=18)
        draw.polygon([(x0 + 260, cy + 75), (x0 + 220, cy + 25), (x0 + 300, cy + 25)], fill="#F12B2B")
        draw_choice_words(draw, text_base, ["up", "down"], [x0 + 420, y0 + 43, x0 + 1030, y1 - 43], correct="up")
        text_base.fitted_text(draw, "The blue arrow points up.", [x0 + 1080, y0 + 25, x1 - 20, y1 - 25],
                              max_size=40, min_size=28, colour=NAVY, bold=True, max_lines=1)
    elif mechanic in {"big-small", "tall-short", "heavy-light", "long-short", "full-empty", "capacity"}:
        prompt = page["activity"]["mechanics"]["items"][0]["prompt"]
        if mechanic in {"big-small", "capacity"}:
            draw.ellipse([x0 + 45, cy - 62, x0 + 169, cy + 62], fill="#2381F2", outline=NAVY, width=3)
            draw.ellipse([x0 + 230, cy - 32, x0 + 294, cy + 32], fill="#2381F2", outline=NAVY, width=3)
            draw.ellipse([x0 + 25, cy - 78, x0 + 190, cy + 78], outline=PURPLE, width=5)
        elif mechanic == "tall-short":
            draw.rectangle([x0 + 65, cy - 70, x0 + 135, cy + 70], fill="#49B83D", outline=NAVY, width=3)
            draw.rectangle([x0 + 220, cy - 30, x0 + 290, cy + 70], fill="#49B83D", outline=NAVY, width=3)
            draw.ellipse([x0 + 35, cy - 82, x0 + 165, cy + 82], outline=PURPLE, width=5)
        elif mechanic == "long-short":
            draw.rectangle([x0 + 35, cy - 18, x0 + 260, cy + 18], fill="#2381F2", outline=NAVY, width=3)
            draw.rectangle([x0 + 320, cy - 18, x0 + 425, cy + 18], fill="#2381F2", outline=NAVY, width=3)
            draw.ellipse([x0 + 15, cy - 55, x0 + 280, cy + 55], outline=PURPLE, width=5)
        elif mechanic == "full-empty":
            draw.rectangle([x0 + 55, cy - 55, x0 + 145, cy + 60], fill="#62B8F3", outline=NAVY, width=3)
            draw.rectangle([x0 + 210, cy - 55, x0 + 300, cy + 60], fill="white", outline=NAVY, width=3)
            draw.ellipse([x0 + 30, cy - 75, x0 + 170, cy + 78], outline=PURPLE, width=5)
        else:
            draw.rounded_rectangle([x0 + 55, cy - 55, x0 + 155, cy + 55], radius=12, fill="#777777", outline=NAVY, width=3)
            draw.polygon([(x0 + 230, cy), (x0 + 285, cy - 40), (x0 + 285, cy + 40)], fill="#DDEEFF", outline=NAVY)
            draw.ellipse([x0 + 25, cy - 75, x0 + 180, cy + 75], outline=PURPLE, width=5)
        text_base.fitted_text(draw, prompt, [x0 + 520, y0 + 22, x1 - 20, y1 - 22],
                              max_size=40, min_size=29, colour=NAVY, bold=True, max_lines=2)
    elif mechanic == "daily-routine-order":
        # Unrelated build-up example: one, two and three blocks.
        for stage in range(1, 4):
            left = x0 + 40 + (stage - 1) * 325
            for block in range(stage):
                draw.rectangle([left + block * 58, cy - 25, left + 50 + block * 58, cy + 25],
                               fill=["#F25E5E", "#2381F2", "#49B83D"][block], outline=NAVY, width=2)
            text_base.fitted_text(draw, str(stage), [left + 185, cy - 42, left + 255, cy + 42],
                                  max_size=47, min_size=37, colour=NAVY, bold=True, max_lines=1)
    elif mechanic in {"sort-by-one-attribute", "classify-familiar-items"}:
        label = "RED" if mechanic == "sort-by-one-attribute" else "FRUITS"
        if mechanic == "sort-by-one-attribute":
            draw.polygon([(x0 + 145, cy - 62), (x0 + 210, cy + 52), (x0 + 80, cy + 52)],
                         fill="#F12B2B", outline=NAVY)
        else:
            draw.ellipse([x0 + 80, cy - 58, x0 + 200, cy + 58], fill="#F2B33D", outline=NAVY, width=3)
            draw.line([x0 + 140, cy - 60, x0 + 155, cy - 85], fill="#49B83D", width=8)
        draw.line([x0 + 300, cy, x0 + 620, cy], fill=PURPLE, width=5)
        draw.polygon([(x0 + 620, cy), (x0 + 575, cy - 28), (x0 + 575, cy + 28)], fill=PURPLE)
        base.panel(draw, [x0 + 690, y0 + 24, x0 + 1040, y1 - 24], fill=BLUE, outline="#1768B3", width=3)
        text_base.fitted_text(draw, label, [x0 + 720, y0 + 45, x0 + 1010, y1 - 45], max_size=43, min_size=32,
                              colour=NAVY, bold=True, max_lines=1)
    elif mechanic == "read-picture-graph":
        for i in range(3):
            left = x0 + 60 + i * 145
            draw.ellipse([left, cy - 46, left + 92, cy + 46], fill="#FFD522", outline=NAVY, width=3)
        text_base.fitted_text(draw, "3 circles", [x0 + 650, y0 + 30, x1 - 25, y1 - 30], max_size=44, min_size=32,
                              colour=NAVY, bold=True, max_lines=1)
    elif mechanic in {"mixed-maths-problems", "mixed-maths-review"}:
        for i in range(2):
            draw.ellipse([x0 + 70 + i * 115, cy - 36, x0 + 142 + i * 115, cy + 36], fill="#F12B2B", outline=NAVY, width=2)
        text_base.fitted_text(draw, "2 objects", [x0 + 390, y0 + 30, x1 - 25, y1 - 30], max_size=44, min_size=32,
                              colour=NAVY, bold=True, max_lines=1)
    elif mechanic == "maths-around-me-find":
        draw.ellipse([x0 + 45, cy - 42, x0 + 129, cy + 42], fill="#F12B2B", outline=NAVY, width=3)
        draw.rectangle([x0 + 170, cy - 42, x0 + 254, cy + 42], fill="#2381F2", outline=NAVY, width=3)
        draw.polygon([(x0 + 345, cy - 48), (x0 + 292, cy + 42), (x0 + 398, cy + 42)], fill="#49B83D", outline=NAVY)
        draw.ellipse([x0 + 150, cy - 62, x0 + 275, cy + 62], outline=PURPLE, width=5)
        text_base.fitted_text(draw, "Find and circle the blue square.", [x0 + 500, y0 + 25, x1 - 25, y1 - 25],
                              max_size=44, min_size=31, colour=NAVY, bold=True, max_lines=1)


def full_width_rows(count, top=TASK_TOP, bottom=TASK_BOTTOM, gap=24):
    height = (bottom - top - gap * (count - 1)) // count
    return [[170, top + i * (height + gap), 2310, top + i * (height + gap) + height] for i in range(count)]


def late_render_match(canvas, draw, page, assets, text_base, template):
    draw_simple_model(canvas, draw, page, assets, text_base, template)
    mechanics = page["activity"]["mechanics"]
    left_names = mechanics["left"]
    right_names = mechanics["right"]
    rows = full_width_rows(4)
    for index, box in enumerate(rows):
        y0, y1 = box[1], box[3]
        base.panel(draw, box, outline=SOFT_PURPLE, width=3)
        late_paste_fit(canvas, assets[left_names[index]], [210, y0 + 8, 760, y1 - 52], 2)
        object_label(draw, text_base, left_names[index], [210, y1 - 55, 760, y1 - 8])
        draw.ellipse([820, (y0 + y1)//2 - 16, 852, (y0 + y1)//2 + 16], fill="white", outline=PURPLE, width=4)
        draw.ellipse([1628, (y0 + y1)//2 - 16, 1660, (y0 + y1)//2 + 16], fill="white", outline=PURPLE, width=4)
        late_paste_fit(canvas, assets[right_names[index]], [1710, y0 + 8, 2250, y1 - 52], 2)
        object_label(draw, text_base, right_names[index], [1710, y1 - 55, 2250, y1 - 8])


def late_render_hero_targets(canvas, draw, page, assets, text_base, template):
    mechanic = page["activity"]["mechanic"]
    if mechanic == "maths-reflection-choice":
        base.panel(draw, [190, 720, 2290, 2560], outline=SOFT_PURPLE, width=3)
        late_paste_fit(canvas, assets["maths_explorer_celebration"], [240, 760, 2240, 2510], 5)
        prompts = ["I can count.", "I can find shapes.", "I can make patterns."]
        for i, prompt in enumerate(prompts):
            left = 210 + i * 700
            draw.rectangle([left, 2690, left + 72, 2762], fill="white", outline=PURPLE, width=4)
            text_base.fitted_text(draw, prompt, [left + 95, 2655, left + 625, 2800], max_size=39, min_size=29,
                                  colour=NAVY, bold=True, align="left", max_lines=2)
        return
    draw_simple_model(canvas, draw, page, assets, text_base, template)
    if mechanic == "shape-hunt-scene":
        base.panel(draw, [190, TASK_TOP, 2290, 2440], outline=SOFT_PURPLE, width=3)
        late_paste_fit(canvas, assets["main_playground_scene"], [220, TASK_TOP + 25, 2260, 2415], 4)
        labels = ["circle", "square", "triangle", "rectangle"]
        w = 500
        for i, label in enumerate(labels):
            left = 190 + i * 530
            base.panel(draw, [left, 2490, left + w, 2990], fill="#FAF8FF", outline=SOFT_PURPLE, width=3)
            cx = left + w // 2
            if label == "circle":
                draw.ellipse([cx - 95, 2550, cx + 95, 2740], fill="#FFD522", outline=NAVY, width=4)
            elif label == "square":
                draw.rectangle([cx - 95, 2550, cx + 95, 2740], fill="#2381F2", outline=NAVY, width=4)
            elif label == "triangle":
                draw.polygon([(cx, 2535), (cx - 110, 2740), (cx + 110, 2740)], fill="#49B83D", outline=NAVY)
            else:
                draw.rectangle([cx - 135, 2580, cx + 135, 2720], fill="#F25E5E", outline=NAVY, width=4)
            text_base.fitted_text(draw, label, [left + 20, 2850, left + w - 20, 2975], max_size=34, min_size=25,
                                  colour=NAVY, bold=True, max_lines=2)
    elif mechanic == "maths-around-me-find":
        base.panel(draw, [190, TASK_TOP, 2290, 2580], outline=SOFT_PURPLE, width=3)
        late_paste_fit(canvas, assets["maths_around_me_scene"], [220, TASK_TOP + 20, 2260, 2560], 3)
        prompts = ["Find number 5", "Find the clock", "Find the red-blue pattern", "Find big and small trees"]
        for i, prompt in enumerate(prompts):
            left = 190 + (i % 2) * 1060
            top = 2630 + (i // 2) * 155
            draw.ellipse([left, top + 26, left + 78, top + 104], fill="#E7D9FA", outline=PURPLE, width=4)
            text_base.fitted_text(draw, str(i + 1), [left + 12, top + 38, left + 66, top + 92], max_size=34, min_size=28,
                                  colour=NAVY, bold=True, max_lines=1)
            text_base.fitted_text(draw, prompt, [left + 105, top, left + 990, top + 125], max_size=39, min_size=30,
                                  colour=NAVY, bold=True, align="left", max_lines=2)


def late_render_rows(canvas, draw, page, assets, text_base, template, mode="sequence"):
    mechanic = page["activity"]["mechanic"]
    draw_simple_model(canvas, draw, page, assets, text_base, template)
    names = base.asset_order(page)
    rows = full_width_rows(len(names))
    if mechanic == "identify-repeating-pattern":
        for name, box in zip(names, rows):
            base.panel(draw, box, outline=SOFT_PURPLE, width=3)
            late_paste_fit(canvas, assets[name], [box[0] + 45, box[1] + 25, box[2] - 390, box[3] - 72], 2)
            object_label(draw, text_base, name, [box[0] + 45, box[3] - 72, box[2] - 390, box[3] - 20], size=27)
            text_base.fitted_text(draw, "Draw next:", [box[2] - 350, box[1] + 45, box[2] - 65, box[1] + 125],
                                  max_size=30, min_size=24, colour=NAVY, bold=True, max_lines=1)
            base.panel(draw, [box[2] - 320, box[1] + 145, box[2] - 90, box[3] - 95],
                       fill="#FFF9DE", outline="#D9A91B", width=4, radius=18)
        return
    if mechanic == "complete-repeating-pattern":
        for name, box in zip(names, rows):
            base.panel(draw, box, outline=SOFT_PURPLE, width=3)
            late_paste_fit(canvas, assets[name], [box[0] + 45, box[1] + 25, box[2] - 45, box[3] - 72], 2)
            object_label(draw, text_base, name, [box[0] + 45, box[3] - 72, box[2] - 45, box[3] - 20], size=27)
        return
    if mechanic == "follow-direction-path":
        endpoint_names = {
            "mouse_to_cheese": ("mouse", "cheese"),
            "bee_to_flower": ("bee", "flower"),
            "car_to_garage": ("car", "garage"),
        }
        for name, box in zip(names, rows):
            base.panel(draw, box, outline=SOFT_PURPLE, width=3)
            left_crop, right_crop = route_endpoint_crops(name, assets[name])
            late_paste_fit(canvas, left_crop, [box[0] + 40, box[1] + 35, box[0] + 500, box[3] - 85], 2)
            late_paste_fit(canvas, right_crop, [box[2] - 500, box[1] + 35, box[2] - 40, box[3] - 85], 2)
            route_y = (box[1] + box[3]) // 2
            for dot in range(10):
                cx = box[0] + 560 + dot * ((box[2] - box[0] - 1120) // 9)
                draw.ellipse([cx - 12, route_y - 12, cx + 12, route_y + 12], fill=PURPLE)
            left_label, right_label = endpoint_names[name]
            object_label(draw, text_base, name, [box[0] + 40, box[3] - 82, box[0] + 500, box[3] - 20], value=left_label)
            object_label(draw, text_base, name, [box[2] - 500, box[3] - 82, box[2] - 40, box[3] - 20], value=right_label)
        return
    if mechanic == "daily-routine-order":
        for name, box in zip(names, rows):
            base.panel(draw, box, outline=SOFT_PURPLE, width=3)
            late_paste_fit(canvas, assets[name], [box[0] + 35, box[1] + 20, box[2] - 330, box[3] - 85], 2)
            object_label(draw, text_base, name, [box[0] + 35, box[3] - 80, box[2] - 330, box[3] - 25])
            base.panel(draw, [box[2] - 250, (box[1] + box[3])//2 - 72, box[2] - 105, (box[1] + box[3])//2 + 72],
                       fill="#FFF9DE", outline="#D9A91B", width=4, radius=18)


def scaled_region(box, factor, *, bottom=True):
    x0, y0, x1, y1 = box
    width = x1 - x0
    height = y1 - y0
    new_width = width * factor
    new_height = height * factor
    left = x0 + (width - new_width) / 2
    top = y1 - new_height if bottom else y0 + (height - new_height) / 2
    return [left, top, left + new_width, top + new_height]


def late_render_comparison(canvas, draw, page, assets, text_base, template):
    mechanic = page["activity"]["mechanic"]
    draw_simple_model(canvas, draw, page, assets, text_base, template)
    if mechanic == "position-word-choice":
        items = page["activity"]["mechanics"]["items"]
        boxes = []
        for row in range(2):
            for col in range(3):
                boxes.append([170 + col * 720, TASK_TOP + row * 1035, 850 + col * 720, TASK_TOP + row * 1035 + 1005])
        for item, box in zip(items, boxes):
            base.panel(draw, box, outline=SOFT_PURPLE, width=3)
            late_paste_fit(canvas, assets[item["asset"]], [box[0] + 20, box[1] + 20, box[2] - 20, box[3] - 230], 2)
            object_label(draw, text_base, item["asset"], [box[0] + 25, box[3] - 225, box[2] - 25, box[3] - 175], size=26)
            draw_choice_words(draw, text_base, item["choices"], [box[0] + 25, box[3] - 145, box[2] - 25, box[3] - 45])
        return
    items = page["activity"]["mechanics"]["items"]
    rows = full_width_rows(len(items))
    for item, box in zip(items, rows):
        base.panel(draw, box, outline=SOFT_PURPLE, width=3)
        text_base.fitted_text(draw, item["prompt"], [box[0] + 30, box[1] + 12, box[2] - 30, box[1] + 92],
                              max_size=39, min_size=30, colour=NAVY, bold=True, max_lines=1)
        mid = (box[0] + box[2]) // 2
        left_region = [box[0] + 45, box[1] + 105, mid - 35, box[3] - 25]
        right_region = [mid + 35, box[1] + 105, box[2] - 45, box[3] - 25]
        if mechanic == "big-small":
            right_region = scaled_region(right_region, 0.58)
        elif mechanic == "tall-short":
            right_region = scaled_region(right_region, 0.64)
        elif mechanic == "long-short":
            # Asset-fit normalisation otherwise stretches both members of the
            # pair to the same width. Keep the short object visibly shorter.
            right_region = scaled_region(right_region, 0.58, bottom=False)
        elif mechanic == "capacity":
            right_region = scaled_region(right_region, 0.58)
        left_region[3] -= 48
        right_region[3] -= 48
        late_paste_fit(canvas, assets[item["assets"][0]], left_region, 2)
        late_paste_fit(canvas, assets[item["assets"][1]], right_region, 2)
        object_label(draw, text_base, item["assets"][0], [left_region[0], left_region[3], left_region[2], left_region[3] + 48], size=27)
        object_label(draw, text_base, item["assets"][1], [right_region[0], right_region[3], right_region[2], right_region[3] + 48], size=27)


def numbered_asset_grid(canvas, draw, assets, names, boxes, text_base):
    for number, (name, box) in enumerate(zip(names, boxes), 1):
        base.panel(draw, box, outline=SOFT_PURPLE, width=3)
        late_paste_fit(canvas, assets[name], [box[0] + 15, box[1] + 15, box[2] - 15, box[3] - 78], 2)
        object_label(draw, text_base, name, [box[0] + 25, box[3] - 72, box[2] - 25, box[3] - 18], size=26)
        draw.ellipse([box[0] + 18, box[1] + 18, box[0] + 82, box[1] + 82], fill="#E7D9FA", outline=PURPLE, width=3)
        text_base.fitted_text(draw, str(number), [box[0] + 24, box[1] + 24, box[0] + 76, box[1] + 76],
                              max_size=36, min_size=28, colour=NAVY, bold=True, max_lines=1)


def late_render_classification(canvas, draw, page, assets, text_base, template):
    mechanic = page["activity"]["mechanic"]
    draw_simple_model(canvas, draw, page, assets, text_base, template)
    categories = page["activity"]["mechanics"]["categories"]
    names = base.asset_order(page)
    cat_count = len(categories)
    slots_per_category = len(names) // cat_count
    cat_gap = 30
    cat_w = (2140 - cat_gap * (cat_count - 1)) // cat_count
    for index, category in enumerate(categories):
        left = 170 + index * (cat_w + cat_gap)
        base.panel(draw, [left, TASK_TOP, left + cat_w, 1190], fill=BLUE if index % 2 else "#F5F0FF", outline=SOFT_PURPLE, width=3)
        text_base.fitted_text(draw, category["label"], [left + 25, TASK_TOP + 25, left + cat_w - 25, TASK_TOP + 115],
                              max_size=43, min_size=32, colour=NAVY, bold=True, max_lines=1)
        text_base.fitted_text(draw, "Write picture numbers:", [left + 25, TASK_TOP + 105, left + cat_w - 25, TASK_TOP + 165],
                              max_size=29, min_size=23, colour=INK, max_lines=1)
        slot_gap = 18
        usable = cat_w - 90
        slot_w = min(132, (usable - slot_gap * (slots_per_category - 1)) // slots_per_category)
        total_w = slots_per_category * slot_w + (slots_per_category - 1) * slot_gap
        slot_left = left + (cat_w - total_w) // 2
        for slot in range(slots_per_category):
            x0 = slot_left + slot * (slot_w + slot_gap)
            draw.rounded_rectangle(
                [x0, TASK_TOP + 174, x0 + slot_w, TASK_TOP + 244],
                radius=14,
                fill="white",
                outline=PURPLE,
                width=3,
            )
    cols = 4 if len(names) == 8 else 3
    rows = (len(names) + cols - 1) // cols
    gap = 24
    width = (2140 - gap * (cols - 1)) // cols
    height = (TASK_BOTTOM - 1250 - gap * (rows - 1)) // rows
    boxes = []
    for i in range(len(names)):
        row, col = divmod(i, cols)
        left = 170 + col * (width + gap)
        top = 1250 + row * (height + gap)
        boxes.append([left, top, left + width, top + height])
    numbered_asset_grid(canvas, draw, assets, names, boxes, text_base)


def late_render_picture_graph(canvas, draw, page, assets, text_base, template):
    draw_simple_model(canvas, draw, page, assets, text_base, template)
    rows = [("graph_apple", "APPLES", 4), ("graph_banana", "BANANAS", 2), ("graph_orange", "ORANGES", 3)]
    for index, (name, label, count) in enumerate(rows):
        top = TASK_TOP + index * 430
        base.panel(draw, [180, top, 2300, top + 400], outline=SOFT_PURPLE, width=3)
        base.panel(draw, [205, top + 35, 690, top + 365], fill="#F5F1FF", outline=SOFT_PURPLE, width=2, radius=18)
        text_base.fitted_text(draw, label, [235, top + 115, 660, top + 285], max_size=42, min_size=32,
                              colour=NAVY, bold=True, max_lines=1)
        for item in range(count):
            left = 760 + item * 360
            late_paste_fit(canvas, assets[name], [left, top + 55, left + 300, top + 345], 2)
    text_base.fitted_text(draw, "Which fruit has the most?", [210, 2300, 990, 2420], max_size=40, min_size=31,
                          colour=NAVY, bold=True, align="left", max_lines=1)
    draw_choice_words(draw, text_base, ["apples", "bananas", "oranges"], [1040, 2300, 2250, 2420])
    text_base.fitted_text(draw, "How many oranges?", [210, 2600, 990, 2720], max_size=40, min_size=31,
                          colour=NAVY, bold=True, align="left", max_lines=1)
    draw_choice_words(draw, text_base, ["2", "3", "4"], [1200, 2600, 2100, 2720])


def late_render_mixed_review(canvas, draw, page, assets, text_base, template):
    mechanic = page["activity"]["mechanic"]
    draw_simple_model(canvas, draw, page, assets, text_base, template)
    if mechanic == "mixed-maths-problems":
        names = base.asset_order(page)
        questions = [
            "3 children need a ball. There are 2 balls. How many more?",
            "Share 4 apples between 2 children. How many apples each?",
            "The bus has 5 seats. 3 are filled. How many are empty?",
        ]
        rows = full_width_rows(3)
        for name, question, box in zip(names, questions, rows):
            base.panel(draw, box, outline=SOFT_PURPLE, width=3)
            late_paste_fit(canvas, assets[name], [box[0] + 25, box[1] + 25, 1280, box[3] - 75], 2)
            object_label(draw, text_base, name, [box[0] + 25, box[3] - 72, 1280, box[3] - 20], size=27)
            text_base.fitted_text(draw, question, [1320, box[1] + 55, 2240, box[3] - 170], max_size=38, min_size=28,
                                  colour=NAVY, bold=True, align="left", max_lines=3)
            base.panel(draw, [1910, box[3] - 155, 2110, box[3] - 35], fill="#FFF9DE", outline="#D9A91B", width=4, radius=18)
        return
    # P041: four purposeful review quadrants rather than eight generic cards.
    boxes = [[180, TASK_TOP, 1225, 1900], [1255, TASK_TOP, 2300, 1900],
             [180, 1930, 1225, TASK_BOTTOM], [1255, 1930, 2300, TASK_BOTTOM]]
    for box in boxes:
        base.panel(draw, box, outline=SOFT_PURPLE, width=3)
    text_base.fitted_text(draw, "1. Count the stars.", [215, 955, 1190, 1060], max_size=38, min_size=29,
                          colour=NAVY, bold=True, align="left", max_lines=1)
    late_paste_fit(canvas, assets["review_five_stars"], [260, 1080, 1135, 1570], 2)
    draw_choice_words(draw, text_base, ["4", "5", "6"], [390, 1635, 1030, 1760])
    text_base.fitted_text(draw, "2. Circle the group with more.", [1290, 955, 2265, 1060], max_size=38, min_size=27,
                          colour=NAVY, bold=True, align="left", max_lines=1)
    late_paste_fit(canvas, assets["review_two_apples"], [1290, 1110, 1730, 1740], 2)
    late_paste_fit(canvas, assets["review_four_apples"], [1810, 1110, 2250, 1740], 2)
    text_base.fitted_text(draw, "3. Tick under the triangle.", [215, 1960, 1190, 2065], max_size=38, min_size=28,
                          colour=NAVY, bold=True, align="left", max_lines=1)
    shape_names = ["review_circle", "review_triangle", "review_square"]
    for i, name in enumerate(shape_names):
        left = 230 + i * 320
        late_paste_fit(canvas, assets[name], [left, 2100, left + 250, 2535], 2)
        object_label(draw, text_base, name, [left, 2535, left + 250, 2590], size=25)
        draw.rectangle([left + 85, 2680, left + 155, 2750], fill="white", outline=PURPLE, width=4)
    text_base.fitted_text(draw, "4. What comes next?", [1290, 1960, 2265, 2065], max_size=38, min_size=29,
                          colour=NAVY, bold=True, align="left", max_lines=1)
    late_paste_fit(canvas, assets["review_pattern_red_blue"], [1320, 2110, 2240, 2480], 2)
    object_label(draw, text_base, "review_pattern_red_blue", [1320, 2480, 2240, 2540], value="red ball - blue ball", size=25)
    draw.ellipse([1540, 2630, 1660, 2750], fill="#F12B2B", outline=NAVY, width=3)
    draw.ellipse([1900, 2630, 2020, 2750], fill="#2381F2", outline=NAVY, width=3)


def late_render_certificate(canvas, draw, page, assets, text_base, template):
    base.panel(draw, [210, 720, 2270, 3180], fill="#FFFDF2", outline="#D9A91B", width=8, radius=42)
    late_paste_fit(canvas, assets["certificate_math_badge"], [920, 775, 1560, 1240], 2)
    text_base.fitted_text(draw, "Certificate of Completion", [400, 1270, 2080, 1480], max_size=72, min_size=52,
                          colour=NAVY, bold=True, max_lines=1)
    text_base.fitted_text(draw, "This certificate is proudly presented to", [440, 1540, 2040, 1680], max_size=42, min_size=32,
                          colour=INK, max_lines=1)
    draw.line([500, 1900, 1980, 1900], fill=PURPLE, width=4)
    text_base.fitted_text(draw, "for completing Early Maths Adventures", [430, 1990, 2050, 2170], max_size=46, min_size=34,
                          colour=NAVY, bold=True, max_lines=2)
    late_paste_fit(canvas, assets["certificate_trophy"], [980, 2200, 1500, 2650], 2)
    draw.line([400, 2800, 980, 2800], fill=PURPLE, width=3)
    draw.line([1500, 2800, 2080, 2800], fill=PURPLE, width=3)
    text_base.fitted_text(draw, "Date", [560, 2820, 820, 2920], max_size=34, min_size=27, colour=NAVY, max_lines=1)
    text_base.fitted_text(draw, "Teacher", [1660, 2820, 1920, 2920], max_size=34, min_size=27, colour=NAVY, max_lines=1)
    late_paste_fit(canvas, assets["certificate_confetti_left"], [230, 800, 650, 1280], 1)
    late_paste_fit(canvas, assets["certificate_confetti_right"], [1830, 800, 2250, 1280], 1)
    late_paste_fit(canvas, assets["certificate_shape_border"], [480, 2980, 2000, 3120], 1)


def command_line_option(name):
    try:
        return Path(sys.argv[sys.argv.index(name) + 1])
    except (ValueError, IndexError):
        return None


def late_render_back_cover(canvas, page, assets):
    """Compose a complete branded back cover around the approved hero art."""
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, canvas.width, canvas.height], fill="#F7F2FC")
    draw.rounded_rectangle([80, 80, 2400, 3428], radius=58, fill="white", outline=PURPLE, width=10)

    logo_path = command_line_option("--logo")
    if logo_path and logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA")
        logo.thumbnail((300, 220), Image.Resampling.LANCZOS)
        canvas.paste(logo, (150 + (300 - logo.width) // 2, 120 + (220 - logo.height) // 2), logo)

    text_engine.fitted_text(draw, "BCube Future Skills Learning Series™", [500, 110, 2170, 205],
                            max_size=39, min_size=30, colour=PURPLE, bold=True, max_lines=1)
    text_engine.fitted_text(draw, "Early Maths Adventures", [500, 205, 2170, 350],
                            max_size=72, min_size=52, colour=NAVY, bold=True, max_lines=1)
    base.panel(draw, [2010, 350, 2260, 455], fill=GOLD, outline="#D9A91B", width=3, radius=26)
    text_engine.fitted_text(draw, "LKG (4+)", [2030, 365, 2240, 440], max_size=35, min_size=28,
                            colour=NAVY, bold=True, max_lines=1)
    text_engine.fitted_text(draw, "Count • Compare • Discover", [470, 360, 1940, 455],
                            max_size=43, min_size=32, colour="#E35B25", bold=True, max_lines=1)

    base.panel(draw, [170, 505, 2310, 2080], fill="#F5FAFF", outline="#6AA9D8", width=4, radius=36)
    late_paste_fit(canvas, assets["early_maths_back_cover_scene"], [210, 545, 2270, 2040], 0)

    text_engine.fitted_text(
        draw,
        "Build confidence with counting, shapes, patterns and everyday problem solving.",
        [260, 2130, 2220, 2290],
        max_size=46,
        min_size=34,
        colour=NAVY,
        bold=True,
        max_lines=2,
    )

    pillars = [
        ("COUNTING", "#EAF4FF", "#1768B3"),
        ("SHAPES", "#FFF2D5", "#D68A00"),
        ("PATTERNS", "#F2ECFF", PURPLE),
        ("PROBLEM SOLVING", "#ECF8E8", "#4B8F3A"),
    ]
    for index, (label, fill, outline) in enumerate(pillars):
        col = index % 2
        row = index // 2
        x0 = 240 + col * 1030
        y0 = 2350 + row * 170
        base.panel(draw, [x0, y0, x0 + 960, y0 + 125], fill=fill, outline=outline, width=3, radius=28)
        text_engine.fitted_text(draw, label, [x0 + 35, y0 + 18, x0 + 925, y0 + 107],
                                max_size=38, min_size=29, colour=NAVY, bold=True, max_lines=1)

    draw.line([250, 2725, 2230, 2725], fill="#D8C8EA", width=4)
    text_engine.fitted_text(draw, "BCube Future Academy", [300, 2770, 2180, 2870],
                            max_size=43, min_size=34, colour=PURPLE, bold=True, max_lines=1)
    text_engine.fitted_text(draw, "407, DSMAX Sky Supreme KST Bangalore - 560060", [300, 2890, 2180, 2980],
                            max_size=33, min_size=27, colour=INK, max_lines=1)
    text_engine.fitted_text(draw, "info@bcubefutureacademy.in  |  bcubefutureacademy.in", [300, 3000, 2180, 3090],
                            max_size=33, min_size=27, colour=INK, max_lines=1)
    text_engine.fitted_text(draw, "© 2026 BCube Future Academy. First Edition, 2026. All rights reserved.",
                            [300, 3130, 2180, 3220], max_size=29, min_size=23, colour="#555555", max_lines=1)
    text_engine.fitted_text(draw, "Learning today. Exploring tomorrow.", [450, 3260, 2030, 3350],
                            max_size=34, min_size=27, colour="#E35B25", bold=True, max_lines=1)


base.render_match = late_render_match
base.render_hero_targets = late_render_hero_targets
base.render_rows = late_render_rows
base.render_comparison = late_render_comparison
base.render_classification = late_render_classification
base.render_asset_grid = late_render_mixed_review
base.render_certificate = late_render_certificate
base.render_back_cover = late_render_back_cover


# picture-graph uses a dedicated renderer rather than the generic asset grid.
original_main = base.main


def patched_main():
    # Base dispatch resolves these module attributes when main executes.
    original_grid = base.render_asset_grid

    def dispatching_grid(canvas, draw, page, assets, text_base, template, controls=True):
        if page["activity"]["render_kind"] == "picture-graph":
            return late_render_picture_graph(canvas, draw, page, assets, text_base, template)
        return original_grid(canvas, draw, page, assets, text_base, template)

    base.render_asset_grid = dispatching_grid
    try:
        return original_main()
    finally:
        base.render_asset_grid = original_grid

if __name__ == "__main__":
    raise SystemExit(patched_main())
