# AI Renderer Adapter Contract

## Purpose
Defines the model-agnostic interface used by BCube Prompt Runtime™ to submit a validated, self-contained Gold Production Prompt™ to any supported image-generation provider.

## Mandatory principle
Adapters MUST NOT receive modular rule references, unresolved variables, template IDs as instructions, or external dependencies. They receive only the final expanded prompt plus runtime metadata.

## Request contract
- `requestId`
- `promptFingerprint`
- `modelProfileId`
- `finalPrompt`
- `outputSize`
- `outputFormat`
- `seed` when supported
- `referenceAssets` when supported
- `safetyProfile`

## Response contract
- `requestId`
- `providerJobId`
- `status`
- `generatedAssets`
- `providerMetadata`
- `warnings`
- `errorCode`
- `errorMessage`

## Adapter responsibilities
1. Translate only provider-specific transport fields.
2. Preserve final prompt wording unless the model profile explicitly authorizes formatting changes.
3. Never omit exact text, branding, character identity, activity-space, or safety requirements.
4. Return generation metadata required for audit and regression testing.
5. Normalize provider failures into the runtime error model.

## Prohibited behaviour
- Summarizing the final prompt.
- Replacing explicit instructions with rule IDs.
- Silently removing negative constraints.
- Adding provider-specific creative interpretation.
- Retrying with modified content without a recorded runtime decision.

## Release gate
An adapter is production-ready only after passing contract, regression, metadata, and failure-handling tests.