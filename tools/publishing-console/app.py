#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

ROOT = Path(__file__).resolve().parents[2]
BOOKS_FILE = ROOT / "bcube-publishing-sdk/books/cover-books.json"
PUBLISH_SCRIPT = ROOT / "scripts/bcube_publish.py"
UPLOAD_DIR = ROOT / "production-renders/web-console/uploads"
OUTPUT_DIR = ROOT / "production-renders/v5"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 40 * 1024 * 1024
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def load_registry() -> dict:
    return json.loads(BOOKS_FILE.read_text(encoding="utf-8"))


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def build_command(form: dict[str, str], illustration: Path) -> list[str]:
    page_type = form.get("page_type", "cover")
    command = [
        sys.executable,
        str(PUBLISH_SCRIPT),
        "--level",
        form["level"],
        "--book",
        form["book"],
        "--page",
        "cover" if page_type == "cover" else "activity",
        "--provider",
        "manual",
        "--illustration",
        str(illustration),
        "--confirm-clean-illustration",
    ]
    if page_type != "cover":
        fields = [
            ("physical_page", "--physical-page"),
            ("page_number", "--page-number"),
            ("page_id", "--page-id"),
            ("activity_type", "--activity-type"),
            ("title", "--title"),
            ("objective", "--objective"),
            ("instruction", "--instruction"),
            ("teacher_prompt", "--teacher-prompt"),
            ("parent_prompt", "--parent-prompt"),
        ]
        for key, flag in fields:
            value = form.get(key, "").strip()
            if value:
                command.extend([flag, value])
    if form.get("approve") == "true":
        reviewer = form.get("reviewer", "").strip()
        if not reviewer:
            raise ValueError("Reviewer is required when approving a page")
        command.extend(["--approve", "--reviewer", reviewer])
    return command


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/registry")
def registry():
    return jsonify(load_registry())


@app.post("/api/publish")
def publish():
    if "illustration" not in request.files:
        return jsonify({"ok": False, "error": "Illustration file is required"}), 400
    upload = request.files["illustration"]
    if not upload.filename or not allowed_file(upload.filename):
        return jsonify({"ok": False, "error": "Use PNG, JPG, JPEG or WEBP"}), 400

    safe_name = secure_filename(upload.filename)
    staged = UPLOAD_DIR / f"{uuid.uuid4().hex}-{safe_name}"
    upload.save(staged)

    try:
        command = build_command(request.form.to_dict(), staged)
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=900,
            check=False,
            env=os.environ.copy(),
        )
        return jsonify(
            {
                "ok": completed.returncode == 0,
                "return_code": completed.returncode,
                "command": command,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        ), 200 if completed.returncode == 0 else 422
    except (ValueError, subprocess.TimeoutExpired) as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/artifacts/<path:filename>")
def artifacts(filename: str):
    return send_from_directory(OUTPUT_DIR, filename)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("BCUBE_CONSOLE_PORT", "5050")), debug=False)
