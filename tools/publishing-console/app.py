#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

ROOT = Path(__file__).resolve().parents[2]
BOOKS_FILE = ROOT / "bcube-publishing-sdk/books/cover-books.json"
PUBLISH_SCRIPT = ROOT / "scripts/bcube_publish.py"
UPLOADS = ROOT / "production-renders/web-console/uploads"
WORK = ROOT / "production-renders/v5"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024
UPLOADS.mkdir(parents=True, exist_ok=True)


def load_registry() -> dict:
    return json.loads(BOOKS_FILE.read_text(encoding="utf-8"))


def page_id_for(level: str, book_slug: str, physical_page: int) -> str:
    registry = load_registry()
    level_data = registry["levels"][level]
    book = level_data["books"][book_slug]
    return f"{book['prefix']}-{level_data['id_level']}-V4-P{physical_page:03d}"


def save_upload() -> Path:
    uploaded = request.files.get("illustration")
    if uploaded is None or not uploaded.filename:
        raise ValueError("Choose an illustration file.")
    suffix = Path(uploaded.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError("Illustration must be PNG, JPG, JPEG or WEBP.")
    filename = f"{uuid.uuid4().hex}-{secure_filename(uploaded.filename)}"
    destination = UPLOADS / filename
    uploaded.save(destination)
    return destination


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/registry")
def registry():
    value = load_registry()
    levels = {}
    for slug, level in value["levels"].items():
        levels[slug] = {
            "display_level": level["display_level"],
            "age": level["age"],
            "id_level": level["id_level"],
            "books": {
                book_slug: {
                    "title": " ".join(book["title_lines"]),
                    "prefix": book["prefix"],
                }
                for book_slug, book in level["books"].items()
            },
        }
    return jsonify({"series": value["series"], "levels": levels})


@app.post("/api/publish")
def publish():
    try:
        level = request.form.get("level", "").strip()
        book = request.form.get("book", "").strip()
        page_type = request.form.get("page_type", "cover").strip()
        provider = request.form.get("provider", "manual").strip()
        if level not in {"nursery", "lkg", "ukg"}:
            raise ValueError("Select a valid level.")
        registry = load_registry()
        if book not in registry["levels"][level]["books"]:
            raise ValueError("Select a valid book.")
        illustration = save_upload()
        command = [
            sys.executable,
            str(PUBLISH_SCRIPT),
            "--level", level,
            "--book", book,
            "--provider", provider,
            "--illustration", str(illustration),
            "--confirm-clean-illustration",
        ]
        if page_type == "cover":
            command += ["--page", "cover"]
        else:
            physical_page = int(request.form.get("physical_page", "0"))
            printed_page = int(request.form.get("page_number", "0"))
            if physical_page < 1:
                raise ValueError("Physical page must be at least 1.")
            command += [
                "--page", "activity",
                "--physical-page", str(physical_page),
                "--page-number", str(printed_page),
                "--page-id", request.form.get("page_id") or page_id_for(level, book, physical_page),
                "--activity-type", request.form.get("activity_type", page_type),
                "--title", request.form.get("title", "").strip(),
                "--objective", request.form.get("objective", "").strip(),
                "--instruction", request.form.get("instruction", "").strip(),
                "--teacher-prompt", request.form.get("teacher_prompt", "").strip(),
                "--parent-prompt", request.form.get("parent_prompt", "").strip(),
            ]
        if request.form.get("approve") == "true":
            reviewer = request.form.get("reviewer", "").strip()
            if not reviewer:
                raise ValueError("Reviewer is required for approval.")
            command += ["--approve", "--reviewer", reviewer]
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=900)
        return jsonify({
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "command": command,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }), 200 if completed.returncode == 0 else 400
    except (ValueError, KeyError, TimeoutError, subprocess.TimeoutExpired) as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/artifact/<path:relative_path>")
def artifact(relative_path: str):
    target = (ROOT / relative_path).resolve()
    if ROOT not in target.parents or not target.is_file():
        return jsonify({"ok": False, "error": "Artifact not found."}), 404
    return send_from_directory(target.parent, target.name)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
