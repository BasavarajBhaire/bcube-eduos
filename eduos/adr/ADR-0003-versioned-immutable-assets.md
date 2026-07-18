# ADR-0003: Approved Assets Are Versioned and Immutable

Status: **Accepted**

## Context

Repeated generation changed the BCube logo, Star mascot, teachers and visual identity between pages.

## Decision

Every reusable asset must have an immutable versioned ID, lifecycle status and SHA-256 checksum. Only GOLD assets may be used in releasable pages. Existing asset bytes may not be replaced under the same version.

## Consequences

- Changed bytes require a new asset version.
- Missing, altered or non-GOLD assets fail resolution.
- Published pages remain reproducible.
