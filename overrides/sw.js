const CACHE='cmh-core-v0.5.4.1';
const CORE=['./','index.html','styles.css','config.js','ads.js','analytics.js','feedback.js','game.js','manifest.webmanifest','privacy.html','assets/images/title.webp','assets/audio/main.mp3'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET')return;
  e.respondWith(caches.match(e.request).then(hit=>hit||fetch(e.request).then(res=>{const copy=res.clone();caches.open(CACHE).then(c=>c.put(e.request,copy)).catch(()=>{});return res}).catch(()=>hit)));
});
