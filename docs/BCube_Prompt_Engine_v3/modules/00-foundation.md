---
title: "Foundation and Normative Language"
product: "BCube Prompt Engine v3.0"
edition: "Founder Edition"
version: "3.0.0"
status: "Active"
phase: "Foundation"
owner: "BCube Future Academy"
last_updated: "2026-07-16"
source_documents:
  - BCube_Prompt_Engine_v3_Complete_Production_Standard_Master_Part_1.docx
---

# Foundation and Normative Language

> Normative status: This module is part of the BCube Prompt Engine v3.0 Complete Production Standard. `MUST`, `SHALL`, `SHOULD`, `MAY`, and `MUST NOT` carry their formal specification meanings.

## 1. Purpose

BCube Prompt Engine™ v3.0 is the governed production system used to compile educational intent, publishing constraints, visual grammar, teacher facilitation, parent partnership, illustration direction, character continuity, and quality controls into deterministic BCube Gold Production Prompts™.

This foundation module establishes the language, identifiers, data model, inheritance rules, compliance expectations, and change-control principles used by every downstream engine and production asset.

## 2. Scope

This standard applies to:

- Nursery, LKG, UKG, Grade 1, and future-grade workbook prompts.
- Covers, front matter, activity pages, review pages, assessments, certificates, and back covers.
- Teacher guides, parent resources, posters, flashcards, digital learning assets, and related publications.
- Human-authored prompts, AI-assisted prompt generation, compiler-generated prompts, and release validation.
- Markdown, YAML, JSON, DOCX, PDF, image, and digital distribution artifacts derived from this repository.

This standard does not replace curriculum judgment, editorial review, illustration direction, or child-safety review. It coordinates those responsibilities through one governed production system.

## 3. Source-of-truth policy

1. Markdown, YAML, and JSON under version control are normative.
2. Files under `generated/` are reproducible distribution artifacts and MUST NOT be edited manually.
3. A generated DOCX or PDF MUST identify the source version used to produce it.
4. Conflicts between generated artifacts and normative source files MUST be resolved in favor of normative source files.
5. Every production release MUST be traceable to a repository commit.

## 4. Normative language

| Term | Meaning |
| --- | --- |
| MUST | Mandatory requirement. Failure is non-compliant. |
| SHALL | Formal mandatory requirement. Equivalent in force to MUST. |
| MUST NOT | Prohibited behavior. |
| SHOULD | Recommended requirement. Deviations require a documented rationale. |
| SHOULD NOT | Discouraged behavior. Use requires a documented rationale. |
| MAY | Optional capability or behavior. |
| CAN | Statement of capability, not a requirement. |

Normative terms SHOULD be written in uppercase when used as requirements.

## 5. Foundational principles

All BCube Prompt Engine outputs MUST preserve the following principles:

1. **Child first** — every decision supports safety, comprehension, engagement, dignity, and development.
2. **Learning before decoration** — every visual and textual element has an educational or navigational purpose.
3. **Teacher enabled** — pages help teachers facilitate, question, observe, scaffold, and assess.
4. **Parent connected** — suitable pages extend learning through practical, low-burden family engagement.
5. **Future ready** — curiosity, communication, creativity, critical thinking, collaboration, confidence, and character are intentionally developed.
6. **Inclusive by design** — representation, accessibility, and participation are built in rather than added later.
7. **Print and digital ready** — assets are designed for reliable production across approved formats.
8. **Traceable and governed** — every rule, fragment, template, validation result, and release has an owner and version.
9. **Human reviewed** — AI assists production but does not replace accountable educational and publishing review.
10. **Continuously improved** — evidence, classroom feedback, defects, and research inform controlled revisions.

## 6. Engine architecture

The compiler executes the following canonical sequence:

1. Publishing Engine (`PE`)
2. Design Engine (`DE`)
3. Visual Grammar Engine (`VG`)
4. Educational Engine (`EE`)
5. Teaching Engine (`TE`)
6. Parent Partnership Engine (`PP`)
7. Illustration Engine (`IE`)
8. Character Engine (`CE`)
9. Quality Assurance Engine (`QA`)
10. Prompt Compiler (`PC`)

