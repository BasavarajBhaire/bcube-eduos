# BCube Asset Registry™ Index

This index is the authoritative catalog of reusable BCube assets. The registry stores maintainable source assets; the compiler expands approved assets into complete page-specific instructions before image generation.

## Non-negotiable rule

The image model MUST never receive registry IDs, module references, inheritance instructions, file paths, placeholders, or statements such as “use the common standard.” Every referenced asset MUST be resolved and expanded into explicit natural-language instructions in the final Gold Production Prompt™.

## Asset lifecycle

`draft → review → approved → gold-certified → deprecated → archived`

Only `approved` and `gold-certified` assets may be used in production compilation.

## Canonical categories

| Prefix | Asset type | Example |
| --- | --- | --- |
| CHAR | Character | `CHAR-STAR-001` |
| TPL | Template | `TPL-WORKBOOK-ACTIVITY-001` |
| RULE | Rule | `RULE-PC-SELF-001` |
| FRAG | Prompt fragment | `FRAG-PUB-PRINT-001` |
| BRAND | Brand profile | `BRAND-BCUBE-001` |
| LOGO | Logo asset | `LOGO-BCUBE-PRIMARY-001` |
| TYPE | Typography | `TYPE-PRESCHOOL-001` |
| LAYOUT | Layout | `LAYOUT-A4-WORKBOOK-001` |
| STYLE | Illustration style | `STYLE-PRESCHOOL-GOLD-001` |
| ACT | Activity pattern | `ACT-OBSERVE-SPEAK-001` |
| OBJ | Learning objective | `OBJ-COMM-GREETING-001` |
| RUBRIC | Assessment rubric | `RUBRIC-OBSERVATION-001` |
| TEACHER | Teacher persona | `TEACHER-FACILITATOR-001` |
| PARENT | Parent persona | `PARENT-HOME-PARTNER-001` |
| PROFILE | Build profile | `PROFILE-GOLD-PRINT-001` |

## Registry entry requirements

Every asset manifest must declare:

- immutable asset ID;
- semantic version;
- lifecycle status;
- accountable owner;
- dependencies with version ranges;
- validation profile;
- compiler expansion mode and source;
- source format and path;
- change timestamps.

## Dependency resolution

Dependencies are resolved before compilation. Missing, circular, deprecated, or incompatible dependencies are hard failures. Protected assets—official logo, publisher identity, exact page text, Star identity, copyright details and safety rules—cannot be overridden by page-level data.

## Production release gate

An asset is production-ready only when:

1. its manifest validates against `schemas/asset-manifest.schema.json`;
2. all required dependencies resolve;
3. its compiler expansion has no unresolved variables;
4. its validation suite passes;
5. its expansion is verified inside at least one complete page prompt;
6. the final prompt contains no asset IDs or external references.
