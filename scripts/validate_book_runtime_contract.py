#!/usr/bin/env python3
"""Validate one BCube book runtime contract and fail on any renderable gap.

READY pages must prove that their illustration prompt, output filename, named
crop manifest, layout and execution prompt were compiled from the same source
spreadsheet row.
"""
from __future__ import annotations

import argparse
import hashlib
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


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def validate_alignment(page_id: str, page: dict[str, Any]) -> None:
    illustration = page.get("illustration", {})
    mechanics = page.get("mechanics", {})
    layout = page.get("layout", {})
    validation = page.get("validation", {})
    lineage = page.get("source_lineage", {})
    prompt = str(illustration.get("prompt") or "").strip()
    execution = str(mechanics.get("page_execution_prompt") or "").strip()
    filename = str(illustration.get("source_asset") or "").strip()
    template = str(layout.get("template") or "").strip()
    crops = illustration.get("asset_crops")
    assets = illustration.get("assets")
    if not prompt:
        raise ValueError(f"{page_id}: exact illustration prompt is missing")
    if not execution:
        raise ValueError(f"{page_id}: exact page execution prompt is missing")
    if not filename:
        raise ValueError(f"{page_id}: illustration output filename is missing")
    if not template or template == "CONTRACT_REQUIRED":
        raise ValueError(f"{page_id}: page-specific asset layout is missing")
    if not isinstance(crops, dict) or not crops:
        raise ValueError(f"{page_id}: named crop manifest is missing")
    if not isinstance(assets, list) or set(assets) != set(crops):
        raise ValueError(f"{page_id}: contract assets do not exactly match illustration crop names")
    expected_crop_hash = digest(json.dumps(crops, sort_keys=True, separators=(",", ":")))
    if mechanics.get("crop_manifest_sha256") != expected_crop_hash:
        raise ValueError(f"{page_id}: crop manifest hash mismatch")
    if illustration.get("prompt_sha256") != digest(prompt):
        raise ValueError(f"{page_id}: illustration prompt hash mismatch")
    if lineage.get("illustration_prompt_sha256") != digest(prompt):
        raise ValueError(f"{page_id}: source-lineage illustration prompt hash mismatch")
    if lineage.get("execution_prompt_sha256") != digest(execution):
        raise ValueError(f"{page_id}: source-lineage execution prompt hash mismatch")
    if validation.get("illustration_contract_aligned") is not True:
        raise ValueError(f"{page_id}: illustration_contract_aligned must be true")


def validate(path: Path, require_all_ready: bool) -> dict[str, Any]:
    loader = load_module()
    contract = load_json(path)
    if contract.get("allow_fallback") is not False:
        raise ValueError("Book contract must set allow_fallback=false")
    alignment = contract.get("illustration_alignment")
    if not isinstance(alignment, dict) or not alignment.get("workbook_sha256"):
        raise ValueError("Book contract must identify the authoritative illustration workbook and SHA-256")
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
            validate_alignment(page_id, page)
            ready.append(page_id)
        except Exception as exc:
            invalid[page_id] = str(exc)
    result = {
        "contract": str(path),
        "page_count": len(pages),
        "ready_count": len(ready),
        "blocked_count": len(blocked),
        "invalid_count": len(invalid),
        "illustration_aligned_count": len(ready),
        "ready_pages": ready,
        "blocked_pages": blocked,
        "invalid_pages": invalid,
        "all_ready": not blocked and not invalid,
    }
    if invalid or (require_all_ready and blocked):
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
