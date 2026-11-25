import asyncio,sys
from playwright.async_api import async_playwright
async def m(loc,path):
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--host-resolver-rules=MAP html-classic.itch.zone 127.0.0.1","--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    ctx=await b.new_context(locale=loc,viewport={"width":1100,"height":650})
    pg=await ctx.new_page();errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    await pg.goto(f"http://html-classic.itch.zone:8765/{path}");await pg.wait_for_timeout(7000)
    await pg.click('[data-a=guest]');await pg.wait_for_timeout(1200)
    await pg.click('[data-a=start]');await pg.wait_for_timeout(8000)
    await pg.evaluate("UI.closeModal&&UI.closeModal();const b=document.querySelector('[data-a=bbegin]');b&&b.click();1");await pg.wait_for_timeout(6000)
    await pg.evaluate("toggleBattleView(false);BT.speed=4;1")
    for k in ["inf","spear","archer","cav","all"]:
      await pg.evaluate(f"grpSelect('{k}');grpCmd('{k}','skill');renderBattleHUD();1");await pg.wait_for_timeout(1500)
    await pg.screenshot(path=f"/tmp/auto_{path[:2]}0.png",timeout=120000)
    r=await pg.evaluate("JSON.stringify({t:BT.t,cd:BT.gcd,fires:(BT.fires||[]).length,stuck:(BT.stuck||[]).length,parts:(BT.parts||[]).length})");print(r)
    for i in range(8):
      await pg.wait_for_timeout(8000)
      st=await pg.evaluate("BT?JSON.stringify({t:Math.round(BT.t),over:BT.over,o:bOurs().filter(act).length,f:bFoes().length}):'nobt'");print(st)
      if '"over":true' in st or st=='nobt':break
      await pg.evaluate("if(BT){for(const k of ['inf','spear','archer','cav','all'])grpCmd(k,'skill');}1")
    await pg.screenshot(path=f"/tmp/auto_{path[:2]}1.png",timeout=120000)
    await pg.evaluate("prologueEnd();1");await pg.wait_for_timeout(8000)
    await pg.evaluate("UI.closeModal&&UI.closeModal();const y=[...document.querySelectorAll('button')].find(b=>/혼자|myself|alone/i.test(b.textContent));y&&y.click();1");await pg.wait_for_timeout(2000)
    await pg.evaluate("UI.closeModal&&UI.closeModal();try{S.speed=8}catch(e){}1");await pg.wait_for_timeout(20000)
    print("day",await pg.evaluate("S&&S.day"))
    await pg.screenshot(path=f"/tmp/auto_{path[:2]}2.png",timeout=120000)
    print("errs",errs[:6]);await b.close()
asyncio.run(m(sys.argv[1],sys.argv[2]))
