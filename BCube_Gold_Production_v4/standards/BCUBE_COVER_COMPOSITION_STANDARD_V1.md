# BCube Cover Composition Standard™ v1.0

## Scope

This standard applies to every Nursery, LKG, UKG and future BCube book cover. The approved Nursery Communication Champions cover is the visual baseline. No book may use a free-form full-page AI-generated cover.

## Mandatory production pipeline

1. Resolve the exact approved page package and cover contract.
2. Verify the official BCube logo and approved Star master through the locked asset registry.
3. Generate only the book-specific illustration layer. The illustration layer must contain no logo, mascot, title, badge, footer, pillar labels, skill text or other final typography.
4. Compose all brand assets, typography and geometry deterministically.
5. Validate the output against this standard and the golden reference before promotion.
6. Fail closed on any missing asset, unknown template version, layout conflict or critical defect.

## Locked cover geometry

- A4 portrait, 2480 × 3508 px, 300 DPI target.
- Flat, front-facing print page; no mockup, page curl, perspective, device frame or hand-held presentation.
- Official logo: top-left protected zone; exact binary asset; never generated, redrawn, traced, recoloured, cropped, distorted or obscured.
- Series banner: top-centre/right purple banner with gold outline and exact series name.
- Title: dominant two-line hierarchy using the approved Communication Champions proportions, alignment, weight, shadow and two-colour treatment.
- Age badge: premium circular level badge at top-right. Nursery uses the exact wording `NURSERY`, `3+`, `YEARS`; LKG and UKG use their locked level wording.
- Book strapline: one deterministic book-specific strapline below the title.
- Main illustration: one cohesive premium teacher–children learning scene. The teacher facilitates; children respond naturally; Star supports rather than dominates.
- Book skill panel: six book-specific skill capsules aligned vertically beside the main illustration unless a locked book override exists.
- Core-pillar panel: exactly five pillar positions using the portfolio-approved names and order declared by the cover contract. Pillar names, abbreviations and icons are deterministic assets/text.
- Footer: locked purple `BUILD • CREATE • BECOME` band plus deterministic book-specific keyword line.
- No production metadata, filenames, source IDs, QA tables, prompt text or internal instructions on the child-facing cover.

## Asset lock

The following are critical protected assets:

- official BCube logo;
- approved Star mascot master;
- level badge geometry;
- series banner geometry;
- title typography contract;
- five-pillar panel;
- footer system;
- book-specific skill-capsule system.

Similarity is not compliance. An AI-created or manually redrawn approximation is a critical defect even when visually close.

## Illustration standard

- Premium preschool publishing quality with warm light, clean anatomy, inclusive children, natural expressions and purposeful teacher–student interaction.
- The generated illustration must exclude the logo, Star, title, series banner, age badge, skill text, pillar panel and footer.
- Star is composited only from the approved locked master.
- Illustrations must be unique to the book and must not reuse another book cover scene.

## Five-pillar rule

Every cover contract must explicitly declare five main pillars. The composer must use exactly those five labels in the declared order. It may not infer, omit, add or replace a pillar. The approved Communication Champions cover is the structural reference, while each book supplies its approved book-specific pillar set.

## Acceptance gate

A cover is promotable only when all checks pass:

- exact asset hashes resolve;
- illustration layer contains no protected branding or final typography;
- all required text matches the cover contract;
- title, banner, badge, skill panel, pillar panel and footer geometry are within locked tolerances;
- no crop, collision, overflow, duplicate title, generated text or generated protected asset;
- 2480 × 3508 output with 300 DPI metadata;
- visual QA score 100/100;
- zero critical defects.

Any failure blocks page generation and release promotion.