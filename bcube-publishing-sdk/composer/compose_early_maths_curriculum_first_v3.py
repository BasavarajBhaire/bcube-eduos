#!/usr/bin/env python3
"""Early Maths P009-P021 composer with completed models and QA fixes.

Fixes:
- consistent vertical padding between goal, instruction, model and activity;
- larger P012 YES/NO response targets;
- stronger P018 starts, jump endpoints and adjacent answer choices;
- explicit P020 visual change strips;
- actual circle-to-clock completed model on P021.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "bcube-publishing-sdk/composer/compose_early_maths_curriculum_first_v2.py"
SPACED_COMMON = ROOT / "bcube-publishing-sdk/composer/compose_runtime_learning_page_spaced.py"

spec = importlib.util.spec_from_file_location("early_maths_curriculum_first_v2_module", V2)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {V2}")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
original = module.original
original.COMMON_PATH = SPACED_COMMON


def render_equal_groups(canvas, draw, page, assets, base, template, common):
    """P012: make the response action large and visually separate."""
    y = 835
    for row in page["activity"]["mechanics"]["rows"]:
        original.row_box(common, draw, y, y + 625)
        original.paste_asset(common, canvas, assets[row["left"]], [230, y + 25, 1080, y + 410])
        original.paste_asset(common, canvas, assets[row["right"]], [1150, y + 25, 2000, y + 410])

        original.text(base, draw, template, "Are they equal?", [250, y + 430, 1120, y + 580], size=31, lines=1)
        for value, cx in (("YES", 1540), ("NO", 1950)):
            radius = 82
            draw.ellipse(
                [cx - radius, y + 505 - radius, cx + radius, y + 505 + radius],
                fill="#FFFFFF",
                outline=template["colours"]["purple"],
                width=6,
            )
            original.text(
                base,
                draw,
                template,
                value,
                [cx - 68, y + 437, cx + 68, y + 573],
                size=38,
                lines=1,
            )
        y += 700


def render_number_line(canvas, draw, page, assets, base, template, common):
    """P018: emphasise start, every jump endpoint and nearby choices."""
    y = 835
    for row in page["activity"]["mechanics"]["rows"]:
        original.row_box(common, draw, y, y + 625)
        original.paste_asset(common, canvas, assets[row["asset"]], [220, y + 125, 555, y + 515])

        start_n, end_n = row["range"]
        count = end_n - start_n
        x0, x1, line_y = 640, 1710, y + 315
        draw.line([x0, line_y, x1, line_y], fill="#5B3F9A", width=8)
        step = (x1 - x0) / count

        for n in range(start_n, end_n + 1):
            x = x0 + (n - start_n) * step
            draw.line([x, line_y - 28, x, line_y + 28], fill="#5B3F9A", width=5)
            original.text(base, draw, template, n, [x - 44, line_y + 38, x + 44, line_y + 110], size=31, lines=1)

        # Strong start marker and label.
        draw.ellipse([x0 - 23, line_y - 23, x0 + 23, line_y + 23], fill="#E25454", outline="#FFFFFF", width=4)
        original.text(base, draw, template, "START", [x0 - 90, line_y - 105, x0 + 90, line_y - 48], size=23, colour="#E25454", lines=1)

        # Arcs plus a visible endpoint dot after every jump.
        for jump_index in range(row["jumps"]):
            a = x0 + jump_index * step
            b = x0 + (jump_index + 1) * step
            draw.arc([a, line_y - 155, b, line_y + 15], 180, 360, fill="#E25454", width=7)
            draw.ellipse([b - 11, line_y - 11, b + 11, line_y + 11], fill="#E25454")

        # Bring the response panel closer and enlarge child targets.
        common.panel(draw, [1760, y + 85, 2270, y + 560], fill="#FFFDF7", outline="#D9A91B", width=4, radius=22)
        original.text(base, draw, template, "Where do you land?", [1790, y + 110, 2240, y + 205], size=28, lines=2)
        original.answer_choices(draw, base, template, row["choices"], [1780, y + 255, 2250, y + 525], radius=62)
        y += 700


def story_change_strip(draw, base, template, story, y):
    """Show the exact start/change relation without revealing the result."""
    if story["asset"] == "story_ducks":
        start, operation, change = 2, "+", 1
    elif story["asset"] == "story_balls":
        start, operation, change = 1, "+", 2
    elif story["asset"] == "story_biscuits":
        start, operation, change = 3, "−", 1
    else:
        raise ValueError(f"Unsupported maths-story asset: {story['asset']}")

    common_box = [250, y + 475, 1560, y + 590]
    draw.rounded_rectangle(common_box, radius=20, fill="#F4EEFF", outline="#7E57C2", width=4)
    original.text(base, draw, template, "START", [285, y + 492, 535, y + 568], size=24, lines=1)
    original.text(base, draw, template, start, [550, y + 480, 700, y + 580], size=42, lines=1)
    original.text(base, draw, template, operation, [740, y + 480, 870, y + 580], size=42, colour="#E25454", lines=1)
    original.text(base, draw, template, change, [900, y + 480, 1050, y + 580], size=42, lines=1)
    original.text(base, draw, template, "= ?", [1110, y + 480, 1360, y + 580], size=42, lines=1)


def render_math_stories(canvas, draw, page, assets, base, template, common):
    """P020: preserve the approved scene and make the change unambiguous."""
    y = 835
    for story in page["activity"]["mechanics"]["stories"]:
        original.row_box(common, draw, y, y + 625)
        original.paste_asset(common, canvas, assets[story["asset"]], [220, y + 20, 1570, y + 455])
        story_change_strip(draw, base, template, story, y)

        common.panel(draw, [1600, y + 55, 2270, y + 565], fill="#FFFDF7", outline="#D9A91B", width=4, radius=22)
        original.text(base, draw, template, story["question"], [1640, y + 85, 2230, y + 205], size=31, lines=2)
        original.answer_choices(draw, base, template, story["choices"], [1625, y + 260, 2245, y + 525], radius=62)
        y += 700


def visual_model(common, canvas, draw, base, template, page, render_kind, assets):
    """Use V2 models, except P021 uses the real approved circle and clock assets."""
    if render_kind != "curriculum-shape-match":
        return module.visual_model(common, canvas, draw, base, template, page, render_kind, assets)

    common.panel(draw, [180, 610, 2300, 790], fill="#F4EEFF", outline="#7E57C2", width=4)
    original.text(base, draw, template, "COMPLETED EXAMPLE", [210, 635, 560, 765], size=27, lines=2)

    if "shape_circle" not in assets or "object_clock" not in assets:
        raise ValueError("P021 completed model requires shape_circle and object_clock")

    original.paste_asset(common, canvas, assets["shape_circle"], [650, 625, 900, 775])
    module.connector(draw, 1010, 700, 1460, 700)
    original.paste_asset(common, canvas, assets["object_clock"], [1570, 615, 1880, 785])
    original.text(base, draw, template, "circle matches clock", [1900, 645, 2240, 755], size=25, bold=False, lines=2)


original.visual_model = visual_model
original.RENDERERS["curriculum-equal-groups"] = render_equal_groups
original.RENDERERS["curriculum-number-line"] = render_number_line
original.RENDERERS["curriculum-math-stories"] = render_math_stories

if __name__ == "__main__":
    raise SystemExit(original.main())
