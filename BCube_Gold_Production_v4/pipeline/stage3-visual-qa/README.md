# Stage 3 — Visual QA and Regeneration Gate

Stage 3 validates illustration outputs produced by Stage 2 before page assembly or PDF generation.

## Entry gate

Stage 3 requires a Stage 2 manifest with canonical prompt IDs, one output record per requested page, output file references, generation status, provider metadata and prompt SHA-256 traceability.

## Automated checks

- A4 portrait dimensions and minimum production resolution
- file existence, format and readable image metadata
- canonical prompt ID and page-number agreement
- title, logo and required-page-element declarations
- safe-margin and crop-risk declarations
- page-type-specific requirements
- duplicate-output and missing-page detection
- deterministic linkage to Stage 1 prompt hash and Stage 2 job ID

Checks requiring computer vision, OCR, logo detection, character-consistency scoring or typography analysis are represented as provider adapters. They cannot be marked PASS unless their adapter returns evidence.

## Decisions

- `PASS`: all mandatory machine checks passed and no review blocker exists
- `REVIEW`: machine checks passed but one or more human or vision-review gates remain
- `REGENERATE`: recoverable illustration failure; page is added to the regeneration queue
- `BLOCKED`: missing upstream data, missing output or invalid traceability

## Outputs

- `output/stage3-manifest.json`
- `output/page-results.json`
- `output/regeneration-queue.json`
- `output/human-review-queue.json`
- `output/stage3-summary.md`

Stage 3 never claims publication readiness. Human visual approval, prepress proof and publisher sign-off remain mandatory.