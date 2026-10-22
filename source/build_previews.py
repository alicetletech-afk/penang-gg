#!/usr/bin/env python3
"""Shared geographic compositor for map previews, labels, mobile proofs and placement QA."""
import json, os, math, html
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent
ART=ROOT/'assets'/'landmarks'
BASE=ROOT.parent/'work'/'penang-base-preview.png'
OUT=ROOT
W,H=1120,1500
LOC=ROOT/'locations.json'
DATA=json.loads(LOC.read_text(encoding='utf8'))
BY_ID={x['id']:x for x in DATA['locations']}
FONT_BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
FONT_REG='/System/Library/Fonts/Supplemental/Arial.ttf'
DISPLAY_LABELS={'townhall':'Town Hall & City Hall','ferry_museum':'Penang Ferry Museum','ferry_terminal':'Raja Tun Uda Terminal','dim_sum':'Cheng Zheng Dim Sum','floating':'Floating Mosque'}

# Viewports are windows into the same 1120x1500 projected map coordinate system.
VIEWS={
 'full':{'box':(0,0,W,H),'size':(W,H)},
 'north':{'box':(450,90,1120,720),'size':(1120,1053)},
 'georgetown':{'box':(875,410,1065,600),'size':(1200,1200)},
 'mobile_georgetown':{'box':(900,390,1060,700),'size':(390,756)},
 'mobile_georgetown_430':{'box':(900,390,1060,704),'size':(430,844)},
 'mobile_initial':{'box':(520,90,1080,1175),'size':(390,756)},
 'fit_mobile':{'box':(0,0,W,H),'size':(390,844)},
}
# Only display offsets/sizes live here in canonical locations.json. These are map-space px,
# so every view applies its own viewport transform; they never replace a geographic anchor.
DEFAULT_ASSETS={
 'floating':{'ids':['floating'],'offset':[-2,0],'size':112,'priority':100,'zoom':['full','north','georgetown','mobile_georgetown','mobile_initial']},
 'kek':{'ids':['kek'],'offset':[-2,0],'size':118,'priority':100,'zoom':['full','north','georgetown','mobile_georgetown','mobile_initial']},
 'gurney':{'ids':['gurney'],'offset':[0,-8],'size':96,'priority':90,'zoom':['full','north','mobile_initial']},
 'loop':{'ids':['loop'],'offset':[-18,-22],'size':70,'priority':80,'zoom':['georgetown','mobile_georgetown','mobile_georgetown_430']},
 'heritage':{'ids':['armenian','chulia','kimberley'],'offset':[-16,0],'size':78,'priority':100,'zoom':['full','north','georgetown','mobile_georgetown','mobile_georgetown_430','mobile_initial']},
 'townhall':{'ids':['townhall'],'offset':[14,-18],'size':86,'priority':95,'zoom':['north','georgetown','mobile_georgetown','mobile_georgetown_430']},
 'hin':{'ids':['hin'],'offset':[-6,0],'size':82,'priority':85,'zoom':['georgetown','mobile_georgetown','mobile_georgetown_430']},
 'dim_sum':{'ids':['dim_sum'],'offset':[18,43],'size':54,'priority':65,'zoom':['georgetown','mobile_georgetown','mobile_georgetown_430']},
 'ferry_museum':{'ids':['ferry_museum'],'offset':[-18,-8],'size':58,'priority':85,'zoom':['georgetown','mobile_georgetown','mobile_georgetown_430']},
 'ferry_terminal':{'ids':['ferry_terminal'],'offset':[-16,6],'size':58,'priority':90,'zoom':['georgetown','mobile_georgetown','mobile_georgetown_430']},
 'chew':{'ids':['chew'],'offset':[-5,4],'size':76,'priority':75,'zoom':['georgetown','mobile_georgetown','mobile_georgetown_430']},
}
DEFAULT_VIEW_OFFSETS={
 'georgetown':{'loop':(-7,-9),'heritage':(-3,0),'townhall':(5,-7),'hin':(-8,9),'dim_sum':(-15,17),'ferry_museum':(-8,-6),'ferry_terminal':(-13,7),'chew':(-7,18)},
 'mobile_georgetown':{'loop':(-5,-8),'heritage':(-14,18),'townhall':(12,-12),'hin':(-9,18),'dim_sum':(5,41),'ferry_museum':(-5,-2),'ferry_terminal':(-18,15),'chew':(-25,38)},
 'mobile_georgetown_430':{'loop':(-5,-8),'heritage':(-14,18),'townhall':(12,-12),'hin':(-9,18),'dim_sum':(5,41),'ferry_museum':(-5,-2),'ferry_terminal':(-18,15),'chew':(-25,38)},
}
DEFAULT_SIZE_FACTORS={
 'north':{'heritage':.80,'townhall':.70},
 'georgetown':{'loop':.90,'heritage':.90,'townhall':.85,'hin':.90,'dim_sum':.45,'ferry_museum':.78,'ferry_terminal':.72,'chew':.80},
 'mobile_georgetown':{'loop':.68,'heritage':.42,'townhall':.65,'hin':.60,'dim_sum':.45,'ferry_museum':.45,'ferry_terminal':.45,'chew':.48},
 'mobile_georgetown_430':{'loop':.68,'heritage':.42,'townhall':.65,'hin':.60,'dim_sum':.45,'ferry_museum':.45,'ferry_terminal':.45,'chew':.48},
}
DEFAULT_REGIONS=[
 {'id':'george_town','text':'George Town','latitude':5.4190,'longitude':100.3290,'priority':100,'zoom':['full','north']},
 {'id':'tanjung_bungah','text':'Tanjung Bungah','latitude':5.4675,'longitude':100.2950,'priority':95,'zoom':['full','north']},
 {'id':'air_itam','text':'Air Itam','latitude':5.3980,'longitude':100.2760,'priority':95,'zoom':['full','north']},
 {'id':'penang_hill','text':'Penang Hill','latitude':5.4230,'longitude':100.2720,'priority':90,'zoom':['full','north']},
 {'id':'bayan_lepas','text':'Bayan Lepas','latitude':5.2910,'longitude':100.2820,'priority':80,'zoom':['full']},
]
DEFAULT_DETAIL_LABELS={
 'full':[],
 'north':['floating','gurney','kek','hin'],
 'georgetown':['loop','armenian','chulia','kimberley','townhall','hin','ferry_museum','ferry_terminal','chew','dim_sum'],
 'mobile_georgetown':['loop','armenian','chulia','kimberley','townhall','hin','dim_sum','ferry_museum','ferry_terminal','chew'],
 'mobile_georgetown_430':['loop','armenian','chulia','kimberley','townhall','hin','dim_sum','ferry_museum','ferry_terminal','chew'],
 'mobile_initial':['floating','kek','gurney','armenian'],
}

