# BCube Automatic Rejection Rules

Status: MANDATORY

A page must be rejected immediately when any rule below is triggered. Do not continue scoring a critically failed page as acceptable.

## Identity failures

- Wrong book name, level, prompt ID, page number, title or canonical sequence.
- Markdown and JSON identity mismatch.
- Missing required visible wording.
- Added wording not present in the canonical page package.
- Missing, changed or invented activity, teacher move, parent extension or response space.

## Output-form failures

- More than one page appears in the generated image.
- Collage, contact sheet, preview board, book overview, storyboard or composite output.
- Contact sheet, montage, collage, grid, overview or composite presented, linked,
  attached or packaged as a validation deliverable.
- Requested page range delivered as one combined image instead of one individual
  file per logical page.
- Deliverable ZIP or output directory contains a non-page QA composite.
- Corrected artifact is redelivered with a previously shared filename or link,
  allowing a stale cached file to be served.
- Corrected ZIP is not extracted and hash-verified against corrected source pages
  before handoff.
- Mockup, perspective page, page curl, device frame or hands holding the page.
- Landscape output when portrait is required.

## Branding failures

- AI-generated, recreated, recoloured, stretched, cropped or approximate BCube logo.
- Wrong logo placement or insufficient reserved logo zone.
- Wrong age badge.
- Visible page number on a cover when prohibited.
- Missing required page number on an interior page.
- Legacy 41-package or mixed 41/43 structure used for final assembly.
- Missing About This Book page.
- Single-page Contents when the two-page policy applies.
- Contents lists Cover, About This Book, Copyright or either Contents page.
- Contents is not grouped by canonical modules.
- Visible number on P002, P003, P004 or P005.
- Welcome does not show printed page number 5.

## Content and pedagogy failures

- Invented learning content.
- Multiple unrelated learning goals.
- Empty speech balloons or unexplained blank boxes.
- Worksheet elements on a cover.
- Activity too small for Nursery/LKG/UKG use.
- Excessive writing demand or inaccessible instructions.
- Teacher-child interaction unrelated to the objective.

## Illustration failures

- A letter, initial, word label, coloured oval, generic icon or empty frame is used
  in place of the required illustrated person, object, animal, food, action or scene.
- The page instruction names visual choices that are not visibly illustrated.
- Illustration cards contain only text or alphabetic placeholders.
- The illustration is generic and does not demonstrate the exact learning action.
- A required visual element from the canonical scene specification is missing.
- The page has no completed semantic illustration-evidence record or has not passed
  the illustration-content review gate.
- Wrong Star identity.
- Inconsistent teacher or child style that breaks continuity.
- Anatomy errors, uncanny faces or cropped key body parts.
- Frightening, unsafe, stereotyped or shaming imagery.
- Decorative clutter that competes with the learning focus.
- Hero illustration too small to establish a clear focal point.

## Print failures

- Text too small to read at A4.
- Content outside safe margins.
- Clipped text or cropped key objects.
- Poor contrast.
- Tracing path too small for preschool pencil control.
- Colouring regions too tiny or visually fragmented.
- Resolution or composition unsuitable for 300 DPI print production.

## Decision

Any triggered rule sets:

- `critical_defect_count >= 1`
- `approval_status = REJECTED`
- `next_action = REGENERATE`

No manual override is allowed unless the Founder explicitly updates the repository specification.
