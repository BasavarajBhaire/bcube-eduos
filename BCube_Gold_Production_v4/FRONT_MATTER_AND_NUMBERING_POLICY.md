# BCube Portfolio Front Matter and Numbering Policy

Status: FOUNDER APPROVED — MANDATORY FOR ALL LEVELS

Policy version: 1.0.0

Effective date: 2026-07-19

Owner: Basavaraj Bhaire

## Scope

This policy applies consistently to every BCube Gold book in Nursery, LKG and UKG. It replaces the legacy 41-package front-matter arrangement with one common 43-package architecture.

It changes front matter, contents pagination and printed numbering only. Existing book names, learning modules, curriculum sequence, learning objectives and learning-page content remain unchanged.

## Locked 43-package architecture

| Production position | Required page | Counted reader page | Printed number |
|---:|---|---:|---:|
| P001 | Front Cover | Not counted | Hidden |
| P002 | About This Book | 1 | Hidden |
| P003 | Copyright & Publication Details | 2 | Hidden |
| P004 | Contents — Part 1 | 3 | Hidden |
| P005 | Contents — Part 2 | 4 | Hidden |
| P006 | Welcome to `<Book Title>` | 5 | **5** |
| P007 | First page after Welcome | 6 | **6** |
| P008–P043 | Remaining canonical pages in their existing order | 7–42 | **7–42** |

Rules:

- The cover is neither counted nor visibly numbered.
- About This Book, Copyright and both Contents pages are counted internally as pages 1–4 but show no printed number.
- The first visible printed number is 5 on the Welcome page.
- Every page after Welcome shows its reader-facing number sequentially.
- Production prompt IDs remain physical-package identifiers and are not the same as printed page numbers.

## Contents policy

Contents occupies two individual A4 pages: P004 and P005.

The Contents must:

- use approved module headings from the release package;
- list reader-facing pages module-wise;
- begin with `Welcome to <Book Title> — 5`;
- continue through the final reader page 42;
- exclude Front Cover, About This Book, Copyright, Contents Part 1 and Contents Part 2;
- never list prompt IDs, source filenames, internal page types or production terminology;
- never invent, rename, merge or split curriculum modules;
- remain legible at final A4 print size without compressed microtext.

For the 2480 × 3508 px validation build, Contents typography must use at least:

- 46 px bold module headings;
- 44 px page-entry text;
- 44 px bold page numbers;
- 92 px minimum row advance.

Equivalent physical sizes must be preserved in print/PDF workflows. Smaller
Contents typography is a legibility defect.

## About This Book policy

P002 is a new controlled front-matter page for every book.

It must contain:

- the exact book title and level;
- a concise parent/teacher-facing explanation of the book purpose;
- the approved BCube learning approach;
- a brief explanation of how teacher, parent and child use the book together;
- no scored child activity;
- no marketing claims, accreditation claims or invented curriculum outcomes.

Book-specific wording must be derived from that book's canonical objectives and modules.

## Migration mapping from legacy 41-package releases

| Legacy position | New position | Action |
|---:|---:|---|
| P001 Cover | P001 | Preserve; printed number remains hidden |
| — | P002 | Add About This Book |
| P002 Copyright | P003 | Move unchanged except approved metadata corrections |
| P003 Contents | P004–P005 | Replace with two module-wise Contents pages |
| P004 Welcome | P006 | Preserve content; printed page number becomes 5 |
| P005–P041 | P007–P043 | Preserve order and content; shift production ID by +2 and printed number by +1 |

## Portfolio totals after migration

- Nursery: 10 books × 43 packages = 430
- LKG: 10 books × 43 packages = 430
- UKG: 10 books × 43 packages = 430
- Total: 30 books / 1,290 individual page packages

## Enforcement

- No commercial artwork run may mix the legacy 41-page structure with the new 43-package structure.
- A book becomes v4 front-matter ready only after its README, manifest, Markdown, JSON, source spreadsheet, validation report and page-job records all agree.
- Existing 41-page releases remain curriculum sources during migration but are blocked from final v4 book assembly.
- Any exception requires an explicit Founder-approved repository update.
