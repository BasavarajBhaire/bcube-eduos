#!/usr/bin/env python3
"""Render Early Maths full book from mixed approved-asset ZIP formats.

P009-P021 may contain one folder per page with individually named assets.
P022-P044 may contain one composite illustration sheet named exactly
``EM-LKG-V4-Pxxx.png``. The runtime crop map extracts named assets from that
sheet. No generic artwork fallback is allowed.
"""
from __future__ import annotations

import importlib.util
import sys
import zipfile
from io import BytesIO
from pathlib import Path, PurePosixPath

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "scripts/render_early_maths_full_book_approved_assets.py"

MODULE_NAME = "early_maths_full_book_approved_assets_base"
spec = importlib.util.spec_from_file_location(MODULE_NAME, BASE)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {BASE}")
module = importlib.util.module_from_spec(spec)
sys.modules[MODULE_NAME] = module
spec.loader.exec_module(module)

original_assemble_sheet = module.assemble_sheet


def direct_sheet_member(archive: zipfile.ZipFile, page_id: str) -> str | None:
    """Find a page-owned composite sheet regardless of an outer ZIP folder."""
    matches: list[str] = []
    for raw_name in archive.namelist():
        if raw_name.endswith("/"):
            continue
        path = PurePosixPath(raw_name)
        if path.stem != page_id:
            continue
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        matches.append(raw_name)
    if len(matches) > 1:
        raise ValueError(f"Duplicate composite illustration sheets for {page_id}: {matches}")
    return matches[0] if matches else None


def assemble_sheet(page, archive: zipfile.ZipFile, page_id: str, output: Path) -> int:
    """Use a composite page sheet when present; otherwise use named assets."""
    direct_member = direct_sheet_member(archive, page_id)
    if direct_member is not None:
        image = Image.open(BytesIO(archive.read(direct_member))).convert("RGB")
        output.parent.mkdir(parents=True, exist_ok=True)
        image.save(output, "PNG")
        return len(page.get("illustration", {}).get("assets", []))
    try:
        return original_assemble_sheet(page, archive, page_id, output)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"{exc}. The ZIP must contain either named assets inside a {page_id}/ folder "
            f"or one composite sheet named {page_id}.png"
        ) from exc


module.assemble_sheet = assemble_sheet

if __name__ == "__main__":
    raise SystemExit(module.main())
