# Gold Page Publication Pipeline

## Objective
Define the governed path from canonical educational intent to an approved publication page without exposing modular source assets to the image model.

## Pipeline
1. Validate book metadata.
2. Validate canonical page data.
3. Resolve template, character, rule, fragment, and build-profile versions.
4. Construct Prompt Intermediate Representation.
5. Resolve conflicts using governed precedence.
6. Expand every selected requirement into explicit natural-language instructions.
7. Optimize wording without weakening protected requirements.
8. Run prompt linting and Gold Prompt validation.
9. Generate fingerprint and compilation manifest.
10. Submit through an approved AI renderer adapter.
11. Validate generated image against educational, visual, publishing, brand, character, text, and safety gates.
12. Accept, retry without content mutation, or reject.
13. Assemble the approved image into the publication page.
14. Archive prompt, manifest, validation evidence, provider metadata, and final asset.

## Hard stops
The pipeline MUST stop when any of the following occurs:
- unresolved placeholder or variable;
- modular reference remains in the final prompt;
- exact child-facing text is missing or altered;
- publisher, logo, page number, or required footer data is absent;
- character identity is incomplete;
- activity space is not explicitly protected;
- conflicting layout or character placement remains unresolved;
- critical validation failure occurs.

## Retry policy
Retries reuse the same approved final prompt and fingerprint unless a new compilation version is intentionally created. Any prompt change creates a new fingerprint and a new validation cycle.

## Publication evidence package
- canonical inputs;
- resolved asset versions;
- Prompt IR;
- final prompt;
- prompt fingerprint;
- compilation manifest;
- generation metadata;
- validation report;
- approval record;
- final publication asset.