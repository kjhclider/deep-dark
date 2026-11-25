import json,re,glob,sys
allv={o['id']:o for o in json.load(open('/home/claude/tr/all.json'))}
def sig(t): return re.findall(r'</?[a-z0-9]+|data-a="[^"]*"|\n',t)
bad=0;n=0
for f in sorted(glob.glob('/home/claude/tr/o[0-9]*.json')):
    d=json.load(open(f))
    for k,v in d.items():
        n+=1
        if v is None: continue
        src=allv[int(k)]['v']
        if sig(src)!=sig(v): bad+=1;print(f[-8:],k,'SIG',sig(src)[:6],sig(v)[:6])
        if re.search(r'[가-힣]',v): print(f[-8:],k,'KOREAN LEFT',v[:40])
print('checked',n,'bad',bad)
