// 왕 걷기, 방패와 망토, 말 탄 높이를 게임 탭에서 재는 도구 (2026-11-27, 팀원 6)
// 게임 페이지 콘솔에서: await import('/tools/model/king_probe.js') 또는 <script> 로 읽은 뒤 KP.* 를 쓴다
(function(){
const V3=()=>new THREE.Vector3();
const comp=(a,i,k)=>k===0?a.getX(i):k===1?a.getY(i):k===2?a.getZ(i):a.getW(i);
const KP=window.KP={};
// 스킨 적용 후 점 위치(월드). filter(v,i,o) 통과한 것만
KP.skv=function(root,filter){root.updateMatrixWorld(true);const out=[];root.traverse(o=>{if(!o.isSkinnedMesh||!o.visible)return;o.skeleton.update();const p=o.geometry.attributes.position;for(let i=0;i<p.count;i++){const v=V3().fromBufferAttribute(p,i);o.boneTransform(i,v);v.applyMatrix4(o.matrixWorld);if(!filter||filter(v,i,o))out.push(v);}});return out;};
// 뼈 몫으로 고른 점 번호: {mesh:[idx...]}
KP.byWeight=function(root,re,minW){const r=new Map();root.traverse(o=>{if(!o.isSkinnedMesh)return;const si=o.geometry.attributes.skinIndex,sw=o.geometry.attributes.skinWeight,ok=o.skeleton.bones.map(b=>re.test(b.name)),out=[];for(let i=0;i<si.count;i++){let w=0;for(let j=0;j<4;j++)if(ok[comp(si,i,j)])w+=comp(sw,i,j);if(w>=minW)out.push(i);}r.set(o,out);});return r;};
KP.pos=function(root,sel){root.updateMatrixWorld(true);const out=[];for(const [o,idx] of sel){o.skeleton.update();const p=o.geometry.attributes.position;for(const i of idx){const v=V3().fromBufferAttribute(p,i);o.boneTransform(i,v);v.applyMatrix4(o.matrixWorld);out.push(v);}}return out;};
KP.bone=(root,re)=>{let b=null;root.traverse(o=>{if(!b&&o.isBone&&re.test(o.name))b=o;});return b;};
// 동작 하나만 입혀 t초 자세로
KP.pose=function(h,clip,t,keep){const H=h.userData.hero;H.mixer.stopAllAction();const c=typeof clip==="string"?retarget(clip,h.children[0]):clip;const a=H.mixer.clipAction(c);a.reset();a.setEffectiveWeight(1);a.play();H.mixer.setTime(t);h.updateMatrixWorld(true);return a;};
// 소리 끄고 이어하기로 왕궁에 들어간다
KP.enter=async function(){const w=ms=>new Promise(r=>setTimeout(r,ms));const mute=()=>{try{musSet(false);sfxSet(false);MUS.ctx&&MUS.ctx.suspend();}catch(e){}};mute();
  document.querySelector('[data-a=continue]').click();await w(3500);document.querySelector('[data-a=gateSkip]')?.click();await w(2500);S.paused=false;mute();};
// 창이 가려져 있으면 게임 루프가 멈추므로 손으로 프레임을 돌린다(시각 KP.T로 고정, 사건 창이 뜨지 않게)
// 시험 중 사건 창이 뜨면 "나중에 듣는다"로 닫는다(로컬 시험 저장에만 남는다)
KP.later=function(){if(!UI.modalOpen)return false;const b=[...document.querySelectorAll('button.evopt')].find(e=>e.offsetParent&&e.textContent.trim().startsWith("나중에 듣는다"));if(b){b.click();S.paused=false;return true;}return false;};
KP.T=0.33;KP.step=function(n,dt=1/30,each){for(let i=0;i<n;i++){if(UI.modalOpen)KP.later();S.t=KP.T;E.t+=dt;WIND.t.value=E.t;VAT_T.value=E.t;E.onFrame(dt);if(E.camMode==="tp")E.tp.update(dt);if(each)each(i);}S.t=KP.T;renderFrame(E.scene,E.cam,E.t);};
KP.run=(keys,n,warm,f,loopZ=true)=>{E.keys.clear();keys.forEach(k=>E.keys.add(k));const g=[];const wrap=()=>{if(loopZ&&CAP.pos.z<45)CAP.pos.z=60;};KP.step(warm,1/30,wrap);KP.step(n,1/30,()=>{wrap();g.push(f());});E.keys.clear();return {min:+Math.min(...g).toFixed(3),max:+Math.max(...g).toFixed(3),spd:+KC.spd.toFixed(1),h:KC.horse&&KC.horse.userData.hero.cur,k:KC.model.userData.hero.cur};};
// 말 위 틈: 왕 가랑이(엉덩이, 허벅지 몫 0.6, 두 허벅지 사이 12cm, 엉덩이 30cm 안) 가장 낮은 점과 그 바로 아래 말 등 겉면(가로 9cm 안 가장 높은 점). 음수면 말 등에 파묻힘
KP.gapRide=function(m,horse){m.updateMatrixWorld(true);horse.updateMatrixWorld(true);const inv=m.matrixWorld.clone().invert();const hp=KP.bone(m,/Hips$/).getWorldPosition(V3());const hpl=hp.clone().applyMatrix4(inv);
  if(!KP._sel||KP._selM!==m){KP._sel=KP.byWeight(m,/(UpLeg|Hips)$/,0.6);KP._selM=m;}
  let lo=null;for(const v of KP.pos(m,KP._sel)){const l=v.clone().applyMatrix4(inv);if(Math.abs(l.x-hpl.x)>0.12||v.distanceTo(hp)>0.3*m.getWorldScale(V3()).x)continue;if(!lo||v.y<lo.y)lo=v;}
  let top=-9;for(const v of KP.skv(horse,v=>Math.hypot(v.x-lo.x,v.z-lo.z)<0.09))top=Math.max(top,v.y);return lo.y-top;};
// 말 위 틈(독립 확인용): 지금 자세에서 엉덩이 가운데 가로 20cm, 36cm 안의 엉덩이, 허벅지 점마다 같은 6cm 칸의 말 몸 전체 가장 높은 점과의 틈, 그 가장 작은 값
KP.gapRide2=function(m,horse){m.updateMatrixWorld(true);horse.updateMatrixWorld(true);const inv=m.matrixWorld.clone().invert();const hp=KP.bone(m,/Hips$/).getWorldPosition(V3()),hpl=hp.clone().applyMatrix4(inv);
  if(!KP._sel||KP._selM!==m){KP._sel=KP.byWeight(m,/(UpLeg|Hips)$/,0.6);KP._selM=m;}
  const rid=new Set();m.traverse(o=>rid.add(o));const hsc=horse.getWorldScale(V3()).x;
  const G=new Map();for(const v of KP.skv(horse,(v,i,o)=>!rid.has(o)&&!/hair/i.test(o.material.name)&&Math.hypot(v.x-hp.x,v.z-hp.z)<0.6*hsc)){const k=Math.round(v.x/0.06)+","+Math.round(v.z/0.06);if(!(G.get(k)>v.y))G.set(k,v.y);}
  const hinv=horse.matrixWorld.clone().invert();let c=9;for(const v of KP.pos(m,KP._sel)){const hl=v.clone().applyMatrix4(hinv);if(Math.abs(hl.x)>0.16||v.distanceTo(hp)>0.45*m.getWorldScale(V3()).x||v.y>hp.y)continue;   /* 엉덩이에서 50cm 넘게 앞(월드)은 투구 왕 치마 앞자락 끝(51057 등 점 4개)이 말 기갑 속에 숨는 것뿐이라 뺀다 */const t=G.get(Math.round(v.x/0.06)+","+Math.round(v.z/0.06));if(t!==undefined&&v.y-t<c)c=v.y-t;}return c;};
// 말 위 동작 모음: 서기, 속보, 질주, 질주 중 베기, 선 채 베기(질주 뒤), 찌르기를 times번 되풀이해 가장 작은, 큰 틈
KP.rideTest=function(times=2){const f=()=>KP.gapRide2(KC.model,KC.horse);const acc={};const add=(k,r)=>{const a=acc[k]||(acc[k]=[9,-9]);a[0]=Math.min(a[0],r.min);a[1]=Math.max(a[1],r.max);};
  for(let n=0;n<times;n++){CAP.pos.x=0;CAP.pos.z=60;add("idle",KP.run([],3,20,f));add("trot",KP.run(["w"],8,40,f));add("gal",KP.run(["w","shift"],8,60,f));KC.wantAtk=1;add("atkGal",KP.run(["w","shift"],20,1,f));KC.wantAtk=1;add("atkStop",KP.run([],20,1,f));KC.wantKick=true;add("stab",KP.run([],12,1,f));add("turn",KP.run(["a","w"],10,20,f));}
  const o={};for(const k in acc)o[k]=acc[k][0].toFixed(3)+"~"+acc[k][1].toFixed(3);return o;};
// 군중 기수 틈(독립 확인용): 그 순간 말과 기수의 구운 점 전체를 풀어, 말 기준 가운데 띠(가로 16cm)에 든 기수 점(발 아래쪽 제외: 말 등 높이 - 40cm 위)마다 같은 6cm 칸 말 꼭대기와의 틈, 가장 작은 값
KP.crowdGap=function(cr,kind,vi,t0,sp){const hb=cr.bk,rb=cr.rider.bk,hs=cr.scale,rs=cr.rider.scale;const hc=(hb.clips[cr.rider&&(kind==="attack"||kind==="sneak"||kind==="melee")?"idle":kind]||hb.clips.idle),c=hc[vi%hc.length];const rL=rb.clips[kind]||rb.clips.idle,rc=rL[vi%rL.length];
  const a=vatFrame(c,t0,sp),b=vatFrame(rc,t0,sp);const fa=a[2]<0.5?a[0]:a[1],fb=b[2]<0.5?b[0]:b[1];
  // 기수 놓인 높이: push가 넣는 값(가까운 프레임 짝)
  const yy=crowdSeatYY(cr.seat,fa,fb);
  const G=new Map();let maxTop=-9;for(let i=0;i<hb.V;i++){const x=vatP(hb,fa,i,0)*hs,z=vatP(hb,fa,i,2)*hs;if(Math.abs(x)>0.4||Math.abs(z)>0.9)continue;const y=vatP(hb,fa,i,1)*hs;const k=Math.round(x/0.06)+","+Math.round(z/0.06);if(!(G.get(k)>y))G.set(k,y);if(Math.abs(x)<0.1)maxTop=Math.max(maxTop,y);}
  let cl=9;for(let i=0;i<rb.V;i++){const x=vatP(rb,fb,i,0)*rs;if(Math.abs(x)>0.16)continue;const y=vatP(rb,fb,i,1)*rs+yy;if(y<maxTop-0.4)continue;const z=vatP(rb,fb,i,2)*rs;const t=G.get(Math.round(x/0.06)+","+Math.round(z/0.06));if(t!==undefined&&y-t<cl)cl=y-t;}return cl;};
// 방패가 등 뒤(망토 쪽)로 넘어간 정도: 몸 앞 방향(망토 무게중심 → 엉덩이)으로 엉덩이보다 lim 넘게 뒤에 있는 방패 점 수와 가장 뒤 깊이. window._cape, window._shield(점 번호)를 먼저 골라 둔다
KP.behind=function(k,lim){k.updateMatrixWorld(true);const inv=k.matrixWorld.clone().invert();const hip=KP.bone(k,/Hips$/).getWorldPosition(V3()).applyMatrix4(inv);
  const cp=KP.pos(k,window._cape).map(v=>v.applyMatrix4(inv));const cc=V3();cp.forEach(v=>cc.add(v));cc.multiplyScalar(1/cp.length);const f=hip.clone().sub(cc).setY(0).normalize();
  const sp=KP.pos(k,window._shield).map(v=>v.applyMatrix4(inv));let n=0,mn=9;for(const v of sp){const d=v.clone().sub(hip).dot(f);mn=Math.min(mn,d);if(d<lim)n++;}return [n,+mn.toFixed(2)];};
// 칼날 점: 게임이 쥐여 준 칼(보이는 prop sword의 점) + 투구 왕처럼 모델에 붙은 칼(오른손 몫 0.99 넘고 손에서 25cm 넘게 떨어진 점)
KP.blade=function(m){m.updateMatrixWorld(true);const out=[];m.traverse(o=>{if(o.userData&&o.userData.prop==="sword"&&o.visible){o.traverse(x=>{if(x.isMesh&&x.visible){const p=x.geometry.attributes.position;for(let i=0;i<p.count;i++)out.push(V3().fromBufferAttribute(p,i).applyMatrix4(x.matrixWorld));}});}});
  if(m.userData.helmet){if(!m.userData._bladeSel){const sel=KP.byWeight(m,/RightHand$/,0.99);const h=KP.bone(m,/RightHand$/).getWorldPosition(V3());const s2=new Map();for(const [o,idx] of sel){const ps=KP.pos(m,new Map([[o,idx]]));s2.set(o,idx.filter((i,j)=>ps[j].distanceTo(h)>0.25*m.scale.x));}m.userData._bladeSel=s2;}out.push(...KP.pos(m,m.userData._bladeSel));}
  return out;};
// 말 몸 안에 든 칼날 점 수: 말 기준 6cm 칸(x,z)마다 말 점의 가장 낮은, 높은 높이 사이에 있고, 칸 둘레 8칸에도 말이 있는 점(가장자리 오판 줄임)
KP.swordIn=function(m,horse){const rid=new Set();m.traverse(o=>rid.add(o));horse.updateMatrixWorld(true);const inv=horse.matrixWorld.clone().invert();const G=new Map();
  for(const v of KP.skv(horse,(v,i,o)=>!rid.has(o)&&!/hair/i.test(o.material.name))){const l=v.clone().applyMatrix4(inv);const k=Math.round(l.x/0.06)*4096+Math.round(l.z/0.06);const g=G.get(k);if(!g)G.set(k,[l.y,l.y]);else{g[0]=Math.min(g[0],l.y);g[1]=Math.max(g[1],l.y);}}
  let n=0,deep=0;const bl=KP.blade(m);for(const v of bl){const l=v.clone().applyMatrix4(inv);const cx=Math.round(l.x/0.06),cz=Math.round(l.z/0.06);const g=G.get(cx*4096+cz);if(!g||l.y<g[0]||l.y>g[1])continue;let ok=true;for(const [a,b] of [[1,0],[-1,0],[0,1],[0,-1]])if(!G.has((cx+a)*4096+cz+b))ok=false;if(ok){n++;deep=Math.max(deep,Math.min(l.y-g[0],g[1]-l.y));}}return [n,+deep.toFixed(2),bl.length];};
// 전투 연습(들판 회전)에 들어간다, 전투 왕을 다른 갑주로 바꾼다("old" = 선왕)
KP.practice=async function(){const w=ms=>new Promise(r=>setTimeout(r,ms));try{musSet(false);sfxSet(false);MUS.ctx&&MUS.ctx.suspend();}catch(e){}
  document.querySelector('[data-a=gateSkip]')?.click();await w(1200);document.querySelector('[data-a=practice]').click();await w(1500);document.querySelector('[data-a=gateSkip]')?.click();await w(1200);document.querySelector('[data-a=practiceGo]').click();await w(7000);document.querySelector('[data-a=bbegin]')?.click();await w(1000);
  const b=[...document.querySelectorAll('button')].find(b=>b.offsetParent&&b.textContent.trim()==="알겠다");if(b)b.click();await w(300);KP.step(5);};
KP.battleKing=function(kind){let n;if(kind==="old"){const p0=S.prologue;S.prologue=true;n=makeKing("ashen");S.prologue=p0;}else n=makeKing(kind);const o=BR.king;n.position.copy(o.position);o.parent.add(n);o.parent.remove(o);BR.king=n;KC.model=n;KP.step(3);return n;};
KP.swTestB=function(){const f=()=>KP.swordIn(KC.model,KC.horse)[0];const r={};const R=(k,x)=>r[k]=x.min+"~"+x.max+" "+x.k+" "+x.spd;R("idle",KP.run([],4,20,f,false));R("trot",KP.run(["w"],10,40,f,false));R("gal",KP.run(["w","shift"],10,50,f,false));R("turn",KP.run(["a","w","shift"],10,10,f,false));KC.wantAtk=1;R("atkGal",KP.run(["w","shift"],30,1,f,false));KC.wantAtk=1;R("atk",KP.run([],30,1,f,false));KC.wantKick=true;R("stab",KP.run([],16,1,f,false));R("after",KP.run([],10,10,f,false));return r;};
// 따로 그리기: 화면 위에 캔버스를 얹어 objs만 그린다(cam 위치, look 지점)
KP.dots=function(k,sel,col){const ps=KP.pos(k,sel);const g=new THREE.BufferGeometry().setFromPoints(ps);const p=new THREE.Points(g,new THREE.PointsMaterial({color:col,size:0.012,depthTest:false}));p.renderOrder=9;return p;};
KP.draw=function(objs,cam,look){if(!KP.R){const c=document.createElement('canvas');c.width=1200;c.height=700;c.style.cssText='position:fixed;left:0;top:0;z-index:99999;width:100vw';document.body.appendChild(c);KP.cv=c;KP.R=new THREE.WebGLRenderer({canvas:c,antialias:true,preserveDrawingBuffer:true});KP.S=new THREE.Scene();KP.S.background=new THREE.Color(0x8a8a90);KP.S.add(new THREE.HemisphereLight(0xffffff,0x444444,2.2));const d=new THREE.DirectionalLight(0xffffff,2);d.position.set(2,4,3);KP.S.add(d);}
  KP.cv.style.height=(innerWidth*700/1200)+'px';KP.S.children.forEach(o=>{if(!o.isLight)KP.S.remove(o);});objs.forEach(o=>KP.S.add(o));const c=new THREE.PerspectiveCamera(30,1200/700,0.05,50);c.position.set(...cam);c.lookAt(new THREE.Vector3(...look));KP.R.render(KP.S,c);KP.cv.style.display='block';};
KP.hide=()=>{if(KP.cv)KP.cv.style.display='none';};
// 땅에 닿은 발이 땅 위에서 미끄러지는 속도(월드, 초속 m): 낮은 발의 월드 위치 변화. secs 동안 매 프레임 잰다
KP.slide=async function(m,secs){const H=m.userData.hero;const L=KP.bone(m,/LeftFoot$/),R=KP.bone(m,/RightFoot$/);const v=[];let pl=null,pr=null,t0=performance.now(),last=t0;
  while(performance.now()-t0<secs*1000){await new Promise(r=>requestAnimationFrame(r));const now=performance.now(),dt=(now-last)/1000;last=now;m.updateMatrixWorld(true);const l=L.getWorldPosition(new THREE.Vector3()),r=R.getWorldPosition(new THREE.Vector3());
    if(pl){const lo=l.y<r.y?[l,pl]:[r,pr];const s=Math.hypot(lo[0].x-lo[1].x,lo[0].z-lo[1].z)/Math.max(dt,1e-3);v.push(s);}pl=l;pr=r;}
  v.sort((a,b)=>a-b);return {med:+v[Math.floor(v.length/2)].toFixed(2),p25:+v[Math.floor(v.length/4)].toFixed(2),cur:H.cur,ts:+(H.acts[H.cur]&&H.acts[H.cur].timeScale||0).toFixed(2),spd:+KC.spd.toFixed(2)};};
})();
