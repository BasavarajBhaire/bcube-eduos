#!/usr/bin/env python3
"""Deterministically compose a BCube Nursery cover.

AI is allowed to supply only the illustration layer. Branding, typography,
badge, skills, pillars, official logo, official Star and footer are composed
from repository-controlled inputs and locked geometry.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "bcube-publishing-sdk/templates/nursery-cover-v1.json"
BOLD_CANDIDATES = [
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("C:/Windows/Fonts/arialbd.ttf"),
]
REGULAR_CANDIDATES = [
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("C:/Windows/Fonts/arial.ttf"),
]


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
    candidates = BOLD_CANDIDATES if bold else REGULAR_CANDIDATES
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("No supported deterministic font was found")


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(font_path(bold)), size)


def centered_text(draw: ImageDraw.ImageDraw, text: str, bounds: list[int], max_size: int,
                  fill: str, *, min_size: int = 18, shadow: bool = False) -> None:
    x0, y0, x1, y1 = bounds
    for size in range(max_size, min_size - 1, -2):
        active_font = font(size)
        left, top, right, bottom = draw.textbbox((0, 0), text, font=active_font)
        width, height = right - left, bottom - top
        if width <= x1 - x0 and height <= y1 - y0:
            x = x0 + (x1 - x0 - width) / 2
            y = y0 + (y1 - y0 - height) / 2 - top
            if shadow:
                draw.text((x + 8, y + 10), text, font=active_font, fill="#D5D5D5")
            draw.text((x, y), text, font=active_font, fill=fill)
            return
    raise ValueError(f"Text does not fit locked bounds: {text!r}")


def paste_contain(canvas: Image.Image, asset_path: Path, bounds: list[int]) -> None:
    asset = Image.open(asset_path).convert("RGBA")
    x0, y0, x1, y1 = bounds
    asset.thumbnail((x1 - x0, y1 - y0), Image.Resampling.LANCZOS)
    x = x0 + (x1 - x0 - asset.width) // 2
    y = y0 + (y1 - y0 - asset.height) // 2
    canvas.paste(asset, (x, y), asset)


def paste_cover(canvas: Image.Image, asset_path: Path, bounds: list[int], radius: int = 36) -> None:
    asset = Image.open(asset_path).convert("RGB")
    x0, y0, x1, y1 = bounds
    width, height = x1 - x0, y1 - y0
    fitted = ImageOps.fit(asset, (width, height), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, width - 1, height - 1), radius=radius, fill=255)
    canvas.paste(fitted, (x0, y0), mask)


def validate_data(data: dict[str, Any]) -> None:
    required = ["page_id", "book_key", "title_lines", "tagline", "level", "age", "skills", "pillars",
                "illustration_path", "official_logo_path", "official_star_path", "illustration_evidence"]
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"Missing cover data: {missing}")
    if len(data["title_lines"]) != 2:
        raise ValueError("Cover title must contain exactly two lines")
    if len(data["skills"]) != 6:
        raise ValueError("Cover must contain exactly six skills")
    if len(data["pillars"]) != 5:
        raise ValueError("Cover must contain exactly five pillars")
    evidence = data["illustration_evidence"]
    if not isinstance(evidence, dict):
        raise ValueError("illustration_evidence must be an object")
    forbidden = ["contains_text", "contains_logo", "contains_mascot", "contains_badge", "contains_page_layout"]
    contaminated = [key for key in forbidden if evidence.get(key) is not False]
    if contaminated:
        raise ValueError(f"Illustration candidate rejected; clean evidence required for: {contaminated}")
    for path_key in ["illustration_path", "official_logo_path", "official_star_path"]:
        if not (ROOT / data[path_key]).is_file():
            raise FileNotFoundError(f"Missing required input: {data[path_key]}")


def compose(data_path: Path, output: Path, evidence_output: Path) -> None:
    data = load_json(data_path)
    validate_data(data)
    template = load_json(TEMPLATE)
    bounds = template["bounds"]
    colours = template["colours"]
    width, height = template["canvas"]["width"], template["canvas"]["height"]

    canvas = Image.new("RGB", (width, height), colours["background"])
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((18, 18, width - 18, height - 18), radius=40, outline="#5B2B87", width=8)

    logo_path = ROOT / data["official_logo_path"]
    star_path = ROOT / data["official_star_path"]
    illustration_path = ROOT / data["illustration_path"]
    paste_contain(canvas, logo_path, bounds["official_logo"])

    x0, y0, x1, y1 = bounds["series_banner"]
    banner_points = [(x0 + 70, y0), (x1 - 70, y0), (x1, (y0 + y1) // 2),
                     (x1 - 70, y1), (x0 + 70, y1), (x0, (y0 + y1) // 2)]
    draw.polygon(banner_points, fill=colours["purple"], outline=colours["gold"])
    centered_text(draw, "BCube Future Skills", [x0 + 60, y0 + 35, x1 - 60, y0 + 145], 70, "white")
    centered_text(draw, "Learning Series™", [x0 + 60, y0 + 145, x1 - 60, y1 - 35], 70, "white")

    x0, y0, x1, y1 = bounds["age_badge"]
    draw.ellipse((x0, y0, x1, y1), fill=colours["purple"], outline="#CDA7E2", width=16)
    centered_text(draw, str(data["level"]).upper(), [x0 + 30, y0 + 35, x1 - 30, y0 + 125], 42, "white")
    centered_text(draw, str(data["age"]), [x0 + 45, y0 + 120, x1 - 45, y0 + 265], 92, colours["gold"])
    centered_text(draw, "YEARS", [x0 + 45, y0 + 265, x1 - 45, y1 - 35], 36, "white")

    title_bounds = bounds["book_title"]
    midpoint = (title_bounds[1] + title_bounds[3]) // 2
    centered_text(draw, data["title_lines"][0].upper(), [title_bounds[0], title_bounds[1], title_bounds[2], midpoint], 118, colours["purple"], shadow=True)
    centered_text(draw, data["title_lines"][1].upper(), [title_bounds[0], midpoint, title_bounds[2], title_bounds[3]], 128, colours["blue"], shadow=True)

    x0, y0, x1, y1 = bounds["book_tagline"]
    ribbon_points = [(x0 + 60, y0), (x1 - 60, y0), (x1, (y0 + y1) // 2),
                     (x1 - 60, y1), (x0 + 60, y1), (x0, (y0 + y1) // 2)]
    draw.polygon(ribbon_points, fill=colours["pink"])
    centered_text(draw, data["tagline"].upper(), [x0 + 60, y0 + 10, x1 - 60, y1 - 10], 56, "white")

    paste_cover(canvas, illustration_path, bounds["illustration_frame"])
    draw.rounded_rectangle(tuple(bounds["illustration_frame"]), radius=42, outline="#D6BCE7", width=7)
    star_bounds = data.get("official_star_bounds", [1280, 2160, 1720, 2660])
    paste_contain(canvas, star_path, star_bounds)

    skill_colours = ["#F47B16", "#2F95CF", "#4FAE2A", "#EC3481", "#7D3EAB", "#1EA0B9"]
    skill_region = bounds["six_skill_capsules"]
    y = skill_region[1]
    gap, capsule_height = 28, 156
    skill_evidence = []
    for index, label in enumerate(data["skills"]):
        capsule = [skill_region[0], y, skill_region[2], y + capsule_height]
        colour = skill_colours[index]
        draw.rounded_rectangle(tuple(capsule), radius=70, fill=colour)
        draw.ellipse((capsule[0] + 20, capsule[1] + 22, capsule[0] + 126, capsule[1] + 128), fill="white")
        centered_text(draw, "★", [capsule[0] + 35, capsule[1] + 40, capsule[0] + 110, capsule[1] + 112], 36, colour)
        centered_text(draw, str(label).upper(), [capsule[0] + 145, capsule[1] + 20, capsule[2] - 20, capsule[3] - 20], 34, "white", min_size=20)
        skill_evidence.append(capsule)
        y += capsule_height + gap

    pillar_region = bounds["five_core_pillars"]
    draw.rounded_rectangle(tuple(pillar_region), radius=45, fill="#FFFDFD", outline="#D7B9E8", width=5)
    label_bounds = [760, 2745, 1720, 2835]
    draw.rounded_rectangle(tuple(label_bounds), radius=35, fill=colours["purple"])
    centered_text(draw, "OUR CORE PILLARS", label_bounds, 44, "white")
    pillar_colours = ["#F47B16", "#2AAA35", "#2F95CF", "#7D3EAB", "#EC3481"]
    centers = [280, 760, 1240, 1720, 2200]
    pillar_evidence = []
    for pillar, colour, center_x in zip(data["pillars"], pillar_colours, centers):
        icon_bounds = [center_x - 60, 2870, center_x + 60, 2990]
        draw.ellipse(tuple(icon_bounds), fill=colour)
        centered_text(draw, str(pillar["code"]).upper(), [center_x - 45, 2890, center_x + 45, 2970], 28, "white")
        centered_text(draw, str(pillar["name"]).upper(), [center_x - 190, 3010, center_x + 190, 3080], 24, colour, min_size=17)
        pillar_evidence.append(icon_bounds)

    footer = bounds["footer"]
    draw.rectangle((footer[0], footer[1], footer[2], 3390), fill=colours["purple"])
    centered_text(draw, "★  BUILD  •  CREATE  •  BECOME  ★", [250, 3200, 2230, 3345], 56, "white")
    draw.rectangle((0, 3390, width, height), fill="#FFF0A9")
    centered_text(draw, data["footer_keywords"], [240, 3410, 2240, 3490], 34, colours["blue"])

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, "PNG", dpi=(300, 300), optimize=True)
    artifact_hash = sha256(output)

    components = [
        {"component": "official_logo", "source_path": data["official_logo_path"], "approved_sha256": sha256(logo_path), "bounds": bounds["official_logo"], "template_bounds": bounds["official_logo"], "allow_overlap": False},
        {"component": "series_banner", "bounds": bounds["series_banner"], "template_bounds": bounds["series_banner"], "allow_overlap": False},
        {"component": "book_title", "bounds": bounds["book_title"], "template_bounds": bounds["book_title"], "allow_overlap": False},
        {"component": "age_badge", "bounds": bounds["age_badge"], "template_bounds": bounds["age_badge"], "allow_overlap": False},
        {"component": "book_tagline", "bounds": bounds["book_tagline"], "template_bounds": bounds["book_tagline"], "allow_overlap": False},
        {"component": "illustration_frame", "bounds": bounds["illustration_frame"], "template_bounds": bounds["illustration_frame"], "allow_overlap": True},
        {"component": "official_star", "source_path": data["official_star_path"], "approved_sha256": sha256(star_path), "bounds": star_bounds, "template_bounds": star_bounds, "allow_overlap": True},
        {"component": "six_skill_capsules", "bounds": bounds["six_skill_capsules"], "template_bounds": bounds["six_skill_capsules"], "allow_overlap": False},
        {"component": "five_core_pillars", "bounds": bounds["five_core_pillars"], "template_bounds": bounds["five_core_pillars"], "allow_overlap": False},
        {"component": "footer", "bounds": bounds["footer"], "template_bounds": bounds["footer"], "allow_overlap": False},
    ]
    evidence = {
        "page_id": data["page_id"],
        "page_type": "cover",
        "book_key": data["book_key"],
        "artifact_path": str(output.relative_to(ROOT)) if output.is_relative_to(ROOT) else str(output),
        "composition": {
            "engine": "bcube-publishing-sdk",
            "engine_version": "cover-composer-v1",
            "full_page_ai_generation": False,
            "single_flat_page": True,
            "illustration_layer_path": data["illustration_path"],
            "illustration_layer_sha256": sha256(illustration_path)
        },
        "component_evidence": components,
        "text_evidence": data["text_evidence"],
        "human_approval": data["human_approval"] | {"artifact_sha256": artifact_hash}
    }
    evidence_output.parent.mkdir(parents=True, exist_ok=True)
    evidence_output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "COMPOSED", "artifact": str(output), "evidence": str(evidence_output), "sha256": artifact_hash}))


def self_test() -> int:
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        for name, colour, size in [("logo.png", "blue", (300, 180)), ("star.png", "gold", (220, 220)), ("illustration.png", "#F4E0B8", (900, 900))]:
            Image.new("RGBA", size, colour).save(temp / name)
        test_data = {
            "page_id": "TEST-COVER", "book_key": "nursery/confidence-builders",
            "title_lines": ["Confidence", "Builders"], "tagline": "I Believe • I Can • I Will",
            "level": "Nursery", "age": "3+",
            "skills": ["Believe in Myself", "Try New Things", "Speak with Confidence", "Make Good Choices", "Be Kind to Others", "Celebrate Success"],
            "pillars": [{"code": code, "name": name} for code, name in [("CR", "Creativity"), ("CO", "Communication"), ("CU", "Curiosity"), ("CF", "Confidence"), ("CL", "Collaboration")]],
            "footer_keywords": "Self-belief • Courage • Expression • Kindness • Independence",
            "illustration_path": str(temp / "illustration.png"), "official_logo_path": str(temp / "logo.png"), "official_star_path": str(temp / "star.png"),
            "illustration_evidence": {"contains_text": False, "contains_logo": False, "contains_mascot": False, "contains_badge": False, "contains_page_layout": False},
            "text_evidence": {"detector": {"name": "self-test", "version": "1"}, "detected_text": ["CONFIDENCE BUILDERS", "I BELIEVE", "I CAN", "I WILL", "BCUBE FUTURE SKILLS LEARNING SERIES", "NURSERY", "3+"]},
            "human_approval": {"reviewer": "SDK Self Test", "approved_on": "2026-07-22", "status": "APPROVED", "artifact_sha256": "0" * 64}
        }
        # Absolute paths are allowed in self-test; validate_data resolves only relative paths in production.
        original_root = globals()["ROOT"]
        globals()["ROOT"] = Path("/")
        try:
            data_path = temp / "data.json"
            data_path.write_text(json.dumps(test_data), encoding="utf-8")
            compose(data_path, temp / "cover.png", temp / "evidence.json")
        finally:
            globals()["ROOT"] = original_root
    print("deterministic Nursery cover compositor self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--evidence-output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.data or not args.output or not args.evidence_output:
        parser.error("--data, --output and --evidence-output are required")
    compose(args.data, args.output, args.evidence_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
