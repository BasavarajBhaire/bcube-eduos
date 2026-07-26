#!/usr/bin/env python3
"""Render Early Maths P009-P021 from the approved committed asset archive.

The archive may contain page folders at its root or below one outer folder,
for example ``Early Maths Adventures/EM-LKG-V4-P009/...``. The renderer locates
page folders by page ID, validates exact asset filenames, assembles temporary
crop-compatible sheets, renders the complete curriculum-first scope, and writes
one evidence summary. Pages without illustration assets render deterministically.
"""
from __future__ import annotations

import argparse
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
DEFAULT_ARCHIVE = ROOT / "assets" / "illustrations" / "early-maths-adventures" / "lkg" / "early-maths-approved-assets-p009-p021.zip"
CONTRACT = ROOT / "runtime-contracts" / "lkg" / "early-maths-adventures.json"
BUILDER = ROOT / "scripts" / "build_early_maths_curriculum_first_runtime.py"
COMPOSER = ROOT / "bcube-publishing-sdk" / "composer" / "compose_early_maths_curriculum_first.py"
PAGE_IDS = [f"EM-LKG-V4-P{n:03d}" for n in range(9, 22)]


@dataclass
class Result:
    page_id: str
    status: str
    reason: str = ""
    output: str = ""
    evidence: str = ""
    asset_count: int = 0


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object expected: {path}")
    return value


def parse_pages(value: str | None) -> list[str]:
    if not value or value.lower() == "all":
        return PAGE_IDS
    selected: list[str] = []
    for token in value.split(","):
        token = token.strip().upper()
        if token.startswith("P") and token[1:].isdigit():
            token = f"EM-LKG-V4-P{int(token[1:]):03d}"
        if token not in PAGE_IDS:
            raise ValueError(f"Unsupported page selection: {token}")
        if token not in selected:
            selected.append(token)
    return selected


def crop_box(spec: dict[str, Any], width: int, height: int) -> tuple[int, int, int, int]:
    x = float(spec["x"]); y = float(spec["y"])
    w = float(spec["w"]); h = float(spec["h"])
    return round(x * width), round(y * height), round((x + w) * width), round((y + h) * height)


def trim_white(asset: Image.Image) -> Image.Image:
    rgba = asset.convert("RGBA")
    rgb = rgba.convert("RGB")
    background = Image.new("RGB", rgb.size, (255, 255, 255))
    diff = ImageChops.difference(rgb, background).convert("L")
    diff = diff.point(lambda value: 255 if value > 12 else 0)
    bbox = diff.getbbox()
    return rgba.crop(bbox) if bbox else rgba


def page_members(archive: zipfile.ZipFile, page_id: str) -> dict[str, str]:
    """Return basename -> full member path for one page, regardless of outer folders."""
    matches: dict[str, str] = {}
    for raw_name in archive.namelist():
        if raw_name.endswith("/"):
            continue
        path = PurePosixPath(raw_name)
        parts = path.parts
        if page_id not in parts:
            continue
        page_index = parts.index(page_id)
        if page_index != len(parts) - 2:
            continue
        basename = path.name
        if basename in matches:
            raise ValueError(f"Duplicate archive asset name for {page_id}: {basename}")
        matches[basename] = raw_name
    return matches


def read_asset(archive: zipfile.ZipFile, members: dict[str, str], page_id: str, asset_name: str) -> Image.Image:
    for extension in (".jpg", ".jpeg", ".png", ".webp"):
        basename = f"{asset_name}{extension}"
        member = members.get(basename)
        if member:
            return trim_white(Image.open(BytesIO(archive.read(member))))
    raise FileNotFoundError(f"Missing approved asset: {page_id}/{asset_name}")


def assemble_sheet(page: dict[str, Any], archive: zipfile.ZipFile, page_id: str, output: Path) -> int:
    assets = list(page["illustration"].get("assets", []))
    crops = page["illustration"].get("asset_crops", {})
    if set(assets) != set(crops):
        raise ValueError("Runtime asset names and crop names differ")

    members = page_members(archive, page_id)
    expected_stems = set(assets)
    present_stems = {Path(name).stem for name in members}
    missing = sorted(expected_stems - present_stems)
    extras = sorted(present_stems - expected_stems)
    if missing:
        raise FileNotFoundError(f"Missing approved assets for {page_id}: {missing}")
    if extras:
        raise ValueError(f"Unexpected approved assets for {page_id}: {extras}")

    size = 2400
    sheet = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    for name in assets:
        source = read_asset(archive, members, page_id, name)
        left, top, right, bottom = crop_box(crops[name], size, size)
        cell_w = right - left; cell_h = bottom - top
        inset = max(16, round(min(cell_w, cell_h) * 0.035))
        fit_w = max(1, cell_w - 2 * inset); fit_h = max(1, cell_h - 2 * inset)
        scale = min(fit_w / source.width, fit_h / source.height)
        resized = source.resize((max(1, round(source.width * scale)), max(1, round(source.height * scale))), Image.Resampling.LANCZOS)
        x = left + (cell_w - resized.width) // 2
        y = top + (cell_h - resized.height) // 2
        sheet.paste(resized, (x, y), resized)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(output, "PNG")
    return len(assets)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Early Maths from the approved individual-asset archive")
    parser.add_argument("--logo", type=Path, required=True)
    parser.add_argument("--asset-archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--pages", default="all", help="all or comma-separated P009,P010,...")
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
    contract = load_json(CONTRACT)
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    results: list[Result] = []

    with tempfile.TemporaryDirectory(prefix="bcube-approved-assets-") as temp_name, zipfile.ZipFile(archive_path) as archive:
        temp = Path(temp_name)
        blank = temp / "blank.png"
        Image.new("RGB", (1200, 1200), "white").save(blank)

        for page_id in selected:
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
                    sys.executable, str(COMPOSER),
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
                results.append(Result(page_id, "GENERATED", output=str(output), evidence=str(evidence), asset_count=asset_count))
            except Exception as exc:
                results.append(Result(page_id, "FAILED", reason=str(exc)))
                if args.fail_fast:
                    break

    summary = {
        "engine": "BCube approved individual asset archive renderer",
        "scope": selected,
        "generated": sum(r.status == "GENERATED" for r in results),
        "failed": sum(r.status == "FAILED" for r in results),
        "asset_archive": str(archive_path),
        "policy": "Exact approved assets; nested archive folders supported; no image API; no generic fallback.",
        "results": [asdict(r) for r in results],
    }
    summary_path = evidence_dir / "approved-assets-render-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("scope", "generated", "failed", "policy")}, indent=2))
    print(f"Summary: {summary_path}")
    if summary["failed"]:
        for result in results:
            if result.status == "FAILED":
                print(f"FAILED {result.page_id}: {result.reason}", file=sys.stderr)
    return 0 if summary["failed"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
