"""Build reusable clay landmark models and transparent WebP renders with Blender 5.x."""
import bpy, math, os
from mathutils import Vector
ROOT=os.path.dirname(os.path.abspath(__file__))
ASSET_DIR=os.path.join(ROOT,'assets','landmarks');os.makedirs(ASSET_DIR,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=True
scene.render.resolution_x=600;scene.render.resolution_y=600;scene.render.resolution_percentage=100
scene.render.film_transparent=True
scene.render.image_settings.file_format='WEBP';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.quality=88
scene.render.image_settings.color_mode='RGBA';scene.render.filepath=os.path.join(ASSET_DIR,'asset.webp')
scene.view_settings.view_transform='AgX'
world=bpy.data.worlds.new('Transparent pastel studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.81,.89,.89,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45;scene.world=world
# shared hand-shaped clay palette

def mat(n,c,rough=.78,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;return m
cream=mat('Cream clay',(.96,.88,.74));sand=mat('Warm stone',(.83,.69,.48));coral=mat('Terracotta coral',(.82,.40,.31));peach=mat('Peach plaster',(.94,.61,.46));yellow=mat('Butter yellow',(.95,.76,.38));blue=mat('Peranakan blue',(.39,.65,.69));sky=mat('Mosque soft blue',(.39,.68,.78));sage=mat('Sage green',(.43,.63,.42));mint=mat('Mint green',(.63,.76,.52));leaf=mat('Light leaf',(.72,.81,.52));dark=mat('Window glass',(.22,.36,.38));wood=mat('Dark timber',(.43,.25,.16));gold=mat('Warm brass clay',(.87,.63,.25));white=mat('Ivory',(.99,.95,.85));road=mat('Garden path',(.96,.83,.64));sea=mat('Water turquoise',(.40,.75,.78));

def activate(coll):
 bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children['Landmarks'].children[coll.name]
def cube(n,loc,dim,ma,b=.07):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma)
 if b:
  m=o.modifiers.new('Soft molded corners','BEVEL');m.width=min(b,min(dim)/3);m.segments=4;o.modifiers.new('Soft surface normals','WEIGHTED_NORMAL')
 return o
def sphere(n,loc,sc,ma):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=1,location=loc);o=bpy.context.object;o.name=n;o.scale=sc;o.data.materials.append(ma);bpy.ops.object.shade_smooth();return o
def cylinder(n,loc,r,depth,ma,verts=20):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=n;o.data.materials.append(ma);m=o.modifiers.new('Soft turned edge','BEVEL');m.width=min(.06,r*.25,depth*.15);m.segments=3;o.modifiers.new('Smooth normals','WEIGHTED_NORMAL');return o
def cone(n,loc,r1,r2,depth,ma,verts=20):
 bpy.ops.mesh.primitive_cone_add(vertices=verts,radius1=r1,radius2=r2,depth=depth,location=loc);o=bpy.context.object;o.name=n;o.data.materials.append(ma);m=o.modifiers.new('Soft tapered edge','BEVEL');m.width=min(.045,depth*.1);m.segments=3;o.modifiers.new('Smooth normals','WEIGHTED_NORMAL');return o
def curve(n,pts,ma,width=.05):
 c=bpy.data.curves.new(n,'CURVE');c.dimensions='3D';c.bevel_depth=width;c.bevel_resolution=3;s=c.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
 for bp,p in zip(s.bezier_points,pts): bp.co=p;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
 o=bpy.data.objects.new(n,c);bpy.context.collection.objects.link(o);o.data.materials.append(ma);return o
def onion_dome(n,loc,rx,ry,height,ma):
 # A softly pinched bulb dome built from a revolved hand-shaped profile.
 profile=[(0,0),(.48,.08),(.82,.22),(1,.45),(.94,.66),(.68,.79),(.39,.88),(.19,1),(0,1.06)]
 verts=[]; faces=[]; steps=32
 for radius,zf in profile:
  for i in range(steps):
   a=math.tau*i/steps; verts.append((loc[0]+math.cos(a)*rx*radius,loc[1]+math.sin(a)*ry*radius,loc[2]+height*zf))
 for j in range(len(profile)-1):
  for i in range(steps):
   a=j*steps+i; b=j*steps+(i+1)%steps; faces.append((a,b,b+steps,a+steps))
 me=bpy.data.meshes.new(n+' mesh');me.from_pydata(verts,[],faces);me.materials.append(ma);o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);o.modifiers.new('Soft dome surface','SUBSURF').levels=1;o.modifiers.new('Dome normals','WEIGHTED_NORMAL');return o
