# Communication Champions — Nursery Illustration QA

Version: v3.0 illustration pilot  
Pages reviewed: 1–5 of 41  
Approved logo: `assets/BCube_Academy_approved_logo.png`

## Decision

The visual direction is approved for continuation, but the generated raster pages are **not yet publication-ready**. Continue with a hybrid production workflow: generate illustration-only artwork, then assemble titles, instructions, response spaces, page numbers, and publication data deterministically at A4 print resolution.

## Validation summary

| Check | Result | Finding |
|---|---|---|
| Approved BCube logo | Pass | Exact supplied logo is visible on pages 1–5. |
| Visual style | Pass | White base, soft BCube palette, rounded outlines, inclusive preschool characters. |
| Star continuity | Pass | Yellow Star mascot with blue cape/scarf and blue shoes remains recognizable. |
| A4 aspect ratio | Pass | Generated images closely match A4 portrait proportions. |
| A4 300 DPI pixels | Fail | Outputs are approximately 1055×1491; final pages require 2480×3508 before bleed. |
| Colour space | Fail | Outputs are sRGB; final print package requires CMYK conversion and proofing. |
| Exact publication data | Source locked | © 2025; BCube Future Academy; 407, DSMAX Sky Supreme KST Bangalore - 560060; info@bcubefutureacademy.in; bcubefutureacademy.in; First Edition 2025. Existing pilot artwork still requires deterministic replacement. |
| Contents accuracy | Fail | Page 3 invents page ranges extending to page 51, while the book has 41 pages. |
| Exact typography | Conditional | Display headings are legible, but body text must be typeset using approved Poppins/Nunito fonts. |
| Safe area and binding | Conditional | Composition is generally safe; deterministic layout must enforce bleed, trim, safe and binding zones. |
| Activity clarity | Pass on pages 4–5 | Direct child action, teacher prompt, parent connection, and meaningful response language are visible. |

## Required production workflow

1. Generate artwork without body copy, page numbers, publication metadata, or fake logos.
2. Preserve the approved Star and classroom character reference system.
3. Build the final page at A4 210×297 mm with 3 mm bleed, 10 mm safe area and 12 mm binding allowance.
4. Place the supplied BCube logo as a locked asset wherever the prompt requests branding.
5. Typeset exact prompt-controlled wording in Poppins Bold and Nunito.
6. Export at 300 DPI, convert/proof in CMYK, and run Gold validation on every page.

## Status

**Pilot Gold QA: BLOCKED FOR PRINT, APPROVED FOR HYBRID REBUILD.**
