#!/usr/bin/env python3
"""Expand deterministic cover evidence into exact component instances."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.evidence.read_text(encoding="utf-8"))
    components = [
        item for item in data.get("component_evidence", [])
        if item.get("component") not in {"six_skill_capsules", "five_core_pillars"}
    ]

    skill_region = [1810, 1080, 2380, 2160]
    y, height, gap = skill_region[1], 156, 28
    for _ in range(6):
        bounds = [skill_region[0], y, skill_region[2], y + height]
        components.append({
            "component": "six_skill_capsules",
            "bounds": bounds,
            "template_bounds": bounds,
            "allow_overlap": False
        })
        y += height + gap

    for center_x in [280, 760, 1240, 1720, 2200]:
        bounds = [center_x - 190, 2860, center_x + 190, 3090]
        components.append({
            "component": "five_core_pillars",
            "bounds": bounds,
            "template_bounds": bounds,
            "allow_overlap": False
        })

    data["component_evidence"] = components
    args.evidence.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"finalized strict component evidence: {args.evidence}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
