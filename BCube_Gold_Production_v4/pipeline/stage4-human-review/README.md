# Stage 4 — Human Review and Approval Gate

Stage 4 consumes the Stage 3 visual-QA manifest and records the publisher's page-level decision before PDF assembly.

## Entry gate

Stage 4 accepts only canonical Nursery records with unique prompt IDs and a Stage 3 decision of `PASS`, `REVIEW`, `REGENERATE`, or `BLOCKED`.

## Reviewer decisions

- `APPROVED` — page may proceed to PDF assembly.
- `APPROVED_WITH_NOTE` — page may proceed, with a non-blocking recorded note.
- `CHANGES_REQUIRED` — create a targeted correction/regeneration item.
- `REJECTED` — page is blocked and must be replaced.
- `PENDING` — no final decision yet.

Automated Stage 3 `PASS` pages may be prefilled as `PENDING_CONFIRMATION`, but they are not publisher-approved until a named reviewer submits a final decision.

## Required review record

Each final decision contains the prompt ID, book slug, page number, Stage 3 evidence hash, reviewer name, role, decision, reason code, note and UTC timestamp.

## Outputs

- `output/review-template.csv`
- `output/review-decisions.json`
- `output/correction-queue.json`
- `output/approval-manifest.json`
- `output/stage4-summary.md`

## Exit gate

Stage 4 passes only when all 440 canonical pages have a final review record, all decisions are `APPROVED` or `APPROVED_WITH_NOTE`, no correction items remain open, and every decision is traceable to the current Stage 3 evidence hash.

PDF assembly and prepress remain blocked until this gate passes.
