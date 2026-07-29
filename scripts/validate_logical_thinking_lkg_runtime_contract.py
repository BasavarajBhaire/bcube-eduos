#!/usr/bin/env python3
"""Validate the Logical Thinking LKG runtime against individual page sources."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "runtime-contracts/lkg/logical-thinking-adventures.json"
PAGE_DIR = ROOT / "production-prompts/logical-thinking-adventures/lkg/v4/pages"
ILLUSTRATIONS = ROOT / "production-prompts/logical-thinking-adventures/lkg/v4/phase2-illustration-prompts.json"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object expected: {path}")
    return value


def page_sources() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in PAGE_DIR.glob("*.json"):
        source = load_json(path)
        page_id = str(source.get("prompt_id") or "").strip()
        if page_id:
            if page_id in result:
                raise ValueError(f"Duplicate individual page source for {page_id}")
            result[page_id] = path
    return result


def main() -> int:
    contract = load_json(CONTRACT)
    illustration_pack = load_json(ILLUSTRATIONS)
    illustration_pages = illustration_pack.get("pages")
    runtime_pages = contract.get("pages")
    if not isinstance(illustration_pages, dict) or not isinstance(runtime_pages, dict):
        raise ValueError("Illustration and runtime contracts must contain page objects")

    expected = [f"LT-LKG-V4-P{n:03d}" for n in range(8, 44)]
    sources = page_sources()
    errors: dict[str, list[str]] = {}

    if contract.get("allow_fallback") is not False:
        raise ValueError("Book contract must disable fallback")
    if contract.get("status") != "TEST_CANDIDATE":
        raise ValueError("Book contract must remain TEST_CANDIDATE")

    for page_id in expected:
        page_errors: list[str] = []
        runtime = runtime_pages.get(page_id)
        artwork = illustration_pages.get(page_id)
        source_path = sources.get(page_id)
        if not isinstance(runtime, dict):
            page_errors.append("runtime page missing")
        if not isinstance(artwork, dict):
            page_errors.append("illustration page missing")
        if source_path is None:
            page_errors.append("individual V4 page JSON missing")
        if page_errors:
            errors[page_id] = page_errors
            continue

        source = load_json(source_path)
        identity = runtime.get("identity", {})
        illustration = runtime.get("illustration", {})
        activity = runtime.get("activity", {})
        layout = runtime.get("layout", {})
        validation = runtime.get("validation", {})
        lineage = runtime.get("source_lineage", {})

        if identity.get("title") != source.get("page", {}).get("title"):
            page_errors.append("title does not match individual page JSON")
        if identity.get("physical_page") != int(page_id.rsplit("P", 1)[1]):
            page_errors.append("physical page does not match page ID")
        if illustration.get("source_asset") != artwork.get("output_filename"):
            page_errors.append("source asset does not match illustration contract")
        if illustration.get("assets") != artwork.get("asset_names"):
            page_errors.append("asset order does not match illustration contract")
        if illustration.get("asset_crops") != artwork.get("asset_crops"):
            page_errors.append("crop map does not match illustration contract")
        if illustration.get("prompt") != artwork.get("prompt"):
            page_errors.append("illustration prompt does not match source contract")
        if not activity.get("mechanic") or not activity.get("render_kind") or not activity.get("response_mode"):
            page_errors.append("page-specific activity contract is incomplete")
        if not layout.get("template"):
            page_errors.append("page-specific layout template is missing")
        if any(layout.get(key) is not False for key in ("parent_panel", "home_connection", "generic_response_panel")):
            page_errors.append("prohibited generic panels are enabled")
        if validation.get("status") != "READY" or validation.get("allow_fallback") is not False:
            page_errors.append("runtime page is not READY/fail-closed")
        if validation.get("visual_status") != "TEST_CANDIDATE":
            page_errors.append("visual status must remain TEST_CANDIDATE")
        if lineage.get("source_file") != source_path.relative_to(ROOT).as_posix():
            page_errors.append("individual source lineage is incorrect")
        if lineage.get("illustration_contract_file") != ILLUSTRATIONS.relative_to(ROOT).as_posix():
            page_errors.append("illustration source lineage is incorrect")
        if page_errors:
            errors[page_id] = page_errors

    extra_runtime = sorted(set(runtime_pages) - set(expected))
    extra_illustrations = sorted(set(illustration_pages) - set(expected))
    result = {
        "contract": str(CONTRACT),
        "expected_pages": len(expected),
        "runtime_pages": len(runtime_pages),
        "validated_pages": len(expected) - len(errors),
        "invalid_pages": errors,
        "extra_runtime_pages": extra_runtime,
        "extra_illustration_pages": extra_illustrations,
        "status": "PASS" if not errors and not extra_runtime and not extra_illustrations else "FAIL",
        "visual_status": "TEST_CANDIDATE",
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"Logical Thinking LKG runtime validation FAIL: {exc}")
        raise SystemExit(2)
