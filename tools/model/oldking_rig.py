"""선왕 모델: Old king armor(Sketchfab, Pedro B. Goulart, CC BY 4.0)에 게임의 knight 뼈대(mixamorig)를 입혀 glb로 내보낸다.
이 모델은 AI로 만든 한 덩어리 메시가 아니라 작가가 뼈대(Hip, Belly, Torax, Arm.L 등 77개, mixamo 이름 아님)와 가중치를 직접 칠한 모델이다.
그래서 knight 몸에서 가중치를 옮겨 오지 않고(왕, 바르고스는 그 경계 때문에 늘어났다) 원본 가중치를 그대로 mixamo 이름으로 바꿔 쓴다.
- knight 뼈를 하나씩 모델 뼈 방향으로 돌린 뒤(팔 내린 자세, 손가락까지) 그 자세를 쉼 자세로 두고, 관절 자리를 모델 관절로 옮긴다(방향은 그대로).
  게임은 관절 회전값을 통째로 덮어쓰므로 뼈 방향이 knight와 같아야 하고, 뼈 길이(관절 자리)는 달라도 된다.
- 무기는 모델에 없다. 게임이 쥐여 주는 칼, 방패를 쓴다.
- 점과 면은 지우지 않는다.
사용: blender -b --factory-startup --python oldking_rig.py -- chr/knight.glb old_king_armor.glb oldking.glb preview.png [텍스처크기]"""
import bpy, sys, math, re
from mathutils import Vector, Matrix
argv = sys.argv[sys.argv.index('--') + 1:]
KNIGHT, SRC, OUT, PREV = argv[:4]
TEXSZ = int(argv[4]) if len(argv) > 4 else 2048
TEXSZ_SUB = TEXSZ // 2          # 금속, 거칠기와 노멀 텍스처는 절반 크기로

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=KNIGHT)
kobjs = list(bpy.context.scene.objects)
arm = next(o for o in kobjs if o.type == 'ARMATURE')
kmeshes = [o for o in kobjs if o.type == 'MESH']
KB = {b.name.replace('mixamorig:', ''): b for b in arm.data.bones}
bpy.ops.import_scene.gltf(filepath=SRC)
new = [o for o in bpy.context.scene.objects if o not in kobjs]
oa = next(o for o in new if o.type == 'ARMATURE')
oms = [o for o in new if o.type == 'MESH' and o.vertex_groups]
for o in new:
    if o.type == 'MESH' and o not in oms: bpy.data.objects.remove(o, do_unlink=True)
# 원본 파일은 걷는 듯한 자세로 저장되어 있다. 쉼 자세(두 다리를 모으고 팔을 약 72도 내린 좌우 대칭 자세)로 되돌려 그 자세로 묶는다
for pb in oa.pose.bones: pb.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()
J = {b.name: oa.matrix_world @ b.head_local for b in oa.data.bones}
# 메시를 하나로 합치고 원본 좌표(쉼 자세) 그대로 굳힌다
for o in oms:
    for m in list(o.modifiers): o.modifiers.remove(m)
    mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
bpy.ops.object.select_all(action='DESELECT')
for o in oms: o.select_set(True)
bpy.context.view_layer.objects.active = oms[0]; bpy.ops.object.join(); ok = bpy.context.view_layer.objects.active
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in list(bpy.context.scene.objects):
    if o.type in ('EMPTY',) or o == oa: bpy.data.objects.remove(o, do_unlink=True)
ok.name = 'OldKing'; me = ok.data
# 원본은 위가 +Y, 앞이 +Z다 → 위 +Z, 앞 -Y (X축으로 90도)
R = Matrix.Rotation(math.radians(90), 4, 'X')
me.transform(R); J = {k: R @ v for k, v in J.items()}
z0 = min(v.co.z for v in me.vertices); H = max(v.co.z for v in me.vertices) - z0
# 크기: 엉덩이 높이를 knight 엉덩이에. 발은 바닥(z=0), 몸 가운데는 knight 엉덩이 앞뒤 자리에
def kw(n): return arm.matrix_world @ KB[n].head_local
hips_k = kw('Hips'); hip_m = J['Hip_01']
s = hips_k.z / (hip_m.z - z0)
T = Matrix.Translation(Vector((0, hips_k.y, 0))) @ Matrix.Scale(s, 4) @ Matrix.Translation(Vector((-hip_m.x, -hip_m.y, -z0)))
me.transform(T); J = {k: T @ v for k, v in J.items()}
HS = H * s
print('scale', round(s, 5), 'height', round(HS, 3), 'knight hips', tuple(round(x, 3) for x in hips_k))

