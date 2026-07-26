#!/usr/bin/env python3
"""Render learning pages directly from self-contained book runtime contracts."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

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


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def panel(draw, box, *, fill="#FFFFFF", outline="#8E5AC7", width=4, radius=24):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def paste_fit(canvas: Image.Image, image: Image.Image, box, inset=12):
    x0, y0, x1, y1 = box
    x0 += inset; y0 += inset; x1 -= inset; y1 -= inset
    image = image.convert("RGBA")
    scale = min((x1-x0)/image.width, (y1-y0)/image.height)
    image = image.resize((max(1, round(image.width*scale)), max(1, round(image.height*scale))), Image.Resampling.LANCZOS)
    x = x0 + (x1-x0-image.width)//2
    y = y0 + (y1-y0-image.height)//2
    canvas.paste(image, (x, y), image)


def crop_assets(source: Image.Image, crop_map: dict):
    out = {}
    w, h = source.size
    for name, (x0, y0, x1, y1) in crop_map.items():
        out[name] = source.crop((round(x0*w), round(y0*h), round(x1*w), round(y1*h))).convert("RGBA")
    return out


def header(canvas, draw, page, book_title, logo, base, template):
    colours = template["colours"]
    typography = template["typography"]
    logo = logo.convert("RGBA")
    logo.thumbnail((300, 220), Image.Resampling.LANCZOS)
    canvas.paste(logo, (110 + (300-logo.width)//2, 35 + (220-logo.height)//2), logo)
    base.brand_title(draw, [book_title], [470, 45, 2320, 145], colours, typography)
    base.fitted_text(draw, page["identity"]["title"], [470, 145, 2320, 285], max_size=typography["page_title_max"], min_size=typography["page_title_min"], colour=colours["navy"], bold=True, max_lines=2)
    panel(draw, [150, 305, 2330, 435], fill=colours["blue"], outline="#1768B3", width=3)
    base.fitted_text(draw, "Learning goal: " + page["learning"]["objective"], [185, 315, 2295, 425], max_size=44, min_size=32, colour=colours["navy"], bold=True, max_lines=2)
    panel(draw, [150, 460, 2330, 610], fill=colours["gold"], outline="#E1B12C", width=3)
    base.fitted_text(draw, page["learning"]["instruction"], [185, 472, 2295, 598], max_size=50, min_size=34, colour=colours["line"], bold=True, max_lines=2)


def teacher(draw, page, base, template):
    colours = template["colours"]
    box = [150, 3070, 2300, 3260]
    panel(draw, box, fill="#F0FAED", outline="#5F9D50", width=3)
    base.fitted_text(draw, "TEACHER CUE", [180, 3090, 530, 3235], max_size=34, min_size=27, colour=colours["navy"], bold=True, max_lines=1)
    base.fitted_text(draw, page["guidance"]["teacher_cue"], [560, 3085, 2260, 3240], max_size=35, min_size=26, colour=colours["line"], align="left", max_lines=3)


def render_count(canvas, draw, page, assets, base, template):
    colours = template["colours"]
    groups = page["mechanics"]["groups"]
    cell_w, cell_h = 690, 690
    start_x, start_y = 170, 690
    for index, group in enumerate(groups):
        row, col = divmod(index, 3)
        x0 = start_x + col * 730
        y0 = start_y + row * 1110
        box = [x0, y0, x0 + cell_w, y0 + cell_h]
        panel(draw, box, fill="#FFFFFF", outline=colours["soft_purple"], width=3)
        paste_fit(canvas, assets[group["asset"]], [x0+20, y0+20, x0+cell_w-20, y0+cell_h-145])
        choices = group["choices"]
        cy = y0 + cell_h - 75
        spacing = 150
        first = x0 + cell_w//2 - spacing
        for i, value in enumerate(choices):
            cx = first + i*spacing
            draw.ellipse([cx-42, cy-42, cx+42, cy+42], fill="#FFFFFF", outline=colours["purple"], width=4)
            base.fitted_text(draw, str(value), [cx-35, cy-35, cx+35, cy+35], max_size=38, min_size=28, colour=colours["navy"], bold=True, max_lines=1)


def render_sentence(canvas, draw, page, assets, base, template):
    colours = template["colours"]
    pairs = page["mechanics"]["pairs"]
    start_y = 680
    panel_h = 1030
    for index, pair in enumerate(pairs):
        y0 = start_y + index * 1100
        panel(draw, [180, y0, 2300, y0 + panel_h], fill="#FFFFFF", outline=colours["soft_purple"], width=3)
        paste_fit(canvas, assets[pair["asset"]], [210, y0+20, 1180, y0+panel_h-20])
        base.fitted_text(draw, pair["question"], [1240, y0+120, 2240, y0+300], max_size=46, min_size=34, colour=colours["navy"], bold=True, align="left", max_lines=2)
        answer = pair.get("model_answer") or pair.get("sentence_starter") or ""
        panel(draw, [1220, y0+380, 2250, y0+680], fill="#FFF7D6", outline="#E1B12C", width=3)
        base.fitted_text(draw, answer, [1280, y0+420, 2190, y0+640], max_size=48, min_size=34, colour=colours["line"], bold=True, align="left", max_lines=3)
        cue = "Say the complete sentence." if pair.get("model_answer") else "Complete the sentence aloud."
        base.fitted_text(draw, cue, [1260, y0+740, 2210, y0+870], max_size=34, min_size=26, colour=colours["muted"], align="left", max_lines=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", required=True)
    parser.add_argument("--book", required=True)
    parser.add_argument("--page-id", required=True)
    parser.add_argument("--illustration", type=Path, required=True)
    parser.add_argument("--logo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    args = parser.parse_args()

    loader = load_module("runtime_loader", LOADER)
    base = load_module("runtime_base", BASE)
    page = loader.load_page_contract(level=args.level, book_slug=args.book, page_id=args.page_id)
    manifest = load_json(ROOT / "runtime-contracts/manifest.json")
    relative = manifest["levels"][args.level.lower()]["books"][args.book]
    book = load_json(ROOT / "runtime-contracts" / relative)
    template = load_json(TEMPLATE)
    spec = template["canvas"]
    canvas = Image.new("RGB", (spec["width"], spec["height"]), template["colours"]["background"])
    draw = ImageDraw.Draw(canvas)
    header(canvas, draw, page, book["book"]["title"], Image.open(args.logo), base, template)
    source = Image.open(args.illustration).convert("RGBA")
    assets = crop_assets(source, page["illustration"]["asset_crops"])
    mechanic = page["activity"]["mechanic"]
    if mechanic == "count-and-circle-number":
        render_count(canvas, draw, page, assets, base, template)
    elif mechanic == "question-answer-sentence-pairs":
        render_sentence(canvas, draw, page, assets, base, template)
    else:
        raise loader.PageContractRequired(f"No renderer registered for mechanic {mechanic!r}")
    teacher(draw, page, base, template)
    base.fitted_text(draw, str(page["identity"]["printed_page"]), [2200, 3270, 2370, 3390], max_size=46, min_size=36, colour=template["colours"]["muted"], bold=True, max_lines=1)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.output, "PNG", dpi=(spec["dpi"], spec["dpi"]))
    evidence = {
        "engine": "BCube Runtime Contract Renderer V1",
        "page_id": args.page_id,
        "mechanic": mechanic,
        "book_contract": relative,
        "artifact": str(args.output),
        "artifact_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "qa": {
            "runtime_contract_used": True,
            "fallback_used": False,
            "home_connection_rendered": False,
            "generic_response_panel_rendered": False,
            "status": "REVIEW_CANDIDATE"
        }
    }
    args.evidence_output.parent.mkdir(parents=True, exist_ok=True)
    args.evidence_output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
