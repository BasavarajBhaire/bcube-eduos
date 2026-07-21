from __future__ import annotations

import csv
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOKS = ROOT / "books" / "nursery"
ARCHIVE = ROOT / "archive" / "experimental"
QA = ROOT / "normalization" / "nursery-gold-v5" / "qa"

MIGRATIONS = [
    {
        "branch": "book4/creativity-creators-phase1-2",
        "source": "BCube_Gold_Production_v4/books/nursery/creativity-creators",
        "target": BOOKS / "creativity-challenges",
        "replacements": {
            "Creativity Creators Gold™": "Creativity Challenges Gold™",
            "Creativity Creators": "Creativity Challenges",
            "creativity-creators": "creativity-challenges",
            "Creativity_Creators": "Creativity_Challenges",
            "CR-NURSERY-V3-": "CR-NURSERY-V5-",
            "CR-NURSERY-V4-": "CR-NURSERY-V5-",
        },
    },
    {
        "branch": "book6/problem-solvers-phase1-3",
        "source": "BCube_Gold_Production_v4/books/nursery/problem-solvers",
        "target": BOOKS / "logical-thinking-adventures",
        "replacements": {
            "Problem Solvers Gold™": "Logical Thinking Adventures Gold™",
            "Problem Solvers": "Logical Thinking Adventures",
            "problem-solvers": "logical-thinking-adventures",
            "Problem_Solvers": "Logical_Thinking_Adventures",
            "PS-NURSERY-V3-": "LT-NURSERY-V5-",
            "PS-NURSERY-V4-": "LT-NURSERY-V5-",
            "PS-NURSERY-V5-": "LT-NURSERY-V5-",
        },
    },
]

ARCHIVES = [
    ("book7/creative-thinkers-complete", "BCube_Gold_Production_v4/books/nursery/creative-thinkers", ARCHIVE / "creative-thinkers"),
    ("book8/future-innovators-complete", "BCube_Gold_Production_v4/books/nursery/future-innovators", ARCHIVE / "future-innovators"),
]

TEXT_SUFFIXES = {".md", ".json", ".csv", ".txt", ".yml", ".yaml", ".py"}


def export_tree(branch: str, source: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        shutil.rmtree(destination)
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / "tree.tar"
        subprocess.run(["git", "archive", "--format=tar", "-o", str(archive), branch, source], check=True)
        subprocess.run(["tar", "-xf", str(archive), "-C", tmp], check=True)
        extracted = Path(tmp) / source
        shutil.copytree(extracted, destination)


def replace_text(path: Path, replacements: dict[str, str]) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return
    for old, new in replacements.items():
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def replace_xlsx(path: Path, replacements: dict[str, str]) -> None:
    temp = path.with_suffix(".tmp.xlsx")
    with zipfile.ZipFile(path, "r") as zin, zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith(".xml") or item.filename.endswith(".rels"):
                try:
                    text = data.decode("utf-8")
                    for old, new in replacements.items():
                        text = text.replace(old, new)
                    data = text.encode("utf-8")
                except UnicodeDecodeError:
                    pass
            zout.writestr(item, data)
    temp.replace(path)


def normalize_tree(target: Path, replacements: dict[str, str]) -> None:
    for path in target.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            replace_text(path, replacements)
        elif path.suffix.lower() == ".xlsx":
            replace_xlsx(path, replacements)

    # Rename files and directories after content replacement, deepest paths first.
    for path in sorted(target.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        new_name = path.name
        for old, new in replacements.items():
            new_name = new_name.replace(old, new)
        if new_name != path.name:
            path.rename(path.with_name(new_name))


def count_prompts(target: Path) -> int:
    return len(list((target / "production-prompts").glob("P*.md")))


def forbidden_hits(target: Path, phrases: list[str]) -> list[str]:
    hits: list[str] = []
    for path in target.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if any(p in text for p in phrases):
                hits.append(str(path.relative_to(ROOT)))
    return hits


def main() -> None:
    results = []
    for migration in MIGRATIONS:
        export_tree(migration["branch"], migration["source"], migration["target"])
        normalize_tree(migration["target"], migration["replacements"])
        prompts = count_prompts(migration["target"])
        old_titles = [k for k in migration["replacements"] if "Creators" in k or "Problem Solvers" in k]
        hits = forbidden_hits(migration["target"], old_titles)
        results.append({
            "target": str(migration["target"].relative_to(ROOT)),
            "prompt_count": prompts,
            "old_name_hits": hits,
            "status": "PASS" if prompts == 44 and not hits else "FAIL",
        })

    archive_results = []
    for branch, source, target in ARCHIVES:
        export_tree(branch, source, target)
        archive_results.append({
            "target": str(target.relative_to(ROOT)),
            "preserved": target.exists(),
            "prompt_count": count_prompts(target),
        })

    QA.mkdir(parents=True, exist_ok=True)
    report = {
        "phase": "B",
        "official_migrations": results,
        "experimental_archives": archive_results,
        "overall_decision": "PASS" if all(r["status"] == "PASS" for r in results) and all(a["preserved"] for a in archive_results) else "FAIL",
    }
    (QA / "phase-b-migration-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary = [
        "# Nursery Gold Phase B Migration Summary",
        "",
        "- Creativity Creators → Creativity Challenges",
        "- Problem Solvers → Logical Thinking Adventures",
        "- Creative Thinkers preserved under `archive/experimental`",
        "- Future Innovators preserved under `archive/experimental`",
        "",
    ]
    for result in results:
        summary.append(f"- `{result['target']}`: {result['prompt_count']} prompts — {result['status']}")
    summary += ["", "## Decision", "", f"`{report['overall_decision']} — PHASE B OFFICIAL BOOK MIGRATION`", ""]
    (QA / "phase-b-migration-summary.md").write_text("\n".join(summary), encoding="utf-8")
    if report["overall_decision"] != "PASS":
        raise SystemExit("Phase B migration validation failed")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
