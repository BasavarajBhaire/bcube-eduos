#!/usr/bin/env python3
"""BCube Nursery cover composer v1.2.

Loads the locked v1 compositor, replaces only the illustration-placement strategy,
and keeps all publishing components deterministic.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "bcube-publishing-sdk/composer/compose_nursery_cover.py"

spec = importlib.util.spec_from_file_location("bcube_cover_v11", BASE)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load base composer: {BASE}")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def paste_adaptive_illustration(
    canvas: Image.Image,
    asset_path: Path,
    bounds: list[int],
    background: str,
    safe_inset: int = 28,
    radius: int = 36,
) -> dict[str, Any]:
    """Trim only empty near-white margins, preserve subjects, and bottom-align."""
    asset = Image.open(asset_path).convert("RGB")
    source_size = [asset.width, asset.height]

    mask = Image.new("L", asset.size, 0)
    mask.putdata([255 if min(red, green, blue) < 246 else 0 for red, green, blue in asset.getdata()])
    bbox = mask.getbbox()
    trim_box = None
    if bbox:
        padding = 12
        trim_box = [
            max(0, bbox[0] - padding),
            max(0, bbox[1] - padding),
            min(asset.width, bbox[2] + padding),
            min(asset.height, bbox[3] + padding),
        ]
        asset = asset.crop(tuple(trim_box))

    x0, y0, x1, y1 = bounds
    inner = [x0 + safe_inset, y0 + safe_inset, x1 - safe_inset, y1 - safe_inset]
    target_w, target_h = inner[2] - inner[0], inner[3] - inner[1]
    scale = min(target_w / asset.width, target_h / asset.height)
    rendered_w = max(1, round(asset.width * scale))
    rendered_h = max(1, round(asset.height * scale))
    resized = asset.resize((rendered_w, rendered_h), Image.Resampling.LANCZOS)

    px = inner[0] + (target_w - rendered_w) // 2
    py = inner[3] - rendered_h

    frame_layer = Image.new("RGB", (x1 - x0, y1 - y0), background)
    frame_layer.paste(resized, (px - x0, py - y0))
    rounded_mask = Image.new("L", frame_layer.size, 0)
    ImageDraw.Draw(rounded_mask).rounded_rectangle(
        (0, 0, frame_layer.width - 1, frame_layer.height - 1),
        radius=radius,
        fill=255,
    )
    canvas.paste(frame_layer, (x0, y0), rounded_mask)

    occupancy = (rendered_w * rendered_h) / max(1, target_w * target_h)
    return {
        "mode": "contain-trimmed-bottom",
        "source_size": source_size,
        "trim_box": trim_box,
        "frame_bounds": bounds,
        "safe_inset": safe_inset,
        "vertical_align": "bottom",
        "rendered_bounds": [px, py, px + rendered_w, py + rendered_h],
        "occupancy_ratio": round(occupancy, 6),
        "cropped_subjects": False,
    }


base.paste_safe_illustration = paste_adaptive_illustration


if __name__ == "__main__":
    raise SystemExit(base.main())
