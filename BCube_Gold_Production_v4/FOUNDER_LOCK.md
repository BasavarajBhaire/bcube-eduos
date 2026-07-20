# BCube Founder Lock

Status: FINAL
Owner: Basavaraj Bhaire

The following production decisions are locked and may not be changed by prompts, image models, automation, templates or downstream tooling without an explicit repository update approved by the Founder.

## Locked curriculum authority

1. `production-prompts/README.md` defines the approved portfolio.
2. Each migrated book release README defines the exact 43-package sequence; legacy 41-package READMEs remain curriculum migration inputs only.
3. Each page Markdown and JSON package defines the exact page content.
4. `BCube_Gold_Production_v4` controls visual production only.

## Locked non-negotiables

- No invented book names.
- No invented chapters or pages.
- No page merging or page splitting.
- One source page equals one standalone A4 page image.
- No collage, contact sheet or multi-page composite.
- No AI-generated BCube logo.
- Use only the official logo asset unchanged.
- Preserve canonical visible wording, activities, illustration requirements and prohibitions.
- Preserve page-number policy, including no visible number on covers unless explicitly required.
- Preserve the locked Star identity and approved character continuity.
- Minimum approval score is 95/100 with zero critical defects.
- Every Nursery, LKG and UKG book uses the common 43-package front-matter architecture.
- The cover is unnumbered and not counted.
- About This Book, Copyright and the two Contents pages are internally counted as pages 1–4 but show no visible number.
- Welcome is the first visibly numbered page and must show page 5.
- Contents is two pages, grouped by canonical modules, and excludes all front matter.
- The post-migration portfolio contains 30 books and 1,290 individual page packages.

See `FRONT_MATTER_AND_NUMBERING_POLICY.md`. Existing 41-package releases are legacy migration inputs and may not enter final v4 assembly.

## Override policy

A rule may be changed only through a committed repository update that:

- identifies the exact rule being changed,
- explains the reason,
- updates all affected schemas, manifests and QA documents,
- is explicitly approved by the Founder.

Chat discussion, model preference or generated output never overrides this file.
