# 조각 하나를 재질마다 다른 색으로 칠해 그린다(창문, 지붕 재질 찾기): blender -b --factory-startup --python city_matview.py -- 파일.glb 조각이름 출력.png
import bpy,sys,math,colorsys
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=a[0])
sc=bpy.context.scene;o=bpy.data.objects[a[1]]
for q in sc.objects:q.hide_render=(q!=o)
for i,s in enumerate(o.material_slots):
  m=s.material;c=colorsys.hsv_to_rgb(i/len(o.material_slots),0.8,1);m.diffuse_color=(*c,1);print('mat',i,m.name,c)
sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL'
sc.render.resolution_x=900;sc.render.resolution_y=600
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=max(o.dimensions)*1.4
d=Vector((0.6,-1,0.5)).normalized();c=Vector((0,0,o.dimensions.z/2));o.location=(0,0,0);cam.location=c+d*200;cam.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler()
sc.render.filepath=a[2];bpy.ops.render.render(write_still=True)
