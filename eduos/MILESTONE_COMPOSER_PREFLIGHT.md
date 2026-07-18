# Milestone: Composer Preflight Integration

Status: **Implemented**

## Purpose

Prevent rendering from starting until the exact versioned template and every immutable asset have been verified.

## Execution order

1. Load the page manifest.
2. Resolve the exact template ID.
3. Validate locked A4 geometry.
4. Resolve logo, illustration and character asset IDs.
5. Require every asset to be `GOLD`.
6. Verify every file against its SHA-256 checksum.
7. Resolve asset dependencies recursively.
8. Validate template page type against manifest page type.
9. Apply cover-specific rejection rules.
10. Build the render plan only after all checks pass.

## Fail-closed conditions

Composition is rejected when any of the following occurs:

- unknown template;
- unversioned template reference;
- unknown asset;
- non-GOLD asset;
- missing asset file;
- missing or mismatched SHA-256;
- unresolved dependency;
- duplicate asset reference;
- template and manifest page types differ;
- locked A4 geometry differs;
- a cover requests a visible page number.

## Current production state

The official BCube logo remains in `REVIEW` until its true SHA-256 checksum is calculated and recorded. Therefore, the real Communication Champions cover manifest must fail preflight today. This is intentional and confirms that EduOS does not bypass unresolved assets.

## Tests

`eduos/tests/test_composer_preflight.py` verifies successful dependency resolution and rejection for unknown assets, checksum drift, unknown templates, page-type mismatch and page numbers on covers.
