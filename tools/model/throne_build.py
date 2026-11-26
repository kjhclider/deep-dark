# 망자의 왕좌 탑 모델 만들기 (2026-11-26, throne 세션)
# blender -b --factory-startup --python throne_build.py -- the_high_black_tower.glb throne.glb [preview.png]
# - The High Black Tower(LaetitiaIrata, CC BY)의 탑, 검은 언덕, 바닥판, 용암 웅덩이를 네 덩어리(tower, hill, plate, lava)로 나눠 내보낸다
# - 게임 좌표: 원점은 탑 한가운데 바닥판 높이, 언덕 계단 아래 끝이 +Z(glTF) 쪽, 단위는 원본 x SCALE
# - 선(면 0개) 메시, 바닥판 아래 치마는 버린다. 언덕(4.5만 면)은 줄인다. 탑의 앞, 뒤 겹친 면은 그대로 둔다(원본이 한쪽 면만 그린다)
import bpy,sys,math
from mathutils import Vector,Matrix
a=sys.argv[sys.argv.index('--')+1:];SRC,OUT=a[0],a[1];PRE=a[2] if len(a)>2 else None
SCALE=0.02      # 원본 단위(인치로 보임) → 게임 단위. 탑 꼭대기 약 88
HILL_RATIO=0.2  # 언덕 면 남기는 비율
TEX=1024
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC);bpy.context.view_layer.update()
sc=bpy.context.scene
def bake(o):
  o.data=o.data.copy();o.data.transform(o.matrix_world.copy());o.parent=None;o.matrix_world=Matrix.Identity(4)
ms=[o for o in sc.objects if o.type=='MESH']
for o in ms:
  if len(o.data.polygons)==0 or o.name in('Material2.085','Material2.086'):bpy.data.objects.remove(o,do_unlink=True)
ms=[o for o in sc.objects if o.type=='MESH']
for o in ms:bake(o)
for o in list(sc.objects):
  if o.type!='MESH':bpy.data.objects.remove(o,do_unlink=True)
bpy.context.view_layer.update()
def mat(o):return o.data.materials[0].name if o.data.materials and o.data.materials[0] else ''
groups={'tower':[],'hill':[],'plate':[],'lava':[]}
for o in sc.objects:
  m=mat(o)
  if m=='material_5' and max((o.matrix_world@v.co).z for v in o.data.vertices)<0:groups['lava'].append(o)
  elif o.name=='Material2.084':groups['plate'].append(o)
  elif m=='material_2':groups['hill'].append(o)
  else:groups['tower'].append(o)
