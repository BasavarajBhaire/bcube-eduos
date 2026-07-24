#!/usr/bin/env python3
"""Finalise Learning Page Contract V2 after portfolio-wide content locking."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

REFINER_PATH = Path(__file__).with_name("refine_learning_contract_v2.py")


def load_refiner() -> ModuleType:
    specification = importlib.util.spec_from_file_location(
        "bcube_learning_refiner_for_finaliser",
        REFINER_PATH,
    )
    if specification is None or specification.loader is None:
        raise ValueError(f"Cannot load learning refiner: {REFINER_PATH}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def finalise_contract(
    contract: dict[str, Any],
    *,
    curated_override_applied: bool,
) -> dict[str, Any]:
    changes: list[str] = []
    if contract.get("content_status") != "LOCKED":
        refiner = load_refiner()
        refiner.refine_contract(
            contract,
            curated_override_applied=curated_override_applied,
        )
        changes.append("portfolio-content-lock")
    contract.setdefault("source_lineage", {})
    contract["source_lineage"].update(
        {
            "learning_contract_finaliser": "learning-contract-finaliser-v1.1",
            "contract_finalisation_changes": changes,
            "contract_finalisation_applied": bool(changes),
            "portfolio_content_status": contract.get("content_status"),
        }
    )
    return contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--curated-override-applied", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    finalised = finalise_contract(
        load(args.contract),
        curated_override_applied=args.curated_override_applied,
    )
    output = args.output or args.contract
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(finalised, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "FINALISED",
                "page_id": finalised["identity"]["page_id"],
                "content_status": finalised.get("content_status"),
                "changes": finalised["source_lineage"]["contract_finalisation_changes"],
                "output": str(output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"BCube learning-contract finalisation FAIL: {exc}", file=__import__("sys").stderr)
        raise SystemExit(2)
