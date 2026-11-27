# 망자의 요새 조각 모델(fort.glb)을 만든다 (fortress 세션, 2026-11-26)
# blender -b --factory-startup --python fort_build.py -- assets폴더 out.glb 미리보기폴더
# 원본(읽기만): low_poly_dark_castle.glb(C), gothic_building_for_aria_pack_1.0.glb, villains_lair.glb
# 조각마다 바닥 가운데가 원점, 앞(성문 쪽)이 게임 +Z(Blender -Y). 미터 단위. 이름은 아래 PIECES 표
import bpy,bmesh,sys,os,math,mathutils
a=sys.argv[sys.argv.index('--')+1:];SRC,OUT,PV=a[0],a[1],a[2];os.makedirs(PV,exist_ok=True)
TEX=1024
bpy.ops.wm.read_factory_settings(use_empty=True)
def tris(me):return sum(len(p.vertices)-2 for p in me.polygons)
def imp(fn):
  before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=os.path.join(SRC,fn))
  return [o for o in bpy.data.objects if o not in before]
def chain(o):
  s=[];p=o
  while p:s.append(p.name);p=p.parent
  return s
def join(objs,name):
  # 세계 좌표로 굳혀 하나의 메시로 (재질 유지)
  bm=bmesh.new();mats=[];me=bpy.data.meshes.new(name)
  for o in objs:
    t=o.data.copy();t.transform(o.matrix_world)
    idx={}
    for i,m in enumerate(t.materials):
      if m not in mats:mats.append(m)
      idx[i]=mats.index(m)
    for p in t.polygons:p.material_index=idx.get(p.material_index,0)
    bm.from_mesh(t);bpy.data.meshes.remove(t)
  bm.to_mesh(me);bm.free()
  for m in mats:me.materials.append(m)
  return me
def bbox(me):
  vs=[v.co for v in me.vertices];return mathutils.Vector([min(v[i] for v in vs) for i in range(3)]),mathutils.Vector([max(v[i] for v in vs) for i in range(3)])
def ground(me,scale=1.0):
  # 크기를 맞추고 바닥 가운데를 원점으로. 원래 가운데(미터)를 돌려준다
  me.transform(mathutils.Matrix.Scale(scale,4));mn,mx=bbox(me);c=(mn+mx)/2
  me.transform(mathutils.Matrix.Translation((-c.x,-c.y,-mn.z)));return (c.x,c.y,mn.z),mx-mn
def decimate(me,target,merge=0.0):
  o=bpy.data.objects.new('tmp',me);bpy.context.scene.collection.objects.link(o)
  if merge>0:
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=merge);bm.to_mesh(me);bm.free()
  t=tris(me)
  bpy.context.view_layer.objects.active=o;o.select_set(True)
  for k in range(3):
    t=tris(me)
    if t<=target*1.1:break
    d=o.modifiers.new('d','DECIMATE');d.ratio=target/t;d.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier='d')
  if tris(me)>target*1.3:
    # 모으기로 더 안 줄면(붙지 않은 조각이 많을 때) 평면 녹이기
    d=o.modifiers.new('p','DECIMATE');d.decimate_type='DISSOLVE';d.angle_limit=math.radians(8);bpy.ops.object.modifier_apply(modifier='p')
    d=o.modifiers.new('t','TRIANGULATE');bpy.ops.object.modifier_apply(modifier='t')
  me.validate();bpy.data.objects.remove(o);return me
def drop_small(me,thr):
  # 붙지 않은 작은 조각(대각선 thr m 미만: 장식 못, 작은 첨두)을 지운다. 첨탑처럼 조각이 많으면 모으기로는 안 준다
  bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();seen=set();kill=[]
  for v in bm.verts:
    if v.index in seen:continue
    comp=[];st=[v];seen.add(v.index)
    while st:
      x=st.pop();comp.append(x)
      for e in x.link_edges:
        y=e.other_vert(x)
        if y.index not in seen:seen.add(y.index);st.append(y)
    co=[q.co for q in comp];d=(mathutils.Vector([max(c[i] for c in co) for i in range(3)])-mathutils.Vector([min(c[i] for c in co) for i in range(3)])).length
    if d<thr:kill+=comp
  n0=len(bm.verts);bmesh.ops.delete(bm,geom=kill,context='VERTS');bm.to_mesh(me);bm.free();return n0-len(me.vertices)
