# BCube Gold Production v4

This directory contains the locked BCube Gold page-design and artwork-production standard for Nursery, LKG and UKG. Existing `production-prompts` v3 packages remain the curriculum source during the portfolio front-matter migration.

## Founder-approved portfolio architecture

All 30 books must migrate to the common 43-package architecture defined in:

- [`FRONT_MATTER_AND_NUMBERING_POLICY.md`](FRONT_MATTER_AND_NUMBERING_POLICY.md)
- [`PORTFOLIO_43_PAGE_MIGRATION_PLAN.md`](PORTFOLIO_43_PAGE_MIGRATION_PLAN.md)
- [`portfolio-front-matter-policy.json`](portfolio-front-matter-policy.json)

The legacy 41-package releases must not be used for final v4 book assembly until their front matter, identifiers and printed numbering have been migrated and validated.

## Canonical source hierarchy

1. `production-prompts/README.md` — official 30-book portfolio plan.
2. Each migrated book release README — official 43-package sequence, prompt IDs, logical pages and printed-number policy. Legacy 41-package READMEs remain curriculum migration inputs only.
3. Each page Markdown/JSON package — official page objective, visible wording, child activity, teacher move, parent extension, illustration requirements and prohibitions.
4. `BCube_Gold_Production_v4/` — visual-production layer only; it must not rewrite curriculum, book names, chapters, page titles, page order or learning objectives.

## Locked portfolio

- Nursery target: 10 books × 43 packages = 430
- LKG target: 10 books × 43 packages = 430
- UKG target: 10 books × 43 packages = 430
- Portfolio target: 30 books / 1,290 individual page packages

See:

- [`../production-prompts/README.md`](../production-prompts/README.md)
- [`CANONICAL_BOOK_AND_PAGE_INDEX.md`](CANONICAL_BOOK_AND_PAGE_INDEX.md)

## Non-negotiable production rules

- Use only book names already present in `production-prompts/README.md`.
- Use only page/chapter titles already present in that book's release README.
- Apply the locked front-matter and numbering policy before creating final book artwork.
- Read the individual page Markdown/JSON before creating its illustration.
- Produce one standalone A4 page image per source page.
- Never create collages, contact sheets, overview boards or multiple chapters inside one generated image.
- Never invent a new book, chapter, activity, learning objective or page sequence.
- Improve only layout, illustration quality, teaching clarity and print production.
- Use the official BCube logo asset only; never ask an image model to redraw it.
- Reserve a fixed clean logo zone during artwork generation and place the official logo afterward.
- Follow the page-specific source even when it differs from a reusable template.
- A4 portrait, print-first, safe margins and publication-ready hierarchy.
- Design principle: Less. Bigger. Better.

## Production workflow

For every generated page:

1. Select the canonical book and page from the release README.
2. Read that page's Markdown and JSON source.
3. Extract exact title, page number, objective, visible wording, child response, teacher guidance, parent extension, illustration scene and prohibitions.
4. Generate one individual page only.
5. Composite the official logo without alteration.
6. Validate the page against the source package and print QA checklist.
7. Store the result under the matching book/level/page path.

No standalone book named `Alphabet Champions` or `Alphabet Adventures` exists in the locked portfolio. Alphabet-related pages must remain inside the approved literacy books and exact page sequences where they already occur.
