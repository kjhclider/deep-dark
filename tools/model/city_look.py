# H1 Medieval Modular City Realistic: 조각(건물)을 위치로 묶어 목록과 위에서 본 그림용 JSON을 만든다
# blender -b --factory-startup --python city_look.py -- 원본.glb 결과.json
import bpy,bmesh,sys,json,time
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:];src,out=a[0],a[1]
t0=time.time()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
print('import',time.time()-t0,flush=True)
parts=[]
for ob in list(bpy.context.scene.objects):
  if ob.type!='MESH':continue
  me=ob.data;mw=ob.matrix_world
  bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table()
  seen=set()
  for f in bm.faces:
    if f.index in seen:continue
    st=[f];seen.add(f.index);comp=[]
    while st:
      g=st.pop();comp.append(g)
      for e in g.edges:
        for h in e.link_faces:
          if h.index not in seen:seen.add(h.index);st.append(h)
    vs={v for g in comp for v in g.verts}
    ps=[mw@v.co for v in vs]
    mn=[min(p[i] for p in ps) for i in range(3)];mx=[max(p[i] for p in ps) for i in range(3)]
    mat=me.materials[comp[0].material_index].name if me.materials else ''
    parts.append({'o':ob.name,'mat':mat,'n':len(comp),'mn':mn,'mx':mx,'f0':comp[0].index})
  bm.free()
print('parts',len(parts),time.time()-t0,flush=True)
json.dump(parts,open(out,'w'))
