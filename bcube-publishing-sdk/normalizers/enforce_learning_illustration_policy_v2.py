#!/usr/bin/env python3
"""Enforce illustration-only and official-character separation for Learning Page Contract V2."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

OFFICIAL_STAR_ZONE = "clear lower-right official Star overlay zone"
STAR_PROHIBITION = "No generated, redrawn, traced, substituted, or embedded Star mascot inside the uploaded illustration."
TEXT_PROHIBITION = "No visible words, letters, numbers, labels, answers, logo, page border, or worksheet mechanics inside the illustration."
LAYOUT_PROHIBITION = "No full-page layout, instruction panel, response line, answer box, matching line, or decorative frame inside the illustration."


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def clean(value: Any) -> str:
    return " ".join(str(value or "").split()).strip()


def unique(values: list[Any]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = clean(value)
        key = text.casefold()
        if text and key not in seen:
            seen.add(key)
            result.append(text)
    return result


def remove_star_objects(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [clean(value) for value in values if clean(value) and "star" not in clean(value).casefold()]


def enforce_policy(contract: dict[str, Any]) -> dict[str, Any]:
    illustration = contract.get("illustration")
    assets = contract.get("assets")
    lineage = contract.get("source_lineage")
    if not isinstance(illustration, dict) or not isinstance(assets, dict) or not isinstance(lineage, dict):
        raise ValueError("Learning contract lacks illustration, assets, or source_lineage data")
    policy = clean(illustration.get("star_policy"))
    if policy not in {"prohibited", "official-asset-separate", "not-required"}:
        raise ValueError(f"Unsupported Star policy: {policy!r}")

    illustration["artwork_only"] = True
    illustration["no_visible_text"] = True
    illustration["no_logo"] = True
    illustration["no_page_layout"] = True
    illustration["required_objects"] = remove_star_objects(illustration.get("required_objects"))
    illustration["forbidden_objects"] = unique(
        [
            *(illustration.get("forbidden_objects") if isinstance(illustration.get("forbidden_objects"), list) else []),
            STAR_PROHIBITION,
            TEXT_PROHIBITION,
            LAYOUT_PROHIBITION,
        ]
    )

    protected = illustration.get("protected_response_zones")
    protected_values = protected if isinstance(protected, list) else []
    changes: list[str] = []
    if policy == "official-asset-separate":
        if not assets.get("official_star_path"):
            raise ValueError("official-asset-separate requires assets.official_star_path")
        protected_values = unique([*protected_values, OFFICIAL_STAR_ZONE])
        scene = clean(illustration.get("scene"))
        overlay_sentence = (
            "Reserve a clear lower-right area for the official Star asset overlay; do not draw Star in the artwork."
        )
        if overlay_sentence.casefold() not in scene.casefold():
            illustration["scene"] = clean(f"{scene} {overlay_sentence}")
            changes.append("illustration.scene.star-overlay-reservation")
    else:
        assets.pop("official_star_path", None)
    illustration["protected_response_zones"] = unique(protected_values)
    lineage["illustration_policy_enforcer"] = "learning-illustration-policy-v2.0"
    lineage["illustration_policy_changes"] = changes
    return contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    contract = load(args.contract)
    enforced = enforce_policy(contract)
    output = args.output or args.contract
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(enforced, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "ILLUSTRATION_POLICY_ENFORCED",
                "page_id": enforced["identity"]["page_id"],
                "star_policy": enforced["illustration"]["star_policy"],
                "output": str(output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"BCube learning illustration-policy enforcement FAIL: {exc}", file=__import__("sys").stderr)
        raise SystemExit(2)
