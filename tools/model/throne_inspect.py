# 망자의 왕좌 탑 원본 살피기 (throne 세션)
import bpy,sys
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=a[0]);bpy.context.view_layer.update()
tot=0
for o in bpy.data.objects:
  if o.type=='MESH':
    ps=[o.matrix_world@v.co for v in o.data.vertices]
    lo=[min(p[i] for p in ps) for i in range(3)];hi=[max(p[i] for p in ps) for i in range(3)]
    tot+=len(o.data.polygons)
    print('MESH',o.name,len(o.data.polygons),[round(x,2) for x in lo],[round(x,2) for x in hi],[m.name if m else None for m in o.data.materials])
  else:print('OBJ',o.type,o.name)
print('TOTAL',tot)
for im in bpy.data.images:print('IMG',im.name,tuple(im.size))
for m in bpy.data.materials:
  if m.use_nodes:
    b=m.node_tree.nodes.get('Principled BSDF')
    print('MAT',m.name,[(n.type,n.image.name if getattr(n,'image',None) else '',[l.to_socket.name for o2 in n.outputs for l in o2.links]) for n in m.node_tree.nodes if n.type=='TEX_IMAGE'], b and [round(x,2) for x in b.inputs['Emission Color'].default_value], b and b.inputs['Emission Strength'].default_value)
