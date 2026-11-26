# H2 Modular Medieval Building(rakshaan, CC BY)에서 조립된 2층 석조 회관 하나를 떼어 낸다(낱개 부품, 바닥판 제외)
# 지붕 기와가 한쪽 비탈에만 있어 용마루 기준으로 대칭해 채운다. 가운데 바닥 원점, 용마루가 X축(박공이 ±X)
# blender -b --factory-startup --python hall_build.py -- modular_medieval_building.glb hall.glb 목표면수 미리보기.png
import bpy,bmesh,sys,math
from mathutils import Vector,Matrix
a=sys.argv[sys.argv.index('--')+1:];src,out,TARGET,prev=a[0],a[1],int(a[2]),a[3]
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=src)
keep=[]
for o in list(bpy.context.scene.objects):
  if o.type!='MESH':continue
  ws=[o.matrix_world@Vector(c) for c in o.bound_box];mny=min(w.y for w in ws)
  pn=o.parent.name if o.parent else o.name
  if mny>=14.2 and not pn.startswith(('Floor_Tile','Plane')):keep.append(o)
for o in list(bpy.context.scene.objects):
  if o.type=='MESH' and o not in keep:bpy.data.objects.remove(o,do_unlink=True)
# 지붕 대칭
roof=[o for o in keep if o.parent and o.parent.name.startswith('Roof_Tile')][0]
r2=roof.copy();r2.data=roof.data.copy();bpy.context.scene.collection.objects.link(r2);keep.append(r2)
bpy.ops.object.select_all(action='DESELECT')
for o in keep:o.select_set(True)
bpy.context.view_layer.objects.active=keep[0]
# 부모를 풀고 세계 변환을 굳힌다
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM');bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
mn=Vector((1e9,)*3);mx=-mn
for o in keep:
  if o is r2:continue
  for v in o.data.vertices:mn=Vector(map(min,mn,v.co));mx=Vector(map(max,mx,v.co))
cy=(mn.y+mx.y)/2
r2.data.transform(Matrix.Translation((0,cy,0))@Matrix.Scale(-1,4,(0,1,0))@Matrix.Translation((0,-cy,0)));r2.data.flip_normals()
bpy.ops.object.join();o=bpy.context.view_layer.objects.active;o.name='hall'
o.data.transform(Matrix.Translation((-(mn.x+mx.x)/2,-cy,-max(mn.z,-0.05))))
bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.001);bm.to_mesh(o.data);bm.free()
t0=sum(len(p.vertices)-2 for p in o.data.polygons)
if t0>TARGET:
  m=o.modifiers.new('c','DECIMATE');m.ratio=TARGET/t0;m.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier='c')
print('hall',t0,'->',sum(len(p.vertices)-2 for p in o.data.polygons),'size',mx-mn,'mats',[m.name for m in o.data.materials])
for m in o.data.materials:
  nt=m.node_tree;bsdf=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if not bsdf:continue
  for inp in ('Normal','Roughness','Metallic'):
    for l in list(bsdf.inputs[inp].links):nt.links.remove(l)
  bsdf.inputs['Roughness'].default_value=0.9;bsdf.inputs['Metallic'].default_value=0
  for n in list(nt.nodes):
    if n.type=='TEX_IMAGE' and not n.outputs['Color'].links and not n.outputs['Alpha'].links:nt.nodes.remove(n)
bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
bpy.ops.export_scene.gltf(filepath=out,use_selection=True,export_format='GLB',export_yup=True,export_materials='EXPORT')
sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='TEXTURE'
sc.render.resolution_x=1400;sc.render.resolution_y=700
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=20;cam.data.clip_end=5000
o2=o.copy();sc.collection.objects.link(o2);o.location.x=-9;o2.location.x=9;o2.rotation_euler.z=math.pi
d=Vector((0.6,-1,0.5)).normalized();cam.location=Vector((0,0,5))+d*200;cam.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler()
sc.render.filepath=prev;bpy.ops.render.render(write_still=True)