# 원본 뼈 → mixamo 뼈. 두 뼈 사이에 이어 붙는 다음 관절(방향을 맞출 때 씀)
FING = ('Thumb', 'Index', 'Middle', 'Ring', 'Pinky')
MAP = {'Hip': 'Hips', 'Torax': 'Spine2', 'Neck': 'Neck', 'Head': 'Head'}
for sd, k in (('L', 'Left'), ('R', 'Right')):
    for src, dst in (('Clavicule', 'Shoulder'), ('Arm', 'Arm'), ('Forearm', 'ForeArm'), ('Hand', 'Hand'), ('Femur', 'UpLeg'), ('Shin', 'Leg'), ('Feet', 'Foot'), ('FeetTip', 'ToeBase'),
                     ('ShoulderPad', 'Shoulder'), ('ElbowPad', 'ForeArm'), ('KneePad', 'Leg')):
        MAP['%s.%s' % (src, sd)] = k + dst
    for f in FING:
        for i in (1, 2, 3): MAP['%s%d.%s' % (f, i, sd)] = '%sHand%s%d' % (k, f, i)
def jn(short):   # 'Arm.L' → 'Arm.L_07' (원본 뼈 이름 뒤에 번호가 붙어 있다)
    return next(n for n in J if re.fullmatch(re.escape(short) + r'_\d+', n))
JM = {}           # mixamo 이름 → 모델 관절 자리
for short, dst in MAP.items():
    if re.search(r'Pad', short): continue
    JM[dst] = J[jn(short)]
# 등뼈: 원본은 Belly 하나, knight는 Spine, Spine1 둘. Spine은 Belly 밑, Spine1은 Belly 가운데
JM['Spine'] = J[jn('Belly')]; JM['Spine1'] = (J[jn('Belly')] + J[jn('Torax')]) / 2
for k in sorted(JM): print('joint %-22s %.3f %.3f %.3f' % (k, *JM[k]))
missing = [k for k in JM if k not in KB]
print('knight lacks', missing)

# 가중치: 원본 그룹을 mixamo 이름으로 합친다. Belly는 높이로 Spine과 Spine1에 나눈다
gsrc = {g.index: g.name for g in ok.vertex_groups}
W = []
zb, zt = JM['Spine'].z, JM['Spine2'].z
for v in me.vertices:
    acc = {}
    for g in v.groups:
        n = gsrc[g.group]; short = re.sub(r'_\d+$', '', n)
        if short == 'Belly':
            t = max(0.0, min(1.0, (v.co.z - zb) / max(1e-6, zt - zb)))
            acc['Spine'] = acc.get('Spine', 0) + g.weight * (1 - t); acc['Spine1'] = acc.get('Spine1', 0) + g.weight * t; continue
        dst = MAP.get(short)
        if dst is None: print('unmapped group', n); continue
        if dst not in KB: dst = re.sub(r'(Thumb|Index|Middle|Ring|Pinky)\d$', '', dst)   # knight에 없는 손가락 마디는 손에
        acc[dst] = acc.get(dst, 0) + g.weight
    W.append(acc)
