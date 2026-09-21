from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def replace(path, old, new, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'patch failed: {label}')
    p.write_text(s.replace(old,new),encoding='utf-8')

def insert_before(path, marker, block, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if marker not in s:
        raise SystemExit(f'patch failed: {label}')
    p.write_text(s.replace(marker,block+marker,1),encoding='utf-8')

# GAME.JS
replace(Path('game.js'),
"{name:'Maid Cafe',     music:'assets/audio/stages_1_4.mp3', speed:84,  shots:0,    minions:0, chase:0.00, timer:180, hue:'#ff6aaa'},",
"{name:'Maid Cafe',     music:'assets/audio/stages_1_4.mp3', speed:84,  shots:0,    minions:0, chase:0.018,timer:180, hue:'#ff6aaa'},",'stage1 anti-inert')
replace(Path('game.js'),
"player:{x:Math.floor(GW/2), y:1, drawing:false, trailStart:{x:Math.floor(GW/2),y:1}, trailPath:[]},",
"player:{x:Math.floor(GW/2), y:1, drawing:false, autoRetract:false, trailStart:{x:Math.floor(GW/2),y:1}, trailPath:[]},",'state auto retract')
replace(Path('game.js'),
"speedBoostUntil:0, freezeUntil:0, slowUntil:0, shield:0,",
"speedBoostUntil:0, freezeUntil:0, slowUntil:0, shield:0, dashStamina:100, dashExhausted:false,",'dash state')
replace(Path('game.js'),
'''    <p><span class="kbd">SPACE</span> 안전영역에서 바깥으로 선 긋기 시작. 시작 후에는 SPACE를 떼어도 선이 유지됩니다.</p>
    <p>선을 다시 안전영역에 연결하면 <b>보스가 없는 쪽</b>을 점령하고 이미지가 공개됩니다.</p>
    <p>선을 잘못 그었을 때는 <b>방금 지나온 경로를 그대로 되짚어</b> 돌아가면 라인을 되감을 수 있습니다. 단, 이전 라인을 옆에서 가로질러 교차하면 MISS입니다.</p>''',
'''    <p><span class="kbd">SPACE</span>를 누른 채 안전영역 밖으로 나가 선을 긋습니다. <b>SPACE를 놓으면 방금 그은 선을 따라 자동으로 안전지대까지 후퇴</b>합니다.</p>
    <p><span class="kbd">SHIFT</span>를 누르면 스태미나를 사용해 짧게 DASH합니다.</p>
    <p>선을 다시 안전영역에 연결하면 <b>보스가 없는 쪽</b>을 점령하고 이미지가 공개됩니다.</p>
    <p>직접 방향키로 방금 지나온 경로를 되짚어도 라인을 되감을 수 있습니다. 단, 이전 라인을 옆에서 가로질러 교차하면 MISS입니다.</p>''','howto')
replace(Path('game.js'),
'<p>모바일은 화면 아래 방향키와 CAPTURE 버튼을 사용합니다.</p>',
'<p>모바일은 화면 아래 방향키 + CAPTURE + DASH 버튼을 사용합니다.</p><p class="muted">Stage 1은 튜토리얼이라 보스가 탄을 쏘지 않습니다. Stage 2부터 적탄이 등장합니다.</p>','mobile howto')
replace(Path('game.js'),
"state.player={x:Math.floor(GW/2),y:1,drawing:false,trailStart:{x:Math.floor(GW/2),y:1},trailPath:[]};",
"state.player={x:Math.floor(GW/2),y:1,drawing:false,autoRetract:false,trailStart:{x:Math.floor(GW/2),y:1},trailPath:[]};",'init player')
replace(Path('game.js'),
"state.enemies.push({x:(c.x+.5)*CELL,y:(c.y+.5)*CELL,vx:Math.cos(ang)*speed,vy:Math.sin(ang)*speed,speed,r:i?7:11,isBoss:i===0,chase:cfg.chase*(i?1.25:1),shotTimer:cfg.shots?Math.random()*cfg.shots:Infinity})",
"state.enemies.push({x:(c.x+.5)*CELL,y:(c.y+.5)*CELL,vx:Math.cos(ang)*speed,vy:Math.sin(ang)*speed,speed,r:i?7:11,isBoss:i===0,chase:cfg.chase*(i?1.25:1),shotTimer:cfg.shots?Math.random()*cfg.shots:Infinity,lastX:(c.x+.5)*CELL,lastY:(c.y+.5)*CELL,stuckFor:0})",'enemy state')
replace(Path('game.js'),
"state.shotAcc=0;state.speedBoostUntil=0;state.freezeUntil=0;state.slowUntil=0;state.shield=0;state.stageStartedAt=Date.now();",
"state.shotAcc=0;state.speedBoostUntil=0;state.freezeUntil=0;state.slowUntil=0;state.shield=0;state.dashStamina=100;state.dashExhausted=false;state.stageStartedAt=Date.now();",'reset dash')
replace(Path('game.js'),
"state.player.drawing=false;state.player.trailPath=[];rebuildVisualLayers();state.lastArea=before;state.area=calcArea();",
"state.player.drawing=false;state.player.autoRetract=false;state.player.trailPath=[];rebuildVisualLayers();state.lastArea=before;state.area=calcArea();",'capture retract reset')
replace(Path('game.js'),
"const input={dirs:new Set(),lastDir:null,capture:false,touchDir:null};",
"const input={dirs:new Set(),lastDir:null,capture:false,dash:false,touchDir:null};",'dash input')
insert_before(Path('game.js'),'function movePlayer(){\n',r'''function beginAutoRetract(){
  const p=state.player;
  if(state.mode!=='playing'||state.paused||!p.drawing||(p.trailPath?.length||0)===0)return;
  p.autoRetract=true;state.moveAcc=0;audio.beep(360,.045,'triangle',.016);
}
function retractTrailStep(){
  const p=state.player,path=p.trailPath||[];
  if(!p.drawing||!p.autoRetract){p.autoRetract=false;return}
  if(path.length){const cur=path[path.length-1];if(cur&&getCell(cur.x,cur.y)===TRAIL)setCell(cur.x,cur.y,UNCLAIMED);path.pop()}
  if(path.length){const prev=path[path.length-1];p.x=prev.x;p.y=prev.y}
  else{p.x=p.trailStart.x;p.y=p.trailStart.y;p.drawing=false;p.autoRetract=false;p.trailPath=[];audio.beep(310,.055,'triangle',.016);toast('라인 회수')}
}
function stopAutoRetract(){if(state.player?.autoRetract)state.player.autoRetract=false}

''','retract functions')
replace(Path('game.js'),'function movePlayer(){\n  const d=direction();if(!d)return;','function movePlayer(){\n  const p=state.player;if(p.autoRetract)return;\n  const d=direction();if(!d)return;','move auto guard')
replace(Path('game.js'),'const [dx,dy]=dirVec(d),p=state.player,nx=p.x+dx,ny=p.y+dy;','const [dx,dy]=dirVec(d),nx=p.x+dx,ny=p.y+dy;','move p decl')
replace(Path('game.js'),'p.drawing=true;p.trailStart={x:p.x,y:p.y};p.x=nx;p.y=ny;','p.drawing=true;p.autoRetract=false;p.trailStart={x:p.x,y:p.y};p.x=nx;p.y=ny;','start trail')
replace(Path('game.js'),'setCell(p.x,p.y,UNCLAIMED);\n      path.pop();p.x=nx;p.y=ny;','setCell(p.x,p.y,UNCLAIMED);\n      path.pop();p.x=nx;p.y=ny;p.autoRetract=false;','manual retract')
replace(Path('game.js'),'p.x=nx;p.y=ny;p.drawing=false;p.trailPath=[];','p.x=nx;p.y=ny;p.drawing=false;p.autoRetract=false;p.trailPath=[];','line cancel')
replace(Path('game.js'),
"function clearTrail(){for(let i=0;i<grid.length;i++)if(grid[i]===TRAIL)grid[i]=UNCLAIMED;const p=state.player;p.x=p.trailStart.x;p.y=p.trailStart.y;p.drawing=false;p.trailPath=[];rebuildVisualLayers()}",
"function clearTrail(){for(let i=0;i<grid.length;i++)if(grid[i]===TRAIL)grid[i]=UNCLAIMED;const p=state.player;p.x=p.trailStart.x;p.y=p.trailStart.y;p.drawing=false;p.autoRetract=false;p.trailPath=[];rebuildVisualLayers()}",'clear trail')
replace(Path('game.js'),r'''function updateEnemies(dt){
  const cfg=STAGES[state.stage], frozen=now()<state.freezeUntil, slow=now()<state.slowUntil;
  if(frozen)return;
  for(const e of state.enemies){
    const speed=e.speed*(slow ? 0.55 : 1);
    if(state.player.drawing&&e.chase>0){const tx=(state.player.x+.5)*CELL,ty=(state.player.y+.5)*CELL,dx=tx-e.x,dy=ty-e.y,len=Math.hypot(dx,dy)||1;const tvx=dx/len*speed,tvy=dy/len*speed;e.vx=e.vx*(1-e.chase)+tvx*e.chase;e.vy=e.vy*(1-e.chase)+tvy*e.chase;const vl=Math.hypot(e.vx,e.vy)||1;e.vx=e.vx/vl*speed;e.vy=e.vy/vl*speed}
    let nx=e.x+e.vx*dt,ny=e.y+e.vy*dt;let c=cellAtPixel(nx,e.y),cell=getCell(c.x,c.y);if(cell===TRAIL){failLife('보스가 라인을 끊었습니다');return}if(cell===CLAIMED){e.vx*=-1;nx=e.x+e.vx*dt}
    c=cellAtPixel(e.x,ny);cell=getCell(c.x,c.y);if(cell===TRAIL){failLife('보스가 라인을 끊었습니다');return}if(cell===CLAIMED){e.vy*=-1;ny=e.y+e.vy*dt}
    e.x=clamp(nx,CELL*2.5,W-CELL*2.5);e.y=clamp(ny,CELL*2.5,H-CELL*2.5);
    if(state.player.drawing&&dist(e.x,e.y,(state.player.x+.5)*CELL,(state.player.y+.5)*CELL)<e.r+8){failLife('보스 충돌');return}
    if(e.isBoss&&cfg.shots){e.shotTimer-=dt*1000;if(e.shotTimer<=0){e.shotTimer=cfg.shots*(.8+Math.random()*.45);shoot(e)}}
  }
}
''',r'''function updateEnemies(dt){
  const cfg=STAGES[state.stage], frozen=now()<state.freezeUntil, slow=now()<state.slowUntil;
  if(frozen)return;
  for(const e of state.enemies){
    const speed=e.speed*(slow ? 0.55 : 1);
    if(state.player.drawing&&e.chase>0){const tx=(state.player.x+.5)*CELL,ty=(state.player.y+.5)*CELL,dx=tx-e.x,dy=ty-e.y,len=Math.hypot(dx,dy)||1;const tvx=dx/len*speed,tvy=dy/len*speed;e.vx=e.vx*(1-e.chase)+tvx*e.chase;e.vy=e.vy*(1-e.chase)+tvy*e.chase;const vl=Math.hypot(e.vx,e.vy)||1;e.vx=e.vx/vl*speed;e.vy=e.vy/vl*speed}
    let nx=e.x+e.vx*dt,ny=e.y+e.vy*dt,bounced=false;
    let c=cellAtPixel(nx,e.y),cell=getCell(c.x,c.y);if(cell===TRAIL){failLife('보스가 라인을 끊었습니다');return}if(cell===CLAIMED){e.vx*=-1;e.vy+=(Math.random()-.5)*speed*.28;bounced=true;nx=e.x+e.vx*dt}
    c=cellAtPixel(e.x,ny);cell=getCell(c.x,c.y);if(cell===TRAIL){failLife('보스가 라인을 끊었습니다');return}if(cell===CLAIMED){e.vy*=-1;e.vx+=(Math.random()-.5)*speed*.28;bounced=true;ny=e.y+e.vy*dt}
    if(bounced){const vl=Math.hypot(e.vx,e.vy)||1;e.vx=e.vx/vl*speed;e.vy=e.vy/vl*speed}
    e.x=clamp(nx,CELL*2.5,W-CELL*2.5);e.y=clamp(ny,CELL*2.5,H-CELL*2.5);
    const moved=dist(e.x,e.y,e.lastX??e.x,e.lastY??e.y);e.stuckFor=moved<.35?(e.stuckFor||0)+dt:0;e.lastX=e.x;e.lastY=e.y;
    if(e.stuckFor>1.15){const cx=W/2-e.x,cy=H/2-e.y,base=Math.atan2(cy,cx)+(Math.random()-.5)*.8;e.vx=Math.cos(base)*speed;e.vy=Math.sin(base)*speed;e.stuckFor=0}
    if(state.player.drawing&&dist(e.x,e.y,(state.player.x+.5)*CELL,(state.player.y+.5)*CELL)<e.r+8){failLife('보스 충돌');return}
    if(e.isBoss&&cfg.shots){e.shotTimer-=dt*1000;if(e.shotTimer<=0){e.shotTimer=cfg.shots*(.8+Math.random()*.45);shoot(e)}}
  }
}
''','enemy anti stuck')
replace(Path('game.js'),'const mw=miniMap.width,mh=miniMap.height;\n  miniCtx.fillStyle',r'''const mw=miniMap.width,mh=miniMap.height;
  const boss=state.enemies.find(e=>e.isBoss);
  if(boss){const bx=(boss.x-cam.sx)/cam.sw*W,by=(boss.y-cam.sy)/cam.sh*H,px=((state.player.x+.5)*CELL-cam.sx)/cam.sw*W,py=((state.player.y+.5)*CELL-cam.sy)/cam.sh*H;miniMap.classList.toggle('avoid-left',(bx>W*.76&&by>H*.68)||(px>W*.79&&py>H*.72))}else miniMap.classList.remove('avoid-left');
  miniCtx.fillStyle''','adaptive minimap')
replace(Path('game.js'),"$('#progressBar').style.width=`${Math.min(100,state.area)}%`;updateMusicLabel();","$('#progressBar').style.width=`${Math.min(100,state.area)}%`;const sb=$('#staminaBar');if(sb)sb.style.width=`${clamp(state.dashStamina,0,100)}%`;const sl=$('#staminaLabel');if(sl)sl.textContent=state.dashExhausted?'RECOVER':'DASH';updateMusicLabel();",'stamina hud')
replace(Path('game.js'),r'''    const moveInterval=(now()<state.speedBoostUntil?0.038:0.058);state.moveAcc+=dt;while(state.moveAcc>=moveInterval){movePlayer();state.moveAcc-=moveInterval;if(state.paused)break}
    if(!state.paused){updateEnemies(dt);updateProjectiles(dt);state.timerAcc+=dt;if(state.timerAcc>=.1){state.timeLeft-=state.timerAcc;state.timerAcc=0;if(state.timeLeft<=0){state.timeLeft=STAGES[state.stage].timer;failLife('TIME UP')}}const danger=dangerCheck();if(window.CMH_CONFIG?.GAMEPLAY?.DANGER_BGM_ENABLED!==false)audio.setDanger(danger)}
''',r'''    const moving=!!direction(),p=state.player;let dashActive=input.dash&&moving&&!p.autoRetract&&!state.dashExhausted&&state.dashStamina>0;
    if(dashActive){state.dashStamina=Math.max(0,state.dashStamina-dt*38);if(state.dashStamina<=0){state.dashExhausted=true;dashActive=false;toast('DASH 회복 중…')}}else{state.dashStamina=Math.min(100,state.dashStamina+dt*22);if(state.dashExhausted&&state.dashStamina>=32)state.dashExhausted=false}
    state.moveAcc+=dt;
    if(p.autoRetract){const retractInterval=.032;while(state.moveAcc>=retractInterval&&p.autoRetract){retractTrailStep();state.moveAcc-=retractInterval;if(state.paused)break}}
    else{let moveInterval=(now()<state.speedBoostUntil?0.038:0.058);if(dashActive)moveInterval*=.62;while(state.moveAcc>=moveInterval){movePlayer();state.moveAcc-=moveInterval;if(state.paused)break}}
    if(!state.paused){updateEnemies(dt);updateProjectiles(dt);state.timerAcc+=dt;if(state.timerAcc>=.1){state.timeLeft-=state.timerAcc;state.timerAcc=0;if(state.timeLeft<=0){state.timeLeft=STAGES[state.stage].timer;failLife('TIME UP')}}const danger=dangerCheck();if(window.CMH_CONFIG?.GAMEPLAY?.DANGER_BGM_ENABLED!==false)audio.setDanger(danger)}
''','dash loop')
replace(Path('game.js'),r'''window.addEventListener('keydown',e=>{if(keyMap[e.code]){input.dirs.add(keyMap[e.code]);input.lastDir=keyMap[e.code];if(state.mode==='playing')e.preventDefault()}if(e.code==='Space'){input.capture=true;if(state.mode==='playing')e.preventDefault()}if(e.code==='Escape'&&state.mode==='playing'&&!state.paused)showPause()});
window.addEventListener('keyup',e=>{if(keyMap[e.code])input.dirs.delete(keyMap[e.code]);if(e.code==='Space')input.capture=false});
window.addEventListener('blur',()=>{input.dirs.clear();input.capture=false;if(state.mode==='playing'&&!state.paused)showPause()});
''',r'''window.addEventListener('keydown',e=>{if(keyMap[e.code]){input.dirs.add(keyMap[e.code]);input.lastDir=keyMap[e.code];if(state.mode==='playing')e.preventDefault()}if(e.code==='Space'){input.capture=true;stopAutoRetract();if(state.mode==='playing')e.preventDefault()}if(e.code==='ShiftLeft'||e.code==='ShiftRight'){input.dash=true;if(state.mode==='playing')e.preventDefault()}if(e.code==='Escape'&&state.mode==='playing'&&!state.paused)showPause()});
window.addEventListener('keyup',e=>{if(keyMap[e.code])input.dirs.delete(keyMap[e.code]);if(e.code==='Space'){input.capture=false;beginAutoRetract()}if(e.code==='ShiftLeft'||e.code==='ShiftRight')input.dash=false});
window.addEventListener('blur',()=>{input.dirs.clear();input.capture=false;input.dash=false;beginAutoRetract()});\n// v0.6.5 focus pause hotfix: losing iframe/window focus does not pause; hiding the tab does.\ndocument.addEventListener('visibilitychange',()=>{if(!document.hidden)return;input.dirs.clear();input.capture=false;input.dash=false;beginAutoRetract();if(state.mode==='playing'&&!state.paused)showPause()});
''','keyboard input')
replace(Path('game.js'),r'''const cap=$('#captureTouchBtn');cap.addEventListener('pointerdown',e=>{e.preventDefault();input.capture=true;cap.classList.add('active')});['pointerup','pointercancel','pointerleave'].forEach(ev=>cap.addEventListener(ev,e=>{e.preventDefault();input.capture=false;cap.classList.remove('active')}));
''',r'''const cap=$('#captureTouchBtn');cap.addEventListener('pointerdown',e=>{e.preventDefault();input.capture=true;stopAutoRetract();cap.classList.add('active')});['pointerup','pointercancel','pointerleave'].forEach(ev=>cap.addEventListener(ev,e=>{e.preventDefault();input.capture=false;beginAutoRetract();cap.classList.remove('active')}));
const dashBtn=$('#dashTouchBtn');if(dashBtn){const dashDown=e=>{e.preventDefault();input.dash=true;dashBtn.classList.add('active')},dashUp=e=>{e.preventDefault();input.dash=false;dashBtn.classList.remove('active')};dashBtn.addEventListener('pointerdown',dashDown);['pointerup','pointercancel','pointerleave'].forEach(ev=>dashBtn.addEventListener(ev,dashUp))}
''','touch input')

# INDEX.HTML
replace(Path('index.html'),'<div class="version">v0.5 feedback beta</div>','<div class="version">v0.5.3 playfeel beta</div>','version label')
replace(Path('index.html'),'''            <p><b>SPACE</b>를 누른 채 바깥으로 나가 선을 만들고, 다시 안전영역에 닿으면 영역을 획득합니다.</p>
            <p>모바일은 아래 방향키 + <b>CAPTURE</b> 버튼을 사용합니다.</p>''','''            <p><b>SPACE</b>를 누른 채 바깥으로 나가 선을 만들고, 다시 안전영역에 닿으면 영역을 획득합니다.</p>
            <p><b>SPACE를 놓으면</b> 그었던 선을 따라 자동으로 안전지대까지 후퇴합니다.</p>
            <p><b>SHIFT</b>는 스태미나를 쓰는 짧은 DASH입니다.</p>
            <p class="muted">Stage 1은 튜토리얼이라 적탄이 없고, Stage 2부터 적탄이 등장합니다.</p>
            <p>모바일은 아래 방향키 + <b>CAPTURE / DASH</b> 버튼을 사용합니다.</p>''','tutorial')
replace(Path('index.html'),'''        <div id="progressBar" class="progress-bar"></div>
          <span class="threshold t80">80</span><span class="threshold t90">90</span><span class="threshold t100">100</span>
        </div>
        <div id="musicLabel" class="music-label">♫</div>''','''        <div id="progressBar" class="progress-bar"></div>
          <span class="threshold t80">80</span><span class="threshold t90">90</span><span class="threshold t100">100</span>
        </div>
        <div class="stamina-box" aria-label="대시 스태미나"><span id="staminaLabel">DASH</span><div class="stamina-track"><div id="staminaBar" class="stamina-bar"></div></div></div>
        <div id="musicLabel" class="music-label">♫</div>''','stamina ui')
replace(Path('index.html'),'''        <button id="captureTouchBtn" class="capture-btn">CAPTURE</button>
      </div>''','''        <div class="mobile-actions"><button id="dashTouchBtn" class="dash-btn">DASH</button><button id="captureTouchBtn" class="capture-btn">CAPTURE</button></div>
      </div>''','mobile dash')

# STYLES.CSS
css=root/'styles.css'
s=css.read_text(encoding='utf-8')
s += r'''

/* v0.5.3 playfeel hotfix: adaptive minimap + stamina dash */
.mini-map{transition:opacity .16s ease,filter .16s ease}
.mini-map.avoid-left{right:auto!important;left:14px!important;opacity:.94}
.stamina-box{display:flex;align-items:center;gap:6px;min-width:128px;color:#e9dcf0;font-size:.58rem;font-weight:900;letter-spacing:.08em;white-space:nowrap}
.stamina-track{width:82px;height:8px;border-radius:999px;overflow:hidden;border:1px solid rgba(255,255,255,.16);background:#211329}
.stamina-bar{height:100%;width:100%;border-radius:999px;background:linear-gradient(90deg,#49e6ff,#8b5cff,#ff5ca8);box-shadow:0 0 10px rgba(73,230,255,.28);transition:width .08s linear}
.mobile-actions{display:flex;align-items:center;gap:10px}
.dash-btn{width:74px;height:54px;border-radius:18px;border:2px solid rgba(255,255,255,.25);background:linear-gradient(145deg,#317cf4,#744cff);box-shadow:0 0 20px rgba(75,114,255,.28);font-weight:950;font-size:.78rem;letter-spacing:.06em;touch-action:none}
.dash-btn.active{transform:scale(.96);filter:brightness(1.25)}
@media (max-width:800px),(pointer:coarse){.mini-map.avoid-left{left:8px!important;right:auto!important}.stamina-box{min-width:92px;gap:4px;font-size:.5rem}.stamina-track{width:54px;height:7px}.mobile-actions{gap:7px}.dash-btn{width:64px;height:48px}.capture-btn{width:92px;height:68px}}
@media (max-width:520px){.music-label{display:none}.stamina-box{min-width:88px}.stamina-track{width:52px}}
'''
css.write_text(s,encoding='utf-8')
print('v0.5.3 playfeel patch applied')
