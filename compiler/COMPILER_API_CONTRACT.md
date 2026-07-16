# BCube Gold Prompt Compiler™ API Contract

## Compile request

```json
{
  "bookId": "BOOK-CC-NUR-001",
  "pageId": "PAGE-005",
  "buildProfile": "GOLD-PRINT",
  "modelProfile": "openai-gpt-image",
  "locale": "en-IN"
}
```

## Compiler stages

1. Resolve canonical entities.
2. Resolve asset versions.
3. Build dependency graph.
4. Expand rules, fragments, templates and characters.
5. Construct Prompt IR.
6. Resolve conflicts using governed precedence.
7. Optimize without deleting unique requirements.
8. Validate hard gates.
9. Generate fingerprint and manifest.
10. Emit one self-contained final prompt.

## Successful response

```json
{
  "status": "PASS",
  "promptId": "PROMPT-CC-NUR-005",
  "fingerprint": "sha256:...",
  "compiledPrompt": "...",
  "manifestPath": "...",
  "validationReportPath": "..."
}
```

## Failure response

```json
{
  "status": "FAIL",
  "errors": [
    {
      "code": "UNRESOLVED_PLACEHOLDER",
      "severity": "critical",
      "location": "branding.logo"
    }
  ]
}
```

## Hard requirements

- Final prompts MUST be fully self-contained.
- No rule IDs, registry IDs, placeholders or inheritance instructions may remain.
- Exact child-facing text MUST be preserved.
- Protected brand, character and safety fields MUST NOT be overridden.
- A failed hard gate MUST block generation.
