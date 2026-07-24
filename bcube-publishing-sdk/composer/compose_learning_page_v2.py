#!/usr/bin/env python3
"""Compose BCube Learning Page Contract V2 with deterministic worksheet mechanics."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = ROOT / "bcube-publishing-sdk/templates/learning-page-v2.json"
BOLD = [
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("C:/Windows/Fonts/arialbd.ttf"),
]
REGULAR = [
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("C:/Windows/Fonts/arial.ttf"),
]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def resolve(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = BOLD if bold else REGULAR
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    raise FileNotFoundError("No deterministic font is available")


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


def fitted_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    bounds: list[int],
    *,
    max_size: int,
    min_size: int,
    colour: str,
    bold: bool = False,
    align: str = "center",
    max_lines: int | None = None,
) -> dict[str, Any]:
    x0, y0, x1, y1 = bounds
    for size in range(max_size, min_size - 1, -2):
        active = font(size, bold)
        lines = wrap(draw, text, active, x1 - x0)
        if max_lines is not None and len(lines) > max_lines:
            continue
        line_height = int(size * 1.25)
        total_height = len(lines) * line_height
        if total_height > y1 - y0:
            continue
        y = y0 + ((y1 - y0) - total_height) // 2
        for line in lines:
            line_width = draw.textlength(line, font=active)
            x = x0 if align == "left" else x0 + ((x1 - x0) - line_width) / 2
            draw.text((x, y), line, font=active, fill=colour)
            y += line_height
        return {"bounds": bounds, "font_size": size, "lines": lines}
    raise ValueError(f"Text does not fit locked bounds: {text!r}")


def brand_title(
    draw: ImageDraw.ImageDraw,
    title_lines: list[str],
    bounds: list[int],
    colours: dict[str, str],
    typography: dict[str, Any],
) -> dict[str, Any]:
    lines = [str(value).strip() for value in title_lines if str(value).strip()]
    if not lines:
        raise ValueError("book_title_lines must be a non-empty list")
    first, second = lines[0], " ".join(lines[1:])
    x0, y0, x1, y1 = bounds
    for size in range(typography["book_title_max"], typography["book_title_min"] - 1, -2):
        active = font(size, True)
        first_width = draw.textlength(first, font=active)
        second_text = f" {second}" if second else ""
        second_width = draw.textlength(second_text, font=active)
        if first_width + second_width <= x1 - x0:
            x = x0 + ((x1 - x0) - first_width - second_width) / 2
            y = y0 + ((y1 - y0) - int(size * 1.2)) / 2
            draw.text((x, y), first, font=active, fill=colours["purple"])
            if second_text:
                draw.text((x + first_width, y), second_text, font=active, fill="#1768B3")
            return {
                "bounds": bounds,
                "font_size": size,
                "lines": [" ".join(lines)],
                "coloured_segments": lines,
            }
    raise ValueError(f"Registered book title does not fit the learning-page header: {' '.join(lines)!r}")


def remove_near_white(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    rgba.putdata(
        [
            (255, 255, 255, 0) if r > 246 and g > 246 and b > 246 else (r, g, b, a)
            for r, g, b, a in rgba.getdata()
        ]
    )
    bbox = rgba.getbbox()
    if bbox is None:
        raise ValueError("Illustration contains no visible artwork after background removal")
    return rgba.crop(bbox)


def paste_illustration(
    canvas: Image.Image,
    source: Path,
    bounds: list[int],
    *,
    inset: int,
    trim_near_white: bool,
) -> dict[str, Any]:
    original_image = Image.open(source).convert("RGBA")
    original_size = [original_image.width, original_image.height]
    image = remove_near_white(original_image) if trim_near_white else original_image
    source_crop_size = [image.width, image.height]
    x0, y0, x1, y1 = bounds
    x0 += inset
    y0 += inset
    x1 -= inset
    y1 -= inset
    available_width = x1 - x0
    available_height = y1 - y0
    scale = min(available_width / image.width, available_height / image.height)
    width = max(1, round(image.width * scale))
    height = max(1, round(image.height * scale))
    image = image.resize((width, height), Image.Resampling.LANCZOS)
    x = x0 + (available_width - width) // 2
    y = y0 + (available_height - height) // 2
    canvas.paste(image, (x, y), image)
    occupancy = round((width * height) / (available_width * available_height), 4)
    return {
        "source_size": original_size,
        "visible_source_size": source_crop_size,
        "available_bounds": [x0, y0, x1, y1],
        "rendered_bounds": [x, y, x + width, y + height],
        "visible_occupancy": occupancy,
        "trimmed_near_white": trim_near_white,
    }


def label(
    draw: ImageDraw.ImageDraw,
    text: str,
    bounds: list[int],
    colours: dict[str, str],
    typography: dict[str, Any],
) -> dict[str, Any]:
    return fitted_text(
        draw,
        text,
        bounds,
        max_size=typography["component_label_max"],
        min_size=typography["component_label_min"],
        colour=colours["navy"],
        bold=True,
        align="left",
        max_lines=1,
    )


def dashed_line(draw: ImageDraw.ImageDraw, start: tuple[int, int], end_x: int, colour: str, width: int, dash: int) -> None:
    x, y = start
    visible = True
    while x < end_x:
        next_x = min(end_x, x + dash)
        if visible:
            draw.line((x, y, next_x, y), fill=colour, width=width)
        visible = not visible
        x = next_x


def writing_guides(
    draw: ImageDraw.ImageDraw,
    bounds: list[int],
    *,
    dotted: bool,
    label_text: str,
    colours: dict[str, str],
    typography: dict[str, Any],
) -> dict[str, Any]:
    x0, y0, x1, y1 = bounds
    label_height = 54
    label_render = label(draw, label_text, [x0 + 12, y0, x1 - 12, y0 + label_height], colours, typography)
    line_top = y0 + label_height + 24
    line_bottom = y1 - 22
    middle = (line_top + line_bottom) // 2
    draw.line((x0 + 24, line_top, x1 - 24, line_top), fill=colours["guide"], width=3)
    if dotted:
        dashed_line(draw, (x0 + 24, middle), x1 - 24, colours["muted"], 3, 18)
    else:
        draw.line((x0 + 24, middle, x1 - 24, middle), fill="#CED3DA", width=2)
    draw.line((x0 + 24, line_bottom, x1 - 24, line_bottom), fill=colours["line"], width=4)
    return {
        "type": "trace_line" if dotted else "copy_line",
        "bounds": bounds,
        "label": label_render,
        "guide_lines": 3,
        "dotted_middle": dotted,
    }


def model_phrase(
    draw: ImageDraw.ImageDraw,
    bounds: list[int],
    text: str,
    colours: dict[str, str],
    typography: dict[str, Any],
) -> dict[str, Any]:
    draw.rounded_rectangle(bounds, radius=24, fill=colours["gold"], outline="#E1B12C", width=3)
    rendered = fitted_text(
        draw,
        text,
        [bounds[0] + 26, bounds[1] + 12, bounds[2] - 26, bounds[3] - 12],
        max_size=typography["model_text_max"],
        min_size=typography["model_text_min"],
        colour=colours["line"],
        bold=True,
        max_lines=2,
    )
    return {"type": "model_phrase", "bounds": bounds, "text": rendered}


def matching_anchors(
    draw: ImageDraw.ImageDraw,
    bounds: list[int],
    count: int,
    colours: dict[str, str],
    worksheet: dict[str, Any],
) -> dict[str, Any]:
    x0, y0, x1, y1 = bounds
    diameter = worksheet["matching_anchor_diameter"]
    usable_height = y1 - y0 - 40
    step = usable_height / max(1, count)
    anchors: list[dict[str, Any]] = []
    for index in range(count):
        centre_y = round(y0 + 20 + step * (index + 0.5))
        left = [x0 + 80, centre_y - diameter // 2, x0 + 80 + diameter, centre_y + diameter // 2]
        right = [x1 - 80 - diameter, centre_y - diameter // 2, x1 - 80, centre_y + diameter // 2]
        draw.ellipse(left, fill=colours["white"], outline=colours["purple"], width=4)
        draw.ellipse(right, fill=colours["white"], outline=colours["blue"], width=4)
        anchors.append({"index": index + 1, "left": left, "right": right})
    return {"type": "matching_anchors", "bounds": bounds, "count": count, "anchors": anchors}


def creative_response_area(
    draw: ImageDraw.ImageDraw,
    bounds: list[int],
    label_text: str,
    colours: dict[str, str],
    typography: dict[str, Any],
) -> dict[str, Any]:
    draw.rounded_rectangle(bounds, radius=28, fill=colours["white"], outline=colours["purple"], width=4)
    label_render = label(
        draw,
        label_text,
        [bounds[0] + 28, bounds[1] + 14, bounds[2] - 28, bounds[1] + 72],
        colours,
        typography,
    )
    return {"type": "creative_response_area", "bounds": bounds, "label": label_render}


def choice_targets(
    draw: ImageDraw.ImageDraw,
    bounds: list[int],
    count: int,
    colours: dict[str, str],
    worksheet: dict[str, Any],
) -> dict[str, Any]:
    x0, y0, x1, y1 = bounds
    diameter = worksheet["choice_target_diameter"]
    columns = min(4, count)
    rows = (count + columns - 1) // columns
    gap_x = (x1 - x0 - columns * diameter) / (columns + 1)
    gap_y = (y1 - y0 - rows * diameter) / (rows + 1)
    targets: list[list[int]] = []
    for index in range(count):
        row, column = divmod(index, columns)
        left = round(x0 + gap_x * (column + 1) + diameter * column)
        top = round(y0 + gap_y * (row + 1) + diameter * row)
        target = [left, top, left + diameter, top + diameter]
        draw.ellipse(target, fill=colours["white"], outline=colours["purple"], width=4)
        targets.append(target)
    return {"type": "choice_targets", "bounds": bounds, "count": count, "targets": targets}


def number_boxes(
    draw: ImageDraw.ImageDraw,
    bounds: list[int],
    count: int,
    colours: dict[str, str],
) -> dict[str, Any]:
    x0, y0, x1, y1 = bounds
    gap = 28
    box_width = min(250, (x1 - x0 - gap * (count - 1)) // count)
    total_width = box_width * count + gap * (count - 1)
    start_x = x0 + (x1 - x0 - total_width) // 2
    box_height = min(180, y1 - y0 - 40)
    top = y0 + (y1 - y0 - box_height) // 2
    boxes: list[list[int]] = []
    for index in range(count):
        left = start_x + index * (box_width + gap)
        box = [left, top, left + box_width, top + box_height]
        draw.rounded_rectangle(box, radius=24, fill=colours["white"], outline=colours["purple"], width=4)
        boxes.append(box)
    return {"type": "number_response_boxes", "bounds": bounds, "count": count, "boxes": boxes}


def sort_bins(
    draw: ImageDraw.ImageDraw,
    bounds: list[int],
    labels: list[str],
    colours: dict[str, str],
    typography: dict[str, Any],
) -> dict[str, Any]:
    x0, y0, x1, y1 = bounds
    count = len(labels)
    gap = 34
    width = (x1 - x0 - gap * (count - 1)) // count
    bins: list[dict[str, Any]] = []
    for index, value in enumerate(labels):
        left = x0 + index * (width + gap)
        box = [left, y0, left + width, y1]
        draw.rounded_rectangle(box, radius=28, fill=colours["white"], outline=colours["purple"], width=4)
        heading = fitted_text(
            draw,
            value,
            [left + 20, y0 + 12, left + width - 20, y0 + 72],
            max_size=typography["component_label_max"],
            min_size=typography["component_label_min"],
            colour=colours["navy"],
            bold=True,
            max_lines=1,
        )
        draw.line((left + 30, y0 + 90, left + width - 30, y0 + 90), fill=colours["guide"], width=3)
        bins.append({"bounds": box, "heading": heading})
    return {"type": "sort_bins", "bounds": bounds, "count": count, "bins": bins}


def sequence_slots(
    draw: ImageDraw.ImageDraw,
    bounds: list[int],
    count: int,
    colours: dict[str, str],
) -> dict[str, Any]:
    x0, y0, x1, y1 = bounds
    gap = 24
    width = (x1 - x0 - gap * (count - 1)) // count
    slots: list[dict[str, Any]] = []
    for index in range(count):
        left = x0 + index * (width + gap)
        box = [left, y0 + 24, left + width, y1 - 12]
        draw.rounded_rectangle(box, radius=24, fill=colours["white"], outline=colours["purple"], width=4)
        badge = [left + 16, y0 + 38, left + 74, y0 + 96]
        draw.ellipse(badge, fill=colours["purple"])
        fitted_text(
            draw,
            str(index + 1),
            badge,
            max_size=30,
            min_size=22,
            colour="white",
            bold=True,
            max_lines=1,
        )
        slots.append({"index": index + 1, "bounds": box, "badge": badge})
    return {"type": "sequence_slots", "bounds": bounds, "count": count, "slots": slots}


def response_box(
    draw: ImageDraw.ImageDraw,
    bounds: list[int],
    label_text: str,
    lines: int,
    colours: dict[str, str],
    typography: dict[str, Any],
) -> dict[str, Any]:
    draw.rounded_rectangle(bounds, radius=28, fill=colours["white"], outline=colours["purple"], width=4)
    label_render = label(
        draw,
        label_text,
        [bounds[0] + 24, bounds[1] + 12, bounds[2] - 24, bounds[1] + 70],
        colours,
        typography,
    )
    top = bounds[1] + 96
    bottom = bounds[3] - 28
    spacing = (bottom - top) / max(1, lines)
    guides: list[int] = []
    for index in range(lines):
        y = round(top + spacing * (index + 1))
        draw.line((bounds[0] + 36, y, bounds[2] - 36, y), fill=colours["guide"], width=3)
        guides.append(y)
    return {"type": "response_box", "bounds": bounds, "label": label_render, "guides": guides}


def speech_response(
    draw: ImageDraw.ImageDraw,
    bounds: list[int],
    label_text: str,
    colours: dict[str, str],
    typography: dict[str, Any],
) -> dict[str, Any]:
    bubble = [bounds[0] + 20, bounds[1] + 20, bounds[2] - 60, bounds[3] - 42]
    draw.rounded_rectangle(bubble, radius=48, fill=colours["white"], outline=colours["purple"], width=4)
    tail = [
        (bubble[2] - 110, bubble[3]),
        (bubble[2] - 36, bubble[3] + 65),
        (bubble[2] - 52, bubble[3] - 4),
    ]
    draw.polygon(tail, fill=colours["white"], outline=colours["purple"])
    label_render = fitted_text(
        draw,
        label_text,
        [bubble[0] + 36, bubble[1] + 20, bubble[2] - 36, bubble[3] - 20],
        max_size=typography["component_label_max"],
        min_size=typography["component_label_min"],
        colour=colours["navy"],
        bold=True,
        max_lines=2,
    )
    return {"type": "speech_response", "bounds": bounds, "bubble": bubble, "label": label_render}


def prediction_observation(
    draw: ImageDraw.ImageDraw,
    bounds: list[int],
    labels: list[str],
    colours: dict[str, str],
    typography: dict[str, Any],
) -> dict[str, Any]:
    return sort_bins(draw, bounds, labels, colours, typography) | {"type": "prediction_observation"}


def maze_path(
    draw: ImageDraw.ImageDraw,
    bounds: list[int],
    rows: int,
    columns: int,
    colours: dict[str, str],
    typography: dict[str, Any],
) -> dict[str, Any]:
    x0, y0, x1, y1 = bounds
    cell_w = (x1 - x0) / columns
    cell_h = (y1 - y0) / rows
    draw.rounded_rectangle(bounds, radius=24, fill=colours["white"], outline=colours["purple"], width=5)
    for column in range(1, columns):
        x = round(x0 + cell_w * column)
        draw.line((x, y0, x, y1), fill=colours["line"], width=3)
    for row in range(1, rows):
        y = round(y0 + cell_h * row)
        draw.line((x0, y, x1, y), fill=colours["line"], width=3)
    route: list[tuple[int, int]] = []
    for row in range(rows):
        sequence = range(columns) if row % 2 == 0 else range(columns - 1, -1, -1)
        for column in sequence:
            route.append((row, column))
    route_points = [
        (
            round(x0 + cell_w * (column + 0.5)),
            round(y0 + cell_h * (row + 0.5)),
        )
        for row, column in route
    ]
    draw.line(route_points, fill=colours["gold"], width=max(18, round(min(cell_w, cell_h) * 0.28)), joint="curve")
    start_bounds = [x0 + 12, y0 + 12, x0 + round(cell_w) - 12, y0 + round(cell_h) - 12]
    finish_bounds = [x1 - round(cell_w) + 12, y1 - round(cell_h) + 12, x1 - 12, y1 - 12]
    fitted_text(draw, "START", start_bounds, max_size=24, min_size=18, colour=colours["navy"], bold=True, max_lines=1)
    fitted_text(draw, "FINISH", finish_bounds, max_size=24, min_size=18, colour=colours["navy"], bold=True, max_lines=1)
    return {
        "type": "maze_path",
        "bounds": bounds,
        "rows": rows,
        "columns": columns,
        "route_points": len(route_points),
    }


def model_example_box(
    draw: ImageDraw.ImageDraw,
    bounds: list[int],
    label_text: str,
    colours: dict[str, str],
    typography: dict[str, Any],
) -> dict[str, Any]:
    draw.rounded_rectangle(bounds, radius=24, fill=colours["gold"], outline="#E1B12C", width=3)
    rendered = label(
        draw,
        label_text,
        [bounds[0] + 20, bounds[1] + 10, bounds[2] - 20, bounds[3] - 10],
        colours,
        typography,
    )
    return {"type": "model_example", "bounds": bounds, "label": rendered}


def component_weights(components: list[dict[str, Any]]) -> list[float]:
    weights = {
        "model_phrase": 0.72,
        "model_example": 0.72,
        "trace_line": 1.0,
        "copy_line": 1.0,
        "matching_anchors": 1.0,
        "creative_response_area": 1.8,
        "number_response_boxes": 1.0,
        "sort_bins": 1.35,
        "sequence_slots": 1.0,
        "choice_targets": 1.0,
        "maze_path": 2.3,
        "prediction_observation": 1.45,
        "response_box": 1.4,
        "speech_response": 1.0,
        "comparison_symbols": 0.8,
    }
    return [weights.get(str(item.get("type")), 1.0) for item in components]


def split_bounds(bounds: list[int], components: list[dict[str, Any]], gap: int = 18) -> list[list[int]]:
    x0, y0, x1, y1 = bounds
    weights = component_weights(components)
    usable = y1 - y0 - gap * (len(components) - 1)
    total = sum(weights)
    heights = [round(usable * weight / total) for weight in weights]
    heights[-1] += usable - sum(heights)
    result: list[list[int]] = []
    top = y0
    for height in heights:
        result.append([x0, top, x1, top + height])
        top += height + gap
    return result


def draw_deterministic_components(
    draw: ImageDraw.ImageDraw,
    components: list[dict[str, Any]],
    bounds: list[int],
    template: dict[str, Any],
) -> dict[str, Any]:
    colours = template["colours"]
    typography = template["typography"]
    worksheet = template["worksheet"]
    draw.rounded_rectangle(
        bounds,
        radius=worksheet["response_radius"],
        fill="#FCFAFF",
        outline=colours["soft_purple"],
        width=3,
    )
    inner = [bounds[0] + 28, bounds[1] + 24, bounds[2] - 28, bounds[3] - 24]
    component_bounds = split_bounds(inner, components)
    rendered: list[dict[str, Any]] = []
    for item, item_bounds in zip(components, component_bounds):
        component_type = str(item["type"])
        if component_type == "model_phrase":
            result = model_phrase(draw, item_bounds, str(item.get("text") or ""), colours, typography)
        elif component_type == "trace_line":
            result = writing_guides(
                draw,
                item_bounds,
                dotted=True,
                label_text=str(item.get("label") or "Trace"),
                colours=colours,
                typography=typography,
            )
        elif component_type == "copy_line":
            result = writing_guides(
                draw,
                item_bounds,
                dotted=False,
                label_text=str(item.get("label") or "Try it"),
                colours=colours,
                typography=typography,
            )
        elif component_type == "matching_anchors":
            result = matching_anchors(
                draw,
                item_bounds,
                int(item.get("count", 4)),
                colours,
                worksheet,
            )
        elif component_type == "creative_response_area":
            result = creative_response_area(
                draw,
                item_bounds,
                str(item.get("label") or "My work"),
                colours,
                typography,
            )
        elif component_type == "number_response_boxes":
            result = number_boxes(draw, item_bounds, int(item.get("count", 4)), colours)
        elif component_type == "sort_bins":
            labels = item.get("labels")
            if not isinstance(labels, list) or not labels:
                labels = [f"Group {index + 1}" for index in range(int(item.get("count", 2)))]
            result = sort_bins(draw, item_bounds, [str(value) for value in labels], colours, typography)
        elif component_type == "sequence_slots":
            result = sequence_slots(draw, item_bounds, int(item.get("count", 4)), colours)
        elif component_type == "choice_targets":
            result = choice_targets(
                draw,
                item_bounds,
                int(item.get("count", 4)),
                colours,
                worksheet,
            )
        elif component_type == "maze_path":
            result = maze_path(
                draw,
                item_bounds,
                int(item.get("rows", 7)),
                int(item.get("columns", 9)),
                colours,
                typography,
            )
        elif component_type == "prediction_observation":
            labels = item.get("labels") if isinstance(item.get("labels"), list) else ["I think", "I noticed"]
            result = prediction_observation(draw, item_bounds, [str(value) for value in labels], colours, typography)
        elif component_type == "response_box":
            result = response_box(
                draw,
                item_bounds,
                str(item.get("label") or "My response"),
                int(item.get("lines", 3)),
                colours,
                typography,
            )
        elif component_type == "speech_response":
            result = speech_response(
                draw,
                item_bounds,
                str(item.get("label") or "Say or tell"),
                colours,
                typography,
            )
        elif component_type == "model_example":
            result = model_example_box(
                draw,
                item_bounds,
                str(item.get("label") or "Look"),
                colours,
                typography,
            )
        elif component_type == "comparison_symbols":
            result = choice_targets(draw, item_bounds, 3, colours, worksheet)
            result["type"] = "comparison_symbols"
        else:
            raise ValueError(f"Unsupported deterministic component: {component_type}")
        rendered.append(result)
    return {
        "bounds": bounds,
        "component_count": len(rendered),
        "component_types": [item["type"] for item in rendered],
        "items": rendered,
    }


def adult_panel(
    draw: ImageDraw.ImageDraw,
    bounds: list[int],
    heading: str,
    body: str,
    fill: str,
    outline: str,
    template: dict[str, Any],
) -> dict[str, Any]:
    colours = template["colours"]
    typography = template["typography"]
    draw.rounded_rectangle(bounds, radius=32, fill=fill, outline=outline, width=4)
    heading_render = fitted_text(
        draw,
        heading,
        [bounds[0] + 28, bounds[1] + 18, bounds[2] - 28, bounds[1] + 92],
        max_size=typography["adult_heading"],
        min_size=28,
        colour=colours["navy"],
        bold=True,
        max_lines=1,
    )
    body_render = fitted_text(
        draw,
        body,
        [bounds[0] + 38, bounds[1] + 105, bounds[2] - 38, bounds[3] - 32],
        max_size=typography["adult_body_max"],
        min_size=typography["adult_body_min"],
        colour=colours["line"],
        align="left",
        max_lines=10,
    )
    return {"bounds": bounds, "heading": heading_render, "body": body_render}


def validate_geometry(template: dict[str, Any], layout: dict[str, Any]) -> dict[str, Any]:
    common = template["common_bounds"]
    illustration = layout["illustration"]
    response = layout["response"]
    overlap = not (
        illustration[2] <= response[0]
        or response[2] <= illustration[0]
        or illustration[3] <= response[1]
        or response[3] <= illustration[1]
    )
    if overlap:
        raise ValueError("Illustration and deterministic response areas overlap")
    adult_overlap = not (
        common["teacher_panel"][2] <= common["parent_panel"][0]
        or common["parent_panel"][2] <= common["teacher_panel"][0]
    )
    if adult_overlap:
        raise ValueError("Teacher and parent panels overlap")
    return {
        "illustration_response_overlap": False,
        "teacher_parent_overlap": False,
        "illustration_response_gap": response[1] - illustration[3],
    }


def compose(contract_path: Path, output: Path, evidence_output: Path) -> None:
    contract = load(contract_path)
    template = load(TEMPLATE_PATH)
    identity = contract["identity"]
    learning = contract["learning"]
    activity = contract["activity"]
    guidance = contract["guidance"]
    layout = template["layout_variants"].get(activity["layout_variant"])
    if not isinstance(layout, dict):
        raise ValueError(f"Unsupported layout variant: {activity['layout_variant']!r}")
    canvas_spec = template["canvas"]
    colours = template["colours"]
    typography = template["typography"]
    bounds = template["common_bounds"]
    canvas = Image.new("RGB", (canvas_spec["width"], canvas_spec["height"]), colours["background"])
    draw = ImageDraw.Draw(canvas)

    logo = Image.open(resolve(contract["assets"]["official_logo_path"])).convert("RGBA")
    logo.thumbnail((bounds["logo"][2] - bounds["logo"][0], bounds["logo"][3] - bounds["logo"][1]), Image.Resampling.LANCZOS)
    logo_x = bounds["logo"][0] + (bounds["logo"][2] - bounds["logo"][0] - logo.width) // 2
    logo_y = bounds["logo"][1] + (bounds["logo"][3] - bounds["logo"][1] - logo.height) // 2
    canvas.paste(logo, (logo_x, logo_y), logo)
    logo_render = {"rendered_bounds": [logo_x, logo_y, logo_x + logo.width, logo_y + logo.height]}

    book_title_render = brand_title(
        draw,
        identity["book_title_lines"],
        bounds["book_title"],
        colours,
        typography,
    )
    title_render = fitted_text(
        draw,
        identity["title"],
        bounds["page_title"],
        max_size=typography["page_title_max"],
        min_size=typography["page_title_min"],
        colour=colours["navy"],
        bold=True,
        max_lines=2,
    )

    draw.rounded_rectangle(bounds["objective"], radius=28, fill=colours["blue"], outline="#1768B3", width=4)
    objective_render = fitted_text(
        draw,
        f"Learning goal: {learning['objective']}",
        [bounds["objective"][0] + 34, bounds["objective"][1] + 12, bounds["objective"][2] - 34, bounds["objective"][3] - 12],
        max_size=typography["objective_max"],
        min_size=typography["objective_min"],
        colour=colours["navy"],
        bold=True,
        max_lines=3,
    )
    draw.rounded_rectangle(bounds["instruction"], radius=30, fill=colours["gold"], outline="#E1B12C", width=4)
    instruction_render = fitted_text(
        draw,
        learning["student_instruction"],
        [bounds["instruction"][0] + 34, bounds["instruction"][1] + 14, bounds["instruction"][2] - 34, bounds["instruction"][3] - 14],
        max_size=typography["instruction_max"],
        min_size=typography["instruction_min"],
        colour=colours["line"],
        bold=True,
        max_lines=3,
    )

    draw.rounded_rectangle(
        layout["illustration"],
        radius=template["illustration"]["frame_radius"],
        fill=template["illustration"]["frame_fill"],
        outline=template["illustration"]["frame_outline"],
        width=template["illustration"]["frame_border_width"],
    )
    illustration_render = paste_illustration(
        canvas,
        resolve(contract["assets"]["illustration_path"]),
        layout["illustration"],
        inset=layout["illustration_inset"],
        trim_near_white=template["illustration"]["trim_near_white"],
    )
    worksheet_render = draw_deterministic_components(
        draw,
        contract["deterministic_components"],
        layout["response"],
        template,
    )

    teacher_body = f"{guidance['teacher']['model']} Ask: {guidance['teacher']['question']}"
    teacher_render = adult_panel(
        draw,
        bounds["teacher_panel"],
        "TEACHER GUIDANCE",
        teacher_body,
        colours["green"],
        "#5F9D50",
        template,
    )
    parent_render = adult_panel(
        draw,
        bounds["parent_panel"],
        "PARENT PARTNERSHIP",
        guidance["parent_extension"],
        colours["pink"],
        "#D17A98",
        template,
    )
    page_number_render = None
    if identity["page_number_visible"] and identity["page_number"] > 0:
        page_number_render = fitted_text(
            draw,
            str(identity["page_number"]),
            bounds["page_number"],
            max_size=44,
            min_size=34,
            colour=colours["muted"],
            bold=True,
            max_lines=1,
        )

    geometry = validate_geometry(template, layout)
    if worksheet_render["component_count"] != contract["qa_requirements"]["component_count"]:
        raise ValueError("Rendered worksheet component count does not match the learning contract")
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, "PNG", dpi=(canvas_spec["dpi"], canvas_spec["dpi"]))
    evidence = {
        "engine": "BCube Publishing Engine Learning Pages V2",
        "contract_version": contract["contract_version"],
        "template_version": template["template_version"],
        "page_id": identity["page_id"],
        "layout_variant": activity["layout_variant"],
        "primary_activity": activity["primary"],
        "canvas": canvas_spec,
        "artifact": str(output),
        "artifact_sha256": sha256(output),
        "inputs": {
            "contract_sha256": sha256(contract_path),
            "illustration_sha256": sha256(resolve(contract["assets"]["illustration_path"])),
            "logo_sha256": sha256(resolve(contract["assets"]["official_logo_path"])),
        },
        "components": {
            "official_logo": logo_render,
            "book_title": book_title_render,
            "page_title": title_render,
            "objective": objective_render,
            "instruction": instruction_render,
            "illustration": illustration_render,
            "worksheet": worksheet_render,
            "teacher_panel": teacher_render,
            "parent_panel": parent_render,
            "page_number": page_number_render,
        },
        "measured_geometry": geometry,
        "component_count_gate": {
            "expected": contract["qa_requirements"]["component_count"],
            "actual": worksheet_render["component_count"],
            "pass": worksheet_render["component_count"] == contract["qa_requirements"]["component_count"],
        },
        "semantic_review": {
            "scene": contract["illustration"]["scene"],
            "focal_point": contract["illustration"]["focal_point"],
            "required_objects": contract["illustration"]["required_objects"],
            "forbidden_objects": contract["illustration"]["forbidden_objects"],
            "star_policy": contract["illustration"]["star_policy"],
            "human_review_required": True,
        },
        "qa": {
            "one_physical_page": True,
            "measured_geometry": True,
            "hard_coded_pass_flags": 0,
            "status": "REVIEW_CANDIDATE",
        },
    }
    evidence_output.parent.mkdir(parents=True, exist_ok=True)
    evidence_output.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "COMPOSED", "artifact": str(output), "evidence": str(evidence_output)}, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    args = parser.parse_args()
    compose(args.contract, args.output, args.evidence_output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"BCube learning-page composition FAIL: {exc}", file=__import__("sys").stderr)
        raise SystemExit(2)
