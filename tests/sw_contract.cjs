/* Node VM simulation, NOT an actual browser service-worker test. */
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const scope = 'https://example.test/piano-studio-next/';
const prefix = 'piano-studio-next-v2:/piano-studio-next/:';
const stores = new Map();
const listeners = {};
const key = r => typeof r === 'string' ? r : r.url;
const makeStore = () => ({
  data: new Map(),
  async addAll(urls) { for (const url of urls) this.data.set(url, new Response('CACHED:' + url)); },
  async put(req, res) { this.data.set(key(req), res); },
  async match(req) { const r = this.data.get(key(req)); return r && r.clone(); }
});
const caches = {
  async keys() { return [...stores.keys()]; },
  async open(name) { if (!stores.has(name)) stores.set(name, makeStore()); return stores.get(name); },
  async delete(name) { return stores.delete(name); }
};
let offline = false, badStatus = false;
const context = {
  URL, caches,
  fetch: async req => { if (offline) throw new Error('offline'); return new Response('NETWORK', {status: badStatus ? 404 : 200}); },
  self: {registration: {scope}, clients: {claim: async () => {}}, addEventListener: (n,f) => {listeners[n] = f;}}
};
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(__dirname,'..','app','sw.js'),'utf8').replace('__BUILD_ID__','TEST'),context);
let count=0;
function check(name, fn) { fn(); count++; console.log('PASS',name); }
async function lifecycle(name) { let p; listeners[name]({waitUntil: x => {p=x;}}); await p; }
async function request(url, method='GET') { let handled=false,p; listeners.fetch({request:new Request(url,{method}),respondWith:x=>{handled=true;p=x;}}); return {handled,response:handled?await p:null}; }
(async () => {
  for (const name of ['hps-v15','piano-studio-v1:/piano-studio/:OLD','another-app',prefix+'OLD','piano-studio-next-v2:/other/:OLD']) await caches.open(name);
  await lifecycle('install'); await lifecycle('activate');
  check('namespaced v1 cache retained',()=>assert(stores.has('piano-studio-v1:/piano-studio/:OLD')));
  check('v1 cache retained',()=>assert(stores.has('hps-v15')));
  check('other app cache retained',()=>assert(stores.has('another-app')));
  check('same app other-scope cache retained',()=>assert(stores.has('piano-studio-next-v2:/other/:OLD')));
  check('old own-scope cache deleted',()=>assert(!stores.has(prefix+'OLD')));
  check('new cache installed',()=>assert(stores.has(prefix+'TEST')));
  let r=await request(scope+'index.html');check('network app responds',()=>assert(r.handled&&r.response.ok));
  offline=true;r=await request(scope+'index.html');const cached=await r.response.text();check('cached app used on network failure',()=>assert.equal(cached,'NETWORK'));
  r=await request(scope+'bp.bundle.js');check('model asset available in simulated cache',()=>assert(r.handled&&r.response.ok));
  r=await request(scope+'app/version-switch.js');check('switcher available offline',()=>assert(r.handled&&r.response.ok));
  r=await request(scope+'missing.js');check('missing script not replaced with HTML',()=>assert(!r.handled));
  r=await request('https://example.test/piano-studio/index.html');check('v1 requests not intercepted',()=>assert(!r.handled));
  r=await request(scope+'index.html','POST');check('non-GET requests ignored',()=>assert(!r.handled));
  r=await request('https://unrelated.test/index.html');check('external requests ignored',()=>assert(!r.handled));
  offline=false;badStatus=true;r=await request(scope+'index.html');const fallback=await r.response.text();check('HTTP error does not overwrite good cache',()=>assert.equal(fallback,'NETWORK'));
  badStatus=false; r=await request('https://fonts.googleapis.com/css2?family=Jua');check('font loaded in own cache',()=>assert(r.handled&&r.response.ok));
  offline=true;r=await request('https://fonts.googleapis.com/css2?family=Jua');check('font available offline',()=>assert(r.handled&&r.response.ok));
  console.log(JSON.stringify({scope:'Node VM simulation, not browser PWA execution',passed:count,total:count}));
})().catch(error=>{console.error(error);process.exitCode=1;});
