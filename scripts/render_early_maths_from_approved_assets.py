#!/usr/bin/env python3
"""Render Early Maths P009-P021 from approved individual illustration assets.

The source of truth is one PNG per named asset under:
assets/illustrations/early-maths-adventures/lkg/curriculum-first/<PAGE_ID>/

The script validates exact filenames, assembles temporary crop-compatible sheets
from the runtime contract, renders every page in the curriculum-first scope, and
writes one evidence summary. Pages without illustration assets render directly.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ASSETS = ROOT / "assets" / "illustrations" / "early-maths-adventures" / "lkg" / "curriculum-first"
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


def trim(asset: Image.Image) -> Image.Image:
    rgba = asset.convert("RGBA")
    alpha = rgba.getchannel("A")
    bbox = alpha.getbbox()
    return rgba.crop(bbox) if bbox else rgba


def assemble_sheet(page: dict[str, Any], page_dir: Path, output: Path) -> int:
    assets = list(page["illustration"].get("assets", []))
    crops = page["illustration"].get("asset_crops", {})
    if set(assets) != set(crops):
        raise ValueError("Runtime asset names and crop names differ")

    expected = {f"{name}.png" for name in assets}
    present = {p.name for p in page_dir.glob("*.png")}
    missing = sorted(expected - present)
    extras = sorted(present - expected)
    if missing:
        raise FileNotFoundError(f"Missing approved assets: {missing}")
    if extras:
        raise ValueError(f"Unexpected PNG assets in {page_dir}: {extras}")

    size = 2400
    sheet = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    for name in assets:
        source = trim(Image.open(page_dir / f"{name}.png"))
        left, top, right, bottom = crop_box(crops[name], size, size)
        cell_w = right - left; cell_h = bottom - top
        inset = max(20, round(min(cell_w, cell_h) * 0.06))
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
    parser = argparse.ArgumentParser(description="Render Early Maths curriculum-first pages from approved individual assets")
    parser.add_argument("--logo", type=Path, required=True)
    parser.add_argument("--assets-dir", type=Path, default=DEFAULT_ASSETS)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--pages", default="all", help="all or comma-separated P009,P010,...")
    parser.add_argument("--fail-fast", action="store_true")
    args = parser.parse_args()

    logo = args.logo.expanduser().resolve()
    assets_dir = args.assets_dir.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    evidence_dir = args.evidence_dir.expanduser().resolve()
    if not logo.is_file():
        raise SystemExit(f"Logo not found: {logo}")
    if not assets_dir.is_dir():
        raise SystemExit(f"Approved assets directory not found: {assets_dir}")

    selected = parse_pages(args.pages)
    subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, check=True)
    contract = load_json(CONTRACT)
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    results: list[Result] = []

    with tempfile.TemporaryDirectory(prefix="bcube-approved-assets-") as temp_name:
        temp = Path(temp_name)
        blank = temp / "blank.png"
        Image.new("RGB", (1200, 1200), "white").save(blank)

        for page_id in selected:
            try:
                page = contract["pages"][page_id]
                asset_names = list(page.get("illustration", {}).get("assets", []))
                if asset_names:
                    page_dir = assets_dir / page_id
                    if not page_dir.is_dir():
                        raise FileNotFoundError(f"Approved page asset directory not found: {page_dir}")
                    source = temp / f"{page_id}.png"
                    asset_count = assemble_sheet(page, page_dir, source)
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
        "engine": "BCube approved individual asset renderer",
        "scope": selected,
        "generated": sum(r.status == "GENERATED" for r in results),
        "failed": sum(r.status == "FAILED" for r in results),
        "assets_root": str(assets_dir),
        "policy": "Exact committed individual assets; no AI generation; no generic fallback.",
        "results": [asdict(r) for r in results],
    }
    summary_path = evidence_dir / "approved-assets-render-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("scope", "generated", "failed", "policy")}, indent=2))
    print(f"Summary: {summary_path}")
    return 0 if summary["failed"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
