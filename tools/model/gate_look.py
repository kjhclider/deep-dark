# blender -b --factory-startup --python gate_look.py -- in.glb outdir
# 정문 모델 살펴보기: glb를 읽어 조각마다 크기를 적고 앞(f), 옆(s), 위(t)에서 그린 그림을 남긴다(outdir은 절대 경로)
import bpy,sys,os,math
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:];src,out=a[0],a[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='TEXTURE'
sc.render.resolution_x=sc.render.resolution_y=512
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.type='ORTHO'
meshes=[o for o in sc.objects if o.type=='MESH']
def bb(o):
  ps=[o.matrix_world@Vector(c) for c in o.bound_box];return Vector([min(p[i] for p in ps) for i in range(3)]),Vector([max(p[i] for p in ps) for i in range(3)])
for o in meshes:
  lo,hi=bb(o);print('PART',o.name,len(o.data.polygons),'faces',[round(x,2) for x in lo],[round(x,2) for x in hi])
for o in meshes:
  for m in meshes:m.hide_render=(m!=o)
  lo,hi=bb(o);c=(lo+hi)/2;s=max(hi-lo)
  if s>1000:continue
  for tag,d in (('f',Vector((0,1,0))),('s',Vector((-1,0,0))),('t',Vector((0,0,-1)))):
    cam.location=c-d*s*3;cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=s*1.1;cam.data.clip_end=s*10
    sc.render.filepath=os.path.join(out,f'{o.name.split("_")[0]}_{tag}.png');bpy.ops.render.render(write_still=True)
for m in meshes:m.hide_render=False

