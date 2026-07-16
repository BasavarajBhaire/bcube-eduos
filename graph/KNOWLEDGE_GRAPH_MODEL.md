# BCube Knowledge Graph™ Model

## Purpose

The Knowledge Graph connects educational intent, reusable assets, rules and generated outputs without duplicating source data.

## Node types

- Organization
- Brand
- Series
- Book
- Unit
- Lesson
- Page
- Activity
- LearningObjective
- Competency
- Character
- Template
- Rule
- Fragment
- ValidationProfile
- BuildProfile
- GeneratedPrompt
- GeneratedAsset

## Relationship types

- `CONTAINS`
- `USES_TEMPLATE`
- `USES_CHARACTER`
- `IMPLEMENTS_RULE`
- `HAS_OBJECTIVE`
- `DEVELOPS_COMPETENCY`
- `REQUIRES_FRAGMENT`
- `VALIDATED_BY`
- `GENERATES`
- `DERIVED_FROM`
- `SUPERSEDES`

## Example

`PAGE-005` → `USES_CHARACTER` → `STAR-001`

`PAGE-005` → `HAS_OBJECTIVE` → `OBJ-GREETING-001`

`PAGE-005` → `USES_TEMPLATE` → `TPL-ACT-001`

`PROMPT-CC-NUR-005` → `DERIVED_FROM` → `PAGE-005`

## Integrity rules

- Every generated prompt MUST link to one canonical Page entity.
- Every character reference MUST resolve to one active Character asset version.
- Every template reference MUST resolve before prompt compilation.
- Cyclic inheritance among rules or templates is prohibited.
- Generated outputs MUST remain traceable to canonical inputs and versions.

## Query examples

- Find every Nursery page using Star that develops communication.
- Find prompts affected by a change to the official publisher address.
- Find pages using a deprecated template.
- Find all Gold-certified assets derived from a specific rule version.
