---
fragment_id: PF-PUB-001
title: Standard A4 Publishing Block
engine: Publishing
version: 3.0.0
status: Active
---

# PF-PUB-001 — Standard A4 Publishing Block

## Parameters

- `level`
- `page_type`
- `page_number`
- `binding_margin_mm` (default: 12)
- `safe_margin_mm` (default: 10)

## Compiler-ready fragment

> Create an A4 portrait educational workbook page at 210 × 297 mm trim size with 3 mm bleed, 300 DPI print resolution, a clean white or approved pastel background, {{safe_margin_mm}} mm safe margins, and a {{binding_margin_mm}} mm inside binding margin. Keep all essential text, faces, hands, learning objects, official branding, and child response spaces inside the live area. Reserve a clear title zone, protected activity zone, and consistent footer with page number {{page_number}}. Apply the approved visual-to-text ratio for {{level}} and the approved layout behavior for page type {{page_type}}.

## Dependencies

- `PE-GEO-001`
- `PE-GEO-002`
- approved page template

## Validation

- all parameters resolve
- level is supported
- page number is valid
- safe margin is at least 8 mm
- binding margin is at least 12 mm for standard bound books

## Example

`level=Nursery 3+`, `page_type=Activity`, `page_number=12`

## Change history

- 3.0.0 — Initial active fragment.
