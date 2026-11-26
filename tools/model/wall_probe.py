import bpy,mathutils
for key in ['wall_large001','wall_90_exterior001','wall_small001']:
  o=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(key) and 'hide' not in o.name][0]
  vs=[o.matrix_world@v.co for v in o.data.vertices]
  mn=mathutils.Vector([min(v[i] for v in vs) for i in range(3)]);mx=mathutils.Vector([max(v[i] for v in vs) for i in range(3)])
  H=mx.z-mn.z
  top=[v for v in vs if v.z>mn.z+H*0.93]
  print(key,'min',tuple(round(x,2) for x in mn),'max',tuple(round(x,2) for x in mx))
  # 크레넬 위치(맨 위 7%)
  print(' crenel x range',round(min(v.x for v in top),2),round(max(v.x for v in top),2),'y range',round(min(v.y for v in top),2),round(max(v.y for v in top),2))
  # 높이별 히스토그램: 위를 향한 면(바닥, 통로)의 높이
  import collections
  hs=collections.Counter()
  for p in o.data.polygons:
    n=(o.matrix_world.to_3x3()@p.normal).normalized()
    if n.z>0.9:hs[round((o.matrix_world@p.center).z-mn.z,1)]+=p.area*o.matrix_world.to_scale()[0]**2
  print(' up faces by height',sorted(hs.items(),key=lambda x:-x[1])[:8])
