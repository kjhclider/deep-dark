# src.blend에서 조각 하나씩 미리보기 (workbench, 텍스처색)
import bpy,sys,os,mathutils,math
a=sys.argv[sys.argv.index('--')+1:];out=a[0];names=a[1:]
sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.color_type='TEXTURE';sc.display.shading.light='STUDIO'
sc.render.resolution_x=640;sc.render.resolution_y=480
cam=bpy.data.cameras.new('c');co=bpy.data.objects.new('c',cam);sc.collection.objects.link(co);sc.camera=co
for o in bpy.data.objects:
  if o.type=='MESH':o.hide_render=True
for key in names:
  obs=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(key)]
  for o in obs:o.hide_render=False
  pts=[o.matrix_world@mathutils.Vector(c) for o in obs for c in o.bound_box]
  c=sum(pts,mathutils.Vector())/len(pts);r=max((p-c).length for p in pts)
  for k,(az,el) in enumerate([(-35,35),(145,35)]):
    d=mathutils.Vector((math.cos(math.radians(el))*math.sin(math.radians(az)),-math.cos(math.radians(el))*math.cos(math.radians(az)),math.sin(math.radians(el))))
    co.location=c+d*r*3.4;co.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler()
    sc.render.filepath=os.path.join(out,f'pv_{key}_{k}.png');bpy.ops.render.render(write_still=True)
  for o in obs:o.hide_render=True
