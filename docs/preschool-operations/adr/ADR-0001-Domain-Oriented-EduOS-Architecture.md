# ADR-0001 — Domain-Oriented EduOS Architecture

**Status:** Proposed  
**Date:** 2026-08-17  
**Owner:** Technology Architecture

## Context

Bcube Future Preschool requires digital capabilities across admissions, student operations, academics, assessment, parent engagement, finance, people, safety and analytics. Prematurely creating a microservice for every business capability would increase operational complexity before scale and team boundaries justify it.

## Decision drivers

- clear ownership and maintainability
- ability to evolve domains independently
- low initial operational complexity
- traceability to preschool operating processes
- future scalability

## Options considered

### A — Single undifferentiated application
Simple initially but encourages tight coupling and unclear domain ownership.

### B — Microservice per capability from day one
Strong deployment isolation but high distributed-system and operational overhead.

### C — Domain-oriented modular architecture
Define strong logical domain boundaries first and choose physical deployment boundaries based on scale, risk and team ownership.

## Decision

Adopt **Option C**. Maintain explicit domain/service contracts and data ownership while allowing early implementation to use a modular monolith or a limited number of deployables. Extract independently deployed services only when justified.

## Consequences

### Positive
- preserves architecture discipline without unnecessary infrastructure complexity
- supports incremental evolution
- aligns technology boundaries with the preschool operating model

### Trade-offs
- requires active enforcement of module/domain boundaries
- later extraction may require migration work

## Follow-up

Define domain ownership, API/event contracts, data boundaries, security model and criteria for service extraction.
