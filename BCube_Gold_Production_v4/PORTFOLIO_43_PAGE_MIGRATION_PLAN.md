# BCube 30-Book Migration Plan — 43-Package Architecture

Status: APPROVED ROLLOUT PLAN

Depends on: `FRONT_MATTER_AND_NUMBERING_POLICY.md`

## Objective

Migrate every Nursery, LKG and UKG Gold book from the legacy 41-package front matter to the locked 43-package architecture without changing curriculum sequence or learning-page content.

## Rollout order

### Phase 1 — Reference book

1. Nursery — Communication Champions
2. Validate P001–P010 visually.
3. Validate the complete 43-package manifest and printed-number mapping.
4. Approve the book as the reusable structural reference.

### Phase 2 — Remaining Nursery books

1. Curiosity Explorers
2. Fine Motor Fun
3. Creativity Challenges
4. Confidence Builders
5. STEM Explorers
6. My World & General Awareness
7. Logical Thinking Adventures
8. Healthy Habits & Safety
9. Art & Colour Fun

### Phase 3 — LKG books

1. Communication Champions
2. Early Literacy Adventures
3. Early Maths Adventures
4. Logical Thinking Adventures
5. STEM Explorers
6. Creativity Challenges
7. My World & General Awareness
8. Healthy Habits & Safety
9. Art & Colour Fun
10. Confidence & Social Skills

### Phase 4 — UKG books

1. Communication Masters
2. Reading & Literacy Adventures
3. Maths Explorers
4. Logic & Brain Builders
5. Young Scientists
6. Creative Design Studio
7. My Amazing World
8. Digital Explorers
9. Healthy Me & Wellbeing
10. Financial Literacy & Life Skills

## Per-book migration checklist

- [ ] Preserve the exact approved book name and level.
- [ ] Add P002 About This Book using book-specific canonical objectives.
- [ ] Move Copyright to P003 and verify publisher metadata.
- [ ] Replace Contents with module-wise P004 and P005.
- [ ] Move Welcome to P006 and assign printed page number 5.
- [ ] Shift every legacy P005–P041 package to P007–P043.
- [ ] Preserve page titles, objectives, activities, teacher moves, parent connections, scenes and prohibitions.
- [ ] Update prompt IDs and every internal cross-reference.
- [ ] Update release README and manifest to 43 packages.
- [ ] Update Markdown and JSON packages.
- [ ] Update the source spreadsheet and its SHA-256 record.
- [ ] Update validation totals and reports.
- [ ] Validate that Contents excludes front matter and lists pages 5–42 module-wise.
- [ ] Validate that printed numbers are hidden for P001–P005 and visible from P006.
- [ ] Regenerate v4 production specifications.
- [ ] Produce two-page Contents proof at readable A4 size.
- [ ] Block commercial assembly until zero critical defects.

## Migration gates

### Gate A — Identity

- Exactly 43 production packages.
- Prompt IDs form one uninterrupted P001–P043 sequence.
- Exactly one Cover, About, Copyright, Contents Part 1, Contents Part 2 and Welcome page.

### Gate B — Numbering

- P001 has no logical or printed number.
- P002–P005 have logical numbers 1–4 and hidden printed numbers.
- P006 has logical and printed number 5.
- P043 has logical and printed number 42.

### Gate C — Curriculum preservation

- Every legacy learning page maps to exactly one new package.
- No learning page is removed, duplicated, merged, split or reordered.
- Canonical page content remains byte-comparable except for identifiers and numbering fields.

### Gate D — Contents

- Two Contents pages only.
- Module-wise grouping matches the release modules.
- First entry is Welcome at page 5.
- Final entry points to page 42.
- No front-matter entry appears.

## Completion definition

The portfolio migration is complete only when all 30 releases pass all four gates and the portfolio index reports 1,290 validated packages with zero critical defects.
