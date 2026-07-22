#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
composer = ROOT / "bcube-publishing-sdk/composer/compose_nursery_cover.py"
template_path = ROOT / "bcube-publishing-sdk/templates/nursery-cover-v1.json"
text = composer.read_text(encoding="utf-8")

start = text.index("def paste_safe_illustration(")
end = text.index("\ndef draw_vector_icon", start)
new_func = '''def paste_safe_illustration(canvas: Image.Image, asset_path: Path, bounds: list[int], background: str,
                            safe_inset: int = 28, radius: int = 36, *,
                            vertical_align: str = "bottom", trim_near_white: bool = True,
                            trim_padding: int = 12) -> dict[str, Any]:
    """Place a clean illustration without clipping while removing empty white margins."""
    asset = Image.open(asset_path).convert("RGB")
    source_size = [asset.width, asset.height]
    trim_box = None
    if trim_near_white:
        mask = Image.new("L", asset.size, 0)
        mask_pixels = []
        for red, green, blue in asset.getdata():
            mask_pixels.append(255 if min(red, green, blue) < 246 else 0)
        mask.putdata(mask_pixels)
        bbox = mask.getbbox()
        if bbox:
            left = max(0, bbox[0] - trim_padding)
            top = max(0, bbox[1] - trim_padding)
            right = min(asset.width, bbox[2] + trim_padding)
            bottom = min(asset.height, bbox[3] + trim_padding)
            trim_box = [left, top, right, bottom]
            asset = asset.crop((left, top, right, bottom))

    x0, y0, x1, y1 = bounds
    inner = [x0 + safe_inset, y0 + safe_inset, x1 - safe_inset, y1 - safe_inset]
    target_w, target_h = inner[2] - inner[0], inner[3] - inner[1]
    scale = min(target_w / asset.width, target_h / asset.height)
    rendered_w = max(1, round(asset.width * scale))
    rendered_h = max(1, round(asset.height * scale))
    resized = asset.resize((rendered_w, rendered_h), Image.Resampling.LANCZOS)
    px = inner[0] + (target_w - rendered_w) // 2
    if vertical_align == "bottom":
        py = inner[3] - rendered_h
    elif vertical_align == "top":
        py = inner[1]
    elif vertical_align == "center":
        py = inner[1] + (target_h - rendered_h) // 2
    else:
        raise ValueError(f"Unsupported illustration vertical alignment: {vertical_align}")

    frame_layer = Image.new("RGB", (x1 - x0, y1 - y0), background)
    frame_layer.paste(resized, (px - x0, py - y0))
    mask = Image.new("L", frame_layer.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, frame_layer.width - 1, frame_layer.height - 1), radius=radius, fill=255)
    canvas.paste(frame_layer, (x0, y0), mask)
    occupancy = (rendered_w * rendered_h) / max(1, target_w * target_h)
    return {
        "mode": "contain-trimmed",
        "source_size": source_size,
        "trim_box": trim_box,
        "trim_near_white": trim_near_white,
        "frame_bounds": bounds,
        "safe_inset": safe_inset,
        "vertical_align": vertical_align,
        "rendered_bounds": [px, py, px + rendered_w, py + rendered_h],
        "occupancy_ratio": round(occupancy, 6),
        "cropped_subjects": False,
    }

'''
text = text[:start] + new_func + text[end+1:]

old_call = 'illustration_render = paste_safe_illustration(canvas, illustration_path, bounds["illustration_frame"], colours["background"], safe_inset=template["rules"].get("illustration_safe_inset",28))'
new_call = '''illustration_render = paste_safe_illustration(
        canvas,
        illustration_path,
        bounds["illustration_frame"],
        colours["background"],
        safe_inset=template["rules"].get("illustration_safe_inset", 28),
        vertical_align=template["rules"].get("illustration_vertical_align", "bottom"),
        trim_near_white=template["rules"].get("illustration_trim_near_white", True),
        trim_padding=template["rules"].get("illustration_trim_padding", 12),
    )'''
if old_call not in text:
    raise SystemExit("illustration call pattern not found")
text = text.replace(old_call, new_call)
text = text.replace('star_bounds=data.get("official_star_bounds",[1280,2160,1720,2660])', 'star_bounds = bounds["official_star"]')
text = text.replace('"engine_version":"cover-composer-v1.1"', '"engine_version":"cover-composer-v1.2"')
composer.write_text(text, encoding="utf-8")

template = json.loads(template_path.read_text(encoding="utf-8"))
template["template_id"] = "BCUBE-NURSERY-COVER-V1.2"
template["bounds"]["official_star"] = [1220, 2100, 1750, 2690]
template["rules"].update({
    "illustration_placement": "contain-trimmed",
    "illustration_vertical_align": "bottom",
    "illustration_trim_near_white": True,
    "illustration_trim_padding": 12,
    "illustration_min_occupancy_ratio": 0.55,
    "official_star_anchor": "bottom-right",
    "official_star_required": True
})
template_path.write_text(json.dumps(template, indent=2) + "\n", encoding="utf-8")
print("cover layout v1.2 patch applied")
