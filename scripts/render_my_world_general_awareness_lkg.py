#!/usr/bin/env python3
"""Render the curriculum-first My World & General Awareness LKG validation wave."""
from __future__ import annotations

import argparse
from collections import deque
import importlib.util
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "curriculum/my-world-general-awareness/lkg/curriculum-first-p008-p016-v1.json"
TEXT_ENGINE = ROOT / "bcube-publishing-sdk/composer/compose_learning_page_v2.py"
ART_ROOT = ROOT / "assets/illustrations/my-world-general-awareness/lkg"
ART_MANIFEST = ART_ROOT / "manifest.json"
WIDTH, HEIGHT = 2480, 3508
NAVY = "#123F72"
PURPLE = "#7E57C2"
SOFT_PURPLE = "#A077E8"
BLUE = "#E8F4FF"
GOLD = "#FFF4C6"
GREEN = "#F0FAED"
INK = "#31353A"
ORANGE = "#F29B38"
RED = "#F05A47"
TEAL = "#45A7A0"
# Default production scope: printed content pages 7-42. Front matter P001-P007
# and the back cover P044 remain available through an explicit --pages choice.
PAGES = tuple(range(8, 44))
CURRENT_CANVAS = None
CURRENT_ART = {}
SHARED_ART = {}
PAGE_ART_CACHE = {}


