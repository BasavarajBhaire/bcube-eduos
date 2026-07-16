# Prompt Conflict Resolution Policy

## Purpose

This policy defines deterministic precedence when source assets disagree during compilation.

## Precedence order

1. Child safety and legal requirements
2. Publishing geometry and trim safety
3. Exact approved page data
4. Approved book metadata
5. Canonical character specification
6. Approved page template
7. Educational objective and assessment evidence
8. Teacher and parent interaction requirements
9. Illustration and visual grammar preferences
10. Decorative preferences

## Protected fields

The following fields cannot be overridden by lower-precedence sources:

- page title
- page number
- age level
- learning objective
- official logo asset
- publisher identity
- trim size and safe margins
- canonical mascot identity
- exact child-facing instruction
- safety requirements

## Common conflict examples

### Character placement

If a template places Star on the right but page data requires Star as the central focal point, page data wins because the page-specific learning scene has higher precedence than a generic layout preference.

### Background

If illustration style suggests a detailed classroom but the activity template requires a large white response area, the protected activity space wins.

### Teacher presence

If a generic character fragment includes a teacher but the approved page data marks teacher presence as false, the teacher is omitted unless a teaching rule makes the teacher mandatory.

### Text

Exact approved visible text always overrides paraphrased fragment wording.

## Compiler behaviour

- Resolvable conflicts are corrected automatically and recorded in the compilation log.
- Protected-field conflicts stop compilation.
- Two sources at the same precedence level require an explicit page-level resolution.
- Silent conflict resolution is prohibited.

## Audit record

Each resolved conflict must record:

- conflicting sources
- affected field
- selected value
- precedence rule applied
- compiler version
- timestamp
