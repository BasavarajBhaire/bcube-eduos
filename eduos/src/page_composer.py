#!/usr/bin/env python3
"""Deterministic BCube A4 page composer.

This module intentionally refuses to generate logos, typography, or page layouts with AI.
It composes approved raster assets into a fixed A4 canvas. Pillow is optional and only
required when rendering.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

A4_WIDTH = 2480
A4_HEIGHT = 3508
DPI = 300


def build_plan(manifest: dict[str, Any]) -> dict[str, Any]:
    page = manifest["page"]
    return {
        "canvas": {"width": A4_WIDTH, "height": A4_HEIGHT, "dpi": DPI, "background": "#FFFFFF"},
        "template": manifest["composition"]["template"],
        "layers": [
            {"kind": "illustration", "asset": manifest["assets"]["illustration"], "mode": "contain"},
            {"kind": "logo", "asset": manifest["assets"]["logo"], "mode": "exact_asset"},
            {"kind": "title", "text": page["title"], "mode": "deterministic_text"},
            {"kind": "visible_text", "items": page["visible_text"], "mode": "deterministic_text"},
            {"kind": "page_number", "value": page["number"], "visible": page.get("show_page_number", True)},
        ],
        "output_filename": f"{manifest['identity']['prompt_id']}.png",
    }


def render(manifest: dict[str, Any], output_dir: Path) -> Path:
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise RuntimeError("Rendering requires Pillow: pip install Pillow") from exc

    plan = build_plan(manifest)
    canvas = Image.new("RGB", (A4_WIDTH, A4_HEIGHT), "white")
    draw = ImageDraw.Draw(canvas)
    # Phase 1 deliberately renders a preflight proof only. Approved templates will
    # provide exact coordinates and fonts in Phase 2; no AI layout fallback exists.
    draw.rectangle((100, 100, A4_WIDTH - 100, A4_HEIGHT - 100), outline="black", width=4)
    draw.text((140, 140), manifest["page"]["title"], fill="black")
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / plan["output_filename"]
    canvas.save(output, dpi=(DPI, DPI))
    return output


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("Usage: page_composer.py <manifest.json> [output-dir]", file=sys.stderr)
        return 2
    manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if len(sys.argv) == 2:
        print(json.dumps(build_plan(manifest), indent=2))
        return 0
    output = render(manifest, Path(sys.argv[2]))
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
