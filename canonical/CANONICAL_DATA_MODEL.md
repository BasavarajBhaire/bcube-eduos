# BCube Canonical Data Model

## Purpose

The Canonical Data Model (CDM) is the stable source-of-truth structure used by BCube EduOS™. Prompts, images, PDFs and other publication outputs are derived artifacts and MUST NOT replace canonical educational data.

## Entity hierarchy

Organization → Brand → Series → Book → Unit → Lesson → Page → Activity

## Core identifiers

- Organization: `ORG-BCUBE-001`
- Brand: `BRAND-BCUBE-001`
- Series: `SER-FUTURE-SKILLS-001`
- Book: `BOOK-{CODE}-{LEVEL}-{NNN}`
- Unit: `UNIT-{NN}`
- Lesson: `LESSON-{NN}`
- Page: `PAGE-{NNN}`
- Activity: `ACT-{NNN}`

Identifiers are immutable once published.

## Canonical page intent

A Page entity contains educational intent only:

- title
- page number
- learning objective
- competency
- activity
- teacher interaction
- child response
- parent connection
- illustration intent
- assessment evidence
- template reference
- character references

It MUST NOT contain reusable publishing, branding or character details that belong in registries.

## Derivation rule

Canonical data + registries + rules + template + build profile → Prompt IR → Gold Production Prompt™ → generated output.

## Governance

- Canonical data changes require version history.
- Generated prompts MUST record source entity versions.
- A generated prompt MUST be reproducible from the same canonical inputs.
- No AI-generated output may silently modify canonical educational intent.