def ensure_manifest():
 manifest=DATA.get('map_presentation')
 if not manifest:
  manifest={'coordinate_system':'map_position in the retained local equirectangular projection','regions':DEFAULT_REGIONS,'label_policy':{'full':'major regions only','north':'major regions and selected landmark names','georgetown':'collision-aware destination and district labels','minimum_pin_target_px':44}}
  DATA['map_presentation']=manifest
 # Refresh presentation policy and view configuration while leaving all destination coordinates intact.
 manifest['assets']={k:{'anchor_location_ids':v['ids'],'asset':f'assets/landmarks/{k}.webp','display_offset_px':{'x':v['offset'][0],'y':v['offset'][1]},'display_offsets_by_view':{view:{'x':values[k][0],'y':values[k][1]} for view,values in DEFAULT_VIEW_OFFSETS.items() if k in values},'size_factors_by_view':{view:values[k] for view,values in DEFAULT_SIZE_FACTORS.items() if k in values},'asset_size_px':v['size'],'label_priority':v['priority'],'zoom_visibility':v['zoom']} for k,v in DEFAULT_ASSETS.items()}
 manifest['regions']=DEFAULT_REGIONS
 manifest['zoom_scale_policy']={'full':1.05,'north':.88,'georgetown':.24,'mobile_georgetown':.55,'mobile_georgetown_430':.55,'mobile_initial':.82,'units':'multiplier on projected asset size; geography remains fixed'}
 manifest['detail_label_visibility']=DEFAULT_DETAIL_LABELS
 # Explicit geo/display separation on each existing destination; coordinates are copied unchanged.
 for item in DATA['locations']:
  lat=item.get('latitude');lon=item.get('longitude')
  item['geo_anchor']=None if lat is None or lon is None else {'latitude':lat,'longitude':lon}
  item['display_offset_px']={'x':0,'y':0} # interactive pin remains on its true anchor
  item.setdefault('label_priority',70 if item.get('map_pin') else 0)
  item.setdefault('zoom_visibility',['full','north','georgetown'] if item.get('map_pin') else [])
 manifest['viewports']={k:{'box_map_px':list(v['box']),'output_px':list(v['size']),'scale_policy':'uniform geographic projection + viewport fit'} for k,v in VIEWS.items()}
 LOC.write_text(json.dumps(DATA,ensure_ascii=False,indent=2),encoding='utf8')
 return DATA['map_presentation']
