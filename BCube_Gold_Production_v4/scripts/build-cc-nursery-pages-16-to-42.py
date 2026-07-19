"""Build Communication Champions Nursery v4 reader pages 16–42.

Each legacy P015–P041 curriculum page maps to v4 P017–P043 and reader
page 16–42. Outputs are individual A4 PNG files.
"""

from pathlib import Path
from math import cos, sin, pi

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets/nursery/communication-champions"
LOGO = ASSETS / "P006/bcube-academy-logo.jpg"
OUT = ROOT / "output/nursery/communication-champions/validation/complete-v4-43-pages"
W, H = 2480, 3508
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BLUE = "#123D7A"
INK = "#32465A"
PASTELS = ["#FCE4EA", "#E4F1FF", "#FFF1C9", "#E9F4D9", "#EFE5FA", "#FFEBDD"]
LINES = ["#EE7896", "#5EA4DF", "#EAB536", "#7DB64B", "#9A75C7", "#E58B55"]


def ft(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REGULAR, size)


def centred(draw, text, cx, y, face, fill=BLUE):
    box = draw.textbbox((0, 0), text, font=face)
    draw.text((cx - (box[2] - box[0]) / 2, y), text, font=face, fill=fill)


def wrap(draw, text, face, max_width):
    words = text.split()
    lines, line = [], ""
    for word in words:
        trial = (line + " " + word).strip()
        if line and draw.textlength(trial, font=face) > max_width:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


