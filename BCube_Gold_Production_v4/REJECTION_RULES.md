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
- Mockup, perspective page, page curl, device frame or hands holding the page.
- Landscape output when portrait is required.

## Branding failures

- AI-generated, recreated, recoloured, stretched, cropped or approximate BCube logo.
- Wrong logo placement or insufficient reserved logo zone.
- Wrong age badge.
- Visible page number on a cover when prohibited.
- Missing required page number on an interior page.

## Content and pedagogy failures

- Invented learning content.
- Multiple unrelated learning goals.
- Empty speech balloons or unexplained blank boxes.
- Worksheet elements on a cover.
- Activity too small for Nursery/LKG/UKG use.
- Excessive writing demand or inaccessible instructions.
- Teacher-child interaction unrelated to the objective.

## Illustration failures

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