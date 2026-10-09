// 우리집 연주실 오프라인 캐시
const VER='hps-v17';
const SHELL=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png','./bp.bundle.js','./vexflow-bravura.js'];
self.addEventListener('install',e=>{ e.waitUntil(caches.open(VER).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting())); });
self.addEventListener('activate',e=>{ e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==VER).map(k=>caches.delete(k)))).then(()=>self.clients.claim())); });
self.addEventListener('fetch',e=>{
  const req=e.request; if(req.method!=='GET') return;
  const url=new URL(req.url);
  if(url.origin===location.origin){
    // 앱 파일: 네트워크 우선(업데이트 반영), 실패하면 캐시
    e.respondWith(fetch(req).then(r=>{ const cp=r.clone(); caches.open(VER).then(c=>c.put(req,cp)); return r; }).catch(()=>caches.match(req).then(r=>r||caches.match('./index.html'))));
  } else if(/fonts\.(googleapis|gstatic)\.com$/.test(url.hostname)){
    // 글꼴: 캐시 우선
    e.respondWith(caches.match(req).then(r=>r||fetch(req).then(res=>{ const cp=res.clone(); caches.open(VER).then(c=>c.put(req,cp)); return res; })));
  }
});
