"""Build 16 individual Nursery Communication Champions validation pages.

Output sequence follows FRONT_MATTER_AND_NUMBERING_POLICY.md:
cover (uncounted) plus reader pages 1–15.
"""

from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "output/nursery/communication-champions/validation/P001-P010"
ASSETS = ROOT / "assets/nursery/communication-champions"
NEW_ART = ASSETS / "cover-to-page-15"
LOGO = ASSETS / "P006/bcube-academy-logo.jpg"
OUT = ROOT / "output/nursery/communication-champions/validation/new-design-cover-to-page-15"
W, H = 2480, 3508
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BLUE = "#123D7A"


def ft(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REGULAR, size)


def centred(draw, text, cx, y, face, fill=BLUE):
    box = draw.textbbox((0, 0), text, font=face)
    draw.text((cx - (box[2] - box[0]) / 2, y), text, font=face, fill=fill)


def add_logo(page):
    source = Image.open(LOGO).convert("RGB")
    source.thumbnail((500, 405), Image.Resampling.LANCZOS)
    panel = Image.new("RGB", (600, 455), "white")
    panel.paste(source, ((600-source.width)//2, (455-source.height)//2))
    page.paste(panel, (20, 15))


def title(page, text, size=86):
    draw = ImageDraw.Draw(page)
    draw.rounded_rectangle((700, 45, 2395, 270), radius=38, fill="white")
    centred(draw, text, 1570, 80, ft(size, True))


def page_number(page, number):
    draw = ImageDraw.Draw(page)
    draw.ellipse((2200, 3250, 2385, 3435), fill="white", outline="#F2B400", width=8)
    centred(draw, str(number), 2292, 3290, ft(64, True))


def hide_legacy_number(page):
    draw = ImageDraw.Draw(page)
    draw.ellipse((2180, 3230, 2400, 3450), fill="white")


def save(page, package, slug):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"CC-NURSERY-V4-P{package:03d}-{slug}.png"
    page.convert("RGB").save(path, "PNG", dpi=(300, 300), optimize=True)
    print(path)


def clean_page():
    page = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(page)
    draw.ellipse((-220, 3030, 630, 3880), fill="#FBD1D7")
    draw.ellipse((1960, -380, 2810, 470), fill="#FFE59B")
    draw.ellipse((1960, 3100, 2820, 3960), fill="#D6EAFF")
    add_logo(page)
    return page


def contents_rows():
    return [
        ("Welcome to Communication Champions", 5, "Welcome"),
        ("Meet Star", 6, "Module 1 – Me & My Family"),
        ("My Name", 7, None), ("My Photo", 8, None),
        ("My Feelings", 9, None), ("My Birthday", 10, None),
        ("My Family", 11, None), ("Draw My Family", 12, None),
        ("Family Members", 13, None), ("Who Is in My Family?", 14, None),
        ("My Favourite Toy", 15, None), ("My Favourite Toy Activity", 16, None),
        ("Foods I Like", 17, None), ("Healthy Habits", 18, None),
        ("Animals Around Me", 19, "Module 2 – My World"),
        ("Colours Around Me", 20, None), ("I Can Speak", 21, None),
        ("My Friends", 22, "Module 3 – Friends & Communication"),
        ("Playground Talk", 23, None), ("Let’s Talk Together", 24, None),
        ("Listening Time", 25, None), ("Show and Tell", 26, None),
        ("Sharing Toys", 27, None), ("Taking Turns", 28, None),
        ("Kind Words", 29, None), ("Asking for Help", 30, None),
        ("Communication Game", 31, None),
        ("My Favourite Food", 32, "Module 4 – My World & Expression"),
        ("My Pet", 33, None), ("Favourite Animal", 34, None),
        ("At the Park", 35, None),
        ("My School", 36, "Module 5 – School & Expression"),
        ("My Classroom", 37, None), ("Story Time", 38, None),
        ("Music and Singing", 39, None), ("My Daily Routine", 40, None),
        ("Certificate of Completion", 41, "Closing Pages"),
        ("I Am a Communication Champion!", 42, None),
    ]


def build_contents(part, rows):
    page = clean_page()
    title(page, f"Contents — Part {part}", 74)
    draw = ImageDraw.Draw(page)
    draw.rounded_rectangle((190, 480, 2290, 3180), radius=45, fill="white", outline="#D8E7F6", width=7)
    y = 555
    for name, number, module in rows:
        if module:
            draw.rounded_rectangle((280, y, 2200, y+82), radius=24, fill="#FFF0C8")
            draw.text((330, y+16), module, font=ft(38, True), fill="#9B6400")
            y += 110
        draw.text((350, y), name, font=ft(36), fill="#26384E")
        centred(draw, str(number), 2120, y, ft(36, True), "#E49B00")
        y += 78
    return page


def from_legacy(old_package, new_number, source_name=None):
    name = source_name or f"CC-NURSERY-V3-P{old_package:03d}.png"
    page = Image.open(LEGACY / name).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    hide_legacy_number(page)
    page_number(page, new_number)
    return page


def compose_new_art(filename, heading, instruction, number, body):
    page = Image.open(NEW_ART / filename).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    add_logo(page)
    title(page, heading, 72 if len(heading) > 19 else 86)
    draw = ImageDraw.Draw(page)
    draw.rounded_rectangle((650, 300, 2290, 455), radius=42, fill="#FFF8DF", outline="#F2C75C", width=5)
    centred(draw, instruction, 1470, 345, ft(38, True))
    body(draw)
    page_number(page, number)
    return page


def main():
    # P001 cover, uncounted.
    cover = Image.open(LEGACY / "CC-NURSERY-V3-P001.png").convert("RGB")
    save(cover, 1, "front-cover")

    # P002 About This Book, counted as 1, number hidden.
    about = clean_page(); title(about, "About This Book", 84)
    d = ImageDraw.Draw(about)
    d.rounded_rectangle((230, 520, 2250, 2960), radius=55, fill="#FFFFFF", outline="#D8E7F6", width=8)
    centred(d, "Communication Champions — Nursery (3+)", 1240, 650, ft(54, True))
    paragraphs = [
        "This book helps young children listen, speak, share ideas and connect with confidence.",
        "Children learn through conversation, pictures, movement, drawing, tracing and playful teacher-guided activities.",
        "Star models friendly language. The teacher demonstrates each task, pauses for the child’s response and celebrates every attempt.",
        "Families can repeat the same communication skill during simple daily routines at home.",
    ]
    y = 850
    for text in paragraphs:
        words = text.split(); lines=[]; line=""
        for word in words:
            trial=(line+" "+word).strip()
            if d.textlength(trial, font=ft(42)) > 1580:
                lines.append(line); line=word
            else: line=trial
        lines.append(line)
        for ln in lines:
            centred(d, ln, 1240, y, ft(42), "#33465C"); y += 62
        y += 105
    d.rounded_rectangle((430, 2600, 2050, 2780), radius=38, fill="#EAF4DF")
    centred(d, "Listen • Speak • Share • Connect", 1240, 2650, ft(46, True), "#285B35")
    save(about, 2, "about-this-book")

    # P003 Copyright, counted as 2, number hidden.
    copyright_page = Image.open(LEGACY / "CC-NURSERY-V3-P002.png").convert("RGB")
    hide_legacy_number(copyright_page)
    save(copyright_page, 3, "copyright-publication-details")

    rows = contents_rows()
    save(build_contents(1, rows[:21]), 4, "contents-part-1")
    save(build_contents(2, rows[21:]), 5, "contents-part-2")

    # P006–P012 reuse validated visual designs with corrected reader numbering.
    mapping = [
        (6, 4, 5, "welcome"),
        (7, 5, 6, "meet-star"),
        (8, 6, 7, "my-name"),
        (9, 7, 8, "my-photo"),
        (10, 8, 9, "my-feelings"),
        (11, 9, 10, "my-birthday"),
        (12, 10, 11, "my-family"),
    ]
    for package, old, number, slug in mapping:
        source = "CC-NURSERY-V3-P006.png" if old == 6 else None
        save(from_legacy(old, number, source), package, slug)

    def draw_family_body(draw):
        draw.rounded_rectangle((330, 560, 2150, 740), radius=35, fill="white", outline="#D8E7F6", width=5)
        draw.text((420, 610), "This is my family.  I drew", font=ft(42, True), fill=BLUE)
        draw.line((1260, 670, 2030, 670), fill="#6FA6D9", width=7)

    save(compose_new_art("draw-my-family.png", "Draw My Family", "Draw the people you call family.", 12, draw_family_body), 13, "draw-my-family")

    labels = ["mother", "father", "sister", "brother", "grandmother", "grandfather"]
    def family_members_body(draw):
        xs = [465, 1240, 2010, 465, 1240, 2010]
        ys = [1590, 1590, 1590, 2800, 2800, 2800]
        for label, x, y in zip(labels, xs, ys):
            centred(draw, label, x, y, ft(37, True))
        draw.rounded_rectangle((430, 3100, 2050, 3215), radius=28, fill="white", outline="#F2C75C", width=5)
        centred(draw, "This is my", 900, 3128, ft(38, True))
        draw.line((1130, 3170, 1910, 3170), fill=BLUE, width=5)

    save(compose_new_art("family-members.png", "Family Members", "Point to a picture. Say the family word.", 13, family_members_body), 14, "family-members")

    match_labels = ["mother", "father", "sister", "brother"]
    def matching_body(draw):
        xs = [330, 910, 1490, 2070]
        # Remove generated cards and the overlapping note, then rebuild a
        # deterministic aligned vocabulary row.
        draw.rectangle((0, 2420, W, 3235), fill="white")
        draw.rounded_rectangle((430, 2460, 2050, 2605), radius=34, fill="#FFF8DF", outline="#F2C75C", width=5)
        centred(draw, "Point to each person. Say the family word.", 1240, 2502, ft(38, True))
        for label, x in zip(match_labels, xs):
            draw.rounded_rectangle((x-255, 2750, x+255, 3050), radius=34, fill="white", outline="#AFCDF6", width=6)
            centred(draw, label, x, 2860, ft(39, True))

    family_match = compose_new_art(
        "who-is-in-my-family.png",
        "Who Is in My Family?",
        "Look at each person.",
        14,
        matching_body,
    )
    # The generated source included a second Star behind the logo. Clear the
    # complete brand zone and reapply only the approved logo.
    ImageDraw.Draw(family_match).rectangle((0, 0, 720, 720), fill="white")
    add_logo(family_match)
    save(family_match, 15, "who-is-in-my-family")

    def toy_body(draw):
        # Purposeful mascot model text; no unexplained empty board.
        centred(draw, "My toy", 705, 2570, ft(38, True))
        # Clear generated overlapping note rows and rebuild them with a
        # protected right margin for the printed page number.
        draw.rectangle((840, 2680, W, 3315), fill="white")
        draw.rounded_rectangle((900, 2780, 2080, 2965), radius=42, fill="#FFF2F5", outline="#F49AB0", width=6)
        draw.text((990, 2835), "I like my", font=ft(40, True), fill=BLUE)
        draw.line((1310, 2890, 1950, 2890), fill=BLUE, width=6)
        draw.rounded_rectangle((900, 3020, 2080, 3205), radius=42, fill="#EFF8FF", outline="#79B8E8", width=6)
        draw.text((990, 3075), "It is", font=ft(40, True), fill=BLUE)
        draw.line((1170, 3130, 1950, 3130), fill=BLUE, width=6)

    save(compose_new_art("my-favourite-toy.png", "My Favourite Toy", "Draw one favourite toy. Tell us about it.", 15, toy_body), 16, "my-favourite-toy")


if __name__ == "__main__":
    main()
