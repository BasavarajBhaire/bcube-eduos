#!/usr/bin/env python3
"""Run BCube Phase 6 illustration automation for one book, level, or portfolio."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "bcube-publishing-sdk/books/cover-books.json"
GENERATOR = ROOT / "scripts/bcube_generate_illustrations.py"
STATE_ROOT = ROOT / "illustration-engine/portfolio-runs"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def targets(level: str, book: str | None) -> list[tuple[str, str]]:
    registry = load(REGISTRY)
    levels = [level] if level != "all" else ["nursery", "lkg", "ukg"]
    output: list[tuple[str, str]] = []
    for current in levels:
        books = registry["levels"][current]["books"]
        if book:
            if book not in books:
                raise ValueError(f"Unknown {current.upper()} book {book!r}")
            output.append((current, book))
        else:
            output.extend((current, slug) for slug in books)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", choices=["nursery","lkg","ukg","all"], default="all")
    parser.add_argument("--book")
    parser.add_argument("--provider", choices=["manual","command","comfyui","mock"], default="manual")
    parser.add_argument("--command")
    parser.add_argument("--workflow", type=Path)
    parser.add_argument("--comfyui-server", default="http://127.0.0.1:8188")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--require-square", action="store_true")
    args = parser.parse_args()
    if args.book and args.level == "all":
        raise ValueError("--book requires a specific --level")
    run_key = f"{args.level}-{args.book or 'portfolio'}-{args.provider}"
    state_path = STATE_ROOT / f"{run_key}.json"
    state = load(state_path) if args.resume and state_path.is_file() else {"phase":"6","provider":args.provider,"results":{}}
    failed = 0
    for level, slug in targets(args.level, args.book):
        key = f"{level}/{slug}"
        if args.resume and state["results"].get(key, {}).get("status") == "PASS":
            continue
        command = [sys.executable, str(GENERATOR), "--level", level, "--book", slug, "--provider", args.provider]
        if args.command: command.extend(["--command", args.command])
        if args.workflow: command.extend(["--workflow", str(args.workflow)])
        if args.comfyui_server: command.extend(["--comfyui-server", args.comfyui_server])
        if args.dry_run: command.append("--dry-run")
        if args.require_square: command.append("--require-square")
        result = subprocess.run(command, cwd=ROOT)
        status = "PASS" if result.returncode == 0 else "FAIL"
        state["results"][key] = {"status":status,"returncode":result.returncode}
        state["completed"] = sum(item["status"] == "PASS" for item in state["results"].values())
        state["failed"] = sum(item["status"] == "FAIL" for item in state["results"].values())
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        if result.returncode:
            failed += 1
            if not args.continue_on_error:
                break
    print(json.dumps({"status":"PASS" if failed == 0 else "PARTIAL_FAILURE","state":str(state_path),"completed":state.get("completed",0),"failed":state.get("failed",0)}, indent=2))
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError) as exc:
        print(f"BCube Phase 6 PORTFOLIO ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
