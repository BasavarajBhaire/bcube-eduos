# BCube EduOS v1.0

Status: **Phase 1 foundation complete; template versioning milestone implemented**

BCube EduOS is the deterministic publishing layer for BCube preschool books. It extends the existing v3 production prompts and the locked v4 governance rules; it does not replace curriculum sources.

## Non-negotiable architecture

`Repository source -> Page manifest -> Versioned template -> Asset resolver -> Deterministic composer -> QA validator -> Export`

AI may generate illustration assets only. AI must not control final typography, logo placement, page geometry, page numbering, template selection, or release approval.

## Phase 1 modules

- `config/eduos.yaml` — system-wide production settings
- `schemas/page-manifest.schema.json` — machine-readable page contract
- `schemas/template-registry.schema.json` — machine-readable template-registry contract
- `registries/template-registry.json` — founder-locked versioned templates and page coordinates
- `src/manifest_validator.py` — manifest and governance validation
- `src/template_registry.py` — fail-closed template resolution and inheritance
- `src/page_composer.py` — deterministic A4 composition entry point
- `src/qa_engine.py` — critical rejection gates and weighted scoring
- `examples/communication-champions-cover.json` — reference manifest
- `tests/test_phase1.py` — executable foundation smoke tests
- `tests/test_template_registry.py` — template versioning and fail-closed tests
- `MILESTONE_TEMPLATE_VERSIONING.md` — semantic-version and reproducibility rules

## Versioned template rule

Every page manifest must reference an exact immutable template ID such as:

- `COVER_V1.0.0`
- `LESSON_V1.0.0`
- `TRACE_V1.0.0`
- `COLOR_V1.0.0`
- `MATCH_V1.0.0`

Aliases such as `cover`, `latest`, or `current` are prohibited. Published manifests are never silently upgraded to a newer template.

## Compatibility

Canonical curriculum remains in `production-prompts/`. Founder-locked production governance remains in `BCube_Gold_Production_v4/`.

## Acceptance rule

A page is releasable only when:

1. all critical checks pass;
2. the QA score is at least 95/100;
3. the official logo is composited from an approved asset;
4. exactly one flat A4 portrait page is produced;
5. visible wording and identity match the canonical source;
6. an exact versioned template resolves successfully;
7. all template regions remain inside the locked A4 canvas.

## Run locally

```bash
python eduos/src/manifest_validator.py eduos/examples/communication-champions-cover.json
python eduos/src/template_registry.py COVER_V1.0.0
python eduos/src/qa_engine.py eduos/examples/communication-champions-cover.json
python -m unittest eduos/tests/test_phase1.py
python -m unittest eduos/tests/test_template_registry.py
```