PRES=ensure_manifest()

def transform(view):
 box=VIEWS[view]['box']; out=VIEWS[view]['size']; sx=out[0]/(box[2]-box[0]); sy=out[1]/(box[3]-box[1])
 return box,sx,sy

def mapxy(item_or_xy):
 if isinstance(item_or_xy,dict):
  pos=item_or_xy.get('map_position')
  return None if not pos else (float(pos['x']),float(pos['y']))
 return tuple(map(float,item_or_xy))

def geo_xy(lat,lon):
 p=DATA['map_projection']
 return (p['pixel_x_origin']+(lon-p['longitude_origin'])*111320*p['cos_latitude']*p['scale'],
         p['pixel_y_origin']-(lat-p['latitude_origin'])*110540*p['scale'])

def viewxy(pt,view):
 box,sx,sy=transform(view); return ((pt[0]-box[0])*sx,(pt[1]-box[1])*sy)

def asset_anchor(spec):
 ps=[mapxy(BY_ID[i]) for i in spec['anchor_location_ids'] if i in BY_ID and mapxy(BY_ID[i])]
 return (sum(p[0] for p in ps)/len(ps),sum(p[1] for p in ps)/len(ps)) if ps else None

def load_asset(key):
 spec=PRES['assets'][key]
 im=Image.open(ROOT/spec['asset']).convert('RGBA')
 alpha=im.getchannel('A'); box=alpha.point(lambda v:255 if v>10 else 0).getbbox()
 if box: im=im.crop(box)
 pad=max(5,round(max(im.size)*.07)); padded=Image.new('RGBA',(im.width+2*pad,im.height+2*pad),(0,0,0,0));padded.alpha_composite(im,(pad,pad))
 return padded

def asset_records(view):
 _,sx,sy=transform(view); records=[]
 view_scale={'full':1.05,'north':.88,'georgetown':.24,'mobile_georgetown':.55,'mobile_georgetown_430':.55,'mobile_initial':.82}.get(view,1)
 for key,spec in PRES['assets'].items():
  if view not in spec['zoom_visibility']:continue
  anchor=asset_anchor(spec)
  if not anchor:continue
  off=spec['display_offset_px']; off=spec.get('display_offsets_by_view',{}).get(view,off)
  center=(anchor[0]+off['x'],anchor[1]+off['y'])
  screen=viewxy(center,view); size=float(spec['asset_size_px'])*math.sqrt(sx*sy)*view_scale*float(spec.get('size_factors_by_view',{}).get(view,1.0))
  im=load_asset(key); im.thumbnail((round(size),round(size)),Image.Resampling.LANCZOS)
  rect=(screen[0]-im.width/2,screen[1]-im.height/2,screen[0]+im.width/2,screen[1]+im.height/2)
  records.append({'id':key,'spec':spec,'anchor_map':anchor,'center_map':center,'anchor_screen':viewxy(anchor,view),'center_screen':screen,'image':im,'rect':rect,'priority':spec['label_priority']})
 return records

def intersect_area(a,b):
 w=max(0,min(a[2],b[2])-max(a[0],b[0]));h=max(0,min(a[3],b[3])-max(a[1],b[1]));return w*h