# 몸통, 엉덩이, 어깨, 위팔, 허벅지 가중치를 이웃 점과 고르게 편다. 원본 가중치는 엉덩이 뒤(엉덩이~허벅지)와 어깨뼈 아래(가슴~위팔)에서
# 1~2cm 사이에 1.0 → 0.4로 바뀌어, 원본 뼈대보다 크게 움직이는 게임 동작에서는 그 짧은 변이 7~14cm로 늘어났다.
# 이 뼈들에만 묶인 점끼리 펴고(팔뚝, 손, 다리 아래, 머리 점은 바꾸지도 이웃으로 쓰지도 않는다), 텍스처 이음매의 같은 자리 점은 한 점으로 본다
import os, numpy as np
SMOOTH_N = int(os.environ.get('SMOOTH_N', '20'))
SOFT = re.compile(r'(Hips|Spine\d?|Neck|(Left|Right)(Shoulder|Arm|UpLeg))$')
if SMOOTH_N:
    names = sorted({n for a in W for n in a}); col = {n: j for j, n in enumerate(names)}; nV = len(W)
    Wm = np.zeros((nV, len(names)))
    for i, a in enumerate(W):
        for n, w in a.items(): Wm[i, col[n]] = w
    Wm /= np.maximum(Wm.sum(1, keepdims=True), 1e-9)
    okm = np.array([bool(a) and all(SOFT.fullmatch(n) for n in a) for a in W])
    rep = np.arange(nV); key = {}
    for v in me.vertices:
        if not okm[v.index]: continue
        kk = (round(v.co.x * 2000), round(v.co.y * 2000), round(v.co.z * 2000))
        if kk in key: rep[v.index] = key[kk]
        else: key[kk] = v.index
    E = rep[np.array([(e.vertices[0], e.vertices[1]) for e in me.edges])]
    E = E[(E[:, 0] != E[:, 1]) & okm[E[:, 0]] & okm[E[:, 1]]]; E = np.concatenate([E, E[:, ::-1]])
    Wr = np.zeros_like(Wm); np.add.at(Wr, rep, Wm); Wr /= np.maximum(Wr.sum(1, keepdims=True), 1e-9)
    am = np.zeros(nV); np.maximum.at(am, rep, okm.astype(float))
    for _ in range(SMOOTH_N):
        acc = np.zeros_like(Wr); cnt = np.zeros(nV)
        np.add.at(acc, E[:, 0], Wr[E[:, 1]]); np.add.at(cnt, E[:, 0], 1)
        avg = np.where(cnt[:, None] > 0, acc / np.maximum(cnt[:, None], 1), Wr)
        Wr = Wr + (avg - Wr) * (0.5 * am)[:, None]
    for i in np.nonzero(okm)[0]: W[i] = {names[j]: float(Wr[rep[i], j]) for j in np.nonzero(Wr[rep[i]] > 0.005)[0]}
    print('smoothed', int(okm.sum()), 'iterations', SMOOTH_N)
for g in list(ok.vertex_groups): ok.vertex_groups.remove(g)
VG = {}
for i, acc in enumerate(W):
    tot = sum(acc.values())
    for n, w in sorted(acc.items(), key=lambda x: -x[1])[:4]:
        if w / max(tot, 1e-9) < 0.01: continue
        if n not in VG: VG[n] = ok.vertex_groups.new(name='mixamorig:' + n)
        VG[n].add([i], w / tot, 'REPLACE')
print('groups', sorted(VG))
nw = sum(1 for a in W if not a); print('verts without weight', nw)

# knight 뼈를 모델 뼈 방향으로 돌린다(부모부터). 방향 = 이 관절에서 다음 관절로
NEXT = {'Spine': 'Spine1', 'Spine1': 'Spine2', 'Spine2': 'Neck', 'Neck': 'Head'}
for k in ('Left', 'Right'):
    NEXT.update({k + 'Shoulder': k + 'Arm', k + 'Arm': k + 'ForeArm', k + 'ForeArm': k + 'Hand', k + 'Hand': k + 'HandMiddle1',
                 k + 'UpLeg': k + 'Leg', k + 'Leg': k + 'Foot', k + 'Foot': k + 'ToeBase'})
    for f in FING: NEXT.update({'%sHand%s1' % (k, f): '%sHand%s2' % (k, f), '%sHand%s2' % (k, f): '%sHand%s3' % (k, f)})
def kids_of(n):   # knight에서 n의 자식 중 NEXT 대상
    return arm.pose.bones['mixamorig:' + NEXT[n]]
bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
def _dep(b):
    d = 0
    while b.parent: b = b.parent; d += 1
    return d
order = [b.name.replace('mixamorig:', '') for b in sorted(arm.data.bones, key=_dep)]   # 부모부터
# 팔다리만 돌린다. 쇄골, 등뼈, 목은 knight 방향 그대로 둔다: 게임 동작이 이 뼈들의 회전을 knight 값으로 덮어써,
# 쇄골을 모델 쇄골 방향(가슴 가운데 앞에서 뒤로 28도)으로 돌려 묶었더니 대기 자세에서도 팔이 통째로 앞으로 돌아 팔과 가슴 사이가 늘어났다(Arm~Spine2 600)
import os
AIM = re.compile(os.environ.get('AIM', r'(Left|Right)(Arm|ForeArm|Hand|Hand(Thumb|Index|Middle|Ring|Pinky)\d|UpLeg|Leg|Foot)$'))
def mdir(n):
    if not AIM.fullmatch(n): return None
    if n in NEXT and NEXT[n] in JM: return (JM[NEXT[n]] - JM[n]).normalized()
    m = re.match(r'(Left|Right)Hand(Thumb|Index|Middle|Ring|Pinky)3$', n)   # 손가락 끝마디는 둘째 마디 방향
    if m and n in JM: return (JM[n] - JM[n[:-1] + '2']).normalized()
    return None
