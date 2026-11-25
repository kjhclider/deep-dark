import asyncio,sys
from playwright.async_api import async_playwright
async def m():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--host-resolver-rules=MAP html-classic.itch.zone 127.0.0.1","--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    ctx=await b.new_context(locale="ko-KR",viewport={"width":1100,"height":650})
    pg=await ctx.new_page();errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    await pg.goto("http://html-classic.itch.zone:8765/index.html");await pg.wait_for_timeout(6000)
    await pg.click('[data-a=guest]');await pg.wait_for_timeout(1200)
    await pg.click('[data-a=start]');await pg.wait_for_timeout(8000)
    await pg.evaluate("UI.closeModal&&UI.closeModal();const b=document.querySelector('[data-a=bbegin]');b&&b.click();1");await pg.wait_for_timeout(5000)
    await pg.evaluate("toggleBattleView(false);S.hints=S.hints||{};for(const k of ['inf','spear','archer','cav','all'])S.hints['sk_'+k]=1;BT.gateOpen=true;BT.headless=true;for(let i=0;i<330&&!BT.over;i++)stepBattle(1/15);BT.headless=false;1")
    await pg.wait_for_timeout(4000)
    print(await pg.evaluate("JSON.stringify({t:BT.t|0,over:BT.over,eng:bOurs().filter(s=>s.engaged).map(s=>s.t)})"))
    for k in ["inf","spear","cav","all"]:
      r=await pg.evaluate(f"""(()=>{{const sq=grpSquads('{k}');if(!sq.length)return 'none';const cx=sq.reduce((a,s)=>a+s.x,0)/sq.length,cz=sq.reduce((a,s)=>a+s.z,0)/sq.length;E.ctrl.set(cx,cz-8,{ '70' if k=='all' else '48'},0,0.6,true);window._t0=BT.t;return cx+','+cz;}})()""")
      await pg.wait_for_timeout(2500)
      await pg.screenshot(path=f"/tmp/sk_{k}_a.png",timeout=120000)
      await pg.evaluate(f"window._t0=BT.t;grpCmd('{k}','skill');window._iv=setInterval(()=>{{if(BT.t-window._t0>=0.35){{BT.paused=true;clearInterval(window._iv);}}}},10);1")
      await pg.wait_for_timeout(2500)
      await pg.screenshot(path=f"/tmp/sk_{k}_0.png",timeout=120000)
      await pg.evaluate("BT.paused=false;window._iv=setInterval(()=>{if(BT.t-window._t0>=1.6){BT.paused=true;clearInterval(window._iv);}},10);1")
      await pg.wait_for_timeout(6000)
      await pg.screenshot(path=f"/tmp/sk_{k}_1.png",timeout=120000)
      await pg.evaluate("BT.paused=false;1")
      print(k,r)
    print("errs",errs[:5]);await b.close()
asyncio.run(m())
