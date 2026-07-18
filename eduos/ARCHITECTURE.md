# BCube EduOS 1.0 Architecture

Status: **Governing architecture**

BCube EduOS is a deterministic educational operating system that converts approved learning outcomes into governed print and digital learning experiences.

## Scope

EduOS governs:

- knowledge models,
- books, chapters and pages,
- versioned templates,
- immutable assets,
- AI-assisted illustration generation,
- deterministic page composition,
- quality gates,
- release and export.

EduOS does not replace canonical curriculum sources. Curriculum authority remains in `production-prompts/`; founder-locked publishing rules remain in `BCube_Gold_Production_v4/`.

## Platform principles

1. **Repository is the source of truth.**
2. **AI is a worker, never the authority.**
3. **Final layout is deterministic.**
4. **Every reusable object is versioned.**
5. **Published releases are immutable.**
6. **Unknown or unresolved inputs fail closed.**
7. **Any critical defect blocks release regardless of score.**
8. **Every milestone must be executable, testable and tied to a known failure mode.**

## Core engines

### 1. Knowledge Engine
Owns skills, competencies, learning outcomes, prerequisites, progression and evidence.

### 2. Publishing Engine
Owns books, chapters, page manifests, templates, layout and composition.

### 3. Content Engine
Owns stories, activities, worksheets, assessments, parent guidance and teacher guidance.

### 4. Asset Engine
Owns approved logos, characters, scenes, icons, decorations and activity masters.

### 5. AI Orchestration Engine
Routes illustration-only work to supported models and records model, prompt, seed, version and validation evidence.

### 6. Quality and Release Engine
Runs schema validation, asset resolution, geometry checks, QA scoring, regression checks and release gating.

### 7. Experience Engine
Evaluates age appropriateness, visual balance, cognitive load, playfulness, emotional safety and engagement.

## Canonical flow

`Learning outcome -> Content package -> Page manifest -> Template resolution -> Asset resolution -> Illustration generation -> Deterministic composition -> QA -> Regression -> Release -> Export`

## Ownership boundaries

- Knowledge Engine decides **what must be learned**.
- Content Engine decides **what activity or content demonstrates learning**.
- Publishing Engine decides **how the page is structured**.
- Asset Engine decides **which approved visual assets are allowed**.
- AI Orchestration may create **new candidate illustration assets only**.
- Quality and Release Engine decides **whether output may be released**.

No engine may silently assume the responsibility of another.

## Versioning

All templates, schemas, manifests, assets, character definitions, QA rules and releases use semantic versioning.

- Patch: defect correction without approved visual or behavioural change.
- Minor: backward-compatible capability addition.
- Major: incompatible or founder-approved identity, structure or behaviour change.

## Release invariants

A release is valid only when:

- all referenced IDs resolve exactly,
- all checksums match,
- all critical validations pass,
- QA score is at least 95/100,
- the output is reproducible from recorded inputs,
- release artifacts are immutable.

## Architecture governance

Significant architectural decisions require an Architecture Decision Record under `eduos/adr/`. Accepted ADRs are binding until replaced by a newer ADR.
