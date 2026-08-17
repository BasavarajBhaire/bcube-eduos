# ADR-0002 — Versioned Curriculum Traceability

**Status:** Proposed  
**Date:** 2026-08-17  
**Owner:** Academic + Data Architecture

## Context

Bcube curriculum and publishing artifacts evolve over time. Lesson plans, observations and progress evidence must remain interpretable even after a book/page/activity is revised.

## Decision

Academic operational records will reference stable, version-aware curriculum identifiers down to the appropriate activity/page/objective level.

Target chain:

`Programme → Series → Book → Version → Page/Activity → Learning Objective → Lesson Plan → Delivery → Observation → Progress`

## Rationale

Without versioned traceability, historical evidence can silently point to changed content, making academic review and analytics unreliable.

## Consequences

- publishing/curriculum artifacts need stable identifiers and version metadata
- lesson plans and observations should persist the referenced curriculum version
- revisions should create new versions rather than mutate historical meaning
- analytics can compare delivery/evidence against the exact curriculum artifact used

## Follow-up

Align existing Bcube publishing identifiers with the EduOS curriculum catalog and define import/synchronization contracts.
