# BCube Deterministic Execution Contract

Status: FINAL and LOCKED

This contract governs all book-artwork production under `BCube_Gold_Production_v4`.

## Mandatory governance documents

Every production job must comply with:

- `FOUNDER_LOCK.md`
- `GOLD_ACCEPTANCE_CRITERIA_v1.md`
- `QA_SCORECARD.md`
- `REJECTION_RULES.md`
- `IMAGE_GENERATION_PIPELINE.md`
- `FRONT_MATTER_AND_NUMBERING_POLICY.md`
- `INDIVIDUAL_PAGE_OUTPUT_POLICY.md`

## Source of truth

1. `production-prompts/README.md` defines the approved 30-book portfolio.
2. Each migrated book release README defines the exact 43-package sequence.
3. Each page Markdown and JSON package defines the exact page content.
4. `BCube_Gold_Production_v4` may improve visual execution only. It may not invent, rename, reorder, merge or remove books, pages, chapters, objectives, activities or visible wording.

## Deterministic page pipeline

For every page, execute these steps in this order:

1. Resolve the book from the canonical portfolio.
2. Confirm that the book has completed the 43-package front-matter migration; block final production when it has not.
3. Resolve the exact page from the migrated book release README.
4. Load both the page Markdown and page JSON.
5. Validate book name, level, production position, logical page, printed-number visibility, title and prompt ID against the release README.
5. Apply only the page-specific instructions plus locked v4 visual rules.
6. Generate exactly one flat, front-facing A4 portrait page.
7. Reserve the official logo zone or place the exact official logo asset through deterministic composition; never redraw the logo.
8. Run the preflight and postflight rejection gates.
9. Complete the weighted QA scorecard.
10. Accept only at 95/100 or higher with zero critical defects.
11. Save one page image using the canonical prompt ID as the filename.

## Non-negotiable output rules

- One source page equals one standalone image.
- Never create collages, overview boards, contact sheets or multi-page composites.
- A page-range request always produces one individual A4 file per page; never use
  one combined image as the result or user-facing validation preview.
- Do not deliver or link an internal QA montage/contact sheet. Deliver individual
  pages directly or a ZIP containing only individual page files.
- Never invent a book or chapter.
- Never change the canonical page title.
- Never add activities, teacher boxes, parent boxes, speech bubbles or labels unless the page package requires them.
- Never place an AI-generated BCube logo.
- Never mark a page approved when it conflicts with the source package.
- Never use chat history as curriculum authority when repository content exists.
- Never approve a page below 95/100.
- Any critical failure overrides the numeric score.

## Fixed production geometry

- A4 portrait: 210 × 297 mm
- 3 mm bleed
- Minimum 10 mm safe margin
- 12 mm binding margin
- 300 DPI
- CMYK-safe print palette
- Flat, front-facing page only

## Locked numbering geometry

- P001 cover: no logical number and no printed number.
- P002–P005: logical pages 1–4, printed numbers hidden.
- P006 Welcome: logical and printed page 5.
- P007–P043: logical and printed pages 6–42.
- Contents occupies P004 and P005 and excludes all front matter.

## File naming

`<PROMPT_ID>.png`

Example:

`CC-NURSERY-V3-P001.png`

## Approval rule

A page is approved only when:

- source identity matches,
- exact visible wording matches,
- required illustration scene matches,
- required activities and response spaces match,
- prohibited elements are absent,
- official-logo handling is respected,
- one-page-only output is respected,
- delivery contains only individual page files and no contact sheet, montage,
  collage, overview, grid or composite,
- print geometry is valid,
- weighted QA score is at least 95/100,
- critical defect count is zero.

Any failed critical check blocks release and requires regeneration. No manual override is allowed unless the Founder explicitly updates the repository specification.
