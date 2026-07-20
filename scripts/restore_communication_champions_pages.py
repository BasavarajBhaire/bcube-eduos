#!/usr/bin/env python3
"""Create faithful recovery candidates for selected Communication Champions pages.

This recovery pass never crops, clears, moves, replaces, or reconstructs page content.
It only creates print-size copies using high-quality resampling and very restrained
sharpening. Every output remains pending visual review and is never auto-approved.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageStat

SOURCE_DIR = Path("BCube_Gold_Production_v4/approved-assets/nursery/communication-champions/pages")
WORK_ROOT = Path("BCube_Gold_Production_v4/restoration-work/nursery/communication-champions")
OUTPUT_DIR = WORK_ROOT / "recovery-candidates"
REJECTED_DIR = WORK_ROOT / "rejected-unsafe-outputs"
ISOLATED_DIR = WORK_ROOT / "isolated"
REPORT_DIR = WORK_ROOT / "validation"
CONTACT_DIR = WORK_ROOT / "contact-sheets"

TARGET_SIZE = (2480, 3508)
TARGET_PAGE_IDS = {
    *range(9, 14),
    *range(15, 17),
    *range(26, 44),
}
PAGE_PATTERN = re.compile(r"(?:^|[-_])P(\d{3})(?:[-_.]|$)", re.IGNORECASE)
MAX_ROUNDTRIP_MAE = 8.0
CONTACT_THUMB = (310, 439)


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


def prepare_directories() -> None:
    for directory in (OUTPUT_DIR, REJECTED_DIR, ISOLATED_DIR, REPORT_DIR, CONTACT_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    # Remove prior generated candidates so stale/broken pages cannot survive a run.
    for directory in (OUTPUT_DIR, CONTACT_DIR):
        for path in directory.iterdir():
            if path.is_file() or path.is_symlink():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)

    # Preserve any previously committed unsafe pages for audit, never for approval.
    legacy = WORK_ROOT / "restored-pages"
    if legacy.exists():
        for path in legacy.iterdir():
            destination = REJECTED_DIR / path.name
            if path.is_file():
                shutil.copy2(path, destination)
        shutil.rmtree(legacy)


def faithful_enhance(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    if rgb.size == TARGET_SIZE:
        # Existing 300-DPI-size pages are preserved pixel-for-pixel.
        return rgb.copy()
    resized = rgb.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
    # Very mild sharpening only after enlargement; no contrast or colour changes.
    return resized.filter(ImageFilter.UnsharpMask(radius=0.8, percent=55, threshold=6))


def roundtrip_mae(source: Image.Image, output: Image.Image) -> float:
    comparison = output.resize(source.size, Image.Resampling.LANCZOS)
    diff = ImageChops.difference(source.convert("RGB"), comparison.convert("RGB"))
    stats = ImageStat.Stat(diff)
    return float(sum(stats.mean) / len(stats.mean))


def create_contact_sheets(rows: list[dict[str, Any]]) -> list[str]:
    valid_rows = [row for row in rows if row.get("status") == "pending-visual-review"]
    outputs: list[str] = []
    per_sheet = 6
    for sheet_index in range(math.ceil(len(valid_rows) / per_sheet)):
        batch = valid_rows[sheet_index * per_sheet:(sheet_index + 1) * per_sheet]
        width = CONTACT_THUMB[0] * 2 + 90
        height = len(batch) * (CONTACT_THUMB[1] + 56) + 55
        canvas = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(canvas)
        draw.text((20, 15), "SOURCE", fill="black")
        draw.text((CONTACT_THUMB[0] + 55, 15), "RECOVERY CANDIDATE", fill="black")
        y = 48
        for row in batch:
            with Image.open(row["source"]) as src:
                source_thumb = src.convert("RGB").resize(CONTACT_THUMB, Image.Resampling.LANCZOS)
            with Image.open(row["output"]) as out:
                output_thumb = out.convert("RGB").resize(CONTACT_THUMB, Image.Resampling.LANCZOS)
            canvas.paste(source_thumb, (20, y))
            canvas.paste(output_thumb, (CONTACT_THUMB[0] + 55, y))
            draw.text((20, y + CONTACT_THUMB[1] + 8), f"{row['page_id']}  MAE={row['roundtrip_mae']:.3f}", fill="black")
            y += CONTACT_THUMB[1] + 56
        destination = CONTACT_DIR / f"recovery-review-{sheet_index + 1:02d}.jpg"
        canvas.save(destination, "JPEG", quality=90, optimize=True)
        outputs.append(destination.as_posix())
    return outputs


def main() -> None:
    if not SOURCE_DIR.is_dir():
        raise SystemExit(f"Source directory not found: {SOURCE_DIR}")

    prepare_directories()
    files = sorted(
        (path for path in SOURCE_DIR.iterdir() if path.is_file() and path.suffix.lower() == ".png"),
        key=lambda path: path.name.lower(),
    )
    selected = [path for path in files if page_id(path) in TARGET_PAGE_IDS]
    if len(selected) != len(TARGET_PAGE_IDS):
        found = {page_id(path) for path in selected}
        missing = sorted(TARGET_PAGE_IDS - found)
        raise SystemExit(f"Missing target page files: {missing}")

    records: list[dict[str, Any]] = []
    for source in selected:
        pid = page_id(source)
        source_sha = digest(source)
        valid, error = image_is_valid(source)
        record: dict[str, Any] = {
            "page_id": f"P{pid:03d}",
            "source": source.as_posix(),
            "source_sha256": source_sha,
            "valid_source": valid,
            "status": "pending",
        }
        if not valid:
            isolated = ISOLATED_DIR / source.name
            shutil.copy2(source, isolated)
            record.update({"status": "rejected-unreadable-source", "error": error, "isolated_copy": isolated.as_posix()})
            records.append(record)
            continue

        with Image.open(source) as opened:
            opened.load()
            original = opened.convert("RGB")
            candidate = faithful_enhance(original)
            mae = roundtrip_mae(original, candidate)
            record["source_dimensions"] = list(original.size)
            record["roundtrip_mae"] = mae

        destination = OUTPUT_DIR / source.name
        candidate.save(destination, format="PNG", dpi=(300, 300), optimize=True)
        with Image.open(destination) as check:
            check.load()
            output_dimensions = list(check.size)

        source_unchanged = digest(source) == source_sha
        mechanical_pass = (
            output_dimensions == list(TARGET_SIZE)
            and source_unchanged
            and mae <= MAX_ROUNDTRIP_MAE
        )
        record.update({
            "status": "pending-visual-review" if mechanical_pass else "rejected-mechanical-validation",
            "output": destination.as_posix(),
            "output_dimensions": output_dimensions,
            "output_sha256": digest(destination),
            "source_unchanged": source_unchanged,
            "mechanical_validation_passed": mechanical_pass,
            "visual_validation": "required",
            "approved": False,
        })
        records.append(record)

    contact_sheets = create_contact_sheets(records)
    report = {
        "policy": {
            "automatic_header_editing": False,
            "automatic_visual_approval": False,
            "merge_allowed": False,
            "required_final_state": "explicit-human-visual-approval",
        },
        "target_size": list(TARGET_SIZE),
        "max_roundtrip_mae": MAX_ROUNDTRIP_MAE,
        "contact_sheets": contact_sheets,
        "pages": records,
    }
    (REPORT_DIR / "recovery-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    pending = sum(row["status"] == "pending-visual-review" for row in records)
    rejected = len(records) - pending
    lines = [
        "# Communication Champions recovery review",
        "",
        "**MERGE BLOCKED — these files are candidates only and are not visually approved.**",
        "",
        f"- Target pages: {len(records)}",
        f"- Pending visual review: {pending}",
        f"- Rejected mechanically/unreadable: {rejected}",
        f"- Output: {TARGET_SIZE[0]} × {TARGET_SIZE[1]} px with 300-DPI metadata",
        "- No header, logo, title, illustration, activity, colour, text, or layout element was moved or replaced.",
        "- Existing target-size pages were copied pixel-for-pixel.",
        "- Low-resolution pages were enlarged using Lanczos with restrained sharpening.",
        "- Contact sheets are mandatory review evidence; no automatic visual approval is permitted.",
        "",
        "| Page | Source dimensions | Status | MAE | Source unchanged | Approved |",
        "|---|---:|---|---:|:---:|:---:|",
    ]
    for row in records:
        dims = " × ".join(map(str, row.get("source_dimensions", []))) or "—"
        mae = f"{row['roundtrip_mae']:.3f}" if "roundtrip_mae" in row else "—"
        unchanged = "yes" if row.get("source_unchanged") else "n/a"
        lines.append(f"| {row['page_id']} | {dims} | {row['status']} | {mae} | {unchanged} | no |")
    (REPORT_DIR / "RECOVERY_REVIEW.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    if rejected:
        raise SystemExit(f"Recovery created {pending} review candidates; {rejected} pages were rejected.")
    print(f"Created {pending} faithful recovery candidates. Visual approval remains required; merge is blocked.")


if __name__ == "__main__":
    main()
