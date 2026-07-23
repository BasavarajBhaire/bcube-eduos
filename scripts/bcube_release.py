#!/usr/bin/env python3
"""Create an approved and locked BCube production release package."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / 'scripts/bcube_preflight.py'
BOOK_BUILDER = ROOT / 'scripts/build_bcube_book.py'
REGISTRY = ROOT / 'bcube-publishing-sdk/books/cover-books.json'


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
    level_data = registry['levels'].get(level)
    if not isinstance(level_data, dict):
        raise ValueError(f'Unknown level: {level}')
    book = level_data['books'].get(slug)
    if not isinstance(book, dict):
        raise ValueError(f'Unknown {level.upper()} book {slug!r}')
    return level_data, book


def git_value(*args: str) -> str:
    try:
        return subprocess.check_output(['git', *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return 'unknown'


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--level', choices=['nursery', 'lkg', 'ukg'], required=True)
    parser.add_argument('--book', required=True)
    parser.add_argument('--reviewer')
    parser.add_argument('--approve', action='store_true')
    parser.add_argument('--release-root', type=Path, default=ROOT / 'production-releases')
    args = parser.parse_args()

    level_data, book = resolve(args.level, args.book)
    book_id = f"{book['prefix']}-{level_data['id_level']}-V4"
    preflight_path = ROOT / 'production-renders/preflight' / f'{book_id}.preflight.json'

    subprocess.run([sys.executable, str(PREFLIGHT), '--level', args.level, '--book', args.book, '--output', str(preflight_path)], cwd=ROOT, check=True)
    preflight = load(preflight_path)
    if preflight.get('status') != 'PASS':
        raise ValueError('Release blocked because production preflight did not pass')

    subprocess.run([sys.executable, str(BOOK_BUILDER), '--level', args.level, '--book', args.book, '--require-complete'], cwd=ROOT, check=True)
    source_pdf = ROOT / 'production-renders/books' / f'{book_id}.pdf'
    source_manifest = ROOT / 'production-renders/books' / f'{book_id}.manifest.json'
    if not source_pdf.is_file() or not source_manifest.is_file():
        raise FileNotFoundError('Book PDF or assembly manifest was not created')

    release_dir = args.release_root / args.level / args.book / 'v4'
    release_dir.mkdir(parents=True, exist_ok=True)
    pdf_name = f'{book_id}-PRINT-READY.pdf'
    pdf_target = release_dir / pdf_name
    shutil.copy2(source_pdf, pdf_target)
    shutil.copy2(preflight_path, release_dir / f'{book_id}.preflight.json')
    shutil.copy2(source_manifest, release_dir / f'{book_id}.assembly.json')

    approved = bool(args.approve)
    reviewer = args.reviewer or ('UNSPECIFIED' if approved else None)
    release_manifest = {
        'release_standard': 'BCube Phase 4 Production Release v1.0',
        'state': 'APPROVED_LOCKED' if approved else 'REVIEW_REQUIRED',
        'approved': approved,
        'reviewer': reviewer,
        'approved_at_utc': datetime.now(timezone.utc).isoformat() if approved else None,
        'level': args.level,
        'book': args.book,
        'book_title': ' '.join(book['title_lines']),
        'book_id': book_id,
        'page_count': preflight['page_count'],
        'critical_defects': len(preflight['defects']),
        'pdf': pdf_name,
        'pdf_sha256': sha256(pdf_target),
        'source_commit': git_value('rev-parse', 'HEAD'),
        'source_branch': git_value('rev-parse', '--abbrev-ref', 'HEAD'),
        'preflight_report': f'{book_id}.preflight.json',
        'assembly_manifest': f'{book_id}.assembly.json',
    }
    manifest_path = release_dir / f'{book_id}.release.json'
    manifest_path.write_text(json.dumps(release_manifest, indent=2) + '\n', encoding='utf-8')

    zip_path = release_dir / f'{book_id}-RELEASE.zip'
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(release_dir.iterdir()):
            if path == zip_path:
                continue
            archive.write(path, path.name)

    lock_path = release_dir / f'{book_id}.release.lock'
    if approved:
        lock_path.write_text(json.dumps({'book_id': book_id, 'pdf_sha256': release_manifest['pdf_sha256'], 'manifest_sha256': sha256(manifest_path)}, indent=2) + '\n', encoding='utf-8')

    print(json.dumps({'status': release_manifest['state'], 'release_dir': str(release_dir), 'manifest': str(manifest_path), 'package': str(zip_path), 'lock': str(lock_path) if approved else None}, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(f'BCube Phase 4 RELEASE BLOCKED: {exc}', file=sys.stderr)
        raise SystemExit(2)
