# Illustration Content Validation Policy

Status: MANDATORY — BLOCKING GATE

## Purpose

File-count and geometry validation are not evidence of a valid preschool page.
Every learning page must contain content-specific illustrations that make the
instruction understandable before the child reads the labels.

## Required page evidence

Each rendered learning page must have a sibling `.illustration-evidence.json`
record with:

- `page_file`
- `canonical_instruction`
- `canonical_scene`
- `required_visual_elements`
- `observed_visual_elements`
- `illustration_regions`
- `contains_text_only_picture_substitutes` (must be `false`)
- `contains_empty_required_visual_regions` (must be `false`)
- `instruction_supported_by_illustrations` (must be `true`)
- `review_status` (must be `PASS`)
- `reviewed_by`

Every required visual element must appear in `observed_visual_elements`. Each
illustration region must name the depicted subject and use `kind` equal to
`illustration` or `official_asset`. Text, initials, letters, labels, ovals,
blank frames and generic placeholders are never valid picture evidence.

## Mandatory review sequence

1. Identity and numbering validation.
2. Individual-page output validation.
3. Instruction-to-illustration semantic validation.
4. A4 legibility, safe-area and overlap validation.
5. Human visual review at full-page size.
6. Clean ZIP extraction and repeat of gates 2–4.

No book may be marked complete or used as the base for another book until every
learning page passes all six steps.

## Scope

This policy applies to every Nursery, LKG and UKG book. Communication Champions
reader pages 16–41 must be corrected and approved before the remaining Nursery
books resume production.
