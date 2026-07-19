#!/usr/bin/env python3
"""Apply locked header clearance and approved Star asset to corrected CC pages."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT.parent/'production-prompts/communication-champions/nursery/v3/illustrations/final/CC-NURSERY-V3-P005-meet-star.png'
FALLBACK=ROOT/'output/nursery/communication-champions/validation/complete-v4-43-pages/CC-NURSERY-V4-P007-meet-star.png'
ASSET=ROOT/'OFFICIAL_ASSETS/STAR-MASCOT-APPROVED-V4.png'
OUT=ROOT/'output/nursery/communication-champions/validation/corrected-reader-pages-16-41-v2'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
INSTRUCTIONS={
 'P017':'Show one toy. Name it, describe it and say what you do.',
 'P018':'Circle two foods you like. Say your choice.',
 'P019':'Tick healthy habits. Cross the other choices.',
}

def make_asset():
    try:
        im=Image.open(SRC).convert('RGBA')
    except Exception:
        im=Image.open(FALLBACK).convert('RGBA')
    # Approved coloured Star only; coordinates are from the locked Meet Star page.
    crop=im.crop((170,760,1330,1990))
    px=crop.load()
    for y in range(crop.height):
        for x in range(crop.width):
            r,g,b,a=px[x,y]
            if r>246 and g>246 and b>246: px[x,y]=(255,255,255,0)
            # Exclude the teacher who appears below-left on the source page.
            if x < 430 and y > 760: px[x,y]=(255,255,255,0)
            if y < 130: px[x,y]=(255,255,255,0)
    ASSET.parent.mkdir(parents=True,exist_ok=True)
    crop.save(ASSET,'PNG')

def fix(path,instruction):
    im=Image.open(path).convert('RGBA'); d=ImageDraw.Draw(im)
    # Clear former banner, then place it outside logo safe zone x=0..590, y=0..500.
    d.rectangle((400,330,2290,650),fill='white')
    d.rounded_rectangle((650,390,2240,620),radius=42,fill='#FFF8DF',outline='#E8B832',width=6)
    face=ImageFont.truetype(BOLD,38)
    box=d.textbbox((0,0),instruction,font=face)
    d.text((1445-(box[2]-box[0])/2,470),instruction,font=face,fill='#123D7A')
    # Replace improvised bottom icon with the locked approved asset.
    d.rectangle((0,3000,520,3508),fill='white')
    star=Image.open(ASSET).convert('RGBA'); star.thumbnail((360,390),Image.Resampling.LANCZOS)
    im.alpha_composite(star,(45,3070))
    im.convert('RGB').save(path,'PNG',dpi=(300,300),compress_level=6)

make_asset()
for path in OUT.glob('*.png'):
    code=next((k for k in INSTRUCTIONS if k in path.name),None)
    if code: fix(path,INSTRUCTIONS[code])
