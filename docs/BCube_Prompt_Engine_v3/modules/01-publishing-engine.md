---
title: "Phase 1 - Publishing Engine"
product: "BCube Prompt Engine v3.0"
edition: "Founder Edition"
version: "3.0.0"
status: "Active"
phase: "1"
owner: "BCube Future Academy"
last_updated: "2026-07-15"
source_documents:
  - BCube_Prompt_Engine_v3_Phase_1_Publishing_Engine_FINAL.docx
  - BCube_Prompt_Engine_v3_Complete_Production_Standard_Master_Part_2.docx
  - BCube_Prompt_Engine_v3_Complete_Production_Standard_Master_Part_3.docx
---

# Phase 1 - Publishing Engine

> Normative status: This module is part of the BCube Prompt Engine v3.0 Complete Production Standard. `MUST`, `SHALL`, `SHOULD`, `MAY`, and `MUST NOT` carry their formal specification meanings.

BCube Prompt Engine™ v3.0

Phase 1 — Publishing Engine™

Final Production Specification • Founder Edition • Version 3.0

The authoritative publishing and print-production rules used by the BCube Prompt Engine™ to compile consistent, child-friendly, premium, print-ready workbook page prompts.

## Document Control

| Field | Value |
| --- | --- |
| Document | BCube Prompt Engine™ v3.0 — Publishing Engine™ |
| Document ID | BCPE-V3-PH1-PE |
| Status | FINAL |
| Owner | BCube Future Academy |
| Applies To | Nursery, LKG, UKG, Grade 1+ publishing prompts |
| Review Cycle | Annual or upon major production-system change |
| Change Control | BCube EduOS™ governance and semantic versioning |

## 1. Purpose and Scope

The Publishing Engine™ is the first mandatory engine in the BCube Prompt Engine™ v3.0 compilation sequence. It converts broad creative intent into a precise publishing specification. Its purpose is to ensure that every generated page is physically producible, visually legible, developmentally appropriate, brand-consistent, and safe for commercial printing.

- Applies to covers, front matter, activity pages, review pages, certificates, teacher guidance pages and back covers.

- Controls page geometry, trim safety, bleed, live area, visual-to-text ratio, typography zones, print colour, image resolution and export readiness.

- Provides machine-readable rules that downstream Design, Visual Grammar, Illustration and QA engines inherit.

- Prevents common failures such as cropped content, tiny text, crowded activity zones, inconsistent page numbering, low-resolution artwork and incorrect logo placement.

## 2. Engine Position in the Compilation Pipeline

The Publishing Engine™ runs before all other visual engines because page geometry and production limits constrain every later decision.

| Stage | Engine | Primary Output |
| --- | --- | --- |
| 1 | Publishing Engine™ | Physical page and print specification |
| 2 | Design Engine™ | Layout hierarchy and component placement |
| 3 | Visual Grammar Engine™ | Focal point, eye flow and visual rhythm |
| 4 | Educational Engine™ | Learning objective and evidence |
| 5 | Teaching Engine™ | Teacher-child interaction |
| 6 | Parent Partnership Engine™ | Home extension |
| 7 | Illustration Engine™ | Scene execution |
| 8 | Character Engine™ | Character consistency |
| 9 | Quality Assurance Engine™ | Validation and scoring |
| 10 | Prompt Compiler™ | Final production prompt |

## 3. Mandatory Page Geometry

Unless a product brief explicitly authorizes another format, all standard BCube workbook pages use A4 portrait geometry.

| Parameter | Standard | Tolerance | Rule |
| --- | --- | --- | --- |
| Trim size | 210 × 297 mm | ±0.5 mm | Final printed page size |
| Orientation | Portrait | None | Landscape requires product-level approval |
| Bleed | 3 mm minimum | 3–5 mm | Background artwork extends through bleed |
| Safe margin | 10 mm | Minimum 8 mm | No essential text or faces outside this zone |
| Binding margin | 12 mm inside edge | 12–15 mm | Increase for perfect binding |
| Footer zone | 10–14 mm | Fixed | Page number and optional footer only |
| Header zone | 20–28 mm | By template | Logo and page title hierarchy |

## 4. Live Area and Content Zones

The live area is the region within which all essential learning content must remain. Each page is divided into zones so the Prompt Compiler™ can describe location and priority consistently.

