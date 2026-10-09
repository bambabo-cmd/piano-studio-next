/* Piano Studio Next — 곡 제목 찾기 (alpha.28)
 * 기존 엔진의 전역(activeTrack, melodyNotesOf, guessKey, keyInfo, project, showOverlay, hideOverlay, $, toast,
 * scheduleSave, refreshSongList, clamp)을 그대로 사용하는 추가 스크립트. 녹음·채보·저장 로직은 변경하지 않는다.
 * ① 내장 멜로디 DB(동요·캐럴·민요·고전 45곡)와 조·옥타브·누락에 강한 간격 정렬 비교 (오프라인)
 * ② Musipedia 윤곽(Parsons code) 검색 결과를 앱 안에 표시 (musipedia.org/<contour>, 무료·로그인 없음)
 * ③ 선택: 구글 계이름 검색, AI 챗봇용 질문 글 복사
 */
'use strict';
/* ================= title finder helper ================= */
function melodyToText(t,opt={}){ const ns=melodyNotesOf(t).slice().sort((a,b)=>a.s-b.s||b.p-a.p); const mono=[]; for(const n of ns){ const l=mono[mono.length-1]; if(l&&n.s-l.s<.05){ if(n.p>l.p){ l.p=n.p; } continue; } mono.push({p:n.p,s:n.s,d:n.d}); }
  if(!mono.length) return null; const beat=60/project.bpm; const key=guessKey(mono); const {root,minor}=keyInfo(key); const shift=opt.toC?((minor?9:0)-root+12)%12:0; let oshift=shift>6?-12:0; { const med=mono.map(n=>n.p+shift+oshift).sort((a,b)=>a-b)[mono.length>>1]; if(opt.toC&&med>=72) oshift-=12; else if(opt.toC&&med<55) oshift+=12; } const tr=p=>p+shift+oshift;
  const gaps=mono.map((n,i)=>i<mono.length-1?mono[i+1].s-n.s:n.d).map(g=>g/beat); const cand=[1,.5,.25]; let unit=.5; for(const u of cand){ const ok=gaps.filter(g=>Math.abs(g/u-Math.round(g/u))<.25).length/gaps.length; if(ok>.8){ unit=u; break; } }
  const toks=[]; mono.forEach((n,i)=>{ const p=tr(n.p); const pc=((p%12)+12)%12; const o=Math.floor(p/12)-1; const name=['도','도#','레','레#','미','파','파#','솔','솔#','라','라#','시'][pc]; const nxt=mono[i+1]; const gap=(nxt?nxt.s-n.s:n.d)/beat; let len=Math.max(1,Math.round(gap/unit)); const held=Math.round(Math.min(gap,n.d*1.15)/beat/unit); const noteLen=Math.max(1,Math.min(len,held||1)); const oct=o===4?'':String(o); toks.push(name+oct+'-'.repeat(noteLen-1)); for(let r=noteLen;r<len;r++) toks.push('쉼'); });
  const out=[]; for(const tk of toks){ const l=out[out.length-1]; if(tk==='쉼'&&l&&/^쉼-*$/.test(l)) out[out.length-1]=l+'-'; else out.push(tk); }
  const parsons='*'+mono.slice(1).map((n,i)=>n.p===mono[i].p?'R':n.p>mono[i].p?'U':'D').join('');
  const keyName=(opt.toC?(minor?'A':'C')+(minor?'m':''):key); return {text:out.join(' '),unit,key:keyName.replace('m',' 단조')+(/m$/.test(keyName)?'':' 장조'),parsons,bpm:project.bpm,count:mono.length}; }
