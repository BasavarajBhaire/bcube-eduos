# BCube Asset Resolver Contract

## Purpose

The Asset Resolver is the only supported interface between the compiler/runtime and governed assets. Compilers must not depend on repository file paths.

## Input

```json
{
  "assetUri": "eduos://brand/logo/master/1.0.0",
  "buildProfile": "PROFILE-GOLD-PRINT-001",
  "locale": "en-IN",
  "outputContext": "interior-workbook-page"
}
```

## Resolution Order

1. Validate URI syntax.
2. Load the exact version or apply the approved version range.
3. Verify lifecycle status.
4. Verify Gold-production eligibility.
5. Resolve declared dependencies recursively.
6. Select the correct representation or variant for the build profile.
7. Apply policies.
8. Return semantic expansion, binary reference, fingerprint and validation requirements.

## Output

```json
{
  "assetId": "BRAND-LOGO-001",
  "resolvedVersion": "1.0.0",
  "status": "approved",
  "semanticExpansion": "Place the official BCube Academy full-colour logo at the top-left...",
  "binaryPath": "assets/brand/logo/master/bcube-academy-master-logo.png",
  "fingerprint": "sha256:<value>",
  "policies": ["POLICY-BRAND-LOGO-001"],
  "validationProfile": "GOLD"
}
```

## Hard Failures

- Asset not found
- Ambiguous version
- Draft, deprecated or archived asset used for production
- Missing mandatory binary representation
- Broken dependency
- Unsupported output context
- Failed checksum
- Missing policy
- Unresolved placeholder

## Prompt Isolation

Asset IDs, URIs, paths and rule references are internal metadata. They must be removed before the final prompt reaches an image model. Only the fully expanded semantic instructions are emitted.

## Publication Rule

For brand assets such as logos, the resolver must make the original binary available to the page-assembly stage. Final production should composite the governed binary instead of relying on an AI model to reproduce the logo.
