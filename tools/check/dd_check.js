// Deep Dark 자동 화면 투어와 자동 검사 (2026-11-27, 팀원 7)
// 쓰는 법은 tools/check/README.md. 게임 페이지(http://localhost:8777/index.html, serve.py)에서 읽는다:
//   await new Promise(r=>{const s=document.createElement('script');s.src='/tools/check/dd_check.js?'+Date.now();s.onload=r;document.head.appendChild(s);});
//   await DDC.all('2026-11-27_1')      // 투어 + 검사 + 비교 페이지 (판 이름은 영문, 숫자, _, -)
// 창이 가려져 있어도 되게 게임 프레임을 손으로 돌린다(DDC.step). 저장은 막는다(이어하기 저장을 덮어쓰지 않는다).
(function(){
const V3=()=>new THREE.Vector3();
const D=window.DDC={run:null,errs:[],shots:[],res:[],T:0.33};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
const $$=s=>[...document.querySelectorAll(s)];
D.post=async(path,body,q={})=>{const qs=new URLSearchParams({run:D.run,...q}).toString();for(let i=0;i<4;i++){try{const r=await fetch(`/check/${path}?${qs}`,{method:"POST",body});return await r.json();}catch(e){if(i===3)throw e;await wait(400);}}};   // 서버가 잠깐 바쁘면 다시

/* ── 준비: 소리 끄기, 저장 막기, 오류 모으기 ── */
D.mute=()=>{try{musSet(false);sfxSet(false);MUS.ctx&&MUS.ctx.suspend();}catch(e){}};
D.guard=function(){D.mute();if(D._g)return;D._g=1;
  Storage.prototype.setItem=function(){D.blocked=(D.blocked||0)+1;};   // 이 탭 안에서는 아무것도 저장하지 않는다
  window.saveGame=async function(){};
  const ce=console.error;console.error=function(...a){D.errs.push(a.map(x=>String(x&&x.message||x)).join(" ").slice(0,160));return ce.apply(console,a);};
  addEventListener("error",e=>D.errs.push("ERR "+e.message));addEventListener("unhandledrejection",e=>D.errs.push("REJ "+String(e.reason&&e.reason.message||e.reason).slice(0,160)));};

/* ── 프레임 돌리기 (사건 창은 닫는다) ── */
D.closeEvents=()=>{if(!UI.modalOpen)return;const tn=$$('[data-a=tutNo]').find(e=>e.offsetParent);if(tn){tn.click();UI.modalBlocking=false;}const b=$$('button.evopt').find(e=>e.offsetParent&&/나중에|later/i.test(e.textContent));if(b)b.click();else if(!UI.modalBlocking)UI.closeModal();if(S)S.paused=false;};
D.step=function(n=1,dt=1/30,keys,each){if(keys){E.keys.clear();keys.forEach(k=>E.keys.add(k));}
  for(let i=0;i<n;i++){D.closeEvents();if(S&&D.T!=null)S.t=D.T;E.t+=dt;WIND.t.value=E.t;VAT_T.value=E.t;
    if(typeof cullUpdate==="function")cullUpdate(E.cam,(UI.mode==="capital"||UI.mode==="palace")?70:Infinity);
    try{E.onFrame&&E.onFrame(dt);}catch(e){D.errs.push("frame "+e.message);}
    if(E.camMode==="tp")E.tp.update(dt);else if(E.camMode!=="free")E.ctrl.update(dt);if(each)each(i);}
  if(keys)E.keys.clear();if(S&&D.T!=null)S.t=D.T;};
D.render=()=>{renderFrame(E.scene,E.cam,E.t);};

/* ── 사진: 3D 화면만(글씨, 단추는 검사로 잰다) ── */
D.shot=async function(name,title){D.render();const url=E.renderer.domElement.toDataURL("image/jpeg",0.8);D.shots.push(name);
  if(D.run)await D.post("shot",url,{name,title});return url.length;};
D.both=async function(name,title,warm=8){for(const [T,s,t] of [[0.95,"_night"," (밤)"],[0.33,"_day"," (아침)"]]){D.T=T;if(S)S.t=T;if(UI.mode==="battle"&&typeof BR!=="undefined"&&BR.lights)dayNight(BR.lights,BR.sky,E.scene,null,null);D.step(warm);await D.shot(name+s,title+t);}};   /* 전투는 빛을 싸움 시작 때 한 번만 정하니 시각을 바꾼 뒤 다시 맞춘다 */
D.aspect=function(w,h){const p=E.canvas.parentElement;if(w){p.style.width=w+"px";p.style.height=h+"px";}else{p.style.width="";p.style.height="";}resizeEngine();};

/* ── 장면 이동 ── */
D.newGame=async function(){if(UI.mode!=="title")return;startNewGame(false);   // 로그인 문(gateThen)을 건너 새 판(프롤로그 없이)for(let i=0;i<30&&UI.mode!=="capital";i++){await wait(500);D.closeEvents();$$('[data-a=gateSkip]').forEach(b=>b.click());}
  for(let i=0;i<6;i++){UI.closeModal&&UI.closeModal();const y=$$('button').find(b=>b.offsetParent&&/혼자|myself|alone/i.test(b.textContent));if(y)y.click();await wait(200);}if(S){S.paused=false;S.hints=Object.fromEntries(Object.keys(HINTS).map(k=>[k,1]));}D.mute();};
D.cap=function(x,z,face,yaw,pitch=0.28,dd=7){if(UI.mode!=="capital"){if(UI.mode==="palace")leavePalace();else enterCapital();}if(KC.mounted&&!D.keepHorse)capMount();
  CAP.pos.x=x;CAP.pos.z=z;KC.face=face;CAP.face=face;E.tp.yaw=yaw;E.tp.pitch=pitch;E.tp.dd=E.tp.dist=dd;E.tp.manualT=9;E.tp.snap=true;D.step(10,1/30,null,()=>{E.tp.manualT=9;});};
D.walkCap=function(z,keys=["w"]){let n=0;const off=()=>UI.mode==="palace"?PAL.pos.z-(PT.zp-PT.zc):CAP.pos.z;while(n<500&&off()>z){D.step(1,1/30,keys);n++;}return n;};
D.battleWait=async function(){for(let i=0;i<40&&UI.mode!=="battle";i++){await wait(300);}for(let i=0;i<10;i++){D.closeEvents();const b=$$('[data-a=bbegin]').find(b=>b.offsetParent);if(b)b.click();const ok=$$('button').find(b=>b.offsetParent&&/^(알겠다|OK)$/.test(b.textContent.trim()));if(ok)ok.click();await wait(150);}D.mute();};

/* ── 투어 ── */
D.SCENES=[];const sc=(name,title,fn)=>D.SCENES.push({name,title,fn});
sc("title_16x9","처음 화면 16:9",async()=>{D.aspect(1280,720);await D.both("title_16x9","처음 화면 16:9",30);});
sc("title_4x3","처음 화면 4:3",async()=>{D.aspect(1024,768);await D.both("title_4x3","처음 화면 4:3",30);});
sc("title_phone","처음 화면 휴대폰 가로",async()=>{D.aspect(812,375);await D.both("title_phone","처음 화면 휴대폰 가로 812x375",30);D.aspect();});
sc("newgame","",async()=>{D.aspect(1280,720);await D.newGame();});
sc("cap_yard","왕궁 마당",async()=>{D.cap(0,-50,Math.PI,0.25,0.3,9);await D.both("cap_yard","왕궁 마당(성채 앞, 계단 위)");});
sc("cap_stair","신전 계단과 기둥",async()=>{const zf=STAIR.z0-STAIR.L;D.cap(-4,zf+6,Math.PI*0.85,0.7,0.2,7);await D.both("cap_stair","신전 계단 위 돌기둥");});
sc("door_front","대전 문 앞(문 열림)",async()=>{D.cap(0.3,-75,Math.PI,0,0.28,7);D.step(30);await D.both("door_front","대전 문 앞, 문 열림, 문 너머 대전");});
sc("door_cross","대전 문 지나는 순간",async()=>{D.cap(0.3,-77,Math.PI,0,0.28,7);D.walkCap(-83.6);await D.both("door_cross","대전 문을 막 넘은 순간(카메라는 아직 밖)",1);});
sc("palace_in","대전 안",async()=>{if(UI.mode!=="palace")enterPalace();PAL.pos.x=0;PAL.pos.z=8;PAL.face=Math.PI;E.tp.yaw=0;E.tp.snap=true;D.step(10);await D.both("palace_in","대전 안(왕좌 쪽)");
  PAL.pos.z=17;PAL.face=0;E.tp.yaw=Math.PI;E.tp.manualT=9;E.tp.snap=true;D.step(40,1/30,null,()=>{E.tp.manualT=9;});await D.both("palace_door_in","대전 안에서 문 쪽(문 너머 왕궁)");});
sc("horse","말 탄 왕",async()=>{D.cap(CAP.horsePos.x,CAP.horsePos.z+0.1,0,Math.PI,0.25,9);if(!KC.mounted)capMount();D.keepHorse=1;CAP.pos.x=0;CAP.pos.z=40;KC.face=0;E.tp.yaw=Math.PI/2;E.tp.manualT=9;E.tp.snap=true;D.step(30,1/30,["w"],()=>{E.tp.manualT=9;E.tp.yaw=KC.face+Math.PI/2;});
  await D.both("horse_side","말 탄 왕(옆)",2);E.tp.yaw=KC.face+Math.PI;E.tp.snap=true;D.step(2);await D.both("horse_back","말 탄 왕(뒤)",2);capMount();D.keepHorse=0;});
sc("walk","걷는 왕",async()=>{D.cap(0,30,0,Math.PI,0.25,6);D.step(30,1/30,["w"],()=>{E.tp.manualT=9;E.tp.yaw=KC.face+Math.PI-0.7;});await D.both("walk_leftback","걷는 왕(왼쪽 뒤)",2);});
sc("market","시장",async()=>{D.cap(22,6,Math.PI/2,-Math.PI/2+0.3,0.3,9);await D.both("market","시장 노점");});
sc("gate","정문",async()=>{D.cap(0,CAP_R-28,0,Math.PI,0.15,9);await D.both("gate","정문(안쪽에서)");});
sc("map","지도",async()=>{openMap();D.step(5);const set=(s,d)=>{E.ctrl.set(s.x,s.z+d*0.4,d,0,0.95,true);D.step(10);};
  const cap=siteById("capital");set(cap,260);await D.both("map_capital","지도: 왕도 둘레");
  const v=SITES.filter(s=>s.kind==="village").slice(0,2);for(const s of v){set(s,160);await D.both("map_"+s.id,"지도: "+s.name);}
  const th=SITES.find(s=>s.kind==="throne");if(th){set(th,220);await D.both("map_throne","지도: 망자의 왕좌");}});
sc("city","도시 화면",async()=>{const v=SITES.find(s=>s.kind==="village");enterSiteView(v.id);D.step(20);await D.both("city_"+v.id,"도시 화면: "+v.name);});
const battle=(name,title,start)=>sc(name,title,async()=>{UI.closeModal&&UI.closeModal();start();await D.battleWait();await wait(1500);D.step(200,1/30);   /* 전투가 자리 잡은 뒤(약 7초) 찍고 잰다: 성벽 모델이 늦게 오고 성벽 위 디딜 곳 표를 만드는 데 1초 안팎 걸린다 */await D.both(name,title,10);
  if(D.battleProbe)D.battleProbe(name);});
battle("battle_city","도시 방어전",()=>practiceStart("village"));
for(const L of [0,1,2,3])battle("battle_walls"+L,"왕궁 방어전 성벽 "+L+"단계",()=>{practiceStart("siege");S.bld.walls=L;});
battle("battle_prologue","프롤로그 전투",()=>startPrologue());
battle("battle_throne","망자의 왕좌 전투",()=>{practiceStart("gen");UI.closeModal();const a=WAR.ourArmy;startBattle({kind:"assault",site:"f_throne",our:a,foes:S.sites.f_throne.garrison,title:"망자의 왕좌 (확인)"});});

D.tour=async function(only){D.guard();for(const s of D.SCENES){if(only&&!only.includes(s.name))continue;try{await s.fn();}catch(e){D.errs.push("scene "+s.name+": "+e.message);}}D.aspect();};
/* 영어판: en.html에서 따로 부른다 (DDC.tourEn) */
D.tourEn=async function(){D.guard();D.aspect(1280,720);await D.both("en_title","영어판 처음 화면",30);await D.newGame();D.cap(0,-50,Math.PI,0.25,0.3,9);await D.both("en_capital","영어판 왕궁");D.aspect();};

/* ── 검사 ── */
const R=(id,name,pass,value,limit)=>{D.res.push({id,name,pass,value,limit});return pass;};
D.ck={};
// 1. 방패가 망토 뒤로 넘어가는지 (팀원 6 KP.behind와 같은 방법, 점은 무게로 고름)
D.ck.shield=function(){const k=CAP.king;if(!window.KP||!k.userData.helmet)return R("shield","방패가 망토 뒤로 넘어감(걷기, 달리기)",null,"투구 왕 아님 또는 KP 없음","");
  if(!window._shield){const arm=KP.bone(k,/LeftForeArm$/),hand=KP.bone(k,/LeftHand$/);const sel=KP.byWeight(k,/LeftForeArm$/,0.99);const out=new Map();k.updateMatrixWorld(true);const a=arm.getWorldPosition(V3()),b=hand.getWorldPosition(V3());const ab=b.clone().sub(a);
    for(const [o,idx] of sel){const ps=KP.pos(k,new Map([[o,idx]]));out.set(o,idx.filter((i,j)=>{const p=ps[j].clone().sub(a);const t=Math.max(0,Math.min(1,p.dot(ab)/ab.lengthSq()));return p.distanceTo(ab.clone().multiplyScalar(t))>0.12*k.scale.x;}));}window._shield=out;
    const inv=k.matrixWorld.clone().invert();const hip=KP.bone(k,/Hips$/).getWorldPosition(V3()).applyMatrix4(inv);const cs=KP.byWeight(k,/(Spine|Hips)$|Spine\d$/,0.99);const c2=new Map();for(const [o,idx] of cs){const ps=KP.pos(k,new Map([[o,idx]]));c2.set(o,idx.filter((i,j)=>ps[j].clone().applyMatrix4(inv).z<hip.z-0.12));}window._cape=c2;}
  let worst=0,depth=9;D.cap(0,30,0,Math.PI,0.25,6);for(const keys of [["w"],["w","shift"]]){D.step(40,1/30,keys,()=>{const [n,mn]=KP.behind(k,-0.12);worst=Math.max(worst,n);depth=Math.min(depth,mn);});}
  return R("shield","방패가 망토 뒤로 넘어감(걷기, 달리기)",worst===0,`넘어간 점 최대 ${worst}개, 가장 뒤 ${depth}m`,"0개");};
// 2. 걷기 배속과 발 미끄러짐
D.ck.walk=function(){const k=CAP.king,H=k.userData.hero;if(!H||!window.KP)return R("walk","걷기 배속, 발 미끄러짐",null,"KP 없음","");
  /* 1/120초 간격으로 재고, 디딘 발 = 가장 낮은 높이에서 1.5cm 안(땅에 붙어 있는 동안). 1/30초, 4cm로 재면 발이 땅에 닿고 떨어지는 순간이 섞여 실제보다 크게 나왔다 */
  const L=KP.bone(k,/LeftFoot$/),Rr=KP.bone(k,/RightFoot$/);const out={};for(const [nm,keys] of [["걷기",["w"]],["달리기",["w","shift"]]]){D.cap(0,20,0,Math.PI,0.25,6);let pl=null,pr=null;const v=[],ts=[];D.step(30,1/30,keys);
    D.step(150,1/120,keys,()=>{k.updateMatrixWorld(true);const l=L.getWorldPosition(V3()),r=Rr.getWorldPosition(V3());if(pl){const lo=l.y<r.y?[l,pl]:[r,pr];v.push([lo[0].y,Math.hypot(lo[0].x-lo[1].x,lo[0].z-lo[1].z)*120]);}pl=l;pr=r;const a=H.acts&&H.acts[H.cur];if(a)ts.push(a.timeScale);});
    const ymin=Math.min(...v.map(s=>s[0]));const c=v.filter(s=>s[0]<ymin+0.015).map(s=>s[1]).sort((a,b)=>a-b);ts.sort((a,b)=>a-b);out[nm]={slide:+c[c.length>>1].toFixed(2),ts:+(ts[ts.length>>1]||0).toFixed(2),spd:+KC.spd.toFixed(1)};}
  const ok=Object.values(out).every(o=>o.slide<0.6&&o.ts>0.7&&o.ts<1.4);return R("walk","걷기 배속, 발 미끄러짐",ok,Object.entries(out).map(([k,o])=>`${k} 초속 ${o.spd}m 배속 ${o.ts}, 디딘 발 ${o.slide}m/s`).join(" / "),"배속 0.7~1.4, 디딘 발 0.6m/s 아래");};
// 3. 왕이 기둥, 나무, 덤불, 건물을 뚫는지 (걷기, 말): 물건 둘레에서 물건 쪽으로 2초 걸어 들어가 몸 반지름 안에 막힌 칸이 남는지
D.ck.collide=function(){if(!OCC.g)capOccBuild();const tests=[];const zf=STAIR.z0-STAIR.L;for(const sx of [-1,1])tests.push({x:sx*(STAIR.hw+0.6),z:zf-1.2,nm:"계단 기둥"});
  const M=new THREE.Matrix4();for(const o of CAP.scene.children){if(!o.isInstancedMesh||o.userData.noOcc||o.instanceMatrix.usage===THREE.DynamicDrawUsage)continue;for(let i=0;i<o.count&&tests.length<14;i++){o.getMatrixAt(i,M);const x=M.elements[12],z=M.elements[14];if(Math.hypot(x,z)<CAP_R-15)tests.push({x,z,nm:"나무"});}}
  for(const c of CAP.colliders.filter(c=>!c.r&&!c.prop&&!c.keep).slice(0,10))tests.push({x:c.x,z:c.z,nm:"건물"});
  const res={};for(const ride of [false,true]){if(ride!==KC.mounted){if(ride){D.cap(CAP.horsePos.x,CAP.horsePos.z,0,Math.PI);capMount();D.keepHorse=1;}else{capMount();D.keepHorse=0;}}
    let bad=0,n=0;for(const t of tests){for(const a of [0,2.1,4.2]){const r0=t.nm==="건물"?14:4;CAP.pos.x=t.x+Math.sin(a)*r0;CAP.pos.z=t.z+Math.cos(a)*r0;const p=capCollide(CAP.pos.x,CAP.pos.z,kingPad(CAP.king)+(ride?0.45:0));if(Math.hypot(p.x-CAP.pos.x,p.z-CAP.pos.z)>0.05)continue;KC.face=a+Math.PI;E.tp.yaw=a;E.tp.manualT=9;
      D.step(40,1/30,["w"],()=>{E.tp.yaw=a;E.tp.manualT=9;});n++;const q=occPush(CAP.pos.x,CAP.pos.z,ride?0.6:0.25,ride?2:1);
      const inBox=CAP.colliders.some(c=>{if(c.r||c.prop)return false;const cs=Math.cos(c.ry),sn=Math.sin(c.ry),lx=(CAP.pos.x-c.x)*cs-(CAP.pos.z-c.z)*sn,lz=(CAP.pos.x-c.x)*sn+(CAP.pos.z-c.z)*cs;return Math.abs(lx)<c.hw-0.45&&Math.abs(lz)<c.hd-0.45;});if(q||inBox)bad++;}}res[ride?"말":"걷기"]=[bad,n];}
  if(KC.mounted){capMount();D.keepHorse=0;}
  return R("collide","왕이 기둥, 나무, 건물을 뚫음(걷기, 말)",Object.values(res).every(r=>r[0]===0),Object.entries(res).map(([k,r])=>`${k} ${r[0]}/${r[1]}번 뚫음`).join(", "),"0번");};
// 4, 5. 화면 아래 안내 글씨, 단추 겹침 (지금 창 크기에서. PC, 휴대폰 가로로 창 크기를 바꿔 두 번 부른다)
D.ck.overlap=function(tag){const vis=e=>{if(!e||e.hidden)return false;const s=getComputedStyle(e);if(s.display==="none"||s.visibility==="hidden"||+s.opacity<0.05)return false;const r=e.getBoundingClientRect();return r.width>2&&r.height>2;};
  const hit=(a,b)=>{const r=a.getBoundingClientRect(),q=b.getBoundingClientRect();return Math.max(0,Math.min(r.right,q.right)-Math.max(r.left,q.left))*Math.max(0,Math.min(r.bottom,q.bottom)-Math.max(r.top,q.top))>16;};
  const found=[];const scenes=[["왕궁 대장간 앞",()=>{const s=CAP.spots.find(s=>s.id==="forge");D.cap(s.x+0.4,s.z,0,Math.PI);}],["대전 문 앞",()=>D.cap(0.3,-77,Math.PI,0)],["왕궁 마당",()=>D.cap(0,-50,Math.PI,0.25)]];
  for(const [nm,go] of scenes){go();D.step(3);renderPrompt();lockTip();updateLabels();
    /* 화면 위에 뜬 모든 상자(위치가 absolute, fixed인 것): 화면 40% 넘게 덮는 틀, 3D 이름표(.lbl), 창(#modal) 안은 뺀다 */
    const A=innerWidth*innerHeight;const els=$$("body *").filter(e=>{if(e.closest(".lbl,#modal,#win,canvas")||e.tagName==="CANVAS")return false;const p=getComputedStyle(e).position;if(p!=="absolute"&&p!=="fixed")return false;if(!vis(e))return false;const r=e.getBoundingClientRect();return r.width*r.height<A*0.4&&r.width<innerWidth*0.7&&(e.textContent.trim()||e.tagName==="BUTTON");});   // 화면 너비 70% 넘는 줄(윗줄 틀 등)은 담는 틀이라 뺀다
    for(let i=0;i<els.length;i++)for(let j=i+1;j<els.length;j++){const a=els[i],b=els[j];if(a.contains(b)||b.contains(a))continue;if(hit(a,b))found.push(`${nm}: ${a.id||a.textContent.trim().slice(0,8)} × ${b.id||b.textContent.trim().slice(0,8)}`);}}
  return R("overlap_"+tag,`화면 글씨, 단추 겹침 (${tag} ${innerWidth}x${innerHeight})`,found.length===0,found.slice(0,6).join(" / ")||"겹침 없음","0곳");};
// 6. 말 위 높이: 왕, 기병 군중
D.ck.ride=function(){const out=[];let ok=true;if(window.KP){D.cap(CAP.horsePos.x,CAP.horsePos.z,0,Math.PI);if(!KC.mounted)capMount();D.keepHorse=1;CAP.pos.x=0;CAP.pos.z=40;let mn=9,mx=-9;
    for(const keys of [[],["w"],["w","shift"]])D.step(40,1/30,keys,(i)=>{if(i%4)return;const g=KP.gapRide2(KC.model,KC.horse);mn=Math.min(mn,g);mx=Math.max(mx,g);});capMount();D.keepHorse=0;out.push(`왕 ${mn.toFixed(3)}~${mx.toFixed(3)}m`);if(mn<-0.05||mx>0.05)ok=false;
    try{const cr=crowdsFor("cav",20)[0];let a=9,b=-9;for(const kind of ["idle","walk","run"]){const g=KP.crowdGap(cr,kind,0,E.t,1);a=Math.min(a,g);b=Math.max(b,g);}out.push(`기병 군중 ${a.toFixed(3)}~${b.toFixed(3)}m`);if(a<-0.05||b>0.05)ok=false;}catch(e){out.push("기병 군중 못 잼("+e.message.slice(0,40)+")");}}
  else return R("ride","말 위 높이",null,"KP 없음","");
  return R("ride","말 위 높이(엉덩이와 말 등 틈)",ok,out.join(", ")+" (선왕, 지도 모형은 투어 사진으로)","-0.05~0.05m");};
// 7. 왕궁 사람 크기: 군중 모델의 서 있는 키
D.ck.people=function(){const h2f=h=>{const s=(h&0x8000)?-1:1,e=(h>>10)&0x1f,m=h&0x3ff;return e===0?s*Math.pow(2,-14)*(m/1024):s*Math.pow(2,e-15)*(1+m/1024);};const out=[];let ok=true;
  for(const k in CAP.crowd||{}){const bk=CAP.crowd[k].bk,d=bk.texP.image.data,isH=d instanceof Uint16Array;const c=bk.clips.idle&&bk.clips.idle[0];const f0=c?c.start:0;const rows=Math.ceil(bk.V/bk.W);let mx=-9;
    const pts=[];for(let i=0;i<bk.V;i++){const o=((f0*rows*bk.W)+i)*4;pts.push(isH?h2f(d[o+1]):d[o+1]);}pts.sort((a,b)=>a-b);mx=pts[Math.floor(pts.length*0.995)];out.push(`${k} ${mx.toFixed(2)}`);if(mx<1.5)ok=false;}
  return R("people","왕궁 사람 키(군중 서 있는 자세)",ok,out.join(", "),"1.5m 넘게");};
// 8. 대전 문: 상호작용 단추가 뜨는지, 드나들 때 카메라가 튀는지
D.ck.door=function(){D.cap(0.3,-72,Math.PI,0,0.28,7);let prompt=0,maxJump=0,prev=null;const camC=()=>{const c=E.cam.position.clone();if(UI.mode==="palace"){c.z-=PT.zp-PT.zc;c.y+=PT.yc;}return c;};
  const watch=()=>{if(!$("#prompt").hidden)prompt++;const c=camC();if(prev)maxJump=Math.max(maxJump,c.distanceTo(prev));prev=c;};
  D.step(1);prev=camC();let n=0;while(UI.mode==="capital"&&n<400){D.step(1,1/30,["w"],watch);n++;}D.step(40,1/30,["w"],watch);
  PAL.face=0;E.tp.yaw=Math.PI;E.tp.snap=true;D.step(1);prev=camC();n=0;while(UI.mode==="palace"&&n<500){D.step(1,1/30,["w"],()=>{E.tp.yaw=Math.PI;E.tp.manualT=9;watch();});n++;}D.step(30,1/30,["w"],watch);
  return R("door","대전 문: 단추가 뜸, 드나들 때 카메라 튐",prompt===0&&maxJump<0.6,`단추 뜬 프레임 ${prompt}, 카메라 한 프레임 최대 이동 ${maxJump.toFixed(2)}m`,"0, 0.6m 아래");};
// 9. 칼이 말 몸을 뚫음 (말 탄 왕이 서기, 달리기, 베기)
D.ck.sword=function(){if(!window.KP)return R("sword","칼이 말 몸을 뚫음",null,"KP 없음","");D.cap(CAP.horsePos.x,CAP.horsePos.z,0,Math.PI);if(!KC.mounted)capMount();D.keepHorse=1;CAP.pos.x=0;CAP.pos.z=40;let worst=0;
  const f=()=>{worst=Math.max(worst,KP.swordIn(KC.model,KC.horse)[0]);};for(const [keys,atk] of [[[],0],[["w","shift"],0],[["w","shift"],1],[[],1]]){if(atk)KC.wantAtk=1;D.step(24,1/30,keys,(i)=>{if(i%2===0)f();});}capMount();D.keepHorse=0;
  return R("sword","칼이 말 몸을 뚫음(말 위 서기, 질주, 베기)",worst===0,`말 몸 속 칼 점 최대 ${worst}개`,"0개");};
// 10. 카메라가 건물 벽 속 (건물 둘레에서 8방향)
D.ck.camwall=function(){const boxes=CAP.colliders.filter(c=>!c.r&&!c.prop&&!c.keep&&Math.min(c.hw,c.hd)>=1.2);const inBox=(x,z)=>boxes.some(c=>{const cs=Math.cos(c.ry),sn=Math.sin(c.ry),lx=(x-c.x)*cs-(z-c.z)*sn,lz=(x-c.x)*sn+(z-c.z)*cs;return Math.abs(lx)<c.hw-0.3&&Math.abs(lz)<c.hd-0.3;});
  D.cap(0,30,0,Math.PI);let n=0,bad=0;for(const c of boxes){const cs=Math.cos(c.ry),sn=Math.sin(c.ry);for(const [u,v] of [[1,0],[-1,0],[0,1],[0,-1]]){const lx=u*(c.hw+0.8),lz=v*(c.hd+0.8),x=c.x+lx*cs+lz*sn,z=c.z-lx*sn+lz*cs;const p=capCollide(x,z,0.25);if(Math.hypot(p.x-x,p.z-z)>0.2)continue;CAP.pos.x=p.x;CAP.pos.z=p.z;
    for(let a=0;a<8;a++){E.tp.yaw=a*Math.PI/4;E.tp.snap=true;E.tp.dist=E.tp.dd=7;E.tp.update(1/60);n++;if(inBox(E.cam.position.x,E.cam.position.z))bad++;}}}
  return R("camwall","카메라가 건물 벽 속",bad===0,`${bad}/${n}번`,"0번");};
// 11, 12. 전투: 성벽, 탑 속 병사, 허공 병사, 도시 방어전 집 속 병사 (투어 전투 장면마다 부른다)
/* 전투 병사 검사: 게임이 그리는 높이(figY)와 성벽 두께(wIn, WALL_T)를 그대로 쓴다.
   성벽 속 = 성벽 위가 아닌 병사가 서 있는 성벽 두께 속(무너지지 않은 칸). 허공 = 성벽 높이로 그려지는데 발밑 1.2m 안에 아무 모양도 없음(아래로 광선). 집 속 = 도시 집 상자 속 */
D.battleProbe=function(name){try{const B=BT;if(!B||!B.sq)return;let air=0,n=0,inWall=0,inHouse=0,high=0;const houses=B.houses||[];const W=B.wall&&!B.wall.none;const T=W?WALL_T():0;
  const ray=new THREE.Raycaster();ray.far=1.6;const objs=[];E.scene.traverse(o=>{if(o.isMesh&&!o.isSkinnedMesh&&!(o.isInstancedMesh&&o.instanceMatrix.usage===THREE.DynamicDrawUsage)&&o.visible&&!(o.material&&o.material.transparent&&!o.material.depthWrite))objs.push(o);});
  for(const s of B.sq){if(s.dead||s.fled)continue;for(const f of (s.figs||[])){if(!f.alive)continue;n++;const x=f.x,z=f.z,g=bH(x,z);
    if(W){const top=onWallTop(s),y=figY(s,x,z);
      if(top&&y>g+1){high++;let any=false;for(const [ox,oz] of [[0,0],[0.35,0],[-0.35,0],[0,0.35],[0,-0.35]]){ray.set(new THREE.Vector3(x+ox,y+0.3,z+oz),new THREE.Vector3(0,-1,0));if(ray.intersectObjects(objs,false).length){any=true;break;}}if(!any)air++;   /* 발 둘레 다섯 곳 모두 비어야 허공 (가는 울타리, 발판에 빗나가지 않게) */}
      else if(!top&&!s.climbing){const w=wIn(x,z);if(w>0.3&&w<T-0.3&&wallUp(x,z))inWall++;}}
    for(const h of houses){const cs=Math.cos(h.ry||0),sn=Math.sin(h.ry||0),lx=(x-h.x)*cs-(z-h.z)*sn,lz=(x-h.x)*sn+(z-h.z)*cs;if(Math.abs(lx)<h.hw-0.4&&Math.abs(lz)<h.hd-0.4){inHouse++;break;}}}}
  D.res.push({id:"battle_"+name,name:"전투 "+name+": 허공, 성벽 속, 집 속 병사",pass:n?air+inWall+inHouse===0:null,value:n?`병사 ${n}명: 성벽 위 ${high}명 중 발밑이 빈 허공 ${air}, 성벽 두께 속 ${inWall}${W?"":"(성벽 없음)"}, 집 속 ${inHouse}(집 ${houses.length}채)`:"병사 위치를 찾지 못함",limit:"0명"});}catch(e){D.res.push({id:"battle_"+name,name:"전투 "+name,pass:null,value:"못 잼 "+e.message,limit:""});}};
// 13. 백성, 훈련병이 왕, 말 몸 속에 든 횟수 (걷기, 말 타기). 왕이 가는 길 앞에 백성 여덟을 세워 두고 3초 지나간다. 대전: 왕이 신하, 경비 쪽으로 걸어 들어갈 때 가장 가까운 거리
D.ck.crowd=function(){const res=[];let bad=0,n=0;for(const ride of [false,true]){D.cap(0,24,0,Math.PI,0.25,8);if(ride){D.cap(CAP.horsePos.x,CAP.horsePos.z,0,Math.PI);capMount();D.keepHorse=1;CAP.pos.x=0;CAP.pos.z=24;KC.face=0;}
    const ns=CAP.npcs.slice(0,8);ns.forEach((m,i)=>{m.x=((i%3)-1)*0.6;m.z=27+i*1.6;m.wait=0;m.t={x:m.x,z:m.z+40};});let b=0;
    D.step(90,1/30,["w"],()=>{E.tp.yaw=Math.PI;E.tp.manualT=9;for(const c of capBody())for(const m of CAP.npcs){if(Math.hypot(m.x-c.x,m.z-c.z)<c.r)b++;}n++;});res.push((ride?"말":"걷기")+" "+b+"번");bad+=b;if(ride){capMount();D.keepHorse=0;}}
  let pmin=9;if(typeof enterPalace==="function"){enterPalace();const T=[...PAL.court.map(c=>({x:c.x,z:c.z})),...PAL.guards.map(g=>({x:g.position.x,z:g.position.z}))];for(const t of T){PAL.pos.x=t.x;PAL.pos.z=t.z+2.4;PAL.face=Math.PI;E.tp.yaw=0;E.tp.snap=true;D.step(45,1/30,["w"],()=>{E.tp.yaw=0;E.tp.manualT=9;pmin=Math.min(pmin,Math.hypot(PAL.pos.x-t.x,PAL.pos.z-t.z));});}leavePalace();}
  return R("crowd","백성이 왕, 말 몸 속에 든 횟수 / 대전 신하, 경비와 왕 거리",bad===0&&pmin>=0.7,res.join(", ")+` / 대전 가장 가까운 거리 ${pmin.toFixed(2)}m`,"0번, 0.7m 넘게");};
D.ck.errors=function(){return R("errors","콘솔 오류",D.errs.length===0,D.errs.length?`${D.errs.length}건: `+[...new Set(D.errs.map(e=>e.slice(0,70)))].slice(0,4).join(" / "):"없음","0건");};

D.checks=async function(){D.guard();if(!window.KP)await new Promise(r=>{const s=document.createElement('script');s.src='/tools/model/king_probe.js?'+Date.now();s.onload=r;s.onerror=r;document.head.appendChild(s);});
  if(UI.mode==="title")await D.newGame();D.T=0.33;
  for(const k of ["shield","walk","collide","overlap","ride","people","door","sword","camwall","crowd"]){try{k==="overlap"?D.ck.overlap(innerWidth<900?"휴대폰 가로":"PC"):D.ck[k]();}catch(e){R(k,k,null,"못 잼: "+e.message.slice(0,80),"");}}};
D.finish=async function(){D.ck.errors();await D.post("result",JSON.stringify(D.res));return D.post("done","");};
D.all=async function(run){D.run=run;D.res=[];D.guard();await D.tour();await D.checks();return D.finish();};
})();
