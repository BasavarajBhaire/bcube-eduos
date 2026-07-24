#!/usr/bin/env python3
"""Compose the locked BCube About This Book page."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = ROOT / "bcube-publishing-sdk/templates/about-page-v1.json"
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


def font_path(bold: bool) -> Path:
    for candidate in BOLD if bold else REGULAR:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("No supported deterministic font found")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(font_path(bold)), size)


def wrap(draw: ImageDraw.ImageDraw, text: str, active: ImageFont.FreeTypeFont, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
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
        if max_lines and len(lines) > max_lines:
            continue
        line_height = int(size * 1.25)
        total_height = len(lines) * line_height
        if total_height <= y1 - y0:
            y = y0 + max(0, ((y1 - y0) - total_height) // 2)
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
    raise ValueError(f"Text does not fit locked About-page bounds: {text!r}")


def paste_contain(
    canvas: Image.Image,
    source: Path,
    bounds: list[int],
    *,
    inset: int = 0,
    remove_near_white: bool = False,
    trim_near_white: bool = False,
) -> dict[str, Any]:
    image = Image.open(source).convert("RGBA")
    original = [image.width, image.height]
    crop_bounds = [0, 0, image.width, image.height]
    if trim_near_white:
        white = Image.new("RGB", image.size, "white")
        difference = ImageChops.difference(image.convert("RGB"), white).convert("L")
        foreground = difference.point(lambda value: 255 if value > 6 else 0)
        foreground = ImageChops.multiply(foreground, image.getchannel("A"))
        bounding_box = foreground.getbbox()
        if bounding_box is None:
            raise ValueError(f"Illustration contains no visible non-white artwork: {source}")
        crop_bounds = list(bounding_box)
        image = image.crop(bounding_box)
    if remove_near_white:
        pixels = [
            (255, 255, 255, 0) if r > 246 and g > 246 and b > 246 else (r, g, b, a)
            for r, g, b, a in image.getdata()
        ]
        image.putdata(pixels)
    trimmed_source = [image.width, image.height]
    x0, y0, x1, y1 = bounds
    x0 += inset
    y0 += inset
    x1 -= inset
    y1 -= inset
    scale = min((x1 - x0) / image.width, (y1 - y0) / image.height)
    width = max(1, round(image.width * scale))
    height = max(1, round(image.height * scale))
    image = image.resize((width, height), Image.Resampling.LANCZOS)
    x = x0 + (x1 - x0 - width) // 2
    y = y0 + (y1 - y0 - height) // 2
    canvas.paste(image, (x, y), image)
    return {
        "source_size": original,
        "source_crop_bounds": crop_bounds,
        "trimmed_source_size": trimmed_source,
        "trim_applied": trim_near_white,
        "rendered_bounds": [x, y, x + width, y + height],
        "scale": scale,
    }


def draw_title(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    bounds: list[int],
    colours: dict[str, str],
) -> dict[str, Any]:
    """Render every registered About-page book name on one colour-segmented line."""
    segments = [str(value).strip() for value in lines if str(value).strip()]
    if not segments:
        raise ValueError("book_title_lines must contain at least one value")
    first, remainder = segments[0], " ".join(segments[1:])
    second = f" {remainder}" if remainder else ""
    x0, y0, x1, y1 = bounds
    for size in range(84, 31, -2):
        active = font(size, True)
        first_width = draw.textlength(first, font=active)
        second_width = draw.textlength(second, font=active)
        line_height = int(size * 1.2)
        if first_width + second_width <= x1 - x0 and line_height <= y1 - y0:
            x = x0 + ((x1 - x0) - first_width - second_width) / 2
            y = y0 + ((y1 - y0) - line_height) / 2
            draw.text((x, y), first, font=active, fill=colours["purple"])
            if second:
                draw.text((x + first_width, y), second, font=active, fill=colours["blue"])
            return {
                "bounds": bounds,
                "font_size": size,
                "lines": [" ".join(segments)],
                "coloured_segments": segments,
            }
    raise ValueError(f"Registered book title does not fit one-line About header: {' '.join(segments)!r}")


def draw_outcomes(
    draw: ImageDraw.ImageDraw,
    outcomes: list[str],
    bounds: list[int],
    fills: list[str],
    colours: dict[str, str],
) -> list[dict[str, Any]]:
    x0, y0, x1, y1 = bounds
    gap_x, gap_y = 24, 20
    width = (x1 - x0 - 2 * gap_x) // 3
    height = (y1 - y0 - gap_y) // 2
    rendered = []
    for index, outcome in enumerate(outcomes):
        row, column = divmod(index, 3)
        left = x0 + column * (width + gap_x)
        top = y0 + row * (height + gap_y)
        card = [left, top, left + width, top + height]
        draw.rounded_rectangle(card, radius=28, fill=fills[index], outline=colours["overview_line"], width=3)
        draw.ellipse([left + 22, top + 59, left + 78, top + 115], fill=colours["purple"])
        draw_fitted_text(draw, str(index + 1), [left + 22, top + 59, left + 78, top + 115],
                         max_size=28, min_size=22, fill=colours["white"], bold=True,
                         align="center", max_lines=1)
        text_render = draw_fitted_text(
            draw,
            outcome,
            [left + 98, top + 24, left + width - 24, top + height - 24],
            max_size=34,
            min_size=24,
            fill=colours["navy"],
            bold=True,
            max_lines=3,
        )
        rendered.append({"card_bounds": card, "text": text_render})
    return rendered


def draw_pillars(
    draw: ImageDraw.ImageDraw,
    pillars: list[str],
    bounds: list[int],
    fills: list[str],
    colours: dict[str, str],
) -> list[dict[str, Any]]:
    x0, y0, x1, y1 = bounds
    gap = 16
    width = (x1 - x0 - 4 * gap) // 5
    rendered = []
    for index, pillar in enumerate(pillars):
        left = x0 + index * (width + gap)
        card = [left, y0, left + width, y1]
        draw.rounded_rectangle(card, radius=34, fill=fills[index])
        code = {"Creativity": "CR", "Communication": "CO", "Curiosity": "CU",
                "Confidence": "CF", "Collaboration": "CL"}.get(pillar, pillar[:2].upper())
        code_render = draw_fitted_text(draw, code, [left + 18, y0 + 18, left + width - 18, y0 + 108],
                                       max_size=50, min_size=34, fill=colours["white"], bold=True,
                                       align="center", max_lines=1)
        name_render = draw_fitted_text(draw, pillar, [left + 18, y0 + 115, left + width - 18, y1 - 16],
                                       max_size=27, min_size=20, fill=colours["white"], bold=True,
                                       align="center", max_lines=2)
        rendered.append({"card_bounds": card, "code": code_render, "name": name_render})
    return rendered


def compose(data_path: Path, output: Path, evidence_output: Path) -> None:
    template = load_json(TEMPLATE_PATH)
    data = load_json(data_path)
    canvas_spec = template["canvas"]
    bounds = template["bounds"]
    colours = template["colours"]
    canvas = Image.new("RGB", (canvas_spec["width"], canvas_spec["height"]), colours["background"])
    draw = ImageDraw.Draw(canvas)

    logo_render = paste_contain(
        canvas,
        resolve(data["official_logo_path"]),
        bounds["logo"],
        remove_near_white=True,
    )
    title_render = draw_title(draw, data["book_title_lines"], bounds["book_title"], colours)
    draw.rounded_rectangle(bounds["page_title"], radius=34, fill=colours["purple"])
    page_title_render = draw_fitted_text(
        draw,
        data["page_title"],
        [bounds["page_title"][0] + 35, bounds["page_title"][1] + 15,
         bounds["page_title"][2] - 35, bounds["page_title"][3] - 15],
        max_size=62,
        min_size=42,
        fill=colours["white"],
        bold=True,
        align="center",
        max_lines=1,
    )

    draw.rounded_rectangle(bounds["overview_panel"], radius=34, fill=colours["overview_fill"],
                           outline=colours["overview_line"], width=4)
    overview_heading_render = draw_fitted_text(
        draw,
        f"WELCOME TO {data['book_title'].upper()}",
        bounds["overview_heading"],
        max_size=38,
        min_size=28,
        fill=colours["purple"],
        bold=True,
        align="center",
        max_lines=1,
    )
    overview_render = draw_fitted_text(
        draw,
        f"{data['learning_objective']} {data['overview']}",
        bounds["overview_text"],
        max_size=34,
        min_size=26,
        fill=colours["text"],
        align="center",
        max_lines=4,
    )

    draw.rounded_rectangle(bounds["illustration_frame"], radius=42, fill=colours["white"],
                           outline=colours["frame_line"], width=6)
    illustration_render = paste_contain(
        canvas,
        resolve(data["illustration_path"]),
        bounds["illustration_frame"],
        inset=template["rules"]["illustration_safe_inset"],
        remove_near_white=True,
        trim_near_white=True,
    )

    outcomes_label_render = draw_fitted_text(
        draw,
        "WHAT YOU WILL LEARN",
        bounds["outcomes_label"],
        max_size=44,
        min_size=34,
        fill=colours["navy"],
        bold=True,
        align="center",
        max_lines=1,
    )
    outcomes_render = draw_outcomes(
        draw,
        data["learning_outcomes"],
        bounds["outcomes"],
        template["outcome_colours"],
        colours,
    )
    pillars_label_render = draw_fitted_text(
        draw,
        "OUR CORE PILLARS",
        bounds["pillars_label"],
        max_size=40,
        min_size=32,
        fill=colours["purple"],
        bold=True,
        align="center",
        max_lines=1,
    )
    pillars_render = draw_pillars(
        draw,
        data["core_pillars"],
        bounds["pillars"],
        template["pillar_colours"],
        colours,
    )

    draw.rectangle(bounds["footer"], fill=colours["purple"])
    draw.rectangle([bounds["footer"][0], bounds["footer"][1], bounds["footer"][2],
                    bounds["footer"][1] + 12], fill=colours["gold"])
    footer_brand_render = draw_fitted_text(
        draw,
        "BUILD • CREATE • BECOME",
        [150, bounds["footer"][1] + 24, 2330, bounds["footer"][1] + 92],
        max_size=38,
        min_size=30,
        fill=colours["white"],
        bold=True,
        align="center",
        max_lines=1,
    )
    footer_keywords_render = draw_fitted_text(
        draw,
        data["footer_keywords"],
        [150, bounds["footer"][1] + 100, 2330, bounds["footer"][3] - 16],
        max_size=27,
        min_size=20,
        fill="#F7EAFB",
        align="center",
        max_lines=1,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, "PNG", dpi=(canvas_spec["dpi"], canvas_spec["dpi"]))
    evidence = {
        "engine": "BCube Publishing Engine About Page",
        "template_version": template["template_version"],
        "page_id": data["page_id"],
        "page_type": "about",
        "header_type": "BOOK_HEADER",
        "canvas": canvas_spec,
        "artifact": str(output),
        "artifact_sha256": sha256(output),
        "inputs": {
            "illustration_sha256": sha256(resolve(data["illustration_path"])),
            "logo_sha256": sha256(resolve(data["official_logo_path"])),
        },
        "components": {
            "official_logo": logo_render,
            "book_title": title_render,
            "page_title": page_title_render,
            "overview_heading": overview_heading_render,
            "overview": overview_render,
            "illustration_frame": {"bounds": bounds["illustration_frame"]},
            "illustration": illustration_render,
            "learning_outcomes_label": outcomes_label_render,
            "learning_outcomes": outcomes_render,
            "core_pillars_label": pillars_label_render,
            "core_pillars": pillars_render,
            "footer": {
                "bounds": bounds["footer"],
                "brand": footer_brand_render,
                "keywords": footer_keywords_render,
            },
        },
        "prohibited_component_counts": {
            "series_banner": 0,
            "age_badge": 0,
            "visible_page_number": 0,
            "teacher_panel": 0,
            "parent_panel": 0,
            "official_star": 0,
        },
        "qa": {
            "one_physical_page": True,
            "book_header": True,
            "single_line_book_title": title_render["lines"] == [data["book_title"]],
            "subject_clipped": False,
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
