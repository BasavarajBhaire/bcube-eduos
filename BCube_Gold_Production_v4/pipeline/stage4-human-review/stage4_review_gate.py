from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

FINAL = {"APPROVED", "APPROVED_WITH_NOTE"}
ALL_DECISIONS = FINAL | {"CHANGES_REQUIRED", "REJECTED", "PENDING"}
EXPECTED_PAGES = 440


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def stage3_rows(payload):
    if isinstance(payload, list):
        return payload
    for key in ("pages", "results", "items", "records"):
        if isinstance(payload.get(key), list):
            return payload[key]
    raise ValueError("Stage 3 manifest has no page records")


def build_template(rows, output: Path) -> None:
    fields = ["prompt_id", "book_slug", "page_number", "stage3_decision", "evidence_hash", "reviewer", "role", "decision", "reason_code", "note", "reviewed_at_utc"]
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "prompt_id": row.get("prompt_id", ""),
                "book_slug": row.get("book_slug", ""),
                "page_number": row.get("page_number", ""),
                "stage3_decision": row.get("decision", ""),
                "evidence_hash": row.get("evidence_hash") or row.get("output_sha256", ""),
                "decision": "PENDING",
            })


def read_reviews(path: Path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage3-manifest", required=True, type=Path)
    parser.add_argument("--reviews", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    rows = stage3_rows(load_json(args.stage3_manifest))
    ids = [r.get("prompt_id") for r in rows]
    if len(rows) != EXPECTED_PAGES or len(set(ids)) != EXPECTED_PAGES or None in ids:
        raise SystemExit("Stage 4 blocked: Stage 3 must contain 440 unique canonical prompt IDs")

    args.output.mkdir(parents=True, exist_ok=True)
    template = args.output / "review-template.csv"
    if not args.reviews:
        build_template(rows, template)

    reviews = read_reviews(args.reviews) if args.reviews else []
    review_map = {r.get("prompt_id"): r for r in reviews}
    decisions = []
    corrections = []
    stale = []

    for row in rows:
        pid = row["prompt_id"]
        expected_hash = row.get("evidence_hash") or row.get("output_sha256", "")
        review = review_map.get(pid, {})
        decision = review.get("decision", "PENDING") or "PENDING"
        if decision not in ALL_DECISIONS:
            decision = "PENDING"
        if review and review.get("evidence_hash", "") != expected_hash:
            stale.append(pid)
            decision = "PENDING"
        record = {
            "prompt_id": pid,
            "book_slug": row.get("book_slug"),
            "page_number": row.get("page_number"),
            "stage3_decision": row.get("decision"),
            "evidence_hash": expected_hash,
            "reviewer": review.get("reviewer", ""),
            "role": review.get("role", ""),
            "decision": decision,
            "reason_code": review.get("reason_code", ""),
            "note": review.get("note", ""),
            "reviewed_at_utc": review.get("reviewed_at_utc", ""),
        }
        decisions.append(record)
        if decision in {"CHANGES_REQUIRED", "REJECTED"}:
            corrections.append(record)

    approved = sum(d["decision"] in FINAL for d in decisions)
    passed = approved == EXPECTED_PAGES and not corrections and not stale
    manifest = {
        "stage": 4,
        "version": "1.0.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "stage3_manifest_sha256": sha256_file(args.stage3_manifest),
        "expected_pages": EXPECTED_PAGES,
        "reviewed_pages": len(reviews),
        "approved_pages": approved,
        "open_corrections": len(corrections),
        "stale_decisions": len(stale),
        "decision": "PASS" if passed else "BLOCKED",
    }
    (args.output / "review-decisions.json").write_text(json.dumps(decisions, indent=2) + "\n", encoding="utf-8")
    (args.output / "correction-queue.json").write_text(json.dumps(corrections, indent=2) + "\n", encoding="utf-8")
    (args.output / "approval-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (args.output / "stage4-summary.md").write_text(
        "# Stage 4 Human Review Summary\n\n"
        f"- Pages expected: {EXPECTED_PAGES}\n- Pages approved: {approved}\n"
        f"- Open corrections: {len(corrections)}\n- Stale decisions: {len(stale)}\n\n"
        f"`{manifest['decision']} — STAGE 4 HUMAN REVIEW AND APPROVAL GATE`\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2))
    if not passed:
        raise SystemExit("Stage 4 remains blocked until all pages receive current final approval")


if __name__ == "__main__":
    main()
