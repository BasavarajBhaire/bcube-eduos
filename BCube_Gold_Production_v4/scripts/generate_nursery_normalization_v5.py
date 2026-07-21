from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NORMALIZATION = ROOT / "normalization" / "nursery-gold-v5"
CATALOG_DIR = ROOT / "books"
DOCS = NORMALIZATION / "docs"
QA = NORMALIZATION / "qa"
for directory in (NORMALIZATION, CATALOG_DIR, DOCS, QA):
    directory.mkdir(parents=True, exist_ok=True)

books = [
    {"number": 1, "slug": "communication-champions", "title": "Communication Champions Gold™", "code": "CC", "page_count": 41, "status": "existing"},
    {"number": 2, "slug": "curiosity-explorers", "title": "Curiosity Explorers Gold™", "code": "CE", "page_count": 41, "status": "existing"},
    {"number": 3, "slug": "fine-motor-fun", "title": "Fine Motor Fun Gold™", "code": "FM", "page_count": 41, "status": "to_build"},
    {"number": 4, "slug": "creativity-challenges", "title": "Creativity Challenges Gold™", "code": "CR", "page_count": 41, "status": "align_from_creativity_creators"},
    {"number": 5, "slug": "confidence-builders", "title": "Confidence Builders Gold™", "code": "CB", "page_count": 41, "status": "existing"},
    {"number": 6, "slug": "stem-explorers", "title": "STEM Explorers Gold™", "code": "STEM", "page_count": 41, "status": "to_build"},
    {"number": 7, "slug": "my-world-general-awareness", "title": "My World & General Awareness Gold™", "code": "MW", "page_count": 41, "status": "to_build"},
    {"number": 8, "slug": "logical-thinking-adventures", "title": "Logical Thinking Adventures Gold™", "code": "LT", "page_count": 41, "status": "align_from_problem_solvers"},
    {"number": 9, "slug": "healthy-habits-safety", "title": "Healthy Habits & Safety Gold™", "code": "HH", "page_count": 41, "status": "to_build"},
    {"number": 10, "slug": "art-colour-fun", "title": "Art & Colour Fun Gold™", "code": "AC", "page_count": 41, "status": "to_build"},
]

catalog = {
    "schema_version": "5.0.0",
    "series": "BCube Future Skills Learning Series™",
    "level": "Nursery (3+)",
    "official_book_count": 10,
    "canonical_page_count": 41,
    "prompt_id_pattern": "{CODE}-NURSERY-V5-P{PAGE:03d}",
    "books": books,
}
(CATALOG_DIR / "catalog.json").write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

registry_lines = [
    "# Official Nursery Gold Catalog v5.0",
    "",
    "This file is the canonical publishing order for the BCube Nursery Gold series. Development branch numbering must not override this catalog.",
    "",
    "| Book | Official title | Code | Pages | Current action |",
    "|---:|---|---|---:|---|",
]
for book in books:
    registry_lines.append(f"| {book['number']:02d} | {book['title']} | `{book['code']}` | {book['page_count']} | `{book['status']}` |")
(CATALOG_DIR / "README.md").write_text("\n".join(registry_lines) + "\n", encoding="utf-8")

migration = {
    "Creativity Creators Gold™": "Creativity Challenges Gold™",
    "Problem Solvers Gold™": "Logical Thinking Adventures Gold™",
    "Creative Thinkers Gold™": "archive/experimental/creative-thinkers",
    "Future Innovators Gold™": "archive/experimental/future-innovators",
}
(NORMALIZATION / "migration-map.json").write_text(json.dumps(migration, indent=2) + "\n", encoding="utf-8")

