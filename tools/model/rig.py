"""Achilles(OBJ, A자 자세)를 게임의 knight 뼈대(mixamorig, T자 자세)에 입혀 glb로 내보낸다.
사용: blender -b --factory-startup --python rig.py -- knight.glb mesh.obj texture.png out.glb preview.png [팔각도] [키]"""
import bpy, sys, math, mathutils
from mathutils import Vector, Matrix
argv = sys.argv[sys.argv.index('--') + 1:]
KNIGHT, OBJ, TEX, OUT, PREV = argv[:5]
ARM_DEG = float(argv[5]) if len(argv) > 5 else None
TOP = float(argv[6]) if len(argv) > 6 else 103.0   # 말총 빼고 투구 꼭대기 높이(OBJ 단위)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=KNIGHT)
kobjs = list(bpy.context.scene.objects)
arm = next(o for o in kobjs if o.type == 'ARMATURE')
kmeshes = [o for o in kobjs if o.type == 'MESH' and o.name != 'Icosphere']
bpy.ops.wm.obj_import(filepath=OBJ)
ach = next(o for o in bpy.context.scene.objects if o not in kobjs and o.type == 'MESH')
ach.name = 'Hoplite'

def bw(name):
    b = arm.data.bones[name]; return arm.matrix_world @ b.head_local

# 1) 크기와 위치: 투구 꼭대기를 knight 머리 꼭대기에, 발을 바닥에
k_top = bw('mixamorig:HeadTop_End').z
s = k_top / TOP
ach.scale = (s, s, s); bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT'); ach.select_set(True); bpy.context.view_layer.objects.active = ach
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
me = ach.data
zs = [v.co.z for v in me.vertices]; ys = [v.co.y for v in me.vertices]
dz = -min(zs)
hips = bw('mixamorig:Hips')
# 앞뒤: 엉덩이 높이 근처 단면의 가운데를 knight 엉덩이에
sl = [v.co for v in me.vertices if abs(v.co.z + dz - hips.z) < 0.08]
cy = (min(p.y for p in sl) + max(p.y for p in sl)) / 2
for v in me.vertices: v.co.z += dz; v.co.y += hips.y - cy
print('scale', round(s, 5), 'shift y', round(hips.y - cy, 3))

# 2) 팔 각도: 손끝(가장 바깥 점)과 어깨 높이로 잰다
la = bw('mixamorig:LeftArm')
tipL = max(me.vertices, key=lambda v: v.co.x).co.copy()
ang = math.degrees(math.atan2(la.z - tipL.z, tipL.x - la.x)) if ARM_DEG is None else ARM_DEG
print('arm down deg', round(ang, 1), 'tip', [round(c, 3) for c in tipL], 'shoulder', [round(c, 3) for c in la])

# 3) knight 뼈대를 같은 A자로 굽힌다 (어깨 뼈를 앞뒤 축(Y)으로 돌림)
bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
for side, sgn in (('Left', 1), ('Right', -1)):
    pb = arm.pose.bones['mixamorig:%sArm' % side]
    head = pb.head.copy()   # 뼈대 공간
    R = Matrix.Translation(head) @ Matrix.Rotation(math.radians(ang) * sgn, 4, 'Y') @ Matrix.Translation(-head)
    pb.matrix = R @ pb.matrix
    bpy.context.view_layer.update()
bpy.ops.object.mode_set(mode='OBJECT')

# 4) 굽힌 knight 몸을 굳혀 가중치의 출처로 쓴다
src_list = []
for km in kmeshes:
    c = km.copy(); c.data = km.data.copy(); bpy.context.scene.collection.objects.link(c)
    bpy.ops.object.select_all(action='DESELECT'); c.select_set(True); bpy.context.view_layer.objects.active = c
    for m in c.modifiers:
        if m.type == 'ARMATURE': bpy.ops.object.modifier_apply(modifier=m.name)
    c.parent = None; src_list.append(c)
bpy.ops.object.select_all(action='DESELECT')
for c in src_list: c.select_set(True)
bpy.context.view_layer.objects.active = src_list[0]; bpy.ops.object.join(); src = bpy.context.view_layer.objects.active
src.matrix_world = src.matrix_world  # 그대로

# 5) 가중치 옮기기 (가장 가까운 면에서 보간)
for g in src.vertex_groups:
    if g.name not in ach.vertex_groups: ach.vertex_groups.new(name=g.name)
