# BCube Global Page Production Lock™

Status: **MANDATORY — FAIL CLOSED**

Applies to: **Nursery, LKG and UKG; every book, cover, front-matter page, learning page, certificate and back cover.**

Approved baseline: the finalized **Communication Champions** production method and the V4 prompt architecture already merged into this repository.

## 1. Purpose

This policy prevents book-by-book drift and permanently blocks the failure mode where an image model invents the BCube logo, redraws Star, generates page typography, creates a poster instead of a workbook page, changes the approved hierarchy, or ignores the page-specific teaching design.

Every future BCube page must inherit this policy automatically. A page-specific prompt may add requirements, but it may never weaken or override this lock.

## 2. Mandatory production pipeline

A final page is a composed publishing artifact, not a single free-form AI image.

1. Read the exact finalized V4 Markdown/JSON package for the physical page.
2. Resolve the approved page template for its type: cover, front matter, learning/activity, reflection, certificate or back cover.
3. Load the official BCube logo from the approved asset registry.
4. Load the approved Star master from the approved asset registry when required.
5. Generate or source only the illustration layer required by the page prompt.
6. Compose title, instructions, model phrase, activity frames, response areas, teacher guidance, parent partnership, badges, footer and page number as deterministic editable layout elements.
7. Validate the composed page against the release manifest and this global lock.
8. Export exactly one flat, front-facing print page.

The illustration model must never be asked to generate the entire final page with branding and typography embedded in the artwork.

## 3. Locked assets

### Official BCube logo

- Use only the approved official BCube logo asset.
- Never generate, redraw, reinterpret, approximate, recolour, crop, distort, simplify, cover or replace it.
- Never use a textual substitute such as “BCube”, “A BCube LLP Brand”, or an invented cube mark.
- The logo must be placed by deterministic composition after illustration generation.
- Missing official logo asset means **STOP — DO NOT GENERATE THE FINAL PAGE**.

### Approved Star mascot

- Use only the approved Star master asset where the page package requires Star.
- Never generate a new star character, substitute a generic star, alter the face, change the point count, clothing, shoes, cape, colours or proportions.
- Star must be composited as a controlled asset unless an explicitly approved master-derived pose exists.
- Missing approved Star asset means **STOP — DO NOT GENERATE THE FINAL PAGE**.

## 4. Typography and wording lock

- All visible text must come from the exact finalized page package.
- Titles, instructions, model phrases, teacher prompts, parent prompts, labels, badges, page numbers and footer text must be deterministic editable text layers.
- Never allow an image model to render final page text.
- Never paraphrase, shorten, expand, translate or invent visible wording unless the source package explicitly permits it.
- No spelling errors, duplicated titles, broken words, pseudo-text or unreadable labels.

## 5. Layout and publishing lock

- A4 portrait, 210 × 297 mm, 2480 × 3508 px target, 300 DPI.
- 3 mm bleed, minimum 10 mm safe margin and 12 mm binding margin unless a stricter page rule applies.
- Flat, front-facing, print-ready composition only.
- No mockup, book perspective, page curl, device frame, hands holding the page, contact sheet, collage or multiple pages.
- Preserve the approved BCube title hierarchy, visual balance, activity frames, protected response areas, teacher–student interaction and parent partnership system.
- Covers must follow the approved BCube cover architecture; interior pages must follow the approved interior-page architecture.
- Do not convert an educational workbook page into a poster, infographic, prompt sheet, metadata sheet or production-specification page.
- Production metadata, source IDs, QA tables, prohibited-element lists and internal compiler notes must never appear on the child-facing final page.

## 6. Illustration-layer rules

The illustration layer may contain only the visual scene, objects and characters required by the exact page prompt.

- No logo, title, instruction, badge, page number, footer, speech text or activity text inside the generated illustration.
- Speech/thought balloons may be illustrated only as empty controlled shapes when the layout template requires later text composition; decorative empty balloons are prohibited.
- Maintain the age-level visual ratio and complexity defined by the finalized prompt.
- Preserve natural expressions, correct anatomy, inclusive representation, clear actions and unobstructed response areas.
- Never reuse another book’s cover scene or learning illustration.

## 7. Communication Champions baseline

The approved Communication Champions method is the global reference for:

- one physical page per output;
- exact page-specific prompt execution;
- official-logo and approved-Star asset placement;
- deterministic title, instruction and page-number composition;
- teacher–student pedagogy visibly connected to the objective;
- parent partnership where specified;
- protected child response space;
- clean premium preschool publishing hierarchy;
- no generated typography and no invented branding.

Other books must inherit the method, not copy Communication Champions content or illustrations.

## 8. Page-type requirements

### Cover

- Official logo and approved series identity are deterministic assets/text.
- Exact book title and level badge only.
- Unique book-specific scene.
- No interior activity panels, teacher notes, source metadata, QA tables or printed page number.

### Front matter

- Use the approved BCube front-matter template.
- Child/teacher/parent-facing content only.
- Internal production metadata stays outside the final artwork.

### Learning/activity pages

- Exact title and printed page number.
- Maximum activity load defined by level and page prompt.
- Visible teacher–student interaction only when required by the page package.
- Protected child response region must remain usable after composition.

### Certificate/reflection

- Preserve exact achievement wording, child-name/date/signature fields and celebratory hierarchy.
- Do not invent awards, scores or claims.

### Back cover

- Exactly one true back cover per physical book.
- No printed page number.
- Follow the approved back-cover publishing template and official publisher details.

## 9. Global fail-closed acceptance gate

Reject the page and do not mark it complete when any item below occurs:

- official logo missing, invented or altered;
- Star missing, invented or altered when required;
- generated or corrupted typography;
- wrong title, wording, physical page or printed page;
- poster/infographic/specification-sheet appearance instead of final workbook page;
- internal metadata visible on the child-facing page;
- wrong template or page type;
- missing teacher, parent, activity or response component required by the prompt;
- cropped content, unsafe margins, overlap or unusable response area;
- reused illustration from another page/book;
- multiple pages or a mockup in one output;
- any unresolved asset reference or placeholder.

Acceptance requires **100/100**, **zero critical defects**, exact manifest identity and confirmed use of official controlled assets.

## 10. Mandatory execution declaration

Before generating any page, the production process must resolve and record:

- book, level, prompt ID, physical page and printed page;
- page type and exact title;
- V4 source package path;
- template ID;
- official logo asset ID and checksum;
- approved Star asset ID and checksum when required;
- illustration-only generation brief;
- deterministic text/layout composition plan;
- output path and QA result.

If any mandatory value is unresolved, generation must stop.

## 11. Scope of enforcement

This lock applies globally to:

- all existing finalized Nursery, LKG and UKG V4 prompts;
- all future books and levels;
- all manual, Canva, Figma, Illustrator, InDesign, Python, image-model or automated production workflows;
- all regenerated, corrected and replacement pages.

No book may opt out. No page-specific prompt may authorize invented branding, generated typography or free-form full-page generation.