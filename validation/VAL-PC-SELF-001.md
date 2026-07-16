# VAL-PC-SELF-001 — Self-Contained Final Prompt Gate

Status: Active  
Severity: Critical  
Owner: Quality Assurance Engine™  
Validates: PC-SELF-001

## Requirement

Every prompt submitted to an image-generation system MUST be complete without repository access, external modules, prior-chat context or unstated assumptions.

## Failure patterns

The validator SHALL fail the prompt when it detects:

- unresolved placeholders;
- rule IDs presented as instructions instead of expanded meaning;
- references to common, shared, attached, previous or external instructions;
- missing exact page title or page number;
- missing page-specific scene direction;
- missing complete mascot or character instructions when characters are required;
- missing teacher interaction, activity-space protection or negative constraints;
- ambiguous phrases such as “continue the same style” or “use previous character”.

## Detection tokens

Critical matches include:

- `{{` or `}}`
- `${`
- `<TBD>` or `TBD`
- `use common module`
- `follow module`
- `refer to rule`
- `same as previous`
- `as attached`
- `use the character bible`
- bare normative IDs such as `PE-*`, `DE-*`, `VG-*`, `EE-*`, `TE-*`, `PP-*`, `IE-*`, `CE-*`, `QA-*` or `PC-*` inside the image-generation instruction body.

## Pass conditions

A prompt passes only when:

1. all required sections from `compiler/FINAL_PROMPT_TEMPLATE.md` are present;
2. all variables are resolved;
3. all exact visible text is supplied;
4. the illustration direction is unique to the page;
5. the prompt can be copied into a fresh image-generation session and used without explanation.

## Failure action

Critical failure. Compilation and image generation MUST stop. The compiler SHALL report the missing or unresolved content and regenerate the prompt after expansion.