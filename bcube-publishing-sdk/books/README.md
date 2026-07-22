# Book-Driven Nursery Cover Pipeline

The smart cover command generates page data automatically from `nursery-books.json`.

## First run: compose a review candidate

```bash
python scripts/run_bcube_cover_pipeline.py \
  --book confidence-builders \
  --illustration "D:/BCube/illustrations/confidence-builders-cover.png" \
  --confirm-clean-illustration
```

The command:

1. validates and stages the illustration under `production-renders/illustrations/`;
2. finds the first readable approved logo and Star candidate registered in `nursery-books.json`;
3. creates `production-renders/page-data/CB-NURSERY-V4-P001.json`;
4. composes the deterministic cover candidate;
5. creates an evidence manifest;
6. stops before production QA so the candidate can be reviewed.

Default candidate output:

```text
production-renders/pages/CB-NURSERY-V4-P001.png
```

## Second run: approve and run final QA

After inspecting the candidate:

```bash
python scripts/run_bcube_cover_pipeline.py \
  --book confidence-builders \
  --illustration "D:/BCube/illustrations/confidence-builders-cover.png" \
  --confirm-clean-illustration \
  --approve \
  --reviewer "Basavaraj Bhaire"
```

A production page is accepted only when evidence-based render QA returns PASS.

## Important

`--confirm-clean-illustration` is an explicit production assertion. Use it only when the supplied image contains no text, logo, mascot, age badge, skill panel, footer, or full-page book layout.
