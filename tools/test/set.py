import asyncio,sys
from playwright.async_api import async_playwright
async def m(mob,loc):
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--host-resolver-rules=MAP html-classic.itch.zone 127.0.0.1","--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    kw=dict(viewport={"width":844,"height":390},is_mobile=True,has_touch=True) if mob else dict(viewport={"width":1280,"height":720})
    ctx=await b.new_context(locale="ko-KR",**kw);pg=await ctx.new_page();errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    await pg.goto("http://html-classic.itch.zone:8765/index.html");await pg.wait_for_timeout(6000)
    await pg.click('[data-a=guest]');await pg.wait_for_timeout(800)
    await pg.evaluate("document.querySelector('[data-a=startSkip]').click()");await pg.wait_for_timeout(9000)
    await pg.evaluate("UI.closeModal&&UI.closeModal();const y=[...document.querySelectorAll('button')].find(b=>/혼자/.test(b.textContent));y&&y.click();1");await pg.wait_for_timeout(2000)
    t=("m" if mob else "p")
    await pg.evaluate("UI.closeModal&&UI.closeModal();UI.openModal(settingsModal());1");await pg.wait_for_timeout(1200)
    await pg.screenshot(path=f"/tmp/set_{t}0.png",timeout=120000)
    await pg.evaluate("document.querySelector('.window').scrollTop=9999");await pg.wait_for_timeout(600)
    await pg.screenshot(path=f"/tmp/set_{t}1.png",timeout=120000)
    for a in ["music","sfxtoggle"]:
      await pg.evaluate(f"document.querySelector('.window [data-a={a}]').click()");await pg.wait_for_timeout(500)
    await pg.evaluate("const r=document.querySelector('#brightV');r.value=120;r.dispatchEvent(new Event('input',{bubbles:true}));1")
    print("ruler ko",await pg.evaluate("S.ruler"))
    if loc=="sw":
      await pg.evaluate("saveGame&&saveGame();1");await pg.wait_for_timeout(1500)
      await pg.evaluate("document.querySelector('.window [data-a=lang]').click()");await pg.wait_for_timeout(7000)
      print(pg.url, await pg.evaluate("JSON.stringify([typeof LOADED!=='undefined'&&LOADED&&LOADED.ruler,document.querySelector('.tmenu')&&document.querySelector('.tmenu').textContent.slice(0,80)])"))
      await pg.screenshot(path="/tmp/set_en_title.png",timeout=120000)
    print("errs",errs[:4]);await b.close()
asyncio.run(m(sys.argv[1]=="m",sys.argv[2]))
