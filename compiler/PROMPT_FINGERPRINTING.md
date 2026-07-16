# Prompt Fingerprinting Standard

## Purpose

Every compiled BCube Gold Production Prompt™ must be traceable to the exact inputs that produced it.

## Fingerprint Inputs

The compiler shall calculate a deterministic fingerprint from:

- compiler version;
- book metadata version;
- page metadata version;
- rule library version;
- template version;
- character profile versions;
- illustration profile version;
- output model profile;
- normalized page input hash.

## Canonical Form

Before hashing, inputs shall be normalized by:

1. sorting object keys;
2. removing non-semantic whitespace;
3. converting line endings to LF;
4. excluding volatile timestamps;
5. resolving all references to versioned identifiers.

## Output

The fingerprint shall use SHA-256 and be stored as:

`bcube-prompt-sha256:<64-hex-digest>`

## Required Metadata

Every compiled prompt manifest must include:

- `promptId`;
- `fingerprint`;
- `compilerVersion`;
- `compiledAt`;
- `sourceVersions`;
- `modelProfile`;
- `validationStatus`.

## Release Rule

A prompt may not be released for image generation if its fingerprint is missing or cannot be reproduced from the recorded source inputs.
