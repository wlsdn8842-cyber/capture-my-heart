(() => {
  'use strict';

  const cfg = window.CMH_CONFIG?.COLLECTION || {};
  let overlay = null;

  function enabled(){ return cfg.ENABLED !== false && !!cfg.ENDPOINT; }
  function esc(s=''){ return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
  function track(name, params={}){ try{ window.CMH_ANALYTICS?.track?.(name, params); }catch(_){} }
  function sessionId(){ try{return window.CMH_ANALYTICS?.sessionId?.()||''}catch(_){return ''} }

  function injectStyles(){
    if(document.getElementById('cmhCollectionStyles')) return;
    const s=document.createElement('style');
    s.id='cmhCollectionStyles';
    s.textContent=`
      .cmh-collection-overlay{position:fixed;inset:0;z-index:10030;background:rgba(3,1,8,.9);display:flex;align-items:center;justify-content:center;padding:16px;backdrop-filter:blur(11px)}
      .cmh-collection-card{width:min(590px,96vw);max-height:94vh;overflow:auto;background:linear-gradient(150deg,rgba(43,12,58,.99),rgba(8,5,19,.99));border:1px solid rgba(255,255,255,.2);border-radius:24px;padding:22px;box-shadow:0 28px 90px rgba(0,0,0,.7)}
      .cmh-collection-head{display:flex;align-items:flex-start;gap:12px}.cmh-collection-head>div{flex:1}.cmh-collection-head h2{margin:2px 0 5px}.cmh-collection-badge{font-size:.72rem;font-weight:900;letter-spacing:.08em;color:#ffb6d8}
      .cmh-collection-x{width:42px;height:42px;border-radius:50%;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.07);cursor:pointer}
      .cmh-collection-card label{display:block;margin:16px 0 7px;font-weight:850}.cmh-collection-card input[type=email]{width:100%;min-height:48px;border-radius:14px;border:1px solid rgba(255,255,255,.18);background:#12091b;color:#fff;padding:11px 13px;font:inherit;outline:none}
      .cmh-collection-card input[type=email]:focus{border-color:#ff70b5;box-shadow:0 0 0 3px rgba(255,112,181,.12)}
      .cmh-collection-consent{display:flex!important;align-items:flex-start;gap:9px;margin:15px 0 8px!important;padding:12px;border:1px solid rgba(255,255,255,.11);border-radius:14px;background:rgba(255,255,255,.045);font-weight:650!important;line-height:1.45}
      .cmh-collection-consent input{margin-top:3px;flex:0 0 auto}.cmh-collection-note{font-size:.77rem;color:#cbbbd0;line-height:1.55}.cmh-collection-note a{color:#ff9aca}
      .cmh-collection-status{min-height:24px;margin:11px 0;color:#ffe0ef;font-size:.88rem}.cmh-collection-actions{display:flex;gap:9px;margin-top:10px}.cmh-collection-actions>*{flex:1}
      .cmh-collection-success{padding:14px;border-radius:16px;background:rgba(77,214,155,.08);border:1px solid rgba(77,214,155,.25);margin:14px 0}.cmh-collection-success strong{display:block;margin-bottom:4px;color:#9cffd1}
      .cmh-honeypot{position:absolute!important;left:-9999px!important;width:1px!important;height:1px!important;opacity:0!important;pointer-events:none!important}
      .ending-collection{margin:12px 0 10px;padding:12px;border:1px solid rgba(255,105,181,.25);border-radius:16px;background:rgba(255,79,163,.065);text-align:center}.ending-collection .btn{width:100%}.ending-collection small{display:block;margin-top:7px;color:#d9c5dc}
      @media(max-width:600px){.cmh-collection-card{padding:17px}.cmh-collection-actions{flex-direction:column}.cmh-collection-actions>*{width:100%}}
    `;
    document.head.appendChild(s);
  }

  function close(){
    if(overlay){overlay.remove();overlay=null}
  }

  async function submit(form, score){
    const status=form.querySelector('#cmhCollectionStatus');
    const submitBtn=form.querySelector('#cmhCollectionSubmit');
    const email=String(form.querySelector('#cmhCollectionEmail')?.value||'').trim();
    const marketingConsent=!!form.querySelector('#cmhMarketingConsent')?.checked;
    const website=String(form.querySelector('#cmhCompany')?.value||'');
    if(!email){status.textContent='이메일 주소를 입력해 주세요.';return}

    submitBtn.disabled=true;
    status.textContent='컬렉션 링크를 준비하는 중…';
    track('collection_request_start',{marketing_consent:marketingConsent});

    try{
      const res=await fetch(cfg.ENDPOINT,{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
          email,
          marketingConsent,
          consentVersion:cfg.CONSENT_VERSION||'',
          gameVersion:window.CMH_CONFIG?.VERSION||'',
          score:Number(score||0),
          sessionId:sessionId(),
          website
        })
      });
      const data=await res.json().catch(()=>({}));
      if(!res.ok || !data?.ok){
        if(res.status===429) throw new Error('rate_limited');
        if(res.status>=500) throw new Error('server_error');
        throw new Error(data?.code||'request_failed');
      }

      track('collection_request_complete',{
        marketing_consent:marketingConsent,
        delivery:data.delivery||'unknown'
      });

      const sent=data.delivery==='sent';
      form.innerHTML=`
        <div class="cmh-collection-head"><div><div class="cmh-collection-badge">COMPLETE COLLECTION</div><h2>♥ 준비됐어요!</h2></div><button type="button" class="cmh-collection-x" id="cmhCollectionClose2" aria-label="닫기">✕</button></div>
        <div class="cmh-collection-success"><strong>${sent?'이메일 발송 완료':'컬렉션 요청 저장 완료'}</strong>
          ${sent?'입력한 이메일로 Complete Collection 링크를 보냈습니다.':'현재 자동 메일 발송 공급자가 연결되기 전이라, 아래 버튼에서 지금 바로 컬렉션을 받을 수 있습니다.'}
        </div>
        ${marketingConsent?'<p class="cmh-collection-note">게임 업데이트·이벤트·신작 등 광고성 이메일 수신 동의도 저장했습니다. 광고 메일에는 수신거부 링크가 제공됩니다.</p>':''}
        <div class="cmh-collection-actions"><a class="btn primary" id="cmhCollectionOpen" href="${esc(data.collectionUrl||'#')}" target="_blank" rel="noopener">MY COLLECTION 열기</a><button type="button" class="btn tertiary" id="cmhCollectionDone">닫기</button></div>`;
      form.querySelector('#cmhCollectionClose2').onclick=close;
      form.querySelector('#cmhCollectionDone').onclick=close;
      form.querySelector('#cmhCollectionOpen').onclick=()=>track('collection_claim_open',{delivery:data.delivery||'unknown'});
    }catch(err){
      submitBtn.disabled=false;
      const code=String(err?.message||'');
      status.textContent=code==='rate_limited'
        ? '짧은 시간에 요청이 너무 많습니다. 잠시 후 다시 시도해 주세요.'
        : code==='server_error'
          ? '서버 처리 중 문제가 발생했습니다. 잠시 후 다시 시도해 주세요.'
          : '요청을 저장하지 못했습니다. 네트워크 상태를 확인하고 다시 시도해 주세요.';
      track('collection_request_error',{code:code.slice(0,60)});
    }
  }

  function show({score=0}={}){
    if(!enabled()) return;
    injectStyles();
    close();
    overlay=document.createElement('div');
    overlay.className='cmh-collection-overlay';
    overlay.setAttribute('role','dialog');
    overlay.setAttribute('aria-modal','true');
    overlay.setAttribute('aria-label','Complete Collection 이메일 받기');
    overlay.innerHTML=`
      <form class="cmh-collection-card" id="cmhCollectionForm">
        <div class="cmh-collection-head">
          <div><div class="cmh-collection-badge">ALL STAGES CLEAR REWARD</div><h2>📩 MY COMPLETE COLLECTION</h2></div>
          <button type="button" class="cmh-collection-x" id="cmhCollectionClose" aria-label="닫기">✕</button>
        </div>
        <p class="muted">완주한 Stage 1~10 이미지를 한 번에 저장할 수 있는 컬렉션 링크를 받아보세요.</p>
        <label for="cmhCollectionEmail">이메일</label>
        <input id="cmhCollectionEmail" type="email" inputmode="email" autocomplete="email" maxlength="254" required placeholder="you@example.com">
        <input id="cmhCompany" class="cmh-honeypot" type="text" tabindex="-1" autocomplete="off" aria-hidden="true">
        <label class="cmh-collection-consent" for="cmhMarketingConsent">
          <input id="cmhMarketingConsent" type="checkbox">
          <span><b>[선택]</b> Capture My Heart의 게임 업데이트·이벤트·신작 등 <b>광고성 정보</b>를 이메일로 받겠습니다.</span>
        </label>
        <p class="cmh-collection-note">광고 수신에 동의하지 않아도 컬렉션을 받을 수 있습니다. 보상 발송용 이메일은 최대 7일 후 삭제됩니다. 마케팅에 동의한 이메일은 수신 철회 전까지 구독 정보로 처리됩니다. <a href="privacy.html" target="_blank" rel="noopener">개인정보처리방침</a></p>
        <div id="cmhCollectionStatus" class="cmh-collection-status" aria-live="polite"></div>
        <div class="cmh-collection-actions"><button type="button" class="btn tertiary" id="cmhCollectionLater">나중에</button><button type="submit" class="btn primary" id="cmhCollectionSubmit">컬렉션 받기</button></div>
      </form>`;
    document.body.appendChild(overlay);
    track('collection_open',{score:Number(score||0)});
    const form=overlay.querySelector('#cmhCollectionForm');
    overlay.querySelector('#cmhCollectionClose').onclick=close;
    overlay.querySelector('#cmhCollectionLater').onclick=close;
    overlay.addEventListener('click',e=>{if(e.target===overlay)close()});
    form.addEventListener('submit',e=>{e.preventDefault();submit(form,score)});
    setTimeout(()=>overlay?.querySelector('#cmhCollectionEmail')?.focus(),60);
  }

  injectStyles();
  window.CMH_COLLECTION={show,close,enabled};
})();