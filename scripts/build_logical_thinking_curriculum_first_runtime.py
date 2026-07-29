#!/usr/bin/env python3
"""Build the fail-closed Logical Thinking Adventures LKG runtime contract."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "curriculum/logical-thinking-adventures/lkg/curriculum-first-p008-p043-v1.json"
MANIFEST = ROOT / "production-prompts/logical-thinking-adventures/lkg/v4/release-manifest.json"
OUTPUT = ROOT / "runtime-contracts/lkg/logical-thinking-adventures.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def crop_grid(names: list[str]) -> dict[str, dict[str, float]]:
    if not names:
        return {}
    count = len(names)
    cols = 1 if count == 1 else 2 if count <= 12 else 3
    rows = (count + cols - 1) // cols
    gap_x, gap_y = 0.055, 0.035
    cell_w = (1 - gap_x * (cols + 1)) / cols
    cell_h = (1 - gap_y * (rows + 1)) / rows
    return {
        name: {
            "x": round(gap_x + (index % cols) * (cell_w + gap_x), 6),
            "y": round(gap_y + (index // cols) * (cell_h + gap_y), 6),
            "w": round(cell_w, 6), "h": round(cell_h, 6), "padding": 0.008,
        }
        for index, name in enumerate(names)
    }


def main() -> int:
    blueprint = load(BLUEPRINT)
    manifest = load(MANIFEST)
    release_pages = {entry["prompt_id"]: entry for entry in manifest["pages"]}
    pages: dict[str, Any] = {}
    for page_id, source in blueprint["pages"].items():
        release = release_pages[page_id]
        assets = list(source["illustration_assets"])
        physical = int(release["physical"])
        if physical == 42:
            page_type = "certificate"
        elif physical in {41, 43}:
            page_type = "celebration"
        else:
            page_type = "learning_page"
        pages[page_id] = {
            "identity": {
                "page_id": page_id, "book_slug": "logical-thinking-adventures", "level": "lkg",
                "physical_page": physical, "printed_page": release["printed"], "title": source["title"], "page_type": page_type,
            },
            "learning": {
                "objective": source["objective"], "instruction": source["instruction"],
                "expected_response": source["expected_response"], "model_text": source["model_example"],
                "child_thinking": source["child_thinking"],
            },
            "activity": {
                "archetype": source["archetype"], "mechanic": source["mechanic"],
                "render_kind": source["render_kind"], "response_mode": "page-specific",
                "mechanics": source["renderer_controls"],
            },
            "illustration": {
                "source_asset": f"{page_id}.png" if assets else "DETERMINISTIC_NO_ART",
                "assets": assets, "asset_crops": crop_grid(assets), "asset_meanings": source["illustration_assets"],
                "requires_generated_art": bool(assets), "artwork_only": True, "crop_safe": True, "must_match_prompt": bool(assets),
            },
            "layout": {
                "template": source["archetype"], "parent_panel": False, "home_connection": False,
                "generic_response_panel": False,
                "completed_example": not bool(source["model_example"].get("assessment_safe") or source["model_example"].get("not_required")),
                "independent_answers_unmarked": True, "object_names_visible": True,
            },
            "guidance": {"teacher_cue": source["teacher_cue"]},
            "validation": {
                "status": "READY", "allow_fallback": False, "illustration_contract_aligned": True,
                "curriculum_first": True, "teaching_gates": source["validation_gates"], "blocked_reasons": [],
            },
        }
    contract = {
        "contract_version": "bcube-book-runtime-contract-v2-curriculum-first",
        "book": {"title": "Logical Thinking Adventures", "slug": "logical-thinking-adventures", "prefix": "LT"},
        "level": "LKG", "age": "4+", "allow_fallback": False,
        "curriculum_first_scope": list(pages), "pages": pages,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(pages)} Logical Thinking pages to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