def hiproof(n,x,y,z,w,d,ma,rise=.3):
 v=[(x-w/2,y-d/2,z),(x+w/2,y-d/2,z),(x+w/2,y+d/2,z),(x-w/2,y+d/2,z),(x-w*.27,y,z+rise),(x+w*.27,y,z+rise)]
 f=[(0,1,5,4),(2,3,4,5),(1,2,5),(3,0,4),(0,3,2,1)]
 me=bpy.data.meshes.new(n+' mesh');me.from_pydata(v,[],f);me.materials.append(ma);o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);o.modifiers.new('Rounded hand-shaped eaves','BEVEL').width=.055;o.modifiers.new('Roof normals','WEIGHTED_NORMAL');return o
def collection(name):
 c=bpy.data.collections.new(name);bpy.data.collections['Landmarks'].children.link(c);activate(c);return c
# base collection
root=bpy.data.collections.new('Landmarks');scene.collection.children.link(root)
assets=[]
# 1. Kek Lok Si — terraced halls and an unmistakable seven-tier Chinese pagoda.
c=collection('kek');assets.append(('kek',c))
cube('Temple plinth',(0,0,.14),(3.6,2.8,.28),sand,.15)
for i in range(4): cube('Temple terrace stair',(0,-1.15+i*.35,.27+i*.10),(1.55,.31,.13),cream,.055)
for j,(z,w,d,color) in enumerate([(.57,2.45,1.65,coral),(1.12,1.98,1.35,cream),(1.65,1.5,1.06,peach)]):
 cube('Prayer hall mass '+str(j),(-.28,.05,z),(w*.84,d*.70,.48),color,.14)
 for dx in [-w*.34,w*.34]:
  for dy in [-d*.27,d*.27]: cylinder('Carved hall column',(-.28+dx,.05+dy,z),.065,.53,wood,12)
 hiproof('Swept temple roof '+str(j),-.28,.05,z+.27,w*1.12,d*1.12,coral if j==1 else wood,.32)
 # Soft clay ridge caps and painted ceramic roof bands.
 curve('Temple roof ridge ornament '+str(j),[(-.28-w*.24,.05,z+.58),(-.28,.05,z+.62),(-.28+w*.24,.05,z+.58)],gold,.035)
 for dx in [-w*.34,0,w*.34]:
  for k in range(3): sphere('Clay roof tile bead',(-.28+dx,-d*.53+k*.22,z+.43),(.055,.045,.045),yellow if k==1 else coral)
 cube('Temple frieze panel',(-.28,-d*.36,z+.06),(w*.55,.05,.16),gold,.045)
 for dx in [-w*.56,w*.56]:
  for dy in [-d*.55,d*.55]: sphere('Golden lifted eave tip',(-.28+dx,.05+dy,z+.47),(.11,.11,.12),gold)
# seven shrinking octagonal tower storeys
for j in range(7):
 z=.52+j*.47;r=.66-j*.047
 cylinder('Pagoda octagonal chamber',(1.0,.52,z),r*.70,.39,[coral,cream,peach][j%3],8)
 cylinder('Pagoda roof eave',(1.0,.52,z+.23),r,.13,wood if j%2 else coral,8)
 for k in range(8):
  a=math.tau*k/8;cylinder('Pagoda slender timber post',(1+math.cos(a)*r*.63,.52+math.sin(a)*r*.63,z),.027,.32,gold,10)
 for k in range(8):
  a=math.tau*k/8;sphere('Pagoda curled roof corner',(1+math.cos(a)*r,.52+math.sin(a)*r,z+.25),(.07,.07,.075),gold)
