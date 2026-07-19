# BCube Gold QA Scorecard

Status: MANDATORY
Minimum passing score: 95/100
Critical defects allowed: 0

## Usage

Complete this scorecard after generating each page and before saving it as approved. Any critical failure blocks release regardless of total score.

## Identity gate — critical

- [ ] Book matches canonical repository.
- [ ] Level matches canonical repository.
- [ ] Prompt ID matches canonical repository.
- [ ] Page number and title match canonical repository.
- [ ] Markdown and JSON were both loaded.
- [ ] Visible wording matches exactly.
- [ ] Required illustration scene matches.
- [ ] Required activity and response space match.
- [ ] No invented content is present.

## Single-page gate — critical

- [ ] Exactly one standalone page is present.
- [ ] No collage, contact sheet, preview board or multi-page composite.
- [ ] Flat, front-facing A4 portrait page only.

## Brand gate — critical

- [ ] Official BCube logo asset used unchanged, or exact reserved logo zone maintained for post-composition.
- [ ] No generated, redrawn, recoloured, cropped or distorted logo.
- [ ] Correct age badge policy.
- [ ] Correct page-number policy.
- [ ] Book manifest uses the locked 43-package architecture.
- [ ] Production position, logical page and printed-number visibility agree.
- [ ] P001–P005 numbering is hidden and P006 Welcome visibly starts at 5.
- [ ] Contents uses two pages, canonical module headings and no front-matter entries.

## Print gate — critical

- [ ] A4 portrait geometry.
- [ ] 3 mm bleed.
- [ ] 10 mm safe margin.
- [ ] 12 mm binding margin.
- [ ] 300 DPI target.
- [ ] No clipped text or cropped key objects.
- [ ] Text remains readable at A4 print size.

## Weighted scoring

| Category | Maximum | Score |
|---|---:|---:|
| Repository accuracy | 20 | |
| Layout quality | 15 | |
| Illustration quality | 15 | |
| Educational effectiveness | 15 | |
| Print readability | 10 | |
| Character consistency | 10 | |
| Brand consistency | 5 | |
| Child engagement | 5 | |
| Parent/teacher appeal | 3 | |
| Premium finish | 2 | |
| **Total** | **100** | |

## Decision

- [ ] BCube Gold Certified: score 95–100 and zero critical defects.
- [ ] Rejected: score below 95 or any critical defect.

## QA record

- Prompt ID:
- Output filename:
- Reviewer:
- Date:
- Critical defect count:
- Total score:
- Decision:
- Regeneration notes:
