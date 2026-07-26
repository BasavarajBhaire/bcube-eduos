#!/usr/bin/env python3
"""Full-book Early Maths composer with response-safe choice rendering.

Use this entry point for P022 onward. Any independent choice with visible text is
rendered without an enclosing answer circle. Blank connector dots and writing
boxes remain available for mechanics that genuinely require them.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_COMPOSER = ROOT / "bcube-publishing-sdk/composer/compose_runtime_learning_page.py"
POLICY_PATH = ROOT / "bcube-publishing-sdk/composer/early_maths_response_policy.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


base = load_module("early_maths_full_book_base", BASE_COMPOSER)
policy = load_module("early_maths_response_policy_full", POLICY_PATH)
original_circle = base.circle


def response_safe_circle(draw, text_base, template, cx, cy, text=""):
    """Text choices stay plain; empty connector/response markers stay circular."""
    if text not in (None, ""):
        policy.draw_plain_choice_with_base(
            text_base,
            draw,
            template,
            text,
            [cx - 72, cy - 64, cx + 72, cy + 64],
            size=42,
        )
        return
    original_circle(draw, text_base, template, cx, cy, text)


base.circle = response_safe_circle

if __name__ == "__main__":
    raise SystemExit(base.main())