def merge_slots(me):
  # 같은 재질이 두 칸이면 하나로(내보낼 때 그리기 묶음이 하나 준다)
  uniq=[];mp={}
  for i,m in enumerate(me.materials):
    if m not in uniq:uniq.append(m)
    mp[i]=uniq.index(m)
  for p in me.polygons:p.material_index=mp.get(p.material_index,0)
  me.materials.clear()
  for m in uniq:me.materials.append(m)
def strip_uv(me,keep=1):
  while len(me.uv_layers)>keep:me.uv_layers.remove(me.uv_layers[-1])
FLAT=None
def voxel_lo(me,target):
  # 지도용: 복셀로 다시 떠서(겉모양만) 면을 줄이고 단색 검은 돌. 붙지 않은 조각이 많아도 깨끗하다
  global FLAT
  if FLAT is None:
    FLAT=bpy.data.materials.new('gb_flat');FLAT.use_nodes=True;b=[n for n in FLAT.node_tree.nodes if n.type=='BSDF_PRINCIPLED'][0]
    b.inputs['Base Color'].default_value=(0.032,0.030,0.036,1);b.inputs['Roughness'].default_value=0.95
  mn,mx=bbox(me);w=min(mx.x-mn.x,mx.y-mn.y)
  o=bpy.data.objects.new('vx',me);bpy.context.scene.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True)
  r=o.modifiers.new('r','REMESH');r.mode='VOXEL';r.voxel_size=max(0.12,w/28);bpy.ops.object.modifier_apply(modifier='r')
  bpy.data.objects.remove(o);decimate(me,target);me.materials.clear();me.materials.append(FLAT);strip_uv(me,0)
  for p in me.polygons:p.material_index=0
  return me
OUTS=[]
def keep(me,name,info=''):
  o=bpy.data.objects.new(name,me);OUTS.append(o);mn,mx=bbox(me)
  print('PIECE',name,'tris',tris(me),'size',[round(mx[i]-mn[i],2) for i in range(3)],info)
  return o
