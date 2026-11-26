"""Aegis Sentinel(Sketchfab, PixForge, CC BY)에 게임의 knight 뼈대(mixamorig)를 입혀 glb로 내보낸다.
- 모델은 팔을 내린 자세 그대로 묶는다. 게임은 관절 회전값을 통째로 덮어쓰므로 쉼 자세가 T자가 아니어도 동작이 맞다
- 칼은 오른손, 방패는 왼쪽 팔뚝에 통째로 묶는다. 망토는 다리 대신 등뼈와 엉덩이를 따른다
사용: blender -b --factory-startup --python aegis_rig.py -- knight.glb aegis.glb out.glb preview.png [텍스처크기]"""
import bpy, sys, math, mathutils, re
from mathutils import Vector, Matrix
argv = sys.argv[sys.argv.index('--') + 1:]
KNIGHT, AEGIS, OUT, PREV = argv[:4]
TEXSZ = int(argv[4]) if len(argv) > 4 else 2048
ARM_DOWN = 76.0          # 팔이 수평에서 아래로 내려간 각도(도)
SHOULDER_H = 0.67        # 어깨 관절 높이(모델 키에 대한 비율)
LEG_OUT = 9.0            # 다리가 바깥으로 벌어진 각도(도)
R_LEG_BACK = 7.0         # 오른다리가 뒤로 빠진 각도(도)
# 팔 관절 자리(만든 모델 좌표, 오른쪽 기준. 왼쪽은 x를 뒤집는다). knight 팔은 이 모델보다 짧고 몸 쪽으로 붙어 있어
# 팔 뼈가 팔 속이 아니라 옆구리 쪽(5~11cm 안쪽)을 지나갔다. 모델 팔의 중심선과 텍스처(살갗, 팔 보호대, 장갑) 경계로 팔꿈치와 손목을 옮긴다
ELBOW = (-0.41, 1.40)    # (x, 높이): 위팔 살갗이 끝나고 파란 팔 보호대가 시작하는 곳(텍스처 색으로 잼)
WRIST = (-0.44, 1.14)    # 팔 보호대가 끝나고 장갑이 시작하는 곳. 손가락은 0.93~0.99, 그 아래는 칼
import os
CAPE_CUT = float(os.environ.get('CAPE_CUT', '0'))   # 망토를 이 높이 비율 아래로 잘라 낸다(0이면 그대로, 비교용)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=KNIGHT)
kobjs = list(bpy.context.scene.objects)
arm = next(o for o in kobjs if o.type == 'ARMATURE')
kmeshes = [o for o in kobjs if o.type == 'MESH' and o.name != 'Icosphere']
bpy.ops.import_scene.gltf(filepath=AEGIS)
ams = [o for o in bpy.context.scene.objects if o not in kobjs and o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in ams: o.select_set(True)
bpy.context.view_layer.objects.active = ams[0]; bpy.ops.object.join(); ag = bpy.context.view_layer.objects.active
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM'); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in list(bpy.context.scene.objects):
    if o.type == 'EMPTY': bpy.data.objects.remove(o, do_unlink=True)
ag.name = 'Aegis'; me = ag.data
me.transform(Matrix.Rotation(math.radians(-90), 4, 'Z'))      # 앞을 -Y로
zs = [v.co.z for v in me.vertices]; z0 = min(zs); H = max(zs) - z0
def hr(co): return (co.z - z0) / H                              # 원래 높이 비율(0=발, 1=말총 끝)
# 망토: 텍스처가 펼쳐진 조각(UV 섬) 단위로 고른다. 위치로 점마다 가르면 망토, 팔, 다리가 맞붙은 곳에서
# 발뒤꿈치, 위팔, 손 옆이 번갈아 잘못 묶여 구멍이나 덤 팔이 생겼다. 망토는 몸 뒤쪽 점이 90% 넘는 큰 섬(바깥면, 안쪽면 둘)이고,
# 망토 표면에 바로 붙은 작은 섬도 망토로 친다. 나머지(팔, 다리, 몸)는 knight에서 옮겨 온 가중치를 그대로 쓴다
import bmesh
from mathutils import kdtree
bmu = bmesh.new(); bmu.from_mesh(me); uvl = bmu.loops.layers.uv.active; bmu.faces.ensure_lookup_table()
def uk(l): return (round(l[uvl].uv.x, 5), round(l[uvl].uv.y, 5))
fid = {}; isl = []
for f in bmu.faces:
    if f.index in fid: continue
    fid[f.index] = len(isl); stk = [f]; cur = [f]
    while stk:
        x = stk.pop()
        for l in x.loops:
            for lf in l.edge.link_loops:
                g = lf.face
                if g.index in fid: continue
                if {uk(l), uk(l.link_loop_next)} == {uk(lf), uk(lf.link_loop_next)}: fid[g.index] = len(isl); stk.append(g); cur.append(g)
    isl.append(sorted({v.index for f2 in cur for v in f2.verts}))
capeset = set()
for vs in isl:
    if len(vs) > 1500 and sum(1 for i in vs if me.vertices[i].co.y > 0.095) > len(vs) * 0.9: capeset.update(vs)
kd = kdtree.KDTree(len(capeset))
for i in capeset: kd.insert(me.vertices[i].co, i)
kd.balance()
for vs in isl:   # 망토 가장자리 조각: 큰 망토 섬에 맞닿고(0.1mm), 점 절반이 망토 표면에서 2cm 안, 60% 넘게 몸 뒤쪽
    if len(vs) > 400 or set(vs) <= capeset: continue
    ds = sorted(kd.find(me.vertices[i].co)[2] for i in vs)
    if ds[0] < 0.0001 and ds[len(ds) // 2] < 0.02 and sum(1 for i in vs if me.vertices[i].co.y > 0.095) >= len(vs) * 0.6: capeset.update(vs)
# 방패: 상자로 고르면 테두리 일부가 상자 밖으로 나가 몸에 묶여, 팔을 들면 방패 한쪽이 뜯겨 보였다 → 절반 넘게 방패 상자 안에 있는 UV 섬은 통째로 방패
def inshield(c): h = (c.z - z0) / H; return c.x > 0.165 and 0.27 < h < 0.65 and abs(c.y) < 0.17
shieldset = set()
for vs in isl:
    if set(vs) <= capeset: continue
    if sum(1 for i in vs if inshield(me.vertices[i].co)) >= len(vs) * 0.5: shieldset.update(i for i in vs if i not in capeset)
bmu.free()
# 부위 고르기 (원래 좌표 기준, 정면 -Y, 캐릭터의 왼쪽 = +X)
part = {}
for v in me.vertices:
    c = v.co; h = hr(c)
    if v.index in capeset: part[v.index] = 'drop' if h < CAPE_CUT else 'cape'
    elif v.index in shieldset: part[v.index] = 'shield'
    elif c.x < -0.15 and 0.05 < h < 0.405 and c.y < 0.0: part[v.index] = 'blade'     # 발 높이(5% 아래)는 오른발 앞코다. 칼로 묶으면 손을 따라 바닥 근처에 점처럼 떠다닌다
print('parts', {k: sum(1 for p in part.values() if p == k) for k in ('shield', 'blade', 'cape', 'drop')})
# 크기와 자리: 어깨 높이를 knight 어깨에, 발을 바닥에, 몸통 앞뒤 가운데를 knight 엉덩이에
def bw(n): return arm.matrix_world @ arm.data.bones[n].head_local
la = bw('mixamorig:LeftArm'); hips = bw('mixamorig:Hips')
s = la.z / (SHOULDER_H * H)
sl = [v.co for v in me.vertices if abs(hr(v.co) - 0.64) < 0.01 and v.co.y < 0.09]
cy = (min(p.y for p in sl) + max(p.y for p in sl)) / 2
me.transform(Matrix.Translation(Vector((0, -cy, -z0))))
me.transform(Matrix.Scale(s, 4))
me.transform(Matrix.Translation(Vector((0, hips.y, 0))))
print('scale', round(s, 4), 'height', round(H * s, 3))

# knight 뼈대를 팔 내린 자세로
bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
for side, sgn in (('Left', 1), ('Right', -1)):
    pb = arm.pose.bones['mixamorig:%sArm' % side]; head = pb.head.copy()
    pb.matrix = Matrix.Translation(head) @ Matrix.Rotation(math.radians(ARM_DOWN) * sgn, 4, 'Y') @ Matrix.Translation(-head) @ pb.matrix
    bpy.context.view_layer.update()
# 다리: Aegis는 두 발을 벌리고(바깥으로 약 9도) 오른발을 뒤로(약 7도) 뺀 자세다. 뼈도 같은 각도로 (안 맞추면 걸을 때 팔자걸음)
for name, axis, deg in (('LeftUpLeg', 'Y', -LEG_OUT), ('RightUpLeg', 'Y', LEG_OUT), ('RightUpLeg', 'X', R_LEG_BACK)):
    pb = arm.pose.bones['mixamorig:' + name]; head = pb.head.copy()
    pb.matrix = Matrix.Translation(head) @ Matrix.Rotation(math.radians(deg), 4, axis) @ Matrix.Translation(-head) @ pb.matrix
    bpy.context.view_layer.update()
bpy.ops.object.mode_set(mode='OBJECT')
# 굽힌 knight 몸을 굳혀 가중치 출처로
src = []
for km in kmeshes:
    c = km.copy(); c.data = km.data.copy(); bpy.context.scene.collection.objects.link(c)
    bpy.ops.object.select_all(action='DESELECT'); c.select_set(True); bpy.context.view_layer.objects.active = c
    for m in list(c.modifiers):
        if m.type == 'ARMATURE': bpy.ops.object.modifier_apply(modifier=m.name)
    c.parent = None; src.append(c)
bpy.ops.object.select_all(action='DESELECT')
for c in src: c.select_set(True)
bpy.context.view_layer.objects.active = src[0]; bpy.ops.object.join(); srcm = bpy.context.view_layer.objects.active
for g in srcm.vertex_groups:
    if g.name not in ag.vertex_groups: ag.vertex_groups.new(name=g.name)
dt = ag.modifiers.new('dt', 'DATA_TRANSFER'); dt.object = srcm
dt.use_vert_data = True; dt.data_types_verts = {'VGROUP_WEIGHTS'}; dt.vert_mapping = 'POLYINTERP_NEAREST'
dt.layers_vgroup_select_src = 'ALL'; dt.layers_vgroup_select_dst = 'NAME'
bpy.ops.object.select_all(action='DESELECT'); ag.select_set(True); bpy.context.view_layer.objects.active = ag
bpy.ops.object.modifier_apply(modifier='dt')
# 부위별로 덮어쓴다
VG = {g.name: g for g in ag.vertex_groups}
def setw(i, ws):
    for g in ag.vertex_groups: g.remove([i])
    for n, w in ws:
        if w > 0: VG['mixamorig:' + n].add([i], w, 'REPLACE')
for i, p in part.items():
    if p == 'shield': setw(i, [('LeftForeArm', 1.0)])
    elif p == 'blade': setw(i, [('RightHand', 1.0)])
    elif p == 'cape':
        t = max(0.0, min(1.0, (0.66 - h) / 0.45))      # 위(0) → 아래(1)
        setw(i, [('Spine2', max(0.0, 1 - t * 1.6)), ('Spine1', 0.5 - abs(t - 0.45)), ('Spine', max(0.0, t * 1.3 - 0.3)), ('Hips', max(0.0, t * 1.6 - 0.6))])
# 팔: knight에서 가장 가까운 점으로 옮긴 가중치는 팔 내린 자세에서 팔뚝 안쪽 일부를 위팔에 묶었다.
# 팔꿈치를 굽히면 그 조각만 곧게 남아 팔뚝이 두 개처럼 보였다(사용자: "팔이 두 개잖아").
# 팔 뼈(위팔, 팔뚝, 손)에 묶인 점은 세 마디 중 가장 가까운 마디에 다시 묶고, 팔꿈치와 손목 근처는 두 마디에 나눠 부드럽게 굽힌다
def _ph(n): return arm.matrix_world @ arm.pose.bones['mixamorig:' + n].head
def _proj(p, a, b):
    ab = b - a; t = (p - a).dot(ab) / max(ab.dot(ab), 1e-9); tc = max(0.0, min(1.0, t)); return tc, (p - (a + ab * tc)).length
gnm = {g.index: g.name for g in ag.vertex_groups}; rearm = 0; JOINT = {}
# 팔에서 몸으로 돌릴 허리 아래 점이 따를 가중치: knight에서 팔이 아닌 가장 가까운 점(엉덩이, 허벅지 섞기 그대로).
# 망토 공식(Spine, Spine1 섞기)으로 묶었더니 손 옆 치마 자락이 바로 옆 허벅지 점과 따로 움직여 걸을 때 길게 늘어났다(2026-11-26)
sgnm = {g.index: g.name for g in srcm.vertex_groups}
srcB = [v for v in srcm.data.vertices if len(v.groups) and not re.search(r'(Arm|Hand)', sgnm[max(v.groups, key=lambda g: g.weight).group])]
srcKD = kdtree.KDTree(len(srcB))
for v in srcB: srcKD.insert(srcm.matrix_world @ v.co, v.index)
srcKD.balance()
def knightbody(co):
    v = srcm.data.vertices[srcKD.find(co)[1]]
    return [(sgnm[g.group].replace('mixamorig:', ''), g.weight) for g in v.groups if not re.search(r'(Arm|Hand)', sgnm[g.group])]
LOWBODY = float(os.environ.get('LOWBODY', '0.55'))   # 이 높이 비율 아래는 knight 몸 가중치를 쓴다
ARM_OUT = 0.14 * (H * s) / 2.48; tobody = 0
ARM_IN = 0.08 * (H * s) / 2.48   # 팔 중심선에서 이 안쪽인데 몸통에 묶인 점은 팔 안쪽 면이다(어깨 관절 근처 20%는 몸통과 이어지니 빼고)
for sd in ('Left', 'Right'):
    sx = -1 if sd == 'Right' else 1; A0 = _ph(sd + 'Arm'); A1 = Vector((sx * -ELBOW[0], A0.y, ELBOW[1])); A2 = Vector((sx * -WRIST[0], A0.y, WRIST[1])); A3 = A2 + (A2 - A1) * 0.9
    JOINT[sd] = (A1.copy(), A2.copy())
    for v in me.vertices:
        if part.get(v.index) in ('blade', 'shield', 'cape') or not len(v.groups): continue
        (tu, du), (tf, df), (th, dh) = _proj(v.co, A0, A1), _proj(v.co, A1, A2), _proj(v.co, A2, A3)
        dn = gnm[max(v.groups, key=lambda g: g.weight).group]
        if sd == 'Left' and re.search(r'LeftHand', dn): setw(v.index, [('LeftForeArm', 1.0)]); rearm += 1; continue   # 방패를 쥔 왼손: 방패는 팔뚝에 묶여 있어 손이 따로 꺾이면 방패와 손 사이가 찢어진다 → 손도 팔뚝에 통째로
        if re.search(r'%sHand.+' % sd, dn): setw(v.index, [(sd + 'Hand', 1.0)]); rearm += 1; continue   # 손가락: 이 모델은 칼 손잡이, 방패 손잡이를 이미 쥔 모양이라 손가락 뼈를 따라가면 주먹을 쥘 때 뾰족하게 튄다 → 손에 통째로
        # 팔 뼈에 묶였거나, 팔뼈 중심선에서 11cm 안쪽인데 몸통에 묶인 점(팔 내린 자세에서 몸통에 붙은 팔 안쪽 면)
        if not (re.search(r'%s(Arm|ForeArm|Hand)$' % sd, dn) or (min(du, df, dh) < ARM_IN and not (k0 := (du == min(du, df, dh) and tu < 0.2)))): continue
        k = min((du, 0), (df, 1), (dh, 2))[1]
        # 예전 knight 팔이 옆구리에 붙어 있어 옆구리 갑옷까지 팔로 옮겨 왔다. 새 팔 중심선에서 멀고(ARM_OUT) 몸 쪽에 있으면 몸통에 묶는다
        if min(du, df, dh) > ARM_OUT and abs(v.co.x) < abs((A0, A1, A2)[k].x) and not (k == 0 and tu < 0.2):
            hh = v.co.z / (H * s); t2 = max(0.0, min(1.0, (0.66 - hh) / 0.45))
            if hh < LOWBODY: setw(v.index, knightbody(v.co)); tobody += 1; continue
            setw(v.index, [('Spine2', max(0.0, 1 - t2 * 1.6)), ('Spine1', 0.5 - abs(t2 - 0.45)), ('Spine', max(0.0, t2 * 1.3 - 0.3)), ('Hips', max(0.0, t2 * 1.6 - 0.6))]); tobody += 1; continue
        if k == 0: ws = [(sd + 'Arm', 1.0)] if tu < 0.85 else [(sd + 'Arm', 1 - (tu - 0.85) / 0.3), (sd + 'ForeArm', (tu - 0.85) / 0.3)]
        elif k == 1:
            if tf < 0.15: ws = [(sd + 'ForeArm', 0.5 + tf / 0.3), (sd + 'Arm', 0.5 - tf / 0.3)]
            elif tf > 0.85: ws = [(sd + 'ForeArm', 1 - (tf - 0.85) / 0.3), (sd + 'Hand', (tf - 0.85) / 0.3)]
            else: ws = [(sd + 'ForeArm', 1.0)]
        else: ws = [(sd + 'Hand', 1.0)] if th > 0.15 else [(sd + 'Hand', 0.5 + th / 0.3), (sd + 'ForeArm', 0.5 - th / 0.3)]
        setw(v.index, ws); rearm += 1
print('arm verts reweighted along bones', rearm, 'side armor back to body', tobody)
# 팔 둘레의 작은 부스러기 조각(점 40개 미만): 몸통에 묶이면 팔을 들 때 제자리에 남아 점처럼 떠 보인다 → 팔 중심선 가까이(ARM_OUT) 있으면 가장 가까운 팔 마디에 통째로 묶는다
bmd = bmesh.new(); bmd.from_mesh(me); bmd.verts.ensure_lookup_table(); seen = set(); crumbs = 0
for v0 in bmd.verts:
    if v0.index in seen: continue
    stk = [v0]; comp = []; seen.add(v0.index)
    while stk:
        x = stk.pop(); comp.append(x.index)
        for e in x.link_edges:
            y = e.other_vert(x)
            if y.index not in seen: seen.add(y.index); stk.append(y)
    if len(comp) >= 40 or any(part.get(i) in ('blade', 'shield', 'cape') for i in comp): continue
    c = sum((me.vertices[i].co for i in comp), Vector()) / len(comp)
    best = None
    for sd in JOINT:
        sx = -1 if sd == 'Right' else 1; A0 = _ph(sd + 'Arm'); A1, A2 = JOINT[sd]; A3 = A2 + (A2 - A1) * 0.9
        for nm, (a, b) in zip(('Arm', 'ForeArm', 'Hand'), ((A0, A1), (A1, A2), (A2, A3))):
            t, d = _proj(c, a, b)
            if nm == 'Arm' and t < 0.2: continue
            if best is None or d < best[0]: best = (d, sd + nm)
    if best and best[0] < ARM_OUT:
        for i in comp: setw(i, [(best[1], 1.0)])
        crumbs += len(comp)
bmd.free(); print('arm crumbs bound', crumbs)
# 텍스처 조각(UV 섬) 단위로 팔과 몸을 맞춘다: 한 섬이 팔과 몸으로 찢어지면 늘어나거나(치마 끈이 손을 따라 떠다님) 갈라진다
gn3 = {g.index: g.name for g in ag.vertex_groups}
def isarm(i):
    gs = me.vertices[i].groups
    return len(gs) and re.search(r'(Left|Right)(Arm|ForeArm|Hand)', gn3[max(gs, key=lambda g: g.weight).group])
fixb = fixa = 0
for vs in isl:
    vs = [i for i in vs if part.get(i) not in ('blade', 'shield', 'cape')]
    if not vs: continue
    na = [i for i in vs if isarm(i)]; nb = [i for i in vs if not isarm(i)]
    if na and len(na) < len(vs) * 0.5 and nb:      # 팔이 아닌 조각: 팔에 묶인 점은 같은 조각의 가장 가까운 몸 점을 따른다
        kd2 = kdtree.KDTree(len(nb))
        for i in nb: kd2.insert(me.vertices[i].co, i)
        kd2.balance()
        for i in na:
            j = kd2.find(me.vertices[i].co)[1]
            setw(i, [(gn3[g.group].replace('mixamorig:', ''), g.weight) for g in me.vertices[j].groups]); fixb += 1
    elif nb and len(na) >= len(vs) * 0.8:              # 팔 조각: 몸에 묶인 점도 가장 가까운 팔 점을 따른다
        kd2 = kdtree.KDTree(len(na))
        for i in na: kd2.insert(me.vertices[i].co, i)
        kd2.balance()
        for i in nb:
            j = kd2.find(me.vertices[i].co)[1]
            setw(i, [(gn3[g.group].replace('mixamorig:', ''), g.weight) for g in me.vertices[j].groups]); fixa += 1
print('uv islands: arm verts back to body', fixb, 'body verts to arm', fixa)
# 마지막으로 팔에 묶인 점을 모두 위치대로 다시 묶는다: 위에서 가까운 점의 가중치를 베껴 오다 팔뚝 높이의 점이 위팔에 묶이기도 했다(팔꿈치를 굽히면 손 옆에 조각이 떠 보임)
final = 0
for sd in JOINT:
    A0 = _ph(sd + 'Arm'); A1, A2 = JOINT[sd]; A3 = A2 + (A2 - A1) * 0.9
    for v in me.vertices:
        if part.get(v.index) in ('blade', 'shield', 'cape') or not len(v.groups): continue
        dn = gn3[max(v.groups, key=lambda g: g.weight).group]
        if not re.search(r'%s(Arm|ForeArm|Hand)' % sd, dn): continue
        (tu, du), (tf, df), (th, dh) = _proj(v.co, A0, A1), _proj(v.co, A1, A2), _proj(v.co, A2, A3)
        k = min((du, 0), (df, 1), (dh, 2))[1]
        if k == 0: ws = [(sd + 'Arm', 1.0)] if tu < 0.85 else [(sd + 'Arm', 1 - (tu - 0.85) / 0.3), (sd + 'ForeArm', (tu - 0.85) / 0.3)]
        elif k == 1:
            if tf < 0.15: ws = [(sd + 'ForeArm', 0.5 + tf / 0.3), (sd + 'Arm', 0.5 - tf / 0.3)]
            elif tf > 0.85 and sd == 'Right': ws = [(sd + 'ForeArm', 1 - (tf - 0.85) / 0.3), (sd + 'Hand', (tf - 0.85) / 0.3)]
            else: ws = [(sd + 'ForeArm', 1.0)]
        else: ws = [('RightHand', 1.0)] if sd == 'Right' else [('LeftForeArm', 1.0)]
        setw(v.index, ws); final += 1
print('arm verts final rebind', final)
# 팔, 손에 묶였지만 본체(팔, 손, 칼, 방패)와 떨어진 덩어리: 손 옆 허리의 가죽 띠, 허리띠 부스러기가 손을 따라 공중에 떠다녔다
# 팔 쪽 점끼리 이어진 덩어리(이음매는 같은 자리 점으로 잇는다)를 나눠, 가장 큰 본체와 칼날 위 조각만 남기고 나머지는 가장 가까운 몸 점의 가중치를 따른다
def armside(i):
    gs = me.vertices[i].groups
    if part.get(i) in ('blade', 'shield'): return 'Right' if part[i] == 'blade' else 'Left'
    if not len(gs): return None
    m = re.match(r'mixamorig:(Left|Right)(Arm|ForeArm|Hand)', gn3[max(gs, key=lambda g: g.weight).group]); return m.group(1) if m else None
bmf = bmesh.new(); bmf.from_mesh(me); bmf.verts.ensure_lookup_table()
sideOf = [armside(i) for i in range(len(me.vertices))]
par = list(range(len(me.vertices)))
def _f(x):
    while par[x] != x: par[x] = par[par[x]]; x = par[x]
    return x
def _u(a, b):
    a, b = _f(a), _f(b)
    if a != b: par[b] = a
for e in bmf.edges:
    a, b = e.verts[0].index, e.verts[1].index
    if sideOf[a] and sideOf[a] == sideOf[b]: _u(a, b)
posk = {}
for i, sd in enumerate(sideOf):
    if not sd: continue
    co = me.vertices[i].co; kk = (sd, round(co.x * 2000), round(co.y * 2000), round(co.z * 2000))
    if kk in posk: _u(posk[kk], i)
    else: posk[kk] = i
bmf.free()
groups = {}
for i, sd in enumerate(sideOf):
    if sd: groups.setdefault(_f(i), []).append(i)
bladeKD = kdtree.KDTree(sum(1 for p in part.values() if p == 'blade'))
for i, p in part.items():
    if p == 'blade': bladeKD.insert(me.vertices[i].co, i)
bladeKD.balance()
body = [v.index for v in me.vertices if not sideOf[v.index] and v.index not in capeset and len(v.groups)]
bodyKD = kdtree.KDTree(len(body))
for i in body: bodyKD.insert(me.vertices[i].co, i)
bodyKD.balance()
mainOf = {}
for r, vs in groups.items():
    sd = sideOf[vs[0]]
    if sd not in mainOf or len(vs) > len(groups[mainOf[sd]]): mainOf[sd] = r
loose = 0
for r, vs in groups.items():
    if r == mainOf[sideOf[vs[0]]]: continue
    if any(part.get(i) in ('blade', 'shield') for i in vs): continue
    ds = sorted(bladeKD.find(me.vertices[i].co)[2] for i in vs)
    if ds[len(ds) // 2] < 0.03: continue   # 칼날 위 조각
    for i in vs:
        j = bodyKD.find(me.vertices[i].co)[1]
        setw(i, [(gn3[g.group].replace('mixamorig:', ''), g.weight) for g in me.vertices[j].groups]); loose += 1
print('loose arm pieces back to body', loose, 'groups', len(groups))
# (치마를 엉덩이와 허벅지 섞기로 따로 묶어 보았으나 치마와 허벅지 살갗 사이가 더 늘어나 되돌렸다, 2026-11-26)
# 허리 아래(치마, 엉덩이) 가중치를 이웃 점과 고르게 편다: knight에서 가장 가까운 점으로 옮긴 가중치는 knight 가랑이, 엉덩이 경계를 그대로 가져와
# 치마 조각 안에서 1cm 사이에 왼, 오른 허벅지 몫이 0.40/0.40 → 0.67/0.18로 뛰었다. 다리를 벌리면 그 한 변만 길게 늘어나 치마 아랫단이 두 다리 사이에 판처럼 걸렸다.
# 이음매로 갈라진 점은 같은 자리끼리 이어 함께 편다. 팔, 손, 칼, 방패, 망토 점은 바꾸지도, 이웃으로 쓰지도 않는다
import numpy as np
SMOOTH_N = int(os.environ.get('SMOOTH_N', '40')); SMOOTH_LO, SMOOTH_HI = (float(x) for x in os.environ.get('SMOOTH_BAND', '0.30,0.56').split(','))
ELB_N = int(os.environ.get('ELB_N', '30')); ELB_R = float(os.environ.get('ELB_R', '0.10'))
def wmatrix():
    gnx = {g.index: g.name for g in ag.vertex_groups}; Wm = np.zeros((len(me.vertices), len(ag.vertex_groups)))
    for v in me.vertices:
        for g in v.groups: Wm[v.index, g.group] = g.weight
    return gnx, Wm / np.maximum(Wm.sum(1, keepdims=True), 1e-9)
def smoothw(ok, a, n, tag):
    """ok: 바꾸고 이웃으로 쓸 점, a: 펴는 세기(0~1). 같은 자리 점(이음매)은 ok끼리만 한 점으로 본다"""
    gnx, Wm = wmatrix(); nV = len(me.vertices)
    key = {}; rep = np.arange(nV)
    for v in me.vertices:
        if not ok[v.index]: continue     # 편 대상끼리만 잇는다(팔, 망토 점과 같은 자리라고 섞으면 0.50/0.50 점이 생겼다)
        kk = (round(v.co.x * 2000), round(v.co.y * 2000), round(v.co.z * 2000))
        if kk in key: rep[v.index] = key[kk]
        else: key[kk] = v.index
    E = np.array([(e.vertices[0], e.vertices[1]) for e in me.edges]); E = rep[E]
    E = E[(E[:, 0] != E[:, 1]) & ok[E[:, 0]] & ok[E[:, 1]]]
    E = np.concatenate([E, E[:, ::-1]])
    am = np.zeros(nV); np.maximum.at(am, rep, a * ok)    # 한 자리의 점 중 하나라도 편 대상이면 대표 점을 편다
    Wr = np.zeros_like(Wm); np.add.at(Wr, rep, Wm); Wr /= np.maximum(Wr.sum(1, keepdims=True), 1e-9)
    for _ in range(n):
        acc = np.zeros_like(Wr); cnt = np.zeros(nV)
        np.add.at(acc, E[:, 0], Wr[E[:, 1]]); np.add.at(cnt, E[:, 0], 1)
        avg = np.where(cnt[:, None] > 0, acc / np.maximum(cnt[:, None], 1), Wr)
        Wr = Wr + (avg - Wr) * (0.5 * am)[:, None]
    chg = 0
    for i in range(nV):
        if not ok[i] or am[rep[i]] <= 0: continue
        setw(i, [(gnx[j].replace('mixamorig:', ''), float(Wr[rep[i], j])) for j in np.nonzero(Wr[rep[i]] > 0.005)[0]]); chg += 1
    print('smoothed', tag, chg)
nV = len(me.vertices); notpart = np.array([part.get(i) not in ('blade', 'shield', 'cape') for i in range(nV)])
if SMOOTH_N:
    gn4, Wm = wmatrix(); nG = Wm.shape[1]
    armG = np.array([bool(re.search(r'(Left|Right)(Arm|ForeArm|Hand)', gn4[j])) for j in range(nG)])
    ok = (Wm.sum(1) > 0) & (Wm[:, armG].sum(1) < 0.01) & notpart   # 팔 몫이 조금이라도 있는 점은 뺀다(손이 허리 높이라 팔 몫이 몸으로 번졌다)
    hz = np.array([v.co.z for v in me.vertices]) / (H * s)
    a = np.clip(np.minimum((hz - (SMOOTH_LO - 0.05)) / 0.05, ((SMOOTH_HI + 0.05) - hz) / 0.05), 0, 1)
    smoothw(ok, a, SMOOTH_N, 'lower body')
# 팔꿈치 둘레: 위팔과 팔뚝 중 가까운 마디로 나눠 묶어, 팔꿈치 뒤쪽에서 1~2cm 사이에 팔뚝 1.00 → 위팔 0.77로 뛰었다(팔을 굽히면 그 변만 늘어남).
# 팔꿈치 관절에서 ELB_R 안쪽, 위팔과 팔뚝에만 묶인 점끼리 가중치를 편다(손, 칼, 방패, 몸 점은 건드리지 않는다)
if ELB_N:
    gn5, Wm = wmatrix(); R = ELB_R * (H * s) / 2.48
    for sd in JOINT:
        ug = [j for j, nm in gn5.items() if nm in ('mixamorig:%sArm' % sd, 'mixamorig:%sForeArm' % sd)]
        d = np.array([(v.co - JOINT[sd][0]).length for v in me.vertices])
        ok = (Wm[:, ug].sum(1) > 0.99) & notpart & (d < R * 2)
        smoothw(ok, np.clip((R * 2 - d) / R, 0, 1), ELB_N, 'elbow ' + sd)
capeV2 = set(capeset)   # (점을 지우지 않으므로 번호 그대로)
bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.01)
bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
bpy.ops.object.vertex_group_normalize_all(lock_active=False)
bpy.ops.object.mode_set(mode='OBJECT')
# 팔(손, 칼, 방패)과 다리를 한꺼번에 잇는 면은 AI 모델의 찌꺼기다: 움직이면 길게 늘어나니 지운다
import bmesh, re
gname = {g.index: g.name for g in ag.vertex_groups}
def chain(v):
    if not len(v.groups): return 'body'
    n = gname[max(v.groups, key=lambda g: g.weight).group]
    m = re.search(r'(Left|Right)(Shoulder|Arm|ForeArm|Hand)', n)
    if m: return 'arm' + m.group(1)
    if re.search(r'(UpLeg|Leg|Foot|Toe)', n): return 'leg'
    return 'body'
ch = [chain(v) for v in me.vertices]
bm = bmesh.new(); bm.from_mesh(me)
bad = [f for f in bm.faces if len({ch[v.index] for v in f.verts} & {'armLeft', 'armRight'}) and 'leg' in {ch[v.index] for v in f.verts}]
bad += [f for f in bm.faces if {'armLeft', 'armRight'} <= {ch[v.index] for v in f.verts}]
# 그 밖의 찌꺼기 면(게임 동작에서 2.5배 넘게 늘어나는 면을 재어 찾음): 머리와 등뼈를 목 없이 바로 잇는 면(말총이 망토 깃에 붙음),
# 망토와 다리를 잇는 면(망토 자락이 허벅지에 붙음), 왼다리와 오른다리를 잇는 면(치마 앞자락이 양다리에 걸침)
gnf = {g.index: g.name.replace('mixamorig:', '') for g in ag.vertex_groups}
dnm = [gnf[max(v.groups, key=lambda g: g.weight).group] if len(v.groups) else '' for v in me.vertices]
headfix = set()
def legside(n):
    m = re.match(r'(Left|Right)(UpLeg|Leg|Foot|Toe)', n); return m.group(1) if m else None
for f in bm.faces:
    ns = [dnm[v.index] for v in f.verts]
    if any(n.startswith('Head') for n in ns) and any(n.startswith('Spine') for n in ns): bad.append(f); continue
    sides = {legside(n) for n in ns} - {None}
    if len(sides) == 2: bad.append(f); continue
    if sides and any(v.index in capeV2 for v in f.verts) and any(not legside(n) for n in ns): bad.append(f)
# 팔과 옆구리(몸통, 엉덩이)를 잇는 면도 찌꺼기다: 팔을 휘두르면 팔과 옆구리 사이에 검은 판이 늘어나 팔이 하나 더 있는 것처럼 보인다(사용자: "팔이 두 개잖아")
# 진짜 어깨 살은 어깨 관절 가까이에서만 몸통과 이어지므로, 어깨 관절에서 12cm 아래부터 지운다
shZ = {sd: (arm.matrix_world @ arm.pose.bones['mixamorig:%sArm' % sd].head).z - 0.12 * (H * s) / 2.48 for sd in ('Left', 'Right')}
for f in bm.faces:
    cs = {ch[v.index] for v in f.verts}
    for sd in ('Left', 'Right'):
        if 'arm' + sd in cs and 'body' in cs and f.calc_center_median().z < shZ[sd]: bad.append(f); break
bm.verts.ensure_lookup_table()
drop = [bm.verts[i] for i, p in part.items() if p == 'drop']
bmesh.ops.delete(bm, geom=list(set(bad)), context='FACES')
drop = [v for v in drop if v.is_valid]
bmesh.ops.delete(bm, geom=drop, context='VERTS'); print('dropped verts', len(drop))
bm.to_mesh(me); bm.free(); me.update()
print('removed faces', len(set(bad)))
# 팔 내린 자세를 쉼 자세로 (메시와 뼈대가 같은 자세에서 묶인다)
bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE'); bpy.ops.pose.select_all(action='SELECT'); bpy.ops.pose.armature_apply(selected=False); bpy.ops.object.mode_set(mode='OBJECT')
# 팔꿈치, 손목 관절을 모델의 실제 자리로 옮긴다(손가락 뼈도 손목과 함께 옮긴다). 게임 동작은 관절 회전값만 쓰므로 팔 길이가 달라도 된다
bpy.ops.object.mode_set(mode='EDIT'); eb = arm.data.edit_bones; inv = arm.matrix_world.inverted()
for sd, (el, wr) in JOINT.items():
    fa, hd = eb['mixamorig:%sForeArm' % sd], eb['mixamorig:%sHand' % sd]
    d = inv @ wr - hd.head
    kids = [b for b in eb if b.name.startswith('mixamorig:%sHand' % sd) and b.name != hd.name]
    for b in kids: b.head = b.head + d; b.tail = b.tail + d
    hd.tail = hd.tail + d; hd.head = inv @ wr
    fa.head = inv @ el; fa.tail = inv @ wr
    eb['mixamorig:%sArm' % sd].tail = inv @ el
bpy.ops.object.mode_set(mode='OBJECT')
for o in list(bpy.context.scene.objects):
    if o.type == 'MESH' and o.name != ag.name: bpy.data.objects.remove(o, do_unlink=True)
mw = ag.matrix_world.copy(); ag.parent = arm; ag.matrix_world = mw
am = ag.modifiers.new('Armature', 'ARMATURE'); am.object = arm
# 텍스처 줄이기
for img in bpy.data.images:
    if img.size[0] > TEXSZ: img.scale(TEXSZ, TEXSZ)
bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); ag.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_animations=False, export_skins=True, export_image_format='JPEG', export_jpeg_quality=85)
print('exported', OUT)
# 확인: 팔을 들어 칼을 휘두르는 자세로 찍어 본다 (칼, 방패, 망토가 제 뼈를 따라가는지)
bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
pb = arm.pose.bones['mixamorig:RightArm']; pb.rotation_mode = 'XYZ'; pb.rotation_euler = (0, 0, math.radians(-70))
pb = arm.pose.bones['mixamorig:LeftArm']; pb.rotation_mode = 'XYZ'; pb.rotation_euler = (0, 0, math.radians(50))
pb = arm.pose.bones['mixamorig:LeftUpLeg']; pb.rotation_mode = 'XYZ'; pb.rotation_euler = (math.radians(-35), 0, 0)
bpy.ops.object.mode_set(mode='OBJECT')
scene = bpy.context.scene
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); scene.collection.objects.link(cam); scene.camera = cam
cam.data.type = 'ORTHO'; cam.data.ortho_scale = H * s * 1.15
scene.render.engine = 'BLENDER_WORKBENCH'; scene.display.shading.color_type = 'TEXTURE'; scene.render.resolution_x = 700; scene.render.resolution_y = 700
for tag, loc, rot in (('front', (0, -10, H * s / 2), (90, 0, 0)), ('side', (10, 0, H * s / 2), (90, 0, 90)), ('back', (0, 10, H * s / 2), (90, 0, 180))):
    cam.location = loc; cam.rotation_euler = tuple(math.radians(a) for a in rot)
    scene.render.filepath = PREV.replace('.png', '_%s.png' % tag); bpy.ops.render.render(write_still=True)
print('done')