rot = 0
for n in order:
    d1 = mdir(n)
    if d1 is None or n not in KB: continue
    pb = arm.pose.bones['mixamorig:' + n]
    if n in NEXT and 'mixamorig:' + NEXT[n] in arm.pose.bones: d0 = (arm.matrix_world @ kids_of(n).head) - (arm.matrix_world @ pb.head)
    else: d0 = (arm.matrix_world @ pb.tail) - (arm.matrix_world @ pb.head)
    if d0.length < 1e-6: continue
    q = d0.normalized().rotation_difference(d1)
    head = pb.head.copy()
    aw = arm.matrix_world.to_3x3().normalized(); qa = (aw.inverted() @ q.to_matrix() @ aw).to_4x4()   # 회전을 뼈대 좌표로
    pb.matrix = Matrix.Translation(head) @ qa @ Matrix.Translation(-head) @ pb.matrix
    bpy.context.view_layer.update(); rot += 1
print('bones aimed', rot)
bpy.ops.pose.select_all(action='SELECT'); bpy.ops.pose.armature_apply(selected=False); bpy.ops.object.mode_set(mode='OBJECT')
# 관절 자리를 모델로 옮긴다(뼈 방향, 비틀림은 그대로 두고 통째로 옮긴다). 짝이 없는 뼈(손가락 끝, 머리 끝)는 부모와 같이 옮긴다
bpy.ops.object.mode_set(mode='EDIT'); eb = arm.data.edit_bones; inv = arm.matrix_world.inverted()
delta = {}
def depth(b):
    d = 0
    while b.parent: b = b.parent; d += 1
    return d
for b in sorted(eb, key=depth):
    n = b.name.replace('mixamorig:', '')
    if n in JM: delta[b.name] = (inv @ JM[n]) - b.head
    elif b.parent and b.parent.name in delta: delta[b.name] = delta[b.parent.name]
    else: delta[b.name] = Vector()
for b in eb:
    d = delta[b.name]; b.head = b.head + d; b.tail = b.tail + d
bpy.ops.object.mode_set(mode='OBJECT')
for n in ('Hips', 'LeftArm', 'LeftForeArm', 'LeftHand', 'RightUpLeg', 'RightFoot', 'Head'):
    p = arm.matrix_world @ arm.data.bones['mixamorig:' + n].head_local; print('bone %-12s %.3f %.3f %.3f' % (n, *p))
# knight 몸을 지우고 묶는다
for o in kmeshes: bpy.data.objects.remove(o, do_unlink=True)
for o in list(bpy.context.scene.objects):
    if o.type == 'MESH' and o != ok: bpy.data.objects.remove(o, do_unlink=True)
mw = ok.matrix_world.copy(); ok.parent = arm; ok.matrix_world = mw
am = ok.modifiers.new('Armature', 'ARMATURE'); am.object = arm
# 텍스처 줄이기: 색은 TEXSZ, 나머지는 절반
mat = me.materials[0]
base = None
for nd in mat.node_tree.nodes:
    if nd.type == 'BSDF_PRINCIPLED':
        l = nd.inputs['Base Color'].links
        if l: base = l[0].from_node.image
for img in bpy.data.images:
    sz = TEXSZ if img == base else TEXSZ_SUB
    if img.size[0] > sz: img.scale(sz, sz)
    print('image', img.name, img.size[:], 'base' if img == base else '')
bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); ok.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_animations=False, export_skins=True, export_image_format='JPEG', export_jpeg_quality=85)
print('exported', OUT)
# 미리보기(쉼 자세). 동작 확인은 게임 안에서 한다(README)
scene = bpy.context.scene
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); scene.collection.objects.link(cam); scene.camera = cam
cam.data.type = 'ORTHO'; cam.data.ortho_scale = HS * 1.15
scene.render.engine = 'BLENDER_WORKBENCH'; scene.display.shading.color_type = 'TEXTURE'; scene.render.resolution_x = 700; scene.render.resolution_y = 700
for tag, loc, rot_ in (('front', (0, -10, HS / 2), (90, 0, 0)), ('side', (10, 0, HS / 2), (90, 0, 90)), ('back', (0, 10, HS / 2), (90, 0, 180))):
    cam.location = loc; cam.rotation_euler = tuple(math.radians(a) for a in rot_)
    scene.render.filepath = PREV.replace('.png', '_%s.png' % tag); bpy.ops.render.render(write_still=True)
print('done')
