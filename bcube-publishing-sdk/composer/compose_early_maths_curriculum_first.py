#!/usr/bin/env python3
"""Curriculum-first renderer for Early Maths Adventures LKG P009-P021.

Each render kind implements one approved teaching mechanic. There is no generic
fallback. Pages with no generated-art requirement are rendered deterministically.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
COMMON_PATH = ROOT / "bcube-publishing-sdk/composer/compose_runtime_learning_page.py"
BASE_PATH = ROOT / "bcube-publishing-sdk/composer/compose_learning_page_v2.py"
LOADER_PATH = ROOT / "bcube-publishing-sdk/runtime/load_book_contract.py"
TEMPLATE_PATH = ROOT / "bcube-publishing-sdk/templates/learning-page-v2.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def text(base, draw, template, value, box, *, size=38, bold=True, align="center", colour=None, lines=2):
    base.fitted_text(draw, str(value), box, max_size=size, min_size=max(20, size - 14), colour=colour or template["colours"]["navy"], bold=bold, align=align, max_lines=lines)


def tight_asset(asset: Image.Image) -> Image.Image:
    """Trim transparent or opaque near-white sheet padding before placement."""
    rgba = asset.convert("RGBA")
    alpha = rgba.getchannel("A")
    rgb = rgba.convert("RGB")
    white = Image.new("RGB", rgb.size, (255, 255, 255))
    difference = ImageChops.difference(rgb, white).convert("L")
    ink = difference.point(lambda value: 255 if value > 8 else 0)
    visible = ImageChops.multiply(alpha, ink)
    bbox = visible.getbbox() or alpha.getbbox()
    if not bbox:
        return rgba
    left, top, right, bottom = bbox
    margin = max(4, round(max(right - left, bottom - top) * 0.035))
    left = max(0, left - margin); top = max(0, top - margin)
    right = min(rgba.width, right + margin); bottom = min(rgba.height, bottom + margin)
    return rgba.crop((left, top, right, bottom))


def paste_asset(common, canvas, asset: Image.Image, box, *, inset=0):
    common.paste_fit(canvas, tight_asset(asset), box, inset=inset)


def answer_choices(draw, base, template, values, box, *, radius=52):
    x0, y0, x1, y1 = box
    gap = (x1 - x0) // (len(values) + 1)
    for i, value in enumerate(values, 1):
        cx = x0 + gap * i; cy = (y0 + y1) // 2
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill="#FFFFFF", outline=template["colours"]["purple"], width=5)
        text(base, draw, template, value, [cx - radius + 8, cy - radius + 8, cx + radius - 8, cy + radius - 8], size=38, lines=1)


def row_box(common, draw, y0, y1):
    box = [180, y0, 2300, y1]
    common.panel(draw, box, outline="#7E57C2", width=3)
    return box


def visual_model(common, canvas, draw, base, template, page, render_kind, assets):
    common.panel(draw, [180, 630, 2300, 780], fill="#F4EEFF", outline="#7E57C2", width=3)
    text(base, draw, template, "MODEL", [210, 655, 450, 750], size=30, lines=1)
    if render_kind == "curriculum-count-match":
        for x in (660, 770, 880):
            draw.regular_polygon((x, 705, 36), 5, rotation=-90, fill="#F5C84C", outline="#35405A")
        draw.ellipse([1040, 680, 1090, 730], fill="#FFFFFF", outline="#7E57C2", width=4)
        draw.line([1090, 705, 1570, 705], fill="#7E57C2", width=5)
        draw.ellipse([1570, 680, 1620, 730], fill="#FFFFFF", outline="#7E57C2", width=4)
        text(base, draw, template, "3", [1690, 655, 1880, 755], size=62, lines=1)
    elif render_kind == "curriculum-number-line":
        x0, x1, y = 650, 1740, 710
        draw.line([x0, y, x1, y], fill="#5B3F9A", width=6)
        step = (x1 - x0) / 5
        for n in range(6):
            x = x0 + n * step
            draw.line([x, y - 18, x, y + 18], fill="#5B3F9A", width=4)
            text(base, draw, template, n, [x - 35, y + 22, x + 35, y + 70], size=24, lines=1)
        draw.ellipse([x0 - 13, y - 13, x0 + 13, y + 13], fill="#E25454")
        draw.arc([x0, y - 95, x0 + step, y + 5], 180, 360, fill="#E25454", width=5)
        text(base, draw, template, "Land on 1", [1830, 665, 2220, 750], size=30, lines=1)
    elif render_kind == "curriculum-shape-match":
        draw.ellipse([670, 665, 790, 745], fill="#F5A35C", outline="#35405A", width=5)
        draw.ellipse([940, 680, 990, 730], fill="#FFFFFF", outline="#7E57C2", width=4)
        draw.line([990, 705, 1460, 705], fill="#7E57C2", width=5)
        draw.ellipse([1460, 680, 1510, 730], fill="#FFFFFF", outline="#7E57C2", width=4)
        draw.ellipse([1660, 645, 1790, 765], fill="#FFF7D6", outline="#35405A", width=5)
        text(base, draw, template, "oval", [1840, 665, 2180, 745], size=28, bold=False, lines=1)
    else:
        model = page.get("learning", {}).get("model_text")
        short = model.get("story") or model.get("prompt") or "Look at the completed example." if isinstance(model, dict) else "Look at the completed example."
        text(base, draw, template, short, [520, 655, 2220, 750], size=28, bold=False, align="left", lines=2)


def render_count_match(canvas, draw, page, assets, base, template, common):
    m = page["activity"]["mechanics"]
    pairs = m["correct_pairs"]; numerals = m["numerals"]
    y0, row_h, gap = 815, 475, 30
    for i, (asset_name, _) in enumerate(pairs):
        top = y0 + i * (row_h + gap); bottom = top + row_h
        common.panel(draw, [190, top, 1120, bottom], outline="#7E57C2", width=3)
        paste_asset(common, canvas, assets[asset_name], [220, top + 20, 1000, bottom - 20])
        common.circle(draw, base, template, 1055, (top + bottom) // 2)
        common.panel(draw, [1510, top + 35, 2270, bottom - 35], outline="#1768B3", width=3)
        common.circle(draw, base, template, 1560, (top + bottom) // 2)
        text(base, draw, template, numerals[i], [1660, top + 80, 2180, bottom - 80], size=96, lines=1)


def render_count_circle(canvas, draw, page, assets, base, template, common):
    cards = page["activity"]["mechanics"]["cards"]
    boxes = common.grid_boxes(len(cards), top=815, bottom=2990)
    for card, box in zip(cards, boxes):
        common.panel(draw, box, outline="#7E57C2", width=3)
        paste_asset(common, canvas, assets[card["asset"]], [box[0] + 35, box[1] + 30, box[2] - 35, box[3] - 155])
        answer_choices(draw, base, template, card["choices"], [box[0] + 35, box[3] - 145, box[2] - 35, box[3] - 15])


def render_quantity_comparison(canvas, draw, page, assets, base, template, common):
    rows = page["activity"]["mechanics"]["rows"]
    y = 815
    for row in rows:
        row_box(common, draw, y, y + 650)
        text(base, draw, template, row["prompt"], [250, y + 20, 2230, y + 100], size=32, lines=1)
        paste_asset(common, canvas, assets[row["left"]], [230, y + 110, 1040, y + 600])
        paste_asset(common, canvas, assets[row["right"]], [1440, y + 110, 2250, y + 600])
        y += 710


def render_equal_groups(canvas, draw, page, assets, base, template, common):
    rows = page["activity"]["mechanics"]["rows"]
    y = 815
    for row in rows:
        row_box(common, draw, y, y + 640)
        paste_asset(common, canvas, assets[row["left"]], [220, y + 30, 980, y + 500])
        paste_asset(common, canvas, assets[row["right"]], [1040, y + 30, 1800, y + 500])
        answer_choices(draw, base, template, ["YES", "NO"], [1790, y + 120, 2280, y + 530], radius=56)
        y += 710


def render_missing_number(canvas, draw, page, assets, base, template, common):
    rows = page["activity"]["mechanics"]["rows"]
    y = 850
    for row in rows:
        row_box(common, draw, y, y + 590)
        seq = row["sequence"]; step = 1740 // len(seq)
        for i, value in enumerate(seq):
            x0 = 360 + i * step
            if value is None:
                common.panel(draw, [x0, y + 210, x0 + 190, y + 390], fill="#FFF9DE", outline="#D9A91B", width=4, radius=18)
            else:
                text(base, draw, template, value, [x0, y + 210, x0 + 190, y + 390], size=60, lines=1)
        y += 680


def render_addition(canvas, draw, page, assets, base, template, common):
    y = 815
    for p in page["activity"]["mechanics"]["problems"]:
        row_box(common, draw, y, y + 640)
        paste_asset(common, canvas, assets[p["left"]], [220, y + 40, 820, y + 480])
        text(base, draw, template, "+", [830, y + 150, 980, y + 350], size=78, lines=1)
        paste_asset(common, canvas, assets[p["right"]], [990, y + 40, 1590, y + 480])
        text(base, draw, template, "=", [1600, y + 150, 1750, y + 350], size=72, lines=1)
        answer_choices(draw, base, template, p["choices"], [1720, y + 80, 2270, y + 560])
        y += 710


def render_subtraction(canvas, draw, page, assets, base, template, common):
    y = 815
    for p in page["activity"]["mechanics"]["problems"]:
        row_box(common, draw, y, y + 640)
        paste_asset(common, canvas, assets[p["asset"]], [220, y + 30, 1580, y + 540])
        text(base, draw, template, f"Cross out {p['take_away']}", [1600, y + 55, 2250, y + 170], size=32, lines=1)
        answer_choices(draw, base, template, p["choices"], [1580, y + 230, 2270, y + 590])
        y += 710


def render_before_after(canvas, draw, page, base, template, common):
    y = 820
    for row in page["activity"]["mechanics"]["rows"]:
        row_box(common, draw, y, y + 470)
        common.panel(draw, [420, y + 100, 850, y + 370], fill="#FFF9DE", outline="#D9A91B", width=4, radius=22)
        common.panel(draw, [1025, y + 80, 1455, y + 390], fill="#F4EEFF", outline="#7E57C2", width=4, radius=22)
        text(base, draw, template, row["centre"], [1050, y + 105, 1430, y + 365], size=78, lines=1)
        common.panel(draw, [1630, y + 100, 2060, y + 370], fill="#FFF9DE", outline="#D9A91B", width=4, radius=22)
        y += 520


def render_number_order(canvas, draw, page, base, template, common):
    y = 820
    for row in page["activity"]["mechanics"]["rows"]:
        row_box(common, draw, y, y + 650)
        tokens = row["tokens"]; gap = 1400 // len(tokens)
        for i, value in enumerate(tokens):
            cx = 500 + i * gap
            draw.ellipse([cx - 75, y + 90, cx + 75, y + 240], fill="#F4EEFF", outline="#7E57C2", width=4)
            text(base, draw, template, value, [cx - 60, y + 105, cx + 60, y + 225], size=46, lines=1)
        slots = row["answer"]; gap2 = 1500 // len(slots)
        for i in range(len(slots)):
            x0 = 390 + i * gap2
            common.panel(draw, [x0, y + 350, x0 + 250, y + 560], fill="#FFF9DE", outline="#D9A91B", width=4, radius=20)
        y += 720


def render_number_line(canvas, draw, page, assets, base, template, common):
    y = 820
    for row in page["activity"]["mechanics"]["rows"]:
        row_box(common, draw, y, y + 650)
        paste_asset(common, canvas, assets[row["asset"]], [220, y + 145, 560, y + 500])
        start_n, end_n = row["range"]; count = end_n - start_n
        x0, x1, line_y = 650, 1740, y + 325
        draw.line([x0, line_y, x1, line_y], fill="#5B3F9A", width=7)
        step = (x1 - x0) / count
        for n in range(start_n, end_n + 1):
            x = x0 + (n - start_n) * step
            draw.line([x, line_y - 25, x, line_y + 25], fill="#5B3F9A", width=5)
            text(base, draw, template, n, [x - 45, line_y + 38, x + 45, line_y + 110], size=30, lines=1)
        draw.ellipse([x0 - 16, line_y - 16, x0 + 16, line_y + 16], fill="#E25454", outline="#FFFFFF", width=3)
        for j in range(row["jumps"]):
            a = x0 + j * step; b = x0 + (j + 1) * step
            draw.arc([a, line_y - 150, b, line_y + 15], 180, 360, fill="#E25454", width=6)
        common.panel(draw, [1840, y + 85, 2260, y + 570], fill="#FFFDF7", outline="#D9A91B", width=3, radius=22)
        text(base, draw, template, "Where do you land?", [1870, y + 110, 2230, y + 205], size=27, lines=2)
        answer_choices(draw, base, template, row["choices"], [1855, y + 260, 2245, y + 520], radius=48)
        y += 710


def render_numeral_comparison(canvas, draw, page, base, template, common):
    y = 800
    for row in page["activity"]["mechanics"]["rows"]:
        row_box(common, draw, y, y + 500)
        left, right = row["pair"]
        common.panel(draw, [500, y + 85, 1050, y + 415], fill="#F4EEFF", outline="#7E57C2", width=4, radius=26)
        common.panel(draw, [1430, y + 85, 1980, y + 415], fill="#EAF6FF", outline="#1768B3", width=4, radius=26)
        text(base, draw, template, left, [540, y + 115, 1010, y + 385], size=86, lines=1)
        text(base, draw, template, right, [1470, y + 115, 1940, y + 385], size=86, lines=1)
        y += 550


def render_math_stories(canvas, draw, page, assets, base, template, common):
    y = 815
    for story in page["activity"]["mechanics"]["stories"]:
        row_box(common, draw, y, y + 640)
        paste_asset(common, canvas, assets[story["asset"]], [220, y + 25, 1570, y + 620])
        text(base, draw, template, story["question"], [1600, y + 60, 2260, y + 190], size=32, lines=2)
        answer_choices(draw, base, template, story["choices"], [1580, y + 230, 2270, y + 590])
        y += 710


def render_shape_match(canvas, draw, page, assets, base, template, common):
    m = page["activity"]["mechanics"]
    y0, row_h, gap = 815, 475, 30
    for i, name in enumerate(m["left"]):
        top = y0 + i * (row_h + gap); bottom = top + row_h
        common.panel(draw, [190, top, 1120, bottom], outline="#7E57C2", width=3)
        paste_asset(common, canvas, assets[name], [280, top + 45, 940, bottom - 45])
        common.circle(draw, base, template, 1055, (top + bottom) // 2)
        right_name = m["right"][i]
        common.panel(draw, [1510, top + 35, 2270, bottom - 35], outline="#1768B3", width=3)
        common.circle(draw, base, template, 1560, (top + bottom) // 2)
        paste_asset(common, canvas, assets[right_name], [1640, top + 50, 2160, bottom - 50])


RENDERERS = {
    "curriculum-count-match": render_count_match,
    "curriculum-count-circle": render_count_circle,
    "curriculum-quantity-comparison": render_quantity_comparison,
    "curriculum-equal-groups": render_equal_groups,
    "curriculum-missing-number": render_missing_number,
    "curriculum-picture-addition": render_addition,
    "curriculum-picture-subtraction": render_subtraction,
    "curriculum-before-after": render_before_after,
    "curriculum-number-order": render_number_order,
    "curriculum-number-line": render_number_line,
    "curriculum-numeral-comparison": render_numeral_comparison,
    "curriculum-math-stories": render_math_stories,
    "curriculum-shape-match": render_shape_match,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", required=True); parser.add_argument("--book", required=True)
    parser.add_argument("--page-id", required=True); parser.add_argument("--illustration", type=Path)
    parser.add_argument("--logo", type=Path, required=True); parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    args = parser.parse_args()

    common = load_module("curriculum_common", COMMON_PATH)
    base = load_module("curriculum_base", BASE_PATH)
    loader = load_module("curriculum_loader", LOADER_PATH)
    page = loader.load_page_contract(level=args.level, book_slug=args.book, page_id=args.page_id)
    common.validate(page)
    render_kind = page["activity"]["render_kind"]
    renderer = RENDERERS.get(render_kind)
    if renderer is None:
        raise ValueError(f"No curriculum-first renderer for {render_kind}")

    manifest = load_json(ROOT / "runtime-contracts/manifest.json")
    relative = manifest["levels"][args.level.lower()]["books"][args.book]
    book = load_json(ROOT / "runtime-contracts" / relative)
    template = load_json(TEMPLATE_PATH); spec = template["canvas"]
    canvas = Image.new("RGB", (spec["width"], spec["height"]), template["colours"]["background"])
    draw = ImageDraw.Draw(canvas)
    common.header(canvas, draw, page, book["book"]["title"], Image.open(args.logo), base, template)

    assets: dict[str, Image.Image] = {}
    required_assets = page.get("illustration", {}).get("assets", [])
    if required_assets:
        if args.illustration is None or not args.illustration.is_file():
            raise FileNotFoundError(f"Illustration required for {args.page_id}")
        source = Image.open(args.illustration).convert("RGBA")
        assets = common.crop_assets(source, page["illustration"]["asset_crops"])
    visual_model(common, canvas, draw, base, template, page, render_kind, assets)

    if render_kind in {"curriculum-before-after", "curriculum-number-order", "curriculum-numeral-comparison"}:
        renderer(canvas, draw, page, base, template, common)
    else:
        renderer(canvas, draw, page, assets, base, template, common)

    common.teacher(draw, page, base, template)
    if page["identity"].get("printed_page") is not None:
        text(base, draw, template, page["identity"]["printed_page"], [2200, 3270, 2370, 3390], size=46, colour=template["colours"]["muted"], lines=1)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.output, "PNG", dpi=(spec["dpi"], spec["dpi"]))
    evidence = {
        "engine": "BCube Early Maths Curriculum-First Renderer V1.1",
        "page_id": args.page_id,
        "render_kind": render_kind,
        "artifact": str(args.output),
        "artifact_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "qa": {"curriculum_first": True, "fallback_used": False, "raw_model_json_rendered": False, "near_white_sheet_padding_trimmed": True, "status": "TEST_CANDIDATE"},
    }
    args.evidence_output.parent.mkdir(parents=True, exist_ok=True)
    args.evidence_output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
