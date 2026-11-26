"""바르고스(Corrupted King in Black Armor with Bone Crown, Sketchfab Pigcraft/s8819296, CC BY)에 knight 뼈대(mixamorig)를 입힌다.
vg_prep.py로 면을 줄이고 정면(-Y)으로 돌린 glb(vg_dec.glb)를 입력으로 쓴다. 묶는 방식은 aegis_rig.py(왕 모델)에서 효과가 있었던 것을 이 모델에 맞춰 옮겼다.
- 모델은 팔을 내린 자세 그대로 묶는다. 게임은 관절 회전값을 통째로 덮어쓰므로 쉼 자세가 T자가 아니어도 동작이 맞다
- 칼은 오른손에 통째로, 망토는 등뼈와 엉덩이, 높은 깃은 가슴과 목을 따른다. 망토, 칼, 깃은 UV 섬(텍스처 조각) 단위로 고른다
- 팔꿈치, 손목은 knight 자리가 아니라 모델 팔의 실제 자리(ELBOW, WRIST)로 옮기고, 팔 점은 위팔, 팔뚝, 손 중 가까운 마디에 다시 묶는다
사용: blender -b --factory-startup --python vg_rig.py -- knight.glb vg_dec.glb out.glb preview.png [텍스처크기]"""
import bpy, sys, math, re, bmesh
from mathutils import Vector, Matrix, kdtree
argv = sys.argv[sys.argv.index('--') + 1:]
KNIGHT, SRC, OUT, PREV = argv[:4]
TEXSZ = int(argv[4]) if len(argv) > 4 else 2048
ARM_DOWN = 73.0          # 팔이 수평에서 아래로 내려간 각도(도)
SHOULDER_H = 0.77        # 어깨 관절 높이(모델 키에 대한 비율)
LEG_OUT = 9.0            # 다리가 바깥으로 벌어진 각도(도)
R_LEG_BACK = 0.0         # 오른다리가 뒤로 빠진 각도(도)
# 팔 관절 자리: (x, y, 높이)를 모델 키에 대한 비율로. x는 머리 가운데 기준(캐릭터 왼쪽 +), y는 앞 -
# 팔꿈치는 팔 보호대 윗단(위로 벌어진 깃) 바로 아래, 손목은 팔 보호대가 끝나고 장갑이 시작하는 곳(정면, 옆 그림에 0.02 격자를 대고 잼)
ELBOW = {'Right': (-0.185, 0.0, 0.665), 'Left': (0.19, 0.0, 0.665)}
WRIST = {'Right': (-0.215, -0.045, 0.515), 'Left': (0.195, -0.045, 0.515)}

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=KNIGHT)
kobjs = list(bpy.context.scene.objects)
arm = next(o for o in kobjs if o.type == 'ARMATURE')
kmeshes = [o for o in kobjs if o.type == 'MESH' and o.name != 'Icosphere']
bpy.ops.import_scene.gltf(filepath=SRC)
ams = [o for o in bpy.context.scene.objects if o not in kobjs and o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in ams: o.select_set(True)
bpy.context.view_layer.objects.active = ams[0]; bpy.ops.object.join(); ag = bpy.context.view_layer.objects.active
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM'); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in list(bpy.context.scene.objects):
    if o.type == 'EMPTY': bpy.data.objects.remove(o, do_unlink=True)
ag.name = 'Vargoth'; me = ag.data
zs = [v.co.z for v in me.vertices]; z0 = min(zs); H = max(zs) - z0
def hr(co): return (co.z - z0) / H
headp = [v.co for v in me.vertices if hr(v.co) > 0.88]
cx = (min(p.x for p in headp) + max(p.x for p in headp)) / 2
me.transform(Matrix.Translation(Vector((-cx, 0, 0))))
print('center x', round(cx, 3), 'H', round(H, 4))
def nc(c): return c.x / H, c.y / H, hr(c)                       # 키에 대한 비율 좌표

# UV 섬: 이 모델(AI 생성, 면 줄임)은 텍스처 이음매마다 점이 갈라져 있어 섬 하나가 곧 따로 떨어진 조각이다
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
bmu.free()
print('uv islands', len(isl))
# 칼: 오른쪽 아래 앞으로 뻗은 칼날, 날밑, 자루. 점 절반이 칼 상자 안인 섬은 통째로 칼(오른손)
def inblade(x, y, h): return x < -0.20 and 0.04 < h < 0.50 and y < 0.0
# 망토: 몸 뒤(y>0.085), 등 가운데 위쪽(어깨 사이, y>0.04), 다리 옆으로 벌어진 자락(|x|>0.24, 높이 45% 아래). 점 80%가 그 안인 섬은 통째로 망토
def inback(x, y, h): return y > 0.085 or (y > 0.04 and abs(x) < 0.15 and 0.42 < h < 0.86) or (abs(x) > 0.24 and h < 0.45 and y > -0.05)
# 높은 깃: 머리 둘레(머리 축에서 6.5cm 넘게)로 서 있는 깃. 머리에 묶이면 고개를 돌릴 때 깃이 등과 찢어진다(머리와 가슴 사이가 가장 많이 늘어났다) → 가슴과 목에
def incollar(x, y, h): return 0.80 < h < 0.93 and abs(x) < 0.13 and math.hypot(x, y + 0.01) > 0.065
# 칼자루와 그 끝(금색 고리): 오른손 뒤 위로 비스듬히 나와 있다(손목 자리보다 13~19cm 뒤). 칼 상자 밖이라 허벅지에 묶여 걸을 때 손과 따로 떠다녔다 → 섬 중심이 이 상자 안이면 칼
def inhilt(x, y, h): return -0.215 < x < -0.17 and 0.0 < y < 0.07 and 0.47 < h < 0.56
part = {}
for vs in isl:
    ns = [nc(me.vertices[i].co) for i in vs]
    if sum(1 for p in ns if inblade(*p)) >= len(vs) * 0.5 or inhilt(*[sum(p[k] for p in ns) / len(ns) for k in range(3)]): lab = 'blade'
    elif sum(1 for p in ns if inback(*p)) >= len(vs) * 0.8: lab = 'cape'
    elif sum(1 for p in ns if incollar(*p)) >= len(vs) * 0.6: lab = 'collar'
    else: continue
    for i in vs: part[i] = lab
capeset = {i for i, p in part.items() if p == 'cape'}
# 등 위쪽과 팔 뒤의 망토 조각 중 일부는 몸에 바짝 붙어 위 기준에 안 걸려 knight 팔 가중치를 받았다. 팔을 들면 따라 올라가 망토에 구멍이 났다
# → 망토에 맞닿고(2mm) 점 60%가 몸 뒤쪽(y>0.03)인 섬을 망토로 넓힌다. 어깨 갑옷(높이 72% 위, |x|>0.11)은 팔을 따라야 하니 뺀다
for it in range(4):
    kdc = kdtree.KDTree(len(capeset))
    for i in capeset: kdc.insert(me.vertices[i].co, i)
    kdc.balance(); grown = 0
    for vs in isl:
        if vs[0] in part: continue
        ns = [nc(me.vertices[i].co) for i in vs]; c = [sum(p[k] for p in ns) / len(ns) for k in range(3)]
        if not (0.45 < c[2] < 0.86 and abs(c[0]) < 0.2 and (c[2] < 0.72 or abs(c[0]) < 0.11)): continue
        if sum(1 for p in ns if p[1] > 0.03) < len(vs) * 0.6: continue
        if min(kdc.find(me.vertices[i].co)[2] for i in vs) > 0.002 * H: continue
        for i in vs: part[i] = 'cape'
        capeset.update(vs); grown += len(vs)
    if not grown: break
    print('cape grown', it, grown)
print('parts', {k: sum(1 for p in part.values() if p == k) for k in ('blade', 'cape', 'collar')})

# 크기와 자리: 어깨 높이를 knight 어깨에, 발을 바닥에, 몸통 앞뒤 가운데를 knight 엉덩이에
def bw(n): return arm.matrix_world @ arm.data.bones[n].head_local
la = bw('mixamorig:LeftArm'); hips = bw('mixamorig:Hips')
s = la.z / (SHOULDER_H * H)
sl = [v.co for v in me.vertices if abs(hr(v.co) - 0.66) < 0.01 and v.co.y < 0.09]
cy = (min(p.y for p in sl) + max(p.y for p in sl)) / 2
me.transform(Matrix.Translation(Vector((0, -cy, -z0))))
me.transform(Matrix.Scale(s, 4))
me.transform(Matrix.Translation(Vector((0, hips.y, 0))))
HS = H * s
def tofinal(x, y, h): return Vector((x * HS, (y * H - cy) * s + hips.y, h * HS))
print('scale', round(s, 4), 'height', round(HS, 3))

# knight 뼈대를 팔 내린 자세로
bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
for side, sgn in (('Left', 1), ('Right', -1)):
    pb = arm.pose.bones['mixamorig:%sArm' % side]; head = pb.head.copy()
    pb.matrix = Matrix.Translation(head) @ Matrix.Rotation(math.radians(ARM_DOWN) * sgn, 4, 'Y') @ Matrix.Translation(-head) @ pb.matrix
    bpy.context.view_layer.update()
for name, axis, deg in (('LeftUpLeg', 'Y', -LEG_OUT), ('RightUpLeg', 'Y', LEG_OUT), ('RightUpLeg', 'X', R_LEG_BACK)):
    pb = arm.pose.bones['mixamorig:' + name]; head = pb.head.copy()
    pb.matrix = Matrix.Translation(head) @ Matrix.Rotation(math.radians(deg), 4, axis) @ Matrix.Translation(-head) @ pb.matrix
    bpy.context.view_layer.update()
bpy.ops.object.mode_set(mode='OBJECT')
def _ph(n): return arm.matrix_world @ arm.pose.bones['mixamorig:' + n].head
for n in ('LeftArm', 'LeftForeArm', 'LeftHand', 'RightArm', 'RightForeArm', 'RightHand', 'Neck', 'Head'):
    p = _ph(n); print('knight %-13s x %.3f y %.3f h %.3f' % (n, p.x / HS, ((p.y - hips.y) / s + cy) / H, p.z / HS))
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
VG = {g.name: g for g in ag.vertex_groups}
def setw(i, ws):
    for g in ag.vertex_groups: g.remove([i])
    for n, w in ws:
        if w > 0: VG['mixamorig:' + n].add([i], w, 'REPLACE')
def capew(i):
    h = me.vertices[i].co.z / HS; t = max(0.0, min(1.0, (0.66 - h) / 0.45))      # 위(0) → 아래(1)
    return [('Spine2', max(0.0, 1 - t * 1.6)), ('Spine1', 0.5 - abs(t - 0.45)), ('Spine', max(0.0, t * 1.3 - 0.3)), ('Hips', max(0.0, t * 1.6 - 0.6))]
for i, p in part.items():
    if p == 'blade': setw(i, [('RightHand', 1.0)])
    elif p == 'cape': setw(i, capew(i))
    elif p == 'collar': setw(i, [('Spine2', 0.6), ('Neck', 0.4)])
FIXED = ('blade', 'cape', 'collar')
# 팔: knight 팔은 이 모델 팔보다 몸 쪽에 붙어 있어, 가까운 점으로 옮긴 가중치가 망토 자락과 옆구리를 팔에, 팔 안쪽을 몸통에 묶었다.
# 팔 뼈(위팔, 팔뚝, 손)를 모델 팔의 실제 자리로 옮기고, 팔에 묶인 점은 세 마디 중 가장 가까운 마디에 다시 묶는다(팔꿈치, 손목 근처는 두 마디에 나눠)
def _proj(p, a, b):
    ab = b - a; t = (p - a).dot(ab) / max(ab.dot(ab), 1e-9); tc = max(0.0, min(1.0, t)); return tc, (p - (a + ab * tc)).length
JOINT = {sd: (tofinal(*ELBOW[sd]), tofinal(*WRIST[sd])) for sd in ('Left', 'Right')}
def segs(sd):
    A0 = _ph(sd + 'Arm'); A1, A2 = JOINT[sd]; return A0, A1, A2, A2 + (A2 - A1) * 0.55
def armws(sd, co):
    A0, A1, A2, A3 = segs(sd)
    (tu, du), (tf, df), (th, dh) = _proj(co, A0, A1), _proj(co, A1, A2), _proj(co, A2, A3)
    k = min((du, 0), (df, 1), (dh, 2))[1]
    if k == 0: ws = [(sd + 'Arm', 1.0)] if tu < 0.85 else [(sd + 'Arm', 1 - (tu - 0.85) / 0.3), (sd + 'ForeArm', (tu - 0.85) / 0.3)]
    elif k == 1:
        if tf < 0.15: ws = [(sd + 'ForeArm', 0.5 + tf / 0.3), (sd + 'Arm', 0.5 - tf / 0.3)]
        elif tf > 0.85: ws = [(sd + 'ForeArm', 1 - (tf - 0.85) / 0.3), (sd + 'Hand', (tf - 0.85) / 0.3)]
        else: ws = [(sd + 'ForeArm', 1.0)]
    else: ws = [(sd + 'Hand', 1.0)] if th > 0.15 else [(sd + 'Hand', 0.5 + th / 0.3), (sd + 'ForeArm', 0.5 - th / 0.3)]
    return ws, k, (tu, tf, th), min(du, df, dh)
gnm = {g.index: g.name for g in ag.vertex_groups}
def dname(v): return gnm[max(v.groups, key=lambda g: g.weight).group] if len(v.groups) else ''
ARM_OUT = 0.14 * HS / 2.48; ARM_IN = 0.08 * HS / 2.48; FA_IN = 0.058 * HS
rearm = 0; tobody = []
# 옆구리로 돌릴 점은 가장 가까운 몸 점(팔, 칼, 망토, 깃이 아닌 점)의 가중치를 따른다. 높이로만 등뼈 가중치를 주었더니 허리띠, 엉덩이 옆에서 엉덩이 점과 맞붙어 늘어났다
bodyIdx = [v.index for v in me.vertices if part.get(v.index) not in FIXED and len(v.groups) and not re.search(r'(Left|Right)(Shoulder|Arm|ForeArm|Hand)', dname(v))]
bodyKD0 = kdtree.KDTree(len(bodyIdx))
for i in bodyIdx: bodyKD0.insert(me.vertices[i].co, i)
bodyKD0.balance()
bodyW0 = {i: [(gnm[g.group].replace('mixamorig:', ''), g.weight) for g in me.vertices[i].groups] for i in bodyIdx}
for sd in ('Left', 'Right'):
    A0, A1, A2, A3 = segs(sd)
    for v in me.vertices:
        if part.get(v.index) in FIXED or not len(v.groups): continue
        dn = dname(v)
        if re.search(r'%sHand.+' % sd, dn): setw(v.index, [(sd + 'Hand', 1.0)]); rearm += 1; continue   # 손가락: 칼자루를 쥔 모양으로 굳어 있어 손에 통째로
        ws, k, (tu, tf, th), d = armws(sd, v.co)
        # 팔뚝은 팔 보호대가 두꺼워(반지름 약 0.05 키) 몸통에 묶인 안쪽 면이 중심선에서 11cm까지 떨어져 있다. 팔뚝 마디이고 몸통 바깥(|x|>0.135 키)이면 FA_IN까지 팔로
        fa_in = k == 1 and d < FA_IN and abs(v.co.x) > 0.135 * HS
        if not (re.search(r'%s(Arm|ForeArm|Hand)$' % sd, dn) or fa_in or (d < ARM_IN and not (k == 0 and tu < 0.2))): continue
        # 팔에 묶였지만 새 팔 중심선에서 멀고 몸 쪽에 있는 점(옆구리 갑옷)은 몸통에
        if d > ARM_OUT and abs(v.co.x) < abs((A0, A1, A2)[k].x) and not (k == 0 and tu < 0.2):
            tobody.append(v.index); continue
        setw(v.index, ws); rearm += 1
for i in tobody: setw(i, bodyW0[bodyKD0.find(me.vertices[i].co)[1]])
print('arm verts reweighted along bones', rearm, 'side armor back to body', len(tobody))
# 팔 둘레의 작은 조각(UV 섬, 점 40개 미만)이 몸에 묶이면 팔을 들 때 제자리에 남아 점처럼 떠 보인다(팔뚝 앞 17점 조각이 15cm 떨어졌다)
# → 중심이 위팔(어깨 쪽 20% 빼고)이나 팔뚝 중심선 가까이(ARM_OUT) 있으면 그 마디에 통째로. 손 마디는 허리띠와 겹쳐 빼고, 손은 아래 섬 규칙에 맡긴다
crumbs = 0
for vs in isl:
    if len(vs) >= 40 or any(part.get(i) in FIXED for i in vs): continue
    c = sum((me.vertices[i].co for i in vs), Vector()) / len(vs)
    best = None
    for sd in ('Left', 'Right'):
        A0, A1, A2, A3 = segs(sd)
        for nm, (a, b) in (('Arm', (A0, A1)), ('ForeArm', (A1, A2))):
            t, d = _proj(c, a, b)
            if nm == 'Arm' and t < 0.2: continue
            if best is None or d < best[0]: best = (d, sd)
    if best and best[0] < ARM_OUT:
        for i in vs: setw(i, armws(best[1], me.vertices[i].co)[0])
        crumbs += len(vs)
print('arm crumbs bound', crumbs)
# UV 섬 단위로 팔과 몸을 맞춘다: 한 섬이 팔과 몸으로 찢어지면 늘어나거나 갈라진다
gn3 = {g.index: g.name for g in ag.vertex_groups}
def isarm(i):
    gs = me.vertices[i].groups
    return len(gs) and re.search(r'(Left|Right)(Arm|ForeArm|Hand)', gn3[max(gs, key=lambda g: g.weight).group])
fixb = fixa = 0
for vs in isl:
    vs = [i for i in vs if part.get(i) not in FIXED]
    if not vs: continue
    na = [i for i in vs if isarm(i)]; nb = [i for i in vs if not isarm(i)]
    if na and len(na) < len(vs) * 0.5 and nb:      # 팔이 아닌 조각: 팔에 묶인 점은 같은 조각의 가장 가까운 몸 점을 따른다
        kd2 = kdtree.KDTree(len(nb))
        for i in nb: kd2.insert(me.vertices[i].co, i)
        kd2.balance()
        for i in na:
            j = kd2.find(me.vertices[i].co)[1]
            setw(i, [(gn3[g.group].replace('mixamorig:', ''), g.weight) for g in me.vertices[j].groups]); fixb += 1
    elif nb and na:                                    # 팔 조각(80% 넘게 팔, 또는 절반 넘게 팔이고 중심이 팔 중심선 가까이): 몸에 묶인 점도 팔로
        sd = 'Left' if 'Left' in gn3[max(me.vertices[na[0]].groups, key=lambda g: g.weight).group] else 'Right'
        c = sum((me.vertices[i].co for i in vs), Vector()) / len(vs)
        if not (len(na) >= len(vs) * 0.8 or armws(sd, c)[3] < ARM_OUT): continue
        for i in nb: setw(i, armws(sd, me.vertices[i].co)[0]); fixa += 1
print('uv islands: arm verts back to body', fixb, 'body verts to arm', fixa)
# 팔에 묶인 점을 모두 위치대로 다시 묶는다(가까운 점의 가중치를 베껴 오다 팔뚝 높이의 점이 위팔에 묶이기도 한다)
final = 0
for sd in ('Left', 'Right'):
    for v in me.vertices:
        if part.get(v.index) in FIXED or not len(v.groups): continue
        if not re.search(r'%s(Arm|ForeArm|Hand)' % sd, dname(v)): continue
        setw(v.index, armws(sd, v.co)[0]); final += 1
print('arm verts final rebind', final)
# 팔, 손에 묶였지만 본체(팔, 손, 칼)와 떨어진 덩어리(허리띠, 옆구리 부스러기, 망토 조각)는 가장 가까운 몸 점을 따른다
def armside(i):
    if part.get(i) == 'blade': return 'Right'
    if part.get(i) in FIXED: return None
    m = re.match(r'mixamorig:(Left|Right)(Arm|ForeArm|Hand)', dname(me.vertices[i])); return m.group(1) if m else None
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
for i, sd in enumerate(sideOf):     # 이음매는 같은 자리 점으로 잇는다
    if not sd: continue
    co = me.vertices[i].co; kk = (sd, round(co.x * 2000), round(co.y * 2000), round(co.z * 2000))
    if kk in posk: _u(posk[kk], i)
    else: posk[kk] = i
bmf.free()
groups = {}
for i, sd in enumerate(sideOf):
    if sd: groups.setdefault(_f(i), []).append(i)
body = [v.index for v in me.vertices if not sideOf[v.index] and part.get(v.index) != 'blade' and len(v.groups)]
bodyKD = kdtree.KDTree(len(body))
for i in body: bodyKD.insert(me.vertices[i].co, i)
bodyKD.balance()
mainOf = {}
for r, vs in groups.items():
    sd = sideOf[vs[0]]
    if sd not in mainOf or len(vs) > len(groups[mainOf[sd]]): mainOf[sd] = r
loose = []
for r, vs in groups.items():
    if r == mainOf[sideOf[vs[0]]] or any(part.get(i) == 'blade' for i in vs): continue
    loose.append(len(vs))
    for i in vs:
        j = bodyKD.find(me.vertices[i].co)[1]
        setw(i, [(gn3[g.group].replace('mixamorig:', ''), g.weight) for g in me.vertices[j].groups])
print('loose arm pieces back to body', len(loose), sum(loose), 'groups', len(groups), 'main', {k: len(groups[v]) for k, v in mainOf.items()})
bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.01)
bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
bpy.ops.object.vertex_group_normalize_all(lock_active=False)
bpy.ops.object.mode_set(mode='OBJECT')
# 찌꺼기 면(AI 모델이 부위 사이를 이어 붙인 면, 움직이면 길게 늘어난다)을 지운다. 점은 지우지 않는다
gname = {g.index: g.name for g in ag.vertex_groups}
def chain(v):
    if not len(v.groups): return 'body'
    n = gname[max(v.groups, key=lambda g: g.weight).group]
    m = re.search(r'(Left|Right)(Shoulder|Arm|ForeArm|Hand)', n)
    if m: return 'arm' + m.group(1)
    if re.search(r'(UpLeg|Leg|Foot|Toe)', n): return 'leg'
    return 'body'
