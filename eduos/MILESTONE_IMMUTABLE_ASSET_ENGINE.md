# Milestone: Immutable Asset Engine

Status: **Implemented — checksum activation pending for the official logo**

## Failure prevented

This milestone prevents generated or silently modified logos, characters, scenes and activity assets from entering released pages.

## Release contract

An asset may be resolved only when all conditions are true:

1. the manifest references an exact versioned `asset_id`;
2. the asset exists in `asset-registry.json`;
3. its lifecycle status is `GOLD`;
4. it has a verified SHA-256 checksum;
5. the repository file exists;
6. the computed SHA-256 equals the registry value;
7. all declared dependencies resolve successfully.

Any failure blocks page composition.

## Important integrity correction

The official logo currently remains in `REVIEW` status because its Git blob SHA is known but its SHA-256 has not yet been calculated by the local or CI runtime. EduOS deliberately fails closed rather than treating a Git blob SHA or an invented value as a SHA-256 checksum.

After the runtime calculates the real SHA-256, the registry may be updated to `GOLD` through a reviewed commit.

## Commands

```bash
python eduos/src/asset_registry.py LOGO_BCUBE.PRIMARY.V1.0.0
python -m unittest eduos/tests/test_asset_registry.py
```

## Versioning

- Patch: metadata correction without changing bytes.
- Minor: new compatible variant or pose.
- Major: visible redesign or breaking usage change requiring Founder approval.
- Existing versions are never overwritten.
