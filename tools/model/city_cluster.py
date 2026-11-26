# city_look.py 결과(조각 상자)를 겹침으로 묶어 건물 덩어리 목록을 만든다
# python city_cluster.py city_parts.json 여유 결과.json [재질글자(제외)]
import json,sys,collections
P=json.load(open(sys.argv[1]));M=float(sys.argv[2])
par=list(range(len(P)))
def f(i):
  while par[i]!=i:par[i]=par[par[i]];i=par[i]
  return i
G=collections.defaultdict(list);C=4.0
for i,p in enumerate(P):
  for gx in range(int((p['mn'][0]-M)//C),int((p['mx'][0]+M)//C)+1):
    for gy in range(int((p['mn'][1]-M)//C),int((p['mx'][1]+M)//C)+1):G[(gx,gy)].append(i)
def ov(a,b):return all(a['mn'][k]-M<=b['mx'][k] and b['mn'][k]-M<=a['mx'][k] for k in range(3))
for cell,L in G.items():
  if len(L)>3000:print('big cell',cell,len(L))
  for x in range(len(L)):
    for y in range(x+1,len(L)):
      a,b=L[x],L[y]
      if f(a)!=f(b) and ov(P[a],P[b]):par[f(a)]=f(b)
cl=collections.defaultdict(list)
for i in range(len(P)):cl[f(i)].append(i)
out=[]
for k,L in cl.items():
  mn=[min(P[i]['mn'][j] for i in L) for j in range(3)];mx=[max(P[i]['mx'][j] for i in L) for j in range(3)]
  mats=collections.Counter();n=0
  for i in L:mats[P[i]['mat']]+=P[i]['n'];n+=P[i]['n']
  out.append({'parts':L,'n':n,'mn':mn,'mx':mx,'mats':dict(mats)})
out.sort(key=lambda c:-c['n'])
json.dump(out,open(sys.argv[3],'w'))
print(len(out),'clusters')
for i,c in enumerate(out[:60]):print(i,c['n'],[round(v) for v in c['mn']],[round(v) for v in c['mx']],sorted(c['mats'].items(),key=lambda x:-x[1])[:3])
