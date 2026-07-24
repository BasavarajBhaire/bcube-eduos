#!/usr/bin/env python3
"""Local BCube Publishing Console.

Runs only on localhost and delegates page creation to scripts/bcube_publish.py.
"""
from __future__ import annotations

import json
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
UPLOADS = ROOT / "production-renders/v5/console-uploads"
ALLOWED = {".png", ".jpg", ".jpeg", ".webp"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024
page_data = PageDataRegistry(ROOT, REGISTRY)


def registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def require(form, *names: str) -> None:
    missing = [name for name in names if not str(form.get(name, "")).strip()]
    if missing:
        raise ValueError("Missing required fields: " + ", ".join(missing))


def save_upload() -> Path:
    upload = request.files.get("illustration")
    if upload is None or not upload.filename:
        raise ValueError("Choose an illustration file")
    suffix = Path(upload.filename).suffix.lower()
    if suffix not in ALLOWED:
        raise ValueError("Illustration must be PNG, JPG, JPEG, or WEBP")
    UPLOADS.mkdir(parents=True, exist_ok=True)
    name = f"{uuid.uuid4().hex}-{secure_filename(upload.filename)}"
    target = UPLOADS / name
    upload.save(target)
    return target


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
        return jsonify({"ok": True, "pages": [record.public_dict() for record in records]})
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/publish")
def publish():
    uploaded: Path | None = None
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
        uploaded = save_upload()
        command = [
            sys.executable,
            str(PUBLISH),
            "--level", form["level"],
            "--book", form["book"],
            "--provider", "manual",
            "--illustration", str(uploaded),
            "--confirm-clean-illustration",
        ]
        if record.page_type == "cover":
            command += ["--page", "cover"]
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
        payload = {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "command": command[1:],
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "page": record.public_dict(),
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
