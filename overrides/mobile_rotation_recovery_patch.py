from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path, old, new, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'mobile rotation recovery patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

old = r'''function updateMobileViewportVars(){
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
new = r'''let mobileViewportSettleTimer=0;
function updateMobileViewportVars(reason='resize'){
  if(!mobileUXActive())return;
  const vv=window.visualViewport;
  const fallbackW=window.innerWidth||document.documentElement.clientWidth||1;
  const fallbackH=window.innerHeight||document.documentElement.clientHeight||1;
  const w=Math.max(1,Math.round(vv?.width||fallbackW));
  const h=Math.max(1,Math.round(vv?.height||fallbackH));
  const root=document.documentElement;
  root.style.setProperty('--mobile-vw',w+'px');
  root.style.setProperty('--mobile-vh',h+'px');
  root.dataset.cmhOrientation=w>=h?'landscape':'portrait';
}
function mobileRotationRecover(reason='orientation'){
  if(!mobileUXActive())return;
  updateMobileViewportVars(reason);
  input.touchDir=null;input.dash=false;
  const knob=$('#joystickKnob');if(knob)knob.style.transform='translate(-50%,-50%)';
  if(state.mode==='playing'){
    state.lastTs=performance.now();
    render();updateHUD();
    cancelAnimationFrame(state.frameId);
    state.frameId=requestAnimationFrame(loop);
  }
}
function mobileViewportSettle(reason='resize'){
  if(!mobileUXActive())return;
  updateMobileViewportVars(reason);
  clearTimeout(mobileViewportSettleTimer);
  mobileViewportSettleTimer=setTimeout(()=>mobileRotationRecover(reason),180);
}
function mobileOrientationSettle(reason='orientation'){
  if(!mobileUXActive())return;
  [0,80,220,480,850].forEach((delay,index)=>setTimeout(()=>{
    updateMobileViewportVars(reason);
    if(index===4)mobileRotationRecover(reason);
  },delay));
}
if(mobileUXActive()){
  updateMobileViewportVars('boot');
  window.addEventListener('resize',()=>mobileViewportSettle('resize'),{passive:true});
  window.addEventListener('orientationchange',()=>mobileOrientationSettle('orientationchange'),{passive:true});
  screen.orientation?.addEventListener('change',()=>mobileOrientationSettle('screen-orientation'),{passive:true});
  window.visualViewport?.addEventListener('resize',()=>mobileViewportSettle('visual-resize'),{passive:true});
  window.visualViewport?.addEventListener('scroll',()=>mobileViewportSettle('visual-scroll'),{passive:true});
}
'''
rep(Path('game.js'), old, new, 'mobile viewport recovery block')

css=root/'styles.css'
s=css.read_text(encoding='utf-8')
marker='/* v0.13.3 mobile rotation recovery */'
if marker not in s:
    s += r'''

/* v0.13.3 mobile rotation recovery — MOBILE ONLY */
@media (pointer:coarse){
  html,body,.app-shell,.screen{
    width:var(--mobile-vw,100vw)!important;
    height:var(--mobile-vh,100dvh)!important;
    min-height:0!important;
  }
  .title-screen{
    width:var(--mobile-vw,100vw)!important;
    height:var(--mobile-vh,100dvh)!important;
  }
  .title-stage{
    width:min(var(--mobile-vw,100vw),calc(var(--mobile-vh,100dvh) * 1.776833))!important;
    max-width:var(--mobile-vw,100vw)!important;
    max-height:var(--mobile-vh,100dvh)!important;
  }
}
@media (pointer:coarse) and (orientation:landscape){
  .game-screen{
    width:var(--mobile-vw,100vw)!important;
    height:var(--mobile-vh,100dvh)!important;
  }
}
'''
    css.write_text(s,encoding='utf-8')

rep(Path('index.html'),
    '<div class="version">v0.13.2 collection 3d access</div>',
    '<div class="version">v0.13.3 mobile rotation recovery</div>',
    'version label')
rep(Path('config.js'),"VERSION: '0.13.2'","VERSION: '0.13.3'",'config version')
rep(Path('sw.js'),"cmh-core-v0.13.2","cmh-core-v0.13.3",'service worker cache version')

print('v0.13.3 mobile rotation recovery applied')
