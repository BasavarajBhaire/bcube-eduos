#!/usr/bin/env python3
"""Compatibility entry point that routes activity pages into Learning Page Contract V2."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LEARNING_PIPELINE = ROOT / "scripts/run_bcube_learning_pipeline.py"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def manifest_path(level: str, slug: str) -> Path:
    candidates = [
        ROOT / "production-prompts" / slug / level / "v4" / "release-manifest.json",
        ROOT / "production-prompts" / slug / level / "V4" / "release-manifest.json",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"No finalized V4 release manifest found for {level}/{slug}")


def source_page_json(level: str, slug: str, physical_page: int) -> Path:
    manifest = manifest_path(level, slug)
    data = load(manifest)
    for row in data.get("pages", []):
        if isinstance(row, dict) and row.get("physical") == physical_page:
            relative = row.get("json")
            if not isinstance(relative, str) or not relative:
                raise ValueError(f"Physical page {physical_page} has no JSON source in {manifest}")
            source = (manifest.parent / relative).resolve()
            if manifest.parent.resolve() not in source.parents or not source.is_file():
                raise ValueError(f"Invalid page source for physical page {physical_page}: {relative}")
            return source
    raise ValueError(f"Physical page {physical_page} is not registered for {level}/{slug}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="BCube activity compatibility wrapper for Learning Page Contract V2"
    )
    parser.add_argument("--level", choices=["nursery", "lkg", "ukg"], required=True)
    parser.add_argument("--book", required=True)
    parser.add_argument("--illustration", type=Path, required=True)
    parser.add_argument("--physical-page", type=int, required=True)
    parser.add_argument("--page-number", type=int, required=True)
    parser.add_argument("--page-id")
    parser.add_argument("--activity-type")
    parser.add_argument("--title")
    parser.add_argument("--objective")
    parser.add_argument("--instruction")
    parser.add_argument("--teacher-prompt")
    parser.add_argument("--parent-prompt")
    parser.add_argument("--source-page-json", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source_page_json or source_page_json(
        args.level,
        args.book,
        args.physical_page,
    )
    command = [
        sys.executable,
        str(LEARNING_PIPELINE),
        "--level",
        args.level,
        "--book",
        args.book,
        "--illustration",
        str(args.illustration),
        "--source-page-json",
        str(source),
        "--physical-page",
        str(args.physical_page),
        "--page-number",
        str(args.page_number),
    ]
    if args.page_id:
        command += ["--page-id", args.page_id]
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)
    print(
        json.dumps(
            {
                "engine": "BCube Publishing Engine Learning Pages V2",
                "state": "REVIEW_CANDIDATE",
                "legacy_activity_fields_ignored": True,
                "source_page_json": str(source),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"BCube Learning Page compatibility FAIL: {exc}", file=sys.stderr)
        raise SystemExit(2)