ch = [chain(v) for v in me.vertices]
dnm = [gname[max(v.groups, key=lambda g: g.weight).group].replace('mixamorig:', '') if len(v.groups) else '' for v in me.vertices]
def legside(n):
    m = re.match(r'(Left|Right)(UpLeg|Leg|Foot|Toe)', n); return m.group(1) if m else None
shZ = {sd: _ph(sd + 'Arm').z - 0.12 * HS / 2.48 for sd in ('Left', 'Right')}
bm = bmesh.new(); bm.from_mesh(me)
bad = set(); why = {}
for f in bm.faces:
    cs = {ch[v.index] for v in f.verts}; ns = [dnm[v.index] for v in f.verts]
    r = None
    if cs & {'armLeft', 'armRight'} and 'leg' in cs: r = 'arm-leg'
    elif {'armLeft', 'armRight'} <= cs: r = 'arm-arm'
    elif any(n.startswith('Head') for n in ns) and any(n.startswith('Spine') for n in ns): r = 'head-spine'
    elif len({legside(n) for n in ns} - {None}) == 2: r = 'leg-leg'
    elif {legside(n) for n in ns} - {None} and any(v.index in capeset for v in f.verts) and any(not legside(n) for n in ns): r = 'cape-leg'
    else:
        for sd in ('Left', 'Right'):
            if 'arm' + sd in cs and 'body' in cs and f.calc_center_median().z < shZ[sd]: r = 'arm-side'; break
    if r: bad.add(f); why[r] = why.get(r, 0) + 1
