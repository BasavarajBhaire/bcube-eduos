# Master Rule Library

Canonical registry containing active normative rules across the ten BCube Prompt Engine™ engines. Rule identifiers are immutable; changes require a governed version update.

## Rule families

| Prefix | Engine |
|---|---|
| `PE` | Publishing Engine |
| `DE` | Design Engine |
| `VG` | Visual Grammar Engine |
| `EE` | Educational Engine |
| `TE` | Teaching Engine |
| `PP` | Parent Partnership Engine |
| `IE` | Illustration Engine |
| `CE` | Character Engine |
| `QA` | Quality Assurance Engine |
| `PC` | Prompt Compiler |

## File naming

Use `<RULE-ID>.md`, for example `PE-GEO-001.md`.

## Required rule fields

- Rule ID and title
- Status and owner
- Version introduced
- Normative requirement
- Rationale
- Inputs and outputs
- Dependencies and cross-references
- Validation method
- Failure severity
- Compiler impact
- Positive example and anti-pattern
- Change history

## Normative language

Approved rules use **MUST**, **MUST NOT**, **SHALL**, **SHOULD**, and **MAY** consistently.

## Lifecycle

`Draft → Review → Approved → Active → Superseded → Deprecated → Archived`

Critical child-safety, accessibility, print-readiness and educational-integrity rules cannot be overridden at book or page level.