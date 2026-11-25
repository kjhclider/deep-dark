import asyncio,sys
from playwright.async_api import async_playwright
async def m(mob):
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--host-resolver-rules=MAP html-classic.itch.zone 127.0.0.1","--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    kw=dict(viewport={"width":844,"height":390},is_mobile=True,has_touch=True) if mob else dict(viewport={"width":1280,"height":720})
    ctx=await b.new_context(locale="ko-KR",**kw);pg=await ctx.new_page();errs=[];t="m" if mob else "p"
    pg.on("pageerror",lambda e:errs.append(str(e)[:200]))
    await pg.goto("http://html-classic.itch.zone:8765/index.html");await pg.wait_for_timeout(6000)
    await pg.click('[data-a=guest]');await pg.wait_for_timeout(800)
    await pg.evaluate("document.querySelector('[data-a=startSkip]').click()");await pg.wait_for_timeout(9000)
    await pg.evaluate("UI.closeModal&&UI.closeModal();const y=document.querySelector('[data-a=tutNo]');y&&y.click();1");await pg.wait_for_timeout(1500)
    await pg.evaluate("UI.closeModal&&UI.closeModal();S.hints=Object.fromEntries(Object.keys(HINTS).map(k=>[k,1]));practiceStart('field');1");await pg.wait_for_timeout(9000)
    await pg.evaluate("UI.closeModal&&UI.closeModal();const b=document.querySelector('[data-a=bbegin]');b&&b.click();1");await pg.wait_for_timeout(3000)
    await pg.evaluate("BT.headless=true;for(let i=0;i<9000&&!BT.over&&compMenSq(1)>60;i++)stepBattle(1/15);BT.headless=false;for(const s of bFoes()){s.alive=0;s.pool=0;s.dead=true;}1")
    ok=False
    for i in range(25):
      await pg.wait_for_timeout(2000)
      if await pg.evaluate("!!UI.modalOpen"):ok=True;break
    await pg.wait_for_timeout(1500);await pg.screenshot(path=f"/tmp/res_{t}.png",timeout=120000)
    print("modal",ok,await pg.evaluate("BT?BT.over:'nobt'"),"errs",errs[:5]);await b.close()
asyncio.run(m(sys.argv[1]=="m"))
