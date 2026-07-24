#!/usr/bin/env python3
"""Validate Contents, Welcome, and Meet Star input data before composition."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = ROOT / "bcube-publishing-sdk/templates/special-page-v1.json"
PLACEHOLDER_PHRASES = (
    "use the page for its stated front-matter purpose",
    "no additional worksheet task",
    "introduce the page purpose clearly",
    "use this page for orientation only",
    "one dominant learning scene",
    "one dominant focus for",
    "what can you show or tell about welcome",
    "what can you show or tell about meet star",
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def resolve(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def image_info(value: str, label: str, minimum_side: int) -> dict[str, Any]:
    path = resolve(value)
    if not path.is_file():
        raise FileNotFoundError(f"Missing {label}: {path}")
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        if min(image.width, image.height) < minimum_side:
            raise ValueError(f"{label} is too small: {image.width}x{image.height}")
        return {"path": str(path), "size": [image.width, image.height], "mode": image.mode}


def validate_locked_copy(data: dict[str, Any], page_type: str) -> None:
    """Reject production placeholders on child-facing Welcome and Meet Star pages."""
    if page_type not in {"welcome", "meet_star"}:
        return
    fields = ["page_title", "message"]
    if page_type == "meet_star":
        fields.append("purpose")
    combined = " ".join(str(data.get(field) or "") for field in fields).casefold()
    for phrase in PLACEHOLDER_PHRASES:
        if phrase in combined:
            raise ValueError(f"{page_type} contains prohibited placeholder copy: {phrase!r}")


def validate(data_path: Path) -> dict[str, Any]:
    data = load(data_path)
    template = load(TEMPLATE_PATH)
    page_type = data.get("page_type")
    if page_type not in {"contents", "welcome", "meet_star"}:
        raise ValueError(f"Unsupported special page type: {page_type!r}")
    required = {
        "page_id", "page_type", "physical_page", "book_title", "book_title_lines",
        "page_title", "level", "tagline", "core_pillars", "footer_keywords",
        "official_logo_path",
    }
    required.update({
        "contents": {"entries"},
        "welcome": {"page_number", "message", "illustration_path"},
        "meet_star": {"page_number", "message", "purpose", "official_star_path"},
    }[page_type])
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"Missing {page_type} page data: {missing}")
    prohibited = sorted({
        "teacher_prompt", "parent_prompt", "series", "age_badge", "learning_goal",
        "activity_banner",
    }.intersection(data))
    if prohibited:
        raise ValueError(f"{page_type} page contains prohibited components: {prohibited}")
    if not isinstance(data["book_title_lines"], list) or not data["book_title_lines"]:
        raise ValueError("book_title_lines must be a non-empty list")
    if not isinstance(data["core_pillars"], list) or len(data["core_pillars"]) != 5:
        raise ValueError("Exactly five core pillars are required")
    validate_locked_copy(data, str(page_type))
    assets = {"official_logo": image_info(data["official_logo_path"], "official logo", 128)}
    visible_page_number = False
    if page_type == "contents":
        if data["physical_page"] not in {4, 5}:
            raise ValueError("Contents must be physical page 4 or 5")
        entries = data["entries"]
        if not isinstance(entries, list) or len(entries) != template["contents"]["entries_per_page"]:
            raise ValueError("Each Contents page must contain exactly 19 entries")
        expected = list(range(5, 24)) if data["physical_page"] == 4 else list(range(24, 43))
        actual = [entry.get("page") for entry in entries if isinstance(entry, dict)]
        if actual != expected:
            raise ValueError(f"Contents page sequence mismatch: expected {expected}, got {actual}")
        if any(not str(entry.get("module") or "").strip() for entry in entries):
            raise ValueError("Every Contents entry must resolve a canonical module")
    elif page_type == "welcome":
        if (data["physical_page"], data["page_number"]) != (6, 5):
            raise ValueError("Welcome must be physical page 6 and visibly numbered 5")
        assets["illustration"] = image_info(data["illustration_path"], "Welcome illustration", 600)
        visible_page_number = True
    else:
        if (data["physical_page"], data["page_number"]) != (7, 6):
            raise ValueError("Meet Star must be physical page 7 and visibly numbered 6")
        assets["official_star"] = image_info(data["official_star_path"], "official Star", 256)
        visible_page_number = True
    return {
        "status": "PASS",
        "page_id": data["page_id"],
        "page_type": page_type,
        "header_type": template["rules"]["header_type"],
        "visible_page_number": visible_page_number,
        "content_source": data.get("content_source"),
        "content_policy_version": data.get("content_policy_version"),
        "assets": assets,
        "prohibited_component_counts": {
            "series_banner": 0,
            "age_badge": 0,
            "teacher_panel": 0,
            "parent_panel": 0,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate(args.data)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError) as exc:
        print(f"BCube special-page validation FAIL: {exc}", file=__import__("sys").stderr)
        raise SystemExit(2)
