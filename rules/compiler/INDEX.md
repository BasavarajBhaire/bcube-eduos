# Prompt Compiler Rule Index

Owner: Prompt Engine Product Owner  
Prefix: `PC-`

## Active foundation rules

- `PC-LOAD-001` — Engine outputs MUST load in the approved sequence.
- `PC-SCHEMA-001` — Required metadata MUST validate against the canonical schemas.
- `PC-MERGE-001` — Conflicting instructions MUST NOT be resolved silently.
- `PC-VERSION-001` — Every compiled prompt MUST record engine and template versions.
- `PC-RELEASE-001` — Only QA-approved prompts MAY be released.

Outputs: compiled Gold Production Prompt, metadata manifest, validation summary, and audit record.