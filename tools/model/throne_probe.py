# 겹친 면(앞, 뒤) 살피기 (throne 세션)
import bpy,sys
from mathutils import Vector
from mathutils.kdtree import KDTree
a=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=a[0]);bpy.context.view_layer.update()
O={o.name:o for o in bpy.data.objects if o.type=='MESH'}
AX=Vector((2650,2450,0))
def info(n):
  o=O[n];M=o.matrix_world;N=M.to_3x3()
  out=0;tot=0
  for p in o.data.polygons:
    c=M@p.center;nn=(N@p.normal).normalized();h=Vector((c.x-AX.x,c.y-AX.y,0))
    if h.length>1:tot+=1;out+=(1 if nn.dot(h.normalized())>0 else 0)
  return out,tot
for n in ['Material2.001','Material3.001','Material2.004','Material3.004','Material2.073','Material2.074','Material2','Material2.084','Material2.085','Material2.086']:
  print('OUT',n,info(n))
# 073와 074 면 중심이 겹치나
def cents(n):
  o=O[n];M=o.matrix_world;return [M@p.center for p in o.data.polygons]
for A,B in [('Material2.073','Material2.074'),('Material2.001','Material3.001')]:
  ca=cents(A);kd=KDTree(len(ca))
  for i,c in enumerate(ca):kd.insert(c,i)
  kd.balance();cb=cents(B);d=sorted(kd.find(c)[2] for c in cb)
  print('NEAR',A,B,'median',round(d[len(d)//2],2),'p90',round(d[int(len(d)*.9)],2))
m=bpy.data.materials['material_2']
for l in m.node_tree.links:print('LINK',l.from_node.type,l.from_socket.name,'->',l.to_node.type,l.to_socket.name)
for nn in m.node_tree.nodes:
  if nn.type=='BSDF_PRINCIPLED':print('BASE',list(nn.inputs['Base Color'].default_value))
