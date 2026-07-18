# ADR-0005: Release Gates Fail Closed

Status: **Accepted**

## Context

Subjective approval allowed outputs with wrong identity, invented content and branding defects to proceed because they looked visually acceptable.

## Decision

Any unresolved dependency, schema error, checksum mismatch, critical defect or QA score below 95 blocks release. Critical failures override the numeric score. No automatic fallback may substitute an unapproved asset, template or content value.

## Consequences

- Production stops visibly instead of silently degrading.
- Regeneration and correction are mandatory after critical failure.
- Founder-approved repository changes are the only override mechanism.
