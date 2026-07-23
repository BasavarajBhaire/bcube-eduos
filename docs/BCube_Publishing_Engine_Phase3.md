# BCube Publishing Engine — Phase 3

Phase 3 completes the book-production layer after covers, front matter, and activity pages.

## Components

- `compose_completion_pages.py`: certificate and back-cover composition.
- `run_bcube_completion_pipeline.py`: registry-driven completion-page generation.
- `build_bcube_book.py`: rendered-page validation and PDF assembly.
- `bcube_batch_publish.py`: multi-book and multi-level batch orchestration.

## Completion pages

```bash
python scripts/run_bcube_completion_pipeline.py \
  --level nursery \
  --book communication-champions \
  --page certificate

python scripts/run_bcube_completion_pipeline.py \
  --level nursery \
  --book communication-champions \
  --page back-cover
```

## Assemble a book

```bash
python scripts/build_bcube_book.py \
  --level nursery \
  --book communication-champions \
  --require-complete
```

`--require-complete` requires all physical pages P001–P044. Without it, the tool accepts a contiguous partial sequence for testing.

Outputs:

- `production-renders/books/<BOOK-ID>.pdf`
- `production-renders/books/<BOOK-ID>.manifest.json`

The manifest records page order, physical page numbers, image size, DPI, page SHA-256 values, PDF SHA-256, missing pages, and overall status.

## Batch publish

```bash
python scripts/bcube_batch_publish.py \
  --level nursery \
  --completion-pages \
  --require-complete
```

Use `--level all` to process Nursery, LKG, and UKG. Use `--book <slug>` to target one registered book.

## Validation rules

- A4 raster pages must be exactly 2480 × 3508 pixels.
- Page filenames must follow `<PREFIX>-<LEVEL>-V4-PNNN.png`.
- Duplicate physical page numbers fail.
- Non-contiguous sequences fail.
- Complete production builds require P001–P044.
- Certificate is generated as P043 and back cover as P044.
- The PDF page order follows physical page order.
