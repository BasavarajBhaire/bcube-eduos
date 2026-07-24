#!/usr/bin/env python3
"""Validate the BCube Publishing SDK contracts without rendering pages."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SDK = ROOT / "bcube-publishing-sdk"


def load(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Missing required SDK file: {path.relative_to(ROOT)}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    components = load(SDK / "components/component-registry.json")
    templates = load(SDK / "templates/publishing-page-templates.json")
    schema = load(SDK / "schemas/page-data.schema.json")

    canvas = {"width": 2480, "height": 3508, "dpi": 300}
    if components.get("canvas") != canvas or templates.get("canvas") != canvas:
        raise SystemExit("SDK canvas must be exactly 2480x3508 at 300 DPI")

    expected_types = {
        "cover", "about", "publisher", "contents", "welcome", "meet_star", "lesson", "back_cover",
    }
    actual_types = set(templates.get("templates", {}))
    if actual_types != expected_types:
        raise SystemExit(f"Publishing page types mismatch: {sorted(actual_types)}")

    registry = components.get("components", {})
    for page_type, contract in templates["templates"].items():
        required = contract.get("required", [])
        prohibited = contract.get("prohibited", [])
        overlap = set(required) & set(prohibited)
        if overlap:
            raise SystemExit(f"{page_type}: components both required and prohibited: {sorted(overlap)}")
        unknown = [name for name in required if name not in registry]
        if unknown:
            raise SystemExit(f"{page_type}: unknown required components: {unknown}")

    cover = templates["templates"]["cover"]
    if cover["constraints"].get("skill_capsules") != 6:
        raise SystemExit("Cover must require exactly six skill capsules")
    if cover["constraints"].get("core_pillars") != 5:
        raise SystemExit("Cover must require exactly five core pillars")

    contents = templates["templates"]["contents"]
    if contents["constraints"].get("columns") != 2:
        raise SystemExit("Contents must use exactly two columns")
    if not contents["constraints"].get("show_module_names"):
        raise SystemExit("Contents must show module names")
    for forbidden in ("age_badge", "teacher_panel", "parent_panel", "sticky_note", "callout"):
        if forbidden not in contents.get("prohibited", []):
            raise SystemExit(f"Contents must prohibit {forbidden}")

    special_render = load(SDK / "templates/special-page-v1.json")
    special_rules = special_render.get("rules", {})
    if special_rules.get("header_type") != "BOOK_HEADER":
        raise SystemExit("Contents, Welcome, and Meet Star must use BOOK_HEADER")
    for key in ("series_banner", "age_badge", "teacher_panel", "parent_panel"):
        if special_rules.get(key) is not False:
            raise SystemExit(f"Special page template must disable {key}")
    if special_render.get("contents", {}).get("entries_per_page") != 19:
        raise SystemExit("Each Contents page must contain exactly 19 reader-facing entries")
    if special_render.get("welcome", {}).get("expected_printed_page") != 5:
        raise SystemExit("Welcome must visibly start numbering at page 5")
    if special_render.get("meet_star", {}).get("expected_printed_page") != 6:
        raise SystemExit("Meet Star must visibly show page 6")
    if special_render.get("meet_star", {}).get("official_star_count") != 1:
        raise SystemExit("Meet Star must contain exactly one official Star")

    welcome = templates["templates"]["welcome"]
    meet_star = templates["templates"]["meet_star"]
    lesson = templates["templates"]["lesson"]
    if welcome["constraints"].get("printed_page") != 5 or welcome.get("header_type") != "BOOK_HEADER":
        raise SystemExit("Welcome contract must use BOOK_HEADER and printed page 5")
    if meet_star["constraints"].get("official_star") != 1:
        raise SystemExit("Meet Star contract must require one official Star")
    if lesson.get("header_type") != "LESSON_HEADER" or lesson["constraints"].get("default_star") is not False:
        raise SystemExit("Lesson contract must use LESSON_HEADER without a default Star")
    activity_render = load(SDK / "templates/activity-page-v1.json")
    if activity_render.get("rules", {}).get("show_book_title") is not True:
        raise SystemExit("Lesson pages must show the book identity in the header")
    if activity_render.get("rules", {}).get("show_star") is not False:
        raise SystemExit("Lesson pages must not place Star over teacher or parent panels")
    if "star" in activity_render.get("bounds", {}):
        raise SystemExit("Lesson layout must not reserve an overlapping default Star region")

    publisher = templates["templates"]["publisher"]
    if publisher["constraints"].get("illustration") is not False:
        raise SystemExit("Publisher page must prohibit illustrations")
    if publisher.get("header_type") != "MINIMAL_HEADER":
        raise SystemExit("Publisher page must use MINIMAL_HEADER")
    for forbidden in ("age_badge", "official_star", "illustration_layer", "page_number",
                      "teacher_panel", "parent_panel"):
        if forbidden not in publisher.get("prohibited", []):
            raise SystemExit(f"Publisher page must prohibit {forbidden}")
    publisher_render = load(SDK / "templates/publisher-page-v1.json")
    if publisher_render.get("header_type") != "MINIMAL_HEADER":
        raise SystemExit("Rendered Publisher template must use MINIMAL_HEADER")
    publisher_rules = publisher_render.get("rules", {})
    if publisher_rules.get("illustration_allowed") is not False:
        raise SystemExit("Rendered Publisher template must prohibit illustrations")
    if publisher_rules.get("isbn_allowed_without_assignment") is not False:
        raise SystemExit("Rendered Publisher template must prohibit unassigned ISBNs")
    if publisher_rules.get("single_line_book_title_when_fit") is not True:
        raise SystemExit("Publisher book titles must stay on one line when they fit")
    for forbidden in ("illustration_layer", "official_star", "learning_goal", "activity_banner",
                      "teacher_panel", "parent_panel", "visible_page_number"):
        if forbidden not in publisher_rules.get("prohibited_components", []):
            raise SystemExit(f"Rendered Publisher template must prohibit {forbidden}")

    about = templates["templates"]["about"]
    if about.get("header_type") != "BOOK_HEADER":
        raise SystemExit("About page must use BOOK_HEADER")
    for forbidden in ("series_banner", "age_badge", "page_number", "teacher_panel", "parent_panel"):
        if forbidden not in about.get("prohibited", []):
            raise SystemExit(f"About page must prohibit {forbidden}")
    about_render = load(SDK / "templates/about-page-v1.json")
    if about_render.get("header_type") != "BOOK_HEADER":
        raise SystemExit("Rendered About template must use BOOK_HEADER")
    render_rules = about_render.get("rules", {})
    if render_rules.get("learning_outcome_count") != 6 or render_rules.get("core_pillar_count") != 5:
        raise SystemExit("Rendered About template must contain six outcomes and five core pillars")
    for forbidden in ("series_banner", "age_badge", "visible_page_number", "teacher_panel",
                      "parent_panel", "official_star"):
        if forbidden not in render_rules.get("prohibited_components", []):
            raise SystemExit(f"Rendered About template must prohibit {forbidden}")

    page_type_enum = set(schema["properties"]["page_type"]["enum"])
    if page_type_enum != expected_types:
        raise SystemExit("Page-data schema page types do not match template registry")

    illustration = registry.get("illustration_layer", {})
    if illustration.get("text_allowed") is not False or illustration.get("branding_allowed") is not False:
        raise SystemExit("Illustration layer must prohibit typography and branding")

    print("BCube Publishing SDK validation PASS")


if __name__ == "__main__":
    main()
