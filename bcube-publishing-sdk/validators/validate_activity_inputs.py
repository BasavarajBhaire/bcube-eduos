#!/usr/bin/env python3
"""Validate BCube Phase 2 activity-page data before composition."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "bcube-publishing-sdk/templates/activity-page-v1.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def resolve(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def image_info(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing {label}: {path}")
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        if image.width < 600 or image.height < 600:
            raise ValueError(f"{label} is too small: {image.width}x{image.height}")
        return {"path": str(path), "size": [image.width, image.height], "mode": image.mode}


def validate(data_path: Path) -> dict[str, Any]:
    data = load(data_path)
    template = load(TEMPLATE)
    required = ["page_id", "book_title", "level", "age", "page_number", "activity_type", "title",
                "learning_objective", "student_instruction", "teacher_prompt", "parent_prompt",
                "illustration_path", "official_logo_path", "official_star_path"]
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"Missing activity page data: {missing}")
    if data["activity_type"] not in template["supported_activity_types"]:
        raise ValueError(f"Unsupported activity_type {data['activity_type']!r}")
    if not isinstance(data["page_number"], int) or data["page_number"] < 1:
        raise ValueError("page_number must be a positive integer")
    rules = template["rules"]
    limits = {
        "title": rules["max_title_chars"],
        "learning_objective": rules["max_objective_chars"],
        "student_instruction": rules["max_instruction_chars"],
        "teacher_prompt": rules["max_teacher_chars"],
        "parent_prompt": rules["max_parent_chars"],
    }
    overflow = {key: {"length": len(str(data[key])), "limit": limit}
                for key, limit in limits.items() if len(str(data[key])) > limit}
    if overflow:
        raise ValueError(f"Text exceeds activity template limits: {overflow}")
    return {
        "status": "PASS",
        "page_id": data["page_id"],
        "activity_type": data["activity_type"],
        "illustration": image_info(resolve(data["illustration_path"]), "illustration"),
        "official_logo": image_info(resolve(data["official_logo_path"]), "official logo"),
        "official_star": image_info(resolve(data["official_star_path"]), "official Star"),
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
