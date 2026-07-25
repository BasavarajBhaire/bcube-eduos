#!/usr/bin/env python3
"""Compose five Phase 2 pilot learning pages with task-specific interaction layouts.

All other learning pages fall back to the existing Learning Page Contract V2
character-aware composer. Phase 2 pages deliberately omit the parent/homework
panel and use one compact, page-specific teacher cue.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
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
    "YS-UKG-V4-P010",
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
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def paste_contain(canvas: Image.Image, image: Image.Image, bounds: list[int], inset: int = 16) -> list[int]:
    rgba = image.convert("RGBA")
    x0, y0, x1, y1 = bounds
    x0 += inset
    y0 += inset
    x1 -= inset
    y1 -= inset
    scale = min((x1 - x0) / rgba.width, (y1 - y0) / rgba.height)
    width = max(1, round(rgba.width * scale))
    height = max(1, round(rgba.height * scale))
    rgba = rgba.resize((width, height), Image.Resampling.LANCZOS)
    left = x0 + (x1 - x0 - width) // 2
    top = y0 + (y1 - y0 - height) // 2
    canvas.paste(rgba, (left, top), rgba)
    return [left, top, left + width, top + height]


def crop_sprite(source: Image.Image, crop: list[float], base) -> Image.Image:
    width, height = source.size
    x0, y0, x1, y1 = crop
    piece = source.crop((round(x0 * width), round(y0 * height), round(x1 * width), round(y1 * height)))
    rgba = piece.convert("RGBA")
    rgba.putdata([
        (255, 255, 255, 0) if r > 246 and g > 246 and b > 246 else (r, g, b, a)
        for r, g, b, a in rgba.getdata()
    ])
    bbox = rgba.getbbox()
    if bbox is None:
        raise ValueError("Asset crop contains no visible artwork")
    return rgba.crop(bbox)


def round_panel(draw: ImageDraw.ImageDraw, bounds: list[int], *, fill: str = "#FFFFFF", outline: str = "#8E5AC7", width: int = 4, radius: int = 28) -> None:
    draw.rounded_rectangle(bounds, radius=radius, fill=fill, outline=outline, width=width)


def circle(draw: ImageDraw.ImageDraw, centre: tuple[int, int], diameter: int, outline: str) -> list[int]:
    x, y = centre
    half = diameter // 2
    bounds = [x - half, y - half, x + half, y + half]
    draw.ellipse(bounds, fill="#FFFFFF", outline=outline, width=4)
    return bounds


def simple_icon(draw: ImageDraw.ImageDraw, kind: str, bounds: list[int], colours: dict[str, str]) -> None:
    x0, y0, x1, y1 = bounds
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    w, h = x1 - x0, y1 - y0
    navy = colours["navy"]
    if kind in {"ball", "I spoke clearly"}:
        draw.ellipse([cx - w * .20, cy - h * .28, cx + w * .20, cy + h * .28], fill="#E63B32", outline=navy, width=4)
    elif kind in {"toy car", "car", "ask to join a game"}:
        draw.rounded_rectangle([cx - w * .28, cy - h * .14, cx + w * .28, cy + h * .16], radius=16, fill="#2787D8", outline=navy, width=4)
        draw.ellipse([cx - w * .22, cy + h * .08, cx - w * .10, cy + h * .22], fill="#333333")
        draw.ellipse([cx + w * .10, cy + h * .08, cx + w * .22, cy + h * .22], fill="#333333")
    elif kind in {"teddy bear", "rabbit", "dog"}:
        draw.ellipse([cx - w * .20, cy - h * .22, cx + w * .20, cy + h * .20], fill="#C98B52", outline=navy, width=4)
        draw.ellipse([cx - w * .28, cy - h * .32, cx - w * .08, cy - h * .12], fill="#C98B52", outline=navy, width=3)
        draw.ellipse([cx + w * .08, cy - h * .32, cx + w * .28, cy - h * .12], fill="#C98B52", outline=navy, width=3)
        draw.ellipse([cx - 6, cy - 2, cx + 6, cy + 10], fill="#222222")
    elif kind in {"kite", "dinosaur"}:
        draw.polygon([(cx, cy - h * .30), (cx + w * .22, cy), (cx, cy + h * .30), (cx - w * .22, cy)], fill="#E85D9E", outline=navy)
        draw.line((cx, cy + h * .30, cx + w * .14, cy + h * .44), fill=navy, width=4)
    elif kind == "bench":
        draw.rectangle([cx - w * .30, cy - h * .12, cx + w * .30, cy], fill="#B9773A", outline=navy, width=4)
        draw.rectangle([cx - w * .30, cy + h * .04, cx + w * .30, cy + h * .12], fill="#B9773A", outline=navy, width=4)
        draw.line((cx - w * .20, cy + h * .12, cx - w * .22, cy + h * .28), fill=navy, width=5)
        draw.line((cx + w * .20, cy + h * .12, cx + w * .22, cy + h * .28), fill=navy, width=5)
    elif kind in {"tree", "Living"}:
        draw.rectangle([cx - w * .06, cy, cx + w * .06, cy + h * .30], fill="#9B5E2F", outline=navy, width=3)
        draw.ellipse([cx - w * .26, cy - h * .30, cx + w * .26, cy + h * .10], fill="#55B94C", outline=navy, width=4)
    elif kind == "flower":
        for dx, dy in [(-.12,0),(.12,0),(0,-.16),(0,.16)]:
            draw.ellipse([cx + dx*w - 18, cy + dy*h - 18, cx + dx*w + 18, cy + dy*h + 18], fill="#F38BB6", outline=navy, width=2)
        draw.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill="#FFD24A", outline=navy, width=2)
    elif kind == "child":
        draw.ellipse([cx - w * .12, cy - h * .30, cx + w * .12, cy - h * .05], fill="#F2B887", outline=navy, width=3)
        draw.rounded_rectangle([cx - w * .18, cy - h * .02, cx + w * .18, cy + h * .30], radius=18, fill="#F5C542", outline=navy, width=3)
    elif kind == "chair":
        draw.rectangle([cx - w * .20, cy - h * .20, cx + w * .20, cy + h * .05], fill="#B9773A", outline=navy, width=4)
        draw.rectangle([cx - w * .24, cy + h * .05, cx + w * .24, cy + h * .13], fill="#B9773A", outline=navy, width=4)
        draw.line((cx - w*.18, cy+h*.13, cx-w*.20, cy+h*.32), fill=navy, width=5)
        draw.line((cx + w*.18, cy+h*.13, cx+w*.20, cy+h*.32), fill=navy, width=5)
    elif kind == "robot":
        draw.rounded_rectangle([cx - w*.22, cy-h*.24, cx+w*.22, cy+h*.20], radius=12, fill="#B8C4D4", outline=navy, width=4)
        draw.ellipse([cx-w*.10, cy-h*.10, cx-w*.04, cy-h*.04], fill="#1768B3")
        draw.ellipse([cx+w*.04, cy-h*.10, cx+w*.10, cy-h*.04], fill="#1768B3")
        draw.line((cx-w*.10, cy+h*.06, cx+w*.10, cy+h*.06), fill=navy, width=4)
    elif kind in {"meet a new friend", "share an exciting idea", "I looked at my partner", "I listened"}:
        draw.ellipse([cx-w*.22, cy-h*.22, cx-w*.04, cy-h*.02], fill="#F2B887", outline=navy, width=3)
        draw.ellipse([cx+w*.04, cy-h*.22, cx+w*.22, cy-h*.02], fill="#D59A6F", outline=navy, width=3)
        draw.line((cx-w*.13, cy+h*.02, cx-w*.13, cy+h*.25), fill=navy, width=8)
        draw.line((cx+w*.13, cy+h*.02, cx+w*.13, cy+h*.25), fill=navy, width=8)
        draw.line((cx-w*.05, cy, cx+w*.05, cy), fill="#E85D9E", width=5)
    else:
        draw.ellipse([cx - w*.18, cy-h*.18, cx+w*.18, cy+h*.18], fill="#FFD24A", outline=navy, width=4)


def card(draw, base, bounds, title, colours, typography, icon=None, fill="#FFFFFF") -> dict[str, Any]:
    round_panel(draw, bounds, fill=fill, outline=colours["soft_purple"], width=3, radius=24)
    if icon:
        icon_bounds = [bounds[0] + 18, bounds[1] + 16, bounds[0] + 150, bounds[3] - 16]
        simple_icon(draw, icon, icon_bounds, colours)
        text_bounds = [bounds[0] + 165, bounds[1] + 14, bounds[2] - 18, bounds[3] - 14]
    else:
        text_bounds = [bounds[0] + 20, bounds[1] + 12, bounds[2] - 20, bounds[3] - 12]
    rendered = base.fitted_text(draw, title, text_bounds, max_size=40, min_size=24, colour=colours["navy"], bold=True, max_lines=2)
    return {"bounds": bounds, "title": title, "text": rendered}


def draw_header(canvas, draw, contract, template, base):
    colours = template["colours"]
    typography = template["typography"]
    identity = contract["identity"]
    logo_bounds = [110, 35, 410, 260]
    logo = Image.open(resolve(contract["assets"]["official_logo_path"])).convert("RGBA")
    logo.thumbnail((logo_bounds[2]-logo_bounds[0], logo_bounds[3]-logo_bounds[1]), Image.Resampling.LANCZOS)
    lx = logo_bounds[0] + (logo_bounds[2]-logo_bounds[0]-logo.width)//2
    ly = logo_bounds[1] + (logo_bounds[3]-logo_bounds[1]-logo.height)//2
    canvas.paste(logo, (lx, ly), logo)
    book = base.brand_title(draw, identity["book_title_lines"], [470, 45, 2320, 145], colours, typography)
    title = base.fitted_text(draw, identity["title"], [470, 145, 2320, 285], max_size=typography["page_title_max"], min_size=typography["page_title_min"], colour=colours["navy"], bold=True, max_lines=2)
    draw.rounded_rectangle([150, 305, 2330, 425], radius=24, fill=colours["blue"], outline="#1768B3", width=3)
    objective = base.fitted_text(draw, f"Learning goal: {contract['learning']['objective']}", [190, 315, 2290, 415], max_size=34, min_size=24, colour=colours["navy"], bold=True, max_lines=2)
    draw.rounded_rectangle([150, 450, 2330, 590], radius=26, fill=colours["gold"], outline="#E1B12C", width=3)
    instruction = base.fitted_text(draw, contract["learning"]["student_instruction"], [190, 462, 2290, 578], max_size=40, min_size=28, colour=colours["line"], bold=True, max_lines=2)
    return {"logo":[lx,ly,lx+logo.width,ly+logo.height],"book_title":book,"page_title":title,"objective":objective,"instruction":instruction}


def draw_teacher_strip(draw, contract, template, base):
    colours = template["colours"]
    body = contract["guidance"]["teacher"]["model"]
    bounds = [150, 3095, 2180, 3255]
    round_panel(draw, bounds, fill="#F0FAED", outline="#5F9D50", width=3, radius=22)
    base.fitted_text(draw, "TEACHER CUE", [175,3110,500,3240], max_size=28, min_size=22, colour=colours["navy"], bold=True, max_lines=1)
    rendered = base.fitted_text(draw, body, [520,3108,2150,3242], max_size=30, min_size=22, colour=colours["line"], align="left", max_lines=3)
    return {"bounds":bounds,"body":rendered}


def render_read_match(canvas, draw, contract, template, base, source):
    colours = template["colours"]
    typography = template["typography"]
    phase2 = contract["phase2"]
    crops = phase2["asset_crops"]
    sprites = {name: crop_sprite(source, box, base) for name, box in crops.items()}
    main = [180, 640, 2300, 2220]
    small = [260, 2270, 2220, 3020]
    round_panel(draw, main, fill="#FFFFFF", outline=colours["soft_purple"], width=4, radius=30)
    row_h = (main[3]-main[1]-80)//4
    rendered=[]
    for i, (word, picture) in enumerate(zip(phase2["main_words"], phase2["main_picture_order"])):
        cy = main[1]+40+row_h*i+row_h//2
        base.fitted_text(draw, word, [250,cy-row_h//3,650,cy+row_h//3], max_size=72, min_size=54, colour="#111111", bold=True, align="left", max_lines=1)
        left_anchor = circle(draw,(720,cy),42,colours["purple"])
        right_anchor = circle(draw,(1640,cy),42,colours["blue"])
        image_bounds=[1710,cy-row_h//2+12,2200,cy+row_h//2-12]
        rb=paste_contain(canvas,sprites[picture],image_bounds,8)
        rendered.append({"word":word,"picture":picture,"left_anchor":left_anchor,"right_anchor":right_anchor,"picture_bounds":rb})
    round_panel(draw, small, fill="#FFFFFF", outline="#5F9D50", width=4, radius=28)
    base.fitted_text(draw,"Read and match again.",[420,2280,2060,2350],max_size=34,min_size=26,colour=colours["navy"],bold=True,max_lines=1)
    row_h=(small[3]-small[1]-110)//3
    small_rendered=[]
    for i,(word,picture) in enumerate(zip(phase2["small_words"],phase2["small_picture_order"])):
        cy=small[1]+90+row_h*i+row_h//2
        base.fitted_text(draw,word,[350,cy-row_h//3,700,cy+row_h//3],max_size=58,min_size=42,colour="#111111",bold=True,align="left",max_lines=1)
        la=circle(draw,(760,cy),36,"#4A9B3A")
        ra=circle(draw,(1580,cy),36,"#4A9B3A")
        pb=[1640,cy-row_h//2+8,2110,cy+row_h//2-8]
        rb=paste_contain(canvas,sprites[picture],pb,6)
        small_rendered.append({"word":word,"picture":picture,"left_anchor":la,"right_anchor":ra,"picture_bounds":rb})
    return {"type":"phase2-read-match","main":rendered,"small":small_rendered}


def render_i_can_speak(canvas, draw, contract, template, base, source):
    colours=template["colours"]
    hero=[210,640,2270,1650]
    round_panel(draw,hero,fill="#FFFFFF",outline=colours["soft_purple"],width=3)
    hero_render=paste_contain(canvas,base.remove_near_white(source),hero,26)
    phase2=contract["phase2"]
    cards=[]
    x_positions=[220,920,1620]
    for x,choice,sentence in zip(x_positions,phase2["choices"],phase2["sentences"]):
        bounds=[x,1710,x+640,2320]
        round_panel(draw,bounds,fill="#FFFFFF",outline=colours["soft_purple"],width=3)
        simple_icon(draw,choice,[x+90,1750,x+550,2030],colours)
        base.fitted_text(draw,sentence,[x+35,2050,x+605,2280],max_size=38,min_size=26,colour=colours["navy"],bold=True,max_lines=3)
        circle(draw,(x+600,1755),38,colours["purple"])
        cards.append({"choice":choice,"bounds":bounds})
    round_panel(draw,[330,2380,2150,2670],fill=colours["gold"],outline="#E1B12C",width=3)
    base.fitted_text(draw,contract["learning"]["model_text"],[380,2405,2100,2645],max_size=50,min_size=32,colour=colours["line"],bold=True,max_lines=2)
    round_panel(draw,[330,2720,2150,2980],fill="#F0FAED",outline="#5F9D50",width=3)
    base.fitted_text(draw,phase2["partner_cue"],[380,2740,2100,2960],max_size=38,min_size=28,colour=colours["navy"],bold=True,max_lines=2)
    return {"type":"phase2-speak-listen","hero":hero_render,"cards":cards}


def render_observe(canvas, draw, contract, template, base, source):
    colours=template["colours"]
    scene=[180,640,2300,2410]
    round_panel(draw,scene,fill="#FFFFFF",outline=colours["soft_purple"],width=3)
    scene_render=paste_contain(canvas,base.remove_near_white(source),scene,22)
    strip=[240,2470,2240,2990]
    round_panel(draw,strip,fill="#FFFFFF",outline="#5F9D50",width=3)
    targets=contract["phase2"]["targets"]
    width=(strip[2]-strip[0]-100)//4
    items=[]
    for i,target in enumerate(targets):
        left=strip[0]+30+i*width
        bounds=[left,2510,left+width-25,2940]
        simple_icon(draw,target,[left+30,2530,left+width-55,2800],colours)
        base.fitted_text(draw,target,[left+25,2810,left+width-50,2915],max_size=34,min_size=25,colour=colours["navy"],bold=True,max_lines=1)
        circle(draw,(left+width-55,2550),34,"#4A9B3A")
        items.append({"target":target,"bounds":bounds})
    return {"type":"phase2-observe-find","scene":scene_render,"targets":items}


def render_sort(canvas, draw, contract, template, base, source):
    colours=template["colours"]
    phase2=contract["phase2"]
    cue=[180,640,2300,1260]
    round_panel(draw,cue,fill="#FFFFFF",outline=colours["soft_purple"],width=3)
    cue_render=paste_contain(canvas,base.remove_near_white(source),cue,22)
    item_area=[180,1310,2300,2100]
    round_panel(draw,item_area,fill="#FFFFFF",outline=colours["soft_purple"],width=3)
    items=[]
    cols=3
    cell_w=(item_area[2]-item_area[0]-100)//cols
    cell_h=(item_area[3]-item_area[1]-80)//2
    for i,name in enumerate(phase2["items"]):
        row,col=divmod(i,cols)
        left=item_area[0]+35+col*cell_w
        top=item_area[1]+30+row*cell_h
        bounds=[left,top,left+cell_w-25,top+cell_h-25]
        card(draw,base,bounds,name,colours,template["typography"],icon=name)
        circle(draw,(bounds[2]-35,bounds[1]+35),32,colours["purple"])
        items.append({"name":name,"bounds":bounds})
    bins=[]
    for i,label_text in enumerate(phase2["categories"]):
        left=250+i*1040
        bounds=[left,2160,left+940,2990]
        round_panel(draw,bounds,fill="#F8F5FF",outline=colours["purple"],width=4)
        simple_icon(draw,label_text,[left+260,2220,left+680,2550],colours)
        base.fitted_text(draw,label_text,[left+80,2580,left+860,2740],max_size=54,min_size=38,colour=colours["navy"],bold=True,max_lines=1)
        base.fitted_text(draw,"Place or draw the matching items here.",[left+70,2760,left+870,2950],max_size=31,min_size=24,colour=colours["line"],max_lines=2)
        bins.append({"label":label_text,"bounds":bounds})
    return {"type":"phase2-sort","cue":cue_render,"items":items,"bins":bins}


def render_creative_speaking(canvas, draw, contract, template, base, source):
    colours=template["colours"]
    hero=[200,640,2280,1580]
    round_panel(draw,hero,fill="#FFFFFF",outline=colours["soft_purple"],width=3)
    hero_render=paste_contain(canvas,base.remove_near_white(source),hero,20)
    phase2=contract["phase2"]
    base.fitted_text(draw,"1. Choose a character",[250,1610,2230,1680],max_size=38,min_size=28,colour=colours["navy"],bold=True,max_lines=1)
    characters=[]
    for i,name in enumerate(phase2["characters"]):
        bounds=[250+i*690,1700,850+i*690,2080]
        card(draw,base,bounds,name,colours,template["typography"],icon=name)
        circle(draw,(bounds[2]-40,bounds[1]+40),34,colours["purple"])
        characters.append({"name":name,"bounds":bounds})
    base.fitted_text(draw,"2. Choose a situation",[250,2110,2230,2180],max_size=38,min_size=28,colour=colours["navy"],bold=True,max_lines=1)
    situations=[]
    for i,name in enumerate(phase2["situations"]):
        bounds=[250+i*690,2200,850+i*690,2580]
        card(draw,base,bounds,name,colours,template["typography"],icon=name)
        circle(draw,(bounds[2]-40,bounds[1]+40),34,colours["purple"])
        situations.append({"name":name,"bounds":bounds})
    round_panel(draw,[300,2630,2180,2810],fill=colours["gold"],outline="#E1B12C",width=3)
    base.fitted_text(draw,contract["learning"]["model_text"],[350,2650,2130,2790],max_size=44,min_size=30,colour=colours["line"],bold=True,max_lines=2)
    checks=[]
    for i,label_text in enumerate(phase2["self_check"]):
        bounds=[300+i*620,2850,850+i*620,3030]
        card(draw,base,bounds,label_text,colours,template["typography"],icon=label_text,fill="#F0FAED")
        checks.append({"label":label_text,"bounds":bounds})
    return {"type":"phase2-creative-speaking","hero":hero_render,"characters":characters,"situations":situations,"self_check":checks}


def compose_phase2(contract_path: Path, output: Path, evidence_output: Path) -> None:
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
        activity=render_creative_speaking(canvas,draw,contract,template,base,source)
    else:
        raise ValueError(f"Unsupported Phase 2 pilot page: {page_id}")
    teacher=draw_teacher_strip(draw,contract,template,base)
    page_number=None
    identity=contract["identity"]
    if identity["page_number_visible"] and identity["page_number"]>0:
        page_number=base.fitted_text(draw,str(identity["page_number"]),[2200,3270,2370,3390],max_size=44,min_size=34,colour=colours["muted"],bold=True,max_lines=1)
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
        "qa":{"parent_panel_removed":True,"generic_activity_box_removed":True,"task_specific_layout":True,"status":"REVIEW_CANDIDATE"}
    }
    evidence_output.parent.mkdir(parents=True,exist_ok=True)
    evidence_output.write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":"COMPOSED_PHASE2_PILOT","artifact":str(output),"evidence":str(evidence_output)},indent=2))


def compose(contract_path: Path, output: Path, evidence_output: Path) -> None:
    contract=load(contract_path)
    page_id=contract.get("identity",{}).get("page_id")
    if page_id in PILOT_IDS and isinstance(contract.get("phase2"),dict):
        compose_phase2(contract_path,output,evidence_output)
        return
    fallback=load_module("bcube_phase2_fallback",FALLBACK_PATH)
    fallback.compose(contract_path,output,evidence_output)


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
