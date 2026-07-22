#!/usr/bin/env python3
"""Run deterministic BCube Nursery cover composition and evidence-based QA.

This command never invokes an image generator. It accepts an already-reviewed,
illustration-only candidate and refuses contaminated illustration evidence.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_nursery_cover.py"
VALIDATOR = ROOT / "scripts/validate_rendered_page.py"


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True, help="Cover page-data JSON")
    parser.add_argument("--output", type=Path, required=True, help="Final PNG output")
    parser.add_argument("--evidence", type=Path, required=True, help="Evidence manifest output")
    parser.add_argument("--report", type=Path, required=True, help="Render QA report output")
    args = parser.parse_args()

    run([
        sys.executable, str(COMPOSER),
        "--data", str(args.data),
        "--output", str(args.output),
        "--evidence-output", str(args.evidence),
    ])
    run([
        sys.executable, str(VALIDATOR),
        "--artifact", str(args.output),
        "--manifest", str(args.evidence),
        "--output", str(args.report),
    ])
    print(f"BCube cover pipeline PASS: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
