# glb 안의 텍스처를 다시 담는다: 최대 크기로 줄이고, 알파가 필요 없으면 JPEG로
# python glb_pack.py 입력.glb 출력.glb 최대크기 [이미지이름:크기,...]
import json,struct,sys,io
from PIL import Image
src,dst,MX=sys.argv[1],sys.argv[2],int(sys.argv[3])
OV={k:int(v) for k,v in (x.split(':') for x in sys.argv[4].split(','))} if len(sys.argv)>4 and sys.argv[4] else {}
d=open(src,'rb').read();l=struct.unpack('<I',d[12:16])[0];j=json.loads(d[20:20+l]);o=20+l;bl=struct.unpack('<I',d[o:o+4])[0];bin_=d[o+8:o+8+bl]
bv=j['bufferViews'];imgv={im['bufferView'] for im in j.get('images',[])}
newbin=bytearray();remap={}
def pad(b):
  while len(b)%4:b.append(0)
for i,v in enumerate(bv):
  raw=bin_[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]
  if i in imgv:
    im=[x for x in j['images'] if x['bufferView']==i][0];I=Image.open(io.BytesIO(raw));I.load()
    t=OV.get(im.get('name'),MX);w,h=I.size
    if max(w,h)>t:I=I.resize((max(1,w*t//max(w,h)),max(1,h*t//max(w,h))),Image.LANCZOS)
    alpha=I.mode in('RGBA','LA') or (I.mode=='P' and 'transparency' in I.info)
    if alpha:
      A=I.convert('RGBA');alpha=A.getchannel('A').getextrema()[0]<250
    bio=io.BytesIO()
    if alpha:I.convert('RGBA').save(bio,'PNG',optimize=True);im['mimeType']='image/png'
    else:I.convert('RGB').save(bio,'JPEG',quality=82);im['mimeType']='image/jpeg'
    raw=bio.getvalue();print(im.get('name'),w,'->',I.size[0],'png' if alpha else 'jpg',len(raw)//1024,'KB')
  pad(newbin);v['byteOffset']=len(newbin);v['byteLength']=len(raw);newbin+=raw
pad(newbin);j['buffers'][0]['byteLength']=len(newbin)
js=json.dumps(j,separators=(',',':')).encode()
while len(js)%4:js+=b' '
out=struct.pack('<III',0x46546C67,2,12+8+len(js)+8+len(newbin))+struct.pack('<II',len(js),0x4E4F534A)+js+struct.pack('<II',len(newbin),0x004E4942)+bytes(newbin)
open(dst,'wb').write(out);print('size',len(out))
