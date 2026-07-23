#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
composer = ROOT / "bcube-publishing-sdk/composer/compose_nursery_cover.py"
text = composer.read_text(encoding="utf-8")
start = text.index("def paste_safe_illustration(")
end = text.index("\ndef draw_vector_icon", start)
replacement = '''def paste_safe_illustration(canvas: Image.Image, asset_path: Path, bounds: list[int], background: str,
                            safe_inset: int = 20, radius: int = 36,
                            min_occupancy: float = 0.72) -> dict[str, Any]:
    """Trim empty margins, scale artwork strongly, and bottom-align without cropping subjects."""
    asset = Image.open(asset_path).convert("RGB")
    source_size = [asset.width, asset.height]

    # Detect only near-white empty canvas. Subject pixels and coloured classroom details remain.
    probe = asset.resize((max(1, asset.width // 4), max(1, asset.height // 4)), Image.Resampling.BILINEAR)
    mask = Image.new("L", probe.size, 0)
    mask_pixels = []
    for red, green, blue in probe.getdata():
        mask_pixels.append(255 if min(red, green, blue) < 242 or max(red, green, blue) - min(red, green, blue) > 10 else 0)
    mask.putdata(mask_pixels)
    bbox = mask.getbbox()
    if bbox:
        scale_x, scale_y = asset.width / probe.width, asset.height / probe.height
        trim = [
            max(0, int(bbox[0] * scale_x) - 10),
            max(0, int(bbox[1] * scale_y) - 10),
            min(asset.width, int(bbox[2] * scale_x) + 10),
            min(asset.height, int(bbox[3] * scale_y) + 10),
        ]
    else:
        trim = [0, 0, asset.width, asset.height]

    trimmed = asset.crop(tuple(trim))
    x0, y0, x1, y1 = bounds
    inner = [x0 + safe_inset, y0 + safe_inset, x1 - safe_inset, y1 - safe_inset]
    target_w, target_h = inner[2] - inner[0], inner[3] - inner[1]
    scale = min(target_w / trimmed.width, target_h / trimmed.height)
    rendered_w = max(1, round(trimmed.width * scale))
    rendered_h = max(1, round(trimmed.height * scale))
    resized = trimmed.resize((rendered_w, rendered_h), Image.Resampling.LANCZOS)
    px = inner[0] + (target_w - rendered_w) // 2
    py = inner[3] - rendered_h

    frame_layer = Image.new("RGB", (x1 - x0, y1 - y0), background)
    frame_layer.paste(resized, (px - x0, py - y0))
    mask_layer = Image.new("L", frame_layer.size, 0)
    ImageDraw.Draw(mask_layer).rounded_rectangle((0, 0, frame_layer.width - 1, frame_layer.height - 1), radius=radius, fill=255)
    canvas.paste(frame_layer, (x0, y0), mask_layer)

    frame_area = max(1, target_w * target_h)
    occupancy = (rendered_w * rendered_h) / frame_area
    if occupancy < min_occupancy:
        raise ValueError(
            f"FAIL_ILLUSTRATION_OCCUPANCY: rendered illustration occupies {occupancy:.3f}; minimum is {min_occupancy:.3f}"
        )
    return {
        "mode": "adaptive-trim-contain-bottom",
        "source_size": source_size,
        "trim_box": trim,
        "frame_bounds": bounds,
        "safe_inset": safe_inset,
        "rendered_bounds": [px, py, px + rendered_w, py + rendered_h],
        "vertical_alignment": "bottom",
        "occupancy_ratio": round(occupancy, 6),
        "cropped_subjects": False,
    }

'''
text = text[:start] + replacement + text[end+1:]
text = text.replace(
    'illustration_render = paste_safe_illustration(canvas, illustration_path, bounds["illustration_frame"], colours["background"], safe_inset=template["rules"].get("illustration_safe_inset",28))',
    'illustration_render = paste_safe_illustration(\n        canvas, illustration_path, bounds["illustration_frame"], colours["background"],\n        safe_inset=template["rules"].get("illustration_safe_inset", 20),\n        min_occupancy=template["rules"].get("illustration_min_occupancy", 0.72),\n    )'
)
text = text.replace('"engine_version":"cover-composer-v1.1"', '"engine_version":"cover-composer-v1.3"')
composer.write_text(text, encoding="utf-8")

template_path = ROOT / "bcube-publishing-sdk/templates/nursery-cover-v1.json"
template = json.loads(template_path.read_text(encoding="utf-8"))
template["template_id"] = "BCUBE-NURSERY-COVER-V1.3"
template.setdefault("rules", {})["illustration_safe_inset"] = 20
template["rules"]["illustration_min_occupancy"] = 0.72
template["rules"]["illustration_vertical_alignment"] = "bottom"
template["rules"]["illustration_trim_near_white"] = True
template_path.write_text(json.dumps(template, indent=2) + "\n", encoding="utf-8")
