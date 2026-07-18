# Milestone: EduOS Runtime Kernel

Status: Implemented

The runtime is the only supported orchestration entry point for deterministic page preflight.

## Execution order

1. Load manifest identity.
2. Resolve the exact versioned template.
3. Resolve and checksum-verify every referenced asset.
4. Enforce template/page-type compatibility.
5. Build the deterministic composition plan.
6. Emit an auditable event sequence.
7. Fail closed on any unresolved dependency.

## Runtime events

- `manifest.loaded`
- `template.resolved`
- `assets.verified`
- `composition.preflight_passed`
- `runtime.failed`

## Invariants

- No rendering begins before preflight passes.
- Unknown templates are rejected.
- Non-GOLD or checksum-mismatched assets are rejected.
- Duplicate asset references are rejected.
- Failures emit a runtime event and stop execution.
- Capability providers must be explicit, enabled and unambiguous.

## Command

```bash
python -m eduos.kernel.runtime eduos/examples/communication-champions-cover.json
python -m unittest eduos/tests/test_runtime.py
```
