# BCube Publishing Engine V5 — QA Backlog

## Release gate

A page is production-eligible only when all P0 checks pass, machine QA reports zero critical defects, and human approval is bound to the final artifact SHA-256.

## P0 — Critical

- **QA-001 — Official Star missing:** fail with `FAIL_OFFICIAL_STAR_NOT_VISIBLE`.
- **QA-002 — Star source is a workbook page:** fail with `FAIL_OFFICIAL_STAR_NOT_STANDALONE`.
- **QA-003 — Star background is not transparent:** fail with `FAIL_OFFICIAL_STAR_BACKGROUND_NOT_TRANSPARENT`.
- **QA-004 — Illustration source integrity:** delete stale staged files and bind the staged candidate to recorded evidence.
- **QA-005 — Illustration contamination:** reject text, logo, mascot, badge, embedded page, or full-page layout evidence.
- **QA-006 — Required asset missing:** fail closed; never substitute a placeholder.

## P1 — High

- **QA-007 — Illustration safe placement:** preserve aspect ratio and never crop faces or limbs.
- **QA-008 — Illustration occupancy:** enforce the approved frame occupancy range.
- **QA-009 — Footer and banner symbols:** draw deterministic vector symbols, not unsupported font glyphs.
- **QA-010 — Cross-book content:** reject prohibited book-specific text and assets.

## P2 — Medium

- **QA-011 — Golden-master geometry:** compare locked component bounds within approved tolerance.
- **QA-012 — Candidate traceability:** retain prompt, source hash, staged hash, composition evidence, QA report, reviewer, and final hash.
- **QA-013 — Visual difference artifact:** generate a review overlay for geometry or source-region differences.

## Current blocker

The repository must contain a dedicated transparent official Star mascot PNG. A complete workbook page or crop instruction is not an acceptable production asset.
