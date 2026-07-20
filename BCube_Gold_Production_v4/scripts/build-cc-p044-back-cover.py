#!/usr/bin/env python3
"""Deterministically compose the unnumbered Communication Champions back cover."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[2]; V4=ROOT/"BCube_Gold_Production_v4"
W,H=2480,3508; NAVY="#123f7c"; GOLD="#efad00"; PINK="#f8b9c8"; BLUE="#a9d6f5"; GREEN="#b9d99c"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def f(n,b=False): return ImageFont.truetype(BOLD if b else FONT,n)
def center(d,box,text,font,fill=NAVY):
    b=d.textbbox((0,0),text,font=font); d.text((box[0]+(box[2]-box[0]-b[2]+b[0])/2,box[1]+(box[3]-box[1]-b[3]+b[1])/2-b[1]),text,font=font,fill=fill)

im=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(im)
# Locked full-bleed corner language matching the front/interior system.
d.pieslice((-420,-380,820,860),0,180,fill="#ffdce5")
d.pieslice((1770,-420,2900,710),0,180,fill="#ffe49a")
d.pieslice((-500,2890,850,4240),180,360,fill="#dcefcf")
d.pieslice((1700,2860,3000,4160),180,360,fill="#d9edff")

logo=Image.open(V4/"approved-assets/brand/Official_BCube_Logo-v1.png").convert("RGBA")
logo.thumbnail((650,570),Image.Resampling.LANCZOS); im.paste(logo,((W-logo.width)//2,220),logo)
center(d,(180,830,2300,1060),"Communication Champions",f(112,True))
badge=(935,1085,1545,1215); d.rounded_rectangle(badge,42,fill="#fff0b9",outline=GOLD,width=6); center(d,badge,"Nursery (3+)",f(52,True))

copy=(220,1320,2260,1700); d.rounded_rectangle(copy,55,fill="#fffaf0",outline="#f2c35c",width=6)
center(d,(300,1380,2180,1505),"Little voices grow into confident communication.",f(50,True))
center(d,(300,1510,2180,1640),"Listen • Speak • Share • Connect",f(58,True),GOLD)

cards=[(PINK,"LISTEN","with care"),(BLUE,"SPEAK","with confidence"),(GREEN,"CONNECT","with kindness")]
for i,(colour,a,b) in enumerate(cards):
    x=215+i*700; box=(x,1840,x+650,2205)
    d.rounded_rectangle(box,48,fill=colour,outline="white",width=8)
    center(d,(x+20,1880,x+630,2030),a,f(54,True)); center(d,(x+20,2020,x+630,2155),b,f(38,True))

center(d,(250,2380,2230,2570),"Every word connects us.",f(72,True))
d.line((560,2650,1920,2650),fill=GOLD,width=5)
center(d,(320,2715,2160,2840),"BCube Future Academy",f(46,True))
center(d,(320,2835,2160,2950),"BCube Future Skills Learning Series™",f(35))
center(d,(320,2995,2160,3110),"bcubefutureacademy.in",f(38,True))
center(d,(320,3100,2160,3215),"info@bcubefutureacademy.in",f(34))

out=V4/"output/nursery/communication-champions/validation/candidates/CC-NURSERY-V4-P044-back-cover.png"
out.parent.mkdir(parents=True,exist_ok=True); im.save(out,"PNG",dpi=(300,300),compress_level=6)
with Image.open(out) as check: check.load(); assert check.size==(W,H)
print(out)
