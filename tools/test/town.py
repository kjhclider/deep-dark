import asyncio,sys
from playwright.async_api import async_playwright
async def m():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--host-resolver-rules=MAP html-classic.itch.zone 127.0.0.1","--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    ctx=await b.new_context(locale="ko-KR",viewport={"width":1280,"height":720});pg=await ctx.new_page();errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)[:200]))
    async def ev(js,w=1200):
      try:r=await pg.evaluate(js)
      except Exception as e:errs.append("EV "+js[:40]+" :: "+str(e)[:160]);r=None
      await pg.wait_for_timeout(w);return r
    await pg.goto("http://html-classic.itch.zone:8765/index.html");await pg.wait_for_timeout(6000)
    await pg.click('[data-a=guest]');await pg.wait_for_timeout(800)
    await ev("document.querySelector('[data-a=startSkip]').click()",9000)
    await ev("UI.closeModal&&UI.closeModal();const y=[...document.querySelectorAll('button')].find(b=>/혼자/.test(b.textContent));y&&y.click();1",2000)
    await ev("UI.closeModal&&UI.closeModal();S.hints=Object.fromEntries(Object.keys(HINTS).map(k=>[k,1]));S.guideOff=true;document.querySelectorAll('#hint,#tutNow,#guide').forEach(e=>e.hidden=true);S.t=0.45;1")
    for i,(x,z,yaw,pit,dd) in enumerate([(0,80,1.2,0.22,14),(0,110,-1.3,0.2,14),(0,150,3.14,0.16,30),(-40,35,1.6,0.3,22)]):
      await ev(f"CAP.pos.x={x};CAP.pos.z={z};E.tp.yaw={yaw};E.tp.pitch={pit};E.tp.dd={dd};E.tp.snap=true;document.querySelectorAll('#hint,#tutNow').forEach(e=>e.hidden=true);1",3500)
      await pg.screenshot(path=f"/tmp/tw{i}.png",timeout=120000)
    print("errs",errs[:6]);await b.close()
asyncio.run(m())