dt = ach.modifiers.new('dt', 'DATA_TRANSFER'); dt.object = src
dt.use_vert_data = True; dt.data_types_verts = {'VGROUP_WEIGHTS'}; dt.vert_mapping = 'POLYINTERP_NEAREST'
dt.layers_vgroup_select_src = 'ALL'; dt.layers_vgroup_select_dst = 'NAME'
bpy.ops.object.select_all(action='DESELECT'); ach.select_set(True); bpy.context.view_layer.objects.active = ach
bpy.ops.object.modifier_apply(modifier='dt')
# 가중치 정규화, 너무 작은 것 정리
bpy.ops.object.mode_set(mode='WEIGHT_PAINT'); bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.01)
bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4); bpy.ops.object.vertex_group_normalize_all(lock_active=False)
bpy.ops.object.mode_set(mode='OBJECT')

# 6) A자를 쉼 자세로 둔 임시 뼈대에 붙이고, 팔을 들어 T자로 편 뒤 굳힌다 (보통 자세 잡기와 같은 변형)
tmp = arm.copy(); tmp.data = arm.data.copy(); bpy.context.scene.collection.objects.link(tmp)
bpy.ops.object.select_all(action='DESELECT'); tmp.select_set(True); bpy.context.view_layer.objects.active = tmp
bpy.ops.object.mode_set(mode='POSE'); bpy.ops.pose.select_all(action='SELECT'); bpy.ops.pose.armature_apply(selected=False)
for side, sgn in (('Left', -1), ('Right', 1)):
    pb = tmp.pose.bones['mixamorig:%sArm' % side]; head = pb.head.copy()
    R = Matrix.Translation(head) @ Matrix.Rotation(math.radians(ang) * sgn, 4, 'Y') @ Matrix.Translation(-head)
    pb.matrix = R @ pb.matrix; bpy.context.view_layer.update()
bpy.ops.object.mode_set(mode='OBJECT')
tm = ach.modifiers.new('tpose', 'ARMATURE'); tm.object = tmp
bpy.ops.object.select_all(action='DESELECT'); ach.select_set(True); bpy.context.view_layer.objects.active = ach
bpy.ops.object.modifier_apply(modifier='tpose')
bpy.data.objects.remove(tmp, do_unlink=True)
bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE'); bpy.ops.pose.select_all(action='SELECT'); bpy.ops.pose.transforms_clear(); bpy.ops.object.mode_set(mode='OBJECT')
# 7) knight 몸은 지우고 Achilles를 뼈대에 붙인다
for o in list(bpy.context.scene.objects):
    if o.type == 'MESH' and o.name != ach.name: bpy.data.objects.remove(o, do_unlink=True)
mw = ach.matrix_world.copy(); ach.parent = arm; ach.matrix_world = mw
am = ach.modifiers.new('Armature', 'ARMATURE'); am.object = arm

# 8) 재질: 텍스처 한 장
mat = bpy.data.materials.new('Hoplite_MAT'); mat.use_nodes = True
bsdf = mat.node_tree.nodes.get('Principled BSDF'); img = mat.node_tree.nodes.new('ShaderNodeTexImage'); img.image = bpy.data.images.load(TEX)
mat.node_tree.links.new(img.outputs['Color'], bsdf.inputs['Base Color']); bsdf.inputs['Roughness'].default_value = 0.7; bsdf.inputs['Metallic'].default_value = 0.2
me.materials.clear(); me.materials.append(mat)
bpy.ops.object.select_all(action='DESELECT'); ach.select_set(True); bpy.context.view_layer.objects.active = ach
bpy.ops.object.shade_smooth()

# 9) 내보내기 (뼈대 + 메시, 애니메이션 없음)
bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); ach.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_animations=False, export_skins=True, export_apply=False, export_image_format='JPEG', export_jpeg_quality=88)
print('exported', OUT)

# 10) 확인용 그림: 앞, 옆
scene = bpy.context.scene
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); scene.collection.objects.link(cam); scene.camera = cam
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 2.6
light = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); scene.collection.objects.link(light); light.rotation_euler = (math.radians(50), 0, math.radians(20))
scene.render.engine = 'BLENDER_WORKBENCH'; scene.display.shading.color_type = 'TEXTURE'; scene.display.shading.light = 'STUDIO'
scene.render.resolution_x = 700; scene.render.resolution_y = 700
for tag, loc, rot in (('front', (0, -10, 1.05), (90, 0, 0)), ('side', (10, 0, 1.05), (90, 0, 90))):
    cam.location = loc; cam.rotation_euler = tuple(math.radians(a) for a in rot)
    scene.render.filepath = PREV.replace('.png', '_%s.png' % tag); bpy.ops.render.render(write_still=True)
print('done')
