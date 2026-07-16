# BCube Validation Library

The Validation Library contains reusable checks applied to rules, page metadata, prompt fragments, compiled prompts, illustrations and release packages.

Release requires the applicable BCube Gold score and **zero Critical defects**.

## Validation stages

1. Author-time validation
2. Schema validation
3. Engine validation
4. Cross-engine validation
5. Compiler validation
6. Generated-asset validation
7. Gold certification review
8. Post-release audit

## Severity levels

| Severity | Meaning | Default action |
|---|---|---|
| Critical | Child safety, educational integrity, accessibility, trim safety or release-blocking failure | Stop compilation and block release |
| Major | Significant quality or standards failure | Rework required |
| Minor | Limited non-critical deviation | Correct before final release where practical |
| Cosmetic | Aesthetic issue with no learning or production impact | Track and improve |

## Validation identifiers

Use `VAL-<ENGINE>-<NNN>`, for example `VAL-PE-001`.

## Required validation record

- Validation ID
- Governing rule ID
- Input artifact and version
- Test method
- Expected result
- Actual result
- Pass/fail status
- Severity
- Remediation
- Evidence
- Validator and timestamp

## Execution levels

Validation runs at fragment, engine, compiled-prompt, generated-asset and release-package levels.

## Gold release rule

All Critical checks must pass. Major, Minor and total-score thresholds are governed by the active BCube Gold Certification Standard™ version.