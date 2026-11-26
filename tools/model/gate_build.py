# 왕궁 정문 모델 만들기 (2026-11-26, gate 세션)
# blender -b --factory-startup --python gate_build.py -- medieval_fortress_kit.glb castle_style_door.glb gate.glb preview.png
# - medieval_fortress_kit(Aya Rady, CC BY)의 조각 "2"(아치 문루)를 가운데, 조각 "3"(원뿔 지붕 반원탑)을 양옆에 둔다
# - castle_style_door(Visthetique, CC BY)의 문짝 두 짝(Frame.001, Frame.002)을 문루 아치에 맞춰 넣는다(틀은 뺀다. 유리 자리는 검은 쇠)
# - 게임 좌표 그대로 만든다: 원점은 성문 가운데 땅, 바깥(성 밖)이 glTF +Z(Blender -Y), 단위 m
# - 텍스처는 1k JPEG, 금속/거칠기 맵은 빼고 값으로 둔다
import bpy,sys,math
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
a=sys.argv[sys.argv.index('--')+1:];KIT,DOOR,OUT,PRE=a[0],a[1],a[2],a[3] if len(a)>3 else None
GATE_W=13.0     # 문루 너비(지금 코드 성문의 아치 덩어리 너비와 같게)
TOWER_H=24.0    # 양옆 탑 높이(성벽 탑 21보다 조금 높게)
TEX=1024

bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
def imp(p):
  before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=p);bpy.context.view_layer.update();return [o for o in bpy.data.objects if o not in before]
def vbb(objs):
  ps=[o.matrix_world@v.co for o in objs for v in o.data.vertices];return Vector([min(p[i] for p in ps) for i in range(3)]),Vector([max(p[i] for p in ps) for i in range(3)])
def bake(o):
  # 월드 변환을 메시 점에 넣고 부모를 끊는다
  o.data=o.data.copy();o.data.transform(o.matrix_world.copy());o.parent=None;o.matrix_world=Matrix.Identity(4)

kit=imp(KIT)
keep={}
for o in kit:
  if o.type=='MESH':
    k=o.name.split('_')[0]
    if k in ('2','3'):keep[k]=o
house,tower=keep['2'],keep['3']
for o in (house,tower):bake(o)
for o in kit:
  if o not in (house,tower):bpy.data.objects.remove(o,do_unlink=True)
bpy.context.view_layer.update()
def norm(o,s):
  lo,hi=vbb([o]);c=(lo+hi)/2
  o.data.transform(Matrix.Translation((-c.x,-c.y,-lo.z)));o.data.transform(Matrix.Scale(s,4))
lo,hi=vbb([house]);sh=GATE_W/(hi.x-lo.x);norm(house,sh)
lo,hi=vbb([tower]);st=TOWER_H/(hi.z-lo.z);norm(tower,st)
bpy.context.view_layer.update()
hl,hh=vbb([house]);tl,th=vbb([tower])
print('HOUSE',[round(v,2) for v in hl],[round(v,2) for v in hh],'scale',round(sh,3))
print('TOWER',[round(v,2) for v in tl],[round(v,2) for v in th],'scale',round(st,3))

# 아치 크기: gate_look.py의 앞면 그림(조각 2, 투명 픽셀)으로 잰 원본 값. 폭 3.0m, 꼭대기 3.46m(원본 단위)
AW=3.0*sh;AH=3.46*sh
print('ARCH W',round(AW,2),'H',round(AH,2))

# 탑: 문루 양옆, 둥근 면이 바깥(-Y)
tw=th.x-tl.x
for sx in (-1,1):
  t=tower if sx<0 else tower.copy()
  if sx>0:sc.collection.objects.link(t)
  t.location=(sx*(GATE_W/2+tw/2-0.4),(hh.y+hl.y)/2+0.3,0);t.name='tower'+('L' if sx<0 else 'R')
house.name='house'

# 문짝
dr=imp(DOOR)
leaves=[o for o in dr if o.type=='MESH' and o.name.startswith(('Frame.001','Frame.002'))]
for o in leaves:bake(o)
for o in dr:
  if o not in leaves:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.object.select_all(action='DESELECT')
for o in leaves:o.select_set(True)
bpy.context.view_layer.objects.active=leaves[0];bpy.ops.object.join();door=bpy.context.active_object;door.name='door'
dl,dh=vbb([door])
# 아치 폭에 맞추고 높이는 아치 꼭대기까지(옆과 위로 조금 더 넓혀 통로 벽 속에 묻는다)
# 통로(아치)가 뚫려 있어, 문짝을 아치보다 넓고 높게 키워 앞면 안쪽에 두면 남는 곳은 통로 벽과 천장 속에 묻힌다
sxd=(AW+1.2)/(dh.x-dl.x);szd=(AH+1.4)/(dh.z-dl.z)
door.data.transform(Matrix.Translation((-(dl.x+dh.x)/2,-(dl.y+dh.y)/2,-dl.z)))
door.data.transform(Matrix.Diagonal((sxd,3.0,szd,1)))
door.location=(0,hl.y+1.2,0)   # 앞면에서 1.2m 안쪽
print('DOOR scale',round(sxd,2),round(szd,2),'y',door.location.y)
# 유리 칸은 문짝 나무로 채운다(성문에 유리는 맞지 않는다). 나무 텍스처를 앞에서 비추듯 UV를 x, z로 다시 준다
wood=[m for m in door.data.materials if m and 'Glass' not in m.name][0]
gi=[i for i,m in enumerate(door.data.materials) if m and 'Glass' in m.name]
uvl=door.data.uv_layers.active
for p in door.data.polygons:
  if p.material_index in gi:
    for li in p.loop_indices:
      co=door.data.vertices[door.data.loops[li].vertex_index].co;uvl.data[li].uv=(co.x/AW*0.6+0.5,co.z/AH*0.6)
for i in gi:door.data.materials[i]=wood

# 재질: 금속/거칠기 맵을 빼고 값으로, 텍스처는 1k
for m in bpy.data.materials:
  if not m.use_nodes:continue
  nt=m.node_tree;b=nt.nodes.get('Principled BSDF')
  if not b:continue
  for inp in ('Metallic','Roughness'):
    for l in list(b.inputs[inp].links):nt.links.remove(l)
  g=False
  b.inputs['Metallic'].default_value=0.8 if g else 0.0
  b.inputs['Roughness'].default_value=0.5 if g else 0.9
used=set()
for o in sc.objects:
  if o.type!='MESH':continue
  for m in o.data.materials:
    if m and m.use_nodes:
      for n in m.node_tree.nodes:
        if n.type=='TEX_IMAGE' and n.image and any(o2.links for o2 in n.outputs):used.add(n.image)
for im in used:
  w,h=im.size
  if max(w,h)>TEX:k=TEX/max(w,h);im.scale(max(1,int(w*k)),max(1,int(h*k)))
print('IMAGES',[(i.name,tuple(i.size)) for i in used])
print('FACES',sum(len(o.data.polygons) for o in sc.objects if o.type=='MESH'))

bpy.ops.object.select_all(action='DESELECT')
for o in sc.objects:
  if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT,use_selection=True,export_format='GLB',export_image_format='JPEG',export_jpeg_quality=82,export_apply=True,export_yup=True,export_materials='EXPORT')
print('WROTE',OUT)

if PRE:
  sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='TEXTURE'
  sc.render.resolution_x=1024;sc.render.resolution_y=640
  cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam
  c=Vector((0,0,11));d=Vector((0.35,1,-0.2)).normalized();cam.location=c-d*60;cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
  sc.render.filepath=PRE;bpy.ops.render.render(write_still=True)
