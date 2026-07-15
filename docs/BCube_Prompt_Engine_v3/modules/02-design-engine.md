---
title: "Phase 2 - Design Engine"
product: "BCube Prompt Engine v3.0"
edition: "Founder Edition"
version: "3.0.0"
status: "Active"
phase: "2"
owner: "BCube Future Academy"
last_updated: "2026-07-15"
source_documents:
  - BCube_Prompt_Engine_v3_Phase_2_Design_Engine_FINAL.docx
  - BCube_Prompt_Engine_v3_Complete_Production_Standard_Master_Part_4.docx
---

# Phase 2 - Design Engine

> Normative status: This module is part of the BCube Prompt Engine v3.0 Complete Production Standard. `MUST`, `SHALL`, `SHOULD`, `MAY`, and `MUST NOT` carry their formal specification meanings.

## Purpose

Design Engine™ transforms the publishing specification into a consistent page layout system. It defines visual hierarchy, reusable layout components, spacing, typography application, iconography, component placement, and template behavior so every BCube page follows one coherent design language.

## 1. Design Principles

Objective: Standardize this design layer across every BCube publication.

- Child-first clarity

- One dominant learning focus

- Consistency before decoration

- Purposeful white space

- Accessible layouts

- Premium publishing appearance

### Compiler Output

Produces a normalized design specification describing page grid, component positions, spacing rules, typography hierarchy and template identifiers for downstream engines.

### Acceptance Criteria

All pages exhibit consistent layout, visual hierarchy, spacing, component placement and design language regardless of book or subject.

## 2. Layout Grid System

Objective: Standardize this design layer across every BCube publication.

- 12-column responsive print grid

- Header, content and footer regions

- Consistent gutters

- Template locking

- Alignment rules

- Baseline spacing

### Compiler Output

Produces a normalized design specification describing page grid, component positions, spacing rules, typography hierarchy and template identifiers for downstream engines.

### Acceptance Criteria

All pages exhibit consistent layout, visual hierarchy, spacing, component placement and design language regardless of book or subject.

## 3. Visual Hierarchy

Objective: Standardize this design layer across every BCube publication.

- Title > Illustration > Activity > Teacher prompt > Parent prompt > Footer

- Single primary focal area

- Limit competing visual elements

### Compiler Output

Produces a normalized design specification describing page grid, component positions, spacing rules, typography hierarchy and template identifiers for downstream engines.

### Acceptance Criteria

All pages exhibit consistent layout, visual hierarchy, spacing, component placement and design language regardless of book or subject.

## 4. Component Library

Objective: Standardize this design layer across every BCube publication.

- Page title

- Learning objective

- Instruction box

- Teacher tip

- Parent extension

- Activity panel

- Reward badge

- Footer

- Icons

### Compiler Output

Produces a normalized design specification describing page grid, component positions, spacing rules, typography hierarchy and template identifiers for downstream engines.

### Acceptance Criteria

All pages exhibit consistent layout, visual hierarchy, spacing, component placement and design language regardless of book or subject.

## 5. Typography Application

Objective: Standardize this design layer across every BCube publication.

- Heading scale

- Instruction scale

- Consistent line spacing

- Readable contrast

- Maximum line lengths

### Compiler Output

Produces a normalized design specification describing page grid, component positions, spacing rules, typography hierarchy and template identifiers for downstream engines.

### Acceptance Criteria

All pages exhibit consistent layout, visual hierarchy, spacing, component placement and design language regardless of book or subject.

## 6. Colour & UI Tokens

Objective: Standardize this design layer across every BCube publication.

- Primary brand colours

- Secondary learning colours

- Semantic colours

- Neutral palette

- Accessibility contrast

### Compiler Output

Produces a normalized design specification describing page grid, component positions, spacing rules, typography hierarchy and template identifiers for downstream engines.

### Acceptance Criteria

All pages exhibit consistent layout, visual hierarchy, spacing, component placement and design language regardless of book or subject.

## 7. Iconography Standards

Objective: Standardize this design layer across every BCube publication.

- Simple rounded icons

