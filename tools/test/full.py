import asyncio,sys
from playwright.async_api import async_playwright
async def m(mob,page,loc):
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--host-resolver-rules=MAP html-classic.itch.zone 127.0.0.1","--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    kw=dict(viewport={"width":844,"height":390},is_mobile=True,has_touch=True) if mob else dict(viewport={"width":1280,"height":720})
    ctx=await b.new_context(locale=loc,**kw)
    pg=await ctx.new_page();errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)));pg.on("console",lambda m:errs.append("C:"+m.text[:150]) if m.type=="error" and "ERR_" not in m.text and "Failed to load" not in m.text else None)
    t=("m" if mob else "p")+page[:2]
    n=[0]
    async def shot(name):
      await pg.screenshot(path=f"/tmp/f_{t}_{n[0]:02d}{name}.png",timeout=120000);n[0]+=1
    async def ev(js,w=1500):
      try: r=await pg.evaluate(js)
      except Exception as e: errs.append("EV:"+js[:50]+" "+str(e)[:120]);r=None
      await pg.wait_for_timeout(w);return r
    await pg.goto(f"http://html-classic.itch.zone:8765/{page}");await pg.wait_for_timeout(7000)
    await shot("login")
    await pg.click('[data-a=guest]');await pg.wait_for_timeout(1500);await shot("title")
    await ev("document.querySelector('[data-a=changes]').click()");await shot("changes");await ev("UI.closeModal()",500)
    await pg.click('[data-a=start]');await pg.wait_for_timeout(8000);await shot("prologue")
    await ev("UI.closeModal&&UI.closeModal()",800);await shot("deploy")
    await ev("const b=document.querySelector('[data-a=bbegin]');b&&b.click()",7000);await shot("battle")
    await ev("document.querySelector('[data-a=help]').click()");await shot("help");await ev("UI.closeModal()",500)
    await ev("document.querySelector('[data-a=settings]').click()");await shot("settings");await ev("UI.closeModal()",500)
    await ev("BT.headless=true;for(let i=0;i<2000&&!BT.over;i++)stepBattle(1/15);BT.headless=false;if(!BT.over)finishBattle(true);1",5000);await shot("result")
    await ev("prologueEnd()",9000);await shot("crown")
    await ev("UI.closeModal&&UI.closeModal();const y=[...document.querySelectorAll('button')].find(b=>/혼자|own|alone|myself/i.test(b.textContent));y&&y.click();1",2000)
    await ev("UI.closeModal&&UI.closeModal();document.querySelectorAll('#hint').forEach(e=>e.hidden=true)",1500);await shot("capital")
    await ev("UI.openModal(kingdomModal())");await shot("kingdom")
    tabs=await ev("[...document.querySelectorAll('[data-a=ktab]')].map(b=>b.dataset.t||b.dataset.k||b.textContent)",100)
    print("tabs",tabs)
    for i in range(1,len(tabs or [])):
      await ev(f"document.querySelectorAll('[data-a=ktab]')[{i}].click()",1200);await shot(f"ktab{i}")
    await ev("UI.closeModal();openMap()",5000);await ev("UI.closeModal&&UI.closeModal();document.querySelectorAll('#hint').forEach(e=>e.hidden=true)",800);await shot("map")
    await ev("UI.sel={kind:'site',id:S.sites?Object.keys(S.sites)[1]:(SITES[1]||{}).id};renderSide()",1200);await shot("side")
    for d in ["compose","armies","build"]:
      await ev(f"UI.closeModal&&UI.closeModal();const b=document.querySelector('#dock [data-a={d}]');b&&b.click()",1500);await shot("dock_"+d)
    await ev("UI.closeModal&&UI.closeModal()",300)
    print("errs",errs[:8]);await b.close()
asyncio.run(m(sys.argv[1]=="m",sys.argv[2],sys.argv[3]))
