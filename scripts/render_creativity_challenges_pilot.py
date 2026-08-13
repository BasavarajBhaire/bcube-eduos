#!/usr/bin/env python3
"""Render the curriculum-first Creativity Challenges LKG validation waves."""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "curriculum/creativity-challenges/lkg/curriculum-first-p008-p024-v1.json"
TEXT_ENGINE = ROOT / "bcube-publishing-sdk/composer/compose_learning_page_v2.py"
WIDTH, HEIGHT = 2480, 3508
NAVY = "#123F72"
PURPLE = "#7E57C2"
SOFT_PURPLE = "#A077E8"
BLUE = "#E8F4FF"
GOLD = "#FFF4C6"
GREEN = "#F0FAED"
INK = "#31353A"
PILOT = tuple(range(8, 33))


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


def fitted(text, draw, value, box, *, size=36, minimum=24, colour=NAVY, bold=False, lines=1, align="center"):
    text.fitted_text(draw, value, box, max_size=size, min_size=minimum, colour=colour, bold=bold, max_lines=lines, align=align)


def header(canvas, draw, page, logo, text):
    logo_image = logo.copy().convert("RGBA")
    logo_image.thumbnail((300, 220), Image.Resampling.LANCZOS)
    canvas.paste(logo_image, (105 + (300 - logo_image.width) // 2, 35 + (220 - logo_image.height) // 2), logo_image)
    fitted(text, draw, "Creativity Challenges", [470, 45, 2320, 145], size=43, minimum=34, colour=PURPLE, bold=True)
    fitted(text, draw, page["title"], [470, 140, 2320, 275], size=69, minimum=45, bold=True, lines=2)
    panel(draw, [150, 305, 2330, 445], fill=BLUE, outline="#1768B3", width=3)
    fitted(text, draw, "Learning goal: " + page["objective"], [190, 318, 2290, 432], size=46, minimum=31, bold=True, lines=2)
    panel(draw, [150, 490, 2330, 650], fill=GOLD, outline="#E1A81C", width=3)
    fitted(text, draw, page["instruction"], [190, 505, 2290, 635], size=49, minimum=30, colour=INK, bold=True, lines=2)


def model_shell(draw, text):
    panel(draw, [170, 700, 2310, 900], fill="#F6F1FF", outline=SOFT_PURPLE, width=3)
    panel(draw, [195, 720, 535, 880], fill="#E7D9FA", outline=SOFT_PURPLE, width=2, radius=18)
    fitted(text, draw, "COMPLETED\nEXAMPLE", [220, 737, 510, 862], size=35, minimum=27, bold=True, lines=2)
    return 575, 720, 2275, 880


def arrow(draw, x0, y, x1):
    draw.line([x0, y, x1, y], fill=PURPLE, width=7)
    draw.polygon([(x1, y), (x1 - 42, y - 27), (x1 - 42, y + 27)], fill=PURPLE)


def completed_model(draw, number, text):
    x0, y0, x1, y1 = model_shell(draw, text)
    cy = (y0 + y1) // 2
    if number == 8:
        draw.arc([x0 + 25, cy - 55, x0 + 260, cy + 55], 190, 350, fill=NAVY, width=7)
        arrow(draw, x0 + 310, cy, x0 + 500)
        points = [(x0 + 585, cy + 25), (x0 + 650, cy - 25), (x0 + 715, cy + 25), (x0 + 780, cy - 25), (x0 + 845, cy + 15)]
        draw.line(points, fill="#55A94B", width=38, joint="curve")
        draw.ellipse([x0 + 825, cy - 15, x0 + 895, cy + 55], fill="#73C85E", outline=NAVY, width=3)
        draw.ellipse([x0 + 872, cy + 2, x0 + 884, cy + 14], fill=NAVY)
        message = "A curved line can become a snake."
    elif number == 9:
        draw.ellipse([x0 + 45, cy - 55, x0 + 155, cy + 55], outline=NAVY, width=6)
        arrow(draw, x0 + 215, cy, x0 + 405)
        draw.ellipse([x0 + 500, cy - 55, x0 + 610, cy + 55], fill="#F05A47", outline=NAVY, width=5)
        draw.line([x0 + 555, cy - 52, x0 + 555, cy + 52], fill=NAVY, width=4)
        draw.ellipse([x0 + 535, cy - 16, x0 + 547, cy - 4], fill=NAVY)
        draw.ellipse([x0 + 569, cy - 16, x0 + 581, cy - 4], fill=NAVY)
        draw.ellipse([x0 + 610, cy - 20, x0 + 642, cy + 20], fill=NAVY, outline=NAVY)
        for sx, sy in ((520, -34), (588, -35), (523, 27), (586, 27)):
            draw.ellipse([x0 + sx, cy + sy, x0 + sx + 13, cy + sy + 13], fill=NAVY)
        message = "A circle can become a ladybird."
    elif number == 10:
        draw.arc([x0 + 35, cy - 65, x0 + 155, cy + 55], 90, 270, fill=NAVY, width=6)
        draw.line([x0 + 95, cy - 65, x0 + 95, cy + 55], fill="#B7B7B7", width=3)
        arrow(draw, x0 + 210, cy, x0 + 400)
        draw.ellipse([x0 + 490, cy - 60, x0 + 610, cy + 60], outline=NAVY, width=6)
        for angle in range(0, 360, 45):
            radians = math.radians(angle)
            draw.line([x0 + 550 + math.cos(radians) * 72, cy + math.sin(radians) * 72,
                       x0 + 550 + math.cos(radians) * 105, cy + math.sin(radians) * 105], fill="#F0A91B", width=7)
        message = "Use the clue to finish the sun."
    elif number == 11:
        draw.ellipse([x0 + 35, cy - 58, x0 + 155, cy + 58], outline=NAVY, width=6)
        arrow(draw, x0 + 215, cy, x0 + 405)
        colours = ("#F05A47", "#F7C843", "#4EA3F1", "#66B95A")
        draw.pieslice([x0 + 490, cy - 60, x0 + 610, cy + 60], 0, 90, fill=colours[0], outline=NAVY, width=3)
        draw.pieslice([x0 + 490, cy - 60, x0 + 610, cy + 60], 90, 180, fill=colours[1], outline=NAVY, width=3)
        draw.pieslice([x0 + 490, cy - 60, x0 + 610, cy + 60], 180, 270, fill=colours[2], outline=NAVY, width=3)
        draw.pieslice([x0 + 490, cy - 60, x0 + 610, cy + 60], 270, 360, fill=colours[3], outline=NAVY, width=3)
        message = "One shape can hold several colours."
    elif number == 12:
        for index, colour in enumerate(("#F05A47", "#4EA3F1", "#F05A47", "#4EA3F1")):
            draw.ellipse([x0 + 35 + index * 92, cy - 36, x0 + 103 + index * 92, cy + 32], fill=colour, outline=NAVY, width=3)
        arrow(draw, x0 + 430, cy, x0 + 610)
        fitted(text, draw, "red, blue, red, blue", [x0 + 660, cy - 45, x0 + 1080, cy + 45], size=32, minimum=24, bold=True)
        message = "Repeat a small unit to make a pattern."
    elif number == 13:
        draw.ellipse([x0 + 35, cy - 62, x0 + 165, cy + 62], outline=NAVY, width=5)
        arrow(draw, x0 + 220, cy, x0 + 405)
        draw.ellipse([x0 + 490, cy - 62, x0 + 620, cy + 62], outline=NAVY, width=5)
        draw.ellipse([x0 + 525, cy - 24, x0 + 545, cy - 4], fill=NAVY)
        draw.ellipse([x0 + 570, cy - 24, x0 + 590, cy - 4], fill=NAVY)
        draw.arc([x0 + 530, cy - 2, x0 + 585, cy + 42], 10, 170, fill=NAVY, width=5)
        message = "Small face details can show a feeling."
    elif number == 14:
        draw.ellipse([x0 + 35, cy - 48, x0 + 180, cy + 48], outline=NAVY, width=5)
        arrow(draw, x0 + 230, cy, x0 + 415)
        draw.ellipse([x0 + 500, cy - 48, x0 + 645, cy + 48], outline=NAVY, width=5)
        draw.ellipse([x0 + 500, cy - 88, x0 + 545, cy - 35], outline=NAVY, width=4)
        draw.ellipse([x0 + 600, cy - 88, x0 + 645, cy - 35], outline=NAVY, width=4)
        for px in (515, 625):
            draw.line([x0 + px, cy + 40, x0 + px - 10, cy + 85], fill=NAVY, width=5)
        message = "A simple body shape can become an animal."
    elif number == 15:
        draw.line([x0 + 95, cy + 62, x0 + 95, cy - 25], fill="#4E9D55", width=7)
        draw.ellipse([x0 + 58, cy - 65, x0 + 132, cy + 8], outline=NAVY, width=4)
        arrow(draw, x0 + 210, cy, x0 + 395)
        for angle in range(0, 360, 60):
            radians = math.radians(angle)
            px, py = x0 + 555 + math.cos(radians) * 55, cy + math.sin(radians) * 55
            draw.ellipse([px - 38, py - 38, px + 38, py + 38], outline=NAVY, width=4)
        draw.ellipse([x0 + 520, cy - 35, x0 + 590, cy + 35], outline=NAVY, width=4)
        draw.line([x0 + 555, cy + 70, x0 + 555, cy + 110], fill="#4E9D55", width=7)
        message = "Change petals and leaves to invent a plant."
    elif number == 16:
        draw.ellipse([x0 + 45, cy - 55, x0 + 155, cy + 55], outline=NAVY, width=5)
        arrow(draw, x0 + 215, cy, x0 + 400)
        draw.ellipse([x0 + 490, cy - 55, x0 + 600, cy + 55], outline=NAVY, width=5)
        draw.polygon([(x0 + 505, cy - 45), (x0 + 520, cy - 100), (x0 + 548, cy - 50)], outline=NAVY, width=4)
        draw.ellipse([x0 + 520, cy - 18, x0 + 538, cy], fill=NAVY)
        draw.ellipse([x0 + 560, cy - 18, x0 + 578, cy], fill=NAVY)
        draw.arc([x0 + 532, cy + 5, x0 + 570, cy + 38], 5, 175, fill=NAVY, width=4)
        message = "Combine features to create a fantasy friend."
    elif number == 17:
        centres = (x0 + 105, x0 + 360, x0 + 615)
        for index, (cx, label) in enumerate(zip(centres, ("FIRST", "NEXT", "LAST"))):
            panel(draw, [cx - 85, cy - 68, cx + 85, cy + 68], fill="#FFFFFF", outline=PURPLE, width=3, radius=12)
            if index == 0:
                draw.ellipse([cx - 22, cy - 18, cx + 22, cy + 12], fill="#8B5A2B", outline=NAVY, width=2)
            elif index == 1:
                draw.line([cx, cy + 18, cx, cy - 18], fill="#4E9D55", width=6)
                draw.ellipse([cx - 28, cy - 25, cx, cy + 2], fill="#73C85E", outline=NAVY, width=2)
                draw.ellipse([cx, cy - 25, cx + 28, cy + 2], fill="#73C85E", outline=NAVY, width=2)
            else:
                draw.line([cx, cy + 25, cx, cy - 8], fill="#4E9D55", width=6)
                for angle in range(0, 360, 72):
                    radians = math.radians(angle)
                    px, py = cx + math.cos(radians) * 27, cy - 17 + math.sin(radians) * 27
                    draw.ellipse([px - 15, py - 15, px + 15, py + 15], fill="#F6C445", outline=NAVY, width=2)
                draw.ellipse([cx - 14, cy - 31, cx + 14, cy - 3], fill="#8B5A2B", outline=NAVY, width=2)
            fitted(text, draw, label, [cx - 75, cy + 31, cx + 75, cy + 60], size=18, minimum=15, bold=True)
            if index < 2:
                arrow(draw, cx + 92, cy, cx + 145)
        message = "A seed grows: first, next and last."
    elif number == 18:
        for index, colour in enumerate(("#F05A47", "#F7C843", "#4EA3F1")):
            left = x0 + 35 + index * 105
            draw.polygon([(left + 40, cy - 45), (left, cy + 40), (left + 85, cy + 40)], fill=colour, outline=NAVY)
        arrow(draw, x0 + 390, cy, x0 + 555)
        draw.ellipse([x0 + 625, cy - 48, x0 + 755, cy + 48], fill="#4EA3F1", outline=NAVY, width=4)
        draw.polygon([(x0 + 625, cy), (x0 + 565, cy - 52), (x0 + 565, cy + 52)], fill="#F7C843", outline=NAVY)
        draw.ellipse([x0 + 715, cy - 16, x0 + 729, cy - 2], fill=NAVY)
        draw.polygon([(x0 + 690, cy + 45), (x0 + 720, cy + 78), (x0 + 742, cy + 39)], fill="#F05A47", outline=NAVY)
        message = "Arrange shapes first, then glue your collage."
    elif number == 19:
        draw.rectangle([x0 + 35, cy - 45, x0 + 150, cy + 45], outline=NAVY, width=5)
        draw.ellipse([x0 + 55, cy + 35, x0 + 85, cy + 65], outline=NAVY, width=4)
        draw.ellipse([x0 + 110, cy + 35, x0 + 140, cy + 65], outline=NAVY, width=4)
        arrow(draw, x0 + 215, cy, x0 + 400)
        draw.rectangle([x0 + 490, cy - 55, x0 + 620, cy + 45], outline=NAVY, width=5)
        draw.ellipse([x0 + 510, cy + 35, x0 + 545, cy + 70], outline=NAVY, width=4)
        draw.ellipse([x0 + 570, cy + 35, x0 + 605, cy + 70], outline=NAVY, width=4)
        draw.line([x0 + 555, cy - 55, x0 + 555, cy - 82], fill=NAVY, width=5)
        draw.ellipse([x0 + 542, cy - 98, x0 + 568, cy - 72], fill="#F05A47", outline=NAVY, width=3)
        message = "Add a special feature to invent a toy."
    elif number == 20:
        draw.ellipse([x0 + 35, cy - 42, x0 + 115, cy + 38], outline=NAVY, width=4)
        draw.rectangle([x0 + 140, cy - 42, x0 + 220, cy + 38], outline=NAVY, width=4)
        draw.polygon([(x0 + 280, cy - 48), (x0 + 235, cy + 38), (x0 + 325, cy + 38)], outline=NAVY, width=4)
        arrow(draw, x0 + 365, cy, x0 + 520)
        draw.rectangle([x0 + 590, cy - 30, x0 + 760, cy + 65], outline=NAVY, width=5)
        draw.polygon([(x0 + 675, cy - 96), (x0 + 575, cy - 28), (x0 + 775, cy - 28)], outline=NAVY, width=5)
        message = "Combine shapes to build a picture."
    elif number == 21:
        draw.rectangle([x0 + 35, cy - 38, x0 + 165, cy + 42], outline=NAVY, width=5)
        arrow(draw, x0 + 220, cy, x0 + 400)
        draw.rectangle([x0 + 490, cy - 38, x0 + 650, cy + 42], outline=NAVY, width=5)
        draw.ellipse([x0 + 505, cy + 30, x0 + 550, cy + 75], outline=NAVY, width=4)
        draw.ellipse([x0 + 590, cy + 30, x0 + 635, cy + 75], outline=NAVY, width=4)
        draw.polygon([(x0 + 650, cy - 35), (x0 + 720, cy), (x0 + 650, cy + 35)], outline=NAVY, width=4)
        message = "Add the parts a vehicle needs to move."
    elif number == 22:
        draw.rectangle([x0 + 35, cy - 45, x0 + 165, cy + 75], outline=NAVY, width=5)
        draw.polygon([(x0 + 100, cy - 115), (x0 + 15, cy - 42), (x0 + 185, cy - 42)], outline=NAVY, width=5)
        arrow(draw, x0 + 220, cy, x0 + 400)
        draw.rectangle([x0 + 490, cy - 45, x0 + 650, cy + 75], outline=NAVY, width=5)
        draw.polygon([(x0 + 570, cy - 95), (x0 + 465, cy - 42), (x0 + 675, cy - 42)], outline=NAVY, width=5)
        draw.ellipse([x0 + 525, cy - 5, x0 + 565, cy + 35], outline=NAVY, width=3)
        draw.arc([x0 + 610, cy + 15, x0 + 730, cy + 100], 180, 360, fill="#55A94B", width=6)
        message = "Add useful and surprising house features."
    elif number == 23:
        draw.ellipse([x0 + 35, cy - 50, x0 + 145, cy + 50], fill="#B7E69F", outline="#55A94B", width=6)
        draw.line([x0 + 145, cy, x0 + 235, cy - 35], fill="#8B5A2B", width=8)
        arrow(draw, x0 + 285, cy, x0 + 440)
        draw.ellipse([x0 + 515, cy - 58, x0 + 665, cy + 58], fill="#B7E69F", outline="#55A94B", width=5)
        draw.polygon([(x0 + 665, cy), (x0 + 735, cy - 55), (x0 + 735, cy + 55)], fill="#C99655", outline="#8B5A2B", width=5)
        draw.ellipse([x0 + 540, cy - 18, x0 + 554, cy - 4], fill=NAVY)
        message = "Arrange natural pieces to make new art."
    elif number == 24:
        draw.ellipse([x0 + 35, cy - 55, x0 + 145, cy + 55], outline=NAVY, width=5)
        arrow(draw, x0 + 205, cy, x0 + 390)
        draw.ellipse([x0 + 480, cy - 55, x0 + 590, cy + 55], outline=NAVY, width=5)
        for px in range(x0 + 500, x0 + 580, 20):
            draw.ellipse([px, cy - 10, px + 8, cy - 2], fill=NAVY)
            draw.ellipse([px, cy + 18, px + 8, cy + 26], fill=NAVY)
        message = "Use different marks to show texture."
    elif number == 25:
        for px, py, colour in ((75, -28, "#F05A47"), (112, 18, "#F7C843"), (150, -20, "#4EA3F1")):
            draw.ellipse([x0 + px - 20, cy + py - 20, x0 + px + 20, cy + py + 20], fill=colour, outline=NAVY, width=2)
        arrow(draw, x0 + 220, cy, x0 + 405)
        draw.line([x0 + 545, cy + 55, x0 + 545, cy - 15], fill="#55A94B", width=7)
        for angle, colour in zip(range(0, 360, 72), ("#F05A47", "#F7C843", "#4EA3F1", "#A077E8", "#F29B38")):
            radians = math.ra×Í¸ÖÚ$z{-®éÜj×“Â##SÂ“ƒÒÂ6—¦SÓ3ÂÖ–æ–×VÓÓ#2Â&öÆCÕG'VRÂÆ–vãÒ&ÆVgB"¢G&ræVÆÆ—6R…³S#Â#3SÂ“cÂ#csÒÂf–ÆÃÒ"4S„c„db"Â÷WFÆ–æSÒ"3“”C”c""Âv–GFƒÓB¢G&ræÆ–æR…³#ƒÂ#c#ÂS#Â#c#ÒÂf–ÆÃÒ"3s4#3T""Âv–GFƒÓ¢G&ræÆ–æR…³“cÂ#c#Â##Â#c#ÒÂf–ÆÃÒ"3s4#3T""Âv–GFƒÓ¢f—GFVB‡FW‡BÂG&rÂ$E$rD„R%$”DtRõdU"D„RTDDÄR"Â³sSÂ##3Âs3Â#3ÒÂ6—¦SÓ#bÂÖ–æ–×VÓÓ#Â6öÆ÷W#Ò"3ƒdD#‚"Â&öÆCÕG'VR¢æVÂ†G&rÂ³sÂ#ƒ3Â#3Â3sÒÂf–ÆÃÒ"4cdcdb"¢f—GFVB‡FW‡BÂG&rÂ#26†V6²–÷W"–FV¢"Â³##Â#ƒsÂsÂ#“CÒÂ6—¦SÓ#’ÂÖ–æ–×VÓÓ#"Â&öÆCÕG'VRÂÆ–vãÒ&ÆVgB"¢f÷"–æFW‚ÂÆ&VÂ–âVçVÖW&FR‚‚'7FæG2W"Â'v–FRVæ÷Vv‚"Â&¶VW26"G'’"’“ ¢ÆVgBÒs²–æFW‚¢S ¢G&rç&÷VæFVE÷&V7FævÆR…¶ÆVgBÂ#ƒsÂÆVgB³SÂ#“#ÒÂ&F—W3ÓrÂ÷WFÆ–æSÕU%ÄRÂv–GFƒÓ2¢f—GFVB‡FW‡BÂG&rÂÆ&VÂÂ¶ÆVgB³cRÂ#ƒSRÂÆVgB³CSRÂ#“CÒÂ6—¦SÓ#2ÂÖ–æ–×VÓÓ‚Â&öÆCÕG'VRÂÆ–vãÒ&ÆVgB"  ¦FVb&VæFW%÷#’†6çf2ÂG&rÂFW‡B“ ¢æVÂ†G&rÂ³sÂ“SÂ#3ÂCÒÂf–ÆÃÒ"4cdcdb"¢f—GFVB‡FW‡BÂG&rÂ#6†ö÷6RöæR&ö&ÆVÒf÷"–÷W"–çfVçF–öââ"Â³##Â“ƒÂ##SÂSÒÂ6—¦SÓ3ÂÖ–æ–×VÓÓ#2Â&öÆCÕG'VRÂÆ–vãÒ&ÆVgB"¢6†ö–6W2Ò‚‚$4%%’Ôå’Dõ•2"Â&&r"’Â‚%$T4‚4ôÔUD„”är„”t‚"Â'&V6‚"’Â‚$´TUE$”ä²4ôôÂ"Â&6ööÂ"’¢f÷"–æFW‚Â†Æ&VÂÂ¶–æB’–âVçVÖW&FR†6†ö–6W2“ ¢ÆVgBÒ#3²–æFW‚¢s ¢æVÂ†G&rÂ¶ÆVgBÂƒÂÆVgB³c#Â3CÒÂf–ÆÃÒ'v†—FR"Â÷WFÆ–æSÒ"44$#tc2"Âv–GFƒÓ2¢G&ræVÆÆ—6R…¶ÆVgB³#RÂÂÆVgB³sRÂSÒÂ÷WFÆ–æSÕU%ÄRÂv–GFƒÓ2¢–b¶–æBÓÒ&&r# ¢G&rç&V7FævÆR…¶ÆVgB³#ÂCÂÆVgB³#3Â#cÒÂ÷WFÆ–æSÔäe’Âv–GFƒÓB¢G&ræ&2…¶ÆVgB³CÂÂÆVgB³#ÂsÒÂƒÂ3cÂf–ÆÃÔäe’Âv–GFƒÓB¢VÆ–b¶–æBÓÒ'&V6‚# ¢G&ræÆ–æR…¶ÆVgB³cÂRÂÆVgB³cÂ#sÒÂf–ÆÃÔäe’Âv–GFƒÓ‚¢G&ræÆ–æR…¶ÆVgB³#Â#sÂÆVgB³#Â#sÒÂf–ÆÃÔäe’Âv–GFƒÓ‚¢G&ræVÆÆ—6R…¶ÆVgB³3RÂ“ÂÆVgB³ƒRÂCÒÂ÷WFÆ–æSÔäe’Âv–GFƒÓB¢VÇ6S ¢G&rç&V7FævÆR…¶ÆVgB³#RÂÂÆVgB³#RÂ#sÒÂ÷WFÆ–æSÔäe’Âv–GFƒÓB¢G&ræÆ–æR…¶ÆVgB³cRÂƒÂÆVgB³cRÂ#ÒÂf–ÆÃÔäe’Âv–GFƒÓB¢f—GFVB‡FW‡BÂG&rÂÆ&VÂÂ¶ÆVgB³#SÂÂÆVgB³S“Â3ÒÂ6—¦SÓ#BÂÖ–æ–×VÓÓ‚Â&öÆCÕG'VRÂÆ–æW3Ó2¢æVÂ†G&rÂ³sÂCSÂ#3Â#csÒÂf–ÆÃÒ'v†—FR"¢f—GFVB‡FW‡BÂG&rÂ#"G&r–÷W"–çfVçF–öââFB'&÷w2Fò6†÷rGvòW6VgVÂ'G2â"Â³##ÂCƒÂ##SÂSSÒÂ6—¦SÓ3ÂÖ–æ–×VÓÓ#2Â&öÆCÕG'VRÂÆ–vãÒ&ÆVgB"¢æVÂ†G&rÂ³3ÂcÂ#ƒÂ#SCÒÂf–ÆÃÒ"4dddDc‚"Â÷WFÆ–æSÒ"44$#tc2"Âv–GFƒÓ2¢f—GFVB‡FW‡BÂG&rÂ$E$rD„R”ådTåD”ôâ„U$R"Â³sSÂ#3Âs3Â#ÒÂ6—¦SÓ3ÂÖ–æ–×VÓÓ#2Â6öÆ÷W#Ò"43#d3‚"Â&öÆCÕG'VR¢G&ræÆ–æR…³3SÂscÂsÂscÒÂf–ÆÃÕU%ÄRÂv–GFƒÓ2¢'&÷r†G&rÂsÂscÂƒ3¢G&ræÆ–æR…³cSÂ#3#Â#SÂ#3#ÒÂf–ÆÃÕU%ÄRÂv–GFƒÓ2¢'&÷r†G&rÂc3Â#3#ÂS¢æVÂ†G&rÂ³sÂ#s#Â#3Â3sÒÂf–ÆÃÒ"4cdcdb"¢f—GFVB‡FW‡BÂG&rÂ#2æÖRæBW‡Æ–â–÷W"–çfVçF–öââ"Â³##Â#sSÂÂ#ƒ#ÒÂ6—¦SÓ3ÂÖ–æ–×VÓÓ#2Â&öÆCÕG'VRÂÆ–vãÒ&ÆVgB"¢f—GFVB‡FW‡BÂG&rÂ$—B—26ÆÆVB"Â³#SÂ#ƒsÂcSÂ#“3ÒÂ6—¦SÓ#RÂÖ–æ–×VÓÓ’Â&öÆCÕG'VRÂÆ–vãÒ&ÆVgB"¢G&ræÆ–æR…³cCÂ#“#Â#SÂ#“#ÒÂf–ÆÃÕU%ÄRÂv–GFƒÓ2¢f—GFVB‡FW‡BÂG&rÂ$—B†VÇ2'’"Â³#SÂ#“sÂcSÂ33ÒÂ6—¦SÓ#RÂÖ–æ–×VÓÓ’Â&öÆCÕG'VRÂÆ–vãÒ&ÆVgB"¢G&ræÆ–æR…³cCÂ3#Â#SÂ3#ÒÂf–ÆÃÕU%ÄRÂv–GFƒÓ2  ¦FVb&VæFW%÷3†6çf2ÂG&rÂFW‡B“ ¢&÷†W2Ò…³sÂ“SÂ#RÂ“ÒÂ³#sRÂ“SÂ#3Â“ÒÂ³sÂ“SÂ#RÂ#“#ÒÂ³#sRÂ“SÂ#3Â#“#Ò¢F—FÆW2Ò‚$4³¢v†B—2F†R&ö&ÆVÓò"Â$”Ôt”äS¢6†ö÷6R†öÆFW"–FVâ"Â$Ô´S¢G&r–÷W"FW6–vââ"Â$”Õ$õdS¢FW7BæB6†ævR—Bâ"¢f÷"–æFW‚Â†&÷‚ÂF—FÆR’–âVçVÖW&FR‡¦—†&÷†W2ÂF—FÆW2’“ ¢6&Eö†VFW"†G&rÂFW‡BÂ–æFW‚³ÂF—FÆRÂ&÷‚¢–b–æFW‚ÓÒ ¢f÷"‚Â6öÆ÷W"–â‚ƒ3ƒÂ"4cTCr"’ÂƒSCÂ"3DT4c"’ÂƒsÂ"4ct3ƒC2"’“ ¢G&ræÆ–æR…·‚Â#cÂ‚³CÂ3ƒÒÂf–ÆÃÖ6öÆ÷W"Âv–GFƒÓ#"¢&ö×Eö&æB†G&rÂFW‡BÂ$7&–öç2&öÆÂv’æBvWBÖ—†VBWâ"Â³#SÂSÂ#RÂcÒ¢f—GFVB‡FW‡BÂG&rÂ$vööB†öÆFW"×W7B"Â³#SÂcsÂsÂs3ÒÂ6—¦SÓ#BÂÖ–æ–×VÓÓ‚Â&öÆCÕG'VRÂÆ–vãÒ&ÆVgB"¢G&ræÆ–æR…³cƒÂs#ÂÂs#ÒÂf–ÆÃÕU%ÄRÂv–GFƒÓ2¢VÆ–b–æFW‚ÓÒ ¢f÷"6†ö–6RÂ†¶–æBÂÆ&VÂ’–âVçVÖW&FR‚‚‚&7W"Â&7W"’Â‚&&÷‚"Â&&÷‚"’Â‚'&öÆÂ"Â'GV&R"’’“ ¢ÆVgBÒ3CR²6†ö–6R£3 ¢G&ræVÆÆ—6R…¶ÆVgBÂSÂÆVgB³CRÂ“UÒÂ÷WFÆ–æSÕU%ÄRÂv–GFƒÓ2¢–b¶–æBÓÒ&7W# ¢G&rçöÇ–vöâ…²†ÆVgB³sÂ#C’Â†ÆVgB³SRÂ#C’Â†ÆVgB³CÂC’Â†ÆVgB³ƒRÂC•ÒÂ÷WFÆ–æSÔäe’¢VÆ–b¶–æBÓÒ&&÷‚# ¢G&rç&V7FævÆR…¶ÆVgB³sÂ#CÂÆVgB³cÂCÒÂ÷WFÆ–æSÔäe’Âv–GFƒÓB¢VÇ6S ¢G&ræVÆÆ—6R…¶ÆVgB³cRÂ#cÂÆVgB³cRÂ3“ÒÂ÷WFÆ–æSÔäe’Âv–GFƒÓB¢f—GFVB‡FW‡BÂG&rÂÆ&VÂÂ¶ÆVgB³CRÂC3ÂÆVgB³“ÂC“ÒÂ6—¦SÓ#"ÂÖ–æ–×VÓÓrÂ&öÆCÕG'VR¢f—GFVB‡FW‡BÂG&rÂ$×’–FV6öÖ&–æW2"Â³3SÂcCÂƒÂsÒÂ6—¦SÓ#BÂÖ–æ–×VÓÓ‚Â&öÆCÕG'VRÂÆ–vãÒ&ÆVgB"¢G&ræÆ–æR…³ƒÂc“Â###Âc“ÒÂf–ÆÃÕU%ÄRÂv–GFƒÓ2¢VÆ–b–æFW‚ÓÒ# ¢æVÂ†G&rÂ³#cÂ#ÂÂ#sCÒÂf–ÆÃÒ"4dddDc‚"Â÷WFÆ–æSÒ"44$#tc2"Âv–GFƒÓ2¢f—GFVB‡FW‡BÂG&rÂ$E$r”õU"5$”ôâ„ôÄDU""Â³3ƒÂ#3sÂ““Â#CcÒÂ6—¦SÓ#rÂÖ–æ–×VÓÓ#Â6öÆ÷W#Ò"4$$T32"Â&öÆCÕG'VR¢f—GFVB‡FW‡BÂG&rÂ%6†÷rv†W&RF†R7&–öç2vòâ"Â³3#Â#sƒÂSÂ#ƒCÒÂ6—¦SÓ#2ÂÖ–æ–×VÓÓ‚Â&öÆCÕG'VR¢VÇ6S ¢f—GFVB‡FW‡BÂG&rÂ$gFW"FW7F–ærÂF–6²v†Bv÷&·3¢"Â³3SÂ#Â###Â#sÒÂ6—¦SÓ#RÂÖ–æ–×VÓÓ’Â&öÆCÕG'VRÂÆ–vãÒ&ÆVgB"¢f÷"&÷rÂÆ&VÂ–âVçVÖW&FR‚‚&†öÆG26—‚7&–öç2"Â'7FæG2v—F†÷WBfÆÆ–ær"Â&V7’Fò6''’"’“ ¢F÷Ò##²&÷r£ ¢G&rç&÷VæFVE÷&V7FævÆR…³3sÂF÷ÂC#ÂF÷³SÒÂ&F—W3ÓrÂ÷WFÆ–æSÕU%ÄRÂv–GFƒÓ2¢f—GFVB‡FW‡BÂG&rÂÆ&VÂÂ³CCÂF÷Ó‚Â#“ÂF÷³cÒÂ6—¦SÓ#2ÂÖ–æ–×VÓÓ‚Â&öÆCÕG'VRÂÆ–vãÒ&ÆVgB"¢&ö×Eö&æB†G&rÂFW‡BÂ$G&röæR–×&÷fVÖVçBâ"Â³3sÂ#ScÂ#“Â#cCÒ¢æVÂ†G&rÂ³3sÂ#csÂ#“Â#ƒCÒÂf–ÆÃÒ'v†—FR"Â÷WFÆ–æSÒ"44$#tc2"Âv–GFƒÓ2¢f—GFVB‡FW‡BÂG&rÂ%FVÆÂ'FæW#¢’6†ævVBõõõõõõõõõò&V6W6Rõõõõõõõõõòâ"Â³3Â#“ƒÂ#ƒÂ3cÒÂ6—¦SÓ#’ÂÖ–æ–×VÓÓ#"Â&öÆCÕG'VR  ¦FVbVÖö¦•öf6R†G&rÂ7‚Â7’ÂÖööBÂ&F—W3ÓSR“ ¢G&ræVÆÆ—6R…¶7‚×&F—W2Â7’×&F—W2Â7‚·&F—W2Â7’·&F—W5ÒÂf–ÆÃÒ"4ct3ƒC2"Â÷WFÆ–æSÔäe’Âv–GFƒÓ2¢G&ræVÆÆ—6R…¶7‚×&F—W2¢ã3‚Â7’×&F—W2¢ã#‚Â7‚×&F—W2¢ã‚Â7’×&F—W2¢ã…ÒÂf–ÆÃÔäe’¢G&ræVÆÆ—6R…¶7‚·&F—W2¢ã‚Â7’×&F—W2¢ã#‚Â7‚·&F—W2¢ã3‚Â7’×&F—W2¢ã…ÒÂf–ÆÃÔäe’¢–bÖööB–â‚&†’"Â&W†6—FVB"“ ¢G&ræ&2…¶7‚×&F—W2¢ã3‚Â7’×&F—W2¢ãRÂ7‚·&F—W2¢ã3‚Â7’·&F—W2¢ãC…ÒÂRÂsRÂf–ÆÃÔäe’Âv–GFƒÓB¢VÆ–bÖööBÓÒ'7W'&—6VB# ¢G&ræVÆÆ—6R…¶7‚×&F—W2¢ãrÂ7’·&F—W2¢ãRÂ7‚·&F—W2¢ãrÂ7’·&F—W2¢ã3…ÒÂ÷WFÆ–æSÔäe’Âv–GFƒÓB¢VÆ–bÖööBÓÒ'6B# ¢G&ræ&2…¶7‚×&F—W2¢ã3‚Â7’·&F—W2¢ã‚Â7‚·&F—W2¢ã3‚Â7’·&F—W2¢ãc%ÒÂ“Â3SÂf–ÆÃÔäe’Âv–GFƒÓB¢VÆ–bÖööBÓÒ&æw'’# ¢G&ræÆ–æR…¶7‚×&F—W2¢ãC2Â7’×&F—W2¢ã3RÂ7‚×&F—W2¢ã2Â7’×&F—W2¢ã…ÒÂf–ÆÃÔäe’Âv–GFƒÓB¢G&ræÆ–æR…¶7‚·&F—W2¢ã2Â7’×&F—W2¢ã‚Â7‚·&F—W2¢ãC2Â7’×&F—W2¢ã3UÒÂf–ÆÃÔäe’Âv–GFƒÓB¢G&ræÆ–æR…¶7‚×&F—W2¢ã#‚Â7’·&F—W2¢ã3RÂ7‚·&F—W2¢ã#‚Â7’·&F—W2¢ã3UÒÂf–ÆÃÔäe’Âv–GFƒÓB¢VÇ6S ¢G&ræ&2…¶7‚×&F—W2¢ã2Â7’·&F—W2¢ãRÂ7‚·&F—W2¢ã2Â7’·&F—W2¢ã3…ÒÂÂsÂf–ÆÃÔäe’Âv–GFƒÓ2  ¦FVb&VæFW%÷3†6çf2ÂG&rÂFW‡B“ ¢æVÂ†G&rÂ³sÂ“SÂ#3Â3#ÒÂf–ÆÃÒ"4cdcdb"¢f—GFVB‡FW‡BÂG&rÂ#6†ö÷6RF‡&VRfVVÆ–æw2f÷"–÷W"7F÷'’â"Â³##Â“ƒÂ##SÂSÒÂ6—¦SÓ3ÂÖ–æ–×VÓÓ#2Â&öÆCÕG'VRÂÆ–vãÒ&ÆVgB"¢ÖööG2Ò‚&†’"Â'7W'&—6VB"Â'6B"Â&W†6—FVB"Â&æw'’"Â&6ÆÒ"¢f÷"–æFW‚ÂÖööB–âVçVÖW&FR†ÖööG2“ ¢7‚Ò3cR²–æFW‚£3CP¢VÖö¦•öf6R†G&rÂ7‚ÂSÂÖööBÂSR¢G&ræVÆÆ—6R…¶7‚ÓÂ#CÂ7‚ÓSbÂ#ƒEÒÂ÷WFÆ–æSÕU%ÄRÂv–GFƒÓ2¢f—GFVB‡FW‡BÂG&rÂÖööBÂ¶7‚ÓC"Â##‚Â7‚³#RÂ#“…ÒÂ6—¦SÓ#ÂÖ–æ–×VÓÓrÂ&öÆCÕG'VRÂÆ–vãÒ&ÆVgB"¢&÷†W2Ò…³sÂ3sÂƒcÂ#sÒÂ³ƒ“RÂ3sÂSƒRÂ#sÒÂ³c#Â3sÂ#3Â#sÒ¢f÷"–æFW‚Â†&÷‚ÂÆ&VÂ’–âVçVÖW&FR‡¦—†&÷†W2Â‚$d•%5B"Â$äU…B"Â$Ä5B"’’“ ¢6&Eö†VFW"†G&rÂFW‡BÂ–æFW‚³"ÂÆ&VÂÂ&÷‚¢f—GFVB‡FW‡BÂG&rÂ$G&röæR6†÷6VâVÖö¦’†W&Râ"Â¶&÷…³Ò³cRÂ&÷…³Ò³CRÂ&÷…³%ÒÓcRÂ&÷…³Ò³#UÒÂ6—¦SÓ#"ÂÖ–æ–×VÓÓrÂ6öÆ÷W#Ò"3cs3„"Â&öÆCÕG'VR¢G&ræVÆÆ—6R…²†&÷…³Ò¶&÷…³%Ò’òó"ÓƒRÂ&÷…³Ò³#3RÂ†&÷…³Ò¶&÷…³%Ò’òó"³ƒRÂ&÷…³Ò³CUÒÂ÷WFÆ–æSÒ"44$#tc2"Âv–GFƒÓB¢æVÂ†G&rÂ¶&÷…³Ò³SRÂ&÷…³Ò³CSRÂ&÷…³%ÒÓSRÂ&÷…³5ÒÓ3ÒÂf–ÆÃÒ"4dddDc‚"Â÷WFÆ–æSÒ"44$#tc2"Âv–GFƒÓ2¢f—GFVB‡FW‡BÂG&rÂ$E$rt„B„Tå2"Â¶&÷…³Ò³#Â&÷…³Ò³ƒÂ&÷…³%ÒÓ#Â&÷…³Ò³“ÒÂ6—¦SÓ#BÂÖ–æ–×VÓÓ‚Â6öÆ÷W#Ò"4#„T3"Â&öÆCÕG'VR¢æVÂ†G&rÂ³sÂ#sSÂ#3Â3sÒÂf–ÆÃÒ"4cdcdb"¢f—GFVB‡FW‡BÂG&rÂ#Rv—fR–÷W"7F÷'’F—FÆR"Â³##Â#sƒÂ“Â#ƒCUÒÂ6—¦SÓ#’ÂÖ–æ–×VÓÓ#"Â&öÆCÕG'VRÂÆ–vãÒ&ÆVgB"¢G&ræÆ–æR…³ƒƒÂ#ƒ3RÂ#ƒÂ#ƒ3UÒÂf–ÆÃÕU%ÄRÂv–GFƒÓ2¢f—GFVB‡FW‡BÂG&rÂ%FVÆÂ—BÆ÷VC¢f—'7BõõõõõõõõõòâæW‡BõõõõõõõõõòâÆ7Bõõõõõõõõõòâ"Â³#sÂ#“Â##Â3UÒÂ6—¦SÓ#rÂÖ–æ–×VÓÓ#Â&öÆCÕG'VRÂÆ–æW3Ó"  ¦FVbÖ÷fVÖVçE÷7–Ö&öÂ†G&rÂ¶–æBÂ7‚Â7’Â&F—W3ÓSR“ ¢6öÆ÷W'2Ò²&6Æ#¢"4cTCr"Â'7Fö×#¢"3DT4c"Â'F#¢"4ct3ƒC2"Â'GW&â#¢"3cd#“T"Â&§V×#¢"4stS‚'Ð¢G&ræVÆÆ—6R…¶7‚×&F—W2Â7’×&F—W2Â7‚·&F—W2Â7’·&F—W5ÒÂf–ÆÃÖ6öÆ÷W'5¶¶–æEÒÂ÷WFÆ–æSÔäe’Âv–GFƒÓ2¢f—GFVEöÆ&VÂÒ²&6Æ#¢$4Ä"Â'7Fö×#¢%5DôÕ"Â'F#¢%D"Â'GW&â#¢%EU$â"Â&§V×#¢$¥TÕ'Õ¶¶–æEÐ¢&WGW&âf—GFVEöÆ&VÀ  ¦FVb&VæFW%÷3"†6çf2ÂG&rÂFW‡B“ ¢f—GFVB‡FW‡BÂG&rÂ#6’V6‚6&BÂF†VâW&f÷&Ò—G2f÷W"&VG2–â÷&FW"â"Â³“Â“3Â##“Â““UÒÂ6—¦SÓ3ÂÖ–æ–×VÓÓ#2Â&öÆCÕG'VRÂÆ–vãÒ&ÆVgB"¢6&G2Ò…³sÂ#Â#3Â3sÒÂ³sÂC#Â#3ÂssÒÂ³sÂƒ#Â#3Â#sÒ¢GFW&ç2Ò‚‚&6Æ"Â&6Æ"Â'7Fö×"Â'7Fö×"’Â‚'F"Â'GW&â"Â'F"Â'GW&â"’Â‚&§V×"Â&6Æ"Â&§V×"Â&6Æ"’¢f÷"&÷rÂ†&÷‚ÂGFW&â’–âVçVÖW&FR‡¦—†6&G2ÂGFW&ç2’“ ¢æVÂ†G&rÂ&÷‚Âf–ÆÃÒ'v†—FR"¢f—GFVB‡FW‡BÂG&rÂb%$…•D„Ò·&÷r³Ò"Â³#Â&÷…³Ò³3RÂS#Â&÷…³Ò³ÒÂ6—¦SÓ#RÂÖ–æ–×VÓÓ’Â&öÆCÕG'VRÂÆ–vãÒ&ÆVgB"¢f÷"–æFW‚Â¶–æB–âVçVÖW&FR‡GFW&â“ ¢7‚Òsc²–æFW‚£3s ¢Æ&VÂÒÖ÷fVÖVçE÷7–Ö&öÂ†G&rÂ¶–æBÂ7‚Â&÷…³Ò³sRÂc"¢f—GFVB‡FW‡BÂG&rÂÆ&VÂÂ¶7‚ÓƒÂ&÷…³Ò³#CRÂ7‚³ƒÂ&÷…³Ò³3UÒÂ6—¦SÓ#ÂÖ–æ–×VÓÓbÂ&öÆCÕG'VR¢æVÂ†G&rÂ³sÂ###Â#3Â#ƒsÒÂf–ÆÃÒ"4cdcdb"¢f—GFVB‡FW‡BÂG&rÂ#"7&VFR–÷W"÷vâf÷W"Ö&VBÖ÷fVÖVçBGFW&ââ"Â³##Â##SÂ##SÂ#3#ÒÂ6—¦SÓ3ÂÖ–æ–×VÓÓ#2Â&öÆCÕG'VRÂÆ–vãÒ&ÆVgB"¢f—GFVB‡FW‡BÂG&rÂ$6†ö÷6Rg&öÓ¢"Â³#CÂ#3ƒÂcÂ#CCÒÂ6—¦SÓ#BÂÖ–æ–×VÓÓ‚Â&öÆCÕG'VRÂÆ–vãÒ&ÆVgB"¢f÷"–æFW‚Â¶–æB–âVçVÖW&FR‚‚&6Æ"Â'7Fö×"Â'F"Â'GW&â"Â&§V×"’“ ¢7‚Òs²–æFW‚£3 ¢Æ&VÂÒÖ÷fVÖVçE÷7–Ö&öÂ†G&rÂ¶–æBÂ7‚Â#CÂC"¢f—GFVB‡FW‡BÂG&rÂÆ&VÂÂ¶7‚Óc"Â#CcRÂ7‚³c"Â#SÒÂ6—¦SÓrÂÖ–æ–×VÓÓBÂ&öÆCÕG'VR¢f÷"–æFW‚–â&ævRƒB“ ¢ÆVgBÒ3²–æFW‚£S ¢æVÂ†G&rÂ¶ÆVgBÂ#SƒÂÆVgB³3ƒÂ#s“UÒÂf–ÆÃÒ'v†—FR"Â÷WFÆ–æSÕU%ÄRÂv–GFƒÓB¢f—GFVB‡FW‡BÂG&rÂ7G"†–æFW‚³’Â¶ÆVgB³CÂ#c3ÂÆVgB³#CÂ#sCÒÂ6—¦SÓC‚ÂÖ–æ–×VÓÓ3bÂ6öÆ÷W#Ò"4#„T3"Â&öÆCÕG'VR¢æVÂ†G&rÂ³sÂ#“#Â#3Â3sÒÂf–ÆÃÒ'v†—FR"¢f—GFVB‡FW‡BÂG&rÂ#2'FæW"6†V6³¢"Â³##Â#“SÂcSÂ3#ÒÂ6—¦SÓ#rÂÖ–æ–×VÓÓ#Â&öÆCÕG'VRÂÆ–vãÒ&ÆVgB"¢f÷"–æFW‚ÂÆ&VÂ–âVçVÖW&FR‚‚$’¶WBF†R&VB"Â$×’'FæW"6÷–VB—B"’“ ¢ÆVgBÒs#²–æFW‚£cS ¢G&rç&÷VæFVE÷&V7FævÆR…¶ÆVgBÂ#“cÂÆVgB³C‚Â3…ÒÂ&F—W3ÓrÂ÷WFÆ–æSÕU%ÄRÂv–GFƒÓ2¢f—GFVB‡FW‡BÂG&rÂÆ&VÂÂ¶ÆVgB³cÂ#“CRÂÆVgB³cÂ3#UÒÂ6—¦SÓ#2ÂÖ–æ–×VÓÓ‚Â&öÆCÕG'VRÂÆ–vãÒ&ÆVgB"  ¥$TäDU$U%2Ò°¢ƒ¢&VæFW%÷‚Â“¢&VæFW%÷’Â¢&VæFW%÷Â¢&VæFW%÷Â#¢&VæFW%÷"À¢3¢&VæFW%÷2ÂC¢&VæFW%÷BÂS¢&VæFW%÷RÂc¢&VæFW%÷bÀ¢s¢&VæFW%÷rÂƒ¢&VæFW%÷‚Â“¢&VæFW%÷’Â#¢&VæFW%÷#À¢#¢&VæFW%÷#Â##¢&VæFW%÷#"Â#3¢&VæFW%÷#2Â#C¢&VæFW%÷#BÀ¢#S¢&VæFW%÷#RÂ#c¢&VæFW%÷#bÂ#s¢&VæFW%÷#rÂ#ƒ¢&VæFW%÷#‚À¢#“¢&VæFW%÷#’Â3¢&VæFW%÷3Â3¢&VæFW%÷3Â3#¢&VæFW%÷3"À§Ð  ¦FVb&VæFW%ööæR†çVÖ&W"Â&ÇVW&–çBÂÆövòÂ÷WGWEöF—#¢F‚ÂWf–FVæ6UöF—#¢F‚ÂFW‡B“ ¢vUö–BÒb$5"ÔÄ´rÕcBÕ¶çVÖ&W#£6GÒ ¢vRÒ&ÇVW&–çE²'vW2%Õ·vUö–EÐ¢6çf2Ò–ÖvRææWr‚%$t""Â…t”ED‚Â„T”t…B’Â"4ddd4cr"¢G&rÒ–ÖvTG&räG&r†6çf2¢†VFW"†6çf2ÂG&rÂvRÂÆövòÂFW‡B¢6ö×ÆWFVEöÖöFVÂ†G&rÂçVÖ&W"ÂFW‡B¢$TäDU$U%5¶çVÖ&W%Ò†6çf2ÂG&rÂFW‡B¢FV6†W%öfö÷FW"†G&rÂvRÂFW‡B¢÷WGWEöF—"æÖ¶F—"‡&VçG3ÕG'VRÂW†—7Eöö³ÕG'VR¢Wf–FVæ6UöF—"æÖ¶F—"‡&VçG3ÕG'VRÂW†—7Eöö³ÕG'VR¢÷WGWBÒ÷WGWEöF—"òb'·vUö–GÒçær ¢6çf2ç6fR†÷WGWBÂ%är"¢†Wf–FVæ6UöF—"òb'·vUö–GÒæ§6öâ"’çw&—FU÷FW‡B†§6öâæGV×2‡°¢'vUö–B#¢vUö–BÀ¢'7FGW2#¢%52"À¢&6ö×ÆWFVEöW†×ÆU÷f—6–&ÆR#¢G'VRÀ¢&–æFWVæFVçEöç7vW'5÷VæÖ&¶VB#¢G'VRÀ¢'&W7öç6U÷76U÷W'÷6VgVÂ#¢G'VRÀ¢&ö&¦V7Eö7&÷2#¢fÇ6RÀ¢'&VçE÷æVÂ#¢fÇ6RÀ¢'FV6†W%ö7VU÷vU÷7V6–f–2#¢G'VP¢ÒÂ–æFVçCÓ"’²%Æâ"ÂVæ6öF–æsÒ'WFbÓ‚"¢&WGW&â÷WGW@  ¦FVb6öçF7E÷6†VWB‡F‡2Â÷WGWB“ ¢F‡VÖ%÷rÒC ¢F‡VÖ%ö‚Ò&÷VæB‡F‡VÖ%÷r¢„T”t…Bòt”ED‚¢6†VWBÒ–ÖvRææWr‚%$t""Â‡F‡VÖ%÷r¢ÆVâ‡F‡2’ÂF‡VÖ%ö‚’Â'v†—FR"¢f÷"–æFW‚ÂF‚–âVçVÖW&FR‡F‡2“ ¢–ÖvRÒ–ÖvRæ÷Vâ‡F‚’æ6öçfW'B‚%$t""¢–ÖvRçF‡VÖ&æ–Â‚‡F‡VÖ%÷rÂF‡VÖ%ö‚’Â–ÖvRå&W6×Æ–æräÄä5¤õ2¢6†VWBç7FR†–ÖvRÂ†–æFW‚¢F‡VÖ%÷rÂ’¢6†VWBç6fR†÷WGWBÂ%är"  ¦FVbÖ–â‚“ ¢'6W"Ò&w'6Rä&wVÖVçE'6W"‚¢'6W"æFEö&wVÖVçB‚"ÒÖÆövò"ÂG—SÕF‚Â&WV—&VCÕG'VR¢'6W"æFEö&wVÖVçB‚"ÒÖ÷WGWBÖF—""ÂG—SÕF‚ÂFVfVÇCÕ$ôõBò'v÷&²Ö7&VF—f—G’Ö6†ÆÆVævW2×–Æ÷B"¢'6W"æFEö&wVÖVçB‚"ÒÖWf–FVæ6RÖF—""ÂG—SÕF‚ÂFVfVÇCÕ$ôõBò'v÷&²Ö7&VF—f—G’Ö6†ÆÆVævW2×–Æ÷BÖWf–FVæ6R"¢&w2Ò'6W"ç'6Uö&w2‚¢&ÇVW&–çBÒ§6öâæÆöG2„$ÅTU$”åBç&VE÷FW‡B†Væ6öF–æsÒ'WFbÓ‚"’¢ÆövòÒ–ÖvRæ÷Vâ†&w2æÆövò’æ6öçfW'B‚%$t$"¢FW‡BÒÆöEöÖöGVÆR‚&7&VF—f—G•ö6†ÆÆVævW5÷FW‡EöVæv–æR"ÂDU…EôTät”äR¢÷WGWG2Ò·&VæFW%ööæR†çVÖ&W"Â&ÇVW&–çBÂÆövòÂ&w2æ÷WGWEöF—"Â&w2æWf–FVæ6UöF—"ÂFW‡B’f÷"çVÖ&W"–â”ÄõEÐ¢6öçF7BÒ&w2æ÷WGWEöF—"ç&VçBò'v÷&²Ö7&VF—f—G’Ö6†ÆÆVævW2×–Æ÷BÖ6öçF7Bçær ¢6öçF7E÷6†VWB†÷WGWG2Â6öçF7B¢7VÖÖ'’Ò²'66÷R#¢·F‚ç7FVÒf÷"F‚–â÷WGWG5ÒÂ&vVæW&FVB#¢ÆVâ†÷WGWG2’Â&f–ÆVB#¢Â&6öçF7E÷6†VWB#¢7G"†6öçF7B—Ð¢†&w2æWf–FVæ6UöF—"ò&7&VF—f—G’×–Æ÷B×7VÖÖ'’æ§6öâ"’çw&—FU÷FW‡B†§6öâæGV×2‡7VÖÖ'’Â–æFVçCÓ"’²%Æâ"ÂVæ6öF–æsÒ'WFbÓ‚"¢&–çB†§6öâæGV×2‡7VÖÖ'’Â–æFVçCÓ"’¢&WGW&â   ¦–bõöæÖUõòÓÒ%õöÖ–åõò# ¢&—6R7—7FVÔW†—B†Ö–â‚’