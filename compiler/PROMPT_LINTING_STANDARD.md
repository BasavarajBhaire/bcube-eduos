# Prompt Linting Standard

## Purpose
The prompt linter detects structural and wording defects before Gold validation. Linting does not replace validation; it prepares the compiled prompt for deterministic review.

## Error classes

### LINT-E001 — Unresolved variable
Reject `{{...}}`, `${...}`, `<placeholder>`, TODO markers, and equivalent unresolved tokens.

### LINT-E002 — External dependency
Reject phrases such as “follow the common rules”, “use the character standard”, “apply module”, or bare rule/fragment/template identifiers used as image instructions.

### LINT-E003 — Contradictory instruction
Reject incompatible page sizes, orientations, placements, colours, character states, or activity-zone directions.

### LINT-E004 — Missing protected content
Reject absence of required exact title, activity text, child-facing instruction, page number, branding, or mandatory footer content.

### LINT-E005 — Incomplete canonical character
Reject a recurring character when protected visual identity fields are absent.

### LINT-E006 — Empty instructional container
Reject empty speech balloons, instruction boxes, labels, or response panels unless the page data explicitly defines a child-completion area.

## Warning classes
- excessive repetition;
- vague placement language;
- decorative detail without educational purpose;
- excessive prompt length caused by non-protected duplication;
- optional guidance not clearly separated from rendered page text.

## Protected text
The linter MUST compare exact rendered text against canonical page data. Protected text may not be paraphrased, corrected, translated, abbreviated, or reordered without a new approved source revision.

## Output
The linter returns:
- status: PASS or FAIL;
- errors with codes and locations;
- warnings;
- protected-text comparison;
- unresolved-token count;
- external-reference count;
- contradiction count.

Only lint status PASS may proceed to Gold Prompt validation.