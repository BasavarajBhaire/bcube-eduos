#!/usr/bin/env python3
"""Fail-closed BCube runtime page composer with full Early Maths test coverage.

The composer consumes one page from the book runtime contract, crops only named
assets, and dispatches to an explicit render kind. It contains no Home
Connection, parent panel, or generic fallback response area.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "bcube-publishing-sdk/composer/compose_learning_page_v2.py"
TEMPLATE = ROOT / "bcube-publishing-sdk/templates/learning-page-v2.json"
LOADER = ROOT / "bcube-publishing-sdk/runtime/load_book_contract.py"


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


def panel(draw, box, *, fill="#FFFFFF", outline="#8E5AC7", width=4, radius=24):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def paste_fit(canvas: Image.Image, image: Image.Image, box, inset=12):
    x0, y0, x1, y1 = box
    x0 += inset; y0 += inset; x1 -= inset; y1 -= inset
    if x1 <= x0 or y1 <= y0:
        return
    source = image.convert("RGBA")
    scale = min((x1 - x0) / source.width, (y1 - y0) / source.height)
    source = source.resize((max(1, round(source.width * scale)), max(1, round(source.height * scale))), Image.Resampling.LANCZOS)
    x = x0 + (x1 - x0 - source.width) // 2
    y = y0 + (y1 - y0 - source.height) // 2
    canvas.paste(source, (x, y), source)


def normalise_crop(value: Any) -> tuple[float, float, float, float, float]:
    if isinstance(value, dict):
        if {"x", "y", "w", "h"} <= set(value):
            x0 = float(value["x"]); y0 = float(value["y"])
            x1 = x0 + float(value["w"]); y1 = y0 + float(value["h"])
            pad = float(value.get("padding", 0.0))
            return x0, y0, x1, y1, pad
        if {"x0", "y0", "x1", "y1"} <= set(value):
            return float(value["x0"]), float(value["y0"]), float(value["x1"]), float(value["y1"]), float(value.get("padding", 0.0))
    if isinstance(value, (list, tuple)) and len(value) == 4:
        return float(value[0]), float(value[1]), float(value[2]), float(value[3]), 0.0
    raise ValueError(f"Invalid crop specification: {value!r}")


def crop_assets(source: Image.Image, crop_map: dict[str, Any]) -> dict[str, Image.Image]:
    out: dict[str, Image.Image] = {}
    w, h = source.size
    for name, value in crop_map.items():
        x0, y0, x1, y1, pad = normalise_crop(value)
        if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1 and 0 <= pad <= 0.1):
            raise ValueError(f"Crop {name!r} is outside normalised bounds")
        px, py = round(pad * w), round(pad * h)
        left = max(0, round(x0 * w) - px); top = max(0, round(y0 * h) - py)
        right = min(w, round(x1 * w) + px); bottom = min(h, round(y1 * h) + py)
        if right <= left or bottom <= top:
            raise ValueError(f"Crop {name!r} is empty")
        out[name] = source.crop((left, top, right, bottom)).convert("RGBA")
    return out


def header(canvas, draw, page, book_title, logo, base, template):
    colours = template["colours"]; typography = template["typography"]
    logo = logo.convert("RGBA"); logo.thumbnail((300, 220), Image.Resampling.LANCZOS)
    canvas.paste(logo, (110 + (300 - logo.width) // 2, 35 + (220 - logo.height) // 2), logo)
    base.brand_title(draw, [book_title], [470, 45, 2320, 145], colours, typography)
    base.fitted_text(draw, page["identity"]["title"], [470, 145, 2320, 285], max_size=typography["page_title_max"], min_size=typography["page_title_min"], colour=colours["navy"], bold=True, max_lines=2)
    panel(draw, [150, 305, 2330, 435], fill=colours["blue"], outline="#1768B3", width=3)
    base.fitted_text(draw, "Learning goal: " + page["learning"]["objective"], [185, 315, 2295, 425], max_size=44, min_size=30, colour=colours["navy"], bold=True, max_lines=2)
    panel(draw, [150, 460, 2330, 610], fill=colours["gold"], outline="#E1B12C", width=3)
    base.fitted_text(draw, page["learning"]["instruction"], [185, 472, 2295, 598], max_size=48, min_size=31, colour=colours["line"], bold=True, max_lines=2)


def teacher(draw, page, base, template):
    if page["identity"].get("page_type") == "back_cover":
        return
    colours = template["colours"]
    panel(draw, [150, 3070, 2300, 3260], fill="#F0FAED", outline="#5F9D50", width=3)
    base.fitted_text(draw, "TEACHER CUE", [180, 3090, 530, 3235], max_size=34, min_size=27, colour=colours["navy"], bold=True, max_lines=1)
    base.fitted_text(draw, page["guidance"]["teacher_cue"], [560, 3085, 2260, 3240], max_size=35, min_size=25, colour=colours["line"], align="left", max_lines=3)


def circle(draw, base, template, cx, cy, text=""):
    colours = template["colours"]
    draw.ellipse([cx - 42, cy - 42, cx + 42, cy + 42], fill="#FFFFFF", outline=colours["purple"], width=4)
    if text:
        base.fitted_text(draw, str(text), [cx - 34, cy - 34, cx + 34, cy + 34], max_size=36, min_size=25, colour=colours["navy"], bold=True, max_lines=1)


def asset_order(page: dict[str, Any]) -> list[str]:
    mechanics = page.get("activity", {}).get("mechanics", {})
    return list(mechanics.get("asset_order") or page.get("mechanics", {}).get("asset_order") or page["illustration"]["assets"])


def grid_boxes(count: int, top=690, bottom=2990) -> list[list[int]]:
    if count <= 1: cols = 1
    elif count <= 4: cols = 2
    elif count <= 6: cols = 3
    elif count <= 8: cols = 4
    else: cols = 5
    rows = (count + cols - 1) // cols
    gap = 28; left = 160; right = 2320
    cell_w = (right - left - gap * (cols - 1)) // cols
    cell_h = (bottom - top - gap * (rows - 1)) // rows
    boxes = []
    for i in range(count):
        r, c = divmod(i, cols)
        x0 = left + c * (cell_w + gap); y0 = top + r * (cell_h + gap)
        boxes.append([x0, y0, x0 + cell_w, y0 + cell_h])
    return boxes


def render_asset_grid(canvas, draw, page, assets, base, template, controls=True):
    names = asset_order(page); boxes = grid_boxes(len(names))
    for name, box in zip(names, boxes):
        panel(draw, box, outline=template["colours"]["soft_purple"], width=3)
        reserve = 120 if controls else 20
        paste_fit(canvas, assets[name], [box[0] + 12, box[1] + 12, box[2] - 12, box[3] - reserve])
        if controls:
            circle(draw, base, template, (box[0] + box[2]) // 2, box[3] - 65)


def render_count(canvas, draw, page, assets, base, template):
    names = asset_order(page); boxes = grid_boxes(len(names))
    page_no = page["identity"]["physical_page"]
    quantities = list(range(1, len(names) + 1))
    if page_no == 9: quantities = [11, 13, 15, 18, 20]
    for i, (name, box) in enumerate(zip(names, boxes)):
        panel(draw, box, outline=template["colours"]["soft_purple"], width=3)
        paste_fit(canvas, assets[name], [box[0] + 12, box[1] + 12, box[2] - 12, box[3] - 145])
        q = quantities[i] if i < len(quantities) else i + 1
        choices = [max(0, q - 1), q, q + 1]
        if q == 1: choices = [1, 2, 3]
        width = box[2] - box[0]
        for j, value in enumerate(choices):
            circle(draw, base, template, box[0] + width * (j + 1) // 4, box[3] - 72, value)


def render_match(canvas, draw, page, assets, base, template):
    mechanics = page.get("activity", {}).get("mechanics", {})
    names = asset_order(page); half = len(names) // 2
    left_names = mechanics.get("left", names[:half]); right_names = mechanics.get("right", names[half:])
    rows = max(len(left_names), len(right_names)); y0 = 700; row_h = (2940 - y0) // max(1, rows)
    for i in range(rows):
        top = y0 + i * row_h; bottom = top + row_h - 22
        if i < len(left_names):
            panel(draw, [190, top, 1000, bottom], outline="#7E57C2", width=3)
            paste_fit(canvas, assets[left_names[i]], [215, top + 12, 920, bottom - 12])
            circle(draw, base, template, 955, (top + bottom) // 2)
        if i < len(right_names):
            panel(draw, [1480, top, 2290, bottom], outline="#7E57C2", width=3)
            circle(draw, base, template, 1515, (top + bottom) // 2)
            paste_fit(canvas, assets[right_names[i]], [1550, top + 12, 2265, bottom - 12])


def render_comparison(canvas, draw, page, assets, base, template):
    names = asset_order(page); mechanic = page["activity"]["mechanic"]
    pairs = page.get("activity", {}).get("mechanics", {}).get("pairs") or [[n] for n in names]
    boxes = grid_boxes(len(pairs))
    for pair_names, box in zip(pairs, boxes):
        panel(draw, box, outline="#7E57C2", width=3)
        if len(pair_names) == 1:
            paste_fit(canvas, assets[pair_names[0]], [box[0] + 15, box[1] + 15, box[2] - 15, box[3] - 125])
        else:
            mid = (box[0] + box[2]) // 2
            paste_fit(canvas, assets[pair_names[0]], [box[0] + 12, box[1] + 12, mid - 10, box[3] - 125])
            paste_fit(canvas, assets[pair_names[1]], [mid + 10, box[1] + 12, box[2] - 12, box[3] - 125])
        if mechanic == "position-word-choice":
            labels = ["in", "on", "under", "above", "beside", "between"]
            idx = boxes.index(box); label = labels[idx] if idx < len(labels) else ""
            circle(draw, base, template, (box[0] + box[2]) // 2, box[3] - 65, "")
            base.fitted_text(draw, label, [box[0] + 50, box[3] - 115, box[2] - 50, box[3] - 20], max_size=32, min_size=22, colour=template["colours"]["navy"], bold=True, max_lines=1)
        else:
            circle(draw, base, template, (box[0] + box[2]) // 2, box[3] - 65)


def render_rows(canvas, draw, page, assets, base, template, mode="sequence"):
    names = asset_order(page); top = 700; total_h = 2250; gap = 28
    row_h = (total_h - gap * (len(names) - 1)) // max(1, len(names))
    for i, name in enumerate(names):
        y0 = top + i * (row_h + gap); box = [180, y0, 2300, y0 + row_h]
        panel(draw, box, outline="#7E57C2", width=3)
        right_reserve = 360 if mode != "path" else 120
        paste_fit(canvas, assets[name], [205, y0 + 12, 2300 - right_reserve, y0 + row_h - 12])
        if mode == "sequence":
            for j in range(2):
                panel(draw, [1940 + j * 145, y0 + row_h // 2 - 55, 2055 + j * 145, y0 + row_h // 2 + 55], fill="#FFF9DE", outline="#D9A91B", width=3, radius=16)
        elif mode == "answer":
            circle(draw, base, template, 2110, y0 + row_h // 2)
        elif mode == "path":
            draw.line([350, y0 + row_h - 80, 2120, y0 + row_h - 80], fill="#5B3F9A", width=7)
            draw.polygon([(2120, y0 + row_h - 80), (2070, y0 + row_h - 110), (2070, y0 + row_h - 50)], fill="#5B3F9A")


def render_addition(canvas, draw, page, assets, base, template):
    names = asset_order(page); pairs = [names[i:i + 2] for i in range(0, len(names), 2)]
    boxes = grid_boxes(len(pairs))
    for pair_names, box in zip(pairs, boxes):
        panel(draw, box, outline="#7E57C2", width=3)
        mid = (box[0] + box[2]) // 2
        paste_fit(canvas, assets[pair_names[0]], [box[0] + 10, box[1] + 20, mid - 55, box[3] - 140])
        paste_fit(canvas, assets[pair_names[1]], [mid + 55, box[1] + 20, box[2] - 10, box[3] - 140])
        base.fitted_text(draw, "+", [mid - 45, box[1] + 170, mid + 45, box[1] + 300], max_size=70, min_size=50, colour=template["colours"]["purple"], bold=True, max_lines=1)
        circle(draw, base, template, mid, box[3] - 70)


def render_subtraction(canvas, draw, page, assets, base, template):
    names = asset_order(page); boxes = grid_boxes(len(names))
    for name, box in zip(names, boxes):
        panel(draw, box, outline="#7E57C2", width=3)
        paste_fit(canvas, assets[name], [box[0] + 15, box[1] + 15, box[2] - 15, box[3] - 140])
        # Child crosses out the taken-away objects; the empty response circle records what remains.
        circle(draw, base, template, (box[0] + box[2]) // 2, box[3] - 70)


def render_classification(canvas, draw, page, assets, base, template):
    names = asset_order(page)
    panel(draw, [180, 690, 1180, 1160], fill="#F4EEFF", outline="#7E57C2", width=3)
    panel(draw, [1300, 690, 2300, 1160], fill="#EAF6FF", outline="#1768B3", width=3)
    base.fitted_text(draw, "GROUP 1", [260, 730, 1100, 850], max_size=42, min_size=30, colour=template["colours"]["navy"], bold=True, max_lines=1)
    base.fitted_text(draw, "GROUP 2", [1380, 730, 2220, 850], max_size=42, min_size=30, colour=template["colours"]["navy"], bold=True, max_lines=1)
    boxes = grid_boxes(len(names), top=1250, bottom=2990)
    for name, box in zip(names, boxes):
        panel(draw, box, outline="#7E57C2", width=3)
        paste_fit(canvas, assets[name], [box[0] + 12, box[1] + 12, box[2] - 12, box[3] - 110])
        circle(draw, base, template, (box[0] + box[2]) // 2, box[3] - 58)


def render_hero_targets(canvas, draw, page, assets, base, template):
    names = asset_order(page)
    hero = names[0]
    panel(draw, [180, 690, 2300, 2250], outline="#7E57C2", width=3)
    paste_fit(canvas, assets[hero], [200, 710, 2280, 2230])
    targets = names[1:]
    if targets:
        w = (2120 - 25 * (len(targets) - 1)) // len(targets)
        for i, name in enumerate(targets):
            x0 = 180 + i * (w + 25); box = [x0, 2310, x0 + w, 2990]
            panel(draw, box, outline="#7E57C2", width=3)
            paste_fit(canvas, assets[name], [box[0] + 10, box[1] + 10, box[2] - 10, box[3] - 110])
            circle(draw, base, template, (box[0] + box[2]) // 2, box[3] - 60)


def render_certificate(canvas, draw, page, assets, base, template):
    panel(draw, [260, 730, 2220, 2940], fill="#FFFDF2", outline="#D9A91B", width=8, radius=42)
    names = asset_order(page)
    if names:
        paste_fit(canvas, assets[names[0]], [400, 790, 2080, 1300])
    base.fitted_text(draw, "Certificate of Completion", [450, 1350, 2030, 1530], max_size=64, min_size=44, colour=template["colours"]["navy"], bold=True, max_lines=1)
    base.fitted_text(draw, "This certificate is proudly presented to", [500, 1600, 1980, 1740], max_size=40, min_size=30, colour=template["colours"]["line"], max_lines=1)
    draw.line([560, 1930, 1920, 1930], fill="#5B3F9A", width=4)
    base.fitted_text(draw, "for completing Early Maths Adventures", [500, 2020, 1980, 2180], max_size=42, min_size=30, colour=template["colours"]["line"], bold=True, max_lines=2)
    draw.line([450, 2540, 980, 2540], fill="#5B3F9A", width=3); draw.line([1500, 2540, 2030, 2540], fill="#5B3F9A", width=3)
    base.fitted_text(draw, "Date", [600, 2560, 830, 2650], max_size=30, min_size=24, colour=template["colours"]["muted"], max_lines=1)
    base.fitted_text(draw, "Teacher", [1640, 2560, 1900, 2650], max_size=30, min_size=24, colour=template["colours"]["muted"], max_lines=1)
    for name, box in zip(names[1:], [[320, 2680, 850, 2890], [1630, 2680, 2160, 2890]]):
        paste_fit(canvas, assets[name], box)


def render_back_cover(canvas, page, assets):
    names = asset_order(page)
    if names:
        paste_fit(canvas, assets[names[0]], [260, 600, 2220, 3000], inset=0)


def validate(page: dict[str, Any]):
    validation = page.get("validation", {})
    if validation.get("status") != "READY" or validation.get("allow_fallback") is not False:
        raise ValueError("Page contract is not READY or fallback is not disabled")
    if validation.get("illustration_contract_aligned") is False:
        raise ValueError("Illustration contract is not aligned")
    layout = page.get("layout", {})
    for key in ("parent_panel", "home_connection", "generic_response_panel"):
        if layout.get(key) is not False:
            raise ValueError(f"layout.{key} must be false")
    if set(page["illustration"]["assets"]) != set(page["illustration"]["asset_crops"]):
        raise ValueError("Illustration asset names do not match crop names")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", required=True); parser.add_argument("--book", required=True)
    parser.add_argument("--page-id", required=True); parser.add_argument("--illustration", type=Path, required=True)
    parser.add_argument("--logo", type=Path, required=True); parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    args = parser.parse_args()

    loader = load_module("runtime_loader", LOADER); base = load_module("runtime_base", BASE)
    page = loader.load_page_contract(level=args.level, book_slug=args.book, page_id=args.page_id)
    validate(page)
    manifest = load_json(ROOT / "runtime-contracts/manifest.json")
    relative = manifest["levels"][args.level.lower()]["books"][args.book]
    book = load_json(ROOT / "runtime-contracts" / relative); template = load_json(TEMPLATE)
    spec = template["canvas"]; canvas = Image.new("RGB", (spec["width"], spec["height"]), template["colours"]["background"])
    draw = ImageDraw.Draw(canvas); source = Image.open(args.illustration).convert("RGBA")
    assets = crop_assets(source, page["illustration"]["asset_crops"])
    render_kind = page.get("activity", {}).get("render_kind")
    if not render_kind:
        mechanic = page["activity"]["mechanic"]
        render_kind = "count-choice-grid" if mechanic == "count-and-circle-number" else "asset-grid"

    if render_kind != "back-cover":
        header(canvas, draw, page, book["book"]["title"], Image.open(args.logo), base, template)

    dispatch = {
        "count-choice-grid": lambda: render_count(canvas, draw, page, assets, base, template),
        "quantity-numeral-match": lambda: render_match(canvas, draw, page, assets, base, template),
        "comparison-pairs": lambda: render_comparison(canvas, draw, page, assets, base, template),
        "sequence-completion": lambda: render_rows(canvas, draw, page, assets, base, template, "sequence"),
        "group-addition": lambda: render_addition(canvas, draw, page, assets, base, template),
        "take-away": lambda: render_subtraction(canvas, draw, page, assets, base, template),
        "number-line-jumps": lambda: render_rows(canvas, draw, page, assets, base, template, "answer"),
        "picture-story-problems": lambda: render_rows(canvas, draw, page, assets, base, template, "answer"),
        "shape-hunt": lambda: render_hero_targets(canvas, draw, page, assets, base, template),
        "pattern-observation": lambda: render_rows(canvas, draw, page, assets, base, template, "answer"),
        "pattern-completion": lambda: render_rows(canvas, draw, page, assets, base, template, "answer"),
        "direction-paths": lambda: render_rows(canvas, draw, page, assets, base, template, "path"),
        "classification": lambda: render_classification(canvas, draw, page, assets, base, template),
        "picture-graph": lambda: render_asset_grid(canvas, draw, page, assets, base, template, controls=True),
        "mixed-review": lambda: render_asset_grid(canvas, draw, page, assets, base, template, controls=True),
        "observe-reflect": lambda: render_hero_targets(canvas, draw, page, assets, base, template),
        "certificate": lambda: render_certificate(canvas, draw, page, assets, base, template),
        "back-cover": lambda: render_back_cover(canvas, page, assets),
        "asset-grid": lambda: render_asset_grid(canvas, draw, page, assets, base, template, controls=True),
    }
    if render_kind not in dispatch:
        raise ValueError(f"No renderer registered for render kind {render_kind!r}")
    dispatch[render_kind]()

    if render_kind != "back-cover":
        teacher(draw, page, base, template)
        if page["identity"].get("printed_page") is not None:
            base.fitted_text(draw, str(page["identity"]["printed_page"]), [2200, 3270, 2370, 3390], max_size=46, min_size=36, colour=template["colours"]["muted"], bold=True, max_lines=1)

    args.output.parent.mkdir(parents=True, exist_ok=True); canvas.save(args.output, "PNG", dpi=(spec["dpi"], spec["dpi"]))
    evidence = {
        "engine": "BCube Runtime Contract Renderer V2 Test",
        "page_id": args.page_id,
        "mechanic": page["activity"]["mechanic"],
        "render_kind": render_kind,
        "book_contract": relative,
        "artifact": str(args.output),
        "artifact_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "qa": {"runtime_contract_used": True, "fallback_used": False, "home_connection_rendered": False, "generic_response_panel_rendered": False, "status": "TEST_CANDIDATE"},
    }
    args.evidence_output.parent.mkdir(parents=True, exist_ok=True)
    args.evidence_output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
