---
rule_id: PE-GEO-001
title: Standard Page Geometry
engine: Publishing
version: 3.0.0
status: Active
severity: Critical
owner: BCube Publishing Lead
---

# PE-GEO-001 — Standard Page Geometry

## Purpose

Ensure every BCube page is physically manufacturable, consistently proportioned, and compatible with the approved publishing workflow.

## Scope

Applies to standard workbook interiors, assessments, certificates, teacher resources, and parent resources unless an approved product profile explicitly overrides the format.

## Normative requirement

Every standard BCube workbook page **MUST** use the approved A4 portrait geometry profile before Design Engine or Illustration Engine instructions are applied.

## Default profile

| Parameter | Value |
| --- | --- |
| Trim size | 210 × 297 mm |
| Orientation | Portrait |
| Bleed | 3 mm minimum |
| Safe margin | 10 mm |
| Binding margin | 12 mm minimum on inside edge |
| Footer zone | 10–14 mm |
| Header zone | Template controlled |

## Inputs

- product level
- page type
- binding type
- template ID
- orientation override approval, when applicable

## Outputs

- resolved trim profile
- bleed dimensions
- safe-area rectangle
- binding offset
- protected header and footer zones

## Dependencies

- `PE-GEO-002`
- approved template profile
- product-level publishing brief

## Validation

1. Confirm trim size matches the selected profile.
2. Confirm orientation is valid.
3. Calculate bleed and safe areas.
4. Confirm all critical content is inside the safe area.
5. Confirm binding margin meets the selected binding method.
6. Reject the page on any critical mismatch.

## Failure severity

Critical. Compilation and release MUST stop when geometry is unresolved or invalid.

## Compiler mapping

The Prompt Compiler inserts the resolved geometry block before all design and illustration instructions.

## Gold example

An A4 portrait activity page with 3 mm bleed, 10 mm safe margins, a 12 mm inside binding margin, and all text, faces, learning objects, and activity spaces inside the live area.

## Anti-patterns

- essential content touching trim
- page number outside the footer zone
- inconsistent orientation inside one book
- artwork cropped through a child's face or hand
- no additional allowance for binding

## Change history

- 3.0.0 — Initial active rule.
