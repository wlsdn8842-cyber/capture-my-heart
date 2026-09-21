from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path, old, new, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'mobile controls patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

# Replace four tiny direction buttons with one thumb-friendly analog-style joystick.
rep(Path('index.html'), '''        <div class="dpad">
          <button class="dkey up" data-dir="up">▲</button>
          <button class="dkey left" data-dir="left">◀</button>
          <button class="dkey right" data-dir="right">▶</button>
          <button class="dkey down" data-dir="down">▼</button>
        </div>''', '''        <div id="moveJoystick" class="move-joystick" role="group" aria-label="이동 조이스틱">
          <div class="joystick-guide" aria-hidden="true"><span class="joy-up">▲</span><span class="joy-left">◀</span><span class="joy-right">▶</span><span class="joy-down">▼</span></div>
          <div id="joystickKnob" class="joystick-knob" aria-hidden="true"></div>
        </div>''', 'joystick markup')

rep(Path('index.html'), '모바일은 아래 방향키 + <b>CAPTURE / DASH</b> 버튼을 사용합니다.', '모바일은 왼쪽 <b>조이스틱</b> + 오른쪽 <b>CAPTURE / DASH</b> 버튼을 사용합니다.', 'tutorial mobile copy')

rep(Path('game.js'), '<p>모바일은 화면 아래 방향키 + CAPTURE + DASH 버튼을 사용합니다.</p>', '<p>모바일은 화면 아래 <b>조이스틱 + CAPTURE + DASH</b> 버튼을 사용합니다.</p>', 'howto mobile copy')

old_touch = r'''document.querySelectorAll('.dkey').forEach(b=>{const dir=b.dataset.dir;const down=e=>{e.preventDefault();input.touchDir=dir;b.classList.add('active')};const up=e=>{e.preventDefault();if(input.touchDir===dir)input.touchDir=null;b.classList.remove('active')};b.addEventListener('pointerdown',down);b.addEventListener('pointerup',up);b.addEventListener('pointercancel',up);b.addEventListener('pointerleave',up)});
const cap=$('#captureTouchBtn');cap.addEventListener('pointerdown',e=>{e.preventDefault();input.capture=true;stopAutoRetract();cap.classList.add('active')});['pointerup','pointercancel','pointerleave'].forEach(ev=>cap.addEventListener(ev,e=>{e.preventDefault();input.capture=false;beginAutoRetract();cap.classList.remove('active')}));
const dashBtn=$('#dashTouchBtn');if(dashBtn){const dashDown=e=>{e.preventDefault();input.dash=true;dashBtn.classList.add('active')},dashUp=e=>{e.preventDefault();input.dash=false;dashBtn.classList.remove('active')};dashBtn.addEventListener('pointerdown',dashDown);['pointerup','pointercancel','pointerleave'].forEach(ev=>dashBtn.addEventListener(ev,dashUp))}
'''

new_touch = r'''const joy=$('#moveJoystick'),joyKnob=$('#joystickKnob');
if(joy&&joyKnob){
  let joyPointer=null;
  const resetJoy=()=>{input.touchDir=null;joyKnob.style.transform='translate(-50%,-50%)';joy.classList.remove('active')};
  const updateJoy=e=>{
    const r=joy.getBoundingClientRect(),cx=r.left+r.width/2,cy=r.top+r.height/2,dx=e.clientX-cx,dy=e.clientY-cy;
    const dist=Math.hypot(dx,dy),max=Math.min(r.width,r.height)*.29,dead=Math.min(r.width,r.height)*.11,scale=dist>max?max/(dist||1):1;
    joyKnob.style.transform=`translate(-50%,-50%) translate(${dx*scale}px,${dy*scale}px)`;
    if(dist<dead){input.touchDir=null;return}
    input.touchDir=Math.abs(dx)>Math.abs(dy)?(dx<0?'left':'right'):(dy<0?'up':'down');
  };
  joy.addEventListener('pointerdown',e=>{e.preventDefault();if(joyPointer!==null)return;joyPointer=e.pointerId;joy.setPointerCapture?.(e.pointerId);joy.classList.add('active');updateJoy(e);navigator.vibrate?.(8)});
  joy.addEventListener('pointermove',e=>{if(e.pointerId!==joyPointer)return;e.preventDefault();updateJoy(e)});
  const joyUp=e=>{if(e.pointerId!==joyPointer)return;e.preventDefault();try{joy.releasePointerCapture?.(e.pointerId)}catch(_){}joyPointer=null;resetJoy()};
  joy.addEventListener('pointerup',joyUp);joy.addEventListener('pointercancel',joyUp);joy.addEventListener('lostpointercapture',e=>{if(e.pointerId===joyPointer){joyPointer=null;resetJoy()}});
  joy.addEventListener('contextmenu',e=>e.preventDefault());
}

function bindHoldButton(el,onDown,onUp){
  if(!el)return;let pointer=null;
  const down=e=>{e.preventDefault();if(pointer!==null)return;pointer=e.pointerId;el.setPointerCapture?.(e.pointerId);el.classList.add('active');onDown();navigator.vibrate?.(10)};
  const up=e=>{if(pointer===null||e.pointerId!==pointer)return;e.preventDefault();const id=pointer;pointer=null;el.classList.remove('active');onUp();try{el.releasePointerCapture?.(id)}catch(_){}};
  el.addEventListener('pointerdown',down);el.addEventListener('pointerup',up);el.addEventListener('pointercancel',up);el.addEventListener('lostpointercapture',e=>{if(pointer!==null&&e.pointerId===pointer){pointer=null;el.classList.remove('active');onUp()}});el.addEventListener('contextmenu',e=>e.preventDefault());
}
const cap=$('#captureTouchBtn');bindHoldButton(cap,()=>{input.capture=true;stopAutoRetract()},()=>{input.capture=false;beginAutoRetract()});
const dashBtn=$('#dashTouchBtn');bindHoldButton(dashBtn,()=>{input.dash=true},()=>{input.dash=false});
'''
rep(Path('game.js'), old_touch, new_touch, 'joystick and robust action buttons')

