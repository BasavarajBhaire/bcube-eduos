# BCube Cloud Illustration Engine

The cloud illustration engine extends the local Phase 6/7 automation for machines that cannot run FLUX locally. It reads the approved cover prompt workbook, calls a RunPod Serverless endpoint, validates each downloaded PNG, retries with deterministic prompt repairs, and generates review and release evidence.

## Features

- No OpenAI dependency.
- RunPod Serverless provider.
- Concurrent workers.
- Resume previously approved images.
- Retry and automatic prompt repair for occupancy, white-border, size, and square-format failures.
- Per-image JSON evidence.
- SHA-256, size, DPI, occupancy, border, timing, and estimated-cost evidence.
- HTML review gallery.
- Prompt and illustration ZIP packages.
- Nursery, LKG, UKG, or all-level processing.

## Environment

Never commit the API key.

### Git Bash

```bash
export RUNPOD_API_KEY="your-key"
export RUNPOD_ENDPOINT_ID="your-endpoint-id"
```

### Windows PowerShell

```powershell
$env:RUNPOD_API_KEY="your-key"
$env:RUNPOD_ENDPOINT_ID="your-endpoint-id"
```

## RunPod endpoint contract

The endpoint receives:

```json
{
  "input": {
    "prompt": "full BCube illustration prompt",
    "page_id": "CC-NURSERY-V4-P001",
    "width": 1254,
    "height": 1254,
    "workflow": {}
  }
}
```

`workflow` is omitted unless `--workflow` is supplied.

The completed RunPod output must expose an image through one of these fields, either directly or inside `output`, `result`, or `images`:

```text
image_url
output_url
url
image_base64
base64
image
```

The provider supports both an HTTP(S) download URL and base64-encoded PNG bytes.

## Validate the workbook locally without cloud cost

```bash
python scripts/bcube_cloud_illustrations.py \
  --workbook "D:\BCube\Illustration_Prompts\BCube_All_Levels_Distinctive_Cover_Illustration_Prompts_V5_3.xlsx" \
  --level nursery \
  --provider mock \
  --workers 4 \
  --batch-name cloud-mock-test \
  --require-complete
```

The mock provider generates deterministic QA fixtures only. It does not create publication illustrations.

## Generate Nursery covers through RunPod

```bash
python scripts/bcube_cloud_illustrations.py \
  --workbook "D:\BCube\Illustration_Prompts\BCube_All_Levels_Distinctive_Cover_Illustration_Prompts_V5_3.xlsx" \
  --level nursery \
  --provider runpod \
  --workers 2 \
  --max-retries 2 \
  --resume \
  --cost-per-second 0.00034 \
  --require-complete
```

Start with `--workers 1` or `2`. Increase concurrency only when the endpoint scaling and spending limit are configured.

## Use a workflow payload

Some RunPod ComfyUI workers accept an API-format workflow inside the endpoint input:

```bash
python scripts/bcube_cloud_illustrations.py \
  --workbook "D:\BCube\Illustration_Prompts\BCube_All_Levels_Distinctive_Cover_Illustration_Prompts_V5_3.xlsx" \
  --level all \
  --provider runpod \
  --workflow "D:\BCube\comfyui\bcube-cover-workflow-api.json" \
  --workers 2 \
  --resume \
  --require-complete
```

The endpoint handler is responsible for mapping `prompt`, `page_id`, `width`, and `height` into the chosen ComfyUI workflow. Different RunPod templates use different handler contracts, so verify the endpoint's sample request before a paid batch.

## Output

```text
production-renders/cloud-illustration-batches/<batch>/
├── images/
│   ├── nursery/
│   ├── lkg/
│   └── ukg/
├── prompts/
├── reports/
├── batch-manifest.json
├── illustration-review.html
├── <batch>-ILLUSTRATIONS.zip
└── <batch>-PROMPTS.zip
```

## Human approval

Automated checks validate structure, not artistic correctness. Review every item in `illustration-review.html` for:

- unexpected text or watermark;
- malformed hands, faces, or bodies;
- duplicated people or objects;
- accidental logo or Star mascot;
- cropped subjects;
- mismatch with the subject-specific cover concept;
- repetitive compositions across books;
- model and checkpoint commercial licensing.

Do not pass an illustration to the publishing release pipeline solely because structural QA reports `APPROVED`.
