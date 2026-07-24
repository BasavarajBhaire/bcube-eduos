#!/usr/bin/env python3
"""Build BCube About, Publisher, and Contents pages for registered books."""
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
LEGACY_COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_front_matter.py"
ABOUT_COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_about_page.py"
ABOUT_VALIDATOR = ROOT / "bcube-publishing-sdk/validators/validate_about_inputs.py"


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


def repo_relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def stage_illustration(source: Path, page_id: str) -> Path:
    source = source.expanduser().resolve()
    if not valid_image(source):
        raise FileNotFoundError(f"Illustration is missing or unreadable: {source}")
    destination = ROOT / "production-renders/front-matter/illustrations" / f"{page_id}.png"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        image.convert("RGB").save(destination, "PNG", dpi=(300, 300))
    return destination


def build_data(args: argparse.Namespace) -> tuple[Path, Path, Path, Path | None]:
    level, slug, page_type = args.level, args.book, args.page
    registry, level_data, book = resolve(level, slug)
    physical = {"about": 2, "publisher": 3, "contents": 4}[page_type]
    page_id = args.page_id or f"{book['prefix']}-{level_data['id_level']}-V4-P{physical:03d}"
    title = " ".join(book["title_lines"])

    if page_type == "about":
        if args.illustration is None:
            raise ValueError("About pages require --illustration")
        illustration = stage_illustration(args.illustration, page_id)
        data: dict[str, Any] = {
            "page_id": page_id,
            "page_type": "about",
            "physical_page": physical,
            "book_title": title,
            "book_title_lines": list(book["title_lines"]),
            "page_title": args.title or "About This Book",
            "level": level_data["display_level"],
            "learning_objective": args.objective or (
                f"Introduce families and teachers to the purpose and learning journey of {title}."
            ),
            "overview": args.instruction or (
                "Explore the book through guided play, conversation, observation, and child response."
            ),
            "learning_outcomes": list(book["skills"]),
            "core_pillars": [pillar["name"] for pillar in registry["shared"]["pillars"]],
            "footer_keywords": book["footer_keywords"],
            "illustration_path": repo_relative(illustration),
            "official_logo_path": resolve_logo(registry),
        }
    else:
        data = {
            "page_id": page_id,
            "page_type": page_type,
            "book_title": title,
            "level": level_data["display_level"],
            "age": level_data["age"],
            "series": registry["series"],
            "logo_path": resolve_logo(registry),
        }
        if page_type == "publisher":
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
    report = ROOT / "validation/rendered-pages" / f"{page_id}.about-input.json" if page_type == "about" else None
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return data_path, output, evidence, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", choices=["nursery", "lkg", "ukg"], required=True)
    parser.add_argument("--book", required=True)
    parser.add_argument("--page", choices=["about", "publisher", "contents"], required=True)
    parser.add_argument("--illustration", type=Path)
    parser.add_argument("--page-id")
    parser.add_argument("--title")
    parser.add_argument("--objective")
    parser.add_argument("--instruction")
    args = parser.parse_args()
    data, output, evidence, report = build_data(args)
    composer = ABOUT_COMPOSER if args.page == "about" else LEGACY_COMPOSER
    if args.page == "about":
        if report is None:
            raise ValueError("About-page input report path was not resolved")
        report.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [sys.executable, str(ABOUT_VALIDATOR), "--data", str(data), "--output", str(report)],
            cwd=ROOT,
            check=True,
        )
    subprocess.run(
        [sys.executable, str(composer), "--data", str(data), "--output", str(output),
         "--evidence-output", str(evidence)],
        cwd=ROOT,
        check=True,
    )
    print(f"BCube front matter COMPOSED: {output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(f"BCube front matter ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
