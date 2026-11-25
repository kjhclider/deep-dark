import asyncio,sys
from playwright.async_api import async_playwright
async def m(mob):
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--host-resolver-rules=MAP html-classic.itch.zone 127.0.0.1","--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    kw=dict(viewport={"width":844,"height":390},is_mobile=True,has_touch=True) if mob else dict(viewport={"width":1100,"height":650})
    ctx=await b.new_context(locale="ko-KR",**kw)
    pg=await ctx.new_page();errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    await pg.goto("http://html-classic.itch.zone:8765/index.html");await pg.wait_for_timeout(6000)
    await pg.click('[data-a=guest]');await pg.wait_for_timeout(1200)
    await pg.click('[data-a=start]');await pg.wait_for_timeout(8000)
    await pg.evaluate("UI.closeModal&&UI.closeModal();const b=document.querySelector('[data-a=bbegin]');b&&b.click();1");await pg.wait_for_timeout(8000)
    t="m" if mob else "p"
    await pg.evaluate("toggleBattleView(false);S.hints=S.hints||{};S.hints.sk_archer=1;1");await pg.wait_for_timeout(1000)
    await pg.evaluate("""grpCmd('archer','skill');window._ft0=BT.t;const P=BT.proj.filter(p=>p.k==='fire');const cx=P.reduce((a,p)=>a+p.x1,0)/P.length,cz=P.reduce((a,p)=>a+p.z1,0)/P.length;window._fc=[cx,cz];
      const ax=P.reduce((a,p)=>a+p.x0,0)/P.length,az=P.reduce((a,p)=>a+p.z0,0)/P.length;E.ctrl.set((cx+ax)/2,(cz+az)/2,60,0,0.55,true);1""")
    shots=[0.5,1.0,2.0,4.0,8.0,13.0]
    for i,w in enumerate(shots):
      for _ in range(600):
        el=await pg.evaluate("BT.t-window._ft0")
        if el>=w:break
        await pg.wait_for_timeout(100)
      if i==2: await pg.evaluate("E.ctrl.set(window._fc[0],window._fc[1]-6,34,0,0.6,true);1")
      await pg.screenshot(path=f"/tmp/fire_{t}{i}.png",timeout=120000)
    print("errs",errs[:5]);await b.close()
asyncio.run(m(sys.argv[1]=="m"))