def label_candidates(anchor,text,font_size,view,associated=None,occupied=(),assets=None):
 f=ImageFont.truetype(FONT_BOLD,font_size); box=f.getbbox(text); w=box[2]-box[0]+24;h=box[3]-box[1]+18
 assets=assets if assets is not None else asset_records(view); assoc=next((a for a in assets if associated and associated in a['spec']['anchor_location_ids']),None)
 radius=max(34,font_size*2.5)
 if assoc: radius=max(radius, (assoc['rect'][2]-assoc['rect'][0])/2+font_size*.85)
 # Deterministic alternatives centered around the true projected anchor.
 candidates=[(0,-radius),(radius,-radius/2),(radius,0),(radius,radius/2),(0,radius),(-radius,radius/2),(-radius,0),(-radius,-radius/2),
            (0,-radius*1.7),(radius*1.7,0),(0,radius*1.7),(-radius*1.7,0)]
 for mult in (2.4,3.2,4.1):
  candidates.extend([(0,-radius*mult),(radius*mult,0),(0,radius*mult),(-radius*mult,0),
                     (radius*mult*.72,-radius*mult*.72),(radius*mult*.72,radius*mult*.72),
                     (-radius*mult*.72,radius*mult*.72),(-radius*mult*.72,-radius*mult*.72)])
 sw,sh=VIEWS[view]['size']
 best=None
 for dx,dy in candidates:
  x,y=anchor[0]+dx,anchor[1]+dy; rect=(x-w/2,y-h/2,x+w/2,y+h/2)
  score=(abs(dx)+abs(dy))*.12
  collision=False
  if rect[0]<10:score+=(10-rect[0])*25
  if rect[1]<10:score+=(10-rect[1])*25
  if rect[2]>sw-10:score+=(rect[2]-(sw-10))*25
  if rect[3]>sh-10:score+=(rect[3]-(sh-10))*25
  for a in assets:
   area=intersect_area(rect,a['rect'])
   if area:
    score+=area*(8 if a is assoc else 15);collision=True
  for q in occupied:
   area=intersect_area(rect,q)
   if area:score+=area*60;collision=True
  candidate={'text':text,'center':(x,y),'rect':rect,'font_size':font_size,'associated':associated,'score':score}
  if best is None or score<best['score']:best=candidate
  if score<1000 and not collision and rect[0]>=10 and rect[1]>=10 and rect[2]<=sw-10 and rect[3]<=sh-10:return candidate
 # caller can hide low-priority labels when every placement collides.
 return {'text':text,'center':None,'rect':None,'font_size':font_size,'associated':associated,'score':1e12}

def labels_for(view):
 _,sx,sy=transform(view); scale=math.sqrt(sx*sy)
 view_assets=asset_records(view)
 asset_by_key={a['id']:a for a in view_assets}
 if view in ('full','north'):
  specs=[r for r in PRES['regions'] if view in r['zoom']]
  entries=[(r['text'],viewxy((geo_xy(r['latitude'],r['longitude'])[0]+r.get('display_offset_px',{}).get('x',0),geo_xy(r['latitude'],r['longitude'])[1]+r.get('display_offset_px',{}).get('y',0)),view),r['priority'],None) for r in specs]
 else:
  entries=[]
  for ident in PRES['detail_label_visibility'].get(view,[]):
   if ident in ('armenian','chulia','kimberley'):
    name=BY_ID[ident]['name']; item=BY_ID[ident]
   else:
    item=BY_ID.get(ident)
    if not item:continue
    name=DISPLAY_LABELS.get(ident,item['name'])
   anchor=mapxy(item)
   if anchor:
    asset_id='heritage' if ident in ('armenian','chulia','kimberley') else ident
    asset=asset_by_key.get(asset_id)
    point=asset['center_screen'] if asset else viewxy(anchor,view)
    entries.append((name,point,item.get('label_priority',70),ident))
  # Context district tags are neutral area names, not added itinerary stops.
  if view=='georgetown':
   entries += [('Chinatown',viewxy(geo_xy(5.4140,100.3325),view),60,None),('Little India',viewxy(geo_xy(5.4147,100.3285),view),55,None)]
 entries.sort(key=lambda e:-e[2]); chosen=[]; output=[]
 font_size={'full':15,'north':17,'georgetown':12,'mobile_georgetown':10,'mobile_georgetown_430':10,'mobile_initial':13}.get(view,15)
 for text,anchor,priority,ident in entries:
  label=label_candidates(anchor,text,font_size,view,ident,[q['rect'] for q in chosen],view_assets)
  rect=label['rect']
  if rect is None:
   if priority>=90:output.append({**label,'hidden':True})
   continue
  if any(intersect_area(rect,q['rect'])>0 for q in chosen):
   label=label_candidates(anchor,text,font_size,view,ident,[q['rect'] for q in chosen],view_assets)
   if label['rect'] is None:continue
  chosen.append(label);output.append({**label,'hidden':False,'priority':priority})
 return output

