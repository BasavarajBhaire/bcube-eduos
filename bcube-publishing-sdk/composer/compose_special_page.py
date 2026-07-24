#!/usr/bin/env python3
"""Compose locked Contents, Welcome, and Meet Star pages."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = ROOT / "bcube-publishing-sdk/templates/special-page-v1.json"
BOLD = [Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"), Path("C:/Windows/Fonts/arialbd.ttf")]
REGULAR = [Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), Path("C:/Windows/Fonts/arial.ttf")]
PILLAR_COLOURS = ["#F57C00", "#25A43A", "#2E98CE", "#8E3DB3", "#ED2F7C"]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def resolve(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for candidate in BOLD if bold else REGULAR:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    raise FileNotFoundError("No deterministic font is available")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wrap(draw: ImageDraw.ImageDraw, text: str, active: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in str(text).split():
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=active) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fitted_text(draw: ImageDraw.ImageDraw, text: str, bounds: list[int], *, max_size: int,
                min_size: int, colour: str, bold: bool = False, align: str = "center",
                max_lines: int | None = None) -> dict[str, Any]:
    x0, y0, x1, y1 = bounds
    for size in range(max_size, min_size - 1, -2):
        active = font(size, bold)
        lines = wrap(draw, text, active, x1 - x0)
        if max_lines is not None and len(lines) > max_lines:
            continue
        line_height = int(size * 1.25)
        if len(lines) * line_height > y1 - y0:
            continue
        y = y0 + ((y1 - y0) - len(lines) * line_height) // 2
        for line in lines:
            width = draw.textlength(line, font=active)
            x = x0 if align == "left" else x0 + ((x1 - x0) - width) / 2
            draw.text((x, y), line, font=active, fill=colour)
            y += line_height
        return {"bounds": bounds, "font_size": size, "lines": lines}
    raise ValueError(f"Text does not fit locked bounds: {text!r}")


def paste_contain(canvas: Image.Image, source: Path, bounds: list[int], *, inset: int = 0,
                  remove_near_white: bool = False) -> dict[str, Any]:
    image = Image.open(source).convert("RGBA")
    original = [image.width, image.height]
    if remove_near_white:
        pixels = [
            (255, 255, 255, 0) if r > 246 and g > 246 and b > 246 else (r, g, b, a)
            for r, g, b, a in image.getdata()
        ]
        image.putdata(pixels)
    x0, y0, x1, y1 = bounds
    x0 += inset; y0 += inset; x1 -= inset; y1 -= inset
    scale = min((x1 - x0) / image.width, (y1 - y0) / image.height)
    width, height = max(1, round(image.width * scale)), max(1, round(image.height * scale))
    image = image.resize((width, height), Image.Resampling.LANCZOS)
    x = x0 + (x1 - x0 - width) // 2
    y = y0 + (y1 - y0 - height) // 2
    canvas.paste(image, (x, y), image)
    return {"source_size": original, "rendered_bounds": [x, y, x + width, y + height]}


def brand_title(draw: ImageDraw.ImageDraw, title_lines: list[str], bounds: list[int], colours: dict[str, str]) -> dict[str, Any]:
    lines = [str(value).strip() for value in title_lines if str(value).strip()]
    if not lines:
        raise ValueError("book_title_lines must contain at least one value")
    x0, y0, x1, y1 = bounds
    first, second = lines[0], " ".join(lines[1:])
    for size in range(78, 43, -2):
        active = font(size, True)
        first_width = draw.textlength(first, font=active)
        second_width = draw.textlength(f" {second}", font=active) if second else 0
        if first_width + second_width <= x1 - x0:
            x = x0 + ((x1 - x0) - first_width - second_width) / 2
            y = y0 + ((y1 - y0) - int(size * 1.2)) / 2
            draw.text((x, y), first, font=active, fill=colours["purple"])
            if second:
                draw.text((x + first_width, y), f" {second}", font=active, fill=colours["blue"])
            return {"bounds": bounds, "font_size": size, "lines": [" ".join(lines)], "coloured_segments": lines}
    return fitted_text(draw, "\n".join(lines), bounds, max_size=58, min_size=42,
                       colour=colours["purple"], bold=True, max_lines=2)


def draw_footer(canvas: Image.Image, draw: ImageDraw.ImageDraw, bounds: list[int], text: str,
                colours: dict[str, str]) -> dict[str, Any]:
    x0, y0, x1, y1 = bounds
    draw.rectangle(bounds, fill=colours["purple"])
    draw.rectangle((x0, y0, x1, y0 + 12), fill=colours["gold"])
    return fitted_text(draw, text, [x0 + 100, y0 + 30, x1 - 100, y1 - 20], max_size=34,
                       min_size=26, colour="white", bold=True, max_lines=2)


def draw_pillars(draw: ImageDraw.ImageDraw, bounds: list[int], pillars: list[str]) -> dict[str, Any]:
    if len(pillars) != 5:
        raise ValueError("Exactly five core pillars are required")
    x0, y0, x1, y1 = bounds
    gap = 22
    width = (x1 - x0 - gap * 4) // 5
    rendered: list[dict[str, Any]] = []
    for index, pillar in enumerate(pillars):
        left = x0 + index * (width + gap)
        box = [left, y0 + 30, left + width, y1 - 20]
        draw.rounded_rectangle(box, radius=38, fill=PILLAR_COLOURS[index])
        item = fitted_text(draw, pillar, [left + 20, y0 + 48, left + width - 20, y1 - 35],
                           max_size=32, min_size=24, colour="white", bold=True, max_lines=2)
        rendered.append(item)
    return {"count": 5, "items": rendered, "bounds": bounds}


def module_label(value: str) -> str:
    cleaned = str(value).strip()
    if cleaned == "FRONT_MATTER":
        return "Welcome"
    return cleaned.replace("_", " ").title() or "Learning Journey"


def draw_contents(draw: ImageDraw.ImageDraw, data: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    spec = template["contents"]
    entries = data["entries"]
    if len(entries) != spec["entries_per_page"]:
        raise ValueError(f"Contents page must contain exactly {spec['entries_per_page']} entries")
    draw.rounded_rectangle(spec["body"], radius=42, fill="#FFFFFF", outline="#D9C7E8", width=5)
    midpoint = 10
    columns = [entries[:midpoint], entries[midpoint:]]
    rendered: list[dict[str, Any]] = []
    for column_index, items in enumerate(columns):
        x0, y0, x1, y1 = spec["columns"][column_index]
        y = y0
        previous_module = ""
        for item in items:
            module = module_label(item.get("module", ""))
            if module != previous_module:
                if previous_module:
                    y += 16
                draw.rounded_rectangle((x0, y, x1, y + 68), radius=22,
                                       fill=["#6F3D91", "#1768B3"][column_index])
                module_render = fitted_text(
                    draw,
                    module,
                    [x0 + 22, y + 2, x1 - 22, y + 66],
                    max_size=spec["module_heading_max_px"],
                    min_size=spec["module_heading_min_px"],
                    colour="white",
                    bold=True,
                    align="left",
                    max_lines=1,
                )
                rendered.append({
                    "component": "module_heading",
                    "module": module,
                    "column": column_index,
                    "y": y,
                    "typography": module_render,
                })
                y += 82
                previous_module = module
            active = font(44)
            page_font = font(44, True)
            page_text = str(item["page"])
            page_width = draw.textlength(page_text, font=page_font)
            title = str(item["title"])
            if item.get("physical") == 6 and not title.casefold().startswith("welcome to"):
                title = f"Welcome to {data['book_title']}"
            available = x1 - x0 - page_width - 95
            if draw.textlength(title, font=active) > available:
                active = font(42)
            if draw.textlength(title, font=active) > available:
                raise ValueError(f"Contents entry is too long for locked typography: {title!r}")
            draw.text((x0 + 8, y + 18), title, font=active, fill=template["colours"]["text"])
            start = x0 + 20 + draw.textlength(title, font=active)
            end = x1 - page_width - 26
            for dot_x in range(round(start), round(end), 18):
                draw.ellipse((dot_x, y + 48, dot_x + 4, y + 52), fill="#A6ADBA")
            draw.text((x1 - page_width - 8, y + 18), page_text, font=page_font,
                      fill=template["colours"]["blue"])
            rendered.append({"component": "contents_entry", "title": title, "page": item["page"],
                             "module": module, "column": column_index, "y": y})
            y += spec["row_advance_min_px"]
        if y > y1:
            raise ValueError("Contents entries exceed the locked column bounds")
    return {
        "items": rendered,
        "entry_count": sum(item["component"] == "contents_entry" for item in rendered),
        "module_heading_count": sum(item["component"] == "module_heading" for item in rendered),
        "columns": 2,
    }


def validate(data: dict[str, Any], template: dict[str, Any]) -> None:
    page_type = data.get("page_type")
    if page_type not in {"contents", "welcome", "meet_star"}:
        raise ValueError(f"Unsupported special page type: {page_type!r}")
    required = ["page_id", "page_type", "physical_page", "book_title", "book_title_lines",
                "page_title", "level", "tagline", "core_pillars", "footer_keywords",
                "official_logo_path"]
    if page_type == "contents":
        required.append("entries")
    elif page_type == "welcome":
        required.extend(["page_number", "message", "illustration_path"])
    else:
        required.extend(["page_number", "message", "purpose", "official_star_path"])
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"Missing {page_type} page data: {missing}")
    prohibited = {"teacher_prompt", "parent_prompt", "series", "age_badge"}
    present = sorted(prohibited.intersection(data))
    if present:
        raise ValueError(f"{page_type} page contains prohibited components: {present}")
    for asset_key in ("official_logo_path", "illustration_path", "official_star_path"):
        if asset_key in data and not resolve(str(data[asset_key])).is_file():
            raise FileNotFoundError(f"Missing {asset_key}: {data[asset_key]}")
    if page_type == "contents" and data["physical_page"] not in {4, 5}:
        raise ValueError("Contents must be physical page 4 or 5")
    if page_type == "welcome" and (data["physical_page"], data["page_number"]) != (6, 5):
        raise ValueError("Welcome must be physical page 6 and visibly numbered 5")
    if page_type == "meet_star" and (data["physical_page"], data["page_number"]) != (7, 6):
        raise ValueError("Meet Star must be physical page 7 and visibly numbered 6")


def compose(data_path: Path, output: Path, evidence_output: Path) -> None:
    template = load(TEMPLATE_PATH)
    data = load(data_path)
    validate(data, template)
    canvas_spec = template["canvas"]
    colours = template["colours"]
    bounds = template["common_bounds"]
    canvas = Image.new("RGB", (canvas_spec["width"], canvas_spec["height"]), colours["background"])
    draw = ImageDraw.Draw(canvas)
    logo_render = paste_contain(canvas, resolve(data["official_logo_path"]), bounds["logo"], remove_near_white=True)
    title_render = brand_title(draw, data["book_title_lines"], bounds["book_title"], colours)
    page_title_render = fitted_text(draw, data["page_title"], bounds["page_title"], max_size=72,
                                    min_size=44, colour=colours["navy"], bold=True, max_lines=2)
    draw.rounded_rectangle(bounds["tagline"], radius=34, fill="#FFF3BE", outline=colours["gold"], width=4)
    tagline_render = fitted_text(draw, data["tagline"], [bounds["tagline"][0] + 40, bounds["tagline"][1] + 12,
                                                          bounds["tagline"][2] - 40, bounds["tagline"][3] - 12],
                                  max_size=42, min_size=30, colour=colours["text"], bold=True, max_lines=2)
    components: dict[str, Any] = {
        "official_logo": logo_render,
        "book_title": title_render,
        "page_title": page_title_render,
        "tagline": tagline_render,
    }
    page_type = data["page_type"]
    if page_type == "contents":
        components["module_groups"] = draw_contents(draw, data, template)
    elif page_type == "welcome":
        spec = template["welcome"]
        draw.rounded_rectangle(spec["message"], radius=34, fill="#EAF5FF", outline=colours["blue"], width=4)
        components["welcome_message"] = fitted_text(draw, data["message"],
                                                     [spec["message"][0] + 40, spec["message"][1] + 22,
                                                      spec["message"][2] - 40, spec["message"][3] - 22],
                                                     max_size=44, min_size=30, colour=colours["navy"],
                                                     bold=True, max_lines=4)
        draw.rounded_rectangle(spec["illustration_frame"], radius=44, fill="#FFFFFF",
                               outline=colours["purple"], width=6)
        components["illustration"] = paste_contain(canvas, resolve(data["illustration_path"]),
                                                    spec["illustration_frame"], inset=36)
    else:
        spec = template["meet_star"]
        draw.rounded_rectangle(spec["message"], radius=34, fill="#EAF5FF", outline=colours["blue"], width=4)
        components["star_message"] = fitted_text(draw, data["message"],
                                                  [spec["message"][0] + 40, spec["message"][1] + 20,
                                                   spec["message"][2] - 40, spec["message"][3] - 20],
                                                  max_size=44, min_size=30, colour=colours["navy"],
                                                  bold=True, max_lines=4)
        components["official_star"] = paste_contain(canvas, resolve(data["official_star_path"]),
                                                     spec["star"], remove_near_white=True)
        draw.rounded_rectangle(spec["purpose"], radius=34, fill="#F3EAF9", outline=colours["purple"], width=4)
        components["purpose"] = fitted_text(draw, data["purpose"],
                                             [spec["purpose"][0] + 50, spec["purpose"][1] + 30,
                                              spec["purpose"][2] - 50, spec["purpose"][3] - 30],
                                             max_size=42, min_size=28, colour=colours["text"], max_lines=5)
    components["core_pillars"] = draw_pillars(draw, bounds["pillars"], data["core_pillars"])
    if page_type != "contents":
        components["page_number"] = fitted_text(draw, str(data["page_number"]), bounds["page_number"],
                                                 max_size=46, min_size=36, colour=colours["muted"],
                                                 bold=True, max_lines=1)
    components["footer"] = draw_footer(canvas, draw, bounds["footer"], data["footer_keywords"], colours)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, "PNG", dpi=(canvas_spec["dpi"], canvas_spec["dpi"]))
    evidence = {
        "engine": "BCube Publishing Engine",
        "template_version": template["template_version"],
        "page_id": data["page_id"],
        "page_type": page_type,
        "header_type": "BOOK_HEADER",
        "canvas": canvas_spec,
        "artifact_sha256": sha256(output),
        "components": components,
        "prohibited_component_counts": {
            "series_banner": 0,
            "age_badge": 0,
            "teacher_panel": 0,
            "parent_panel": 0,
            "visible_page_number": 0 if page_type == "contents" else 1,
            "illustration": 1 if page_type == "welcome" else 0,
            "official_star": 1 if page_type == "meet_star" else 0,
        },
        "qa": {"one_physical_page": True, "text_overflow": False, "status": "PASS"},
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
