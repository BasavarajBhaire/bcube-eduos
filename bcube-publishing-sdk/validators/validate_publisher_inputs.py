#!/usr/bin/env python3
"""Validate BCube Publisher/Copyright page data before composition."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "bcube-publishing-sdk/templates/publisher-page-v1.json"


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
        "page_title", "level", "publisher", "publication_code", "document_id",
        "copyright_notice", "official_logo_path",
    }
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"Missing Publisher-page data: {missing}")
    if data["page_type"] != "publisher":
        raise ValueError("Publisher-page data must use page_type 'publisher'")
    if data["physical_page"] != template["rules"]["physical_page"]:
        raise ValueError("Publisher/Copyright must be physical page 3")
    if data["page_title"] != "Publication & Copyright":
        raise ValueError("Publisher page_title must be exactly 'Publication & Copyright'")

    prohibited_fields = {
        "series", "series_banner", "age", "age_badge", "page_number",
        "visible_page_number", "illustration", "illustration_path",
        "illustration_layer", "official_star", "official_star_path",
        "learning_goal", "objective", "instruction", "activity_type",
        "teacher_prompt", "teacher_panel", "parent_prompt", "parent_panel",
        "core_pillars", "isbn",
    }
    present = sorted(field for field in prohibited_fields if field in data)
    if present:
        raise ValueError(f"Publisher-page data contains prohibited components: {present}")

    title_lines = data["book_title_lines"]
    if not isinstance(title_lines, list) or not 1 <= len(title_lines) <= 2:
        raise ValueError("book_title_lines must contain one or two lines")
    if any(not isinstance(line, str) or not line.strip() for line in title_lines):
        raise ValueError("book_title_lines cannot contain blank values")

    publisher = data["publisher"]
    required_publisher = {
        "name", "address", "email", "website", "phone",
        "copyright_year", "production_status", "country_of_print",
    }
    if not isinstance(publisher, dict):
        raise ValueError("publisher must be an object")
    missing_publisher = sorted(required_publisher - set(publisher))
    if missing_publisher:
        raise ValueError(f"Missing publisher details: {missing_publisher}")
    if publisher["phone"] != "+91 79750 59945":
        raise ValueError("Publisher phone must be the approved +91 79750 59945")
    if publisher["production_status"] not in {
        "DRAFT", "DESIGN REVIEW", "PILOT", "PRINT PROOF", "PRINT APPROVED"
    }:
        raise ValueError("Publisher production_status is not an approved pre-print maturity label")

    publication_code = str(data["publication_code"])
    if not re.fullmatch(r"BCUBE-(NUR|LKG|UKG)-[A-Z]{2}-\d{3}", publication_code):
        raise ValueError(f"Invalid BCube Publication Code: {publication_code}")
    document_id = str(data["document_id"])
    if not re.fullmatch(r"[A-Z]{2}-(NURSERY|LKG|UKG)-PILOT-2026", document_id):
        raise ValueError(f"Invalid Document ID: {document_id}")
    if "ISBN" in json.dumps(data, ensure_ascii=False).upper():
        raise ValueError("Do not display ISBN until an official ISBN is assigned")

    return {
        "status": "PASS",
        "page_id": data["page_id"],
        "page_type": "publisher",
        "header_type": template["header_type"],
        "visible_page_number": False,
        "illustration_required": False,
        "component_counts": {
            "official_logo": 1,
            "book_title": 1,
            "page_title": 1,
            "publisher_details": 1,
            "publication_code": 1,
            "document_id": 1,
            "copyright_notice": 1,
            "illustration_layer": 0,
            "teacher_panel": 0,
            "parent_panel": 0,
            "official_star": 0,
        },
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
