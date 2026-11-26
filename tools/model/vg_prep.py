"""큰 AI 모델을 합치고, 면 수를 줄이고, 정면(-Y)으로 돌려 glb로 저장한 뒤 높이별 단면을 찍는다.
사용: blender -b --python vg_prep.py -- in.glb out.glb grid.png [목표 면 수]"""
import bpy, sys, math, mathutils
from mathutils import Matrix, Vector
argv = sys.argv[sys.argv.index('--') + 1:]
IN, OUT, GRID = argv[:3]
TARGET = int(argv[3]) if len(argv) > 3 else 60000
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=IN)
ms = [o for o in bpy.context.scene.objects if o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in ms: o.select_set(True)
bpy.context.view_layer.objects.active = ms[0]; bpy.ops.object.join(); ob = bpy.context.view_layer.objects.active
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM'); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in list(bpy.context.scene.objects):
    if o.type == 'EMPTY': bpy.data.objects.remove(o, do_unlink=True)
# 겹친 점 합치기(조각 경계), 면 줄이기
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.remove_doubles(threshold=0.0002); bpy.ops.object.mode_set(mode='OBJECT')
n0 = len(ob.data.polygons)
dm = ob.modifiers.new('dec', 'DECIMATE'); dm.ratio = min(1.0, TARGET / max(1, n0)); dm.use_collapse_triangulate = True
bpy.ops.object.modifier_apply(modifier='dec')
print('faces', n0, '->', len(ob.data.polygons))
me = ob.data; me.transform(Matrix.Rotation(math.radians(-90), 4, 'Z'))
zs = [v.co.z for v in me.vertices]; z0 = min(zs); H = max(zs) - z0
print('H', round(H, 4), 'z0', round(z0, 4))
for z10 in range(0, 101, 4):
    z = z0 + H * z10 / 100
    sl = [v.co for v in me.vertices if abs(v.co.z - z) < H * 0.01]
    if sl: print('h%3d%%  x %.3f..%.3f  y %.3f..%.3f' % (z10, min(p.x for p in sl), max(p.x for p in sl), min(p.y for p in sl), max(p.y for p in sl)))
for h in (0.03, 0.08, 0.15, 0.22, 0.30, 0.38):
    for side, sg in (('L', 1), ('R', -1)):
        pts = [v.co for v in me.vertices if abs((v.co.z - z0) / H - h) < 0.006 and v.co.x * sg > 0.01 and abs(v.co.x) < 0.16 and -0.12 < v.co.y < 0.1]
        if pts: print('leg h %.2f %s c %.3f  y %.3f' % (h, side, (min(p.x for p in pts) + max(p.x for p in pts)) / 2, (min(p.y for p in pts) + max(p.y for p in pts)) / 2))
bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_image_format='JPEG', export_jpeg_quality=90)
scene = bpy.context.scene
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); scene.collection.objects.link(cam); scene.camera = cam
cam.data.type = 'ORTHO'; cam.data.ortho_scale = H * 1.1
scene.render.engine = 'BLENDER_WORKBENCH'; scene.display.shading.color_type = 'TEXTURE'; scene.render.resolution_x = 800; scene.render.resolution_y = 800
zc = z0 + H / 2
for i in range(11):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -1, z0 + H * i / 10)); c = bpy.context.object; c.scale = (2, 0.001, H * 0.002)
for i in range(-6, 7):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(i * 0.05, -1, zc)); c = bpy.context.object; c.scale = (0.0015, 0.001, 2)
for tag, loc, rot in (('front', (0, -10, zc), (90, 0, 0)), ('side', (10, 0, zc), (90, 0, 90))):
    cam.location = loc; cam.rotation_euler = tuple(math.radians(a) for a in rot)
    scene.render.filepath = GRID.replace('.png', '_%s.png' % tag); bpy.ops.render.render(write_still=True)
print('done')
