# BCube Deterministic Image Generation Pipeline

Status: MANDATORY

## Goal

Convert one canonical repository page package into one validated, publication-ready A4 page without changing curriculum content.

## Required inputs

- Canonical portfolio entry.
- Book release README entry.
- Page Markdown package.
- Page JSON package.
- Official BCube logo asset.
- Locked character references.
- `EXECUTION_CONTRACT.md`.
- `GOLD_ACCEPTANCE_CRITERIA_v1.md`.
- `QA_SCORECARD.md`.
- `REJECTION_RULES.md`.
- `FRONT_MATTER_AND_NUMBERING_POLICY.md`.

## Execution sequence

1. Resolve one page by canonical prompt ID.
2. Confirm the source belongs to a migrated 43-package manifest.
3. Load the matching Markdown and JSON.
3. Cross-check book, level, page, title, prompt ID and visible wording.
4. Build a page job from the manifest and schema.
5. Generate only the illustration/background layer when exact branding or typography cannot be guaranteed by the image model.
6. Compose the final A4 page with deterministic layout tooling.
7. Place the exact official BCube logo asset unchanged.
8. Place exact repository text using approved typography.
9. Export exactly one standalone PNG named `<PROMPT_ID>.png`.
10. Run critical rejection checks.
11. Complete the weighted QA scorecard.
12. Approve only at 95/100 or higher with zero critical defects.
13. Otherwise regenerate or recompose; never silently accept.

## Multi-image prevention

Every generation job must state all of the following:

- exactly one page,
- exactly one A4 portrait canvas,
- no collage,
- no contact sheet,
- no preview grid,
- no book overview,
- no multiple variants,
- no second page,
- no thumbnail board.

Any detected second page or page-like frame is a critical failure.

## Logo handling

The image model must not redraw the BCube logo. Use one of two approved paths:

1. Reserve a clean logo zone and composite the official asset afterward.
2. Use a deterministic page compositor that places the exact official asset.

No generative approximation is permitted.

## Cover-specific rule

For cover pages:

- no visible page number unless the canonical package explicitly requires it,
- no worksheet boxes,
- no learning-objective box,
- no teacher tips,
- no parent corner,
- no child response space,
- one strong hero scene and exact cover wording only.

## Front-matter-specific rules

- P002 About This Book is adult-facing and contains no scored child activity.
- P003 Copyright uses only locked controlled publication metadata.
- P004 and P005 form one module-wise Contents sequence across two standalone A4 pages.
- P001–P005 show no printed number.
- P006 Welcome is the first page with a visible number and shows 5.

## Output states

- `queued`
- `source_validated`
- `generated`
- `rejected`
- `regeneration_required`
- `gold_certified`

Only `gold_certified` outputs may enter the final book assembly.
