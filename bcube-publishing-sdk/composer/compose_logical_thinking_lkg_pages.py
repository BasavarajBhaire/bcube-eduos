#!/usr/bin/env python3
"""Dedicated page-specific composer for Logical Thinking Adventures LKG.

Every LT page ID is explicitly registered. Shared helpers are allowed, but no
page may fall back to the generic runtime page renderer.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any, Callable

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "bcube-publishing-sdk/composer/compose_runtime_learning_page.py"
LOADER = ROOT / "bcube-publishing-sdk/runtime/load_book_contract.py"
BASE = ROOT / "bcube-publishing-sdk/composer/compose_learning_page_v2.py"
TEMPLATE = ROOT / "bcube-publishing-sdk/templates/learning-page-v2.json"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def order(page: dict[str, Any]) -> list[str]:
    return list(page.get("mechanics", {}).get("asset_order") or page["illustration"]["assets"])


def choice_rows(rt, canvas, draw, page, assets, base, template, count: int):
    boxes = rt.grid_boxes(len(order(page)), top=690, bottom=2990)
    for name, box in zip(order(page), boxes):
        rt.panel(draw, box, outline="#7E57C2", width=3)
        rt.paste_fit(canvas, assets[name], [box[0] + 12, box[1] + 12, box[2] - 12, box[3] - 130])
        width = box[2] - box[0]
        for i in range(count):
            rt.circle(draw, base, template, box[0] + width * (i + 1) // (count + 1), box[3] - 65)


def find_difference(rt, canvas, draw, page, assets, base, template):
    names = order(page)
    if len(names) != 2:
        raise ValueError("Find the Difference requires two scenes")
    for name, box in zip(names, ([170, 700, 1210, 2960], [1270, 700, 2310, 2960])):
        rt.panel(draw, box, outline="#7E57C2", width=3)
        rt.paste_fit(canvas, assets[name], [box[0] + 12, box[1] + 12, box[2] - 12, box[3] - 12])


def spot_same(rt, canvas, draw, page, assets, base, template):
    choice_rows(rt, canvas, draw, page, assets, base, template, 3)


def odd_one_out(rt, canvas, draw, page, assets, base, template):
    choice_rows(rt, canvas, draw, page, assets, base, template, 4)


def match_pairs(rt, canvas, draw, page, assets, base, template):
    rt.render_match(canvas, draw, page, assets, base, template)


def hidden_objects(rt, canvas, draw, page, assets, base, template):
    rt.render_hero_targets(canvas, draw, page, assets, base, template)


def complete_pattern(rt, canvas, draw, page, assets, base, template):
    choice_rows(rt, canvas, draw, page, assets, base, template, 3)


def story_sequence(rt, canvas, draw, page, assets, base, template):
    boxes = rt.grid_boxes(len(order(page)), top=700, bottom=2960)
    for name, box in zip(order(page), boxes):
        rt.panel(draw, box, outline="#7E57C2", width=3)
        rt.paste_fit(canvas, assets[name], [box[0] + 12, box[1] + 12, box[2] - 12, box[3] - 125])
        rt.panel(draw, [box[0] + 35, box[3] - 100, box[0] + 150, box[3] - 18], fill="#FFF9DE", outline="#D9A91B", width=3, radius=16)


def sort_page(rt, canvas, draw, page, assets, base, template):
    rt.render_classification(canvas, draw, page, assets, base, template)


def compare_page(rt, canvas, draw, page, assets, base, template):
    rt.render_comparison(canvas, draw, page, assets, base, template)


def maze_or_code(rt, canvas, draw, page, assets, base, template):
    boxes = rt.grid_boxes(len(order(page)), top=700, bottom=2960)
    for name, box in zip(order(page), boxes):
        rt.panel(draw, box, outline="#7E57C2", width=3)
        rt.paste_fit(canvas, assets[name], [box[0] + 12, box[1] + 12, box[2] - 12, box[3] - 12])


def draw_finish(rt, canvas, draw, page, assets, base, template):
    boxes = rt.grid_boxes(len(order(page)), top=700, bottom=2960)
    for name, box in zip(order(page), boxes):
        mid = (box[0] + box[2]) // 2
        rt.panel(draw, box, outline="#7E57C2", width=3)
        rt.paste_fit(canvas, assets[name], [box[0] + 12, box[1] + 12, mid - 10, box[3] - 12])
        draw.line([mid, box[1] + 20, mid, box[3] - 20], fill="#B7A4D8", width=3)


def memory_page(rt, canvas, draw, page, assets, base, template):
    boxes = rt.grid_boxes(len(order(page)), top=700, bottom=2960)
    for i, (name, box) in enumerate(zip(order(page), boxes)):
        rt.panel(draw, box, outline="#7E57C2", width=3)
        rt.paste_fit(canvas, assets[name], [box[0] + 12, box[1] + 12, box[2] - 12, box[3] - 12])
        label = "LOOK" if i == 0 else "REMEMBER"
        base.fitted_text(draw, label, [box[0] + 35, box[1] + 25, box[2] - 35, box[1] + 100], max_size=34, min_size=26, colour=template["colours"]["navy"], bold=True, max_lines=1)


def review_page(rt, canvas, draw, page, assets, base, template):
    choice_rows(rt, canvas, draw, page, assets, base, template, 3)


def journal(rt, canvas, draw, page, assets, base, template):
    names = order(page)
    if names:
        rt.panel(draw, [180, 700, 2300, 1550], outline="#7E57C2", width=3)
        rt.paste_fit(canvas, assets[names[0]], [210, 730, 2270, 1520])
    rt.panel(draw, [180, 1620, 2300, 2870], fill="#FFFFFF", outline="#7E57C2", width=4)
    base.fitted_text(draw, "Draw one activity that made you think.", [250, 1660, 2230, 1790], max_size=40, min_size=30, colour=template["colours"]["navy"], bold=True, max_lines=2)


def celebration(rt, canvas, draw, page, assets, base, template):
    rt.render_asset_grid(canvas, draw, page, assets, base, template, controls=False)


def certificate(rt, canvas, draw, page, assets, base, template):
    rt.panel(draw, [260, 730, 2220, 2940], fill="#FFFDF2", outline="#D9A91B", width=8, radius=42)
    names = order(page)
    if names:
        rt.paste_fit(canvas, assets[names[0]], [400, 790, 2080, 1290])
    base.fitted_text(draw, "Certificate of Completion", [450, 1360, 2030, 1530], max_size=64, min_size=44, colour=template["colours"]["navy"], bold=True, max_lines=1)
    base.fitted_text(draw, "This certificate is proudly presented to", [500, 1610, 1980, 1750], max_size=40, min_size=30, colour=template["colours"]["line"], max_lines=1)
    draw.line([560, 1940, 1920, 1940], fill="#5B3F9A", width=4)
    base.fitted_text(draw, "for completing Logical Thinking Adventures", [500, 2030, 1980, 2200], max_size=42, min_size=30, colour=template["colours"]["line"], bold=True, max_lines=2)


def explorer(rt, canvas, draw, page, assets, base, template):
    rt.render_asset_grid(canvas, draw, page, assets, base, template, controls=False)
    y = 2700
    for label in ("I looked carefully", "I matched", "I sorted", "I solved"):
        rt.circle(draw, base, template, 350, y)
        base.fitted_text(draw, label, [430, y - 45, 2100, y + 45], max_size=34, min_size=26, colour=template["colours"]["line"], align="left", max_lines=1)
        y += 90


Renderer = Callable[..., None]
PAGE_RENDERERS: dict[str, Renderer] = {
    "LT-LKG-V4-P008": find_difference,
    "LT-LKG-V4-P009": spot_same,
    "LT-LKG-V4-P010": odd_one_out,
    "LT-LKG-V4-P011": match_pairs,
    "LT-LKG-V4-P012": hidden_objects,
    "LT-LKG-V4-P013": complete_pattern,
    "LT-LKG-V4-P014": story_sequence,
    "LT-LKG-V4-P015": complete_pattern,
    "LT-LKG-V4-P016": complete_pattern,
    "LT-LKG-V4-P017": sort_page,
    "LT-LKG-V4-P018": sort_page,
    "LT-LKG-V4-P019": sort_page,
    "LT-LKG-V4-P020": match_pairs,
    "LT-LKG-V4-P021": review_page,
    "LT-LKG-V4-P022": match_pairs,
    "LT-LKG-V4-P023": compare_page,
    "LT-LKG-V4-P024": compare_page,
    "LT-LKG-V4-P025": compare_page,
    "LT-LKG-V4-P026": maze_or_code,
    "LT-LKG-V4-P027": review_page,
    "LT-LKG-V4-P028": review_page,
    "LT-LKG-V4-P029": draw_finish,
    "LT-LKG-V4-P030": memory_page,
    "LT-LKG-V4-P031": match_pairs,
    "LT-LKG-V4-P032": match_pairs,
    "LT-LKG-V4-P033": review_page,
    "LT-LKG-V4-P034": review_page,
    "LT-LKG-V4-P035": maze_or_code,
    "LT-LKG-V4-P036": review_page,
    "LT-LKG-V4-P037": review_page,
    "LT-LKG-V4-P038": review_page,
    "LT-LKG-V4-P039": review_page,
    "LT-LKG-V4-P040": journal,
    "LT-LKG-V4-P041": celebration,
    "LT-LKG-V4-P042": certificate,
    "LT-LKG-V4-P043": explorer,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", required=True)
    parser.add_argument("--book", required=True)
    parser.add_argument("--page-id", required=True)
    parser.add_argument("--illustration", type=Path, required=True)
    parser.add_argument("--logo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    args = parser.parse_args()

    expected = {f"LT-LKG-V4-P{n:03d}" for n in range(8, 44)}
    if set(PAGE_RENDERERS) != expected:
        raise ValueError("Logical Thinking page registry is incomplete")
    if args.page_id not in PAGE_RENDERERS:
        raise ValueError(f"No dedicated renderer for {args.page_id}")

    rt = module("runtime", RUNTIME)
    loader = module("loader", LOADER)
    base = module("base", BASE)
    page = loader.load_page_contract(level=args.level, book_slug=args.book, page_id=args.page_id)
    rt.validate(page)
    template = load_json(TEMPLATE)
    spec = template["canvas"]
    canvas = Image.new("RGB", (spec["width"], spec["height"]), template["colours"]["background"])
    draw = ImageDraw.Draw(canvas)
    source = Image.open(args.illustration).convert("RGBA")
    assets = rt.crop_assets(source, page["illustration"]["asset_crops"])

    rt.header(canvas, draw, page, "Logical Thinking Adventures", Image.open(args.logo), base, template)
    PAGE_RENDERERS[args.page_id](rt, canvas, draw, page, assets, base, template)
    rt.teacher(draw, page, base, template)
    printed = page["identity"].get("printed_page")
    if printed is not None:
        base.fitted_text(draw, str(printed), [2200, 3270, 2370, 3390], max_size=46, min_size=36, colour=template["colours"]["muted"], bold=True, max_lines=1)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.output, dpi=(300, 300))
    args.evidence_output.parent.mkdir(parents=True, exist_ok=True)
    args.evidence_output.write_text(json.dumps({"page_id": args.page_id, "renderer": "compose_logical_thinking_lkg_pages.py", "function": PAGE_RENDERERS[args.page_id].__name__, "status": "TEST_CANDIDATE"}, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
