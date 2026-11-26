# 왕궁 성벽, 탑 모델 만들기 (modular_medieval_wall_set, Andrei.D, CC BY 4.0)
# blender -b src.blend --python wall_prep.py -- out.glb preview_dir [wall_tris corner_tris tex]
#  src.blend: 원본 glb를 Blender로 읽어 저장한 것(wall_look.py가 만든다)
#  cw_wall : wall_large(길이 9.8, 두께 4.6, 높이 12.4). 가운데가 원점, 바닥 z=0, 흉벽(바깥)이 +Y(three.js -Z)
#  cw_tower: wall_90_exterior(바깥 모서리) 넷을 돌려 붙인 네모 탑. 아래에 같은 조각의 밑동(0~CUT)을 하나 더 쌓아 높인다
import bpy,bmesh,sys,os,math,mathutils
a=sys.argv[sys.argv.index('--')+1:];OUT=a[0];PV=a[1]
WT=int(a[2]) if len(a)>2 else 2400;CT=int(a[3]) if len(a)>3 else 1500;TEX=int(a[4]) if len(a)>4 else 1024
CUT=7.05   # 탑 밑동 높이(원본 단위 m). 위 조각 통로 10.75 + 7.05 = 17.8, 게임에서 1.18배 = 21
def grab(key,hide=False):
  o=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(key) and (('hide' in o.name)==hide)][0]
  me=o.data.copy();me.transform(o.matrix_world);n=bpy.data.objects.new(key+'_w',me);return n
def decimate(o,target):
  bpy.context.scene.collection.objects.link(o)
  tri=sum(len(p.vertices)-2 for p in o.data.polygons)
  m=o.modifiers.new('d','DECIMATE');m.decimate_type='COLLAPSE';m.ratio=min(1,target/tri);m.use_collapse_triangulate=True
  bpy.context.view_layer.objects.active=o;dg=bpy.context.evaluated_depsgraph_get()
  me=bpy.data.meshes.new_from_object(o.evaluated_get(dg));o.modifiers.clear();o.data=me
  bpy.context.scene.collection.objects.unlink(o)
  print('decimate',o.name,tri,'->',sum(len(p.vertices)-2 for p in me.polygons))
def bbox(me):
  vs=[v.co for v in me.vertices];return mathutils.Vector([min(v[i] for v in vs) for i in range(3)]),mathutils.Vector([max(v[i] for v in vs) for i in range(3)])
