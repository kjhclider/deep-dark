# 언덕 UV 살피기 (throne 세션): 원본과 줄인 뒤의 UV 범위, 면적 대비 UV 늘어남
import bpy,sys,math
a=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=a[0]);bpy.context.view_layer.update()
for o in bpy.data.objects:
  if o.type!='MESH' or o.name not in a[1].split(','):continue
  me=o.data;uv=me.uv_layers.active.data;us=[];vs=[];rat=[]
  for p in me.polygons:
    L=[uv[i].uv for i in p.loop_indices];us+= [x.x for x in L];vs+=[x.y for x in L]
    if len(L)>=3:
      ua=abs((L[1].x-L[0].x)*(L[2].y-L[0].y)-(L[2].x-L[0].x)*(L[1].y-L[0].y))/2
      if p.area>1e-9:rat.append(ua/p.area)
  rat.sort();n=len(rat)
  print('UV',o.name,len(me.polygons),'u',round(min(us),2),round(max(us),2),'v',round(min(vs),2),round(max(vs),2),'ratio p10/50/90',[ '%.3g'%rat[int(n*q)] for q in (0.1,0.5,0.9)],'zero',sum(1 for r in rat if r<rat[n//2]*0.02))
im=bpy.data.images.get('Image_3')
if im:im.filepath_raw=a[2];im.file_format='PNG';im.save();print('SAVED')
