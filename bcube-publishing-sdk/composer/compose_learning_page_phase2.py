#!/usr/bin/env python3
"""Task-specific Phase 2 composer for five BCube pilot learning pages.

Every visual choice is extracted from the uploaded illustration artwork through
page-owned named crop manifests. Generic replacement icons are prohibited.
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
    "EL-LKG-V4-P023",
    "CC-NURSERY-V4-P022",
    "CE-NURSERY-V4-P010",
    "ST-LKG-V4-P010",
    "CM-UKG-V4-P032",
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


def panel(draw: ImageDraw.ImageDraw, bounds: list[int], fill="#FFFFFF", outline="#8E5AC7", width=4, radius=28) -> None:
    draw.rounded_rectangle(bounds, radius=radius, fill=fill, outline=outline, width=width)


def anchor(draw: ImageDraw.ImageDraw, centre: tuple[int, int], diameter: int, outline: str) -> list[int]:
    x, y = centre
    half = diameter // 2
    bounds = [x-half, y-half, x+half, y+half]
    draw.ellipse(bounds, fill="#FFFFFF", outline=outline, width=6)
    return bounds


def paste_contain(canvas: Image.Image, image: Image.Image, bounds: list[int], inset=8) -> list[int]:
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


def largest_component(image: Image.Image, min_fraction: float = 0.012) -> Image.Image:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    width, height = rgba.size
    scale = min(1.0, 520/max(width, height))
    sw, sh = max(1, round(width*scale)), max(1, round(height*scale))
    mask = alpha.resize((sw, sh), Image.Resampling.NEAREST).point(lambda p: 255 if p>18 else 0)
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
                x,y = queue.popleft(); count += 1
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
    count, box = components[0]
    if count < sw*sh*min_fraction:
        raise ValueError("Asset crop principal object is too small")
    inverse = 1/scale
    x0=max(0,round(box[0]*inverse)-5); y0=max(0,round(box[1]*inverse)-5)
    x1=min(width,round(box[2]*inverse)+5); y1=min(height,round(box[3]*inverse)+5)
    return rgba.crop((x0,y0,x1,y1))


def crop_sprite(source: Image.Image, crop: list[float], keep_all=False) -> Image.Image:
    width,height = source.size
    x0,y0,x1,y1 = crop
    piece = source.crop((round(x0*width),round(y0*height),round(x1*width),round(y1*height)))
    cleaned = remove_near_white(piece)
    return cleaned if keep_all else largest_component(cleaned)


def crop_assets(source: Image.Image, phase2: dict[str, Any], keep_all: set[str] | None = None) -> dict[str, Image.Image]:
    crops = phase2.get("asset_crops")
    if not isinstance(crops, dict) or not crops:
        raise ValueError("Phase 2 page requires a named asset_crops manifest")
    keep_all = keep_all or set()
    return {name: crop_sprite(source, box, name in keep_all) for name, box in crops.items()}


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
    bounds=[150,3060,2300,3265]
    panel(draw,bounds,fill="#F0FAED",outline="#5F9D50",width=3,radius=22)
    heading=base.fitted_text(draw,"TEACHER CUE",[180,3082,560,3240],max_size=34,min_size=28,colour=colours["navy"],bold=True,max_lines=1)
    body=base.fitted_text(draw,contract["guidance"]["teacher"]["model"],[590,3078,2260,3248],max_size=38,min_size=28,colour=colours["line"],align="left",max_lines=3)
    return {"bounds":bounds,"heading":heading,"body":body}


def draw_asset_card(canvas, draw, base, colours, bounds, asset, label, *, anchor_visible=True, number=None):
    panel(draw,bounds,outline=colours["soft_purple"],width=3,radius=22)
    picture_bounds=[bounds[0]+40,bounds[1]+35,bounds[2]-40,bounds[3]-105]
    rendered=paste_contain(canvas,asset,picture_bounds,4)
    text=base.fitted_text(draw,label,[bounds[0]+25,bounds[3]-100,bounds[2]-25,bounds[3]-20],max_size=40,min_size=28,colour=colours["navy"],bold=True,max_lines=2)
    marker=None
    if anchor_visible:
        marker=anchor(draw,(bounds[2]-38,bounds[1]+38),36,colours["purple"])
    if number is not None:
        draw.ellipse([bounds[0]+18,bounds[1]+18,bounds[0]+78,bounds[1]+78],fill="#FFFFFF",outline=colours["purple"],width=4)
        base.fitted_text(draw,str(number),[bounds[0]+20,bounds[1]+20,bounds[0]+76,bounds[1]+76],max_size=34,min_size=28,colour=colours["navy"],bold=True,max_lines=1)
    return {"bounds":bounds,"picture":rendered,"label":text,"anchor":marker,"number":number}


def render_read_match(canvas, draw, contract, template, base, source):
    colours=template["colours"]; phase2=contract["phase2"]
    sprites=crop_assets(source,phase2)
    main=[180,650,2300,2200]; small=[240,2240,2240,3010]
    panel(draw,main,outline=colours["soft_purple"],width=4,radius=30)
    row_h=(main[3]-main[1]-70)//4; main_items=[]
    for i,(word,picture) in enumerate(zip(phase2["main_words"],phase2["main_picture_order"])):
        cy=main[1]+35+row_h*i+row_h//2
        base.fitted_text(draw,word,[245,cy-row_h//3,690,cy+row_h//3],max_size=84,min_size=64,colour="#111111",bold=True,align="left",max_lines=1)
        left=anchor(draw,(735,cy),46,colours["purple"]); right=anchor(draw,(1510,cy),46,colours["purple"])
        picture_bounds=paste_contain(canvas,sprites[picture],[1570,cy-row_h//2+6,2180,cy+row_h//2-6],2)
        main_items.append({"word":word,"picture":picture,"left_anchor":left,"right_anchor":right,"picture_bounds":picture_bounds})
    panel(draw,small,outline="#5F9D50",width=4,radius=28)
    base.fitted_text(draw,"Read and match again.",[330,2250,2150,2340],max_size=46,min_size=36,colour=colours["navy"],bold=True,max_lines=1)
    row_h=(small[3]-small[1]-115)//3; small_items=[]
    for i,(word,picture) in enumerate(zip(phase2["small_words"],phase2["small_picture_order"])):
        cy=small[1]+95+row_h*i+row_h//2
        base.fitted_text(draw,word,[330,cy-row_h//3,730,cy+row_h//3],max_size=70,min_size=52,colour="#111111",bold=True,align="left",max_lines=1)
        left=anchor(draw,(770,cy),40,"#3E8F35"); right=anchor(draw,(1470,cy),40,"#3E8F35")
        picture_bounds=paste_contain(canvas,sprites[picture],[1530,cy-row_h//2+2,2160,cy+row_h//2-2],0)
        small_items.append({"word":word,"picture":picture,"left_anchor":left,"right_anchor":right,"picture_bounds":picture_bounds})
    return {"type":"phase2-read-match","main":main_items,"small":small_items}


def render_i_can_speak(canvas, draw, contract, template, base, source):
    colours=template["colours"]; phase2=contract["phase2"]
    assets=crop_assets(source,phase2,keep_all={"model_scene"})
    hero=[210,650,2270,1600]; panel(draw,hero,outline=colours["soft_purple"],width=3)
    hero_render=paste_contain(canvas,assets["model_scene"],hero,20)
    cards=[]
    for index,(choice,sentence) in enumerate(zip(phase2["choices"],phase2["sentences"])):
        x=220+index*700; bounds=[x,1660,x+640,2310]
        cards.append(draw_asset_card(canvas,draw,base,colours,bounds,assets[choice],sentence))
    panel(draw,[330,2360,2150,2640],fill=colours["gold"],outline="#E1B12C",width=3)
    phrase=base.fitted_text(draw,contract["learning"]["model_text"],[380,2385,2100,2615],max_size=54,min_size=36,colour=colours["line"],bold=True,max_lines=2)
    panel(draw,[330,2690,2150,2975],fill="#F0FAED",outline="#5F9D50",width=3)
    partner=base.fitted_text(draw,phase2["partner_cue"],[380,2715,2100,2950],max_size=42,min_size=30,colour=colours["navy"],bold=True,max_lines=2)
    return {"type":"phase2-speak-listen","hero":hero_render,"cards":cards,"phrase":phrase,"partner":partner}


def render_observe(canvas, draw, contract, template, base, source):
    colours=template["colours"]; phase2=contract["phase2"]
    assets=crop_assets(source,phase2,keep_all={"scene"})
    scene=[180,650,2300,2360]; panel(draw,scene,outline=colours["soft_purple"],width=3)
    scene_render=paste_contain(canvas,assets["scene"],scene,18)
    strip=[220,2410,2260,3000]; panel(draw,strip,outline="#5F9D50",width=3)
    cards=[]
    for index,target in enumerate(phase2["targets"]):
        left=250+index*500; bounds=[left,2460,left+450,2945]
        cards.append(draw_asset_card(canvas,draw,base,colours,bounds,assets[target],target))
    return {"type":"phase2-observe-find","scene":scene_render,"targets":cards}


def render_sort(canvas, draw, contract, template, base, source):
    colours=template["colours"]; phase2=contract["phase2"]
    assets=crop_assets(source,phase2)
    item_area=[180,650,2300,1900]; panel(draw,item_area,outline=colours["soft_purple"],width=3)
    cards=[]
    for index,name in enumerate(phase2["items"]):
        row,column=divmod(index,3)
        left=220+column*700; top=700+row*575; bounds=[left,top,left+640,top+520]
        cards.append(draw_asset_card(canvas,draw,base,colours,bounds,assets[name],name,anchor_visible=False,number=index+1))
    groups=[]
    for index,label in enumerate(phase2["categories"]):
        left=250+index*1040; bounds=[left,1960,left+940,2990]
        panel(draw,bounds,fill="#F8F5FF",outline=colours["purple"],width=4)
        title=base.fitted_text(draw,label,[left+60,1990,left+880,2120],max_size=58,min_size=42,colour=colours["navy"],bold=True,max_lines=1)
        cue=base.fitted_text(draw,"Write the picture numbers.",[left+80,2140,left+860,2240],max_size=34,min_size=26,colour=colours["line"],max_lines=1)
        lines=[]
        for line_index in range(3):
            y=2340+line_index*190
            draw.line((left+150,y,left+790,y),fill="#7C8799",width=3)
            lines.append([left+150,y,left+790,y])
        groups.append({"label":label,"bounds":bounds,"title":title,"cue":cue,"lines":lines})
    return {"type":"phase2-sort-number-record","items":cards,"groups":groups}


def render_creative(canvas, draw, contract, template, base, source):
    colours=template["colours"]; phase2=contract["phase2"]
    assets=crop_assets(source,phase2,keep_all={"model_scene","meet a new friend","ask to join a game","share an exciting idea"})
    hero=[200,650,2280,1470]; panel(draw,hero,outline=colours["soft_purple"],width=3)
    hero_render=paste_contain(canvas,assets["model_scene"],hero,18)
    base.fitted_text(draw,"1. Choose a character",[250,1490,2230,1575],max_size=44,min_size=32,colour=colours["navy"],bold=True,max_lines=1)
    character_cards=[]
    for index,name in enumerate(phase2["characters"]):
        bounds=[240+index*700,1590,870+index*700,2070]
        character_cards.append(draw_asset_card(canvas,draw,base,colours,bounds,assets[name],name))
    base.fitted_text(draw,"2. Choose a situation",[250,2090,2230,2175],max_size=44,min_size=32,colour=colours["navy"],bold=True,max_lines=1)
    situation_cards=[]
    for index,name in enumerate(phase2["situations"]):
        bounds=[240+index*700,2190,870+index*700,2620]
        situation_cards.append(draw_asset_card(canvas,draw,base,colours,bounds,assets[name],name))
    panel(draw,[300,2650,2180,2825],fill=colours["gold"],outline="#E1B12C",width=3)
    phrase=base.fitted_text(draw,contract["learning"]["model_text"],[350,2670,2130,2805],max_size=48,min_size=34,colour=colours["line"],bold=True,max_lines=2)
    checks=[]
    for index,label in enumerate(phase2["self_check"]):
        bounds=[300+index*620,2850,850+index*620,3025]
        panel(draw,bounds,fill="#F0FAED",outline=colours["soft_purple"],width=3,radius=20)
        marker=anchor(draw,(bounds[0]+55,(bounds[1]+bounds[3])//2),38,"#3E8F35")
        text=base.fitted_text(draw,label,[bounds[0]+95,bounds[1]+18,bounds[2]-20,bounds[3]-18],max_size=34,min_size=25,colour=colours["navy"],bold=True,max_lines=2)
        checks.append({"label":label,"bounds":bounds,"marker":marker,"text":text})
    return {"type":"phase2-creative-speaking","hero":hero_render,"characters":character_cards,"situations":situation_cards,"phrase":phrase,"self_check":checks}


def compose_phase2(contract_path: Path, output: Path, evidence_output: Path) -> None:
    base=load_module("bcube_phase2_base",BASE_PATH)
    contract=load(contract_path); template=load(TEMPLATE_PATH)
    page_id=contract["identity"]["page_id"]
    canvas_spec=template["canvas"]; colours=template["colours"]
    canvas=Image.new("RGB",(canvas_spec["width"],canvas_spec["height"]),colours["background"])
    draw=ImageDraw.Draw(canvas)
    header=draw_header(canvas,draw,contract,template,base)
    source=Image.open(resolve(contract["assets"]["illustration_path"])).convert("RGBA")
    renderers={
        "EL-LKG-V4-P023":render_read_match,
        "CC-NURSERY-V4-P022":render_i_can_speak,
        "CE-NURSERY-V4-P010":render_observe,
        "ST-LKG-V4-P010":render_sort,
        "CM-UKG-V4-P032":render_creative,
    }
    if page_id not in renderers:
        raise ValueError(f"Unsupported Phase 2 pilot page: {page_id}")
    activity=renderers[page_id](canvas,draw,contract,template,base,source)
    teacher=draw_teacher_strip(draw,contract,template,base)
    identity=contract["identity"]
    page_number=None
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
        "qa":{"parent_panel_removed":True,"generic_activity_box_removed":True,"generic_replacement_icons_removed":True,"named_asset_crop_manifest_used":True,"task_specific_layout":True,"print_readable_typography":True,"status":"REVIEW_CANDIDATE"}
    }
    evidence_output.parent.mkdir(parents=True,exist_ok=True)
    evidence_output.write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":"COMPOSED_PHASE2_PILOT","artifact":str(output),"evidence":str(evidence_output)},indent=2))


def compose(contract_path: Path, output: Path, evidence_output: Path) -> None:
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
