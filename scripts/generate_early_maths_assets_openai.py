#!/usr/bin/env python3
"""Generate individual Early Maths curriculum-first assets with the OpenAI Images API.

The script reads the approved P009-P021 curriculum blueprint, generates one image
per named asset, saves exact filenames under page folders, skips existing files
by default, retries transient failures, and writes a resumable JSON report.

No OpenAI SDK dependency is required; it uses the HTTPS API directly.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "curriculum" / "early-maths-adventures" / "lkg" / "curriculum-first-p009-p021-v1.json"
DEFAULT_ENDPOINT = "https://api.openai.com/v1/images/generations"
SUPPORTED_MODELS = ("gpt-image-1", "gpt-image-1-mini")
SUPPORTED_SIZES = ("1024x1024", "1024x1536", "1536x1024", "auto")
SUPPORTED_QUALITY = ("low", "medium", "high", "auto")
SUPPORTED_BACKGROUND = ("transparent", "opaque", "auto")

COMMON_PROMPT = """Create exactly one isolated preschool workbook illustration asset.
Book: Early Maths Adventures. Level: LKG (4+).
Premium children's publishing quality; clean rounded outlines; bright friendly colours;
large recognisable forms; correct anatomy; correct object count; simple uncluttered composition.
Keep every important element fully inside the canvas with 12-18% clear padding on every side.
Use a transparent background. Do not add text, numerals, labels, title, logo, mascot, border,
worksheet controls, answer marks, arrows, watermark, shadows touching the canvas edge, or extra objects.
The output must contain only the requested asset and must be suitable for direct placement on a workbook page.
"""


@dataclass
class AssetResult:
    page_id: str
    asset_name: str
    status: str
    output_path: str
    prompt_sha256: str
    image_sha256: str = ""
    attempts: int = 0
    error: str = ""


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object expected: {path}")
    return value


def parse_pages(raw: str | None, available: list[str]) -> list[str]:
    if not raw or raw.strip().lower() in {"all", "*"}:
        return available
    selected: list[str] = []
    aliases = {page_id.split("-")[-1].upper(): page_id for page_id in available}
    for token in raw.split(","):
        value = token.strip().upper()
        if not value:
            continue
        if value in available:
            page_id = value
        elif value in aliases:
            page_id = aliases[value]
        elif value.startswith("P") and value[1:].isdigit():
            page_id = aliases.get(f"P{int(value[1:]):03d}", "")
        else:
            page_id = ""
        if not page_id:
            raise ValueError(f"Unknown page selector: {token!r}")
        if page_id not in selected:
            selected.append(page_id)
    return selected


def build_prompt(page_id: str, page: dict[str, Any], asset_name: str, description: str) -> str:
    return (
        f"{COMMON_PROMPT}\n"
        f"Page ID: {page_id}\n"
        f"Page title: {page['title']}\n"
        f"Learning objective: {page['objective']}\n"
        f"Child action: {page['instruction']}\n"
        f"Exact asset filename: {asset_name}.png\n"
        f"Create: {description}.\n"
        "Count lock: any stated quantity is exact. Do not add or omit objects. "
        "Arrange repeated objects with clear separation so a four-year-old can count each item once."
    )


def api_request(*, endpoint: str, api_key: str, model: str, prompt: str, size: str,
                quality: str, background: str, timeout: int) -> tuple[bytes, dict[str, Any]]:
    body = json.dumps({
        "model": model,
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "background": background,
        "output_format": "png",
        "n": 1,
    }).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "bcube-eduos-asset-generator/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    data = payload.get("data")
    if not isinstance(data, list) or not data:
        raise RuntimeError("OpenAI response did not contain image data")
    encoded = data[0].get("b64_json")
    if not isinstance(encoded, str) or not encoded:
        raise RuntimeError("OpenAI response did not contain data[0].b64_json")
    return base64.b64decode(encoded), payload


def is_retryable(exc: Exception) -> bool:
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code in {408, 409, 429, 500, 502, 503, 504}
    return isinstance(exc, (urllib.error.URLError, TimeoutError, ConnectionError))


def error_text(exc: Exception) -> str:
    if isinstance(exc, urllib.error.HTTPError):
        try:
            body = exc.read().decode("utf-8", errors="replace")
            payload = json.loads(body)
            message = payload.get("error", {}).get("message")
            if message:
                return f"HTTP {exc.code}: {message}"
        except Exception:
            pass
        return f"HTTP {exc.code}: {exc.reason}"
    return str(exc)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate individual Early Maths assets with OpenAI")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--pages", help="Comma-separated selectors such as P009,P018,P021; default: all pages requiring art")
    parser.add_argument("--model", choices=SUPPORTED_MODELS, default="gpt-image-1")
    parser.add_argument("--size", choices=SUPPORTED_SIZES, default="1024x1024")
    parser.add_argument("--quality", choices=SUPPORTED_QUALITY, default="high")
    parser.add_argument("--background", choices=SUPPORTED_BACKGROUND, default="transparent")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--endpoint", default=os.environ.get("OPENAI_IMAGES_ENDPOINT", DEFAULT_ENDPOINT))
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--delay-seconds", type=float, default=1.0)
    parser.add_argument("--fail-fast", action="store_true")
    args = parser.parse_args()

    if args.max_retries < 0:
        raise SystemExit("--max-retries must be zero or greater")
    blueprint = load_json(BLUEPRINT)
    pages = blueprint.get("pages", {})
    art_pages = [page_id for page_id, page in pages.items() if page.get("illustration_assets")]
    selected = parse_pages(args.pages, art_pages)
    api_key = os.environ.get(args.api_key_env, "").strip()
    if not args.dry_run and not api_key:
        raise SystemExit(f"Environment variable {args.api_key_env} is not set")

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[AssetResult] = []
    started_at = int(time.time())

    for page_id in selected:
        page = pages[page_id]
        page_dir = output_dir / page_id
        page_dir.mkdir(parents=True, exist_ok=True)
        for asset_name, description in page["illustration_assets"].items():
            output = page_dir / f"{asset_name}.png"
            prompt = build_prompt(page_id, page, asset_name, description)
            prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
            if output.is_file() and not args.overwrite:
                results.append(AssetResult(page_id, asset_name, "SKIPPED_EXISTS", str(output), prompt_hash,
                                           hashlib.sha256(output.read_bytes()).hexdigest()))
                print(f"SKIP {page_id}/{asset_name}.png")
                continue
            if args.dry_run:
                results.append(AssetResult(page_id, asset_name, "DRY_RUN", str(output), prompt_hash))
                print(f"DRY  {page_id}/{asset_name}.png")
                continue

            attempts = 0
            while True:
                attempts += 1
                try:
                    image_bytes, _ = api_request(
                        endpoint=args.endpoint,
                        api_key=api_key,
                        model=args.model,
                        prompt=prompt,
                        size=args.size,
                        quality=args.quality,
                        background=args.background,
                        timeout=args.timeout,
                    )
                    temp = output.with_suffix(".png.part")
                    temp.write_bytes(image_bytes)
                    temp.replace(output)
                    image_hash = hashlib.sha256(image_bytes).hexdigest()
                    results.append(AssetResult(page_id, asset_name, "GENERATED", str(output), prompt_hash,
                                               image_hash, attempts))
                    print(f"DONE {page_id}/{asset_name}.png")
                    break
                except Exception as exc:
                    message = error_text(exc)
                    if attempts <= args.max_retries and is_retryable(exc):
                        wait = min(60.0, (2 ** (attempts - 1)) + random.random())
                        print(f"RETRY {page_id}/{asset_name}.png in {wait:.1f}s: {message}", file=sys.stderr)
                        time.sleep(wait)
                        continue
                    results.append(AssetResult(page_id, asset_name, "FAILED", str(output), prompt_hash,
                                               attempts=attempts, error=message))
                    print(f"FAIL {page_id}/{asset_name}.png: {message}", file=sys.stderr)
                    if args.fail_fast:
                        break
                    break
            if args.fail_fast and results[-1].status == "FAILED":
                break
            if args.delay_seconds > 0:
                time.sleep(args.delay_seconds)
        if args.fail_fast and results and results[-1].status == "FAILED":
            break

    summary = {
        "schema_version": "bcube-openai-image-generation-report-v1",
        "started_at_unix": started_at,
        "finished_at_unix": int(time.time()),
        "blueprint": str(BLUEPRINT),
        "model": args.model,
        "size": args.size,
        "quality": args.quality,
        "background": args.background,
        "endpoint": args.endpoint,
        "selected_pages": selected,
        "generated": sum(r.status == "GENERATED" for r in results),
        "skipped": sum(r.status == "SKIPPED_EXISTS" for r in results),
        "dry_run": sum(r.status == "DRY_RUN" for r in results),
        "failed": sum(r.status == "FAILED" for r in results),
        "results": [asdict(r) for r in results],
    }
    report = output_dir / "generation-report.json"
    report.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("generated", "skipped", "dry_run", "failed")}, indent=2))
    print(f"Report: {report}")
    return 0 if summary["failed"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
