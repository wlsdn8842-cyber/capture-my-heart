from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path, old, new, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'mobile ux v2 patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

marker="const joy=$('#moveJoystick'),joyKnob=$('#joystickKnob');\n"
block=r'''function mobileUXActive(){return !!window.matchMedia?.('(pointer: coarse)')?.matches}
let mobileCaptureLocked=false;
function syncMobileCaptureButton(){
  const b=$('#captureTouchBtn');if(!b)return;
  const on=mobileUXActive()&&mobileCaptureLocked;
  b.classList.toggle('capture-locked',on);
  b.setAttribute('aria-pressed',on?'true':'false');
  b.textContent=on?'CAPTURE ON':'CAPTURE';
}
function setMobileCaptureLock(on,reason='manual'){
  if(!mobileUXActive())return;
  const next=!!on;
  if(next===mobileCaptureLocked){input.capture=next;syncMobileCaptureButton();return}
  mobileCaptureLocked=next;input.capture=next;syncMobileCaptureButton();
  track(next?'mobile_capture_lock_on':'mobile_capture_lock_off',{reason});
  if(next)stopAutoRetract();
}
function resetMobileCaptureLock(reason='reset'){
  if(!mobileUXActive())return;
  if(mobileCaptureLocked)setMobileCaptureLock(false,reason);
  else{input.capture=false;syncMobileCaptureButton()}
}
function updateMobileViewportVars(){
  if(!mobileUXActive())return;
  const vv=window.visualViewport;
  const w=Math.max(1,Math.round(vv?.width||window.innerWidth||document.documentElement.clientWidth||1));
  const h=Math.max(1,Math.round(vv?.height||window.innerHeight||document.documentElement.clientHeight||1));
  document.documentElement.style.setProperty('--mobile-vw',w+'px');
  document.documentElement.style.setProperty('--mobile-vh',h+'px');
}
if(mobileUXActive()){
  updateMobileViewportVars();
  window.addEventListener('resize',updateMobileViewportVars,{passive:true});
  window.addEventListener('orientationchange',()=>setTimeout(updateMobileViewportVars,80),{passive:true});
  window.visualViewport?.addEventListener('resize',updateMobileViewportVars,{passive:true});
  window.visualViewport?.addEventListener('scroll',updateMobileViewportVars,{passive:true});
}
'''
rep(Path('game.js'),marker,block+marker,'mobile helpers')

old=r'''const cap=$('#captureTouchBtn');bindHoldButton(cap,()=>{input.capture=true;stopAutoRetract()},()=>{input.capture=false;beginAutoRetract()});
const dashBtn=$('#dashTouchBtn');bindHoldButton(dashBtn,()=>{input.dash=true},()=>{input.dash=false});
'''
new=r'''const cap=$('#captureTouchBtn');
if(cap){
  cap.setAttribute('aria-pressed','false');
  cap.addEventListener('pointerdown',e=>{
    if(!mobileUXActive())return;
    e.preventDefault();
    if(mobileCaptureLocked){
      setMobileCaptureLock(false,'manual');
      if(state.player?.drawing)beginAutoRetract();
    }else{
      setMobileCaptureLock(true,'manual');
    }
    navigator.vibrate?.(10);
  });
  cap.addEventListener('contextmenu',e=>e.preventDefault());
  syncMobileCaptureButton();
}
const dashBtn=$('#dashTouchBtn');bindHoldButton(dashBtn,()=>{input.dash=true},()=>{input.dash=false});
'''
rep(Path('game.js'),old,new,'mobile one-shot capture')

old="  state.player.drawing=false;state.player.autoRetract=false;state.player.trailPath=[];rebuildVisualLayers();state.lastArea=before;state.area=calcArea();\n"
new="  state.player.drawing=false;state.player.autoRetract=false;state.player.trailPath=[];rebuildVisualLayers();state.lastArea=before;state.area=calcArea();\n  if(mobileUXActive())resetMobileCaptureLock('capture_complete');\n"
rep(Path('game.js'),old,new,'capture complete unlock')

old="  else{p.x=p.trailStart.x;p.y=p.trailStart.y;p.drawing=false;p.autoRetract=false;p.trailPath=[];audio.beep(310,.055,'triangle',.016);toast('라인 회수')}\n"
new="  else{p.x=p.trailStart.x;p.y=p.trailStart.y;p.drawing=false;p.autoRetract=false;p.trailPath=[];if(mobileUXActive())resetMobileCaptureLock('retract_complete');audio.beep(310,.055,'triangle',.016);toast('라인 회수')}\n"
rep(Path('game.js'),old,new,'retract complete unlock')

