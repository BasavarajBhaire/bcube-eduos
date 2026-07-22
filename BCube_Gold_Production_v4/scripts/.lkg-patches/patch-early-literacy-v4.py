#!/usr/bin/env python3
"""Patch the LKG V4 compiler for cumulative portfolio tracking and the audited Early Literacy closing-page correction."""
from __future__ import annotations

from pathlib import Path

COMPILER = Path("BCube_Gold_Production_v4/scripts/build-lkg-v4-prompts.py")


def patch_source_correction(text: str) -> str:
    marker = 'slug == "early-literacy-adventures" and source.get("prompt_id") == "EL-LKG-V3-P041"'
    if marker in text:
        return text
    needle = '''            fields = source_fields(source)
            if physical == 1:
'''
    replacement = '''            fields = source_fields(source)
            if slug == "early-literacy-adventures" and source.get("prompt_id") == "EL-LKG-V3-P041":
                fields.update({
                    "title": "My Literacy Celebration",
                    "page_type": "reflection",
                    "objective": "Reflect on and celebrate literacy learning.",
                    "scene": "Teacher-led literacy celebration with six expressive LKG children and approved Star; each child shares one short literacy reflection.",
                    "focal": "Children confidently sharing one reading or literacy achievement with their teacher and classmates.",
                })
                fields["overrides"] = list(fields.get("overrides", [])) + [
                    "V4 editorial correction: source metadata title 'Back Cover' conflicts with its teacher-led classroom reflection activity. Render this source-backed page as 'My Literacy Celebration' on printed page 42; preserve its activity, evidence, facilitation, parent connection, illustration intent, and source lineage."
                ]
                fields["approved_source_instruction"] += (
                    "\\n\\nV4 EDITORIAL CORRECTION: The canonical source title 'Back Cover' conflicts with the approved classroom celebration and reflection content. "
                    "Use the exact visible title 'My Literacy Celebration' on printed page 42. Preserve the source activity, expected evidence, teacher reflection question, parent connection, six-child classroom scene, and all negative constraints."
                )
            if physical == 1:
'''
    if needle not in text:
        raise RuntimeError("Source correction insertion point not found")
    return text.replace(needle, replacement, 1)


def patch_cumulative_tracking(text: str) -> str:
    marker = '"books_validated": len(results)'
    if marker in text:
        return text
    start = text.index("def write_agenda(")
    end = text.index("\ndef main()", start)
    function = """def write_agenda(completed_slug: str, result: dict) -> None:
    completed = [
        slug for slug in ORDER
        if (PROMPTS / slug / "lkg" / "v4" / "release-manifest.json").is_file()
    ]
    results = [validate_book(slug) for slug in completed]
    rows = []
    for index, slug in enumerate(ORDER, start=1):
        profile = BOOKS[slug]
        status = "COMPLETE — V4 prompts" if slug in completed else "QUEUED"
        rows.append(f"| {index} | {profile['book']} | {profile['prefix']} | {status} |")

    overall_status = "PASS" if results and all(item["status"] == "PASS" for item in results) else "FAIL"
    next_book = next((slug for slug in ORDER if slug not in completed), None)
    totals = {
        key: sum(item[key] for item in results)
        for key in ("page_prompts", "markdown_files", "json_files", "source_backed_pages", "checks", "critical_defects")
    }
    agenda = f'''# BCube LKG V4 Production Agenda

Status date: 22 July 2026

## Delivery rule

Every completed LKG book follows this closed workflow:

1. read the canonical 41-page V3 source set;
2. migrate to the approved 44-physical-page V4 structure;
3. preserve page-specific content and exact execution blueprints;
4. validate Markdown, JSON, numbering, source lineage, and required locks;
5. commit the complete book on a dedicated branch;
6. push and open a pull request;
7. merge to `main` before starting the next book.

No completed book may remain only in chat, only locally, or on an unmerged branch.

## Lessons carried forward from Nursery

- Never use a generic prompt when an individual source instruction exists.
- Never lose page-specific model phrases, activities, expected responses, response spaces, illustration requirements, or prohibited extras.
- Never generate or redraw the approved logo or Star.
- Never combine pages into contact sheets, collages, or multi-page outputs.
- Never leave completed work on a diverged branch.
- Keep one exact identity across source, prompt ID, title, numbering, manifest, and output filename.
- Treat About This Book, split Contents, and Back Cover as controlled portfolio additions, not curriculum rewrites.
- Correct contradictory source metadata transparently while preserving source lineage and educational intent.

## Official LKG sequence

| No. | Book | Prefix | Status |
| ---: | --- | --- | --- |
{chr(10).join(rows)}

## Locked LKG structure

- 41 canonical V3 source pages.
- 44 physical V4 pages.
- P001 cover: uncounted and unnumbered.
- P002 About This Book: logical page 1; printed number hidden.
- P003 Copyright: logical page 2; printed number hidden.
- P004–P005 Contents Parts 1–2: logical pages 3–4; printed numbers hidden.
- P006–P043: printed pages 5–42.
- P044 back cover: uncounted and unnumbered.
- A4 portrait, 300 DPI, 3 mm bleed, minimum 10 mm safe margin, 12 mm binding margin.
- Approximately 60–70% visual and 30–40% text/activity.
- LKG (4+) badge on cover only.
- Maximum two core activities and one optional extension.
- British English and one approved Star identity.
'''
    (V4_ROOT / "LKG_PRODUCTION_AGENDA.md").write_text(agenda, encoding="utf-8")

    qa = {
        "validation_version": "4.0.0",
        "level": LEVEL,
        "books_validated": len(results),
        "books_total": len(ORDER),
        "completed_books": completed,
        **totals,
        "status": overall_status,
        "next_book": next_book,
        "book_results": results,
    }
    qa_path = V4_ROOT / "qa" / "lkg-v4-prompts-validation.json"
    qa_path.parent.mkdir(parents=True, exist_ok=True)
    qa_path.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")

    portfolio = {
        "manifest_version": "4.0.0",
        "series": SERIES,
        "level": LEVEL,
        "status": overall_status,
        "books_total": len(ORDER),
        "books_completed": len(completed),
        "completed": [
            {"slug": slug, "book": BOOKS[slug]["book"], "prompts": 44}
            for slug in completed
        ],
        "queue": [slug for slug in ORDER if slug not in completed],
        "totals": totals,
        "validation_report": str(qa_path.relative_to(ROOT)),
    }
    portfolio_path = PROMPTS / "lkg" / "V4_PORTFOLIO_MANIFEST.json"
    portfolio_path.parent.mkdir(parents=True, exist_ok=True)
    portfolio_path.write_text(json.dumps(portfolio, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
"""
    return text[:start] + function + text[end:]


def main() -> None:
    text = COMPILER.read_text(encoding="utf-8")
    text = patch_source_correction(text)
    text = patch_cumulative_tracking(text)
    COMPILER.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
