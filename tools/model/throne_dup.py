# 언덕 겹친 면 세기 (throne 세션)
import bpy,sys
from mathutils.kdtree import KDTree
a=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=a[0]);bpy.context.view_layer.update()
O={o.name:o for o in bpy.data.objects if o.type=='MESH'}
A,B=O['Material2.073'],O['Material2.074']
ca=[A.matrix_world@p.center for p in A.data.polygons];kd=KDTree(len(ca))
for i,c in enumerate(ca):kd.insert(c,i)
kd.balance()
for tol in (0.5,2,5,20):
  print('TOL',tol,sum(1 for p in B.data.polygons if kd.find(B.matrix_world@p.center)[2]<tol),'of',len(B.data.polygons))
# 같은 물체 안 겹침
for o in (A,B):
  c=[o.matrix_world@p.center for p in o.data.polygons];k=KDTree(len(c))
  for i,x in enumerate(c):k.insert(x,i)
  k.balance();d=sum(1 for i,x in enumerate(c) if any(j!=i and dd<0.5 for (_,j,dd) in k.find_n(x,2)))
  print('SELF',o.name,d)
