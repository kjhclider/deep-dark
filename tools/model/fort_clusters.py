# Gothic Building 팩: 조각들을 x 위치로 덩어리(건물)로 나눠 덩어리마다 미리보기를 그린다 (fortress 세션)
# blender -b --factory-startup --python fort_clusters.py -- in.glb outdir
import bpy,sys,os,mathutils
a=sys.argv[sys.argv.index('--')+1:];src,out=a[0],a[1];os.makedirs(out,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
M=[o for o in bpy.data.objects if o.type=='MESH']
def bb(o):
  v=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box];return [min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]
B={o.name:bb(o) for o in M}
M.sort(key=lambda o:B[o.name][0][0]);cl=[]
for o in M:
  mn,mx=B[o.name]
  if cl and mn[0]<=cl[-1]['x1']+0.003*100:cl[-1]['x1']=max(cl[-1]['x1'],mx[0]);cl[-1]['o'].append(o)
  else:cl.append({'x1':mx[0],'o':[o]})
sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='TEXTURE'
sc.render.resolution_x=600;sc.render.resolution_y=700
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.type='ORTHO'
for i,c in enumerate(cl):
  S=set(o.name for o in c['o'])
  for o in M:o.hide_render=o.name not in S
  mn=[min(B[n][0][k] for n in S) for k in range(3)];mx=[max(B[n][1][k] for n in S) for k in range(3)]
  print('CL',i,len(S),'min',[round(x,3) for x in mn],'max',[round(x,3) for x in mx])
  ce=mathutils.Vector([(mn[k]+mx[k])/2 for k in range(3)]);R=max(mx[k]-mn[k] for k in range(3))
  cam.data.ortho_scale=R*1.1;cam.data.clip_end=R*20
  v=mathutils.Vector((1,-1,0.5)).normalized();cam.location=ce+v*R*3;cam.rotation_euler=(-v).to_track_quat('-Z','Y').to_euler()
  sc.render.filepath=os.path.join(out,'gb_cl%02d.png'%i);bpy.ops.render.render(write_still=True)