/* ================= built-in melody database (offline title finder) ================= */
var PSN_SONG_DB=[
 ['반짝반짝 작은별 (모차르트 변주곡 주제)','동요',[60,60,67,67,69,69,67,65,65,64,64,62,62,60]],
 ['나비야','동요',[67,64,64,65,62,62,60,62,64,65,67,67,67,67,64,64,65,62,62,60,64,67,67,64,64,64]],
 ['학교종','동요',[67,67,69,69,67,67,64,67,67,64,64,62,67,67,69,69,67,67,64,67,64,62,64,60]],
 ['생일 축하합니다','동요',[67,67,69,67,72,71,67,67,69,67,74,72,67,67,79,76,72,71,69,77,77,76,72,74,72]],
 ['징글벨','캐럴',[64,64,64,64,64,64,64,67,60,62,64,65,65,65,65,65,64,64,64,64,62,62,64,62,67]],
 ['고요한 밤 거룩한 밤','캐럴',[67,69,67,64,67,69,67,64,74,74,71,72,72,67]],
 ['환희의 송가 (베토벤 교향곡 9번)','클래식',[64,64,65,67,67,65,64,62,60,60,62,64,64,62,62]],
 ['엘리제를 위하여 (베토벤)','클래식',[76,75,76,75,76,71,74,72,69,60,64,69,71,64,68,71,72]],
 ['캐논 (파헬벨)','클래식',[76,74,72,71,69,67,69,71,72,74,76,77,76,74,72,71,69,67,69,71]],
 ['아리랑','민요',[67,67,67,69,67,69,72,69,67,72,74,72,69,67,69]],
 ['산토끼','동요',[67,64,64,67,64,64,67,69,67,64,62,60,62,64,65,67,67,69,67,64,62,60]],
 ['떴다 떴다 비행기 (Mary Had a Little Lamb)','동요',[64,62,60,62,64,64,64,62,62,62,64,67,67,64,62,60,62,64,64,64,64,62,62,64,62,60]],
 ['우리 서로 학교길에 (Frère Jacques)','동요',[60,62,64,60,60,62,64,60,64,65,67,64,65,67]],
 ['런던 브리지','동요',[67,69,67,65,64,65,67,62,64,65,64,65,67,67,69,67,65,64,65,67,62,67,64,60]],
 ['석별의 정 (Auld Lang Syne)','민요',[67,72,72,72,76,74,72,74,76,74,72,72,76,79,81]],
 ['미뉴에트 G장조 (바흐)','클래식',[74,67,69,71,72,74,67,67,76,72,74,76,78,79,67,67]],
 ['터키 행진곡 (모차르트)','클래식',[71,69,68,69,72,74,72,71,72,76,77,76,75,76,84,83,84,83,84]],
 ['젓가락 행진곡','기타',[65,67,65,67,65,67,65,67,65,67,65,67,64,67,64,67,64,67,64,67,64,67,64,67,62,71,62,71]],
 ['애국가','기타',[67,67,69,71,74,76,74,71,67,69,71,67,74,72,71,69]],
 ['기쁘다 구주 오셨네','캐럴',[72,71,69,67,65,64,62,60,67,69,69,71,71,72]],
 ['운명 교향곡 (베토벤 5번)','클래식',[67,67,67,63,65,65,65,62]],
 ['사계 봄 (비발디)','클래식',[64,68,68,68,66,64,71,71,69,68,69,71,68,68,68,66,64,71]],
 ['브람스 자장가','클래식',[64,64,67,64,64,67,64,67,72,71,69,69,67]],
 ['그린슬리브즈','민요',[69,72,74,76,77,76,74,71,67,69,71,72,71,69]],
 ['교향곡 40번 (모차르트)','클래식',[63,62,62,63,62,62,63,62,62,70,70,69,69,67,67]],
 ['양키 두들','민요',[60,60,62,64,60,64,62,67,60,60,62,64,60,71]],
 ['오 수재너','민요',[60,62,64,67,67,69,67,64,60,62,64,64,62,60,62]],
 ['클레멘타인 (넓고 넓은 바닷가에)','민요',[60,60,60,67,64,64,64,60,60,64,67,67,65,64,62]],
 ['We Wish You a Merry Christmas','캐럴',[60,65,65,67,65,64,62,62,62,67,67,69,67,65,64,60]],
 ['Deck the Halls','캐럴',[67,65,64,62,60,62,64,60,62,64,65,62,64,62,60,71,60]],
 ['소나무야 (O Tannenbaum)','캐럴',[60,65,65,65,67,69,69,69,67,69,70,64,67,65]],
 ['어메이징 그레이스','기타',[67,72,76,72,76,74,72,69,67,72,76,72,76,74,79]],
 ['라 쿠카라차','민요',[60,60,60,65,69,60,60,60,65,69,65,65,64,64,62,62,60]],
 ['피아노 소나타 16번 K.545 (모차르트)','클래식',[60,64,67,71,72,74,72,69,67,72,67,65,64,65,64,62,60]],
 ['엔터테이너 (조플린)','클래식',[74,75,76,84,76,84,76,84,84,86,87,88,84,86,84]],
 ['아이네 클라이네 나흐트무지크 (모차르트)','클래식',[67,62,67,62,67,62,67,71,74,72,69,72,69,72,69,66,69,62]],
 ['놀람 교향곡 (하이든)','클래식',[60,60,64,64,67,67,64,65,65,62,62,71,71,67]],
 ['Baa Baa Black Sheep','동요',[60,60,67,67,69,71,72,69,67,65,65,64,64,62,62,60]],
 ['Row Row Row Your Boat','동요',[60,60,60,62,64,64,62,64,65,67,72,72,72,67,67,67,64,64,64,60,60,60]],
 ['Old MacDonald','동요',[67,67,67,62,64,64,62,71,71,69,69,67]],
 ['거미가 줄을 타고 (Itsy Bitsy Spider)','동요',[67,60,60,60,62,64,64,64,62,60,62,64,60]],
 ['If You\'re Happy and You Know It','동요',[60,60,65,65,65,65,65,64,65,67,67,67,67,67,67,67,65,67,69]],
 ['The Wheels on the Bus','동요',[60,65,65,65,65,69,72,69,65,67,64,60,64,67]],
 ['Au Clair de la Lune','동요',[60,60,60,62,64,62,60,64,62,62,60]],
 ['This Old Man','동요',[67,64,67,67,64,67,69,67,65,64,62,64,65]],
];
function intervalsOf(ps){ const r=[]; for(let i=1;i<ps.length;i++) r.push(ps[i]-ps[i-1]); return r; }
var foldIv=i=>{ let f=((i%12)+12)%12; if(f>6) f-=12; return f; };
function ivCost(a,b){ if(a===b) return 0; const sa=Math.sign(a), sb=Math.sign(b); let c; if(sa===sb&&Math.abs(a-b)<=2) c=.4; else if(sa===sb) c=.7; else c=1; const fa=foldIv(a), fb=foldIv(b); if(fa===fb) c=Math.min(c,.3); return c; }
function alignScore(q,ref){ // q: query intervals (may be longer / start later), ref: db intervals. returns best normalized similarity
  const n=ref.length; let best=0;
  for(let off=0;off<=Math.min(6,Math.max(0,q.length-4));off++){ const s=q.slice(off, off+n+Math.ceil(n*.5)); const m=s.length; if(m<4) break;
    // semi-global: ref must be fully consumed, s can end early (free trailing)
    const D=[]; for(let i=0;i<=n;i++){ D.push(new Float32Array(m+1)); } for(let i=1;i<=n;i++) D[i][0]=D[i-1][0]+(ref[i-1]===0?.4:1); for(let j=1;j<=m;j++) D[0][j]=D[0][j-1]+(s[j-1]===0?.4:1);
    for(let i=1;i<=n;i++) for(let j=1;j<=m;j++){ D[i][j]=Math.min(D[i-1][j-1]+ivCost(ref[i-1],s[j-1]), D[i-1][j]+(ref[i-1]===0?.4:1), D[i][j-1]+(s[j-1]===0?.4:1)); }
    let dmin=1e9; for(let j=Math.max(1,Math.floor(n*.6));j<=m;j++) dmin=Math.min(dmin,D[n][j]); const sim=1-dmin/n; if(sim>best) best=sim; }
  return best; }
