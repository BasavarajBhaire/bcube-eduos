#!/usr/bin/env python3
"""Deterministically compose the CC Nursery V4 P023 My Friends candidate."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[2]
V4=ROOT/"BCube_Gold_Production_v4"
W,H=2480,3508
NAVY="#123f7c"; GOLD="#edae00"; PALE="#fff8dc"; BLUE="#d9edff"; PINK="#fde0e8"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def font(size,bold=False): return ImageFont.truetype(BOLD if bold else FONT,size)
def center(draw,box,text,f,fill=NAVY):
    b=draw.textbbox((0,0),text,font=f); x=box[0]+(box[2]-box[0]-(b[2]-b[0]))/2
    y=box[1]+(box[3]-box[1]-(b[3]-b[1]))/2-b[1]; draw.text((x,y),text,font=f,fill=fill)
def contain(im,box):
    x1,y1,x2,y2=box; copy=im.copy(); copy.thumbnail((x2-x1,y2-y1),Image.Resampling.LANCZOS)
    return copy,(x1+(x2-x1-copy.width)//2,y1+(y2-y1-copy.height)//2)

page=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(page)
# Locked corner geometry; content never enters these zones.
d.pieslice((1980,-280,2740,480),0,180,fill="#ffe59b")
d.pieslice((-300,3060,620,3980),180,360,fill=PINK)
d.pieslice((1930,3060,2820,3950),180,360,fill=BLUE)

logo=Image.open(V4/"approved-assets/brand/Official_BCube_Logo-v1.png").convert("RGBA")
logo.thumbnail((340,300),Image.Resampling.LANCZOS); page.paste(logo,(85,55),logo)
center(d,(440,55,1980,275),"My Friends",font(126,True))

banner=(430,330,2260,550); d.rounded_rectangle(banner,42,fill=PALE,outline=GOLD,width=7)
center(d,banner,"Point to two friendly actions. Say what a friend can do.",font(46,True))

art=Image.open(V4/"assets/nursery/communication-champions/P023/my-friends-three-actions-v1.png").convert("RGB")
# The generated authoring asset is a three-panel strip. Split only at its known
# white gutters, then contain each complete panel—never focal-crop a subject.
cuts=((20,175,558,780),(578,195,1110,790),(1128,180,1672,800))
for i,cut in enumerate(cuts):
    panel=art.crop(cut); box=(125+i*745,650,800+i*745,2250)
    d.rounded_rectangle(box,34,fill="white",outline=("#79b5e2","#90c872","#efb13b")[i],width=5)
    fitted,pos=contain(panel,(box[0]+18,box[1]+18,box[2]-18,box[3]-18)); page.paste(fitted,pos)

labels=[("GREET",BLUE),("SHARE","#e7f5df"),("HELP","#fff0ca")]
for i,(label,col) in enumerate(labels):
    x1=125+i*745; box=(x1,2350,x1+675,2485)
    d.rounded_rectangle(box,28,fill=col,outline=NAVY,width=4); center(d,box,label,font(48,True))

model=(200,2570,2280,2725); d.rounded_rectangle(model,30,fill="#f2faea",outline="#8dbf65",width=5)
center(d,model,"A friend can greet, share and help.",font(50,True))
response=(200,2785,2280,2985); d.rounded_rectangle(response,30,fill="white",outline="#79b5e2",width=6)
d.text((285,2840),"A friend can",font=font(54,True),fill=NAVY)
d.line((800,2915,2090,2915),fill=NAVY,width=5)

# Footer intentionally reserves the mascot zone until the approved Star asset is locked.
page_no=(2180,3170,2370,3360); d.ellipse(page_no,fill="white",outline=GOLD,width=8); center(d,page_no,"22",font(62,True))

out=V4/"output/nursery/communication-champions/validation/candidates/CC-NURSERY-V4-P023-my-friends.png"
out.parent.mkdir(parents=True,exist_ok=True); page.save(out,"PNG",dpi=(300,300),compress_level=6)
# Force a complete decode now; metadata-only opens do not detect truncated IDAT streams.
with Image.open(out) as check:
    check.load()
    if check.size != (W,H): raise RuntimeError(f"invalid output dimensions: {check.size}")
print(out)