bmesh.ops.delete(bm, geom=list(bad), context='FACES_ONLY')
bm.to_mesh(me); bm.free(); me.update()
print('removed faces', len(bad), why)
# 팔 내린 자세를 쉼 자세로 (메시와 뼈대가 같은 자세에서 묶인다)
bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE'); bpy.ops.pose.select_all(action='SELECT'); bpy.ops.pose.armature_apply(selected=False); bpy.ops.object.mode_set(mode='OBJECT')
# 팔꿈치, 손목 관절을 모델의 실제 자리로 옮긴다(손가락 뼈도 손목과 함께). 게임 동작은 관절 회전값만 쓰므로 팔 길이가 달라도 된다
bpy.ops.object.mode_set(mode='EDIT'); eb = arm.data.edit_bones; inv = arm.matrix_world.inverted()
for sd, (el, wr) in JOINT.items():
    fa, hd = eb['mixamorig:%sForeArm' % sd], eb['mixamorig:%sHand' % sd]
    d = inv @ wr - hd.head
    for b in [b for b in eb if b.name.startswith('mixamorig:%sHand' % sd) and b.name != hd.name]: b.head = b.head + d; b.tail = b.tail + d
    hd.tail = hd.tail + d; hd.head = inv @ wr
    fa.head = inv @ el; fa.tail = inv @ wr
    eb['mixamorig:%sArm' % sd].tail = inv @ el
