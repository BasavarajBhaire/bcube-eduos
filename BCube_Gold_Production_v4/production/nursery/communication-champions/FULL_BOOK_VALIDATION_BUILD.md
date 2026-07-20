# Communication Champions Nursery — Full v4 Validation Build

Status: COMPLETE FOR VISUAL VALIDATION

Build date: 2026-07-20

## Architecture

- 43 individual physical packages.
- P001: uncounted front cover.
- P002–P005: counted reader pages 1–4 with printed numbers hidden.
- P006–P043: reader pages 5–42 with visible sequential numbers.
- Legacy P015–P041 curriculum content maps to v4 P017–P043.

## Output contract

- Exactly 43 individual A4 portrait PNG files.
- Each page is 2480 × 3508 px at 300 DPI metadata.
- No contact sheet, montage or composite is included in the deliverable.
- The full archive is clean-extracted and every PNG is decoded before handoff.

## Builders

- P001–P016:
  BCube_Gold_Production_v4/scripts/build-cc-nursery-cover-to-page-15.py
- P017–P043:
  BCube_Gold_Production_v4/scripts/build-cc-nursery-pages-16-to-42.py

## Validation result

PASS: 43 extracted individual A4 PNG pages decoded at 2480 × 3508.

This is a visual-validation build. Commercial print approval still requires the
normal Gold QA, CMYK conversion, physical proof and Founder review gates.
