from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STAGE2 = ROOT / "pipeline" / "stage2-illustration-generation" / "output" / "stage2-manifest.json"
OUTPUT = Path(__file__).resolve().parent / "output"

MANDATORY_STAGE2_FIELDS = {"prompt_id", "job_id", "prompt_sha256", "status"}
READY_STATUSES = {"GENERATED", "SUCCEEDED", "READY_FOR_QA"}


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Required input not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    for key in ("pages", "jobs", "outputs", "records"):
        value = payload.get(key) if isinstance(payload, dict) else None
        if isinstance(value, list):
            return value
    raise ValueError("Stage 2 manifest must contain a page/job/output record list")


def evaluate(record: dict[str, Any]) -> dict[str, Any]:
    missing = sorted(MANDATORY_STAGE2_FIELDS - set(record))
    reasons: list[str] = []
    checks: dict[str, Any] = {
        "required_stage2_fields": not missing,
        "generation_succeeded": record.get("status") in READY_STATUSES,
        "canonical_prompt_id": isinstance(record.get("prompt_id"), str) and "-NURSERY-V5-P" in record.get("prompt_id", ""),
        "traceability_present": bool(record.get("job_id")) and len(str(record.get("prompt_sha256", ""))) == 64,
    }
    if missing:
        reasons.append("missing fields: " + ", ".join(missing))
    if not checks["generation_succeeded"]:
        reasons.append(f"Stage 2 status is {record.get('status')!r}")

    output_path_raw = record.get("output_path") or record.get("file_path") or record.get("asset_path")
    output_path = Path(output_path_raw) if output_path_raw else None
    checks["output_reference_present"] = output_path is not None
    checks["output_file_exists"] = bool(output_path and output_path.exists())
    if output_path and output_path.exists():
        checks["output_sha256"] = sha256_file(output_path)
        checks["supported_extension"] = output_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}
    else:
        checks["supported_extension"] = False
        if not output_path:
            reasons.append("output path is missing")
        else:
            reasons.append(f"output file not found: {output_path}")

    mandatory_pass = all(
        checks.get(name) is True
        for name in (
            "required_stage2_fields",
            "generation_succeeded",
            "canonical_prompt_id",
            "traceability_present",
            "output_reference_present",
            "output_file_exists",
            "supported_extension",
        )
    )

    vision_evidence = record.get("visual_qa_evidence")
    if not mandatory_pass:
        decision = "REGENERATE" if checks["generation_succeeded"] else "BLOCKED"
    elif vision_evidence:
        decision = "PASS" if vision_evidence.get("decision") == "PASS" else "REGENERATE"
    else:
        decision = "REVIEW"
        reasons.append("vision/OCR/brand/character evidence not supplied")

    return {
        "prompt_id": record.get("prompt_id"),
        "job_id": record.get("job_id"),
        "prompt_sha256": record.get("prompt_sha256"),
        "output_path": output_path_raw,
        "checks": checks,
        "decision": decision,
        "reasons": reasons,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage2-manifest", type=Path, default=DEFAULT_STAGE2)
    parser.add_argument("--expected-pages", type=int, default=440)
    args = parser.parse_args()

    OUTPUT.mkdir(parents=True, exist_ok=True)
    records = normalize_records(load_json(args.stage2_manifest))
    results = [evaluate(record) for record in records]

    prompt_ids = [item["prompt_id"] for item in results if item["prompt_id"]]
    duplicate_ids = sorted({value for value in prompt_ids if prompt_ids.count(value) > 1})
    decisions = {name: sum(item["decision"] == name for item in results) for name in ("PASS", "REVIEW", "REGENERATE", "BLOCKED")}

    regeneration = [item for item in results if item["decision"] == "REGENERATE"]
    human_review = [item for item in results if item["decision"] == "REVIEW"]
    complete = len(results) == args.expected_pages and not duplicate_ids
    overall = "PASS" if complete and decisions["PASS"] == args.expected_pages else "BLOCKED"

    manifest = {
        "stage": 3,
        "name": "Visual QA and Regeneration Gate",
        "expected_pages": args.expected_pages,
        "received_pages": len(results),
        "unique_prompt_ids": len(set(prompt_ids)),
        "duplicate_prompt_ids": duplicate_ids,
        "decisions": decisions,
        "overall_decision": overall,
        "entry_gate_complete": complete,
    }

    (OUTPUT / "page-results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "regeneration-queue.json").write_text(json.dumps(regeneration, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "human-review-queue.json").write_text(json.dumps(human_review, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "stage3-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "stage3-summary.md").write_text(
        "# Stage 3 Visual QA Summary\n\n"
        f"- Expected pages: {args.expected_pages}\n"
        f"- Received pages: {len(results)}\n"
        f"- PASS: {decisions['PASS']}\n"
        f"- REVIEW: {decisions['REVIEW']}\n"
        f"- REGENERATE: {decisions['REGENERATE']}\n"
        f"- BLOCKED: {decisions['BLOCKED']}\n"
        f"- Duplicate prompt IDs: {len(duplicate_ids)}\n\n"
        f"`{overall} — STAGE 3 VISUAL QA GATE`\n",
        encoding="utf-8",
    )

    print(json.dumps(manifest, indent=2))
    if overall != "PASS":
        raise SystemExit("Stage 3 is not ready for downstream PDF assembly")


if __name__ == "__main__":
    main()
