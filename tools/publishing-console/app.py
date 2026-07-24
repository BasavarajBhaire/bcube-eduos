#!/usr/bin/env python3
"""Local BCube Publishing Web Console.

Runs only on localhost and delegates page generation to scripts/bcube_publish.py.
"""
from __future__ import annotations

import json
import subprocess
import sys
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

ROOT = Path(__file__).resolve().parents[2]
BOOKS_PATH = ROOT / "bcube-publishing-sdk/books/cover-books.json"
PUBLISH_SCRIPT = ROOT / "scripts/bcube_publish.py"
UPLOAD_DIR = ROOT / "production-renders/console-uploads"
OUTPUT_DIR = ROOT / "production-renders/v5"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 40 * 1024 * 1024


def load_registry() -> dict:
    return json.loads(BOOKS_PATH.read_text(encoding="utf-8"))


def page_id_for(level: str, book: str, physical_page: int) -> str:
    registry = load_registry()
    level_data = registry["levels"][level]
    book_data = level_data["books"][book]
    return f"{book_data['prefix']}-{level_data['id_level']}-V4-P{physical_page:03d}"


def save_upload() -> Path:
    upload = request.files.get("illustration")
    if not upload or not upload.filename:
        raise ValueError("Choose an illustration file.")
    suffix = Path(upload.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError("Illustration must be PNG, JPG, JPEG, or WEBP.")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    target = UPLOAD_DIR / f"{uuid.uuid4().hex}-{secure_filename(upload.filename)}"
    upload.save(target)
    return target


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/books")
def books():
    registry = load_registry()
    response = {}
    for level, level_data in registry.get("levels", {}).items():
        response[level] = {
            "display_level": level_data.get("display_level", level.title()),
            "age": level_data.get("age", ""),
            "books": [
                {
                    "slug": slug,
                    "title": " ".join(book.get("title_lines", [slug])),
                    "prefix": book.get("prefix", ""),
                }
                for slug, book in level_data.get("books", {}).items()
            ],
        }
    return jsonify(response)


@app.post("/api/publish")
def publish():
    illustration = None
    try:
        level = request.form["level"].strip()
        book = request.form["book"].strip()
        page_kind = request.form.get("page_kind", "cover").strip()
        provider = request.form.get("provider", "manual").strip()
        illustration = save_upload()

        command = [
            sys.executable,
            str(PUBLISH_SCRIPT),
            "--level", level,
            "--book", book,
            "--page", "cover" if page_kind == "cover" else "activity",
            "--provider", provider,
            "--illustration", str(illustration),
            "--confirm-clean-illustration",
        ]

        generated_page_id = None
        if page_kind != "cover":
            physical_page = int(request.form["physical_page"])
            page_number = int(request.form.get("page_number") or 0)
            generated_page_id = request.form.get("page_id") or page_id_for(level, book, physical_page)
            required_fields = {
                "activity_type": request.form.get("activity_type"),
                "title": request.form.get("title"),
                "objective": request.form.get("objective"),
                "instruction": request.form.get("instruction"),
                "teacher_prompt": request.form.get("teacher_prompt"),
                "parent_prompt": request.form.get("parent_prompt"),
            }
            missing = [name for name, value in required_fields.items() if not (value or "").strip()]
            if missing:
                raise ValueError("Complete these fields: " + ", ".join(missing))
            command += [
                "--physical-page", str(physical_page),
                "--page-number", str(page_number),
                "--page-id", generated_page_id,
                "--activity-type", required_fields["activity_type"].strip(),
                "--title", required_fields["title"].strip(),
                "--objective", required_fields["objective"].strip(),
                "--instruction", required_fields["instruction"].strip(),
                "--teacher-prompt", required_fields["teacher_prompt"].strip(),
                "--parent-prompt", required_fields["parent_prompt"].strip(),
            ]

        if request.form.get("approve") == "true":
            reviewer = request.form.get("reviewer", "").strip()
            if not reviewer:
                raise ValueError("Reviewer name is required for approval.")
            command += ["--approve", "--reviewer", reviewer]

        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=600,
        )
        output = (completed.stdout or "") + ("\n" + completed.stderr if completed.stderr else "")
        if completed.returncode != 0:
            return jsonify({"ok": False, "command": command, "output": output}), 400

        return jsonify({
            "ok": True,
            "command": command,
            "output": output,
            "page_id": generated_page_id,
            "output_root": str(OUTPUT_DIR),
        })
    except (KeyError, ValueError, FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    finally:
        if illustration and illustration.is_file():
            illustration.unlink(missing_ok=True)


@app.get("/api/output/<path:filename>")
def output_file(filename: str):
    return send_from_directory(OUTPUT_DIR, filename)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
