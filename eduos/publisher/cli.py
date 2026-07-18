#!/usr/bin/env python3
"""BCube Publisher CLI.

First executable product built on EduOS. The initial command performs strict
preflight only; it never bypasses unresolved templates, assets or policies.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "eduos" / "src"
KERNEL = ROOT / "eduos" / "kernel"
for module_path in (SRC, KERNEL):
    if str(module_path) not in sys.path:
        sys.path.insert(0, str(module_path))

from runtime import EduOSRuntime, RuntimeFailure  # type: ignore  # noqa: E402


def publish_manifest(manifest_path: Path, repository_root: Path) -> dict:
    runtime = EduOSRuntime(repository_root=repository_root)
    result = runtime.run(manifest_path)
    return {
        "status": "PREFLIGHT_PASSED",
        "prompt_id": result.prompt_id,
        "template_id": result.template_id,
        "asset_ids": result.asset_ids,
        "events": result.events,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bcube", description="BCube Publisher")
    subcommands = parser.add_subparsers(dest="command", required=True)

    publish = subcommands.add_parser("publish", help="Preflight and publish a page manifest")
    publish.add_argument("manifest", type=Path)
    publish.add_argument("--root", type=Path, default=ROOT)
    publish.add_argument("--json", action="store_true", help="Print machine-readable output")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = publish_manifest(args.manifest, args.root)
    except (RuntimeFailure, OSError, ValueError, KeyError) as exc:
        payload = {"status": "REJECTED", "error": str(exc)}
        if getattr(args, "json", False):
            print(json.dumps(payload, indent=2))
        else:
            print(f"REJECTED: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"PREFLIGHT PASSED: {result['prompt_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
