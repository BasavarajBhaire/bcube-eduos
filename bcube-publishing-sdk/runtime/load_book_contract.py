#!/usr/bin/env python3
"""Load one page from a self-contained BCube book runtime contract.

Runtime rendering must use this loader. It never infers page mechanics and never
falls back to a generic layout.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "runtime-contracts/manifest.json"


class RuntimeContractError(RuntimeError):
    pass


class BookContractNotFound(RuntimeContractError):
    pass


class PageContractRequired(RuntimeContractError):
    pass


class InvalidRuntimeContract(RuntimeContractError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise BookContractNotFound(str(path))
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise InvalidRuntimeContract(f"{path} must contain a JSON object")
    return value


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise InvalidRuntimeContract(message)


def validate_page_contract(page_id: str, page: dict[str, Any]) -> None:
    required = {
        "identity",
        "learning",
        "activity",
        "illustration",
        "mechanics",
        "guidance",
        "layout",
        "validation",
    }
    missing = required - set(page)
    _require(not missing, f"{page_id}: missing sections {sorted(missing)}")
    _require(page["identity"].get("page_id") == page_id, f"{page_id}: identity mismatch")
    _require(bool(page["learning"].get("objective")), f"{page_id}: objective required")
    _require(bool(page["learning"].get("instruction")), f"{page_id}: instruction required")
    _require(bool(page["activity"].get("mechanic")), f"{page_id}: exact mechanic required")
    _require(bool(page["illustration"].get("source_asset")), f"{page_id}: source asset required")
    _require(page["illustration"].get("artwork_only") is True, f"{page_id}: artwork_only must be true")
    assets = page["illustration"].get("assets")
    crops = page["illustration"].get("asset_crops")
    _require(isinstance(assets, list) and assets, f"{page_id}: named assets required")
    _require(isinstance(crops, dict) and crops, f"{page_id}: named crop manifest required")
    _require(set(assets) == set(crops), f"{page_id}: assets and crop names must match exactly")
    for name, crop in crops.items():
        _require(isinstance(crop, list) and len(crop) == 4, f"{page_id}: crop {name!r} must have four values")
        _require(all(isinstance(v, (int, float)) and 0 <= v <= 1 for v in crop), f"{page_id}: crop {name!r} must be normalised")
        _require(crop[0] < crop[2] and crop[1] < crop[3], f"{page_id}: crop {name!r} is invalid")
    layout = page["layout"]
    _require(layout.get("parent_panel") is False, f"{page_id}: parent panel prohibited")
    _require(layout.get("home_connection") is False, f"{page_id}: Home Connection prohibited")
    _require(layout.get("generic_response_panel") is False, f"{page_id}: generic response panel prohibited")
    validation = page["validation"]
    _require(validation.get("allow_fallback") is False, f"{page_id}: fallback prohibited")
    _require(validation.get("status") == "READY", f"{page_id}: contract is not READY")


def load_page_contract(*, level: str, book_slug: str, page_id: str) -> dict[str, Any]:
    manifest = _load_json(MANIFEST)
    _require(manifest.get("allow_fallback") is False, "Root manifest must prohibit fallback")
    level_key = level.strip().lower()
    books = manifest.get("levels", {}).get(level_key, {}).get("books", {})
    relative = books.get(book_slug)
    if not relative:
        raise BookContractNotFound(f"No runtime contract registered for {level}/{book_slug}")
    book = _load_json(ROOT / "runtime-contracts" / relative)
    _require(book.get("allow_fallback") is False, f"{relative}: fallback must be false")
    page = book.get("pages", {}).get(page_id)
    if not isinstance(page, dict):
        raise PageContractRequired(f"{page_id}: independent runtime contract required")
    validate_page_contract(page_id, page)
    return page
