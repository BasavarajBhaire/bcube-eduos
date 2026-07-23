# BCube Publishing Engine™ — Phase 5

Phase 5 provides the commercial portfolio orchestration layer above the Phase 4 release gate.

## Capabilities

- Resumable publishing for one book, one level, or all 30 registered books.
- Fail-fast or continue-on-error execution.
- Review-only or approved-and-locked releases.
- Release integrity verification using PDF, manifest, lock, and ZIP SHA-256 evidence.
- Deterministic Nursery, LKG, UKG, or all-level catalog bundles.
- Machine-readable run state and catalog reports.

## Publish one approved book

```bash
python scripts/bcube_publish_portfolio.py \
  --level nursery \
  --book communication-champions \
  --approve \
  --reviewer "Basavaraj Bhaire"
```

## Resume a portfolio run

```bash
python scripts/bcube_publish_portfolio.py \
  --level all \
  --approve \
  --reviewer "Basavaraj Bhaire" \
  --resume \
  --continue-on-error
```

## Verify a release

```bash
python scripts/bcube_verify_release.py \
  --release-dir production-releases/nursery/communication-champions/v4
```

## Build a complete catalog

```bash
python scripts/bcube_bundle_catalog.py --level all --require-all
```

The orchestrator is fail-closed. A book cannot be marked PASS when its Phase 4 release command or Phase 5 integrity verification fails.
