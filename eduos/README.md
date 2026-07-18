# BCube EduOS v1.0

Status: **Architecture frozen; Runtime kernel and first Publisher CLI implemented**

BCube EduOS is the deterministic educational and publishing layer for BCube preschool products. It extends the existing v3 production prompts and the locked v4 governance rules; it does not replace curriculum sources.

## Governing documents

- `CONSTITUTION.md` — founder-locked scope, invariants and change-control rules
- `ARCHITECTURE.md` — platform scope, engines, ownership boundaries, versioning and release invariants
- `adr/` — binding Architecture Decision Records explaining why core rules exist

## Non-negotiable architecture

`Canonical source -> Page manifest -> EduOS Runtime -> Versioned template -> Versioned assets -> Deterministic composer -> QA -> Regression -> Release -> Export`

AI may generate candidate illustration assets only. AI must not control final typography, logo placement, page geometry, page numbering, template selection, content authority or release approval.

## Implemented modules

- `kernel/runtime.py` — fail-closed orchestration entry point
- `kernel/event_bus.py` — auditable runtime events
- `kernel/capability_registry.py` — explicit provider resolution
- `publisher/cli.py` — first executable BCube Publisher command
- `config/eduos.yaml` — system-wide production settings
- `schemas/page-manifest.schema.json` — page contract requiring exact template and asset IDs
- `schemas/template-registry.schema.json` — template-registry contract
- `schemas/asset-registry.schema.json` — immutable-asset contract
- `registries/template-registry.json` — founder-locked versioned templates and coordinates
- `registries/asset-registry.json` — versioned asset lifecycle and checksum records
- `src/manifest_validator.py` — manifest and governance validation
- `src/template_registry.py` — fail-closed template resolution and inheritance
- `src/asset_registry.py` — GOLD-only asset resolution and SHA-256 verification
- `src/page_composer.py` — deterministic composer with mandatory preflight
- `src/qa_engine.py` — critical rejection gates and weighted scoring
- `examples/communication-champions-cover.json` — reference manifest using immutable IDs
- `tests/test_runtime.py` — runtime orchestration and event tests
- `tests/test_publisher_cli.py` — Publisher CLI contract test
- `tests/test_phase1.py` — foundation smoke tests
- `tests/test_template_registry.py` — template fail-closed tests
- `tests/test_asset_registry.py` — immutable-asset and checksum tests
- `tests/test_composer_preflight.py` — integrated preflight tests

## Publisher command

The first product interface is intentionally narrow and strict:

```bash
python -m eduos.publisher.cli publish eduos/examples/communication-champions-cover.json --json
```

The command runs runtime preflight. It does not bypass unresolved assets, fabricate logos, silently switch templates or approve incomplete pages.

## Runtime execution order

1. Load manifest identity.
2. Resolve the exact versioned template.
3. Resolve and checksum-verify every referenced asset.
4. Enforce template/page-type compatibility.
5. Build the deterministic composition plan.
6. Emit auditable lifecycle events.
7. Stop immediately on any unresolved dependency.

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

## Current production blocker

The real Communication Champions cover remains correctly blocked until the official logo and cover illustration assets have verified SHA-256 values and `GOLD` status. The next implementation sprint is asset certification followed by deterministic rendering and PDF export.
