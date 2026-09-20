(() => {
  'use strict';

  const cfg = window.CMH_CONFIG?.ANALYTICS || {};
  const QUEUE_KEY = 'cmh.analytics.queue';
  const VISITOR_KEY = 'cmh.analytics.visitor';
  const VISIT_KEY = 'cmh.analytics.visitNo';
  const SESSION_KEY = 'cmh.analytics.session';
  const SESSION_STARTED_KEY = 'cmh.analytics.sessionStartedAt';
  const FIRST_SEEN_KEY = 'cmh.analytics.firstSeenAt';
  const LAST_SEEN_KEY = 'cmh.analytics.lastSeenAt';
  let flushing = false;
  let heartbeatTimer = null;

  function enabled(){ return cfg.ENABLED !== false && !!cfg.ENDPOINT && !!cfg.API_KEY; }
  function uid(prefix='ev'){ return prefix+'_'+Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,9); }
  function safeLocalGet(k){ try{return localStorage.getItem(k)}catch(_){return null} }
  function safeLocalSet(k,v){ try{localStorage.setItem(k,v)}catch(_){} }
  function safeSessionGet(k){ try{return sessionStorage.getItem(k)}catch(_){return null} }
  function safeSessionSet(k,v){ try{sessionStorage.setItem(k,v)}catch(_){} }

  function visitorId(){
    let id=safeLocalGet(VISITOR_KEY);
    if(!id){ id=uid('v'); safeLocalSet(VISITOR_KEY,id); safeLocalSet(FIRST_SEEN_KEY,new Date().toISOString()); }
    return id;
  }
  function sessionId(){
    let id=safeSessionGet(SESSION_KEY);
    if(!id){
      id=uid('s');
      safeSessionSet(SESSION_KEY,id);
      safeSessionSet(SESSION_STARTED_KEY,String(Date.now()));
      const next=Math.max(1,(Number(safeLocalGet(VISIT_KEY))||0)+1);
      safeLocalSet(VISIT_KEY,String(next));
    }
    return id;
  }
  function visitNo(){ sessionId(); return Math.max(1,Number(safeLocalGet(VISIT_KEY))||1); }
  function sessionSeconds(){
    const start=Number(safeSessionGet(SESSION_STARTED_KEY))||Date.now();
    return Math.max(0,Math.min(86400,Math.round((Date.now()-start)/1000)));
  }
  function device(){
    const w=Math.min(window.innerWidth||9999,screen?.width||9999);
    const coarse=window.matchMedia?.('(pointer: coarse)')?.matches;
    if(coarse && w<=767)return 'mobile';
    if(coarse && w<=1100)return 'tablet';
    return 'desktop';
  }
  function referrerHost(){
    try{return document.referrer?new URL(document.referrer).hostname.slice(0,120):''}catch(_){return ''}
  }
  function readQueue(){ try{return JSON.parse(safeLocalGet(QUEUE_KEY)||'[]')}catch(_){return []} }
  function writeQueue(items){ safeLocalSet(QUEUE_KEY,JSON.stringify(items.slice(-(cfg.MAX_LOCAL_QUEUE||200)))) }
  function enqueue(x){const q=readQueue();q.push(x);writeQueue(q)}
  function remove(id){writeQueue(readQueue().filter(x=>x.id!==id))}
  function cleanParams(params={}){
    const out={};
    for(const [k,v] of Object.entries(params||{})){
      if(v===undefined || typeof v==='function')continue;
      if(typeof v==='string')out[k]=v.slice(0,160);
      else if(typeof v==='number'||typeof v==='boolean'||v===null)out[k]=v;
      else if(Array.isArray(v))out[k]=v.slice(0,12).map(x=>typeof x==='string'?x.slice(0,80):x);
    }
    return out;
  }
  function payload(name,params={}){
    const g=window.CMH_GAME?.state||{};
    return {
      id:uid('ev'),
      occurred_at:new Date().toISOString(),
      version:window.CMH_CONFIG?.VERSION||'',
      visitor_id:visitorId(),
      session_id:sessionId(),
      visit_no:visitNo(),
      event_name:String(name||'unknown').toLowerCase().replace(/[^a-z0-9_]/g,'_').slice(0,48),
      stage:Number.isFinite(Number(params.stage))?Number(params.stage):(Number(g.stage)||null),
      score:Number.isFinite(Number(params.score))?Math.max(0,Number(params.score)):(Number(g.score)||0),
      area:Number.isFinite(Number(params.area))?Math.max(0,Math.min(100,Number(params.area))):(Number(g.area)||0),
      lives:Number.isFinite(Number(params.lives))?Math.max(0,Number(params.lives)):(Number(g.lives)||0),
      session_seconds:sessionSeconds(),
      device:device(),
      viewport:`${window.innerWidth}x${window.innerHeight}`,
      language:(navigator.language||'').slice(0,16),
      referrer_host:referrerHost(),
      path:(location.pathname||'/').slice(0,160),
      params:cleanParams(params)
    };
  }
  async function post(item){
    if(!enabled())return false;
    const ac=new AbortController();
    const timer=setTimeout(()=>ac.abort(),cfg.REQUEST_TIMEOUT_MS||5500);
    try{
      const r=await fetch(cfg.ENDPOINT,{
        method:'POST',
        headers:{
          'Content-Type':'application/json',
          'apikey':cfg.API_KEY,
          'Authorization':'Bearer '+cfg.API_KEY,
          'Prefer':'return=minimal'
        },
        body:JSON.stringify(item),
        signal:ac.signal,
        keepalive:true
      });
      return r.ok || r.status===409;
    }catch(_){return false}
    finally{clearTimeout(timer)}
  }
  async function flush(){
    if(!enabled()||flushing)return;
    flushing=true;
    try{
      const q=readQueue();
      for(const item of q.slice(0,25)){
        const ok=await post(item);
        if(ok)remove(item.id); else break;
      }
    }finally{flushing=false}
  }
  function track(name,params={}){
    if(!enabled())return;
    const item=payload(name,params);
    enqueue(item);
    flush();
  }
  function heartbeat(){
    if(document.visibilityState==='visible')track('session_heartbeat',{visible:true});
  }
  function init(){
    visitorId();sessionId();
    safeLocalSet(LAST_SEEN_KEY,new Date().toISOString());
    track('session_start',{
      returning:visitNo()>1,
      visit_no:visitNo(),
      first_seen_at:(safeLocalGet(FIRST_SEEN_KEY)||'').slice(0,32)
    });
    track('page_view',{});
    flush();
    heartbeatTimer=setInterval(heartbeat,60000);
    document.addEventListener('visibilitychange',()=>{
      if(document.visibilityState==='hidden'){
        track('page_hidden',{});
      }else{
        track('page_visible',{});
        safeLocalSet(LAST_SEEN_KEY,new Date().toISOString());
      }
    });
    window.addEventListener('pagehide',()=>{track('session_end',{reason:'pagehide'});flush()});
    window.addEventListener('online',flush);
  }

  window.CMH_ANALYTICS={track,flush,sessionId,visitorId,visitNo,sessionSeconds,enabled};
  init();
})();