def draw_assets(canvas,view,records,diagnostic=False):
 draw=ImageDraw.Draw(canvas,'RGBA')
 for rec in records:
  ax,ay=rec['anchor_screen'];cx,cy=rec['center_screen'];im=rec['image']
  canvas.alpha_composite(im,(round(cx-im.width/2),round(cy-im.height/2)))
 return canvas

def draw_labels(canvas,view,labels,diagnostic=False):
 dr=ImageDraw.Draw(canvas,'RGBA')
 for label in labels:
  if label.get('hidden') or label['rect'] is None:continue
  x,y=label['center'];l,t,r,b=label['rect'];fs=label['font_size'];f=ImageFont.truetype(FONT_BOLD,fs)
  dr.rounded_rectangle((l,t,r,b),radius=max(6,fs*.42),fill=(255,249,231,238),outline=(191,160,119,230),width=max(1,round(fs/12)))
  tb=f.getbbox(label['text']); tw=tb[2]-tb[0];th=tb[3]-tb[1]
  dr.text((x-tw/2,y-th/2-tb[1]),label['text'],font=f,fill=(55,75,68,255))
 return canvas

def render_view(view,add_labels=True,diagnostic=False):
 box=VIEWS[view]['box'];size=VIEWS[view]['size']
 base=Image.open(BASE).convert('RGBA').crop(box).resize(size,Image.Resampling.LANCZOS)
 recs=asset_records(view);draw_assets(base,view,recs)
 labels=labels_for(view) if add_labels else []
 draw_labels(base,view,labels)
 return base,recs,labels

# All artwork views derive from the shared map-space scene and unchanged geographic anchors.
full,full_assets,full_labels=render_view('full')
full.convert('RGB').save(OUT/'penang-preview-full.png')
full.save(OUT/'penang-map.webp','WEBP',quality=91,method=6)
north,_,_=render_view('north');north.convert('RGB').save(OUT/'penang-preview-north.png')
town,_,_=render_view('georgetown');town.convert('RGB').save(OUT/'penang-preview-george-town.png')
label_free,_,_=render_view('full',add_labels=False);label_free.convert('RGB').save(OUT/'penang-preview-label-free.png')

def svg_label_group(group,view):
 _,sx,sy=transform(view); box,_,_=transform(view); items=labels_for(view); out=[f'<g class="{group}">']
 for label in items:
  if label.get('hidden') or label['rect'] is None:continue
  x,y=label['center']; w=label['rect'][2]-label['rect'][0];h=label['rect'][3]-label['rect'][1]
  mx=box[0]+x/sx;my=box[1]+y/sy;mw=w/sx;mh=h/sy;fs=label['font_size']/math.sqrt(sx*sy)
  out.append(f'<g class="label"><rect x="{mx-mw/2:.2f}" y="{my-mh/2:.2f}" width="{mw:.2f}" height="{mh:.2f}" rx="{mh*.43:.2f}"/><text x="{mx:.2f}" y="{my:.2f}" style="font-size:{fs:.2f}px">{html.escape(label["text"])}</text></g>')
 out.append('</g>');return '\n'.join(out)
svg='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 1500"><style>.label rect{fill:#fff9e7;fill-opacity:.94;stroke:#bfa077;stroke-width:1.5}.label text{font:700 1em 'Avenir Next',Arial,sans-serif;fill:#374b44;text-anchor:middle;dominant-baseline:middle}.detail,.mobile-initial,.mobile-georgetown{display:none}.show-details .major{display:none}.show-north .major{display:none}.show-north .north{display:inline}.show-georgetown .major{display:none}.show-georgetown .georgetown{display:inline}.show-mobile-initial .major{display:none}.show-mobile-initial .mobile-initial{display:inline}.show-mobile-georgetown .major{display:none}.show-mobile-georgetown .mobile-georgetown{display:inline}</style>'''+svg_label_group('major','full')+svg_label_group('north','north')+svg_label_group('georgetown','georgetown')+svg_label_group('mobile-initial','mobile_initial')+svg_label_group('mobile-georgetown','mobile_georgetown')+'</svg>'
(OUT/'penang-labels.svg').write_text(svg,encoding='utf8')

