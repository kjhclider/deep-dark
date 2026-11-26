"""왕궁 시장 노점과 소품을 시장 팩(medieval_market_asset_pack.glb, vmatthew, CC BY)에서 골라 작은 glb 하나로 만든다.
사용: blender -b --factory-startup --python market_build.py -- medieval_market_asset_pack.glb market.glb preview_prefix

나오는 노드(게임 좌표, 미터, 바닥 가운데가 원점):
- stall: 노점 틀(판자 계산대, 기둥). stall_cloth: 천막(흑백으로 바꿔 게임에서 노점마다 색을 곱한다)
- goods_a(채소, 과일), goods_b(병, 항아리), goods_c(채소 다른 배치): 계산대 위 물건. stall과 같은 원점, 같은 크기
- prop_barrel, prop_boxes, prop_sacks, prop_pots, prop_bucket: 노점 옆에 두는 소품
천막 앞뒤 방향: 계산대가 앞뒤 대칭이라 게임 앞(+z)이 어느 쪽이어도 된다. 긴 쪽이 x."""
import bpy, sys, math
import numpy as np
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index('--') + 1:]
IN, OUT = argv[0], argv[1]
PREV = argv[2] if len(argv) > 2 else None
S_STALL = 0.62   # 계산대 윗면 높이 2.08 → 1.29m (지금 코드 노점 1.35m)
S_PROP = 0.45    # 통 높이 2.28 → 1.03m

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=IN)
scene = bpy.context.scene

def meshes_of(parent_names):
    out = []
    for o in scene.objects:
        if o.type != 'MESH': continue
        p = o.parent.name if o.parent else ''
        if any(p == n or (n.endswith('*') and p.startswith(n[:-1])) for n in parent_names): out.append(o)
    return out

# 계산대 위 물건 묶음(부모 이름). 원본 배치 그대로가 goods_a
ITEMS = {
    'apples': ['Wooden Crate', 'Apple*'],
    'carrots': ['Wooden Crate.003', 'Carrot*'],
    'shrooms': ['Wooden Crate.001', 'Shroom*'],
    'melons': ['Melon', 'Melon2'],
    'bottles': ['Wooden Crate.002', 'Bottle1', 'Bottle2', 'Bottle3'],
    'pots': ['Pottery1', 'Pottery2', 'Sack2.001'],
}
GOODS = {
    'goods_a': [('apples', 0, 0, 0), ('carrots', 0, 0, 0), ('melons', 0, 0, 0), ('shrooms', 0, 0, 0), ('pots', 0, 0, 0)],
    'goods_b': [('pots', 0, 0, 0), ('bottles', -3.6, 0.2, -0.23), ('melons', 0.4, 0, 0), ('shrooms', 0.4, 0, 0)],
    'goods_c': [('carrots', -0.9, 0, 0), ('apples', 0.9, 0, 0), ('melons', 0, 0, 0), ('shrooms', 0, 0, 0), ('pots', 3.8, 0, 0)],
}
PROPS = {
    'prop_barrel': ['Barrel1'],
    'prop_boxes': ['Box1', 'Box2', 'Box3'],
    'prop_sacks': ['Sack1', 'Sack2'],
    'prop_pots': ['Pottery3', 'Pottery4'],
    'prop_bucket': ['Bucket'],
}
# 면 줄이기 비율(재질 이름 앞부분)
DEC = {'Apple': 0.35, 'Carrot': 0.45, 'Shroom': 0.35, 'Melon': 0.5, 'Pottery': 0.35, 'Bottle': 0.45,
       'Wood_Barrel': 0.3, 'Metal_Barrel': 0.4, 'Plug_Barrel': 0.5, 'Metal': 0.35, 'Wood': 0.4, 'Sack1': 0.45, 'Sack2': 0.45}

stall_src = meshes_of(['Stall'])
st_planks = [o for o in stall_src if 'Planks' in o.name][0]
bb = [st_planks.matrix_world @ Vector(c) for c in st_planks.bound_box]
ORG = Vector(((min(v.x for v in bb) + max(v.x for v in bb)) / 2, (min(v.y for v in bb) + max(v.y for v in bb)) / 2, min(v.z for v in bb)))
print('stall origin', ORG)

