# BCube Book Production Workflow

## Operating mode

Repository-driven work mode. Chat instructions may start or stop a run, but may not redefine curriculum or page structure.

## Book run

A book run consumes one canonical manifest and produces one image per job.

### Stage 1 — Source validation

For each manifest entry:

- Open the release README.
- Confirm page number, prompt ID and exact title.
- Open the page Markdown.
- Open the page JSON.
- Fail immediately if identity fields disagree.

### Stage 2 — Job compilation

Compile a page job containing only:

- canonical metadata,
- exact visible wording,
- exact objective,
- exact child action,
- exact teacher move,
- exact parent connection,
- exact illustration scene,
- exact response space,
- page-specific prohibitions,
- global print geometry,
- official-logo reservation.

No information may be inferred from a previous generated page.

### Stage 3 — Artwork generation

- Generate exactly one A4 portrait page.
- Do not generate the BCube logo.
- Do not create multiple variants.
- Do not create an overview, collage or contact sheet.
- Do not add text or sections absent from the compiled job.

### Stage 4 — QA

Critical checks:

1. Correct book, level, page, prompt ID and title.
2. Exactly one page in the output image.
3. Exact required visible wording.
4. Required scene and characters.
5. Required activities and response spaces only.
6. All page prohibitions respected.
7. No generated or altered logo.
8. A4 portrait and safe margins.
9. No critical defect.

Any failure sets status to `qa-failed`; the page cannot be approved.

### Stage 5 — Output

- File: `<PROMPT_ID>.png`
- Directory: manifest `output_directory`
- Status progression: `queued` → `source-validated` → `generating` → `generated` → `approved`
- A failed page becomes `qa-failed` and is regenerated from the same source package.

## Communication Champions first run

Manifest:

`BCube_Gold_Production_v4/manifests/nursery/communication-champions.json`

Expected output count: 41 standalone PNG pages.

Validation occurs after the full first book is produced. No other book begins until this run is reviewed and accepted.
