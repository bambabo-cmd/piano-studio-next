/* Shared v1/v2 navigation. No engine/handler replacement or cross-version DB copy. */
(() => {
  'use strict';
  if (window.PianoVersionSwitch) return;
  const config = document.currentScript;
  const current = config && config.dataset.currentVersion === '1' ? '1' : '2';
  const destinations = Object.freeze({
    '1':'https://bambabo-cmd.github.io/piano-studio/',
    '2':'https://bambabo-cmd.github.io/piano-studio-next/'
  });
  let pending = false;
  function workState() {
    let rec = false;
    try { rec = typeof recording !== 'undefined' && !!recording; } catch (_) {}
    rec = rec || !!document.querySelector('#recBtn.recording,[data-recording="true"]');
    const overlay = document.getElementById('overlay');
    const busy = !!(overlay && !overlay.hidden && overlay.getClientRects().length);
    return {recording:rec, busy};
  }
  async function saveCurrentProject() {
    // Global lexical bindings are from the original app's classic script.
    // Using one real IndexedDB transaction avoids saveNow() swallowing quota errors.
    const p = typeof project !== 'undefined' ? project : null;
    if (!p) return 'no-project';
    const db = typeof DB !== 'undefined' ? DB.db : null;
    if (!db || typeof db.transaction !== 'function') throw new Error('곡 저장소가 준비되지 않았습니다.');
    const snapshot = typeof structuredClone === 'function' ? structuredClone(p) : {...p};
    snapshot.updatedAt = Date.now();
    await new Promise((resolve, reject) => {
      const tx = db.transaction(['projects','meta'], 'readwrite');
      let settled = false;
      const done = (error) => {
        if (settled) return;
        settled = true; clearTimeout(timer);
        error ? reject(error) : resolve();
      };
      const timer = setTimeout(() => { try { tx.abort(); } catch (_) {} done(new Error('저장 확인 시간이 초과되었습니다.')); }, 10000);
      tx.oncomplete = () => done();
      tx.onerror = tx.onabort = () => done(tx.error || new Error('곡 저장에 실패했습니다.'));
      try {
        tx.objectStore('projects').put(snapshot);
        tx.objectStore('meta').put(snapshot.id, 'last');
      } catch (error) { try { tx.abort(); } catch (_) {} done(error); }
    });
    return 'saved';
  }
  function boot() {
    const header = document.querySelector('header.top') || document.querySelector('.top');
    if (!header) { console.warn('[Version switch] Original app header missing; no controls replaced.'); return; }
    const nav = document.createElement('nav');
    nav.className = 'ps-version-switch'; nav.id = 'ps-version-switch';
    nav.setAttribute('aria-label','우리집 연주실 버전 선택');
    for (const v of ['1','2']) {
      const el = document.createElement(v === current ? 'span' : 'a');
      el.className = 'ps-version-item'; el.dataset.version = v;
      el.innerHTML = '<span>버전 '+v+'</span><span class="ps-version-sub">'+(v==='1'?'기존':'Next')+'</span>';
      if (v === current) {
        el.setAttribute('aria-current','page');
        el.setAttribute('aria-label','버전 '+v+' · 현재 사용 중');
      } else {
        el.href = destinations[v];
        el.setAttribute('aria-label','버전 '+v+(v==='1'?' 기존 앱':' Next')+'으로 이동');
        el.title = '현재 곡을 저장한 뒤 이동합니다. 두 버전의 곡 목록은 별도입니다.';
        el.addEventListener('click', async (event) => {
          // Ctrl/Cmd-click opens another tab without unloading this one.
          if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button !== 0) return;
          event.preventDefault();
          if (pending) return;
          const state = workState();
          if (state.recording) {
            window.alert('녹음 중에는 버전을 이동하지 않습니다.\n먼저 녹음을 멈추고 악보 생성이 끝난 뒤 다시 눌러 주세요.');
            return;
          }
          if (state.busy) {
            window.alert('악보 분석·파일 처리 또는 확인창이 열려 있습니다.\n현재 작업을 마친 뒤 버전을 이동해 주세요.');
            return;
          }
          pending = true; nav.setAttribute('aria-busy','true');
          status.textContent = '현재 곡을 저장하고 있습니다.';
          try {
            await saveCurrentProject();
            // Recheck after asynchronous storage: never interrupt a new recording.
            const after = workState();
            if (after.recording || after.busy) throw new Error('새 작업이 시작되어 이동을 취소했습니다.');
            // Cancellable integration event is also used by the test harness.
            const go = new CustomEvent('piano-version-navigate', {cancelable:true, detail:{version:v,url:destinations[v]}});
            if (window.dispatchEvent(go)) window.location.assign(destinations[v]);
            status.textContent = '버전 '+v+'으로 이동합니다.';
          } catch (error) {
            status.textContent = '저장을 확인하지 못해 이동하지 않았습니다.';
            window.alert('이동하지 않았습니다.\n'+(error && error.message || error)+'\n필요하면 파일 메뉴에서 곡 파일을 먼저 내보내세요.');
          } finally { pending=false; nav.removeAttribute('aria-busy'); }
        });
      }
      nav.appendChild(el);
    }
    const status = document.createElement('span');
    status.className='ps-version-sr'; status.setAttribute('role','status');
    nav.appendChild(status);
    const title = header.querySelector('h1');
    if (title && title.parentElement === header) title.insertAdjacentElement('afterend',nav);
    else header.prepend(nav);
  }
  window.PianoVersionSwitch = Object.freeze({current, destinations, workState});
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',boot,{once:true}); else boot();
})();
