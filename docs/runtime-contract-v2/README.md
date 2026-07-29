# BCube Runtime Contract V2 starter update

This package establishes the contract and renderer architecture required to fix the Early Maths pages without generic fallback.

## Included

- `runtime-contracts/schema/bcube-page-runtime-contract-v2.schema.json`
- `bcube-publishing-sdk/composer/crop_engine.py`
- `bcube-publishing-sdk/composer/runtime_validation.py`
- `bcube-publishing-sdk/composer/renderer_registry.py`
- `bcube-publishing-sdk/composer/renderers/early_maths.py`

## Required integration

1. Import `renderers.early_maths` from the runtime composer so registrations occur.
2. Validate each page with `validate_page_contract` before rendering.
3. Dispatch by `activity.render_kind` using `get_renderer`.
4. Pass a rendering context object that exposes the page-specific drawing methods referenced in `early_maths.py`.
5. Recompile Early Maths contracts into the V2 shape. Do not guess crop coordinates in the renderer.

## Fail-closed rules

- No renderer registration: fail.
- Missing crop: fail.
- Crop outside source image: fail.
- Asset list and crop keys mismatch: fail.
- Generic response panel, Home Connection or Parent Panel enabled: fail.
- Contract status not READY: fail.

This is the architectural foundation. The exact per-page crop coordinates and mechanics payload still need to be populated from the approved workbook/page prompts.
