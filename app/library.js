/* Piano Studio Next — 기본곡 보관함 + 악보 전체 화면 보기 (alpha.30)
 * 기본곡: Mutopia Project의 퍼블릭 도메인/CC BY-SA 악보(LilyPond)에서 만든 음표 데이터(app/library/*.json).
 * 기존 엔진 전역(project, addTrack, renderTracks, drawRoll, fitView, scheduleSave, buildScore, renderScore, loadVF, showOverlay …)만 사용.
 */
'use strict';
var PSN_LIB_INDEX=null;
async function psnLibIndex(){ if(PSN_LIB_INDEX) return PSN_LIB_INDEX; const r=await fetch('./app/library/index.json',{cache:'no-cache'}); if(!r.ok) throw new Error('index'); PSN_LIB_INDEX=await r.json(); return PSN_LIB_INDEX; }
function psnLibFmt(sec){ const m=Math.floor(sec/60), s=Math.round(sec%60); return m+':'+String(s).padStart(2,'0'); }
async function psnLibraryOpen(){ if(!project){ toast('먼저 곡을 열거나 새 곡을 만드세요.'); return; }
  showOverlay('기본곡 목록을 읽는 중…',null); let ix; try{ ix=await psnLibIndex(); }catch(e){ hideOverlay(); toast('기본곡 목록을 불러오지 못했어요. 인터넷에 한 번 연결한 뒤 다시 열어 주세요.'); return; }
  const esc=s=>String(s).replace(/</g,'&lt;'); const msg=$('#ovMsg'); const hasNotes=project.tracks.some(t=>t.notes.length);
  const byComp={}; ix.forEach(e=>{ (byComp[e.composer]=byComp[e.composer]||[]).push(e); });
  msg.innerHTML=`<b>기본곡 보관함</b> <span class="hint">· 야마하 P-70 내장곡 중 ${ix.length}곡 (퍼블릭 도메인 악보 기반)</span>
   <div class="hint" style="margin:4px 0 8px">${hasNotes?'지금 열린 곡에 오른손·왼손 트랙으로 추가돼요. 비교·연습용으로 쓰거나, 깨끗하게 쓰려면 먼저 ‘새 곡’을 만드세요.':'지금 열린 곡에 오른손·왼손 트랙으로 들어가고, 빠르기·박자·곡 이름도 맞춰져요.'}</div>
   <div class="sug-list" style="max-height:56vh">${Object.keys(byComp).map(c=>`<div style="font-weight:600;margin-top:6px">${esc(c)}</div>`+byComp[c].map(e=>`<label><span>#${e.p70} ${esc(e.title)}</span> <span class="hint">${psnLibFmt(e.duration)} · ${e.notes}음</span><button class="pv psnLibAdd" data-id="${esc(e.id)}">곡에 추가</button></label>`).join('')).join('')}</div>
   <div class="hint" style="margin-top:8px">악보 출처: Mutopia Project (퍼블릭 도메인 또는 CC BY-SA). 자세한 저작권 표시는 <a href="./app/LIBRARY_CREDITS.md" target="_blank" rel="noopener">LIBRARY_CREDITS.md</a>. 자동 변환이라 원곡 악보와 세부(꾸밈음·페달)는 다를 수 있어요.</div>`;
  const bx=$('#ovBtns'); bx.innerHTML=''; const c=document.createElement('button'); c.textContent='닫기'; c.className='on'; c.onclick=()=>{ hideOverlay(); msg.innerHTML=''; }; bx.append(c);
  msg.querySelectorAll('.psnLibAdd').forEach(b=>b.onclick=()=>psnLibraryAdd(b.dataset.id)); }
async function psnLibraryAdd(id){ const e=(PSN_LIB_INDEX||[]).find(x=>x.id===id); showOverlay('기본곡을 읽는 중…',null);
  let song; try{ const r=await fetch('./app/library/'+encodeURIComponent(id)+'.json',{cache:'force-cache'}); if(!r.ok) throw 0; song=await r.json(); }catch(err){ hideOverlay(); toast('이 곡 파일을 불러오지 못했어요.'); return; }
  const fresh=!project.tracks.some(t=>t.notes.length);
  if(fresh){ project.bpm=song.bpm; project.beatsPerBar=song.beatsPerBar; if($('#bpm')) $('#bpm').value=song.bpm; if($('#bpb')&&[...$('#bpb').options].some(o=>+o.value===song.beatsPerBar)) $('#bpb').value=song.beatsPerBar; if(typeof renderBeats==='function') renderBeats(); if(/^(LinuxPC|첫 번째 곡|곡 \d+|직접 입력|새 곡)/.test(project.name)||!project.name) { project.name=song.name; if($('#songName')) $('#songName').value=project.name; } }
  const made=[]; for(const tr of song.tracks){ if(!tr.notes.length) continue; const t=addTrack({name:(e?e.title:song.name)+' · '+tr.name,instrument:'piano',volume:.8,notes:tr.notes.map(([p,s,d,v,h])=>({id:nid(),p,s,d,v,h}))}); made.push(t); }
  if(made.length){ activeTrackId=made[0].id; }
  if(typeof selected!=='undefined') selected.clear(); renderTracks(); if(typeof fitView==='function') fitView(); drawRoll(); scheduleSave(); if(typeof refreshSongList==='function') refreshSongList();
  hideOverlay(); $('#ovMsg').innerHTML=''; toast(`‘${song.name}’을(를) 트랙 ${made.length}개로 넣었어요. ▶ 재생으로 들어보세요.`,5000); }

/* ---------- full-screen score reader: 1 page portrait, 2 pages landscape, tap left/right ---------- */
var PSN_SV={el:null,pages:[],page:0,tracks:'all',split:'hand',grid:1};
async function psnScoreFull(){ if(!project||!project.tracks.some(t=>t.notes.length)){ toast('악보로 만들 음표가 없어요.'); return; }
  try{ await loadVF(); }catch(e){ toast('악보 그리기 파일을 불러오지 못했어요. 인터넷 연결 후 다시 시도해 주세요.'); return; }
  if(!PSN_SV.el){ const el=document.createElement('div'); el.id='psnScoreFull'; el.innerHTML=`<style>
    #psnScoreFull{position:fixed;inset:0;z-index:9000;background:#fff;color:#111;display:flex;flex-direction:column;font:14px/1.4 "IBM Plex Sans KR",system-ui,sans-serif}
    #psnScoreFull[hidden]{display:none !important}
    #psnScoreFull .bar{display:flex;gap:8px;align-items:center;padding:6px 10px;border-bottom:1px solid #ddd;background:#fafafa;flex-wrap:wrap}
    #psnScoreFull .bar select,#psnScoreFull .bar button{font:inherit;padding:4px 10px;border:1px solid #ccc;border-radius:8px;background:#fff;color:#111;min-height:34px}
    #psnScoreFull .pg{flex:1;display:flex;align-items:stretch;justify-content:center;gap:10px;padding:8px;min-height:0;position:relative;user-select:none;-webkit-user-select:none;touch-action:pan-y}
    #psnScoreFull .page{flex:1 1 0;min-width:0;display:flex;align-items:flex-start;justify-content:center;overflow:hidden}
    #psnScoreFull .page svg{width:100%;height:100%;max-height:100%}
    #psnScoreFull .zone{position:absolute;top:0;bottom:0;width:30%;cursor:pointer}
    #psnScoreFull .zone.l{left:0}#psnScoreFull .zone.r{right:0}
    #psnScoreFull .num{font-variant-numeric:tabular-nums;margin-left:auto;color:#555}
    #psnScoreFull .hint{color:#777;font-size:12px}
   </style><div class="bar"><select class="tr"></select><select class="sp"><option value="hand">양손 자동</option><option value="60">가운데 도 기준</option><option value="none">한 줄</option></select><select class="gr"><option value="1">16분음표</option><option value="2">8분음표</option><option value="4">4분음표</option></select><button class="prev">◀</button><span class="num"></span><button class="next">▶</button><span class="hint">화면 왼쪽/오른쪽을 누르면 앞·뒤 쪽</span><button class="close" style="margin-left:6px;font-weight:600;border-color:#888">✕ 닫기</button></div><div class="pg"><div class="page a"></div><div class="page b"></div><div class="zone l"></div><div class="zone r"></div></div>`;
    document.body.appendChild(el); PSN_SV.el=el;
    el.querySelector('.close').onclick=psnScoreClose; el.querySelector('.prev').onclick=()=>psnScoreGo(-1); el.querySelector('.next').onclick=()=>psnScoreGo(1);
    el.querySelector('.zone.l').onclick=()=>psnScoreGo(-1); el.querySelector('.zone.r').onclick=()=>psnScoreGo(1);
    el.querySelector('.tr').onchange=e=>{ PSN_SV.tracks=e.target.value; psnScoreRender(); }; el.querySelector('.sp').onchange=e=>{ PSN_SV.split=e.target.value; psnScoreRender(); }; el.querySelector('.gr').onchange=e=>{ PSN_SV.grid=+e.target.value; psnScoreRender(); };
    let sx=null; el.querySelector('.pg').addEventListener('touchstart',e=>{ sx=e.touches[0].clientX; },{passive:true}); el.querySelector('.pg').addEventListener('touchend',e=>{ if(sx==null) return; const dx=e.changedTouches[0].clientX-sx; sx=null; if(Math.abs(dx)>60) psnScoreGo(dx<0?1:-1); },{passive:true});
    window.addEventListener('resize',()=>{ if(PSN_SV.el&&!PSN_SV.el.hidden){ const W=psnScorePer()===2?1000:(innerWidth<700?640:900); if(W!==PSN_SV.renderW) psnScoreRender(); else psnScoreLayout(); } });
    document.addEventListener('keydown',e=>{ if(!PSN_SV.el||PSN_SV.el.hidden) return; if(e.key==='ArrowRight'||e.key==='PageDown'||e.key===' '){ e.preventDefault(); psnScoreGo(1); } else if(e.key==='ArrowLeft'||e.key==='PageUp'){ e.preventDefault(); psnScoreGo(-1); } else if(e.key==='Escape'){ psnScoreClose(); } },true); }
  const sel=PSN_SV.el.querySelector('.tr'); const trs=project.tracks.filter(t=>t.notes.length); sel.innerHTML='<option value="all">모든 트랙</option>'+trs.map(t=>`<option value="${t.id}">${String(t.name).replace(/</g,'&lt;')}</option>`).join(''); if(!trs.some(t=>t.id===PSN_SV.tracks)) PSN_SV.tracks=trs.length===1?trs[0].id:'all'; sel.value=PSN_SV.tracks; PSN_SV.el.querySelector('.sp').value=PSN_SV.split; PSN_SV.el.querySelector('.gr').value=String(PSN_SV.grid);
  PSN_SV.el.hidden=false; PSN_SV.el.style.display=''; document.body.style.overflow='hidden'; PSN_SV.page=0; psnScoreRender(); try{ if(screen.orientation&&screen.orientation.lock) screen.orientation.lock('any').catch(()=>{}); }catch(e){} }
function psnScoreClose(){ if(!PSN_SV.el) return; PSN_SV.el.hidden=true; PSN_SV.el.style.display='none'; document.body.style.overflow=''; }
function psnScoreRender(){ const trs=PSN_SV.tracks==='all'?project.tracks.filter(t=>t.notes.length):project.tracks.filter(t=>t.id===PSN_SV.tracks); if(!trs.length) return;
  const split=PSN_SV.split==='none'?null:PSN_SV.split==='hand'?'hand':+PSN_SV.split; const score=buildScore(trs,{split,grid:PSN_SV.grid,legato:true});
  const W=psnScorePer()===2?1000:(innerWidth<700?640:900); PSN_SV.renderW=W; const tmp=document.createElement('div'); tmp.style.cssText='position:absolute;left:-9999px;top:0;width:'+W+'px'; document.body.appendChild(tmp);
  try{ PSN_SV.pages=renderScore(score,tmp,{width:W,title:project.name,subtitle:trs.length===1?trs[0].name:''}); }catch(e){ console.error(e); toast('악보를 그리다 문제가 생겼어요: '+(e.message||e)); PSN_SV.pages=[]; }
  tmp.remove(); PSN_SV.page=Math.min(PSN_SV.page,Math.max(0,PSN_SV.pages.length-1)); psnScoreLayout(); }
function psnScorePer(){ return innerWidth>innerHeight&&innerWidth>=900?2:1; }
function psnScoreLayout(){ const per=psnScorePer(); const n=PSN_SV.pages.length; if(per===2) PSN_SV.page-=PSN_SV.page%2; const a=PSN_SV.el.querySelector('.page.a'), b=PSN_SV.el.querySelector('.page.b'); a.innerHTML=''; b.innerHTML=''; b.style.display=per===2?'':'none';
  const put=(box,i)=>{ if(i<n){ const s=PSN_SV.pages[i].cloneNode(true); s.removeAttribute('width'); s.removeAttribute('height'); s.setAttribute('preserveAspectRatio','xMidYMin meet'); box.appendChild(s); } };
  put(a,PSN_SV.page); if(per===2) put(b,PSN_SV.page+1);
  const last=per===2?Math.min(n,PSN_SV.page+2):PSN_SV.page+1; PSN_SV.el.querySelector('.num').textContent=n?`${PSN_SV.page+1}${per===2&&last>PSN_SV.page+1?'–'+last:''} / ${n}`:'0 / 0';
  PSN_SV.el.querySelector('.prev').disabled=PSN_SV.page<=0; PSN_SV.el.querySelector('.next').disabled=last>=n; }
function psnScoreGo(dir){ const per=psnScorePer(), n=PSN_SV.pages.length; let p=PSN_SV.page+dir*per; if(p<0) p=0; if(p>=n) return; PSN_SV.page=p; psnScoreLayout(); }
window.psnLibraryOpen=psnLibraryOpen; window.psnScoreFull=psnScoreFull;
