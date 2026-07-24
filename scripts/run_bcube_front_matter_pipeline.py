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
ABOUT_COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_about_page.py"
ABOUT_VALIDATOR = ROOT / "bcube-publishing-sdk/validators/validate_about_inputs.py"
PUBLISHER_COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_publisher_page.py"
PUBLISHER_VALIDATOR = ROOT / "bcube-publishing-sdk/validators/validate_publisher_inputs.py"
SPECIAL_COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_special_page.py"
SPECIAL_VALIDATOR = ROOT / "bcube-publishing-sdk/validators/validate_special_inputs.py"


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


def resolve_star(registry: dict[str, Any]) -> str:
    candidates = registry.get("shared", {}).get("official_star_candidates", [])
    for candidate in candidates:
        if valid_image(ROOT / candidate):
            return candidate
    raise FileNotFoundError("No valid official BCube Star found in shared registry candidates")


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


def publication_number(level: str, slug: str) -> int:
    portfolio = load(ROOT / f"production-prompts/{level}/V4_PORTFOLIO_MANIFEST.json")
    books = portfolio.get("books") if level == "nursery" else portfolio.get("completed")
    if not isinstance(books, list):
        raise ValueError(f"Portfolio manifest contains no official book sequence for {level}")
    for index, book in enumerate(books, start=1):
        if isinstance(book, dict) and book.get("slug") == slug:
            return index
    raise ValueError(f"{slug!r} is not in the official {level.upper()} portfolio sequence")


