# 왕의 말(chr/horse.glb = chrb/horse.wasm) 만들기: Sketchfab "Akhal-Teke Stallion (Rigged & Animated)"
# (Animal Animator, CC BY 4.0)을 게임용으로 줄인다.
#
#   blender -b --factory-startup --python horse_prep.py -- 원본.glb horse.glb [몸통면수=36000]
#
# 원본: assets\akhal-teke_stallion__rigged__animated_3d_model.glb (44MB, 몸통 10만 면, 눈 한 쪽 2만4천 면, 텍스처 4k)
# 하는 일
#  - 몸통은 65535점 제한 때문에 두 조각(mesh_0, mesh_0.001)으로 나뉘어 있다. 합치고 같은 자리 점을 붙인 뒤 면 수를 줄인다.
#  - 눈은 400면, 혀는 300면으로 줄인다. 속눈썹, 꼬리털(얇은 판)은 그대로 둔다.
#  - 텍스처: 몸 색 2k, 몸 노멀과 거칠기 1k, 털 1k, 눈과 혀 256.
#  - 크기: 머리 끝까지 1.75m(게임은 CHR_DEF.horse.h로 다시 맞추지만 파일도 실제 크기로 둔다). 방향은 그대로(머리가 glTF +Z).
#  - 동작: 원본에는 Chewing(서서 씹기, 9.4초), Trot(속보, 4걸음), Run_Gallop(질주, 4걸음)뿐이다.
#      Idle = Chewing 전체, Walk = Trot 한 걸음(17.6프레임), Run = Run_Gallop 한 걸음(12프레임).
#      한 걸음만 남기는 까닭: 군중(VAT)은 동작 하나를 12~14장으로 굽는데, 4걸음을 12장에 담으면 다리가 튄다.
#      쓰러짐 동작은 없다. 게임은 기수가 탄 탈것의 시체를 군중으로 그리지 않아(병사 시체 그리기에서 rider가 있으면 건너뜀) 쓰이지 않는다.
import bpy, sys, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = argv[0], argv[1]
BODY_TRIS = int(argv[2]) if len(argv) > 2 else 36000
H = 1.75

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
for o in list(bpy.data.objects):
    if o.type == 'MESH' and o.name.startswith('Icosphere'):
        bpy.data.objects.remove(o, do_unlink=True)

arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
mat_of = lambda o: o.data.materials[0].name if o.data.materials else ''

def sel_only(objs, active=None):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = active or objs[0]

# 1) 몸통 두 조각 합치기, 같은 자리 점 붙이기
body = [o for o in meshes if mat_of(o) == 'Akhal_Teke_Baked_Mat']
body.sort(key=lambda o: -len(o.data.vertices))
sel_only(body, body[0]); bpy.ops.object.join(); B = body[0]; B.name = 'HorseBody'
sel_only([B]); bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles(threshold=0.0004); bpy.ops.object.mode_set(mode='OBJECT')

def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)

def decimate(o, target):
    if o.data.shape_keys:   # 모양 키는 게임이 쓰지 않고, 있으면 줄이기가 안 된다. 지금 섞인 모양 그대로 굳힌다(그냥 지우면 입술이 벌어져 이가 드러난다)
        mix = o.shape_key_add(name='mix', from_mix=True)
        co = [p.co.copy() for p in mix.data]
        o.shape_key_clear()
        for v, c in zip(o.data.vertices, co): v.co = c
    t = tris(o)
    if t <= target: return
    m = o.modifiers.new('dec', 'DECIMATE'); m.decimate_type = 'COLLAPSE'; m.ratio = target / t
    m.use_collapse_triangulate = True
    # 갑옷처럼 이음매가 보이지 않게: UV 경계는 지키고 대칭으로
    m.use_symmetry = False
    sel_only([o]); bpy.ops.object.modifier_apply(modifier=m.name)

decimate(B, BODY_TRIS)
for o in [x for x in bpy.data.objects if x.type == 'MESH']:
    if o == B: continue
    mn = mat_of(o)
    if mn == 'Horse_Eye_Mat': decimate(o, 400)
    elif mn == 'Horse_Tongue_Mat': decimate(o, 300)

# 2) 정점마다 뼈 가중치는 4개까지(게임 VAT 굽기, glTF 모두 4개), 합 1로
for o in [x for x in bpy.data.objects if x.type == 'MESH']:
    sel_only([o])
    bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
    bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)

