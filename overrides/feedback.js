(() => {
  'use strict';

  const cfg = window.CMH_CONFIG?.FEEDBACK || {};
  const QUEUE_KEY = 'cmh.feedback.queue';
  const SESSION_KEY = 'cmh.feedback.session';
  let overlay = null;
  let restorePause = false;

  function enabled(){ return cfg.ENABLED !== false; }
  function uid(){ return 'fb_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2,8); }
  function sessionId(){
    try{
      let id=sessionStorage.getItem(SESSION_KEY);
      if(!id){id=uid();sessionStorage.setItem(SESSION_KEY,id)}
      return id;
    }catch(_){return uid()}
  }
  function readQueue(){ try{return JSON.parse(localStorage.getItem(QUEUE_KEY)||'[]')}catch(_){return []} }
  function writeQueue(items){ try{localStorage.setItem(QUEUE_KEY,JSON.stringify(items.slice(-(cfg.MAX_LOCAL_QUEUE||50))))}catch(_){} }
  function enqueue(payload){ const q=readQueue(); q.push(payload); writeQueue(q); }
  function removeQueued(id){ writeQueue(readQueue().filter(x=>x.id!==id)); }

  function track(name, params={}){
    try{ window.gtag?.('event', name, params); }catch(_){}
  }

  async function post(payload){
    if(!cfg.ENDPOINT || !cfg.API_KEY) return {ok:false,reason:'no_endpoint'};
    const ac = new AbortController();
    const timer=setTimeout(()=>ac.abort(),cfg.REQUEST_TIMEOUT_MS||6500);
    try{
      const res=await fetch(cfg.ENDPOINT,{
        method:'POST',
        headers:{
          'Content-Type':'application/json',
          'apikey':cfg.API_KEY,
          'Authorization':'Bearer '+cfg.API_KEY,
          'Prefer':'return=minimal'
        },
        body:JSON.stringify(payload),
        signal:ac.signal,
        keepalive:true
      });
      // Primary key makes retries idempotent: if a prior request reached Supabase
      // but the response was lost, a duplicate-id 409 means it is already stored.
      if(res.ok || res.status===409) return {ok:true,status:res.status,duplicate:res.status===409};
      let detail='';
      try{detail=(await res.text()).slice(0,300)}catch(_){}
      return {ok:false,status:res.status,detail};
    }catch(e){return {ok:false,reason:e?.name||'network_error'}}
    finally{clearTimeout(timer)}
  }

  async function submit(payload){
    enqueue(payload);
    const result=await post(payload);
    if(result.ok) removeQueued(payload.id);
    return result;
  }

  async function flushQueue(){
    if(!cfg.ENDPOINT || !cfg.API_KEY) return;
    const q=readQueue();
    for(const item of q.slice(0,10)){
      const r=await post(item);
      if(r.ok) removeQueued(item.id);
      else break;
    }
  }

  function close(){
    if(!overlay)return;
    overlay.remove();overlay=null;
    const g=window.CMH_GAME;
    if(g?.state?.mode==='playing' && restorePause===false){
      g.state.paused=false;
      g.state.lastTs=performance.now();
      g.audio?.resumeBase?.();
    }
  }

  function chipGroup(name, values, selected=''){
    return `<div class="fb-chip-group" role="group" aria-label="${name}">${values.map(v=>`<button type="button" class="fb-chip ${selected===v.value?'selected':''}" data-field="${name}" data-value="${v.value}">${v.label}</button>`).join('')}</div>`;
  }

  function show(source='manual'){
    if(!enabled())return;
    if(overlay)overlay.remove();
    const g=window.CMH_GAME;
    restorePause=!!g?.state?.paused;
    if(g?.state?.mode==='playing')g.state.paused=true;

    const st=g?.state||{};
    overlay=document.createElement('div');
    overlay.className='feedback-overlay';
    overlay.setAttribute('role','dialog');overlay.setAttribute('aria-modal','true');overlay.setAttribute('aria-label','게임 피드백');
    overlay.innerHTML=`<form class="feedback-card" id="cmhFeedbackForm">
      <div class="feedback-head"><div><small>30초면 됩니다</small><h2>💬 이 게임, 어땠나요?</h2></div><button type="button" id="fbClose" class="fb-x" aria-label="닫기">✕</button></div>
      <p class="muted">재미와 난이도를 먼저 보고 빠르게 다듬는 공개 베타입니다.</p>

      <label class="fb-label">재미있었나요?</label>
      ${chipGroup('fun',[1,2,3,4,5].map(n=>({value:String(n),label:'♥'.repeat(n)})))}

      <label class="fb-label">난이도는 어땠나요?</label>
      ${chipGroup('difficulty',[{value:'easy',label:'쉬움'},{value:'good',label:'딱 좋음'},{value:'hard',label:'어려움'}])}

      <label class="fb-label">다음 캐릭터가 궁금해서 계속 하고 싶었나요?</label>
      ${chipGroup('curiosity',[{value:'yes',label:'응, 계속!'},{value:'maybe',label:'조금'},{value:'no',label:'아니'}])}

      <label class="fb-label" for="fbComment">한 가지만 바꾼다면?</label>
      <textarea id="fbComment" maxlength="500" placeholder="조작, 난이도, 음악, 이미지, 버그… 자유롭게"></textarea>

      <div id="fbStatus" class="fb-status" aria-live="polite"></div>
      <div class="feedback-actions"><button type="button" id="fbLater" class="btn tertiary">나중에</button><button type="submit" class="btn primary">피드백 보내기</button></div>
    </form>`;
    document.body.appendChild(overlay);
    track('feedback_open',{source,stage:st.stage||0});

    const picks={fun:'',difficulty:'',curiosity:''};
    overlay.querySelectorAll('.fb-chip').forEach(btn=>btn.addEventListener('click',()=>{
      const field=btn.dataset.field,value=btn.dataset.value;picks[field]=value;
      overlay.querySelectorAll(`.fb-chip[data-field="${field}"]`).forEach(x=>x.classList.toggle('selected',x===btn));
    }));
    overlay.querySelector('#fbClose').onclick=close;
    overlay.querySelector('#fbLater').onclick=close;
    overlay.addEventListener('click',e=>{if(e.target===overlay)close()});
    overlay.querySelector('#cmhFeedbackForm').addEventListener('submit',async e=>{
      e.preventDefault();
      const status=overlay.querySelector('#fbStatus');
      if(!picks.fun){status.textContent='재미 점수만 먼저 골라주세요 🙂';return}
      const payload={
        id:uid(),
        created_at:new Date().toISOString(),
        version:window.CMH_CONFIG?.VERSION||'',
        session_id:sessionId(),
        source,
        stage:Number(st.stage||0),
        score:Number(st.score||0),
        area:Number((st.area||0).toFixed?.(1) ?? st.area ?? 0),
        lives:Number(st.lives||0),
        fun:Number(picks.fun),
        difficulty:picks.difficulty||null,
        curiosity:picks.curiosity||null,
        comment:overlay.querySelector('#fbComment').value.trim(),
        viewport:`${window.innerWidth}x${window.innerHeight}`,
        touch:matchMedia('(pointer: coarse)').matches,
        user_agent:navigator.userAgent.slice(0,240)
      };
      status.textContent='보내는 중…';
      const result=await submit(payload);
      track('feedback_submit',{source,stage:payload.stage,fun:payload.fun,difficulty:payload.difficulty||'none',curiosity:payload.curiosity||'none',delivered:!!result.ok});
      if(result.ok){status.textContent='고마워요! 피드백이 전송됐습니다 ♥';setTimeout(close,900)}
      else if(result.reason==='no_endpoint'){
        status.innerHTML='피드백을 이 기기에 저장했습니다. <b>수집 서버 연결 전 베타 모드</b>입니다.';
        setTimeout(close,1500);
      }else{status.textContent='네트워크 문제로 이 기기에 임시 저장했습니다. 다음 접속 때 다시 전송합니다.';setTimeout(close,1800)}
    });
  }

  function queueSize(){return readQueue().length}
  window.CMH_FEEDBACK={show,submit,flushQueue,queueSize,enabled};
  setTimeout(flushQueue,1200);
})();
