# B Medieval Pentagon Castle(Sereib, CC BY)을 가볍게: 재질 갈래(돌, 나무 등 9가지)마다 한 덩어리, 텍스처 한 장, 면 줄이기
# blender -b --factory-startup --python pcastle_build.py -- medieval_pentagon_castle.glb pcastle.glb 몸통면수 미리보기.png [몸통복셀 0.22] [흉벽면수 22000]
import bpy,bmesh,sys,re,math
from mathutils import Vector,Matrix
a=sys.argv[sys.argv.index('--')+1:];src,out,TARGET,prev=a[0],a[1],int(a[2]),a[3]
VOX=float(a[4]) if len(a)>4 else 0.22;TILE=2.5;BUD=TARGET
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=src)
obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
fam={}
for o in obs:
  m=o.data.materials[0];k=re.sub(r'_\d+$','',m.name);fam.setdefault(k,[]).append(o)
def tris(o):return sum(len(p.vertices)-2 for p in o.data.polygons)
tot=sum(tris(o) for o in obs);res=[]
# 바닥 가운데를 원점으로
mn=Vector((1e9,)*3);mx=-mn
for o in obs:
  for c in o.bound_box:w=o.matrix_world@Vector(c);mn=Vector(map(min,mn,w));mx=Vector(map(max,mx,w))
ctr=Vector(((mn.x+mx.x)/2,(mn.y+mx.y)/2,mn.z));print('bbox',mn,mx)
# 흉벽 톱니(성벽, 탑 꼭대기 띠): 1m 칸마다 가장 높은 곳에서 TOPH m 안의 면은 따로 촘촘한 복셀(TOPVOX)로 만든다(멀리서 보는 몸통은 VOX)
TOPH=2.0;TOPVOX=0.06;TOPB=int(a[5]) if len(a)>5 else 22000;CELL=1.0
gmax={}
for o in obs:
  mw=o.matrix_world
  for v in o.data.vertices:
    w=mw@v.co-ctr;key=(int(w.x//CELL),int(w.y//CELL))
    if w.z>gmax.get(key,-1e9):gmax[key]=w.z
def istop(c):
  k=(int(c.x//CELL),int(c.y//CELL));g=max(gmax.get((k[0]+dx,k[1]+dy),-1e9) for dx in(-1,0,1) for dy in(-1,0,1))
  return g>6 and c.z>g-TOPH
def proc(o,vox,budget):
  if tris(o)==0:return
  m=o.modifiers.new('s','SOLIDIFY');m.thickness=0.25 if vox>0.1 else 0.12;m.offset=0;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier='s')   # 얇은 판(탑 벽면)도 복셀에 남게
  m=o.modifiers.new('v','REMESH');m.mode='VOXEL';m.voxel_size=vox;m.use_smooth_shade=False;bpy.ops.object.modifier_apply(modifier='v')
  t1=tris(o);m=o.modifiers.new('c','DECIMATE');m.ratio=min(1,budget/max(1,t1));m.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier='c')
tot_top=0;split={}
for k,L in fam.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in L:o.select_set(True)
  bpy.context.view_layer.objects.active=L[0];bpy.ops.object.join();o=bpy.context.view_layer.objects.active
  bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.data.transform(Matrix.Translation(-ctr))
  mat=o.data.materials[0];mat.name=k
  for i in range(len(o.data.materials)):o.data.materials[i]=mat
  while len(o.data.materials)>1:o.data.materials.pop(index=len(o.data.materials)-1)
  for p in o.data.polygons:p.material_index=0
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.003);bm.to_mesh(o.data);bm.free()
  t0=tris(o);top=None
  if t0>8000:
    top=o.copy();top.data=o.data.copy();bpy.context.scene.collection.objects.link(top)
    for ob,keep in ((o,False),(top,True)):
      bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if istop(f.calc_center_median())!=keep],context='FACES');bm.to_mesh(ob.data);bm.free()
    tot_top+=tris(top)
  split[k]=(o,top,t0)
for k,(o,top,t0) in split.items():
  if t0>8000:
    # 돌 하나하나가 모델링된 벽: 복셀로 껍데기를 다시 만든 뒤 줄이고, 면 방향으로 반복 UV(TILE m마다 텍스처 한 장)
    tt=tris(top);proc(o,VOX,BUD*t0/tot);proc(top,TOPVOX,TOPB*tt/max(1,tot_top))
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);top.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.join()
    bm=bmesh.new();bm.from_mesh(o.data);uv=bm.loops.layers.uv.verify()
    for f in bm.faces:
      n=f.normal;ax=max(range(3),key=lambda i:abs(n[i]))
      for l in f.loops:
        c=l.vert.co;u,v=((c.y,c.z),(c.x,c.z),(c.x,c.y))[ax];l[uv].uv=(u/TILE,v/TILE)
    bm.to_mesh(o.data);bm.free()
  o.name='pc_'+k;res.append(o);print('fam',k,t0,'->',tris(o),flush=True)
print('total',tot,'->',sum(tris(o) for o in res))
for o in res:
  nt=o.data.materials[0].node_tree;bsdf=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
  bsdf.inputs['Roughness'].default_value=0.9
  for n in list(nt.nodes):
    if n.type=='TEX_IMAGE' and not n.outputs['Color'].links:nt.nodes.remove(n)
bpy.ops.object.select_all(action='DESELECT')
for o in res:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=out,use_selection=True,export_format='GLB',export_yup=True,export_materials='EXPORT',export_normals=False)   # 법선 없이: 게임(GLTFLoader)이 평면 음영으로 그려 점을 나눠 쓰니 용량이 준다
sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='TEXTURE'
sc.render.resolution_x=1200;sc.render.resolution_y=900
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam
cam.data.type='ORTHO';cam.data.ortho_scale=80;cam.data.clip_end=5000
d=Vector((0.5,-1,0.6)).normalized();cam.location=Vector((0,0,10))+d*500;cam.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler()
sc.render.filepath=prev;bpy.ops.render.render(write_still=True)
# 가까이: 정문 쪽 성벽과 탑 꼭대기
cam.data.ortho_scale=26;d=Vector((0.3,-1,0.45)).normalized();cam.location=Vector((6,-24,16))+d*500;cam.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler()
sc.render.filepath=prev.replace('.png','_near.png');bpy.ops.render.render(write_still=True)
