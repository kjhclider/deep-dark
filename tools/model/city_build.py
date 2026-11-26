# H1 Medieval Modular City Realistic에서 고른 조각(city_pick.py의 city_pieces.json)을 떼어 작은 glb로 만든다
# blender -b --factory-startup --python city_build.py -- 원본.glb city_pieces.json 결과.glb 미리보기.png
# 조각마다 가운데 바닥이 원점, 단위는 원본 그대로(게임에서 배율을 준다). 멀리서 쓰는 가벼운 판은 이름 뒤 _lo
import bpy,bmesh,sys,json,math
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:];src,pj,out,prev=a[0],a[1],a[2],a[3]
PC=json.load(open(pj))
CAP={'house':1800,'tower':2400,'gatetower':3500,'fountain':600,'well':400,'bigtree':3000,'tree':1300}
CAPLO={'house':350}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
want={}
for n,v in PC.items():
  for o,f0 in v['parts']:want.setdefault(o,{})[f0]=n
src_obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
pieces={}
for ob in src_obs:
  if ob.name not in want:continue
  W=want[ob.name];bm=bmesh.new();bm.from_mesh(ob.data);bm.faces.ensure_lookup_table()
  seen=set();sel={}
  for f in bm.faces:
    if f.index in seen:continue
    st=[f];seen.add(f.index);comp=[]
    while st:
      g=st.pop();comp.append(g.index)
      for e in g.edges:
        for h in e.link_faces:
          if h.index not in seen:seen.add(h.index);st.append(h)
    n=W.get(f.index)
    if n:sel.setdefault(n,[]).extend(comp)
  bm.free()
  for n,fl in sel.items():
    me=ob.data.copy();o2=bpy.data.objects.new(n+'_p',me);bpy.context.scene.collection.objects.link(o2);o2.matrix_world=ob.matrix_world.copy()
    b2=bmesh.new();b2.from_mesh(me);b2.faces.ensure_lookup_table();keep=set(fl)
    bmesh.ops.delete(b2,geom=[f for f in b2.faces if f.index not in keep],context='FACES')
    b2.to_mesh(me);b2.free();pieces.setdefault(n,[]).append(o2)
for ob in src_obs:bpy.data.objects.remove(ob,do_unlink=True)
def tris(o):return sum(len(p.vertices)-2 for p in o.data.polygons)
final=[]
for n,L in pieces.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in L:o.select_set(True)
  bpy.context.view_layer.objects.active=L[0]
  if len(L)>1:bpy.ops.object.join()
  o=bpy.context.view_layer.objects.active;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
  c=PC[n]['c'];o.data.transform(__import__('mathutils').Matrix.Translation((-c[0],-c[1],-max(c[2],0))));o.name=n
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.002);bm.to_mesh(o.data);bm.free()
  kind=''.join(ch for ch in n if not ch.isdigit())
  t0=tris(o);cap=CAP.get(kind,2000)
  lo=None
  if kind in CAPLO:
    lo=o.copy();lo.data=o.data.copy();lo.name=n+'_lo';bpy.context.scene.collection.objects.link(lo)
    # 가벼운 판: 집은 골조(lambert9, 면 대부분)를 빼고 회벽과 지붕만
    bm=bmesh.new();bm.from_mesh(lo.data);mi=[i for i,s in enumerate(lo.data.materials) if s and s.name.startswith('lambert9')]
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index in mi],context='FACES');bm.to_mesh(lo.data);bm.free()
    m=lo.modifiers.new('d','DECIMATE');m.ratio=min(1,CAPLO[kind]/max(1,tris(lo)));m.use_collapse_triangulate=True
    bpy.context.view_layer.objects.active=lo;bpy.ops.object.modifier_apply(modifier='d')
  if t0>cap:
    m=o.modifiers.new('d','DECIMATE');m.ratio=cap/t0;m.use_collapse_triangulate=True
    bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier='d')
  print('piece',n,t0,'->',tris(o),('lo %d'%tris(lo)) if lo else '',flush=True)
  final.append(o)
  if lo:final.append(lo)
# 재질: 노멀, 거칠기 텍스처를 떼고 기본색만, 1k(작은 것 512)로 줄인다. 빠진 텍스처(지붕 흰색)는 지붕 재질 텍스처로
used=set()
for o in final:
  for s in o.material_slots:
    if s.material:used.add(s.material)
imgs={}
for m in used:
  nt=m.node_tree;bsdf=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if not bsdf:continue
  for inp in ('Normal','Roughness','Metallic','Transmission Weight','Specular IOR Level'):
    if inp in bsdf.inputs:
      for l in list(bsdf.inputs[inp].links):nt.links.remove(l)
  bsdf.inputs['Metallic'].default_value=0.0;bsdf.inputs['Roughness'].default_value=0.9
  for n in list(nt.nodes):
    if n.type=='TEX_IMAGE' and not n.outputs['Color'].links and not n.outputs['Alpha'].links:nt.nodes.remove(n)
  bc=bsdf.inputs['Base Color'].links
  if bc and bc[0].from_node.type=='TEX_IMAGE':
    im=bc[0].from_node.image
    if im is None or im.size[0]==0 or (im.pixels and len(im.pixels)==0):
      print('missing image in',m.name)
    imgs.setdefault(im.name if im else None,(im,[]))[1].append(m.name)
for k,(im,ms) in imgs.items():
  if im is None:continue
  try:
    w,h=im.size
  except Exception:continue
  if w==0:print('empty image',k,ms);continue
  alpha=any(n.outputs['Alpha'].links for mm in ms for n in bpy.data.materials[mm].node_tree.nodes if n.type=='TEX_IMAGE' and n.image==im)
  t=512
  if w>t:im.scale(t,int(h*t/w))
  if not alpha:im.file_format='JPEG'
  print('img',k,w,'->',im.size[0],'alpha' if alpha else 'jpeg',ms)
# 내보내기
bpy.ops.object.select_all(action='DESELECT')
for o in final:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=out,use_selection=True,export_format='GLB',export_image_format='AUTO',export_jpeg_quality=82,export_apply=True,export_yup=True,export_normals=True,export_texcoords=True,export_materials='EXPORT')
# 미리보기: 조각을 줄지어 놓고 비스듬히
sc=bpy.context.scene;x=0
for o in final:
  if o.name.endswith('_lo'):continue
  o.location=(x,0,0);x+=o.dimensions.x+6
  lo=bpy.data.objects.get(o.name+'_lo')
  if lo:lo.location=(o.location.x,-30,0)
sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='TEXTURE'
sc.render.resolution_x=2400;sc.render.resolution_y=900
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam
cam.data.type='ORTHO';cam.data.ortho_scale=x*1.02;cam.data.clip_end=5000
d=Vector((0.35,-1,0.6)).normalized();cam.location=Vector((x/2,-15,10))+d*800;cam.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler()
sc.render.filepath=prev;bpy.ops.render.render(write_still=True)
