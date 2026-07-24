# BCube Publishing SDK

Status: PRE-PRINT PILOT

This SDK is the only approved path for producing BCube publication pages.

## Production flow

1. Resolve the exact V4 page package from the release manifest.
2. Load the page-type master template and component registry.
3. Generate only the page-specific illustration layer when an illustration is allowed.
4. Compose official assets, editable typography and book/page data deterministically.
5. Validate the final render and composition manifest.
6. Accept only at 100/100 with zero critical defects.

Direct full-page generation by an image model is prohibited.

## Structure

- `templates/` — immutable page-type geometry and component slots.
- `components/` — reusable component contracts.
- `schemas/` — page-data and composition-manifest schemas.
- `composer/` — deterministic composition entry point.
- `validators/` — SDK and page-data validation.
- `books/` — book-specific data only; no duplicated layout rules.

## Locked publishing page types

- Cover
- About This Book
- Publisher / Copyright
- Contents
- Back Cover

Learning-page templates will be added only after the two-book publishing-framework validation is approved.

## Non-negotiable rules

- Official logo and Star assets are referenced by registry ID and verified hash.
- Branding, typography, badges, page numbers, skill capsules, pillars and footers are never generated inside illustration artwork.
- One physical page produces one flat front-facing output.
- A4 portrait: 2480 × 3508 px, 300 DPI.
- Missing, stale or contradictory inputs fail closed.

## About-page renderer

`templates/about-page-v1.json`, `validators/validate_about_inputs.py` and
`composer/compose_about_page.py` implement the locked About-page contract. The
book name is the primary two-colour header and `About This Book` is the
secondary title. The renderer includes the approved illustration, six learning
outcomes, five core pillars and standard footer, while failing closed on lesson
panels, series branding, the age badge, page numbering or Star placement.

## Publisher/Copyright renderer

`templates/publisher-page-v1.json`,
`validators/validate_publisher_inputs.py` and
`composer/compose_publisher_page.py` implement the locked administrative-page
contract. It uses `MINIMAL_HEADER` and deterministic publisher metadata. No
illustration, Star, learning goal, activity banner, teacher/parent panel, age
badge, page number or unassigned ISBN is permitted. Before the first approved
physical print, it uses the maturity label `PILOT` rather than an edition
number.
