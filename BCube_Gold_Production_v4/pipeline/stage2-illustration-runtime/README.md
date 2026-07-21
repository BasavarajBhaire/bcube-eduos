# Stage 2 — Book-by-Book Illustration Runtime

This runtime executes illustration generation one official Nursery book at a time.

## Entry gate

A book may run only when Stage 1 provides exactly 44 compiled prompts with canonical IDs, unique page numbers, `READY` status, and no blocked records.

## Execution modes

- `validate` — verify the selected book and produce no provider calls.
- `dry-run` — build all 44 provider requests and manifests without generating binary assets.
- `generate` — call the configured provider adapter, store outputs, and create the Stage 2 handoff manifest.
- `resume` — skip already valid assets and retry only missing or failed pages.

## Book-by-book command

```bash
python BCube_Gold_Production_v4/pipeline/stage2-illustration-runtime/illustration_engine.py \
  --book communication-champions \
  --mode dry-run
```

Supported official slugs are loaded from `books/catalog.json`.

## Provider contract

A provider adapter receives a compiled prompt and returns image bytes plus provider metadata. The runtime is provider-neutral. The initial `http-json` adapter expects an HTTPS endpoint and credentials through environment variables; secrets are never committed.

Required environment variables for real generation:

- `BCUBE_IMAGE_PROVIDER_URL`
- `BCUBE_IMAGE_PROVIDER_TOKEN`

Optional:

- `BCUBE_IMAGE_MODEL`
- `BCUBE_IMAGE_TIMEOUT_SECONDS`
- `BCUBE_IMAGE_MAX_RETRIES`

## Output layout

```text
output/<book-slug>/
├── pages/P001.png ... P044.png
├── requests/
├── responses/
├── generation-manifest.json
├── failed-pages.json
└── stage2-summary.md
```

Every output record contains the canonical prompt ID, prompt SHA-256, output SHA-256, provider model, attempt count, UTC timestamps and status.

## Safety controls

- one book per run
- maximum 44 pages
- resumable and idempotent jobs
- exponential retry with bounded attempts
- no overwrite of a valid asset unless `--force` is supplied
- generation stops when Stage 1 inputs are incomplete
- binary artwork is uploaded as a workflow artifact rather than committed to Git

## Exit gate

A selected book passes Stage 2 only when all 44 pages are generated, uniquely mapped to P001–P044, have non-empty supported image files, and carry output hashes. The resulting manifest becomes the input to Stage 3 Visual QA.