# ---------- C: Low Poly Dark Castle ----------
dc=imp('low_poly_dark_castle.glb')
M={}
for m in bpy.data.materials:M[m.name]=m
def setcol(name,rgb,emit=None,rough=0.95):
  m=M.get(name)
  if not m:return
  b=[n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'][0]
  b.inputs['Base Color'].default_value=(*rgb,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=0
  if emit:b.inputs['Emission Color'].default_value=(*emit,1);b.inputs['Emission Strength'].default_value=1.0
# 모두 검게: 갈색 벽돌은 검보라 돌로, 회색 지붕과 가시는 쇳빛으로, 붉은 창은 빛나게
setcol('Set_4_-_Material.003',(0.030,0.027,0.034))
setcol('Set_4_-_Material.004',(0.012,0.011,0.013))
setcol('Set_4_-_Material',(0.040,0.004,0.008))
setcol('Set_4_-_Material.002',(0.10,0.10,0.11),rough=0.6)
setcol('Set_4_-_Material.001',(0.5,0.02,0.02),emit=(0.9,0.05,0.04))
for nm in ['Set_4_-_Material.003','Set_4_-_Material.004','Set_4_-_Material','Set_4_-_Material.002','Set_4_-_Material.001']:
  if nm in M:M[nm].name='dc_'+{'Set_4_-_Material.003':'stone','Set_4_-_Material.004':'black','Set_4_-_Material':'blood','Set_4_-_Material.002':'iron','Set_4_-_Material.001':'glow'}[nm]
def dcgrp(top):return [o for o in dc if o.type=='MESH' and top in chain(o)[1:2]]
LAY={}
for top,name in [('Castle','dc_keep'),('Gate','dc_gate'),('Tower','dc_tower')]:
  me=join(dcgrp(top),name);c,s=ground(me);LAY[name]=c;keep(me,name,'orig center %s'%[round(x,2) for x in c])
  strip_uv(me,0)
  if name=='dc_keep':lme=me.copy();decimate(lme,3000);keep(lme,'dc_keep_lo')
  if name=='dc_tower':lme=me.copy();decimate(lme,500);keep(lme,'dc_tower_lo')
for top in ['Tower.001','Tower.002','Tower.003','Wall.002','Wall.003','Wall.004','Wall.005','Wall.006']:
  me=join(dcgrp(top),'t');c,s=ground(me);print('LAYOUT',top,'center',[round(x,2) for x in c],'size',[round(x,2) for x in s]);bpy.data.meshes.remove(me)
# 성벽: 낮은 벽돌 성벽(높이 4) 아래에 흉벽 없는 몸통을 한 번 더 쌓아 높이 7.2로. 길이 방향 X
src=join(dcgrp('Wall.002'),'w');ground(src);mn,mx=bbox(src)
low=src.copy();bm=bmesh.new();bm.from_mesh(low)
bmesh.ops.bisect_plane(bm,geom=bm.verts[:]+bm.edges[:]+bm.faces[:],plane_co=(0,0,3.2),plane_no=(0,0,1),clear_outer=True);bm.to_mesh(low);bm.free()
bm=bmesh.new()
for mesh,dz in ((low,0),(src,3.2)):
  t=mesh.copy();t.transform(mathutils.Matrix.Translation((0,0,dz)));bm.from_mesh(t);bpy.data.meshes.remove(t)
bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.002)
wme=bpy.data.meshes.new('dc_wall');bm.to_mesh(wme);bm.free()
for m in src.materials:wme.materials.append(m)
ground(wme);wme.validate();strip_uv(wme,0);decimate(wme,2400);keep(wme,'dc_wall','tall wall (two courses)')
lme=wme.copy();voxel_lo(lme,300);keep(lme,'dc_wall_lo')   # 벽돌이 따로 떨어진 조각이라 모으기로 안 준다
# 통로 높이 재기: 성벽 가운데(두께 가운데 띠)에서 가장 높은 점이 흉벽 사이 바닥이다
zs=sorted(round(v.co.z,2) for v in wme.vertices if abs(v.co.y)<0.25 and abs(v.co.x)<6)
print('WALK mid-band top z',zs[-5:] if zs else None)
from collections import Counter
print('WALL z hist',sorted(Counter(round(v.co.z,1) for v in wme.vertices).items())[-14:])
print('WALL y range at top',sorted(set(round(v.co.y,2) for v in wme.vertices if v.co.z>6.5))[:12])
# ---------- Gothic Building For Aria Pack ----------
gb=[o for o in imp('gothic_building_for_aria_pack_1.0.glb') if o.type=='MESH']
def bbw(o):
  v=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box];return min(p.x for p in v),max(p.x for p in v)
# gb_great(153m 큰 첨탑)는 작은 조각이 많아 줄이면 찢겨 뺐다. 큰 첨탑은 gb_spire를 키워 쓴다
GB={'gb_chapel':(1490,2510,2500,450),'gb_hall':(3370,4630,2500,450),'gb_tier':(5280,6720,3000,550),'gb_tower':(7280,8720,3500,650),
    'gb_spire':(9410,10590,2500,500),'gb_butt':(13300,16120,2500,500),'gb_ruin':(19300,22120,3000,600),'gb_arch':(22300,29700,5000,1000)}
stone=None;glass=None
for m in bpy.data.materials:
  if m.name=='Dark':stone=m
  if m.name=='Glass':glass=m
# 돌: 기본색, 노멀 1k. 더 검게(기본색 곱하기), 유리창은 망자의 녹색 불빛
b=[n for n in stone.node_tree.nodes if n.type=='BSDF_PRINCIPLED'][0];nt=stone.node_tree
base=b.inputs['Base Color'].links[0].from_node;nrm=b.inputs['Normal'].links[0].from_node if b.inputs['Normal'].links else None
ntex=nrm.inputs['Color'].links[0].from_node if nrm else None
for n in list(nt.nodes):
  if n not in (b,base,nrm,ntex) and n.type!='OUTPUT_MATERIAL':nt.nodes.remove(n)
b.inputs['Metallic'].default_value=0;b.inputs['Roughness'].default_value=0.9
for t,suf in ((base,'_c'),(ntex,'_n')):
  if t and t.image and t.image.size[0]>TEX:im=t.image.copy();im.scale(TEX,TEX);im.name='gb'+suf;im.pack();t.image=im
