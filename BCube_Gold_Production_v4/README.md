# BCube Gold Production v4

This directory contains the locked BCube Gold page-design and artwork-production standard for Nursery, LKG and UKG. Existing `production-prompts` v3 curriculum packages remain unchanged and are the only curriculum source of truth.

## Canonical source hierarchy

1. `production-prompts/README.md` — official 30-book portfolio plan.
2. Each book release README — official 41-page sequence, prompt IDs and page titles.
3. Each page Markdown/JSON package — official page objective, visible wording, child activity, teacher move, parent extension, illustration requirements and prohibitions.
4. `BCube_Gold_Production_v4/` — visual-production layer only; it must not rewrite curriculum, book names, chapters, page titles, page order or learning objectives.

## Locked portfolio

- Nursery: 10 books × 41 pages
- LKG: 10 books × 41 pages
- UKG: 10 books × 41 pages
- Total: 30 books / 1,230 individual page packages

See:

- [`../production-prompts/README.md`](../production-prompts/README.md)
- [`CANONICAL_BOOK_AND_PAGE_INDEX.md`](CANONICAL_BOOK_AND_PAGE_INDEX.md)

## Non-negotiable production rules

- Use only book names already present in `production-prompts/README.md`.
- Use only page/chapter titles already present in that book's release README.
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