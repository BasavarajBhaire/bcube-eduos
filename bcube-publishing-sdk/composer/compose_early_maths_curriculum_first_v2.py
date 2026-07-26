#!/usr/bin/env python3
"""Early Maths curriculum-first composer with mandatory completed model examples.

This wrapper preserves the approved P009-P021 renderers while replacing the
placeholder model sentence with a visible, solved example for every mechanic.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

from PIL import ImageDraw

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / "bcube-publishing-sdk/composer/compose_early_maths_curriculum_first.py"


def load_original():
    spec = importlib.util.spec_from_file_location("early_maths_curriculum_first_v1", ORIGINAL)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {ORIGINAL}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


original = load_original()


def model_panel(common, draw):
    common.panel(draw, [180, 610, 2300, 800], fill="#F4EEFF", outline="#7E57C2", width=4)


def label(base, draw, template):
    original.text(base, draw, template, "COMPLETED EXAMPLE", [210, 635, 560, 775], size=27, lines=2)


def dot(draw: ImageDraw.ImageDraw, x: int, y: int, fill: str = "#F5C84C", r: int = 27):
    draw.ellipse([x-r, y-r, x+r, y+r], fill=fill, outline="#35405A", width=3)


def circled_text(base, draw, template, value, cx, cy, radius=48):
    draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], fill="#FFFFFF", outline="#E25454", width=6)
    original.text(base, draw, template, value, [cx-radius+6, cy-radius+6, cx+radius-6, cy+radius-6], size=34, lines=1)


def connector(draw, x0, y0, x1, y1):
    draw.ellipse([x0-20, y0-20, x0+20, y0+20], fill="#FFFFFF", outline="#7E57C2", width=4)
    draw.line([x0+20, y0, x1-20, y1], fill="#7E57C2", width=6)
    draw.ellipse([x1-20, y1-20, x1+20, y1+20], fill="#FFFFFF", outline="#7E57C2", width=4)


def visual_model(common, canvas, draw, base, template, page, render_kind, assets):
    model_panel(common, draw)
    label(base, draw, template)
    y = 705

    if render_kind == "curriculum-count-match":
        for x in (700, 800, 900):
            draw.regular_polygon((x, y, 32), 5, rotation=-90, fill="#F5C84C", outline="#35405A")
        connector(draw, 1030, y, 1510, y)
        original.text(base, draw, template, "3", [1600, 645, 1800, 770], size=62, lines=1)
        return

    if render_kind == "curriculum-count-circle":
        if "group_1_apple" in assets:
            original.paste_asset(common, canvas, assets["group_1_apple"], [650, 625, 930, 785])
        else:
            dot(draw, 790, y, "#E25454", 45)
        for value, cx in zip((1, 2, 3), (1200, 1450, 1700)):
            if value == 1:
                circled_text(base, draw, template, value, cx, y)
            else:
                original.text(base, draw, template, value, [cx-45, y-45, cx+45, y+45], size=34, lines=1)
        return

    if render_kind == "curriculum-quantity-comparison":
        for x in (710, 790):
            dot(draw, x, y, "#E25454")
        for x in (1190, 1270, 1350, 1430):
            dot(draw, x, y, "#E25454")
        draw.rounded_rectangle([1125, 650, 1495, 760], radius=28, outline="#E25454", width=6)
        original.text(base, draw, template, "MORE", [1600, 650, 1940, 760], size=30, lines=1)
        return

    if render_kind == "curriculum-equal-groups":
        for x in (690, 770, 850):
            dot(draw, x, y, "#F5A35C")
        for x in (1110, 1190, 1270):
            dot(draw, x, y, "#F5A35C")
        circled_text(base, draw, template, "YES", 1670, y, 58)
        original.text(base, draw, template, "NO", [1840, 660, 2010, 750], size=30, lines=1)
        return

    if render_kind == "curriculum-missing-number":
        for value, cx in zip((1, 2, 3), (760, 1080, 1400)):
            fill = "#FFF9DE" if value == 2 else "#FFFFFF"
            common.panel(draw, [cx-80, 650, cx+80, 760], fill=fill, outline="#D9A91B", width=4, radius=18)
            original.text(base, draw, template, value, [cx-65, 660, cx+65, 750], size=42, lines=1)
        original.text(base, draw, template, "2 fills the blank", [1580, 650, 2140, 760], size=28, bold=False, lines=1)
        return

    if render_kind == "curriculum-picture-addition":
        dot(draw, 720, y, "#5FA8D3", 34)
        original.text(base, draw, template, "+", [850, 655, 980, 755], size=52, lines=1)
        dot(draw, 1110, y, "#5FA8D3", 34)
        original.text(base, draw, template, "=", [1240, 655, 1370, 755], size=48, lines=1)
        circled_text(base, draw, template, 2, 1600, y)
        return

    if render_kind == "curriculum-picture-subtraction":
        xs = (700, 800, 900)
        for x in xs:
            dot(draw, x, y, "#E25454", 34)
        draw.line([865, 670, 935, 740], fill="#7E57C2", width=7)
        draw.line([935, 670, 865, 740], fill="#7E57C2", width=7)
        original.text(base, draw, template, "=", [1110, 655, 1240, 755], size=48, lines=1)
        circled_text(base, draw, template, 2, 1490, y)
        return

    if render_kind == "curriculum-before-after":
        for value, cx in zip((4, 5, 6), (760, 1120, 1480)):
            common.panel(draw, [cx-100, 650, cx+100, 760], fill="#FFFFFF", outline="#7E57C2", width=4, radius=18)
            original.text(base, draw, template, value, [cx-80, 660, cx+80, 750], size=42, lines=1)
        return

    if render_kind == "curriculum-number-order":
        original.text(base, draw, template, "3   1   2", [650, 630, 1150, 700], size=34, lines=1)
        original.text(base, draw, template, "→", [1180, 645, 1330, 755], size=48, lines=1)
        original.text(base, draw, template, "1   2   3", [1380, 630, 1900, 700], size=34, lines=1)
        draw.line([1390, 745, 1880, 745], fill="#E25454", width=5)
        return

    if render_kind == "curriculum-number-line":
        x0, x1 = 680, 1580
        draw.line([x0, y, x1, y], fill="#5B3F9A", width=6)
        step = (x1-x0)/5
        for n in range(6):
            x = x0+n*step
            draw.line([x, y-18, x, y+18], fill="#5B3F9A", width=4)
            original.text(base, draw, template, n, [x-30, y+22, x+30, y+65], size=22, lines=1)
        draw.arc([x0, y-90, x0+step, y+5], 180, 360, fill="#E25454", width=6)
        circled_text(base, draw, template, 1, 1840, y)
        return

    if render_kind == "curriculum-numeral-comparison":
        original.text(base, draw, template, "4", [700, 645, 900, 765], size=62, lines=1)
        original.text(base, draw, template, "<", [1040, 650, 1240, 760], size=58, colour="#E25454", lines=1)
        original.text(base, draw, template, "7", [1380, 645, 1580, 765], size=62, lines=1)
        original.text(base, draw, template, "4 is less than 7", [1660, 655, 2200, 755], size=25, bold=False, lines=1)
        return

    if render_kind == "curriculum-math-stories":
        dot(draw, 700, y, "#E25454", 34)
        dot(draw, 800, y, "#E25454", 34)
        original.text(base, draw, template, "+", [920, 655, 1040, 755], size=48, lines=1)
        dot(draw, 1160, y, "#E25454", 34)
        original.text(base, draw, template, "=", [1280, 655, 1400, 755], size=46, lines=1)
        circled_text(base, draw, template, 3, 1610, y)
        return

    if render_kind == "curriculum-shape-match":
        draw.ellipse([680, 655, 800, 755], fill="#F5A35C", outline="#35405A", width=5)
        connector(draw, 930, y, 1430, y)
        draw.ellipse([1600, 645, 1740, 765], fill="#FFF7D6", outline="#35405A", width=5)
        original.text(base, draw, template, "circle → round object", [1790, 655, 2220, 755], size=24, bold=False, lines=2)
        return

    raise ValueError(f"No completed model implementation for {render_kind}")


original.visual_model = visual_model

if __name__ == "__main__":
    raise SystemExit(original.main())
