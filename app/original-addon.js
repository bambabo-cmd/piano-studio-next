/* Piano Studio original-app bridge. Calls existing DOM handlers; never replaces them. */
(() => {
  'use strict';
  if(window.__PianoOriginalAddon)return;
  window.__PianoOriginalAddon={version:2,ready:false};
  const q=id=>document.getElementById(id);
  function boot() {
    const required=['mpOpen','mpStart','mpClose','metroPanel','recBtn','playBtn','shOpen'];
    const missing=required.filter(id=>!q(id));
    if(missing.length){console.error('[Piano UI Tools v2] Original controls missing:',missing);return;}
    const original={open:q('mpOpen'),start:q('mpStart'),close:q('mpClose'),panel:q('metroPanel'),rec:q('recBtn'),play:q('playBtn'),sheet:q('shOpen')};
    const header=document.querySelector('header.top')||document.querySelector('.top');
    if(!header){console.error('[Piano UI Tools v2] Original header missing.');return;}
    const tools=document.createElement('div');tools.id='ps-tools-theme';
    tools.innerHTML='<label>화면 모드 <select id="ps-theme-select" data-theme-select aria-label="화면 모드"><option value="system">시스템 기본</option><option value="dark">다크 모드</option><option value="light">일반 모드</option></select></label><button id="ps-metro-settings">♩ 메트로놈 설정</button>';
    header.appendChild(tools);
    const dock=document.createElement('nav');dock.id='ps-tools-dock';dock.setAttribute('aria-label','주요 기능 바로가기');
    dock.innerHTML='<button data-ps-action="record"><span aria-hidden="true">●</span><span>녹음</span></button><button data-ps-action="sheet"><span aria-hidden="true">▤</span><span>악보 보기</span></button><button data-ps-action="play"><span aria-hidden="true">▶</span><span>재생</span></button><button data-ps-action="metro" aria-pressed="false"><span aria-hidden="true">♩</span><span>메트로놈</span></button><span id="ps-tools-status" role="status">앱 준비 중</span>';
    document.body.appendChild(dock);
    const buttons=Object.fromEntries([...dock.querySelectorAll('[data-ps-action]')].map(el=>[el.dataset.psAction,el]));
    const ready=()=>Object.values(original).filter(el=>el.tagName==='BUTTON').every(el=>typeof el.onclick==='function');
    function update() {
      const available=ready();window.__PianoOriginalAddon.ready=available;
      const running=original.open.classList.contains('running');
      buttons.metro.setAttribute('aria-pressed',String(running));
      buttons.metro.setAttribute('aria-label',running?'메트로놈 정지':'메트로놈 단독 실행');
      buttons.metro.lastElementChild.textContent=running?'메트로놈 정지':'메트로놈';
      const recording=original.rec.classList.contains('recording');
      buttons.record.lastElementChild.textContent=recording?'녹음 중지':'녹음';
      buttons.record.setAttribute('aria-label',recording?'녹음 중지':'녹음 시작');
      buttons.play.lastElementChild.textContent=original.play.textContent.includes('정지')||original.play.textContent.includes('멈')?'재생 정지':'재생';
      for(const [name,el] of Object.entries(buttons)) {
        const target=name==='record'?original.rec:name==='sheet'?original.sheet:name==='play'?original.play:original.start;
        el.disabled=!available||target.disabled;
      }
      q('ps-tools-status').textContent=!available?'앱 준비 중':running?'메트로놈 단독 실행 중':'기존 기능 그대로 · 빠른 실행';
    }
    q('ps-theme-select').addEventListener('change',event=>{
      const saved=window.PianoTheme.set(event.target.value);
      if(!saved)q('ps-tools-status').textContent='테마는 이번 화면에서만 유지됩니다.';
    });
    q('ps-metro-settings').addEventListener('click',()=>{if(ready())original.open.click();});
    buttons.record.onclick=()=>original.rec.click();
    buttons.sheet.onclick=()=>original.sheet.click();
    buttons.play.onclick=()=>original.play.click();
    buttons.metro.onclick=()=>{
      if(!ready())return;
      if(!original.open.classList.contains('running')){
        // Opening runs the app's mpLoad, so saved BPM/meter/sound are honored.
        // Close before starting; both calls stay inside the original user gesture.
        original.open.click(); original.close.click();
      }
      original.start.click(); buttons.metro.focus(); update();
    };
    const observer=new MutationObserver(update);
    for(const element of [original.open,original.start,original.rec,original.play,original.sheet])
      observer.observe(element,{attributes:true,childList:true,characterData:true,subtree:true,attributeFilter:['class','disabled','aria-pressed']});
    // Original init() wires handlers synchronously before its first DB await in the inspected source.
    // The short retry also handles a slower or deferred script without rewriting any handlers.
    let tries=0;
    function waitReady(){update();if(!ready()&&++tries<100)setTimeout(waitReady,100);}
    waitReady();window.PianoTheme.apply();
    window.__PianoOriginalAddon.diagnostics=()=>({ready:ready(),version:2,theme:window.PianoTheme.get(),
      metronomeRunning:original.open.classList.contains('running'),originalIds:required.every(id=>!!q(id))});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
