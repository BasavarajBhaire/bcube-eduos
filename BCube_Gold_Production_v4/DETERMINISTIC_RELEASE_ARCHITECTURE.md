# Deterministic Hybrid Production Architecture

## Decision

BCube books use a hybrid model, but **AI is permitted only in authoring**. It is never part of a release build.

1. **Authoring** — people may create or revise an illustration with AI or design tools.
2. **Composition** — the illustration is placed in a versioned page template with canonical text.
3. **Approval** — a reviewer compares the rendered page with its canonical source package and records every required QA check.
4. **Locking** — the approved full page becomes an immutable, hash-addressed golden PNG.
5. **Release** — the build copies locked pages byte-for-byte in manifest order and creates a deterministic ZIP.

This keeps authoring flexible while making repeated releases identical.

## Sources of truth

- `manifests/<level>/<book>.release-v4.json` — exact 44-page physical order, identity, numbering, source package, template and filename for each book.
- `templates/template-registry.v1.json` — canvas, safe areas, layer order, fit mode and brand placement contracts.
- `approved-assets/brand/asset-lock.json` — approved logo and Star mascot hashes.
- `approved-assets/<level>/<book>/asset-lock.json` — approved golden-page hashes.
- `schemas/qa-record.schema.json` — minimum human semantic review contract.

Every release manifest maps 41 curriculum source packages to 44 physical pages by adding About This Book, splitting Contents into Parts 1 and 2, and adding an unnumbered back cover. It does not invent new curriculum. New books must be scaffolded with `scripts/create-book-release-framework.py`; manual page renumbering is prohibited.

## Fail-closed workflow

From `BCube_Gold_Production_v4`:

```bash
python3 scripts/validate-deterministic-release.py --mode manifest
python3 scripts/validate-deterministic-release.py --mode manifest \
  --manifest manifests/nursery/confidence-builders.release-v4.json \
  --asset-lock approved-assets/nursery/confidence-builders/asset-lock.json
python3 scripts/promote-approved-page.py CC-NURSERY-V4-P017 candidate.png \
  --reviewer "Reviewer name" --source-package-version 4.0.0 \
  --qa-record qa/CC-NURSERY-V4-P017.json --founder-approved
python3 scripts/validate-deterministic-release.py --mode release
python3 scripts/build-deterministic-release.py --release-id CC-NURSERY-V4-2026-07-20
python3 scripts/build-deterministic-release.py --release-id CB-NURSERY-V4-2026-07-20 \
  --manifest manifests/nursery/confidence-builders.release-v4.json \
  --asset-lock approved-assets/nursery/confidence-builders/asset-lock.json
```

A missing asset, changed hash, wrong dimension, wrong page count or failed QA record blocks the build.

## Non-negotiable rules

- One physical page per PNG; contact sheets are previews only and never release assets.
- Canvas is 2480 × 3508 px at the locked portrait aspect ratio.
- No automatic crop, generative fill or illustration substitution in release mode.
- The official logo and Star mascot are files, not prompts or extractions from earlier pages.
- Page text comes from the canonical source package, not the image generator.
- Replacing an approved page requires an explicit retirement/version change.
- A release build has no network dependency and invokes no image generation model.

## Why the earlier rebuild changed

The repository described a hybrid approach but did not enforce its boundary. Generated illustrations were treated as reproducible inputs, page mappings still depended on 41 legacy entries, asset identities were not hash-locked, and validation checked filenames/count rather than semantic scene requirements. A rebuild was therefore a new creative generation run. This architecture closes those gaps.
