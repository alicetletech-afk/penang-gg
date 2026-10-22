#!/usr/bin/env python3
"""Build the 2D cartoon Penang map from the included OSM polygon and canonical locations.json."""
import json, math, html, os
ROOT=os.path.dirname(os.path.abspath(__file__))
GEO=os.path.join(ROOT,'data','penang-island.geojson')
LOC=os.path.join(ROOT,'locations.json')
OUT=os.path.join(ROOT,'penang-base.svg')
W,H=1120,1500
features=json.load(open(GEO,encoding='utf8'))['features']
ring=features[0]['geometry']['coordinates'][0]
loc=json.load(open(LOC,encoding='utf8'))
# Equirectangular local projection: longitude is corrected by latitude cosine.
lat0=sum(p[1] for p in ring[:-1])/len(ring[:-1]); lon0=sum(p[0] for p in ring[:-1])/len(ring[:-1]); coslat=math.cos(math.radians(lat0))
projected=[((lon-lon0)*111320*coslat,(lat-lat0)*110540) for lon,lat in ring]
minx=min(x for x,y in projected); maxx=max(x for x,y in projected); miny=min(y for x,y in projected); maxy=max(y for x,y in projected)
margin=74; scale=min((W-2*margin)/(maxx-minx),(H-2*margin)/(maxy-miny))
ox=(W-(maxx-minx)*scale)/2-minx*scale; oy=(H-(maxy-miny)*scale)/2+maxy*scale
def xy(lon,lat):
 x=(lon-lon0)*111320*coslat; y=(lat-lat0)*110540
 return (ox+x*scale,oy-y*scale)
def path_for(coords):
 pts=[xy(lon,lat) for lon,lat in coords]
 return 'M '+' L '.join(f'{x:.1f},{y:.1f}' for x,y in pts)+' Z'
coast=path_for(ring)
# Distances and small decorative marks use the same geographic projection as pins.
def pathgeo(points): return 'M '+' L '.join(f'{xy(lon,lat)[0]:.1f},{xy(lon,lat)[1]:.1f}' for lon,lat in points)
def smoothgeo(points, closed=False):
    # Catmull-Rom converted to cubic curves for hand-shaped landscape edges.
    pts=[xy(*p) for p in points]
    if closed: pts=pts[:-1]
    if len(pts)<3: return pathgeo(points)
    out=f'M {pts[0][0]:.1f},{pts[0][1]:.1f}'
    n=len(pts)
    for i in range(n if closed else n-1):
        p0=pts[(i-1)%n] if (closed or i>0) else pts[i]
        p1=pts[i]; p2=pts[(i+1)%n]; p3=pts[(i+2)%n] if (closed or i+2<n) else p2
        c1=(p1[0]+(p2[0]-p0[0])/6,p1[1]+(p2[1]-p0[1])/6)
        c2=(p2[0]-(p3[0]-p1[0])/6,p2[1]-(p3[1]-p1[1])/6)
        out+=f' C {c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}'
    return out+(' Z' if closed else '')
