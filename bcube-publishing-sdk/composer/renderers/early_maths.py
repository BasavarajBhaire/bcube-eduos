from __future__ import annotations

from typing import Any
from PIL import Image

from ..crop_engine import crop_from_manifest
from ..renderer_registry import register


def _crop_assets(page: dict[str, Any], source: Image.Image) -> dict[str, Image.Image]:
    crops = page["illustration"]["asset_crops"]
    return {name: crop_from_manifest(source, spec) for name, spec in crops.items()}


@register("count-choice-grid")
def render_count_choice_grid(page: dict[str, Any], ctx: Any):
    assets = _crop_assets(page, ctx.source)
    cards = page["activity"]["mechanics"]["cards"]
    return ctx.render_count_choice_cards(page, cards, assets)


@register("quantity-numeral-match")
def render_quantity_numeral_match(page: dict[str, Any], ctx: Any):
    assets = _crop_assets(page, ctx.source)
    pairs = page["activity"]["mechanics"]["pairs"]
    return ctx.render_matching_pairs(page, pairs, assets)


@register("comparison-pairs")
def render_comparison_pairs(page: dict[str, Any], ctx: Any):
    assets = _crop_assets(page, ctx.source)
    pairs = page["activity"]["mechanics"]["pairs"]
    return ctx.render_comparison_pairs(page, pairs, assets)


@register("sequence-completion")
def render_sequence_completion(page: dict[str, Any], ctx: Any):
    assets = _crop_assets(page, ctx.source)
    rows = page["activity"]["mechanics"]["rows"]
    return ctx.render_sequence_rows(page, rows, assets)


@register("group-addition")
def render_group_addition(page: dict[str, Any], ctx: Any):
    assets = _crop_assets(page, ctx.source)
    problems = page["activity"]["mechanics"]["problems"]
    return ctx.render_group_addition(page, problems, assets)


@register("take-away")
def render_take_away(page: dict[str, Any], ctx: Any):
    assets = _crop_assets(page, ctx.source)
    problems = page["activity"]["mechanics"]["problems"]
    return ctx.render_take_away(page, problems, assets)


@register("before-after")
def render_before_after(page: dict[str, Any], ctx: Any):
    assets = _crop_assets(page, ctx.source)
    rows = page["activity"]["mechanics"]["rows"]
    return ctx.render_before_after(page, rows, assets)


@register("number-order")
def render_number_order(page: dict[str, Any], ctx: Any):
    assets = _crop_assets(page, ctx.source)
    rows = page["activity"]["mechanics"]["rows"]
    return ctx.render_number_order(page, rows, assets)


@register("number-line-jumps")
def render_number_line(page: dict[str, Any], ctx: Any):
    assets = _crop_assets(page, ctx.source)
    rows = page["activity"]["mechanics"]["rows"]
    return ctx.render_number_line(page, rows, assets)


@register("picture-story-problems")
def render_picture_stories(page: dict[str, Any], ctx: Any):
    assets = _crop_assets(page, ctx.source)
    stories = page["activity"]["mechanics"]["stories"]
    return ctx.render_picture_stories(page, stories, assets)


@register("shape-object-match")
def render_shape_object_match(page: dict[str, Any], ctx: Any):
    assets = _crop_assets(page, ctx.source)
    pairs = page["activity"]["mechanics"]["pairs"]
    return ctx.render_matching_pairs(page, pairs, assets)


@register("shape-hunt")
def render_shape_hunt(page: dict[str, Any], ctx: Any):
    assets = _crop_assets(page, ctx.source)
    return ctx.render_shape_hunt(page, page["activity"]["mechanics"], assets)


@register("pattern-observation")
def render_pattern_observation(page: dict[str, Any], ctx: Any):
    assets = _crop_assets(page, ctx.source)
    rows = page["activity"]["mechanics"]["rows"]
    return ctx.render_pattern_rows(page, rows, assets, complete=False)


@register("pattern-completion")
def render_pattern_completion(page: dict[str, Any], ctx: Any):
    assets = _crop_assets(page, ctx.source)
    rows = page["activity"]["mechanics"]["rows"]
    return ctx.render_pattern_rows(page, rows, assets, complete=True)


@register("position-choice")
def render_position_choice(page: dict[str, Any], ctx: Any):
    assets = _crop_assets(page, ctx.source)
    cards = page["activity"]["mechanics"]["cards"]
    return ctx.render_position_cards(page, cards, assets)


@register("direction-paths")
def render_direction_paths(page: dict[str, Any], ctx: Any):
    assets = _crop_assets(page, ctx.source)
    paths = page["activity"]["mechanics"]["paths"]
    return ctx.render_direction_paths(page, paths, assets)
