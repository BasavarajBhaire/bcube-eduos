#!/usr/bin/env python3
"""Fail-closed dispatcher for BCube book runtime contracts.

The legacy, modern-generic and archetype fallback renderers are intentionally
not reachable from this entry point. A page renders only when its book runtime
contract exists, validates, and has an exact mechanic renderer.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RUNTIME_COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_runtime_learning_page.py"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def resolve(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def level_from_page_id(page_id: str) -> str:
    parts = page_id.split("-")
    if len(parts) < 3:
        raise ValueError(f"Invalid page ID: {page_id}")
    value = parts[1].lower()
    if value not in {"nursery", "lkg", "ukg"}:
        raise ValueError(f"Unsupported level in page ID: {page_id}")
    return value


def compose(contract_path: Path, output: Path, evidence_output: Path) -> None:
    generated = load(contract_path)
    identity = generated.get("identity")
    assets = generated.get("assets")
    if not isinstance(identity, dict) or not isinstance(assets, dict):
        raise ValueError("Generated learning contract is missing identity or assets")

    page_id = str(identity.get("page_id") or "")
    book_slug = str(identity.get("book_slug") or "")
    illustration = str(assets.get("illustration_path") or "")
    logo = str(assets.get("official_logo_path") or "")
    if not page_id or not book_slug or not illustration or not logo:
        raise ValueError("Runtime dispatch requires page_id, book_slug, illustration_path and official_logo_path")

    command = [
        sys.executable,
        str(RUNTIME_COMPOSER),
        "--level", level_from_page_id(page_id),
        "--book", book_slug,
        "--page-id", page_id,
        "--illustration", str(resolve(illustration)),
        "--logo", str(resolve(logo)),
        "--output", str(output),
        "--evidence-output", str(evidence_output),
    ]
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="BCube runtime-contract learning page dispatcher")
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    args = parser.parse_args()
    compose(args.contract, args.output, args.evidence_output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"BCube Runtime Contract Render FAIL: {exc}", file=sys.stderr)
        raise SystemExit(2)
