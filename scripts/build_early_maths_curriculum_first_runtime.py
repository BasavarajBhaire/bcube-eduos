#!/usr/bin/env python3
"""Build Early Maths runtime and overlay the approved curriculum-first P009-P021 blueprint."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_BUILDER = ROOT / "scripts" / "build_early_maths_test_runtime_contract.py"
BLUEPRINT = ROOT / "curriculum" / "early-maths-adventures" / "lkg" / "curriculum-first-p009-p021-v1.json"
OUTPUT = ROOT / "runtime-contracts" / "lkg" / "early-maths-adventures.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object expected: {path}")
    return value


def crop_grid(names: list[str]) -> dict[str, dict[str, float]]:
    if not names:
        return {}
    cols = 1 if len(names) <= 3 else 2 if len(names) <= 8 else 3
    rows = (len(names) + cols - 1) // cols
    gx, gy = 0.08, 0.07
    cw = (1 - gx * (cols + 1)) / cols
    ch = (1 - gy * (rows + 1)) / rows
    crops: dict[str, dict[str, float]] = {}
    for index, name in enumerate(names):
        r, c = divmod(index, cols)
        x = gx + c * (cw + gx); y = gy + r * (ch + gy)
        crops[name] = {"x": round(x, 5), "y": round(y, 5), "w": round(cw, 5), "h": round(ch, 5), "padding": 0.008}
    return crops


def main() -> int:
    base = load_module("early_maths_base_builder", BASE_BUILDER)
    result = base.main()
    if result not in (None, 0):
        raise RuntimeError(f"Base builder returned {result}")

    contract = load_json(OUTPUT)
    blueprint = load_json(BLUEPRINT)
    deterministic_pages = {"EM-LKG-V4-P013", "EM-LKG-V4-P016", "EM-LKG-V4-P017", "EM-LKG-V4-P019"}

    for page_id, source in blueprint["pages"].items():
        if page_id not in contract["pages"]:
            raise KeyError(page_id)
        page = contract["pages"][page_id]
        is_deterministic = page_id in deterministic_pages
        assets = [] if is_deterministic else list(source.get("illustration_assets", {}))
        page["identity"]["title"] = source["title"]
        page["learning"] = {
            "objective": source["objective"],
            "instruction": source["instruction"],
            "expected_response": source["expected_response"],
            "model_text": source["model_example"],
        }
        page["activity"] = {
            "archetype": source["archetype"],
            "mechanic": source["mechanic"],
            "render_kind": source["render_kind"],
            "response_mode": "page-specific",
            "mechanics": source["renderer_controls"],
        }
        page["illustration"] = {
            "source_asset": "DETERMINISTIC_NO_ART" if is_deterministic else f"{page_id}.png",
            "assets": assets,
            "asset_crops": crop_grid(assets),
            "asset_meanings": {name: source.get("illustration_assets", {}).get(name, "") for name in assets},
            "requires_generated_art": not is_deterministic,
            "crop_safe": True,
            "must_match_prompt": not is_deterministic,
        }
        page["layout"] = {
            "template": source["archetype"],
            "blueprint": source["layout"],
            "parent_panel": False,
            "home_connection": False,
            "generic_response_panel": False,
        }
        page["guidance"] = {"teacher_cue": source["teacher_cue"]}
        page["validation"] = {
            "status": "READY",
            "allow_fallback": False,
            "illustration_contract_aligned": True,
            "curriculum_first": True,
            "teaching_gates": source["validation_gates"],
            "blocked_reasons": [],
        }

    contract["curriculum_first_scope"] = list(blueprint["pages"])
    contract["contract_version"] = "bcube-book-runtime-contract-v2-curriculum-first-test"
    OUTPUT.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Applied curriculum-first overlay to {len(blueprint['pages'])} pages in {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