def slim_mat(mat):
  # 기본색, 노멀맵만 남기고(1k로 줄여) 나머지(AO, 거칠기 텍스처)는 뺀다
  nt=mat.node_tree;bsdf=[n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'][0]
  base=bsdf.inputs['Base Color'].links[0].from_node if bsdf.inputs['Base Color'].links else None
  nrm=bsdf.inputs['Normal'].links[0].from_node if bsdf.inputs['Normal'].links else None
  ntex=nrm.inputs['Color'].links[0].from_node if nrm and nrm.inputs['Color'].links else None
  for n in list(nt.nodes):
    if n not in (bsdf,base,nrm,ntex) and n.type!='OUTPUT_MATERIAL':nt.nodes.remove(n)
  bsdf.inputs['Metallic'].default_value=0;bsdf.inputs['Roughness'].default_value=0.92
  for t in (base,ntex):
    if t and t.image and t.image.size[0]>TEX:
      im=t.image.copy();im.scale(TEX,TEX);im.name=mat.name+('_c' if t is base else '_n');im.pack();t.image=im
  return mat
src_wall=grab('wall_large001');src_corner=grab('wall_90_exterior001')
# 성벽: 흉벽이 -Y에 있다 -> 180도 돌려 +Y로, 가운데 원점, 바닥 0
me=src_wall.data;mn,mx=bbox(me);c=(mn+mx)/2
hw=grab('wall_large001',True).data;hn,hx=bbox(hw);print('wall core length',hx.x-hn.x,'bbox',mx.x-mn.x,'core center',(hn.x+hx.x)/2-c.x)
me.transform(mathutils.Matrix.Rotation(math.pi,4,'Z')@mathutils.Matrix.Translation((-c.x,-c.y,-mn.z)))
decimate(src_wall,WT)
# 탑 모서리: 흉벽이 -X, -Y 쪽. 바닥을 정사각(평균 폭)으로 맞추고 열린 끝(+X,+Y)을 원점에
me=src_corner.data;mn,mx=bbox(me);s=((mx.x-mn.x)+(mx.y-mn.y))/2
# 열린 끝은 겉 돌이 튀어나와 bbox가 실제 이음 면보다 길다: 속(hide) 조각의 끝을 이음 면으로 본다
hm=grab('wall_90_exterior001',True).data;hn,hx=bbox(hm);print('corner end gap',mx.x-hx.x,mx.y-hx.y)
TF=mathutils.Matrix.Diagonal((s/(mx.x-mn.x),s/(mx.y-mn.y),1,1))@mathutils.Matrix.Translation((-mx.x,-mx.y,-mn.z))
me.transform(TF);hm.transform(TF);hn,hx=bbox(hm);me.transform(mathutils.Matrix.Translation((-hx.x,-hx.y,0)));s=s-min(hx.x,hx.y)*-1
print('corner shift',hx.x,hx.y)
print('corner square',s)
decimate(src_corner,CT)
# 밑동: 모서리 조각의 0~CUT 부분
low=src_corner.data.copy();bm=bmesh.new();bm.from_mesh(low)
r=bmesh.ops.bisect_plane(bm,geom=bm.verts[:]+bm.edges[:]+bm.faces[:],plane_co=(0,0,CUT),plane_no=(0,0,1),clear_outer=True)
bm.to_mesh(low);bm.free()
bm=bmesh.new()
for k in range(4):
  R=mathutils.Matrix.Rotation(k*math.pi/2,4,'Z')
  for mesh,dz in ((low,0),(src_corner.data,CUT)):
    t=mesh.copy();t.transform(R@mathutils.Matrix.Translation((0,0,dz)));bm.from_mesh(t);bpy.data.meshes.remove(t)
bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.002)
tme=bpy.data.meshes.new('cw_tower');bm.to_mesh(tme);bm.free()
tme.materials.append(src_corner.data.materials[0])
print('tower tris',sum(len(p.vertices)-2 for p in tme.polygons),'half',s,'top walkway',CUT+10.75)
# 내보낼 장면
scn=bpy.data.scenes.new('out');bpy.context.window.scene=scn
ow=bpy.data.objects.new('cw_wall',src_wall.data);ot=bpy.data.objects.new('cw_tower',tme)
ot.location.x=20
for o in (ow,ot):scn.collection.objects.link(o)
for m in {ow.data.materials[0],tme.materials[0]}:slim_mat(m)
for o in (ow,ot):
  for p in o.data.polygons:p.use_smooth=True
bpy.ops.object.select_all(action='DESELECT')
for o in (ow,ot):o.select_set(True)
# 미리보기
scn.render.engine='BLENDER_WORKBENCH';scn.display.shading.color_type='TEXTURE';scn.display.shading.light='STUDIO'
scn.render.resolution_x=800;scn.render.resolution_y=500
cam=bpy.data.cameras.new('c');co=bpy.data.objects.new('c',cam);scn.collection.objects.link(co);scn.camera=co
for k,(loc,tgt) in enumerate([((-14,-26,16),(6,0,7)),((26,30,14),(6,0,7)),((10,-8,40),(10,0,8))]):
  co.location=loc;co.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler()
  scn.render.filepath=os.path.join(PV,f'prep_{k}.png');bpy.ops.render.render(write_still=True)
ot.location.x=0
# 다른 조각은 지우고 내보낸다(선택만 내보내기가 다른 장면 것까지 넣었다)
for o in list(bpy.data.objects):
  if o not in (ow,ot):bpy.data.objects.remove(o)
for sc0 in list(bpy.data.scenes):
  if sc0!=scn:bpy.data.scenes.remove(sc0)
bpy.ops.export_scene.gltf(filepath=OUT,use_selection=False,use_active_scene=True,export_format='GLB',export_image_format='JPEG',export_jpeg_quality=82,export_apply=False,export_materials='EXPORT',export_tangents=False,export_texcoords=True,export_normals=True,export_yup=True)
print('saved',OUT,os.path.getsize(OUT))
