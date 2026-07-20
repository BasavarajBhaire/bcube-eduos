#!/usr/bin/env python3
"""Inventory approved Communication Champions page PNGs without modifying them."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image

SOURCE_DIR = Path(
    "BCube_Gold_Production_v4/approved-assets/nursery/communication-champions/pages"
)
OUTPUT_DIR = Path(
    "BCube_Gold_Production_v4/restoration-work/nursery/communication-champions/inventory"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_image(path: Path) -> dict[str, Any]:
    record: dict[str, Any] = {
        "name": path.name,
        "relative_path": path.as_posix(),
        "size_bytes": path.stat().st_size,
        "sha256": sha256(path),
        "valid": False,
    }
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            record.update(
                {
                    "width": image.width,
                    "height": image.height,
                    "mode": image.mode,
                    "format": image.format,
                    "valid": True,
                }
            )
    except Exception as exc:  # inventory must record failures rather than stop
        record["error"] = f"{type(exc).__name__}: {exc}"
    return record


def main() -> None:
    if not SOURCE_DIR.is_dir():
        raise SystemExit(f"Source directory not found: {SOURCE_DIR}")

    pages = sorted(
        [path for path in SOURCE_DIR.iterdir() if path.is_file() and path.suffix.lower() == ".png"],
        key=lambda path: path.name.lower(),
    )
    if not pages:
        raise SystemExit(f"No PNG files found in: {SOURCE_DIR}")

    records = [inspect_image(path) for path in pages]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = OUTPUT_DIR / "communication_champions_pages_inventory.json"
    json_path.write_text(json.dumps(records, indent=2), encoding="utf-8")

    lines = [
        "# Communication Champions approved page inventory",
        "",
        f"Source: `{SOURCE_DIR.as_posix()}`",
        "",
        "| File | Dimensions | Bytes | Valid | SHA-256 |",
        "|---|---:|---:|:---:|---|",
    ]
    for record in records:
        dimensions = (
            f"{record.get('width')} × {record.get('height')}"
            if record.get("valid")
            else "unreadable"
        )
        lines.append(
            "| {name} | {dimensions} | {size_bytes} | {valid} | `{sha}` |".format(
                name=record["name"],
                dimensions=dimensions,
                size_bytes=record["size_bytes"],
                valid="yes" if record.get("valid") else "no",
                sha=record["sha256"],
            )
        )
        if record.get("error"):
            lines.append(f"| ↳ error | `{record['error']}` |  |  |  |")

    (OUTPUT_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Inventoried {len(records)} PNG files into {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