| Zone | Purpose | Constraint |
| --- | --- | --- |
| Z01 — Brand Header | Top-left logo, series identity, page title | Never obstruct the page title or activity |
| Z02 — Learning Focus | Objective, target vocabulary or brief instruction | Maximum 15% of page area |
| Z03 — Main Illustration | Primary teacher-child learning scene | Usually 45–60% of page area |
| Z04 — Child Activity | Tracing, matching, colouring, speaking or response space | Must be physically usable |
| Z05 — Teacher Support | Teacher prompt or facilitation cue | Compact and visually distinct |
| Z06 — Parent Extension | Optional home connection | Small, non-dominant support box |
| Z07 — Footer | Page number, encouragement, rights text where required | Never carry core instruction |

## 5. Visual-to-Text Ratio by Level

| Level | Visual | Text | Production Interpretation |
| --- | --- | --- | --- |
| Nursery (3+) | 70–80% | 20–30% | Large objects, few instructions, strong white space |
| LKG (4+) | 60–70% | 30–40% | Richer scenes, short guided prompts |
| UKG (5+) | 55–65% | 35–45% | More structured activities and readiness cues |
| Grade 1+ | 45–60% | 40–55% | Greater text density while retaining child-friendly hierarchy |

## 6. Typography Production Rules

- Use highly legible rounded sans-serif typefaces approved by BCube brand governance.

- Never place body text directly over detailed artwork.

- Maintain strong hierarchy between page title, activity instruction, teacher guidance and parent extension.

- Avoid all-caps body instructions; reserve capitals for very short labels only.

- Minimum effective print size: 14 pt for Nursery child-facing text, 12 pt for LKG, 11 pt for UKG, unless tested and approved.

- Teacher and parent guidance may be smaller but must remain comfortably readable in print.

- Line spacing must prevent crowding; default 1.15–1.3 depending on typeface.

- Limit child instructions to one action per sentence whenever possible.

| Element | Recommended Size | Weight | Maximum Length |
| --- | --- | --- | --- |
| Page title | 24–34 pt | Bold | 1–6 words |
| Learning objective | 11–14 pt | Medium | 18 words |
| Child instruction | 14–20 pt | Semibold | 12 words per instruction |
| Teacher prompt | 10–12 pt | Regular | 30 words |
| Parent extension | 9.5–11 pt | Regular | 35 words |
| Page number | 9–11 pt | Regular | Numeric |

## 7. Image and Illustration Resolution

- Raster artwork must be at least 300 pixels per inch at final placed size.

- Logos, simple icons and line art should use vector formats where possible.

- Do not upscale low-resolution images as a substitute for native-quality generation.

- Avoid compression artefacts, jagged outlines, muddy gradients and low-quality shadows.

- Every final illustration must preserve clean edges around characters, activity objects and text-safe zones.

- Generated images must not contain embedded unintended text, signatures, watermarks or unrelated logos.

## 8. Colour and Print Behaviour

- Design for reliable CMYK reproduction while keeping digital source files in a managed colour workflow.

- Use white or very light pastel page backgrounds for interior pages unless a special spread is approved.

- Avoid large areas of dense black or heavily saturated colour that increase ink load and reduce child readability.

- Maintain sufficient contrast between text and background.

- Do not depend on colour alone to communicate correct/incorrect, match groups or sequence.

- Test pale yellows, light blues and light greens for print visibility; subtle digital colours may disappear in print.

- Keep skin tones natural, diverse and consistent across pages.

## 9. White Space and Density Rules

White space is a learning aid. It separates instructions, reduces cognitive load and preserves a premium publishing appearance.

- Maintain visible breathing room around the page title, main scene and response area.

- Do not fill empty areas with decorative stars, balloons or icons unless they serve a learning purpose.

- Keep at least 6 mm between unrelated text boxes or visual components.

- Keep at least 8 mm around child writing, tracing or colouring spaces.

- A page must have one dominant learning focus; secondary decorative content may not compete for attention.

- Avoid more than three major content zones on Nursery activity pages unless the activity itself requires sequencing.

## 10. Cover Publishing Rules

- The cover must communicate subject, age level, series identity and emotional promise within three seconds.

- Official BCube logo placement follows current brand standards and remains clear of trim and character overlap.

- Age badge appears on the cover only unless a product brief states otherwise.

