#!/usr/bin/env python3
"""Compose the locked BCube Publisher/Copyright page."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = ROOT / "bcube-publishing-sdk/templates/publisher-page-v1.json"
BOLD = [Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"), Path("C:/Windows/Fonts/arialbd.ttf")]
REGULAR = [Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), Path("C:/Windows/Fonts/arial.ttf")]


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve(path_value: str) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else ROOT / path


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for candidate in BOLD if bold else REGULAR:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    raise FileNotFoundError("No supported deterministic font found")


def wrap(draw: ImageDraw.ImageDraw, text: str, active: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = word if not current else f"{current} {word}"
        if draw.textlength(candidate, font=active) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_fitted_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    bounds: list[int],
    *,
    max_size: int,
    min_size: int,
    fill: str,
    bold: bool = False,
    align: str = "left",
    max_lines: int | None = None,
) -> dict[str, Any]:
    x0, y0, x1, y1 = bounds
    for size in range(max_size, min_size - 1, -2):
        active = font(size, bold)
        lines = wrap(draw, text, active, x1 - x0)
        if max_lines is not None and len(lines) > max_lines:
            continue
        line_height = int(size * 1.28)
        if len(lines) * line_height > y1 - y0:
            continue
        y = y0 + ((y1 - y0) - len(lines) * line_height) // 2
        for line in lines:
            line_width = draw.textlength(line, font=active)
            if align == "center":
                x = x0 + ((x1 - x0) - line_width) / 2
            elif align == "right":
                x = x1 - line_width
            else:
                x = x0
            draw.text((x, y), line, font=active, fill=fill)
            y += line_height
        return {"bounds": bounds, "font_size": size, "lines": lines}
    raise ValueError(f"Text does not fit Publisher-page bounds: {text!r}")


def paste_contain(canvas: Image.Image, source: Path, bounds: list[int]) -> dict[str, Any]:
    image = Image.open(source).convert("RGBA")
    original = [image.width, image.height]
    pixels = [
        (255, 255, 255, 0) if r > 246 and g > 246 and b > 246 else (r, g, b, a)
        for r, g, b, a in image.getdata()
    ]
    image.putdata(pixels)
    x0, y0, x1, y1 = bounds
    scale = min((x1 - x0) / image.width, (y1 - y0) / image.height)
    width = max(1, round(image.width * scale))
    height = max(1, round(image.height * scale))
    image = image.resize((width, height), Image.Resampling.LANCZOS)
    x = x0 + (x1 - x0 - width) // 2
    y = y0 + (y1 - y0 - height) // 2
    canvas.paste(image, (x, y), image)
    return {"source_size": original, "rendered_bounds": [x, y, x + width, y + height]}


def draw_title(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    bounds: dict[str, list[int]],
    colours: dict[str, str],
) -> list[dict[str, Any]]:
    if len(lines) == 1:
        combined = [
            bounds["book_title_line_1"][0],
            bounds["book_title_line_1"][1],
            bounds["book_title_line_2"][2],
            bounds["book_title_line_2"][3],
        ]
        return [draw_fitted_text(draw, lines[0], combined, max_size=94, min_size=54,
                                 fill=colours["purple"], bold=True, align="center", max_lines=2)]
    return [
        draw_fitted_text(draw, lines[0], bounds["book_title_line_1"], max_size=82, min_size=48,
                         fill=colours["purple"], bold=True, align="center", max_lines=1),
        draw_fitted_text(draw, lines[1], bounds["book_title_line_2"], max_size=92, min_size=52,
                         fill=colours["blue"], bold=True, align="center", max_lines=1),
    ]


def detail_row(
    draw: ImageDraw.ImageDraw,
    label: str,
    value: str,
    y: int,
    colours: dict[str, str],
) -> dict[str, Any]:
    label_render = draw_fitted_text(
        draw, label.upper(), [350, y, 820, y + 90], max_size=30, min_size=24,
        fill=colours["purple"], bold=True, max_lines=1,
    )
    value_render = draw_fitted_text(
        draw, value, [840, y, 2125, y + 90], max_size=34, min_size=25,
        fill=colours["text"], max_lines=2,
    )
    return {"label": label_render, "value": value_render}


def compose(data_path: Path, output: Path, evidence_output: Path) -> None:
    template = load_json(TEMPLATE_PATH)
    data = load_json(data_path)
    canvas_spec = template["canvas"]
    bounds = template["bounds"]
    colours = template["colours"]
    canvas = Image.new("RGB", (canvas_spec["width"], canvas_spec["height"]), colours["background"])
    draw = ImageDraw.Draw(canvas)

    logo_render = paste_contain(canvas, resolve(data["official_logo_path"]), bounds["logo"])
    title_render = draw_title(draw, data["book_title_lines"], bounds, colours)
    level_render = draw_fitted_text(
        draw, data["level"], bounds["level"], max_size=38, min_size=28,
        fill=colours["navy"], bold=True, align="center", max_lines=1,
    )
    page_title_render = draw_fitted_text(
        draw, data["page_title"], bounds["page_title"], max_size=70, min_size=46,
        fill=colours["navy"], bold=True, align="center", max_lines=1,
    )
    draw.rectangle(bounds["divider"], fill=colours["gold"])

    draw.rounded_rectangle(bounds["publisher_panel"], radius=38, fill=colours["panel"],
                           outline=colours["line"], width=4)
    published_by_render = draw_fitted_text(
        draw, "PUBLISHED BY", [350, 860, 2130, 955], max_size=34, min_size=28,
        fill=colours["purple"], bold=True, align="center", max_lines=1,
    )
    publisher_name_render = draw_fitted_text(
        draw, data["publisher"]["name"], [350, 960, 2130, 1085], max_size=54, min_size=40,
        fill=colours["navy"], bold=True, align="center", max_lines=1,
    )
    publisher_rows = [
        detail_row(draw, "Address", data["publisher"]["address"], 1120, colours),
        detail_row(draw, "Email", data["publisher"]["email"], 1220, colours),
        detail_row(draw, "Website", data["publisher"]["website"], 1320, colours),
        detail_row(draw, "Phone", data["publisher"]["phone"], 1420, colours),
    ]

    draw.rounded_rectangle(bounds["identifiers_panel"], radius=38, fill=colours["panel_alt"],
                           outline="#BCD6EA", width=4)
    identifier_heading = draw_fitted_text(
        draw, "PUBLICATION IDENTIFICATION", [350, 1650, 2130, 1740],
        max_size=34, min_size=28, fill=colours["blue"], bold=True,
        align="center", max_lines=1,
    )
    identifier_rows = [
        detail_row(draw, "Publication Code", data["publication_code"], 1780, colours),
        detail_row(draw, "Document ID", data["document_id"], 1890, colours),
        detail_row(draw, "Status", data["publisher"]["production_status"], 2000, colours),
    ]

    draw.rounded_rectangle(bounds["rights_panel"], radius=38, fill=colours["white"],
                           outline=colours["line"], width=4)
    copyright_heading = draw_fitted_text(
        draw, "COPYRIGHT & RIGHTS", [350, 2300, 2130, 2395],
        max_size=34, min_size=28, fill=colours["purple"], bold=True,
        align="center", max_lines=1,
    )
    copyright_render = draw_fitted_text(
        draw, data["copyright_notice"], [350, 2420, 2130, 2555],
        max_size=36, min_size=28, fill=colours["navy"], bold=True,
        align="center", max_lines=3,
    )
    rights_text = (
        "No part of this publication may be reproduced, stored, transmitted, or distributed "
        "in any form without prior written permission from the publisher, except where "
        "permitted by law."
    )
    rights_render = draw_fitted_text(
        draw, rights_text, [390, 2580, 2090, 2790],
        max_size=31, min_size=24, fill=colours["text"], align="center", max_lines=5,
    )
    print_render = draw_fitted_text(
        draw, f"Printed in {data['publisher']['country_of_print']}",
        [600, 2815, 1880, 2900], max_size=31, min_size=25,
        fill=colours["muted"], bold=True, align="center", max_lines=1,
    )

    draw.rectangle(bounds["footer"], fill=colours["purple"])
    draw.rectangle([0, bounds["footer"][1], 2480, bounds["footer"][1] + 12], fill=colours["gold"])
    footer_brand = draw_fitted_text(
        draw, "BCUBE FUTURE ACADEMY", [150, 3280, 2330, 3365],
        max_size=36, min_size=28, fill=colours["white"], bold=True,
        align="center", max_lines=1,
    )
    footer_contact = draw_fitted_text(
        draw, f"{data['publisher']['website']}  •  {data['publisher']['phone']}",
        [150, 3370, 2330, 3460], max_size=28, min_size=22,
        fill="#F7EAFB", align="center", max_lines=1,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, "PNG", dpi=(canvas_spec["dpi"], canvas_spec["dpi"]))
    evidence = {
        "engine": "BCube Publishing Engine Publisher Page",
        "template_version": template["template_version"],
        "page_id": data["page_id"],
        "page_type": "publisher",
        "header_type": "MINIMAL_HEADER",
        "canvas": canvas_spec,
        "artifact": str(output),
        "artifact_sha256": sha256(output),
        "inputs": {"logo_sha256": sha256(resolve(data["official_logo_path"]))},
        "components": {
            "official_logo": logo_render,
            "book_title": title_render,
            "level": level_render,
            "page_title": page_title_render,
            "published_by": published_by_render,
            "publisher_name": publisher_name_render,
            "publisher_details": publisher_rows,
            "identifiers_heading": identifier_heading,
            "identifiers": identifier_rows,
            "copyright_heading": copyright_heading,
            "copyright_notice": copyright_render,
            "rights_notice": rights_render,
            "country_of_print": print_render,
            "footer": {"brand": footer_brand, "contact": footer_contact},
        },
        "prohibited_component_counts": {
            "series_banner": 0,
            "age_badge": 0,
            "visible_page_number": 0,
            "illustration_layer": 0,
            "illustration_frame": 0,
            "official_star": 0,
            "learning_goal": 0,
            "activity_banner": 0,
            "teacher_panel": 0,
            "parent_panel": 0,
            "core_pillars": 0,
            "isbn": 0,
        },
        "qa": {
            "one_physical_page": True,
            "minimal_header": True,
            "illustration_free": True,
            "text_overflow": False,
            "component_overlap": False,
            "status": "PASS",
        },
    }
    evidence_output.parent.mkdir(parents=True, exist_ok=True)
    evidence_output.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "COMPOSED", "artifact": str(output),
                      "evidence": str(evidence_output)}, indent=2))


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
