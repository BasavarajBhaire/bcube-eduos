# OpenAI asset generation — Early Maths Adventures LKG

This workflow generates one PNG per named curriculum asset. It removes manual image downloading, renaming and combined-sheet cropping.

## Security and billing

- Create an API key in the OpenAI Platform.
- Do not commit the key to Git or place it in a workbook.
- API billing is separate from a ChatGPT subscription.

PowerShell, current terminal only:

```powershell
$env:OPENAI_API_KEY="your-api-key"
```

PowerShell, persist for future terminals:

```powershell
setx OPENAI_API_KEY "your-api-key"
```

Open a new terminal after using `setx`.

## Pull the implementation

```bash
cd /d/bcube/BCube_books_repo/bcube-eduos
git fetch origin
git reset --hard origin/agent/phase2-five-page-pilot
```

## Safe preview without API calls

```bash
python scripts/generate_early_maths_assets_openai.py \
  --pages P009,P018,P021 \
  --output-dir "D:\BCube\Books\Early Maths Adventures\openai-assets" \
  --dry-run
```

The dry run creates the folder plan and `generation-report.json`, but does not call OpenAI.

## Generate the proof set

```bash
python scripts/generate_early_maths_assets_openai.py \
  --pages P009,P018,P021 \
  --output-dir "D:\BCube\Books\Early Maths Adventures\openai-assets"
```

P013 is not listed because it is a deterministic page and needs no generated art.

## Generate every P009–P021 asset that requires art

```bash
python scripts/generate_early_maths_assets_openai.py \
  --pages all \
  --output-dir "D:\BCube\Books\Early Maths Adventures\openai-assets"
```

Default generation settings:

- model: `gpt-image-1`
- size: `1024x1024`
- quality: `high`
- background: `transparent`
- output: PNG

For a lower-cost trial:

```bash
python scripts/generate_early_maths_assets_openai.py \
  --pages P009,P018,P021 \
  --model gpt-image-1-mini \
  --quality medium \
  --output-dir "D:\BCube\Books\Early Maths Adventures\openai-assets-mini"
```

## Resume behaviour

Existing PNG files are skipped automatically. Rerun the same command after a network or rate-limit failure.

To replace existing images:

```bash
python scripts/generate_early_maths_assets_openai.py \
  --pages P009 \
  --overwrite \
  --output-dir "D:\BCube\Books\Early Maths Adventures\openai-assets"
```

## Output structure

```text
openai-assets/
├── EM-LKG-V4-P009/
│   ├── group_2_kites.png
│   ├── group_4_ducks.png
│   ├── group_6_cupcakes.png
│   └── group_8_balls.png
├── EM-LKG-V4-P018/
│   ├── frog.png
│   ├── rabbit.png
│   └── bee.png
├── EM-LKG-V4-P021/
│   └── ...
└── generation-report.json
```

`generation-report.json` records exact paths, prompt hashes, output hashes, attempts and failures. It does not contain the API key.

## Failure handling

The generator retries common temporary API errors and rate limits. Use `--fail-fast` when testing one page, or leave it off to continue generating other assets after an individual failure.

The generator does not automatically approve educational correctness. Exact quantity and visual-story validation must occur before assets are accepted for page rendering.
