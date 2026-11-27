# 원본 glb에서 이름(부모 이름 포함)으로 고른 조각만 남겨 미리보기 그림을 만든다 (fortress 세션)
# blender -b --factory-startup --python fort_pick.py -- in.glb out.png 이름1,이름2,...   (이름 앞부분이 같으면 고른다. '-'로 시작하면 뺀다)
import bpy,sys,os,mathutils
a=sys.argv[sys.argv.index('--')+1:];src,out,keys=a[0],a[1],a[2].split(',')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
inc=[k for k in keys if not k.startswith('-')];exc=[k[1:] for k in keys if k.startswith('-')]
def nm(o):
  s=[o.name];p=o.parent
  while p:s.append(p.name);p=p.parent
  return s
keep=[]
for o in list(bpy.data.objects):
  if o.type!='MESH':continue
  ns=nm(o);ok=any(n.startswith(k) for n in ns for k in inc) and not any(n.startswith(k) for n in ns for k in exc)
  if ok:keep.append(o)
  else:bpy.data.objects.remove(o)
mn=[1e9]*3;mx=[-1e9]*3
for o in keep:
  for c in o.bound_box:
    v=o.matrix_world@mathutils.Vector(c)
    for i in range(3):mn[i]=min(mn[i],v[i]);mx[i]=max(mx[i],v[i])
print('PICK',len(keep),'min',[round(x,2) for x in mn],'max',[round(x,2) for x in mx])
sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='TEXTURE'
sc.render.resolution_x=900;sc.render.resolution_y=700
c=mathutils.Vector([(mn[i]+mx[i])/2 for i in range(3)]);R=max(mx[i]-mn[i] for i in range(3))
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));sc.collection.objects.link(cam);sc.camera=cam
cam.data.type='ORTHO';cam.data.ortho_scale=R*1.1;cam.data.clip_end=R*20
for nm2,d in [('iso',(1,-1,0.7)),('iso2',(-1,1,0.5))]:
  v=mathutils.Vector(d).normalized();cam.location=c+v*R*3
  cam.rotation_euler=(-v).to_track_quat('-Z','Y').to_euler()
  sc.render.filepath=out.replace('.png','_'+nm2+'.png');bpy.ops.render.render(write_still=True)
