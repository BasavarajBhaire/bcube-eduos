# BCube Illustration Pipeline — Stage 1 Prompt Compiler v6.0

Stage 1 converts canonical Nursery production prompts into deterministic generation-ready prompt packages.

## Source of truth

1. `BCube_Gold_Production_v4/books/catalog.json`
2. Each official book's `production-prompts/P001.md` through `P044.md`
3. BCube Gold Publishing Standard v5.1

## Outputs

For every official book, the compiler writes:

- `output/<book-slug>/compiled/P001.txt` through `P044.txt`
- `output/<book-slug>/manifest.json`
- `output/<book-slug>/validation-report.json`
- `output/generation-queue.json`
- `output/stage1-summary.md`

## Validation gates

- Exactly 10 official Nursery books
- Exactly 44 source prompts per book
- Canonical prompt IDs matching `<CODE>-NURSERY-V5-P###`
- Unique page numbers and prompt IDs
- Required publishing instructions in every compiled prompt
- No empty source prompts

## Run

```bash
python BCube_Gold_Production_v4/pipeline/stage1-prompt-compiler/compiler/prompt_compiler.py
```

The compiler is deterministic: the same repository state produces the same compiled prompt content and SHA-256 hashes.
