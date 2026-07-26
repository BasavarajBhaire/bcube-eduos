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

from PIL import Image, ImageDraw

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


def answer_choices(draw, base, template, values, box):
    x0, y0, x1, y1 = box
    gap = (x1 - x0) // (len(values) + 1)
    for i, value in enumerate(values, 1):
        cx = x0 + gap * i; cy = (y0 + y1) // 2
        draw.ellipse([cx - 48, cy - 48, cx + 48, cy + 48], fill="#FFFFFF", outline=template["colours"]["purple"], width=4)
        text(base, draw, template, value, [cx - 38, cy - 38, cx + 38, cy + 38], size=36, lines=1)


def row_box(common, draw, y0, y1):
    box = [180, y0, 2300, y1]
    common.panel(draw, box, outline="#7E57C2", width=3)
    return box


def model_strip(common, draw, base, template, page):
    model = page.get("learning", {}).get("model_text")
    if not model:
        return
    common.panel(draw, [180, 630, 2300, 760], fill="#F4EEFF", outline="#7E57C2", width=3)
    text(base, draw, template, "MODEL", [210, 650, 470, 735], size=30, lines=1)
    text(base, draw, template, json.dumps(model, ensure_ascii=False).replace('"', ''), [500, 642, 2260, 742], size=28, bold=False, align="left", lines=2)


