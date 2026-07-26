#!/usr/bin/env python3
"""Runtime learning-page helpers with explicit vertical breathing room.

This module reuses the approved runtime helper implementation and replaces only
its header geometry. It keeps a visible gap between the learning-goal banner,
instruction banner, completed-example panel, and first activity block.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "bcube-publishing-sdk/composer/compose_runtime_learning_page.py"

spec = importlib.util.spec_from_file_location("runtime_learning_page_base_spaced", BASE)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {BASE}")
base_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base_module
spec.loader.exec_module(base_module)

for name in dir(base_module):
    if not name.startswith("__"):
        globals()[name] = getattr(base_module, name)


def header(canvas, draw, page, book_title, logo, base, template):
    colours = template["colours"]
    typography = template["typography"]

    logo = logo.convert("RGBA")
    logo.thumbnail((300, 220), Image.Resampling.LANCZOS)
    canvas.paste(logo, (110 + (300 - logo.width) // 2, 35 + (220 - logo.height) // 2), logo)

    base.brand_title(draw, [book_title], [470, 45, 2320, 145], colours, typography)
    base.fitted_text(
        draw,
        page["identity"]["title"],
        [470, 145, 2320, 280],
        max_size=typography["page_title_max"],
        min_size=typography["page_title_min"],
        colour=colours["navy"],
        bold=True,
        max_lines=2,
    )

    # 20 px after title, 30 px between banners, 35 px before model panel.
    panel(draw, [150, 300, 2330, 420], fill=colours["blue"], outline="#1768B3", width=3)
    base.fitted_text(
        draw,
        "Learning goal: " + page["learning"]["objective"],
        [185, 310, 2295, 410],
        max_size=42,
        min_size=29,
        colour=colours["navy"],
        bold=True,
        max_lines=2,
    )

    panel(draw, [150, 450, 2330, 575], fill=colours["gold"], outline="#E1B12C", width=3)
    base.fitted_text(
        draw,
        page["learning"]["instruction"],
        [185, 462, 2295, 563],
        max_size=45,
        min_size=30,
        colour=colours["line"],
        bold=True,
        max_lines=2,
    )
