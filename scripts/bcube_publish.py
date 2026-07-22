#!/usr/bin/env python3
"""BCube Publishing Engine v5 unified orchestration CLI.

V5 consumes the existing V4/SDK assets and deterministic cover pipeline. Raw
provider images are staged as candidates and never treated as production pages.
Approved artifacts are promoted only after explicit reviewer approval and QA.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BOOKS = ROOT / "bcube-publishing-sdk/books/nursery-books.json"
COVER_PIPELINE = ROOT / "scripts/run_bcube_cover_pipeline.py"
WORK = ROOT / "production-renders/v5"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_book(level: str, slug: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if level != "nursery":
        raise ValueError("V5 currently has a deterministic compositor registered for Nursery covers only")
    registry = load_json(BOOKS)
    book = registry.get("books", {}).get(slug)
    if not isinstance(book, dict):
        available = ", ".join(sorted(registry.get("books", {})))
        raise ValueError(f"Unknown Nursery book {slug!r}. Registered books: {available}")
    return registry, book


def illustration_prompt(book: dict[str, Any]) -> str:
    title = " ".join(book["title_lines"])
    skills = ", ".join(book["skills"])
    return f"""Create only one premium preschool illustration layer for the Nursery book {title}.

Scene: a warm Indian preschool classroom with one friendly teacher and four diverse Nursery children participating in a confidence-building activity. One child proudly completes a simple achievable task while the teacher and classmates encourage the child. Show natural joy, courage, kindness, independence and participation. The illustration should visually support these skills: {skills}.

Style: premium commercial preschool workbook illustration, rounded friendly characters, expressive natural faces, clean thick outlines, bright but balanced colours, soft pastel classroom, simple large recognisable objects, uncluttered composition, suitable for children aged 3+.

Composition: illustration only, portrait-oriented scene designed to crop into a tall rounded rectangular frame. Keep important characters away from the extreme edges.

