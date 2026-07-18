# BCube EduOS v1.0

Status: **Phase 1 foundation complete**

BCube EduOS is the deterministic publishing layer for BCube preschool books. It extends the existing v3 production prompts and the locked v4 governance rules; it does not replace curriculum sources.

## Non-negotiable architecture

`Repository source -> Page manifest -> Asset resolver -> Deterministic composer -> QA validator -> Export`

AI may generate illustration assets only. AI must not control final typography, logo placement, page geometry, page numbering, or release approval.

## Phase 1 modules

- `config/eduos.yaml` — system-wide production settings
- `schemas/page-manifest.schema.json` — machine-readable page contract
- `src/manifest_validator.py` — manifest and governance validation
- `src/page_composer.py` — deterministic A4 composition entry point
- `src/qa_engine.py` — critical rejection gates and weighted scoring
- `examples/communication-champions-cover.json` — reference manifest
- `tests/test_phase1.py` — executable smoke tests

## Compatibility

Canonical curriculum remains in `production-prompts/`. Founder-locked production governance remains in `BCube_Gold_Production_v4/`.

## Acceptance rule

A page is releasable only when:

1. all critical checks pass;
2. the QA score is at least 95/100;
3. the official logo is composited from an approved asset;
4. exactly one flat A4 portrait page is produced;
5. visible wording and identity match the canonical source.

## Run locally

```bash
python eduos/src/manifest_validator.py eduos/examples/communication-champions-cover.json
python eduos/src/qa_engine.py eduos/examples/communication-champions-cover.json
python -m unittest eduos/tests/test_phase1.py
```
