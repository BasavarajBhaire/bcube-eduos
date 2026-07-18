# ADR-0001: Repository Is the Source of Truth

Status: **Accepted**

## Context

Chat history and free-form prompts caused book, page, wording and activity drift.

## Decision

Canonical curriculum, page identity, visible wording and production rules must be resolved from version-controlled repository sources. Chat history may clarify intent but cannot override repository content.

## Consequences

- Missing canonical content blocks production.
- Conflicting sources require explicit resolution.
- Every release records source paths and commit SHA.
