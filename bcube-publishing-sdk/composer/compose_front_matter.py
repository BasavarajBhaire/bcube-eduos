#!/usr/bin/env python3
"""Compose BCube front-matter pages from structured JSON."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
CANVAS = (2480, 3508)
PURPLE = "#643595"
PINK = "#ED2F7C"
BLUE = "#1768B3"
TEXT = "#2E2E2E"
BG = "#FFFDF8"
BOLD = [Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"), Path("C:/Windows/Fonts/arialbd.ttf")]
REGULAR = [Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), Path("C:/Windows/Fonts/arial.ttf")]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for path in (BOLD if bold else REGULAR):
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    raise FileNotFoundError("No deterministic font found")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Front-matter data must be a JSON object")
    return value


def wrap(draw: ImageDraw.ImageDraw, text: str, active: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if draw.textbbox((0, 0), trial, font=active)[2] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_centered(draw: ImageDraw.ImageDraw, text: str, y: int, size: int, fill: str, bold: bool = True) -> int:
    active = font(size, bold)
    box = draw.textbbox((0, 0), text, font=active)
    x = (CANVAS[0] - (box[2] - box[0])) // 2
    draw.text((x, y), text, font=active, fill=fill)
    return y + (box[3] - box[1])


def validate(data: dict[str, Any]) -> None:
    required = {"page_id", "page_type", "book_title", "level", "age", "series", "logo_path"}
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"Missing front-matter data: {missing}")
    if data["page_type"] not in {"about", "publisher", "contents"}:
        raise ValueError(f"Unsupported front-matter page type: {data['page_type']}")
    logo = ROOT / data["logo_path"]
    if not logo.is_file():
        raise FileNotFoundError(f"Missing official logo: {logo}")
    if data["page_type"] == "contents" and not isinstance(data.get("entries"), list):
        raise ValueError("Contents page requires entries")


def compose(data_path: Path, output: Path, evidence_path: Path) -> None:
    data = load(data_path)
    validate(data)
    canvas = Image.new("RGB", CANVAS, BG)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((20, 20, CANVAS[0]-20, CANVAS[1]-20), radius=42, outline=PURPLE, width=8)

    logo = Image.open(ROOT / data["logo_path"]).convert("RGBA")
    logo.thumbnail((360, 280), Image.Resampling.LANCZOS)
    canvas.paste(logo, (100, 80), logo if logo.mode == "RGBA" else None)

    draw.rounded_rectangle((500, 75, 2280, 315), radius=35, fill=PURPLE)
    draw_centered(draw, data["series"], 115, 62, "white")
    draw_centered(draw, f"{data['book_title']} • {data['level']} {data['age']}", 335, 54, BLUE)

    page_type = data["page_type"]
    title = {"about": "About This Book", "publisher": "Publisher Information", "contents": "Contents"}[page_type]
    draw_centered(draw, title, 470, 82, PURPLE)
    draw.line((280, 585, 2200, 585), fill=PINK, width=8)

    if page_type == "about":
        y = 680
        for paragraph in data.get("paragraphs", []):
            active = font(42)
            for line in wrap(draw, paragraph, active, 1850):
                draw.text((315, y), line, font=active, fill=TEXT)
                y += 58
            y += 30
        pillars = data.get("pillars", [])
        if pillars:
            draw_centered(draw, "BCube Core Pillars", y + 20, 54, PURPLE)
            y += 120
            for index, pillar in enumerate(pillars):
                x = 250 + (index % 3) * 730
                py = y + (index // 3) * 180
                draw.rounded_rectangle((x, py, x+610, py+120), radius=40, fill=["#F57C00", "#25A43A", "#2E98CE", "#8E3DB3", "#ED2F7C"][index % 5])
                draw.text((x+40, py+34), pillar, font=font(36, True), fill="white")
    elif page_type == "publisher":
        y = 710
        rows = data.get("publisher_rows", [])
        for label, value in rows:
            draw.rounded_rectangle((280, y, 2200, y+145), radius=26, fill="#F3EAF9")
            draw.text((330, y+45), label, font=font(34, True), fill=PURPLE)
            draw.text((870, y+45), value, font=font(34), fill=TEXT)
            y += 175
    else:
        y = 670
        entries = data["entries"]
        midpoint = (len(entries) + 1) // 2
        columns = [entries[:midpoint], entries[midpoint:]]
        for col, items in enumerate(columns):
            x = 250 + col * 1110
            cy = y
            for item in items:
                module = item.get("module", "")
                title_text = item["title"]
                page = str(item["page"])
                if module:
                    draw.text((x, cy), module, font=font(31, True), fill=PINK)
                    cy += 48
                draw.text((x, cy), title_text, font=font(31), fill=TEXT)
                page_box = draw.textbbox((0, 0), page, font=font(31, True))
                draw.text((x+900-(page_box[2]-page_box[0]), cy), page, font=font(31, True), fill=BLUE)
                cy += 72

    draw.text((170, 3370), "BCube Future Academy", font=font(28, True), fill=PURPLE)
    draw.text((2140, 3370), data["page_id"], font=font(24), fill="#777777")
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, "PNG", dpi=(300, 300))
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    evidence = {"engine":"BCube Publishing Engine V6","page_id":data["page_id"],"page_type":page_type,"canvas":{"width":2480,"height":3508,"dpi":300},"artifact_sha256":digest,"status":"COMPOSED"}
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(evidence, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"status":"COMPOSED","artifact":str(output),"evidence":str(evidence_path),"sha256":digest}))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    args = parser.parse_args()
    compose(args.data, args.output, args.evidence_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
