# BCube Illustration Preview Cost Control

Use the preview command before any paid production batch. It creates a temporary workbook containing only the first requested matching rows, so the cloud provider cannot receive more prompts than the preview limit.

## Why this exists

A structurally valid illustration may still be visually unsuitable for BCube. Preview mode limits financial exposure while the visual direction, model and prompt are being validated.

## Safe mock test

```bash
python scripts/bcube_preview_illustrations.py \
  --workbook "D:\BCube\Illustration_Prompts\BCube_All_Levels_Distinctive_Cover_Illustration_Prompts_V5_3.xlsx" \
  --level nursery \
  --preview 2 \
  --provider mock \
  --batch-name nursery-preview-test
```

## Paid RunPod preview

```bash
python scripts/bcube_preview_illustrations.py \
  --workbook "D:\BCube\Illustration_Prompts\BCube_All_Levels_Distinctive_Cover_Illustration_Prompts_V5_3.xlsx" \
  --level nursery \
  --preview 1 \
  --provider runpod \
  --endpoint-id "$RUNPOD_ENDPOINT_ID" \
  --api-key "$RUNPOD_API_KEY" \
  --workers 1 \
  --max-retries 0 \
  --batch-name nursery-paid-preview-1
```

The default retry count is zero to prevent an unexpected failed image from creating additional paid requests. Increase `--max-retries` only after the provider and model have been validated.

## Output

The preview batch contains:

- individual PNG illustrations;
- individual prompt files;
- per-image QA reports;
- `batch-manifest.json`;
- `illustration-review.html`;
- prompt and illustration ZIP files;
- `preview-gate.json`.

`preview-gate.json` always contains:

```json
{
  "mode": "PREVIEW",
  "full_run_authorized": false
}
```

The command never launches the remaining workbook rows automatically.

## Approval sequence

1. Generate one paid preview with `--preview 1`.
2. Open `illustration-review.html`.
3. Validate subject identity, age suitability, character anatomy, white background, no text, no logo, no Star mascot and complete uncropped subjects.
4. Refine the model or prompt if needed.
5. Generate a five-image preview.
6. Only after human approval, run `bcube_cloud_illustrations.py` for the full selected level.

## Full run after approval

```bash
python scripts/bcube_cloud_illustrations.py \
  --workbook "D:\BCube\Illustration_Prompts\BCube_All_Levels_Distinctive_Cover_Illustration_Prompts_V5_3.xlsx" \
  --level nursery \
  --provider runpod \
  --workers 2 \
  --max-retries 1 \
  --resume \
  --require-complete
```

Human visual approval remains mandatory. Structural QA alone does not confirm commercial illustration quality.
