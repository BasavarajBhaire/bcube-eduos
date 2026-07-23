#!/usr/bin/env python3
"""Batch-build completion pages and assembled PDFs for registered BCube books."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'bcube-publishing-sdk/books/cover-books.json'


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError(f'{path} must contain an object')
    return value


def run(command: list[str]) -> None:
    print('+', ' '.join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--level', choices=['nursery', 'lkg', 'ukg', 'all'], default='all')
    parser.add_argument('--book')
    parser.add_argument('--require-complete', action='store_true')
    parser.add_argument('--completion-pages', action='store_true')
    args = parser.parse_args()
    registry = load(REGISTRY)
    selected_levels = list(registry['levels']) if args.level == 'all' else [args.level]
    built = []
    for level in selected_levels:
        books = registry['levels'][level]['books']
        selected = [args.book] if args.book else sorted(books)
        for slug in selected:
            if slug not in books:
                raise ValueError(f'Unknown {level.upper()} book {slug!r}')
            if args.completion_pages:
                for page in ('certificate', 'back-cover'):
                    run([sys.executable, 'scripts/run_bcube_completion_pipeline.py', '--level', level, '--book', slug, '--page', page])
            command = [sys.executable, 'scripts/build_bcube_book.py', '--level', level, '--book', slug]
            if args.require_complete:
                command.append('--require-complete')
            run(command)
            built.append(f'{level}/{slug}')
    print(json.dumps({'status': 'PASS', 'books_built': built, 'count': len(built)}, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(f'BCube batch publish ERROR: {exc}', file=sys.stderr)
        raise SystemExit(2)
