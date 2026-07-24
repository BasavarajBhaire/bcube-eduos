# BCube Design Constitution™ v1.0

Status: **Canonical and binding**

This constitution is the single source of truth for BCube book design, composition, asset usage, validation, approval and publication. V4 remains the approved content specification. V5 and later engines must implement this constitution and may not weaken it.

## 1. Precedence

1. Approved page-specific instruction.
2. Approved page-type contract.
3. This constitution.
4. Book metadata and design tokens.
5. Illustration prompt.

A lower-precedence source may never override a higher-precedence rule.

## 2. Production architecture

AI may create only the illustration layer. The publishing engine must deterministically compose all branding, typography, badges, titles, ribbons, icons, panels, pillars, footer, page number and publisher information.

Raw AI output is never a production page. The required lifecycle is:

`Prompt → Illustration Candidate → Illustration QA → Deterministic Composition → Render QA → Human Approval → Approved Artifact`

## 3. Canvas and print standard

- A4 portrait.
- 2480 × 3508 pixels.
- 300 DPI.
- 3 mm bleed where the print package requires bleed.
- All critical content inside the safe area.
- One physical page equals one flat output image.
- No mock-up perspective, contact sheet, composite preview or watermark.

## 4. Official assets

- The official BCube logo must be loaded from the approved asset registry.
- The official Star mascot must be loaded from the approved asset registry or extracted through a validated, locked crop from an approved source asset.
- AI must not redraw, reinterpret or approximate the logo or Star.
- Required skill and pillar icons must be repository-controlled assets or deterministic engine vectors.
- Missing, invalid or unregistered required assets cause a fail-closed rejection.
- Asset paths and SHA-256 hashes must be recorded in render evidence.

## 5. Cover contract

Every Nursery cover must contain:

- official BCube logo;
- `BCube Future Skills Learning Series™` banner;
- Nursery `3+ YEARS` badge;
- approved two-line book-title convention and locked colour treatment;
- approved book tagline;
- one clean illustration frame;
- exactly six book-specific skill capsules;
- exactly five core pillars: Creativity, Communication, Curiosity, Confidence and Collaboration;
- locked `BUILD • CREATE • BECOME` footer;
- book-specific footer keywords.

The cover must not contain a printed page number.

## 6. Front-matter rules

- About This Book, Publisher/Copyright and Contents pages do not display a printed page number.
- Internal counting starts at About This Book.
- The first learning page displays the correct internal number after all front-matter pages.
- Publisher/Copyright pages contain no illustration and no mascot.
- About pages use the complete book title on one colour-segmented line in the header, not the generic series banner.
- About pages retain the locked illustration frame and fit the visible artwork inside it after trimming empty white source canvas; stretching and subject cropping are prohibited.
- Contents pages show the book title, module names and all learning-page titles.
- Contents pages do not show the age badge, sticky notes, teacher panels, parent panels or decorative callouts.

## 7. Illustration-layer rules

Illustrations must contain no:

- visible words, letters or numbers;
- logo, watermark or publisher branding;
- mascot or Star character;
- badge, banner, ribbon, footer or page number;
- skill capsules, pillar icons or page-layout fragments;
- embedded workbook thumbnails or foreign graphics.

Illustration placement must preserve aspect ratio, use safe-contain geometry, avoid cropping faces or limbs, and meet the template occupancy target without overflowing the frame.

## 8. Typography, colour and geometry

- Book-title line colours, type hierarchy, series banner, badge, tagline, frame, skill panel, pillar panel and footer geometry are locked by the page template.
- Unsupported font glyphs are prohibited; decorative stars must be deterministic vectors when font support is uncertain.
- No component may move outside the template tolerance.
- No hidden, clipped or overlapping label is allowed.
- No duplicated mascot or duplicated component is allowed.

## 9. Content isolation

Each book has required and prohibited visible terms. Cross-book content is a critical defect. For example, a Confidence Builders page must reject Communication Champions identity text or communication-specific wall slogans.

## 10. QA and approval

A production page requires both:

1. Machine QA: PASS with zero critical defects.
2. Human approval bound to the exact final artifact SHA-256.

Machine QA must independently verify dimensions, DPI, asset hashes, component counts, geometry, overlap, required text, prohibited text, illustration cleanliness and template conformance. Self-declared boolean claims are insufficient evidence.

A candidate remains under `production-renders/v5/candidates`. Only an explicitly approved, hash-bound artifact may be promoted to `production-renders/v5/approved`.

## 11. Permanent-learning rule

When a defect is identified once, the corresponding prevention must be encoded in the engine, template, registry or validator before large-scale generation continues. Repeated manual correction of the same defect is not acceptable.

## 12. Change control

Any change to this constitution requires:

- a version increment;
- a pull request;
- passing repository, SDK and V5 validation;
- documented migration impact;
- no silent weakening of existing fail-closed rules.

All BCube Nursery, LKG, UKG and future publishing systems inherit this constitution unless a stricter approved level-specific contract applies.
