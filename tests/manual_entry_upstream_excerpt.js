/* Manual-entry excerpt from the user's upstream index.html, lines 1704-1725.
 * Source: bambabo-cmd/piano-studio @ bd54de7e73274429c843aa0230623eaa1d700aa6.
 * Retrieved as text, not a full downloaded checkout. Test surrounding app is synthetic.
 */
const KO_MAP={'도':0,'레':2,'미':4,'파':5,'솔':7,'라':9,'시':11,'c':0,'d':2,'e':4,'f':5,'g':7,'a':9,'b':11};
function parseNoteText(text,baseBeats){ const toks=text.replace(/[,，]/g,' ').split(/\s+/).filter(Boolean); const out=[]; const bad=[]; let oct=4;
  for(const raw of toks){ let t=raw; let m=t.match(/^(쉼|_|\.|r)(-*)(\/?)$/i); const dur=len=>baseBeats*len;
    if(m){ const len=(1+m[2].length)*(m[3]?.5:1); out.push({rest:true,beats:dur(len)}); continue; }
    m=t.match(/^(도|레|미|파|솔|라|시|[a-gA-G])([#♯]|[b♭])?(\d)?([\^v]*)(-*)(\/*)$/); if(!m){ bad.push(raw); continue; }
    let pc=KO_MAP[m[1].toLowerCase()]; if(m[2]==='#'||m[2]==='♯') pc+=1; if(m[2]==='b'||m[2]==='♭') pc-=1; let o=m[3]?+m[3]:oct; for(const ch of m[4]) o+=ch==='^'?1:-1;
    const len=(1+m[5].length)*Math.pow(.5,m[6].length); out.push({p:clamp((o+1)*12+pc,21,108),beats:dur(len)}); }
  return {notes:out,bad}; }
function newEmptyTrack(){ const t=addTrack({name:'직접 입력 '+(project.tracks.length+1)}); renderTracks(); drawRoll(); scheduleSave(); toast('빈 트랙을 만들었어요. ‘그리기’로 음표를 찍거나 ‘타이핑으로 넣기’를 쓰세요.',4500); return t; }
function openTypeEntry(){ if(!project) return; showOverlay('',null); const msg=$('#ovMsg'); const beat=60/project.bpm;
  msg.innerHTML=`<b>타이핑으로 음표 넣기</b><div class="hint" style="margin:4px 0 8px">계이름을 띄어쓰기로 적으세요. <b>-</b>는 길게(한 칸 더), <b>/</b>는 반으로, <b>쉼</b>은 쉼표, <b>#</b>·<b>b</b>는 반음, 숫자는 옥타브(기본 4), <b>^</b>·<b>v</b>는 한 옥타브 위·아래. 영어 c d e f g a b도 돼요.<br>예: <code>도 도 솔 솔 라 라 솔- 파 파 미 미 레 레 도-</code></div>
   <textarea id="teText" rows="4" style="width:100%;font:inherit;padding:8px;border:1px solid var(--line);border-radius:10px;background:var(--paper);color:inherit"></textarea>
   <div class="row" style="justify-content:flex-start;margin-top:8px;gap:12px;flex-wrap:wrap"><label>한 글자 길이 <select id="teLen"><option value="1">1박</option><option value="0.5" selected>½박</option><option value="0.25">¼박</option><option value="2">2박</option></select></label>
   <label>넣을 위치 <select id="tePos"><option value="end">트랙 끝에 이어서</option><option value="play">재생 위치부터</option><option value="bar">1마디 처음부터</option></select></label>
   <label><input type="checkbox" id="teLH"> 왼손으로 표시</label></div>`;
  const bx=$('#ovBtns'); const c=document.createElement('button'); c.textContent='취소'; const o=document.createElement('button'); o.textContent='넣기'; o.className='on';
  c.onclick=()=>{ hideOverlay(); msg.innerHTML=''; };
  o.onclick=()=>{ const {notes,bad}=parseNoteText($('#teText').value,+$('#teLen').value); if(bad.length){ toast('읽을 수 없는 글자: '+bad.slice(0,5).join(', ')); return; } if(!notes.length){ toast('넣을 음표가 없어요.'); return; }
    let t=activeTrack(); if(!t) t=newEmptyTrack(); const posSel=$('#tePos').value; let s=posSel==='play'?pos:posSel==='bar'?0:(t.notes.length?Math.max(...t.notes.map(n=>n.s+n.d)):0); if(posSel==='end'&&gridSec()) s=Math.round(s/gridSec())*gridSec();
    const lh=$('#teLH').checked; hideOverlay(); msg.innerHTML='';
    edit(tr=>{ for(const n of notes){ const d=n.beats*beat; if(!n.rest) tr.notes.push({id:nid(),p:n.p,s,d:d*.92,v:95,h:lh?'L':'R'}); s+=d; } }); fitView(activeTrack()); drawRoll(); toast(`음표 ${notes.filter(n=>!n.rest).length}개를 넣었어요.`); };
  bx.append(c,o); $('#teText').focus(); }
