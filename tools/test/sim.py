import asyncio
from playwright.async_api import async_playwright
async def m():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--host-resolver-rules=MAP html-classic.itch.zone 127.0.0.1","--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg=await b.new_page(viewport={"width":900,"height":500});errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    await pg.goto("http://html-classic.itch.zone:8765/index.html");await pg.wait_for_timeout(6000)
    await pg.click('[data-a=guest]');await pg.wait_for_timeout(1000)
    await pg.click('[data-a=start]');await pg.wait_for_timeout(8000)
    await pg.evaluate("UI.closeModal&&UI.closeModal();const b=document.querySelector('[data-a=bbegin]');b&&b.click();1");await pg.wait_for_timeout(3000)
    r=await pg.evaluate("""(()=>{try{BT.headless=true;BT.auto=true;let n=0;const used={};
      while(!BT.over&&n<30000){if(n%300===0)for(const k of ['inf','spear','archer','cav','all']){const before=BT.gcd&&BT.gcd[k];grpCmd(k,'skill');if(BT.gcd[k]!==before)used[k]=(used[k]||0)+1;}
        stepBattle(1/15);n++;}
      return JSON.stringify({n,t:Math.round(BT.t),over:BT.over,log:BT.log.slice(-6),used,o:compMenSq(0),f:compMenSq(1)});}catch(e){return 'ERR '+e.stack}})()""")
    print(r);print("errs",errs[:5]);await b.close()
asyncio.run(m())
