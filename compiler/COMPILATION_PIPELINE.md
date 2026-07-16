# BCube Gold Prompt Compiler™ — Compilation Pipeline

## Non-negotiable output rule
The final prompt sent to an image model MUST be one self-contained, page-specific instruction set. It MUST NOT contain rule IDs, module names, unresolved variables, inheritance references, or instructions to consult another file.

## Pipeline
1. Load governed global standards.
2. Load book metadata.
3. Load page data.
4. Load referenced character and template records.
5. Expand all reusable rules and fragments into explicit natural-language instructions.
6. Build the canonical Prompt Intermediate Representation (IR).
7. Resolve conflicts using the precedence model.
8. Inject mandatory missing requirements.
9. Remove duplicate and semantically redundant instructions.
10. Order sections consistently for image-model comprehension.
11. Validate the IR and compiled prompt.
12. Emit the final Gold Production Prompt™ and validation report.

## Precedence
Safety and legal > publishing > exact page data > template > character canon > book defaults > optional style preferences.

## Required final section order
1. Technical and publishing specification
2. Exact page identity and text
3. Learning objective and child outcome
4. Page layout and visual hierarchy
5. Complete scene direction
6. Complete character descriptions and interactions
7. Child activity and protected response space
8. Teacher guidance
9. Parent guidance where applicable
10. Brand and footer requirements
11. Negative constraints
12. Final quality acceptance conditions

## Hard failures
Compilation MUST stop when any placeholder, rule ID, contradictory geometry, missing exact title, missing page number, undefined character, incomplete activity area, or unresolved mandatory validation remains.
