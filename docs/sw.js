const C='uti-v6-2026-10-08';
const A=['./','manifest.webmanifest','icon-192.png','icon-512.png','apple-touch-icon.png','fonts/atkinson-400.woff2','fonts/atkinson-700.woff2'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(A.map(u=>new Request(u,{cache:'reload'})))).then(()=>self.skipWaiting()));});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',e=>{
  const r=e.request; if(r.method!=='GET'||new URL(r.url).origin!==location.origin)return;
  const key=r.mode==='navigate'?'./':r;
  e.respondWith(caches.open(C).then(async c=>{
    const hit=await c.match(key,{ignoreSearch:true});
    const net=fetch(r).then(res=>{if(res.ok&&!res.redirected)c.put(key,res.clone());return res;}).catch(()=>hit);
    return hit||net;
  }));
});
