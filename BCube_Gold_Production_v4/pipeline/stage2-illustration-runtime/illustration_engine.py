#!/usr/bin/env python3
"""BCube Stage 2 book-by-book illustration runtime.

The runtime is deliberately provider-neutral. It validates a 44-page Stage 1
book queue, creates deterministic request records, and optionally calls a
configured HTTP JSON image provider. Binary assets are written to the runtime
output directory and should be stored as CI artifacts or external objects.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "books" / "catalog.json"
STAGE1 = ROOT / "pipeline" / "stage1-prompt-compiler" / "output"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "output"
PROMPT_ID_RE = re.compile(r"^[A-Z]+-NURSERY-V6-P(\d{3})$")
SUPPORTED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


@dataclass(frozen=True)
class PromptRecord:
    prompt_id: str
    book_slug: str
    page_number: int
    prompt_path: str
    prompt_sha256: str
    status: str


@dataclass
class GenerationRecord:
    prompt_id: str
    book_slug: str
    page_number: int
    prompt_sha256: str
    output_path: str
    output_sha256: str | None
    provider: str
    model: str
    attempts: int
    status: str
    error: str | None
    started_at: str
    completed_at: str | None


class ProviderError(RuntimeError):
    pass


class HttpJsonProvider:
    """Simple adapter for providers returning base64 image content in JSON.

    Expected response field: `image_base64`. Optional fields: `extension`,
    `model`, and `provider_request_id`.
    """

    def __init__(self) -> None:
        self.url = os.environ.get("BCUBE_IMAGE_PROVIDER_URL", "").strip()
        self.token = os.environ.get("BCUBE_IMAGE_PROVIDER_TOKEN", "").strip()
        self.model = os.environ.get("BCUBE_IMAGE_MODEL", "default")
        self.timeout = int(os.environ.get("BCUBE_IMAGE_TIMEOUT_SECONDS", "180"))
        self.max_retries = int(os.environ.get("BCUBE_IMAGE_MAX_RETRIES", "3"))
        if not self.url or not self.token:
            raise ProviderError(
                "Real generation requires BCUBE_IMAGE_PROVIDER_URL and "
                "BCUBE_IMAGE_PROVIDER_TOKEN."
            )

    def generate(self, prompt: str, prompt_id: str) -> tuple[bytes, str, dict[str, Any], int]:
        payload = json.dumps(
            {
                "prompt_id": prompt_id,
                "prompt": prompt,
                "model": self.model,
                "size": "A4 portrait",
                "quality": "print-ready",
            }
        ).encode("utf-8")
        attempts = 0
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            attempts = attempt
            request = urllib.request.Request(
                self.url,
                data=payload,
                method="POST",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                    "User-Agent": "BCube-EduOS-Stage2/1.0",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    body = json.loads(response.read().decode("utf-8"))
                encoded = body.get("image_base64")
                if not encoded:
                    raise ProviderError("Provider response has no image_base64 field.")
                extension = str(body.get("extension", "png")).lower().lstrip(".")
                if extension not in SUPPORTED_EXTENSIONS:
                    raise ProviderError(f"Unsupported provider extension: {extension}")
                return base64.b64decode(encoded), extension, body, attempts
            except (urllib.error.URLError, TimeoutError, ValueError, ProviderError) as exc:
                last_error = exc
                if attempt < self.max_retries:
                    time.sleep(min(2 ** (attempt - 1), 8))
        raise ProviderError(f"Provider failed after {attempts} attempts: {last_error}")


def load_catalog_book(slug: str) -> dict[str, Any]:
    if not CATALOG.exists():
        raise FileNotFoundError(f"Catalog not found: {CATALOG}")
    catalog = read_json(CATALOG)
    matches = [book for book in catalog.get("books", []) if book.get("slug") == slug]
    if len(matches) != 1:
        official = ", ".join(book.get("slug", "") for book in catalog.get("books", []))
        raise ValueError(f"Unknown official book slug '{slug}'. Available: {official}")
    book = matches[0]
    if int(book.get("page_count", 0)) != 44:
        raise ValueError(f"Book '{slug}' is not configured for 44 pages.")
    return book


def locate_stage1_queue(slug: str) -> Path:
    candidates = [
        STAGE1 / slug / "generation-queue.json",
        STAGE1 / slug / "manifest.json",
        STAGE1 / "generation-queue.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"No Stage 1 queue found for '{slug}'. Complete Stage 1 compilation first."
    )


def load_prompt_records(slug: str) -> list[PromptRecord]:
    queue_path = locate_stage1_queue(slug)
    data = read_json(queue_path)
    raw_records = data.get("records", data.get("pages", data if isinstance(data, list) else []))
    records: list[PromptRecord] = []
    for item in raw_records:
        if item.get("book_slug") != slug:
            continue
        records.append(
            PromptRecord(
                prompt_id=str(item["prompt_id"]),
                book_slug=slug,
                page_number=int(item["page_number"]),
                prompt_path=str(item["prompt_path"]),
                prompt_sha256=str(item["prompt_sha256"]),
                status=str(item.get("status", "")),
            )
        )
    validate_records(records, slug)
    return sorted(records, key=lambda record: record.page_number)


def validate_records(records: list[PromptRecord], slug: str) -> None:
    errors: list[str] = []
    if len(records) != 44:
        errors.append(f"expected 44 Stage 1 records, found {len(records)}")
    ids = [record.prompt_id for record in records]
    pages = [record.page_number for record in records]
    if len(ids) != len(set(ids)):
        errors.append("duplicate prompt IDs")
    if pages != list(range(1, 45)) and sorted(pages) != list(range(1, 45)):
        errors.append("page numbers must be exactly 1–44")
    for record in records:
        match = PROMPT_ID_RE.match(record.prompt_id)
        if not match or int(match.group(1)) != record.page_number:
            errors.append(f"invalid canonical ID/page mapping: {record.prompt_id}")
        if record.status != "READY":
            errors.append(f"{record.prompt_id} is not READY")
        prompt_path = ROOT / record.prompt_path
        if not prompt_path.exists():
            errors.append(f"missing compiled prompt: {record.prompt_path}")
            continue
        actual_hash = sha256_bytes(prompt_path.read_bytes())
        if actual_hash != record.prompt_sha256:
            errors.append(f"stale prompt hash: {record.prompt_id}")
    if errors:
        raise ValueError(f"Stage 1 entry gate failed for '{slug}': " + "; ".join(errors[:20]))


def run(args: argparse.Namespace) -> int:
    book = load_catalog_book(args.book)
    records = load_prompt_records(args.book)
    output_root = Path(args.output).resolve() / args.book
    request_dir = output_root / "requests"
    response_dir = output_root / "responses"
    pages_dir = output_root / "pages"
    for directory in (request_dir, response_dir, pages_dir):
        directory.mkdir(parents=True, exist_ok=True)

    provider = HttpJsonProvider() if args.mode in {"generate", "resume"} else None
    generation_records: list[GenerationRecord] = []
    failures: list[dict[str, Any]] = []

    for record in records:
        prompt_path = ROOT / record.prompt_path
        prompt = prompt_path.read_text(encoding="utf-8")
        page_stem = f"P{record.page_number:03d}"
        request_payload = {
            "prompt_id": record.prompt_id,
            "book_slug": record.book_slug,
            "page_number": record.page_number,
            "prompt_path": record.prompt_path,
            "prompt_sha256": record.prompt_sha256,
            "model": os.environ.get("BCUBE_IMAGE_MODEL", "default"),
            "created_at": utc_now(),
        }
        write_json(request_dir / f"{page_stem}.json", request_payload)

        existing = next((path for path in pages_dir.glob(f"{page_stem}.*") if path.suffix[1:].lower() in SUPPORTED_EXTENSIONS), None)
        if args.mode == "resume" and existing and existing.stat().st_size > 0 and not args.force:
            generation_records.append(
                GenerationRecord(
                    prompt_id=record.prompt_id,
                    book_slug=record.book_slug,
                    page_number=record.page_number,
                    prompt_sha256=record.prompt_sha256,
                    output_path=str(existing.relative_to(output_root)),
                    output_sha256=sha256_bytes(existing.read_bytes()),
                    provider="existing",
                    model="existing",
                    attempts=0,
                    status="GENERATED",
                    error=None,
                    started_at=utc_now(),
                    completed_at=utc_now(),
                )
            )
            continue

        started = utc_now()
        if args.mode in {"validate", "dry-run"}:
            generation_records.append(
                GenerationRecord(
                    prompt_id=record.prompt_id,
                    book_slug=record.book_slug,
                    page_number=record.page_number,
                    prompt_sha256=record.prompt_sha256,
                    output_path=f"pages/{page_stem}.png",
                    output_sha256=None,
                    provider="not-called",
                    model=os.environ.get("BCUBE_IMAGE_MODEL", "default"),
                    attempts=0,
                    status="VALIDATED" if args.mode == "validate" else "DRY_RUN_READY",
                    error=None,
                    started_at=started,
                    completed_at=utc_now(),
                )
            )
            continue

        assert provider is not None
        try:
            image, extension, metadata, attempts = provider.generate(prompt, record.prompt_id)
            output_path = pages_dir / f"{page_stem}.{extension}"
            if output_path.exists() and not args.force and args.mode != "resume":
                raise FileExistsError(f"Output exists: {output_path}; use --force or resume mode.")
            output_path.write_bytes(image)
            safe_metadata = {key: value for key, value in metadata.items() if key != "image_base64"}
            write_json(response_dir / f"{page_stem}.json", safe_metadata)
            generation_records.append(
                GenerationRecord(
                    prompt_id=record.prompt_id,
                    book_slug=record.book_slug,
                    page_number=record.page_number,
                    prompt_sha256=record.prompt_sha256,
                    output_path=str(output_path.relative_to(output_root)),
                    output_sha256=sha256_bytes(image),
                    provider="http-json",
                    model=str(metadata.get("model", provider.model)),
                    attempts=attempts,
                    status="GENERATED",
                    error=None,
                    started_at=started,
                    completed_at=utc_now(),
                )
            )
        except Exception as exc:  # page failure is recorded and remaining pages continue
            failure = {"prompt_id": record.prompt_id, "page_number": record.page_number, "error": str(exc)}
            failures.append(failure)
            generation_records.append(
                GenerationRecord(
                    prompt_id=record.prompt_id,
                    book_slug=record.book_slug,
                    page_number=record.page_number,
                    prompt_sha256=record.prompt_sha256,
                    output_path=f"pages/{page_stem}.png",
                    output_sha256=None,
                    provider="http-json",
                    model=os.environ.get("BCUBE_IMAGE_MODEL", "default"),
                    attempts=0,
                    status="FAILED",
                    error=str(exc),
                    started_at=started,
                    completed_at=utc_now(),
                )
            )

    generated = sum(record.status == "GENERATED" for record in generation_records)
    manifest = {
        "schema_version": "1.0.0",
        "stage": 2,
        "book": {"slug": args.book, "title": book.get("title"), "number": book.get("number")},
        "mode": args.mode,
        "expected_pages": 44,
        "records": [asdict(record) for record in generation_records],
        "generated": generated,
        "failed": len(failures),
        "stage3_ready": generated == 44 and not failures,
        "created_at": utc_now(),
    }
    write_json(output_root / "generation-manifest.json", manifest)
    write_json(output_root / "failed-pages.json", failures)
    summary = (
        f"# Stage 2 Summary — {book.get('title')}\n\n"
        f"- Mode: `{args.mode}`\n"
        f"- Records: {len(generation_records)}/44\n"
        f"- Generated: {generated}/44\n"
        f"- Failed: {len(failures)}\n"
        f"- Stage 3 ready: {'YES' if manifest['stage3_ready'] else 'NO'}\n"
    )
    (output_root / "stage2-summary.md").write_text(summary, encoding="utf-8")

    print(summary)
    if args.mode in {"generate", "resume"} and not manifest["stage3_ready"]:
        return 2
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate one 44-page BCube book.")
    parser.add_argument("--book", required=True, help="Official book slug from books/catalog.json")
    parser.add_argument("--mode", choices=("validate", "dry-run", "generate", "resume"), default="validate")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    try:
        sys.exit(run(parse_args()))
    except Exception as exc:
        print(f"Stage 2 failed: {exc}", file=sys.stderr)
        sys.exit(1)