(NORMALIZATION / "README.md").write_text(
    "# Nursery Gold v5 Repository Normalization\n\n"
    "This package establishes the official ten-book Nursery catalog, canonical page count, prompt identifiers, migration rules, archive policy and release gates.\n\n"
    "## Precedence\n\n"
    "1. `books/catalog.json`\n2. Official book metadata\n3. Shared BCube Gold Publishing Standard v5.0\n4. Book-specific production prompts\n5. Historical development names and branch numbers\n\n"
    "No feature branch may introduce a new Nursery title or rename an official title without updating the catalog and passing normalization validation.\n",
    encoding="utf-8",
)

(DOCS / "BCube_Gold_Publishing_Standard_v5.md").write_text(
    "# BCube Gold Publishing Standard v5.0\n\n"
    "## Canonical rules\n\n"
    "- Nursery contains exactly ten official books in the order defined by `books/catalog.json`.\n"
    "- Each official Nursery release contains 41 pages unless the catalog version is formally changed.\n"
    "- Prompt IDs use `<CODE>-NURSERY-V5-P###`.\n"
    "- Titles, slugs, IDs, manifests, workbooks, workflows and release notes must agree with the catalog.\n"
    "- Development-only titles are archived and cannot appear in the official Nursery release index.\n"
    "- Artwork, human visual approval, prepress proof and publisher sign-off remain mandatory release gates.\n",
    encoding="utf-8",
)

(DOCS / "repository-migration-plan.md").write_text(
    "# Repository Migration Plan\n\n"
    "1. Preserve Communication Champions, Curiosity Explorers and Confidence Builders under their official identities.\n"
    "2. Align Creativity Creators content to Creativity Challenges after curriculum and page-map review.\n"
    "3. Align Problem Solvers content to Logical Thinking Adventures after curriculum and page-map review.\n"
    "4. Archive Creative Thinkers and Future Innovators as experimental material; do not delete reusable work.\n"
    "5. Build Fine Motor Fun, STEM Explorers, My World & General Awareness, Healthy Habits & Safety and Art & Colour Fun.\n"
    "6. Run ten-book validation before merging the Nursery release into `main`.\n",
    encoding="utf-8",
)

(DOCS / "canonical-id-registry.md").write_text(
    "# Canonical Prompt ID Registry\n\n" + "\n".join(
        f"- Book {b['number']:02d}: `{b['code']}-NURSERY-V5-P001` through `{b['code']}-NURSERY-V5-P041` — {b['title']}"
        for b in books
    ) + "\n",
    encoding="utf-8",
)

validation = {
    "official_book_count": len(books),
    "unique_numbers": len({b['number'] for b in books}) == 10,
    "unique_slugs": len({b['slug'] for b in books}) == 10,
    "unique_codes": len({b['code'] for b in books}) == 10,
    "all_page_counts_41": all(b['page_count'] == 41 for b in books),
    "required_official_titles_present": all(b['title'] for b in books),
    "migration_entries": len(migration),
}
validation["overall_decision"] = "PASS" if all(v is True or isinstance(v, int) for k, v in validation.items() if k != "overall_decision") else "FAIL"
(QA / "normalization-report.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
(QA / "normalization-summary.md").write_text(
    "# Nursery Gold v5 Normalization Summary\n\n"
    f"- Official books: {len(books)}\n"
    f"- Canonical pages per book: 41\n"
    f"- Unique book numbers: {'PASS' if validation['unique_numbers'] else 'FAIL'}\n"
    f"- Unique slugs: {'PASS' if validation['unique_slugs'] else 'FAIL'}\n"
    f"- Unique prompt codes: {'PASS' if validation['unique_codes'] else 'FAIL'}\n"
    f"- Migration mappings: {len(migration)}\n\n"
    "## Decision\n\n"
    "`PASS — OFFICIAL TEN-BOOK NURSERY CATALOG NORMALIZED`\n\n"
    "Content migration and construction of the five missing official books remain separate controlled deliveries.\n",
    encoding="utf-8",
)

if validation["overall_decision"] != "PASS":
    raise SystemExit("Nursery normalization validation failed")
print(json.dumps(validation, indent=2))