Hard exclusions: no words, no letters, no numbers, no signs, no posters with writing, no logo, no brand marks, no BCube text, no book title, no series banner, no age badge, no mascot, no star character, no ribbons, no skill capsules, no pillar icons, no footer, no border, no page number, no book-cover layout, no watermark.
"""


def validate_image(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        if image.width < 768 or image.height < 768:
            raise ValueError(f"Illustration is too small: {image.width}x{image.height}; minimum side is 768px")
        if image.width >= 2200 and image.height >= 3200:
            raise ValueError("Illustration looks like a full A4 page; supply an illustration-only candidate")


def generate_openai(prompt: str, destination: Path) -> None:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Install dependencies with: python -m pip install -r requirements.txt") from exc
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required for --provider openai")
    client = OpenAI()
    response = client.images.generate(
        model=os.getenv("BCUBE_IMAGE_MODEL", "gpt-image-1.5"), prompt=prompt,
        size="1024x1536", quality="high", output_format="png", n=1,
    )
    encoded = getattr(response.data[0], "b64_json", None)
    if not encoded:
        raise RuntimeError("Image provider returned no base64 image data")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(base64.b64decode(encoded))


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def copy_artifact(source: Path, destination: Path, *, required: bool = True) -> str | None:
    if not source.is_file():
        if required:
            raise FileNotFoundError(f"Expected pipeline artifact was not created: {source}")
        return None
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return sha256(destination)


def stage_candidate(provider: str, source: Path | None, prompt: str, staged: Path, confirm: bool) -> None:
    if provider == "reuse":
        if not staged.is_file():
            raise FileNotFoundError(f"No staged candidate exists: {staged}")
        return
    if provider == "manual":
        if source is None:
            raise ValueError("--illustration is required for --provider manual")
        if not confirm:
            raise ValueError("Manual candidates require --confirm-clean-illustration")
        validate_image(source)
        staged.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, staged)
    elif provider == "openai":
        generate_openai(prompt, staged)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    validate_image(staged)


def write_review_manifest(*, page_id: str, book: str, level: str, state: str,
                          provider: str, reviewer: str | None, paths: dict[str, Path]) -> Path:
    hashes = {name: sha256(path) for name, path in paths.items() if path.is_file()}
    manifest = {
        "engine": "BCube Publishing Engine v5",
        "page_id": page_id,
        "book": book,
        "level": level,
        "state": state,
        "provider": provider,
        "review": {
            "status": "APPROVED" if state == "PRODUCTION_PASS" else "PENDING",
            "reviewer": reviewer,
            "reviewed_on": str(date.today()) if reviewer else None,
        },
        "artifacts": {name: {"path": str(path.relative_to(ROOT)), "sha256": hashes.get(name)}
                      for name, path in paths.items() if path.is_file()},
    }
    target = WORK / "manifests" / f"{page_id}.review.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="BCube Publishing Engine v5")
    parser.add_argument("--level", choices=["nursery", "lkg", "ukg"], required=True)
    parser.add_argument("--book", required=True)
    parser.add_argument("--page", default="cover", choices=["cover", "about", "publisher", "contents", "back-cover"])
    parser.add_argument("--provider", choices=["manual", "openai", "reuse"], default=os.getenv("BCUBE_IMAGE_PROVIDER", "manual"))
    parser.add_argument("--illustration", type=Path)
    parser.add_argument("--confirm-clean-illustration", action="store_true")
    parser.add_argument("--approve", action="store_true")
    parser.add_argument("--reviewer")
    parser.add_argument("--prompt-only", action="store_true")
    args = parser.parse_args()

    if args.page != "cover":
        raise ValueError(f"No deterministic {args.page} compositor is registered yet; V5 fails closed")
    _, book = resolve_book(args.level, args.book)
    page_id = book["page_id"]
    prompt = illustration_prompt(book)

    prompt_path = WORK / "prompts" / f"{page_id}.illustration.txt"
    candidate_illustration = WORK / "candidates/illustrations" / f"{page_id}.png"
    candidate_page = WORK / "candidates/pages" / f"{page_id}.png"
    approved_illustration = WORK / "approved/illustrations" / f"{page_id}.png"
    approved_page = WORK / "approved/pages" / f"{page_id}.png"
    evidence_copy = WORK / "evidence" / f"{page_id}.json"
    page_data_copy = WORK / "manifests" / f"{page_id}.page-data.json"
    report_copy = WORK / "reports" / f"{page_id}.render-report.json"

    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt, encoding="utf-8")
    if args.prompt_only:
        print(prompt)
        print(f"Saved: {prompt_path}")
        return 0

    source = args.illustration.expanduser().resolve() if args.illustration else None
    stage_candidate(args.provider, source, prompt, candidate_illustration, args.confirm_clean_illustration)

    command = [sys.executable, str(COVER_PIPELINE), "--book", args.book,
               "--illustration", str(candidate_illustration), "--confirm-clean-illustration"]
    if args.approve:
        if not args.reviewer:
            raise ValueError("--reviewer is required with --approve")
        command += ["--approve", "--reviewer", args.reviewer]
    run(command)

    legacy_page = ROOT / "production-renders/pages" / f"{page_id}.png"
    legacy_evidence = ROOT / "production-renders/qa-manifests" / f"{page_id}.json"
    legacy_page_data = ROOT / "production-renders/page-data" / f"{page_id}.json"
    legacy_report = ROOT / "validation/rendered-pages" / f"{page_id}.render-report.json"

    copy_artifact(legacy_page, candidate_page)
    copy_artifact(legacy_evidence, evidence_copy)
    copy_artifact(legacy_page_data, page_data_copy)

    state = "REVIEW_CANDIDATE"
    active_page = candidate_page
    if args.approve:
        copy_artifact(candidate_illustration, approved_illustration)
        copy_artifact(candidate_page, approved_page)
        copy_artifact(legacy_report, report_copy)
        state = "PRODUCTION_PASS"
        active_page = approved_page

    manifest = write_review_manifest(
        page_id=page_id, book=args.book, level=args.level, state=state,
        provider=args.provider, reviewer=args.reviewer,
        paths={"prompt": prompt_path, "candidate_illustration": candidate_illustration,
               "candidate_page": candidate_page, "approved_illustration": approved_illustration,
               "approved_page": approved_page, "composition_evidence": evidence_copy,
               "page_data": page_data_copy, "qa_report": report_copy},
    )
    print(json.dumps({
        "engine": "BCube Publishing Engine v5", "state": state,
        "page": str(active_page), "review_manifest": str(manifest),
        "qa_report": str(report_copy) if args.approve else None,
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"BCube V5 FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
