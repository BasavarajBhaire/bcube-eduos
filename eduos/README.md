# BCube EduOS v1.0

Status: **Platform architecture, versioned templates, immutable assets and composer preflight implemented**

BCube EduOS is the deterministic educational and publishing layer for BCube preschool products. It extends the existing v3 production prompts and the locked v4 governance rules; it does not replace curriculum sources.

## Governing architecture

- `ARCHITECTURE.md` — platform scope, engines, ownership boundaries, versioning and release invariants
- `adr/` — binding Architecture Decision Records explaining why core rules exist

## Non-negotiable architecture

`Learning outcome -> Content package -> Page manifest -> Versioned template -> Versioned assets -> Illustration candidate -> Deterministic composer -> QA -> Regression -> Release -> Export`

AI may generate candidate illustration assets only. AI must not control final typography, logo placement, page geometry, page numbering, template selection, content authority or release approval.

## Implemented modules

- `config/eduos.yaml` — system-wide production settings
- `schemas/page-manifest.schema.json` — page contract requiring exact template and asset IDs
- `schemas/template-registry.schema.json` — machine-readable template-registry contract
- `schemas/asset-registry.schema.json` — machine-readable immutable-asset contract
- `registries/template-registry.json` — founder-locked versioned templates and coordinates
- `registries/asset-registry.json` — versioned asset lifecycle and checksum records
- `src/manifest_validator.py` — manifest and governance validation
- `src/template_registry.py` — fail-closed template resolution and inheritance
- `src/asset_registry.py` — GOLD-only asset resolution and SHA-256 verification
- `src/page_composer.py` — deterministic composer with mandatory template-and-asset preflight
- `src/qa_engine.py` — critical rejection gates and weighted scoring
- `examples/communication-champions-cover.json` — reference manifest using immutable IDs
- `tests/test_phase1.py` — executable foundation smoke tests
- `tests/test_template_registry.py` — template versioning and fail-closed tests
- `tests/test_asset_registry.py` — immutable-asset and checksum tests
- `tests/test_composer_preflight.py` — integrated template-and-asset preflight tests
- `MILESTONE_TEMPLATE_VERSIONING.md` — semantic-version and reproducibility rules
- `MILESTONE_IMMUTABLE_ASSET_ENGINE.md` — immutable-asset rules
- `MILESTONE_COMPOSER_PREFLIGHT.md` — integrated composition gates

## Accepted architecture decisions

1. Repository sources are authoritative.
2. AI is limited to candidate illustration generation.
3. Approved assets are versioned and immutable.
4. Final page layout is template-driven.
5. Release gates fail closed.

## Versioned reference rules

Every page manifest must reference exact immutable IDs, for example:

- template: `COVER_V1.0.0`
- logo: `LOGO_BCUBE.PRIMARY.V1.0.0`
- character: `STAR.WELCOME.V1.0.0`

Aliases such as `cover`, `latest`, `current`, raw file paths or descriptive character names are prohibited. Published manifests are never silently upgraded.

## Compatibility

Canonical curriculum remains in `production-prompts/`. Founder-locked production governance remains in `BCube_Gold_Production_v4/`.

## Acceptance rule

A page is releasable only when:

1. all critical checks pass;
2. the QA score is at least 95/100;
3. the official logo is composited from an approved immutable asset;
4. exactly one flat A4 portrait page is produced;
5. visible wording and identity match the canonical source;
6. an exact versioned template resolves successfully;
7. all template regions remain inside the locked A4 canvas;
8. all referenced assets resolve with matching SHA-256 checksums;
9. template page type matches the manifest page type;
10. the release records the canonical source commit.

## Run locally

```bash
python eduos/src/manifest_validator.py eduos/examples/communication-champions-cover.json
python eduos/src/template_registry.py COVER_V1.0.0
python eduos/src/asset_registry.py LOGO_BCUBE.PRIMARY.V1.0.0
python eduos/src/page_composer.py eduos/examples/communication-champions-cover.json
python eduos/src/qa_engine.py eduos/examples/communication-champions-cover.json
python -m unittest eduos/tests/test_phase1.py
python -m unittest eduos/tests/test_template_registry.py
python -m unittest eduos/tests/test_asset_registry.py
python -m unittest eduos/tests/test_composer_preflight.py
```

The current real cover manifest is expected to fail composer preflight until the official logo and all cover assets have verified SHA-256 values and `GOLD` status.