def render_count_match(canvas, draw, page, assets, base, template, common):
    m = page["activity"]["mechanics"]
    pairs = m["correct_pairs"]; numerals = m["numerals"]
    y0, row_h, gap = 800, 500, 35
    for i, (asset_name, _) in enumerate(pairs):
        top = y0 + i * (row_h + gap); bottom = top + row_h
        common.panel(draw, [190, top, 1050, bottom], outline="#7E57C2", width=3)
        common.paste_fit(canvas, assets[asset_name], [220, top + 20, 930, bottom - 20])
        common.circle(draw, base, template, 995, (top + bottom) // 2)
        common.panel(draw, [1470, top, 2270, bottom], outline="#1768B3", width=3)
        common.circle(draw, base, template, 1520, (top + bottom) // 2)
        text(base, draw, template, numerals[i], [1600, top + 70, 2180, bottom - 70], size=92, lines=1)


def render_count_circle(canvas, draw, page, assets, base, template, common):
    cards = page["activity"]["mechanics"]["cards"]
    boxes = common.grid_boxes(len(cards), top=800, bottom=2990)
    for card, box in zip(cards, boxes):
        common.panel(draw, box, outline="#7E57C2", width=3)
        common.paste_fit(canvas, assets[card["asset"]], [box[0] + 20, box[1] + 20, box[2] - 20, box[3] - 150])
        answer_choices(draw, base, template, card["choices"], [box[0] + 35, box[3] - 145, box[2] - 35, box[3] - 15])


def render_quantity_comparison(canvas, draw, page, assets, base, template, common):
    rows = page["activity"]["mechanics"]["rows"]
    y = 800
    for row in rows:
        box = row_box(common, draw, y, y + 660)
        text(base, draw, template, row["prompt"], [250, y + 20, 2230, y + 100], size=32, lines=1)
        common.paste_fit(canvas, assets[row["left"]], [230, y + 110, 1040, y + 590])
        common.paste_fit(canvas, assets[row["right"]], [1440, y + 110, 2250, y + 590])
        y += 720


def render_equal_groups(canvas, draw, page, assets, base, template, common):
    rows = page["activity"]["mechanics"]["rows"]
    y = 800
    for row in rows:
        row_box(common, draw, y, y + 650)
        common.paste_fit(canvas, assets[row["left"]], [220, y + 30, 980, y + 480])
        common.paste_fit(canvas, assets[row["right"]], [1040, y + 30, 1800, y + 480])
        answer_choices(draw, base, template, ["YES", "NO"], [1790, y + 120, 2280, y + 530])
        y += 720


def render_missing_number(canvas, draw, page, assets, base, template, common):
    rows = page["activity"]["mechanics"]["rows"]
    y = 850
    for row in rows:
        row_box(common, draw, y, y + 590)
        if row.get("asset") in assets:
            common.paste_fit(canvas, assets[row["asset"]], [220, y + 25, 2260, y + 565])
        seq = row["sequence"]; step = 1740 // len(seq)
        for i, value in enumerate(seq):
            x0 = 360 + i * step
            if value is None:
                common.panel(draw, [x0, y + 210, x0 + 190, y + 390], fill="#FFF9DE", outline="#D9A91B", width=4, radius=18)
            else:
                text(base, draw, template, value, [x0, y + 210, x0 + 190, y + 390], size=60, lines=1)
        y += 680


def render_addition(canvas, draw, page, assets, base, template, common):
    y = 800
    for p in page["activity"]["mechanics"]["problems"]:
        row_box(common, draw, y, y + 650)
        common.paste_fit(canvas, assets[p["left"]], [220, y + 40, 820, y + 450])
        text(base, draw, template, "+", [830, y + 150, 980, y + 350], size=78, lines=1)
        common.paste_fit(canvas, assets[p["right"]], [990, y + 40, 1590, y + 450])
        text(base, draw, template, "=", [1600, y + 150, 1750, y + 350], size=72, lines=1)
        answer_choices(draw, base, template, p["choices"], [1720, y + 80, 2270, y + 560])
        y += 720


def render_subtraction(canvas, draw, page, assets, base, template, common):
    y = 800
    for p in page["activity"]["mechanics"]["problems"]:
        row_box(common, draw, y, y + 650)
        common.paste_fit(canvas, assets[p["asset"]], [220, y + 30, 1580, y + 540])
        text(base, draw, template, f"Cross out {p['take_away']}", [1600, y + 55, 2250, y + 170], size=32, lines=1)
        answer_choices(draw, base, template, p["choices"], [1580, y + 230, 2270, y + 590])
        y += 720


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
        common.paste_fit(canvas, assets[row["asset"]], [210, y + 100, 520, y + 430])
        start_n, end_n = row["range"]; count = end_n - start_n
        x0, x1, line_y = 620, 1940, y + 320
        draw.line([x0, line_y, x1, line_y], fill="#5B3F9A", width=7)
        step = (x1 - x0) / count
        for n in range(start_n, end_n + 1):
            x = x0 + (n - start_n) * step
            draw.line([x, line_y - 25, x, line_y + 25], fill="#5B3F9A", width=5)
            text(base, draw, template, n, [x - 45, line_y + 35, x + 45, line_y + 105], size=30, lines=1)
        for j in range(row["jumps"]):
            a = x0 + j * step; b = x0 + (j + 1) * step
            draw.arc([a, line_y - 150, b, line_y + 15], 180, 360, fill="#E25454", width=6)
        answer_choices(draw, base, template, row["choices"], [1850, y + 100, 2280, y + 570])
        y += 720


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
    y = 800
    for story in page["activity"]["mechanics"]["stories"]:
        row_box(common, draw, y, y + 650)
        common.paste_fit(canvas, assets[story["asset"]], [220, y + 25, 1570, y + 620])
        text(base, draw, template, story["question"], [1600, y + 60, 2260, y + 190], size=32, lines=2)
        answer_choices(draw, base, template, story["choices"], [1580, y + 230, 2270, y + 590])
        y += 720


def render_shape_match(canvas, draw, page, assets, base, template, common):
    m = page["activity"]["mechanics"]
    y0, row_h, gap = 800, 500, 35
    for i, name in enumerate(m["left"]):
        top = y0 + i * (row_h + gap); bottom = top + row_h
        common.panel(draw, [190, top, 1050, bottom], outline="#7E57C2", width=3)
        common.paste_fit(canvas, assets[name], [250, top + 50, 900, bottom - 50])
        common.circle(draw, base, template, 995, (top + bottom) // 2)
        right_name = m["right"][i]
        common.panel(draw, [1470, top, 2270, bottom], outline="#1768B3", width=3)
        common.circle(draw, base, template, 1520, (top + bottom) // 2)
        common.paste_fit(canvas, assets[right_name], [1600, top + 35, 2180, bottom - 35])


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
    model_strip(common, draw, base, template, page)

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
        "engine": "BCube Early Maths Curriculum-First Renderer V1",
        "page_id": args.page_id,
        "render_kind": render_kind,
        "artifact": str(args.output),
        "artifact_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "qa": {"curriculum_first": True, "fallback_used": False, "status": "TEST_CANDIDATE"},
    }
    args.evidence_output.parent.mkdir(parents=True, exist_ok=True)
    args.evidence_output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
