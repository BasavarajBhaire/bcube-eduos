#!/usr/bin/env python3
"""Verify a BCube approved release package and its lock evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any


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


def verify(release_dir: Path) -> dict[str, Any]:
    manifests = sorted(release_dir.glob('*.release.json'))
    locks = sorted(release_dir.glob('*.release.lock'))
    packages = sorted(release_dir.glob('*-RELEASE.zip'))
    if len(manifests) != 1 or len(locks) != 1 or len(packages) != 1:
        raise ValueError('Expected exactly one release manifest, lock, and ZIP package')
    manifest_path, lock_path, package_path = manifests[0], locks[0], packages[0]
    manifest = load(manifest_path)
    lock = load(lock_path)
    if manifest.get('state') != 'APPROVED_LOCKED' or manifest.get('approved') is not True:
        raise ValueError('Release is not approved and locked')
    pdf_path = release_dir / str(manifest.get('pdf', ''))
    preflight_path = release_dir / str(manifest.get('preflight_report', ''))
    assembly_path = release_dir / str(manifest.get('assembly_manifest', ''))
    for path in (pdf_path, preflight_path, assembly_path):
        if not path.is_file():
            raise FileNotFoundError(f'Missing release component: {path}')
    pdf_hash = sha256(pdf_path)
    manifest_hash = sha256(manifest_path)
    if pdf_hash != manifest.get('pdf_sha256') or pdf_hash != lock.get('pdf_sha256'):
        raise ValueError('PDF SHA-256 does not match release evidence')
    if manifest_hash != lock.get('manifest_sha256'):
        raise ValueError('Release manifest SHA-256 does not match lock evidence')
    with zipfile.ZipFile(package_path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f'Corrupt ZIP member: {bad}')
        names = set(archive.namelist())
        required = {pdf_path.name, preflight_path.name, assembly_path.name, manifest_path.name}
        missing = sorted(required - names)
        if missing:
            raise ValueError(f'Release ZIP is missing files: {missing}')
    return {
        'status': 'PASS',
        'book_id': manifest.get('book_id'),
        'release_dir': str(release_dir),
        'pdf_sha256': pdf_hash,
        'manifest_sha256': manifest_hash,
        'package_sha256': sha256(package_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--release-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = verify(args.release_dir)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, zipfile.BadZipFile) as exc:
        print(f'BCube Phase 5 VERIFY FAILED: {exc}')
        raise SystemExit(2)
