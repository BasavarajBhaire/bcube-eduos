#!/usr/bin/env python3
"""Strict adaptive Nursery cover compositor.

Delegates deterministic publishing geometry to the approved base compositor while
replacing only illustration placement with content-aware trimming, adaptive
scale-up, bottom alignment, and evidence-rich QA.
"""
from __future__ import annotations

import argparse
import importlib.util
import math
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

MIN_OCCUPANCY = 0.70
MAX_SAFE_OVERFLOW = 0.06
OCCUPANCY_EPSILON = 1e-9


def _content_bbox(asset: Image.Image, *, threshold: int = 246, colour_delta: int = 8) -> list[int]:
    """Return a conservative box around visible, non-near-white content."""
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


def _adaptive_dimensions(
    source_w: int,
    source_h: int,
    target_w: int,
    target_h: int,
    min_occupancy: float,
) -> tuple[int, int, float, float]:
    """Return integer dimensions that deterministically meet the occupancy target."""
    contain_scale = min(target_w / source_w, target_h / source_h)
    rendered_w = max(1, round(source_w * contain_scale))
    rendered_h = max(1, round(source_h * contain_scale))
    frame_area = max(1, target_w * target_h)
    initial_occupancy = (rendered_w * rendered_h) / frame_area

    if initial_occupancy + OCCUPANCY_EPSILON >= min_occupancy:
        return rendered_w, rendered_h, contain_scale, initial_occupancy

    scale_factor = math.sqrt(min_occupancy / max(initial_occupancy, OCCUPANCY_EPSILON))
    adaptive_scale = contain_scale * scale_factor

    # Ceil rather than round so integer rasterisation cannot land microscopically
    # below the requested occupancy while displaying the same rounded percentage.
    candidate_w = max(1, math.ceil(source_w * adaptive_scale))
    candidate_h = max(1, math.ceil(source_h * adaptive_scale))

    max_w = round(target_w * (1 + MAX_SAFE_OVERFLOW))
    max_h = round(target_h * (1 + MAX_SAFE_OVERFLOW))

    # Guard against any residual integer-boundary deficit by increasing the
    # smaller proportional dimension one pixel at a time within the safe limit.
    while (candidate_w * candidate_h) / frame_area + OCCUPANCY_EPSILON < min_occupancy:
        width_ratio = candidate_w / max(1, target_w)
        height_ratio = candidate_h / max(1, target_h)
        if width_ratio <= height_ratio and candidate_w < max_w:
            candidate_w += 1
        elif candidate_h < max_h:
            candidate_h += 1
        elif candidate_w < max_w:
            candidate_w += 1
        else:
            break

    if candidate_w > max_w or candidate_h > max_h:
        raise ValueError(
            "FAIL_ILLUSTRATION_SAFE_FIT: occupancy target requires more than "
            f"{MAX_SAFE_OVERFLOW:.0%} bounded overflow"
        )

    final_occupancy = (candidate_w * candidate_h) / frame_area
    if final_occupancy + OCCUPANCY_EPSILON < min_occupancy:
        raise ValueError(
            f"FAIL_ILLUSTRATION_OCCUPANCY: {final_occupancy:.9f}; "
            f"expected at least {min_occupancy:.9f}"
        )

    applied_scale = max(candidate_w / source_w, candidate_h / source_h)
    return candidate_w, candidate_h, applied_scale, final_occupancy


def paste_strict_illustration(
    canvas: Image.Image,
    asset_path: Path,
    bounds: list[int],
    background: str,
    safe_inset: int = 20,
    radius: int = 36,
) -> dict[str, Any]:
    """Trim empty canvas, adaptively scale, and bottom-align with bounded safe overflow."""
    asset = Image.open(asset_path).convert("RGB")
    source_size = [asset.width, asset.height]
    trim_box = _content_bbox(asset)
    trimmed = asset.crop(tuple(trim_box))

    x0, y0, x1, y1 = bounds
    inner = [x0 + safe_inset, y0 + safe_inset, x1 - safe_inset, y1 - safe_inset]
    target_w, target_h = inner[2] - inner[0], inner[3] - inner[1]

    rendered_w, rendered_h, applied_scale, occupancy = _adaptive_dimensions(
        trimmed.width,
        trimmed.height,
        target_w,
        target_h,
        MIN_OCCUPANCY,
    )
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

    overflow = {
        "left": max(0, inner[0] - px),
        "top": max(0, inner[1] - py),
        "right": max(0, px + rendered_w - inner[2]),
        "bottom": max(0, py + rendered_h - inner[3]),
    }
    return {
        "mode": "v5.1-adaptive-trim-scale-bottom",
        "layout_version": "5.1.1",
        "source_size": source_size,
        "trim_box": trim_box,
        "trimmed_size": [trimmed.width, trimmed.height],
        "frame_bounds": bounds,
        "safe_inset": safe_inset,
        "target_size": [target_w, target_h],
        "rendered_bounds": [px, py, px + rendered_w, py + rendered_h],
        "vertical_alignment": "bottom",
        "adaptive_scale_factor": round(applied_scale, 9),
        "occupancy_ratio": round(occupancy, 9),
        "occupancy_target": MIN_OCCUPANCY,
        "occupancy_epsilon": OCCUPANCY_EPSILON,
        "bounded_overflow": overflow,
        "subject_clipped": False,
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
