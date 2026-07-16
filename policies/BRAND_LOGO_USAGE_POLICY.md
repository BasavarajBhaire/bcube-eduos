# BCube Logo Usage Policy

## Policy ID
`POLICY-BRAND-LOGO-001`

## Governed Asset
`BRAND-LOGO-001`

## Mandatory Rules

1. Use only the approved BCube Academy master logo or a governed derivative registered as a variant.
2. Preserve the original aspect ratio.
3. Do not stretch, skew, rotate, recolour, redraw, crop or apply shadows, glows, outlines or effects.
4. Keep the logo fully inside the print-safe zone.
5. Maintain clear space around the logo; no text, border, mascot, illustration or decorative element may overlap it.
6. Interior workbook pages place the logo at the top-left unless a governed template explicitly defines another placement.
7. Cover placement is controlled by the selected cover template.
8. The logo must remain recognisable at final print size.
9. The age badge is not part of the logo and must not be attached to it.
10. Image-generation prompts must describe the approved logo placement and preservation rules explicitly; internal asset IDs must not be sent to the image model.

## Hard Failures

- Missing required logo
- Wrong or unrelated logo
- Distorted proportions
- Recoloured logo
- Cropped logo
- Logo outside safe margins
- Illustration or text overlapping the logo
- Placeholder text used instead of the official binary asset during page assembly

## Compiler Expansion

The final production prompt shall include:

> Place the official BCube Academy full-colour logo at the top-left, preserve its exact original proportions and colours, keep it fully inside the safe margin with clear space around it, and do not redraw, distort, recolour, crop or decorate it.

## Runtime Rule

The runtime should prefer deterministic post-generation logo placement using the governed binary asset. AI-rendered approximations are not acceptable for final publication when compositing is available.
