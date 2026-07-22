# BCube Template Lock and Render QA

Status: PRE-PRINT PILOT

This layer closes the gap between a valid production prompt and a valid rendered page.

## Mandatory production flow

1. Read the exact individual V4 page package from `main`.
2. Resolve the page type and locked reference contract.
3. Generate only the page-specific illustration layer.
4. Compose official assets, editable typography, badges, panels and footer deterministically.
5. Produce one flat A4 PNG at 2480 × 3508 px and 300 DPI.
6. Run `scripts/validate_rendered_page.py` using a page QA manifest.
7. Accept only a 100/100 PASS with zero critical defects.

Direct full-page image-model output is prohibited for production pages.

## Why prompt QA was insufficient

Prompt QA proves that instructions exist. It does not prove that a rendered PNG follows them. Render QA therefore validates the artifact itself and requires explicit visual confirmation for every required and prohibited component.

## Locked page families

- Cover
- About This Book
- Publisher / Copyright
- Contents
- Back Cover

The reference registry is book-agnostic. Book-specific names, taglines, modules, lesson titles, page numbers and illustrations are injected through composition manifests.

## Fail-closed policy

A render fails when any required component is missing, any prohibited component is present, an official asset cannot be hash-verified, the page geometry is wrong, DPI metadata is missing, content differs from the individual page package, or any visual check is unresolved.

## Repository gate

`.github/workflows/validate-rendered-pages.yml` validates the engine and every committed production render manifest. A failed render must not be described as production-ready or merged.
