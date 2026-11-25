import asyncio,sys
from playwright.async_api import async_playwright
async def m(mob):
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--host-resolver-rules=MAP html-classic.itch.zone 127.0.0.1","--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    kw=dict(viewport={"width":844,"height":390},is_mobile=True,has_touch=True) if mob else dict(viewport={"width":1280,"height":720})
    ctx=await b.new_context(locale="ko-KR",**kw);pg=await ctx.new_page();errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    await pg.goto("http://html-classic.itch.zone:8765/index.html");await pg.wait_for_timeout(6000)
    await pg.click('[data-a=guest]');await pg.wait_for_timeout(800)
    await pg.evaluate("document.querySelector('[data-a=startSkip]').click()");await pg.wait_for_timeout(9000)
    await pg.evaluate("UI.closeModal&&UI.closeModal();const y=[...document.querySelectorAll('button')].find(b=>/길잡이와/.test(b.textContent));y&&y.click();1");await pg.wait_for_timeout(2500)
    out=[]
    for i in range(7):
      await pg.evaluate("UI.closeModal&&UI.closeModal();document.querySelectorAll('#hint').forEach(e=>e.hidden=true);1");await pg.wait_for_timeout(1500)
      out.append(await pg.evaluate("(()=>{try{S.guideOff=false;S.tut=S.tut||{};const it=guideItems();S.tut.curI=it.findIndex(x=>!x[3]);S.tut.pend=undefined;return [UI.mode,it[S.tut.curI][0],fixJosa(tutNowText())]}catch(e){return String(e)}})()"))
      if i==0: await pg.screenshot(path=f"/tmp/goal_{'m' if mob else 'p'}.png",timeout=120000)
      await pg.evaluate(f"(()=>{{const it=guideItems();const c=it.findIndex(x=>!x[3]);S.tut.skip=(S.tut.skip||[]).concat([c]);S.tut.curI=undefined;S.tut.pend=undefined;renderGuide();{'openMap();' if i==3 else ''}}})()");await pg.wait_for_timeout(1500)
    for o in out:print(o)
    print("errs",errs[:4]);await b.close()
asyncio.run(m(sys.argv[1]=="m"))
