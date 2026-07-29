#!/usr/bin/env python3
"""Render Logical Thinking Adventures LKG P008-P017 from approved sheets."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_logical_thinking_curriculum_first.py"
BUILDER = ROOT / "scripts/build_logical_thinking_curriculum_first_runtime.py"
SCOPE = [f"LT-LKG-V4-P{number:03d}" for number in range(8, 18)]


def parse_pages(value: str | None) -> list[str]:
    if not value or value.lower() == "all":
        return SCOPE
    result: list[str] = []
    for token in value.split(","):
        token = token.strip().upper()
        if token.startswith("P") and token[1:].isdigit():
            token = f"LT-LKG-V4-P{int(token[1:]):03d}"
        if token not in SCOPE:
            raise ValueError(f"Wave 1 supports only P008-P017: {token}")
        if token not in result:
            result.append(token)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--logo", type=Path, required=True)
    parser.add_argument("--illustrations-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--pages", default="all")
    args = parser.parse_args()
    scope = parse_pages(args.pages)
    subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, check=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for page_id in scope:
        source = args.illustrations_dir / f"{page_id}.png"
        output = args.output_dir / f"{page_id}.png"
        evidence = args.evidence_dir / f"{page_id}.json"
        if not source.is_file():
            results.append({"page_id": page_id, "status": "FAILED", "reason": f"Missing {source}"})
            continue
        command = [
            sys.executable, str(COMPOSER), "--page-id", page_id,
            "--illustration", str(source), "--logo", str(args.logo),
            "--output", str(output), "--evidence-output", str(evidence),
        ]
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        if completed.returncode:
            results.append({"page_id": page_id, "status": "FAILED", "reason": completed.stderr.strip() or completed.stdout.strip()})
        else:
            results.append({"page_id": page_id, "status": "GENERATED", "output": str(output), "evidence": str(evidence)})
    summary = {
        "book": "Logical Thinking Adventures", "level": "LKG", "scope": scope,
        "generated": sum(item["status"] == "GENERATED" for item in results),
        "failed": sum(item["status"] == "FAILED" for item in results),
        "policy": "Approved page sheets; exact curriculum-first layouts; open child responses; no fallback.",
        "results": results,
    }
    summary_path = args.evidence_dir / "logical-thinking-wave1-render-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["failed"] == 0 else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Logical Thinking wave 1 render FAIL: {exc}", file=sys.stderr)
        raise SystemExit(2)
