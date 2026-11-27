# 요새 모델(원본 glb)을 열어 조각 목록과 미리보기 그림을 만든다 (fortress 세션)
# blender -b --factory-startup --python fort_look.py -- in.glb outdir [이름접두어]
import bpy,sys,os,mathutils,math
a=sys.argv[sys.argv.index('--')+1:];src,out=a[0],a[1];pre=a[2] if len(a)>2 else 'look'
os.makedirs(out,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
mn=[1e9]*3;mx=[-1e9]*3
for o in bpy.data.objects:
  if o.type!='MESH':continue
  bb=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
  omn=[min(v[i] for v in bb) for i in range(3)];omx=[max(v[i] for v in bb) for i in range(3)]
  for i in range(3):mn[i]=min(mn[i],omn[i]);mx[i]=max(mx[i],omx[i])
  print('OBJ',o.name,'par',o.parent.name if o.parent else None,'tris',sum(len(p.vertices)-2 for p in o.data.polygons),'size',[round(omx[i]-omn[i],2) for i in range(3)],'min',[round(x,2) for x in omn],'mats',[m.name for m in o.data.materials])
print('ALL min',mn,'max',mx)
sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='TEXTURE'
sc.render.resolution_x=900;sc.render.resolution_y=700
c=mathutils.Vector([(mn[i]+mx[i])/2 for i in range(3)]);R=max(mx[i]-mn[i] for i in range(3))
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam
cam.data.type='ORTHO';cam.data.ortho_scale=R*1.1;cam.data.clip_end=R*20
for nm,d in [('front',(0,-1,0.0001)),('side',(1,0,0.0001)),('iso',(1,-1,0.8)),('top',(0.0001,0.0001,1))]:
  v=mathutils.Vector(d).normalized();cam.location=c+v*R*3
  cam.rotation_euler=(-v).to_track_quat('-Z','Y').to_euler()
  sc.render.filepath=os.path.join(out,pre+'_'+nm+'.png');bpy.ops.render.render(write_still=True)
