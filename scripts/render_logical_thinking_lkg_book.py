#!/usr/bin/env python3
"""Render Logical Thinking Adventures LKG with the dedicated page registry."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "runtime-contracts/lkg/logical-thinking-adventures.json"
COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_logical_thinking_lkg_pages.py"
PAGE_RE = re.compile(r"LT-LKG-V4-P\d{3}", re.IGNORECASE)
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def load_json(path: Path):
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--illustrations-dir", type=Path, required=True)
    parser.add_argument("--logo", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--page-id")
    parser.add_argument("--fail-fast", action="store_true")
    args = parser.parse_args()

    if not CONTRACT.is_file():
        raise SystemExit("Runtime contract missing. Run scripts/build_logical_thinking_lkg_runtime_contract.py first.")
    if not args.illustrations_dir.is_dir():
        raise SystemExit(f"Illustrations directory not found: {args.illustrations_dir}")
    if not args.logo.is_file():
        raise SystemExit(f"Logo not found: {args.logo}")

    contract = load_json(CONTRACT)
    pages = contract.get("pages", {})
    expected = {f"LT-LKG-V4-P{n:03d}" for n in range(8, 44)}
    if set(pages) != expected:
        raise SystemExit("Logical Thinking runtime contract must contain exactly P008-P043")

    illustrations = {}
    duplicates = {}
    for path in sorted(args.illustrations_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTS:
            continue
        match = PAGE_RE.search(path.stem)
        if not match:
            continue
        page_id = match.group(0).upper()
        if page_id in illustrations:
            duplicates.setdefault(page_id, [str(illustrations[page_id])]).append(str(path))
        else:
            illustrations[page_id] = path

    if args.page_id:
        requested = args.page_id.upper()
        expected &= {requested}
        illustrations = {k: v for k, v in illustrations.items() if k == requested}

    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for page_id in sorted(expected):
        illustration = illustrations.get(page_id)
        if illustration is None:
            results.append({"page_id": page_id, "status": "MISSING_ILLUSTRATION"})
            if args.fail_fast:
                break
            continue
        output = args.output_dir / f"{page_id}.png"
        evidence = args.evidence_dir / f"{page_id}.json"
        process = subprocess.run([
            sys.executable, str(COMPOSER),
            "--level", "lkg",
            "--book", "logical-thinking-adventures",
            "--page-id", page_id,
            "--illustration", str(illustration),
            "--logo", str(args.logo),
            "--output", str(output),
            "--evidence-output", str(evidence),
        ], cwd=ROOT, capture_output=True, text=True)
        if process.returncode == 0:
            results.append({"page_id": page_id, "status": "GENERATED", "output": str(output)})
        else:
            results.append({"page_id": page_id, "status": "FAILED", "reason": (process.stderr or process.stdout).strip()})
            if args.fail_fast:
                break

    summary = {
        "expected_pages": len(expected),
        "generated": sum(r["status"] == "GENERATED" for r in results),
        "failed": sum(r["status"] == "FAILED" for r in results),
        "missing": [r["page_id"] for r in results if r["status"] == "MISSING_ILLUSTRATION"],
        "duplicates": duplicates,
        "status": "TEST_CANDIDATE",
        "results": results,
    }
    summary_path = args.evidence_dir / "book-render-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("expected_pages", "generated", "failed", "missing", "duplicates", "status")}, indent=2))
    print(f"Summary: {summary_path}")
    return 0 if summary["failed"] == 0 and not summary["missing"] and not duplicates else 2


if __name__ == "__main__":
    raise SystemExit(main())
