#!/usr/bin/env python3
"""Read authoritative page metadata and resolved Learning Page Contract V2 previews."""
from __future__ import annotations

import importlib.util
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

SUPPORTED_ACTIVITY_TYPES = {
    "observe", "match", "trace", "colour", "draw", "speak", "listen",
    "count", "compare", "connect", "complete", "maze", "explore", "think",
    "reflect", "sequence", "sort", "circle", "assessment",
}
DEFAULT_TEACHER_PROMPT = (
    "Model once, invite one response, pause for processing, scaffold through gesture or choice, "
    "and affirm effort."
)
DEFAULT_PARENT_PROMPT = (
    "Use a familiar home routine or everyday object to extend the learning without adding a scored task."
)


@dataclass(frozen=True)
class PageRecord:
    physical_page: int
    printed_page: int | None
    printed_visible: bool
    page_id: str
    page_type: str
    page_type_label: str
    activity_type: str | None
    title: str
    module: str
    objective: str
    instruction: str
    source_instruction: str
    teacher_prompt: str
    parent_prompt: str
    source: str
    learning_contract: dict[str, Any] | None = None

    def public_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["printed_page_label"] = str(self.printed_page) if self.printed_visible else "Hidden"
        result["requires_illustration"] = self.page_type not in {
            "copyright", "contents", "meet-star",
        }
        if self.learning_contract:
            result["learning_pipeline"] = "learning-page-contract-v2"
            result["layout_variant"] = self.learning_contract.get("layout_variant")
            result["expected_response"] = self.learning_contract.get("expected_response")
            result["deterministic_component_types"] = self.learning_contract.get(
                "deterministic_component_types", []
            )
            result["illustration_scene"] = self.learning_contract.get("illustration_scene")
            result["illustration_focal_point"] = self.learning_contract.get(
                "illustration_focal_point"
            )
            result["illustration_required_objects"] = self.learning_contract.get(
                "required_objects", []
            )
            result["illustration_forbidden_objects"] = self.learning_contract.get(
                "forbidden_objects", []
            )
            result["star_policy"] = self.learning_contract.get("star_policy")
            result["content_status"] = self.learning_contract.get("status")
            result["content_issues"] = self.learning_contract.get("issues", [])
        return result