cone('Pagoda spire',(1,.52,4.0),.10,0,.34,gold)
cylinder('Bodhisattva pedestal',(-1.36,.45,.46),.31,.56,cream,12);sphere('Goddess statue',(-1.36,.45,1.02),(.19,.17,.57),gold);sphere('Goddess halo',(-1.36,.45,1.48),(.28,.08,.30),yellow)
# 2. Tanjung Bungah floating mosque, with coastal raft and blue dome.
c=collection('floating');assets.append(('floating',c))
cube('Mosque aqua coastal platform',(0,0,.10),(3.2,2.25,.20),sea,.22);cube('Sandstone mosque apron',(0,0,.25),(2.45,1.85,.18),cream,.15)
for dx in [-.77,.77]:
 for dy in [-.48,.48]: cylinder('Open arcade support',(dx,dy,.62),.075,.72,blue,16)
cube('Mosque prayer hall',(0,0,.94),(1.9,1.34,.94),white,.18)
cube('Mosque entrance arch surround',(0,-.71,.83),(.53,.08,.67),cream,.20)
cube('Mosque entrance inset',(0,-.765,.80),(.29,.035,.47),blue,.13)
for dx in [-.38,.38]: sphere('Mosque facade rosette',(dx,-.70,1.28),(.075,.035,.075),gold)
for dx in [-1.15,1.15]:
 for dy in [-.78,.78]: cylinder('Stilt over seawater',(dx,dy,-.03),.07,.55,wood,14)
for dx in [-.58,.58]:
 cube('Arched window inset',(dx,-.69,.98),(.27,.04,.45),sky,.12);cube('Window mullion',(dx,-.72,.98),(.035,.04,.40),white,.018)
cylinder('Dome drum',(0,0,1.47),.47,.28,cream,24);onion_dome('Blue onion-shaped mosque dome',(0,0,1.54),.66,.66,.48,sky);cone('Dome finial',(0,0,2.12),.075,0,.23,gold)
for dx in [-1.08,1.08]:
 cylinder('Minaret shaft',(dx,0,1.23),.13,1.82,white);cylinder('Minaret balcony',(dx,0,1.83),.22,.12,gold);cone('Pointed minaret roof',(dx,0,2.35),.22,.015,.42,blue);sphere('Minaret cap',(dx,0,2.60),(.055,.055,.09),gold)
