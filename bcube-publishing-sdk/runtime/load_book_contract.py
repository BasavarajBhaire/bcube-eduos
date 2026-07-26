#!/usr/bin/env python3
"""Load one page from a self-contained BCube book runtime contract.

The loader supports both the original V1 page shape and the V2 page shape used
by the Early Maths full-book test renderer. It never infers a missing page and
never falls back to a generic layout.
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


def _valid_crop(crop: Any) -> bool:
    if isinstance(crop, list) and len(crop) == 4:
        return all(isinstance(v, (int, float)) and 0 <= v <= 1 for v in crop) and crop[0] < crop[2] and crop[1] < crop[3]
    if isinstance(crop, dict) and {"x", "y", "w", "h"} <= set(crop):
        values = [crop["x"], crop["y"], crop["w"], crop["h"]]
        if not all(isinstance(v, (int, float)) for v in values):
            return False
        x, y, w, h = map(float, values)
        return 0 <= x < 1 and 0 <= y < 1 and 0 < w <= 1 and 0 < h <= 1 and x + w <= 1.000001 and y + h <= 1.000001
    return False


def validate_page_contract(page_id: str, page: dict[str, Any]) -> None:
    required = {"identity", "learning", "activity", "illustration", "guidance", "layout", "validation"}
    missing = required - set(page)
    _require(not missing, f"{page_id}: missing sections {sorted(missing)}")
    _require(page["identity"].get("page_id") == page_id, f"{page_id}: identity mismatch")
    _require(bool(page["learning"].get("objective")), f"{page_id}: objective required")
    _require(bool(page["learning"].get("instruction")), f"{page_id}: instruction required")
    activity = page["activity"]
    _require(bool(activity.get("mechanic")), f"{page_id}: exact mechanic required")
    _require(bool(activity.get("render_kind") or page.get("mechanics")), f"{page_id}: render kind or V1 mechanics required")

    illustration = page["illustration"]
    _require(bool(illustration.get("source_asset")), f"{page_id}: source asset required")
    if "artwork_only" in illustration:
        _require(illustration.get("artwork_only") is True, f"{page_id}: artwork_only must be true")
    assets = illustration.get("assets")
    crops = illustration.get("asset_crops")
    _require(isinstance(assets, list) and assets, f"{page_id}: named assets required")
    _require(isinstance(crops, dict) and crops, f"{page_id}: named crop manifest required")
    _require(set(assets) == set(crops), f"{page_id}: assets and crop names must match exactly")
    for name, crop in crops.items():
        _require(_valid_crop(crop), f"{page_id}: crop {name!r} is invalid")

    if "mechanics" in activity:
        _require(isinstance(activity["mechanics"], dict) and activity["mechanics"], f"{page_id}: activity.mechanics required")
    else:
        _require(isinstance(page.get("mechanics"), dict) and page["mechanics"], f"{page_id}: V1 mechanics required")

    layout = page["layout"]
    _require(layout.get("parent_panel") is False, f"{page_id}: parent panel prohibited")
    _require(layout.get("home_connection") is False, f"{page_id}: Home Connection prohibited")
    _require(layout.get("generic_response_panel") is False, f"{page_id}: generic response panel prohibited")
    validation = page["validation"]
    _require(validation.get("allow_fallback") is False, f"{page_id}: fallback prohibited")
    _require(validation.get("status") == "READY", f"{page_id}: contract is not READY")
    if "illustration_contract_aligned" in validation:
        _require(validation.get("illustration_contract_aligned") is True, f"{page_id}: illustration contract is not aligned")


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
