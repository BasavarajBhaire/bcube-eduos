#!/usr/bin/env python3
"""BCube Phase 6 provider-independent illustration automation.

No OpenAI dependency. Supports manual queueing, local command execution,
ComfyUI HTTP generation, deterministic CI generation, QA, retries and queues.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageStat

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "bcube-publishing-sdk/books/cover-books.json"
ENGINE = ROOT / "illustration-engine"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_book(level: str, slug: str) -> None:
    registry = load_json(REGISTRY)
    level_data = registry.get("levels", {}).get(level)
    if not isinstance(level_data, dict):
        raise ValueError(f"Unknown level: {level}")
    if slug not in level_data.get("books", {}):
        raise ValueError(f"Unknown {level.upper()} book {slug!r}")


def prompt_files(level: str, slug: str) -> list[Path]:
    candidates = [
        ROOT / "production-prompts" / slug / level / "v4" / "pages",
        ROOT / "production-prompts" / slug / level / "V4" / "pages",
        ROOT / "production-prompts" / level / slug / "v4" / "pages",
    ]
    for directory in candidates:
        if directory.is_dir():
            found = sorted(directory.glob("*.json"))
            if found:
                return found
    token = f"-{level.upper()}-V4-P"
    return sorted(
        path for path in (ROOT / "production-prompts").rglob("*.json")
        if token in path.name and slug in str(path).lower()
    )


def extract_prompt(data: dict[str, Any], path: Path) -> tuple[str, str]:
    page_id = str(data.get("page_id") or data.get("prompt_id") or path.stem)
    for key in ("illustration_prompt", "prompt", "production_prompt", "full_prompt", "art_direction"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return page_id, value.strip()
    illustration = data.get("illustration")
    if isinstance(illustration, str) and illustration.strip():
        return page_id, illustration.strip()
    if isinstance(illustration, dict):
        for key in ("prompt", "description", "art_direction"):
            value = illustration.get(key)
            if isinstance(value, str) and value.strip():
                return page_id, value.strip()
    raise ValueError(f"No illustration prompt found in {path}")


@dataclass
class Job:
    page_id: str
    prompt: str
    source: str
    output: Path


class Provider:
    name = "base"
    def generate(self, job: Job) -> Path:
        raise NotImplementedError


class ManualProvider(Provider):
    name = "manual"
    def generate(self, job: Job) -> Path:
        raise RuntimeError(f"MANUAL_REQUIRED: place an image at {job.output}")


class MockProvider(Provider):
    name = "mock"
    def generate(self, job: Job) -> Path:
        job.output.parent.mkdir(parents=True, exist_ok=True)
        image = Image.new("RGB", (1254, 1254), "white")
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((70, 70, 1184, 1184), radius=100, fill="#F7D66A")
        draw.ellipse((250, 250, 1004, 1004), fill="#7CC8F5")
        image.save(job.output, "PNG", dpi=(300, 300))
        return job.output


class CommandProvider(Provider):
    name = "command"
    def __init__(self, command: str | None):
        if not command:
            raise ValueError("--command is required for provider=command")
        self.command = command

    def generate(self, job: Job) -> Path:
        job.output.parent.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env.update({"BCUBE_PROMPT": job.prompt, "BCUBE_OUTPUT": str(job.output), "BCUBE_PAGE_ID": job.page_id})
        command = self.command.format(prompt=job.prompt, output=str(job.output), page_id=job.page_id)
        subprocess.run(command, shell=True, cwd=ROOT, env=env, check=True)
        if not job.output.is_file():
            raise FileNotFoundError(f"Local generator did not create {job.output}")
        return job.output


class ComfyUIProvider(Provider):
    name = "comfyui"
    def __init__(self, server: str, workflow: Path | None, timeout: int):
        if workflow is None:
            raise ValueError("--workflow is required for provider=comfyui")
        self.server = server.rstrip("/")
        self.workflow = load_json(workflow)
        self.timeout = timeout

    def generate(self, job: Job) -> Path:
        raw = json.dumps(self.workflow).replace("{{BCUBE_PROMPT}}", job.prompt).replace("{{BCUBE_PAGE_ID}}", job.page_id)
        payload = json.dumps({"prompt": json.loads(raw)}).encode("utf-8")
        request = urllib.request.Request(self.server + "/prompt", data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=30) as response:
            prompt_id = json.loads(response.read().decode("utf-8"))["prompt_id"]
        deadline = time.time() + self.timeout
        while time.time() < deadline:
            with urllib.request.urlopen(self.server + f"/history/{prompt_id}", timeout=30) as response:
                history = json.loads(response.read().decode("utf-8"))
            entry = history.get(prompt_id)
            if entry:
                for node in entry.get("outputs", {}).values():
                    for image in node.get("images", []):
                        params = urllib.parse.urlencode({"filename": image["filename"], "subfolder": image.get("subfolder", ""), "type": image.get("type", "output")})
                        job.output.parent.mkdir(parents=True, exist_ok=True)
                        urllib.request.urlretrieve(self.server + "/view?" + params, job.output)
                        return job.output
            time.sleep(2)
        raise TimeoutError(f"ComfyUI generation timed out for {job.page_id}")


def validate_image(path: Path, min_occupancy: float, require_square: bool) -> dict[str, Any]:
    defects: list[str] = []
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            rgba = image.convert("RGBA")
            width, height = rgba.size
            if width < 1024 or height < 1024:
                defects.append("IMAGE_TOO_SMALL")
            if require_square and abs(width - height) > max(width, height) * 0.02:
                defects.append("NOT_SQUARE")
            rgb = Image.new("RGB", rgba.size, "white")
            rgb.paste(rgba, mask=rgba.getchannel("A"))
            diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, "white")).convert("L")
            bbox = diff.point(lambda p: 255 if p > 18 else 0).getbbox()
            occupancy = 0.0 if not bbox else ((bbox[2]-bbox[0]) * (bbox[3]-bbox[1])) / (width * height)
            if occupancy < min_occupancy:
                defects.append("LOW_OCCUPANCY")
            border = max(4, int(min(width, height) * 0.02))
            strips = [rgb.crop((0,0,width,border)), rgb.crop((0,height-border,width,height)), rgb.crop((0,0,border,height)), rgb.crop((width-border,0,width,height))]
            border_mean = sum(sum(ImageStat.Stat(strip).mean) / 3 for strip in strips) / len(strips)
            if border_mean < 235:
                defects.append("BORDER_NOT_WHITE")
            dpi = image.info.get("dpi", (0,0))[0]
            return {"status":"PASS" if not defects else "FAIL","path":str(path),"size":[width,height],"dpi":dpi,"occupancy":round(occupancy,4),"border_mean":round(border_mean,2),"sha256":sha256(path),"defects":defects}
    except Exception as exc:
        return {"status":"FAIL","path":str(path),"defects":[f"UNREADABLE_IMAGE: {exc}"]}


def make_provider(args: argparse.Namespace) -> Provider:
    if args.provider == "manual": return ManualProvider()
    if args.provider == "mock": return MockProvider()
    if args.provider == "command": return CommandProvider(args.command)
    if args.provider == "comfyui": return ComfyUIProvider(args.comfyui_server, args.workflow, args.timeout)
    raise ValueError(args.provider)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", choices=["nursery","lkg","ukg"], required=True)
    parser.add_argument("--book", required=True)
    parser.add_argument("--page-id")
    parser.add_argument("--provider", choices=["manual","command","comfyui","mock"], default="manual")
    parser.add_argument("--command")
    parser.add_argument("--comfyui-server", default="http://127.0.0.1:8188")
    parser.add_argument("--workflow", type=Path)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--min-occupancy", type=float, default=0.55)
    parser.add_argument("--require-square", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    validate_book(args.level, args.book)
    sources = prompt_files(args.level, args.book)
    if not sources:
        raise FileNotFoundError(f"No V4 prompt JSON files found for {args.level}/{args.book}")
    provider = make_provider(args)
    pending = ENGINE / "queue/pending" / args.level / args.book
    approved = ENGINE / "queue/approved" / args.level / args.book
    rejected = ENGINE / "queue/rejected" / args.level / args.book
    reports = ENGINE / "reports" / args.level / args.book
    results: list[dict[str, Any]] = []
    for source in sources:
        try:
            page_id, prompt = extract_prompt(load_json(source), source)
        except ValueError:
            continue
        if args.page_id and page_id != args.page_id:
            continue
        output = pending / f"{page_id}.png"
        job = Job(page_id, prompt, str(source.relative_to(ROOT)), output)
        if args.dry_run:
            results.append({"page_id":page_id,"state":"PLANNED","source":job.source,"output":str(output)})
            continue
        state, report, error = "FAILED", {}, None
        for attempt in range(args.max_retries + 1):
            try:
                generated = provider.generate(job)
                report = validate_image(generated, args.min_occupancy, args.require_square)
                report["attempt"] = attempt + 1
                if report["status"] == "PASS":
                    approved.mkdir(parents=True, exist_ok=True)
                    final = approved / generated.name
                    shutil.copy2(generated, final)
                    report["approved_path"] = str(final)
                    state = "APPROVED"
                    break
                error = ", ".join(report.get("defects", []))
            except RuntimeError as exc:
                error, state = str(exc), "MANUAL_REQUIRED"
                break
            except Exception as exc:
                error = str(exc)
        if state not in {"APPROVED","MANUAL_REQUIRED"} and output.exists():
            rejected.mkdir(parents=True, exist_ok=True)
            shutil.copy2(output, rejected / output.name)
            state = "REJECTED"
        reports.mkdir(parents=True, exist_ok=True)
        item = {"page_id":page_id,"provider":provider.name,"state":state,"source":job.source,"prompt_sha256":hashlib.sha256(prompt.encode()).hexdigest(),"qa":report,"error":error}
        (reports / f"{page_id}.json").write_text(json.dumps(item, indent=2) + "\n", encoding="utf-8")
        results.append(item)
    summary = {"phase":"6","level":args.level,"book":args.book,"provider":provider.name,"total":len(results),"approved":sum(r.get("state")=="APPROVED" for r in results),"manual_required":sum(r.get("state")=="MANUAL_REQUIRED" for r in results),"failed":sum(r.get("state") in {"FAILED","REJECTED"} for r in results),"results":results}
    summary_path = reports / "summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k != "results"} | {"summary":str(summary_path)}, indent=2))
    return 0 if summary["failed"] == 0 else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, subprocess.CalledProcessError, TimeoutError) as exc:
        print(f"BCube Phase 6 ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
