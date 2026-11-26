# 만든 glb의 조각을 골라 나란히 놓고 그려 본다
# blender -b --factory-startup --python city_prev.py -- 파일.glb 미리보기.png "이름,이름,..." [yaw도]
import bpy,sys,math
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:];src,prev,names=a[0],a[1],a[2].split(',');yaw=math.radians(float(a[3]) if len(a)>3 else 20)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
sc=bpy.context.scene
for o in sc.objects:o.hide_render=True
x=0;H=1
for n in names:
  o=bpy.data.objects.get(n)
  if not o:print('no',n);continue
  o.hide_render=False
  for c in o.children_recursive:c.hide_render=False
  o.location=(x+o.dimensions.x/2,0,0);x+=o.dimensions.x+4;H=max(H,o.dimensions.z)
sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='TEXTURE'
sc.render.resolution_x=1600;sc.render.resolution_y=int(1600*max(0.35,H*1.3/x))
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam
cam.data.type='ORTHO';cam.data.ortho_scale=x*1.05;cam.data.clip_end=5000
d=Vector((math.sin(yaw),-math.cos(yaw),0.45)).normalized();cam.location=Vector((x/2,0,H*0.4))+d*800;cam.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler()
sc.render.filepath=prev;bpy.ops.render.render(write_still=True)
