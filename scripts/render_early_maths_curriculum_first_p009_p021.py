#!/usr/bin/env python3
"""Render only the approved Early Maths curriculum-first batch P009-P021.

This command intentionally does not render the rest of the book. It builds the
curriculum-first runtime contract, validates required illustration files, renders
artless pages deterministically, and writes a page-by-page evidence summary.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE_IDS = [f"EM-LKG-V4-P{n:03d}" for n in range(9, 22)]
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")


@dataclass
class Result:
    page_id: str
    status: str
    reason: str = ""
    illustration: str = ""
    output: str = ""
    evidence: str = ""


def load_json(path: Path):
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object expected: {path}")
    return value


def find_illustration(directory: Path, page_id: str) -> Path | None:
    pattern = re.compile(re.escape(page_id), re.IGNORECASE)
    matches = [p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTS and pattern.search(p.stem)]
    if len(matches) > 1:
        raise ValueError(f"Duplicate illustrations for {page_id}: {[str(p) for p in matches]}")
    return matches[0] if matches else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Early Maths curriculum-first P009-P021 test batch")
    parser.add_argument("--illustrations-dir", type=Path, required=True)
    parser.add_argument("--logo", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--page-id", choices=PAGE_IDS)
    parser.add_argument("--fail-fast", action="store_true")
    args = parser.parse_args()

    illustrations_dir = args.illustrations_dir.expanduser().resolve()
    logo = args.logo.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    evidence_dir = args.evidence_dir.expanduser().resolve()
    if not illustrations_dir.is_dir():
        raise SystemExit(f"Illustrations directory not found: {illustrations_dir}")
    if not logo.is_file():
        raise SystemExit(f"Logo not found: {logo}")

    subprocess.run([sys.executable, str(ROOT / "scripts/build_early_maths_curriculum_first_runtime.py")], cwd=ROOT, check=True)
    contract = load_json(ROOT / "runtime-contracts/lkg/early-maths-adventures.json")
    selected = [args.page_id] if args.page_id else PAGE_IDS
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    results: list[Result] = []

    with tempfile.TemporaryDirectory(prefix="bcube-curriculum-first-") as temp_name:
        blank = Path(temp_name) / "blank.png"
        from PIL import Image
        Image.new("RGBA", (1200, 1200), "white").save(blank)

        for page_id in selected:
            page = contract["pages"].get(page_id)
            if not isinstance(page, dict):
                results.append(Result(page_id, "FAILED", "Page missing from runtime contract"))
                continue
            requires_art = bool(page.get("illustration", {}).get("requires_generated_art"))
            try:
                illustration = find_illustration(illustrations_dir, page_id) if requires_art else blank
                if requires_art and illustration is None:
                    raise FileNotFoundError(f"Required regenerated illustration not found for {page_id}")
                output = output_dir / f"{page_id}.png"
                evidence = evidence_dir / f"{page_id}.json"
                command = [
                    sys.executable,
                    str(ROOT / "bcube-publishing-sdk/composer/compose_early_maths_curriculum_first.py"),
                    "--level", "lkg",
                    "--book", "early-maths-adventures",
                    "--page-id", page_id,
                    "--logo", str(logo),
                    "--output", str(output),
                    "--evidence-output", str(evidence),
                ]
                if illustration is not None:
                    command.extend(["--illustration", str(illustration)])
                process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
                if process.returncode != 0:
                    raise RuntimeError((process.stderr or process.stdout or "Renderer failed").strip())
                results.append(Result(page_id, "GENERATED", illustration=str(illustration) if requires_art else "DETERMINISTIC_NO_ART", output=str(output), evidence=str(evidence)))
            except Exception as exc:
                results.append(Result(page_id, "FAILED", str(exc)))
                if args.fail_fast:
                    break

    summary = {
        "scope": selected,
        "generated": sum(r.status == "GENERATED" for r in results),
        "failed": sum(r.status == "FAILED" for r in results),
        "results": [asdict(r) for r in results],
        "policy": "Curriculum-first P009-P021 only. No generic fallback and no full-book activation.",
    }
    summary_path = evidence_dir / "curriculum-first-p009-p021-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("scope", "generated", "failed", "policy")}, indent=2))
    print(f"Summary: {summary_path}")
    return 0 if not summary["failed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
