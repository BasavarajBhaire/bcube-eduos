#!/usr/bin/env python3
"""Run strict BCube commercial print preflight for one rendered book."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'bcube-publishing-sdk/books/cover-books.json'
PAGE_RE = re.compile(r'^(?P<prefix>[A-Z]{2})-(?P<level>NURSERY|LKG|UKG)-V4-P(?P<physical>\d{3})\.png$')
EXPECTED_SIZE = (2480, 3508)
EXPECTED_PHYSICAL = tuple(range(1, 45))


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError(f'{path} must contain a JSON object')
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def resolve(level: str, slug: str) -> tuple[dict[str, Any], dict[str, Any]]:
    registry = load(REGISTRY)
    level_data = registry.get('levels', {}).get(level)
    if not isinstance(level_data, dict):
        raise ValueError(f'Unknown level: {level}')
    book = level_data.get('books', {}).get(slug)
    if not isinstance(book, dict):
        raise ValueError(f'Unknown {level.upper()} book {slug!r}')
    return level_data, book


def preflight(level: str, slug: str, pages_dir: Path) -> dict[str, Any]:
    level_data, book = resolve(level, slug)
    prefix = book['prefix']
    id_level = level_data['id_level']
    stem = f'{prefix}-{id_level}-V4-P'
    candidates = sorted(pages_dir.glob(f'{stem}*.png'))
    parsed: dict[int, Path] = {}
    defects: list[dict[str, Any]] = []

    for path in candidates:
        match = PAGE_RE.match(path.name)
        if not match:
            continue
        physical = int(match.group('physical'))
        if physical in parsed:
            defects.append({'code': 'DUPLICATE_PAGE', 'physical': physical, 'paths': [str(parsed[physical]), str(path)]})
        else:
            parsed[physical] = path

    missing = [n for n in EXPECTED_PHYSICAL if n not in parsed]
    extras = [n for n in parsed if n not in EXPECTED_PHYSICAL]
    if missing:
        defects.append({'code': 'MISSING_PAGES', 'physical_pages': missing})
    if extras:
        defects.append({'code': 'UNEXPECTED_PAGES', 'physical_pages': extras})

    pages: list[dict[str, Any]] = []
    for physical in sorted(parsed):
        path = parsed[physical]
        try:
            with Image.open(path) as image:
                size = image.size
                dpi_value = image.info.get('dpi', (0, 0))
                dpi = float(dpi_value[0] if isinstance(dpi_value, (tuple, list)) else dpi_value or 0)
                mode = image.mode
                image.verify()
            if size != EXPECTED_SIZE:
                defects.append({'code': 'INVALID_PAGE_SIZE', 'physical': physical, 'actual': list(size), 'expected': list(EXPECTED_SIZE)})
            if dpi < 299:
                defects.append({'code': 'INVALID_DPI', 'physical': physical, 'actual': dpi, 'minimum': 299})
            pages.append({'physical': physical, 'path': str(path), 'size': list(size), 'dpi': dpi, 'mode': mode, 'sha256': sha256(path)})
        except Exception as exc:
            defects.append({'code': 'UNREADABLE_PAGE', 'physical': physical, 'path': str(path), 'error': str(exc)})

    required_roles = {1: 'cover', 2: 'about', 3: 'publisher', 4: 'contents_part_1', 5: 'contents_part_2', 43: 'certificate', 44: 'back_cover'}
    role_status = {str(page): {'role': role, 'present': page in parsed} for page, role in required_roles.items()}
    status = 'PASS' if not defects else 'FAIL'
    return {
        'engine': 'BCube Phase 4 Production Preflight',
        'status': status,
        'level': level,
        'book': slug,
        'book_title': ' '.join(book['title_lines']),
        'book_id': f'{prefix}-{id_level}-V4',
        'expected_page_count': 44,
        'page_count': len(parsed),
        'required_roles': role_status,
        'defects': defects,
        'pages': pages,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--level', choices=['nursery', 'lkg', 'ukg'], required=True)
    parser.add_argument('--book', required=True)
    parser.add_argument('--pages-dir', type=Path, default=ROOT / 'production-renders/pages')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = preflight(args.level, args.book, args.pages_dir)
    output = args.output or ROOT / 'production-renders/preflight' / f"{report['book_id']}.preflight.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'report': str(output), 'defect_count': len(report['defects'])}, indent=2))
    return 0 if report['status'] == 'PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
