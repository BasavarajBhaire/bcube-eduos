from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "books" / "nursery" / "problem-solvers"
PHASE5 = BOOK / "phase5"
PHASE6 = BOOK / "phase6"
QA = BOOK / "qa"

for directory in (PHASE5, PHASE6, QA):
    directory.mkdir(parents=True, exist_ok=True)

phase5_files = {
    "README.md": """# Phase 5 — Artwork Production Framework

This phase controls generation, review, approval and release of the 44 Problem Solvers Gold page artworks.

## Status
Framework complete. Artwork production is tracked page by page.

## Required outcome
Every page must pass educational, problem-solving clarity, visual, brand, typography, accessibility and print-readiness review before release.
""",
    "artwork-pipeline.md": """# Artwork Pipeline

1. Load the approved production prompt and locked assets.
2. Generate one flat A4 portrait page.
3. Verify title, page number, logo, instruction and visual hierarchy.
4. Confirm the Observe–Think–Try–Solve activity is unambiguous.
5. Review Nursery suitability, accessibility and illustration consistency.
6. Record the decision in `page-review-status.csv`.
7. Approve only when every required gate passes.

No placeholder or unreviewed image may enter the release package.
""",
    "illustration-generation-guidelines.md": """# Illustration Generation Guidelines

- A4 portrait, print-oriented composition and generous safe margins.
- Premium preschool illustration style with rounded forms and clean outlines.
- One dominant problem-solving focus per page.
- Large, recognisable objects suitable for Nursery children.
- Preserve Star mascot proportions and supportive expression language.
- Avoid dense scenes, hidden ambiguity, trick questions, photorealism and decorative pseudo-instructions.
- Child-facing text must remain exact, short and legible.
- Visual clues must be sufficient, fair and developmentally appropriate.
""",
    "review-checklist.md": """# Phase 5 Page Review Checklist

## Content
- Exact page title and instruction
- Activity matches the intended learning objective
- Observe–Think–Try–Solve step is clear
- One defensible solution or intentionally open response is explicit
- Teacher and parent support are age appropriate

## Design
- Correct logo, title hierarchy and page number
- A4 portrait composition and safe margins
- No clipping, overlap or overcrowding
- Typography remains readable at print size

## Illustration
- Star and children remain consistent
- Objects are recognisable and culturally inclusive
- Clues are visible without accidental distraction
- No unsafe, confusing or inaccessible visual cues

## Decision
Approve only when every item passes.
""",
    "illustration-release-plan.md": """# Illustration Release Plan

Artwork is released in four review batches:

- Batch 1: P001–P011
- Batch 2: P012–P022
- Batch 3: P023–P033
- Batch 4: P034–P044

Each batch requires prompt-to-page review, problem-solving clarity review, illustration consistency review and publishing review before approval.
""",
}

for name, content in phase5_files.items():
    (PHASE5 / name).write_text(content, encoding="utf-8")

