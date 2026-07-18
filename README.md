# BCube EduOS

The canonical documentation, machine-readable production standards, and deterministic publishing implementation for **BCube Academy – Future Skills Preschool**.

## Authoritative publishing standards

- [BCube Publishing Standard (BPS)](docs/BCube_Publishing_Standard/README.md)
- [BPS v1.0 – Gold Edition](docs/BCube_Publishing_Standard/BCube_Publishing_Standard_v1.0.md)
- [BCube Publishing Handbook (BPH)](docs/BCube_Publishing_Handbook/README.md)
- [Gold Nursery Production Program](docs/Book_Production/Gold_Nursery_Production_Program.md)

BPS is the mandatory authority for educational, editorial, design, illustration, asset, quality, print, and release requirements. BPH provides practical implementation guidance.

## Prompt and curriculum sources

- [BCube Prompt Engine v3.0](docs/BCube_Prompt_Engine_v3/README.md)
- [Complete Production Standard](docs/BCube_Prompt_Engine_v3/BCube_Prompt_Engine_v3.md)
- [Complete Nursery, LKG, and UKG Production Prompts v3 portfolio](production-prompts/README.md)

Official book names, page identities, learning objectives, visible wording, and production order must be read from the canonical repository sources. Guessing or reconstructing them from memory is prohibited.

## EduOS implementation

The `eduos/` platform provides the deterministic execution foundation:

- versioned template registry;
- immutable asset registry and checksum validation;
- compiler and Page Object Model;
- runtime preflight and auditable events;
- deterministic page composition foundations;
- QA rejection gates;
- Publisher CLI foundation.

AI may produce candidate illustration assets only. It does not own the official logo, final typography, layout, page numbering, curriculum, or release approval.

## Current production priority

The active goal is the **Gold Nursery Production Program**, beginning with `Communication Champions` as the reference production book.

A book is not considered printable until every required page is Gold, the final PDF passes technical preflight, and a physical proof is approved.

## Repository model

Markdown is the authoritative human-readable source. YAML and JSON provide executable rules, templates, manifests, registries, validation controls, examples, and schemas. Word, PDF, PNG, and other exports are generated release artifacts.

## Top-level structure

| Path | Purpose |
| --- | --- |
| `docs/` | Publishing standards, handbook, production governance, curriculum and generated editions |
| `eduos/` | Runtime, compiler, registries, QA, Publisher, and deterministic publishing implementation |
| `production-prompts/` | Versioned book-level production prompt releases |
| `rules/` | Canonical normative rule registry |
| `templates/` | Reusable page and prompt templates |
| `fragments/` | Versioned prompt fragments |
| `validation/` | Validation policies and release gates |
| `examples/` | Reference page and prompt implementations |
| `schemas/` | JSON Schemas for machine validation |
| `scripts/` | Documentation generation and validation |

## Release status

- BCube Prompt Engine: v3.0.0 Founder Edition
- BCube Publishing Standard: v1.0.0 Gold Edition
- EduOS: implementation in progress
- Nursery books: production in progress; not yet approved for commercial printing
