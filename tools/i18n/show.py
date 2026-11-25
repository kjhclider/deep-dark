import json,sys
b=json.load(open(f'/home/claude/tr/b{int(sys.argv[1]):02d}.json'))
for o in b:
    v=o['v']
    if len(v)<28 or o['k']=='T':
        c=o['c'].replace('⟦'+v+'⟧','⟦⟧');a=c.find('⟦⟧');c=c[max(0,a-32):a+30]
        print(f"{o['id']}|{v}|| {c}")
    else: print(f"{o['id']}|{v}")