def build(name, srcs, offs, org, scale):
    """srcs의 복사본을 offs만큼 옮겨 하나로 합치고 org를 원점으로, scale배로."""
    new = []
    for o, off in zip(srcs, offs):
        c = o.copy(); c.data = o.data.copy(); scene.collection.objects.link(c)
        mw = o.matrix_world.copy(); c.parent = None; c.matrix_world = mw
        new.append((c, off))
    bpy.ops.object.select_all(action='DESELECT')
    for c, off in new:
        c.select_set(True)
    bpy.context.view_layer.objects.active = new[0][0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for c, off in new:
        c.data.transform(Matrix.Translation(Vector(off)))
        mat = c.data.materials[0].name if c.data.materials else ''
        r = next((v for k, v in DEC.items() if mat.startswith(k)), None)
        if r and len(c.data.polygons) > 60:
            bpy.context.view_layer.objects.active = c
            m = c.modifiers.new('dec', 'DECIMATE'); m.ratio = r
            bpy.ops.object.modifier_apply(modifier='dec')
    bpy.ops.object.select_all(action='DESELECT')
    for c, off in new: c.select_set(True)
    bpy.context.view_layer.objects.active = new[0][0]
    if len(new) > 1: bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = name; ob.data.name = name
    ob.data.transform(Matrix.Scale(scale, 4) @ Matrix.Translation(-org))
    ob.location = (0, 0, 0)
    print('built', name, len(ob.data.polygons), 'faces')
    return ob

outs = []
outs.append(build('stall', [o for o in stall_src if 'Fabric' not in o.name], [(0, 0, 0)] * 3, ORG, S_STALL))
outs.append(build('stall_cloth', [o for o in stall_src if 'Fabric' in o.name], [(0, 0, 0)], ORG, S_STALL))
for g, lst in GOODS.items():
    srcs, offs = [], []
    for it, dx, dy, dz in lst:
        ms = meshes_of(ITEMS[it]); srcs += ms; offs += [(dx, dy, dz)] * len(ms)
    outs.append(build(g, srcs, offs, ORG, S_STALL))
for p, names in PROPS.items():
    ms = meshes_of(names)
    pts = [o.matrix_world @ Vector(c) for o in ms for c in o.bound_box]
    org = Vector(((min(v.x for v in pts) + max(v.x for v in pts)) / 2, (min(v.y for v in pts) + max(v.y for v in pts)) / 2, min(v.z for v in pts)))
    outs.append(build(p, ms, [(0, 0, 0)] * len(ms), org, S_PROP))

keep = set(o.name for o in outs)
for o in list(scene.objects):
    if o.name not in keep: bpy.data.objects.remove(o, do_unlink=True)
for b in (bpy.data.meshes,):
    for m in list(b):
        if m.users == 0: b.remove(m)

# 재질: 거칠기/금속 텍스처는 빼고(값으로), 색과 노멀만 남긴다. 텍스처 크기를 줄인다. 투명 섞기를 끈다.
used = set()
for o in outs:
    for m in o.data.materials:
        if m: used.add(m)
def tex_size(mname):
    if mname.startswith('Stall'): return 1024
    if mname.startswith(('Apple', 'Carrot', 'Shroom')): return 256
    return 512
for m in used:
    nt = m.node_tree; bs = [n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'][0]
    metal = m.name.startswith('Metal') or 'Metal' in m.name
    sep = [n for n in nt.nodes if n.type == 'SEPARATE_COLOR']
    dead = []
    for n in sep:
        dead += [l.from_node for l in n.inputs[0].links] + [n]
    for n in dead:
        nt.nodes.remove(n)
    for l in list(bs.inputs['Alpha'].links): nt.links.remove(l)
    bs.inputs['Alpha'].default_value = 1.0
    bs.inputs['Roughness'].default_value = 0.55 if metal else 0.88
    bs.inputs['Metallic'].default_value = 0.5 if metal else 0.0
    try: m.surface_render_method = 'DITHERED'
    except Exception: pass
    try: m.blend_method = 'OPAQUE'
    except Exception: pass
    sz = tex_size(m.name)
    for n in nt.nodes:
        if n.type == 'TEX_IMAGE' and n.image:
            im = n.image
            is_nrm = any(l.to_node.type == 'NORMAL_MAP' for l in n.outputs[0].links)
            s = sz // 2 if is_nrm else sz
            if im.size[0] > s: im.scale(s, s)
            if m.name == 'Stall_Fabric' and not is_nrm:
                px = np.array(im.pixels[:], dtype=np.float32).reshape(-1, 4)
                lum = px[:, 0] * 0.2126 + px[:, 1] * 0.7152 + px[:, 2] * 0.0722
                # 빨간 줄(어두움) → 0.42, 흰 줄 → 0.95: 게임에서 노점 색을 곱해 같은 색 두 톤 줄무늬
                lo, hi = np.percentile(lum, 8), np.percentile(lum, 92)
                t = np.clip((lum - lo) / max(1e-4, hi - lo), 0, 1)
                g = 0.42 + t * 0.53
                g = g * (0.85 + 0.15 * np.clip(lum / max(hi, 1e-4), 0, 1.2))   # 결(주름, 얼룩) 조금 남기기
                px[:, 0] = g; px[:, 1] = g; px[:, 2] = g
                im.pixels[:] = px.reshape(-1).tolist()
            im.pack()

if PREV:
    sc = scene; sc.render.engine = 'BLENDER_WORKBENCH'; sc.display.shading.color_type = 'TEXTURE'; sc.display.shading.light = 'STUDIO'
    sc.render.resolution_x = 1000; sc.render.resolution_y = 650
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
    # 미리보기 배치: 노점 셋을 나란히, 소품은 앞에
    dup = []
    lay = {'stall': [(-3.2, 0), (0, 0), (3.2, 0)], 'stall_cloth': [(-3.2, 0), (0, 0), (3.2, 0)], 'goods_a': [(-3.2, 0)], 'goods_b': [(0, 0)], 'goods_c': [(3.2, 0)],
           'prop_barrel': [(-4, -2.2)], 'prop_boxes': [(-2.4, -2.2)], 'prop_sacks': [(-0.6, -2.2)], 'prop_pots': [(1, -2.2)], 'prop_bucket': [(2.4, -2.2)]}
    for o in outs:
        for (x, y) in lay.get(o.name, []):
            d = o.copy(); sc.collection.objects.link(d); d.location = (x, y, 0); dup.append(d)
        o.hide_render = True
    tgt = Vector((0, -0.6, 1.2))
    for nm, d in (('front', Vector((0, -1, 0.45))), ('side', Vector((0.8, -0.5, 0.5))), ('back', Vector((0, 1, 0.4)))):
        cam.location = tgt + d.normalized() * 11; cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = PREV + '_' + nm + '.png'; bpy.ops.render.render(write_still=True)
    for d in dup: bpy.data.objects.remove(d, do_unlink=True)
    for o in outs: o.hide_render = False

kw = dict(filepath=OUT, export_format='GLB', export_apply=True, export_animations=False, export_image_format='JPEG', use_selection=False)
props = bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
for k in ('export_jpeg_quality', 'export_image_quality'):
    if k in props: kw[k] = 82
bpy.ops.export_scene.gltf(**kw)
print('exported', OUT)