stone.name='gb_stone'
for n in list(glass.node_tree.nodes):
  if n.type=='BSDF_PRINCIPLED':gb_b=n
glass.blend_method='OPAQUE' if hasattr(glass,'blend_method') else None
gb_b.inputs['Base Color'].default_value=(0.02,0.05,0.02,1);gb_b.inputs['Alpha'].default_value=1.0
gb_b.inputs['Emission Color'].default_value=(0.20,0.85,0.30,1);gb_b.inputs['Emission Strength'].default_value=1.0
try:gb_b.inputs['Transmission Weight'].default_value=0
except Exception:pass
glass.name='gb_glow'
for name,(x0,x1,hi,lo) in GB.items():
  objs=[o for o in gb if x0<=bbw(o)[0] and bbw(o)[1]<=x1]
  me=join(objs,name)
  for i,m in enumerate(me.materials):
    if m and m.name=='Light':me.materials[i]=stone
  merge_slots(me);c,s=ground(me,0.01)
  t0=tris(me);H=max(s);k1=drop_small(me,H*0.006);lme=me.copy();decimate(me,hi,0.002);keep(me,name,'from %d, small verts cut %d'%(t0,k1))
  strip_uv(me,1);voxel_lo(lme,lo);keep(lme,name+'_lo')
# ---------- A: Villain's Lair (뱀 굴: 뚜껑 열린 굴에서 기어 나오는 검은 뱀) ----------
vl=imp('villains_lair.glb')
objs=[o for o in vl if o.type=='MESH' and any(n in ('SnakeLow_58','Cube.106_5') for n in chain(o))]
print('serpent parts',[o.name for o in objs])
me=join(objs,'vl_serpent')
for m in me.materials:
  bb=[n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED']
  if not bb:continue
  bb=bb[0]
  for nn in ('Base Color','Normal'):
    if bb.inputs[nn].links:
      t=bb.inputs[nn].links[0].from_node
      if t.type=='NORMAL_MAP' and t.inputs['Color'].links:t=t.inputs['Color'].links[0].from_node
      if getattr(t,'image',None) and t.image.size[0]>512:im=t.image.copy();im.scale(512,512);im.pack();t.image=im
c,s=ground(me);strip_uv(me,1);decimate(me,3000,0.0005);keep(me,'vl_serpent','size native %s'%[round(x,1) for x in s])
# ---------- 미리보기와 내보내기 ----------
scn=bpy.data.scenes.new('out');bpy.context.window.scene=scn
x=0
for o in OUTS:
  scn.collection.objects.link(o);mn,mx=bbox(o.data);o.location.x=x-mn.x;x+=mx.x-mn.x+4
scn.render.engine='BLENDER_WORKBENCH';scn.display.shading.color_type='TEXTURE';scn.display.shading.light='STUDIO'
scn.render.resolution_x=1800;scn.render.resolution_y=600
cam=bpy.data.cameras.new('c');cam.type='ORTHO';cam.ortho_scale=x*1.02;co=bpy.data.objects.new('c',cam);scn.collection.objects.link(co);scn.camera=co
co.location=(x/2,-x,x*0.25);co.rotation_euler=(mathutils.Vector((x/2,0,x*0.12))-co.location).to_track_quat('-Z','Y').to_euler();cam.clip_end=x*5
scn.render.filepath=os.path.join(PV,'fort_all.png');bpy.ops.render.render(write_still=True)
for o in OUTS:o.location.x=0
for o in list(bpy.data.objects):
  if o not in OUTS:bpy.data.objects.remove(o)
for s0 in list(bpy.data.scenes):
  if s0!=scn:bpy.data.scenes.remove(s0)
for o in OUTS:
  # 각진 모서리(40도)만 갈라 점을 함께 쓴다(면마다 갈라 내보내면 파일이 세 배)
  o.data.validate();o.data.set_sharp_from_angle(angle=math.radians(40))
bpy.ops.export_scene.gltf(filepath=OUT,use_selection=False,use_active_scene=True,export_format='GLB',export_image_format='JPEG',export_jpeg_quality=82,export_apply=False,export_materials='EXPORT',export_tangents=False,export_texcoords=True,export_normals=True,export_yup=True)
print('saved',OUT,os.path.getsize(OUT))
