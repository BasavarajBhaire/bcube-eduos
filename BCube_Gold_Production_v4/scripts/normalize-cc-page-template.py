#!/usr/bin/env python3
"""Normalize generated CC pages to locked header, corner and mascot regions."""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES=True
ROOT=Path(__file__).resolve().parents[1]
MASCOT=ROOT/'OFFICIAL_ASSETS/STAR-MASCOT-APPROVED-V4.png'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
W,H=2480,3508

def main():
 p=argparse.ArgumentParser(); p.add_argument('source'); p.add_argument('output'); p.add_argument('instruction'); a=p.parse_args()
 with Image.open(a.source) as src:
  im=src.convert('RGBA').resize((W,H),Image.Resampling.LANCZOS)
 d=ImageDraw.Draw(im)
 # Locked clean top-right corner: one pale-yellow quarter-circle only.
 d.rectangle((1980,0,W,650),fill='white')
 d.ellipse((2140,-430,3000,430),fill='#FFE49A')
 # Locked instruction banner begins beyond logo protected zone.
 d.rectangle((400,330,2290,660),fill='white')
 d.rounded_rectangle((650,390,2240,620),radius=42,fill='#FFF8DF',outline='#E8B832',width=6)
 face=ImageFont.truetype(BOLD,38); box=d.textbbox((0,0),a.instruction,font=face)
 d.text((1445-(box[2]-box[0])/2,470),a.instruction,font=face,fill='#123D7A')
 # Locked official Star; generated mascot is always removed.
 d.rectangle((0,3000,540,H),fill='white')
 star=Image.open(MASCOT).convert('RGBA'); star.thumbnail((360,390),Image.Resampling.LANCZOS)
 im.alpha_composite(star,(45,3070))
 Path(a.output).parent.mkdir(parents=True,exist_ok=True)
 im.convert('RGB').save(a.output,'PNG',dpi=(300,300),compress_level=6)

if __name__=='__main__': main()