- Main title must remain readable at thumbnail size.

- Star mascot has a purposeful role related to the book theme rather than appearing as unrelated decoration.

- Do not overload the cover with more than one primary scene and three secondary learning cues.

- Spine and back cover are planned as part of the same production file.

## 11. Interior Brand Placement

- Official BCube logo appears in the approved header position on standard interior pages.

- Do not stretch, recolour, redraw or simplify the logo.

- Keep the logo visually subordinate to the page title and learning activity.

- Do not place the Nursery/LKG/UKG badge on standard interior activity pages.

- Page number appears consistently in the approved footer position.

- Series name, trademark and copyright wording must use approved phrasing.

## 12. Activity-Space Production Rules

- Tracing paths must be thick enough for the target age and leave room for imperfect pencil control.

- Colouring areas must be large, clearly enclosed and not broken by unnecessary fine detail.

- Matching activities must have unambiguous targets and sufficient line-drawing space.

- Cut-and-paste activities must show clear cut lines and safe adult-supervision cues where applicable.

- Writing areas must match the age level and expected response length.

- Do not let character hands, props, speech bubbles or decorative borders block the child response area.

## 13. Front Matter and Back Matter Rules

| Page Type | Mandatory Purpose |
| --- | --- |
| Cover | Subject identity, level, logo, series, compelling visual |
| Copyright | Publisher, rights, edition, printing and legal details |
| Contents | Accurate page titles and page numbers |
| Welcome | Teacher/child orientation and book promise |
| Meet Star | Mascot role and tone |
| Review Pages | Mixed evidence, not decorative recap |
| Certificate | Child name, teacher signature, date, official branding |
| Back Cover | Series message, publisher identity, optional product summary |

## 14. Accessibility and Inclusive Publishing

- Use clear layouts that can be understood even when a child cannot read every word.

- Avoid relying only on red/green colour distinctions.

- Keep instructions literal, concise and supported by visuals.

- Provide strong figure-ground separation between important objects and backgrounds.

- Represent diverse children without tokenism or stereotyping.

- Show adaptive participation naturally when relevant.

- Avoid tiny labels, dense text blocks and decorative scripts.

## 15. Production Rules for AI-Generated Artwork

- The prompt must explicitly reserve title, instruction and activity zones.

- AI-generated artwork must not render final instructional text unless the workflow supports controlled typography.

- All text should normally be added in the page-layout stage rather than inside the illustration.

- The prompt must prohibit watermarks, signatures, random labels and gibberish.

- The prompt must state the final page orientation, focal point, safe margins and activity-space requirements.

- Artwork is rejected if essential faces, hands, learning objects or activity areas are cropped.

- Artwork must be editable or composable enough to support final publishing layout.

## 16. Mandatory Negative Production Rules

- No watermarks, stock marks, signatures or unrelated logos.

- No dark full-page backgrounds for standard preschool interiors.

- No photorealistic children in the standard workbook illustration system.

- No distorted anatomy, extra fingers, missing limbs or cropped faces.

- No unsafe classroom setups, hazardous materials or unsupervised risky actions.

- No illegible text, gibberish, fake UI, random symbols or meaningless labels.

- No overcrowded layouts, tiny activity elements or decorative clutter.

- No important content outside the safe area.

## 17. Publishing Engine Input Schema

| Field | Required | Example | Validation |
| --- | --- | --- | --- |
| product_level | Yes | Nursery 3+ | Must match approved level list |
| page_type | Yes | Activity | Must match template category |
| page_number | Yes | 12 | Integer and sequence-valid |
| page_title | Yes | My Family | Exact approved title |
| orientation | Yes | A4 portrait | Must match product brief |
| visual_text_ratio | Yes | 75:25 | Within level range |
| activity_space | Conditional | Large colouring area | Required for response pages |
| logo_position | Yes | Top left | Approved brand position |
| footer_number | Yes | Bottom right | Consistent with template |

## 18. Publishing Engine Output Block

The Publishing Engine™ emits a structured block that the Prompt Compiler™ inserts at the beginning of every final production prompt.

