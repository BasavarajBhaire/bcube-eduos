# BCube Publishing Engine v5

V5 is the executable orchestration layer above the approved V4 production prompts, the BCube Publishing SDK, deterministic composers, and evidence-based render QA.

It does not replace V4. V4 remains the source specification.

## Pipeline

1. Resolve level, book, page type and V4 source prompt.
2. Compile an illustration-only prompt.
3. Generate or import an illustration candidate through a provider adapter.
4. Run fail-closed illustration QA.
5. Call the existing deterministic page compositor.
6. Generate evidence and run rendered-page QA.
7. Require human approval bound to the exact artifact hash before production eligibility.

## Providers

- `manual`: imports an existing clean illustration.
- `openai`: generates an illustration through the OpenAI Images API using `OPENAI_API_KEY`.

The provider is selected with `--provider` or `BCUBE_IMAGE_PROVIDER`.

## Current production scope

The V5 orchestrator supports the locked Nursery cover compositor already present in the SDK. The orchestration contracts are page-type-neutral so About, Publisher, Contents, Back Cover and learning-page composers can be registered without changing the CLI.

## Commands

Generate a review candidate with the OpenAI provider:

```bash
python scripts/bcube_publish.py \
  --level nursery \
  --book confidence-builders \
  --page cover \
  --provider openai
```

Import an existing illustration:

```bash
python scripts/bcube_publish.py \
  --level nursery \
  --book confidence-builders \
  --page cover \
  --provider manual \
  --illustration "D:/BCube/confidence-scene.png" \
  --confirm-clean-illustration
```

After reviewing the candidate, bind approval and run final QA:

```bash
python scripts/bcube_publish.py \
  --level nursery \
  --book confidence-builders \
  --page cover \
  --provider reuse \
  --approve \
  --reviewer "Basavaraj Bhaire"
```

## Environment

```bash
export OPENAI_API_KEY="..."
export BCUBE_IMAGE_PROVIDER="openai"
export BCUBE_IMAGE_MODEL="gpt-image-1.5"
```

No key is stored in the repository.
