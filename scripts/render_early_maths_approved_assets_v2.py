#!/usr/bin/env python3
"""Normalise user-approved Early Maths asset names and render P009-P021.

This compatibility entry point accepts the Work Mode ZIP exactly as generated,
renames semantic filenames to the runtime contract names inside a temporary ZIP,
and delegates to render_early_maths_from_approved_assets.py.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DELEGATE = ROOT / "scripts" / "render_early_maths_from_approved_assets.py"

ALIASES: dict[str, dict[str, str]] = {
    "EM-LKG-V4-P011": {
        "less_apples_2": "row1_left",
        "more_apples_5": "row1_right",
        "more_fish_6": "row2_left",
        "less_fish_3": "row2_right",
        "less_stars_4": "row3_left",
        "more_stars_7": "row3_right",
    },
    "EM-LKG-V4-P012": {
        "equal_oranges_left_4": "row1_left",
        "equal_oranges_right_4": "row1_right",
        "unequal_butterflies_left_3": "row2_left",
        "unequal_butterflies_right_5": "row2_right",
        "equal_blocks_left_6": "row3_left",
        "equal_blocks_right_6": "row3_right",
    },
    "EM-LKG-V4-P014": {
        "join_birds_group_a_2": "p1_left",
        "join_birds_group_b_1": "p1_right",
        "join_cars_group_a_3": "p2_left",
        "join_cars_group_b_2": "p2_right",
        "join_flowers_group_a_4": "p3_left",
        "join_flowers_group_b_2": "p3_right",
    },
    "EM-LKG-V4-P015": {
        "takeaway_apples_scene": "set_5_apples",
        "takeaway_fish_scene": "set_4_fish",
        "takeaway_balloons_scene": "set_6_balloons",
    },
}


def page_id_from_parts(parts: tuple[str, ...]) -> str | None:
    for part in parts:
        if part.startswith("EM-LKG-V4-P"):
            return part
    return None


def normalise_archive(source: Path, destination: Path) -> None:
    with zipfile.ZipFile(source) as incoming, zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as outgoing:
        seen: set[str] = set()
        for info in incoming.infolist():
            if info.is_dir():
                continue
            path = PurePosixPath(info.filename)
            page_id = page_id_from_parts(path.parts)
            if page_id is None:
                continue
            page_index = path.parts.index(page_id)
            if page_index != len(path.parts) - 2:
                continue
            extension = path.suffix.lower()
            if extension not in {".png", ".jpg", ".jpeg", ".webp"}:
                continue
            source_stem = path.stem
            target_stem = ALIASES.get(page_id, {}).get(source_stem, source_stem)
            target = f"{page_id}/{target_stem}{extension}"
            if target in seen:
                raise ValueError(f"Duplicate normalised asset: {target}")
            seen.add(target)
            outgoing.writestr(target, incoming.read(info.filename))


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Early Maths using the approved Work Mode ZIP")
    parser.add_argument("--logo", type=Path, required=True)
    parser.add_argument("--asset-archive", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--pages", default="all")
    parser.add_argument("--fail-fast", action="store_true")
    args = parser.parse_args()

    archive = args.asset_archive.expanduser().resolve()
    if not archive.is_file():
        raise SystemExit(f"Approved asset archive not found: {archive}")

    with tempfile.TemporaryDirectory(prefix="bcube-normalised-early-maths-") as temp_name:
        normalised = Path(temp_name) / "early-maths-approved-normalised.zip"
        normalise_archive(archive, normalised)
        command = [
            sys.executable, str(DELEGATE),
            "--logo", str(args.logo),
            "--asset-archive", str(normalised),
            "--output-dir", str(args.output_dir),
            "--evidence-dir", str(args.evidence_dir),
            "--pages", args.pages,
        ]
        if args.fail_fast:
            command.append("--fail-fast")
        return subprocess.run(command, cwd=ROOT).returncode


if __name__ == "__main__":
    raise SystemExit(main())
