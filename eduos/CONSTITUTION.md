# BCube EduOS Constitution v1.0

Status: **FOUNDER LOCKED**

## North Star

EduOS exists to produce commercially publishable BCube books reliably, reproducibly and at scale.

## Non-negotiable principles

1. Repository content is the source of truth.
2. AI may propose candidate illustration assets only.
3. Final typography, geometry, logo placement, page numbering and release approval are deterministic.
4. Every public contract, template, asset, policy and release is versioned.
5. Published assets and releases are immutable.
6. Every page must resolve an exact template and exact asset IDs.
7. Unknown, missing, non-GOLD or checksum-invalid assets fail closed.
8. Any critical defect blocks release regardless of score.
9. Release requires a QA score of at least 95/100.
10. Every architectural rule must be enforced by executable code and automated tests.

## Production priority

The platform exists to publish books. Books do not exist merely to validate the platform.

## Architecture freeze

EduOS v1.0 core scope is limited to:

- runtime orchestration;
- manifest validation;
- template resolution;
- asset resolution;
- deterministic page composition;
- QA and release gating;
- export required for book production.

Teacher Studio, Parent Studio, AI Tutor, analytics, franchise systems and unrelated platform modules are outside the v1.0 core.

## Change control

A breaking change requires:

1. an Architecture Decision Record;
2. a new semantic version;
3. automated tests;
4. regression validation;
5. Founder approval when brand, curriculum, character identity or release policy changes.
