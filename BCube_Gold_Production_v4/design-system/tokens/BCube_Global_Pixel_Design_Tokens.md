# BCube Global Pixel Design Tokens

Status: PRE-PRINT PILOT  
Canonical canvas: 2480 × 3508 px at 300 DPI  
Scope: Nursery, LKG, UKG and future levels

## Purpose

This contract converts BCube page composition from relative placement into deterministic pixel geometry. AI may create only the illustration layer. It must never decide the placement of the official logo, approved Star mascot, title typography, age badge, skill capsules, teacher panel, parent panel, pillar system, footer or page number.

The machine-readable source of truth is:

`BCube_Gold_Production_v4/design-system/tokens/BCube_Global_Pixel_Design_Tokens.json`

## Canonical page geometry

- Canvas: 2480 × 3508 px
- Resolution: 300 DPI
- Trim: A4 portrait, 210 × 297 mm
- Bleed: 3 mm
- Minimum safe margin: 10 mm
- Binding margin: 12 mm
- Coordinate origin: top-left
- All coordinates are integer pixels
- Scaling is permitted only proportionally from the canonical 2480 × 3508 canvas

## Layering rule

Every output is composed in this order:

1. Page background and fixed frame
2. Illustration layer inside its assigned frame
3. Official BCube logo asset
4. Approved Star asset, when the page contract allows it
5. Deterministic title and instructional typography
6. Fixed badges, panels, icons and core pillars
7. Footer and page number, when visible
8. QA overlay check, removed before export

The illustration layer must contain no logo, Star mascot, title, badge, panel label, page number, footer or core-pillar typography.

## Page-type geometry

### Cover

The cover uses fixed regions for:

- official logo
- series banner
- two-line `{Book Name}` title hierarchy
- circular `{Age Group}` badge
- book-specific strapline
- main illustration frame
- six book-skill capsules
- five core pillars
- primary and secondary footer bands

The illustration frame and core-pillar label must not touch or overlap. Only one Star mascot and one official logo are permitted.

### Publisher / Copyright

The publisher page uses fixed regions for:

- official logo
- `{Book Name}`
- `{Age Group}`
- publisher identity and address
- website, email and phone
- copyright and maturity status
- `{Publication Code}` and `{Document ID}`
- printed-in line and optional QR block

Illustration, Star, teacher panels, parent panels, activity panels and visible page numbers are prohibited.

### About This Book

The About page uses:

- `{Book Name}` as the primary header
- `{Page Title}` as the secondary header
- no repeated `{Series Name}` banner
- hidden page number
- fixed intro-text and learning-outcome regions
- one controlled illustration frame
- optional teacher and parent panels only when required by the approved page package

### Contents

The Contents page uses fixed navigation regions, small supporting icons only and hidden numbering. A dominant illustration is prohibited.

### Lesson

The lesson template uses fixed regions for title, illustration/activity, teacher guidance, parent guidance, core pillars, footer and visible page number. The age badge is prohibited on interior lesson pages.

## Global defect gates

Reject the page when any of the following occurs:

- official logo is generated, redrawn, substituted or duplicated;
- approved Star is generated, substituted or duplicated;
- text is embedded in the AI illustration layer;
- a region overlaps another protected region;
- the illustration frame has a duplicate border or unexplained second line;
- the core-pillar label is hidden behind the pillar panel;
- content falls outside the trim-safe region;
- front-matter numbering is visible;
- the publisher page contains an illustration;
- the page dimensions or DPI differ from the canonical export;
- any critical defect remains unresolved.

Acceptance requires 100/100 QA and zero critical defects.

## Governance

Global pixel tokens may define publishing infrastructure only. They must not replace the page-specific educational objective, activity, teacher guidance, parent connection, illustration scene or evidence defined by the individual V4 prompt package.

Book identity values are resolved through placeholders such as `{Book Name}`, `{Age Group}`, `{Publication Code}` and `{Document ID}`. No individual book title may be hard-coded into this global contract.