def _trim_white(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    difference = ImageChops.difference(rgb, Image.new("RGB", rgb.size, "white"))
    mask = difference.convert("L").point(lambda value: 255 if value > 8 else 0)
    bounds = mask.getbbox()
    if bounds is None:
        return rgb
    left, top, right, bottom = bounds
    padding = max(4, round(min(rgb.size) * 0.015))
    return rgb.crop((max(0, left-padding), max(0, top-padding), min(rgb.width, right+padding), min(rgb.height, bottom+padding)))


def _focus_main_subject(image: Image.Image, *, component_ratio: float = 0.16) -> Image.Image:
    """Crop away small disconnected fragments leaked from adjacent grid cells."""
    rgb = image.convert("RGB")
    scale = min(1.0, 280 / max(rgb.size))
    preview = rgb.resize((max(1, round(rgb.width*scale)), max(1, round(rgb.height*scale))), Image.Resampling.BILINEAR)
    pixels = preview.load()
    width, height = preview.size
    foreground = bytearray(width * height)
    for y in range(height):
        for x in range(width):
            red, green, blue = pixels[x, y]
            foreground[y*width+x] = 1 if min(255-red, 255-green, 255-blue) > 12 else 0

    seen = bytearray(width * height)
    components = []
    for start in range(width * height):
        if not foreground[start] or seen[start]:
            continue
        queue = deque([start])
        seen[start] = 1
        count = 0
        left = right = start % width
        top = bottom = start // width
        while queue:
            position = queue.popleft()
            x, y = position % width, position // width
            count += 1
            left, right = min(left, x), max(right, x)
            top, bottom = min(top, y), max(bottom, y)
            for neighbour in (position-1, position+1, position-width, position+width):
                if neighbour < 0 or neighbour >= width*height or seen[neighbour] or not foreground[neighbour]:
                    continue
                nx, ny = neighbour % width, neighbour // width
                if abs(nx-x) + abs(ny-y) != 1:
                    continue
                seen[neighbour] = 1
                queue.append(neighbour)
        components.append((count, left, top, right+1, bottom+1))

    if not components:
        return rgb
    largest = max(component[0] for component in components)
    kept = [component for component in components if component[0] >= max(12, largest * component_ratio)]
    left = min(component[1] for component in kept)
    top = min(component[2] for component in kept)
    right = max(component[3] for component in kept)
    bottom = max(component[4] for component in kept)
    padding = 5
    return rgb.crop((
        max(0, round((left-padding)/scale)),
        max(0, round((top-padding)/scale)),
        min(rgb.width, round((right+padding)/scale)),
        min(rgb.height, round((bottom+padding)/scale)),
    ))


def _resolve_crop_ranges(values, count: int, *, page_id: str, axis: str):
    if values is None:
        return [(index/count, (index+1)/count) for index in range(count)]
    if len(values) == count+1 and all(isinstance(value, (int, float)) for value in values):
        ranges = list(zip(values, values[1:]))
    elif len(values) == count and all(isinstance(value, list) and len(value) == 2 for value in values):
        ranges = [tuple(value) for value in values]
    else:
        raise ValueError(f"Invalid {axis} crop bands for {page_id}")
    if any(start < 0 or end > 1 or start >= end for start, end in ranges):
        raise ValueError(f"Invalid {axis} crop band range for {page_id}")
    return ranges


def activate_page_art(page_id: str, manifest: dict) -> None:
    global CURRENT_ART
    if page_id in PAGE_ART_CACHE:
        CURRENT_ART = PAGE_ART_CACHE[page_id]
        return
    spec = manifest["pages"][page_id]
    sheet = Image.open(ART_ROOT / spec["file"]).convert("RGB")
    columns = spec["grid"]["columns"]
    rows = spec["grid"]["rows"]
    crop_bands = spec.get("crop_bands", {})
    x_ranges = _resolve_crop_ranges(crop_bands.get("x"), columns, page_id=page_id, axis="x")
    y_ranges = _resolve_crop_ranges(crop_bands.get("y"), rows, page_id=page_id, axis="y")
    art = {}
    for index, label in enumerate(spec["order"]):
        row, column = divmod(index, columns)
        # Keep nearly the complete generated cell.  A former 8.5% inset removed
        # valid edge detail (bedposts, people and vehicles).  Disconnected-component
        # cleanup below is the safe place to reject neighbouring-cell fragments.
        left = sheet.width * x_ranges[column][0]
        right = sheet.width * x_ranges[column][1]
        top = sheet.height * y_ranges[row][0]
        bottom = sheet.height * y_ranges[row][1]
        inset_x = (right - left) * spec.get("crop_inset", 0.006)
        inset_y = (bottom - top) * spec.get("crop_inset", 0.006)
        crop = sheet.crop((round(left+inset_x), round(top+inset_y),
                           round(right-inset_x), round(bottom-inset_y)))
        if page_id != "MW-LKG-V4-P015":
            # Dense room scenes contain several legitimate small components;
            # matching sheets benefit from a stronger fragment filter.
            if page_id == "MW-LKG-V4-P009":
                component_ratio = 0.12
            elif page_id in {"MW-LKG-V4-P010", "MW-LKG-V4-P011", "MW-LKG-V4-P013"}:
                # These matching sheets contain small pieces of neighbouring
                # cells around otherwise complete subjects. Keep only substantial
                # components so shoes, faces and building slivers cannot leak into
                # the final activity cards.
                component_ratio = 0.65
            else:
                component_ratio = spec.get("component_ratio", 0.18)
            crop = _focus_main_subject(crop, component_ratio=component_ratio)
            # A few generated cells have a subject connected to a tiny edge leak,
            # so component filtering alone cannot separate it. These conservative
            # trims remove only the contaminated outer strip and retain the full
            # named subject.
            edge_trims = {
                ("MW-LKG-V4-P010", "ask for help"): (0.15, 0.00),
                ("MW-LKG-V4-P010", "library"): (0.00, 0.05),
                ("MW-LKG-V4-P010", "learn together"): (0.25, 0.00),
                ("MW-LKG-V4-P013", "send a letter"): (0.00, 0.05),
                ("MW-LKG-V4-P013", "library"): (0.06, 0.00),
                ("MW-LKG-V4-P013", "post office"): (0.08, 0.00),
                ("MW-LKG-V4-P013", "call firefighters"): (0.05, 0.00),
                ("MW-LKG-V4-P026", "eid crescent"): (0.00, 0.10),
                ("MW-LKG-V4-P034", "take a photo"): (0.00, 0.16),
            }
            left_trim, right_trim = edge_trims.get((page_id, label.lower()), (0.0, 0.0))
            if left_trim or right_trim:
                crop = crop.crop((
                    round(crop.width * left_trim),
                    0,
                    round(crop.width * (1.0 - right_trim)),
                    crop.height,
                ))
        art[label.lower()] = _trim_white(crop)
    PAGE_ART_CACHE[page_id] = art
    CURRENT_ART = art


def activate_shared_art(manifest: dict) -> None:
    """Load curriculum-aligned extras used to complete balanced 4+4 layouts."""
    global SHARED_ART
    spec = manifest.get("shared_assets")
    if not spec:
        SHARED_ART = {}
        return
    sheet = Image.open(ART_ROOT / spec["file"]).convert("RGB")
    columns = spec["grid"]["columns"]
    rows = spec["grid"]["rows"]
    crop_bands = spec.get("crop_bands", {})
    x_ranges = _resolve_crop_ranges(crop_bands.get("x"), columns, page_id="shared_assets", axis="x")
    y_ranges = _resolve_crop_ranges(crop_bands.get("y"), rows, page_id="shared_assets", axis="y")
    art = {}
    for index, label in enumerate(spec["order"]):
        row, column = divmod(index, columns)
        left = sheet.width * x_ranges[column][0]
        right = sheet.width * x_ranges[column][1]
        top = sheet.height * y_ranges[row][0]
        bottom = sheet.height * y_ranges[row][1]
        inset_x = (right - left) * spec.get("crop_inset", 0.006)
        inset_y = (bottom - top) * spec.get("crop_inset", 0.006)
        crop = sheet.crop((round(left+inset_x), round(top+inset_y),
                           round(right-inset_x), round(bottom-inset_y)))
        crop = _focus_main_subject(crop, component_ratio=spec.get("component_ratio", 0.02))
        art[label.lower()] = _trim_white(crop)
    SHARED_ART = art


def paste_generated_art(label: str, box) -> bool:
    if CURRENT_CANVAS is None:
        return False
    source = CURRENT_ART.get(label.lower()) or SHARED_ART.get(label.lower())
    if source is None:
        return False
    x0, y0, x1, y1 = map(int, box)
    available_width = max(1, x1-x0)
    available_height = max(1, y1-y0)
    image = source.copy().convert("RGBA")
    # PIL.thumbnail() never enlarges an image.  The generated grid crops are often
    # only 200-450 px, while the workbook card gives them substantially more room.
    # Resize explicitly so every subject uses the available card without cropping.
    scale = min(available_width / image.width, available_height / image.height)
    image = image.resize((max(1, round(image.width * scale)),
                          max(1, round(image.height * scale))), Image.Resampling.LANCZOS)
    # Remove only the nearly-white sheet background; retain soft object shadows.
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            red, green, blue, alpha = pixels[x, y]
            if red > 248 and green > 248 and blue > 248:
                pixels[x, y] = (red, green, blue, 0)
    position = (x0+(available_width-image.width)//2, y0+(available_height-image.height)//2)
    CURRENT_CANVAS.paste(image, position, image)
    return True


def paste_page_art(page_id: str, label: str, box, manifest: dict) -> bool:
    global CURRENT_ART
    previous = CURRENT_ART
    activate_page_art(page_id, manifest)
    pasted = paste_generated_art(label, box)
    CURRENT_ART = previous
    return pasted


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def panel(draw, box, *, fill="#FFFFFF", outline=SOFT_PURPLE, width=4, radius=24):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def fitted(text, draw, value, box, *, size=36, minimum=22, colour=NAVY, bold=False, lines=1, align="center"):
    text.fitted_text(draw, value, box, max_size=size, min_size=minimum, colour=colour,
                     bold=bold, max_lines=lines, align=align)


def header(canvas, draw, page, logo, text):
    logo_image = logo.copy().convert("RGBA")
    logo_image.thumbnail((300, 220), Image.Resampling.LANCZOS)
    canvas.paste(logo_image, (105 + (300-logo_image.width)//2, 35 + (220-logo_image.height)//2), logo_image)
    fitted(text, draw, "My World & General Awareness", [440, 45, 2320, 145], size=42, minimum=31, colour=PURPLE, bold=True)
    fitted(text, draw, page["title"], [440, 140, 2320, 275], size=68, minimum=43, bold=True, lines=2)
    panel(draw, [150, 305, 2330, 445], fill=BLUE, outline="#1768B3", width=3)
    fitted(text, draw, "Learning goal: " + page["objective"], [190, 318, 2290, 432], size=45, minimum=30, bold=True, lines=2)
    panel(draw, [150, 490, 2330, 650], fill=GOLD, outline="#E1A81C", width=3)
    fitted(text, draw, page["instruction"], [190, 505, 2290, 635], size=47, minimum=28, colour=INK, bold=True, lines=2)


def model_shell(draw, text):
    panel(draw, [170, 700, 2310, 900], fill="#F6F1FF", outline=SOFT_PURPLE, width=3)
    panel(draw, [195, 720, 535, 880], fill="#E7D9FA", outline=SOFT_PURPLE, width=2, radius=18)
    fitted(text, draw, "COMPLETED\nEXAMPLE", [220, 737, 510, 862], size=35, minimum=27, bold=True, lines=2)
    return [575, 720, 2275, 880]


def arrow(draw, x0, y, x1):
    draw.line([x0, y, x1, y], fill=PURPLE, width=7)
    draw.polygon([(x1, y), (x1-42, y-27), (x1-42, y+27)], fill=PURPLE)


def completed_model(draw, number, text):
    x0, y0, x1, y1 = model_shell(draw, text)
    cy = (y0+y1)//2
    letter_examples = {
        9: ("bedroom", "B", "bed", "Bedroom matches bed."),
        10: ("library", "C", "read books", "Library matches read books."),
        11: ("doctor", "C", "stethoscope", "Doctor matches stethoscope."),
        13: ("hospital", "E", "get medical care", "Hospital matches medical care."),
        16: ("library", "D", "borrow a storybook", "Library matches borrow a storybook."),
        32: ("doctor", "A", "stethoscope", "A doctor matches a stethoscope."),
        34: ("television", "D", "watch programme", "A television matches watching a programme."),
    }
    if number in letter_examples:
        source, letter, target, message = letter_examples[number]
        draw_icon(draw, source, [x0+5, y0+2, x0+270, y1-28])
        fitted(text, draw, source, [x0+5, y1-42, x0+270, y1-5], size=22, minimum=18, bold=True)
        arrow(draw, x0+300, cy, x0+440)
        draw.rounded_rectangle([x0+475, cy-48, x0+575, cy+48], radius=16, fill="white", outline=PURPLE, width=4)
        fitted(text, draw, letter, [x0+487, cy-36, x0+563, cy+36], size=42, minimum=34, bold=True)
        draw_icon(draw, target, [x0+610, y0+2, x0+900, y1-28])
        fitted(text, draw, target, [x0+600, y1-42, x0+915, y1-5], size=21, minimum=17, bold=True)
        fitted(text, draw, message, [x0+950, y0+25, x1-15, y1-25], size=30, minimum=21, bold=True, lines=2, align="left")
        retur×ýÒÚ$z{-®éÜj×#‚"Â&&—&B"Å³SsÃs#ÃƒSÃ“3ÒÆÖæ–fW7B¢f—GFVB‡FW‡BÆG&rÂ$4ôÕÄUDTBU„ÕÄS¢’6r&—&B–âF†R&²â"Å³ƒ“ÃsCRÃ##Ã“ÒÇ6—¦SÓ3bÆÖ–æ–×VÓÓ#bÆ&öÆCÕG'VRÆÆ–æW3Ó"ÆÆ–vãÒ&ÆVgB"¢æVÂ†G&rÅ³sÃÃ#3Ã#CsÒÆf–ÆÃÒ'v†—FR"Æ÷WFÆ–æSÕDTÂÇv–GFƒÓRÇ&F—W3ÓC¢f—GFVB‡FW‡BÆG&rÂ$E$rt„B”õRäõD”4TBDôD’"Å³33ÃcÃ#SÃcÒÇ6—¦SÓCÆÖ–æ–×VÓÓ3Æ6öÆ÷W#ÕU%ÄRÆ&öÆCÕG'VR¢&ö×G3Õ²$’6rõõõõõõõõõõõõõõõõõõõõõõõõõõõò"Â$—Bv2Bõõõõõõõõõõõõõõõõõõõõõõõò"Â$’fVÇBõõõõõõõõõõõõõõõõõõõõõõõõõõò%Ð¢f÷"–æFW‚Ç&ö×B–âVçVÖW&FR‡&ö×G2“ ¢f—GFVB‡FW‡BÆG&rÇ&ö×BÅ³#cÃ#SC¶–æFW‚£SÃ##Ã#cc¶–æFW‚£SÒÇ6—¦SÓ3‚ÆÖ–æ–×VÓÓ#‚Æ6öÆ÷W#Ô”ä²Æ&öÆCÕG'VRÆÆ–vãÒ&ÆVgB"¢FV6†W%öfö÷FW"†G&rÇvRÇFW‡B  ¦FVb7F%ö÷WFÆ–æR†G&rÂ6VçFW"Â&F—W2Â¢Âf–ÆÃÒ'v†—FR"Â÷WFÆ–æSÕU%ÄRÂv–GFƒÓR“ ¢ö–çG3ÕµÐ¢f÷"–æFW‚–â&ævRƒ“ ¢ævÆSÖÖF‚ç&F–ç2‚Ó“¶–æFW‚£3b“²#×&F—W2–b–æFW‚S#ÓÓVÇ6R&F—W2£ãCP¢ö–çG2æVæB‚†6VçFW%³Ò¶ÖF‚æ6÷2†ævÆR’§"Æ6VçFW%³Ò¶ÖF‚ç6–â†ævÆR’§"’¢G&rçöÇ–vöâ‡ö–çG2Æf–ÆÃÖf–ÆÂÆ÷WFÆ–æSÖ÷WFÆ–æR¢G&ræÆ–æR‡ö–çG2µ·ö–çG5³ÕÒÆf–ÆÃÖ÷WFÆ–æRÇv–GFƒ×v–GF‚Æ¦ö–çCÒ&7W'fR"  ¦FVb&VæFW%÷C÷7V6–Â†6çf2ÂG&rÂFW‡BÂvRÂÆövòÂÖæ–fW7B“ ¢†VFW"†6çf2ÆG&rÇvRÆÆövòÇFW‡B¢æVÂ†G&rÅ³sÃsÃ#3Ã“ÒÆf–ÆÃÒ"4cdcdb"¢7F%ö÷WFÆ–æR†G&rÂƒsÃƒR’ÃsÆf–ÆÃÒ"4ddCƒDB"¢f—GFVB‡FW‡BÆG&rÂ$4ôÕÄUDTBU„ÕÄS¢6öÆ÷W"7F"f÷"6öÖWF†–ær–÷R6âFòâ"Å³ƒ#ÃsCÃ##3ÃƒsUÒÇ6—¦SÓ3BÆÖ–æ–×VÓÓ#RÆ&öÆCÕG'VRÆÆ–æW3Ó"ÆÆ–vãÒ&ÆVgB"¢F÷–73Õ²$Õ•4TÄbbdÔ”Å’"Â%44„ôôÂb4ôÔÕTä•E’"Â$äEU$R"Â$T%D‚4$R%Ð¢f÷"–æFW‚ÇF÷–2–âVçVÖW&FR‡F÷–72“ ¢“Ó“ƒ¶–æFW‚£S ¢æVÂ†G&rÅ³##Ç“Ã##cÇ“³C#ÒÆf–ÆÃÒ"4dddDc‚"–b–æFW‚S#ÓÓVÇ6R$ÅTR¢f—GFVB‡FW‡BÆG&rÇF÷–2Å³3Ç“³SRÃ3#Ç“³SÒÇ6—¦SÓ3rÆÖ–æ–×VÓÓ#‚Æ&öÆCÕG'VRÆÆ–vãÒ&ÆVgB"¢f—GFVB‡FW‡BÆG&rÂ$6öÆ÷W"öæR7F"â"Å³3Ç“³ƒRÃ#SÇ“³#sUÒÇ6—¦SÓ3ÆÖ–æ–×VÓÓ#BÆ6öÆ÷W#Ô”ä²ÆÆ–vãÒ&ÆVgB"¢f÷"7F%ö–æFW‚–â&ævRƒ2“ ¢7F%ö÷WFÆ–æR†G&rÂƒS·7F%ö–æFW‚£#cÇ“³#’Ãƒ"¢f—GFVB‡FW‡BÆG&rÂ$’Ò&÷VBöb†÷r’æ÷F–6RÂF†–æ²æB6&R"Å³3Ã#“3Ã#ƒÃ3SÒÇ6—¦SÓC2ÆÖ–æ–×VÓÓ3Æ6öÆ÷W#ÕDTÂÆ&öÆCÕG'VR¢FV6†W%öfö÷FW"†G&rÇvRÇFW‡B  ¦FVb&VæFW%÷C÷7V6–Â†6çf2ÂG&rÂFW‡BÂvRÂÆövòÂÖæ–fW7B“ ¢G&rç&÷VæFVE÷&V7FævÆR…³SÃ#Ã#33Ã33CÒÇ&F—W3ÓcÆf–ÆÃÒ"4dddDc‚"Æ÷WFÆ–æSÒ"4Sƒ2"Çv–GFƒÓ"¢G&rç&÷VæFVE÷&V7FævÆR…³#RÃsRÃ##sRÃ3#ƒUÒÇ&F—W3ÓSÆ÷WFÆ–æSÕU%ÄRÇv–GFƒÓR¢7FUöÆövò†6çf2ÆÆövòÅ³“Ã##ÃSƒÃSCÒ¢f—GFVB‡FW‡BÆG&rÂ$4U%D”d”4DRôb4ôÕÄUD”ôâ"Å³3ÃScÃ#ƒÃsCÒÇ6—¦SÓsRÆÖ–æ–×VÓÓSÆ6öÆ÷W#ÕU%ÄRÆ&öÆCÕG'VR¢f—GFVB‡FW‡BÆG&rÂ%F†—26W'F–f–6FR—2&÷VFÇ’&W6VçFVBFò"Å³CSÃƒ#Ã#3Ã“CÒÇ6—¦SÓCÆÖ–æ–×VÓÓ3Æ6öÆ÷W#Ô”ä²¢G&ræÆ–æR…³C3ÃÃ#SÃÒÆf–ÆÃÔäe’Çv–GFƒÓR¢f—GFVB‡FW‡BÆG&rÂ$4„”ÄN(	•2äÔR"Å³ƒÃ3ÃcƒÃ#ÒÇ6—¦SÓ#rÆÖ–æ–×VÓÓ#"Æ6öÆ÷W#Ò"3cCsC„""Æ&öÆCÕG'VR¢f—GFVB‡FW‡BÆG&rÂ&f÷"6ö×ÆWF–ær"Å³sÃ3CÃsƒÃCCÒÇ6—¦SÓC"ÆÖ–æ–×VÓÓ3Æ6öÆ÷W#Ô”ä²¢f—GFVB‡FW‡BÆG&rÂ$×’v÷&ÆBbvVæW&Âv&VæW72(	BÄ´r"Å³#ƒÃSÃ##ÃccÒÇ6—¦SÓS‚ÆÖ–æ–×VÓÓCÆ&öÆCÕG'VR¢f—GFVB‡FW‡BÆG&rÂ&æB6†÷v–ær7W&–÷6—G’Â6öæf–FVæ6RæB6&Rf÷"F†Rv÷&ÆBâ"Å³C#ÃsCÃ#cÃ“#ÒÇ6—¦SÓ3’ÆÖ–æ–×VÓÓ#’Æ6öÆ÷W#ÕDTÂÆ&öÆCÕG'VRÆÆ–æW3Ó"¢G&u÷7F%öÖ66÷B†G&rÅ³ƒSÃ“SÃc3Ã#sÒ¢G&ræÆ–æR…³3Ã#“#ÃSÃ#“#ÒÆf–ÆÃÔäe’Çv–GFƒÓB“²G&ræÆ–æR…³C3Ã#“#Ã#ƒÃ#“#ÒÆf–ÆÃÔäe’Çv–GFƒÓB¢f—GFVB‡FW‡BÆG&rÂ$DDR"Å³SÃ#“CÃƒSÃ3#ÒÇ6—¦SÓ#rÆÖ–æ–×VÓÓ#Æ6öÆ÷W#Ò"3cCsC„""Æ&öÆCÕG'VR¢f—GFVB‡FW‡BÆG&rÂ%DT4„U"4”täEU$R"Å³SCÃ#“CÃ#sÃ3#ÒÇ6—¦SÓ#rÆÖ–æ–×VÓÓ#Æ6öÆ÷W#Ò"3cCsC„""Æ&öÆCÕG'VR¢G&u÷&–çFVEöçVÖ&W"†G&rÇFW‡BÇvU²'&–çFVE÷vR%Ò  ¦FVb76W76ÖVçEöf6R†G&rÂ6VçFW"Â&F—W2Â¢Â¶æ÷vãÔfÇ6RÂ6VÆV7FVCÔfÇ6R“ ¢7‚Æ7“Ö6VçFW ¢f–ÆÃÒ"4DDcTD2"–b6VÆV7FVBVÇ6R'v†—FR ¢÷WFÆ–æSÕDTÂ–b6VÆV7FVBVÇ6RU%ÄP¢G&ræVÆÆ—6R…¶7‚×&F—W2Æ7’×&F—W2Æ7‚·&F—W2Æ7’·&F—W5ÒÆf–ÆÃÖf–ÆÂÆ÷WFÆ–æSÖ÷WFÆ–æRÇv–GFƒÓR¢W–U÷#ÖÖ‚ƒBÇ&F—W2òó"¢f÷"W–U÷‚–â†7‚×&F—W2£ã3"Æ7‚·&F—W2£ã3"“ ¢G&ræVÆÆ—6R…¶W–U÷‚ÖW–U÷"Æ7’×&F—W2£ã‚ÖW–U÷"ÆW–U÷‚¶W–U÷"Æ7’×&F—W2£ã‚¶W–U÷%ÒÆf–ÆÃÔäe’¢–b¶æ÷vã ¢G&ræ&2…¶7‚×&F—W2£ã3‚Æ7’×&F—W2£ãRÆ7‚·&F—W2£ã3‚Æ7’·&F—W2£ãC…ÒÃ‚Ãs"Æf–ÆÃÔäe’Çv–GFƒÓR¢VÇ6S ¢G&ræÆ–æR…¶7‚×&F—W2£ã#RÆ7’·&F—W2£ã#‚Æ7‚·&F—W2£ã#RÆ7’·&F—W2£ã#…ÒÆf–ÆÃÔäe’Çv–GFƒÓR  ¦FVb&VæFW%÷C%÷7V6–Â†6çf2ÂG&rÂFW‡BÂvRÂÆövòÂÖæ–fW7B“ ¢†VFW"†6çf2ÆG&rÇvRÆÆövòÇFW‡B¢æVÂ†G&rÅ³sÃsÃ#3Ã“#ÒÆf–ÆÃÒ"4cdcdb"¢f—GFVB‡FW‡BÆG&rÂ$4ôÕÄUDTBU„ÕÄS¢tTD„U""Å³#3ÃsSÃSÃƒSÒÇ6—¦SÓ3BÆÖ–æ–×VÓÓ#RÆ&öÆCÕG'VRÆÆ–vãÒ&ÆVgB"¢76W76ÖVçEöf6R†G&rÂƒ#cÃƒR’ÃsÆ¶æ÷vãÕG'VRÇ6VÆV7FVCÕG'VR¢f—GFVB‡FW‡BÆG&rÂ$’´äõr•B"Å³3cÃsSRÃƒÃƒSÒÇ6—¦SÓ3"ÆÖ–æ–×VÓÓ#BÆ&öÆCÕG'VRÆÆ–vãÒ&ÆVgB"¢F÷–73Õ²‚$dÔ”Å’"Ã‚Â&Ö÷F†W""’Â‚%Ä4U2"ÃbÂ&Æ–'&'’"’Â‚$äEU$R"Ã#‚Â'G&VR"’Â‚$dôôB"Ã#BÂ&&ææ"’Â‚%4dUE’"Ã3bÂ'vV"&–7–6ÆR†VÆÖWB"’Â‚$T%D‚4$R"Ã#’Â&6Æ÷F‚&r"•Ð¢f÷"–æFW‚Â‡F÷–2Ç6÷W&6RÆÆ&VÂ’–âVçVÖW&FR‡F÷–72“ ¢“Ó“s¶–æFW‚£33P¢æVÂ†G&rÅ³“Ç“Ã##“Ç“³#“UÒÆf–ÆÃÒ'v†—FR"–b–æFW‚S#ÓÓVÇ6R"4c„d4db"¢7FU÷vUö'B†b$ÕrÔÄ´rÕcBÕ·6÷W&6S£6GÒ"ÆÆ&VÂÅ³##Ç“³#ÃS3Ç“³#sUÒÆÖæ–fW7B¢f—GFVB‡FW‡BÆG&rÇF÷–2Å³SsÇ“³sRÃ3Ç“³#ÒÇ6—¦SÓ3RÆÖ–æ–×VÓÓ#bÆ&öÆCÕG'VRÆÆ–vãÒ&ÆVgB"¢f÷"6†ö–6Uö–æFW‚Æ6†ö–6R–âVçVÖW&FR…²$’´äõr•B"Â$’ÒÄT$ä”är%Ò“ ¢ƒÓ“¶6†ö–6Uö–æFW‚£S# ¢76W76ÖVçEöf6R†G&rÂ‡ƒ³cÇ“³R’ÃcÆ¶æ÷vãÖ6†ö–6Uö–æFWƒÓÓ¢f—GFVB‡FW‡BÆG&rÆ6†ö–6RÅ·ƒÓ3RÇ“³“Çƒ³3“Ç“³#sÒÇ6—¦SÓ#RÆÖ–æ–×VÓÓ’Æ&öÆCÕG'VR¢FV6†W%öfö÷FW"†G&rÇvRÇFW‡B  ¦FVb&VæFW%÷C5÷7V6–Â†6çf2ÂG&rÂFW‡BÂvRÂÆövòÂÖæ–fW7B“ ¢†VFW"†6çf2ÆG&rÇvRÆÆövòÇFW‡B¢æVÂ†G&rÅ³sÃsÃ#3Ã“SÒÆf–ÆÃÒ"4cdcdb"¢7FU÷vUö'B‚$ÕrÔÄ´rÕcBÕ#‚"Â'G&VR"Å³ScÃs#ÃƒSÃ“3ÒÆÖæ–fW7B¢f—GFVB‡FW‡BÆG&rÂ$4ôÕÄUDTBU„ÕÄS¢’ÆV&æVBF†BÆçG2æVVBvFW"â"Å³ƒ“ÃsCRÃ###Ã“ÒÇ6—¦SÓ3RÆÖ–æ–×VÓÓ#RÆ&öÆCÕG'VRÆÆ–æW3Ó"ÆÆ–vãÒ&ÆVgB"¢æVÂ†G&rÅ³sÃÃ#3Ã#ccÒÆf–ÆÃÒ'v†—FR"Æ÷WFÆ–æSÕDTÂÇv–GFƒÓRÇ&F—W3ÓC¢f—GFVB‡FW‡BÆG&rÂ$E$r”õU"ddõU$•DRD„”äre$ôÒD„•2$ôô²"Å³3ÃcÃ#ƒÃsÒÇ6—¦SÓCÆÖ–æ–×VÓÓ#’Æ6öÆ÷W#ÕU%ÄRÆ&öÆCÕG'VR¢f—GFVB‡FW‡BÆG&rÂ$’ÆV&æVB&÷WBõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõõò"Å³#cÃ#ssÃ###Ã#“ÒÇ6—¦SÓ3‚ÆÖ–æ–×VÓÓ#‚Æ6öÆ÷W#Ô”ä²Æ&öÆCÕG'VRÆÆ–vãÒ&ÆVgB"¢FV6†W%öfö÷FW"†G&rÇvRÇFW‡B  ¦FVb&VæFW%÷CE÷7V6–Â†6çf2ÂG&rÂFW‡BÂvRÂÆövòÂÖæ–fW7B“ ¢7FUöÆövò†6çf2ÆÆövòÅ³scÃƒÃs#ÃcSÒ¢f—GFVB‡FW‡BÆG&rÂ$$7V&RgWGW&R6¶–ÆÇ2ÆV&æ–ær6W&–W>(J""Å³3Ãs#Ã#ƒÃƒ3ÒÇ6—¦SÓC‚ÆÖ–æ–×VÓÓ3BÆ6öÆ÷W#ÕU%ÄRÆ&öÆCÕG'VR¢f—GFVB‡FW‡BÆG&rÂ$Õ’tõ$ÄBbtTäU$Ât$TäU52"Å³#cÃ“Ã###ÃƒÒÇ6—¦SÓc"ÆÖ–æ–×VÓÓC2Æ&öÆCÕG'VR¢f—GFVB‡FW‡BÆG&rÂ$Ä´r"Å³ƒƒÃÃcÃ#ÒÇ6—¦SÓSÆÖ–æ–×VÓÓ3‚Æ6öÆ÷W#ÕDTÂÆ&öÆCÕG'VR¢æVÂ†G&rÅ³#SÃ3#Ã##3ÃssÒÆf–ÆÃÒ"4c„cDdb"Æ÷WFÆ–æSÕ4ôeEõU%ÄRÇv–GFƒÓBÇ&F—W3ÓC"¢f—GFVB‡FW‡BÆG&rÂ$¦÷–gVÂf÷VæFF–öâf÷"æ÷F–6–ærÂæÖ–æræB6&–ærf÷"fÖ–Ç’Â6öÖ×Væ—G’ÂæGW&RÂ6fWG’æB÷W"V'F‚â"Å³3“ÃC#Ã#“ÃcƒÒÇ6—¦SÓC2ÆÖ–æ–×VÓÓ3Æ6öÆ÷W#Ô”ä²Æ&öÆCÕG'VRÆÆ–æW3Ó2¢–ÆÆ'3Õ²$7&VF—f—G’"Â$6öÖ×Væ–6F–öâ"Â$7W&–÷6—G’"Â$6öæf–FVæ6R%Ð¢f÷"–æFW‚Ç–ÆÆ"–âVçVÖW&FR‡–ÆÆ'2“ ¢6öÃÖ–æFW‚S#²&÷sÖ–æFW‚òó#²ƒÓ3¶6öÂ£“ƒ²“Ó“·&÷r£#c ¢æVÂ†G&rÅ·ƒÇ“Çƒ³ƒƒÇ“³“ÒÆf–ÆÃÔtôÄB–b–æFW‚S#ÓÓVÇ6R$ÅTRÆ÷WFÆ–æSÕDTÂÇv–GFƒÓ2Ç&F—W3Ó3‚¢f—GFVB‡FW‡BÆG&rÇ–ÆÆ"Å·ƒ³CÇ“³CRÇƒ³ƒCÇ“³CUÒÇ6—¦SÓCÆÖ–æ–×VÓÓ3Æ&öÆCÕG'VR¢G&u÷7F%öÖ66÷B†G&rÅ³“Ã#CÃSƒÃ3cÒ¢f—GFVB‡FW‡BÆG&rÂ$$7V&RgWGW&R6FV×’"Å³#sÃ3“Ã##Ã3sÒÇ6—¦SÓ3’ÆÖ–æ–×VÓÓ3Æ&öÆCÕG'VR¢f—GFVB‡FW‡BÆG&rÂ#CrÂE4Ô‚6·’7W&VÖRµ5B&ævÆ÷&RÒScc(
"–æfô&7V&VgWGW&V6FV×’æ–â(
"&7V&VgWGW&V6FV×’æ–â"Å³##Ã3ƒÃ##cÃ3#ƒÒÇ6—¦SÓ#rÆÖ–æ–×VÓÓ#Æ6öÆ÷W#Ô”ä²Æ&öÆCÕG'VRÆÆ–æW3Ó"¢f—GFVB‡FW‡BÆG&rÂ,*’##b$7V&RgWGW&R6FV×’âf—'7BVF—F–öâÂ##bâÆÂ&–v‡G2&W6W'fVBâ"Å³#CÃ333Ã##CÃ3CÒÇ6—¦SÓ#RÆÖ–æ–×VÓÓ’Æ6öÆ÷W#Ò"3cCsC„""  ¥$TäDU$U%3×°¢ƒ§&VæFW%÷‚Ã“§&VæFW%÷’Ã§&VæFW%÷Ã§&VæFW%÷Ã#§&VæFW%÷"À¢3§&VæFW%÷2ÃC§&VæFW%÷BÃS§&VæFW%÷RÃc§&VæFW%÷bÃs§&VæFW%÷rÀ¢ƒ§&VæFW%÷‚Ã“§&VæFW%÷’Ã#§&VæFW%÷#Ã#§&VæFW%÷#Ã##§&VæFW%÷#"À¢#3§&VæFW%÷#2Ã#C§&VæFW%÷#BÃ#S§&VæFW%÷#RÃ#c§&VæFW%÷#bÃ#s§&VæFW%÷#rÀ¢#ƒ§&VæFW%÷#‚Ã#“§&VæFW%÷#’Ã3§&VæFW%÷3Ã3§&VæFW%÷3Ã3#§&VæFW%÷3"À¢33§&VæFW%÷32Ã3C§&VæFW%÷3BÃ3S§&VæFW%÷3RÃ3c§&VæFW%÷3bÀ§Ð ¥5T4”Åõ$TäDU$U%3×°¢§&VæFW%÷÷7V6–ÂÃ#§&VæFW%÷%÷7V6–ÂÃ3§&VæFW%÷5÷7V6–ÂÀ¢C§&VæFW%÷E÷7V6–ÂÃS§&VæFW%÷U÷7V6–ÂÃc§&VæFW%÷e÷7V6–ÂÀ¢s§&VæFW%÷u÷7V6–ÂÃ3s§&VæFW%÷3u÷7V6–ÂÃ3ƒ§&VæFW%÷3…÷7V6–ÂÀ¢3“§&VæFW%÷3•÷7V6–ÂÃC§&VæFW%÷C÷7V6–ÂÃC§&VæFW%÷C÷7V6–ÂÀ¢C#§&VæFW%÷C%÷7V6–ÂÃC3§&VæFW%÷C5÷7V6–ÂÃCC§&VæFW%÷CE÷7V6–ÂÀ§Ð  ¦FVb&VæFW%ööæR†çVÖ&W"Â&ÇVW&–çBÂÆövòÂ÷WGWEöF—#¥F‚ÂWf–FVæ6UöF—#¥F‚ÂFW‡BÂ'EöÖæ–fW7B“ ¢vÆö&Â5U%$TåEô4åd2Â5U%$TåEô%@¢vUö–CÖb$ÕrÔÄ´rÕcBÕ¶çVÖ&W#£6GÒ ¢vSÖ&ÇVW&–çE²'vW2%Õ·vUö–EÐ¢6çf3Ô–ÖvRææWr‚%$t""Â…t”ED‚Ä„T”t…B’Â"4ddd4cr"¢5U%$TåEô4åd2Ò6çf0¢G&sÔ–ÖvTG&räG&r†6çf2¢–bçVÖ&W"–â5T4”Åõ$TäDU$U%3 ¢5U%$TåEô%BÒ·Ð¢5T4”Åõ$TäDU$U%5¶çVÖ&W%Ò†6çf2ÆG&rÇFW‡BÇvRÆÆövòÆ'EöÖæ–fW7B¢VÇ6S ¢7F—fFU÷vUö'B‡vUö–BÂ'EöÖæ–fW7B¢†VFW"†6çf2ÆG&rÇvRÆÆövòÇFW‡B¢6ö×ÆWFVEöÖöFVÂ†G&rÆçVÖ&W"ÇFW‡B¢$TäDU$U%5¶çVÖ&W%Ò†6çf2ÆG&rÇFW‡B¢FV6†W%öfö÷FW"†G&rÇvRÇFW‡B¢÷WGWEöF—"æÖ¶F—"‡&VçG3ÕG'VRÆW†—7Eöö³ÕG'VR“²Wf–FVæ6UöF—"æÖ¶F—"‡&VçG3ÕG'VRÆW†—7Eöö³ÕG'VR¢÷WGWCÖ÷WGWEöF—"öb'·vUö–GÒçær#²6çf2ç6fR†÷WGWBÂ%är"ÆG“Òƒ3Ã3’¢&W7öç6UöÖV6†æ–72Ò°¢s¢&6—&6ÆRvVF†W"v÷&B"Ãƒ¢'6÷'B–7GW&RçVÖ&W'2"Ã“¢'Æ6R'BçVÖ&W'2"À¢#¢&G&ræ–ÖÂÖ†öÖRÖfööBÆ–æW2"Ã#¢'6÷'B–7GW&RçVÖ&W'2"À¢##¢&6†ö÷6RæBw&—FRGvòçVÖ&W'2"Ã#3¢'6÷'B–7GW&RçVÖ&W'2"À¢#C¢'6÷'B–7GW&RçVÖ&W'2"Ã#S¢&6—&6ÆRöÆ—FR7F–öâ"À¢Ð¢†Wf–FVæ6UöF—"öb'·vUö–GÒæ§6öâ"’çw&—FU÷FW‡B†§6öâæGV×2‡°¢'vUö–B#§vUö–BÂ'7FGW2#¢%52"Â&6ö×ÆWFVEöW†×ÆU÷f—6–&ÆR#¥G'VRÀ¢&–æFWVæFVçEöç7vW'5÷VæÖ&¶VB#¥G'VRÂ'&W7öç6U÷76U÷W'÷6VgVÂ#¥G'VRÀ¢&ö&¦V7EöæÖW5÷f—6–&ÆR#¥G'VRÂ&vVæW&FVEö–ÆÇW7G&F–öç5÷W6VB#¦çVÖ&W"æ÷B–âƒ"Ã2ÃBÃRÃCÃCB’À¢&vVæW&FVEö76WEö6÷VçB#¦ÆVâ†'EöÖæ–fW7E²'vW2%ÒævWB‡vUö–BÇ·Ò’ævWB‚&÷&FW""ÅµÒ’’À¢&ÆWGFW%öÖF6†–æu÷&W7öç6R#¦çVÖ&W"–âƒ’ÃÃÃ2ÃbÃ3"Ã3B’À¢&ÖF6†–æuö6†ö–6W5öÆWGFW&VB#¦çVÖ&W"–âƒ’ÃÃÃ2ÃbÃ3"Ã3B’À¢'&W7öç6UöÖV6†æ–2#§&W7öç6UöÖV6†æ–72ævWB†çVÖ&W"Â'vR×7V6–f–2"’À¢&6ö×öæVçEö7&÷ö&æG5÷W6VB#¢&7&÷ö&æG2"–â'EöÖæ–fW7E²'vW2%ÒævWB‡vUö–BÇ·Ò’À¢'&VçE÷æVÂ#¤fÇ6RÂ'FV6†W%ö7VU÷vU÷7V6–f–2#¥G'VP¢ÒÆ–æFVçCÓ"’²%Æâ"ÆVæ6öF–æsÒ'WFbÓ‚"¢&WGW&â÷WGW@  ¦FVb6öçF7E÷6†VWB‡F‡2Æ÷WGWB“ ¢F‡VÖ%÷sÓ3–bÆVâ‡F‡2“ã#VÇ6R3c²F‡VÖ%öƒ×&÷VæB‡F‡VÖ%÷r¤„T”t…Bõt”ED‚“²6öÇ3ÓB–bÆVâ‡F‡2“ã#VÇ6R3²&÷w3ÖÖF‚æ6V–Â†ÆVâ‡F‡2’ö6öÇ2¢6†VWCÔ–ÖvRææWr‚%$t""Â‡F‡VÖ%÷r¦6öÇ2ÇF‡VÖ%ö‚§&÷w2’Â'v†—FR"¢f÷"’ÇF‚–âVçVÖW&FR‡F‡2“ ¢–ÖvSÔ–ÖvRæ÷Vâ‡F‚’æ6öçfW'B‚%$t""“²–ÖvRçF‡VÖ&æ–Â‚‡F‡VÖ%÷rÇF‡VÖ%ö‚’Ä–ÖvRå&W6×Æ–æräÄä5¤õ2¢6†VWBç7FR†–ÖvRÂ‚†’V6öÇ2’§F‡VÖ%÷rÂ†’òö6öÇ2’§F‡VÖ%ö‚’¢6†VWBç6fR†÷WGWBÂ%är"  ¦FVb6öç6öÆ–FFU÷Fb‡F‡2Â÷WGWB“ ¢g&öÒ–ò–×÷'B'—FW4”ð¢g&öÒ&W÷'FÆ"æÆ–"çvW6—¦W2–×÷'B@¢g&öÒ&W÷'FÆ"æÆ–"çWF–Ç2–×÷'B–ÖvU&VFW ¢g&öÒ&W÷'FÆ"çFfvVâ–×÷'B6çf22Feö6çf0¢÷WGWBç&VçBæÖ¶F—"‡&VçG3ÕG'VRÆW†—7Eöö³ÕG'VR¢Fö7VÖVçC×Feö6çf2ä6çf2‡7G"†÷WGWB’ÇvW6—¦SÔBÇvT6ö×&W76–öãÓ¢f÷"F‚–âF‡3 ¢§VsÔ'—FW4”ò‚¢–ÖvRæ÷Vâ‡F‚’æ6öçfW'B‚%$t""’ç6fR†§VrÂ$¥Tr"ÇVÆ—G“Ó“"Ç7V'6×Æ–æsÓÆ÷F–Ö—¦SÕG'VRÆG“Òƒ3Ã3’¢§Vrç6VV²ƒ¢Fö7VÖVçBæG&t–ÖvR„–ÖvU&VFW"†§Vr’ÃÃÇv–GFƒÔE³ÒÆ†V–v‡CÔE³ÒÇ&W6W'fT7V7E&F–óÕG'VRÆæ6†÷#Ò&2"¢Fö7VÖVçBç6†÷uvR‚¢Fö7VÖVçBç6fR‚  ¦FVb'6U÷vW2‡fÇVS¢7G"’ÓâGWÆU¶–çBÂââåÓ ¢6VÆV7FVBÒµÐ¢f÷"Fö¶Vâ–âfÇVRç7Æ—B‚"Â"“ ¢Fö¶VâÒFö¶Vâç7G&—‚’çWW"‚¢–bæ÷BFö¶Vã ¢6öçF–çVP¢–b"Ò"–âFö¶Vã ¢7F'E÷FW‡BÂVæE÷FW‡BÒFö¶Vâç7Æ—B‚"Ò"Â¢7F'EöF–v—G2Ò""æ¦ö–â†6†&7FW"f÷"6†&7FW"–â7F'E÷FW‡B–b6†&7FW"æ—6F–v—B‚’¢VæEöF–v—G2Ò""æ¦ö–â†6†&7FW"f÷"6†&7FW"–âVæE÷FW‡B–b6†&7FW"æ—6F–v—B‚’¢–bæ÷B7F'EöF–v—G2÷"æ÷BVæEöF–v—G3 ¢&—6R&w'6Rä&wVÖVçEG—TW'&÷"†b$–çfÆ–BvR&ævS¢·Fö¶VçÒ"¢7F'BÂVæBÒ–çB‡7F'EöF–v—G2’Â–çB†VæEöF–v—G2¢–b7F'BâVæC ¢&—6R&w'6Rä&wVÖVçEG—TW'&÷"†b%vR&ævR×W7B&R66VæF–æs¢·Fö¶VçÒ"¢6VÆV7FVBæW‡FVæB‡&ævR‡7F'BÂVæB³’¢VÇ6S ¢F–v—G2Ò""æ¦ö–â†6†&7FW"f÷"6†&7FW"–âFö¶Vâ–b6†&7FW"æ—6F–v—B‚’¢–bæ÷BF–v—G3 ¢&—6R&w'6Rä&wVÖVçEG—TW'&÷"†b$–çfÆ–BvS¢·Fö¶VçÒ"¢6VÆV7FVBæVæB†–çB†F–v—G2’¢÷&FW&VBÒGWÆR†F–7Bæg&öÖ¶W—2‡6VÆV7FVB’¢7W÷'FVC×6WB…$TäDU$U%2—Ç6WB…5T4”Åõ$TäDU$U%2¢Vç7W÷'FVBÒ¶çVÖ&W"f÷"çVÖ&W"–â÷&FW&VB–bçVÖ&W"æ÷B–â7W÷'FVEÐ¢–bæ÷B÷&FW&VB÷"Vç7W÷'FVC ¢&—6R&w'6Rä&wVÖVçEG—TW'&÷"†b%7W÷'FVBvW2&RÕCC²–çfÆ–B6VÆV7F–öã¢·Vç7W÷'FVB÷"fÇVWÒ"¢&WGW&â÷&FW&V@  ¦FVbÖ–â‚“ ¢'6W#Ö&w'6Rä&wVÖVçE'6W"‚¢'6W"æFEö&wVÖVçB‚"ÒÖÆövò"ÇG—SÕF‚Ç&WV—&VCÕG'VR¢'6W"æFEö&wVÖVçB‚"Ò×vW2"ÇG—S×'6U÷vW2ÆFVfVÇCÕtU2Æ†VÇÒ%vR6VÆV7F–öâÂf÷"W†×ÆRrÓ#R÷"rÅ’Õ#"¢'6W"æFEö&wVÖVçB‚"ÒÖ÷WGWBÖF—""ÇG—SÕF‚ÆFVfVÇCÕ$ôõBò'v÷&²Ö×’×v÷&ÆB×‚×#R"¢'6W"æFEö&wVÖVçB‚"ÒÖWf–FVæ6RÖF—""ÇG—SÕF‚ÆFVfVÇCÕ$ôõBò'v÷&²Ö×’×v÷&ÆB×‚×#RÖWf–FVæ6R"¢'6W"æFEö&wVÖVçB‚"ÒÖ6öçF7B×6†VWB"ÇG—SÕF‚¢'6W"æFEö&wVÖVçB‚"Ò×Fb"ÇG—SÕF‚Æ†VÇÒ$÷F–öæÂ6öç6öÆ–FFVBDb÷WGWB"¢&w3×'6W"ç'6Uö&w2‚¢&ÇVW&–çCÖ§6öâæÆöG2„$ÅTU$”åBç&VE÷FW‡B†Væ6öF–æsÒ'WFbÓ‚"’“²ÆövóÔ–ÖvRæ÷Vâ†&w2æÆövò’æ6öçfW'B‚%$t$"¢'EöÖæ–fW7CÖ§6öâæÆöG2„%EôÔä”dU5Bç&VE÷FW‡B†Væ6öF–æsÒ'WFbÓ‚"’¢7F—fFU÷6†&VEö'B†'EöÖæ–fW7B¢FW‡CÖÆöEöÖöGVÆR‚&×•÷v÷&ÆE÷FW‡EöVæv–æR"ÅDU…EôTät”äR¢÷WGWG3Õ·&VæFW%ööæR†âÆ&ÇVW&–çBÆÆövòÆ&w2æ÷WGWEöF—"Æ&w2æWf–FVæ6UöF—"ÇFW‡BÆ'EöÖæ–fW7B’f÷"â–â&w2çvW5Ð¢6öçF7CÖ&w2æ6öçF7E÷6†VWB÷"&w2æ÷WGWEöF—"ç&VçBöb'v÷&²Ö×’×v÷&ÆB×¶&w2çvW5³Ó£6GÒ×¶&w2çvW5²ÓÓ£6GÒÖ6öçF7Bçær ¢6öçF7Bç&VçBæÖ¶F—"‡&VçG3ÕG'VRÆW†—7Eöö³ÕG'VR“²6öçF7E÷6†VWB†÷WGWG2Æ6öçF7B¢–b&w2çFc ¢6öç6öÆ–FFU÷Fb†÷WGWG2Æ&w2çFb¢7VÖÖ'“×²'66÷R#¥·ç7FVÒf÷"–â÷WGWG5ÒÂ&vVæW&FVB#¦ÆVâ†÷WGWG2’Â&f–ÆVB#£Â&6öçF7E÷6†VWB#§7G"†6öçF7B’Â'Fb#§7G"†&w2çFb’–b&w2çFbVÇ6RæöæWÐ¢†&w2æWf–FVæ6UöF—"ò&×’×v÷&ÆB×–Æ÷B×7VÖÖ'’æ§6öâ"’çw&—FU÷FW‡B†§6öâæGV×2‡7VÖÖ'’Æ–æFVçCÓ"’²%Æâ"ÆVæ6öF–æsÒ'WFbÓ‚"¢&–çB†§6öâæGV×2‡7VÖÖ'’Æ–æFVçCÓ"’“²&WGW&â   ¦–bõöæÖUõóÓÒ%õöÖ–åõò# ¢&—6R7—7FVÔW†—B†Ö–â‚’ 