- Consistent stroke width

- Meaningful symbols

- No decorative-only icons

### Compiler Output

Produces a normalized design specification describing page grid, component positions, spacing rules, typography hierarchy and template identifiers for downstream engines.

### Acceptance Criteria

All pages exhibit consistent layout, visual hierarchy, spacing, component placement and design language regardless of book or subject.

## 8. Template System

Objective: Standardize this design layer across every BCube publication.

- Cover template

- Activity template

- Assessment template

- Certificate template

- Review template

- Story template

### Compiler Output

Produces a normalized design specification describing page grid, component positions, spacing rules, typography hierarchy and template identifiers for downstream engines.

### Acceptance Criteria

All pages exhibit consistent layout, visual hierarchy, spacing, component placement and design language regardless of book or subject.

## 9. Responsive Composition Rules

Objective: Standardize this design layer across every BCube publication.

- Balance illustration and activity

- Reserve response space

- Protect safe zones

- Avoid overlap

### Compiler Output

Produces a normalized design specification describing page grid, component positions, spacing rules, typography hierarchy and template identifiers for downstream engines.

### Acceptance Criteria

All pages exhibit consistent layout, visual hierarchy, spacing, component placement and design language regardless of book or subject.

## 10. Design Validation

Objective: Standardize this design layer across every BCube publication.

- Alignment

- Spacing

- Readability

- Brand consistency

- Template compliance

- Print readiness

### Compiler Output

Produces a normalized design specification describing page grid, component positions, spacing rules, typography hierarchy and template identifiers for downstream engines.

### Acceptance Criteria

All pages exhibit consistent layout, visual hierarchy, spacing, component placement and design language regardless of book or subject.

## Standard Design Tokens

| Token | Purpose | Example |
| --- | --- | --- |
| SP-8 | Base spacing | 8 mm |
| GRID-12 | Layout grid | 12-column |
| TITLE-H1 | Primary title | Page title |
| ACT-ZONE | Activity area | Tracing/Matching |
| ILLUS-PRIMARY | Main illustration | 45–60% page |
| FOOTER-STD | Footer | Page number |

## Compiler Sequence

Publishing Engine™ → Design Engine™ → Visual Grammar Engine™ → Educational Engine™ → Teaching Engine™ → Illustration Engine™ → QA Engine™ → Prompt Compiler™

## Phase 2 Deliverables

- BCube Design Language™ specification

- Grid system

- Component library

- Template library

- Design tokens

- Visual hierarchy rules

- Layout validation checklist

- Compiler-ready design block


---

## Normative expansion from `BCube_Prompt_Engine_v3_Complete_Production_Standard_Master_Part_4.docx`

## Purpose

This part expands the Design Engine™ into a normative engineering specification. It defines reusable layout rules, design tokens, grid behavior, spacing, typography application, component placement and validation requirements.

### DE-GRID-001

Requirement: Every page SHALL be based on an approved BCube layout grid.

Rationale: Creates consistent, reusable page structures across every BCube publication.

Inputs: Publishing metadata, template ID, design tokens, page type.

Outputs: Resolved layout, component positions, spacing and typography metadata.

Validation: Check grid alignment, spacing consistency, template compliance and hierarchy.

Compiler Impact: Provides normalized design instructions for downstream engines.

### DE-GRID-002

Requirement: Components MUST snap to the defined grid and spacing tokens.

Rationale: Creates consistent, reusable page structures across every BCube publication.

Inputs: Publishing metadata, template ID, design tokens, page type.

Outputs: Resolved layout, component positions, spacing and typography metadata.

Validation: Check grid alignment, spacing consistency, template compliance and hierarchy.

Compiler Impact: Provides normalized design instructions for downstream engines.

### DE-HIER-001

Requirement: A page SHALL have one dominant visual hierarchy.

Rationale: Creates consistent, reusable page structures across every BCube publication.

Inputs: Publishing metadata, template ID, design tokens, page type.

Outputs: Resolved layout, component positions, spacing and typography metadata.

Validation: Check grid alignment, spacing consistency, template compliance and hierarchy.

