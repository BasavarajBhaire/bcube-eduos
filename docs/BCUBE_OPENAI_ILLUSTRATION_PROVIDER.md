# BCube OpenAI Illustration Provider

The OpenAI provider is intended for carefully bounded cover previews and approved cover batches. It does not require a RunPod endpoint ID. Authentication uses only an OpenAI API key.

## Configure the API key

Git Bash:

```bash
export OPENAI_API_KEY="sk-proj-..."
```

PowerShell:

```powershell
$env:OPENAI_API_KEY="sk-proj-..."
```

Do not commit API keys to GitHub, Excel files, YAML files, screenshots, logs or shell-history examples.

## First paid test: one cover, no retry

```bash
python scripts/bcube_preview_illustrations.py \
  --workbook "D:\BCube\Illustration_Prompts\BCube_All_Levels_Distinctive_Cover_Illustration_Prompts_V5_3.xlsx" \
  --level nursery \
  --preview 1 \
  --provider openai \
  --openai-model gpt-image-1 \
  --openai-quality medium \
  --openai-size 1024x1024 \
  --openai-background opaque \
  --workers 1 \
  --max-retries 0 \
  --cost-per-image 0.00 \
  --batch-name nursery-openai-preview-1
```

`--cost-per-image` is a manual accounting estimate. Check the current OpenAI pricing page and set the current per-image estimate before relying on `--max-budget-usd`. The engine deliberately does not hard-code pricing because prices can change.

Example with an explicit safety ceiling:

```bash
python scripts/bcube_preview_illustrations.py \
  --workbook "D:\BCube\Illustration_Prompts\BCube_All_Levels_Distinctive_Cover_Illustration_Prompts_V5_3.xlsx" \
  --level nursery \
  --preview 1 \
  --provider openai \
  --workers 1 \
  --max-retries 0 \
  --cost-per-image 0.25 \
  --max-budget-usd 0.25 \
  --batch-name nursery-openai-preview-1
```

The batch is rejected before any API request when:

```text
selected images × cost per image × maximum attempts > maximum budget
```

## Review output

```text
production-renders/cloud-illustration-batches/
└── nursery-openai-preview-1/
    ├── images/
    ├── prompts/
    ├── reports/
    ├── batch-manifest.json
    ├── preview-gate.json
    ├── illustration-review.html
    ├── nursery-openai-preview-1-ILLUSTRATIONS.zip
    └── nursery-openai-preview-1-PROMPTS.zip
```

The preview gate always records:

```json
{
  "full_run_authorized": false
}
```

Preview mode never starts the remaining workbook rows automatically.

## Recommended approval sequence

1. Generate one Nursery cover with zero retries.
2. Review subject identity, composition, white background, unwanted text, anatomy, cropping and BCube suitability.
3. Refine the workbook prompt when needed.
4. Generate a five-cover preview.
5. Approve the visual system.
6. Run an explicitly authorized full cover batch.

## Full OpenAI batch after approval

```bash
python scripts/bcube_openai_illustrations.py \
  --workbook "D:\BCube\Illustration_Prompts\BCube_All_Levels_Distinctive_Cover_Illustration_Prompts_V5_3.xlsx" \
  --level nursery \
  --model gpt-image-1 \
  --quality medium \
  --size 1024x1024 \
  --background opaque \
  --workers 1 \
  --max-retries 0 \
  --cost-per-image 0.25 \
  --max-budget-usd 2.50 \
  --require-complete \
  --batch-name nursery-openai-approved
```

Use one worker initially. Increase concurrency only after confirming account rate limits and output quality.

## API behavior

The provider sends a request to:

```text
POST https://api.openai.com/v1/images/generations
```

It supports base64 image output and URL output. The generated image then passes through the existing BCube structural QA checks:

- image readability;
- minimum dimensions;
- square-format tolerance;
- foreground occupancy;
- white outer border;
- DPI metadata;
- SHA-256 evidence.

Automated structural QA does not replace human visual approval. Review every paid image before publishing.