TECHNICAL AND PUBLISHING SPECIFICATION: Create an A4 portrait educational workbook page, 210 × 297 mm trim size, with 3 mm bleed, 300 DPI print resolution, clean white or approved pastel background, 10 mm safe margins, 12 mm inside binding margin, clear title zone, protected activity response area, official BCube logo in the approved header position, and page number in the approved footer position. Keep all essential text, faces, hands, learning objects and activity spaces inside the live area. Maintain the level-specific visual-to-text ratio, strong print contrast, uncluttered white space and commercial publishing quality.

## 19. Publishing Validation Checklist

☐ Correct trim size and orientation

☐ Bleed included where background reaches trim

☐ All essential content inside safe margins

☐ Binding margin protected

☐ Logo correctly positioned and unobstructed

☐ Title clearly readable

☐ Page number correctly positioned

☐ Visual-to-text ratio appropriate for level

☐ Child response area physically usable

☐ Typography large enough for print

☐ Illustration resolution suitable for final size

☐ Colour and contrast print-safe

☐ No embedded gibberish or unintended text

☐ No cropped faces, hands or learning objects

☐ No prohibited watermarks or unrelated logos

## 20. Gold Publishing Score

| Category | Weight | Minimum Passing Score |
| --- | --- | --- |
| Geometry and trim safety | 20% | 18/20 |
| Readability and typography | 15% | 13/15 |
| Activity usability | 20% | 18/20 |
| Visual density and white space | 15% | 13/15 |
| Brand placement | 10% | 9/10 |
| Print and colour readiness | 10% | 9/10 |
| Accessibility | 10% | 9/10 |

Passing rule: minimum total score 90/100, with no critical failure in trim safety, activity usability, logo integrity, accessibility or print resolution.

## 21. Compiler Rules

- The Publishing Engine block must appear before educational and illustration instructions.

- Page-specific geometry may override defaults only when an approved template ID is supplied.

- Conflicting downstream instructions are ignored when they violate safe margins, print resolution or brand placement.

- The Compiler must carry forward the exact page title and number from the page data schema.

- The final prompt must preserve a protected response area when the activity requires child output.

- The Publishing Engine version must be logged in the final prompt metadata.

## 22. Versioning and Change Control

- Major version: structural change to page geometry or production rules.

- Minor version: new template category, colour policy or layout capability.

- Patch version: clarification, correction or non-breaking validation update.

- Every release includes change summary, effective date, owner, affected products and migration guidance.

- Books already in production remain pinned to their approved engine version unless formally migrated.

## 23. Final Acceptance Criteria

Phase 1 is complete when the Publishing Engine™ can generate a consistent publishing specification for any approved BCube page type and every compiled prompt can be validated against the geometry, readability, activity, brand, accessibility and print-readiness rules in this document.

## 24. Phase 1 Deliverables

- Publishing Engine™ final specification

- A4 page geometry standard

- Live-area and zone definitions

- Typography production rules

- Visual-to-text ratios by level

- Cover and interior branding rules

- Activity-space standards

- AI artwork production constraints

- Publishing input schema

- Compiler-ready output block

- Validation checklist and Gold Publishing Score

- Version and change-control policy

## Approval Statement

This document is adopted as the authoritative Phase 1 specification for BCube Prompt Engine™ v3.0. All future BCube Gold Production Prompts™ must inherit and comply with these publishing rules before illustration generation.


---

## Normative expansion from `BCube_Prompt_Engine_v3_Complete_Production_Standard_Master_Part_2.docx`

## Introduction

Part II begins the detailed rulebook for the Publishing Engine™. Each rule follows a normative structure with identifiers, requirements, rationale, validation, and compiler impact.

### PE-GEO-001

Requirement: Every standard workbook page SHALL use the approved page geometry.

Rationale: Uniform production and printing.

Validation: Check page size, orientation and bleed.

Compiler Impact: Publishing block generated.

### PE-GEO-002

Requirement: Essential content MUST remain inside the safe area.

Rationale: Prevents trim loss.

Validation: Measure all critical elements against safe margin.

Compiler Impact: Safe-area flag.

### PE-LAY-001

Requirement: Pages SHALL reserve protected zones for title, activity and footer.

Rationale: Supports consistent layouts.

Validation: Template compliance review.

Compiler Impact: Layout metadata.

### PE-TYP-001

Requirement: Child-facing typography MUST meet minimum readability standards.

Rationale: Supports early readers.

Validation: Font size and contrast validation.

Compiler Impact: Typography block.

