# glb의 메시 조각마다 이름, 부모, 세계 상자, 재질, 면 수를 찍는다: blender -b --factory-startup --python glb_list.py -- 파일.glb
import bpy,sys
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=sys.argv[sys.argv.index('--')+1])
for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  ws=[o.matrix_world@Vector(c) for c in o.bound_box];mn=[min(w[i] for w in ws) for i in range(3)];mx=[max(w[i] for w in ws) for i in range(3)]
  print('OB',o.name,o.parent.name if o.parent else '-',' '.join(f'{a:.2f}..{b:.2f}' for a,b in zip(mn,mx)),[m.name for m in o.data.materials],sum(len(q.vertices)-2 for q in o.data.polygons))
