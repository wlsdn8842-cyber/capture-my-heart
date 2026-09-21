from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path, old, new, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'bonus scene patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

# Stage 1-3 at 90%+ use their WebM bonus scenes in the clear modal.
rep(Path('game.js'),
"""  const continueBtn=!perfect?`<button id="keepBtn" class="btn secondary">KEEP PLAYING · ${target}</button>`:'';
  const artSrc=stageSrc(state.stage);
  openModal(`<div class="clear-review">
      <div class="clear-photo-wrap">
        <img id="clearPhoto" class="clear-photo" src="${artSrc}" alt="Stage ${state.stage} clear artwork" title="클릭해서 확대">
        <div class="clear-photo-badge">${title} · Stage ${state.stage} ${STAGES[state.stage].name}</div>
        <button id="clearZoomBtn" class="clear-zoom-btn" type="button" aria-label="클리어 이미지 확대">🔍 확대</button>
      </div>""",
"""  const continueBtn=!perfect?`<button id="keepBtn" class="btn secondary">KEEP PLAYING · ${target}</button>`:'';
  const artSrc=stageSrc(state.stage);
  const bonusSceneSrc=state.stage===1?'assets/bonus/stage1_maid_bonus.webm':state.stage===2?'assets/bonus/stage2_racinggirl_bonus.webm':state.stage===3?'assets/bonus/stage3_officelady_bonus.webm':'';
  const hasBonusScene=Boolean(bonusSceneSrc)&&level>=90;
  const mediaHtml=hasBonusScene
    ? `<video id="clearBonusVideo" class="clear-photo clear-bonus-video" src="${bonusSceneSrc}" autoplay muted loop playsinline preload="auto" poster="${artSrc}"></video>
       <img id="clearPhoto" class="clear-photo bonus-still-image hidden" src="${artSrc}" alt="Stage ${state.stage} clear artwork" title="클릭해서 확대">
       <div id="bonusUnlockBadge" class="bonus-scene-unlocked">♥ 90% BONUS SCENE UNLOCKED</div>`
    : `<img id="clearPhoto" class="clear-photo" src="${artSrc}" alt="Stage ${state.stage} clear artwork" title="클릭해서 확대">`;
  const mediaButton=hasBonusScene
    ? `<div class="bonus-media-actions">
         <button id="bonusReplayBtn" class="bonus-media-btn" type="button" aria-label="보너스 씬 다시 재생">↻ 다시 재생</button>
         <button id="bonusToggleBtn" class="bonus-media-btn" type="button" aria-label="일반 이미지 보기">🖼 일반 이미지</button>
       </div>`
    : `<button id="clearZoomBtn" class="clear-zoom-btn" type="button" aria-label="클리어 이미지 확대">🔍 확대</button>`;
  openModal(`<div class="clear-review">
      <div class="clear-photo-wrap">
        ${mediaHtml}
        <div class="clear-photo-badge">${title} · Stage ${state.stage} ${STAGES[state.stage].name}</div>
        ${mediaButton}
      </div>""",
'clear modal bonus media')

