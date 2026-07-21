#!/usr/bin/env python3
"""BCube Page Composer™ scaffold.

This module validates the deterministic publishing inputs before rendering.
Binary composition will be enabled after approved logo, mascot, font, badge,
and illustration assets are added to the repository or supplied at runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parents[1]
ASSET_REGISTRY = BASE / "assets" / "registry.json"
LAYOUT = BASE / "design-system" / "layout.json"
TEMPLATE = BASE / "templates" / "interior-page.json"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_page_spec(spec: dict[str, Any], template: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in template["required_content"]:
        if spec.get(field) in (None, ""):
            errors.append(f"missing required field: {field}")
    page_number = spec.get("page_number")
    if page_number is not None and not 1 <= int(page_number) <= 44:
        errors.append("page_number must be between 1 and 44")
    illustration = Path(str(spec.get("illustration_path", "")))
    if str(illustration) and not illustration.exists():
        errors.append(f"illustration not found: {illustration}")
    return errors


def build_manifest(spec: dict[str, Any]) -> dict[str, Any]:
    registry = load_json(ASSET_REGISTRY)
    layout = load_json(LAYOUT)
    template = load_json(TEMPLATE)
    errors = validate_page_spec(spec, template)

    fixed_assets: dict[str, Any] = {}
    logo = Path(registry["assets"]["logo"]["path"])
    fixed_assets["logo"] = {
        "path": str(logo),
        "exists": logo.exists(),
        "sha256": sha256(logo) if logo.exists() else None,
    }

    illustration_path = Path(str(spec.get("illustration_path", "")))
    manifest = {
        "schema_version": "1.0.0",
        "engine": "BCube Page Composer",
        "template_id": template["template_id"],
        "page": {
            "title": spec.get("page_title"),
            "number": spec.get("page_number"),
            "illustration_path": str(illustration_path),
            "illustration_sha256": sha256(illustration_path) if illustration_path.exists() else None,
        },
        "fixed_assets": fixed_assets,
        "geometry": layout["page"],
        "regions": template["regions"],
        "validation": {
            "errors": errors,
            "decision": "READY" if not errors and fixed_assets["logo"]["exists"] else "BLOCKED",
        },
    }
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate one BCube page-composition request.")
    parser.add_argument("--spec", required=True, help="JSON page specification")
    parser.add_argument("--manifest", required=True, help="Output manifest path")
    args = parser.parse_args()

    spec = load_json(Path(args.spec))
    manifest = build_manifest(spec)
    output = Path(args.manifest)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["validation"], indent=2))
    if manifest["validation"]["decision"] != "READY":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
