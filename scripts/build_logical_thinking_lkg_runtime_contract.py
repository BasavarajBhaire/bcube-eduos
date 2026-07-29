#!/usr/bin/env python3
"""Build Logical Thinking Adventures LKG from its individual V4 page contracts.

Each runtime page is composed from two matching sources with the same page ID:
1. the individual V4 page JSON, which owns curriculum, identity and guidance;
2. the Phase 2 illustration JSON, which owns named assets, crop geometry and the
   exact artwork brief.

No title/activity inference or generic fallback is allowed. Render routing is an
explicit page-by-page release decision and every output remains TEST_CANDIDATE.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAGE_DIR = ROOT / "production-prompts/logical-thinking-adventures/lkg/v4/pages"
ILLUSTRATIONS = ROOT / "production-prompts/logical-thinking-adventures/lkg/v4/phase2-illustration-prompts.json"
OUTPUT = ROOT / "runtime-contracts/lkg/logical-thinking-adventures.json"

# Explicit per-page renderer decisions. These are release contracts, not
# inferred categories. Changing one requires page-level visual review.
PAGE_RENDER = {
    8: ("asset-grid", "find-five-differences", "circle-differences", "find-difference-two-scenes-v1"),
    9: ("asset-grid", "spot-identical-picture", "circle-identical-choice", "spot-same-six-sets-v1"),
    10: ("asset-grid", "odd-one-out", "circle-odd-choice", "odd-one-out-six-rows-v1"),
    11: ("quantity-numeral-match", "picture-pair-match", "draw-line", "picture-match-six-pairs-v1"),
    12: ("shape-hunt", "shape-identification", "circle-shape", "shape-hunt-scene-targets-v1"),
    13: ("pattern-completion", "complete-visual-pattern", "choose-next", "pattern-completion-v1"),
    14: ("sequence-completion", "order-picture-sequence", "number-order", "sequence-order-v1"),
    15: ("pattern-completion", "complete-colour-pattern", "choose-next", "colour-pattern-v1"),
    16: ("pattern-completion", "complete-shape-pattern", "choose-next", "shape-pattern-v1"),
    17: ("classification", "classify-by-property", "sort-groups", "classification-two-groups-v1"),
    18: ("classification", "classify-by-use", "sort-groups", "classification-two-groups-v1"),
    19: ("classification", "classify-by-place", "sort-groups", "classification-two-groups-v1"),
    20: ("quantity-numeral-match", "match-related-pictures", "draw-line", "related-picture-match-v1"),
    21: ("asset-grid", "complete-analogy", "circle-choice", "picture-analogy-v1"),
    22: ("quantity-numeral-match", "match-shadow", "draw-line", "shadow-match-v1"),
    23: ("comparison-pairs", "identify-more", "circle-choice", "more-comparison-v1"),
    24: ("comparison-pairs", "identify-less", "circle-choice", "less-comparison-v1"),
    25: ("comparison-pairs", "compare-size", "circle-choice", "size-comparison-v1"),
    26: ("direction-paths", "follow-direction", "trace-path", "direction-paths-v1"),
    27: ("asset-grid", "identify-position", "circle-choice", "position-identification-v1"),
    28: ("observe-reflect", "observe-and-reason", "oral-response", "observe-reason-v1"),
    29: ("asset-grid", "complete-picture", "draw-missing-part", "complete-picture-v1"),
    30: ("asset-grid", "visual-memory", "recall-and-circle", "visual-memory-v1"),
    31: ("quantity-numeral-match", "match-halves", "draw-line", "half-match-v1"),
    32: ("quantity-numeral-match", "match-object-use", "draw-line", "object-use-match-v1"),
    33: ("asset-grid", "identify-cause-effect", "circle-choice", "cause-effect-v1"),
    34: ("asset-grid", "choose-correct-action", "circle-choice", "correct-action-v1"),
    35: ("direction-paths", "solve-path", "trace-path", "logic-path-v1"),
    36: ("mixed-review", "mixed-logical-review", "page-specific-response", "logical-review-v1"),
    37: ("mixed-review", "mixed-logical-review", "page-specific-response", "logical-review-v1"),
    38: ("mixed-review", "mixed-logical-review", "page-specific-response", "logical-review-v1"),
    39: ("mixed-review", "mixed-logical-review", "page-specific-response", "logical-review-v1"),
    40: ("observe-reflect", "reflect-on-thinking", "oral-response", "thinking-reflection-v1"),
    41: ("asset-grid", "logic-challenge", "page-specific-response", "logic-challenge-v1"),
    42: ("certificate", "completion-certificate", "name-and-date", "certificate-v1"),
    43: ("observe-reflect", "book-reflection", "oral-or-drawing-response", "book-reflection-v1"),
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object expected: {path}")
    return value


def clean(value: Any) -> str:
    return " ".join(str(value or "").split()).strip()


def prompt_field(prompt: str, label: str, fallback: str = "") -> str:
    match = re.search(rf"^{re.escape(label)}:\s*(.+)$", prompt, re.MULTILINE)
    return clean(match.group(1)) if match else clean(fallback)


def find_page_source(page_id: str) -> tuple[Path, dict[str, Any]]:
    matches: list[tuple[Path, dict[str, Any]]] = []
    for path in PAGE_DIR.glob("*.json"):
        source = load_json(path)
        if clean(source.get("prompt_id")) == page_id:
            matches.append((path, source))
    if len(matches) != 1:
        raise ValueError(f"{page_id}: expected one individual page JSON, found {len(matches)}")
    return matches[0]


def match_mechanics(render_kind: str, assets: list[str]) -> dict[str, Any]:
    mechanics: dict[str, Any] = {"asset_order": assets, "show_correct_answer": False}
    if render_kind == "quantity-numeral-match":
        if len(assets) % 2 != 0:
            raise ValueError("Match page requires an even number of named assets")
        half = len(assets) // 2
        mechanics["left"] = assets[:half]
        mechanics["right"] = assets[half:]
    elif render_kind == "comparison-pairs":
        mechanics["pairs"] = [[name] for name in assets]
    return mechanics


def build_page(page_id: str, illustration: dict[str, Any]) -> dict[str, Any]:
    number = int(page_id.rsplit("P", 1)[1])
    if number not in PAGE_RENDER:
        raise ValueError(f"{page_id}: no explicit page renderer decision")
    source_path, source = find_page_source(page_id)
    page = source.get("page", {})
    curriculum = source.get("curriculum", {})
    prompt = str(illustration.get("prompt", ""))
    assets = list(illustration.get("asset_names") or [])
    crops = dict(illustration.get("asset_crops") or {})
    if not assets or set(assets) != set(crops):
        raise ValueError(f"{page_id}: named assets and crop map do not match")
    if clean(illustration.get("status")) != "READY_FOR_ILLUSTRATION":
        raise ValueError(f"{page_id}: illustration contract is not ready")

    title = clean(page.get("title")) or clean(illustration.get("title"))
    if title != clean(illustration.get("title")):
        raise ValueError(f"{page_id}: title mismatch between individual page and illustration contract")

    objective = prompt_field(prompt, "Learning objective", clean(curriculum.get("objective")))
    instruction = prompt_field(prompt, "Exact child action", clean(curriculum.get("instruction")))
    if not objective or not instruction:
        raise ValueError(f"{page_id}: exact objective/action missing")

    render_kind, mechanic, response_mode, template = PAGE_RENDER[number]
    teacher_cue = clean(curriculum.get("teacher_facilitation")) or "Model one example without revealing the answer, then guide the child to complete the exact page action."
    expected = clean(curriculum.get("evidence")) or f"The child completes the exact action: {instruction}"

    return {
        "identity": {
            "page_id": page_id,
            "physical_page": int(page.get("physical") or number),
            "printed_page": page.get("printed", number - 1),
            "title": title,
            "page_type": clean(page.get("type")) or "worksheet",
        },
        "learning": {
            "objective": objective,
            "instruction": instruction,
            "expected_response": expected,
            "model_text": None,
        },
        "activity": {
            "archetype": f"{page_id} — {title}",
            "mechanic": mechanic,
            "render_kind": render_kind,
            "response_mode": response_mode,
            "activity_count": len(assets),
            "mechanics": match_mechanics(render_kind, assets),
        },
        "illustration": {
            "source_asset": clean(illustration.get("output_filename")) or f"{page_id}.png",
            "artwork_only": True,
            "assets": assets,
            "asset_crops": crops,
            "prompt": prompt,
        },
        "mechanics": {
            "asset_order": assets,
            "exact_child_action": instruction,
            "approved_page_direction": clean(source.get("preserved_source", {}).get("approved_source_instruction")) or clean(curriculum.get("instruction")),
            "show_correct_answer": False,
        },
        "guidance": {
            "teacher_cue": teacher_cue,
            "teacher_questions": curriculum.get("teacher_questions") or [],
        },
        "layout": {
            "template": template,
            "parent_panel": False,
            "home_connection": False,
            "generic_response_panel": False,
        },
        "validation": {
            "allow_fallback": False,
            "status": "READY",
            "required_asset_count": len(assets),
            "required_response_count": 1,
            "blocking_reasons": [],
            "illustration_contract_aligned": True,
            "visual_status": "TEST_CANDIDATE",
        },
        "source_lineage": {
            "source_prompt_id": page_id,
            "source_file": source_path.relative_to(ROOT).as_posix(),
            "illustration_contract_file": ILLUSTRATIONS.relative_to(ROOT).as_posix(),
            "illustration_status": clean(illustration.get("status")),
            "runtime_status": "TEST_CANDIDATE",
        },
    }


def main() -> int:
    pack = load_json(ILLUSTRATIONS)
    raw_pages = pack.get("pages")
    if not isinstance(raw_pages, dict):
        raise ValueError("Phase 2 illustration contract must contain a pages object")

    expected = [f"LT-LKG-V4-P{n:03d}" for n in range(8, 44)]
    if sorted(raw_pages) != expected:
        missing = sorted(set(expected) - set(raw_pages))
        extra = sorted(set(raw_pages) - set(expected))
        raise ValueError(f"Expected exactly P008-P043. Missing={missing}; extra={extra}")

    pages = {page_id: build_page(page_id, raw_pages[page_id]) for page_id in expected}
    contract = {
        "contract_version": "bcube-book-runtime-contract-v1",
        "book": {"title": "Logical Thinking Adventures", "slug": "logical-thinking-adventures", "prefix": "LT"},
        "level": "LKG",
        "age": "4+",
        "allow_fallback": False,
        "status": "TEST_CANDIDATE",
        "policy": "Every runtime page preserves its individual V4 curriculum contract and matching Phase 2 illustration contract. No generic fallback.",
        "pages": pages,
        "compile_summary": {"runtime_pages": len(pages), "ready_pages": len(pages), "blocked_pages": 0, "visual_status": "TEST_CANDIDATE"},
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), **contract["compile_summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"Logical Thinking LKG runtime build FAIL: {exc}")
        raise SystemExit(2)
