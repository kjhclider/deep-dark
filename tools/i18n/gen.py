import json,re,glob,subprocess,sys,os,tempfile
HERE=os.path.dirname(os.path.abspath(__file__));ROOT=os.path.dirname(os.path.dirname(HERE));SEGS=os.path.join(tempfile.gettempdir(),'dd_segs.json')
SRC=sys.argv[1] if len(sys.argv)>1 else os.path.join(ROOT,'index.html')
OUT=sys.argv[2] if len(sys.argv)>2 else os.path.join(ROOT,'en.html')
allv={o['id']:o['v'] for o in json.load(open(os.path.join(HERE,'all.json'),encoding='utf-8'))}
tr={}
for f in sorted(glob.glob(os.path.join(HERE,'o[0-9]*.json'))):
    for k,v in json.load(open(f,encoding='utf-8')).items():
        if v is not None: tr[allv[int(k)]]=v
VER=re.compile(r'v0\.9\.\d+')
def norm(t): return VER.sub('v0.9.X',t)
trn={norm(k):v for k,v in tr.items()}
ov=json.load(open(os.path.join(HERE,'overrides.json'),encoding='utf-8')) if os.path.exists(os.path.join(HERE,'overrides.json')) else {}
subprocess.run(['node',os.path.join(HERE,'ext.js'),SRC,SEGS],check=True,capture_output=True)
segs=json.load(open(SEGS,encoding='utf-8'))
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
 ["0.9.152","Multiplayer: dead-lord requests sent to another player's Claude are accepted only from the host, with limits on model, reply length and frequency, so nobody can spend your API key at will\\nTitle screen: the large sun and halo behind the title are now a small, faint sun under a darker sky\\nWide letter-spacing removed from the subtitle, the What's new button and a few labels\\nMiddle dots in game text replaced with commas; What's new lists each change on its own line"],
 ["0.9.151","Houses: varied timber framing, joist ends under the upper floor, bargeboards and ridge, door frames and doorstep stones, window sills; some have a lean-to shed or a dormer, and a barrel, woodpile or bench by the door\\nWalls: corbels under the parapet, arrow slits and patched masonry\\nTowers: flared base, string course, corbels and arrow slits at different heights\\nSpells and prayers: thin wisps rising from the ground, low dark mist and scattering motes instead of big glowing blobs; the necromancer's bolt is a small dark orb trailing smoke\\n'How to build strong companies' in the Garrison tab is now four short steps\\nEnglish: key names removed on phones, sign-in page in English, singular and plural handled (1 company)"],
 ["0.9.150","Full pass over every line of text: press-this and click-that instructions and nagging phrasing are gone from descriptions, the guide and error messages\\nPhones no longer mention keyboard or mouse; the Controls tab and war-map notes in Help appear on PC only\\nSoldiers pushed off a wall no longer hang in the air at wall height\\nOn phones the mount button is no longer cut off at the right edge\\nNotifications no longer cover the battle result table\\nOutdated wording removed"],
 ["0.9.149","Guidance text shortened to read like other games: the line at the bottom is now an Objective that states the task without telling you which button to press\\nThe raid bar shows only the outlook, without urging you to recruit\\nSettings reorganised into Display, Sound, Mouse, Language, Claude, Game and Saves, one row each; duplicate buttons and rarely used options removed\\nSwitching to English also switches the king's name in a game started in Korean"],
 ["0.9.148","Two typefaces only: a sans for the interface and a serif for titles and story text. Wide letter-spacing, the decorative display face and monospaced numbers are gone\\nUnits flash briefly and kick up dust when they use a skill. Infantry already in contact shove the enemy back on the spot, javelins fly in twice the number, stick in the ground and knock back what they hit, and War Cry and Flank Charge shake the screen slightly\\nThe palace roof no longer covers the lower half of the deployment view\\nOn phones the title menu no longer overlaps the subtitle\\nTitle menu text no longer washes out against the bright sky\\nOutdated wording in Help and Settings cleaned up"],
 ["0.9.147","A calmer, less machine-made look: gold gradient lettering, glowing borders, diamond ornaments and metallic buttons are gone in favour of dark panels with thin borders\\nOne skill per branch (infantry Shove, spearmen Javelins, archers Fire Arrows, cavalry Flank Charge, army War Cry); the overlapping company abilities (R) were folded in\\nFire arrows arc high, stick in the ground and set separate fires that die out one by one, with black smoke, sparks, burning dead and scorch marks afterwards\\nArrows now have shafts, heads and fletching, and spent arrows stay stuck in the ground for a few seconds\\nNo more coloured rings under units using skills\\nThe dead's fire pots fly as pots, not arrows\\nEvery tree differs in size, height, lean and colour\\nHouses vary in plaster and roof colour, roof pitch and chimneys, some built of stone\\nWalls get a plinth, string course and buttresses, with stone colour varying by section\\nArmies marching on the map no longer slide as a rigid block\\nBattle screen cleanup: unit cards and floating labels hidden in the king's view, enemy labels show only the unit letter, king panel shows bars only, duplicate buttons removed, unit cards hidden on phones, the army/dead balance bar no longer covers the middle of the phone screen\\nPalace minimap labels no longer overlap\\nFountain water no longer looks striped\\nEmoji icons removed"],
 ["0.9.146","English version: switch between 한국어 and English with the language button on the title screen or in Settings. First-time players get their device's language. The Lord of the Dead (Claude) speaks English in the English version"],
 ["0.9.145","Trial notice on the title screen"],
 ["0.9.144","itch.io trial: starts without a Claude API key (the Lord of the Dead follows basic rules — add a key in Settings to let Claude command)\\nGoogle sign-in through a browser window"],
 ["0.9.143","Phone: no more 'press this button' instructions — only what to do and where"],
 ["0.9.142","Phone: battle buttons no longer overlap"],
 ["0.9.141","Long notices wrap instead of being cut off\\ndeployment help merged into the advice panel"],
 ["0.9.140","Multiplayer: up to 4 kingdoms in one world, fighting the Dead together"]'''
out=out[:i]+EN_CH+out[j:]
out=out.replace('`${S.day} days in\\nAct I — Legions of the Dead`','`Day ${S.day}\\nAct I — Legions of the Dead`')
open(OUT,'w',encoding='utf-8').write(out)

# English singular/plural: "${n} companies" -> company when n is 1
out=open(OUT,encoding='utf-8').read()
SING={'companies':'company','days':'day','wins':'win','spies':'spy','soldiers':'soldier','villages':'village','armies':'army','kills':'kill','seconds':'second'}
def _pl(m):
    x,sp,w=m.group(1),m.group(2),m.group(3)
    if '=' in x.replace('==','').replace('!=','').replace('>=','').replace('<=','') or '++' in x: return m.group(0)
    return '${%s}%s${(%s)==1?"%s":"%s"}'%(x,sp,x,SING[w],w)
out,npl=re.subn(r'\$\{([^{}`]{1,60})\}( )(companies|days|wins|spies|soldiers|villages|armies|kills|seconds)\b',_pl,out)
open(OUT,'w',encoding='utf-8').write(out);print('plurals',npl)
