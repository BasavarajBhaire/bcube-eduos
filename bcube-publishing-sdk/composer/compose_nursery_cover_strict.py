#!/usr/bin/env python3
"""Strict adaptive Nursery cover compositor.

Delegates all publishing geometry to the approved compositor while replacing
only the illustration placement routine with fail-closed adaptive trimming,
bottom alignment, and minimum occupancy enforcement.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
LEGACY_PATH = HERE / "compose_nursery_cover.py"
_spec = importlib.util.spec_from_file_location("bcube_cover_base", LEGACY_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Unable to load base compositor: {LEGACY_PATH}")
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)


def _content_bbox(asset: Image.Image, *, threshold: int = 246, colour_delta: int = 8) -> list[int]:
    """Return a conservative box around non-empty content."""
    probe = asset.resize(
        (max(1, asset.width // 4), max(1, asset.height // 4)),
        Image.Resampling.BILINEAR,
    )
    mask = Image.new("L", probe.size, 0)
    mask.putdata([
        255 if min(r, g, b) < threshold or max(r, g, b) - min(r, g, b) > colour_delta else 0
        for r, g, b in probe.getdata()
    ])
    bbox = mask.getbbox()
    if not bbox:
        return [0, 0, asset.width, asset.height]
    sx, sy = asset.width / probe.width, asset.height / probe.height
    padding = 12
    return [
        max(0, int(bbox[0] * sx) - padding),
        max(0, int(bbox[1] * sy) - padding),
        min(asset.width, int(bbox[2] * sx) + padding),
        min(asset.height, int(bbox[3] * sy) + padding),
    ]


def paste_strict_illustration(
    canvas: Image.Image,
    asset_path: Path,
    bounds: list[int],
    background: str,
    safe_inset: int = 20,
    radius: int = 36,
) -> dict[str, Any]:
    """Trim empty canvas, fill the usable frame, and bottom-align without subject cropping."""
    asset = Image.open(asset_path).convert("RGB")
    source_size = [asset.width, asset.height]
    trim_box = _content_bbox(asset)
    trimmed = asset.crop(tuple(trim_box))

    x0, y0, x1, y1 = bounds
    inner = [x0 + safe_inset, y0 + safe_inset, x1 - safe_inset, y1 - safe_inset]
    target_w, target_h = inner[2] - inner[0], inner[3] - inner[1]
    scale = min(target_w / trimmed.width, target_h / trimmed.height)
    rendered_w = max(1, round(trimmed.width * scale))
    rendered_h = max(1, round(trimmed.height * scale))
    resized = trimmed.resize((rendered_w, rendered_h), Image.Resampling.LANCZOS)

    px = inner[0] + (target_w - rendered_w) // 2
    py = inner[3] - rendered_h
    frame_layer = Image.new("RGB", (x1 - x0, y1 - y0), background)
    frame_layer.paste(resized, (px - x0, py - y0))
    rounded = Image.new("L", frame_layer.size, 0)
    ImageDraw.Draw(rounded).rounded_rectangle(
        (0, 0, frame_layer.width - 1, frame_layer.height - 1),
        radius=radius,
        fill=255,
    )
    canvas.paste(frame_layer, (x0, y0), rounded)

    occupancy = (rendered_w * rendered_h) / max(1, target_w * target_h)
    if occupancy < 0.70:
        raise ValueError(
            f"FAIL_ILLUSTRATION_OCCUPANCY: {occupancy:.3f}; expected at least 0.700"
        )
    return {
        "mode": "strict-adaptive-trim-bottom",
        "source_size": source_size,
        "trim_box": trim_box,
        "frame_bounds": bounds,
        "safe_inset": safe_inset,
        "rendered_bounds": [px, py, px + rendered_w, py + rendered_h],
        "vertical_alignment": "bottom",
        "occupancy_ratio": round(occupancy, 6),
        "cropped_subjects": False,
    }


base.paste_safe_illustration = paste_strict_illustration


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--evidence-output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return base.self_test()
    if not args.data or not args.output or not args.evidence_output:
        parser.error("--data, --output and --evidence-output are required")
    base.compose(args.data, args.output, args.evidence_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
