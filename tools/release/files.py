# 배포 파일 목록 맞추기: sw.js의 VER, FILES와 version.json(버전, 파일마다 크기, sha1 앞 16자리)을 다시 만든다.
# 쓰는 법(저장소 폴더 game에서): python tools/release/files.py 0.9.154
# - FILES: 지금 목록을 그대로 두고, chr/*.glb, chrb/*.wasm, tex/*.jpg 중 목록에 없는 파일을 더한다(없어진 파일은 뺀다).
# - version.json: FILES 전부에 sw.js를 더해 크기와 sha를 새로 잰다.
import re, json, os, sys, glob, hashlib

ver = sys.argv[1]
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
s = open('sw.js', encoding='utf-8', newline='').read()
m = re.search(r'FILES=\[(.*?)\]', s, re.S)
files = [p for p in json.loads('[' + m.group(1) + ']') if os.path.exists(p)]
for pat in ('chr/*.glb', 'chrb/*.wasm', 'tex/*.jpg'):
    for p in sorted(glob.glob(pat)):
        p = p.replace('\\', '/')
        if p not in files:
            files.append(p)
s = re.sub(r'const VER="[^"]*"', 'const VER="%s"' % ver, s, count=1)
s = s[:m.start(1)] + ', '.join(json.dumps(p) for p in files) + s[m.end(1):]
open('sw.js', 'w', encoding='utf-8', newline='').write(s)

def ent(p):
    b = open(p, 'rb').read()
    return {"path": p, "size": len(b), "sha": hashlib.sha1(b).hexdigest()[:16]}

v = {"version": ver, "files": [ent(p) for p in files + ['sw.js']]}
open('version.json', 'w', encoding='utf-8', newline='').write(json.dumps(v, ensure_ascii=False))
print(len(files), 'files, total', sum(f['size'] for f in v['files']), 'bytes')
