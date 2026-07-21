#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "books" / "catalog.json"
STAGE1 = ROOT / "pipeline" / "stage1-prompt-compiler" / "output"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "output"
OPENAI_URL = "https://api.openai.com/v1/images/generations"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_book(slug: str) -> dict[str, Any]:
    catalog = read_json(CATALOG)
    matches = [b for b in catalog.get("books", []) if b.get("slug") == slug]
    if len(matches) != 1:
        raise ValueError(f"Unknown book slug: {slug}")
    if int(matches[0].get("page_count", 0)) != 44:
        raise ValueError(f"Book {slug} is not configured for 44 pages")
    return matches[0]


def load_queue(slug: str) -> list[dict[str, Any]]:
    path = STAGE1 / slug / "generation-queue.json"
    if not path.exists():
        raise FileNotFoundError(f"No Stage 1 queue found for {slug}: {path}")
    data = read_json(path)
    records = data.get("records", [])
    if len(records) != 44:
        raise ValueError(f"Expected 44 queue records, found {len(records)}")
    records = sorted(records, key=lambda r: int(r["page_number"]))
    for expected, record in enumerate(records, start=1):
        if int(record["page_number"]) != expected:
            raise ValueError("Queue page numbers must be 1-44")
        if record.get("status") != "READY":
            raise ValueError(f"Queue record not READY: {record.get('prompt_id')}")
        prompt_path = ROOT / str(record["prompt_path"])
        if not prompt_path.exists():
            raise FileNotFoundError(f"Compiled prompt missing: {prompt_path}")
        if sha256(prompt_path.read_bytes()) != record["prompt_sha256"]:
            raise ValueError(f"Prompt hash mismatch: {record['prompt_id']}")
    return records


def call_openai(prompt: str, prompt_id: str) -> tuple[bytes, dict[str, Any], int]:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY")
    model = os.environ.get("BCUBE_IMAGE_MODEL", "gpt-image-1.5").strip() or "gpt-image-1.5"
    quality = os.environ.get("BCUBE_IMAGE_QUALITY", "high").strip() or "high"
    size = os.environ.get("BCUBE_IMAGE_SIZE", "1024x1536").strip() or "1024x1536"
    retries = int(os.environ.get("BCUBE_IMAGE_MAX_RETRIES", "3") or "3")
    timeout = int(os.environ.get("BCUBE_IMAGE_TIMEOUT_SECONDS", "300") or "300")
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "output_format": "png",
        "background": "opaque",
        "n": 1
    }).encode("utf-8")
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        request = urllib.request.Request(
            OPENAI_URL,
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "BCube-EduOS-OpenAI-Images/1.0",
                "X-Client-Request-Id": prompt_id,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            items = body.get("data", [])
            encoded = items[0].get("b64_json") if items else None
            if not encoded:
                raise RuntimeError("OpenAI response did not contain data[0].b64_json")
            metadata = {
                "provider": "openai",
                "model": model,
                "quality": quality,
                "size": size,
                "created": body.get("created"),
                "usage": body.get("usage"),
            }
            return base64.b64decode(encoded), metadata, attempt
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            last_error = RuntimeError(f"OpenAI HTTP {exc.code}: {detail[:1000]}")
        except (urllib.error.URLError, TimeoutError, ValueError, RuntimeError) as exc:
            last_error = exc
        if attempt < retries:
            time.sleep(min(2 ** (attempt - 1), 8))
    raise RuntimeError(f"OpenAI generation failed after {retries} attempts: {last_error}")


def run(args: argparse.Namespace) -> int:
    book = load_book(args.book)
    records = load_queue(args.book)
    output_root = Path(args.output).resolve() / args.book
    requests_dir = output_root / "requests"
    responses_dir = output_root / "responses"
    pages_dir = output_root / "pages"
    for directory in (requests_dir, responses_dir, pages_dir):
        directory.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for record in records:
        page = int(record["page_number"])
        stem = f"P{page:03d}"
        prompt_path = ROOT / record["prompt_path"]
        prompt = prompt_path.read_text(encoding="utf-8")
        write_json(requests_dir / f"{stem}.json", {
            "prompt_id": record["prompt_id"],
            "book_slug": args.book,
            "page_number": page,
            "prompt_path": record["prompt_path"],
            "prompt_sha256": record["prompt_sha256"],
            "created_at": now(),
        })

        output_path = pages_dir / f"{stem}.png"
        if args.mode == "resume" and output_path.exists() and output_path.stat().st_size > 0 and not args.force:
            results.append({"prompt_id": record["prompt_id"], "page_number": page, "status": "GENERATED", "output_path": f"pages/{stem}.png", "output_sha256": sha256(output_path.read_bytes()), "provider": "existing", "attempts": 0})
            continue
        if args.mode in {"validate", "dry-run"}:
            results.append({"prompt_id": record["prompt_id"], "page_number": page, "status": "VALIDATED" if args.mode == "validate" else "DRY_RUN_READY", "output_path": f"pages/{stem}.png", "output_sha256": None, "provider": "not-called", "attempts": 0})
            continue
        try:
            image, metadata, attempts = call_openai(prompt, record["prompt_id"])
            if output_path.exists() and not args.force and args.mode != "resume":
                raise FileExistsError(f"Output already exists: {output_path}")
            output_path.write_bytes(image)
            write_json(responses_dir / f"{stem}.json", metadata)
            results.append({"prompt_id": record["prompt_id"], "page_number": page, "status": "GENERATED", "output_path": f"pages/{stem}.png", "output_sha256": sha256(image), "provider": "openai", "model": metadata["model"], "attempts": attempts})
        except Exception as exc:
            failure = {"prompt_id": record["prompt_id"], "page_number": page, "error": str(exc)}
            failures.append(failure)
            results.append({"prompt_id": record["prompt_id"], "page_number": page, "status": "FAILED", "output_path": f"pages/{stem}.png", "output_sha256": None, "provider": "openai", "attempts": 0, "error": str(exc)})

    generated = sum(r["status"] == "GENERATED" for r in results)
    manifest = {
        "schema_version": "1.1.0",
        "stage": 2,
        "provider": "openai",
        "book": {"slug": args.book, "title": book.get("title"), "number": book.get("number")},
        "mode": args.mode,
        "expected_pages": 44,
        "records": results,
        "generated": generated,
        "failed": len(failures),
        "stage3_ready": generated == 44 and not failures,
        "created_at": now(),
    }
    write_json(output_root / "generation-manifest.json", manifest)
    write_json(output_root / "failed-pages.json", failures)
    (output_root / "stage2-summary.md").write_text(
        f"# Stage 2 Summary — {book.get('title')}\n\n- Provider: OpenAI\n- Mode: `{args.mode}`\n- Records: {len(results)}/44\n- Generated: {generated}/44\n- Failed: {len(failures)}\n- Stage 3 ready: {'YES' if manifest['stage3_ready'] else 'NO'}\n",
        encoding="utf-8",
    )
    if args.mode in {"generate", "resume"} and not manifest["stage3_ready"]:
        return 2
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", required=True)
    parser.add_argument("--mode", choices=("validate", "dry-run", "generate", "resume"), default="dry-run")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    try:
        sys.exit(run(parse_args()))
    except Exception as exc:
        print(f"Stage 2 failed: {exc}", file=sys.stderr)
        sys.exit(1)