bpy.ops.object.mode_set(mode='OBJECT')
for o in list(bpy.context.scene.objects):
    if o.type == 'MESH' and o.name != ag.name: bpy.data.objects.remove(o, do_unlink=True)
mw = ag.matrix_world.copy(); ag.parent = arm; ag.matrix_world = mw
am = ag.modifiers.new('Armature', 'ARMATURE'); am.object = arm
for img in bpy.data.images:
    if img.size[0] > TEXSZ: img.scale(TEXSZ, TEXSZ)
bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); ag.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_animations=False, export_skins=True, export_image_format='JPEG', export_jpeg_quality=85)
print('exported', OUT)
# 미리보기(쉼 자세). 동작 확인은 게임 안에서 실제 동작으로 한다(README)
scene = bpy.context.scene
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); scene.collection.objects.link(cam); scene.camera = cam
cam.data.type = 'ORTHO'; cam.data.ortho_scale = HS * 1.15
scene.render.engine = 'BLENDER_WORKBENCH'; scene.display.shading.color_type = 'TEXTURE'; scene.render.resolution_x = 700; scene.render.resolution_y = 700
for tag, loc, rot in (('front', (0, -10, HS / 2), (90, 0, 0)), ('side', (10, 0, HS / 2), (90, 0, 90)), ('back', (0, 10, HS / 2), (90, 0, 180))):
    cam.location = loc; cam.rotation_euler = tuple(math.radians(a) for a in rot)
    scene.render.filepath = PREV.replace('.png', '_%s.png' % tag); bpy.ops.render.render(write_still=True)
print('done')
