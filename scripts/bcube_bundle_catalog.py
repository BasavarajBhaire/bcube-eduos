#!/usr/bin/env python3
"""Build a deterministic BCube commercial catalog bundle from approved releases."""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--release-root', type=Path, default=ROOT / 'production-releases')
    parser.add_argument('--level', choices=['nursery', 'lkg', 'ukg', 'all'], default='all')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'production-releases/catalog')
    parser.add_argument('--require-all', action='store_true')
    args = parser.parse_args()

    manifests = sorted(args.release_root.glob('*/*/v4/*.release.json'))
    selected: list[tuple[Path, dict[str, Any]]] = []
    for path in manifests:
        manifest = load(path)
        if manifest.get('state') != 'APPROVED_LOCKED':
            continue
        if args.level != 'all' and manifest.get('level') != args.level:
            continue
        selected.append((path, manifest))
    expected = 30 if args.level == 'all' else 10
    if args.require_all and len(selected) != expected:
        raise ValueError(f'Expected {expected} approved releases, found {len(selected)}')
    if not selected:
        raise ValueError('No approved releases found')

    args.output_dir.mkdir(parents=True, exist_ok=True)
    catalog_name = f"BCUBE-{args.level.upper()}-COMMERCIAL-CATALOG-V4"
    bundle_path = args.output_dir / f'{catalog_name}.zip'
    entries = []
    with zipfile.ZipFile(bundle_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for manifest_path, manifest in selected:
            release_dir = manifest_path.parent
            package = release_dir / f"{manifest['book_id']}-RELEASE.zip"
            lock = release_dir / f"{manifest['book_id']}.release.lock"
            if not package.is_file() or not lock.is_file():
                raise FileNotFoundError(f'Incomplete approved release: {release_dir}')
            arc_prefix = f"{manifest['level']}/{manifest['book']}"
            archive.write(package, f'{arc_prefix}/{package.name}')
            archive.write(manifest_path, f'{arc_prefix}/{manifest_path.name}')
            archive.write(lock, f'{arc_prefix}/{lock.name}')
            entries.append({
                'level': manifest['level'],
                'book': manifest['book'],
                'book_id': manifest['book_id'],
                'package': f'{arc_prefix}/{package.name}',
                'package_sha256': sha256(package),
                'pdf_sha256': manifest['pdf_sha256'],
            })
        catalog = {
            'standard': 'BCube Phase 5 Commercial Catalog v1.0',
            'created_at_utc': datetime.now(timezone.utc).isoformat(),
            'level': args.level,
            'release_count': len(entries),
            'complete': len(entries) == expected,
            'releases': entries,
        }
        archive.writestr(f'{catalog_name}.manifest.json', json.dumps(catalog, indent=2) + '\n')

    report = {'status': 'PASS', 'bundle': str(bundle_path), 'bundle_sha256': sha256(bundle_path), 'release_count': len(entries), 'complete': len(entries) == expected}
    report_path = args.output_dir / f'{catalog_name}.report.json'
    report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, zipfile.BadZipFile) as exc:
        print(f'BCube Phase 5 CATALOG FAILED: {exc}')
        raise SystemExit(2)
