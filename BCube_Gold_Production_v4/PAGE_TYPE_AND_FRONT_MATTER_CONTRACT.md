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

## Page-type contracts

### Cover
- Full premium illustration allowed.
- `{Series Name}`, `{Book Name}`, age badge, six book skills and five core pillars.
- No visible page number.
- Official logo and Star are deterministically composited.

### Publisher / Copyright
- No illustration.
- No Star mascot.
- No teacher, parent or activity panels.
- White or very light neutral background.
- Publisher details only.
- No visible page number.

### About This Book
- Header shows `{Book Name}` and `{Page Title}`.
- Do not repeat the series banner.
- Illustration and learning-outcome icons are allowed.
- No visible page number.

### Contents
- Header shows `{Book Name}` and `{Page Title}`.
- Small navigation icons only; no dominant full-page illustration.
- No visible page number.

### Character Introduction / How to Use
- Page-specific illustration or instructional graphics allowed.
- No visible page number while part of front matter.

### Lesson / Learning Page
- First visible page number appears on the first lesson.
- Front matter counts internally even though its numbers are hidden.
- Example: four counted front-matter pages means Lesson 1 displays page 5.
- Individual V4 page content remains authoritative.

### Assessment / Reflection / Certificate
- Use the page-specific contract.
- Continue visible numbering unless the approved page package explicitly hides it.

### Back Cover
- No visible page number.
- One true back cover only.

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
- the publisher page contains an illustration or mascot;
- front-matter page numbers are visible;
- the first lesson number does not include counted front matter;
- the About page repeats the series banner instead of `{Book Name}`;
- global rules override page-specific educational intent;
- an official asset is generated, redrawn or substituted;
- typography is embedded in the AI illustration layer;
- layout regions overlap, duplicate or fall outside safe margins.

Acceptance requires 100/100 QA and zero critical defects.
