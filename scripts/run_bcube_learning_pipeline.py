#!/usr/bin/env python3
"""Run the BCube Learning Page Contract V2 pipeline from finalized V4 source data."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "bcube-publishing-sdk/books/cover-books.json"
NORMALIZER = ROOT / "bcube-publishing-sdk/normalizers/build_learning_contract_v2.py"
REFINER = ROOT / "bcube-publishing-sdk/normalizers/refine_learning_contract_v2.py"
FINALISER = ROOT / "bcube-publishing-sdk/normalizers/finalise_learning_contract_v2.py"
VALIDATOR = ROOT / "bcube-publishing-sdk/validators/validate_learning_contract_v2.py"
COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_learning_page_character_v2.py"
OVERRIDES = ROOT / "bcube-publishing-sdk/books/learning-page-overrides-v1.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def resolve_book(level: str, slug: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    registry = load(REGISTRY)
    level_data = registry.get("levels", {}).get(level)
    if not isinstance(level_data, dict):
        raise ValueError(f"Unknown level {level!r}")
    book = level_data.get("books", {}).get(slug)
    if not isinstance(book, dict):
        available = ", ".join(sorted(level_data.get("books", {})))
        raise ValueError(f"Unknown {level.upper()} book {slug!r}. Registered books: {available}")
    return registry, level_data, book


def valid_image(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        with Image.open(path) as image:
            image.verify()
        return True
    except Exception:
        return False


def find_asset(candidates: list[str], label: str) -> Path:
    for candidate in candidates:
        path = ROOT / candidate
        if valid_image(path):
            return path
    raise FileNotFoundError(f"No valid {label} asset found")


def repo_relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def safe_source(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if ROOT.resolve() not in resolved.parents or not resolved.is_file():
        raise ValueError(f"Learning source must be a tracked repository file: {path}")
    return resolved


def stage_illustration(source: Path, page_id: str) -> Path:
    source = source.expanduser().resolve()
    if not valid_image(source):
        raise FileNotFoundError(f"Illustration is missing or unreadable: {source}")
    destination = ROOT / "production-renders/activity/illustrations" / f"{page_id}.png"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        image.convert("RGB").save(destination, "PNG", dpi=(300, 300))
    return destination


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def deep_merge(target: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    for key, value in update.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            deep_merge(target[key], value)
        else:
            target[key] = value
    return target


def apply_curated_override(contract: dict[str, Any]) -> bool:
    registry = load(OVERRIDES)
    pages = registry.get("pages")
    if not isinstance(pages, dict):
        raise ValueError("Learning-page override registry contains no pages object")
    page_id = contract["identity"]["page_id"]
    override = pages.get(page_id)
    if not isinstance(override, dict):
        return False
    deep_merge(contract, override)
    contract["qa_requirements"]["component_count"] = len(contract["deterministic_components"])
    contract["source_lineage"]["curated_override_registry"] = repo_relative(OVERRIDES)
    contract["source_lineage"]["curated_override_version"] = registry.get("version")
    return True


def normalise_star_policy(contract: dict[str, Any], official_star: Path) -> None:
    """Use Star only when the page-owned contract explicitly requires the official asset."""
    illustration = contract["illustration"]
    curated = bool(contract.get("source_lineage", {}).get("curated_override_applied"))
    policy = illustration.get("star_policy")
    if curated and policy == "official-asset-separate":
        contract["assets"]["official_star_path"] = repo_relative(official_star)
        return
    if curated and policy == "prohibited":
        contract["assets"].pop("official_star_path", None)
        return
    learning = contract["learning"]
    text = " ".join(
        str(value or "")
        for value in (
            illustration.get("scene"),
            illustration.get("focal_point"),
            learning.get("student_instruction"),
            learning.get("model_text"),
        )
    ).casefold()
    if "star" in text:
        illustration["star_policy"] = "official-asset-separate"
        contract["assets"]["official_star_path"] = repo_relative(official_star)
    else:
        illustration["star_policy"] = "prohibited"
        contract["assets"].pop("official_star_path", None)


def verify_identity(
    contract: dict[str, Any],
    *,
    expected_page_id: str,
    physical_page: int,
    page_number: int,
    level: str,
    slug: str,
) -> None:
    identity = contract["identity"]
    expected = {
        "page_id": expected_page_id,
        "physical_page": physical_page,
        "page_number": page_number,
        "book_slug": slug,
    }
    mismatches = {
        key: {"expected": value, "actual": identity.get(key)}
        for key, value in expected.items()
        if identity.get(key) != value
    }
    if mismatches:
        raise ValueError(f"Learning contract identity mismatch: {mismatches}")
    if not identity.get("page_number_visible"):
        raise ValueError("Learning pages must have a visible printed page number")
    if level not in {"nursery", "lkg", "ukg"}:
        raise ValueError(f"Unknown learning level: {level}")


def run_content_pass(script: Path, contract_path: Path, override_applied: bool) -> None:
    command = [
        sys.executable,
        str(script),
        "--contract",
        str(contract_path),
        "--output",
        str(contract_path),
    ]
    if override_applied:
        command.append("--curated-override-applied")
    run(command)


def build_contract(args: argparse.Namespace) -> tuple[Path, Path, Path, Path]:
    registry, level_data, book = resolve_book(args.level, args.book)
    source = safe_source(args.source_page_json)
    source_data = load(source)
    source_page_id = str(source_data.get("prompt_id") or "")
    expected_page_id = args.page_id or f"{book['prefix']}-{level_data['id_level']}-V4-P{args.physical_page:03d}"
    if source_page_id != expected_page_id:
        raise ValueError(
            f"Selected source page {source_page_id!r} does not match expected page {expected_page_id!r}"
        )
    illustration = stage_illustration(args.illustration, expected_page_id)
    logo = find_asset(list(registry["shared"]["official_logo_candidates"]), "official BCube logo")
    star = find_asset(list(registry["shared"]["official_star_candidates"]), "official BCube Star")
    contract_path = ROOT / "production-renders/activity/page-data" / f"{expected_page_id}.json"
    output = ROOT / "production-renders/activity/pages" / f"{expected_page_id}.png"
    evidence = ROOT / "production-renders/activity/evidence" / f"{expected_page_id}.json"
    report = ROOT / "validation/rendered-pages" / f"{expected_page_id}.activity-input.json"
    for path in (contract_path, output, evidence, report):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.unlink(missing_ok=True)
    run(
        [
            sys.executable,
            str(NORMALIZER),
            "--source-page-json",
            str(source),
            "--illustration-path",
            repo_relative(illustration),
            "--official-logo-path",
            repo_relative(logo),
            "--book-title-lines-json",
            json.dumps(book["title_lines"], ensure_ascii=False),
            "--level",
            level_data["display_level"],
            "--age",
            level_data["age"],
            "--output",
            str(contract_path),
        ]
    )
    contract = load(contract_path)
    override_applied = apply_curated_override(contract)
    contract["source_lineage"]["html_registry_source"] = repo_relative(source)
    contract["source_lineage"]["curated_override_applied"] = override_applied
    contract_path.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    run_content_pass(REFINER, contract_path, override_applied)
    run_content_pass(FINALISER, contract_path, override_applied)
    contract = load(contract_path)
    normalise_star_policy(contract, star)
    verify_identity(
        contract,
        expected_page_id=expected_page_id,
        physical_page=args.physical_page,
        page_number=args.page_number,
        level=args.level,
        slug=args.book,
    )
    contract_path.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return contract_path, output, evidence, report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BCube Learning Page Contract V2 pipeline")
    parser.add_argument("--level", choices=["nursery", "lkg", "ukg"], required=True)
    parser.add_argument("--book", required=True)
    parser.add_argument("--illustration", type=Path, required=True)
    parser.add_argument("--source-page-json", type=Path, required=True)
    parser.add_argument("--physical-page", type=int, required=True)
    parser.add_argument("--page-number", type=int, required=True)
    parser.add_argument("--page-id")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    contract, output, evidence, report = build_contract(args)
    run([sys.executable, str(VALIDATOR), "--contract", str(contract), "--output", str(report)])
    run(
        [
            sys.executable,
            str(COMPOSER),
            "--contract",
            str(contract),
            "--output",
            str(output),
            "--evidence-output",
            str(evidence),
        ]
    )
    print(
        json.dumps(
            {
                "engine": "BCube Publishing Engine Learning Pages V2",
                "state": "REVIEW_CANDIDATE",
                "learning_contract": str(contract),
                "page": str(output),
                "input_qa": str(report),
                "composition_evidence": str(evidence),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"BCube Learning Page V2 FAIL: {exc}", file=sys.stderr)
        raise SystemExit(2)
