#!/usr/bin/env python3
"""Fail-closed Phase 4 validator for Curiosity Explorers Nursery."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "books" / "nursery" / "curiosity-explorers"
PROMPTS = BOOK / "production-prompts"
REQUIRED_SECTIONS = [f"## {i}." for i in range(1, 16)]
REQUIRED_DOCS = [
    BOOK / "qa" / "prompt-validation-report.md",
    BOOK / "qa" / "prompt-consistency-report.md",
    BOOK / "qa" / "prompt-quality-score.md",
    BOOK / "validation" / "design-validation-checklist.md",
    BOOK / "illustration" / "illustration-consistency-matrix.md",
    BOOK / "publishing" / "prepress-checklist.md",
    BOOK / "publishing" / "release-gates.md",
    BOOK / "production" / "asset-map.json",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def main() -> None:
    files = sorted(PROMPTS.glob("P[0-9][0-9][0-9].md"))
    if len(files) != 44:
        fail(f"expected 44 prompts, found {len(files)}")

    ids: set[str] = set()
    results = []
    for index, path in enumerate(files, start=1):
        expected_name = f"P{index:03d}.md"
        if path.name != expected_name:
            fail(f"sequence mismatch: expected {expected_name}, found {path.name}")
        text = path.read_text(encoding="utf-8")
        match = re.search(r"CE-NURSERY-V5-P\d{3}", text)
        if not match:
            fail(f"missing prompt ID in {path.name}")
        prompt_id = match.group(0)
        expected_id = f"CE-NURSERY-V5-P{index:03d}"
        if prompt_id != expected_id:
            fail(f"ID mismatch in {path.name}: {prompt_id}")
        if prompt_id in ids:
            fail(f"duplicate ID: {prompt_id}")
        ids.add(prompt_id)
        missing = [section for section in REQUIRED_SECTIONS if section not in text]
        if missing:
            fail(f"{path.name} missing sections: {missing}")
        for token in ("2480 × 3508", "300 DPI", "Negative constraints", "Acceptance criteria"):
            if token not in text:
                fail(f"{path.name} missing required token: {token}")
        results.append({"file": path.name, "prompt_id": prompt_id, "status": "pass", "score_gate": 95})

    for required in REQUIRED_DOCS:
        if not required.exists():
            fail(f"missing Phase 4 document: {required.relative_to(ROOT)}")

    asset_map = json.loads((BOOK / "production" / "asset-map.json").read_text(encoding="utf-8"))
    if asset_map.get("artwork_generation_allowed") is not False:
        fail("asset map must block artwork generation until human approval")

    report = {
        "phase": 4,
        "book": "Curiosity Explorers Gold",
        "prompt_count": len(results),
        "minimum_quality_score": 95,
        "automated_validation": "pass",
        "human_visual_review_required": True,
        "artwork_generation_allowed": False,
        "pages": results,
    }
    out = BOOK / "qa" / "phase4-validation-report.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: validated {len(results)} prompts; artwork remains blocked pending human review")


if __name__ == "__main__":
    main()
