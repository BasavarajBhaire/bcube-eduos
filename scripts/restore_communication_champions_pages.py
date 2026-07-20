#!/usr/bin/env python3
"""Restore selected Communication Champions pages without regenerating artwork.

The script keeps approved source files untouched. It creates A4 300-DPI PNG copies,
uses high-quality resampling and restrained sharpening, and normalizes only the
header area (logo/title/top-right corner) for the explicitly approved page set.
Unreadable pages are isolated and reported rather than reconstructed.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageStat

SOURCE_DIR = Path("BCube_Gold_Production_v4/approved-assets/nursery/communication-champions/pages")
WORK_ROOT = Path("BCube_Gold_Production_v4/restoration-work/nursery/communication-champions")
OUTPUT_DIR = WORK_ROOT / "restored-pages"
ISOLATED_DIR = WORK_ROOT / "isolated"
REPORT_DIR = WORK_ROOT / "validation"

TARGET_SIZE = (2480, 3508)
TARGET_PAGE_IDS = {
    *range(9, 14),   # P009-P013: printed pages 8-12
    *range(15, 17),  # P015-P016: printed pages 14-15
    *range(26, 44),  # P026-P043: printed pages 25-42
}
PAGE_PATTERN = re.compile(r"(?:^|[-_])P(\d{3})(?:[-_.]|$)", re.IGNORECASE)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def page_id(path: Path) -> int | None:
    match = PAGE_PATTERN.search(path.name)
    return int(match.group(1)) if match else None


def image_is_valid(path: Path) -> tuple[bool, str | None]:
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            image.load()
        return True, None
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def nonwhite_bbox(image: Image.Image, threshold: int = 28) -> tuple[int, int, int, int] | None:
    rgb = image.convert("RGB")
    bg = Image.new("RGB", rgb.size, "white")
    diff = ImageChops.difference(rgb, bg).convert("L")
    mask = diff.point(lambda value: 255 if value > threshold else 0)
    return mask.getbbox()


def extract_logo_source(reference: Image.Image) -> Image.Image | None:
    """Extract the existing approved logo from the top-left header region."""
    w, h = reference.size
    region = reference.crop((0, 0, int(w * 0.34), int(h * 0.17))).convert("RGBA")
    bbox = nonwhite_bbox(region, 24)
    if not bbox:
        return None
    # Small padding preserves antialiasing while excluding surrounding artwork.
    left, top, right, bottom = bbox
    pad = max(4, int(min(region.size) * 0.012))
    box = (max(0, left - pad), max(0, top - pad), min(region.width, right + pad), min(region.height, bottom + pad))
    return region.crop(box)


def normalize_header(image: Image.Image, logo: Image.Image | None) -> Image.Image:
    """Normalize only the header while preserving all lower-page artwork/content."""
    canvas = image.convert("RGBA")
    w, h = canvas.size
    header_h = int(h * 0.165)

    # Extract the page's existing title pixels before clearing the title zone.
    title_zone = canvas.crop((int(w * 0.25), 0, int(w * 0.89), header_h))
    title_bbox = nonwhite_bbox(title_zone, 34)
    title = title_zone.crop(title_bbox) if title_bbox else None

    # Clear only the standardized header zones. The lower 83.5% is untouched.
    clean = Image.new("RGBA", canvas.size, (255, 255, 255, 255))
    clean.alpha_composite(canvas)
    draw_header = Image.new("RGBA", (w, header_h), (255, 255, 255, 255))
    clean.alpha_composite(draw_header, (0, 0))

    # Approved logo: slightly larger, top-left, with publication-safe margins.
    if logo is not None:
        max_logo_w = int(w * 0.235)
        max_logo_h = int(header_h * 0.79)
        scale = min(max_logo_w / logo.width, max_logo_h / logo.height)
        resized_logo = logo.resize((max(1, round(logo.width * scale)), max(1, round(logo.height * scale))), Image.Resampling.LANCZOS)
        clean.alpha_composite(resized_logo, (int(w * 0.035), int(header_h * 0.10)))

    # Reuse the exact existing raster title—no OCR, retyping, or font substitution.
    if title is not None and title.width > 8 and title.height > 8:
        target_max_w = int(w * 0.56)
        target_max_h = int(header_h * 0.47)
        scale = min(target_max_w / title.width, target_max_h / title.height)
        # Increase undersized titles, but never aggressively enlarge a raster title.
        scale = min(max(scale, 1.0), 1.22)
        title = title.resize((max(1, round(title.width * scale)), max(1, round(title.height * scale))), Image.Resampling.LANCZOS)
        x = (w - title.width) // 2
        y = int(header_h * 0.22)
        clean.alpha_composite(title, (x, y))

    return clean.convert("RGB")


def restrained_enhance(image: Image.Image) -> Image.Image:
    resized = image.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
    # Mild local sharpening only; avoids halos and artificial redrawing.
    sharpened = resized.filter(ImageFilter.UnsharpMask(radius=1.15, percent=105, threshold=4))
    return ImageEnhance.Sharpness(sharpened).enhance(1.04)


def find_reference_logo(files: list[Path]) -> Image.Image | None:
    # Prefer P010, previously accepted as the clean header reference.
    ordered = sorted(files, key=lambda p: (page_id(p) != 10, p.name.lower()))
    for path in ordered:
        valid, _ = image_is_valid(path)
        if not valid:
            continue
        with Image.open(path) as image:
            logo = extract_logo_source(image.convert("RGB"))
            if logo is not None:
                return logo.copy()
    return None


def main() -> None:
    if not SOURCE_DIR.is_dir():
        raise SystemExit(f"Source directory not found: {SOURCE_DIR}")

    files = sorted((p for p in SOURCE_DIR.iterdir() if p.is_file() and p.suffix.lower() == ".png"), key=lambda p: p.name.lower())
    selected = [p for p in files if page_id(p) in TARGET_PAGE_IDS]
    if not selected:
        raise SystemExit("No target Communication Champions PNG files were found.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ISOLATED_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    logo = find_reference_logo(files)
    records: list[dict[str, Any]] = []

    for source in selected:
        pid = page_id(source)
        valid, error = image_is_valid(source)
        record: dict[str, Any] = {
            "page_id": f"P{pid:03d}" if pid is not None else None,
            "source": source.as_posix(),
            "source_sha256": digest(source),
            "valid_source": valid,
            "status": "pending",
        }

        if not valid:
            isolated = ISOLATED_DIR / source.name
            shutil.copy2(source, isolated)
            record.update({"status": "isolated-unreadable", "error": error, "isolated_copy": isolated.as_posix()})
            records.append(record)
            continue

        with Image.open(source) as opened:
            opened.load()
            original = opened.convert("RGB")
            record["source_dimensions"] = list(original.size)
            enhanced = restrained_enhance(original)
            restored = normalize_header(enhanced, logo.resize((round(logo.width * TARGET_SIZE[0] / original.width), round(logo.height * TARGET_SIZE[1] / original.height)), Image.Resampling.LANCZOS) if logo else None)

        destination = OUTPUT_DIR / source.name
        restored.save(destination, format="PNG", dpi=(300, 300), optimize=True)
        with Image.open(destination) as check:
            check.load()
            dimensions = list(check.size)

        record.update({
            "status": "restored",
            "output": destination.as_posix(),
            "output_dimensions": dimensions,
            "output_sha256": digest(destination),
            "source_unchanged": digest(source) == record["source_sha256"],
        })
        records.append(record)

    report_json = REPORT_DIR / "restoration-report.json"
    report_json.write_text(json.dumps(records, indent=2), encoding="utf-8")

    restored_count = sum(r["status"] == "restored" for r in records)
    isolated_count = sum(r["status"].startswith("isolated") for r in records)
    lines = [
        "# Communication Champions restoration validation",
        "",
        f"- Target pages: {len(records)}",
        f"- Restored: {restored_count}",
        f"- Isolated: {isolated_count}",
        f"- Output size: {TARGET_SIZE[0]} × {TARGET_SIZE[1]} px, 300 DPI metadata",
        "- Approved source images were not overwritten.",
        "- Existing raster title artwork was reused; no OCR, retyping, font substitution, illustration regeneration, or content reconstruction was performed.",
        "",
        "| Page | Source | Status | Output dimensions | Source unchanged |",
        "|---|---|---|---:|:---:|",
    ]
    for record in records:
        dims = " × ".join(map(str, record.get("output_dimensions", []))) or "—"
        unchanged = "yes" if record.get("source_unchanged") else ("n/a" if not record.get("valid_source") else "no")
        lines.append(f"| {record.get('page_id')} | `{Path(record['source']).name}` | {record['status']} | {dims} | {unchanged} |")
        if record.get("error"):
            lines.append(f"| ↳ issue |  | `{record['error']}` |  |  |")
    (REPORT_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    if restored_count + isolated_count != len(records):
        raise SystemExit("Restoration validation failed: not all target pages were accounted for.")
    print(f"Completed {restored_count} restorations; isolated {isolated_count} unreadable source files.")


if __name__ == "__main__":
    main()
