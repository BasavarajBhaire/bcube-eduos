# BCube Publishing Standard v1.0 – Gold Edition

**Owner:** BCube Academy – Future Skills Preschool  
**Status:** Founder-approved  
**Version:** 1.0.0  
**Effective date:** 19 July 2026

## 1. Purpose

This standard defines the mandatory requirements for designing, producing, validating, printing, and releasing BCube educational products. It replaces informal terms such as “Book Bible” as the authoritative publishing reference.

## 2. Non-negotiable principles

1. Repository content is the single source of truth.
2. Exact official book, chapter, and page names must come from the repository; memory or invented titles are prohibited.
3. One generated illustration or rendered artifact represents one page only.
4. AI may generate candidate illustrations only; it must not generate or alter the official logo, final typography, page geometry, page numbering, or approved wording.
5. Final pages are assembled from versioned templates and certified assets.
6. Covers do not display interior page numbers.
7. Every page must have one dominant learning purpose and one clear child action.
8. Every released page must be reproducible from a repository commit, manifest, template version, asset versions, and publishing-standard version.
9. Critical defects cause immediate rejection regardless of score.
10. No commercial print run is approved without a physical proof review.

## 3. Brand standard

- Public brand: **BCube Academy**
- Descriptor: **Future Skills Preschool**
- The official logo must be composited from the approved repository asset and must never be redrawn by an image model.
- Logo proportions, colours, clear space, and orientation must remain unchanged.
- Publisher contact details must use the approved source:
  - Address: 407, DSMAX Sky Supreme, KST, Bangalore – 560060
  - Email: info@bcubefutureacademy.in
  - Website: bcubefutureacademy.in

## 4. Educational standard

Every page must:

- be appropriate for its declared age and level;
- express one primary learning objective;
- avoid unnecessary cognitive load;
- use direct, encouraging language;
- include a child action that can be understood quickly;
- support teacher use and, where specified, parent reinforcement;
- avoid invented curriculum content.

The curriculum source in the repository takes precedence over production prompts, generated text, or previous chat discussions.

## 5. Editorial standard

- Use exact page titles and visible wording from the canonical source.
- Keep Nursery instructions short, concrete, and action-led.
- Prefer familiar vocabulary and complete sentences.
- Do not add headings, speech bubbles, captions, slogans, or instructions that are absent from the source.
- Proofread spelling, punctuation, capitalization, numbering, and repeated terminology before release.

## 6. Design standard

All print pages use:

- A4 portrait geometry: 210 × 297 mm;
- 2480 × 3508 pixels at 300 DPI for raster masters;
- generous safe margins and uncluttered white space;
- clear visual hierarchy;
- one dominant focal area;
- reusable, versioned page templates;
- deterministic component placement.

AI must not decide the final layout.

## 7. Illustration standard

Illustrations must be:

- age appropriate, warm, friendly, and easy to recognize;
- visually simple enough for preschool learners;
- consistent with approved character references;
- free from logos, page titles, page numbers, and unrelated text;
- free from watermarks and invented branding;
- suitable for commercial print at the required resolution.

Character identity, proportions, clothing, colours, and recurring features must remain consistent across the series.

## 8. Activity standard

A page should contain one major child activity unless the canonical page explicitly requires otherwise.

Approved activity families include speaking, listening, pointing, circling, matching, tracing, colouring, observing, drawing, sorting, and simple role play.

Activities must be visually obvious, developmentally realistic, and possible with standard classroom or home materials.

## 9. Typography standard

- Final text is rendered by the deterministic publishing pipeline, not generated inside illustrations.
- Font families, sizes, weights, line heights, and alignments are controlled by versioned typography tokens.
- Text must remain inside its assigned region without clipping, excessive shrinking, or overflow.
- Body text and instructions must remain legible in a physical A4 print.

## 10. Colour standard

- Use the approved BCube brand palette and approved supporting preschool palette.
- Maintain sufficient contrast for readability.
- Avoid heavy dark backgrounds, harsh contrast, and excessive saturation on Nursery interiors.
- Validate important colours in a physical print proof before commercial release.

## 11. Asset standard

Every production asset must have:

- an immutable versioned asset ID;
- a repository path;
- SHA-256 checksum;
- lifecycle status;
- approval owner;
- usage and dependency metadata where applicable.

Lifecycle: `DRAFT → REVIEW → GOLD → DEPRECATED → ARCHIVED`.

Only `GOLD` assets may be used in Gold pages. Existing Gold versions must never be overwritten; changes require a new version.

## 12. Quality standard

A page must score at least 95/100 and have no critical defects.

Quality dimensions:

- Educational correctness
- Child comprehension and engagement
- Visual clarity and consistency
- Brand compliance
- Technical and print compliance
- Teacher and parent usability where applicable

Critical rejection conditions include:

- wrong or regenerated logo;
- incorrect title or visible wording;
- invented text or activity;
- multiple pages in one output;
- visible page number on a cover;
- unresolved or non-Gold assets;
- unknown or unversioned template;
- content outside safe or trim boundaries;
- missing required content;
- broken character identity;
- output below required dimensions or DPI.

## 13. Print production standard

Before release, verify:

- final trim size and bleed requirements with the selected printer;
- 300 DPI raster content;
- safe margins and no unintended clipping;
- fonts embedded in PDF outputs;
- correct page order and page-number rules;
- cover, copyright, publisher information, and edition metadata;
- colour and black-level behaviour in a physical proof;
- no missing or substituted images.

Commercial printing requires an approved physical proof.

## 14. Release standard

Every released book must include:

- semantic version and edition information;
- source repository commit;
- BPS version;
- template and asset versions;
- final print PDF;
- QA report;
- release notes;
- approval record;
- archived source package.

A book becomes Gold only when every required page is Gold, book-level QA passes, and the physical proof is approved.

## 15. Change governance

- Editorial corrections may be released as patch versions.
- Compatible improvements may be minor versions.
- Changes affecting layout, brand, pedagogy, or published appearance require a major version and founder approval.
- Published editions remain immutable; corrections create a new release.