An engine MAY reference upstream outputs. An engine MUST NOT silently override a mandatory upstream requirement.

## 7. Rule identification

| Prefix | Engine or library |
| --- | --- |
| `PE-` | Publishing Engine |
| `DE-` | Design Engine |
| `VG-` | Visual Grammar Engine |
| `EE-` | Educational Engine |
| `TE-` | Teaching Engine |
| `PP-` | Parent Partnership Engine |
| `IE-` | Illustration Engine |
| `CE-` | Character Engine |
| `QA-` | Quality Assurance Engine |
| `PC-` | Prompt Compiler |
| `TPL-` | Template Library |
| `FRG-` | Prompt Fragment Library |
| `VAL-` | Validation Library |
| `EX-` | Reference Example Library |

Rule identifiers MUST be unique, stable, and never reused for a different requirement.

Recommended structure:

```text
<ENGINE>-<DOMAIN>-<SEQUENCE>
```

Example:

```text
PE-GEO-001
EE-OBJ-004
QA-ACC-012
```

## 8. Canonical rule record

Every normative rule SHOULD contain the following fields:

| Field | Requirement |
| --- | --- |
| Rule ID | Unique stable identifier. |
| Title | Concise human-readable name. |
| Requirement | Normative statement. |
| Rationale | Educational, production, or governance reason. |
| Scope | Products, pages, grades, or engines affected. |
| Inputs | Required metadata or upstream outputs. |
| Outputs | Produced data or prompt instructions. |
| Preconditions | Conditions required before execution. |
| Validation | Automated or human verification method. |
| Failure severity | Critical, Major, Minor, or Cosmetic. |
| Exceptions | Approved deviations and authority required. |
| Cross-references | Related rules, fragments, templates, and validations. |
| Version introduced | First release containing the rule. |
| Owner | Accountable role or council. |
| Status | Draft, Active, Superseded, Deprecated, or Archived. |

## 9. Master prompt data model

### 9.1 Global metadata

- Publisher
- Product family
- Engine version
- Language and locale
- Brand profile
- Output format
- Compliance profile

### 9.2 Book metadata

- Book ID
- Book title
- Series title
- Grade or age level
- Subject or domain
- Edition
- Curriculum version
- Book theme
- Page count

### 9.3 Unit metadata

- Unit ID
- Unit title
- Learning domain
- Competencies
- Vocabulary
- Developmental progression
- Assessment focus

### 9.4 Page metadata

- Page ID
- Page number
- Exact page title
- Page type
- Learning objective
- Child activity
- Teacher action
- Parent extension
- Illustration focus
- Character roster
- Assessment evidence
- Template ID

### 9.5 Compilation metadata

- Prompt ID
- Compiler version
- Engine versions
- Fragment versions
- Template version
- Validation status
- Gold Quality Score™
- Approval status
- Compilation timestamp
- Source commit

## 10. Inheritance and precedence

The canonical precedence order is:

```text
Global → Product → Book → Unit → Page → Approved exception
```

Rules at a lower level MAY specialize an upstream rule only when the upstream rule is explicitly overridable.

The following requirements are protected and MUST NOT be bypassed by ordinary overrides:

- Child safety.
- Accessibility minimums.
- Print-safe geometry.
- Brand integrity.
- Mandatory educational metadata.
- Critical QA gates.
- Copyright and licensing controls.

Any protected-rule exception requires governance approval and a recorded rationale.

## 11. Master prompt skeleton

Every compiled BCube Gold Production Prompt™ SHOULD follow this structure:

1. Compiler metadata
2. Technical and publishing specification
3. Design and page architecture
4. Visual grammar and attention flow
5. Educational intent and competency mapping
6. Teacher facilitation and classroom interaction
7. Parent partnership and home extension
8. Illustration direction
9. Character direction and continuity
10. Page-specific art direction
11. Activity usability requirements
12. Accessibility and inclusion requirements
13. Negative constraints
14. Validation summary
15. Release metadata

