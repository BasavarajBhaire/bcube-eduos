"""Build the Nursery Communication Champions P006 validation page.

Typography is composed deterministically. The illustration remains text-free;
the mascot board wording is always added here so future builds cannot regress
to an empty board or the old "My name" label.
"""

from pathlib import Path
import os

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets/nursery/communication-champions/P006"
OUT = ROOT / "output/nursery/communication-champions/validation/P001-P010"
W, H = 2480, 3508
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BLUE = "#123D7A"


def font(size):
    return ImageFont.truetype(BOLD, size)


def centred(draw, text, centre_x, y, face, fill=BLUE):
    box = draw.textbbox((0, 0), text, font=face)
    draw.text((centre_x - (box[2] - box[0]) / 2, y), text, font=face, fill=fill)


def dotted_line(draw, x1, x2, y, fill="#6FA6D9", width=6, dash=22, gap=16):
    for x in range(x1, x2, dash + gap):
        draw.line((x, y, min(x + dash, x2), y), fill=fill, width=width)


def build():
    page = Image.open(ASSETS / "illustration.jpg").convert("RGB").resize(
        (W, H), Image.Resampling.LANCZOS
    )
    draw = ImageDraw.Draw(page)

    logo_source = Image.open(ASSETS / "bcube-academy-logo.jpg").convert("RGBA")
    white = Image.new("RGBA", logo_source.size, "white")
    white.alpha_composite(logo_source)
    logo_source = white.convert("RGB")
    logo_source.thumbnail((560, 430), Image.Resampling.LANCZOS)
    logo_panel = Image.new("RGB", (720, 470), "white")
    logo_panel.paste(
        logo_source,
        ((720 - logo_source.width) // 2, (470 - logo_source.height) // 2),
    )
    page.paste(logo_panel, (20, 15))

    draw.rounded_rectangle((730, 60, 2390, 255), radius=34, fill="white")
    centred(draw, "My Name", 1600, 85, font(96))
    centred(draw, "What is your name?", 1240, 385, font(56))

    # Locked teaching model: Star introduces itself before the child responds.
    centred(draw, "I am Star", 1740, 1540, font(54))

    # Clear legacy guide marks baked into the validation illustration while
    # preserving the surrounding green activity-panel border.
    draw.rectangle((115, 2195, 2365, 3075), fill="white")

    draw.text((180, 2210), "My name is", font=font(62), fill=BLUE)
    draw.line((610, 2278, 2180, 2278), fill=BLUE, width=7)

    draw.text((190, 2390), "Trace my name.", font=font(43), fill="#3D6F95")
    dotted_line(draw, 300, 2180, 2535)
    dotted_line(draw, 300, 2180, 2655)

    draw.text((190, 2750), "Write my name.", font=font(43), fill="#3D6F95")
    draw.line((300, 2900, 2180, 2900), fill="#6FA6D9", width=7)
    draw.line((300, 3040, 2180, 3040), fill="#6FA6D9", width=7)

    draw.ellipse((2210, 3260, 2375, 3425), fill="white", outline="#F2B400", width=8)
    centred(draw, "6", 2292, 3300, font(64))

    OUT.mkdir(parents=True, exist_ok=True)
    destination = OUT / "CC-NURSERY-V3-P006.png"
    temporary = destination.with_suffix(".tmp.png")
    page.save(temporary, "PNG", dpi=(300, 300))
    with Image.open(temporary) as check:
        check.load()
        if check.size != (W, H):
            raise ValueError(f"Unexpected output size: {check.size}")
    os.replace(temporary, destination)
    print(destination)


if __name__ == "__main__":
    build()