def add_logo(page):
    source = Image.open(LOGO).convert("RGB")
    source.thumbnail((470, 380), Image.Resampling.LANCZOS)
    panel = Image.new("RGB", (570, 430), "white")
    panel.paste(source, ((570-source.width)//2, (430-source.height)//2))
    page.paste(panel, (20, 10))


def star_points(cx, cy, outer, inner):
    points = []
    for i in range(10):
        angle = -pi/2 + i*pi/5
        radius = outer if i % 2 == 0 else inner
        points.append((cx + radius*cos(angle), cy + radius*sin(angle)))
    return points


def draw_star(draw, cx, cy, scale=1.0):
    draw.polygon(star_points(cx, cy, 135*scale, 68*scale), fill="#FFD31A", outline="#E78A00")
    draw.ellipse((cx-48*scale, cy-22*scale, cx-15*scale, cy+14*scale), fill="#1C2A38")
    draw.ellipse((cx+15*scale, cy-22*scale, cx+48*scale, cy+14*scale), fill="#1C2A38")
    draw.arc((cx-40*scale, cy-5*scale, cx+40*scale, cy+65*scale), 15, 165, fill="#B64224", width=max(3, int(6*scale)))
    draw.polygon([(cx-120*scale,cy+50*scale),(cx-200*scale,cy+125*scale),(cx-100*scale,cy+115*scale)], fill="#2778C8")
    draw.ellipse((cx-85*scale,cy+110*scale,cx-12*scale,cy+150*scale),fill="#267BC4",outline="#123D7A")
    draw.ellipse((cx+12*scale,cy+110*scale,cx+85*scale,cy+150*scale),fill="#267BC4",outline="#123D7A")


def page_base(title, number, instruction):
    page = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(page)
    draw.ellipse((-260, 3070, 600, 3930), fill="#FAD3D9")
    draw.ellipse((2000, -380, 2860, 480), fill="#FFE49A")
    draw.ellipse((1990, 3130, 2850, 3990), fill="#D6EAFF")
    add_logo(page)
    draw.rounded_rectangle((690, 40, 2390, 270), radius=38, fill="white")
    size = 72 if len(title) > 24 else 86
    centred(draw, title, 1570, 78, ft(size, True))
    draw.rounded_rectangle((430, 360, 2240, 570), radius=45, fill="#FFF8DF", outline="#F0C659", width=6)
    lines = wrap(draw, instruction, ft(40, True), 1580)
    y = 405 if len(lines) == 1 else 380
    for line in lines[:2]:
        centred(draw, line, 1335, y, ft(40, True)); y += 56
    draw_star(draw, 220, 3170, .62)
    draw.ellipse((2200, 3250, 2385, 3435), fill="white", outline="#F2B400", width=8)
    centred(draw, str(number), 2292, 3290, ft(64, True))
    return page


def card_grid(page, labels, top=720, bottom=2440, cols=3):
    draw = ImageDraw.Draw(page)
    rows = (len(labels)+cols-1)//cols
    gapx, gapy = 55, 70
    left, right = 220, 2260
    cardw = (right-left-gapx*(cols-1))/cols
    cardh = (bottom-top-gapy*(rows-1))/rows
    for i, label in enumerate(labels):
        row, col = divmod(i, cols)
        x = left + col*(cardw+gapx)
        y = top + row*(cardh+gapy)
        draw.rounded_rectangle((x,y,x+cardw,y+cardh),radius=38,fill=PASTELS[i%len(PASTELS)],outline=LINES[i%len(LINES)],width=7)
        # Friendly symbolic illustration: large initial medallion.
        draw.ellipse((x+cardw*.28,y+55,x+cardw*.72,y+cardh*.55),fill="white",outline=LINES[i%len(LINES)],width=6)
        initial = label.strip()[0].upper() if label.strip() else "?"
        centred(draw, initial, x+cardw/2, y+cardh*.18, ft(int(min(110,cardh*.22)),True), LINES[i%len(LINES)])
        face = ft(37 if len(label)<18 else 31, True)
        for j,line in enumerate(wrap(draw,label,face,cardw-70)[:2]):
            centred(draw,line,x+cardw/2,y+cardh*.67+j*46,face)


def response_box(page, text, y=2650, second=None):
    draw = ImageDraw.Draw(page)
    draw.rounded_rectangle((420,y,2190,y+210),radius=40,fill="white",outline="#93BCE2",width=6)
    draw.text((520,y+62),text,font=ft(43,True),fill=BLUE)
    if "______" not in text:
        draw.line((1450,y+125,2050,y+125),fill=BLUE,width=6)
    if second:
        draw.rounded_rectangle((420,y+260,2190,y+470),radius=40,fill="white",outline="#A8CD82",width=6)
        draw.text((520,y+322),second,font=ft(43,True),fill=BLUE)


def drawing_page(title, number, instruction, frame_label, starters, side_labels):
    page = page_base(title, number, instruction)
    draw = ImageDraw.Draw(page)
    draw.rounded_rectangle((230,680,1900,2450),radius=55,fill="white",outline="#68A8DE",width=10)
    centred(draw,frame_label,1065,1450,ft(52,True),"#7C9AB4")
    for i,label in enumerate(side_labels[:3]):
        y=790+i*480
        draw.rounded_rectangle((1950,y,2290,y+330),radius=40,fill=PASTELS[i],outline=LINES[i],width=6)
        centred(draw,label,2120,y+135,ft(34,True))
    response_box(page, starters[0], 2600, starters[1] if len(starters)>1 else None)
    return page


def sequence_page(title, number, instruction, labels, footer):
    page = page_base(title,number,instruction)
    draw=ImageDraw.Draw(page)
    cols=2
    for i,label in enumerate(labels):
        row,col=divmod(i,cols)
        x=260+col*1050; y=720+row*760
        draw.rounded_rectangle((x,y,x+900,y+620),radius=46,fill=PASTELS[i],outline=LINES[i],width=7)
        draw.ellipse((x+40,y+40,x+150,y+150),fill="white",outline=LINES[i],width=5)
        centred(draw,str(i+1),x+95,y+58,ft(52,True),LINES[i])
        centred(draw,label,x+450,y+270,ft(43,True))
    response_box(page,footer,2380)
    return page


def certificate(number):
    page=page_base("Certificate of Completion",number,"Completed with care, confidence and kindness.")
    draw=ImageDraw.Draw(page)
    draw.rounded_rectangle((260,700,2220,2930),radius=70,fill="#FFFDF4",outline="#E4B641",width=14)
    centred(draw,"Communication Champions",1240,890,ft(68,True))
    centred(draw,"This certifies that",1240,1120,ft(48),INK)
    draw.line((600,1300,1880,1300),fill=BLUE,width=7)
    centred(draw,"has completed the Nursery workbook",1240,1390,ft(44),INK)
    skills=["Listen with care","Speak with confidence","Take turns","Use kind words"]
    y=1640
    for i,s in enumerate(skills):
        draw.rounded_rectangle((520,y,1960,y+150),radius=35,fill=PASTELS[i],outline=LINES[i],width=5)
        draw.rectangle((570,y+48,625,y+103),outline=BLUE,width=5)
        draw.text((690,y+44),s,font=ft(42,True),fill=BLUE); y+=190
    draw.text((480,2480),"Date",font=ft(38,True),fill=BLUE); draw.line((650,2530,1050,2530),fill=BLUE,width=5)
    draw.text((1210,2480),"Teacher/Parent Signature",font=ft(34,True),fill=BLUE); draw.line((1680,2530,2070,2530),fill=BLUE,width=5)
    draw.text((480,2680),"My mark",font=ft(38,True),fill=BLUE)
    draw.rounded_rectangle((730,2615,1120,2830),radius=30,fill="white",outline="#93BCE2",width=5)
    return page


SPECS = [
 (15,"My Favourite Toy Activity","Show one toy. Name it, describe it and say what you do.",["name","colour or feature","action"],"This is my ______.  It is ______.  I like to ______ with it.","cards"),
 (16,"Foods I Like","Circle two foods you like. Say your choice.",["banana","apple","rice","roti","carrot","curd"],"I like ______.","cards"),
 (17,"Healthy Habits","Tick healthy habits. Cross the other choices.",["wash hands","brush teeth","drink water","sleep","unwashed food","stay awake late"],"I can ______.","cards"),
 (18,"Animals Around Me","Name the animals. Choose and colour one.",["cat","dog","cow","bird"],"It can ______.","cards"),
 (19,"Colours Around Me","Find red, blue, yellow and green.",["red ball","blue bag","yellow cup","green plant"],"Colour the swatches.","cards"),
 (20,"I Can Speak","Choose one picture and say a sentence.",["ball","family","pet"],"I see a ______.","cards"),
 (21,"My Friends","Point to friendly actions. Say what a friend can do.",["greet","share","help","play peacefully"],"A friend can ______.","cards"),
 (22,"Playground Talk","Choose the polite phrase for each playground moment.",["Can I play?","My turn, please.","Thank you."],"Say one phrase.","cards"),
 (23,"Let’s Talk Together","Follow the conversation path with a partner.",["Hello!","What do you like?","I like ______.","Goodbye!"],"Take two turns.","sequence"),
 (24,"Listening Time","Circle the pictures that show good listening.",["face speaker","calm body","wait turn","interrupt","look at toy"],"I am listening.","cards"),
 (25,"Show and Tell","Use three cues to show and tell about one object.",["name","describe","use"],"This is my ______.  It is ______.  I use it to ______.","cards"),
 (26,"Sharing Toys","Put the sharing pictures in order. Role-play the words.",["You may use it.","Thank you.","My turn next, please."],"Say the sharing words.","sequence"),
 (27,"Taking Turns","Number the pictures from first to last.",["choose game","first child rolls","wait for turn","second child rolls"],"My turn. Your turn.","sequence"),
 (28,"Kind Words","Match each situation to the kind words.",["please","thank you","sorry","excuse me"],"Choose and say one.","cards"),
 (29,"Asking for Help","Choose a trusted helper. Practise asking for help.",["teacher","friend","caregiver"],"Please help me with ______.","cards"),
 (30,"Communication Game","Move a token around the four communication stops.",["Listen","Speak","Take turns","Kind words"],"Start → Finish","sequence"),
 (31,"My Favourite Food","Draw one favourite food on the plate.",["plate","colour","taste"],"My favourite food is ______.","drawing"),
 (32,"My Pet","Draw a pet or an animal you would care for.",["food","water","safe shelter"],"My pet is a ______.","drawing"),
 (33,"Favourite Animal","Choose one animal and describe it.",["elephant","rabbit","parrot","fish"],"My favourite animal is ______.","cards"),
 (34,"At the Park","Find and circle the five park items.",["slide","swing","tree","ball","bench"],"I can ______ at the park.","cards"),
 (35,"My School","Point and say the school words.",["school","teacher","classroom","friends"],"My school is ______.","cards"),
 (36,"My Classroom","Match each classroom object to its place.",["pencil","crayon","book","bag","scissors","glue"],"May I use the ______?","cards"),
 (37,"Story Time","Listen to the three-picture story. Answer the question.",["Asha found a red ball.","She asked whose ball it was.","Ravi said thank you."],"What did Asha find?  ball / book","sequence"),
 (38,"Music and Singing","Copy the actions while singing hello.",["Clap, clap—hello!","Tap, tap—hello!","Wave, wave—hello!"],"I choose ______.","cards"),
 (39,"My Daily Routine","Number the morning routine from first to last.",["waking","brushing teeth","eating breakfast","entering school"],"In the morning, I ______.","sequence"),
]


def build():
    OUT.mkdir(parents=True,exist_ok=True)
    for legacy,title,instruction,labels,footer,kind in SPECS:
        package=legacy+2; number=legacy+1
        if kind=="drawing":
            page=drawing_page(title,number,instruction,"Draw here",footer.split("  "),labels)
        elif kind=="sequence":
            page=sequence_page(title,number,instruction,labels,footer)
        else:
            page=page_base(title,number,instruction)
            card_grid(page,labels,cols=3 if len(labels) in (3,6) else 2)
            response_box(page,footer,2600)
        path=OUT/f"CC-NURSERY-V4-P{package:03d}-{title.lower().replace('’','').replace('!','').replace('?','').replace(' ','-')}.png"
        page.save(path,"PNG",dpi=(300,300),optimize=True)
        print(path)

    cert=certificate(41)
    cert.save(OUT/"CC-NURSERY-V4-P042-certificate-of-completion.png","PNG",dpi=(300,300),optimize=True)

    final=page_base("I Am a Communication Champion!",42,"Tick your achievements. Say the champion pledge.")
    draw=ImageDraw.Draw(final)
    achievements=["I listen with care.","I speak with confidence.","I take turns.","I use kind words."]
    y=760
    for i,text in enumerate(achievements):
        draw.rounded_rectangle((430,y,2100,y+300),radius=48,fill=PASTELS[i],outline=LINES[i],width=7)
        draw.rectangle((510,y+95,590,y+175),fill="white",outline=BLUE,width=6)
        draw.text((690,y+92),text,font=ft(48,True),fill=BLUE); y+=380
    draw.rounded_rectangle((350,2350,2160,2750),radius=60,fill="#FFF1C9",outline="#EAB536",width=8)
    centred(draw,"I am a Communication Champion!",1255,2480,ft(58,True))
    draw_star(draw,1900,3000,1.15)
    final.save(OUT/"CC-NURSERY-V4-P043-i-am-a-communication-champion.png","PNG",dpi=(300,300),optimize=True)


if __name__=="__main__":
    build()