# 3. George Town Peranakan shophouse cluster (shared contextual asset for street pins).
c=collection('heritage');assets.append(('heritage',c))
def shop3d(x,y,w,h,color,roofmat,style):
 cube('Shophouse painted facade',(x,y,.30+h/2),(w,.78,h),color,.12)
 cube('Covered five-foot way',(x,y-.43,.46),(w*1.12,.29,.18),cream,.07)
 for dx in [-w*.42,w*.42]:cube('Arcade pier',(x+dx,y-.51,.68),(.08,.12,.58),white,.04)
 # upper storey windows and colored shutters
 for z in [.76,.34+h*.79]:
  for dx in [-w*.24,w*.24]:
   cube('Deep-set timber window',(x+dx,y-.405,z),(.24,.045,.28),dark,.06)
   cube('Blue painted shutter',(x+dx-.15,y-.44,z),(.055,.04,.27),blue,.022)
   cube('Window sill',(x+dx,y-.48,z-.16),(.36,.09,.06),white,.025)
 cube('Arched shop entrance',(x,y-.415,.57),(.27,.045,.47),wood,.08)
 cube('Carved transom above shop door',(x,y-.46,.84),(.39,.035,.11),gold,.035)
 cube('Continuous pastel stringcourse',(x,y-.405,.99), (w*.96,.04,.055),white,.02)
 for dx in [-w*.34,0,w*.34]:
  sphere('Hand-painted floral medallion',(x+dx,y-.445,1.06),(.055,.025,.055),yellow)
  cube('Window lintel',(x+dx,y-.435,1.26),(.34,.045,.055),cream,.02)
 # Small grille bars and sill brackets distinguish the Peranakan shopfronts.
 for dx in [-w*.24,w*.24]:
  for zz in [.76,.34+h*.79]:
   cube('Window vertical grille',(x+dx,y-.455,zz),(.025,.025,.20),gold,.01)
   for side in [-1,1]: cube('Sill support',(x+dx+side*.12,y-.48,zz-.19),(.035,.04,.09),coral,.012)
 if style==0: hiproof('Peranakan pitched tiled roof',x,y,.30+h,w*1.14,.95,roofmat,.27)
 elif style==1:
  cube('Heritage parapet roof',(x,y,.35+h),(w*1.13,.9,.19),roofmat,.08)
  for dx in [-w*.35,0,w*.35]:cube('Roof tile ridge',(x+dx,y,.47+h),(.04,.75,.04),gold,.018)
 else:
  hiproof('Peranakan blue glazed roof',x,y,.30+h,w*1.18,.99,roofmat,.19)
  for dx in [-w*.58,w*.58]:sphere('Upturned roof tip',(x+dx,y-.42,.49+h),(.10,.09,.11),gold)
# Rich painted roof edging and molded ridge ends make the roofs read as local tiled forms.
for sx in [-1.1,0,1.08]:
 for k in range(5):
  sphere('Glazed roof tile accent',(sx-.36+k*.18,.16,1.80),(.055,.07,.045),blue if k%2 else yellow)
 sphere('Roof ridge finial',(sx,.16,1.92),(.09,.09,.12),gold)
cube('Shophouse lane plinth',(0,0,.1),(3.65,1.7,.20),sand,.15)
shop3d(-1.10,.16,.92,1.36,coral,wood,0);shop3d(0,.16,.88,1.02,yellow,blue,1);shop3d(1.08,.16,.96,1.52,blue,coral,2)
# 4. Penang's paired civic landmarks: the low assembly Town Hall and Victorian City Hall.
c=collection('townhall');assets.append(('townhall',c))
# Shared garden plinth; the two silhouettes are separated so their different dates and roles read clearly.
cube('Civic garden island',(0,0,.14),(4.45,2.55,.27),sage,.18)
cube('Town Hall stone terrace',(-.83,.10,.31),(2.36,1.72,.20),sand,.09)
cube('City Hall stone terrace',(1.30,.10,.31),(1.60,1.72,.20),sand,.09)
# Historic Town Hall: broad one-storey assembly frontage with a veranda, arched openings and a shallow parapet.
cube('Town Hall assembly wing',(-.83,.23,.88),(2.12,1.03,1.02),cream,.13)
cube('Town Hall long verandah roof',(-.83,-.42,1.46),(2.40,.42,.14),white,.07)
cube('Town Hall parapet cap',(-.83,.23,1.45),(2.18,1.10,.14),white,.07)
for i in range(5):
 x=-1.67+i*.42
 cube('Town Hall tall shuttered opening',(x,-.302,.93),(.25,.045,.53),blue,.07)
 cube('Town Hall window arch crown',(x,-.325,1.23),(.32,.045,.11),sand,.045)
 curve('Town Hall rounded arcade arch',[(x-.14,-.366,1.18),(x-.13,-.366,1.29),(x,-.366,1.36),(x+.13,-.366,1.29),(x+.14,-.366,1.18)],gold,.025)
 cube('Town Hall lower panel',(x,-.33,.62),(.26,.045,.10),wood,.025)
for x in [-1.88,-1.25,-.40,.22]:
 cube('Town Hall veranda pier',(x,-.59,.88),(.095,.12,.96),white,.04)
 sphere('Town Hall pier capital',(x,-.59,1.38),(.12,.11,.08),gold)
