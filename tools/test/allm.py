import asyncio,sys,json
from playwright.async_api import async_playwright
async def m(mob,page):
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--host-resolver-rules=MAP html-classic.itch.zone 127.0.0.1","--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    kw=dict(viewport={"width":844,"height":390},is_mobile=True,has_touch=True) if mob else dict(viewport={"width":1280,"height":720})
    ctx=await b.new_context(locale="ko-KR" if page=="index.html" else "en-US",**kw);pg=await ctx.new_page();errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)[:200]))
    tag=("m" if mob else "p")+page[:2];n=[0];names=[]
    async def shot(name):
      await pg.screenshot(path=f"/tmp/am_{tag}_{n[0]:02d}.png",timeout=120000);names.append(name);n[0]+=1
    async def ev(js,w=900):
      try:r=await pg.evaluate(js)
      except Exception as e:errs.append("EV "+js[:60]+" :: "+str(e)[:160]);r=None
      await pg.wait_for_timeout(w);return r
    await pg.goto(f"http://html-classic.itch.zone:8765/{page}");await pg.wait_for_timeout(6000)
    await pg.click('[data-a=guest]');await pg.wait_for_timeout(800)
    await ev("document.querySelector('[data-a=startSkip]').click()",9000)
    await ev("UI.closeModal&&UI.closeModal();const y=document.querySelector('[data-a=tutNo]');y&&y.click();1",1500)
    await ev("UI.closeModal&&UI.closeModal();S.day=12;S.res.gold=5000;S.res.food=5000;S.hints=Object.fromEntries(Object.keys(HINTS).map(k=>[k,1]));document.querySelectorAll('#hint').forEach(e=>e.hidden=true);1")
    ids=await ev("JSON.stringify({bld:Object.keys(BLD),realm:Object.keys(S.realms||{})[0],vil:villagesOwned()[0].id,gen:(S.gens||[])[0]&&S.gens[0].id,gens:(typeof GENERALS!=='undefined'?GENERALS[0].id:null)})",100)
    ids=json.loads(ids or "{}");print(ids)
    calls=[("kingdom","kingdomModal()")]
    await ev("UI.openModal(kingdomModal())");await shot("kingdom")
    nt=await ev("document.querySelectorAll('[data-a=ktab]').length",100) or 0
    for i in range(1,nt):
      await ev(f"document.querySelectorAll('[data-a=ktab]')[{i}].click()");await shot(f"ktab{i}")
    lst=["armiesModal()","composeModal()","councilModal()","duelModal()","forgeModal()","gensModal()","glossaryModal()","helpModal('keys')","helpModal('battle')","helpModal('terms')","helpModal('guide')","helpModal('lose')","pasteModal()","practiceModal()","priestModal()","spyNetModal()","treasuryModal()","warBoardModal()","wardrobeModal()","chronModal()","changesModal()","controlsModal()"]
    lst+= [f"buildingModal('{k}')" for k in ids.get("bld",[])]
    if ids.get("realm"):lst.append(f"diploModal('{ids['realm']}')")
    if ids.get("vil"):lst.append(f"villageModal('{ids['vil']}')")
    g=ids.get("gen") or ids.get("gens")
    if g:lst.append(f"genModal('{g}')")
    for c in lst:
      await ev(f"UI.closeModal&&UI.closeModal();UI.openModal({c});1");await shot(c)
    await ev("UI.closeModal();fireEvent('merchant');1",1200);await shot("event merchant")
    await ev("UI.ev=null;UI.closeModal();herald('전령','북쪽 길에 연기가 오른다.','');1",1200);await shot("herald")
    await ev("UI.closeModal();UI.openModal(actEndModal());1");await shot("actEnd")
    await ev("UI.closeModal();UI.openModal(gameOverModal());1");await shot("gameOver")
    await ev("UI.closeModal();openMap();1",4000)
    await ev("UI.closeModal&&UI.closeModal();const a=S.armies[0];if(a){UI.sel={kind:'army',id:a.id};renderSide();}1");await shot("map army side")
    await ev("const f=SITES.find(s=>s.kind==='fort');UI.sel={kind:'site',id:f.id};renderSide();1");await shot("map fort side")
    await ev("UI.closeModal();practiceStart(Object.keys(typeof PRACT!=='undefined'?PRACT:{field:1})[0]||'field');1",9000);await shot("practice deploy")
    await ev("UI.closeModal&&UI.closeModal();const b=document.querySelector('[data-a=bbegin]');b&&b.click();1",5000);await shot("practice battle")
    await ev("if(BT){BT.headless=true;for(let i=0;i<9000&&!BT.over;i++)stepBattle(1/15);BT.headless=false;if(!BT.over)finishBattle(true);}1",6000);await shot("battle result")
    json.dump(names,open(f"/tmp/am_{tag}.json","w"),ensure_ascii=False)
    print(n[0],"shots");print("errs",errs[:12]);await b.close()
asyncio.run(m(sys.argv[1]=="m",sys.argv[2]))
