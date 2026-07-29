#!/usr/bin/env python3
"""Validate the curriculum-first Early Literacy Adventures LKG blueprint."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "curriculum/early-literacy-adventures/lkg/curriculum-first-p008-p043-v1.json"
MANIFEST = ROOT / "production-prompts/early-literacy-adventures/lkg/v4/release-manifest.json"


class ValidationError(RuntimeError):
    pass


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValidationError(f"{path} must contain a JSON object")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def page_number(page_id: str) -> int:
    match = re.search(r"-P(\d{3})$", page_id)
    if not match:
        raise ValidationError(f"Invalid page ID: {page_id}")
    return int(match.group(1))


def main() -> int:
    blueprint = load(BLUEPRINT)
    manifest = load(MANIFEST)
    pages = blueprint.get("pages")
    require(isinstance(pages, dict), "Blueprint pages must be an object")

    expected = {f"EL-LKG-V4-P{number:03d}" for number in range(8, 44)}
    require(set(pages) == expected, f"Blueprint scope mismatch: missing={sorted(expected - set(pages))}, extra={sorted(set(pages) - expected)}")

    manifest_pages = {entry["prompt_id"]: entry for entry in manifest["pages"]}
    required_fields = {
        "title", "objective", "instruction", "child_thinking", "model_example",
        "expected_response", "archetype", "mechanic", "render_kind",
        "illustration_assets", "renderer_controls", "teacher_cue", "validation_gates",
    }
    failures: list[str] = []
    for page_id, page in pages.items():
        missing = required_fields - set(page)
        if missing:
            failures.append(f"{page_id}: missing {sorted(missing)}")
            continue
        if manifest_pages[page_id]["title"] != page["title"]:
            failures.append(f"{page_id}: title differs from V4 manifest")
        if page_number(page_id) != manifest_pages[page_id]["physical"]:
            failures.append(f"{page_id}: physical page mismatch")
        for field in ("objective", "instruction", "child_thinking", "expected_response", "archetype", "mechanic", "render_kind", "teacher_cue"):
            if not isinstance(page[field], str) or not page[field].strip():
                failures.append(f"{page_id}: {field} is empty")
        if not isinstance(page["model_example"], dict) or not page["model_example"]:
            failures.append(f"{page_id}: model_example is required")
        if not isinstance(page["renderer_controls"], dict) or not page["renderer_controls"]:
            failures.append(f"{page_id}: renderer_controls are required")
        if not isinstance(page["illustration_assets"], dict):
            failures.append(f"{page_id}: illustration_assets must be an object")
        if not isinstance(page["validation_gates"], list) or len(page["validation_gates"]) < 3:
            failures.append(f"{page_id}: at least three validation gates are required")
        controls = page["renderer_controls"]
        if controls.get("require_derangement") is True:
            left = controls.get("left")
            right = controls.get("right")
            correct_pairs = controls.get("correct_pairs")
            if not isinstance(left, list) or not isinstance(right, list) or len(left) != len(right):
                failures.append(f"{page_id}: derangement requires equal left and right lists")
            elif not isinstance(correct_pairs, list):
                failures.append(f"{page_id}: derangement requires correct_pairs")
            else:
                pair_map = {pair[0]: pair[1] for pair in correct_pairs if isinstance(pair, list) and len(pair) == 2}
                aligned = [index for index, value in enumerate(left) if pair_map.get(value) == right[index]]
                if aligned:
                    failures.append(f"{page_id}: right column reveals answers at row(s) {aligned}")

    rules = blueprint.get("global_rules", {})
    for key in (
        "one_primary_child_action", "visible_completed_example", "independent_answers_unmarked",
        "every_response_area_has_a_named_action", "worksheet_mechanics_are_deterministic",
    ):
        require(rules.get(key) is True, f"Global rule {key} must be true")
    for key in ("parent_panel", "home_connection", "generic_response_panel", "allow_fallback"):
        require(rules.get(key) is False, f"Global rule {key} must be false")

    if failures:
        raise ValidationError("\n".join(failures))

    summary = {
        "book": blueprint["book"],
        "scope": blueprint["scope"],
        "validated_pages": len(pages),
        "first_page": min(pages, key=page_number),
        "last_page": max(pages, key=page_number),
        "external_art_pages": sum(bool(page["illustration_assets"]) for page in pages.values()),
        "deterministic_only_pages": sum(not page["illustration_assets"] for page in pages.values()),
        "status": "PASS",
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"Early Literacy curriculum validation FAIL: {exc}")
        raise SystemExit(2)
