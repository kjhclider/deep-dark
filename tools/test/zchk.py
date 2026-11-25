import asyncio
from playwright.async_api import async_playwright
async def m():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--host-resolver-rules=MAP html-classic.itch.zone 127.0.0.1","--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    ctx=await b.new_context(locale="ko-KR",viewport={"width":1100,"height":650});pg=await ctx.new_page();errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    await pg.goto("http://html-classic.itch.zone:8767/index.html");await pg.wait_for_timeout(7000)
    await pg.click('[data-a=guest]');await pg.wait_for_timeout(1000)
    await pg.click('[data-a=start]');await pg.wait_for_timeout(8000)
    print("battle", await pg.evaluate("!!BT"), "gate", await pg.evaluate("!!document.querySelector('.gate,#keyGate')"))
    print("errs",errs[:4]);await b.close()
asyncio.run(m())
