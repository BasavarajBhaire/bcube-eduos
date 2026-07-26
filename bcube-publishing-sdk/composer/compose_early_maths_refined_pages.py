#!/usr/bin/env python3
"""Dedicated fail-closed renderers for Early Maths pages that cannot use generic grids."""
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


def choices(draw, base, template, values, box):
    x0, y0, x1, y1 = box
    if not values:
        raise ValueError("Page-specific choices are required")
    gap = (x1 - x0) // (len(values) + 1)
    for i, value in enumerate(values, 1):
        cx = x0 + gap * i
        cy = (y0 + y1) // 2
        draw.ellipse([cx - 48, cy - 48, cx + 48, cy + 48], fill="#FFFFFF", outline=template["colours"]["purple"], width=4)
        base.fitted_text(draw, str(value), [cx - 42, cy - 42, cx + 42, cy + 42], max_size=34, min_size=22, colour=template["colours"]["navy"], bold=True, max_lines=1)


def prompt(draw, base, template, text, box):
    base.fitted_text(draw, text, box, max_size=31, min_size=22, colour=template["colours"]["navy"], bold=True, align="left", max_lines=2)


def render_p009(canvas, draw, page, assets, base, template, common):
    cards = page["activity"]["mechanics"].get("cards")
    if not cards or len(cards) != 5:
        raise ValueError("P009 requires five exact count cards")
    boxes = [[170, 700, 1130, 1390], [1350, 700, 2310, 1390], [170, 1460, 1130, 2150], [1350, 1460, 2310, 2150], [590, 2220, 1890, 2940]]
    for card, box in zip(cards, boxes):
        asset = card["asset"]
        common.panel(draw, box, outline="#7E57C2", width=3)
        common.paste_fit(canvas, assets[asset], [box[0] + 18, box[1] + 18, box[2] - 18, box[3] - 145])
        choices(draw, base, template, card["choices"], [box[0] + 80, box[3] - 130, box[2] - 80, box[3] - 20])


def render_p015(canvas, draw, page, assets, base, template, common):
    problems = page["activity"]["mechanics"].get("problems")
    if not problems or len(problems) != 3:
        raise ValueError("P015 requires three addition problems")
    y = 700
    for problem in problems:
        box = [180, y, 2300, y + 700]
        common.panel(draw, box, outline="#7E57C2", width=3)
        left = problem["left_asset"]; right = problem["right_asset"]
        common.paste_fit(canvas, assets[left], [220, y + 50, 930, y + 500])
        common.paste_fit(canvas, assets[right], [1150, y + 50, 1860, y + 500])
        base.fitted_text(draw, "+", [950, y + 150, 1130, y + 350], max_size=80, min_size=58, colour=template["colours"]["purple"], bold=True, max_lines=1)
        base.fitted_text(draw, "=", [1880, y + 150, 2040, y + 350], max_size=70, min_size=50, colour=template["colours"]["purple"], bold=True, max_lines=1)
        choices(draw, base, template, problem["choices"], [1450, y + 500, 2240, y + 670])
        y += 760


def render_p016(canvas, draw, page, assets, base, template, common):
    problems = page["activity"]["mechanics"].get("problems")
    if not problems or len(problems) != 3:
        raise ValueError("P016 requires three subtraction problems")
    y = 700
    for problem in problems:
        box = [180, y, 2300, y + 700]
        common.panel(draw, box, outline="#7E57C2", width=3)
        asset = problem["asset"]
        common.paste_fit(canvas, assets[asset], [220, y + 30, 1580, y + 520])
        removed = int(problem["removed"])
        start = int(problem["start"])
        remain = int(problem["remain"])
        prompt(draw, base, template, f"Cross out {removed}.  {start} − {removed} =", [1620, y + 80, 2240, y + 250])
        choices(draw, base, template, problem["choices"], [1580, y + 360, 2260, y + 620])
        if start - removed != remain:
            raise ValueError("P016 subtraction contract is inconsistent")
        y += 760


