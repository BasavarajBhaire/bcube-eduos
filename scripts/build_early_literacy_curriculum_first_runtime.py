#!/usr/bin/env python3
"""Build the fail-closed Early Literacy Adventures LKG runtime contract."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "curriculum/early-literacy-adventures/lkg/curriculum-first-p008-p043-v1.json"
MANIFEST = ROOT / "production-prompts/early-literacy-adventures/lkg/v4/release-manifest.json"
OUTPUT = ROOT / "runtime-contracts/lkg/early-literacy-adventures.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def crop_grid(names: list[str]) -> dict[str, dict[str, float]]:
    if not names:
        return {}
    count = len(names)
    cols = 1 if count == 1 else 2 if count <= 8 else 3
    rows = (count + cols - 1) // cols
    gap_x, gap_y = 0.06, 0.045
    cell_w = (1 - gap_x * (cols + 1)) / cols
    cell_h = (1 - gap_y * (rows + 1)) / rows
    result: dict[str, dict[str, float]] = {}
    for index, name in enumerate(names):
        row, col = divmod(index, cols)
        x = gap_x + col * (cell_w + gap_x)
        y = gap_y + row * (cell_h + gap_y)
        result[name] = {
            "x": round(x, 6), "y": round(y, 6),
            "w": round(cell_w, 6), "h": round(cell_h, 6),
            "padding": 0.008,
        }
    return result


def main() -> int:
    blueprint = load(BLUEPRINT)
    release = load(MANIFEST)
    release_pages = {entry["prompt_id"]: entry for entry in release["pages"]}
    pages: dict[str, dict[str, Any]] = {}

    for page_id, source in blueprint["pages"].items():
        release_page = release_pages[page_id]
        assets = list(source["illustration_assets"])
        requires_art = bool(assets)
        physical = int(release_page["physical"])
        page_type = "certificate" if physical == 41 else "celebration" if physical in {42, 43} else "learning_page"
        asset_crops = crop_grid(assets)
        for name, override in source.get("asset_crop_overrides", {}).items():
            if name not in asset_crops:
                raise ValueError(f"{page_id}: crop override references unknown asset {name}")
            asset_crops[name] = override

        pages[page_id] = {
            "identity": {
                "page_id": page_id,
                "book_slug": "early-literacy-adventures",
                "level": "lkg",
                "physical_page": physical,
                "printed_page": release_page["printed"],
                "title": source["title"],
                "page_type": page_type,
            },
            "learning": {
                "objective": source["objective"],
                "instruction": source["instruction"],
                "expected_response": source["expected_response"],
                "model_text": source["model_example"],
                "child_thinking": source["child_thinking"],
            },
            "activity": {
                "archetype": source["archetype"],
                "mechanic": source["mechanic"],
                "render_kind": source["render_kind"],
                "response_mode": "page-specific",
                "mechanics": source["renderer_controls"],
            },
            "illustration": {
                "source_asset": f"{page_id}.png" if requires_art else "DETERMINISTIC_NO_ART",
                "assets": assets,
                "asset_crops": asset_crops,
                "asset_meanings": source["illustration_assets"],
                "requires_generated_art": requires_art,
                "artwork_only": True,
                "crop_safe": True,
                "must_match_prompt": requires_art,
            },
            "layout": {
                "template": source["archetype"],
                "parent_panel": False,
                "home_connection": False,
                "generic_response_panel": False,
                "completed_example": not bool(source["model_example"].get("assessment_safe") or source["model_example"].get("not_required")),
                "independent_answers_unmarked": True,
            },
            "guidance": {"teacher_cue": source["teacher_cue"]},
            "validation": {
                "status": "READY",
                "allow_fallback": False,
                "illustration_contract_aligned": True,
                "curriculum_first": True,
                "teaching_gates": source["validation_gates"],
                "blocked_reasons": [],
            },
        }

    contract = {
        "contract_version": "bcube-book-runtime-contract-v2-curriculum-first",
        "book": {"title": "Early Literacy Adventures", "slug": "early-literacy-adventures", "prefix": "EL"},
        "level": "LKG",
        "age": "4+",
        "allow_fallback": False,
        "curriculum_first_scope": list(pages),
        "pages": pages,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(pages)} Early Literacy pages to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
