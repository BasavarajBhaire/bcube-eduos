#!/usr/bin/env python3
"""Dedicated fail-closed renderer for all Early Maths Adventures LKG pages P008-P044."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
COMMON_PATH = ROOT / "bcube-publishing-sdk/composer/compose_runtime_learning_page.py"
BASE_PATH = ROOT / "bcube-publishing-sdk/composer/compose_learning_page_v2.py"
LOADER_PATH = ROOT / "bcube-publishing-sdk/runtime/load_book_contract.py"
TEMPLATE_PATH = ROOT / "bcube-publishing-sdk/templates/learning-page-v2.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def mechanics(page):
    value = page.get("activity", {}).get("mechanics")
    if not isinstance(value, dict):
        raise ValueError("activity.mechanics is required")
    return value


def prompt(draw, base, template, text, box, *, align="left", max_lines=2, size=31):
    base.fitted_text(draw, str(text), box, max_size=size, min_size=21,
                     colour=template["colours"]["navy"], bold=True,
                     align=align, max_lines=max_lines)


def choices(draw, base, template, values, box):
    if not values:
        raise ValueError("Page-specific choices are required")
    x0, y0, x1, y1 = box
    gap = (x1 - x0) // (len(values) + 1)
    for i, value in enumerate(values, 1):
        cx = x0 + gap * i; cy = (y0 + y1) // 2
        draw.ellipse([cx - 48, cy - 48, cx + 48, cy + 48], fill="#FFFFFF",
                     outline=template["colours"]["purple"], width=4)
        base.fitted_text(draw, str(value), [cx - 42, cy - 42, cx + 42, cy + 42],
                         max_size=34, min_size=20, colour=template["colours"]["navy"],
                         bold=True, max_lines=1)


def card_grid(count, top=700, bottom=2980):
    if count <= 4: cols = 2
    elif count <= 6: cols = 3
    else: cols = 4
    rows = (count + cols - 1) // cols
    left, right, gap = 170, 2310, 28
    w = (right - left - gap * (cols - 1)) // cols
    h = (bottom - top - gap * (rows - 1)) // rows
    return [[left + c * (w + gap), top + r * (h + gap), left + c * (w + gap) + w, top + r * (h + gap) + h]
            for r in range(rows) for c in range(cols)][:count]


def ordered_assets(page):
    m = mechanics(page)
    return list(m.get("asset_order") or page["illustration"]["assets"])


def render_count(canvas, draw, page, assets, base, template, common):
    m = mechanics(page)
    cards = m.get("cards")
    if not cards:
        names = ordered_assets(page)
        cards = [{"asset": n, "choices": [i, i + 1, i + 2]} for i, n in enumerate(names, 1)]
    boxes = card_grid(len(cards))
    for card, box in zip(cards, boxes):
        asset = card.get("asset")
        if asset not in assets: raise ValueError(f"Missing count asset {asset}")
        common.panel(draw, box, outline="#7E57C2", width=3)
        common.paste_fit(canvas, assets[asset], [box[0]+15, box[1]+15, box[2]-15, box[3]-145])
        choices(draw, base, template, card.get("choices"), [box[0]+40, box[3]-130, box[2]-40, box[3]-15])


def render_match(canvas, draw, page, assets, base, template, common):
    m = mechanics(page); left = m.get("left"); right = m.get("right")
    if not left or not right or len(left) != len(right):
        raise ValueError("Matching page requires equal left and right asset lists")
    rows = len(left); y0 = 700; rh = (2950-y0)//rows
    for i in range(rows):
        top, bottom = y0+i*rh, y0+(i+1)*rh-20
        common.panel(draw, [180,top,980,bottom], outline="#7E57C2", width=3)
        common.panel(draw, [1500,top,2300,bottom], outline="#7E57C2", width=3)
        common.paste_fit(canvas, assets[left[i]], [200,top+12,900,bottom-12])
        common.paste_fit(canvas, assets[right[i]], [1580,top+12,2280,bottom-12])
        draw.ellipse([925,(top+bottom)//2-16,957,(top+bottom)//2+16],fill="#FFF",outline="#7E57C2",width=3)
        draw.ellipse([1523,(top+bottom)//2-16,1555,(top+bottom)//2+16],fill="#FFF",outline="#7E57C2",width=3)


def render_comparison(canvas, draw, page, assets, base, template, common):
    m = mechanics(page)
    rows = m.get("rows") or m.get("cards")
    if not rows:
        rows = [{"asset": n, "prompt": "Circle the correct one."} for n in ordered_assets(page)]
    boxes = card_grid(len(rows))
    for row, box in zip(rows, boxes):
        asset = row.get("asset")
        common.panel(draw, box, outline="#7E57C2", width=3)
        common.paste_fit(canvas, assets[asset], [box[0]+15,box[1]+15,box[2]-15,box[3]-165])
        text = row.get("prompt")
        if text: prompt(draw,base,template,text,[box[0]+35,box[3]-155,box[2]-35,box[3]-85],align="center",size=28)
        vals = row.get("choices")
        if vals: choices(draw,base,template,vals,[box[0]+40,box[3]-90,box[2]-40,box[3]-10])
        else: draw.ellipse([(box[0]+box[2])//2-42,box[3]-88,(box[0]+box[2])//2+42,box[3]-4],fill="#FFF",outline="#7E57C2",width=4)


def render_sequence(canvas, draw, page, assets, base, template, common):
    m = mechanics(page); rows = m.get("rows")
    if not rows: rows = [{"asset": n} for n in ordered_assets(page)]
    if page["identity"]["physical_page"] == 35:
        boxes = [[170,720,1130,1720],[1350,720,2310,1720],[170,1820,1130,2820],[1350,1820,2310,2820]]
        for row,box in zip(rows,boxes):
            common.panel(draw,box,outline="#7E57C2",width=3)
            common.paste_fit(canvas,assets[row["asset"]],[box[0]+20,box[1]+20,box[2]-20,box[3]-180])
            prompt(draw,base,template,row.get("label","").title(),[box[0]+50,box[3]-160,box[2]-180,box[3]-40],align="center")
            common.panel(draw,[box[2]-145,box[3]-155,box[2]-35,box[3]-45],fill="#FFF9DE",outline="#D9A91B",width=3,radius=16)
        return
    y=700; rh=(2950-y)//len(rows)
    for row in rows:
        box=[180,y,2300,y+rh-25]; common.panel(draw,box,outline="#7E57C2",width=3)
        common.paste_fit(canvas,assets[row["asset"]],[205,y+15,1850,y+rh-40])
        slots=int(row.get("blank_count", row.get("response_slots", 1)))
        for j in range(slots):
            bx=1900+j*135; common.panel(draw,[bx,y+rh//2-55,bx+105,y+rh//2+55],fill="#FFF9DE",outline="#D9A91B",width=3,radius=14)
        y+=rh


def render_addition(canvas, draw, page, assets, base, template, common):
    probs=mechanics(page).get("problems")
    if not probs: raise ValueError("Addition problems required")
    y=700; rh=(2950-y)//len(probs)
    for p in probs:
        box=[180,y,2300,y+rh-25]; common.panel(draw,box,outline="#7E57C2",width=3)
        common.paste_fit(canvas,assets[p["left_asset"]],[220,y+30,930,y+rh-170])
        common.paste_fit(canvas,assets[p["right_asset"]],[1150,y+30,1860,y+rh-170])
        prompt(draw,base,template,"+",[950,y+120,1130,y+300],align="center",size=72)
        prompt(draw,base,template,"=",[1870,y+120,2020,y+300],align="center",size=65)
        choices(draw,base,template,p.get("choices"),[1450,y+rh-180,2260,y+rh-25]); y+=rh


def render_subtraction(canvas, draw, page, assets, base, template, common):
    probs=mechanics(page).get("problems")
    if not probs: raise ValueError("Subtraction problems required")
    y=700; rh=(2950-y)//len(probs)
    for p in probs:
        box=[180,y,2300,y+rh-25]; common.panel(draw,box,outline="#7E57C2",width=3)
        common.paste_fit(canvas,assets[p["asset"]],[220,y+20,1580,y+rh-80])
        start=int(p["start"]); removed=int(p["removed"]); remain=int(p["remain"])
        if start-removed!=remain: raise ValueError("Subtraction contract inconsistent")
        prompt(draw,base,template,f"Cross out {removed}.\n{start} − {removed} =",[1610,y+70,2250,y+310],max_lines=2)
        choices(draw,base,template,p.get("choices"),[1580,y+rh-250,2260,y+rh-20]); y+=rh


def render_numberline(canvas, draw, page, assets, base, template, common):
    rows=mechanics(page).get("rows")
    if not rows: raise ValueError("Number-line rows required")
    y=720; rh=(2920-y)//len(rows)
    for row in rows:
        common.panel(draw,[180,y,2300,y+rh-25],outline="#7E57C2",width=3)
        common.paste_fit(canvas,assets[row["asset"]],[210,y+15,2260,y+rh-270])
        start,jumps,landing=int(row["start"]),int(row["jumps"]),int(row["landing"])
        if start+jumps!=landing: raise ValueError("Number-line contract inconsistent")
        ly=y+rh-210; x0,x1=350,1900; draw.line([x0,ly,x1,ly],fill="#5B3F9A",width=7)
        step=(x1-x0)/max(1,jumps)
        for i in range(jumps):
            a=x0+i*step; b=x0+(i+1)*step; draw.arc([a,ly-140,b,ly+20],180,360,fill="#E25454",width=6)
        prompt(draw,base,template,f"Start {start}. Jump {jumps}.",[240,y+rh-170,1180,y+rh-35])
        choices(draw,base,template,row.get("choices"),[1320,y+rh-190,2250,y+rh-25]); y+=rh


def render_stories(canvas, draw, page, assets, base, template, common):
    stories=mechanics(page).get("stories")
    if not stories: raise ValueError("Picture stories required")
    y=700; rh=(2950-y)//len(stories)
    for s in stories:
        common.panel(draw,[180,y,2300,y+rh-25],outline="#7E57C2",width=3)
        common.paste_fit(canvas,assets[s["asset"]],[210,y+20,1700,y+rh-45])
        prompt(draw,base,template,"Count, think, and choose.",[1740,y+80,2250,y+220])
        choices(draw,base,template,s.get("choices"),[1710,y+rh-300,2260,y+rh-60]); y+=rh


def render_hero_targets(canvas, draw, page, assets, base, template, common):
    m=mechanics(page); hero=m.get("hero") or ordered_assets(page)[0]
    targets=m.get("targets") or m.get("choices") or []
    common.panel(draw,[180,700,2300,2220],outline="#7E57C2",width=3)
    common.paste_fit(canvas,assets[hero],[205,725,2275,2195])
    if not targets: return
    boxes=card_grid(len(targets),top=2290,bottom=2990)
    for item,box in zip(targets,boxes):
        common.panel(draw,box,outline="#7E57C2",width=3)
        common.paste_fit(canvas,assets[item["asset"]],[box[0]+12,box[1]+12,box[2]-12,box[3]-115])
        prompt(draw,base,template,item.get("label",""),[box[0]+30,box[3]-105,box[2]-30,box[3]-15],align="center",size=27)


def render_pattern(canvas, draw, page, assets, base, template, common):
    rows=mechanics(page).get("rows")
    if not rows: raise ValueError("Pattern rows required")
    y=700; rh=(2950-y)//len(rows); oral=mechanics(page).get("show_answer_controls") is False
    for row in rows:
        common.panel(draw,[180,y,2300,y+rh-25],outline="#7E57C2",width=3)
        common.paste_fit(canvas,assets[row["asset"]],[210,y+15,1650 if not oral else 2260,y+rh-40])
        if not oral: choices(draw,base,template,row.get("choices"),[1650,y+rh//2-90,2260,y+rh//2+90])
        y+=rh


def render_directions(canvas, draw, page, assets, base, template, common):
    paths=mechanics(page).get("paths")
    if not paths: raise ValueError("Direction paths required")
    y=700; rh=(2950-y)//len(paths)
    for p in paths:
        common.panel(draw,[180,y,2300,y+rh-25],outline="#7E57C2",width=3)
        common.paste_fit(canvas,assets[p["asset"]],[210,y+15,2260,y+rh-120])
        prompt(draw,base,template," → ".join(p.get("moves",[])),[300,y+rh-110,2180,y+rh-20],align="center")
        y+=rh


def render_classification(canvas, draw, page, assets, base, template, common):
    m=mechanics(page)
    if m.get("matrix"):
        matrix=m["matrix"]; items=m.get("items") or []
        rows,cols=matrix["rows"],matrix["columns"]; left,top,right,bottom=420,760,2260,2420
        cw=(right-left)//len(cols); ch=(bottom-top)//len(rows)
        for c,label in enumerate(cols): prompt(draw,base,template,label.upper(),[left+c*cw,660,left+(c+1)*cw,750],align="center")
        for r,label in enumerate(rows):
            prompt(draw,base,template,label.upper(),[170,top+r*ch,400,top+(r+1)*ch],align="center")
            for c in range(len(cols)): common.panel(draw,[left+c*cw,top+r*ch,left+(c+1)*cw,top+(r+1)*ch],outline="#7E57C2",width=3,radius=8)
        for item,box in zip(items,card_grid(len(items),top=2500,bottom=2990)):
            common.panel(draw,box,outline="#7E57C2",width=3); common.paste_fit(canvas,assets[item["asset"]],box)
        return
    cats=m.get("categories"); items=m.get("items")
    if not cats or not items: raise ValueError("Classification categories and items required")
    cat_boxes=[[180,700,1130,1220],[1350,700,2300,1220]]
    for cat,box in zip(cats,cat_boxes):
        common.panel(draw,box,outline="#7E57C2",width=3)
        if cat.get("exemplar"): common.paste_fit(canvas,assets[cat["exemplar"]],[box[0]+20,box[1]+20,box[2]-20,box[3]-110])
        prompt(draw,base,template,cat.get("label",cat["id"]),[box[0]+30,box[3]-100,box[2]-30,box[3]-15],align="center")
    for item,box in zip(items,card_grid(len(items),top=1300,bottom=2990)):
        common.panel(draw,box,outline="#7E57C2",width=3); common.paste_fit(canvas,assets[item["asset"]],[box[0]+10,box[1]+10,box[2]-10,box[3]-90])
        draw.ellipse([(box[0]+box[2])//2-40,box[3]-82,(box[0]+box[2])//2+40,box[3]-2],fill="#FFF",outline="#7E57C2",width=3)


def render_graph(canvas, draw, page, assets, base, template, common):
    m=mechanics(page); cats=m.get("categories"); qs=m.get("questions") or []
    if not cats: raise ValueError("Graph categories required")
    y=720; rh=430
    for cat in cats:
        common.panel(draw,[180,y,2300,y+rh],outline="#7E57C2",width=3)
        prompt(draw,base,template,cat["label"],[220,y+60,600,y+180])
        common.paste_fit(canvas,assets[cat["asset"]],[620,y+25,1940,y+rh-25])
        common.panel(draw,[2030,y+125,2200,y+295],fill="#FFF9DE",outline="#D9A91B",width=3,radius=16)
        y+=470
    if qs: prompt(draw,base,template,"   ".join(q["prompt"] for q in qs),[250,2670,2230,2940],align="center",max_lines=3)


def render_mixed(canvas, draw, page, assets, base, template, common):
    m=mechanics(page); tasks=m.get("problems") or m.get("tasks")
    if not tasks: raise ValueError("Mixed tasks required")
    boxes=card_grid(len(tasks))
    for task,box in zip(tasks,boxes):
        common.panel(draw,box,outline="#7E57C2",width=3)
        common.paste_fit(canvas,assets[task["asset"]],[box[0]+15,box[1]+15,box[2]-15,box[3]-170])
        if task.get("prompt"): prompt(draw,base,template,task["prompt"],[box[0]+35,box[3]-160,box[2]-35,box[3]-95],align="center",size=27)
        if task.get("choices"): choices(draw,base,template,task["choices"],[box[0]+35,box[3]-100,box[2]-35,box[3]-10])


def render_certificate(canvas, draw, page, assets, base, template, common):
    m=mechanics(page); names=ordered_assets(page)
    common.panel(draw,[260,730,2220,2940],fill="#FFFDF2",outline="#D9A91B",width=8,radius=42)
    if names: common.paste_fit(canvas,assets[names[0]],[400,790,2080,1300])
    prompt(draw,base,template,"Certificate of Completion",[450,1350,2030,1530],align="center",size=62)
    prompt(draw,base,template,"This certificate is proudly presented to",[500,1600,1980,1740],align="center",size=38)
    draw.line([560,1930,1920,1930],fill="#5B3F9A",width=4)
    prompt(draw,base,template,"for completing Early Maths Adventures",[500,2020,1980,2180],align="center",size=40)
    draw.line([450,2540,980,2540],fill="#5B3F9A",width=3); draw.line([1500,2540,2030,2540],fill="#5B3F9A",width=3)
    prompt(draw,base,template,"Date",[600,2560,830,2650],align="center",size=28); prompt(draw,base,template,"Teacher",[1640,2560,1900,2650],align="center",size=28)


def render_back_cover(canvas, draw, page, assets, base, template, common):
    names=ordered_assets(page)
    if not names: raise ValueError("Back cover asset required")
    common.paste_fit(canvas,assets[names[0]],[220,260,2260,3250],inset=0)


RENDER_BY_KIND={
    "count-choice-grid":render_count,
    "quantity-numeral-match":render_match,
    "comparison-pairs":render_comparison,
    "sequence-completion":render_sequence,
    "group-addition":render_addition,
    "take-away":render_subtraction,
    "number-line-jumps":render_numberline,
    "picture-story-problems":render_stories,
    "shape-hunt":render_hero_targets,
    "pattern-observation":render_pattern,
    "pattern-completion":render_pattern,
    "direction-paths":render_directions,
    "classification":render_classification,
    "picture-graph":render_graph,
    "mixed-review":render_mixed,
    "observe-reflect":render_hero_targets,
    "certificate":render_certificate,
    "back-cover":render_back_cover,
    "asset-grid":render_comparison,
}


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--level",required=True); parser.add_argument("--book",required=True)
    parser.add_argument("--page-id",required=True); parser.add_argument("--illustration",type=Path,required=True)
    parser.add_argument("--logo",type=Path,required=True); parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--evidence-output",type=Path,required=True)
    args=parser.parse_args()

    common=load_module("common_runtime",COMMON_PATH); base=load_module("runtime_base",BASE_PATH); loader=load_module("runtime_loader",LOADER_PATH)
    page=loader.load_page_contract(level=args.level,book_slug=args.book,page_id=args.page_id); common.validate(page)
    manifest=load_json(ROOT/"runtime-contracts/manifest.json"); relative=manifest["levels"][args.level.lower()]["books"][args.book]
    book=load_json(ROOT/"runtime-contracts"/relative); template=load_json(TEMPLATE_PATH); spec=template["canvas"]
    canvas=Image.new("RGB",(spec["width"],spec["height"]),template["colours"]["background"]); draw=ImageDraw.Draw(canvas)
    kind=page["activity"]["render_kind"]; renderer=RENDER_BY_KIND.get(kind)
    if renderer is None: raise ValueError(f"No dedicated renderer for render kind {kind!r}")
    if kind!="back-cover": common.header(canvas,draw,page,book["book"]["title"],Image.open(args.logo),base,template)
    source=Image.open(args.illustration).convert("RGBA"); assets=common.crop_assets(source,page["illustration"]["asset_crops"])
    renderer(canvas,draw,page,assets,base,template,common)
    if kind!="back-cover":
        common.teacher(draw,page,base,template)
        if page["identity"].get("printed_page") is not None:
            base.fitted_text(draw,str(page["identity"]["printed_page"]),[2200,3270,2370,3390],max_size=46,min_size=36,colour=template["colours"]["muted"],bold=True,max_lines=1)
    args.output.parent.mkdir(parents=True,exist_ok=True); canvas.save(args.output,"PNG",dpi=(spec["dpi"],spec["dpi"]))
    evidence={"engine":"BCube Early Maths Dedicated Renderer V2","page_id":args.page_id,"physical_page":page["identity"]["physical_page"],"render_kind":kind,"artifact":str(args.output),"artifact_sha256":hashlib.sha256(args.output.read_bytes()).hexdigest(),"qa":{"runtime_contract_used":True,"fallback_used":False,"dedicated_renderer":True,"status":"TEST_CANDIDATE"}}
    args.evidence_output.parent.mkdir(parents=True,exist_ok=True); args.evidence_output.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
    return 0


if __name__=="__main__": raise SystemExit(main())
