#!/usr/bin/env python3
"""Compose deterministic BCube certificate and back-cover pages."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
CANVAS = (2480, 3508)
BOLD = [Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'), Path('C:/Windows/Fonts/arialbd.ttf')]
REGULAR = [Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'), Path('C:/Windows/Fonts/arial.ttf')]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError(f'{path} must contain an object')
    return value


def resolve(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for candidate in (BOLD if bold else REGULAR):
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    raise FileNotFoundError('No deterministic font found')


def sha256(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes())
    return digest.hexdigest()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, active_font: ImageFont.FreeTypeFont, max_width: int) -> str:
    paragraphs = str(text).splitlines() or ['']
    wrapped: list[str] = []
    for paragraph in paragraphs:
        words = paragraph.split()
        if not words:
            wrapped.append('')
            continue
        line = words[0]
        for word in words[1:]:
            candidate = f'{line} {word}'
            bounds = draw.textbbox((0, 0), candidate, font=active_font)
            if bounds[2] - bounds[0] <= max_width:
                line = candidate
            else:
                wrapped.append(line)
                line = word
        wrapped.append(line)
    return '\n'.join(wrapped)


def fit_text(draw: ImageDraw.ImageDraw, text: str, box: tuple[int, int, int, int], max_size: int,
             colour: str, *, bold: bool = False, min_size: int = 14) -> None:
    x0, y0, x1, y1 = box
    max_width = x1 - x0
    max_height = y1 - y0
    last_wrapped = str(text)
    last_font = font(min_size, bold)
    last_bounds = draw.multiline_textbbox((0, 0), last_wrapped, font=last_font, spacing=8, align='center')
    for size in range(max_size, min_size - 1, -2):
        active = font(size, bold)
        spacing = max(6, size // 5)
        wrapped = wrap_text(draw, text, active, max_width)
        bounds = draw.multiline_textbbox((0, 0), wrapped, font=active, spacing=spacing, align='center')
        w, h = bounds[2] - bounds[0], bounds[3] - bounds[1]
        last_wrapped, last_font, last_bounds = wrapped, active, bounds
        if w <= max_width and h <= max_height:
            draw.multiline_text((x0 + (max_width - w) / 2, y0 + (max_height - h) / 2), wrapped,
                                font=active, fill=colour, spacing=spacing, align='center')
            return
    w = min(max_width, last_bounds[2] - last_bounds[0])
    h = min(max_height, last_bounds[3] - last_bounds[1])
    draw.multiline_text((x0 + (max_width - w) / 2, y0 + (max_height - h) / 2), last_wrapped,
                        font=last_font, fill=colour, spacing=6, align='center')


def paste_contain(canvas: Image.Image, path: Path, box: tuple[int, int, int, int]) -> dict[str, Any]:
    image = Image.open(path).convert('RGBA')
    image.thumbnail((box[2] - box[0], box[3] - box[1]), Image.Resampling.LANCZOS)
    x = box[0] + (box[2] - box[0] - image.width) // 2
    y = box[1] + (box[3] - box[1] - image.height) // 2
    canvas.paste(image, (x, y), image)
    return {'path': str(path), 'source_size': list(Image.open(path).size), 'rendered_bounds': [x, y, x + image.width, y + image.height]}


def compose_certificate(data: dict[str, Any]) -> tuple[Image.Image, dict[str, Any]]:
    canvas = Image.new('RGB', CANVAS, '#FFFDF7')
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((120, 120, 2360, 3388), radius=60, outline='#5B2C83', width=18)
    draw.rounded_rectangle((160, 160, 2320, 3348), radius=48, outline='#F2B705', width=8)
    logo = paste_contain(canvas, resolve(data['official_logo_path']), (180, 190, 700, 600))
    star = paste_contain(canvas, resolve(data['official_star_path']), (1800, 2050, 2290, 2540))
    fit_text(draw, 'CERTIFICATE OF ACHIEVEMENT', (360, 560, 2120, 850), 112, '#5B2C83', bold=True)
    fit_text(draw, data['book_title'], (400, 850, 2080, 1090), 80, '#E35B25', bold=True)
    fit_text(draw, 'This certificate is proudly presented to', (480, 1120, 2000, 1300), 50, '#333333')
    draw.line((480, 1540, 2000, 1540), fill='#5B2C83', width=5)
    fit_text(draw, data.get('student_name_placeholder', 'Student Name'), (520, 1360, 1960, 1530), 72, '#5B2C83', bold=True)
    message = data.get('achievement_message', 'for completing the learning journey with curiosity, creativity, communication, confidence and collaboration.')
    fit_text(draw, message, (420, 1620, 2060, 2030), 55, '#333333')
    fit_text(draw, f"{data['level']} • {data['age']}", (720, 2080, 1760, 2220), 46, '#5B2C83', bold=True)
    draw.line((420, 2940, 1020, 2940), fill='#666666', width=3)
    draw.line((1460, 2940, 2060, 2940), fill='#666666', width=3)
    fit_text(draw, 'Teacher / Facilitator', (420, 2950, 1020, 3070), 34, '#555555')
    fit_text(draw, 'Date', (1460, 2950, 2060, 3070), 34, '#555555')
    fit_text(draw, 'BCube Future Skills Learning Series™', (500, 3180, 1980, 3290), 34, '#5B2C83', bold=True)
    return canvas, {'page_type': 'certificate', 'logo': logo, 'star': star}


def compose_back_cover(data: dict[str, Any]) -> tuple[Image.Image, dict[str, Any]]:
    canvas = Image.new('RGB', CANVAS, '#F7F2FC')
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((90, 90, 2390, 3418), radius=64, fill='#FFFFFF', outline='#5B2C83', width=16)
    logo = paste_contain(canvas, resolve(data['official_logo_path']), (760, 210, 1720, 870))
    fit_text(draw, data['book_title'], (360, 880, 2120, 1180), 104, '#5B2C83', bold=True)
    fit_text(draw, data.get('tagline', 'Learn • Explore • Grow'), (520, 1190, 1960, 1370), 50, '#E35B25', bold=True)
    star = paste_contain(canvas, resolve(data['official_star_path']), (890, 1480, 1590, 2180))
    fit_text(draw, data.get('message', 'Thank you for learning with BCube Future Academy.'), (430, 2250, 2050, 2520), 56, '#333333')
    fit_text(draw, 'Creativity • Communication • Curiosity • Confidence • Collaboration', (300, 2700, 2180, 2890), 42, '#5B2C83', bold=True)
    fit_text(draw, 'bcubefutureacademy.in\ninfo@bcubefutureacademy.in', (500, 3020, 1980, 3240), 38, '#444444')
    return canvas, {'page_type': 'back_cover', 'logo': logo, 'star': star}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--evidence-output', type=Path, required=True)
    args = parser.parse_args()
    data = load(args.data)
    required = ['page_id', 'page_type', 'book_title', 'level', 'age', 'official_logo_path', 'official_star_path']
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f'Missing completion page data: {missing}')
    if data['page_type'] == 'certificate':
        image, evidence = compose_certificate(data)
    elif data['page_type'] == 'back_cover':
        image, evidence = compose_back_cover(data)
    else:
        raise ValueError(f"Unsupported page_type: {data['page_type']}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output, 'PNG', dpi=(300, 300))
    evidence.update({'page_id': data['page_id'], 'canvas': {'width': CANVAS[0], 'height': CANVAS[1], 'dpi': 300}, 'artifact_sha256': sha256(args.output)})
    args.evidence_output.parent.mkdir(parents=True, exist_ok=True)
    args.evidence_output.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'COMPOSED', 'artifact': str(args.output), 'evidence': str(args.evidence_output)}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
