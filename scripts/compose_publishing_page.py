#!/usr/bin/env python3
"""Deterministic BCube publishing-page compositor.

This command deliberately does not call an image model. It accepts an already
approved illustration layer and composites only repository-controlled assets,
text and geometry. The page-specific layout implementation is supplied by a
JSON composition manifest and must reference a registered page type.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "design-system/template-lock/reference-registry.json"


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def validate_manifest(manifest: dict) -> list[str]:
    errors: list[str] = []
    registry = load(REGISTRY)
    page_type = manifest.get("page_type")
    if page_type not in registry.get("page_types", {}):
        errors.append(f"unregistered page_type: {page_type}")
    if manifest.get("canvas") != {"width_px": 2480, "height_px": 3508, "dpi": 300}:
        errors.append("canvas must be exactly 2480x3508 at 300 DPI")
    if manifest.get("generation_scope") != "illustration-layer-only":
        errors.append("generation_scope must be illustration-layer-only")
    if manifest.get("full_page_ai_generation") is not False:
        errors.append("full_page_ai_generation must be false")
    for key in ("page_id", "page_type", "official_assets", "text_layers", "geometry", "output"):
        if key not in manifest:
            errors.append(f"missing required field: {key}")
    assets = manifest.get("official_assets", [])
    if not isinstance(assets, list) or any(not isinstance(a, dict) or "path" not in a or "sha256" not in a for a in assets):
        errors.append("official_assets must contain path and sha256 for each deterministic asset")
    text = manifest.get("text_layers", [])
    if not isinstance(text, list) or any(not isinstance(t, dict) or "text" not in t or "box" not in t for t in text):
        errors.append("text_layers must contain editable text and exact boxes")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    manifest = load(args.manifest)
    errors = validate_manifest(manifest)
    if errors:
        print(json.dumps({"status": "FAIL", "errors": errors}, indent=2), file=sys.stderr)
        return 1
    if args.validate_only:
        print(json.dumps({"status": "PASS", "page_id": manifest["page_id"], "mode": "validate-only"}))
        return 0
    print(
        "Composition manifest passed preflight. Rendering must be performed by "
        "the approved deterministic renderer; direct full-page AI generation is prohibited.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
