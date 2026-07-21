#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "books" / "catalog.json"
BOOKS = ROOT / "books" / "nursery"
OUTPUT = ROOT / "pipeline" / "stage1-prompt-compiler" / "output"
PAGE_RE = re.compile(r"P(\d{3})$")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", required=True)
    args = parser.parse_args()

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    matches = [b for b in catalog.get("books", []) if b.get("slug") == args.book]
    if len(matches) != 1:
        raise SystemExit(f"Unknown official book: {args.book}")
    book = matches[0]
    source_dir = BOOKS / args.book / "production-prompts"
    if not source_dir.exists():
        raise SystemExit(f"Source prompt directory is missing: {source_dir.relative_to(ROOT)}")

    book_output = OUTPUT / args.book
    compiled_dir = book_output / "compiled"
    compiled_dir.mkdir(parents=True, exist_ok=True)
    records = []
    errors = []

    for page in range(1, 45):
        stem = f"P{page:03d}"
        source = source_dir / f"{stem}.md"
        if not source.exists():
            errors.append(f"missing {source.relative_to(ROOT)}")
            continue
        source_text = source.read_text(encoding="utf-8").strip()
        prompt_id = f"{book['code']}-NURSERY-V6-{stem}"
        compiled = (
            "BCube Compiled Prompt v6.0\n"
            f"Book: {book['title']}\n"
            f"Prompt ID: {prompt_id}\n"
            f"Physical page: {page} of 44\n\n"
            f"{source_text}\n"
        )
        compiled_path = compiled_dir / f"{stem}.txt"
        compiled_path.write_text(compiled, encoding="utf-8")
        rel = str(compiled_path.relative_to(ROOT))
        records.append({
            "prompt_id": prompt_id,
            "book_slug": args.book,
            "page_number": page,
            "prompt_path": rel,
            "prompt_sha256": sha256(compiled.encode("utf-8")),
            "status": "READY",
        })

    if errors or len(records) != 44:
        raise SystemExit("Selected-book Stage 1 preparation failed: " + "; ".join(errors[:20]))

    queue = {
        "schema_version": "1.0.0",
        "compiler_version": "6.0.0",
        "book_slug": args.book,
        "expected_pages": 44,
        "records": records,
    }
    (book_output / "generation-queue.json").write_text(
        json.dumps(queue, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"decision": "PASS", "book": args.book, "ready": len(records)}, indent=2))


if __name__ == "__main__":
    main()
