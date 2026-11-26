# H1 도시 모델을 Workbench로 여러 각도에서 그려 본다(조각 고르기용)
# blender -b --factory-startup --python city_render.py -- 원본.glb 출력접두어 "cx,cy,size,yawdeg,elevdeg;..."
import bpy,sys,math
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:];src,pre,views=a[0],a[1],a[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
sc=bpy.context.scene
sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='TEXTURE'
sc.render.resolution_x=1400;sc.render.resolution_y=1000
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam
cam.data.type='ORTHO';cam.data.clip_end=5000
for i,v in enumerate(views.split(';')):
  cx,cy,size,yaw,el=map(float,v.split(','))
  cam.data.ortho_scale=size
  yaw=math.radians(yaw);el=math.radians(el);d=1500
  # 블렌더 가져오기 뒤 위가 +Z, 원본 xy는 블렌더 (x,-z)->... 그냥 블렌더 좌표 x,y 사용
  dirv=Vector((math.cos(el)*math.sin(yaw),-math.cos(el)*math.cos(yaw),math.sin(el)))
  tgt=Vector((cx,cy,5));cam.location=tgt+dirv*d
  cam.rotation_euler=(-dirv).to_track_quat('-Z','Y').to_euler()
  sc.render.filepath=f'{pre}_{i}.png';bpy.ops.render.render(write_still=True)
