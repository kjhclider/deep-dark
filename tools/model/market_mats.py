"""시장 팩 재질마다 쓰는 텍스처(종류, 크기)를 찍는다. 사용: blender -b --factory-startup --python market_mats.py -- pack.glb"""
import bpy, sys
argv = sys.argv[sys.argv.index('--') + 1:]
bpy.ops.import_scene.gltf(filepath=argv[0])
for m in bpy.data.materials:
    if not m.use_nodes: continue
    out = []
    for n in m.node_tree.nodes:
        if n.type == 'TEX_IMAGE' and n.image:
            to = [l.to_socket.name + '@' + l.to_node.type for l in n.outputs[0].links]
            out.append('%s(%dx%d)->%s' % (n.image.name, n.image.size[0], n.image.size[1], ','.join(to)))
    bs = [n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED']
    col = tuple(round(x, 2) for x in bs[0].inputs['Base Color'].default_value) if bs else None
    print('MAT|%s|%s|%s|%s' % (m.name, col, m.blend_method if hasattr(m,'blend_method') else '', ' '.join(out)))