with (PHASE5 / "page-review-status.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["page", "page_id", "artwork_status", "educational_review", "problem_solving_review", "design_review", "illustration_review", "accessibility_review", "publishing_review", "final_decision"])
    for i in range(1, 45):
        writer.writerow([i, f"PS-NURSERY-V5-P{i:03d}", "not_started", "pending", "pending", "pending", "pending", "pending", "pending", "blocked"])

asset_tracking = {
    "book": "Problem Solvers Gold",
    "page_count": 44,
    "approved_pages": 0,
    "artwork_status": "not_started",
    "required_assets": ["official_bcube_logo", "approved_star_mascot", "locked_font_family", "page_template"],
    "release_allowed": False,
}
(PHASE5 / "asset-tracking.json").write_text(json.dumps(asset_tracking, indent=2) + "\n", encoding="utf-8")

artwork_manifest = {
    "schema_version": "1.0.0",
    "book_id": "PS-NURSERY-V5",
    "expected_pages": 44,
    "approved_pages": 0,
    "batches": [
        {"id": "B1", "range": "P001-P011", "status": "not_started"},
        {"id": "B2", "range": "P012-P022", "status": "not_started"},
        {"id": "B3", "range": "P023-P033", "status": "not_started"},
        {"id": "B4", "range": "P034-P044", "status": "not_started"},
    ],
    "release_allowed": False,
}
(PHASE5 / "artwork-manifest.json").write_text(json.dumps(artwork_manifest, indent=2) + "\n", encoding="utf-8")

phase6_files = {
    "README.md": """# Phase 6 — Publishing Framework

This phase governs final assembly, prepress verification, print approval and release packaging for Problem Solvers Gold.

The framework is complete. Final publication approval depends on 44 approved artwork pages and successful prepress checks.
""",
    "prepress-checklist.md": """# Prepress Checklist

- Final sequence contains exactly 44 physical pages.
- A4 portrait trim size is correct.
- Bleed and safe margins are verified.
- Images meet print resolution requirements.
- Fonts are embedded or converted according to the publishing standard.
- Colour space and export profile match printer requirements.
- Page numbers, titles and logo placement are correct.
- No missing, duplicated, clipped or blank pages.
- Every puzzle remains understandable in printed form.
- Copyright, publisher address, email and website are verified.
""",
    "print-validation.md": """# Print Validation

Validate the final PDF at 100% zoom and through a physical proof. Check line weight, colour consistency, clue visibility, text legibility, trim safety, binding-side clearance and activity usability. Any print defect or obscured problem-solving clue blocks release.
""",
    "final-release-checklist.md": """# Final Release Checklist

- All 44 pages approved in Phase 5
- Final PDF generated and checksum recorded
- Prepress checklist passed
- Physical or certified digital proof approved
- Problem-solving clarity confirmed in print
- Release manifest completed
- Source files and final outputs archived
- Publication status changed to released only after sign-off
""",
    "publication-gates.md": """# Publication Gates

1. Prompt package pass
2. Automated validation pass
3. Human artwork approval for 44/44 pages
4. Problem-solving clarity approval
5. Prepress pass
6. Print proof pass
7. Publisher sign-off

Failure at any gate blocks publication.
""",
    "print-approval.md": """# Print Approval

Book: Problem Solvers Gold
Edition: First Edition

- Editorial approval: pending
- Educational approval: pending
- Problem-solving approval: pending
- Design approval: pending
- Prepress approval: pending
- Publisher approval: pending

Final release is valid only when all approvals are recorded with reviewer and date.
""",
}

for name, content in phase6_files.items():
    (PHASE6 / name).write_text(content, encoding="utf-8")

release_template = {
    "schema_version": "1.0.0",
    "book_id": "PS-NURSERY-V5",
    "title": "Problem Solvers Gold",
    "edition": "First Edition",
    "page_count": 44,
    "source_branch": "book6/problem-solvers-phase1-3",
    "artwork_approved_pages": 0,
    "final_pdf": None,
    "final_pdf_sha256": None,
    "release_zip": None,
    "release_status": "blocked",
    "approvals": [],
}
(PHASE6 / "release-manifest-template.json").write_text(json.dumps(release_template, indent=2) + "\n", encoding="utf-8")

publication_status = {
    "book_id": "PS-NURSERY-V5",
    "framework_status": "complete",
    "artwork_approved_pages": 0,
    "required_pages": 44,
    "problem_solving_approval_status": "not_started",
    "prepress_status": "not_started",
    "print_approval_status": "not_started",
    "publication_status": "blocked",
}
(PHASE6 / "publication-status.json").write_text(json.dumps(publication_status, indent=2) + "\n", encoding="utf-8")

required = [
    *(PHASE5 / name for name in phase5_files),
    PHASE5 / "page-review-status.csv",
    PHASE5 / "asset-tracking.json",
    PHASE5 / "artwork-manifest.json",
    *(PHASE6 / name for name in phase6_files),
    PHASE6 / "release-manifest-template.json",
    PHASE6 / "publication-status.json",
]
missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
summary = {
    "commit": "C",
    "phase5_framework": "pass" if not missing else "fail",
    "phase6_framework": "pass" if not missing else "fail",
    "required_files": len(required),
    "missing_files": missing,
    "overall_decision": "PASS" if not missing else "FAIL",
}
(QA / "commit-c-framework-report.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
(QA / "commit-c-summary.md").write_text(
    "# Commit C Summary\n\n"
    f"- Phase 5 framework: {summary['phase5_framework'].upper()}\n"
    f"- Phase 6 framework: {summary['phase6_framework'].upper()}\n"
    f"- Required framework files: {summary['required_files']}\n"
    f"- Missing files: {len(missing)}\n\n"
    "## Decision\n"
    f"`{summary['overall_decision']} — PHASE 5 AND PHASE 6 FRAMEWORK COMPLETE`\n\n"
    "Actual artwork and final print release remain governed by the recorded approval gates.\n",
    encoding="utf-8",
)

if missing:
    raise SystemExit("Missing required files: " + ", ".join(missing))

print(json.dumps(summary, indent=2))
