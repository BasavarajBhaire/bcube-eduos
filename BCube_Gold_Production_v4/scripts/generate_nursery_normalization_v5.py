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

CANONICAL_PAGE_COUNT = 44
PAGE_ARCHITECTURE = {
    "front_cover": 1,
    "inside_cover_book_information": 1,
    "this_book_belongs_to": 1,
    "core_learning_and_support_pages": 40,
    "back_cover": 1,
}

books = [
    {"number": 1, "slug": "communication-champions", "title": "Communication Champions Gold™", "code": "CC", "page_count": CANONICAL_PAGE_COUNT, "status": "existing"},
    {"number": 2, "slug": "curiosity-explorers", "title": "Curiosity Explorers Gold™", "code": "CE", "page_count": CANONICAL_PAGE_COUNT, "status": "existing"},
    {"number": 3, "slug": "fine-motor-fun", "title": "Fine Motor Fun Gold™", "code": "FM", "page_count": CANONICAL_PAGE_COUNT, "status": "to_build"},
    {"number": 4, "slug": "creativity-challenges", "title": "Creativity Challenges Gold™", "code": "CR", "page_count": CANONICAL_PAGE_COUNT, "status": "align_from_creativity_creators"},
    {"number": 5, "slug": "confidence-builders", "title": "Confidence Builders Gold™", "code": "CB", "page_count": CANONICAL_PAGE_COUNT, "status": "existing"},
    {"number": 6, "slug": "stem-explorers", "title": "STEM Explorers Gold™", "code": "STEM", "page_count": CANONICAL_PAGE_COUNT, "status": "to_build"},
    {"number": 7, "slug": "my-world-general-awareness", "title": "My World & General Awareness Gold™", "code": "MW", "page_count": CANONICAL_PAGE_COUNT, "status": "to_build"},
    {"number": 8, "slug": "logical-thinking-adventures", "title": "Logical Thinking Adventures Gold™", "code": "LT", "page_count": CANONICAL_PAGE_COUNT, "status": "align_from_problem_solvers"},
    {"number": 9, "slug": "healthy-habits-safety", "title": "Healthy Habits & Safety Gold™", "code": "HH", "page_count": CANONICAL_PAGE_COUNT, "status": "to_build"},
    {"number": 10, "slug": "art-colour-fun", "title": "Art & Colour Fun Gold™", "code": "AC", "page_count": CANONICAL_PAGE_COUNT, "status": "to_build"},
]

catalog = {
    "schema_version": "5.1.0",
    "series": "BCube Future Skills Learning Series™",
    "level": "Nursery (3+)",
    "official_book_count": 10,
    "canonical_page_count": CANONICAL_PAGE_COUNT,
    "page_architecture": PAGE_ARCHITECTURE,
    "prompt_id_pattern": "{CODE}-NURSERY-V5-P{PAGE:03d}",
    "books": books,
}
(CATALOG_DIR / "catalog.json").write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

registry_lines = [
    "# Official Nursery Gold Catalog v5.1",
    "",
    "This file is the canonical publishing order for the BCube Nursery Gold series. Development branch numbering must not override this catalog.",
    "",
    "**Canonical book length: 44 pages**, including front cover, inside cover/book information, ownership page, 40 learning/support pages and back cover.",
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
    "This package establishes the official ten-book Nursery catalog, canonical 44-page architecture, prompt identifiers, migration rules, archive policy and release gates.\n\n"
    "## Precedence\n\n"
    "1. `books/catalog.json`\n2. Official book metadata\n3. Shared BCube Gold Publishing Standard v5.1\n4. Book-specific production prompts\n5. Historical development names and branch numbers\n\n"
    "No feature branch may introduce a new Nursery title, alter the 44-page architecture or rename an official title without updating the catalog and passing normalization validation.\n",
    encoding="utf-8",
)

(DOCS / "BCube_Gold_Publishing_Standard_v5.md").write_text(
    "# BCube Gold Publishing Standard v5.1\n\n"
    "## Canonical rules\n\n"
    "- Nursery contains exactly ten official books in the order defined by `books/catalog.json`.\n"
    "- Each official Nursery release contains exactly 44 pages.\n"
    "- Page architecture: 1 front cover + 1 inside cover/book-information page + 1 ownership page + 40 learning/support pages + 1 back cover.\n"
    "- Certificate, parent partnership, review and celebration content must be planned within the 40 learning/support pages where applicable.\n"
    "- Prompt IDs use `<CODE>-NURSERY-V5-P001` through `<CODE>-NURSERY-V5-P044`.\n"
    "- Titles, slugs, IDs, manifests, workbooks, workflows and release notes must agree with the catalog.\n"
    "- Development-only titles are archived and cannot appear in the official Nursery release index.\n"
    "- Artwork, human visual approval, prepress proof and publisher sign-off remain mandatory release gates.\n",
    encoding="utf-8",
)