function findTitles(t){ const ns=melodyNotesOf(t).slice().sort((a,b)=>a.s-b.s||b.p-a.p); const mono=[]; for(const n of ns){ const l=mono[mono.length-1]; if(l&&n.s-l.s<.05){ if(n.p>l.p) l.p=n.p; continue; } mono.push(n.p); }
  if(mono.length<5) return []; const q=intervalsOf(mono);
  return PSN_SONG_DB.map(([name,cat,ps])=>{ const iv=intervalsOf(ps); const raw=alignScore(q,iv); return {name,cat,sim:raw-.15*(1-Math.min(1,iv.length/12))}; }).sort((a,b)=>b.sim-a.sim).slice(0,3); }

function psnOpenTitleFinder(){ const t=activeTrack(); if(!t||!t.notes.length){ toast('멜로디가 있는 트랙을 고르세요.'); return; } const a=melodyToText(t,{toC:false}), c=melodyToText(t,{toC:true}); if(!a) return;
  const unitStr=u=>u===1?'1박':u===.5?'½박':'¼박'; const esc=s=>String(s).replace(/</g,'&lt;');
  const hits=findTitles(t); const lbl=s=>s>=.8?'거의 확실':s>=.65?'비슷해요':'조금 비슷';
  const hitHtml=!hits.length?'<div class="hint">음표가 5개 이상 있어야 찾을 수 있어요.</div>':hits[0].sim<.5?'<div class="hint">앱에 들어 있는 곡 중에는 비슷한 곡이 없어요. 아래 인터넷 검색을 써 보세요.</div>':
    `<div class="sug-list">${hits.filter(h=>h.sim>=.5).map((h,i)=>`<label><b>${esc(h.name)}</b> <span class="hint">${h.cat} · ${Math.round(h.sim*100)}% ${lbl(h.sim)}</span><button class="pv useT" data-n="${esc(h.name)}">곡 이름으로</button></label>`).join('')}</div>`;
  const contour=a.parsons.replace(/^\*/,'').slice(0,30); const musiUrl='https://www.musipedia.org/'+contour;
  const summary=`[멜로디 계이름 · 다장조/가단조로 옮김, 한 글자=${unitStr(c.unit)}, -는 더 길게, 쉼=쉼표]\n${c.text}\n\n[원래 조: ${a.key}, 빠르기 ${a.bpm} BPM, 음 ${a.count}개]\n[높낮이 기호(Parsons code): ${a.parsons}]\n이 멜로디는 무슨 곡인가요? 제목과 작곡가를 알려 주세요.`;
  showOverlay('',null); const msg=$('#ovMsg'); msg.innerHTML=`<b>제목 찾기</b>
   <div style="margin:8px 0 4px"><b>① 앱 안에서 찾기</b> <span class="hint">(인터넷 필요 없음 · 동요·캐럴·민요·유명 클래식 ${PSN_SONG_DB.length}곡)</span></div>${hitHtml}
   <div style="margin:12px 0 4px"><b>② 인터넷에서 찾기</b> <span class="hint">(Musipedia 멜로디 검색 · 무료 · 로그인 없음)</span></div>
   <div class="row" style="justify-content:flex-start;gap:8px;flex-wrap:wrap"><button id="tfMusi" class="on">인터넷에서 이 멜로디 찾기</button><a id="tfMusiOpen" target="_blank" rel="noopener" href="${musiUrl}"><button>새 창에서 열기</button></a><a id="tfGoogle" target="_blank" rel="noopener"><button>구글 계이름 검색</button></a><button id="tfParsons">높낮이 기호 복사</button></div>
   <div id="tfMusiBox" style="margin-top:8px"></div>
   <details style="margin-top:12px"><summary class="hint" style="cursor:pointer">③ (선택) AI 챗봇에게 물어볼 글 만들기</summary>
   <textarea id="tfText" rows="6" readonly style="width:100%;margin-top:6px;font:13px/1.5 ui-monospace,monospace;padding:8px;border:1px solid var(--line);border-radius:10px;background:var(--paper);color:inherit">${esc(summary)}</textarea>
   <div class="row" style="justify-content:flex-start;margin-top:6px"><button id="tfCopy">글 복사하기</button></div></details>`;
  $('#tfGoogle').href='https://www.google.com/search?q='+encodeURIComponent('계이름 '+c.text.split(' ').slice(0,12).join(' '));
  const cp=async(txt,ok)=>{ try{ await navigator.clipboard.writeText(txt); toast(ok); }catch(e){ toast('복사가 막혀 있어요. 글을 길게 눌러 직접 복사해 주세요.'); } };
  $('#tfParsons').onclick=()=>cp(a.parsons,'높낮이 기호를 복사했어요.');
  $('#tfMusi').onclick=async()=>{ const box=$('#tfMusiBox'); box.innerHTML='<div class="hint">인터넷에서 찾는 중…</div>';
    if(!navigator.onLine){ box.innerHTML='<div class="hint">지금은 인터넷에 연결돼 있지 않아요. 연결 후 다시 눌러 주세요.</div>'; return; }
    let shown=false;
    try{ const r=await fetch(musiUrl,{mode:'cors'}); if(r.ok){ const html=await r.text(); const doc=new DOMParser().parseFromString(html,'text/html'); const items=[]; doc.querySelectorAll('a[href]').forEach(x=>{ const tx=(x.textContent||'').trim(); const h=x.getAttribute('href')||''; if(tx.length>3&&/\/(tune|song|melody|[0-9]{3,})/i.test(h)&&!items.some(i=>i.t===tx)) items.push({t:tx,h:new URL(h,musiUrl).href}); });
      if(items.length){ box.innerHTML='<div class="sug-list">'+items.slice(0,8).map(i=>`<label><a href="${i.h}" target="_blank" rel="noopener">${esc(i.t)}</a><button class="pv useT" data-n="${esc(i.t)}">곡 이름으로</button></label>`).join('')+'</div><div class="hint" style="margin-top:4px">Musipedia 검색 결과예요. 높낮이 순서만으로 찾는 거라 비슷한 곡이 섞여 나올 수 있어요.</div>'; shown=true; } } }catch(e){}
    if(!shown){ box.innerHTML=`<div class="hint" style="margin-bottom:6px">검색 결과 페이지를 아래에 띄웠어요. 비어 있으면 ‘새 창에서 열기’를 눌러 주세요.</div><iframe src="${musiUrl}" style="width:100%;height:min(60vh,520px);border:1px solid var(--line);border-radius:10px;background:#fff" referrerpolicy="no-referrer"></iframe>`; }
    msg.querySelectorAll('.useT').forEach(b=>b.onclick=()=>{ project.name=b.dataset.n; $('#songName').value=project.name; scheduleSave(); refreshSongList(); hideOverlay(); msg.innerHTML=''; toast(`곡 이름을 ‘${project.name}’으로 바꿨어요.`); }); }; $('#tfCopy').onclick=()=>cp(summary,'복사했어요.');
  msg.querySelectorAll('.useT').forEach(b=>b.onclick=()=>{ project.name=b.dataset.n; $('#songName').value=project.name; scheduleSave(); refreshSongList(); hideOverlay(); msg.innerHTML=''; toast(`곡 이름을 ‘${project.name}’으로 바꿨어요.`); });
  const bx=$('#ovBtns'); const o=document.createElement('button'); o.textContent='닫기'; o.className='on'; o.onclick=()=>{ hideOverlay(); msg.innerHTML=''; }; bx.append(o); }

window.psnTitleFinder=psnOpenTitleFinder;
