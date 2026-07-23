#!/usr/bin/env python3
"""Validate rendered BCube pages and assemble a deterministic PDF."""
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


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError(f'{path} must contain an object')
    return value


def resolve(level: str, slug: str) -> tuple[dict[str, Any], dict[str, Any]]:
    registry = load(REGISTRY)
    level_data = registry['levels'].get(level)
    if not isinstance(level_data, dict):
        raise ValueError(f'Unknown level: {level}')
    book = level_data['books'].get(slug)
    if not isinstance(book, dict):
        raise ValueError(f'Unknown {level.upper()} book {slug!r}')
    return level_data, book


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def collect(level: str, slug: str, pages_dir: Path) -> tuple[str, list[Path]]:
    level_data, book = resolve(level, slug)
    stem = f"{book['prefix']}-{level_data['id_level']}-V4-P"
    pages = sorted(pages_dir.glob(f'{stem}*.png'))
    if not pages:
        raise FileNotFoundError(f'No rendered pages found for {level}/{slug} in {pages_dir}')
    parsed: dict[int, Path] = {}
    for path in pages:
        match = PAGE_RE.match(path.name)
        if not match:
            continue
        physical = int(match.group('physical'))
        if physical in parsed:
            raise ValueError(f'Duplicate physical page {physical}: {parsed[physical]} and {path}')
        parsed[physical] = path
    ordered = [parsed[key] for key in sorted(parsed)]
    return stem[:-1], ordered


def validate_pages(paths: list[Path], require_complete: bool) -> dict[str, Any]:
    physical = [int(PAGE_RE.match(path.name).group('physical')) for path in paths]
    missing = [number for number in range(min(physical), max(physical) + 1) if number not in physical]
    if require_complete:
        required_missing = [number for number in range(1, 45) if number not in physical]
        if required_missing:
            raise ValueError(f'Missing required physical pages: {required_missing}')
    elif missing:
        raise ValueError(f'Non-contiguous rendered page sequence: missing {missing}')
    page_details = []
    for path in paths:
        with Image.open(path) as image:
            if image.size != (2480, 3508):
                raise ValueError(f'Invalid A4 raster size for {path}: {image.size}')
            dpi = image.info.get('dpi', (0, 0))[0]
            if dpi and dpi < 299:
                raise ValueError(f'Invalid DPI for {path}: {dpi}')
            page_details.append({'path': str(path), 'physical': int(PAGE_RE.match(path.name).group('physical')), 'size': list(image.size), 'dpi': dpi, 'sha256': sha256(path)})
    return {'page_count': len(paths), 'first_physical': min(physical), 'last_physical': max(physical), 'missing': missing, 'pages': page_details}


def assemble(paths: list[Path], output: Path) -> None:
    images = [Image.open(path).convert('RGB') for path in paths]
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        images[0].save(output, 'PDF', resolution=300.0, save_all=True, append_images=images[1:])
    finally:
        for image in images:
            image.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--level', choices=['nursery', 'lkg', 'ukg'], required=True)
    parser.add_argument('--book', required=True)
    parser.add_argument('--pages-dir', type=Path, default=ROOT / 'production-renders/pages')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--require-complete', action='store_true')
    args = parser.parse_args()
    book_key, paths = collect(args.level, args.book, args.pages_dir)
    report = validate_pages(paths, args.require_complete)
    output = args.output or ROOT / 'production-renders/books' / f'{book_key}.pdf'
    manifest = args.manifest or ROOT / 'production-renders/books' / f'{book_key}.manifest.json'
    assemble(paths, output)
    report.update({'status': 'PASS', 'level': args.level, 'book': args.book, 'pdf': str(output), 'pdf_sha256': sha256(output)})
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'PASS', 'pdf': str(output), 'manifest': str(manifest), 'page_count': report['page_count']}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
