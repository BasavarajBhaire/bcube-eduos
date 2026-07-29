#!/usr/bin/env python3
"""Render approved Early Maths assets using the completed QA composer."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "scripts/render_early_maths_from_approved_assets.py"
MODEL_COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_early_maths_curriculum_first_v3.py"

MODULE_NAME = "approved_assets_base"
spec = importlib.util.spec_from_file_location(MODULE_NAME, BASE)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {BASE}")
module = importlib.util.module_from_spec(spec)
sys.modules[MODULE_NAME] = module
spec.loader.exec_module(module)
module.COMPOSER = MODEL_COMPOSER

if __name__ == "__main__":
    raise SystemExit(module.main())
