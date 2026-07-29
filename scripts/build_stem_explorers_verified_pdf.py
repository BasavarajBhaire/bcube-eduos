#!/usr/bin/env python3
"""Build the verified STEM Explorers LKG learning-page PDF."""
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from PIL import Image
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas


FIRST_PAGE = 8
LAST_PAGE = 43
PAGE_SIZE = (2480, 3508)
PDF_PAGE_COUNT = LAST_PAGE - FIRST_PAGE + 1


def page_paths(pages_dir: Path) -> list[Path]:
    expected = [
        pages_dir / f"ST-LKG-V4-P{number:03d}.png"
        for number in range(FIRST_PAGE, LAST_PAGE + 1)
    ]
    missing = [str(path) for path in expected if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing verified page PNGs: {missing}")

    unexpected = sorted(
        path.name
        for path in pages_dir.glob("ST-LKG-V4-P*.png")
        if path not in expected
    )
    if unexpected:
        raise ValueError(f"Unexpected page PNGs in verified directory: {unexpected}")

    for path in expected:
        with Image.open(path) as image:
            if image.size != PAGE_SIZE:
                raise ValueError(f"Unexpected page size for {path}: {image.size}")
    return expected


def build_pdf(pages: list[Path], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    page_width, page_height = A4
    with tempfile.TemporaryDirectory(prefix="stem-explorers-pdf-") as temporary:
        temporary_dir = Path(temporary)
        document = pdf_canvas.Canvas(str(output), pagesize=A4, pageCompression=1)
        document.setTitle("STEM Explorers - LKG")
        document.setAuthor("BCube Future Academy")
        document.setSubject("Verified STEM Explorers learning pages P008-P043")
        for index, png in enumerate(pages, 1):
            with Image.open(png) as source:
                jpeg = temporary_dir / f"page-{index:03d}.jpg"
                source.convert("RGB").save(
                    jpeg,
                    "JPEG",
                    quality=94,
                    subsampling=0,
                    optimize=False,
                    dpi=(300, 300),
                )
            document.drawImage(
                str(jpeg),
                0,
                0,
                width=page_width,
                height=page_height,
                preserveAspectRatio=False,
                mask="auto",
            )
            document.showPage()
        document.save()

    page_count = len(PdfReader(str(output)).pages)
    if page_count != PDF_PAGE_COUNT:
        raise ValueError(f"Expected {PDF_PAGE_COUNT} PDF pages, found {page_count}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    pages = page_paths(args.pages_dir.resolve())
    build_pdf(pages, args.output.resolve())
    print(f"Built {len(pages)} pages: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
