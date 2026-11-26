# 성벽 세트를 읽어 조각마다 크기를 적고 미리보기 그림을 만든다
# blender -b --factory-startup --python wall_look.py -- in.glb outdir
import bpy,sys,os,mathutils,math
a=sys.argv[sys.argv.index('--')+1:];src,out=a[0],a[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out,'src.blend'))
for o in bpy.data.objects:
  if o.type!='MESH':continue
  bb=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
  mn=[min(v[i] for v in bb) for i in range(3)];mx=[max(v[i] for v in bb) for i in range(3)]
  print('OBJ',o.name,'tris',sum(len(p.vertices)-2 for p in o.data.polygons),'size',[round(mx[i]-mn[i],2) for i in range(3)],'min',[round(x,2) for x in mn],'mats',[m.name for m in o.data.materials])
for im in bpy.data.images:print('IMG',im.name,im.size[:])
