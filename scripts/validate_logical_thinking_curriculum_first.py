#!/usr/bin/env python3
"""Validate the Logical Thinking Adventures LKG curriculum-first package."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "curriculum/logical-thinking-adventures/lkg/curriculum-first-p008-p043-v1.json"
MANIFEST = ROOT / "production-prompts/logical-thinking-adventures/lkg/v4/release-manifest.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return value


def page_number(page_id: str) -> int:
    match = re.search(r"-P(\d{3})$", page_id)
    if not match:
        raise RuntimeError(f"Invalid page ID: {page_id}")
    return int(match.group(1))


def main() -> int:
    blueprint, manifest = load(BLUEPRINT), load(MANIFEST)
    pages = blueprint["pages"]
    expected = {f"LT-LKG-V4-P{number:03d}" for number in range(8, 44)}
    failures: list[str] = []
    if set(pages) != expected:
        failures.append(f"scope mismatch: missing={sorted(expected-set(pages))}, extra={sorted(set(pages)-expected)}")
    manifest_pages = {entry["prompt_id"]: entry for entry in manifest["pages"]}
    required = {"title", "objective", "instruction", "child_thinking", "model_example", "expected_response",
                "archetype", "mechanic", "render_kind", "illustration_assets", "renderer_controls", "teacher_cue", "validation_gates"}
    for page_id, page in pages.items():
        missing = required - set(page)
        if missing:
            failures.append(f"{page_id}: missing {sorted(missing)}")
            continue
        if manifest_pages[page_id]["title"] != page["title"]:
            failures.append(f"{page_id}: title differs from V4 manifest")
        if page_number(page_id) != manifest_pages[page_id]["physical"]:
            failures.append(f"{page_id}: physical page mismatch")
        for key in ("objective", "instruction", "child_thinking", "expected_response", "archetype", "mechanic", "render_kind", "teacher_cue"):
            if not isinstance(page[key], str) or not page[key].strip():
                failures.append(f"{page_id}: {key} is empty")
        if not isinstance(page["model_example"], dict) or not page["model_example"]:
            failures.append(f"{page_id}: model_example is missing")
        if not isinstance(page["renderer_controls"], dict) or not page["renderer_controls"]:
            failures.append(f"{page_id}: renderer_controls are missing")
        if len(page["validation_gates"]) < 4:
            failures.append(f"{page_id}: insufficient validation gates")
        controls = page["renderer_controls"]
        if controls.get("require_derangement"):
            left, right = controls.get("left", []), controls.get("right", [])
            pair_map = {pair[0]: pair[1] for pair in controls.get("correct_pairs", [])}
            aligned = [i for i, value in enumerate(left) if i < len(right) and pair_map.get(value) == right[i]]
            if len(left) != len(right) or aligned:
                failures.append(f"{page_id}: matching choices reveal answer at row(s) {aligned}")
    rules = blueprint["global_rules"]
    for key in ("one_primary_child_action", "visible_completed_example", "independent_answers_unmarked",
                "every_response_area_has_a_named_action", "isolated_object_names_visible", "worksheet_mechanics_are_deterministic"):
        if rules.get(key) is not True:
            failures.append(f"global rule {key} must be true")
    for key in ("parent_panel", "home_connection", "generic_response_panel", "allow_fallback"):
        if rules.get(key) is not False:
            failures.append(f"global rule {key} must be false")
    if failures:
        raise RuntimeError("\n".join(failures))
    print(json.dumps({
        "book": blueprint["book"], "validated_pages": len(pages), "first_page": min(pages, key=page_number),
        "last_page": max(pages, key=page_number), "external_art_pages": sum(bool(p["illustration_assets"]) for p in pages.values()),
        "status": "PASS",
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"Logical Thinking curriculum validation FAIL: {exc}")
        raise SystemExit(2)
