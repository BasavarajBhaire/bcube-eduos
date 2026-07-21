from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
STAGE1 = ROOT / "pipeline" / "stage1-prompt-compiler" / "output"
OUT = ROOT / "pipeline" / "stage2-illustration-generation" / "output"
EXPECTED_BOOKS = 10
EXPECTED_PAGES = 440


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Required Stage 1 input not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def locate_queue() -> Path:
    candidates = [
        STAGE1 / "generation-queue.json",
        STAGE1 / "generation_queue.json",
        STAGE1 / "generation-queue.jsonl",
        STAGE1 / "generation_queue.jsonl",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "Stage 1 generation queue is missing. Compile all ten official books before Stage 2 generation."
    )


def read_queue(path: Path) -> list[dict[str, Any]]:
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    payload = load_json(path)
    if isinstance(payload, list):
        return payload
    for key in ("jobs", "queue", "items", "entries"):
        if isinstance(payload.get(key), list):
            return payload[key]
    raise ValueError(f"Unsupported queue structure: {path}")


def canonical_job(entry: dict[str, Any]) -> dict[str, Any]:
    prompt_id = entry.get("prompt_id") or entry.get("id")
    prompt = entry.get("compiled_prompt") or entry.get("prompt") or entry.get("prompt_text")
    status = str(entry.get("status", "")).upper()
    if not prompt_id or not prompt:
        raise ValueError("Queue entry is missing prompt_id or compiled prompt text")
    prompt_hash = entry.get("prompt_sha256") or hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    return {
        "job_id": f"{prompt_id}:{prompt_hash[:16]}",
        "prompt_id": prompt_id,
        "book_number": entry.get("book_number"),
        "book_slug": entry.get("book_slug") or entry.get("slug"),
        "page_number": entry.get("page_number") or entry.get("page"),
        "status": status,
        "prompt_sha256": prompt_hash,
        "compiled_prompt": prompt,
        "output_format": "png",
        "target_page": "A4 portrait",
        "target_dpi": 300,
        "generation_state": "PENDING",
    }


def validate(jobs: list[dict[str, Any]]) -> dict[str, Any]:
    ready = [job for job in jobs if job["status"] == "READY"]
    prompt_ids = [job["prompt_id"] for job in jobs]
    books = {job["book_slug"] for job in jobs if job["book_slug"]}
    report = {
        "expected_books": EXPECTED_BOOKS,
        "detected_books": len(books),
        "expected_pages": EXPECTED_PAGES,
        "queue_entries": len(jobs),
        "ready_entries": len(ready),
        "unique_prompt_ids": len(prompt_ids) == len(set(prompt_ids)),
        "all_entries_ready": len(ready) == EXPECTED_PAGES,
    }
    report["overall_decision"] = (
        "PASS"
        if report["detected_books"] == EXPECTED_BOOKS
        and report["queue_entries"] == EXPECTED_PAGES
        and report["ready_entries"] == EXPECTED_PAGES
        and report["unique_prompt_ids"]
        else "BLOCKED"
    )
    return report


def write_outputs(jobs: list[dict[str, Any]], report: dict[str, Any], mode: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "validation-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "stage": 2,
        "version": "1.0.0",
        "mode": mode,
        "job_count": len(jobs),
        "entry_gate": report["overall_decision"],
        "provider": "unconfigured",
        "storage": "workflow-artifact-or-object-storage",
    }
    (OUT / "stage2-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if mode == "dry-run" and report["overall_decision"] == "PASS":
        with (OUT / "jobs.jsonl").open("w", encoding="utf-8") as handle:
            for job in jobs:
                handle.write(json.dumps(job, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="BCube Stage 2 illustration generation orchestrator")
    parser.add_argument("--mode", choices=("validate", "dry-run", "generate"), default="validate")
    args = parser.parse_args()

    queue_path = locate_queue()
    jobs = [canonical_job(entry) for entry in read_queue(queue_path)]
    report = validate(jobs)
    write_outputs(jobs, report, args.mode)

    if report["overall_decision"] != "PASS":
        raise SystemExit(
            "Stage 2 blocked: Stage 1 must provide 10 books and 440 READY unique prompt entries."
        )
    if args.mode == "generate":
        raise SystemExit(
            "Generation provider is not configured. Add a provider adapter, repository secrets and binary storage first."
        )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
