#!/usr/bin/env python3
"""Archetype-driven Phase 2 learning-page composer.

Routes A05/A06/A10/A12 by contract metadata. Supported pages never use the
legacy Home Connection or generic Say-or-Tell shell.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json
from pathlib import Path
from typing import Any
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'bcube-publishing-sdk/composer/compose_learning_page_v2.py'
FALLBACK=ROOT/'bcube-publishing-sdk/composer/compose_learning_page_character_v2.py'
TEMPLATE=ROOT/'bcube-publishing-sdk/templates/learning-page-v2.json'
SUPPORTED={'A05 Read/Look & Match','A05 Read / Look & Match','A06 Sort & Classify','A10 Speak, Listen & Respond','A12 Observe, Find & Name'}

def module(name,path):
 s=importlib.util.spec_from_file_location(name,path)
 if s is None or s.loader is None: raise RuntimeError(f'Cannot load {path}')
 m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

def load(path):
 v=json.loads(Path(path).read_text(encoding='utf-8'))
 if not isinstance(v,dict): raise ValueError(f'{path} must contain an object')
 return v

def resolve(value):
 p=Path(value); return p if p.is_absolute() else ROOT/p

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def panel(d,b,fill='#FFF',outline='#8E5AC7',width=4,radius=24): d.rounded_rectangle(b,radius=radius,fill=fill,outline=outline,width=width)

def paste(canvas,img,b,inset=8):
 x0,y0,x1,y1=b; x0+=inset; y0+=inset; x1-=inset; y1-=inset
 img=img.convert('RGBA'); scale=min((x1-x0)/img.width,(y1-y0)/img.height)
 img=img.resize((max(1,round(img.width*scale)),max(1,round(img.height*scale))),Image.Resampling.LANCZOS)
 x=x0+(x1-x0-img.width)//2; y=y0+(y1-y0-img.height)//2; canvas.paste(img,(x,y),img); return [x,y,x+img.width,y+img.height]

def clean(img):
 img=img.convert('RGBA'); img.putdata([(255,255,255,0) if r>246 and g>246 and b>246 else (r,g,b,a) for r,g,b,a in img.getdata()])
 box=img.getbbox()
 if box is None: raise ValueError('Empty crop')
 return img.crop(box)

def crops(source,p2):
 data=p2.get('asset_crops')
 if not isinstance(data,dict) or not data: raise ValueError('Named asset_crops are required')
 w,h=source.size; out={}
 for name,(x0,y0,x1,y1) in data.items(): out[name]=clean(source.crop((round(x0*w),round(y0*h),round(x1*w),round(y1*h))))
 return out

def header(canvas,d,c,t,b):
 col=t['colours']; typ=t['typography']; ident=c['identity']
 logo=Image.open(resolve(c['assets']['official_logo_path'])).convert('RGBA'); logo.thumbnail((300,225),Image.Resampling.LANCZOS); canvas.paste(logo,(110+(300-logo.width)//2,35+(225-logo.height)//2),logo)
 b.brand_title(d,ident['book_title_lines'],[470,45,2320,145],col,typ)
 b.fitted_text(d,ident['title'],[470,145,2320,285],max_size=typ['page_title_max'],min_size=typ['page_title_min'],colour=col['navy'],bold=True,max_lines=2)
 panel(d,[150,305,2330,435],fill=col['blue'],outline='#1768B3',width=3); b.fitted_text(d,'Learning goal: '+c['learning']['objective'],[185,315,2295,425],max_size=44,min_size=32,colour=col['navy'],bold=True,max_lines=2)
 panel(d,[150,460,2330,610],fill=col['gold'],outline='#E1B12C',width=3); b.fitted_text(d,c['learning']['student_instruction'],[185,472,2295,598],max_size=52,min_size=38,colour=col['line'],bold=True,max_lines=2)

def teacher(d,c,t,b):
 col=t['colours']; box=[150,3070,2300,3260]; panel(d,box,fill='#F0FAED',outline='#5F9D50',width=3)
 b.fitted_text(d,'TEACHER CUE',[180,3090,530,3235],max_size=34,min_size=27,colour=col['navy'],bold=True,max_lines=1)
 text=c.get('guidance',{}).get('teacher',{}).get('model') or 'Invite one response, pause, and affirm effort.'
 b.fitted_text(d,text,[560,3085,2260,3240],max_size=36,min_size=27,colour=col['line'],align='left',max_lines=3); return box

def card(canvas,d,b,col,box,img,label='',number=None,mark=False):
 panel(d,box,outline=col['soft_purple'],width=3); bottom=80 if label else 20; pic=paste(canvas,img,[box[0]+20,box[1]+20,box[2]-20,box[3]-bottom],3)
 if label: b.fitted_text(d,label,[box[0]+18,box[3]-78,box[2]-18,box[3]-15],max_size=32,min_size=23,colour=col['navy'],bold=True,max_lines=2)
 if number is not None: d.ellipse([box[0]+14,box[1]+14,box[0]+68,box[1]+68],fill='#FFF',outline=col['purple'],width=4); b.fitted_text(d,str(number),[box[0]+16,box[1]+16,box[0]+66,box[1]+66],max_size=30,min_size=24,colour=col['navy'],bold=True,max_lines=1)
 if mark: d.ellipse([box[2]-65,box[1]+15,box[2]-20,box[1]+60],fill='#FFF',outline=col['purple'],width=4)
 return pic

def names(p2,*keys):
 for k in keys:
  v=p2.get(k)
  if isinstance(v,list) and v: return [str(x) for x in v]
 return list(p2['asset_crops'])

def render_a12(canvas,d,c,t,b,source):
 col=t['colours']; p2=c['phase2']; a=crops(source,p2); scene=next((n for n in ('scene','main_scene','hero_scene','model_scene') if n in a),None)
 target=names(p2,'targets','choices','items'); target=[n for n in target if n in a and n!=scene]
 if scene:
  panel(d,[180,650,2300,2240],outline=col['soft_purple'],width=3); paste(canvas,a[scene],[195,665,2285,2225],12); y=2300
 else: y=760
 if not scene and len(a)==5: target=list(a)
 if not scene and len(target)==5:
  for i,n in enumerate(target): card(canvas,d,b,col,[90+i*470,860,520+i*470,2850],a[n])
  return {'type':'A12','targets':target}
 panel(d,[220,y,2260,2990],outline='#5F9D50',width=3)
 for i,n in enumerate(target[:4]): card(canvas,d,b,col,[250+i*500,y+45,690+i*500,2940],a[n],mark=True)
 return {'type':'A12','scene':scene,'targets':target[:4]}

def render_a06(canvas,d,c,t,b,source):
 col=t['colours']; p2=c['phase2']; a=crops(source,p2); items=names(p2,'items','choices','targets')[:6]
 panel(d,[180,650,2300,1880],outline=col['soft_purple'],width=3)
 for i,n in enumerate(items): r,x=divmod(i,3); card(canvas,d,b,col,[220+x*700,700+r*570,860+x*700,1210+r*570],a[n],number=i+1)
 cats=p2.get('categories') or ['Group 1','Group 2']; w=1980//max(2,min(3,len(cats)))
 for i,label in enumerate(cats[:3]): left=250+i*w; box=[left,1950,left+w-80,2990]; panel(d,box,fill='#F8F5FF',outline=col['purple']); b.fitted_text(d,str(label),[left+40,1980,box[2]-40,2100],max_size=46,min_size=32,colour=col['navy'],bold=True,max_lines=2); [d.line((left+100,2360+j*180,box[2]-100,2360+j*180),fill='#7C8799',width=3) for j in range(3)]
 return {'type':'A06','items':items,'categories':cats}

def render_a10(canvas,d,c,t,b,source):
 col=t['colours']; p2=c['phase2']; a=crops(source,p2); hero=next((n for n in ('model_scene','hero_scene','scene') if n in a),None); y=650
 if hero: panel(d,[200,650,2280,1450],outline=col['soft_purple'],width=3); paste(canvas,a[hero],[215,665,2265,1435],12); y=1500
 rows=[]
 if p2.get('characters') and p2.get('situations'): rows=[('Choose a character',p2['characters']),('Choose a situation',p2['situations'])]
 else: rows=[('',[n for n in names(p2,'choices','items','targets') if n in a and n!=hero])]
 for heading,row_names in rows:
  if heading: b.fitted_text(d,heading,[240,y,2240,y+70],max_size=40,min_size=30,colour=col['navy'],bold=True,max_lines=1); y+=85
  for i,n in enumerate(row_names[:6]): r,x=divmod(i,3); card(canvas,d,b,col,[220+x*700,y+r*510,860+x*700,y+455+r*510],a[n],n if len(row_names)<=3 else '',mark=True)
  y+=510*((min(6,len(row_names))+2)//3)
 model=c.get('learning',{}).get('model_text')
 if model and y<2910: panel(d,[300,y+10,2180,min(3010,y+220)],fill=col['gold'],outline='#E1B12C',width=3); b.fitted_text(d,model,[350,y+25,2130,min(2995,y+200)],max_size=44,min_size=31,colour=col['line'],bold=True,max_lines=2)
 return {'type':'A10','hero':hero}

def render_a05(canvas,d,c,t,b,source):
 col=t['colours']; p2=c['phase2']; a=crops(source,p2)
 if p2.get('main_words'):
  words=list(p2['main_words'])+list(p2.get('small_words',[])); pics=list(p2['main_picture_order'])+list(p2.get('small_picture_order',[])); panel(d,[180,650,2300,2990],outline=col['soft_purple']); h=2260//max(1,len(words))
  for i,(w,n) in enumerate(zip(words,pics)): cy=700+i*h+h//2; b.fitted_text(d,w,[245,cy-h//3,700,cy+h//3],max_size=70,min_size=44,colour='#111',bold=True,align='left',max_lines=1); d.ellipse([730,cy-20,770,cy+20],fill='#FFF',outline=col['purple'],width=4); d.ellipse([1480,cy-20,1520,cy+20],fill='#FFF',outline=col['purple'],width=4); paste(canvas,a[n],[1560,cy-h//2+8,2180,cy+h//2-8],3)
 else:
  items=names(p2,'items','choices','targets')[:8]; panel(d,[180,650,2300,2990],outline=col['soft_purple'])
  for i,n in enumerate(items): r,x=divmod(i,4); card(canvas,d,b,col,[220+x*520,710+r*1040,700+x*520,1660+r*1040],a[n],n,mark=True)
 return {'type':'A05'}

def compose_phase2(contract_path,output,evidence_output):
 b=module('phase2_base',BASE); c=load(contract_path); t=load(TEMPLATE); p2=c['phase2']; arch=str(p2.get('archetype') or '')
 if arch not in SUPPORTED: raise ValueError(f'Unsupported Phase 2 archetype: {arch}')
 p2['parent_panel']=False; c.setdefault('guidance',{})['parent_extension']=''; spec=t['canvas']; col=t['colours']; canvas=Image.new('RGB',(spec['width'],spec['height']),col['background']); d=ImageDraw.Draw(canvas); header(canvas,d,c,t,b); source=Image.open(resolve(c['assets']['illustration_path'])).convert('RGBA')
 renderer=render_a05 if arch.startswith('A05') else render_a06 if arch.startswith('A06') else render_a10 if arch.startswith('A10') else render_a12; activity=renderer(canvas,d,c,t,b,source); teacher_box=teacher(d,c,t,b)
 ident=c['identity']; page=None
 if ident['page_number_visible'] and ident['page_number']>0: page=b.fitted_text(d,str(ident['page_number']),[2200,3270,2370,3390],max_size=46,min_size=36,colour=col['muted'],bold=True,max_lines=1)
 output=Path(output); output.parent.mkdir(parents=True,exist_ok=True); canvas.save(output,'PNG',dpi=(spec['dpi'],spec['dpi']))
 evidence={'engine':'BCube Publishing Engine Phase 2 Archetype Renderer','page_id':ident['page_id'],'archetype':arch,'artifact':str(output),'artifact_sha256':sha(output),'components':{'activity':activity,'teacher_cue':teacher_box,'parent_panel':None,'home_connection':None,'generic_say_or_tell':None,'page_number':page},'qa':{'parent_panel_removed':True,'home_connection_removed':True,'generic_say_or_tell_removed':True,'named_asset_crop_manifest_used':True,'task_specific_layout':True,'status':'REVIEW_CANDIDATE'}}
 evidence_output=Path(evidence_output); evidence_output.parent.mkdir(parents=True,exist_ok=True); evidence_output.write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def compose(contract_path,output,evidence_output):
 c=load(contract_path); p2=c.get('phase2'); arch=str(p2.get('archetype') or '') if isinstance(p2,dict) else ''
 if arch in SUPPORTED: compose_phase2(contract_path,output,evidence_output)
 else: module('phase2_fallback',FALLBACK).compose(contract_path,output,evidence_output)

def main():
 p=argparse.ArgumentParser(); p.add_argument('--contract',type=Path,required=True); p.add_argument('--output',type=Path,required=True); p.add_argument('--evidence-output',type=Path,required=True); a=p.parse_args(); compose(a.contract,a.output,a.evidence_output); return 0
if __name__=='__main__': raise SystemExit(main())
