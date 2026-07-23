# BCube Phase 7 — Excel-to-Illustration Automation

Phase 7 reads the approved BCube cover-prompt workbook directly and produces:

- one PNG per workbook row;
- correct page-ID filenames;
- Nursery, LKG and UKG folder separation;
- exported individual prompt text files;
- per-image QA evidence;
- a batch manifest;
- a prompt ZIP;
- an illustration ZIP.

No OpenAI SDK, API key or subscription is required.

## Workbook contract

The selected worksheet must contain these columns:

- `Level`
- `Book Slug`
- `Cover Page ID`
- `Full Cover Illustration Prompt`

The approved workbook uses the worksheet `Complete Book List`.

## Output structure

```text
production-renders/illustration-batches/<batch-name>/
├── images/
│   ├── nursery/<book-slug>/<PAGE-ID>.png
│   ├── lkg/<book-slug>/<PAGE-ID>.png
│   └── ukg/<book-slug>/<PAGE-ID>.png
├── prompts/
├── reports/
├── batch-manifest.json
├── <batch-name>-PROMPTS.zip
└── <batch-name>-ILLUSTRATIONS.zip
```

## Local ComfyUI generation

Start ComfyUI locally and use an API-format workflow containing:

```text
{{BCUBE_PROMPT}}
{{BCUBE_PAGE_ID}}
```

Run:

```bash
python scripts/bcube_generate_from_excel.py \
  --workbook "D:\BCube\BCube_All_Levels_Distinctive_Cover_Illustration_Prompts_V5_3.xlsx" \
  --level all \
  --provider comfyui \
  --workflow "D:\BCube\comfyui\bcube-cover-workflow.json" \
  --comfyui-server http://127.0.0.1:8188 \
  --resume \
  --continue-on-error \
  --require-complete
```

## Generic local generator

Any local program can be integrated through the command provider. The command may use `{prompt}`, `{output}` and `{page_id}`, or read the environment variables `BCUBE_PROMPT`, `BCUBE_OUTPUT` and `BCUBE_PAGE_ID`.

```bash
python scripts/bcube_generate_from_excel.py \
  --workbook "D:\BCube\BCube_All_Levels_Distinctive_Cover_Illustration_Prompts_V5_3.xlsx" \
  --level nursery \
  --provider command \
  --command "python local_generator.py --prompt \"{prompt}\" --output \"{output}\"" \
  --resume \
  --require-complete
```

## Manual prompt package

This exports all individual prompt files and expected PNG paths without generating images:

```bash
python scripts/bcube_generate_from_excel.py \
  --workbook "D:\BCube\BCube_All_Levels_Distinctive_Cover_Illustration_Prompts_V5_3.xlsx" \
  --level all \
  --provider manual
```

## QA gates

Generated candidates are checked for:

- readable PNG content;
- minimum 1024 × 1024 dimensions;
- square aspect ratio;
- minimum foreground occupancy;
- white outer safety border;
- DPI evidence;
- SHA-256 evidence.

`--require-complete` returns a failure unless every selected workbook row has an approved image. `--resume` skips previously generated images that continue to pass QA.

## Important limitation

The automation controls prompts, generation calls, retries, filenames, folders, validation and ZIP packaging. A local image model and commercially permitted checkpoint must still be installed. Output quality depends on the selected local model, workflow, sampler, seed strategy and checkpoint licence.