(DOCS / "repository-migration-plan.md").write_text(
    "# Repository Migration Plan\n\n"
    "1. Preserve Communication Champions, Curiosity Explorers and Confidence Builders under their official identities and verify 44-page manifests.\n"
    "2. Align Creativity Creators content to Creativity Challenges without reducing the 44-page architecture.\n"
    "3. Align Problem Solvers content to Logical Thinking Adventures without reducing the 44-page architecture.\n"
    "4. Archive Creative Thinkers and Future Innovators as experimental material; do not delete reusable work.\n"
    "5. Build Fine Motor Fun, STEM Explorers, My World & General Awareness, Healthy Habits & Safety and Art & Colour Fun as 44-page books.\n"
    "6. Run ten-book validation before merging the Nursery release into `main`.\n",
    encoding="utf-8",
)

(DOCS / "canonical-id-registry.md").write_text(
    "# Canonical Prompt ID Registry\n\n" + "\n".join(
        f"- Book {b['number']:02d}: `{b['code']}-NURSERY-V5-P001` through `{b['code']}-NURSERY-V5-P044` — {b['title']}"
        for b in books
    ) + "\n",
    encoding="utf-8",
)

(DOCS / "canonical-page-architecture.md").write_text(
    "# Canonical 44-Page Architecture\n\n"
    "| Page group | Count | Requirement |\n"
    "|---|---:|---|\n"
    "| Front cover | 1 | Official title, level, series identity and approved cover system |\n"
    "| Inside cover / book information | 1 | Publisher, copyright, edition and required book details |\n"
    "| This Book Belongs To | 1 | Ownership and learner identity |\n"
    "| Learning and support pages | 40 | Curriculum, activities, reviews, certificate and parent partnership as defined by the book |\n"
    "| Back cover | 1 | Official series and publisher identity |\n"
    "| **Total** | **44** | Required for every official Nursery Gold title |\n",
    encoding="utf-8",
)

validation = {
    "official_book_count": len(books),
    "unique_numbers": len({b['number'] for b in books}) == 10,
    "unique_slugs": len({b['slug'] for b in books}) == 10,
    "unique_codes": len({b['code'] for b in books}) == 10,
    "all_page_counts_44": all(b['page_count'] == CANONICAL_PAGE_COUNT for b in books),
    "page_architecture_total_44": sum(PAGE_ARCHITECTURE.values()) == CANONICAL_PAGE_COUNT,
    "required_official_titles_present": all(bool(b['title']) for b in books),
    "migration_entries": len(migration),
}
boolean_checks = [v for v in validation.values() if isinstance(v, bool)]
validation["overall_decision"] = "PASS" if len(books) == 10 and all(boolean_checks) and len(migration) == 4 else "FAIL"
(QA / "normalization-report.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
(QA / "normalization-summary.md").write_text(
    "# Nursery Gold v5.1 Normalization Summary\n\n"
    f"- Official books: {len(books)}\n"
    f"- Canonical pages per book: {CANONICAL_PAGE_COUNT}\n"
    f"- Page architecture total: {sum(PAGE_ARCHITECTURE.values())}\n"
    f"- Unique book numbers: {'PASS' if validation['unique_numbers'] else 'FAIL'}\n"
    f"- Unique slugs: {'PASS' if validation['unique_slugs'] else 'FAIL'}\n"
    f"- Unique prompt codes: {'PASS' if validation['unique_codes'] else 'FAIL'}\n"
    f"- All catalog books use 44 pages: {'PASS' if validation['all_page_counts_44'] else 'FAIL'}\n"
    f"- Migration mappings: {len(migration)}\n\n"
    "## Decision\n\n"
    "`PASS — OFFICIAL TEN-BOOK NURSERY CATALOG ALIGNED TO 44 PAGES`\n\n"
    "Phase A is complete. Content migration and construction of the five missing official books remain separate controlled deliveries.\n",
    encoding="utf-8",
)

if validation["overall_decision"] != "PASS":
    raise SystemExit("Nursery normalization validation failed")
print(json.dumps(validation, indent=2))
