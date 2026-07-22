#!/usr/bin/env python3
"""Fail-closed validation for deterministic BCube cover inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
MIN_VISIBLE_STAR_PIXELS = 5000
MIN_STAR_ALPHA_COVERAGE = 0.08
MAX_STAR_ALPHA_COVERAGE = 0.95


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def resolve(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_image(path: Path, label: str) -> tuple[int, int]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing {label}: {path}")
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        return image.size

    print("STAR ASSET =", star)
    print("EXISTS =", Path(star).exists())

def validate_star(path: Path) -> dict[str, Any]:
    width, height = validate_image(path, "official Star asset")
    with Image.open(path) as image:
        rgba = image.convert("RGBA")
        alpha = rgba.getchannel("A")
        visible = sum(1 for value in alpha.getdata() if value > 24)
        total = width * height
        coverage = visible / total if total else 0.0

    # A full workbook page is not an acceptable mascot asset.
    if width >= 1200 or height >= 1200:
        raise ValueError(
            "FAIL_OFFICIAL_STAR_NOT_STANDALONE: the registered Star asset looks like a full page. "
            "Register a dedicated transparent mascot PNG."
        )
    if visible < MIN_VISIBLE_STAR_PIXELS or coverage < MIN_STAR_ALPHA_COVERAGE:
        raise ValueError(
            f"FAIL_OFFICIAL_STAR_NOT_VISIBLE: visible_pixels={visible}, alpha_coverage={coverage:.4f}"
        )
    if coverage > MAX_STAR_ALPHA_COVERAGE:
        raise ValueError(
            f"FAIL_OFFICIAL_STAR_BACKGROUND_NOT_TRANSPARENT: alpha_coverage={coverage:.4f}"
        )
    return {
        "path": str(path),
        "sha256": sha256(path),
        "size": [width, height],
        "visible_pixels": visible,
        "alpha_coverage": round(coverage, 6),
    }


def validate(page_data_path: Path, expected_illustration_sha256: str | None) -> dict[str, Any]:
    data = load_json(page_data_path)
    illustration = resolve(str(data["illustration_path"]))
    logo = resolve(str(data["official_logo_path"]))
    star = resolve(str(data["official_star_path"]))

    illustration_size = validate_image(illustration, "illustration")
    logo_size = validate_image(logo, "official logo")
    illustration_hash = sha256(illustration)
    if expected_illustration_sha256 and illustration_hash != expected_illustration_sha256:
        raise ValueError(
            "FAIL_ILLUSTRATION_SOURCE_INTEGRITY: staged illustration hash does not match the supplied source"
        )

    evidence = data.get("illustration_evidence", {})
    forbidden = [
        "contains_text", "contains_logo", "contains_mascot", "contains_badge",
        "contains_page_layout", "contains_embedded_page",
    ]
    contaminated = [key for key in forbidden if evidence.get(key) is not False]
    if contaminated:
        raise ValueError(f"FAIL_CLEAN_ILLUSTRATION: {', '.join(contaminated)}")

    result = {
        "status": "PASS",
        "page_data": str(page_data_path),
        "illustration": {
            "path": str(illustration),
            "sha256": illustration_hash,
            "size": list(illustration_size),
        },
        "official_logo": {
            "path": str(logo),
            "sha256": sha256(logo),
            "size": list(logo_size),
        },
        "official_star": validate_star(star),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--page-data", required=True, type=Path)
    parser.add_argument("--expected-illustration-sha256")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate(args.page_data, args.expected_illustration_sha256)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