def render_p019(canvas, draw, page, assets, base, template, common):
    rows = page["activity"]["mechanics"].get("rows")
    if not rows or len(rows) != 3:
        raise ValueError("P019 requires three number-line rows")
    y = 720
    for row in rows:
        box = [180, y, 2300, y + 680]
        common.panel(draw, box, outline="#7E57C2", width=3)
        common.paste_fit(canvas, assets[row["asset"]], [210, y + 15, 2260, y + 420])
        start = int(row["start"]); jumps = int(row["jumps"]); landing = int(row["landing"])
        if start + jumps != landing:
            raise ValueError("P019 jump contract is inconsistent")
        line_y = y + 470
        x0, x1 = 350, 1900
        draw.line([x0, line_y, x1, line_y], fill="#5B3F9A", width=7)
        step = (x1 - x0) / max(1, jumps + 1)
        for i in range(jumps):
            a = x0 + i * step
            b = x0 + (i + 1) * step
            draw.arc([a, line_y - 145, b, line_y + 20], 180, 360, fill="#E25454", width=6)
        prompt(draw, base, template, f"Start at {start}. Jump {jumps}.", [250, y + 520, 1200, y + 650])
        choices(draw, base, template, row["choices"], [1350, y + 500, 2240, y + 660])
        y += 740


def render_p021(canvas, draw, page, assets, base, template, common):
    stories = page["activity"]["mechanics"].get("stories")
    if not stories or len(stories) != 3:
        raise ValueError("P021 requires three complete picture stories")
    y = 700
    for story in stories:
        box = [180, y, 2300, y + 700]
        common.panel(draw, box, outline="#7E57C2", width=3)
        common.paste_fit(canvas, assets[story["asset"]], [210, y + 20, 1700, y + 670])
        prompt(draw, base, template, "Count, think, and choose.", [1740, y + 80, 2250, y + 220])
        choices(draw, base, template, story["choices"], [1710, y + 300, 2260, y + 620])
        y += 760


def render_p035(canvas, draw, page, assets, base, template, common):
    rows = page["activity"]["mechanics"].get("rows")
    if not rows or len(rows) != 4:
        raise ValueError("P035 requires four routine events")
    boxes = [[170, 720, 1130, 1720], [1350, 720, 2310, 1720], [170, 1820, 1130, 2820], [1350, 1820, 2310, 2820]]
    for row, box in zip(rows, boxes):
        common.panel(draw, box, outline="#7E57C2", width=3)
        common.paste_fit(canvas, assets[row["asset"]], [box[0] + 20, box[1] + 20, box[2] - 20, box[3] - 180])
        prompt(draw, base, template, row["label"].title(), [box[0] + 100, box[3] - 160, box[2] - 180, box[3] - 40])
        common.panel(draw, [box[2] - 145, box[3] - 155, box[2] - 35, box[3] - 45], fill="#FFF9DE", outline="#D9A91B", width=3, radius=16)


def render_p037(canvas, draw, page, assets, base, template, common):
    mechanics = page["activity"]["mechanics"]
    matrix = mechanics.get("matrix")
    items = mechanics.get("items")
    if not matrix or not items:
        raise ValueError("P037 requires matrix and items")
    rows = matrix["rows"]; cols = matrix["columns"]
    left, top, right, bottom = 420, 760, 2260, 2460
    cell_w = (right - left) // len(cols); cell_h = (bottom - top) // len(rows)
    for c, label in enumerate(cols):
        prompt(draw, base, template, label.upper(), [left + c * cell_w, 660, left + (c + 1) * cell_w, 750])
    for r, label in enumerate(rows):
        prompt(draw, base, template, label.upper(), [170, top + r * cell_h, 400, top + (r + 1) * cell_h])
        for c in range(len(cols)):
            common.panel(draw, [left + c * cell_w, top + r * cell_h, left + (c + 1) * cell_w, top + (r + 1) * cell_h], outline="#7E57C2", width=3, radius=8)
    item_boxes = common.grid_boxes(len(items), top=2550, bottom=2990)
    for item, box in zip(items, item_boxes):
        common.panel(draw, box, outline="#7E57C2", width=3)
        common.paste_fit(canvas, assets[item["asset"]], box)


