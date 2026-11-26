# 큰 glb의 JSON만 읽어 조각, 재질, 텍스처 크기를 본다
import json,struct,sys
f=open(sys.argv[1],'rb');h=f.read(12);l,t=struct.unpack('<II',f.read(8));j=json.loads(f.read(l))
print('nodes',len(j['nodes']),'meshes',len(j['meshes']),'mats',len(j.get('materials',[])),'images',len(j.get('images',[])))
acc=j['accessors']
for i,n in enumerate(j['nodes']):
  print(i,n.get('name'),'mesh' ,n.get('mesh'),'ch',n.get('children'),'t',n.get('translation'),'s',n.get('scale'),'r',n.get('rotation'),'m',n.get('matrix'))
for i,m in enumerate(j['meshes']):
  tris=0;mats=[]
  for p in m['primitives']:
    tris+=acc[p['indices']]['count']//3 if 'indices' in p else 0;mats.append(p.get('material'))
    mn=acc[p['attributes']['POSITION']].get('min');mx=acc[p['attributes']['POSITION']].get('max')
  print('mesh',i,m.get('name'),'tris',tris,'mats',mats,'min',mn,'max',mx)
for i,m in enumerate(j.get('materials',[])):print('mat',i,m.get('name'),json.dumps({k:v for k,v in m.items() if k!='name'})[:300])
bv=j['bufferViews']
for i,im in enumerate(j.get('images',[])):print('img',i,im.get('name'),im.get('mimeType'),bv[im['bufferView']]['byteLength']//1024,'KB')
