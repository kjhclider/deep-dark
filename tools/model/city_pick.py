# 도시 조각 고르기: city_look/city_cluster 결과에서 쓸 조각(집, 탑, 분수 등)을 골라 city_pieces.json을 만든다
# python city_pick.py 작업폴더
import json,sys,math,os
D=sys.argv[1];J=lambda n:json.load(open(os.path.join(D,n)))
P=J('city_parts.json');H=J('house_cl.json');PR=J('prop_cl.json');W=J('wall_parts.json');HP=J('house_parts.json');PP=J('prop_parts.json')
out={}
def add(name,idx):
  ps=[P[i] for i in idx];mn=[min(p['mn'][k] for p in ps) for k in range(3)];mx=[max(p['mx'][k] for p in ps) for k in range(3)]
  out[name]={'parts':[[p['o'],p['f0']] for p in ps],'c':[(mn[0]+mx[0])/2,(mn[1]+mx[1])/2,mn[2]],'size':[mx[k]-mn[k] for k in range(3)],'n':sum(p['n'] for p in ps)}
HOUSES=[60,63,59,56,54,50,44,33,41,46,38,47]
for k,ci in enumerate(HOUSES):add(f'house{k}',[HP[i]['i'] for i in H[ci]['parts']])
def circ(name,src,cx,cy,r,z0=-99):
  add(name,[p['i'] for p in src if math.hypot((p['mn'][0]+p['mx'][0])/2-cx,(p['mn'][1]+p['mx'][1])/2-cy)<r and p['mn'][2]>=z0])
circ('tower',W,-209,-11,9.6)
circ('gatetower',W,-161,63,8.5)
circ('fountain',PP,-125,35,6.5)
circ('well',PP,-76,-22,2.6)
circ('bigtree',PP,34,11,11.5)
circ('tree',PP,79,45,5)
for n,v in out.items():print(n,v['n'],[round(x,1) for x in v['size']])
json.dump(out,open(os.path.join(D,'city_pieces.json'),'w'))
