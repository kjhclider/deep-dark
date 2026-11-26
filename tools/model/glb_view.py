# glb 하나를 통째로 네 각도에서 그려 본다: blender -b --factory-startup --python glb_view.py -- 파일.glb 출력접두어
import bpy,sys,math
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=a[0])
sc=bpy.context.scene;mn=Vector((1e9,)*3);mx=-mn
tri=0
for o in sc.objects:
  if o.type!='MESH':continue
  tri+=sum(len(p.vertices)-2 for p in o.data.polygons)
  for c in o.bound_box:
    w=o.matrix_world@Vector(c);mn=Vector(map(min,mn,w));mx=Vector(map(max,mx,w))
print('bbox',mn,mx,'tris',tri)
sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='TEXTURE'
sc.render.resolution_x=1000;sc.render.resolution_y=800
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam
cam.data.type='ORTHO';cam.data.ortho_scale=(mx-mn).length*0.9;cam.data.clip_end=1e5
c=(mn+mx)/2
for i,(yaw,el) in enumerate([(30,30),(210,30),(120,20),(0,85)]):
  y=math.radians(yaw);e=math.radians(el);d=Vector((math.cos(e)*math.sin(y),-math.cos(e)*math.cos(y),math.sin(e)))
  cam.location=c+d*(mx-mn).length*3;cam.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler()
  sc.render.filepath=f'{a[1]}_{i}.png';bpy.ops.render.render(write_still=True)
