#!/usr/bin/env python3
"""Build a deterministic composition manifest from BCube page data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("page_data", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    page = load(args.page_data)
    templates = load(SDK / "templates/publishing-page-templates.json")
    components = load(SDK / "components/component-registry.json")

    page_type = page.get("page_type")
    if page_type not in templates["templates"]:
        raise SystemExit(f"Unsupported page type: {page_type}")

    contract = templates["templates"][page_type]
    manifest = {
        "manifest_version": "pre-print-pilot",
        "prompt_id": page["prompt_id"],
        "page_type": page_type,
        "canvas": templates["canvas"],
        "template_contract": contract,
        "component_registry_version": components["registry_version"],
        "composition_mode": "deterministic",
        "ai_scope": "illustration_layer_only",
        "book": page["book"],
        "level": page["level"],
        "physical_page": page["physical_page"],
        "printed_page": page["printed_page"],
        "content": page["content"],
        "assets": page["assets"],
        "acceptance": {"score": 100, "critical_defects": 0, "fail_closed": True}
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