rep(Path('game.js'),
"""  const openZoom=()=>{track('clear_art_zoom',{stage:state.stage,area:state.area});showPhotoZoom(artSrc,`Stage ${state.stage} ${STAGES[state.stage].name}`)};
  $('#clearZoomBtn').onclick=openZoom;$('#clearPhoto').onclick=openZoom;
  if(!perfect)$('#keepBtn').onclick=()=>{track('keep_playing_click',{stage:state.stage,milestone:level});closeModal();state.paused=false;audio.resumeBase();toast(level===80?'90% 보너스를 노려보자!':'99%+ PERFECT를 노려보자!')};""",
"""  if(hasBonusScene){
    track('bonus_scene_view',{stage:state.stage,area:state.area,milestone:level});
    const video=$('#clearBonusVideo'),photo=$('#clearPhoto'),replay=$('#bonusReplayBtn'),toggle=$('#bonusToggleBtn'),badge=$('#bonusUnlockBadge');
    const openZoom=()=>{track('clear_art_zoom',{stage:state.stage,area:state.area});showPhotoZoom(artSrc,`Stage ${state.stage} ${STAGES[state.stage].name}`)};
    if(photo)photo.onclick=openZoom;
    const showStill=()=>{
      if(video){video.pause();video.classList.add('hidden')}
      if(photo)photo.classList.remove('hidden');
      if(replay)replay.classList.add('hidden');
      if(badge)badge.classList.add('hidden');
      if(toggle)toggle.textContent='🎬 서비스씬 보기';
      track('bonus_still_view',{stage:state.stage,area:state.area});
    };
    const showVideo=()=>{
      if(photo)photo.classList.add('hidden');
      if(video){video.classList.remove('hidden');video.currentTime=0;video.play().catch(()=>{})}
      if(replay)replay.classList.remove('hidden');
      if(badge)badge.classList.remove('hidden');
      if(toggle)toggle.textContent='🖼 일반 이미지';
      track('bonus_scene_return',{stage:state.stage,area:state.area});
    };
    if(video){
      video.play().catch(()=>{});
      video.onerror=()=>{showStill();if(toggle)toggle.classList.add('hidden');toast('보너스 영상 로드 실패 · 정지 이미지로 표시',true)};
    }
    if(replay)replay.onclick=()=>{if(video){video.currentTime=0;video.play().catch(()=>{});track('bonus_scene_replay',{stage:state.stage})}};
    if(toggle)toggle.onclick=()=>video?.classList.contains('hidden')?showVideo():showStill();
  }else{
    const openZoom=()=>{track('clear_art_zoom',{stage:state.stage,area:state.area});showPhotoZoom(artSrc,`Stage ${state.stage} ${STAGES[state.stage].name}`)};
    $('#clearZoomBtn').onclick=openZoom;$('#clearPhoto').onclick=openZoom;
  }
  if(!perfect)$('#keepBtn').onclick=()=>{track('keep_playing_click',{stage:state.stage,milestone:level});closeModal();state.paused=false;audio.resumeBase();toast(level===80?'90% 보너스를 노려보자!':'99%+ PERFECT를 노려보자!')};""",
'bonus scene controls')

# Add bonus-scene polish without changing the existing clear layout.
css=root/'styles.css'
with css.open('a',encoding='utf-8') as f:
    f.write(r"""

/* Stage 1-3 90%+ WebM bonus scenes */
.clear-bonus-video{background:#07050a;object-fit:contain!important;object-position:center center!important}
.bonus-still-image{object-fit:contain!important;object-position:center center!important;background:#07050a;cursor:zoom-in}
.bonus-scene-unlocked{position:absolute;left:50%;bottom:14px;transform:translateX(-50%);z-index:4;padding:7px 13px;border:1px solid rgba(255,122,188,.48);border-radius:999px;background:rgba(16,7,18,.78);backdrop-filter:blur(8px);color:#ffd1e8;font-size:.67rem;font-weight:950;letter-spacing:.08em;white-space:nowrap;box-shadow:0 0 22px rgba(255,64,157,.24)}
.bonus-media-actions{position:absolute;right:12px;top:12px;z-index:6;display:flex;gap:7px;flex-wrap:wrap;justify-content:flex-end}
.bonus-media-btn{border:1px solid rgba(255,255,255,.24);border-radius:999px;padding:7px 11px;background:rgba(12,7,18,.78);backdrop-filter:blur(8px);color:#fff;font-size:.68rem;font-weight:900;cursor:pointer;box-shadow:0 0 18px rgba(255,64,157,.18)}
.bonus-media-btn:hover{filter:brightness(1.15);transform:translateY(-1px)}
@media(max-width:600px){.bonus-scene-unlocked{bottom:10px;font-size:.56rem;padding:6px 9px}.bonus-media-actions{top:8px;right:8px;gap:5px}.bonus-media-btn{font-size:.58rem;padding:6px 8px}}
""")

print('stage1-3 bonus scene patch applied')
