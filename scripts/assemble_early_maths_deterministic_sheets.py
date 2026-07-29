#!/usr/bin/env python3
"""Assemble deterministic individual assets into renderer-compatible page sheets.

The curriculum-first runtime currently consumes one source image per page. This
bridge preserves exact individual assets while arranging them using the same
crop-grid contract as the runtime builder, eliminating AI and crop guessing.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

SHEET = 2048
PAGES = {
    "EM-LKG-V4-P009": ["group_2_kites", "group_4_ducks", "group_6_cupcakes", "group_8_balls"],
    "EM-LKG-V4-P018": ["frog", "rabbit", "bee"],
    "EM-LKG-V4-P021": [
        "shape_circle", "shape_square", "shape_triangle", "shape_rectangle",
        "object_flag", "object_clock", "object_door", "object_window",
    ],
}


def crop_grid(names: list[str]) -> dict[str, dict[str, float]]:
    cols = 1 if len(names) <= 3 else 2 if len(names) <= 8 else 3
    rows = (len(names) + cols - 1) // cols
    gx, gy = 0.08, 0.07
    cw = (1 - gx * (cols + 1)) / cols
    ch = (1 - gy * (rows + 1)) / rows
    result = {}
    for index, name in enumerate(names):
        r, c = divmod(index, cols)
        x = gx + c * (cw + gx); y = gy + r * (ch + gy)
        result[name] = {"x": x, "y": y, "w": cw, "h": ch}
    return result


def paste_contain(sheet: Image.Image, asset: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    max_w, max_h = x1 - x0, y1 - y0
    scale = min(max_w / asset.width, max_h / asset.height)
    size = (max(1, int(asset.width * scale)), max(1, int(asset.height * scale)))
    resized = asset.resize(size, Image.Resampling.LANCZOS)
    px = x0 + (max_w - size[0]) // 2
    py = y0 + (max_h - size[1]) // 2
    sheet.alpha_composite(resized, (px, py))


def assemble(root: Path, page_id: str, names: list[str]) -> Path:
    page_dir = root / page_id
    if not page_dir.is_dir():
        raise FileNotFoundError(page_dir)
    sheet = Image.new("RGBA", (SHEET, SHEET), (255, 255, 255, 255))
    for name, spec in crop_grid(names).items():
        asset_path = page_dir / f"{name}.png"
        if not asset_path.is_file():
            raise FileNotFoundError(asset_path)
        asset = Image.open(asset_path).convert("RGBA")
        x0 = int(spec["x"] * SHEET); y0 = int(spec["y"] * SHEET)
        x1 = int((spec["x"] + spec["w"]) * SHEET); y1 = int((spec["y"] + spec["h"]) * SHEET)
        inset_x = int((x1 - x0) * 0.08); inset_y = int((y1 - y0) * 0.08)
        paste_contain(sheet, asset, (x0 + inset_x, y0 + inset_y, x1 - inset_x, y1 - inset_y))
    output = root / f"{page_id}.png"
    sheet.convert("RGB").save(output, "PNG")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Assemble deterministic proof sheets")
    parser.add_argument("--assets-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.assets_dir.expanduser().resolve()
    outputs = [str(assemble(root, page_id, names)) for page_id, names in PAGES.items()]
    report = root / "deterministic-sheets-report.json"
    report.write_text(json.dumps({"outputs": outputs}, indent=2) + "\n", encoding="utf-8")
    print(f"Assembled {len(outputs)} renderer-compatible sheets")
    print(f"Report: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
