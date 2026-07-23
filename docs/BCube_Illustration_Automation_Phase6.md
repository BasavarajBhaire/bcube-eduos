# BCube Illustration Automation Engine™ — Phase 6

Phase 6 automates illustration production without requiring OpenAI or any cloud subscription.

## Providers

- `manual`: creates the queue and reports the expected output path.
- `command`: runs any locally installed image generator through a shell command.
- `comfyui`: submits a workflow to a local ComfyUI server.
- `mock`: deterministic CI-only provider.

The Publishing Engine remains provider-independent. Every candidate must pass BCube illustration QA before being copied to the approved queue.

## Queue structure

```text
illustration-engine/
  queue/
    pending/<level>/<book>/
    approved/<level>/<book>/
    rejected/<level>/<book>/
  reports/<level>/<book>/
  portfolio-runs/
```

## Manual queue

```bash
python scripts/bcube_generate_illustrations.py \
  --level nursery \
  --book communication-champions \
  --provider manual
```

## Local command provider

The command receives these environment variables:

- `BCUBE_PROMPT`
- `BCUBE_OUTPUT`
- `BCUBE_PAGE_ID`

It can also use `{prompt}`, `{output}`, and `{page_id}` placeholders.

```bash
python scripts/bcube_generate_illustrations.py \
  --level nursery \
  --book communication-champions \
  --provider command \
  --command 'python local_generator.py --prompt "{prompt}" --output "{output}"'
```

## Local ComfyUI provider

Export a ComfyUI API workflow JSON and place `{{BCUBE_PROMPT}}` in the positive prompt text. Optionally use `{{BCUBE_PAGE_ID}}` in the filename prefix.

```bash
python scripts/bcube_generate_illustrations.py \
  --level nursery \
  --book communication-champions \
  --provider comfyui \
  --workflow local/comfyui/bcube-workflow.json \
  --comfyui-server http://127.0.0.1:8188 \
  --require-square
```

## Portfolio automation

```bash
python scripts/bcube_generate_illustration_portfolio.py \
  --level all \
  --provider comfyui \
  --workflow local/comfyui/bcube-workflow.json \
  --resume \
  --continue-on-error \
  --require-square
```

## Automatic QA

The built-in deterministic validator checks:

- readable PNG/image stream;
- minimum 1024 × 1024 dimensions;
- square geometry when required;
- foreground occupancy;
- white safety border;
- DPI metadata;
- SHA-256 evidence.

Text, logo, mascot, watermark and semantic-content detection remain extensible QA adapters. Until a trusted local detector is configured, those conditions must remain part of the generation prompt and human approval gate.

## No OpenAI dependency

Phase 6 imports no OpenAI SDK and requires no OpenAI key. Local generation cost is limited to the user's hardware and electricity. The selected local model and checkpoint must have suitable commercial licensing before publication.