# Mobile controls: larger thumb targets, no browser gestures, and stable multi-touch.
css=root/'styles.css'
with css.open('a',encoding='utf-8') as f:
    f.write(r'''

/* v0.5.8 mobile-control hotfix: joystick + reliable CAPTURE/DASH */
.mobile-controls{touch-action:none;-webkit-user-select:none;user-select:none;-webkit-tap-highlight-color:transparent;overscroll-behavior:contain}
.move-joystick{position:relative;width:118px;height:118px;flex:0 0 118px;border-radius:50%;touch-action:none;background:radial-gradient(circle at 38% 34%,rgba(91,216,255,.2),rgba(73,44,103,.24) 52%,rgba(8,5,15,.72));border:2px solid rgba(255,255,255,.22);box-shadow:inset 0 0 24px rgba(73,211,255,.12),0 8px 24px rgba(0,0,0,.34)}
.move-joystick.active{border-color:rgba(92,225,255,.68);box-shadow:inset 0 0 28px rgba(73,211,255,.22),0 0 20px rgba(73,211,255,.18)}
.joystick-guide{position:absolute;inset:0;pointer-events:none;color:rgba(255,255,255,.36);font-size:.66rem;font-weight:900}.joystick-guide span{position:absolute}.joy-up{left:50%;top:8px;transform:translateX(-50%)}.joy-down{left:50%;bottom:8px;transform:translateX(-50%)}.joy-left{left:9px;top:50%;transform:translateY(-50%)}.joy-right{right:9px;top:50%;transform:translateY(-50%)}
.joystick-knob{position:absolute;left:50%;top:50%;width:54px;height:54px;border-radius:50%;transform:translate(-50%,-50%);pointer-events:none;background:radial-gradient(circle at 35% 30%,#c7f8ff,#56cce9 44%,#286da1 100%);border:2px solid rgba(255,255,255,.72);box-shadow:0 5px 16px rgba(0,0,0,.42),0 0 18px rgba(82,218,255,.24);will-change:transform;transition:box-shadow .08s ease}
.move-joystick.active .joystick-knob{box-shadow:0 5px 16px rgba(0,0,0,.42),0 0 24px rgba(82,218,255,.5)}
.capture-btn,.dash-btn{touch-action:none;-webkit-user-select:none;user-select:none;-webkit-tap-highlight-color:transparent;outline:none}
.mobile-actions{min-width:184px;justify-content:flex-end;align-items:flex-end;gap:10px}
.capture-btn{width:98px!important;height:98px!important;flex:0 0 98px;box-shadow:0 0 30px rgba(255,65,153,.48),inset 0 2px rgba(255,255,255,.18);font-size:.82rem}
.dash-btn{width:76px!important;height:62px!important;flex:0 0 76px;border-radius:22px!important;font-size:.74rem!important}
.capture-btn.active,.dash-btn.active{transform:scale(.94)!important;filter:brightness(1.28)!important}
@media (max-width:800px),(pointer:coarse){.mobile-controls{padding:5px 10px max(4px,env(safe-area-inset-bottom));min-height:126px}.move-joystick{width:114px;height:114px;flex-basis:114px}.joystick-knob{width:52px;height:52px}.mobile-actions{min-width:174px;gap:8px}.capture-btn{width:94px!important;height:94px!important;flex-basis:94px}.dash-btn{width:72px!important;height:60px!important;flex-basis:72px}}
@media (max-width:380px){.mobile-controls{padding-left:5px;padding-right:5px}.move-joystick{width:106px;height:106px;flex-basis:106px}.joystick-knob{width:48px;height:48px}.mobile-actions{min-width:164px;gap:6px}.capture-btn{width:90px!important;height:90px!important;flex-basis:90px}.dash-btn{width:68px!important;height:56px!important;flex-basis:68px}}
''')

print('v0.5.8 mobile controls patch applied')
