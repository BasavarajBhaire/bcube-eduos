# BCube Asset Registry™ Specification

## Purpose

The Asset Registry is the governed catalogue for reusable BCube production assets.

## Asset types

- brand
- publisher
- character
- template
- rule
- prompt fragment
- illustration style
- typography system
- colour system
- logo
- validation profile
- build profile
- model profile

## Canonical asset record

```yaml
id: STAR-001
type: character
version: 1.0.0
status: active
owner: Character Engine
dependencies: []
source: characters/star.character.json
protectedFields:
  - canonicalAppearance
  - forbiddenChanges
validationProfile: GOLD
```

## Requirements

- Asset IDs MUST be unique and immutable.
- Every active asset MUST have a semantic version.
- Dependencies MUST resolve before compilation.
- Protected fields MUST NOT be overridden by page data.
- Deprecated assets MUST identify a replacement or migration path.
- The compiler MUST record every resolved asset version in the compilation manifest.

## Lifecycle

Draft → Review → Approved → Active → Superseded → Deprecated → Archived

## Compilation rule

Registry records are internal. Final image prompts MUST contain expanded asset instructions and MUST NOT expose registry IDs or unresolved references.
