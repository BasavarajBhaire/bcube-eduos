#!/usr/bin/env python3
"""Local BCube Publishing Console.

Runs only on localhost and delegates page creation to scripts/bcube_publish.py.
The existing level/book/page selectors also define deterministic storage paths.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from page_data_registry import PageDataRegistry

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "bcube-publishing-sdk/books/cover-books.json"
PUBLISH = ROOT / "scripts/bcube_publish.py"
WORK = ROOT / "production-renders/v5"
UPLOADS = WORK / "console-uploads"
STRUCTURED_PAGES = ROOT / "production-renders/pages-by-level"
STRUCTURED_ILLUSTRATIONS = ROOT / "production-renders/illustrations-by-level"
ALLOWED = {".png", ".jpg", ".jpeg", ".webp"}
APPROVED_ARCHETYPE_ACTIVITIES = {"match", "sort", "speak", "observe"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024
page_data = PageDataRegistry(ROOT, REGISTRY)


def registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def require(form, *names: str) -> None:
    missing = [name for name in names if not str(form.get(name, "")).strip()]
    if missing:
        raise ValueError("Missing required fields: " + ", ".join(missing))


def level_folder(level: str) -> str:
    values = registry().get("levels", {}).get(level, {})
    return str(values.get("display_level") or level).strip().replace(" ", "-")


def safe_storage_path(base: Path, level: str, book: str, page_id: str, suffix: str = ".png") -> Path:
    level_name = secure_filename(level_folder(level)) or secure_filename(level)
    book_name = secure_filename(book)
    page_name = secure_filename(page_id)
    if not level_name or not book_name or not page_name:
        raise ValueError("Cannot resolve structured output path")
    return base / level_name / book_name / f"{page_name}{suffix.lower()}"


def save_upload(*, level: str, book: str, page_id: str) -> tuple[Path, Path]:
    upload = request.files.get("illustration")
    if upload is None or not upload.filename:
        raise ValueError("Choose an illustration file")
    suffix = Path(upload.filename).suffix.lower()
    if suffix not in ALLOWED:
        raise ValueError("Illustration must be PNG, JPG, JPEG, or WEBP")

    expected_stem = secure_filename(page_id).casefold()
    actual_stem = secure_filename(Path(upload.filename).stem).casefold()
    if actual_stem != expected_stem:
        raise ValueError(
            f"Illustration filename must match page ID: expected {page_id}{suffix}, received {upload.filename}"
        )

    UPLOADS.mkdir(parents=True, exist_ok=True)
    temporary = UPLOADS / f"{uuid.uuid4().hex}-{secure_filename(upload.filename)}"
    upload.save(temporary)

    structured = safe_storage_path(STRUCTURED_ILLUSTRATIONS, level, book, page_id, suffix)
    structured.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(temporary, structured)
    return temporary, structured


def store_generated_page(*, level: str, book: str, page_id: str, approving: bool) -> Path:
    state_folder = "approved" if approving else "candidates"
    source = WORK / state_folder / "pages" / f"{page_id}.png"
    if not source.is_file():
        raise FileNotFoundError(f"Generated page was not created: {source}")
    destination = safe_storage_path(STRUCTURED_PAGES, level, book, page_id, ".png")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return destination


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/books")
def books():
    data = registry()
    result = {}
    for level, level_data in data["levels"].items():
        result[level] = {
            "label": level_data["display_level"],
            "age": level_data["age"],
            "id_level": level_data["id_level"],
            "books": {
                slug: {
                    "title": " ".join(book["title_lines"]),
                    "prefix": book["prefix"],
                }
                for slug, book in level_data["books"].items()
            },
        }
    return jsonify(result)


@app.get("/api/pages")
def pages():
    try:
        level = str(request.args.get("level") or "").strip()
        book = str(request.args.get("book") or "").strip()
        if not level or not book:
            raise ValueError("Select a level and book")
        records = page_data.list_pages(level, book)
        public_records = []
        for record in records:
            value = record.public_dict()
            value["approved_archetype_rollout"] = record.activity_type in APPROVED_ARCHETYPE_ACTIVITIES
            value["structured_output_path"] = str(
                safe_storage_path(STRUCTURED_PAGES, level, book, record.page_id, ".png").relative_to(ROOT)
            )
            value["structured_illustration_path"] = str(
                safe_storage_path(STRUCTURED_ILLUSTRATIONS, level, book, record.page_id, ".png").relative_to(ROOT)
            )
            public_records.append(value)
        return jsonify({"ok": True, "pages": public_records})
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/publish")
def publish():
    uploaded: Path | None = None
    structured_illustration: Path | None = None
    try:
        form = request.form
        require(form, "level", "book", "physical_page")
        try:
            physical_page = int(form["physical_page"])
        except (TypeError, ValueError) as exc:
            raise ValueError("Physical page must be a positive integer") from exc
        approving = form.get("approve") == "true"
        if approving:
            require(form, "reviewer")
        record = page_data.get_page(form["level"], form["book"], physical_page)
        if record.learning_contract:
            content_status = record.learning_contract.get("status")
            if content_status != "READY_FOR_ILLUSTRATION_REVIEW":
                issues = record.learning_contract.get("issues") or ["Unresolved learning-page contract"]
                raise ValueError(
                    f"{record.page_id} is blocked for editorial refinement: " + "; ".join(issues)
                )
        command = [
            sys.executable,
            str(PUBLISH),
            "--level", form["level"],
            "--book", form["book"],
        ]
        if record.public_dict()["requires_illustration"]:
            uploaded, structured_illustration = save_upload(
                level=form["level"], book=form["book"], page_id=record.page_id
            )
            command += [
                "--provider", "manual",
                "--illustration", str(uploaded),
                "--confirm-clean-illustration",
            ]
        if record.page_type == "cover":
            command += ["--page", "cover"]
        elif record.page_type == "about-book":
            command += [
                "--page", "about",
                "--physical-page", str(record.physical_page),
                "--page-id", record.page_id,
                "--title", record.title,
                "--objective", record.objective,
                "--instruction", record.instruction,
            ]
        elif record.page_type == "copyright":
            command += [
                "--page", "publisher",
                "--physical-page", str(record.physical_page),
                "--page-id", record.page_id,
            ]
        elif record.page_type == "contents":
            command += [
                "--page", "contents",
                "--physical-page", str(record.physical_page),
                "--page-id", record.page_id,
                "--title", record.title,
            ]
        elif record.page_type == "welcome":
            command += [
                "--page", "welcome",
                "--physical-page", str(record.physical_page),
                "--page-number", str(record.printed_page if record.printed_visible else 0),
                "--page-id", record.page_id,
                "--title", record.title,
                "--objective", record.objective,
                "--instruction", record.instruction,
            ]
        elif record.page_type == "meet-star":
            command += [
                "--page", "meet-star",
                "--physical-page", str(record.physical_page),
                "--page-number", str(record.printed_page if record.printed_visible else 0),
                "--page-id", record.page_id,
                "--title", record.title,
                "--objective", record.objective,
                "--instruction", record.instruction,
            ]
        else:
            command += [
                "--page", "activity",
                "--physical-page", str(record.physical_page),
                "--page-number", str(record.printed_page if record.printed_visible else 0),
                "--page-id", record.page_id,
                "--activity-type", str(record.activity_type),
                "--title", record.title,
                "--objective", record.objective,
                "--instruction", record.instruction,
                "--teacher-prompt", record.teacher_prompt,
                "--parent-prompt", record.parent_prompt,
            ]
        if approving:
            command += ["--approve", "--reviewer", form["reviewer"]]
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=900,
            check=False,
        )
        structured_page: Path | None = None
        storage_error: str | None = None
        if completed.returncode == 0:
            try:
                structured_page = store_generated_page(
                    level=form["level"], book=form["book"], page_id=record.page_id, approving=approving
                )
            except (OSError, ValueError) as exc:
                storage_error = str(exc)
        payload = {
            "ok": completed.returncode == 0 and storage_error is None,
            "returncode": completed.returncode,
            "command": command[1:],
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "page": record.public_dict(),
            "approved_archetype_rollout": record.activity_type in APPROVED_ARCHETYPE_ACTIVITIES,
            "structured_page": str(structured_page.relative_to(ROOT)) if structured_page else None,
            "structured_illustration": (
                str(structured_illustration.relative_to(ROOT)) if structured_illustration else None
            ),
            "storage_error": storage_error,
        }
        return jsonify(payload), 200 if payload["ok"] else 400
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/artifacts/<path:filename>")
def artifacts(filename: str):
    base = (ROOT / "production-renders").resolve()
    target = (base / filename).resolve()
    if base not in target.parents and target != base:
        return jsonify({"ok": False, "error": "Invalid artifact path"}), 400
    return send_from_directory(base, filename)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
