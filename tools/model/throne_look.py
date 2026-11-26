# 탑 원본(또는 결과) 여러 각도로 그려 보기 (throne 세션)
# blender -b --factory-startup --python throne_look.py -- in.glb out_prefix
import bpy,sys,math
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=a[0]);bpy.context.view_layer.update()
sc=bpy.context.scene
ms=[o for o in sc.objects if o.type=='MESH' and len(o.data.polygons)]
ps=[o.matrix_world@v.co for o in ms for v in o.data.vertices]
lo=Vector([min(p[i] for p in ps) for i in range(3)]);hi=Vector([max(p[i] for p in ps) for i in range(3)])
c=(lo+hi)/2;r=(hi-lo).length*0.75
print('BB',lo,hi)
sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='TEXTURE'
sc.render.resolution_x=900;sc.render.resolution_y=700
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam
cam.data.clip_end=r*10;cam.data.clip_start=r/1000
for i,(yaw,pit) in enumerate([(0,15),(90,15),(180,15),(270,15),(45,60)]):
  d=Vector((math.cos(math.radians(yaw))*math.cos(math.radians(pit)),math.sin(math.radians(yaw))*math.cos(math.radians(pit)),-math.sin(math.radians(pit))))
  cam.location=c-d*r*1.3;cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
  sc.render.filepath=a[1]+f'_{i}.png';bpy.ops.render.render(write_still=True)
