# Deep Dark 확인 도구 서버 (2026-11-27, 팀원 7)
# game 폴더를 http://localhost:8777/ 로 보여 주고, 투어 사진과 검사 결과를 tools/check/runs/<판 이름>/ 에 저장한다.
# 게임 주소(8765)와 다른 주소라 브라우저 저장소가 따로다: 이어하기 저장을 건드리지 않는다.
# 실행: python tools/check/serve.py   (game 폴더에서)
import base64, json, os, re, sys, html
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # game
RUNS = os.path.join(ROOT, "tools", "check", "runs")
SAFE = re.compile(r"^[0-9A-Za-z_\-]+$")

def build_compare(run):
    """이번 판과 바로 앞 판을 나란히 놓은 index.html (장면 이름, 앞, 지금) + 검사 표"""
    # 판은 처음 만든 순서(폴더 생성 시각)로 놓는다: 이름 글자순이면 2026-11-27_after가 _base보다 앞에 온다
    runs = sorted((d for d in os.listdir(RUNS) if os.path.isdir(os.path.join(RUNS, d))), key=lambda d: os.path.getctime(os.path.join(RUNS, d)))
    prev = None
    if run in runs:
        i = runs.index(run)
        prev = runs[i - 1] if i > 0 else None
    cur_dir = os.path.join(RUNS, run)
    def shots(d):
        if not d: return {}
        p = os.path.join(RUNS, d, "shots.json")
        return json.load(open(p, encoding="utf8")) if os.path.exists(p) else {}
    cur, old = shots(run), shots(prev)
    rows = []
    for name, info in cur.items():
        o = old.get(name)
        left = f'<img src="../{prev}/{html.escape(o["file"])}" loading="lazy">' if o else '<div class="none">앞 판 없음</div>'
        right = f'<img src="{html.escape(info["file"])}" loading="lazy">'
        rows.append(f'<tr><th>{html.escape(info.get("title", name))}<small>{html.escape(name)}</small></th><td>{left}</td><td>{right}</td></tr>')
    chk = ""
    p = os.path.join(cur_dir, "checks.json")
    if os.path.exists(p):
        res = json.load(open(p, encoding="utf8"))
        po = os.path.join(RUNS, prev, "checks.json") if prev else None
        oldres = {r["id"]: r for r in json.load(open(po, encoding="utf8"))} if po and os.path.exists(po) else {}
        tr = []
        for r in res:
            o = oldres.get(r["id"])
            st = {True: "통과", False: "실패", None: "못 잼"}[r.get("pass")]
            cls = {True: "ok", False: "bad", None: "na"}[r.get("pass")]
            os_ = ("" if not o else {True: "통과", False: "실패", None: "못 잼"}[o.get("pass")])
            tr.append(f'<tr class="{cls}"><td>{html.escape(r["name"])}</td><td>{st}</td><td>{html.escape(str(r.get("value","")))}</td><td>{html.escape(str(r.get("limit","")))}</td><td>{html.escape(os_)}</td></tr>')
        chk = '<h2>자동 검사</h2><table class="chk"><tr><th>항목</th><th>결과</th><th>잰 값</th><th>기준</th><th>앞 판</th></tr>' + "".join(tr) + "</table>"
    page = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>Deep Dark 확인 {html.escape(run)}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{{--bg:#f4f2ee;--fg:#222;--mut:#777;--line:#d8d4cc;--ok:#2d6a3e;--bad:#a22;--na:#888}}
@media (prefers-color-scheme:dark){{:root{{--bg:#16150f;--fg:#e8e4da;--mut:#999;--line:#3a3630}}}}
body{{margin:0;padding:16px;background:var(--bg);color:var(--fg);font:14px/1.5 "Gowun Batang",serif}}
h1{{font-size:20px;margin:0 0 4px}} h2{{font-size:16px;margin:24px 0 8px}} p{{color:var(--mut);margin:0 0 12px}}
table{{border-collapse:collapse;width:100%}} th,td{{border-top:1px solid var(--line);padding:8px;vertical-align:top;text-align:left}}
.shots th{{width:14%}} .shots th small{{display:block;color:var(--mut);font-weight:normal}} .shots img{{width:100%;display:block}}
.none{{color:var(--mut);padding:40px 0;text-align:center}}
.chk td:nth-child(2),.chk th{{white-space:nowrap}} .chk td:nth-child(1){{width:30%}}
.chk tr.ok td:nth-child(2){{color:var(--ok)}} .chk tr.bad td:nth-child(2){{color:var(--bad);font-weight:bold}} .chk tr.na td:nth-child(2){{color:var(--na)}}
</style></head><body>
<h1>Deep Dark 화면 투어와 검사: {html.escape(run)}</h1>
<p>왼쪽은 앞 판({html.escape(prev or "없음")}), 오른쪽은 이번 판. 사진은 3D 화면만 찍는다(글씨, 단추는 검사 표의 겹침 항목으로 잰다).</p>
{chk}
<h2>화면 투어</h2>
<table class="shots"><tr><th>장면</th><th>앞 판</th><th>이번 판</th></tr>{"".join(rows)}</table>
</body></html>'''
    open(os.path.join(cur_dir, "index.html"), "w", encoding="utf8").write(page)
    return prev

class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)
    def log_message(self, *a):
        pass
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()
    def do_POST(self):
        u = urlparse(self.path); q = parse_qs(u.query)
        run = q.get("run", [""])[0]
        if not SAFE.match(run or ""):
            self.send_error(400, "run"); return
        n = int(self.headers.get("Content-Length", "0")); body = self.rfile.read(n)
        d = os.path.join(RUNS, run); os.makedirs(d, exist_ok=True)
        out = {"ok": True}
        if u.path == "/check/shot":
            name = q.get("name", [""])[0]; title = q.get("title", [name])[0]
            if not SAFE.match(name or ""):
                self.send_error(400, "name"); return
            data = body.decode("ascii"); data = data.split(",", 1)[1] if "," in data else data
            fn = name + ".jpg"; open(os.path.join(d, fn), "wb").write(base64.b64decode(data))
            sp = os.path.join(d, "shots.json"); js = json.load(open(sp, encoding="utf8")) if os.path.exists(sp) else {}
            js[name] = {"file": fn, "title": title}; json.dump(js, open(sp, "w", encoding="utf8"), ensure_ascii=False, indent=1)
        elif u.path == "/check/result":
            json.dump(json.loads(body.decode("utf8")), open(os.path.join(d, "checks.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
        elif u.path == "/check/done":
            out["prev"] = build_compare(run); out["page"] = f"/tools/check/runs/{run}/index.html"
        else:
            self.send_error(404); return
        b = json.dumps(out).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8777
    os.makedirs(RUNS, exist_ok=True)
    print(f"http://localhost:{port}/index.html  (결과: {RUNS})", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
