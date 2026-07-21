from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = ROOT / "books" / "catalog.json"
BOOKS_ROOT = ROOT / "books" / "nursery"
PIPELINE_ROOT = ROOT / "pipeline" / "stage1-prompt-compiler"
OUTPUT_ROOT = PIPELINE_ROOT / "output"
EXPECTED_BOOKS = 10
EXPECTED_PAGES = 44

REQUIRED_PUBLISHING_BLOCK = """

## Compiled publishing requirements
Create exactly one final, flat, front-facing A4 portrait page. Use the approved BCube Future Academy branding, safe trim margins, clear visual hierarchy, age-appropriate Nursery (3+) illustration language, print-ready composition, and no watermark or mockup perspective. Preserve the exact page title, activity instruction, page number, character rules, and book-specific teaching intent from the source prompt. Produce no explanation, alternate, or additional page.
""".strip()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_catalog() -> dict:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    if catalog.get("official_book_count") != EXPECTED_BOOKS:
        raise ValueError(f"Expected {EXPECTED_BOOKS} official books")
    if catalog.get("canonical_page_count") != EXPECTED_PAGES:
        raise ValueError(f"Expected canonical page count {EXPECTED_PAGES}")
    return catalog


def validate_source_prompt(text: str, expected_id: str, page: int) -> list[str]:
    errors: list[str] = []
    if not text.strip():
        errors.append("source prompt is empty")
    if expected_id not in text:
        errors.append(f"missing canonical prompt id {expected_id}")
    if not re.search(rf"\b(?:Page|Physical page)\s*:?\s*{page}\b", text, re.IGNORECASE):
        errors.append(f"missing page reference {page}")
    return errors


def compile_book(book: dict) -> tuple[dict, list[dict]]:
    slug = book["slug"]
    code = book["code"]
    title = book["title"]
    source_dir = BOOKS_ROOT / slug / "production-prompts"
    target_dir = OUTPUT_ROOT / slug / "compiled"
    target_dir.mkdir(parents=True, exist_ok=True)

    pages: list[dict] = []
    errors: list[dict] = []
    prompt_ids: set[str] = set()

    for page in range(1, EXPECTED_PAGES + 1):
        page_name = f"P{page:03d}"
        prompt_id = f"{code}-NURSERY-V5-{page_name}"
        source_path = source_dir / f"{page_name}.md"
        if not source_path.exists():
            errors.append({"page": page, "errors": [f"missing {source_path.relative_to(ROOT)}"]})
            continue

        source = source_path.read_text(encoding="utf-8").strip()
        page_errors = validate_source_prompt(source, prompt_id, page)
        if prompt_id in prompt_ids:
            page_errors.append("duplicate prompt id")
        prompt_ids.add(prompt_id)

        compiled = (
            f"BCube Compiled Prompt v6.0\n"
            f"Book: {title}\n"
            f"Prompt ID: {prompt_id}\n"
            f"Physical page: {page} of {EXPECTED_PAGES}\n\n"
            f"{source}\n\n{REQUIRED_PUBLISHING_BLOCK}\n"
        )
        compiled_path = target_dir / f"{page_name}.txt"
        compiled_path.write_text(compiled, encoding="utf-8")
        record = {
            "page": page,
            "prompt_id": prompt_id,
            "source": str(source_path.relative_to(ROOT)),
            "compiled": str(compiled_path.relative_to(ROOT)),
            "sha256": sha256_text(compiled),
            "status": "PASS" if not page_errors else "FAIL",
        }
        pages.append(record)
        if page_errors:
            errors.append({"page": page, "prompt_id": prompt_id, "errors": page_errors})

    manifest = {
        "compiler_version": "6.0.0",
        "book_number": book["number"],
        "book_slug": slug,
        "book_title": title,
        "book_code": code,
        "expected_pages": EXPECTED_PAGES,
        "compiled_pages": len(pages),
        "passed_pages": sum(1 for p in pages if p["status"] == "PASS"),
        "failed_pages": sum(1 for p in pages if p["status"] == "FAIL") + (EXPECTED_PAGES - len(pages)),
        "pages": pages,
    }
    report = {
        "book_slug": slug,
        "expected_pages": EXPECTED_PAGES,
        "source_prompts_found": len(pages),
        "unique_prompt_ids": len(prompt_ids) == len(pages),
        "errors": errors,
        "decision": "PASS" if len(pages) == EXPECTED_PAGES and not errors else "FAIL",
    }
    book_output = OUTPUT_ROOT / slug
    (book_output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (book_output / "validation-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report, pages


def main() -> None:
    catalog = load_catalog()
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    reports: list[dict] = []
    queue: list[dict] = []
    for book in sorted(catalog["books"], key=lambda item: item["number"]):
        report, pages = compile_book(book)
        reports.append(report)
        queue.extend(
            {
                "sequence": len(queue) + 1,
                "book_number": book["number"],
                "book_slug": book["slug"],
                "prompt_id": page["prompt_id"],
                "compiled_prompt": page["compiled"],
                "sha256": page["sha256"],
                "status": "READY" if page["status"] == "PASS" else "BLOCKED",
            }
            for page in pages
        )

    overall_pass = len(reports) == EXPECTED_BOOKS and all(r["decision"] == "PASS" for r in reports)
    queue_doc = {
        "compiler_version": "6.0.0",
        "books": len(reports),
        "expected_prompts": EXPECTED_BOOKS * EXPECTED_PAGES,
        "queued_prompts": len(queue),
        "ready_prompts": sum(1 for item in queue if item["status"] == "READY"),
        "blocked_prompts": sum(1 for item in queue if item["status"] == "BLOCKED"),
        "items": queue,
    }
    (OUTPUT_ROOT / "generation-queue.json").write_text(json.dumps(queue_doc, indent=2) + "\n", encoding="utf-8")

    summary = [
        "# Stage 1 Prompt Compiler v6 Summary",
        "",
        f"- Official books compiled: {len(reports)}/{EXPECTED_BOOKS}",
        f"- Expected prompts: {EXPECTED_BOOKS * EXPECTED_PAGES}",
        f"- Compiled prompts: {len(queue)}",
        f"- Ready prompts: {queue_doc['ready_prompts']}",
        f"- Blocked prompts: {queue_doc['blocked_prompts']}",
        "",
    ]
    summary.extend(
        f"- Book {catalog['books'][index]['number']:02d} — {catalog['books'][index]['title']}: {report['source_prompts_found']}/{EXPECTED_PAGES} — {report['decision']}"
        for index, report in enumerate(reports)
    )
    summary.extend(["", f"`{'PASS' if overall_pass else 'FAIL'} — STAGE 1 PROMPT COMPILATION`", ""])
    (OUTPUT_ROOT / "stage1-summary.md").write_text("\n".join(summary), encoding="utf-8")

    if not overall_pass:
        raise SystemExit("Stage 1 prompt compilation failed")
    print(json.dumps({"decision": "PASS", **queue_doc}, indent=2))


if __name__ == "__main__":
    main()