### PE-CLR-001

Requirement: Interior pages SHOULD use light backgrounds with accessible contrast.

Rationale: Improves readability.

Validation: Contrast review.

Compiler Impact: Colour profile.

### PE-IMG-001

Requirement: Illustrations MUST be suitable for 300 DPI print reproduction.

Rationale: Commercial print quality.

Validation: Resolution validation.

Compiler Impact: Image compliance.

### PE-BRD-001

Requirement: Official BCube branding SHALL follow approved placement rules.

Rationale: Brand consistency.

Validation: Header inspection.

Compiler Impact: Brand metadata.

### PE-ACT-001

Requirement: Activity spaces MUST remain unobstructed.

Rationale: Supports child interaction.

Validation: Activity-zone validation.

Compiler Impact: Activity metadata.

### PE-EXP-001

Requirement: Final output SHALL support PDF/X export workflow.

Rationale: Reliable production.

Validation: Export profile verification.

Compiler Impact: Release metadata.

### PE-VAL-001

Requirement: Publishing Engine SHALL fail compilation on critical geometry defects.

Rationale: Protects production quality.

Validation: Critical error detection.

Compiler Impact: Compilation stop.

## Publishing Engine Prompt Fragment

TECHNICAL SPECIFICATION: • Approved page geometry • Safe margins • Bleed • Title zone • Activity zone • Footer zone • 300 DPI • Print-ready composition • Accessible typography • Protected child response areas

## Expansion Plan

Subsequent sections will expand each rule into detailed parameter tables, edge cases, exceptions, examples, validation algorithms, reusable prompt fragments and machine-readable compiler definitions.


---

## Normative expansion from `BCube_Prompt_Engine_v3_Complete_Production_Standard_Master_Part_3.docx`

## PE-GEO-001 Detailed Specification

This section expands the mandatory page geometry rule into an operational standard suitable for human authors, designers, AI systems and automated validation.

### Objective

Ensure every page is physically manufacturable and visually consistent.

### Scope

Applies to all workbook interiors, assessments, certificates and teacher resources unless an approved exception exists.

### Normative Requirement

Every production prompt SHALL inherit the approved geometry profile before any design or illustration instructions are applied.

### Inputs

Book level, page type, trim profile, template ID, binding type.

### Outputs

Normalized publishing metadata including page size, bleed, safe area, live area and protected zones.

### Dependencies

Publishing Engine is executed before Design Engine and cannot be bypassed.

### Failure Conditions

Missing geometry profile, incorrect orientation, protected content outside safe area, inconsistent template assignment.

### Compiler Behaviour

Compilation stops on critical geometry failures and reports the affected rule identifier.

## Operational Parameters

| Parameter | Default | Allowed Range | Validation |
| --- | --- | --- | --- |
| Trim Size | 210×297 mm | Product profile | Exact match required |
| Orientation | Portrait | Portrait unless approved | Reject mismatch |
| Bleed | 3 mm | 3–5 mm | Warn if >5 mm |
| Safe Margin | 10 mm | 8–15 mm | Reject below minimum |
| Binding Margin | 12 mm | 12–18 mm | Adjust by binding |
| Live Area | Computed | Derived | Auto-generated |
| Header Zone | Reserved | Template driven | Required |
| Footer Zone | Reserved | Template driven | Required |

## Validation Algorithm

Step 1: Load template profile. Step 2: Resolve trim size. Step 3: Calculate bleed and safe area. Step 4: Validate all protected content. Step 5: Validate header, footer and activity zones. Step 6: Emit publishing metadata. Step 7: Pass to Design Engine™.

## Good Practices

- Reserve generous whitespace around child response areas.

- Keep essential faces, hands and learning objects within the live area.

- Allow for binding creep on multi-page books.

- Validate every exported page before illustration approval.

## Anti-Patterns

- Placing page numbers in variable locations.

- Allowing artwork to hide activity spaces.

- Using inconsistent margins between templates.

- Cropping educational objects at trim edges.

## Cross References

Related rules: PE-GEO-002, PE-LAY-001, DE-GRID-001, VG-FOC-001, QA-PUB-001.

## Expansion Note

This pattern will be repeated for every rule in the BCube Prompt Engine™. Each rule will eventually include detailed examples, exception cases, prompt fragments, automated validation logic and implementation notes.
