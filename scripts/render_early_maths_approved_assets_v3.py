#!/usr/bin/env python3
"""Normalise approved Early Maths assets and render with completed examples."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V2 = ROOT / "scripts/render_early_maths_approved_assets_v2.py"
MODEL_DELEGATE = ROOT / "scripts/render_early_maths_from_approved_assets_models.py"

MODULE_NAME = "approved_assets_v2"
spec = importlib.util.spec_from_file_location(MODULE_NAME, V2)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {V2}")
module = importlib.util.module_from_spec(spec)
sys.modules[MODULE_NAME] = module
spec.loader.exec_module(module)
module.DELEGATE = MODEL_DELEGATE

if __name__ == "__main__":
    raise SystemExit(module.main())
