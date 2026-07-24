#!/usr/bin/env python3
"""Run the BCube Phase 2 universal interior activity-page pipeline."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "bcube-publishing-sdk/books/cover-books.json"
VALIDATOR = ROOT / "bcube-publishing-sdk/validators/validate_activity_inputs.py"
COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_activity_page.py"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def resolve_book(level: str, slug: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    registry = load(REGISTRY)
    level_data = registry.get("levels", {}).get(level)
    if not isinstance(level_data, dict):
        raise ValueError(f"Unknown level {level!r}")
    book = level_data.get("books", {}).get(slug)
    if not isinstance(book, dict):
        available = ", ".join(sorted(level_data.get("books", {})))
        raise ValueError(f"Unknown {level.upper()} book {slug!r}. Registered books: {available}")
    return registry, level_data, book


def valid_image(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        with Image.open(path) as image:
            image.verify()
        return True
    except Exception:
        return False


def find_asset(candidates: list[str], label: str) -> Path:
    for candidate in candidates:
        path = ROOT / candidate
        if valid_image(path):
            return path
    raise FileNotFoundError(f"No valid {label} asset found")


def repo_relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def stage_illustration(source: Path, page_id: str) -> Path:
    source = source.expanduser().resolve()
    if not valid_image(source):
        raise FileNotFoundError(f"Illustration is missing or unreadable: {source}")
    destination = ROOT / "production-renders/activity/illustrations" / f"{page_id}.png"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        image.convert("RGB").save(destination, "PNG", dpi=(300, 300))
    return destination


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def build_data(args: argparse.Namespace) -> tuple[Path, Path, Path, Path]:
    registry, level_data, book = resolve_book(args.level, args.book)
    shared = registry["shared"]
    prefix = book["prefix"]
    page_id = args.page_id or f"{prefix}-{level_data['id_level']}-V4-P{args.physical_page:03d}"
    illustration = stage_illustration(args.illustration, page_id)
    logo = find_asset(list(shared["official_logo_candidates"]), "official BCube logo")
    data = {
        "page_id": page_id,
        "book_key": f"{args.level}/{args.book}",
        "book_title": " ".join(book["title_lines"]),
        "book_title_lines": book["title_lines"],
        "level": level_data["display_level"],
        "age": level_data["age"],
        "page_number": args.page_number,
        "physical_page": args.physical_page,
        "activity_type": args.activity_type,
        "title": args.title,
        "learning_objective": args.objective,
        "student_instruction": args.instruction,
        "teacher_prompt": args.teacher_prompt,
        "parent_prompt": args.parent_prompt,
        "illustration_path": repo_relative(illustration),
        "official_logo_path": repo_relative(logo),
    }
    data_path = ROOT / "production-renders/activity/page-data" / f"{page_id}.json"
    output = ROOT / "production-renders/activity/pages" / f"{page_id}.png"
    evidence = ROOT / "production-renders/activity/evidence" / f"{page_id}.json"
    report = ROOT / "validation/rendered-pages" / f"{page_id}.activity-input.json"
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return data_path, output, evidence, report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BCube Phase 2 universal activity-page pipeline")
    parser.add_argument("--level", choices=["nursery", "lkg", "ukg"], required=True)
    parser.add_argument("--book", required=True)
    parser.add_argument("--illustration", type=Path, required=True)
    parser.add_argument("--physical-page", type=int, required=True)
    parser.add_argument("--page-number", type=int, required=True)
    parser.add_argument("--page-id")
    parser.add_argument("--activity-type", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--instruction", required=True)
    parser.add_argument("--teacher-prompt", required=True)
    parser.add_argument("--parent-prompt", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data, output, evidence, report = build_data(args)
    for path in (output, evidence, report):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.unlink(missing_ok=True)
    run([sys.executable, str(VALIDATOR), "--data", str(data), "--output", str(report)])
    run([sys.executable, str(COMPOSER), "--data", str(data), "--output", str(output),
         "--evidence-output", str(evidence)])
    print(json.dumps({
        "engine": "BCube Publishing Engine Phase 2",
        "state": "REVIEW_CANDIDATE",
        "page_data": str(data),
        "page": str(output),
        "input_qa": str(report),
        "composition_evidence": str(evidence),
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(f"BCube Phase 2 FAIL: {exc}", file=sys.stderr)
        raise SystemExit(2)
