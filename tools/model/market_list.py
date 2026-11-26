"""시장 팩의 조각 목록(이름, 크기, 면 수, 재질, 위치)을 찍는다.
사용: blender -b --factory-startup --python market_list.py -- medieval_market_asset_pack.glb"""
import bpy, sys
from mathutils import Vector
argv = sys.argv[sys.argv.index('--') + 1:]
bpy.ops.import_scene.gltf(filepath=argv[0])
for o in sorted(bpy.context.scene.objects, key=lambda o: o.name):
    if o.type != 'MESH': continue
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    mn = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
    mx = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    sz = mx - mn; c = (mn + mx) / 2
    mats = ','.join(m.name for m in o.data.materials if m)
    print('OBJ|%s|par=%s|size=%.2f,%.2f,%.2f|ctr=%.1f,%.1f,%.1f|f=%d|%s' % (o.name, o.parent.name if o.parent else '', sz.x, sz.y, sz.z, c.x, c.y, c.z, len(o.data.polygons), mats))
for im in bpy.data.images:
    print('IMG|%s|%dx%d' % (im.name, im.size[0], im.size[1]))