Compiler Impact: Provides normalized design instructions for downstream engines.

### DE-COMP-001

Requirement: Every page SHALL use only approved UI/page components.

Rationale: Creates consistent, reusable page structures across every BCube publication.

Inputs: Publishing metadata, template ID, design tokens, page type.

Outputs: Resolved layout, component positions, spacing and typography metadata.

Validation: Check grid alignment, spacing consistency, template compliance and hierarchy.

Compiler Impact: Provides normalized design instructions for downstream engines.

### DE-SPC-001

Requirement: Whitespace MUST preserve readability and activity usability.

Rationale: Creates consistent, reusable page structures across every BCube publication.

Inputs: Publishing metadata, template ID, design tokens, page type.

Outputs: Resolved layout, component positions, spacing and typography metadata.

Validation: Check grid alignment, spacing consistency, template compliance and hierarchy.

Compiler Impact: Provides normalized design instructions for downstream engines.

### DE-TOK-001

Requirement: Only approved BCube design tokens MAY be used.

Rationale: Creates consistent, reusable page structures across every BCube publication.

Inputs: Publishing metadata, template ID, design tokens, page type.

Outputs: Resolved layout, component positions, spacing and typography metadata.

Validation: Check grid alignment, spacing consistency, template compliance and hierarchy.

Compiler Impact: Provides normalized design instructions for downstream engines.

### DE-TEMP-001

Requirement: Each page SHALL inherit an approved template profile.

Rationale: Creates consistent, reusable page structures across every BCube publication.

Inputs: Publishing metadata, template ID, design tokens, page type.

Outputs: Resolved layout, component positions, spacing and typography metadata.

Validation: Check grid alignment, spacing consistency, template compliance and hierarchy.

Compiler Impact: Provides normalized design instructions for downstream engines.

### DE-TYPE-001

Requirement: Typography SHALL follow BCube hierarchy and readability rules.

Rationale: Creates consistent, reusable page structures across every BCube publication.

Inputs: Publishing metadata, template ID, design tokens, page type.

Outputs: Resolved layout, component positions, spacing and typography metadata.

Validation: Check grid alignment, spacing consistency, template compliance and hierarchy.

Compiler Impact: Provides normalized design instructions for downstream engines.

### DE-RESP-001

Requirement: Layouts MUST preserve protected activity zones.

Rationale: Creates consistent, reusable page structures across every BCube publication.

Inputs: Publishing metadata, template ID, design tokens, page type.

Outputs: Resolved layout, component positions, spacing and typography metadata.

Validation: Check grid alignment, spacing consistency, template compliance and hierarchy.

Compiler Impact: Provides normalized design instructions for downstream engines.

### DE-VAL-001

Requirement: Design validation MUST complete before Visual Grammar compilation.

Rationale: Creates consistent, reusable page structures across every BCube publication.

Inputs: Publishing metadata, template ID, design tokens, page type.

Outputs: Resolved layout, component positions, spacing and typography metadata.

Validation: Check grid alignment, spacing consistency, template compliance and hierarchy.

Compiler Impact: Provides normalized design instructions for downstream engines.

## Design Token Catalogue

| Token | Purpose | Default |
| --- | --- | --- |
| GRID-12 | Layout grid | 12-column |
| SPACE-08 | Base spacing | 8 mm |
| SPACE-16 | Section spacing | 16 mm |
| TITLE-H1 | Primary heading | Page title |
| BODY-01 | Instruction text | Child readable |
| ACT-AREA | Activity region | Protected |
| SAFE-ZONE | Live content | Mandatory |

## Design Anti-Patterns

- Components floating off-grid

- Inconsistent spacing between pages

- Multiple competing headlines

- Decorative elements inside activity zones

- Typography overlapping illustrations

- Unapproved colours or icons

## Cross References

Related specifications: PE-LAY-001, VG-FOC-001, EE-OBJ-001, QA-DES-001.

## Next Expansion

Subsequent revisions will expand each Design Engine™ rule with diagrams, parameter tables, examples, edge cases, validation algorithms and reusable compiler fragments.
