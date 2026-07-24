#!/usr/bin/env python3
"""Local BCube Publishing Web Console."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "bcube-publishing-sdk/books/cover-books.json"
PUBLISH_SCRIPT = ROOT / "scripts/bcube_publish.py"
OUTPUT_ROOT = ROOT / "production-renders/v5"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 40 * 1024 * 1024


def load_registry() -> dict[str, Any]:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def build_page_id(level: str, book: str, physical_page: int) -> str:
    registry = load_registry()
    level_data = registry["levels"][level]
    book_data = level_data["books"][book]
    return f"{book_data['prefix']}-{level_data['id_level']}-V4-P{physical_page:03d}"


def latest_artifact(page_id: str) -> Path | None:
    candidates = [
        OUTPUT_ROOT / "approved/pages" / f"{page_id}.png",
        OUTPUT_ROOT / "candidates/pages" / f"{page_id}.png",
    ]
    return next((path for path in candidates if path.is_file()), None)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/catalog")
def catalog():
    registry = load_registry()
    levels: dict[str, Any] = {}
    for level_key, level_data in registry["levels"].items():
        levels[level_key] = {
            "display_level": level_data["display_level"],
            "age": level_data["age"],
            "books": {
                slug: {
                    "title": " ".join(book["title_lines"]),
                    "prefix": book["prefix"],
                }
                for slug, book in level_data["books"].items()
            },
        }
    return jsonify({"series": registry["series"], "levels": levels})


@app.post("/api/publish")
def publish():
    form = request.form
    level = form.get("level", "").strip()
    book = form.get("book", "").strip()
    page_kind = form.get("page_kind", "cover").strip()
    provider = form.get("provider", "manual").strip()

    if not level or not book:
        return jsonify({"ok": False, "error": "Level and book are required."}), 400

    physical_page = int(form.get("physical_page", "1") or "1")
    page_id = form.get("page_id", "").strip() or build_page_id(level, book, physical_page)

    uploaded = request.files.get("illustration")
    illustration_path: Path | None = None
    temp_dir = tempfile.TemporaryDirectory(prefix="bcube-console-")
    try:
        if uploaded and uploaded.filename:
            suffix = Path(uploaded.filename).suffix.lower()
            if suffix not in ALLOWED_EXTENSIONS:
                return jsonify({"ok": False, "error": "Illustration must be PNG, JPG, JPEG, or WEBP."}), 400
            safe_name = secure_filename(uploaded.filename)
            illustration_path = Path(temp_dir.name) / safe_name
            uploaded.save(illustration_path)

        command = [
            sys.executable,
            str(PUBLISH_SCRIPT),
            "--level", level,
            "--book", book,
            "--page", "cover" if page_kind == "cover" else "activity",
            "--provider", provider,
        ]

        if illustration_path:
            command += ["--illustration", str(illustration_path)]
        if provider == "manual":
            command.append("--confirm-clean-illustration")
        if form.get("approve") == "true":
            reviewer = form.get("reviewer", "").strip()
            if not reviewer:
                return jsonify({"ok": False, "error": "Reviewer is required for approval."}), 400
            command += ["--approve", "--reviewer", reviewer]

        if page_kind != "cover":
            required = {
                "page_number": form.get("page_number"),
                "activity_type": form.get("activity_type"),
                "title": form.get("title"),
                "objective": form.get("objective"),
                "instruction": form.get("instruction"),
                "teacher_prompt": form.get("teacher_prompt"),
                "parent_prompt": form.get("parent_prompt"),
            }
            missing = [key for key, value in required.items() if value is None or not str(value).strip()]
            if missing:
                return jsonify({"ok": False, "error": f"Missing fields: {', '.join(missing)}"}), 400
            command += [
                "--physical-page", str(physical_page),
                "--page-number", str(required["page_number"]),
                "--page-id", page_id,
                "--activity-type", str(required["activity_type"]),
                "--title", str(required["title"]),
                "--objective", str(required["objective"]),
                "--instruction", str(required["instruction"]),
                "--teacher-prompt", str(required["teacher_prompt"]),
                "--parent-prompt", str(required["parent_prompt"]),
            ]

        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=900,
            check=False,
        )
        artifact = latest_artifact(page_id)
        payload = {
            "ok": result.returncode == 0,
            "return_code": result.returncode,
            "command": command,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "page_id": page_id,
            "artifact_url": f"/api/artifact/{page_id}" if artifact else None,
        }
        return jsonify(payload), 200 if result.returncode == 0 else 500
    except (ValueError, KeyError) as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except subprocess.TimeoutExpired:
        return jsonify({"ok": False, "error": "Publishing timed out after 15 minutes."}), 504
    finally:
        temp_dir.cleanup()


@app.get("/api/artifact/<page_id>")
def artifact(page_id: str):
    path = latest_artifact(page_id)
    if not path:
        return jsonify({"ok": False, "error": "Generated page not found."}), 404
    return send_file(path, mimetype="image/png", max_age=0)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