view_audits={};rendered={}
for name in ('full','north','georgetown','mobile_georgetown','mobile_georgetown_430','mobile_initial'):
 im,ars,labs=render_view(name);rendered[name]=(im,ars,labs);warnings=[]
 for i,a in enumerate(ars):
  for b in ars[:i]:
   if intersect_area(a['rect'],b['rect'])>40:warnings.append(f"asset overlap {b['id']} / {a['id']}")
 for i,a in enumerate([x for x in labs if not x.get('hidden') and x['rect']]):
  for b in [x for x in labs[:i] if not x.get('hidden') and x['rect']]:
   if intersect_area(a['rect'],b['rect'])>0:warnings.append(f"label overlap {b['text']} / {a['text']}")
  for b in ars:
   if intersect_area(a['rect'],b['rect'])>0:warnings.append(f"label / asset overlap {a['text']} / {b['id']}")
 view_audits[name]=warnings

def phone_mock(map_im,size,title):
 w,h=size;header=52;footer=36;bg=Image.new('RGBA',(w,h),(243,239,224,255));dr=ImageDraw.Draw(bg,'RGBA')
 map_h=h-header-footer;map_im=map_im.copy().resize((w,map_h),Image.Resampling.LANCZOS);bg.alpha_composite(map_im,(0,header))
 dr.rectangle((0,0,w,header),fill=(248,245,235,255));f=ImageFont.truetype(FONT_BOLD,max(14,round(w*.044)));dr.text((15,16),title,font=f,fill=(54,72,65,255))
 bw=max(83,round(w*.25));dr.rounded_rectangle((w-bw-12,10,w-12,header-10),radius=15,fill=(255,252,242,255),outline=(186,157,115,255),width=1)
 bf=ImageFont.truetype(FONT_BOLD,max(10,round(w*.028)));txt='FIT ISLAND';tb=dr.textbbox((0,0),txt,font=bf);dr.text((w-bw/2-12-(tb[2]-tb[0])/2,header/2-(tb[3]-tb[1])/2-1),txt,font=bf,fill=(67,87,77,255))
 dr.rectangle((0,h-footer,w,h),fill=(248,245,235,255));ff=ImageFont.truetype(FONT_REG,max(9,round(w*.024)));caption='SIMULATED VIEW • STATIC PREVIEW';tb=dr.textbbox((0,0),caption,font=ff);dr.text(((w-(tb[2]-tb[0]))/2,h-footer+10),caption,font=ff,fill=(101,108,92,255))
 return bg
