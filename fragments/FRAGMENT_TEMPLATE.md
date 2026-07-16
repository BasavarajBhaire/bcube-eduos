---
fragment_id: "PF-XXX-000"
title: "Fragment title"
engine: "Engine name"
status: "Draft"
version: "3.0.0"
parameters: []
---

# PF-XXX-000 — Fragment title

## Purpose

Describe the reusable production instruction emitted by this fragment.

## Parameters

| Parameter | Type | Required | Description | Default |
|---|---|---:|---|---|
| `example` | string | Yes | Example parameter | — |

## Preconditions

- Required rule IDs are active.
- Input metadata passes schema validation.

## Fragment text

```text
Insert compiler-ready prompt content here using {{parameter_name}} placeholders.
```

## Output contract

Define the section of the compiled prompt receiving this fragment.

## Validation

- Required variables resolve.
- No prohibited text is introduced.
- Fragment output remains compatible with the declared engine version.

## Dependencies

List rule IDs, templates and schemas.

## Example rendering

Show a resolved example.

## Change history

| Version | Date | Change | Approved by |
|---|---|---|---|
| 3.0.0 | YYYY-MM-DD | Initial draft | Pending |