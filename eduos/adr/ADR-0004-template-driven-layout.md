# ADR-0004: Page Layout Is Template-Driven

Status: **Accepted**

## Context

Free-form page layout caused drifting logos, crowded pages, clipped content, tiny text and incorrect cover footers.

## Decision

Every page manifest must reference an exact versioned template. Templates define canvas, safe area, regions, allowed components and prohibited components. AI and page content cannot override template geometry.

## Consequences

- Unversioned or unknown templates are rejected.
- Template changes require a new semantic version.
- Covers cannot accidentally inherit interior page elements.