# Subtle district/landscape regions are geographic annotations, clipped to the real island.
forest=[(100.225,5.425),(100.235,5.448),(100.255,5.460),(100.278,5.451),(100.294,5.433),(100.288,5.410),(100.274,5.387),(100.255,5.381),(100.237,5.398)]
urban=[(100.296,5.405),(100.319,5.414),(100.341,5.423),(100.345,5.443),(100.323,5.447),(100.307,5.437)]
# Mainland fragment only provides visual strait context; no mainland itinerary locations are drawn.
svg=[]
def add(s): svg.append(s)
add(f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
<title id="title">Penang Island illustrated travel map</title><desc id="desc">A cartoon base map built from OpenStreetMap coastline geometry, with soft pastel sea, forested central hills, simplified roads and the George Town, Tanjung Bungah and Air Itam districts.</desc>
<defs>
 <filter id="islandShadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="12" stdDeviation="12" flood-color="#577578" flood-opacity=".20"/></filter>
 <clipPath id="islandClip"><path d="{coast}"/></clipPath>
 <pattern id="seaGrain" width="92" height="78" patternUnits="userSpaceOnUse"><path d="M8 18q12-6 24 0m42 24q8-4 16 0M20 65q10-5 20 0" fill="none" stroke="#fff" stroke-width="1.7" stroke-linecap="round" opacity=".18"/><path d="M46 10q5-3 10 0" fill="none" stroke="#fff" stroke-width="1.2" opacity=".12"/></pattern>
 <pattern id="cityDots" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="4" cy="5" r="1.5" fill="#d29e7e" opacity=".22"/><circle cx="14" cy="14" r="1" fill="#d29e7e" opacity=".18"/></pattern>
</defs>
<rect width="{W}" height="{H}" fill="#A8DDE5"/><rect width="{W}" height="{H}" fill="url(#seaGrain)"/>
''')
# Accurate full-island polygon with a light sand cliff rim and a warm, illustrated top surface.
add(f'<path d="{coast}" fill="#E9D5AC" stroke="#FFF6E6" stroke-width="15" stroke-linejoin="round" filter="url(#islandShadow)"/>')
add(f'<path d="{coast}" fill="#E9D5AC" stroke="#D7BC8C" stroke-width="3.8" stroke-linejoin="round"/>')
add(f'<g clip-path="url(#islandClip)">')
add(f'<path d="{smoothgeo(forest,True)}" fill="#A8C8A0" opacity=".30"/>')
# Layered, irregular highland clearings and ridges replace the former flat green blob.
for pts,color,opacity in [([(100.232,5.432),(100.240,5.447),(100.254,5.453),(100.266,5.447),(100.270,5.435),(100.259,5.425),(100.244,5.423)],'#8FB68B','.55'), ([(100.255,5.438),(100.265,5.449),(100.278,5.446),(100.287,5.434),(100.280,5.423),(100.266,5.422)],'#B7CC91','.48'), ([(100.239,5.414),(100.248,5.425),(100.262,5.423),(100.271,5.413),(100.265,5.402),(100.251,5.401)],'#97BA87','.52'), ([(100.265,5.409),(100.275,5.420),(100.286,5.416),(100.291,5.404),(100.281,5.394),(100.270,5.398)],'#B6CB92','.46'), ([(100.246,5.394),(100.257,5.402),(100.269,5.399),(100.278,5.387),(100.265,5.379),(100.251,5.382)],'#8FB68B','.5')]: add(f'<path d="{smoothgeo(pts,True)}" fill="{color}" opacity="{opacity}"/>')
add(f'<path d="{smoothgeo(urban,True)}" fill="url(#cityDots)" opacity=".9"/>')
# Soft, curved contour accents follow the upland spine without implying surveyed elevation.
for pts,sw in [([(100.236,5.432),(100.248,5.445),(100.261,5.445),(100.273,5.436),(100.276,5.424)],2.7), ([(100.245,5.414),(100.255,5.422),(100.268,5.419),(100.279,5.409)],2.1), ([(100.250,5.393),(100.259,5.399),(100.269,5.393)],1.8)]:
 add(f'<path d="{smoothgeo(pts)}" fill="none" stroke="#6F9875" stroke-width="{sw}" stroke-linecap="round" opacity=".40"/>')
# A few narrow highland footpaths sit inside the forest region only; these are decorative trails, not trip routes.
for pts in [[(100.240,5.433),(100.249,5.428),(100.258,5.431),(100.266,5.424)],[(100.252,5.403),(100.258,5.410),(100.268,5.407),(100.275,5.412)]]:
 add(f'<path d="{smoothgeo(pts)}" fill="none" stroke="#F2E7C9" stroke-width="2.3" stroke-linecap="round" opacity=".72"/>')
# Fine, low-contrast street fabric in the old-town district.
for lat in [5.4098,5.4115,5.4132,5.4149,5.4166,5.4183,5.4200,5.4217,5.4234,5.4251]:
    a=xy(100.326,lat); b=xy(100.344,lat)
    add(f'<path d="M {a[0]:.1f},{a[1]:.1f} L {b[0]:.1f},{b[1]:.1f}" stroke="#D8C39D" stroke-width="2.2" opacity=".56"/>')
for lon in [100.327,100.3295,100.332,100.3345,100.337,100.3395,100.342,100.344]:
    a=xy(lon,5.409); b=xy(lon,5.426)
    add(f'<path d="M {a[0]:.1f},{a[1]:.1f} L {b[0]:.1f},{b[1]:.1f}" stroke="#D8C39D" stroke-width="2.2" opacity=".56"/>')
# Coastal green fingers, parks and small islets; all kept quiet behind destination assets.
for lon,lat,rx,ry in [(100.319,5.433,.012,.003),(100.281,5.468,.008,.003),(100.334,5.421,.006,.003),(100.285,5.400,.006,.004)]:
 x,y=xy(lon,lat); add(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx*111320*coslat*scale:.1f}" ry="{ry*110540*scale:.1f}" fill="#B7D2A5" opacity=".88"/>')
# Rounded woodland crowns follow the central spine, with sparser greens in the south and west.
def tree(lon,lat,r=8):
 x,y=xy(lon,lat)
 add(f'<g transform="translate({x:.1f} {y:.1f})"><ellipse cx="0" cy="{r*.8:.1f}" rx="{r*1.25:.1f}" ry="{r*.38:.1f}" fill="#718F70" opacity=".18"/><rect x="-1.5" y="2" width="3" height="{r*.75:.1f}" rx="1.5" fill="#B48262"/><circle cx="0" cy="0" r="{r:.1f}" fill="#77A77B"/><circle cx="-{r*.55:.1f}" cy="2" r="{r*.65:.1f}" fill="#A8C89A"/><circle cx="{r*.58:.1f}" cy="2" r="{r*.56:.1f}" fill="#C5D9A6"/></g>')
for lon,lat,r in [(100.244,5.438,8),(100.252,5.450,10),(100.265,5.449,9),(100.278,5.439,9),(100.287,5.427,7),(100.268,5.422,8),(100.253,5.414,8),(100.245,5.402,7),(100.261,5.392,8),(100.280,5.389,7),(100.238,5.421,7),(100.292,5.447,6),(100.257,5.462,7),(100.226,5.414,6),(100.239,5.385,6),(100.271,5.374,6),(100.299,5.357,5),(100.313,5.335,5),(100.259,5.326,5),(100.235,5.305,5),(100.303,5.294,5)]: tree(lon,lat,r)
# Small rounded hillcaps and shaded foot slopes add depth without changing terrain claims.
for lon,lat,rx,ry in [(100.247,5.434,.010,.006),(100.267,5.431,.011,.007),(100.257,5.408,.010,.006),(100.274,5.414,.008,.006),(100.250,5.390,.008,.005),(100.289,5.365,.007,.004),(100.262,5.343,.008,.004)]:
 x,y=xy(lon,lat); sx=rx*111320*coslat*scale; sy=ry*110540*scale
 add(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{sx:.1f}" ry="{sy:.1f}" fill="#8BB58A" opacity=".35"/><ellipse cx="{x:.1f}" cy="{y+sy*.28:.1f}" rx="{sx*.8:.1f}" ry="{sy*.45:.1f}" fill="#6F9A78" opacity=".18"/>')
# Coastal vegetation ribbons and neighborhood fabric, clipped to land.
for i,(lon,lat) in enumerate([(100.319,5.433),(100.330,5.428),(100.313,5.446),(100.296,5.463),(100.290,5.477),(100.330,5.407),(100.318,5.399),(100.307,5.390)]):
 x,y=xy(lon,lat); add(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{18 if i<5 else 12}" ry="5" fill="#92BF91" opacity=".43"/>')
# Hand-drawn forest canopy texture follows the central highland belt; irregular spacing avoids a grid look.
forest_colors=['#6F9E78','#83AD7E','#A7C48C','#BCD19A']
for row,lat in enumerate([5.454,5.449,5.444,5.439,5.434,5.429,5.424,5.419,5.414,5.409,5.404,5.399,5.394,5.389,5.384]):
    for col,lon in enumerate([100.232,100.238,100.244,100.250,100.256,100.262,100.268,100.274,100.280,100.286]):
        # Mask toward the irregular ridge rather than filling the whole rectangular envelope.
        ridge_center=100.259+0.013*math.sin((lat-5.38)*48)
        if abs(lon-ridge_center) > (0.020 if 5.40 < lat < 5.45 else 0.014): continue
        if (row*7+col*11)%5 == 0: continue
        x,y=xy(lon+((row%2)*.002),lat+(((col%3)-1)*.0007));r=3.2+((row*3+col*5)%4)*.7
        color=forest_colors[(row+col*2)%len(forest_colors)]
        add(f'<g opacity=".77"><ellipse cx="{x:.1f}" cy="{y+r*.75:.1f}" rx="{r*1.3:.1f}" ry="{r*.38:.1f}" fill="#6D8D6C" opacity=".20"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{color}"/><circle cx="{x-r*.48:.1f}" cy="{y+r*.22:.1f}" r="{r*.57:.1f}" fill="#C0D69D"/></g>')
# Coastal groves, especially along the north shore and around the western bays.
for row,lat in enumerate([5.472,5.465,5.458,5.451,5.444,5.437,5.430,5.423,5.416,5.409,5.402,5.395,5.388,5.381]):
    for col,lon in enumerate([100.218,100.226,100.234,100.242,100.250,100.258,100.266,100.274,100.282,100.290,100.298,100.306,100.314]):
        if (row*5+col*3)%7 not in (0,1): continue
        if 100.24 < lon < 100.29 and 5.385 < lat < 5.455: continue
        x,y=xy(lon,lat);r=2.6+((row+col)%3)*.65
        add(f'<g opacity=".53"><circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#84B285"/><circle cx="{x-r*.38:.1f}" cy="{y+r*.2:.1f}" r="{r*.5:.1f}" fill="#BED39D"/></g>')
# District building rows are drawn below as linked blocks so the city reads as a connected fabric.
# Light neighborhood texture near Tanjung Bungah and Air Itam, tapering into the uplands.
for row in range(5):
 for col in range(10):
  lon=100.286+col*.0020+(row%2)*.0006;lat=5.448+row*.0020
  x,y=xy(lon,lat);fill=['#E8C994','#D99576','#E9D8AC','#9AB9B0'][(row+col)%4]
  add(f'<g opacity=".42"><rect x="{x-3.5:.1f}" y="{y-2.4:.1f}" width="7.0" height="4.8" rx="1.5" fill="{fill}"/><path d="M{x-3.7:.1f},{y-1.2:.1f} l3.7,-2.4 3.7,2.4" fill="#B97D64"/></g>')
# Low-density west/south ground texture: soft orchard rows and scattered homes, kept inside the island clip.
for lon,lat,rx,ry in [(100.229,5.351,.014,.007),(100.242,5.326,.012,.006),(100.272,5.315,.010,.005),(100.218,5.382,.008,.005),(100.297,5.329,.008,.004)]:
 x,y=xy(lon,lat);sx=rx*111320*coslat*scale;sy=ry*110540*scale
 add(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{sx:.1f}" ry="{sy:.1f}" fill="#D9C792" opacity=".22"/>')
 for row in range(3):
  yy=y-sy*.55+row*sy*.50
  add(f'<path d="M{x-sx*.78:.1f},{yy:.1f} q{sx*.38:.1f},{-sy*.18:.1f} {sx*.75:.1f},0 t{sx*.75:.1f},0" fill="none" stroke="#A6B77E" stroke-width="1.3" opacity=".38"/>')
for lon,lat in [(100.221,5.357),(100.245,5.336),(100.276,5.303),(100.232,5.287),(100.303,5.318),(100.216,5.395)]:
 x,y=xy(lon,lat);add(f'<g opacity=".55"><rect x="{x-2.7:.1f}" y="{y-2.4:.1f}" width="5.4" height="4.8" rx="1.4" fill="#E5C69A"/><path d="M{x-3:.1f},{y-1:.1f} l3,-2.4 3,2.4" fill="#C9866D"/></g>')
# Gentle patchwork and scattered settlement texture gives the south and west a lived-in landscape.
for row in range(4):
 for col in range(5):
  lon=100.218+col*.017+(row%2)*.006;lat=5.286+row*.020
  x,y=xy(lon,lat);rx=22+((row+col)%3)*5;ry=11+((row*2+col)%3)*3
  tint=['#D8D6A9','#E6D9B5','#C8D7A8','#E4D2A9'][(row+2*col)%4]
  add(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx}" ry="{ry}" fill="{tint}" opacity=".24"/>')
  for line in range(3):
   yy=y-ry*.5+line*ry*.48
   add(f'<path d="M{x-rx*.72:.1f},{yy:.1f} q{rx*.34:.1f},{-ry*.2:.1f} {rx*.7:.1f},0 t{rx*.7:.1f},0" fill="none" stroke="#92A878" stroke-width="1.25" opacity=".36"/>')
# Small, low-density roof clusters suggest existing southern/western town fabric without adding map stops.
for ci,(clon,clat) in enumerate([(100.228,5.348),(100.222,5.312),(100.286,5.300),(100.258,5.331)]):
 for row in range(3):
  for col in range(4):
   lon=clon+col*.0022+(row%2)*.0007;lat=clat+row*.0023
   x,y=xy(lon,lat);roof=['#D58F74','#E0B466','#81AEB0','#E7D5AE'][(row+col+ci)%4]
   add(f'<g opacity=".48"><rect x="{x-3.4:.1f}" y="{y-2.1:.1f}" width="6.8" height="4.5" rx="1.4" fill="#F2E5C7"/><path d="M{x-3.8:.1f},{y-1.1:.1f} l3.8,-2.6 3.8,2.6" fill="{roof}"/><rect x="{x-2.5:.1f}" y="{y-.3:.1f}" width="5.0" height="2.5" rx=".8" fill="#E2CDA8"/></g>')
# Small coastal pocket gardens and neighborhood trees, clustered more densely in the north.
for row in range(8):
 for col in range(12):
  lon=100.286+col*.0048+(row%2)*.0014;lat=5.414+row*.0068
  if 100.322<lon<100.346 and 5.408<lat<5.430:continue
  if (row*7+col*5)%4:continue
  x,y=xy(lon,lat);r=2.4+((row+col)%3)*.6
  add(f'<g opacity=".68"><circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#80AD7D"/><circle cx="{x-r*.42:.1f}" cy="{y+r*.18:.1f}" r="{r*.52:.1f}" fill="#C2D49A"/></g>')
# Small ornamental canopy groups in two old-town cultural quarters, without labels or stop markers.
for lon,lat,col in [(100.330,5.413,'#D77F63'),(100.332,5.414,'#E0A454'),(100.334,5.412,'#6EA6A6'),(100.337,5.416,'#D77F63'),(100.339,5.414,'#E0A454')]:
 x,y=xy(lon,lat); add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{col}" opacity=".42"/>')
# Small Chinatown lanterns and Little India flower-garland marks are neighborhood cues only.
for lon,lat in [(100.3310,5.4140),(100.3335,5.4152),(100.3350,5.4128)]:
 x,y=xy(lon,lat);add(f'<g opacity=".74"><path d="M{x:.1f},{y-5:.1f} v3" stroke="#9B634D" stroke-width=".8"/><ellipse cx="{x:.1f}" cy="{y:.1f}" rx="2.4" ry="3.1" fill="#D8785C"/><path d="M{x-2.2:.1f},{y:.1f} h4.4" stroke="#F0C376" stroke-width=".7"/></g>')
for i,(lon,lat) in enumerate([(100.3277,5.4133),(100.3292,5.4141),(100.3304,5.4127),(100.3311,5.4161)]):
 x,y=xy(lon,lat);add(f'<g opacity=".67"><circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="#D78D9A"/><circle cx="{x-2.5:.1f}" cy="{y+1:.1f}" r="1.3" fill="#E8B85D"/><circle cx="{x+2.5:.1f}" cy="{y+1:.1f}" r="1.3" fill="#78AFA9"/><circle cx="{x:.1f}" cy="{y+2.9:.1f}" r=".9" fill="#F2E5C7"/></g>')
# Composition pass: redraw one broad central upland zone over the earlier drafting marks.
# The clean underpaint removes the previous disconnected green ellipses before the final landscape.
under=[(100.220,5.461),(100.294,5.461),(100.302,5.430),(100.293,5.395),(100.282,5.369),(100.236,5.369),(100.223,5.396),(100.216,5.427)]
add(f'<path d="{smoothgeo(under,True)}" fill="#E9D5AC" opacity=".98"/>')
# A connected main ridge anchors separate, offset hill masses; the silhouettes do not form nested rings.
ridge=[(100.226,5.434),(100.232,5.449),(100.246,5.458),(100.263,5.460),(100.279,5.451),(100.289,5.436),(100.291,5.420),(100.283,5.405),(100.287,5.393),(100.275,5.379),(100.258,5.376),(100.244,5.385),(100.237,5.400),(100.226,5.412)]
north_hill=[(100.235,5.438),(100.242,5.450),(100.253,5.454),(100.264,5.450),(100.270,5.441),(100.266,5.432),(100.255,5.429),(100.246,5.434)]
central_hill=[(100.252,5.431),(100.260,5.439),(100.270,5.437),(100.279,5.428),(100.277,5.418),(100.268,5.414),(100.258,5.418),(100.251,5.424)]
south_hill=[(100.245,5.407),(100.252,5.416),(100.263,5.415),(100.271,5.407),(100.269,5.397),(100.260,5.391),(100.250,5.395)]
add(f'<path d="{smoothgeo(ridge,True)}" fill="#9EBC8C" opacity=".90"/>')
add(f'<path d="{smoothgeo(north_hill,True)}" fill="#78A27A" opacity=".78"/>')
add(f'<path d="{smoothgeo(central_hill,True)}" fill="#B8CC91" opacity=".91"/>')
add(f'<path d="{smoothgeo(south_hill,True)}" fill="#709975" opacity=".67"/>')
# Broad soft ridge highlights and one winding footpath provide depth without concentric contour rings.
for pts,sw,col,op in [([(100.238,5.446),(100.247,5.452),(100.257,5.451)],4,'#D1DDA4','.48'), ([(100.260,5.433),(100.269,5.433),(100.274,5.426)],3,'#D7DDAA','.46'), ([(100.249,5.402),(100.256,5.398)],2.5,'#E2DDB1','.48')]:
 add(f'<path d="{smoothgeo(pts)}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" opacity="{op}"/>')
add(f'<path d="{smoothgeo([(100.239,5.428),(100.247,5.423),(100.256,5.424),(100.263,5.417),(100.271,5.414)])}" fill="none" stroke="#F2E6C7" stroke-width="3.8" stroke-linecap="round" opacity=".82"/>')
# Irregular canopy clusters are placed as groups, at mixed scales, not as a repeated grid.
for lon,lat,r,col in [(100.241,5.445,10,'#6F9B76'),(100.251,5.452,13,'#7FA77A'),(100.263,5.449,9,'#668E70'),(100.276,5.440,12,'#709B76'),(100.284,5.429,8,'#87AC7A'),(100.246,5.427,12,'#6D9874'),(100.261,5.431,10,'#79A47A'),(100.273,5.421,13,'#668E70'),(100.250,5.411,9,'#7DA47A'),(100.263,5.407,12,'#6B9672'),(100.257,5.393,10,'#7DA47A'),(100.277,5.397,8,'#719975')]:
 x,y=xy(lon,lat);add(f'<g opacity=".86"><ellipse cx="{x+2:.1f}" cy="{y+5:.1f}" rx="{r*1.25:.1f}" ry="{r*.55:.1f}" fill="#577C66" opacity=".16"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}"/><circle cx="{x-r*.42:.1f}" cy="{y-r*.20:.1f}" r="{r*.62:.1f}" fill="#B7CC91"/><circle cx="{x+r*.48:.1f}" cy="{y-r*.08:.1f}" r="{r*.50:.1f}" fill="#8FB384"/></g>')
# Southern and western countryside: large quiet orchard/coastal transitions remain intentionally sparse.
for pts,color in [
 ([(100.210,5.376),(100.223,5.389),(100.238,5.383),(100.239,5.367),(100.228,5.355),(100.214,5.359)],'#C9D0A0'),
 ([(100.218,5.329),(100.232,5.341),(100.249,5.336),(100.253,5.319),(100.241,5.304),(100.222,5.308)],'#D5D0A1'),
 ([(100.250,5.294),(100.268,5.305),(100.285,5.297),(100.291,5.281),(100.276,5.269),(100.258,5.276)],'#C3CF9F'),
 ([(100.282,5.352),(100.297,5.361),(100.310,5.352),(100.306,5.337),(100.291,5.333)],'#D4D5A9')]:
 add(f'<path d="{smoothgeo(pts,True)}" fill="{color}" opacity=".44"/>')
# Focused George Town fabric. The street layout follows the district's approximate
# north-east grid and shoreline orientation; buildings are illustrative, not survey footprints.
city_layer_start=len(svg)
add('<g id="george-town-urban" clip-path="url(#islandClip)">')
# Old-town coverage is a single connected field of blocks, with small bends and varied widths.
# Keep the waterfront to the east (higher longitude) and taper blocks toward the south.
lon_edges=[100.3208,100.3241,100.3274,100.3307,100.3340,100.3373,100.3405,100.3436,100.3450]
lat_edges=[5.4005,5.4043,5.4081,5.4119,5.4157,5.4195,5.4233,5.4270,5.4290]
# Narrow curved lanes have a cream center and a fine shadow edge to separate blocks.
for j,lat in enumerate(lat_edges):
    pts=[]
    for i,lon in enumerate(lon_edges):
        pts.append((lon,lat+0.00014*math.sin(i*.72+j*.45)+0.00008*(i/len(lon_edges))))
    d=smoothgeo(pts)
    add(f'<path d="{d}" fill="none" stroke="#CDB990" stroke-width="5.4" stroke-linecap="round" opacity=".48"/>')
    add(f'<path d="{d}" fill="none" stroke="#FFF3D9" stroke-width="4.2" stroke-linecap="round" opacity=".96"/>')
for i,lon in enumerate(lon_edges):
    pts=[]
    for j,lat in enumerate(lat_edges): pts.append((lon+0.00012*math.sin(j*.68+i*.4),lat))
    d=smoothgeo(pts)
    add(f'<path d="{d}" fill="none" stroke="#CDB990" stroke-width="5.0" stroke-linecap="round" opacity=".46"/>')
    add(f'<path d="{d}" fill="none" stroke="#FFF3D9" stroke-width="3.8" stroke-linecap="round" opacity=".97"/>')
# Compact perimeter walls and dozens of roof forms give each block its own rhythm.
roof_colors=['#B86E5E','#C78064','#D3A46F','#8EA19A','#A95D51','#CC8B72','#7F9C93','#D0A05D']
wall_colors=['#E9CDA5','#DFA98A','#E8D8B4','#D9B89E','#D9C995','#E3BE9A','#C9D0AA','#E5C7B1']
for row in range(len(lat_edges)-1):
  for col in range(len(lon_edges)-1):
    x0,y0=xy(lon_edges[col]+.00012,lat_edges[row]+.00013)
    x1,y1=xy(lon_edges[col+1]-.00012,lat_edges[row+1]-.00013)
    left,right=min(x0,x1),max(x0,x1); top,bottom=min(y0,y1),max(y0,y1)
    bw,bh=right-left,bottom-top
    # Little India is a warm, bright market rhythm; Chinatown uses coral and jade roof accents.
    quarter='india' if 100.3245<=lon_edges[col]<=100.3302 and 5.4100<=lat_edges[row]<=5.4176 else ('china' if 100.3302<=lon_edges[col]<=100.3375 and 5.4110<=lat_edges[row]<=5.4198 else 'old')
    blockfill=['#E8D2AE','#E4C9A7','#EBD9B6','#E1C5A5'][(row+col)%4]
    add(f'<rect x="{left:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="3.2" fill="{blockfill}" stroke="#C9B28E" stroke-width=".9" opacity=".94"/>')
    # Small courtyard: a quiet green pocket appears in roughly one block in five.
    if (row*5+col*3)%5==1:
      gx=left+bw*(.48 if (row+col)%2 else .56); gy=top+bh*.50
      add(f'<rect x="{gx-2.5:.1f}" y="{gy-2.0:.1f}" width="5.0" height="4.0" rx="1.8" fill="#9FBE8F" opacity=".9"/>')
      add(f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="1.4" fill="#6E9976"/>')
    n=max(3,round(bw/10.5))
    unit=bw/n
    for side in range(2):
      for k in range(n):
        # Tight connected frontages face the inner lane; block corners vary to avoid a stamp-like grid.
        inset=1.0+((row+col+k+side)%3)*.22
        xx=left+k*unit+inset
        yy=top+side*(bh*.51)+1.0
        ww=unit-1.7; hh=bh*.46-2.3
        roof=roof_colors[(row*3+col+k+side*2)%len(roof_colors)]
        wall=wall_colors[(row+col*2+k+side)%len(wall_colors)]
        if quarter=='india':
          wall=['#E9B984','#E59680','#E8D06F','#A9C8B9','#E8A07D'][(row+col+k+side)%5]
          roof=['#B96A53','#D0825A','#C7A24F','#779D91'][(row+k+side)%4]
        if quarter=='china' and k%3==0:
          roof='#B85D50'; wall=['#E9D4AD','#DDBA91','#D9C8A6'][(row+side)%3]
        # Soft facade, roof cap, shaded five-foot way, two shuttered upper windows, and doorway.
        add(f'<g opacity=".98"><rect x="{xx:.1f}" y="{yy+2.0:.1f}" width="{ww:.1f}" height="{hh-1.0:.1f}" rx="1.35" fill="{wall}" stroke="#B99A78" stroke-width=".55"/>')
        if (row*2+col+k+side)%4==0:
          add(f'<path d="M{xx-0.7:.1f},{yy+2.1:.1f} q{ww*.25:.1f},-4.0 {ww*.50:.1f},-2.7 q{ww*.25:.1f},-1.3 {ww*.50+0.7:.1f},2.7 v2 h-{ww+1.4:.1f}Z" fill="{roof}"/>')
        elif (row+col+k)%5==0:
          add(f'<path d="M{xx-0.7:.1f},{yy+2.1:.1f} l{ww*.50:.1f},-3.4 l{ww*.50+0.7:.1f},3.4 v2 h-{ww+1.4:.1f}Z" fill="{roof}"/><path d="M{xx+ww*.50:.1f},{yy-1.0:.1f} v3.2" stroke="#E5C995" stroke-width=".65"/>')
        else:
          add(f'<path d="M{xx-0.7:.1f},{yy+2.1:.1f} l{ww*.50:.1f},-2.8 l{ww*.50+0.7:.1f},2.8 v2 h-{ww+1.4:.1f}Z" fill="{roof}"/>')
        wx=xx+ww*.18; wy=yy+hh*.33; win=max(1.7,ww*.18); wh=max(2.0,hh*.24)
        add(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{win:.1f}" height="{wh:.1f}" rx=".45" fill="#88AEB0" stroke="#F1DFBE" stroke-width=".5"/><path d="M{wx+win/2:.1f},{wy:.1f} v{wh:.1f} M{wx-.5:.1f},{wy+wh/2:.1f} h{win+1:.1f}" stroke="#F5E3C3" stroke-width=".42"/>')
        wx2=xx+ww*.63
        add(f'<rect x="{wx2:.1f}" y="{wy:.1f}" width="{win:.1f}" height="{wh:.1f}" rx=".45" fill="#88AEB0" stroke="#F1DFBE" stroke-width=".5"/><path d="M{wx2+win/2:.1f},{wy:.1f} v{wh:.1f}" stroke="#F5E3C3" stroke-width=".42"/>')
        # Covered five-foot walkway and a recessed shop opening.
        add(f'<path d="M{xx:.1f},{yy+hh*.76:.1f} h{ww:.1f}" stroke="#F9E8C8" stroke-width="1.5"/><rect x="{xx+ww*.42:.1f}" y="{yy+hh*.77:.1f}" width="{ww*.18:.1f}" height="{hh*.19:.1f}" rx=".5" fill="#9D7464"/>')
        # Fine roof seams and occasional awnings enliven selected storefronts.
        if (row+col+k)%3==0:
          add(f'<path d="M{xx+ww*.25:.1f},{yy+2.1:.1f} v1.7 M{xx+ww*.75:.1f},{yy+2.1:.1f} v1.7" stroke="#E7C790" stroke-width=".55"/>')
        if quarter=='india' and k%3==1:
          aw=['#D87E68','#D3AA56','#6FA8A0'][(row+col)%3]
          add(f'<path d="M{xx+ww*.12:.1f},{yy+hh*.66:.1f} h{ww*.78:.1f} l-1.0,2.0 h-{ww*.72:.1f}Z" fill="{aw}"/>')
        add('</g>')
# Parklet trees and subtle waterfront promenade accents remain secondary to the architecture.
for lon,lat,r in [(100.3230,5.4233,2.4),(100.3281,5.4212,2.0),(100.3391,5.4180,2.4),(100.3243,5.4097,2.2),(100.3368,5.4082,2.0),(100.3420,5.4130,2.1)]:
  tx,ty=xy(lon,lat)
  add(f'<g><ellipse cx="{tx:.1f}" cy="{ty+1.8:.1f}" rx="{r*1.45:.1f}" ry="{r*.5:.1f}" fill="#637F66" opacity=".2"/><circle cx="{tx:.1f}" cy="{ty:.1f}" r="{r:.1f}" fill="#729A75"/><circle cx="{tx-r*.35:.1f}" cy="{ty-r*.24:.1f}" r="{r*.58:.1f}" fill="#B6CF9C"/></g>')
# Neighborhood character is encoded in roof and shopfront details only, no added stops or pins.
# Short coral lanterns suggest Chinatown; small garland dots mark Little India's commercial frontage.
for lon,lat in [(100.3325,5.4142),(100.3343,5.4160),(100.3362,5.4127),(100.3311,5.4182)]:
  lx,ly=xy(lon,lat)
  add(f'<g opacity=".8"><path d="M{lx:.1f},{ly-2.4:.1f} v1.0" stroke="#94634E" stroke-width=".65"/><ellipse cx="{lx:.1f}" cy="{ly:.1f}" rx="1.0" ry="1.35" fill="#CF6E58"/><path d="M{lx-1:.1f},{ly:.1f} h2" stroke="#E9BF72" stroke-width=".5"/></g>')
for lon,lat in [(100.3268,5.4133),(100.3280,5.4143),(100.3292,5.4125),(100.3273,5.4161)]:
  fx,fy=xy(lon,lat)
  add(f'<g opacity=".8"><circle cx="{fx:.1f}" cy="{fy:.1f}" r="1.15" fill="#D98291"/><circle cx="{fx-1.1:.1f}" cy="{fy+1.0:.1f}" r=".65" fill="#E8B85D"/><circle cx="{fx+1.1:.1f}" cy="{fy+1.0:.1f}" r=".65" fill="#78AFA9"/></g>')
add('</g>')
city_layer_markup='\n'.join(svg[city_layer_start:])
add('</g>')  # close outer land clip group
# Attribution is in the artwork and README; page integrations must retain it.
add('</svg>')
open(OUT,'w',encoding='utf8').write('\n'.join(svg))
# Export the city fabric as its own SVG overlay for independent design review and editing.
urban_svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 1500"><defs><clipPath id="islandClip"><path d="{coast}"/></clipPath></defs>'+city_layer_markup+'</svg>'
open(os.path.join(os.path.dirname(OUT),'penang-george-town-urban.svg'),'w',encoding='utf8').write(urban_svg)
# Persist consistent image coordinates in the single canonical locations dataset.
def inside(lon,lat):
    hit=False
    pts=ring
    j=len(pts)-1
    for i in range(len(pts)):
        xi,yi=pts[i]; xj,yj=pts[j]
        if ((yi>lat)!=(yj>lat)) and lon < (xj-xi)*(lat-yi)/(yj-yi)+xi: hit=not hit
        j=i
    return hit
for locitem in loc['locations']:
 lat=locitem.get('latitude');lon=locitem.get('longitude')
 if lat is None or lon is None: locitem['map_position']=None;continue
 if locitem['id'] in {'butterworth','padang','hatyai'}:
  locitem['map_position']=None; locitem['map_visibility']='journey-only'; continue
 x,y=xy(lon,lat);locitem['map_position']={'x':round(x,2),'y':round(y,2),'projection':'equirectangular local'}
 locitem['map_visibility']='optional' if locitem.get('optional') else ('itinerary' if locitem.get('map_pin') else 'hidden')
 locitem.setdefault('display_offset_px',{'x':0,'y':0})
 locitem['landmark_asset']=f"assets/landmarks/{'heritage' if locitem['id'] in {'armenian','chulia','kimberley'} else locitem['id']}.webp"
loc['map_projection']={'name':'Local equirectangular','latitude_origin':round(lat0,7),'longitude_origin':round(lon0,7),'cos_latitude':round(coslat,8),'scale':scale,'pixel_x_origin':ox,'pixel_y_origin':oy,'source':'OSM-derived Penang main-island polygon'}
loc['map_scope']='Full Penang Island; mainland excluded from interactive itinerary pins.'
open(LOC,'w',encoding='utf8').write(json.dumps(loc,ensure_ascii=False,indent=2))
print('Wrote',OUT,'from',len(ring),'OSM coastline points; SVG bytes',os.path.getsize(OUT))
print('viewBox projection bounds',round(minx),round(maxx),round(miny),round(maxy),'scale',round(scale,4))
