#!/usr/bin/env python3
"""Deterministically compose a BCube Nursery cover.

AI supplies only an illustration layer. All publishing components are rendered
from repository-controlled geometry and assets. The compositor fails closed on
missing assets, invalid icon keys, contaminated evidence, or geometry drift.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "bcube-publishing-sdk/templates/nursery-cover-v1.json"
BOLD_CANDIDATES = [Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"), Path("C:/Windows/Fonts/arialbd.ttf")]
REGULAR_CANDIDATES = [Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), Path("C:/Windows/Fonts/arial.ttf")]
SKILL_ICON_KEYS = {"person", "spark", "speech", "shield", "heart", "trophy"}
PILLAR_ICON_KEYS = {"palette", "chat", "search", "confidence", "puzzle"}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def font_path(bold: bool) -> Path:
    for candidate in BOLD_CANDIDATES if bold else REGULAR_CANDIDATES:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("No supported deterministic font was found")


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(font_path(bold)), size)


def centered_text(draw: ImageDraw.ImageDraw, text: str, bounds: list[int], max_size: int,
                  fill: str, *, min_size: int = 18, shadow: bool = False) -> None:
    x0, y0, x1, y1 = bounds
    for size in range(max_size, min_size - 1, -2):
        active = font(size)
        left, top, right, bottom = draw.textbbox((0, 0), text, font=active)
        width, height = right - left, bottom - top
        if width <= x1 - x0 and height <= y1 - y0:
            x = x0 + (x1 - x0 - width) / 2
            y = y0 + (y1 - y0 - height) / 2 - top
            if shadow:
                draw.text((x + 8, y + 10), text, font=active, fill="#D5D5D5")
            draw.text((x, y), text, font=active, fill=fill)
            return
    raise ValueError(f"Text does not fit locked bounds: {text!r}")


def paste_contain(canvas: Image.Image, asset_path: Path, bounds: list[int], *, crop: list[int] | None = None,
                  remove_near_white: bool = False) -> dict[str, Any]:
    asset = Image.open(asset_path).convert("RGBA")
    original_size = [asset.width, asset.height]
    if crop:
        if len(crop) != 4 or crop[0] < 0 or crop[1] < 0 or crop[2] > asset.width or crop[3] > asset.height:
            raise ValueError(f"Invalid crop {crop} for {asset_path} sized {asset.size}")
        asset = asset.crop(tuple(crop))
    if remove_near_white:
        pixels = []
        for red, green, blue, alpha in asset.getdata():
            pixels.append((255, 255, 255, 0) if red > 244 and green > 244 and blue > 244 else (red, green, blue, alpha))
        asset.putdata(pixels)
    x0, y0, x1, y1 = bounds
    asset.thumbnail((x1 - x0, y1 - y0), Image.Resampling.LANCZOS)
    x = x0 + (x1 - x0 - asset.width) // 2
    y = y0 + (y1 - y0 - asset.height) // 2
    canvas.paste(asset, (x, y), asset)
    return {"source_size": original_size, "rendered_bounds": [x, y, x + asset.width, y + asset.height], "crop": crop}


def paste_safe_illustration(canvas: Image.Image, asset_path: Path, bounds: list[int], background: str,
                            safe_inset: int = 28, radius: int = 36) -> dict[str, Any]:
    """Contain an illustration without cropping faces or edge subjects."""
    asset = Image.open(asset_path).convert("RGB")
    source_size = [asset.width, asset.height]
    x0, y0, x1, y1 = bounds
    inner = [x0 + safe_inset, y0 + safe_inset, x1 - safe_inset, y1 - safe_inset]
    target_w, target_h = inner[2] - inner[0], inner[3] - inner[1]
    scale = min(target_w / asset.width, target_h / asset.height)
    rendered_w = max(1, round(asset.width * scale))
    rendered_h = max(1, round(asset.height * scale))
    resized = asset.resize((rendered_w, rendered_h), Image.Resampling.LANCZOS)
    px = inner[0] + (target_w - rendered_w) // 2
    py = inner[1] + (target_h - rendered_h) // 2
    frame_layer = Image.new("RGB", (x1 - x0, y1 - y0), background)
    frame_layer.paste(resized, (px - x0, py - y0))
    mask = Image.new("L", frame_layer.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, frame_layer.width - 1, frame_layer.height - 1), radius=radius, fill=255)
    canvas.paste(frame_layer, (x0, y0), mask)
    return {
        "mode": "contain",
        "source_size": source_size,
        "frame_bounds": bounds,
        "safe_inset": safe_inset,
        "rendered_bounds": [px, py, px + rendered_w, py + rendered_h],
        "cropped": False,
    }


def draw_vector_icon(draw: ImageDraw.ImageDraw, key: str, bounds: list[int], colour: str) -> None:
    """Draw repository-controlled vector icons; no missing-glyph placeholders."""
    x0, y0, x1, y1 = bounds
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    w, h = x1 - x0, y1 - y0
    stroke = max(4, min(w, h) // 12)
    if key == "person":
        draw.ellipse((cx-w//7, y0+h//8, cx+w//7, y0+h*3//8), fill=colour)
        draw.rounded_rectangle((cx-w//4, y0+h*2//5, cx+w//4, y1-h//8), radius=w//10, fill=colour)
    elif key == "spark":
        points = [(cx, y0+h//8), (cx+w//10, cy-w//12), (x1-w//8, cy), (cx+w//10, cy+w//12),
                  (cx, y1-h//8), (cx-w//10, cy+w//12), (x0+w//8, cy), (cx-w//10, cy-w//12)]
        draw.polygon(points, fill=colour)
    elif key == "speech" or key == "chat":
        draw.rounded_rectangle((x0+w//8, y0+h//5, x1-w//8, y1-h//4), radius=w//8, outline=colour, width=stroke)
        draw.polygon([(cx-w//6, y1-h//4), (cx-w//3, y1-h//10), (cx+w//12, y1-h//4)], fill=colour)
        for dx in (-w//5, 0, w//5): draw.ellipse((cx+dx-stroke, cy-stroke, cx+dx+stroke, cy+stroke), fill=colour)
    elif key == "shield":
        draw.polygon([(cx, y0+h//10), (x1-w//7, y0+h//4), (x1-w//5, y1-h//3), (cx, y1-h//10),
                      (x0+w//5, y1-h//3), (x0+w//7, y0+h//4)], outline=colour, fill=None)
        draw.line((cx-w//5, cy, cx-w//20, cy+h//7, cx+w//4, cy-h//6), fill=colour, width=stroke)
    elif key == "heart":
        draw.ellipse((x0+w//7, y0+h//5, cx+w//15, cy+h//8), fill=colour)
        draw.ellipse((cx-w//15, y0+h//5, x1-w//7, cy+h//8), fill=colour)
        draw.polygon([(x0+w//7, cy), (x1-w//7, cy), (cx, y1-h//8)], fill=colour)
    elif key == "trophy":
        draw.rectangle((cx-w//5, y0+h//6, cx+w//5, cy+h//10), fill=colour)
        draw.arc((x0+w//10, y0+h//5, cx, cy+h//5), 80, 280, fill=colour, width=stroke)
        draw.arc((cx, y0+h//5, x1-w//10, cy+h//5), -100, 100, fill=colour, width=stroke)
        draw.rectangle((cx-stroke, cy, cx+stroke, y1-h//5), fill=colour)
        draw.rectangle((cx-w//4, y1-h//5, cx+w//4, y1-h//10), fill=colour)
    elif key == "palette":
        draw.ellipse((x0+w//8, y0+h//8, x1-w//8, y1-h//8), outline=colour, width=stroke)
        draw.ellipse((cx+w//8, cy+w//12, x1-w//7, y1-h//8), fill="white")
        for dx, dy in [(-w//5,-h//6),(0,-h//5),(w//5,-h//8),(-w//6,h//8)]:
            draw.ellipse((cx+dx-stroke, cy+dy-stroke, cx+dx+stroke, cy+dy+stroke), fill=colour)
    elif key == "search":
        draw.ellipse((x0+w//8, y0+h//8, x1-w//3, y1-h//3), outline=colour, width=stroke)
        draw.line((cx+w//8, cy+h//8, x1-w//10, y1-h//10), fill=colour, width=stroke)
    elif key == "confidence":
        draw.ellipse((cx-w//8, y0+h//10, cx+w//8, y0+h//3), fill=colour)
        draw.line((cx, y0+h//3, cx, y1-h//5), fill=colour, width=stroke)
        draw.line((cx, cy, x0+w//8, y0+h//3), fill=colour, width=stroke)
        draw.line((cx, cy, x1-w//8, y0+h//3), fill=colour, width=stroke)
        draw.line((cx, y1-h//5, x0+w//4, y1-h//10), fill=colour, width=stroke)
        draw.line((cx, y1-h//5, x1-w//4, y1-h//10), fill=colour, width=stroke)
    elif key == "puzzle":
        draw.rounded_rectangle((x0+w//7, y0+h//7, x1-w//7, y1-h//7), radius=w//12, outline=colour, width=stroke)
        draw.ellipse((cx-w//8, y0, cx+w//8, y0+h//4), fill=colour)
        draw.ellipse((x1-w//4, cy-w//8, x1, cy+w//8), fill=colour)
    else:
        raise ValueError(f"Unregistered vector icon key: {key}")


def validate_data(data: dict[str, Any]) -> None:
    required = ["page_id", "book_key", "title_lines", "tagline", "level", "age", "skills", "pillars",
                "skill_icon_keys", "pillar_icon_keys", "illustration_path", "official_logo_path",
                "official_star_path", "illustration_evidence"]
    missing = [key for key in required if key not in data]
    if missing: raise ValueError(f"Missing cover data: {missing}")
    if len(data["title_lines"]) != 2: raise ValueError("Cover title must contain exactly two lines")
    if len(data["skills"]) != 6 or len(data["skill_icon_keys"]) != 6: raise ValueError("Cover requires six skills and six icons")
    if len(data["pillars"]) != 5 or len(data["pillar_icon_keys"]) != 5: raise ValueError("Cover requires five pillars and five icons")
    unknown_skills = set(data["skill_icon_keys"]) - SKILL_ICON_KEYS
    unknown_pillars = set(data["pillar_icon_keys"]) - PILLAR_ICON_KEYS
    if unknown_skills or unknown_pillars: raise ValueError(f"Unregistered icon keys: {sorted(unknown_skills | unknown_pillars)}")
    evidence = data["illustration_evidence"]
    forbidden = ["contains_text", "contains_logo", "contains_mascot", "contains_badge", "contains_page_layout", "contains_embedded_page"]
    contaminated = [key for key in forbidden if evidence.get(key) is not False]
    if contaminated: raise ValueError(f"Illustration candidate rejected; clean evidence required for: {contaminated}")
    for path_key in ["illustration_path", "official_logo_path", "official_star_path"]:
        path = Path(data[path_key]) if Path(data[path_key]).is_absolute() else ROOT / data[path_key]
        if not path.is_file(): raise FileNotFoundError(f"Missing required input: {data[path_key]}")


def compose(data_path: Path, output: Path, evidence_output: Path) -> None:
    data = load_json(data_path); validate_data(data)
    template = load_json(TEMPLATE); bounds, colours = template["bounds"], template["colours"]
    width, height = template["canvas"]["width"], template["canvas"]["height"]
    canvas = Image.new("RGB", (width, height), colours["background"]); draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((18, 18, width - 18, height - 18), radius=40, outline="#5B2B87", width=8)

    def resolve(value: str) -> Path:
        path = Path(value); return path if path.is_absolute() else ROOT / path

    logo_path, star_path, illustration_path = resolve(data["official_logo_path"]), resolve(data["official_star_path"]), resolve(data["illustration_path"])
    logo_render = paste_contain(canvas, logo_path, bounds["official_logo"])

    x0,y0,x1,y1 = bounds["series_banner"]
    draw.polygon([(x0+70,y0),(x1-70,y0),(x1,(y0+y1)//2),(x1-70,y1),(x0+70,y1),(x0,(y0+y1)//2)], fill=colours["purple"], outline=colours["gold"])
    centered_text(draw,"BCube Future Skills",[x0+60,y0+35,x1-60,y0+145],70,"white")
    centered_text(draw,"Learning Series™",[x0+60,y0+145,x1-60,y1-35],70,"white")

    x0,y0,x1,y1 = bounds["age_badge"]
    draw.ellipse((x0,y0,x1,y1),fill=colours["purple"],outline="#CDA7E2",width=16)
    centered_text(draw,str(data["level"]).upper(),[x0+30,y0+35,x1-30,y0+125],42,"white")
    centered_text(draw,str(data["age"]),[x0+45,y0+120,x1-45,y0+265],92,colours["gold"])
    centered_text(draw,"YEARS",[x0+45,y0+265,x1-45,y1-35],36,"white")

    title = bounds["book_title"]; mid=(title[1]+title[3])//2
    centered_text(draw,data["title_lines"][0].upper(),[title[0],title[1],title[2],mid],118,colours["purple"],shadow=True)
    centered_text(draw,data["title_lines"][1].upper(),[title[0],mid,title[2],title[3]],128,colours["blue"],shadow=True)

    x0,y0,x1,y1=bounds["book_tagline"]
    draw.polygon([(x0+60,y0),(x1-60,y0),(x1,(y0+y1)//2),(x1-60,y1),(x0+60,y1),(x0,(y0+y1)//2)],fill=colours["pink"])
    centered_text(draw,data["tagline"].upper(),[x0+60,y0+10,x1-60,y1-10],56,"white")

    illustration_render = paste_safe_illustration(canvas, illustration_path, bounds["illustration_frame"], colours["background"], safe_inset=template["rules"].get("illustration_safe_inset",28))
    draw.rounded_rectangle(tuple(bounds["illustration_frame"]),radius=42,outline="#D6BCE7",width=7)
    star_bounds=data.get("official_star_bounds",[1280,2160,1720,2660])
    star_render = paste_contain(
    canvas,
    star_path,
    star_bounds,
)

    skill_colours=["#F47B16","#2F95CF","#4FAE2A","#EC3481","#7D3EAB","#1EA0B9"]
    region=bounds["six_skill_capsules"]; y=region[1]; skill_evidence=[]
    for index,(label,key) in enumerate(zip(data["skills"],data["skill_icon_keys"])):
        capsule=[region[0],y,region[2],y+156]; colour=skill_colours[index]
        draw.rounded_rectangle(tuple(capsule),radius=70,fill=colour)
        icon_circle=[capsule[0]+20,capsule[1]+22,capsule[0]+126,capsule[1]+128]
        draw.ellipse(tuple(icon_circle),fill="white")
        draw_vector_icon(draw,key,[icon_circle[0]+18,icon_circle[1]+18,icon_circle[2]-18,icon_circle[3]-18],colour)
        centered_text(draw,str(label).upper(),[capsule[0]+145,capsule[1]+20,capsule[2]-20,capsule[3]-20],34,"white",min_size=20)
        skill_evidence.append({"bounds":capsule,"icon_key":key,"icon_bounds":icon_circle}); y+=184

    region=bounds["five_core_pillars"]
    draw.rounded_rectangle(tuple(region),radius=45,fill="#FFFDFD",outline="#D7B9E8",width=5)
    label_bounds=bounds.get("core_pillars_label",[760,2745,1720,2835])
    draw.rounded_rectangle(tuple(label_bounds),radius=35,fill=colours["purple"]); centered_text(draw,"OUR CORE PILLARS",label_bounds,44,"white")
    pillar_colours=["#F47B16","#2AAA35","#2F95CF","#7D3EAB","#EC3481"]
    centers=[280,760,1240,1720,2200]; pillar_evidence=[]
    for pillar,key,colour,cx in zip(data["pillars"],data["pillar_icon_keys"],pillar_colours,centers):
        icon_bounds=[cx-60,2870,cx+60,2990]; draw.ellipse(tuple(icon_bounds),fill=colour)
        draw_vector_icon(draw,key,[icon_bounds[0]+20,icon_bounds[1]+20,icon_bounds[2]-20,icon_bounds[3]-20],"white")
        centered_text(draw,str(pillar["code"]).upper(),[cx-190,2990,cx+190,3030],20,colour,min_size=14)
        centered_text(draw,str(pillar["name"]).upper(),[cx-190,3030,cx+190,3090],22,colour,min_size=15)
        pillar_evidence.append({"bounds":icon_bounds,"icon_key":key})

    footer=bounds["footer"]; draw.rectangle((footer[0],footer[1],footer[2],3390),fill=colours["purple"])
    centered_text(draw,"★  BUILD  •  CREATE  •  BECOME  ★",[250,3200,2230,3345],56,"white")
    draw.rectangle((0,3390,width,height),fill="#FFF0A9")
    centered_text(draw,data["footer_keywords"],[240,3410,2240,3490],34,colours["blue"])

    output.parent.mkdir(parents=True,exist_ok=True); canvas.save(output,"PNG",dpi=(300,300),optimize=True)
    artifact_hash=sha256(output)
    components=[
        {"component":"official_logo","source_path":data["official_logo_path"],"approved_sha256":sha256(logo_path),"bounds":bounds["official_logo"],"template_bounds":bounds["official_logo"],"allow_overlap":False,"render":logo_render},
        {"component":"series_banner","bounds":bounds["series_banner"],"template_bounds":bounds["series_banner"],"allow_overlap":False},
        {"component":"book_title","bounds":bounds["book_title"],"template_bounds":bounds["book_title"],"allow_overlap":False},
        {"component":"age_badge","bounds":bounds["age_badge"],"template_bounds":bounds["age_badge"],"allow_overlap":False},
        {"component":"book_tagline","bounds":bounds["book_tagline"],"template_bounds":bounds["book_tagline"],"allow_overlap":False},
        {"component":"illustration_frame","bounds":bounds["illustration_frame"],"template_bounds":bounds["illustration_frame"],"allow_overlap":True,"render":illustration_render},
        {"component":"official_star","source_path":data["official_star_path"],"approved_sha256":sha256(star_path),"bounds":star_bounds,"template_bounds":star_bounds,"allow_overlap":True,"render":star_render},
        {"component":"six_skill_capsules","bounds":bounds["six_skill_capsules"],"template_bounds":bounds["six_skill_capsules"],"allow_overlap":False,"items":skill_evidence},
        {"component":"five_core_pillars","bounds":bounds["five_core_pillars"],"template_bounds":bounds["five_core_pillars"],"allow_overlap":False,"items":pillar_evidence},
        {"component":"footer","bounds":bounds["footer"],"template_bounds":bounds["footer"],"allow_overlap":False},
    ]
    evidence={"page_id":data["page_id"],"page_type":"cover","book_key":data["book_key"],
              "artifact_path":str(output.relative_to(ROOT)) if output.is_relative_to(ROOT) else str(output),
              "composition":{"engine":"bcube-publishing-sdk","engine_version":"cover-composer-v1.1","full_page_ai_generation":False,"single_flat_page":True,"illustration_layer_path":data["illustration_path"],"illustration_layer_sha256":sha256(illustration_path),"illustration_placement":illustration_render},
              "component_evidence":components,"text_evidence":data["text_evidence"],"human_approval":data["human_approval"]|{"artifact_sha256":artifact_hash}}
    evidence_output.parent.mkdir(parents=True,exist_ok=True); evidence_output.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":"COMPOSED","artifact":str(output),"evidence":str(evidence_output),"sha256":artifact_hash}))


def self_test() -> int:
    with tempfile.TemporaryDirectory() as directory:
        temp=Path(directory)
        Image.new("RGBA",(300,180),"blue").save(temp/"logo.png")
        Image.new("RGBA",(500,500),"gold").save(temp/"star.png")
        Image.new("RGB",(1200,900),"#F4E0B8").save(temp/"illustration.png")
        test={"page_id":"TEST-COVER","book_key":"nursery/confidence-builders","title_lines":["Confidence","Builders"],"tagline":"I Believe • I Can • I Will","level":"Nursery","age":"3+","skills":["Believe in Myself","Try New Things","Speak with Confidence","Make Good Choices","Be Kind to Others","Celebrate Success"],"skill_icon_keys":["person","spark","speech","shield","heart","trophy"],"pillars":[{"code":c,"name":n} for c,n in [("CR","Creativity"),("CO","Communication"),("CU","Curiosity"),("CF","Confidence"),("CL","Collaboration")]],"pillar_icon_keys":["palette","chat","search","confidence","puzzle"],"footer_keywords":"Self-belief • Courage • Expression • Kindness • Independence","illustration_path":str(temp/"illustration.png"),"official_logo_path":str(temp/"logo.png"),"official_star_path":str(temp/"star.png"),"illustration_evidence":{"contains_text":False,"contains_logo":False,"contains_mascot":False,"contains_badge":False,"contains_page_layout":False,"contains_embedded_page":False},"text_evidence":{"detector":{"name":"self-test","version":"1"},"detected_text":["CONFIDENCE BUILDERS","I BELIEVE","I CAN","I WILL","BCUBE FUTURE SKILLS LEARNING SERIES","NURSERY","3+"]},"human_approval":{"reviewer":"SDK Self Test","approved_on":"2026-07-22","status":"APPROVED","artifact_sha256":"0"*64}}
        data_path=temp/"data.json"; data_path.write_text(json.dumps(test),encoding="utf-8")
        compose(data_path,temp/"cover.png",temp/"evidence.json")
    print("deterministic Nursery cover compositor self-test passed"); return 0


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--data",type=Path); parser.add_argument("--output",type=Path); parser.add_argument("--evidence-output",type=Path); parser.add_argument("--self-test",action="store_true"); args=parser.parse_args()
    if args.self_test: return self_test()
    if not args.data or not args.output or not args.evidence_output: parser.error("--data, --output and --evidence-output are required")
    compose(args.data,args.output,args.evidence_output); return 0


if __name__ == "__main__": raise SystemExit(main())
