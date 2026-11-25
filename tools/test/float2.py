import asyncio,sys
from playwright.async_api import async_playwright
async def m():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--host-resolver-rules=MAP html-classic.itch.zone 127.0.0.1","--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    ctx=await b.new_context(locale="ko-KR",viewport={"width":700,"height":400});pg=await ctx.new_page();errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    await pg.goto("http://html-classic.itch.zone:8765/index.html");await pg.wait_for_timeout(6000)
    await pg.click('[data-a=guest]');await pg.wait_for_timeout(1000)
    await pg.click('[data-a=start]');await pg.wait_for_timeout(8000)
    await pg.evaluate("UI.closeModal&&UI.closeModal();const b=document.querySelector('[data-a=bbegin]');b&&b.click();1");await pg.wait_for_timeout(3000)
    await pg.evaluate("toggleBattleView(false);window._hy=new Map();window._stuck=0;window._esc=0;setInterval(()=>{if(!BT)return;for(const s of BT.sq){if(s.escTop)window._esc++;for(const f of s.figs){if(!f.alive)continue;if((f.hy||0)>0.3){const t0=window._hy.get(f);if(t0===undefined)window._hy.set(f,BT.t);else if(BT.t-t0>4){window._stuck++;window._hy.set(f,BT.t+999);}}else window._hy.delete(f);}}},200);1")
    for i in range(40):
      await pg.wait_for_timeout(8000)
      r=await pg.evaluate("BT?JSON.stringify({t:BT.t|0,over:BT.over,fp:BT.fpN||0,stuck:window._stuck,esc:window._esc}):'nobt'")
      if i%5==0 or 'true' in r:print(r)
      if r=='nobt' or '"over":true' in r:break
    print("errs",errs[:4]);await b.close()
asyncio.run(m())
