# PC-SELF-001 — Self-Contained Final Prompt

## Status
Active

## Priority
Critical

## Requirement

The Prompt Compiler **MUST** emit one fully expanded, page-specific production prompt. The compiled output **MUST NOT** contain unresolved references to external rules, modules, fragments, templates, indexes or common instructions.

## Rationale

Image-generation systems do not reliably resolve repository references or infer omitted page-specific requirements. Passing separated common modules directly to generation can produce generic scenes, missing content, incomplete teacher-child interaction, empty activity areas and inconsistent character behaviour.

## Inputs

- approved page metadata;
- applicable rule set;
- selected template;
- selected prompt fragments;
- character continuity profile;
- exact educational text;
- page-specific scene specification;
- negative constraints.

## Compiler behaviour

1. Resolve the complete inheritance chain.
2. Expand every rule and fragment into natural-language production instructions.
3. Replace all variables with approved page values.
4. remove duplicate instructions without removing meaning;
5. detect conflicting requirements;
6. place page-specific instructions after global constraints and before final negative rules;
7. append a validation summary;
8. block output if any unresolved identifier remains.

## Prohibited unresolved patterns

Compilation fails if the final output contains patterns such as:

- `PE-*`, `DE-*`, `VG-*`, `EE-*`, `TE-*`, `PP-*`, `IE-*`, `CE-*`, `QA-*`, `PC-*`;
- `PF-*` or `TPL-*` identifiers;
- “use the common module”;
- “follow the standard rules”;
- “as defined elsewhere”;
- placeholder syntax such as `{{variable}}`, `${variable}`, `<insert>`, or `TBD`.

## Validation

A valid compiled prompt must be independently understandable by a reviewer who has no access to the repository.

## Failure action

Critical compilation failure. The prompt must not be submitted for image generation.

## Cross-references

- PC-ASM-001
- PC-VAL-001
- QA-GATE-001
- WAVE_2_PRODUCTION_PROMPT_POLICY
