#!/usr/bin/env python3
"""Build the fail-closed Logical Thinking Adventures LKG runtime contract.

The Phase 2 illustration prompt pack is the source of truth for page titles,
object order, crop maps, objectives and child actions. Generated pages remain
TEST_CANDIDATE until visual review.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "production-prompts/logical-thinking-adventures/lkg/v4/phase2-illustration-prompts.json"
OUTPUT = ROOT / "runtime-contracts/lkg/logical-thinking-adventures.json"

RENDER_KIND = {
    8: "asset-grid", 9: "asset-grid", 10: "asset-grid",
    11: "quantity-numeral-match", 12: "shape-hunt",
    13: "pattern-completion", 14: "sequence-completion",
    15: "pattern-completion", 16: "pattern-completion",
    17: "classification", 18: "classification", 19: "classification",
    20: "quantity-numeral-match", 21: "asset-grid",
    22: "quantity-numeral-match", 23: "comparison-pairs",
    24: "comparison-pairs", 25: "comparison-pairs",
    26: "direction-paths", 27: "asset-grid", 28: "observe-reflect",
    29: "asset-grid", 30: "asset-grid", 31: "quantity-numeral-match",
    32: "quantity-numeral-match", 33: "asset-grid", 34: "asset-grid",
    35: "direction-paths", 36: "mixed-review", 37: "mixed-review",
    38: "mixed-review", 39: "mixed-review", 40: "observe-reflect",
    41: "asset-grid", 42: "certificate", 43: "observe-reflect",
}

MECHANIC = {
    "asset-grid": "page-specific-activity",
    "quantity-numeral-match": "match-pairs",
    "shape-hunt": "observe-find-name",
    "pattern-completion": "pattern-completion",
    "sequence-completion": "sequence-order",
    "classification": "sort-and-classify",
    "comparison-pairs": "position-identification",
    "direction-paths": "follow-path",
    "mixed-review": "mixed-review",
    "observe-reflect": "observe-reflect",
    "certificate": "certificate",
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object expected: {path}")
    return value


def prompt_value(prompt: str, label: str, fallback: str) -> str:
    match = re.search(rf"^{re.escape(label)}:\s*(.+)$", prompt, re.MULTILINE)
    return match.group(1).strip() if match else fallback


def build_page(page_id: str, source: dict[str, Any]) -> dict[str, Any]:
    number = int(page_id.rsplit("P", 1)[1])
    title = str(source["title"])
    prompt = str(source["prompt"])
    assets = list(source["asset_names"])
    crops = dict(source["asset_crops"])
    if set(assets) != set(crops):
        raise ValueError(f"{page_id}: asset names and crop names do not match")
    render_kind = RENDER_KIND[number]
    page_type = "certificate" if number == 42 else ("reflection" if number >= 40 else "worksheet")
    return {
        "identity": {
            "page_id": page_id,
            "physical_page": number,
            "printed_page": number - 1,
            "title": title,
            "page_type": page_type,
        },
        "learning": {
            "objective": prompt_value(prompt, "Learning objective", title),
            "instruction": prompt_value(prompt, "Exact child action", "Complete the activity."),
            "expected_response": "The child completes the page-specific logical-thinking response independently or with minimal adult support.",
            "model_text": None,
        },
        "activity": {
            "archetype": f"Logical Thinking — {title}",
            "mechanic": MECHANIC[render_kind],
            "render_kind": render_kind,
            "response_mode": "page-specific-response",
            "activity_count": len(assets),
        },
        "illustration": {
            "source_asset": str(source["output_filename"]),
            "artwork_only": True,
            "assets": assets,
            "asset_crops": crops,
            "prompt": prompt,
        },
        "mechanics": {
            "asset_order": assets,
            "show_correct_answer": False,
        },
        "guidance": {
            "teacher_cue": "Model one example without revealing the answer, then invite the child to complete the remaining activity independently."
        },
        "layout": {
            "template": f"logical-thinking-{render_kind}-v1",
            "parent_panel": False,
            "home_connection": False,
            "generic_response_panel": False,
        },
        "validation": {
            "allow_fallback": False,
            "status": "READY",
            "required_asset_count": len(assets),
            "required_response_count": max(1, len(assets)),
            "blocking_reasons": [],
            "illustration_contract_aligned": True,
        },
        "source_lineage": {
            "source_prompt_id": page_id,
            "source_file": SOURCE.relative_to(ROOT).as_posix(),
            "status": "TEST_CANDIDATE",
        },
    }


def main() -> int:
    source = load_json(SOURCE)
    raw_pages = source.get("pages")
    if not isinstance(raw_pages, dict):
        raise ValueError("Phase 2 prompt pack must contain a pages object")
    pages = {page_id: build_page(page_id, page) for page_id, page in sorted(raw_pages.items())}
    expected = [f"LT-LKG-V4-P{number:03d}" for number in range(8, 44)]
    if list(pages) != expected:
        missing = sorted(set(expected) - set(pages))
        extra = sorted(set(pages) - set(expected))
        raise ValueError(f"Expected P008-P043. Missing={missing}; extra={extra}")
    contract = {
        "contract_version": "bcube-book-runtime-contract-v1",
        "book": {
            "title": "Logical Thinking Adventures",
            "slug": "logical-thinking-adventures",
            "prefix": "LT",
        },
        "level": "LKG",
        "age": "4+",
        "allow_fallback": False,
        "status": "TEST_CANDIDATE",
        "pages": pages,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "pages": len(pages), "status": "TEST_CANDIDATE"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
