from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "books" / "nursery" / "creativity-creators"
PHASE5 = BOOK / "phase5"
PHASE6 = BOOK / "phase6"
QA = BOOK / "qa"

for directory in (PHASE5, PHASE6, QA):
    directory.mkdir(parents=True, exist_ok=True)

phase5_files = {
    "README.md": """# Phase 5 — Artwork Production Framework\n\nThis phase controls generation, review, approval and release of the 44 Creativity Creators page artworks.\n\n## Status\nFramework complete. Artwork production is tracked page by page.\n\n## Required outcome\nEvery page must pass educational, visual, brand, typography, accessibility and print-readiness review before release.\n""",
    "artwork-pipeline.md": """# Artwork Pipeline\n\n1. Load the approved production prompt and locked assets.\n2. Generate one flat A4 portrait page.\n3. Check title, page number, logo, instruction and visual hierarchy.\n4. Review educational clarity and Nursery suitability.\n5. Review illustration consistency and accessibility.\n6. Record the decision in `page-review-status.csv`.\n7. Approve only when every required gate passes.\n\nNo placeholder or unreviewed image may enter the release package.\n""",
    "illustration-generation-guidelines.md": """# Illustration Generation Guidelines\n\n- A4 portrait, print-oriented composition and generous safe margins.\n- Premium preschool illustration style with rounded forms and clean outlines.\n- One dominant learning focus per page.\n- Large, recognisable objects suitable for Nursery children.\n- Preserve Star mascot proportions and expression language.\n- Avoid dense scenes, empty speech bubbles, harsh shadows, photorealism and decorative text.\n- Child-facing text must remain exact, short and legible.\n- Creativity pages must allow meaningful child choice rather than prescribing one correct artistic result.\n""",
    "review-checklist.md": """# Phase 5 Page Review Checklist\n\n## Content\n- Exact page title and instruction\n- Activity matches learning objective\n- Creativity pillar is visible in the task\n- Teacher and parent support are age appropriate\n\n## Design\n- Correct logo, title hierarchy and page number\n- A4 portrait composition and safe margins\n- No clipping, overlap or overcrowding\n- Typography remains readable at print size\n\n## Illustration\n- Star and children remain consistent\n- Objects are recognisable and culturally inclusive\n- Activity area is large enough for Nursery children\n- No unsafe, confusing or inaccessible visual cues\n\n## Decision\nApprove only when every item passes.\n""",
    "illustration-release-plan.md": """# Illustration Release Plan\n\nArtwork is released in four review batches:\n\n- Batch 1: P001–P011\n- Batch 2: P012–P022\n- Batch 3: P023–P033\n- Batch 4: P034–P044\n\nEach batch requires prompt-to-page review, illustration consistency review and publishing review before it can be marked approved.\n""",
}

for name, content in phase5_files.items():
    (PHASE5 / name).write_text(content, encoding="utf-8")

with (PHASE5 / "page-review-status.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["page","page_id","artwork_status","educational_review","design_review","illustration_review","accessibility_review","publishing_review","final_decision"])
    for i in range(1, 45):
        writer.writerow([i, f"CC-NURSERY-V5-P{i:03d}", "not_started", "pending", "pending", "pending", "pending", "pending", "blocked"])

asset_tracking = {
    "book": "Creativity Creators Gold",
    "page_count": 44,
    "approved_pages": 0,
    "artwork_status": "not_started",
    "required_assets": ["official_bcube_logo", "approved_star_mascot", "locked_font_family", "page_template"],
    "release_allowed": False,
}
(PHASE5 / "asset-tracking.json").write_text(json.dumps(asset_tracking, indent=2) + "\n", encoding="utf-8")

artwork_manifest = {
    "schema_version": "1.0.0",
    "book_id": "CC-NURSERY-V5",
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
    "README.md": """# Phase 6 — Publishing Framework\n\nThis phase governs final assembly, prepress verification, print approval and release packaging for Creativity Creators Gold.\n\nThe framework is complete. Final publication approval depends on 44 approved artwork pages and successful prepress checks.\n""",
    "prepress-checklist.md": """# Prepress Checklist\n\n- Final sequence contains exactly 44 physical pages.\n- A4 portrait trim size is correct.\n- Bleed and safe margins are verified.\n- Images meet print resolution requirements.\n- Fonts are embedded or converted according to the publishing standard.\n- Colour space and export profile match printer requirements.\n- Page numbers, titles and logo placement are correct.\n- No missing, duplicated, clipped or blank pages.\n- Copyright, publisher address, email and website are verified.\n""",
    "print-validation.md": """# Print Validation\n\nValidate the final PDF at 100% zoom and through a physical proof. Check line weight, colour consistency, text legibility, trim safety, binding-side clearance and activity usability. Any print defect blocks release.\n""",
    "final-release-checklist.md": """# Final Release Checklist\n\n- All 44 pages approved in Phase 5\n- Final PDF generated and checksum recorded\n- Prepress checklist passed\n- Physical or certified digital proof approved\n- Release manifest completed\n- Source files and final outputs archived\n- Publication status changed to released only after sign-off\n""",
    "publication-gates.md": """# Publication Gates\n\n1. Prompt package pass\n2. Automated validation pass\n3. Human artwork approval for 44/44 pages\n4. Prepress pass\n5. Print proof pass\n6. Publisher sign-off\n\nFailure at any gate blocks publication.\n""",
    "print-approval.md": """# Print Approval\n\nBook: Creativity Creators Gold\nEdition: First Edition\n\n- Editorial approval: pending\n- Educational approval: pending\n- Design approval: pending\n- Prepress approval: pending\n- Publisher approval: pending\n\nFinal release is valid only when all approvals are recorded with reviewer and date.\n""",
}
for name, content in phase6_files.items():
    (PHASE6 / name).write_text(content, encoding="utf-8")

release_template = {
    "schema_version": "1.0.0",
    "book_id": "CC-NURSERY-V5",
    "title": "Creativity Creators Gold",
    "edition": "First Edition",
    "page_count": 44,
    "source_branch": "book4/creativity-creators-phase1-2",
    "artwork_approved_pages": 0,
    "final_pdf": None,
    "final_pdf_sha256": None,
    "release_zip": None,
    "release_status": "blocked",
    "approvals": [],
}
(PHASE6 / "release-manifest-template.json").write_text(json.dumps(release_template, indent=2) + "\n", encoding="utf-8")

publication_status = {
    "book_id": "CC-NURSERY-V5",
    "framework_status": "complete",
    "artwork_approved_pages": 0,
    "required_pages": 44,
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
    "commit": "D",
    "phase5_framework": "pass" if not missing else "fail",
    "phase6_framework": "pass" if not missing else "fail",
    "required_files": len(required),
    "missing_files": missing,
    "overall_decision": "PASS" if not missing else "FAIL",
}
(QA / "commit-d-framework-report.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
(QA / "commit-d-summary.md").write_text(
    "# Commit D Summary\n\n"
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
