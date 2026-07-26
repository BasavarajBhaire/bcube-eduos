#!/usr/bin/env python3
"""Shared Early Maths response rendering policy.

Independent activities must present plain selectable text or objects. A visible
circle is reserved for a completed model example only. Connector dots and blank
writing boxes are separate mechanics and are not treated as answer selection.
"""
from __future__ import annotations


def draw_plain_choices(text_fn, base, draw, template, values, box, *, size=42):
    """Render unselected choices as plain text with generous writable spacing."""
    x0, y0, x1, y1 = box
    if not values:
        return
    gap = (x1 - x0) // (len(values) + 1)
    cy = (y0 + y1) // 2
    half_w = max(54, min(110, gap // 3))
    half_h = max(48, min(82, (y1 - y0) // 3))
    for index, value in enumerate(values, 1):
        cx = x0 + gap * index
        text_fn(
            base,
            draw,
            template,
            value,
            [cx - half_w, cy - half_h, cx + half_w, cy + half_h],
            size=size,
            lines=1,
        )


def draw_plain_choice_with_base(base, draw, template, value, box, *, size=40):
    """Render one unselected choice without an enclosing circle or highlight."""
    base.fitted_text(
        draw,
        str(value),
        box,
        max_size=size,
        min_size=max(22, size - 14),
        colour=template["colours"]["navy"],
        bold=True,
        max_lines=1,
    )


def qa_flags() -> dict[str, bool]:
    return {
        "completed_example_may_show_selected_answer": True,
        "independent_choices_are_plain": True,
        "independent_answer_preselected": False,
    }
