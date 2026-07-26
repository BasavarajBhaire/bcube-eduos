#!/usr/bin/env python3
"""Normalise approved Early Maths assets and render with completed examples."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V2 = ROOT / "scripts/render_early_maths_approved_assets_v2.py"
MODEL_DELEGATE = ROOT / "scripts/render_early_maths_from_approved_assets_models.py"

spec = importlib.util.spec_from_file_location("approved_assets_v2", V2)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {V2}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.DELEGATE = MODEL_DELEGATE

if __name__ == "__main__":
    raise SystemExit(module.main())
