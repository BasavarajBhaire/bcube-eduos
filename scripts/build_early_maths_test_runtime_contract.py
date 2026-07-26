#!/usr/bin/env python3
"""Build a complete test-ready Early Maths Adventures LKG runtime contract.

This script uses the already committed page specification map in
`rebuild_early_maths_lkg_illustration_contracts.py`. It is deterministic and
requires no workbook at render time. The resulting contract is suitable for
bulk visual testing of pages P008-P044.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPEC_FILE = ROOT / "scripts" / "rebuild_early_maths_lkg_illustration_contracts.py"
OUTPUT = ROOT / "runtime-contracts" / "lkg" / "early-maths-adventures.json"


def load_specs() -> dict[int, dict[str, Any]]:
    spec = importlib.util.spec_from_file_location("early_maths_specs", SPEC_FILE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {SPEC_FILE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.SPECS


def render_kind(mechanic: str) -> str:
    if mechanic in {"count-match-review-1-10", "count-select-11-20", "count-and-circle-number"}:
        return "count-choice-grid"
    if mechanic in {"count-and-match", "match-2d-shape-to-object", "match-3d-solid-to-object"}:
        return "quantity-numeral-match"
    if mechanic.startswith("compare-") or mechanic in {"identify-equal-groups", "compare-numerals", "position-word-choice"}:
        return "comparison-pairs"
    if mechanic in {"complete-missing-numbers", "number-before-after", "order-numerals", "daily-routine-order"}:
        return "sequence-completion"
    if mechanic == "picture-addition-join-groups":
        return "group-addition"
    if mechanic == "picture-subtraction-cross-out":
        return "take-away"
    if mechanic == "number-line-jumps":
        return "number-line-jumps"
    if mechanic == "picture-maths-stories":
        return "picture-story-problems"
    if mechanic == "shape-hunt-scene":
        return "shape-hunt"
    if mechanic == "identify-repeating-pattern":
        return "pattern-observation"
    if mechanic == "complete-repeating-pattern":
        return "pattern-completion"
    if mechanic == "follow-direction-path":
        return "direction-paths"
    if mechanic in {"sort-by-one-attribute", "classify-two-attributes"}:
        return "classification"
    if mechanic == "read-picture-graph":
        return "picture-graph"
    if mechanic in {"mixed-maths-problems", "mixed-maths-review"}:
        return "mixed-review"
    if mechanic in {"maths-around-me-find", "maths-reflection-choice"}:
        return "observe-reflect"
    if mechanic == "certificate-celebration-assets":
        return "certificate"
    if mechanic == "back-cover-illustration":
        return "back-cover"
    return "asset-grid"


def crop_dict(coords: list[float]) -> dict[str, float]:
    x0, y0, x1, y1 = coords
    return {"x": x0, "y": y0, "w": round(x1 - x0, 6), "h": round(y1 - y0, 6), "padding": 0.012}


def mechanics_payload(spec: dict[str, Any]) -> dict[str, Any]:
    names = list(spec["assets"])
    mechanic = spec["mechanic"]
    payload: dict[str, Any] = {"asset_order": names}
    if mechanic in {"count-and-match", "match-2d-shape-to-object", "match-3d-solid-to-object"}:
        half = len(names) // 2
        payload["left"] = names[:half]
        payload["right"] = names[half:]
    elif "pair" in spec["layout"] or mechanic.startswith("compare-") or mechanic == "identify-equal-groups":
        payload["pairs"] = [names[i:i + 2] for i in range(0, len(names), 2)] if len(names) % 2 == 0 else [[n] for n in names]
    elif mechanic in {"picture-addition-join-groups"}:
        payload["problems"] = [names[i:i + 2] for i in range(0, len(names), 2)]
    else:
        payload["rows"] = names
    return payload


def build_page(number: int, spec: dict[str, Any]) -> dict[str, Any]:
    page_id = f"EM-LKG-V4-P{number:03d}"
    page_type = "back_cover" if number == 44 else "certificate" if number == 42 else "learning_page"
    return {
        "identity": {
            "page_id": page_id,
            "book_slug": "early-maths-adventures",
            "level": "lkg",
            "physical_page": number,
            "printed_page": number - 1,
            "title": spec["title"],
            "page_type": page_type,
        },
        "learning": {
            "objective": spec["objective"],
            "instruction": spec["instruction"],
            "expected_response": spec["response"],
            "model_text": None,
        },
        "activity": {
            "archetype": spec["archetype"],
            "mechanic": spec["mechanic"],
            "render_kind": render_kind(spec["mechanic"]),
            "response_mode": "page-specific",
            "mechanics": mechanics_payload(spec),
        },
        "illustration": {
            "source_asset": f"{page_id}.png",
            "assets": list(spec["assets"]),
            "asset_crops": {name: crop_dict(coords) for name, coords in spec["crops"].items()},
            "crop_safe": True,
            "must_match_prompt": True,
        },
        "layout": {
            "template": spec["layout"],
            "parent_panel": False,
            "home_connection": False,
            "generic_response_panel": False,
        },
        "guidance": {"teacher_cue": spec["teacher"]},
        "validation": {
            "status": "READY",
            "allow_fallback": False,
            "illustration_contract_aligned": True,
            "blocked_reasons": [],
        },
    }


def main() -> int:
    specs = load_specs()
    pages = {f"EM-LKG-V4-P{n:03d}": build_page(n, specs[n]) for n in sorted(specs)}
    contract = {
        "contract_version": "bcube-book-runtime-contract-v2-test",
        "book": {"title": "Early Maths Adventures", "slug": "early-maths-adventures", "prefix": "EM"},
        "level": "LKG",
        "age": "4+",
        "allow_fallback": False,
        "pages": pages,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(pages)} pages to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
