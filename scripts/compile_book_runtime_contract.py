#!/usr/bin/env python3
"""Compile one BCube book into one self-contained runtime-contract JSON.

The compiler is intentionally fail-closed. It preserves existing READY page
contracts, creates BLOCKED entries for pages that still require exact mechanics,
and never invents a generic response layout.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class CompileError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CompileError(f"{path} must contain a JSON object")
    return value


def normalise_level(value: str) -> str:
    key = value.strip().lower()
    mapping = {"nursery": "Nursery", "lkg": "LKG", "ukg": "UKG"}
    if key not in mapping:
        raise CompileError(f"Unknown level: {value}")
    return mapping[key]


def page_number_from_id(page_id: str) -> int:
    match = re.search(r"-P(\d{3})$", page_id)
    if not match:
        raise CompileError(f"Cannot read physical page from {page_id}")
    return int(match.group(1))


def should_compile_page(source: dict[str, Any], minimum_physical_page: int) -> bool:
    page = source.get("page", {})
    physical = int(page.get("physical") or 0)
    page_type = str(page.get("type") or "").casefold()
    if physical < minimum_physical_page:
        return False
    if page_type in {"cover", "copyright", "contents", "welcome", "front_matter"}:
        return False
    return True


def blocked_page(source: dict[str, Any], source_path: Path) -> dict[str, Any]:
    page_id = str(source.get("prompt_id") or "")
    if not page_id:
        raise CompileError(f"Missing prompt_id in {source_path}")
    page = source.get("page", {})
    curriculum = source.get("curriculum", {})
    physical = int(page.get("physical") or page_number_from_id(page_id))
    printed = page.get("printed")
    return {
        "identity": {
            "page_id": page_id,
            "physical_page": physical,
            "printed_page": int(printed) if printed is not None else None,
            "title": str(page.get("title") or "").strip(),
            "page_type": str(page.get("type") or "learning_page").strip(),
        },
        "learning": {
            "objective": str(curriculum.get("objective") or "").strip(),
            "instruction": str(curriculum.get("instruction") or "").strip(),
            "expected_response": str(curriculum.get("evidence") or "").strip(),
            "model_text": None,
        },
        "activity": {
            "archetype": "CONTRACT_REQUIRED",
            "mechanic": "CONTRACT_REQUIRED",
            "response_mode": "CONTRACT_REQUIRED",
            "activity_count": 1,
        },
        "illustration": {
            "source_asset": f"{page_id}.png",
            "artwork_only": True,
            "assets": ["CONTRACT_REQUIRED"],
            "asset_crops": {"CONTRACT_REQUIRED": [0.0, 0.0, 1.0, 1.0]},
        },
        "mechanics": {
            "contract_required": True,
            "source_instruction": str(curriculum.get("instruction") or "").strip(),
            "source_scene": str(curriculum.get("scene") or "").strip(),
        },
        "guidance": {
            "teacher_cue": str(curriculum.get("teacher_facilitation") or "Page-specific teacher cue required.").strip()
        },
        "layout": {
            "template": "CONTRACT_REQUIRED",
            "parent_panel": False,
            "home_connection": False,
            "generic_response_panel": False,
        },
        "validation": {
            "allow_fallback": False,
            "status": "BLOCKED",
            "required_asset_count": 1,
            "required_response_count": 1,
            "blocking_reasons": [
                "Exact activity mechanic not yet compiled.",
                "Named crop manifest not yet approved.",
                "Page-specific layout template not yet assigned."
            ],
        },
        "source_lineage": {
            "source_prompt_id": page_id,
            "source_file": source_path.relative_to(ROOT).as_posix(),
            "compiler": "compile_book_runtime_contract.py",
        },
    }


def compile_book(args: argparse.Namespace) -> dict[str, Any]:
    level_key = args.level.strip().lower()
    level = normalise_level(args.level)
    source_dir = ROOT / "production-prompts" / args.book / level_key / "v4" / "pages"
    if not source_dir.is_dir():
        raise CompileError(f"Source page directory not found: {source_dir}")

    output = ROOT / "runtime-contracts" / level_key / f"{args.book}.json"
    existing: dict[str, Any] = {}
    if output.is_file():
        existing = load_json(output)

    pages: dict[str, Any] = dict(existing.get("pages") or {})
    source_files = sorted(source_dir.glob("*.json"))
    if not source_files:
        raise CompileError(f"No source page JSON files found in {source_dir}")

    book_title = None
    prefix = None
    discovered_ids: set[str] = set()
    for path in source_files:
        source = load_json(path)
        if not should_compile_page(source, args.minimum_physical_page):
            continue
        page_id = str(source.get("prompt_id") or "")
        discovered_ids.add(page_id)
        book = source.get("book", {})
        book_title = book_title or str(book.get("name") or "").strip()
        prefix = prefix or str(book.get("prefix") or "").strip()
        current = pages.get(page_id)
        if isinstance(current, dict) and current.get("validation", {}).get("status") == "READY":
            continue
        pages[page_id] = blocked_page(source, path)

    ordered_pages = dict(sorted(pages.items(), key=lambda item: item[1]["identity"]["physical_page"]))
    ready = sum(1 for page in ordered_pages.values() if page.get("validation", {}).get("status") == "READY")
    blocked = sum(1 for page in ordered_pages.values() if page.get("validation", {}).get("status") == "BLOCKED")

    result = {
        "contract_version": "bcube-book-runtime-contract-v1",
        "book": {
            "title": book_title or existing.get("book", {}).get("title") or args.book,
            "slug": args.book,
            "prefix": prefix or existing.get("book", {}).get("prefix") or "",
        },
        "level": level,
        "age": existing.get("age") or {"Nursery": "3+", "LKG": "4+", "UKG": "5+"}[level],
        "allow_fallback": False,
        "pages": ordered_pages,
        "compile_summary": {
            "source_page_count": len(discovered_ids),
            "runtime_page_count": len(ordered_pages),
            "ready_pages": ready,
            "blocked_pages": blocked,
            "policy": "BLOCKED pages must not render until exact mechanics, assets and layout are approved."
        },
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"output": str(output), **result["compile_summary"]}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile one self-contained BCube book runtime contract")
    parser.add_argument("--level", choices=["nursery", "lkg", "ukg"], required=True)
    parser.add_argument("--book", required=True)
    parser.add_argument("--minimum-physical-page", type=int, default=8)
    return parser.parse_args()


def main() -> int:
    summary = compile_book(parse_args())
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (CompileError, OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"BCube book runtime compile FAIL: {exc}")
        raise SystemExit(2)
