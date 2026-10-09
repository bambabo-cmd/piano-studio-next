/* Piano Studio Next. Cache names include this app's scope, not just a version. */
'use strict';
const BUILD = '__BUILD_ID__';
const ROOT = new URL(self.registration.scope);
const PREFIX = 'piano-studio-next-v2:' + ROOT.pathname + ':';
const CACHE = PREFIX + BUILD;
const SHELL = [
  './', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png',
  './bp.bundle.js', './vexflow-bravura.js', './app/theme.js',
  './app/original-addon.js', './app/original-addon.css', './app/title-finder.js', './app/next-boot.js',
  './app/version-switch.js', './app/version-switch.css', './app/library.js'
].concat("__LIBRARY_FILES__").map(path => new URL(path, ROOT).href);
const KNOWN = new Set(SHELL);
self.addEventListener('install', event => {
  // An existing app keeps its current worker until all its tabs are closed.
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL)));
});
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names.filter(name => name.startsWith(PREFIX) && name !== CACHE)
      .map(name => caches.delete(name)));
    await self.clients.claim();
  })());
});
self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (['fonts.googleapis.com','fonts.gstatic.com'].includes(url.hostname)) {
    event.respondWith((async () => {
      const cache = await caches.open(CACHE);
      const hit = await cache.match(request);
      if (hit) return hit;
      const response = await fetch(request);
      if (response.ok || response.type === 'opaque') await cache.put(request, response.clone());
      return response;
    })());
    return;
  }
  if (url.origin !== ROOT.origin || !url.pathname.startsWith(ROOT.pathname)) return;
  // Do not store arbitrary user files, preview pages, or HTML errors as scripts.
  if (!KNOWN.has(url.href)) return;
  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    try {
      const response = await fetch(request);
      if (response.ok) {
        await cache.put(request, response.clone());
        return response;
      }
      const cached = await cache.match(request);
      return cached || response;
    } catch (error) {
      const cached = await cache.match(request);
      if (cached) return cached;
      if (request.mode === 'navigate') {
        const index = await cache.match(new URL('./index.html', ROOT).href);
        if (index) return index;
      }
      throw error;
    }
  })());
});