# 탑 축과 계단 아래 끝
tw=groups['tower'];ps=[v.co for o in tw if o.name=='Material2.001' for v in o.data.vertices]
cx=sum(p.x for p in ps)/len(ps);cy=sum(p.y for p in ps)/len(ps)
st=[o for o in tw if o.name=='Material2'][0];low=sorted(st.data.vertices,key=lambda v:-((v.co.x-cx)**2+(v.co.y-cy)**2))[:20]
fx=sum(v.co.x for v in low)/len(low);fy=sum(v.co.y for v in low)/len(low);fz=sum(v.co.z for v in low)/len(low)
pl=groups['plate'][0];gz=sorted(v.co.z for v in pl.data.vertices)[len(pl.data.vertices)//2]
print('AXIS',round(cx),round(cy),'FOOT',round(fx),round(fy),round(fz),'GROUND',round(gz))
# 계단 방향을 Blender -Y(= glTF +Z)로 돌린다
ang=math.atan2(fy-cy,fx-cx);rot=-math.pi/2-ang
M=Matrix.Scale(SCALE,4)@Matrix.Rotation(rot,4,'Z')@Matrix.Translation((-cx,-cy,-gz))
out={}
for k,L in groups.items():
  if not L:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in L:o.select_set(True)
  bpy.context.view_layer.objects.active=L[0];bpy.ops.object.join();o=bpy.context.active_object;o.name=k;o.data.name=k
  o.data.transform(M);out[k]=o
# 언덕 면 줄이기
h=out['hill'];f0=len(h.data.polygons)
# 줄이기 전에 같은 자리 점을 합친다: glTF는 텍스처 이음매마다 점이 갈라져 있어, 그대로 줄이면 갈라진 곳이 벌어져 바위 가시에 체크무늬 구멍이 난다
import bmesh
bm=bmesh.new();bm.from_mesh(h.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.01);bm.to_mesh(h.data);bm.free()
md=h.modifiers.new('dec','DECIMATE');md.ratio=HILL_RATIO;md.use_collapse_triangulate=True
bpy.context.view_layer.objects.active=h;bpy.ops.object.modifier_apply(modifier='dec')
print('HILL',f0,'->',len(h.data.polygons))
# 언덕 UV: 원본은 위에서 내려 찍은 평면 투영이라 가파른 바위 면에서 텍스처가 세로로 늘어난다.
# 면마다 가장 큰 법선 축으로 찍는 박스 투영으로 바꾼다(바위 텍스처가 고른 무늬라 이음매가 거의 안 보인다). 반복 간격은 원본과 같게
UV_REP=10.6     # 게임 단위 몇마다 한 번 되풀이(원본: 약 530 원본 단위)
uvl=h.data.uv_layers.active.data
for p in h.data.polygons:
  n=p.normal;ax=max(range(3),key=lambda i:abs(n[i]))
  for li in p.loop_indices:
    co=h.data.vertices[h.data.loops[li].vertex_index].co
    uvl[li].uv=((co.x,co.y) if ax==2 else (co.y,co.z) if ax==0 else (co.x,co.z))
    uvl[li].uv=(uvl[li].uv[0]/UV_REP,uvl[li].uv[1]/UV_REP)
# 계단 끝 위치(게임 좌표)
fp=M@Vector((fx,fy,fz));print('FOOT_GAME',round(fp.x,2),round(-fp.y,2),round(fp.z,2),'(x, glTF z, y)')
for k,o in out.items():
  ps=[v.co for v in o.data.vertices];lo=[min(p[i] for p in ps) for i in range(3)];hi=[max(p[i] for p in ps) for i in range(3)]
  print('PART',k,len(o.data.polygons),[round(x,1) for x in lo],[round(x,1) for x in hi])
# 언덕, 바닥판은 SketchUp 원본이라 면 방향이 섞여 있다(바깥 63%). 양면으로 그린다(탑은 앞, 뒤 면이 따로 있어 그대로)
for m in bpy.data.materials:
  if m.name=='material_2':m.use_backface_culling=False
# 원본 텍스처가 매우 어둡다(평균 36/255). 게임 조명에서 새까맣게 보여 밝힌다(탑은 검은 탑답게 조금 덜)
import numpy as np
LIFT={'material_2':2.3,'material_6':2.0,'material_6_0':2.0}
done=set()
for m in bpy.data.materials:
  if m.name not in LIFT or not m.use_nodes:continue
  if m.name=='material_2':
    b=m.node_tree.nodes.get('Principled BSDF')
    for n in m.node_tree.nodes:
      if n.type=='MIX':
        for i in n.inputs:
          if i.name=='B' and i.type=='RGBA':i.default_value=(1,1,1,1)
  for n in m.node_tree.nodes:
    if n.type=='TEX_IMAGE' and n.image and n.image.name not in done:
      im=n.image;px=np.array(im.pixels[:]).reshape(-1,4);px[:,:3]=np.clip(px[:,:3]*LIFT[m.name],0,1);im.pixels[:]=px.ravel();im.update();done.add(im.name)
      print('LIFT',m.name,im.name,round(float(px[:,:3].mean())*255))
# 텍스처 1k
for im in bpy.data.images:
  w,hh=im.size
  if max(w,hh)>TEX:k=TEX/max(w,hh);im.scale(max(1,int(w*k)),max(1,int(hh*k)))
print('FACES',sum(len(o.data.polygons) for o in out.values()))
bpy.ops.object.select_all(action='DESELECT')
for o in out.values():o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT,use_selection=True,export_format='GLB',export_image_format='JPEG',export_jpeg_quality=82,export_apply=True,export_yup=True,export_materials='EXPORT')
print('WROTE',OUT)
if PRE:
  sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='TEXTURE'
  sc.render.resolution_x=1000;sc.render.resolution_y=700
  cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.clip_end=2000
  c=Vector((0,0,35));d=Vector((0,1,-0.25)).normalized();cam.location=c-d*190;cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
  sc.render.filepath=PRE;bpy.ops.render.render(write_still=True)
