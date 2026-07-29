#!/usr/bin/env python3
"""Build the corrected 44-page Early Maths Adventures LKG book.

The verified source pack omitted physical pages P008 and P009 and placed the
following P009-P027 artwork one physical page early. This builder creates the
two missing curriculum pages, shifts that affected run to P010-P028, corrects
its printed footers, excludes the duplicate second Directions page, preserves
P029-P044, and creates a print-ready PDF and ZIP.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas


WIDTH = 2480
HEIGHT = 3508
DPI = 300

BACKGROUND = "#FFFCF7"
NAVY = "#123F70"
PURPLE = "#7540A1"
BLUE = "#1974C4"
LIGHT_BLUE = "#E8F4FF"
GOLD = "#FFF1B8"
GOLD_LINE = "#E1A914"
LAVENDER = "#F4EEFF"
LAVENDER_LINE = "#8455C4"
GREEN = "#EFF9EA"
GREEN_LINE = "#5F9D50"
TEXT = "#303642"
MUTED = "#657286"
WHITE = "#FFFFFF"

FONT_REGULAR = [
    Path("C:/Windows/Fonts/arial.ttf"),
    Path("C:/Windows/Fonts/segoeui.ttf"),
]
FONT_BOLD = [
    Path("C:/Windows/Fonts/arialbd.ttf"),
    Path("C:/Windows/Fonts/seguisb.ttf"),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for candidate in FONT_BOLD if bold else FONT_REGULAR:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    raise FileNotFoundError("A deterministic Windows font is required")


def wrap(draw: ImageDraw.ImageDraw, value: str, active: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in value.split():
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=active) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fitted_text(
    draw: ImageDraw.ImageDraw,
    value: str,
    box: tuple[int, int, int, int] | list[int],
    *,
    max_size: int,
    min_size: int = 20,
    colour: str = NAVY,
    bold: bool = False,
    max_lines: int = 2,
    align: str = "center",
) -> int:
    x0, y0, x1, y1 = box
    for size in range(max_size, min_size - 1, -2):
        active = font(size, bold)
        lines = wrap(draw, value, active, x1 - x0)
        line_height = round(size * 1.22)
        if len(lines) <= max_lines and len(lines) * line_height <= y1 - y0:
            y = y0 + ((y1 - y0) - len(lines) * line_height) // 2
            for line in lines:
                line_width = draw.textlength(line, font=active)
                x = x0 if align == "left" else x0 + ((x1 - x0) - line_width) / 2
                draw.text((x, y), line, font=active, fill=colour)
                y += line_height
            return size
    raise ValueError(f"Text does not fit: {value!r}")


def panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int] | list[int],
    *,
    fill: str = WHITE,
    outline: str = LAVENDER_LINE,
    width: int = 3,
    radius: int = 24,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def paste_logo(canvas: Image.Image, logo_path: Path) -> None:
    logo = Image.open(logo_path).convert("RGBA")
    logo.thumbnail((230, 230), Image.Resampling.LANCZOS)
    x = 145 + (230 - logo.width) // 2
    y = 30 + (230 - logo.height) // 2
    canvas.paste(logo, (x, y), logo)


def header(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    logo_path: Path,
    *,
    title: str,
    objective: str,
    instruction: str,
) -> None:
    paste_logo(canvas, logo_path)
    fitted_text(draw, "Early Maths Adventures", [620, 40, 2050, 105], max_size=42, min_size=34, colour=PURPLE, bold=True, max_lines=1)
    fitted_text(draw, title, [430, 105, 2260, 255], max_size=62, min_size=46, colour=NAVY, bold=True, max_lines=2)
    panel(draw, [150, 300, 2330, 420], fill=LIGHT_BLUE, outline=BLUE, width=3, radius=26)
    fitted_text(draw, f"Learning goal: {objective}", [210, 315, 2270, 405], max_size=38, min_size=30, colour=NAVY, bold=True, max_lines=2)
    panel(draw, [150, 450, 2330, 580], fill=GOLD, outline=GOLD_LINE, width=3, radius=26)
    fitted_text(draw, instruction, [210, 465, 2270, 565], max_size=40, min_size=30, colour=TEXT, bold=True, max_lines=2)


def teacher_footer(draw: ImageDraw.ImageDraw, cue: str, page_number: int) -> None:
    panel(draw, [150, 3060, 2330, 3265], fill=GREEN, outline=GREEN_LINE, width=3, radius=26)
    fitted_text(draw, "TEACHER CUE", [210, 3105, 505, 3215], max_size=31, min_size=27, colour=NAVY, bold=True, max_lines=1)
    fitted_text(draw, cue, [560, 3090, 2250, 3235], max_size=30, min_size=25, colour=TEXT, bold=False, max_lines=2, align="left")
    fitted_text(draw, str(page_number), [2200, 3280, 2370, 3390], max_size=43, min_size=36, colour=MUTED, bold=True, max_lines=1)


def completed_example_label(draw: ImageDraw.ImageDraw, box: list[int]) -> None:
    panel(draw, box, fill=LAVENDER, outline=LAVENDER_LINE, width=3, radius=22)
    fitted_text(draw, "COMPLETED EXAMPLE", [box[0] + 20, box[1] + 15, box[0] + 325, box[3] - 15], max_size=26, min_size=22, colour=NAVY, bold=True, max_lines=2)


def draw_ten_frame(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int] | list[int],
    count: int,
    *,
    dot_colour: str = "#2E86DE",
    outline: str = "#69758A",
    blank_fill: str = WHITE,
) -> None:
    x0, y0, x1, y1 = box
    gap = 8
    cell_w = (x1 - x0 - gap) / 5
    cell_h = (y1 - y0 - gap) / 2
    radius = int(min(cell_w, cell_h) * 0.29)
    for index in range(10):
        row, col = divmod(index, 5)
        cx = round(x0 + col * cell_w + cell_w / 2)
        cy = round(y0 + row * cell_h + cell_h / 2)
        draw.rounded_rectangle(
            [round(x0 + col * cell_w), round(y0 + row * cell_h), round(x0 + (col + 1) * cell_w), round(y0 + (row + 1) * cell_h)],
            radius=8,
            fill="#F9FBFD",
            outline="#B6C4D4",
            width=2,
        )
        fill = dot_colour if index < count else blank_fill
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=fill, outline=outline, width=2)


DOT_COLOURS = ["#E94B4B", "#2E86DE", "#2DBD65", "#F5A623", "#8E5BC9"]


def draw_dot_group(draw: ImageDraw.ImageDraw, box: list[int], count: int) -> None:
    x0, y0, x1, y1 = box
    columns = 5
    rows = 2
    cell_w = (x1 - x0) / columns
    cell_h = (y1 - y0) / rows
    radius = round(min(cell_w, cell_h) * 0.27)
    for index in range(count):
        row, col = divmod(index, columns)
        cx = round(x0 + cell_w * (col + 0.5))
        cy = round(y0 + cell_h * (row + 0.5))
        colour = DOT_COLOURS[index % len(DOT_COLOURS)]
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=colour, outline=NAVY, width=2)


def render_p008(logo_path: Path, output: Path) -> None:
    canvas = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    header(
        canvas,
        draw,
        logo_path,
        title="Numbers 1-10 Review",
        objective="Recognise numbers 1-10.",
        instruction="Point to each number. Count its dots. Then write the missing numbers.",
    )

    completed_example_label(draw, [180, 625, 2300, 785])
    panel(draw, [545, 648, 695, 765], fill=WHITE, outline=BLUE, width=3, radius=18)
    fitted_text(draw, "3", [560, 655, 680, 758], max_size=58, min_size=48, colour=NAVY, bold=True, max_lines=1)
    draw.line([740, 705, 900, 705], fill=PURPLE, width=5)
    draw.polygon([(900, 705), (872, 685), (872, 725)], fill=PURPLE)
    draw_dot_group(draw, [970, 654, 1250, 756], 3)
    fitted_text(draw, "3 dots", [1320, 655, 1600, 755], max_size=31, min_size=25, colour=NAVY, bold=True, max_lines=1)

    grid_left, grid_top, grid_right, grid_bottom = 160, 825, 2320, 2585
    gap_x, gap_y = 24, 26
    card_w = (grid_right - grid_left - 4 * gap_x) // 5
    card_h = (grid_bottom - grid_top - gap_y) // 2
    for number in range(1, 11):
        row, col = divmod(number - 1, 5)
        left = grid_left + col * (card_w + gap_x)
        top = grid_top + row * (card_h + gap_y)
        box = [left, top, left + card_w, top + card_h]
        fill = "#F8FBFF" if row == 0 else "#FFF9EE"
        panel(draw, box, fill=fill, outline=LAVENDER_LINE, width=3, radius=24)
        fitted_text(draw, str(number), [left + 30, top + 24, left + card_w - 30, top + 205], max_size=78, min_size=64, colour=NAVY, bold=True, max_lines=1)
        draw.line([left + 45, top + 215, left + card_w - 45, top + 215], fill="#D9D2E8", width=3)
        draw_dot_group(draw, [left + 35, top + 270, left + card_w - 35, top + card_h - 65], number)

    panel(draw, [160, 2630, 2320, 3020], fill="#FCFAFF", outline=LAVENDER_LINE, width=3, radius=24)
    fitted_text(draw, "Write the missing numbers.", [220, 2652, 2260, 2732], max_size=32, min_size=28, colour=NAVY, bold=True, max_lines=1)
    values: list[int | None] = [1, 2, None, 4, 5, None, 7, 8, None, 10]
    gap = 16
    box_w = 180
    total = len(values) * box_w + (len(values) - 1) * gap
    start = 160 + (2160 - total) // 2
    for index, value in enumerate(values):
        left = start + index * (box_w + gap)
        box = [left, 2785, left + box_w, 2960]
        panel(draw, box, fill=GOLD if value is None else WHITE, outline=GOLD_LINE if value is None else BLUE, width=3, radius=18)
        if value is not None:
            fitted_text(draw, str(value), [left + 12, 2800, left + box_w - 12, 2947], max_size=53, min_size=45, colour=NAVY, bold=True, max_lines=1)

    teacher_footer(draw, "Point to each numeral, count the dots together, then let the child complete the three blank boxes.", 7)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, "PNG", dpi=(DPI, DPI), compress_level=6)


def render_p009(logo_path: Path, output: Path) -> None:
    canvas = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    header(
        canvas,
        draw,
        logo_path,
        title="Numbers 11-20",
        objective="Recognise numbers 11-20.",
        instruction="Count 10 dots, then count on using the extra dots. Say each number.",
    )

    completed_example_label(draw, [180, 625, 2300, 785])
    draw_ten_frame(draw, [545, 654, 870, 756], 10, dot_colour="#2E86DE")
    fitted_text(draw, "+", [885, 660, 965, 750], max_size=48, min_size=40, colour=PURPLE, bold=True, max_lines=1)
    draw_ten_frame(draw, [980, 654, 1305, 756], 1, dot_colour="#E94B4B")
    fitted_text(draw, "= 11", [1360, 650, 1660, 760], max_size=52, min_size=44, colour=NAVY, bold=True, max_lines=1)

    grid_left, grid_top, grid_right, grid_bottom = 160, 825, 2320, 2700
    gap_x, gap_y = 26, 22
    card_w = (grid_right - grid_left - gap_x) // 2
    card_h = (grid_bottom - grid_top - 4 * gap_y) // 5
    for offset, number in enumerate(range(11, 21)):
        row, col = divmod(offset, 2)
        left = grid_left + col * (card_w + gap_x)
        top = grid_top + row * (card_h + gap_y)
        box = [left, top, left + card_w, top + card_h]
        fill = "#F8FBFF" if col == 0 else "#FFF9EE"
        panel(draw, box, fill=fill, outline=LAVENDER_LINE, width=3, radius=22)
        fitted_text(draw, str(number), [left + 18, top + 32, left + 190, top + card_h - 32], max_size=61, min_size=52, colour=NAVY, bold=True, max_lines=1)
        draw_ten_frame(draw, [left + 210, top + 68, left + 565, top + card_h - 68], 10, dot_colour="#2E86DE")
        draw_ten_frame(draw, [left + 615, top + 68, left + 970, top + card_h - 68], number - 10, dot_colour="#E94B4B")

    panel(draw, [160, 2745, 2320, 3020], fill="#FCFAFF", outline=LAVENDER_LINE, width=3, radius=24)
    fitted_text(draw, "Write the missing numbers.", [210, 2760, 740, 2835], max_size=29, min_size=25, colour=NAVY, bold=True, max_lines=1, align="left")
    sequence: list[int | None] = [11, None, 13, 14, None, 16, 17, None, 19, 20]
    gap = 16
    box_w = 174
    total = len(sequence) * box_w + (len(sequence) - 1) * gap
    start = 160 + (2160 - total) // 2
    for index, value in enumerate(sequence):
        left = start + index * (box_w + gap)
        box = [left, 2850, left + box_w, 2992]
        panel(draw, box, fill=GOLD if value is None else WHITE, outline=GOLD_LINE if value is None else BLUE, width=3, radius=17)
        if value is not None:
            fitted_text(draw, str(value), [left + 10, 2862, left + box_w - 10, 2980], max_size=43, min_size=36, colour=NAVY, bold=True, max_lines=1)

    teacher_footer(draw, "Point to the full ten-frame first. Count on from ten using the red dots, then complete the missing-number row.", 8)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, "PNG", dpi=(DPI, DPI), compress_level=6)


def patch_printed_footer(source: Path, destination: Path, printed_number: int) -> None:
    image = Image.open(source).convert("RGB")
    if image.size != (WIDTH, HEIGHT):
        raise ValueError(f"Unexpected page dimensions for {source}: {image.size}")
    draw = ImageDraw.Draw(image)
    sample = image.getpixel((2380, 3400))
    # The printed number sits below the teacher panel. Keep the replacement
    # patch below y=3268 so the panel border/fill is never damaged.
    draw.rectangle([2160, 3268, 2415, 3425], fill=sample)
    fitted_text(draw, str(printed_number), [2200, 3280, 2370, 3390], max_size=43, min_size=36, colour=MUTED, bold=True, max_lines=1)
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, "PNG", dpi=(DPI, DPI), compress_level=6)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_source(source_dir: Path) -> None:
    required = [source_dir / f"EM-LKG-V4-P{number:03d}.png" for number in list(range(1, 8)) + list(range(9, 45))]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing source PNGs: {missing}")


def build_png_pack(source_dir: Path, output_dir: Path, logo_path: Path) -> list[dict[str, object]]:
    validate_source(source_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    mapping: list[dict[str, object]] = []

    for number in range(1, 8):
        source = source_dir / f"EM-LKG-V4-P{number:03d}.png"
        destination = output_dir / source.name
        shutil.copy2(source, destination)
        mapping.append({"destination": destination.name, "source": source.name, "action": "preserved"})

    p008 = output_dir / "EM-LKG-V4-P008.png"
    p009 = output_dir / "EM-LKG-V4-P009.png"
    render_p008(logo_path, p008)
    render_p009(logo_path, p009)
    mapping.extend([
        {"destination": p008.name, "source": None, "action": "created", "title": "Numbers 1-10 Review", "printed": 7},
        {"destination": p009.name, "source": None, "action": "created", "title": "Numbers 11-20", "printed": 8},
    ])

    for destination_number in range(10, 29):
        source_number = destination_number - 1
        source = source_dir / f"EM-LKG-V4-P{source_number:03d}.png"
        destination = output_dir / f"EM-LKG-V4-P{destination_number:03d}.png"
        patch_printed_footer(source, destination, destination_number - 1)
        mapping.append({
            "destination": destination.name,
            "source": source.name,
            "action": "shifted_and_footer_corrected",
            "printed": destination_number - 1,
        })

    for number in range(29, 45):
        source = source_dir / f"EM-LKG-V4-P{number:03d}.png"
        destination = output_dir / source.name
        shutil.copy2(source, destination)
        mapping.append({"destination": destination.name, "source": source.name, "action": "preserved"})

    pages = sorted(output_dir.glob("EM-LKG-V4-P*.png"))
    expected = [f"EM-LKG-V4-P{number:03d}.png" for number in range(1, 45)]
    actual = [path.name for path in pages]
    if actual != expected:
        raise ValueError(f"Corrected pack does not contain the exact P001-P044 sequence: {actual}")
    for path in pages:
        with Image.open(path) as image:
            if image.size != (WIDTH, HEIGHT):
                raise ValueError(f"Wrong canvas size for {path}: {image.size}")
    return mapping


def build_zip(png_dir: Path, output_zip: Path) -> None:
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=4) as archive:
        for path in sorted(png_dir.glob("EM-LKG-V4-P*.png")):
            archive.write(path, arcname=path.name)


def build_pdf(png_dir: Path, output_pdf: Path) -> None:
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    page_width, page_height = A4
    with tempfile.TemporaryDirectory(prefix="early-maths-pdf-") as temporary:
        temporary_dir = Path(temporary)
        document = pdf_canvas.Canvas(str(output_pdf), pagesize=A4, pageCompression=1)
        document.setTitle("Early Maths Adventures - LKG")
        document.setAuthor("BCube Future Academy")
        document.setSubject("Early Maths Adventures complete 44-page book")
        for index, png in enumerate(sorted(png_dir.glob("EM-LKG-V4-P*.png")), 1):
            with Image.open(png) as source:
                rgb = source.convert("RGB")
                jpeg = temporary_dir / f"page-{index:03d}.jpg"
                rgb.save(jpeg, "JPEG", quality=94, subsampling=0, optimize=False, dpi=(DPI, DPI))
            document.drawImage(str(jpeg), 0, 0, width=page_width, height=page_height, preserveAspectRatio=False, mask="auto")
            document.showPage()
        document.save()
    reader = PdfReader(str(output_pdf))
    if len(reader.pages) != 44:
        raise ValueError(f"Expected 44 PDF pages, found {len(reader.pages)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--logo", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--output-pdf", type=Path, required=True)
    parser.add_argument("--output-zip", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    if not args.logo.is_file():
        raise FileNotFoundError(args.logo)
    mapping = build_png_pack(args.source_dir, args.output_dir, args.logo)
    build_zip(args.output_dir, args.output_zip)
    build_pdf(args.output_dir, args.output_pdf)

    report = {
        "book": "Early Maths Adventures",
        "level": "LKG",
        "physical_pages": 44,
        "created_pages": {
            "EM-LKG-V4-P008": {"title": "Numbers 1-10 Review", "printed_page": 7},
            "EM-LKG-V4-P009": {"title": "Numbers 11-20", "printed_page": 8},
        },
        "sequence_correction": {
            "shifted": "source P009-P027 -> corrected P010-P028",
            "excluded_duplicate": "source P028 (second Directions page)",
            "preserved": "P001-P007 and P029-P044",
        },
        "outputs": {
            "png_directory": str(args.output_dir),
            "zip": str(args.output_zip),
            "zip_sha256": sha256(args.output_zip),
            "pdf": str(args.output_pdf),
            "pdf_sha256": sha256(args.output_pdf),
        },
        "mapping": mapping,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "BUILT", "pages": 44, "pdf": str(args.output_pdf), "zip": str(args.output_zip)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
