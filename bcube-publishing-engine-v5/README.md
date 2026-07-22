# BCube Publishing Engine v5

V5 is the executable orchestration layer above the approved V4 production prompts, the BCube Publishing SDK, deterministic composers, and evidence-based render QA. It does not replace V4; V4 remains the source specification.

## Pipeline

1. Resolve the registered level, book and page type.
2. Compile an illustration-only prompt.
3. Generate or import an illustration into the candidate staging area.
4. Run fail-closed illustration checks.
5. Call the existing deterministic compositor.
6. Store the composed page as a review candidate.
7. Preserve prompt, page data, composition evidence and artifact hashes.
8. Require explicit human approval.
9. Run final rendered-page QA.
10. Promote the exact approved illustration and page into the approved area.

Raw AI or manual input is never placed directly in the approved area.

## Providers

- `manual`: imports an existing clean illustration, such as an illustration created in ChatGPT.
- `reuse`: reuses the already staged illustration candidate for review or approval.
- `openai`: optional API-backed generation using `OPENAI_API_KEY`.

## Traceable artifact structure

```text
production-renders/v5/
├── prompts/
├── candidates/
│   ├── illustrations/
│   └── pages/
├── approved/
│   ├── illustrations/
│   └── pages/
├── manifests/
├── evidence/
└── reports/
```

Each page receives a review manifest containing its workflow state, reviewer, artifact paths and SHA-256 hashes.

## Current production scope

The registered executable path is Nursery cover composition. Unsupported page types fail closed until their deterministic composers are registered. About, Publisher, Contents and Back Cover are not generated through full-page AI as a fallback.

## No-API workflow

Create an illustration-only scene in ChatGPT and save it locally. It must contain no text, logo, mascot, badge, panels, pillars, footer or cover layout.

Create the review candidate:

```bash
python scripts/bcube_publish.py \
  --level nursery \
  --book confidence-builders \
  --page cover \
  --provider manual \
  --illustration "D:/BCube/confidence-scene.png" \
  --confirm-clean-illustration
```

Review:

```text
production-renders/v5/candidates/pages/CB-NURSERY-V4-P001.png
```

After visual approval, run:

```bash
python scripts/bcube_publish.py \
  --level nursery \
  --book confidence-builders \
  --page cover \
  --provider reuse \
  --approve \
  --reviewer "Basavaraj Bhaire"
```

The production-eligible result is promoted to:

```text
production-renders/v5/approved/pages/CB-NURSERY-V4-P001.png
```

The final QA report is stored under `production-renders/v5/reports/`. A page is production eligible only when the engine reports `PRODUCTION_PASS`.

## Optional API environment

```bash
export OPENAI_API_KEY="..."
export BCUBE_IMAGE_PROVIDER="openai"
export BCUBE_IMAGE_MODEL="gpt-image-1.5"
```

No key is stored in the repository.
