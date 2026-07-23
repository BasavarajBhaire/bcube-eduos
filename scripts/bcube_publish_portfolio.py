#!/usr/bin/env python3
"""Run resumable commercial publishing across BCube books and levels."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'bcube-publishing-sdk/books/cover-books.json'
RELEASE = ROOT / 'scripts/bcube_release.py'
VERIFY = ROOT / 'scripts/bcube_verify_release.py'


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError(f'{path} must contain a JSON object')
    return value


def selected_books(level: str, book: str | None) -> list[tuple[str, str]]:
    registry = load(REGISTRY)
    levels = ['nursery', 'lkg', 'ukg'] if level == 'all' else [level]
    items: list[tuple[str, str]] = []
    for level_key in levels:
        books = registry['levels'][level_key]['books']
        if book:
            if book not in books:
                raise ValueError(f'Unknown {level_key.upper()} book {book!r}')
            items.append((level_key, book))
        else:
            items.extend((level_key, slug) for slug in books)
    return items


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--level', choices=['nursery', 'lkg', 'ukg', 'all'], default='all')
    parser.add_argument('--book')
    parser.add_argument('--approve', action='store_true')
    parser.add_argument('--reviewer')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--continue-on-error', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--release-root', type=Path, default=ROOT / 'production-releases')
    parser.add_argument('--state-file', type=Path, default=ROOT / 'production-releases/portfolio-run.json')
    args = parser.parse_args()

    if args.approve and not args.reviewer:
        raise ValueError('--reviewer is required with --approve')

    targets = selected_books(args.level, args.book)
    previous = load(args.state_file) if args.resume and args.state_file.is_file() else {'books': {}}
    state: dict[str, Any] = {
        'phase': 'BCube Phase 5 Commercial Publishing Orchestrator',
        'started_at_utc': datetime.now(timezone.utc).isoformat(),
        'level': args.level,
        'approved': bool(args.approve),
        'reviewer': args.reviewer,
        'books': dict(previous.get('books', {})),
    }

    for level, slug in targets:
        key = f'{level}/{slug}'
        existing = state['books'].get(key, {})
        if args.resume and existing.get('status') == 'PASS':
            continue
        if args.dry_run:
            state['books'][key] = {'status': 'PLANNED'}
            continue
        command = [sys.executable, str(RELEASE), '--level', level, '--book', slug, '--release-root', str(args.release_root)]
        if args.approve:
            command.extend(['--approve', '--reviewer', args.reviewer])
        try:
            subprocess.run(command, cwd=ROOT, check=True)
            release_dir = args.release_root / level / slug / 'v4'
            verify_report = release_dir / 'phase5.verify.json'
            if args.approve:
                subprocess.run([sys.executable, str(VERIFY), '--release-dir', str(release_dir), '--output', str(verify_report)], cwd=ROOT, check=True)
            state['books'][key] = {'status': 'PASS', 'release_dir': str(release_dir), 'verified': bool(args.approve)}
        except subprocess.CalledProcessError as exc:
            state['books'][key] = {'status': 'FAIL', 'exit_code': exc.returncode}
            if not args.continue_on_error:
                break
        finally:
            args.state_file.parent.mkdir(parents=True, exist_ok=True)
            args.state_file.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')

    results = list(state['books'].values())
    state['completed_at_utc'] = datetime.now(timezone.utc).isoformat()
    state['summary'] = {
        'targets': len(targets),
        'passed': sum(1 for item in results if item.get('status') == 'PASS'),
        'failed': sum(1 for item in results if item.get('status') == 'FAIL'),
        'planned': sum(1 for item in results if item.get('status') == 'PLANNED'),
    }
    state['status'] = 'PASS' if state['summary']['failed'] == 0 else 'FAIL'
    args.state_file.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': state['status'], 'state_file': str(args.state_file), **state['summary']}, indent=2))
    return 0 if state['status'] == 'PASS' else 2


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError) as exc:
        print(f'BCube Phase 5 ORCHESTRATION FAILED: {exc}', file=sys.stderr)
        raise SystemExit(2)