# Fine balustrade above the veranda roof and a central round crest.
cube('Town Hall parapet rail',(-.83,-.42,1.64),(2.18,.10,.08),cream,.035)
for i in range(11):
 x=-1.83+i*.20;cylinder('Town Hall baluster',(x,-.42,1.57),.025,.16,white,10)
sphere('Town Hall oval civic crest',(-.83,-.36,1.22),(.17,.045,.20),gold)
# Victorian City Hall: taller eastern wing with a corner tower, arched sash windows and stepped roofline.
cube('Victorian City Hall main block',(1.30,.20,.98),(1.36,1.15,1.30),white,.12)
cube('City Hall projecting entrance bay',(1.30,-.46,.86),(.68,.32,1.05),cream,.10)
for z in [.72,1.27]:
 for x in [.94,1.65]:
  cube('City Hall recessed sash window',(x,-.398,z),(.23,.05,.39),blue,.06)
  cube('City Hall window lintel',(x,-.43,z+.22),(.31,.06,.07),sand,.025)
  curve('City Hall arched sash surround',[(x-.12,-.438,z+.16),(x-.12,-.438,z+.25),(x,-.438,z+.31),(x+.12,-.438,z+.25),(x+.12,-.438,z+.16)],gold,.022)
for x in [.70,1.90]:
 cube('City Hall pilaster',(x,-.43,1.02),(.10,.09,1.12),cream,.035)
cube('City Hall cornice',(1.30,.20,1.68),(1.58,1.34,.15),sand,.06)
cube('City Hall upper parapet',(1.30,.22,1.81),(1.38,1.10,.18),white,.06)
# A restrained Victorian corner pavilion, not a generic Greek pediment.
cube('City Hall clock tower base',(1.72,.24,2.06),(.54,.63,.44),cream,.09)
cube('Clock face surround',(1.72,-.087,2.08),(.32,.045,.32),white,.08)
cylinder('Clock face',(1.72,-.12,2.08),.105,.025,gold,24)
cube('Clock hand vertical',(1.72,-.14,2.11),(.018,.015,.075),wood,.006)
cube('Clock hand horizontal',(1.75,-.14,2.08),(.065,.015,.018),wood,.006)
cube('Clock tower neck',(1.72,.24,2.39),(.40,.49,.27),white,.06)
hiproof('City Hall red tiled pavilion roof',1.72,.24,2.54,.62,.72,coral,.27)
for x in [.67,1.93]:
 sphere('Civic garden tree canopy',(x,.80,.67),(.25,.25,.30),mint);cylinder('Civic garden tree trunk',(x,.80,.46),.06,.38,wood,12)
# 5. Gurney Bay urban park miniature.
c=collection('gurney');assets.append(('gurney',c))
cube('Gurney Bay park island',(0,0,.13),(3.6,2.35,.23),sage,.30);cube('Sea edge walk',(0,-.91,.29),(3.45,.34,.11),cream,.13)
curve('Curving promenade', [(-1.6,-.83,.36),(-.8,-.75,.37),(0,-.87,.37),(.75,-.80,.37),(1.6,-.87,.36)],white,.06)
cylinder('Reflecting pool',(.55,.15,.29),.52,.07,sea,40)
for i in range(7):
 x=-1.5+i*.5;cube('Flower bed',(x,.72,.31),(.38,.33,.15),mint,.11);sphere('Rounded shrub',(x,.72,.50),(.20,.20,.20),leaf)
for x,y in [(-1.22,-.05),(-.75,.28),(1.15,.22),(1.45,-.22)]:
 cylinder('Park tree trunk',(x,y,.62),.08,.55,wood,12);sphere('Park tree canopy',(x,y,.98),(.30,.30,.35),sage);sphere('Canopy lobe',(x+.16,y+.02,1.0),(.20,.20,.23),mint)
