#!/usr/bin/env python3
"""Bulk render BCube pages from downloaded illustration source sheets.

The command is fail-closed, but for Early Maths Adventures it can rebuild the
committed test runtime contract automatically before scanning illustrations.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PAGE_ID_SEARCH = re.compile(r"(?P<page_id>[A-Z]{2}-[A-Z]+-V\d+-P\d{3})", re.IGNORECASE)
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
EARLY_MATHS_DEDICATED_PAGES = set(range(8, 45))


class ContractError(RuntimeError):
    pass


@dataclass
class RenderResult:
    page_id: str
    status: str
    reason: str = ""
    illustration: str = ""
    output: str = ""
    evidence: str = ""
    mechanic: str = ""


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ContractError(f"JSON object expected: {path}")
    return value


def find_contract(runtime_root: Path, level: str, book: str) -> Path:
    manifest = load_json(runtime_root / "manifest.json")
    relative = manifest.get("levels", {}).get(level.lower(), {}).get("books", {}).get(book)
    if not relative:
        raise ContractError(f"No manifest entry for {level}/{book}")
    path = runtime_root / relative
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def build_test_contract_if_supported(repo_root: Path, level: str, book: str) -> None:
    if level.lower() == "lkg" and book == "early-maths-adventures":
        builder = repo_root / "scripts" / "build_early_maths_test_runtime_contract.py"
        if not builder.is_file():
            raise FileNotFoundError(builder)
        subprocess.run([sys.executable, str(builder)], cwd=repo_root, check=True)


def scan_illustrations(directory: Path) -> tuple[dict[str, Path], dict[str, list[str]]]:
    matches: dict[str, Path] = {}
    duplicates: dict[str, list[str]] = {}
    for path in sorted(directory.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTS:
            continue
        match = PAGE_ID_SEARCH.search(path.stem)
        if not match:
            continue
        page_id = match.group("page_id").upper()
        if page_id in matches:
            duplicates.setdefault(page_id, [str(matches[page_id])]).append(str(path))
            continue
        matches[page_id] = path
    return matches, duplicates


def validate_page(page_id: str, page: dict[str, Any]) -> None:
    validation = page.get("validation", {})
    if validation.get("status") != "READY":
        raise ContractError(f"{page_id}: status is not READY")
    if validation.get("allow_fallback") is not False:
        raise ContractError(f"{page_id}: allow_fallback must be false")
    if validation.get("illustration_contract_aligned") is False:
        raise ContractError(f"{page_id}: illustration contract is not aligned")
    illustration = page.get("illustration", {})
    assets = illustration.get("assets")
    crops = illustration.get("asset_crops")
    if not isinstance(assets, list) or not assets:
        raise ContractError(f"{page_id}: illustration.assets is empty")
    if not isinstance(crops, dict) or set(assets) != set(crops):
        raise ContractError(f"{page_id}: assets and named crops do not match")
    activity = page.get("activity", {})
    if not activity.get("mechanic") or not activity.get("render_kind"):
        raise ContractError(f"{page_id}: mechanic/render_kind missing")
    layout = page.get("layout", {})
    for key in ("parent_panel", "home_connection", "generic_response_panel"):
        if layout.get(key) is not False:
            raise ContractError(f"{page_id}: layout.{key} must be false")


def page_number(page_id: str) -> int:
    match = re.search(r"-P(\d{3})$", page_id)
    if not match:
        raise ContractError(f"Invalid page ID: {page_id}")
    return int(match.group(1))


def renderer_command(repo_root: Path, page_id: str, level: str, book: str, illustration: Path, logo: Path, output: Path, evidence: Path) -> list[str]:
    dedicated = level.lower() == "lkg" and book == "early-maths-adventures" and page_number(page_id) in EARLY_MATHS_DEDICATED_PAGES
    composer = "compose_early_maths_refined_pages.py" if dedicated else "compose_runtime_learning_page.py"
    return [
        sys.executable,
        str(repo_root / "bcube-publishing-sdk" / "composer" / composer),
        "--level", level,
        "--book", book,
        "--page-id", page_id,
        "--illustration", str(illustration),
        "--logo", str(logo),
        "--output", str(output),
        "--evidence-output", str(evidence),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Render an entire BCube book from illustration source sheets")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--runtime-root", type=Path)
    parser.add_argument("--level", required=True)
    parser.add_argument("--book", required=True)
    parser.add_argument("--illustrations-dir", type=Path, required=True)
    parser.add_argument("--logo", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--page-id")
    parser.add_argument("--skip-contract-build", action="store_true")
    parser.add_argument("--fail-fast", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    runtime_root = (args.runtime_root or repo_root / "runtime-contracts").resolve()
    illustrations_dir = args.illustrations_dir.resolve()
    logo = args.logo.resolve()
    output_dir = args.output_dir.resolve()
    evidence_dir = args.evidence_dir.resolve()

    if not illustrations_dir.is_dir():
        raise SystemExit(f"Illustrations directory not found: {illustrations_dir}")
    if not logo.is_file():
        raise SystemExit(f"Logo not found: {logo}")
    if not args.skip_contract_build:
        build_test_contract_if_supported(repo_root, args.level, args.book)

    contract_path = find_contract(runtime_root, args.level, args.book)
    contract = load_json(contract_path)
    pages = contract.get("pages", {})
    illustration_map, duplicates = scan_illustrations(illustrations_dir)
    if args.page_id:
        requested = args.page_id.upper()
        illustration_map = {k: v for k, v in illustration_map.items() if k == requested}

    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    results: list[RenderResult] = []
    unexpected: list[str] = []

    for page_id, illustration in sorted(illustration_map.items()):
        page = pages.get(page_id)
        if not isinstance(page, dict):
            unexpected.append(page_id)
            continue
        mechanic = str(page.get("activity", {}).get("mechanic", ""))
        output = output_dir / f"{page_id}.png"
        evidence = evidence_dir / f"{page_id}.json"
        try:
            validate_page(page_id, page)
            expected = str(page.get("illustration", {}).get("source_asset", ""))
            if expected and Path(expected).stem.upper() != page_id:
                raise ContractError(f"{page_id}: expected source asset {expected}")
            process = subprocess.run(
                renderer_command(repo_root, page_id, args.level.lower(), args.book, illustration, logo, output, evidence),
                cwd=repo_root,
                capture_output=True,
                text=True,
            )
            if process.returncode != 0:
                raise RuntimeError((process.stderr or process.stdout or "Renderer failed").strip())
            results.append(RenderResult(page_id, "GENERATED", illustration=str(illustration), output=str(output), evidence=str(evidence), mechanic=mechanic))
        except Exception as exc:
            results.append(RenderResult(page_id, "FAILED", str(exc), str(illustration), str(output), str(evidence), mechanic))
            if args.fail_fast:
                break

    required = set(pages)
    if args.page_id:
        required &= {args.page_id.upper()}
    missing = sorted(required - set(illustration_map))
    generated = [r for r in results if r.status == "GENERATED"]
    failed = [r for r in results if r.status == "FAILED"]
    summary = {
        "book_contract": str(contract_path),
        "contract_pages": len(pages),
        "illustrations_scanned": len(illustration_map),
        "generated": len(generated),
        "failed": len(failed),
        "missing_from_contract": unexpected,
        "missing_illustrations": missing,
        "duplicate_illustrations": duplicates,
        "results": [asdict(item) for item in results],
        "policy": "Fail-closed. No generic fallback is permitted.",
    }
    summary_path = evidence_dir / "book-render-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("book_contract", "contract_pages", "illustrations_scanned", "generated", "failed", "missing_from_contract", "missing_illustrations", "duplicate_illustrations", "policy")}, indent=2))
    print(f"Summary: {summary_path}")
    return 0 if not failed and not unexpected and not duplicates else 2


if __name__ == "__main__":
    raise SystemExit(main())