old="function clearTrail(){for(let i=0;i<grid.length;i++)if(grid[i]===TRAIL)grid[i]=UNCLAIMED;const p=state.player;p.x=p.trailStart.x;p.y=p.trailStart.y;p.drawing=false;p.autoRetract=false;p.trailPath=[];rebuildVisualLayers()}"
new="function clearTrail(){for(let i=0;i<grid.length;i++)if(grid[i]===TRAIL)grid[i]=UNCLAIMED;const p=state.player;p.x=p.trailStart.x;p.y=p.trailStart.y;p.drawing=false;p.autoRetract=false;p.trailPath=[];if(mobileUXActive())resetMobileCaptureLock('line_reset');rebuildVisualLayers()}"
rep(Path('game.js'),old,new,'line reset unlock')

rep(Path('game.js'),
"function showTitle(){\n  state.mode='title';state.paused=false;",
"function showTitle(){\n  if(mobileUXActive())resetMobileCaptureLock('title');\n  state.mode='title';state.paused=false;",
'title unlock')

rep(Path('game.js'),
"function showPause(){\n  if(tutorial.active){toast('튜토리얼에서는 저장/일시정지를 사용하지 않습니다.');return}\n  if(state.mode!=='playing')return;state.paused=true;",
"function showPause(){\n  if(tutorial.active){toast('튜토리얼에서는 저장/일시정지를 사용하지 않습니다.');return}\n  if(state.mode!=='playing')return;if(mobileUXActive())resetMobileCaptureLock('pause');state.paused=true;",
'pause unlock')

rep(Path('game.js'),
"function showGameOver(){\n  state.paused=true;",
"function showGameOver(){\n  if(mobileUXActive())resetMobileCaptureLock('game_over');\n  state.paused=true;",
'gameover unlock')

rep(Path('game.js'),
"function showClearModal(level){\n  state.paused=true;",
"function showClearModal(level){\n  if(mobileUXActive())resetMobileCaptureLock('stage_end');\n  state.paused=true;",
'clear unlock')

rep(Path('game.js'),
"async function startStage(n,fromSave=false){\n  state.stage=clamp(n,1,10);",
"async function startStage(n,fromSave=false){\n  if(mobileUXActive())resetMobileCaptureLock('stage_start');\n  state.stage=clamp(n,1,10);",
'stage start unlock')

rep(Path('game.js'),
"document.addEventListener('visibilitychange',()=>{if(!document.hidden)return;input.dirs.clear();input.capture=false;input.dash=false;beginAutoRetract();if(state.mode==='playing'&&!state.paused)showPause()});",
"document.addEventListener('visibilitychange',()=>{if(!document.hidden)return;if(mobileUXActive())resetMobileCaptureLock('visibility_hidden');input.dirs.clear();input.capture=false;input.dash=false;beginAutoRetract();if(state.mode==='playing'&&!state.paused)showPause()});",
'visibility unlock')

rep(Path('game.js'),
"else if(tutorial.step==='draw'){label='STEP 2 / 4';title='DRAW THE LINE';text=coarse?'CAPTURE를 누른 채 + MOVE':'HOLD SPACE + MOVE';hint='안전영역 밖으로 선을 2칸 이상 그리세요.'}",
"else if(tutorial.step==='draw'){label='STEP 2 / 4';title='DRAW THE LINE';text=coarse?'1. TAP CAPTURE → 2. MOVE':'HOLD SPACE + MOVE';hint=coarse?'CAPTURE는 한 번 탭하면 잠깁니다. 안전영역 밖으로 이동하세요.':'안전영역 밖으로 선을 2칸 이상 그리세요.'}",
'tutorial draw copy')

rep(Path('game.js'),
"else if(tutorial.step==='retract'){label='STEP 4 / 4';title='RELEASE TO RETREAT';text=tutorial.retractArmed?(coarse?'이제 CAPTURE에서 손을 떼세요':'NOW RELEASE SPACE'):(coarse?'CAPTURE + MOVE로 짧게 선을 그리세요':'HOLD SPACE + MOVE로 짧게 선을 그리세요');hint='버튼을 놓으면 방금 그은 선을 따라 안전지대로 후퇴합니다.'}",
"else if(tutorial.step==='retract'){label='STEP 4 / 4';title=coarse?'TAP TO RETREAT':'RELEASE TO RETREAT';text=tutorial.retractArmed?(coarse?'CAPTURE를 다시 탭하세요':'NOW RELEASE SPACE'):(coarse?'1. TAP CAPTURE → 2. MOVE':'HOLD SPACE + MOVE로 짧게 선을 그리세요');hint=coarse?'CAPTURE를 다시 탭하면 방금 그은 선을 따라 안전지대로 후퇴합니다.':'버튼을 놓으면 방금 그은 선을 따라 안전지대로 후퇴합니다.'}",
'tutorial retract copy')

