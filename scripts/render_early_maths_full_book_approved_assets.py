#!/usr/bin/env python3
"""Render Early Maths Adventures LKG P009-P044 from one approved asset ZIP.

P009-P021 use the curriculum-first QA composer. P022-P044 use the full-book
response-safe composer. The runner is fail-closed, supports nested page folders,
uses exact named assets, and writes one result per page plus a summary.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import asdict, dataclass
from io import BytesIO
from pathlib import Path, PurePosixPath
from typing import Any

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "runtime-contracts/lkg/early-maths-adventures.json"
BUILDER = ROOT / "scripts/build_early_maths_curriculum_first_runtime.py"
PILOT_COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_early_maths_curriculum_first_v3.py"
FULL_COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_runtime_learning_page_response_safe.py"
PAGE_IDS = [f"EM-LKG-V4-P{n:03d}" for n in range(9, 45)]

# Compatibility names used by the already approved P009-P021 Work Mode assets.
ALIASES: dict[str, dict[str, str]] = {
    "EM-LKG-V4-P011": {
        "less_apples_2": "row1_left", "more_apples_5": "row1_right",
        "more_fish_6": "row2_left", "less_fish_3": "row2_right",
        "less_stars_4": "row3_left", "more_stars_7": "row3_right",
    },
    "EM-LKG-V4-P012": {
        "equal_oranges_left_4": "row1_left", "equal_oranges_right_4": "row1_right",
        "unequal_butterflies_left_3": "row2_left", "unequal_butterflies_right_5": "row2_right",
        "equal_blocks_left_6": "row3_left", "equal_blocks_right_6": "row3_right",
    },
    "EM-LKG-V4-P014": {
        "join_birds_group_a_2": "p1_left", "join_birds_group_b_1": "p1_right",
        "join_cars_group_a_3": "p2_left", "join_cars_group_b_2": "p2_right",
        "join_flowers_group_a_4": "p3_left", "join_flowers_group_b_2": "p3_right",
    },
    "EM-LKG-V4-P015": {
        "takeaway_apples_scene": "set_5_apples",
        "takeaway_fish_scene": "set_4_fish",
        "takeaway_balloons_scene": "set_6_balloons",
    },
}


@dataclass
class Result:
    page_id: str
    status: str
    reason: str = ""
    output: str = ""
    evidence: str = ""
    asset_count: int = 0
    composer: str = ""


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object expected: {path}")
    return value


def prepare_contract(contract: dict[str, Any], archive: zipfile.ZipFile) -> dict[str, Any]:
    """Allow format-specific entry points to align a compiled contract to an archive.

    The base runner deliberately performs no inference. Compatibility wrappers may
    replace this hook, but must still return a complete fail-closed book contract.
    """
    return contract


def parse_pages(value: str | None) -> list[str]:
    if not value or value.lower() == "all":
        return PAGE_IDS
    selected: list[str] = []
    for raw in value.split(","):
        token = raw.strip().upper()
        if token.startswith("P") and token[1:].isdigit():
            token = f"EM-LKG-V4-P{int(token[1:]):03d}"
        if token not in PAGE_IDS:
            raise ValueError(f"Unsupported page selection: {token}")
        if token not in selected:
            selected.append(token)
    return selected


def trim_white(asset: Image.Image) -> Image.Image:
    rgba = asset.convert("RGBA")
    rgb = rgba.convert("RGB")
    diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, "white")).convert("L")
    diff = diff.point(lambda value: 255 if value > 12 else 0)
    bbox = diff.getbbox()
    return rgba.crop(bbox) if bbox else rgba


def page_members(archive: zipfile.ZipFile, page_id: str) -> dict[str, str]:
    matches: dict[str, str] = {}
    for raw_name in archive.namelist():
        if raw_name.endswith("/"):
            continue
        path = PurePosixPath(raw_name)
        if page_id not in path.parts:
            continue
        page_index = path.parts.index(page_id)
        if page_index != len(path.parts) - 2:
            continue
        extension = path.suffix.lower()
        if extension not in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        source_stem = path.stem
        target_stem = ALIASES.get(page_id, {}).get(source_stem, source_stem)
        basename = f"{target_stem}{extension}"
        if basename in matches:
            raise ValueError(f"Duplicate normalised asset for {page_id}: {basename}")
        matches[basename] = raw_name
    return matches


def read_asset(archive: zipfile.ZipFile, members: dict[str, str], page_id: str, asset_name: str) -> Image.Image:
    for extension in (".jpg", ".jpeg", ".png", ".webp"):
        member = members.get(f"{asset_name}{extension}")
        if member:
            return trim_white(Image.open(BytesIO(archive.read(member))))
    raise FileNotFoundError(f"Missing approved asset: {page_id}/{asset_name}")


def crop_box(spec: dict[str, Any], size: int) -> tuple[int, int, int, int]:
    x, y, w, h = map(float, (spec["x"], spec["y"], spec["w"], spec["h"]))
    return round(x * size), round(y * size), round((x + w) * size), round((y + h) * size)


def assemble_sheet(page: dict[str, Any], archive: zipfile.ZipFile, page_id: str, output: Path) -> int:
    assets = list(page.get("illustration", {}).get("assets", []))
    crops = page.get("illustration", {}).get("asset_crops", {})
    if set(assets) != set(crops):
        raise ValueError(f"{page_id}: runtime asset names and crop names differ")
    members = page_members(archive, page_id)
    expected = set(assets)
    present = {Path(name).stem for name in members}
    missing = sorted(expected - present)
    extras = sorted(present - expected)
    if missing:
        raise FileNotFoundError(f"Missing approved assets for {page_id}: {missing}")
    if extras:
        raise ValueError(f"Unexpected approved assets for {page_id}: {extras}")

    size = 2400
    sheet = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    for name in assets:
        source = read_asset(archive, members, page_id, name)
        left, top, right, bottom = crop_box(crops[name], size)
        cell_w, cell_h = right - left, bottom - top
        inset = max(16, round(min(cell_w, cell_h) * 0.035))
        scale = min((cell_w - 2 * inset) / source.width, (cell_h - 2 * inset) / source.height)
        resized = source.resize(
            (max(1, round(source.width * scale)), max(1, round(source.height * scale))),
            Image.Resampling.LANCZOS,
        )
        x = left + (cell_w - resized.width) // 2
        y = top + (cell_h - resized.height) // 2
        sheet.paste(resized, (x, y), resized)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(output, "PNG")
    return len(assets)


def composer_for(page_id: str) -> Path:
    number = int(page_id.rsplit("P", 1)[1])
    return PILOT_COMPOSER if number <= 21 else FULL_COMPOSER


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Early Maths P009-P044 from approved assets")
    parser.add_argument("--logo", type=Path, required=True)
    parser.add_argument("--asset-archive", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--pages", default="all", help="all or comma-separated P009,...,P044")
    parser.add_argument("--fail-fast", action="store_true")
    args = parser.parse_args()

    logo = args.logo.expanduser().resolve()
    archive_path = args.asset_archive.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    evidence_dir = args.evidence_dir.expanduser().resolve()
    if not logo.is_file():
        raise SystemExit(f"Logo not found: {logo}")
    if not archive_path.is_file():
        raise SystemExit(f"Approved asset archive not found: {archive_path}")

    selected = parse_pages(args.pages)
    subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, check=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    results: list[Result] = []

    with tempfile.TemporaryDirectory(prefix="bcube-early-maths-full-") as temp_name, zipfile.ZipFile(archive_path) as archive:
        contract = prepare_contract(load_json(CONTRACT), archive)
        missing_contracts = [page_id for page_id in selected if page_id not in contract.get("pages", {})]
        if missing_contracts:
            raise SystemExit(f"Runtime contracts missing: {missing_contracts}")
        temp = Path(temp_name)
        blank = temp / "blank.png"
        Image.new("RGB", (1200, 1200), "white").save(blank)

        for page_id in selected:
            composer = composer_for(page_id)
            try:
                page = contract["pages"][page_id]
                asset_names = list(page.get("illustration", {}).get("assets", []))
                if asset_names:
                    source = temp / f"{page_id}.png"
                    asset_count = assemble_sheet(page, archive, page_id, source)
                else:
                    source = blank
                    asset_count = 0

                output = output_dir / f"{page_id}.png"
                evidence = evidence_dir / f"{page_id}.json"
                command = [
                    sys.executable, str(composer),
                    "--level", "lkg",
                    "--book", "early-maths-adventures",
                    "--page-id", page_id,
                    "--illustration", str(source),
                    "--logo", str(logo),
                    "--output", str(output),
                    "--evidence-output", str(evidence),
                ]
                process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
                if process.returncode != 0:
                    raise RuntimeError((process.stderr or process.stdout or "Renderer failed").strip())
                results.append(Result(page_id, "GENERATED", output=str(output), evidence=str(evidence), asset_count=asset_count, composer=composer.name))
            except Exception as exc:
                results.append(Result(page_id, "FAILED", reason=str(exc), composer=composer.name))
                if args.fail_fast:
                    break

    summary = {
        "engine": "BCube Early Maths full-book approved-assets renderer",
        "scope": selected,
        "generated": sum(item.status == "GENERATED" for item in results),
        "failed": sum(item.status == "FAILED" for item in results),
        "asset_archive": str(archive_path),
        "policy": "P009-P021 curriculum-first QA; P022-P044 response-safe; exact approved assets; no fallback.",
        "results": [asdict(item) for item in results],
    }
    summary_path = evidence_dir / "early-maths-full-book-render-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: summary[key] for key in ("scope", "generated", "failed", "policy")}, indent=2))
    print(f"Summary: {summary_path}")
    for result in results:
        if result.status == "FAILED":
            print(f"FAILED {result.page_id}: {result.reason}", file=sys.stderr)
    return 0 if summary["failed"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