def contents_entries(level: str, slug: str, contents_physical: int) -> list[dict[str, Any]]:
    manifest_path = prompt_manifest(level, slug)
    manifest = load(manifest_path)
    first, last = (6, 24) if contents_physical == 4 else (25, 43)
    entries = []
    for page in manifest.get("pages", []):
        printed = page.get("printed")
        physical = page.get("physical")
        if printed is None or not isinstance(physical, int) or not first <= physical <= last:
            continue
        source = load(manifest_path.parent / page["json"])
        preserved = source.get("preserved_source", {}).get("page_data", {})
        module = str(preserved.get("unit_id") or "").strip() if isinstance(preserved, dict) else ""
        if not module:
            source_relative = source.get("source_lineage", {}).get("relative_file")
            if isinstance(source_relative, str) and source_relative.strip():
                canonical_source = load(ROOT / source_relative)
                canonical_page_data = canonical_source.get("page_data", {})
                if isinstance(canonical_page_data, dict):
                    module = str(canonical_page_data.get("unit_id") or "").strip()
        if not module and physical in {6, 7}:
            module = "FRONT_MATTER"
        if not module:
            raise ValueError(f"Contents entry {page.get('prompt_id')} has no canonical module")
        entries.append({
            "physical": physical,
            "title": page["title"],
            "page": printed,
            "module": module,
        })
    if len(entries) != 19:
        raise ValueError(f"Contents physical page {contents_physical} resolved {len(entries)} entries; expected 19")
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
    defaults = {"about": 2, "publisher": 3, "contents": 4, "welcome": 6, "meet-star": 7}
    physical = args.physical_page or defaults[page_type]
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
    elif page_type == "publisher":
        publisher = registry.get("shared", {}).get("publisher")
        if not isinstance(publisher, dict):
            raise ValueError("Shared publisher registry is missing")
        code_level = {"nursery": "NUR", "lkg": "LKG", "ukg": "UKG"}[level]
        number = publication_number(level, slug)
        year = int(publisher["copyright_year"])
        data = {
            "page_id": page_id,
            "page_type": "publisher",
            "physical_page": physical,
            "book_title": title,
            "book_title_lines": list(book["title_lines"]),
            "page_title": "Publication & Copyright",
            "level": level_data["display_level"],
            "publisher": dict(publisher),
            "publication_code": f"BCUBE-{code_level}-{book['prefix']}-{number:03d}",
            "document_id": f"{book['prefix']}-{level_data['id_level']}-PILOT-{year}",
            "copyright_notice": f"© {year} {publisher['name']}. All rights reserved.",
            "official_logo_path": resolve_logo(registry),
        }
    elif page_type == "contents":
        if physical not in {4, 5}:
            raise ValueError("Contents must use physical page 4 or 5")
        data = {
            "page_id": page_id,
            "page_type": "contents",
            "physical_page": physical,
            "book_title": title,
            "book_title_lines": list(book["title_lines"]),
            "page_title": args.title or f"Contents — Part {physical - 3}",
            "level": level_data["display_level"],
            "tagline": book["tagline"],
            "core_pillars": [pillar["name"] for pillar in registry["shared"]["pillars"]],
            "footer_keywords": book["footer_keywords"],
            "official_logo_path": resolve_logo(registry),
            "entries": contents_entries(level, slug, physical),
        }
    elif page_type == "welcome":
        if physical != 6 or args.page_number != 5:
            raise ValueError("Welcome must be physical page 6 and visibly numbered 5")
        if args.illustration is None:
            raise ValueError("Welcome pages require --illustration")
        illustration = stage_illustration(args.illustration, page_id)
        data = {
            "page_id": page_id,
            "page_type": "welcome",
            "physical_page": physical,
            "page_number": args.page_number,
            "book_title": title,
            "book_title_lines": list(book["title_lines"]),
            "page_title": args.title or f"Welcome to {title}",
            "level": level_data["display_level"],
            "tagline": book["tagline"],
            "message": args.instruction or f"Welcome to the {title} learning journey.",
            "core_pillars": [pillar["name"] for pillar in registry["shared"]["pillars"]],
            "footer_keywords": book["footer_keywords"],
            "illustration_path": repo_relative(illustration),
            "official_logo_path": resolve_logo(registry),
        }
    else:
        if physical != 7 or args.page_number != 6:
            raise ValueError("Meet Star must be physical page 7 and visibly numbered 6")
        data = {
            "page_id": page_id,
            "page_type": "meet_star",
            "physical_page": physical,
            "page_number": args.page_number,
            "book_title": title,
            "book_title_lines": list(book["title_lines"]),
            "page_title": args.title or "Meet Star",
            "level": level_data["display_level"],
            "tagline": book["tagline"],
            "message": args.instruction or "Meet Star, your friendly guide for this learning journey.",
            "purpose": args.objective or f"Star encourages children as they explore {title}.",
            "core_pillars": [pillar["name"] for pillar in registry["shared"]["pillars"]],
            "footer_keywords": book["footer_keywords"],
            "official_logo_path": resolve_logo(registry),
            "official_star_path": resolve_star(registry),
        }

    data_path = ROOT / "production-renders/page-data" / f"{page_id}.json"
    output = ROOT / "production-renders/pages" / f"{page_id}.png"
    evidence = ROOT / "production-renders/qa-manifests" / f"{page_id}.json"
    report_suffix = {
        "about": "about-input",
        "publisher": "publisher-input",
        "contents": "contents-input",
        "welcome": "welcome-input",
        "meet-star": "meet-star-input",
    }.get(page_type)
    report = ROOT / "validation/rendered-pages" / f"{page_id}.{report_suffix}.json" if report_suffix else None
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return data_path, output, evidence, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", choices=["nursery", "lkg", "ukg"], required=True)
    parser.add_argument("--book", required=True)
    parser.add_argument("--page", choices=["about", "publisher", "contents", "welcome", "meet-star"], required=True)
    parser.add_argument("--illustration", type=Path)
    parser.add_argument("--physical-page", type=int)
    parser.add_argument("--page-number", type=int)
    parser.add_argument("--page-id")
    parser.add_argument("--title")
    parser.add_argument("--objective")
    parser.add_argument("--instruction")
    args = parser.parse_args()
    data, output, evidence, report = build_data(args)
    composer = {
        "about": ABOUT_COMPOSER,
        "publisher": PUBLISHER_COMPOSER,
        "contents": SPECIAL_COMPOSER,
        "welcome": SPECIAL_COMPOSER,
        "meet-star": SPECIAL_COMPOSER,
    }[args.page]
    validator = {
        "about": ABOUT_VALIDATOR,
        "publisher": PUBLISHER_VALIDATOR,
        "contents": SPECIAL_VALIDATOR,
        "welcome": SPECIAL_VALIDATOR,
        "meet-star": SPECIAL_VALIDATOR,
    }.get(args.page)
    if validator is not None:
        if report is None:
            raise ValueError(f"{args.page.title()}-page input report path was not resolved")
        report.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [sys.executable, str(validator), "--data", str(data), "--output", str(report)],
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