css_path=root/'styles.css'
css=css_path.read_text(encoding='utf-8')
marker='/* v0.8.0 MOBILE ONLY UX v2 */'
if marker not in css:
    css += r'''

/* v0.8.0 MOBILE ONLY UX v2 — DESKTOP FREEZE */
@media (pointer:coarse){
  html,body,.app-shell,.screen{max-width:none!important}
  .app-shell,.game-screen{height:var(--mobile-vh,100dvh)!important;min-height:0!important}
  .game-screen{width:var(--mobile-vw,100vw)!important;max-width:100%!important}
  .capture-btn.capture-locked{
    border-color:rgba(255,255,255,.92)!important;
    background:linear-gradient(145deg,#ff2690,#c31cff)!important;
    box-shadow:0 0 0 4px rgba(255,255,255,.16),0 0 38px rgba(255,45,160,.78),inset 0 2px rgba(255,255,255,.25)!important;
    transform:scale(.98);letter-spacing:.035em;animation:cmhCaptureLockPulse 1.1s ease-in-out infinite alternate
  }
  @keyframes cmhCaptureLockPulse{from{filter:brightness(1)}to{filter:brightness(1.18)}}
  .move-joystick,.capture-btn,.dash-btn{-webkit-tap-highlight-color:transparent;touch-action:none}
}

@media (pointer:coarse) and (orientation:landscape){
  .game-screen{
    --ux-board-h:calc(var(--mobile-vh,100dvh) - 4px);
    --ux-board-w:min(calc(var(--ux-board-h) * 4 / 3),calc(var(--mobile-vw,100vw) - 214px),1120px);
    height:var(--mobile-vh,100dvh)!important;
    padding:0 max(2px,env(safe-area-inset-right)) 0 max(2px,env(safe-area-inset-left))!important;
    overflow:hidden!important
  }
  .game-frame{top:2px!important;width:var(--ux-board-w)!important;max-width:none!important;max-height:var(--ux-board-h)!important;margin:0!important}
  .game-topbar{
    top:max(4px,env(safe-area-inset-top))!important;
    width:min(calc(var(--ux-board-w) - 10px),1096px)!important;
    height:32px!important;gap:2px!important;padding:1px 3px!important;border-radius:10px!important
  }
  .game-topbar .stat{padding:1px 4px!important;border-radius:7px!important}
  .game-topbar .stat small{font-size:.34rem!important}
  .game-topbar .stat strong{font-size:.66rem!important}
  .game-topbar .icon-btn{width:28px!important;height:28px!important;flex:0 0 28px!important}
  .game-bottombar{
    bottom:4px!important;width:min(calc(var(--ux-board-w) - 10px),1096px)!important;
    height:21px!important;padding:1px 6px!important;border-radius:8px!important;gap:6px!important
  }
  .progress-shell{height:8px!important}
  .stamina-box{min-width:92px!important;gap:4px!important;font-size:.48rem!important}
  .stamina-track{width:58px!important;height:6px!important}
  .mobile-controls{
    inset:0!important;pointer-events:none!important;
    display:grid!important;
    grid-template-columns:minmax(0,1fr) var(--ux-board-w) minmax(0,1fr)!important;
    align-items:center!important
  }
  .move-joystick,.mobile-actions{pointer-events:auto!important}
  .move-joystick{
    position:relative!important;left:auto!important;top:auto!important;transform:none!important;
    grid-column:1!important;justify-self:end!important;align-self:center!important;
    margin-right:10px!important;
    width:104px!important;height:104px!important;flex-basis:104px!important
  }
  .joystick-knob{width:48px!important;height:48px!important}
  .mobile-actions{
    position:relative!important;right:auto!important;top:auto!important;transform:none!important;
    grid-column:3!important;justify-self:start!important;align-self:center!important;
    margin-left:10px!important;gap:11px!important
  }
  .capture-btn{width:96px!important;height:96px!important;flex-basis:96px!important;font-size:.74rem!important;border-radius:50%!important}
  .dash-btn{width:78px!important;height:62px!important;flex-basis:62px!important;font-size:.68rem!important;border-radius:22px!important;box-shadow:0 0 24px rgba(81,103,255,.38)!important}
  .mini-map{width:min(15%,96px)!important;min-width:62px!important;bottom:27px!important;right:5px!important}
  .mini-map.avoid-left{left:5px!important;right:auto!important}
}

@media (pointer:coarse) and (orientation:portrait){
  .game-screen{
    height:var(--mobile-vh,100dvh)!important;width:var(--mobile-vw,100vw)!important;
    padding:max(2px,env(safe-area-inset-top)) 4px max(4px,env(safe-area-inset-bottom))!important;
    gap:2px!important;justify-content:flex-start!important;overflow:hidden!important
  }
  .game-topbar{
    order:1;flex:0 0 44px!important;width:calc(100% - 8px)!important;height:44px!important;
    gap:2px!important;padding:2px!important
  }
  .game-topbar .stat{padding:2px 3px!important}
  .game-topbar .stat small{font-size:.38rem!important}
  .game-topbar .stat strong{font-size:.68rem!important}
  .game-topbar .icon-btn{width:32px!important;height:32px!important;flex:0 0 32px!important}
  .game-frame{
    order:2;position:relative!important;top:auto!important;left:auto!important;transform:none!important;
    width:min(calc(100vw - 8px),calc((var(--mobile-vh,100dvh) - 222px)*4/3),760px)!important;
    max-height:none!important;margin:0 auto!important
  }
  .game-bottombar{
    order:3;position:relative!important;left:auto!important;bottom:auto!important;transform:none!important;
    width:min(calc(100vw - 12px),760px)!important;height:24px!important;padding:1px 5px!important;margin:0 auto!important
  }
  .mobile-controls{
    order:4;position:relative!important;inset:auto!important;width:min(calc(100vw - 12px),760px)!important;
    min-height:112px!important;height:112px!important;margin:0 auto!important;
    padding:3px max(8px,env(safe-area-inset-right)) max(3px,env(safe-area-inset-bottom)) max(8px,env(safe-area-inset-left))!important;
    display:flex!important;align-items:center!important;justify-content:space-between!important;pointer-events:auto!important
  }
  .move-joystick{position:relative!important;left:auto!important;top:auto!important;transform:none!important;width:100px!important;height:100px!important;flex-basis:100px!important}
  .joystick-knob{width:46px!important;height:46px!important}
  .mobile-actions{position:relative!important;right:auto!important;top:auto!important;transform:none!important;flex-direction:column!important;gap:7px!important}
  .capture-btn{width:84px!important;height:84px!important;flex-basis:84px!important;font-size:.68rem!important}
  .dash-btn{width:72px!important;height:48px!important;flex-basis:48px!important;font-size:.62rem!important}
  .mini-map{width:min(18%,86px)!important;min-width:60px!important;bottom:28px!important}
}

@media (pointer:coarse) and (orientation:portrait){
  .modal-card.clear-review-card{
    width:calc(var(--mobile-vw,100vw) - 12px)!important;max-width:none!important;
    max-height:calc(var(--mobile-vh,100dvh) - 12px)!important;padding:8px!important;overflow:auto!important
  }
  .clear-review{display:flex!important;flex-direction:column!important;gap:8px!important}
  .clear-photo-wrap{display:flex!important;flex-direction:column!important;overflow:visible!important;background:transparent!important;border:0!important;box-shadow:none!important;gap:7px!important}
  .clear-photo-badge{
    position:relative!important;left:auto!important;top:auto!important;order:1!important;width:100%!important;text-align:center!important;
    padding:7px 10px!important;font-size:clamp(.72rem,3.3vw,.95rem)!important;white-space:normal!important;border-radius:12px!important
  }
  .bonus-media-actions{
    position:relative!important;right:auto!important;top:auto!important;order:2!important;
    display:grid!important;grid-template-columns:1fr 1fr!important;width:100%!important;gap:6px!important
  }
  .bonus-media-btn{width:100%!important;min-height:34px!important;font-size:.65rem!important;padding:6px 8px!important}
  .clear-photo{
    order:3!important;width:100%!important;height:auto!important;
    max-height:min(52vh,calc(var(--mobile-vh,100dvh) * .52))!important;
    aspect-ratio:4/3!important;object-fit:contain!important;object-position:center!important;border-radius:14px!important;background:#050208!important
  }
  .bonus-scene-unlocked{left:50%!important;bottom:9px!important;font-size:.54rem!important;padding:5px 8px!important}
  .clear-review-bottom{display:flex!important;flex-direction:column!important;gap:8px!important}
  .clear-score{width:100%!important;min-width:0!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:5px!important;margin:0!important}
  .clear-score>div{padding:8px 4px!important}
  .clear-score small{font-size:.62rem!important}
  .clear-score strong{font-size:1rem!important}
  .clear-actions{width:100%!important;display:grid!important;grid-template-columns:1fr!important;gap:6px!important}
  .clear-actions .btn{width:100%!important;min-width:0!important;min-height:42px!important;padding:8px 10px!important;font-size:.8rem!important;white-space:normal!important}
}
'''
css_path.write_text(css,encoding='utf-8')

print('v0.8.0 mobile-only UX v2 applied')
