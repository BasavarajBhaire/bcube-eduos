#!/usr/bin/env python3
"""Build BCube About, Publisher, and Contents pages for any registered book."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "bcube-publishing-sdk/books/cover-books.json"
COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_front_matter.py"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def valid_image(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        with Image.open(path) as image:
            image.verify()
        return True
    except Exception:
        return False


def resolve_logo(registry: dict[str, Any]) -> str:
    candidates = registry.get("shared", {}).get("official_logo_candidates", [])
    for candidate in candidates:
        if valid_image(ROOT / candidate):
            return candidate
    raise FileNotFoundError("No valid official BCube logo found in shared registry candidates")


def resolve(level: str, slug: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    registry = load(REGISTRY)
    level_data = registry.get("levels", {}).get(level)
    if not isinstance(level_data, dict):
        raise ValueError(f"Unknown level: {level}")
    book = level_data.get("books", {}).get(slug)
    if not isinstance(book, dict):
        raise ValueError(f"Unknown {level.upper()} book {slug!r}")
    return registry, level_data, book


def prompt_manifest(level: str, slug: str) -> Path:
    candidates = [
        ROOT / f"production-prompts/{slug}/{level}/v4/release-manifest.json",
        ROOT / f"production-prompts/{slug}/{level}/V4/release-manifest.json",
    ]
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError(f"No V4 release manifest found for {level}/{slug}")


def contents_entries(level: str, slug: str) -> list[dict[str, Any]]:
    manifest = load(prompt_manifest(level, slug))
    entries = []
    for page in manifest.get("pages", []):
        printed = page.get("printed")
        physical = page.get("physical")
        if printed is None or not isinstance(physical, int) or physical < 6:
            continue
        entries.append({"title": page["title"], "page": printed, "module": page.get("module", "")})
    return entries


def build_data(level: str, slug: str, page_type: str) -> tuple[Path, Path, Path]:
    registry, level_data, book = resolve(level, slug)
    physical = {"about": 2, "publisher": 3, "contents": 4}[page_type]
    page_id = f"{book['prefix']}-{level_data['id_level']}-V4-P{physical:03d}"
    title = " ".join(book["title_lines"])
    data: dict[str, Any] = {
        "page_id": page_id,
        "page_type": page_type,
        "book_title": title,
        "level": level_data["display_level"],
        "age": level_data["age"],
        "series": "BCube Future Skills Learning Series™",
        "logo_path": resolve_logo(registry),
    }
    if page_type == "about":
        data["paragraphs"] = [
            f"{title} is designed for {level_data['display_level']} children aged {level_data['age']}. It develops age-appropriate knowledge, communication, thinking and independent learning through guided play and purposeful activities.",
            f"Children practise six important outcomes: {', '.join(book['skills'])}. Teachers may model each activity first, while families can reinforce the same skill through short everyday conversations and playful practice.",
        ]
        data["pillars"] = ["Creativity", "Communication", "Curiosity", "Confidence", "Collaboration"]
    elif page_type == "publisher":
        data["publisher_rows"] = [
            ["Publisher", "BCube Future Academy"],
            ["Address", "407, DSMAX Sky Supreme, KST, Bangalore - 560060"],
            ["Email", "info@bcubefutureacademy.in"],
            ["Website", "bcubefutureacademy.in"],
            ["Edition", "First Edition, 2026"],
            ["Copyright", "© 2026 BCube Future Academy. All rights reserved."],
        ]
    else:
        data["entries"] = contents_entries(level, slug)
    data_path = ROOT / "production-renders/page-data" / f"{page_id}.json"
    output = ROOT / "production-renders/pages" / f"{page_id}.png"
    evidence = ROOT / "production-renders/qa-manifests" / f"{page_id}.json"
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return data_path, output, evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", choices=["nursery", "lkg", "ukg"], required=True)
    parser.add_argument("--book", required=True)
    parser.add_argument("--page", choices=["about", "publisher", "contents"], required=True)
    args = parser.parse_args()
    data, output, evidence = build_data(args.level, args.book, args.page)
    subprocess.run([sys.executable, str(COMPOSER), "--data", str(data), "--output", str(output),
                    "--evidence-output", str(evidence)], cwd=ROOT, check=True)
    print(f"BCube V6 front matter COMPOSED: {output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(f"BCube V6 front matter ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
