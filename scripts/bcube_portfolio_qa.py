#!/usr/bin/env python3
"""Build a portfolio-level QA dashboard for all registered BCube books."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from bcube_preflight import ROOT, REGISTRY, preflight


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError(f'{path} must contain a JSON object')
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--level', choices=['nursery', 'lkg', 'ukg', 'all'], default='all')
    parser.add_argument('--pages-dir', type=Path, default=ROOT / 'production-renders/pages')
    parser.add_argument('--output', type=Path, default=ROOT / 'production-renders/portfolio/phase4-portfolio-qa.json')
    args = parser.parse_args()

    registry = load(REGISTRY)
    levels = list(registry['levels']) if args.level == 'all' else [args.level]
    books: list[dict[str, Any]] = []
    summary: dict[str, Any] = {'books_total': 0, 'books_passed': 0, 'books_failed': 0, 'critical_defects': 0, 'levels': {}}

    for level in levels:
        level_books = registry['levels'][level]['books']
        level_summary = {'books_total': len(level_books), 'books_passed': 0, 'books_failed': 0, 'critical_defects': 0}
        for slug in level_books:
            report = preflight(level, slug, args.pages_dir)
            item = {
                'level': level,
                'book': slug,
                'book_id': report['book_id'],
                'status': report['status'],
                'page_count': report['page_count'],
                'defect_count': len(report['defects']),
                'defects': report['defects'],
            }
            books.append(item)
            passed = report['status'] == 'PASS'
            level_summary['books_passed' if passed else 'books_failed'] += 1
            level_summary['critical_defects'] += len(report['defects'])
        summary['levels'][level] = level_summary
        summary['books_total'] += level_summary['books_total']
        summary['books_passed'] += level_summary['books_passed']
        summary['books_failed'] += level_summary['books_failed']
        summary['critical_defects'] += level_summary['critical_defects']

    result = {
        'engine': 'BCube Phase 4 Portfolio QA',
        'status': 'PASS' if summary['books_failed'] == 0 else 'FAIL',
        'summary': summary,
        'books': books,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], 'report': str(args.output), **summary}, indent=2))
    return 0 if result['status'] == 'PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
