# Gold Nursery Production Program

**Status:** Active  
**Primary objective:** Produce commercially printable Nursery books from canonical repository sources.

## Production rule

The repository is authoritative for official book names, page counts, page identities, learning objectives, visible wording, and production order. No title or page content may be guessed from memory.

## Active reference book

`Communication Champions` is the current reference production book. It is not considered complete until every required page is individually composed, validated, assembled into a print PDF, and approved through a physical proof.

## Required production stages

1. **Source lock** — confirm the canonical book and page source at a specific commit.
2. **Page contract** — validate page identity, type, learning purpose, wording, activity, template, and assets.
3. **Illustration candidate** — create artwork only, with no logo, final typography, page number, watermark, or invented text.
4. **Asset certification** — approve, version, checksum, and promote the selected illustration to Gold.
5. **Deterministic composition** — assemble official logo, text, illustration, activity, and footer through the locked template.
6. **Page QA** — apply BPS educational, visual, brand, technical, and publishing gates.
7. **Book QA** — verify sequence, consistency, metadata, copyright, publisher details, and complete PDF.
8. **Physical proof** — inspect colour, readability, margins, trimming, binding, and classroom usability.
9. **Gold release** — archive sources, reports, certificates, and the approved print package.

## Page definition of done

A page is complete only when:

- its exact canonical source is recorded;
- one flat A4 portrait page is produced;
- the official logo is used as an immutable asset;
- all visible wording is exact;
- no critical acceptance condition fails;
- the QA score is at least 95/100;
- the final output and its dependencies are versioned and reproducible.

## Book definition of done

A Nursery book is print ready only when:

- every required page is Gold;
- page order and numbering are correct;
- the cover, copyright, publisher identity, and edition metadata are approved;
- the print PDF passes technical preflight;
- a physical proof has been reviewed and approved;
- the release is tied to a repository commit and archived.

## Current blockers for commercial printing

- The official logo must have a verified SHA-256 and Gold asset status.
- Required recurring characters and illustrations must be certified.
- Deterministic PNG and PDF rendering must be operational end to end.
- Every book page must be composed and pass BPS QA.
- The assembled book must pass physical proof review.

## Progress metrics

Track only measurable production outcomes:

- Gold assets
- Gold pages
- Gold books
- QA pass rate
- unresolved critical defects
- print proofs approved

Architecture or documentation completion does not make a book printable.
