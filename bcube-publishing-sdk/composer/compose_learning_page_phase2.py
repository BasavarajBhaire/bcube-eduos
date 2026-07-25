#!/usr/bin/env python3
"""Task-specific Phase 2 composer for five BCube pilot learning pages.

The pilot renderer removes the parent/homework panel, uses a compact teacher
cue, and renders page-owned interaction mechanics. Other pages fall back to
the existing character-aware Learning Page V2 composer.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import deque
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
BASE_PATH = ROOT / "bcube-publishing-sdk/composer/compose_learning_page_v2.py"
FALLBACK_PATH = ROOT / "bcube-publishing-sdk/composer/compose_learning_page_character_v2.py"
TEMPLATE_PATH = ROOT / "bcube-publishing-sdk/templates/learning-page-v2.json"
PILOT_IDS = {
    "EL-LKG-V4-P023", "CC-NURSERY-V4-P022", "CE-NURSERY-V4-P010",
    "YS-UKG-V4-P010", "CM-UKG-V4-P032",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def resolve(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def panel(draw: ImageDraw.ImageDraw, bounds: list[int], fill="#FFFFFF", outline="#8E5AC7", width=4, radius=28):
    draw.rounded_rectangle(bounds, radius=radius, fill=fill, outline=outline, width=width)


def anchor(draw: ImageDraw.ImageDraw, centre: tuple[int, int], diameter: int, outline: str) -> list[int]:
    x, y = centre
    half = diameter // 2
    bounds = [x-half, y-half, x+half, y+half]
    draw.ellipse(bounds, fill="#FFFFFF", outline=outline, width=6)
    return bounds


def paste_contain(canvas: Image.Image, image: Image.Image, bounds: list[int], inset=10) -> list[int]:
    rgba = image.convert("RGBA")
    x0, y0, x1, y1 = bounds
    x0 += inset; y0 += inset; x1 -= inset; y1 -= inset
    scale = min((x1-x0)/rgba.width, (y1-y0)/rgba.height)
    size = (max(1, round(rgba.width*scale)), max(1, round(rgba.height*scale)))
    rgba = rgba.resize(size, Image.Resampling.LANCZOS)
    left = x0 + (x1-x0-rgba.width)//2
    top = y0 + (y1-y0-rgba.height)//2
    canvas.paste(rgba, (left, top), rgba)
    return [left, top, left+rgba.width, top+rgba.height]


def remove_near_white(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    rgba.putdata([(255,255,255,0) if r>246 and g>246 and b>246 else (r,g,b,a)
                  for r,g,b,a in rgba.getdata()])
    bbox = rgba.getbbox()
    if bbox is None:
        raise ValueError("Illustration contains no visible artwork")
    return rgba.crop(bbox)


def largest_component(image: Image.Image, min_fraction: float = 0.015) -> Image.Image:
    """Keep the principal connected foreground component and discard crop debris."""
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    width, height = rgba.size
    scale = min(1.0, 520 / max(width, height))
    sw, sh = max(1, round(width*scale)), max(1, round(height*scale))
    mask = alpha.resize((sw, sh), Image.Resampling.NEAREST).point(lambda p: 255 if p > 18 else 0)
    pixels = mask.load()
    seen = bytearray(sw*sh)
    components: list[tuple[int, tuple[int,int,int,int]]] = []
    for sy in range(sh):
        for sx in range(sw):
            index = sy*sw+sx
            if seen[index] or not pixels[sx,sy]:
                continue
            queue = deque([(sx,sy)])
            seen[index] = 1
            count = 0
            minx=maxx=sx; miny=maxy=sy
            while queue:
                x,y=queue.popleft(); count+=1
                minx=min(minx,x); maxx=max(maxx,x); miny=min(miny,y); maxy=max(maxy,y)
                for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                    if 0<=nx<sw and 0<=ny<sh:
                        ni=ny*sw+nx
                        if not seen[ni] and pixels[nx,ny]:
                            seen[ni]=1; queue.append((nx,ny))
            components.append((count,(minx,miny,maxx+1,maxy+1)))
    if not components:
        raise ValueError("Asset crop contains no visible artwork")
    components.sort(reverse=True, key=lambda item:item[0])
    best_count, best = components[0]
    if best_count < sw*sh*min_fraction:
        raise ValueError("Asset crop principal object is too small")
    inverse = 1/scale
    x0=max(0, round(best[0]*inverse)-4); y0=max(0, round(best[1]*inverse)-4)
    x1=min(width, round(best[2]*inverse)+4); y1=min(height, round(best[3]*inverse)+4)
    return rgba.crop((x0,y0,x1,y1))


def crop_sprite(source: Image.Image, crop: list[float]) -> Image.Image:
    width,height = source.size
    x0,y0,x1,y1 = crop
    piece = source.crop((round(x0*width),round(y0*height),round(x1*width),round(y1*height)))
    return largest_component(remove_near_white(piece))


def icon(draw: ImageDraw.ImageDraw, kind: str, bounds: list[int], colours: dict[str,str]):
    x0,y0,x1,y1=bounds; cx=(x0+x1)//2; cy=(y0+y1)//2; w=x1-x0; h=y1-y0; navy=colours["navy"]
    if kind in {"ball","I spoke clearly"}:
        draw.ellipse([cx-w*.2,cy-h*.28,cx+w*.2,cy+h*.28],fill="#E63B32",outline=navy,width=4)
    elif kind in {"toy car","car","ask to join a game"}:
        draw.rounded_rectangle([cx-w*.28,cy-h*.14,cx+w*.28,cy+h*.16],radius=14,fill="#2787D8",outline=navy,width=4)
        draw.ellipse([cx-w*.22,cy+h*.08,cx-w*.1,cy+h*.22],fill="#333333")
        draw.ellipse([cx+w*.1,cy+h*.08,cx+w*.22,cy+h*.22],fill="#333333")
    elif kind in {"teddy bear","rabbit","dog"}:
        draw.ellipse([cx-w*.2,cy-h*.22,cx+w*.2,cy+h*.2],fill="#C98B52",outline=navy,width=4)
        draw.ellipse([cx-w*.28,cy-h*.32,cx-w*.08,cy-h*.12],fill="#C98B52",outline=navy,width=3)
        draw.ellipse([cx+w*.08,cy-h*.32,cx+w*.28,cy-h*.12],fill="#C98B52",outline=navy,width=3)
    elif kind in {"kite","dinosaur"}:
        draw.polygon([(cx,cy-h*.3),(cx+w*.22,cy),(cx,cy+h*.3),(cx-w*.22,cy)],fill="#E85D9E",outline=navy)
    elif kind=="bench":
        draw.rectangle([cx-w*.3,cy-h*.12,cx+w*.3,cy],fill="#B9773A",outline=navy,width=4)
        draw.rectangle([cx-w*.3,cy+h*.04,cx+w*.3,cy+h*.12],fill="#B9773A",outline=navy,width=4)
    elif kind in {"tree","Living"}:
        draw.rectangle([cx-w*.06,cy,cx+w*.06,cy+h*.3],fill="#9B5E2F",outline=navy,width=3)
        draw.ellipse([cx-w*.26,cy-h*.3,cx+w*.26,cy+h*.1],fill="#55B94C",outline=navy,width=4)
    elif kind=="flower":
        for dx,dy in [(-.12,0),(.12,0),(0,-.16),(0,.16)]:
            draw.ellipse([cx+dx*w-18,cy+dy*h-18,cx+dx*w+18,cy+dy*h+18],fill="#F38BB6",outline=navy,width=2)
        draw.ellipse([cx-18,cy-18,cx+18,cy+18],fill="#FFD24A",outline=navy,width=2)
    elif kind=="child":
        draw.ellipse([cx-w*.12,cy-h*.3,cx+w*.12,cy-h*.05],fill="#F2B887",outline=navy,width=3)
        draw.rounded_rectangle([cx-w*.18,cy-h*.02,cx+w*.18,cy+h*.3],radius=16,fill="#F5C542",outline=navy,width=3)
    elif kind=="chair":
        draw.rectangle([cx-w*.2,cy-h*.2,cx+w*.2,cy+h*.05],fill="#B9773A",outline=navy,width=4)
        draw.rectangle([cx-w*.24,cy+h*.05,cx+w*.24,cy+h*.13],fill="#B9773A",outline=navy,width=4)
    elif kind=="robot":
        draw.rounded_rectangle([cx-w*.22,cy-h*.24,cx+w*.22,cy+h*.2],radius=12,fill="#B8C4D4",outline=navy,width=4)
    else:
        draw.ellipse([cx-w*.18,cy-h*.18,cx+w*.18,cy+h*.18],fill="#FFD24A",outline=navy,width=4)


def card(draw, base, bounds, title, colours, icon_name=None, fill="#FFFFFF"):
    panel(draw,bounds,fill=fill,outline=colours["soft_purple"],width=3,radius=22)
    if icon_name:
        icon(draw,icon_name,[bounds[0]+18,bounds[1]+16,bounds[0]+150,bounds[3]-16],colours)
        text_bounds=[bounds[0]+165,bounds[1]+14,bounds[2]-18,bounds[3]-14]
    else:
        text_bounds=[bounds[0]+20,bounds[1]+12,bounds[2]-20,bounds[3]-12]
    return base.fitted_text(draw,title,text_bounds,max_size=42,min_size=26,colour=colours["navy"],bold=True,max_lines=2)


def draw_header(canvas, draw, contract, template, base):
    colours=template["colours"]; typography=template["typography"]; identity=contract["identity"]
    logo_bounds=[110,35,410,260]
    logo=Image.open(resolve(contract["assets"]["official_logo_path"])).convert("RGBA")
    logo.thumbnail((logo_bounds[2]-logo_bounds[0],logo_bounds[3]-logo_bounds[1]),Image.Resampling.LANCZOS)
    lx=logo_bounds[0]+(logo_bounds[2]-logo_bounds[0]-logo.width)//2
    ly=logo_bounds[1]+(logo_bounds[3]-logo_bounds[1]-logo.height)//2
    canvas.paste(logo,(lx,ly),logo)
    book=base.brand_title(draw,identity["book_title_lines"],[470,45,2320,145],colours,typography)
    title=base.fitted_text(draw,identity["title"],[470,145,2320,285],max_size=typography["page_title_max"],min_size=typography["page_title_min"],colour=colours["navy"],bold=True,max_lines=2)
    draw.rounded_rectangle([150,305,2330,435],radius=24,fill=colours["blue"],outline="#1768B3",width=3)
    objective=base.fitted_text(draw,f"Learning goal: {contract['learning']['objective']}",[185,315,2295,425],max_size=44,min_size=32,colour=colours["navy"],bold=True,max_lines=2)
    draw.rounded_rectangle([150,460,2330,610],radius=26,fill=colours["gold"],outline="#E1B12C",width=3)
    instruction=base.fitted_text(draw,contract["learning"]["student_instruction"],[185,472,2295,598],max_size=52,min_size=38,colour=colours["line"],bold=True,max_lines=2)
    return {"logo":[lx,ly,lx+logo.width,ly+logo.height],"book_title":book,"page_title":title,"objective":objective,"instruction":instruction}


def draw_teacher_strip(draw, contract, template, base):
    colours=template["colours"]
    body=contract["guidance"]["teacher"]["model"]
    bounds=[150,3060,2300,3265]
    panel(draw,bounds,fill="#F0FAED",outline="#5F9D50",width=3,radius=22)
    heading=base.fitted_text(draw,"TEACHER CUE",[180,3082,560,3240],max_size=34,min_size=28,colour=colours["navy"],bold=True,max_lines=1)
    rendered=base.fitted_text(draw,body,[590,3078,2260,3248],max_size=38,min_size=28,colour=colours["line"],align="left",max_lines=3)
    return {"bounds":bounds,"heading":heading,"body":rendered}


def render_read_match(canvas, draw, contract, template, base, source):
    colours=template["colours"]
    phase2=contract["phase2"]
    sprites={name:crop_sprite(source,box) for name,box in phase2["asset_crops"].items()}
    main=[180,650,2300,2200]
    small=[240,2240,2240,3010]
    panel(draw,main,outline=colours["soft_purple"],width=4,radius=30)
    row_height=(main[3]-main[1]-70)//4
    main_items=[]
    for index,(word,picture) in enumerate(zip(phase2["main_words"],phase2["main_picture_order"])):
        centre_y=main[1]+35+row_height*index+row_height//2
        base.fitted_text(draw,word,[245,centre_y-row_height//3,690,centre_y+row_height//3],max_size=84,min_size=64,colour="#111111",bold=True,align="left",max_lines=1)
        left=anchor(draw,(735,centre_y),46,colours["purple"])
        right=anchor(draw,(1510,centre_y),46,colours["purple"])
        picture_bounds=[1570,centre_y-row_height//2+6,2180,centre_y+row_height//2-6]
        rendered_picture=paste_contain(canvas,sprites[picture],picture_bounds,2)
        main_items.append({"word":word,"picture":picture,"left_anchor":left,"right_anchor":right,"picture_bounds":rendered_picture})
    panel(draw,small,outline="#5F9D50",width=4,radius=28)
    base.fitted_text(draw,"Read and match again.",[330,2250,2150,2340],max_size=46,min_size=36,colour=colours["navy"],bold=True,max_lines=1)
    row_height=(small[3]-small[1]-115)//3
    small_items=[]
    for index,(word,picture) in enumerate(zip(phase2["small_words"],phase2["small_picture_order"])):
        centre_y=small[1]+95+row_height*index+row_height//2
        base.fitted_text(draw,word,[330,centre_y-row_height//3,730,centre_y+row_height//3],max_size=70,min_size=52,colour="#111111",bold=True,align="left",max_lines=1)
        left=anchor(draw,(770,centre_y),40,"#3E8F35")
        right=anchor(draw,(1470,centre_y),40,"#3E8F35")
        picture_bounds=[1530,centre_y-row_height//2+2,2160,centre_y+row_height//2-2]
        rendered_picture=paste_contain(canvas,sprites[picture],picture_bounds,0)
        small_items.append({"word":word,"picture":picture,"left_anchor":left,"right_anchor":right,"picture_bounds":rendered_picture})
    return {"type":"phase2-read-match","main":main_items,"small":small_items}


def render_i_can_speak(canvas,draw,contract,template,base,source):
    colours=template["colours"]
    hero=[210,650,2270,1640]
    panel(draw,hero,outline=colours["soft_purple"],width=3)
    hero_render=paste_contain(canvas,remove_near_white(source),hero,24)
    phase2=contract["phase2"]
    cards=[]
    for x,choice,sentence in zip([220,920,1620],phase2["choices"],phase2["sentences"]):
        bounds=[x,1690,x+640,2310]
        panel(draw,bounds,outline=colours["soft_purple"],width=3)
        icon(draw,choice,[x+90,1730,x+550,2020],colours)
        base.fitted_text(draw,sentence,[x+35,2040,x+605,2280],max_size=42,min_size=30,colour=colours["navy"],bold=True,max_lines=3)
        anchor(draw,(x+600,1735),40,colours["purple"])
        cards.append({"choice":choice,"bounds":bounds})
    panel(draw,[330,2360,2150,2650],fill=colours["gold"],outline="#E1B12C",width=3)
    base.fitted_text(draw,contract["learning"]["model_text"],[380,2380,2100,2625],max_size=54,min_size=36,colour=colours["line"],bold=True,max_lines=2)
    panel(draw,[330,2700,2150,2980],fill="#F0FAED",outline="#5F9D50",width=3)
    base.fitted_text(draw,phase2["partner_cue"],[380,2720,2100,2955],max_size=42,min_size=30,colour=colours["navy"],bold=True,max_lines=2)
    return {"type":"phase2-speak-listen","hero":hero_render,"cards":cards}


def render_observe(canvas,draw,contract,template,base,source):
    colours=template["colours"]
    scene=[180,650,2300,2390]
    panel(draw,scene,outline=colours["soft_purple"],width=3)
    scene_render=paste_contain(canvas,remove_near_white(source),scene,20)
    strip=[240,2440,2240,3000]
    panel(draw,strip,outline="#5F9D50",width=3)
    targets=contract["phase2"]["targets"]
    width=(strip[2]-strip[0]-100)//4
    items=[]
    for index,target in enumerate(targets):
        left=strip[0]+30+index*width
        bounds=[left,2480,left+width-25,2950]
        icon(draw,target,[left+30,2500,left+width-55,2810],colours)
        base.fitted_text(draw,target,[left+25,2820,left+width-50,2930],max_size=42,min_size=30,colour=colours["navy"],bold=True,max_lines=1)
        anchor(draw,(left+width-55,2520),38,"#3E8F35")
        items.append({"target":target,"bounds":bounds})
    return {"type":"phase2-observe-find","scene":scene_render,"targets":items}


def render_sort(canvas,draw,contract,template,base,source):
    colours=template["colours"]
    phase2=contract["phase2"]
    cue=[180,650,2300,1240]
    panel(draw,cue,outline=colours["soft_purple"],width=3)
    cue_render=paste_contain(canvas,remove_near_white(source),cue,20)
    area=[180,1290,2300,2070]
    panel(draw,area,outline=colours["soft_purple"],width=3)
    items=[]
    cell_width=(area[2]-area[0]-100)//3
    cell_height=(area[3]-area[1]-80)//2
    for index,name in enumerate(phase2["items"]):
        row,column=divmod(index,3)
        left=area[0]+35+column*cell_width
        top=area[1]+30+row*cell_height
        bounds=[left,top,left+cell_width-25,top+cell_height-25]
        card(draw,base,bounds,name,colours,icon_name=name)
        anchor(draw,(bounds[2]-35,bounds[1]+35),34,colours["purple"])
        items.append({"name":name,"bounds":bounds})
    bins=[]
    for index,label in enumerate(phase2["categories"]):
        left=250+index*1040
        bounds=[left,2120,left+940,3000]
        panel(draw,bounds,fill="#F8F5FF",outline=colours["purple"],width=4)
        icon(draw,label,[left+260,2180,left+680,2530],colours)
        base.fitted_text(draw,label,[left+80,2550,left+860,2730],max_size=60,min_size=42,colour=colours["navy"],bold=True,max_lines=1)
        base.fitted_text(draw,"Place or draw the matching items here.",[left+70,2750,left+870,2960],max_size=36,min_size=27,colour=colours["line"],max_lines=2)
        bins.append({"label":label,"bounds":bounds})
    return {"type":"phase2-sort","cue":cue_render,"items":items,"bins":bins}


def render_creative(canvas,draw,contract,template,base,source):
    colours=template["colours"]
    phase2=contract["phase2"]
    hero=[200,650,2280,1560]
    panel(draw,hero,outline=colours["soft_purple"],width=3)
    hero_render=paste_contain(canvas,remove_near_white(source),hero,18)
    base.fitted_text(draw,"1. Choose a character",[250,1580,2230,1660],max_size=44,min_size=32,colour=colours["navy"],bold=True,max_lines=1)
    characters=[]
    for index,name in enumerate(phase2["characters"]):
        bounds=[250+index*690,1680,850+index*690,2070]
        card(draw,base,bounds,name,colours,icon_name=name)
        anchor(draw,(bounds[2]-40,bounds[1]+40),36,colours["purple"])
        characters.append({"name":name,"bounds":bounds})
    base.fitted_text(draw,"2. Choose a situation",[250,2090,2230,2170],max_size=44,min_size=32,colour=colours["navy"],bold=True,max_lines=1)
    situations=[]
    for index,name in enumerate(phase2["situations"]):
        bounds=[250+index*690,2190,850+index*690,2580]
        card(draw,base,bounds,name,colours,icon_name=name)
        anchor(draw,(bounds[2]-40,bounds[1]+40),36,colours["purple"])
        situations.append({"name":name,"bounds":bounds})
    panel(draw,[300,2620,2180,2805],fill=colours["gold"],outline="#E1B12C",width=3)
    base.fitted_text(draw,contract["learning"]["model_text"],[350,2640,2130,2785],max_size=48,min_size=34,colour=colours["line"],bold=True,max_lines=2)
    checks=[]
    for index,label in enumerate(phase2["self_check"]):
        bounds=[300+index*620,2840,850+index*620,3020]
        card(draw,base,bounds,label,colours,icon_name=label,fill="#F0FAED")
        checks.append({"label":label,"bounds":bounds})
    return {"type":"phase2-creative-speaking","hero":hero_render,"characters":characters,"situations":situations,"self_check":checks}


def compose_phase2(contract_path: Path, output: Path, evidence_output: Path):
    base=load_module("bcube_phase2_base",BASE_PATH)
    contract=load(contract_path)
    template=load(TEMPLATE_PATH)
    page_id=contract["identity"]["page_id"]
    canvas_spec=template["canvas"]
    colours=template["colours"]
    canvas=Image.new("RGB",(canvas_spec["width"],canvas_spec["height"]),colours["background"])
    draw=ImageDraw.Draw(canvas)
    header=draw_header(canvas,draw,contract,template,base)
    source=Image.open(resolve(contract["assets"]["illustration_path"])).convert("RGBA")
    if page_id=="EL-LKG-V4-P023":
        activity=render_read_match(canvas,draw,contract,template,base,source)
    elif page_id=="CC-NURSERY-V4-P022":
        activity=render_i_can_speak(canvas,draw,contract,template,base,source)
    elif page_id=="CE-NURSERY-V4-P010":
        activity=render_observe(canvas,draw,contract,template,base,source)
    elif page_id=="YS-UKG-V4-P010":
        activity=render_sort(canvas,draw,contract,template,base,source)
    elif page_id=="CM-UKG-V4-P032":
        activity=render_creative(canvas,draw,contract,template,base,source)
    else:
        raise ValueError(f"Unsupported Phase 2 pilot page: {page_id}")
    teacher=draw_teacher_strip(draw,contract,template,base)
    page_number=None
    identity=contract["identity"]
    if identity["page_number_visible"] and identity["page_number"]>0:
        page_number=base.fitted_text(draw,str(identity["page_number"]),[2200,3270,2370,3390],max_size=46,min_size=36,colour=colours["muted"],bold=True,max_lines=1)
    output.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(output,"PNG",dpi=(canvas_spec["dpi"],canvas_spec["dpi"]))
    evidence={
        "engine":"BCube Publishing Engine Phase 2 Pilot",
        "page_id":page_id,
        "archetype":contract["phase2"]["archetype"],
        "canvas":canvas_spec,
        "artifact":str(output),
        "artifact_sha256":sha256(output),
        "inputs":{"contract_sha256":sha256(contract_path),"illustration_sha256":sha256(resolve(contract["assets"]["illustration_path"]))},
        "components":{"header":header,"activity":activity,"teacher_cue":teacher,"parent_panel":None,"page_number":page_number},
        "qa":{"parent_panel_removed":True,"generic_activity_box_removed":True,"task_specific_layout":True,"sprite_component_cleanup":page_id=="EL-LKG-V4-P023","print_readable_typography":True,"status":"REVIEW_CANDIDATE"}
    }
    evidence_output.parent.mkdir(parents=True,exist_ok=True)
    evidence_output.write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":"COMPOSED_PHASE2_PILOT","artifact":str(output),"evidence":str(evidence_output)},indent=2))


def compose(contract_path: Path, output: Path, evidence_output: Path):
    contract=load(contract_path)
    page_id=contract.get("identity",{}).get("page_id")
    if page_id in PILOT_IDS and isinstance(contract.get("phase2"),dict):
        compose_phase2(contract_path,output,evidence_output)
    else:
        load_module("bcube_phase2_fallback",FALLBACK_PATH).compose(contract_path,output,evidence_output)


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--contract",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--evidence-output",type=Path,required=True)
    args=parser.parse_args()
    compose(args.contract,args.output,args.evidence_output)
    return 0


if __name__=="__main__":
    try:
        raise SystemExit(main())
    except (ValueError,FileNotFoundError,RuntimeError,json.JSONDecodeError) as exc:
        print(f"BCube Phase 2 learning-page composition FAIL: {exc}",file=__import__("sys").stderr)
        raise SystemExit(2)
