(() => {
  const ENDPOINT='https://cvfmikycscmfjmooxhni.supabase.co/functions/v1/cmh-admin-dashboard';
  const KEY_STORE='cmh.admin.sessionKey';
  let adminKey=sessionStorage.getItem(KEY_STORE)||'';
  let range='7d', timer=null;

  const $=s=>document.querySelector(s);
  const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const fmt=n=>Number(n||0).toLocaleString('ko-KR');
  const duration=s=>{s=Number(s||0);if(s<60)return s+'초';const m=Math.floor(s/60),r=s%60;return r?m+'분 '+r+'초':m+'분'};
  const kst=iso=>new Intl.DateTimeFormat('ko-KR',{timeZone:'Asia/Seoul',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'}).format(new Date(iso));
  const toast=msg=>{const t=$('#toast');t.textContent=msg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),1800)};

  async function fetchData(key=adminKey){
    const r=await fetch(ENDPOINT+'?range='+encodeURIComponent(range),{headers:{'x-admin-token':key},cache:'no-store'});
    if(r.status===401)throw new Error('AUTH');
    if(!r.ok)throw new Error('HTTP '+r.status);
    return r.json();
  }
  async function login(e){
    e?.preventDefault();
    const key=$('#adminKey').value.trim();
    if(!key)return;
    $('#loginError').textContent='확인 중…';
    try{
      const data=await fetchData(key);
      adminKey=key;sessionStorage.setItem(KEY_STORE,key);
      $('#loginGate').classList.add('hidden');$('#dashboard').classList.remove('hidden');
      $('#loginError').textContent='';render(data);startAuto();
    }catch(err){
      $('#loginError').textContent=err.message==='AUTH'?'관리자 키가 맞지 않습니다.':'연결에 실패했습니다. 잠시 후 다시 시도해주세요.';
    }
  }
  async function refresh(silent=false){
    if(!adminKey)return;
    if(!silent)$('#refreshBtn').textContent='…';
    try{render(await fetchData());if(!silent)toast('최신 데이터로 갱신했습니다.')}
    catch(e){if(e.message==='AUTH')lock();else toast('갱신 실패');}
    finally{$('#refreshBtn').textContent='↻'}
  }
  function lock(){
    adminKey='';sessionStorage.removeItem(KEY_STORE);$('#dashboard').classList.add('hidden');$('#loginGate').classList.remove('hidden');$('#adminKey').value='';$('#adminKey').focus();stopAuto();
  }
  function startAuto(){stopAuto();timer=setInterval(()=>refresh(true),60000)}
  function stopAuto(){if(timer)clearInterval(timer);timer=null}

  function render(d){
    const t=d.totals||{};
    $('#mVisitors').textContent=fmt(t.visitors);
    $('#mSessions').textContent=fmt(t.sessions);
    $('#mStarts').textContent=fmt(t.gameStarts);
    $('#mStartRate').textContent='시작률 '+(t.startRate||0)+'%';
    $('#mAvgTime').textContent=duration(t.avgSessionSec);
    $('#mReturning').textContent=fmt(t.returningVisitors);
    $('#mMaxStage').textContent='Stage '+fmt(t.maxStage);
    $('#mComplete').textContent=fmt(t.completions);
    $('#mFeedback').textContent=fmt(t.feedback);
    $('#mFun').textContent=d.feedbackSummary?.avgFun?('평균 재미 '+d.feedbackSummary.avgFun+' / 5'):'평균 재미 —';
    $('#lastUpdated').textContent='업데이트 '+kst(d.generatedAt);

    renderFunnel(d.funnel||[]);
    renderRank('#deaths',(d.deaths||[]).map(x=>({name:x.reason,value:x.count})));
    renderRank('#sources',(d.sources||[]).map(x=>({name:x.source,value:x.sessions})));
    renderDevices(d.devices||[]);
    renderDaily(d.daily||[]);
    renderFeedback(d.latestFeedback||[],d.feedbackSummary||{});
    renderSessions(d.recentSessions||[]);
  }
  function renderFunnel(rows){
    const max=Math.max(1,...rows.map(r=>r.entrants));
    $('#funnel').innerHTML=rows.map(r=>{
      const ew=Math.max(r.entrants?4:0,r.entrants/max*100),cw=r.entrants?Math.min(100,r.clearers/r.entrants*100):0;
      return '<div class="funnel-row"><div class="funnel-stage">STAGE '+r.stage+'</div><div class="bar-track"><i class="bar-enter" style="width:'+ew+'%"></i><i class="bar-clear" style="width:'+cw+'%"></i></div><div class="funnel-numbers"><b>'+r.entrants+'</b> → '+r.clearers+' <small>('+r.clearRate+'%)</small></div></div>';
    }).join('');
  }
  function renderRank(sel,rows){
    const el=$(sel);if(!rows.length){el.className='rank-list empty-state';el.textContent='아직 데이터가 없습니다.';return}
    el.className='rank-list';const max=Math.max(1,...rows.map(x=>x.value));
    el.innerHTML=rows.slice(0,10).map(x=>'<div class="rank-item"><div class="name">'+esc(x.name)+'</div><div class="value">'+fmt(x.value)+'</div><div class="mini-track"><i style="width:'+(x.value/max*100)+'%"></i></div></div>').join('');
  }
  function renderDevices(rows){
    const labels={desktop:'PC',mobile:'모바일',tablet:'태블릿',unknown:'기타'};
    const total=rows.reduce((a,b)=>a+b.sessions,0)||1;
    $('#devices').innerHTML=(rows.length?rows:[{device:'desktop',sessions:0},{device:'mobile',sessions:0},{device:'tablet',sessions:0}]).map(x=>'<div class="device"><b>'+Math.round(x.sessions/total*100)+'%</b><span>'+esc(labels[x.device]||x.device)+' · '+fmt(x.sessions)+'</span></div>').join('');
  }
  function renderDaily(rows){
    if(!rows.length){$('#daily').innerHTML='<div class="empty-state">아직 데이터가 없습니다.</div>';return}
    const max=Math.max(1,...rows.flatMap(x=>[x.visitors,x.gameStarts]));
    $('#daily').innerHTML=rows.map(x=>'<div class="day"><small>'+x.visitors+' / '+x.gameStarts+'</small><div class="day-bars"><i title="방문자" style="height:'+(x.visitors/max*100)+'%"></i><i title="게임 시작" style="height:'+(x.gameStarts/max*100)+'%"></i></div><label>'+esc(x.date.slice(5))+'</label></div>').join('');
  }
  function renderFeedback(rows,s){
    $('#feedbackSummary').textContent='재미 '+(s.avgFun??'—')+' · 다음 캐릭터 YES '+fmt(s.curiosityYes);
    const el=$('#feedbackList');
    if(!rows.length){el.innerHTML='<div class="empty-state">아직 피드백이 없습니다.</div>';return}
    el.innerHTML=rows.map(x=>{
      const stars='★'.repeat(Math.max(0,Math.min(5,Number(x.fun)||0)))+'☆'.repeat(Math.max(0,5-(Number(x.fun)||0)));
      const comment=x.comment?'<p>'+esc(x.comment)+'</p>':'';
      return '<div class="feedback"><div class="feedback-top"><span class="stars">'+stars+'</span><span>'+kst(x.received_at)+' · Stage '+(x.stage||'-')+'</span></div><div class="tags"><span class="tag">난이도 '+esc(x.difficulty||'-')+'</span><span class="tag">다음 캐릭터 '+esc(x.curiosity||'-')+'</span><span class="tag">'+esc(x.source||'-')+'</span></div>'+comment+'</div>';
    }).join('');
  }
  function renderSessions(rows){
    const body=$('#sessionRows');
    if(!rows.length){body.innerHTML='<tr><td colspan="5">아직 플레이 데이터가 없습니다.</td></tr>';return}
    body.innerHTML=rows.map(x=>'<tr><td>'+kst(x.startedAt)+'</td><td><span class="stage-pill">S'+(x.maxStage||0)+'</span></td><td>'+duration(x.seconds)+'</td><td>'+fmt(x.deaths)+'</td><td>'+esc(x.device||'unknown')+(x.visitNo>1?' · 재방문':'')+'</td></tr>').join('');
  }

  $('#loginForm').addEventListener('submit',login);
  $('#refreshBtn').addEventListener('click',()=>refresh(false));
  $('#lockBtn').addEventListener('click',lock);
  $('#rangeTabs').addEventListener('click',e=>{
    const b=e.target.closest('button[data-range]');if(!b)return;
    range=b.dataset.range;document.querySelectorAll('#rangeTabs button').forEach(x=>x.classList.toggle('active',x===b));refresh(true);
  });

  if(adminKey){
    fetchData().then(d=>{$('#loginGate').classList.add('hidden');$('#dashboard').classList.remove('hidden');render(d);startAuto()}).catch(()=>lock());
  }else setTimeout(()=>$('#adminKey').focus(),50);
})();