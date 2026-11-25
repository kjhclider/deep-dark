import asyncio,sys
from playwright.async_api import async_playwright
async def m(mob):
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--host-resolver-rules=MAP html-classic.itch.zone 127.0.0.1","--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    kw=dict(viewport={"width":844,"height":390},is_mobile=True,has_touch=True) if mob else dict(viewport={"width":1280,"height":720})
    ctx=await b.new_context(locale="ko-KR",**kw);pg=await ctx.new_page();errs=[];t="m" if mob else "p"
    pg.on("pageerror",lambda e:errs.append(str(e)[:200]))
    async def ev(js,w=1200):
      try:r=await pg.evaluate(js)
      except Exception as e:errs.append("EV "+js[:50]+" :: "+str(e)[:150]);r=None
      await pg.wait_for_timeout(w);return r
    await pg.goto("http://html-classic.itch.zone:8765/index.html");await pg.wait_for_timeout(6000)
    await pg.click('[data-a=guest]');await pg.wait_for_timeout(800)
    await ev("document.querySelector('[data-a=startSkip]').click()",9000)
    await ev("UI.closeModal&&UI.closeModal();const y=document.querySelector('[data-a=tutNo]');y&&y.click();1",1500)
    await ev("UI.closeModal&&UI.closeModal();S.day=12;S.hints=Object.fromEntries(Object.keys(HINTS).map(k=>[k,1]));1")
    await ev("UI.openModal(councilModal());1");await ev("document.querySelector('.window [data-a=compose]').click()");await pg.screenshot(path=f"/tmp/r_{t}0.png",timeout=120000)
    await ev("UI.closeModal();openMap();1",4000)
    await ev("UI.closeModal&&UI.closeModal();const f=SITES.find(s=>s.kind==='fortress');UI.sel={kind:'site',id:f.id};renderSide();E.ctrl.set(f.x,f.z,160,0,0.7,true);1",2500);await pg.screenshot(path=f"/tmp/r_{t}1.png",timeout=120000)
    await ev("UI.closeModal();practiceStart('field');1",9000)
    await ev("UI.closeModal&&UI.closeModal();const b=document.querySelector('[data-a=bbegin]');b&&b.click();1",4000)
    await pg.screenshot(path=f"/tmp/r_{t}2.png",timeout=120000)
    await ev("if(BT){BT.headless=true;for(let i=0;i<9000&&!BT.over;i++)stepBattle(1/15);BT.headless=false;}1",1000)
    for i in range(12):
      if await ev("!!document.querySelector('.veil:not([hidden]) .window')",1500):break
    await pg.screenshot(path=f"/tmp/r_{t}3.png",timeout=120000)
    print("errs",errs[:6]);await b.close()
asyncio.run(m(sys.argv[1]=="m"))