# 3) 몸의 금속, 거칠기 텍스처는 뺀다(말털에 금속은 0이고, 게임은 금속 지도가 없으면 거칠기 0.72로 맞춘다). 1MB 줄어든다
bm_ = bpy.data.materials['Akhal_Teke_Baked_Mat']
for n in list(bm_.node_tree.nodes):
    if n.type == 'BSDF_PRINCIPLED':
        for nm, v in (('Metallic', 0.0), ('Roughness', 0.7)):
            for l in list(n.inputs[nm].links): bm_.node_tree.links.remove(l)
            n.inputs[nm].default_value = v

# 텍스처 줄이기
SIZES = {}; KEEP_ALPHA = set()
for m in bpy.data.materials:
    if not m.node_tree: continue
    for n in m.node_tree.nodes:
        if n.type != 'TEX_IMAGE' or not n.image: continue
        to = [l.to_socket.name for o in n.outputs for l in o.links]
        if m.name == 'Akhal_Teke_Baked_Mat': s = 2048 if 'Base Color' in to else 1024
        elif m.name == 'Horse_Hair_Mat': s = 1024
        else: s = 256
        SIZES[n.image.name] = s
        if any(l.to_socket.name == 'Value' or l.to_socket.name == 'Alpha' for o in n.outputs for l in o.links) and m.name == 'Horse_Hair_Mat':
            KEEP_ALPHA.add(n.image.name)   # 털 판의 투명도
for im in bpy.data.images:
    s = SIZES.get(im.name)
    if s and im.size[0] > s:
        im.scale(s, s)
    if s: im.file_format = 'PNG' if im.name in KEEP_ALPHA else 'JPEG'

# 4) 크기: 머리 끝까지 H
top = None
for o in bpy.data.objects:
    if o.type != 'MESH': continue
    for c in o.bound_box:
        z = (o.matrix_world @ Vector(c)).z
        top = z if top is None or z > top else top
rootE = arm
while rootE.parent: rootE = rootE.parent
k = H / top
rootE.scale = rootE.scale * k
bpy.context.view_layer.update()
print('SCALE', k, 'top', top)

# 5) 동작 정리
acts = {a.name: a for a in bpy.data.actions}
def ranged(a, name, f0, f1):
    a.name = name; a.use_frame_range = True; a.frame_start = f0; a.frame_end = f1; a.use_cyclic = True
    a.use_fake_user = True
ranged(acts['Chewing'], 'Idle', 0, 225)
# Trot 한 걸음은 17.6프레임이라 정수 프레임으로 뽑으면 이음매가 튄다 → 18프레임이 되게 시간을 살짝 늘린다(속도 2% 느려짐)
def fcurves_of(a):
    if hasattr(a, 'fcurves') and len(getattr(a, 'fcurves', [])): return list(a.fcurves)
    out = []
    for ly in a.layers:
        for st in ly.strips:
            for cb in st.channelbags: out += list(cb.fcurves)
    return out
for fc in fcurves_of(acts['Trot']):
    for kp in fc.keyframe_points:
        for p in (kp.co, kp.handle_left, kp.handle_right): p.x *= 18 / 17.6
ranged(acts['Trot'], 'Walk', 0, 18)
ranged(acts['Run_Gallop'], 'Run', 0, 12)

# 내보낼 동작을 NLA 트랙으로(내보내기 기본: 액션마다 애니메이션 하나)
arm.animation_data.action = None
for pb in arm.pose.bones:
    pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0); pb.scale = (1, 1, 1)
for name in ['Idle', 'Walk', 'Run']:
    tr = arm.animation_data.nla_tracks.new(); tr.name = name
    st = tr.strips.new(name, 0, bpy.data.actions[name]); tr.mute = True

for o in bpy.data.objects:
    if o.type == 'MESH': print('MESH', o.name, 'tris', tris(o), 'verts', len(o.data.vertices))

bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS',
                          export_force_sampling=True, export_frame_range=False, export_anim_single_armature=True,
                          export_image_format='AUTO', export_jpeg_quality=85, export_skins=True, export_all_influences=False,
                          export_morph=False, export_def_bones=False, export_optimize_animation_size=True,
                          export_apply=False, export_yup=True)
print('DONE', OUT)
