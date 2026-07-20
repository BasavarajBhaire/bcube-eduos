#!/usr/bin/env python3
"""Map 41 curriculum packages plus locked front/back matter to a 44-page release."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V4 = ROOT / "BCube_Gold_Production_v4"
SOURCE = ROOT / "production-prompts/communication-champions/nursery/v3/pages"
OUT = V4 / "manifests/nursery/communication-champions.release-v4.json"

SPECIAL = {
  1: ("CC-NURSERY-V4-P001", "CC-NURSERY-V3-P001", "Cover Page", "cover-page", "cover", None, False, 1),
  2: ("CC-NURSERY-V4-P002", None, "About This Book", "about-this-book", "about_this_book", 1, False, None),
  3: ("CC-NURSERY-V4-P003", "CC-NURSERY-V3-P002", "Copyright & Publication Details", "copyright-publication-details", "copyright", 2, False, 2),
  4: ("CC-NURSERY-V4-P004", "CC-NURSERY-V3-P003", "Contents — Part 1", "contents-part-1", "contents_part_1", 3, False, 3),
  5: ("CC-NURSERY-V4-P005", "CC-NURSERY-V3-P003", "Contents — Part 2", "contents-part-2", "contents_part_2", 4, False, 3),
}

def source_files(n):
    prefix=f"CC-NURSERY-V3-P{n:03d}-"
    js=next(SOURCE.glob(prefix+"*.json"))
    md=js.with_suffix(".md")
    return js,md,json.loads(js.read_text())

def template_for(role, title, source):
    if role in {"cover","back_cover","about_this_book","copyright","contents_part_1","contents_part_2","welcome","certificate","completion"}: return role.replace("_part_1","").replace("_part_2","")
    spec=source.get("page_data",{}).get("individual_specification",{})
    response=(spec.get("response_space") or "").lower()
    scene=source.get("page_data",{}).get("illustration",{}).get("scene","").lower()
    if "colour" in title.lower() or "outline" in scene: return "colouring-pairs"
    if "three" in response or "three" in scene: return "three-panel-activity"
    if "five" in response or "five" in scene: return "five-card-choice"
    if "drawing" in response or "draw" in title.lower(): return "drawing-activity"
    return "illustrated-activity"

jobs=[]
for pos in range(1,45):
    if pos in SPECIAL:
        pid,spid,title,slug,role,logical,visible,srcn=SPECIAL[pos]
        if pos==2:
            js=V4/"production/nursery/communication-champions/pages/CC-NURSERY-V4-P002-about-this-book.json"
            md=js.with_suffix(".md"); data=json.loads(js.read_text())
        else: js,md,data=source_files(srcn)
    elif pos==44:
        pid="CC-NURSERY-V4-P044"; spid=None; title="Back Cover"; slug="back-cover"
        role="back_cover"; logical=None; visible=False
        js=V4/"production/nursery/communication-champions/pages/CC-NURSERY-V4-P044-back-cover.json"
        md=js.with_suffix(".md"); data=json.loads(js.read_text())
    else:
        srcn=pos-2; js,md,data=source_files(srcn)
        pd=data["page_data"]; title=pd["title"]
        slug=js.stem.split(f"P{srcn:03d}-",1)[1]
        pid=f"CC-NURSERY-V4-P{pos:03d}"; spid=f"CC-NURSERY-V3-P{srcn:03d}"
        logical=pos-1; visible=True
        role="welcome" if pos==6 else "certificate" if pos==42 else "completion" if pos==43 else "learning_page"
    def rel(p): return str(p.relative_to(ROOT))
    jobs.append({
      "production_position":pos,"prompt_id":pid,"source_prompt_id":spid,"title":title,"slug":slug,
      "page_role":role,"logical_page_number":logical,"printed_number_visible":visible,
      "source_markdown":rel(md),"source_json":rel(js),"template_id":template_for(role,title,data),
      "asset_lock_id":pid,"output_file":f"{pid}-{slug}.png"
    })

manifest={
 "manifest_version":"4.1.0","book_id":"COMMUNICATION_CHAMPIONS_NURSERY","book":"Communication Champions",
 "level":"Nursery","release_mode":"approved-assets-only","total_packages":44,
 "brand_lock":"BCube_Gold_Production_v4/approved-assets/brand/asset-lock.json","jobs":jobs
}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
print(OUT)
