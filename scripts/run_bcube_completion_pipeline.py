#!/usr/bin/env python3
"""Build BCube certificate and back-cover pages for any registered book."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'bcube-publishing-sdk/books/cover-books.json'
COMPOSER = ROOT / 'bcube-publishing-sdk/composer/compose_completion_pages.py'


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError(f'{path} must contain an object')
    return value


def first_existing(candidates: list[str]) -> str:
    for value in candidates:
        if (ROOT / value).is_file():
            return value
    raise FileNotFoundError(f'No registered asset exists: {candidates}')


def resolve_book(level: str, slug: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    registry = load(REGISTRY)
    level_data = registry.get('levels', {}).get(level)
    if not isinstance(level_data, dict):
        raise ValueError(f'Unknown level: {level}')
    book = level_data.get('books', {}).get(slug)
    if not isinstance(book, dict):
        raise ValueError(f'Unknown {level.upper()} book {slug!r}')
    return registry, level_data, book


def build(level: str, slug: str, page_type: str) -> tuple[Path, Path, Path]:
    registry, level_data, book = resolve_book(level, slug)
    physical = 43 if page_type == 'certificate' else 44
    page_id = f"{book['prefix']}-{level_data['id_level']}-V4-P{physical:03d}"
    shared = registry['shared']
    data = {
        'page_id': page_id,
        'page_type': page_type,
        'book_title': ' '.join(book['title_lines']),
        'level': level_data['display_level'],
        'age': level_data['age'],
        'tagline': book.get('tagline', ''),
        'official_logo_path': first_existing(shared['official_logo_candidates']),
        'official_star_path': first_existing(shared['official_star_candidates']),
    }
    if page_type == 'certificate':
        data['achievement_message'] = f"for successfully completing {data['book_title']} and showing growth in {', '.join(book['skills'][:3])}."
    else:
        data['message'] = f"Keep exploring, creating and growing with {data['book_title']}."
    data_path = ROOT / 'production-renders/page-data' / f'{page_id}.json'
    output = ROOT / 'production-renders/pages' / f'{page_id}.png'
    evidence = ROOT / 'production-renders/qa-manifests' / f'{page_id}.json'
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    subprocess.run([sys.executable, str(COMPOSER), '--data', str(data_path), '--output', str(output), '--evidence-output', str(evidence)], cwd=ROOT, check=True)
    return data_path, output, evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--level', choices=['nursery', 'lkg', 'ukg'], required=True)
    parser.add_argument('--book', required=True)
    parser.add_argument('--page', choices=['certificate', 'back-cover'], required=True)
    args = parser.parse_args()
    page_type = 'back_cover' if args.page == 'back-cover' else args.page
    _, output, _ = build(args.level, args.book, page_type)
    print(f'BCube Phase 3 completion page COMPOSED: {output}')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(f'BCube Phase 3 ERROR: {exc}', file=sys.stderr)
        raise SystemExit(2)
