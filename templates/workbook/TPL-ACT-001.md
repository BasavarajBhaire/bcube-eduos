---
template_id: TPL-ACT-001
title: Standard Preschool Activity Page
category: workbook
version: 3.0.0
status: Active
owner: BCube Design Lead
---

# TPL-ACT-001 — Standard Preschool Activity Page

## Purpose

Provide a reusable page structure for tracing, matching, colouring, circling, speaking, drawing, and simple response activities.

## Compatible levels

- Nursery (3+)
- LKG (4+)
- UKG (5+)

## Required zones

| Zone | Purpose | Requirement |
| --- | --- | --- |
| Z01 | Brand header | Official logo and exact page title |
| Z02 | Brief instruction | One clear child action |
| Z03 | Primary illustration | Main learning scene |
| Z04 | Activity response | Protected, physically usable space |
| Z05 | Teacher prompt | Compact facilitation guidance |
| Z06 | Parent extension | Optional home connection |
| Z07 | Footer | Consistent page number |

## Layout constraints

- A4 portrait
- 3 mm bleed
- 10 mm safe margin
- 12 mm inside binding margin
- one dominant learning objective
- no more than three major visual groups on Nursery pages
- activity zone MUST NOT be covered by characters, props, borders, or speech bubbles

## Required variables

- `page_title`
- `page_number`
- `level`
- `learning_objective`
- `child_instruction`
- `activity_type`
- `primary_scene`
- `teacher_prompt`
- `parent_extension`

## Engine bindings

- Publishing: `PE-GEO-001`, `PE-GEO-002`
- Design: `DE-GRID-001`, `DE-HIER-001`
- Visual Grammar: `VG-FOC-001`, `VG-EYE-001`
- Educational: `EE-OBJ-001`, `EE-ACT-001`
- QA: `QA-GAT-001`

## Validation

- page title is exact and readable
- child instruction contains one principal action
- response area matches the motor and cognitive demands of the age level
- teacher and parent prompts are subordinate to the child activity
- no critical content crosses the safe area

## Gold example

A Nursery colouring page with one large familiar object, a short instruction, a teacher conversation prompt, a small optional parent extension, and generous colouring space.

## Anti-patterns

- multiple unrelated activities
- tiny response objects
- long instructions
- decorative clutter filling white space
- teacher notes dominating the page

## Change history

- 3.0.0 — Initial active template.
