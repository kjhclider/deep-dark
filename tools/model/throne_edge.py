# 언덕 경계 변(구멍) 세기 (throne 세션)
import bpy,sys,bmesh
a=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=a[0]);bpy.context.view_layer.update()
for o in bpy.data.objects:
  if o.type!='MESH' or o.name not in a[1].split(','):continue
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=float(a[2]))
  b=sum(1 for e in bm.edges if len(e.link_faces)==1);nm=sum(1 for e in bm.edges if len(e.link_faces)>2)
  print('EDGE',o.name,len(bm.faces),'boundary',b,'nonmanifold',nm)
