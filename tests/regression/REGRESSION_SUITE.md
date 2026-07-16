# BCube Gold Prompt Compiler™ Regression Suite

## Purpose

The regression suite protects previously approved prompt behavior whenever compiler rules, templates, character profiles, book metadata, validators or model profiles change.

## Mandatory Reference Cases

1. `nursery/communication-champions/meet-star`
2. `nursery/communication-champions/my-family`
3. `nursery/communication-champions/happy-face`
4. `nursery/fine-motor-fun/trace-the-line`
5. `nursery/creativity-challenges/colour-your-way`

## Test Layers

### Schema Regression

All source JSON and intermediate representations must validate against the active schemas.

### Prompt Structure Regression

The compiled prompt must contain every mandatory section in the model-profile order.

### Content Regression

Protected facts must remain unchanged, including:

- exact title and page number;
- publisher identity;
- official logo requirement;
- official Star appearance;
- teacher and child interaction requirements;
- protected activity area;
- exact visible text;
- negative constraints.

### Safety Regression

No change may introduce unsafe behavior, frightening content, exclusion, distorted anatomy or inappropriate developmental expectations.

### Visual-Intent Regression

Automated text checks and human review must confirm that focal hierarchy, page-specific scene, activity clarity and preschool publishing style remain intact.

## Baseline Policy

A baseline may be updated only when:

- the change is intentional;
- the affected rules are documented;
- validation passes;
- a reviewer approves the new expected output;
- the prompt fingerprint changes and is recorded.

## Failure Policy

Any unexpected change to protected facts, mandatory sections or hard validation gates blocks release.
