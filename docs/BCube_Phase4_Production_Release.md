# BCube Publishing Engine — Phase 4 Production Release

Phase 4 converts validated 44-page rendered books into controlled commercial release packages.

## Capabilities

- strict physical-page validation for P001–P044
- duplicate, missing, unexpected, unreadable, size, and DPI defect detection
- required page-role checks for cover, front matter, certificate, and back cover
- per-page SHA-256 evidence
- deterministic print-ready PDF assembly
- release manifest with source branch and commit
- explicit reviewer approval state
- approval lock file
- ZIP release packaging
- portfolio QA across Nursery, LKG, and UKG

## Strict preflight

```bash
python scripts/bcube_preflight.py \
  --level nursery \
  --book communication-champions
```

A production preflight passes only when all 44 physical pages exist and every page is a readable 2480 × 3508 PNG at approximately 300 DPI.

## Review package

```bash
python scripts/bcube_release.py \
  --level nursery \
  --book communication-champions
```

Without `--approve`, the manifest state is `REVIEW_REQUIRED` and no release lock is created.

## Approved locked release

```bash
python scripts/bcube_release.py \
  --level nursery \
  --book communication-champions \
  --approve \
  --reviewer "Basavaraj Bhaire"
```

Approved output is written under:

```text
production-releases/<level>/<book>/v4/
```

The package contains:

- `<BOOK-ID>-PRINT-READY.pdf`
- `<BOOK-ID>.preflight.json`
- `<BOOK-ID>.assembly.json`
- `<BOOK-ID>.release.json`
- `<BOOK-ID>.release.lock`
- `<BOOK-ID>-RELEASE.zip`

## Portfolio QA

```bash
python scripts/bcube_portfolio_qa.py --level all
```

The portfolio report identifies every registered book, its rendered page count, pass/fail state, and actionable critical defects.

## Release gate

The release command is fail-closed. It does not assemble or package a production release when preflight reports any critical defect.
