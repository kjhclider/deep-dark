import asyncio,sys
from playwright.async_api import async_playwright
async def m():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--host-resolver-rules=MAP html-classic.itch.zone 127.0.0.1","--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    ctx=await b.new_context(locale="ko-KR",viewport={"width":1280,"height":720});pg=await ctx.new_page();errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)[:200]))
    async def ev(js,w=1200):
      try:r=await pg.evaluate(js)
      except Exception as e:errs.append("EV "+js[:40]+" :: "+str(e)[:160]);r=None
      await pg.wait_for_timeout(w);return r
    await pg.goto("http://html-classic.itch.zone:8765/index.html");await pg.wait_for_timeout(6000)
    await pg.click('[data-a=guest]');await pg.wait_for_timeout(800)
    await ev("document.querySelector('[data-a=startSkip]').click()",9000)
    await ev("UI.closeModal&&UI.closeModal();const y=document.querySelector('[data-a=tutNo]');y&&y.click();1",1500)
    await ev("UI.closeModal&&UI.closeModal();S.hints=Object.fromEntries(Object.keys(HINTS).map(k=>[k,1]));document.querySelectorAll('#hint').forEach(e=>e.hidden=true);1")
    # town views
    await ev("E.tp.yaw=0.6;E.tp.pitch=0.3;E.tp.dd=16;CAP.pos.x=22;CAP.pos.z=95;1",3500);await pg.screenshot(path="/tmp/b0.png",timeout=120000)
    await ev("CAP.pos.x=-24;CAP.pos.z=150;E.tp.yaw=2.4;E.tp.pitch=0.25;E.tp.dd=18;1",3500);await pg.screenshot(path="/tmp/b1.png",timeout=120000)
    await ev("CAP.pos.x=0;CAP.pos.z=175;E.tp.yaw=3.14;E.tp.pitch=0.2;E.tp.dd=26;1",3500);await pg.screenshot(path="/tmp/b2.png",timeout=120000)
    await ev("practiceStart('field');1",9000)
    await ev("UI.closeModal&&UI.closeModal();const b=document.querySelector('[data-a=bbegin]');b&&b.click();1",3000)
    await ev("toggleBattleView(false);const o=bOurs()[3];window._o=o;E.ctrl.set(o.x,o.z-6,34,0,0.6,true);1",2000)
    await ev("""const o=window._o;window._t0=BT.t;BT.fx.push({k:'raise',x:o.x-9,z:o.z-10,t0:BT.t,dur:1.5},{k:'shock',x:o.x+10,z:o.z-10,t0:BT.t,dur:1.3},{k:'heal',x:o.x-9,z:o.z+2,t0:BT.t,dur:1},{k:'purify',x:o.x+10,z:o.z+2,t0:BT.t,dur:1});
      for(let i=0;i<8;i++)BT.proj.push({x0:o.x-20,z0:o.z-16+i,x1:o.x+20,z1:o.z-18+i*2,t0:BT.t-0.5+i*0.05,dur:1.4,k:i%2?'hex':'holy',h0:0});
      window._iv=setInterval(()=>{if(BT.t-window._t0>=0.55){BT.paused=true;clearInterval(window._iv);}},10);1""",5000)
    await pg.screenshot(path="/tmp/mg0.png",timeout=120000)
    print("errs",errs[:6]);await b.close()
asyncio.run(m())
