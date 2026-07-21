# Stage 2 — Illustration Generation Pipeline v1.0

Stage 2 consumes the validated Stage 1 generation queue and produces deterministic illustration jobs for the BCube Nursery Gold series.

## Hard entry gate

Stage 2 must not submit artwork jobs unless Stage 1 reports:

- 10 official books
- 440 compiled prompts
- 440 `READY` queue entries
- 0 blocked or failed entries
- canonical prompt IDs matching `<CODE>-NURSERY-V5-P###`

Until that gate passes, Stage 2 may run only in validation or dry-run mode.

## Responsibilities

1. Read the Stage 1 generation queue and compiled prompt manifests.
2. Create one immutable artwork job per page.
3. Preserve book, page, prompt ID, prompt hash and source commit traceability.
4. Support resumable execution and idempotency by `prompt_id + prompt_sha256`.
5. Store provider-neutral request and response manifests.
6. Never overwrite an approved artwork asset.
7. Send generated pages to Stage 3 Visual QA; generation does not imply publication approval.

## Output layout

```text
pipeline/stage2-illustration-generation/output/
├── jobs.jsonl
├── stage2-manifest.json
├── validation-report.json
└── books/<slug>/P001/
    ├── request.json
    ├── response.json
    └── artwork.png
```

Binary artwork is expected to be stored as workflow artifacts or external object storage rather than committed for every pipeline run. Metadata and approval manifests remain version controlled.

## Execution modes

- `validate`: verify the Stage 1 gate and source integrity.
- `dry-run`: create all provider-neutral job manifests without invoking an image provider.
- `generate`: invoke the configured provider adapter after secrets and storage are configured.

## Release boundary

Stage 2 is complete only when all 440 pages have generated assets and provider response manifests. Human visual review, typography/layout inspection, prepress and publisher sign-off remain later gates.
