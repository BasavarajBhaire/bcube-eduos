# BCube Prompt Runtime™ API Contract

## Purpose

The runtime executes only compiler-approved Gold Production Prompts™ and manages generation, retry, evaluation, acceptance and publication gating.

## Generate request

```json
{
  "promptId": "PROMPT-CC-NUR-005",
  "fingerprint": "sha256:...",
  "modelProfile": "openai-gpt-image",
  "candidateCount": 1,
  "retryPolicy": "GOLD-STANDARD"
}
```

## Runtime lifecycle

Queued → Submitted → Generated → Asset Validation → Human Review → Approved or Rejected → Published

## Runtime responsibilities

- Verify prompt fingerprint and PASS status.
- Send only the final self-contained prompt to the selected adapter.
- Preserve prompt, model and asset traceability.
- Retry only according to the selected retry policy.
- Never modify canonical educational intent during retry.
- Store all candidate outputs and validation results.
- Block publication when any critical asset validation fails.

## Retry safeguards

Retries MAY clarify rendering instructions but MUST NOT change exact title, child-facing text, page number, learning objective, character identity, protected activity space or publisher identity.

## Runtime output

Each run produces:

- generation manifest
- provider response metadata
- generated asset reference
- asset-validation report
- review decision
- final publication status