class PageDataRegistry:
    """Resolve page-owned production data for registered BCube books."""

    def __init__(self, root: Path, book_registry_path: Path):
        self.root = root.resolve()
        self.book_registry_path = book_registry_path.resolve()
        self._learning_normalizer: ModuleType | None = None
        self._learning_refiner: ModuleType | None = None
        self._learning_finaliser: ModuleType | None = None
        self._learning_overrides: dict[str, Any] | None = None

    @staticmethod
    def _load_object(path: Path) -> dict[str, Any]:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Cannot read page-data source {path}: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"Page-data source must contain a JSON object: {path}")
        return value

    @staticmethod
    def _load_module(name: str, path: Path) -> ModuleType:
        specification = importlib.util.spec_from_file_location(name, path)
        if specification is None or specification.loader is None:
            raise ValueError(f"Cannot load learning-page module: {path}")
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)
        return module

    def _learning_modules(self) -> tuple[ModuleType, ModuleType, ModuleType, dict[str, Any]]:
        if self._learning_normalizer is None:
            self._learning_normalizer = self._load_module(
                "bcube_console_learning_normalizer_v2",
                self.root / "bcube-publishing-sdk/normalizers/build_learning_contract_v2.py",
            )
        if self._learning_refiner is None:
            self._learning_refiner = self._load_module(
                "bcube_console_learning_refiner_v2",
                self.root / "bcube-publishing-sdk/normalizers/refine_learning_contract_v2.py",
            )
        if self._learning_finaliser is None:
            self._learning_finaliser = self._load_module(
                "bcube_console_learning_finaliser_v2",
                self.root / "bcube-publishing-sdk/normalizers/finalise_learning_contract_v2.py",
            )
        if self._learning_overrides is None:
            self._learning_overrides = self._load_object(
                self.root / "bcube-publishing-sdk/books/learning-page-overrides-v1.json"
            )
        return (
            self._learning_normalizer,
            self._learning_refiner,
            self._learning_finaliser,
            self._learning_overrides,
        )

    @staticmethod
    def _deep_merge(target: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
        for key, value in update.items():
            if isinstance(value, dict) and isinstance(target.get(key), dict):
                PageDataRegistry._deep_merge(target[key], value)
            else:
                target[key] = value
        return target

    def _book(self, level: str, slug: str) -> tuple[dict[str, Any], dict[str, Any]]:
        registry = self._load_object(self.book_registry_path)
        level_data = registry.get("levels", {}).get(level)
        if not isinstance(level_data, dict):
            raise ValueError(f"Unknown level: {level}")
        book = level_data.get("books", {}).get(slug)
        if not isinstance(book, dict):
            raise ValueError(f"Unknown {level.upper()} book: {slug}")
        return level_data, book

    def _manifest_path(self, level: str, slug: str) -> Path:
        candidates = [
            self.root / "production-prompts" / slug / level / "v4" / "release-manifest.json",
            self.root / "production-prompts" / slug / level / "V4" / "release-manifest.json",
        ]
        for candidate in candidates:
            if candidate.is_file():
                return candidate.resolve()
        raise ValueError(f"No finalized V4 release manifest found for {level}/{slug}")

    @staticmethod
    def _page_kind(physical: int, page_type: str, title: str) -> tuple[str, str]:
        lowered = title.casefold()
        if physical == 1:
            return "cover", "Cover"
        if physical == 2 or lowered == "about this book":
            return "about-book", "About the Book"
        if physical == 3 or "copyright" in lowered or "publisher" in lowered:
            return "copyright", "Copyright / Publisher"
        if physical in {4, 5} or page_type == "contents":
            return "contents", "Contents"
        if lowered == "welcome" or lowered.startswith("welcome "):
            return "welcome", "Welcome"
        if re.search(r"\bmeet\b.*\bstar\b", lowered):
            return "meet-star", "Meet Star"
        if page_type == "cover":
            return "learning", "Learning Page"
        labels = {
            "certificate": "Certificate",
            "back_cover": "Back Cover",
            "assessment": "Assessment",
            "review": "Review",
            "reflection": "Reflection",
            "worksheet": "Learning Page",
            "activity_page": "Learning Page",
            "teacher_guide": "Teacher Guide",
            "front_matter": "Front Matter",
        }
        return page_type.replace("_", "-"), labels.get(page_type, page_type.replace("_", " ").title())

    @staticmethod
    def _activity_type(page_type: str, title: str, instruction: str, objective: str) -> str:
        if page_type == "assessment":
            return "assessment"
        if page_type in {"certificate", "back_cover", "reflection"}:
            return "reflect"
        text = " ".join((title, instruction, objective)).casefold()
        rules = (
            ("maze", ("maze",)),
            ("trace", ("trace", "pre-writing")),
            ("colour", ("colour", "color", "paint")),
            ("match", ("match", "pair")),
            ("sort", ("sort", "classify", "group")),
            ("sequence", ("sequence", "order", "first next", "before and after")),
            ("count", ("count", "number", "add", "subtract", "more or fewer")),
            ("compare", ("compare", "same and different", "greater", "smaller")),
            ("circle", ("circle",)),
            ("connect", ("connect", "join", "link")),
            ("complete", ("complete", "finish", "fill in")),
            ("draw", ("draw", "sketch")),
            ("listen", ("listen", "sound")),
            ("speak", ("speak", "say", "tell", "talk", "show and tell", "present")),
            ("think", ("think", "reason", "solve", "logic", "why")),
            ("explore", ("explore", "discover", "experiment", "investigate")),
            ("observe", ("observe", "look", "find", "identify", "recognise", "recognize")),
        )
        for activity_type, keywords in rules:
            if any(keyword in text for keyword in keywords):
                return activity_type
        return "reflect" if page_type in {"review", "front_matter", "teacher_guide", "contents"} else "observe"

    @staticmethod
    def _teacher_prompt(curriculum: dict[str, Any]) -> str:
        facilitation = str(curriculum.get("teacher_facilitation") or "").strip()
        questions = curriculum.get("teacher_questions") or []
        questions = [str(question).strip() for question in questions if str(question).strip()]
        parts = [facilitation] if facilitation else []
        if questions:
            parts.append("Ask: " + " ".join(questions))
        return " ".join(parts).strip() or DEFAULT_TEACHER_PROMPT

    @staticmethod
    def _parent_prompt(curriculum: dict[str, Any]) -> str:
        conversation = str(curriculum.get("parent_conversation") or "").strip()
        home = str(curriculum.get("parent_home_activity") or "").strip()
        if conversation and home and conversation.casefold() != home.casefold():
            return f"{conversation} {home}"
        return conversation or home or DEFAULT_PARENT_PROMPT

    @staticmethod
    def _visible_instruction(value: str, limit: int = 220) -> str:
        """Extract child-facing/page-facing text from older technical instructions."""
        text = " ".join(value.split()).strip()
        page_command = re.search(r"\bPAGE\s+\d+\s*:\s*(.+)", text, flags=re.IGNORECASE)
        if page_command:
            text = page_command.group(1).strip()
        if len(text) <= limit:
            return text
        sentences = re.split(r"(?<=[.!?])\s+", text)
        selected: list[str] = []
        for sentence in sentences:
            if sentence.casefold().startswith(("include one clear learning objective", "ensure there are no")):
                continue
            candidate = " ".join(selected + [sentence]).strip()
            if len(candidate) > limit:
                break
            selected.append(sentence)
        if selected:
            return " ".join(selected)
        words: list[str] = []
        for word in text.split():
            if len(" ".join(words + [word])) > limit - 1:
                break
            words.append(word)
        return " ".join(words).rstrip(" ,;:") + "…"

    def _learning_preview(
        self,
        *,
        source_path: Path,
        level_data: dict[str, Any],
        book: dict[str, Any],
    ) -> dict[str, Any]:
        normalizer, refiner, finaliser, override_registry = self._learning_modules()
        try:
            contract = normalizer.build_contract(
                root=self.root,
                v4_path=source_path,
                illustration_path="PENDING_ILLUSTRATION",
                official_logo_path="PENDING_OFFICIAL_LOGO",
                book_title_lines=list(book["title_lines"]),
                level_name=str(level_data["display_level"]),
                age=str(level_data["age"]),
            )
            pages = override_registry.get("pages")
            override = pages.get(contract["identity"]["page_id"]) if isinstance(pages, dict) else None
            override_applied = isinstance(override, dict)
            if override_applied:
                self._deep_merge(contract, override)
                contract["qa_requirements"]["component_count"] = len(
                    contract["deterministic_components"]
                )
            refiner.refine_contract(
                contract,
                curated_override_applied=override_applied,
            )
            finaliser.finalise_contract(
                contract,
                curated_override_applied=override_applied,
            )
            text = " ".join(
                str(value or "")
                for value in (
                    contract["illustration"].get("scene"),
                    contract["illustration"].get("focal_point"),
                    contract["learning"].get("student_instruction"),
                    contract["learning"].get("model_text"),
                )
            ).casefold()
            if not override_applied:
                contract["illustration"]["star_policy"] = (
                    "official-asset-separate" if "star" in text else "prohibited"
                )
            return {
                "status": "READY_FOR_ILLUSTRATION_REVIEW",
                "issues": [],
                "contract_version": contract["contract_version"],
                "primary_activity": contract["activity"]["primary"],
                "secondary_activities": contract["activity"]["secondary"],
                "response_modes": contract["activity"]["response_modes"],
                "layout_variant": contract["activity"]["layout_variant"],
                "objective": contract["learning"]["objective"],
                "instruction": contract["learning"]["student_instruction"],
                "expected_response": contract["learning"]["expected_response"],
                "teacher_model": contract["guidance"]["teacher"]["model"],
                "teacher_question": contract["guidance"]["teacher"]["question"],
                "parent_extension": contract["guidance"]["parent_extension"],
                "deterministic_component_types": [
                    item["type"] for item in contract["deterministic_components"]
                ],
                "deterministic_components": contract["deterministic_components"],
                "illustration_scene": contract["illustration"]["scene"],
                "illustration_focal_point": contract["illustration"]["focal_point"],
                "required_objects": contract["illustration"]["required_objects"],
                "forbidden_objects": contract["illustration"]["forbidden_objects"],
                "protected_response_zones": contract["illustration"][
                    "protected_response_zones"
                ],
                "star_policy": contract["illustration"]["star_policy"],
                "curated_override_applied": override_applied,
                "content_refinement_changes": contract["source_lineage"].get(
                    "content_refinement_changes", []
                ),
                "contract_finalisation_changes": contract["source_lineage"].get(
                    "contract_finalisation_changes", []
                ),
            }
        except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
            return {
                "status": "BLOCKED_NEEDS_EDITORIAL_REFINEMENT",
                "issues": [str(exc)],
                "contract_version": "learning-page-contract-v2.0",
                "primary_activity": None,
                "secondary_activities": [],
                "response_modes": [],
                "layout_variant": None,
                "deterministic_component_types": [],
                "required_objects": [],
                "forbidden_objects": [],
                "star_policy": "prohibited",
            }

    def list_pages(self, level: str, slug: str) -> list[PageRecord]:
        level_data, book = self._book(level, slug)
        manifest_path = self._manifest_path(level, slug)
        manifest = self._load_object(manifest_path)
        if manifest.get("slug") != slug:
            raise ValueError(f"Manifest slug mismatch for {level}/{slug}")
        rows = manifest.get("pages")
        if not isinstance(rows, list) or not rows:
            raise ValueError(f"Manifest contains no pages for {level}/{slug}")

        expected_prefix = str(manifest.get("prefix") or "")
        if not expected_prefix:
            raise ValueError(f"Manifest contains no book prefix for {level}/{slug}")
        expected_level = str(level_data.get("id_level") or "")
        records: list[PageRecord] = []
        seen: set[int] = set()
        manifest_dir = manifest_path.parent.resolve()
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("physical"), int):
                raise ValueError(f"Invalid page entry in {manifest_path}")
            physical = row["physical"]
            if physical in seen:
                raise ValueError(f"Duplicate physical page {physical} in {manifest_path}")
            seen.add(physical)
            relative_json = row.get("json")
            if not isinstance(relative_json, str) or not relative_json:
                raise ValueError(f"Physical page {physical} has no JSON source in {manifest_path}")
            source_path = (manifest_dir / relative_json).resolve()
            if manifest_dir not in source_path.parents or not source_path.is_file():
                raise ValueError(f"Invalid page-data path for physical page {physical}: {relative_json}")
            data = self._load_object(source_path)
            page = data.get("page")
            curriculum = data.get("curriculum")
            if not isinstance(page, dict) or not isinstance(curriculum, dict):
                raise ValueError(f"Page {physical} lacks page/curriculum data: {source_path}")

            expected_id = f"{expected_prefix}-{expected_level}-V4-P{physical:03d}"
            page_id = str(data.get("prompt_id") or "")
            if page_id != expected_id or row.get("prompt_id") != expected_id:
                raise ValueError(f"Prompt ID mismatch for {level}/{slug} physical page {physical}")
            if page.get("physical") != physical:
                raise ValueError(f"Physical page mismatch in {source_path}")
            source_book = data.get("book")
            if not isinstance(source_book, dict) or source_book.get("slug") != slug:
                raise ValueError(f"Book identity mismatch in {source_path}")
            if source_book.get("prefix") != expected_prefix:
                raise ValueError(f"Book prefix mismatch in {source_path}")

            title = str(page.get("title") or row.get("title") or "").strip()
            page_type = str(page.get("type") or "activity_page").strip()
            objective = str(curriculum.get("objective") or "").strip()
            source_instruction = str(curriculum.get("instruction") or "").strip()
            instruction = self._visible_instruction(source_instruction)
            teacher_prompt = self._teacher_prompt(curriculum)
            parent_prompt = self._parent_prompt(curriculum)
            learning_contract = None
            if 8 <= physical <= 43:
                learning_contract = self._learning_preview(
                    source_path=source_path,
                    level_data=level_data,
                    book=book,
                )
                if learning_contract["status"] == "READY_FOR_ILLUSTRATION_REVIEW":
                    objective = str(learning_contract["objective"])
                    instruction = str(learning_contract["instruction"])
                    teacher_prompt = (
                        f"{learning_contract['teacher_model']} "
                        f"Ask: {learning_contract['teacher_question']}"
                    )
                    parent_prompt = str(learning_contract["parent_extension"])
            required = {
                "title": title,
                "objective": objective,
                "instruction": instruction,
                "teacher prompt": teacher_prompt,
                "parent prompt": parent_prompt,
            }
            missing = [name for name, value in required.items() if not value]
            if physical != 1 and missing:
                raise ValueError(f"{page_id} lacks required metadata: {', '.join(missing)}")

            preserved = data.get("preserved_source", {}).get("page_data")
            module = ""
            if isinstance(preserved, dict):
                module = str(preserved.get("unit_id") or "").strip()
            kind, kind_label = self._page_kind(physical, page_type, title)
            activity_type = None if physical == 1 else self._activity_type(
                page_type, title, instruction, objective
            )
            if learning_contract and learning_contract["status"] == "READY_FOR_ILLUSTRATION_REVIEW":
                activity_type = str(learning_contract["primary_activity"])
            if activity_type is not None and activity_type not in SUPPORTED_ACTIVITY_TYPES:
                raise ValueError(f"Unsupported resolved activity type {activity_type!r} for {page_id}")
            printed = page.get("printed")
            printed_page = printed if isinstance(printed, int) else None
            printed_visible = bool(page.get("printed_visible") and printed_page is not None)
            records.append(PageRecord(
                physical_page=physical,
                printed_page=printed_page,
                printed_visible=printed_visible,
                page_id=page_id,
                page_type=kind,
                page_type_label=kind_label,
                activity_type=activity_type,
                title=title,
                module=module,
                objective=objective,
                instruction=instruction,
                source_instruction=source_instruction,
                teacher_prompt=teacher_prompt,
                parent_prompt=parent_prompt,
                source=source_path.relative_to(self.root).as_posix(),
                learning_contract=learning_contract,
            ))
        declared_pages = manifest.get("physical_pages")
        if declared_pages != len(records) or seen != set(range(1, len(records) + 1)):
            raise ValueError(f"Manifest physical-page sequence is incomplete for {level}/{slug}")
        return sorted(records, key=lambda item: item.physical_page)

    def get_page(self, level: str, slug: str, physical_page: int) -> PageRecord:
        if physical_page < 1:
            raise ValueError("Physical page must be a positive integer")
        for page in self.list_pages(level, slug):
            if page.physical_page == physical_page:
                return page
        raise ValueError(f"Physical page {physical_page} is not registered for {level}/{slug}")