## 12. Compliance model

Compliance is evaluated at four levels:

| Level | Meaning |
| --- | --- |
| Rule compliant | Individual requirement passes. |
| Engine compliant | All mandatory engine rules pass. |
| Prompt compliant | Compiler output passes all required engines. |
| Gold certified | Release satisfies certification thresholds and approvals. |

A critical failure in any protected domain blocks release regardless of aggregate score.

## 13. Failure severity

| Severity | Meaning | Default action |
| --- | --- | --- |
| Critical | Child safety, legal, geometry, accessibility, or release-blocking failure. | Block compilation or release. |
| Major | Significant educational, design, brand, or consistency failure. | Rework required. |
| Minor | Limited issue that does not invalidate the page. | Correct before final release where practical. |
| Cosmetic | Non-functional visual refinement. | Track for improvement. |

## 14. Human and AI responsibility

1. AI MAY generate draft content, prompt fragments, layout suggestions, and illustrations.
2. AI output MUST be reviewed against the applicable engine rules.
3. Educational decisions MUST remain accountable to qualified human reviewers.
4. Generated illustrations MUST be checked for anatomy, safety, inclusion, text artifacts, and brand consistency.
5. AI MUST NOT introduce unapproved trademarks, characters, logos, or copyrighted derivatives.
6. The final release decision MUST be attributable to a human owner or authorized governance body.

## 15. Localization

Localized prompts and assets MUST preserve:

- The original learning objective.
- Developmental appropriateness.
- Cultural relevance without stereotyping.
- Layout usability after text expansion.
- Brand and character continuity.
- Validation and certification traceability.

Translation alone is insufficient when examples, gestures, clothing, family contexts, or classroom objects require cultural adaptation.

## 16. Versioning

BCube Prompt Engine uses semantic versioning:

```text
MAJOR.MINOR.PATCH
```

- **MAJOR** — breaking architectural, schema, or governance change.
- **MINOR** — backward-compatible capability, rule set, fragment, or template addition.
- **PATCH** — correction or clarification without intended behavior change.

Every release MUST include:

- Version number.
- Effective date.
- Change summary.
- Impacted modules.
- Migration guidance where required.
- Approval record.

## 17. Lifecycle

Normative assets follow this lifecycle:

```text
Draft → Review → Approved → Active → Superseded → Deprecated → Archived
```

Deprecated assets MUST identify their replacement and planned removal version.

## 18. Repository organization

```text
docs/         Human-readable standards and generated editions
rules/        Canonical normative rule registry
templates/    Reusable page and prompt templates
fragments/    Versioned prompt fragments
validation/   Validation policies and release gates
examples/     Reference implementations and anti-patterns
schemas/      Machine-readable schemas
scripts/      Build, validation, and generation tooling
production-prompts/  Versioned book-level prompt releases
```

## 19. Definition of done

A module is complete when:

- Its purpose and scope are explicit.
- Mandatory rules have stable identifiers.
- Inputs and outputs are defined.
- Validation methods exist.
- Cross-engine dependencies are documented.
- Machine-readable assets are available where applicable.
- Examples and anti-patterns are provided.
- Governance owner and version are recorded.
- Generated documentation can be reproduced.

## 20. Foundation acceptance criteria

This foundation module passes when:

- All engines use consistent normative language.
- Rule IDs are unique and traceable.
- Prompt metadata follows the canonical data model.
- Inheritance and override behavior are deterministic.
- Protected requirements cannot be silently bypassed.
- Versioning and lifecycle rules are applied consistently.
- Source-of-truth and generated-artifact policies are enforced.

## 21. Expansion roadmap

The complete production standard will continue to expand through:

- Detailed engine rules.
- Machine-readable rule and schema definitions.
- Reusable prompt fragments.
- Canonical page and product templates.
- Automated validation controls.
- Gold certification workflows.
- Reference implementations and anti-patterns.
- Book-level production prompt packages.

This module is the governing foundation for that expansion.