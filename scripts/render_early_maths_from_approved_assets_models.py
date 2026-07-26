#!/usr/bin/env python3
"""Render approved Early Maths assets using the completed-model composer."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "scripts/render_early_maths_from_approved_assets.py"
MODEL_COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_early_maths_curriculum_first_v2.py"

spec = importlib.util.spec_from_file_location("approved_assets_base", BASE)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {BASE}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.COMPOSER = MODEL_COMPOSER

if __name__ == "__main__":
    raise SystemExit(module.main())
