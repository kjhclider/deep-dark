import asyncio,sys
from playwright.async_api import async_playwright
async def m():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--host-resolver-rules=MAP html-classic.itch.zone 127.0.0.1","--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    # login page, both languages
    for l in ("en","ko"):
      ctx=await b.new_context(locale="en-US",viewport={"width":500,"height":360});pg=await ctx.new_page();er=[]
      pg.on("pageerror",lambda e:er.append(str(e)[:120]))
      await pg.add_init_script("window.firebase={initializeApp(){},auth(){return {}},firestore(){return {}}}")
      await pg.goto(f"http://html-classic.itch.zone:8765/login.html?l={l}&c=ABCDEFGH");await pg.wait_for_timeout(1500)
      await pg.screenshot(path=f"/tmp/login_{l}.png");print("login",l,await pg.evaluate("document.body.innerText.replace(/\\n+/g,' | ')"),er[:2]);await ctx.close()
    # english mobile
    ctx=await b.new_context(locale="en-US",viewport={"width":844,"height":390},is_mobile=True,has_touch=True);pg=await ctx.new_page();errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)[:200]))
    await pg.goto("http://html-classic.itch.zone:8765/index.html");await pg.wait_for_timeout(7000)
    await pg.click('[data-a=guest]');await pg.wait_for_timeout(800)
    await pg.evaluate("document.querySelector('[data-a=startSkip]').click()");await pg.wait_for_timeout(9000)
    await pg.evaluate("UI.closeModal&&UI.closeModal();const y=document.querySelectorAll('.window .wfoot button')[0];y&&y.click();1");await pg.wait_for_timeout(1500)
    await pg.evaluate("UI.closeModal&&UI.closeModal();S.day=12;S.hints=Object.fromEntries(Object.keys(HINTS).map(k=>[k,1]));UI.openModal(kingdomModal());1");await pg.wait_for_timeout(800)
    await pg.evaluate("document.querySelectorAll('[data-a=ktab]')[2].click()");await pg.wait_for_timeout(1000);await pg.screenshot(path="/tmp/enm0.png",timeout=120000)
    await pg.evaluate("UI.closeModal();UI.openModal(forgeModal());1");await pg.wait_for_timeout(800);await pg.screenshot(path="/tmp/enm1.png",timeout=120000)
    await pg.evaluate("UI.closeModal();UI.openModal(helpModal('battle'));1");await pg.wait_for_timeout(800);await pg.screenshot(path="/tmp/enm2.png",timeout=120000)
    await pg.evaluate("UI.closeModal();practiceStart('field');1");await pg.wait_for_timeout(9000);await pg.screenshot(path="/tmp/enm3.png",timeout=120000)
    print(pg.url,"errs",errs[:5]);await b.close()
asyncio.run(m())
