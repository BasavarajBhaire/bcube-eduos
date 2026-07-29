#!/usr/bin/env python3
"""Render Early Literacy Adventures LKG P008-P017 with approved artwork only."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "runtime-contracts/lkg/early-literacy-adventures.json"
COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_early_literacy_curriculum_first.py"
SCOPE = [f"EL-LKG-V4-P{number:03d}" for number in range(8, 18)]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def parse_pages(value: str | None) -> list[str]:
    if not value:
        return SCOPE
    result: list[str] = []
    for token in value.split(","):
        token = token.strip().upper()
        if token.startswith("P") and token[1:].isdigit():
            token = f"EL-LKG-V4-P{int(token[1:]):03d}"
        if token not in SCOPE:
            raise ValueError(f"Wave 1 page is outside P008-P017: {token}")
        result.append(token)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--logo", type=Path, required=True)
    parser.add_argument("--illustrations-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--pages", help="Optional comma-separated P008-P017 selection")
    args = parser.parse_args()

    contract = load(CONTRACT)
    scope = parse_pages(args.pages)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []

    for page_id in scope:
        page = contract["pages"][page_id]
        illustration = args.illustrations_dir / f"{page_id}.png"
        output = args.output_dir / f"{page_id}.png"
        evidence = args.evidence_dir / f"{page_id}.json"
        command = [
            sys.executable, str(COMPOSER), "--page-id", page_id,
            "--logo", str(args.logo), "--output", str(output),
            "--evidence-output", str(evidence),
        ]
        if page["illustration"]["requires_generated_art"]:
            if not illustration.is_file():
                results.append({"page_id": page_id, "status": "FAILED", "reason": f"Missing approved illustration: {illustration}"})
                continue
            command.extend(["--illustration", str(illustration)])
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        if completed.returncode:
            results.append({"page_id": page_id, "status": "FAILED", "reason": completed.stderr.strip() or completed.stdout.strip()})
        else:
            results.append({"page_id": page_id, "status": "GENERATED", "output": str(output)})

    summary = {
        "book": "Early Literacy Adventures",
        "level": "LKG",
        "scope": scope,
        "generated": sum(item["status"] == "GENERATED" for item in results),
        "failed": sum(item["status"] == "FAILED" for item in results),
        "policy": "Curriculum-first exact renderer; approved page artwork only; no generic fallback.",
        "results": results,
    }
    summary_path = args.evidence_dir / "early-literacy-wave1-render-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["failed"] == 0 else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Early Literacy wave 1 render FAIL: {exc}", file=sys.stderr)
        raise SystemExit(2)