def render_p038(canvas, draw, page, assets, base, template, common):
    categories = page["activity"]["mechanics"].get("categories")
    questions = page["activity"]["mechanics"].get("questions")
    if not categories or len(categories) != 4:
        raise ValueError("P038 requires four graph categories")
    y = 720
    for category in categories:
        box = [180, y, 2300, y + 430]
        common.panel(draw, box, outline="#7E57C2", width=3)
        prompt(draw, base, template, category["label"], [220, y + 60, 600, y + 170])
        common.paste_fit(canvas, assets[category["asset"]], [620, y + 25, 1940, y + 405])
        common.panel(draw, [2030, y + 130, 2200, y + 300], fill="#FFF9DE", outline="#D9A91B", width=3, radius=16)
        y += 470
    if questions:
        prompt(draw, base, template, "   ".join(q["prompt"] for q in questions), [260, 2670, 2220, 2920])


def render_p043(canvas, draw, page, assets, base, template, common):
    mechanics = page["activity"]["mechanics"]
    hero = mechanics.get("hero")
    choices_data = mechanics.get("choices")
    if not hero or not choices_data:
        raise ValueError("P043 requires hero and skill choices")
    common.panel(draw, [180, 700, 2300, 2140], outline="#7E57C2", width=3)
    common.paste_fit(canvas, assets[hero], [210, 730, 2270, 2110])
    boxes = [[180, 2210, 850, 2860], [905, 2210, 1575, 2860], [1630, 2210, 2300, 2860]]
    for choice, box in zip(choices_data, boxes):
        common.panel(draw, box, outline="#7E57C2", width=3)
        common.paste_fit(canvas, assets[choice["asset"]], [box[0] + 15, box[1] + 15, box[2] - 15, box[3] - 130])
        prompt(draw, base, template, choice["label"], [box[0] + 60, box[3] - 120, box[2] - 60, box[3] - 20])
    prompt(draw, base, template, mechanics.get("sentence_starter", "I can ________."), [500, 2890, 1980, 3030])


RENDERERS = {9: render_p009, 15: render_p015, 16: render_p016, 19: render_p019, 21: render_p021, 35: render_p035, 37: render_p037, 38: render_p038, 43: render_p043}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", required=True); parser.add_argument("--book", required=True)
    parser.add_argument("--page-id", required=True); parser.add_argument("--illustration", type=Path, required=True)
    parser.add_argument("--logo", type=Path, required=True); parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    args = parser.parse_args()

    common = load_module("common_runtime", COMMON_PATH)
    base = load_module("runtime_base", BASE_PATH)
    loader = load_module("runtime_loader", LOADER_PATH)
    page = loader.load_page_contract(level=args.level, book_slug=args.book, page_id=args.page_id)
    common.validate(page)
    page_no = int(page["identity"]["physical_page"])
    renderer = RENDERERS.get(page_no)
    if renderer is None:
        raise ValueError(f"No dedicated Early Maths renderer for physical page {page_no}")

    manifest = load_json(ROOT / "runtime-contracts/manifest.json")
    relative = manifest["levels"][args.level.lower()]["books"][args.book]
    book = load_json(ROOT / "runtime-contracts" / relative)
    template = load_json(TEMPLATE_PATH)
    spec = template["canvas"]
    canvas = Image.new("RGB", (spec["width"], spec["height"]), template["colours"]["background"])
    draw = ImageDraw.Draw(canvas)
    common.header(canvas, draw, page, book["book"]["title"], Image.open(args.logo), base, template)
    source = Image.open(args.illustration).convert("RGBA")
    assets = common.crop_assets(source, page["illustration"]["asset_crops"])
    renderer(canvas, draw, page, assets, base, template, common)
    common.teacher(draw, page, base, template)
    if page["identity"].get("printed_page") is not None:
        base.fitted_text(draw, str(page["identity"]["printed_page"]), [2200, 3270, 2370, 3390], max_size=46, min_size=36, colour=template["colours"]["muted"], bold=True, max_lines=1)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.output, "PNG", dpi=(spec["dpi"], spec["dpi"]))
    evidence = {
        "engine": "BCube Early Maths Dedicated Renderer V1",
        "page_id": args.page_id,
        "physical_page": page_no,
        "render_kind": page["activity"]["render_kind"],
        "artifact": str(args.output),
        "artifact_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "qa": {"runtime_contract_used": True, "fallback_used": False, "dedicated_renderer": True, "status": "TEST_CANDIDATE"}
    }
    args.evidence_output.parent.mkdir(parents=True, exist_ok=True)
    args.evidence_output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