for x in [-1.3,1.3]:cylinder('Promenade lamp post',(x,-.73,.73),.035,.72,wood,12);sphere('Warm lamp globe',(x,-.73,1.12),(.12,.12,.12),yellow)
# 6. Hin Bus Depot: old industrial shed with trussed roof and art-yard character.
c=collection('hin');assets.append(('hin',c))
cube('Hin Bus Depot yard',(0,0,.12),(3.2,2.0,.20),road,.17);cube('Depot masonry hall',(0,.12,.90),(2.45,1.30,1.42),coral,.14)
for i in range(5):
 x=-.92+i*.46;cube('Depot clerestory window',(x,-.56,1.32),(.28,.05,.34),sky,.07);cube('Depot muntin',(x,-.59,1.32),(.035,.04,.31),white,.015)
for i in range(4):
 x=-.9+i*.6;hiproof('Depot sawtooth roof module',x,.1,1.63,.74,1.55,wood,.24);cube('Roof skylight',(x,.08,1.80),(.32,.72,.06),blue,.04)
# blank framed art panels in the courtyard
for x,col in [(-1.0,blue),(0, yellow),(1.0,mint)]:cube('Open-air art panel',(x,-.83,.73),(.55,.08,.55),col,.06)
# 7. Loop on Leith: distinctive modern heritage hotel frontage, no text baked in.
c=collection('loop');assets.append(('loop',c))
cube('Loop hotel footpath plinth',(0,0,.15),(2.9,1.75,.28),sand,.14);cube('Loop on Leith hotel facade',(0,.12,1.48),(2.3,1.25,2.48),peach,.18)
cube('Hotel parapet roof',(0,.12,2.80),(2.5,1.40,.22),coral,.12)
for level in range(4):
 z=.68+level*.52
 for i in range(5):
  x=-.86+i*.43;cube('Hotel balcony opening',(x,-.53,z),(.25,.045,.31),blue,.06);cube('Balcony rail',(x,-.64,z-.17),(.32,.08,.055),cream,.025)
for x in [-1.0,1.0]:cube('Hotel corner pilaster',(x,-.56,1.48),(.10,.09,2.25),gold,.035)
# 8. Dim sum storefront.
c=collection('dim_sum');assets.append(('dim_sum',c))
cube('Dim sum tea house plinth',(0,0,.12),(2.8,1.75,.22),sand,.15);cube('Tea house storefront',(0,.10,.78),(2.05,1.12,1.20),yellow,.15);hiproof('Tea house tiled roof',0,.1,1.40,2.3,1.38,coral,.32)
cube('Striped shop awning',(0,-.58,.86),(2.18,.40,.20),coral,.09)
for x in [-.62,0,.62]:cube('Shopfront window',(x,-.48,.92),(.34,.04,.46),blue,.07)
for z in [.68,.84]:cube('Steamer basket',(0,-.79,z),(.52,.44,.18),wood,.07)
# 9. Penang Ferry Museum exterior: retired ferry hull and decks.
c=collection('ferry_museum');assets.append(('ferry_museum',c))
def hull_mesh():
 verts=[(-1.65,-.52,.18),(1.45,-.52,.18),(1.12,.52,.18),(-1.3,.52,.18),(-1.3,-.35,.48),(1.1,-.35,.48),(.84,.35,.48),(-1.05,.35,.48)]
 faces=[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7),(0,3,2,1)]
 me=bpy.data.meshes.new('Ferry hull mesh');me.from_pydata(verts,[],faces);me.materials.append(blue);o=bpy.data.objects.new('Rounded retired ferry hull',me);bpy.context.collection.objects.link(o);o.modifiers.new('Soft ship bow','BEVEL').width=.08;o.modifiers.new('Hull normals','WEIGHTED_NORMAL')
