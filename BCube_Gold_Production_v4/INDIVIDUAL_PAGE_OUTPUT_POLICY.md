# BCube Individual Page Output and Delivery Policy

Status: FOUNDER APPROVED — MANDATORY

Policy version: 1.0.0

Effective date: 2026-07-20

## Repository authority

This repository policy is the permanent source of truth. It overrides chat history,
temporary previews and operator assumptions for every BCube book, level and build.
Every production or validation run must read this file before generating or
delivering page artwork.

## Locked rule

**One logical book page equals one individual A4 portrait file.**

- Generate, review, save and deliver every page separately.
- Never combine two or more book pages into one image, canvas, PDF page, slide,
  preview board, montage, grid, collage or contact sheet.
- A request for a page range means multiple individual files, one file per page.
- A ZIP may contain individual page files, but the ZIP does not replace them with
  a composite image.
- A multi-page PDF may be assembled only when explicitly requested after every
  individual page has passed QA; each PDF page must contain exactly one book page.

## Validation-preview rule

Contact sheets, montages and overview grids are not book pages and are not
validation deliverables.

- Do not present, attach, link or describe a contact sheet as the generated result.
- Do not place contact sheets in the book output directory.
- If an internal contact sheet is temporarily required for operator-only QA, store
  it under a clearly separated temporary QA path and never include it in the
  deliverable ZIP, manifest, release count or user-facing handoff.
- User validation must use the individual page files.

## File and count contract

- Canonical page filename: PROMPT_ID.png, or the migrated v4 equivalent defined
  by the book manifest.
- Each PNG must contain exactly one flat, front-facing A4 portrait page.
- The number of individual PNG files must equal the requested package count.
- Cover through reader page 15 means 16 files: one uncounted cover plus 15 counted
  pages.
- No filenames containing contact-sheet, contact_sheet, montage, collage,
  overview, grid or composite may appear in a deliverable directory or ZIP.

## Handoff contract

Every handoff must:

1. State the exact number of individual page files.
2. Provide the individual files directly or provide a ZIP containing only those
   individual files.
3. Never use a combined-page image as the main preview or result.
4. Identify any non-page QA artifact separately and keep it out of the handoff.

Any violation is a critical defect and requires a corrected rebuild or redelivery.
