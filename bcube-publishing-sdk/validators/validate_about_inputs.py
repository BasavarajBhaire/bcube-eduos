#!/usr/bin/env python3
"""Validate BCube About-page data before deterministic composition."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "bcube-publishing-sdk/templates/about-page-v1.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def resolve(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def image_info(path: Path, label: str, minimum_side: int) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing {label}: {path}")
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        if min(image.width, image.height) < minimum_side:
            raise ValueError(
                f"{label} is too small: {image.width}x{image.height}; "
                f"minimum side is {minimum_side}px"
            )
        return {"path": str(path), "size": [image.width, image.height], "mode": image.mode}


def validate(data_path: Path) -> dict[str, Any]:
    data = load(data_path)
    template = load(TEMPLATE)
    required = {
        "page_id", "page_type", "physical_page", "book_title", "book_title_lines",
        "page_title", "learning_objective", "overview", "learning_outcomes",
        "core_pillars", "footer_keywords", "illustration_path", "official_logo_path",
    }
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"Missing About-page data: {missing}")
    if data["page_type"] != "about":
        raise ValueError("About-page data must use page_type 'about'")
    if data["physical_page"] != 2:
        raise ValueError("About This Book must be physical page 2")
    if data["page_title"] != "About This Book":
        raise ValueError("About page_title must be exactly 'About This Book'")

    prohibited_fields = {
        "series", "series_banner", "age_badge", "page_number", "visible_page_number",
        "teacher_prompt", "teacher_panel", "parent_prompt", "parent_panel",
        "official_star_path", "official_star",
    }
    present = sorted(field for field in prohibited_fields if field in data)
    if present:
        raise ValueError(f"About-page data contains prohibited components: {present}")

    title_lines = data["book_title_lines"]
    if not isinstance(title_lines, list) or not 1 <= len(title_lines) <= 2:
        raise ValueError("book_title_lines must contain one or two lines")
    if any(not isinstance(line, str) or not line.strip() for line in title_lines):
        raise ValueError("book_title_lines cannot contain blank values")
    canonical_title = " ".join(line.strip() for line in title_lines)
    if data["book_title"] != canonical_title:
        raise ValueError("book_title must equal the registered title segments joined on one line")

    rules = template["rules"]
    limits = {
        "learning_objective": rules["max_objective_chars"],
        "overview": rules["max_instruction_chars"],
    }
    overflow = {
        key: {"length": len(str(data[key])), "limit": limit}
        for key, limit in limits.items()
        if len(str(data[key])) > limit
    }
    if overflow:
        raise ValueError(f"Text exceeds About-page template limits: {overflow}")

    outcomes = data["learning_outcomes"]
    if not isinstance(outcomes, list) or len(outcomes) != rules["learning_outcome_count"]:
        raise ValueError("About page must contain exactly six learning outcomes")
    pillars = data["core_pillars"]
    if not isinstance(pillars, list) or len(pillars) != rules["core_pillar_count"]:
        raise ValueError("About page must contain exactly five core pillars")
    for label, values in (("learning outcome", outcomes), ("core pillar", pillars)):
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError(f"Every {label} must contain visible text")

    return {
        "status": "PASS",
        "page_id": data["page_id"],
        "page_type": "about",
        "header_type": template["header_type"],
        "visible_page_number": False,
        "single_line_book_title": template["rules"]["single_line_book_title"],
        "component_counts": {
            "official_logo": 1,
            "book_title": 1,
            "page_title": 1,
            "illustration_frame": 1,
            "learning_outcomes": len(outcomes),
            "core_pillars": len(pillars),
            "teacher_panel": 0,
            "parent_panel": 0,
            "official_star": 0,
        },
        "illustration": image_info(resolve(data["illustration_path"]), "illustration", 600),
        "official_logo": image_info(resolve(data["official_logo_path"]), "official logo", 128),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate(args.data)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