hull_mesh();cube('Ferry main deck',(0,0,.62),(2.1,.80,.27),cream,.09);cube('Ferry upper deck',(-.18,.04,.91),(1.34,.66,.32),white,.09);cube('Ferry bridge',(.48,.02,1.18),(.72,.60,.34),white,.08)
for x in [-.67,-.28,.11,.50]:cube('Ferry blue porthole',(x,-.37,.68),(.18,.035,.13),sky,.05)
for x in [-.55,-.14,.27]:cube('Upper deck window',(x,-.31,.95),(.20,.04,.15),blue,.035)
cylinder('Ferry exhaust stack',(-.72,.08,1.22),.11,.47,coral,16);sphere('Ferry wake puff',(-.85,.08,1.52),(.22,.15,.13),cream)
# 10. Raja Tun Uda ferry terminal and pier.
c=collection('ferry_terminal');assets.append(('ferry_terminal',c))
cube('Terminal waterfront plinth',(0,0,.12),(3.8,2.1,.22),sand,.15);cube('Terminal hall',(0,.38,.83),(2.35,1.12,1.25),cream,.14);cube('Long terminal roof',(0,.38,1.52),(2.6,1.38,.20),coral,.1)
for x in [-.82,-.40,0,.40,.82]:cube('Terminal glass panel',(x,-.20,.87),(.28,.05,.62),sky,.06)
cube('Passenger pier',(1.50,-.48,.22),(1.90,.54,.20),wood,.07)
for i in range(6):cylinder('Pier stilts',(0.78+i*.27,-.74,.07),.045,.35,wood,12)
for dy in [-.73,-.22]:curve('Pier handrail',[(.70,dy,.48),(1.42,dy,.48),(2.35,dy,.48)],cream,.035)
# 11. Chew Jetty: timber stilt houses on a boardwalk.
c=collection('chew');assets.append(('chew',c))
cube('Chew Jetty boardwalk',(0,0,.22),(3.5,.86,.20),wood,.06)
for i in range(12):cylinder('Jetty stilts',(-1.6+i*.29,0,.02),.045,.44,wood,12)
for x,col in [(-1.0,peach),(0,blue),(1.0,yellow)]:
 cube('Clan jetty timber cottage',(x,.12,.85),(.85,.84,1.05),col,.10);hiproof('Cottage clay roof',x,.12,1.40,1.0,1.0,coral,.28)
 for dx in [-.22,.22]:cube('Cottage window',(x+dx,-.315,.90),(.17,.04,.24),dark,.045)
# common area light, camera
bpy.ops.object.light_add(type='AREA',location=(-5,-7,12));light=bpy.context.object;light.name='Large softbox';light.data.energy=1300;light.data.shape='DISK';light.data.size=7
bpy.ops.object.camera_add(location=(8,-10,10));cam=bpy.context.object;cam.name='Shared three-quarter orthographic camera';cam.data.type='ORTHO';scene.camera=cam
# Keep each asset as a named, editable collection and render each against true transparency.
for ident,coll in assets:
 asset_objs=[o for o in coll.objects]
 for o in scene.objects:
  if o.type not in {'CAMERA','LIGHT'}: o.hide_render=(o not in asset_objs)
 # world stays transparent; orient and fit by the actual transformed asset bounds.
 bpy.context.view_layer.update()
 corners=[o.matrix_world@Vector(corner) for o in asset_objs for corner in o.bound_box]
 center=sum(corners,Vector())/len(corners);ext=Vector([max(p[i] for p in corners)-min(p[i] for p in corners) for i in range(3)])
 cam.location=center+Vector((8,-10,12));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=max(ext)*1.75;scene.camera=cam
 scene.render.filepath=os.path.join(ASSET_DIR,ident+'.webp')
 bpy.ops.render.render(write_still=True)
 # Restore hidden model visibility for Blender editing, while preserving collection organization.
 for o in scene.objects:
  if o.type not in {'CAMERA','LIGHT'}: o.hide_render=False
# Save editable source after camera settles on final asset.
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'penang.blend'))
print('Built %d independent clay collections and transparent WebP assets in %s'%(len(assets),ASSET_DIR))