initial=rendered['mobile_initial'][0]
phone_mock(initial,(390,844),'PENANG • NORTH').convert('RGB').save(OUT/'penang-proof-390x844-mobile-initial.png')
phone_mock(initial,(430,932),'PENANG • NORTH').convert('RGB').save(OUT/'penang-proof-430x932-mobile-initial.png')
fit=full.copy();fit.thumbnail((390,756),Image.Resampling.LANCZOS);fitbg=Image.new('RGBA',(390,756),(232,239,229,255));fitbg.alpha_composite(fit,((390-fit.width)//2,(756-fit.height)//2))
phone_mock(fitbg,(390,844),'PENANG • ISLAND').convert('RGB').save(OUT/'penang-proof-fit-island-390x844.png')
phone_mock(rendered['mobile_georgetown'][0],(390,844),'GEORGE TOWN').convert('RGB').save(OUT/'penang-proof-390x844-georgetown.png')
phone_mock(rendered['mobile_georgetown_430'][0],(430,932),'GEORGE TOWN').convert('RGB').save(OUT/'penang-proof-430x932-georgetown.png')

diag=Image.open(BASE).convert('RGBA');d=ImageDraw.Draw(diag,'RGBA')
for a in full_assets:
 l,t,r,b=a['rect'];d.rectangle((l,t,r,b),outline=(218,44,77,220),width=2);ax,ay=a['anchor_screen'];cx,cy=a['center_screen'];d.ellipse((ax-5,ay-5,ax+5,ay+5),fill=(20,65,185,255));d.line((ax,ay,cx,cy),fill=(25,65,185,230),width=2)
for lab in full_labels:
 if lab.get('hidden') or lab['rect'] is None:continue
 d.rectangle(lab['rect'],outline=(140,35,170,240),width=2)
d.text((12,12),'Blue = true geographic anchor • red = artwork bounds • purple = labels • line = display offset',font=ImageFont.truetype(FONT_REG,16),fill=(25,43,50,245),stroke_width=3,stroke_fill=(255,255,255,220))
diag.convert('RGB').save(OUT/'penang-preview-diagnostics.png')
keys=list(PRES['assets']);cols=4;cw,ch=420,390;rows=math.ceil(len(keys)/cols);sheet=Image.new('RGBA',(cols*cw,rows*ch+70),(239,236,222,255));sd=ImageDraw.Draw(sheet,'RGBA');title_font=ImageFont.truetype(FONT_BOLD,30);name_font=ImageFont.truetype(FONT_BOLD,23)
sd.text((32,18),'HELLO, PENANG — Blender landmark assets',font=title_font,fill=(54,70,64,255))
for idx,key in enumerate(keys):
 col,row=idx%cols,idx//cols;x=col*cw+16;y=row*ch+68;sd.rounded_rectangle((x,y,x+cw-32,y+ch-18),radius=22,fill=(255,252,242,255),outline=(212,194,160,255),width=2);im=load_asset(key);im.thumbnail((cw-70,ch-105),Image.Resampling.LANCZOS);sheet.alpha_composite(im,(x+(cw-im.width)//2,y+12+(ch-105-im.height)//2));caption=key.replace('_',' ').title();tb=sd.textbbox((0,0),caption,font=name_font);sd.text((x+(cw-32-(tb[2]-tb[0]))/2,y+ch-58),caption,font=name_font,fill=(62,82,73,255))
sheet.convert('RGB').save(OUT/'penang-preview-landmarks.png')
full.convert('RGB').resize((W*2,H*2),Image.Resampling.LANCZOS).save(OUT/'penang-map.png',optimize=True)
# Art-review deliverables: focused George Town close-up, both static iPhone viewport sizes,
# and a diagnostic in the same tight geographic crop. No label is baked into the base SVG.
geo_free,geo_assets,geo_labels=render_view('georgetown',add_labels=False)
geo_free.convert('RGB').save(OUT/'george-town-final-label-free.png')
town.convert('RGB').save(OUT/'george-town-final-labeled.png')
phone_mock(rendered['mobile_georgetown'][0],(390,844),'GEORGE TOWN').convert('RGB').save(OUT/'george-town-mobile-390.png')
phone_mock(rendered['mobile_georgetown_430'][0],(430,932),'GEORGE TOWN').convert('RGB').save(OUT/'george-town-mobile-430.png')
# Tight-crop placement diagnostic: blue dot is the fixed geographic anchor, red is artwork bounds.
diag_city=geo_free.copy();dd=ImageDraw.Draw(diag_city,'RGBA')
for a in geo_assets:
 l,t,r,b=a['rect'];dd.rectangle((l,t,r,b),outline=(218,44,77,235),width=3);ax,ay=a['anchor_screen'];cx,cy=a['center_screen'];dd.ellipse((ax-6,ay-6,ax+6,ay+6),fill=(20,65,185,255));dd.line((ax,ay,cx,cy),fill=(25,65,185,230),width=3)
for lab in geo_labels:
 if lab.get('hidden') or lab['rect'] is None:continue
 dd.rectangle(lab['rect'],outline=(140,35,170,245),width=3)
dd.text((20,18),'Blue = fixed geographic anchor • red = clay artwork bounds • line = display offset',font=ImageFont.truetype(FONT_REG,22),fill=(25,43,50,245),stroke_width=4,stroke_fill=(255,255,255,235))
diag_city.convert('RGB').save(OUT/'george-town-placement-diagnostic.png')
(OUT/'george-town-landmark-assets.png').write_bytes((OUT/'penang-preview-landmarks.png').read_bytes())

(OUT/'placement-diagnostics.json').write_text(json.dumps({'coordinate_system':'1120x1500 canonical map pixels','assets':[{'id':a['id'],'anchor':a['anchor_screen'],'display_center':a['center_screen'],'bbox':a['rect']} for a in full_assets],'labels':[{'text':l['text'],'bbox':l['rect'],'hidden':l.get('hidden',False)} for l in full_labels],'view_warnings':view_audits,'note':'Illustration offsets only; geographic coordinates unchanged.'},indent=2),encoding='utf8')
print('Rendered all review artwork and static viewport mockups.')
print('Viewport overlap diagnostics:',{k:len(v) for k,v in view_audits.items()})
