import json,re,glob,subprocess,sys
SRC=sys.argv[1] if len(sys.argv)>1 else '/home/claude/deep-dark/index.html'
OUT=sys.argv[2] if len(sys.argv)>2 else '/home/claude/deep-dark/en.html'
allv={o['id']:o['v'] for o in json.load(open('/home/claude/tr/all.json'))}
tr={}
for f in sorted(glob.glob('/home/claude/tr/o[0-9]*.json')):
    for k,v in json.load(open(f)).items():
        if v is not None: tr[allv[int(k)]]=v
VER=re.compile(r'v0\.9\.\d+')
def norm(t): return VER.sub('v0.9.X',t)
trn={norm(k):v for k,v in tr.items()}
ov=json.load(open('/home/claude/tr/overrides.json')) if glob.glob('/home/claude/tr/overrides.json') else {}
subprocess.run(['node','/tmp/tools/ext.js',SRC],check=True,capture_output=True)
segs=json.load(open('/tmp/segs.json'))
s=open(SRC,encoding='utf-8').read()
u2p=[];
for pi,ch in enumerate(s):
    u2p.append(pi)
    if ord(ch)>0xFFFF: u2p.append(pi)
u2p.append(len(s))
for x in segs: x['s']=u2p[x['s']];x['e']=u2p[x['e']]
miss=[];out=s;n=0
skipr=[]
for fn in ['function fixJosa','function touchTxt']:
    a=s.find(fn);b=s.find('\n}',a);skipr.append((a,b))
segs=[x for x in segs if not any(a<=x['s']<b for a,b in skipr)]
for x in sorted(segs,key=lambda x:-x['s']):
    v=x['v']
    pre=s[max(0,x['s']-40):x['s']]
    t=None
    for o in ov.get(v,[]):
        if o['ctx'] in pre: t=o['en'];break
    if t is None: t=trn.get(norm(v))
    if t is None: miss.append(v);continue
    m=VER.search(v)
    if m: t=VER.sub(m.group(0),t)
    if x['k']=='L':
        lit=json.dumps(t,ensure_ascii=False)
    else:
        lit=t.replace('\\','\\\\').replace('`','\\`').replace('${','\\${')
        # keep original escapes like \x27 used in raw: translation already plain
    out=out[:x['s']]+lit+out[x['e']:] if x['k']=='L' else out[:x['s']]+lit+out[x['e']:]
    n+=1
STATIC=[('/완공|완성|마쳤다|도착|돌아왔다|닿았다|출격|무너졌다|포위|회복했다|시작했다|떠났다/','/complete|finished|arriv|returned|marched|fallen|fell|besieged|surrounded|recovered|begun|set out|left for|razed/i'),('const re=/[다요]\\.(\\s|$)/g;','const re=/[.!?](\\s|$)/g;'),('휴대폰을 가로로 돌려 주세요','Please rotate your phone to landscape'),('Deep Dark는 가로 화면에서 한다','Deep Dark is played in landscape'),('1일째 · 1막','Day 1 · Act I'),('aria-label="왕궁 지도"','aria-label="Palace map"'),('aria-label="전장 미니맵"','aria-label="Battle minimap"'),('<html lang="ko">','<html lang="en">')]
for a,b in STATIC: out=out.replace(a,b)
open(OUT,'w',encoding='utf-8').write(out)
print('replaced',n,'missing',len(miss))
for m in miss[:20]: print('MISS',repr(m[:80]))
# English changelog
out=open(OUT,encoding='utf-8').read()
i=out.find('const CHANGES=[');j=out.find('];',i)
EN_CH='''const CHANGES=[
 ["0.9.146","English version: switch between 한국어 and English with the 🌐 button on the title screen or in Settings. First-time players get their device's language. The Lord of the Dead (Claude) speaks English in the English version"],
 ["0.9.145","Trial notice on the title screen"],
 ["0.9.144","itch.io trial: starts without a Claude API key (the Lord of the Dead follows basic rules — add a key in Settings to let Claude command) · Google sign-in through a browser window"],
 ["0.9.143","Phone: no more 'press this button' instructions — only what to do and where"],
 ["0.9.142","Phone: battle buttons no longer overlap"],
 ["0.9.141","Long notices wrap instead of being cut off · deployment help merged into the advice panel"],
 ["0.9.140","Multiplayer: up to 4 kingdoms in one world, fighting the Dead together"]'''
out=out[:i]+EN_CH+out[j:]
out=out.replace('`${S.day} days in · Act I — Legions of the Dead`','`Day ${S.day} · Act I — Legions of the Dead`')
open(OUT,'w',encoding='utf-8').write(out)
