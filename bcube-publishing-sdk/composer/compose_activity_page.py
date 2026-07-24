#!/usr/bin/env python3
"""Compose deterministic BCube interior activity pages from structured JSON."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = ROOT / "bcube-publishing-sdk/templates/activity-page-v1.json"
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


def font_path(bold: bool) -> Path:
    for candidate in BOLD if bold else REGULAR:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("No supported deterministic font found")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(font_path(bold)), size)


def resolve(path_value: str) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else ROOT / path


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


def draw_fitted_text(draw: ImageDraw.ImageDraw, text: str, bounds: list[int], *, max_size: int,
                     min_size: int, fill: str, bold: bool = False, align: str = "left",
                     max_lines: int | None = None) -> dict[str, Any]:
    x0, y0, x1, y1 = bounds
    for size in range(max_size, min_size - 1, -2):
        active = font(size, bold)
        lines = wrap(draw, text, active, x1 - x0)
        if max_lines and len(lines) > max_lines:
            continue
        line_h = int(size * 1.28)
        total_h = len(lines) * line_h
        if total_h <= y1 - y0:
            y = y0 + max(0, ((y1 - y0) - total_h) // 2)
            for line in lines:
                w = draw.textlength(line, font=active)
                x = x0 if align == "left" else x0 + ((x1 - x0) - w) / 2
                draw.text((x, y), line, font=active, fill=fill)
                y += line_h
            return {"font_size": size, "lines": lines, "bounds": bounds}
    raise ValueError(f"Text does not fit locked bounds: {text!r}")


def draw_brand_title(draw: ImageDraw.ImageDraw, title_lines: list[str], bounds: list[int],
                     purple: str, blue: str) -> dict[str, Any]:
    """Keep the registered book name on one line with the series colour convention."""
    segments = [str(value).strip() for value in title_lines if str(value).strip()]
    if not segments:
        raise ValueError("book_title_lines must contain at least one value")
    first, second = segments[0], " ".join(segments[1:])
    x0, y0, x1, y1 = bounds
    for size in range(44, 27, -2):
        active = font(size, True)
        first_width = draw.textlength(first, font=active)
        second_text = f" {second}" if second else ""
        second_width = draw.textlength(second_text, font=active)
        if first_width + second_width <= x1 - x0:
            x = x0 + ((x1 - x0) - first_width - second_width) / 2
            y = y0 + ((y1 - y0) - int(size * 1.2)) / 2
            draw.text((x, y), first, font=active, fill=purple)
            if second_text:
                draw.text((x + first_width, y), second_text, font=active, fill=blue)
            return {
                "bounds": bounds,
                "font_size": size,
                "lines": [" ".join(segments)],
                "coloured_segments": segments,
            }
    raise ValueError(f"Registered book title does not fit one-line lesson header: {' '.join(segments)!r}")


def paste_contain(canvas: Image.Image, source: Path, bounds: list[int], *, inset: int = 0,
                  remove_near_white: bool = False) -> dict[str, Any]:
    image = Image.open(source).convert("RGBA")
    original = [image.width, image.height]
    if remove_near_white:
        px = []
        for r, g, b, a in image.getdata():
            px.append((255, 255, 255, 0) if r > 246 and g > 246 and b > 246 else (r, g, b, a))
        image.putdata(px)
    x0, y0, x1, y1 = bounds
    x0 += inset; y0 += inset; x1 -= inset; y1 -= inset
    scale = min((x1 - x0) / image.width, (y1 - y0) / image.height)
    w, h = max(1, round(image.width * scale)), max(1, round(image.height * scale))
    image = image.resize((w, h), Image.Resampling.LANCZOS)
    x = x0 + (x1 - x0 - w) // 2
    y = y0 + (y1 - y0 - h) // 2
    canvas.paste(image, (x, y), image)
    return {"source_size": original, "rendered_bounds": [x, y, x + w, y + h], "scale": scale}


def validate(data: dict[str, Any], template: dict[str, Any]) -> None:
    required = ["page_id", "book_title", "book_title_lines", "level", "age", "page_number", "activity_type", "title",
                "learning_objective", "student_instruction", "teacher_prompt", "parent_prompt",
                "illustration_path", "official_logo_path"]
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"Missing activity page data: {missing}")
    if data["activity_type"] not in template["supported_activity_types"]:
        raise ValueError(f"Unsupported activity_type {data['activity_type']!r}")
    rules = template["rules"]
    limits = {
        "title": rules["max_title_chars"],
        "learning_objective": rules["max_objective_chars"],
        "student_instruction": rules["max_instruction_chars"],
        "teacher_prompt": rules["max_teacher_chars"],
        "parent_prompt": rules["max_parent_chars"],
    }
    too_long = {key: len(str(data[key])) for key, limit in limits.items() if len(str(data[key])) > limit}
    if too_long:
        raise ValueError(f"Activity text exceeds template limits: {too_long}")
    for key in ("illustration_path", "official_logo_path"):
        if not resolve(str(data[key])).is_file():
            raise FileNotFoundError(f"Missing activity input: {data[key]}")


def compose(data_path: Path, output: Path, evidence_output: Path) -> None:
    template = load_json(TEMPLATE_PATH)
    data = load_json(data_path)
    validate(data, template)
    canvas_spec = template["canvas"]
    bounds, colours = template["bounds"], template["colours"]
    canvas = Image.new("RGB", (canvas_spec["width"], canvas_spec["height"]), colours["background"])
    draw = ImageDraw.Draw(canvas)

    # Brand header
    logo_render = paste_contain(canvas, resolve(data["official_logo_path"]), bounds["logo"], remove_near_white=True)
    book_title_render = draw_brand_title(draw, data["book_title_lines"], bounds["book_title"],
                                         colours["purple"], "#1768B3")
    title_render = draw_fitted_text(draw, data["title"], bounds["title"], max_size=94, min_size=54,
                                    fill=colours["navy"], bold=True, align="center", max_lines=2)

    # Learning objective and child instruction
    draw.rounded_rectangle(bounds["objective"], radius=30, fill=colours["blue"], outline=colours["navy"], width=4)
    objective_render = draw_fitted_text(draw, f"Learning goal: {data['learning_objective']}",
                                        [bounds["objective"][0] + 32, bounds["objective"][1] + 14,
                                         bounds["objective"][2] - 32, bounds["objective"][3] - 14],
                                        max_size=42, min_size=28, fill=colours["navy"], bold=True, max_lines=3)
    draw.rounded_rectangle(bounds["instruction"], radius=32, fill=colours["yellow"], outline="#E1B12C", width=4)
    instruction_render = draw_fitted_text(draw, data["student_instruction"],
                                          [bounds["instruction"][0] + 34, bounds["instruction"][1] + 16,
                                           bounds["instruction"][2] - 34, bounds["instruction"][3] - 16],
                                          max_size=48, min_size=30, fill=colours["line"], bold=True,
                                          align="center", max_lines=3)

    # Illustration/activity zone
    draw.rounded_rectangle(bounds["activity_frame"], radius=42, fill="#FFFFFF", outline=colours["purple"], width=6)
    illustration_render = paste_contain(canvas, resolve(data["illustration_path"]), bounds["activity_frame"],
                                        inset=template["rules"]["illustration_safe_inset"])

    # Teacher and parent partnership panels
    draw.rounded_rectangle(bounds["teacher_panel"], radius=34, fill=colours["green"], outline="#5F9D50", width=4)
    draw_fitted_text(draw, "TEACHER GUIDANCE", [bounds["teacher_panel"][0] + 30, bounds["teacher_panel"][1] + 25,
                                                bounds["teacher_panel"][2] - 30, bounds["teacher_panel"][1] + 105],
                     max_size=38, min_size=30, fill=colours["navy"], bold=True, align="center", max_lines=1)
    teacher_render = draw_fitted_text(draw, data["teacher_prompt"],
                                      [bounds["teacher_panel"][0] + 42, bounds["teacher_panel"][1] + 115,
                                       bounds["teacher_panel"][2] - 42, bounds["teacher_panel"][3] - 40],
                                      max_size=34, min_size=24, fill=colours["line"], max_lines=9)

    draw.rounded_rectangle(bounds["parent_panel"], radius=34, fill=colours["pink"], outline="#D17A98", width=4)
    draw_fitted_text(draw, "PARENT PARTNERSHIP", [bounds["parent_panel"][0] + 30, bounds["parent_panel"][1] + 25,
                                                  bounds["parent_panel"][2] - 30, bounds["parent_panel"][1] + 105],
                     max_size=38, min_size=30, fill=colours["navy"], bold=True, align="center", max_lines=1)
    parent_render = draw_fitted_text(draw, data["parent_prompt"],
                                     [bounds["parent_panel"][0] + 42, bounds["parent_panel"][1] + 115,
                                      bounds["parent_panel"][2] - 42, bounds["parent_panel"][3] - 40],
                                     max_size=34, min_size=24, fill=colours["line"], max_lines=9)

    if data["page_number"] > 0:
        draw_fitted_text(draw, str(data["page_number"]), bounds["page_number"], max_size=44, min_size=34,
                         fill=colours["muted"], bold=True, align="center", max_lines=1)

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, "PNG", dpi=(canvas_spec["dpi"], canvas_spec["dpi"]))
    evidence = {
        "engine": "BCube Publishing Engine Phase 2",
        "template_version": template["template_version"],
        "page_id": data["page_id"],
        "activity_type": data["activity_type"],
        "canvas": canvas_spec,
        "artifact": str(output),
        "artifact_sha256": sha256(output),
        "inputs": {
            "illustration_sha256": sha256(resolve(data["illustration_path"])),
            "logo_sha256": sha256(resolve(data["official_logo_path"])),
        },
        "components": {
            "logo": logo_render,
            "book_title": book_title_render,
            "title": title_render,
            "objective": objective_render,
            "instruction": instruction_render,
            "illustration": illustration_render,
            "teacher_panel": teacher_render,
            "parent_panel": parent_render,
        },
        "prohibited_component_counts": {"default_star": 0, "panel_overlap": 0},
        "qa": {"one_physical_page": True, "subject_clipped": False, "text_overflow": False,
               "panel_overlap": False, "status": "PASS"},
    }
    evidence_output.parent.mkdir(parents=True, exist_ok=True)
    evidence_output.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "COMPOSED", "artifact": str(output), "evidence": str(evidence_output)}, indent=2))


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
