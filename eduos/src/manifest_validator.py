#!/usr/bin/env python3
"""BCube EduOS manifest validator.

Validates critical deterministic production constraints without external packages.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_TOP_LEVEL = {"manifest_version", "identity", "page", "assets", "composition", "qa"}
VALID_LEVELS = {"Nursery", "LKG", "UKG"}
VALID_PAGE_TYPES = {"cover", "lesson", "activity", "review", "certificate", "copyright"}
OFFICIAL_LOGO = "BCube_Gold_Production_v4/OFFICIAL_ASSETS/Official_BCube_Logo.png"


def validate_manifest(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_TOP_LEVEL - data.keys()
    if missing:
        errors.append(f"Missing top-level fields: {sorted(missing)}")
        return errors

    if data.get("manifest_version") != "1.0":
        errors.append("manifest_version must be 1.0")

    identity = data.get("identity", {})
    for field in ("book", "level", "prompt_id", "source_markdown", "source_json"):
        if not identity.get(field):
            errors.append(f"identity.{field} is required")
    if identity.get("level") not in VALID_LEVELS:
        errors.append("identity.level must be Nursery, LKG, or UKG")

    page = data.get("page", {})
    if page.get("type") not in VALID_PAGE_TYPES:
        errors.append("page.type is invalid")
    if not page.get("title"):
        errors.append("page.title is required")
    if not isinstance(page.get("visible_text"), list):
        errors.append("page.visible_text must be a list")
    if page.get("type") == "cover" and page.get("show_page_number", False):
        errors.append("cover pages must not show a page number")

    assets = data.get("assets", {})
    if assets.get("logo") != OFFICIAL_LOGO:
        errors.append("assets.logo must reference the exact official BCube logo")
    if not assets.get("illustration"):
        errors.append("assets.illustration is required")

    composition = data.get("composition", {})
    if composition.get("width_px") != 2480 or composition.get("height_px") != 3508:
        errors.append("composition must be A4 portrait at 2480 x 3508 px")
    if composition.get("dpi") != 300:
        errors.append("composition.dpi must be 300")

    qa = data.get("qa", {})
    if qa.get("minimum_score", 0) < 95:
        errors.append("qa.minimum_score must be at least 95")
    if not qa.get("reject_on"):
        errors.append("qa.reject_on must contain critical rejection conditions")

    return errors


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("Manifest root must be a JSON object")
    return value


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: manifest_validator.py <manifest.json>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        errors = validate_manifest(load_manifest(path))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID: manifest satisfies BCube EduOS v1.0 critical constraints")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
