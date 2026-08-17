# Start Here

## Purpose

This section defines how Bcube Future Preschool operational knowledge is created, reviewed, approved and maintained.

## Core rules

- Prefer one authoritative source and link to it rather than duplicating content.
- Every controlled document must identify owner, status and version.
- Operational procedures must define responsibilities, evidence, exceptions, escalation and measurement.
- Material architecture or operating decisions should have an ADR.
- Safety, safeguarding, employment, privacy, tax and regulatory policies require appropriate professional/legal review before operational adoption.

## Standard document header

```yaml
id: BCUBE-<DOMAIN>-<NUMBER>
title: <Document title>
owner: <Role>
approver: <Role>
status: Draft | Review | Approved | Active | Deprecated | Archived
version: 0.1
last-reviewed: YYYY-MM-DD
next-review: YYYY-MM-DD
```

## Naming conventions

- Policies: `POL-<DOMAIN>-NNN`
- Processes: `PROC-<DOMAIN>-NNN`
- SOPs: `SOP-<DOMAIN>-NNN`
- Checklists: `CHK-<DOMAIN>-NNN`
- Forms: `FRM-<DOMAIN>-NNN`
- Architecture decisions: `ADR-NNNN`

Suggested domains: `ADM`, `ACA`, `STU`, `PAR`, `HR`, `SAF`, `FIN`, `OPS`, `FAC`, `IT`, `DATA`, `MKT`, `QMS`.

## Change control

1. Identify the change and affected documents.
2. Update the source document on a branch.
3. Review operational, academic, safety and technical impacts as applicable.
4. Approve through pull request review.
5. Merge and communicate the effective change.
6. Train affected roles when execution changes.
7. Archive superseded material rather than silently deleting important institutional decisions.

## Master design principle

Every significant Bcube process should answer:

1. What needs to happen?
2. Who owns it?
3. When does it happen?
4. How is it performed?
5. What evidence is retained?
6. What happens when the normal flow fails?
7. How is performance measured?
