#!/usr/bin/env python3
"""Validate one BCube book runtime contract and fail on any renderable gap."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOADER = ROOT / "bcube-publishing-sdk/runtime/load_book_contract.py"


def load_module():
    spec = importlib.util.spec_from_file_location("bcube_runtime_loader", LOADER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {LOADER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def validate(path: Path, require_all_ready: bool) -> dict[str, Any]:
    loader = load_module()
    contract = load_json(path)
    if contract.get("allow_fallback") is not False:
        raise ValueError("Book contract must set allow_fallback=false")
    pages = contract.get("pages")
    if not isinstance(pages, dict) or not pages:
        raise ValueError("Book contract contains no pages")

    ready: list[str] = []
    blocked: dict[str, list[str]] = {}
    invalid: dict[str, str] = {}
    seen_physical: dict[int, str] = {}

    for page_id, page in pages.items():
        if not isinstance(page, dict):
            invalid[page_id] = "Page entry must be an object"
            continue
        physical = page.get("identity", {}).get("physical_page")
        if isinstance(physical, int):
            if physical in seen_physical:
                invalid[page_id] = f"Duplicate physical page with {seen_physical[physical]}"
                continue
            seen_physical[physical] = page_id
        status = page.get("validation", {}).get("status")
        if status == "BLOCKED":
            blocked[page_id] = list(page.get("validation", {}).get("blocking_reasons") or [])
            continue
        try:
            loader.validate_page_contract(page_id, page)
            ready.append(page_id)
        except Exception as exc:  # validator must report every page, not stop at first
            invalid[page_id] = str(exc)

    result = {
        "contract": str(path),
        "page_count": len(pages),
        "ready_count": len(ready),
        "blocked_count": len(blocked),
        "invalid_count": len(invalid),
        "ready_pages": ready,
        "blocked_pages": blocked,
        "invalid_pages": invalid,
        "all_ready": not blocked and not invalid,
    }
    if invalid:
        raise ValueError(json.dumps(result, indent=2))
    if require_all_ready and blocked:
        raise ValueError(json.dumps(result, indent=2))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--require-all-ready", action="store_true")
    args = parser.parse_args()
    print(json.dumps(validate(args.contract, args.require_all_ready), indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"BCube book runtime validation FAIL: {exc}")
        raise SystemExit(2)
