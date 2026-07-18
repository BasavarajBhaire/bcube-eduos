#!/usr/bin/env python3
"""BCube EduOS v1.0 critical QA and weighted scoring engine."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

WEIGHTS = {
    "repository_accuracy": 20,
    "layout_quality": 15,
    "illustration_quality": 15,
    "educational_effectiveness": 15,
    "print_readability": 10,
    "character_consistency": 10,
    "brand_consistency": 5,
    "child_engagement": 5,
    "parent_teacher_appeal": 3,
    "premium_wow_factor": 2,
}
CRITICAL_CHECKS = {
    "single_page",
    "correct_logo",
    "correct_identity",
    "exact_visible_text",
    "print_geometry",
    "no_invented_content",
}


def evaluate(report: dict[str, Any]) -> tuple[bool, int, list[str]]:
    failures: list[str] = []
    checks = report.get("critical_checks", {})
    for name in sorted(CRITICAL_CHECKS):
        if checks.get(name) is not True:
            failures.append(f"critical:{name}")

    scores = report.get("scores", {})
    total = 0
    for category, maximum in WEIGHTS.items():
        value = scores.get(category)
        if not isinstance(value, int) or not 0 <= value <= maximum:
            failures.append(f"invalid_score:{category}")
            continue
        total += value

    if total < 95:
        failures.append(f"score_below_95:{total}")
    return not failures, total, failures


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: qa_engine.py <qa-report.json>", file=sys.stderr)
        return 2
    try:
        report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        passed, total, failures = evaluate(report)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"QA ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"QA SCORE: {total}/100")
    print("GOLD CERTIFIED" if passed else "REJECTED")
    for failure in failures:
        print(f"- {failure}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
