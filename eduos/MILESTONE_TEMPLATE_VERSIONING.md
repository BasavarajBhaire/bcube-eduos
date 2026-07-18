# Milestone: Versioned Production Templates

Status: **Implemented in EduOS v1.0**

## Goal

Guarantee that every published page can be reproduced from an immutable template version. A page manifest must reference an exact template ID such as `COVER_V1.0.0`; generic references such as `cover`, `latest`, or `current` are forbidden.

## Template ID contract

`<TEMPLATE_NAME>_V<MAJOR>.<MINOR>.<PATCH>`

Examples:

- `COVER_V1.0.0`
- `LESSON_V1.0.0`
- `TRACE_V1.0.0`
- `COLOR_V1.0.0`
- `MATCH_V1.0.0`

## Semantic version rules

- **PATCH**: defect correction that does not move regions, change typography hierarchy, alter activity capacity, or change visible composition.
- **MINOR**: backward-compatible enhancement for new manifests. Existing published manifests remain pinned to the previous version.
- **MAJOR**: breaking geometry, layout, component, or behaviour change. Requires Founder approval and new gold-reference pages.

## Fail-closed rules

Production must stop when:

- the template ID is unversioned;
- the template does not exist;
- inheritance is circular;
- a resolved region exceeds the A4 canvas;
- the resolved canvas differs from 2480 × 3508 px at 300 DPI;
- a cover enables page numbering or worksheet regions;
- a template attempts to use a generated-logo fallback.

## Reproducibility

Published page manifests must permanently store:

- exact template ID;
- registry version;
- exact asset IDs and versions;
- source prompt ID;
- composer version;
- QA result and rule-set version.

No production runner may silently upgrade a page manifest to a newer template.

## Initial locked registry

The first registry includes:

- `COVER_V1.0.0`
- `LESSON_V1.0.0`
- `TRACE_V1.0.0`
- `COLOR_V1.0.0`
- `MATCH_V1.0.0`

## Execution

```bash
python eduos/src/template_registry.py COVER_V1.0.0
python -m unittest eduos/tests/test_template_registry.py
```

## Acceptance

This milestone is complete only when all tests pass and every page manifest uses an exact template version.
