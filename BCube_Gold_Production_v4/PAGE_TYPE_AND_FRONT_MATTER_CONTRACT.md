# BCube Page-Type and Front-Matter Contract

Status: PRE-PRINT PILOT
Scope: Nursery, LKG, UKG and future levels

## Architecture

Every page is resolved from three layers:

1. Global publishing layer — assets, geometry, typography, numbering, export and QA only.
2. Book layer — `{Book Name}`, theme, skill language and book-specific visual identity.
3. Individual page layer — exact objective, illustration, child activity, teacher guidance and parent connection.

The global layer must never replace or generalise individual page content.

## Reusable placeholders

Global specifications must use placeholders rather than hard-coded book names:

- `{Book Name}`
- `{Series Name}`
- `{Page Title}`
- `{Age Group}`
- `{Module Name}`
- `{Lesson Title}`
- `{Physical Page}`
- `{Printed Page}`
- `{Official Logo}`
- `{Official Star Mascot}`
- `{Teacher Guidance}`
- `{Parent Guidance}`
- `{Learning Objective}`
- `{Illustration Layer}`

## Header contracts

Every page type must resolve one explicit header contract before composition starts.

### `SERIES_HEADER`

Allowed only on the cover.

- `{Official Logo}`
- `{Series Name}`
- `{Book Name}`
- `{Age Group}` badge
- cover tagline where approved

### `MINIMAL_HEADER`

Used on publisher/copyright pages.

- `{Official Logo}` only when approved by the publisher-page template
- `{Book Name}`
- `{Age Group}`
- no series banner
- no Star mascot
- no decorative illustration

### `BOOK_HEADER`

Used for About, Contents, Character Introduction, How to Use, certificate and other front/end matter.

- `{Official Logo}`
- `{Book Name}` as the primary identity
- `{Page Title}` as the secondary title
- `{Age Group}` badge when allowed by the page contract
- `{Series Name}` banner prohibited

### `LESSON_HEADER`

Used for lesson, assessment and learning pages.

- `{Official Logo}`
- `{Book Name}` or approved compact book identifier
- `{Lesson Title}` or `{Page Title}`
- `{Age Group}` badge when specified by the template
- visible `{Printed Page}` only when the release manifest permits it

A page must never substitute one header contract for another.

## Page-type contracts

### Cover
- Header type: `SERIES_HEADER`.
- Full premium illustration allowed.
- `{Series Name}`, `{Book Name}`, age badge, six book skills and five core pillars.
- No visible page number.
- Official logo and Star are deterministically composited.

### Publisher / Copyright
- Header type: `MINIMAL_HEADER`.
- No illustration.
- No Star mascot.
- No teacher, parent or activity panels.
- White or very light neutral background.
- Publisher details only.
- No visible page number.

### About This Book
- Header type: `BOOK_HEADER`.
- Header shows `{Book Name}` and `{Page Title}`.
- Do not repeat the series banner.
- Illustration and learning-outcome icons are allowed.
- Teacher and parent panels are prohibited.
- No visible page number.

### Contents
- Header type: `BOOK_HEADER`.
- Header shows `{Book Name}` and `{Page Title}`.
- Small navigation icons only; no dominant full-page illustration.
- Teacher and parent panels are prohibited.
- No visible page number.

### Character Introduction / How to Use
- Header type: `BOOK_HEADER`.
- Page-specific illustration or instructional graphics allowed.
- No visible page number while part of front matter.

### Lesson / Learning Page
- Header type: `LESSON_HEADER`.
- First visible page number appears on the first lesson.
- Front matter counts internally even though its numbers are hidden.
- Example: four counted front-matter pages means Lesson 1 displays page 5.
- Individual V4 page content remains authoritative.

### Assessment / Reflection / Certificate
- Use the page-specific approved header contract.
- Continue visible numbering unless the approved page package explicitly hides it.

### Back Cover
- No visible page number.
- One true back cover only.

## Component permission matrix

| Component | Cover | Publisher | About | Contents | Character / How-to | Lesson | Certificate | Back Cover |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Series header | Yes | No | No | No | No | No | No | No |
| Book header | No | Minimal | Yes | Yes | Yes | Compact | Yes | Optional |
| Official logo | Yes | Optional | Yes | Yes | Yes | Yes | Yes | Yes |
| Official Star | Yes | No | Optional | Optional | Yes | Page-specific | Optional | Optional |
| Full illustration | Yes | No | Yes | No | Page-specific | Yes | No | Page-specific |
| Teacher panel | No | No | No | No | No | Yes | No | No |
| Parent panel | No | No | No | No | No | Yes | No | No |
| Visible page number | No | No | No | No | No | Yes | Manifest | No |
| Core pillars | Yes | No | Optional | No | Optional | Template-specific | No | Optional |

Any component marked `No` is a critical defect if present.

## Mandatory GitHub pre-generation preflight

Before any image-generation or composition call, the production process must read the current `main` branch versions of:

1. the page release manifest;
2. the individual V4 page package;
3. `rules/page-type-and-front-matter-contract.json`;
4. the global pixel design tokens;
5. the official asset registry and asset locks.

The preflight must resolve and record:

- page type;
- required header contract;
- allowed and prohibited components;
- visible-page-number rule;
- exact pixel layout token set;
- official logo path;
- official Star path when allowed;
- individual page objective and illustration brief.

Generation must stop when any required file, field or asset is missing, stale or contradictory. Chat memory, prior generated images and generic prompt defaults are not authoritative.

## Numbering rule

- Cover is unnumbered.
- Counted front matter has hidden printed numbers.
- Visible numbering begins on the first learning page at the correct accumulated count.
- Numbering must follow the release manifest, never an AI guess.

## Pre-print maturity labels

Formal edition and semantic release versioning begin only after the first physical print is approved.

Before that milestone, use only:

- DRAFT
- DESIGN REVIEW
- PILOT
- PRINT PROOF
- PRINT APPROVED

After the first approved print, establish First Edition and v1.0.

## Fail-closed rules

Reject a page when:

- a book name is hard-coded in a global template;
- the wrong header contract is used;
- the publisher page contains an illustration or mascot;
- front-matter page numbers are visible;
- the first lesson number does not include counted front matter;
- the About page repeats the series banner instead of `{Book Name}`;
- an About or Contents page contains teacher or parent panels;
- a component prohibited by the page-type matrix is present;
- global rules override page-specific educational intent;
- an official asset is generated, redrawn or substituted;
- typography is embedded in the AI illustration layer;
- layout regions overlap, duplicate or fall outside safe margins;
- the GitHub pre-generation preflight was not completed against current `main`.

Acceptance requires 100/100 QA and zero critical defects.
