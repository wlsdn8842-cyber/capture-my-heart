from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path, old, new, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'movement v2 patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

rep(Path('game.js'),
'''function randomUnclaimedCell(minFromPlayer=10){
  for(let i=0;i<500;i++){const x=3+Math.floor(Math.random()*(GW-6)),y=3+Math.floor(Math.random()*(GH-6));if(getCell(x,y)===UNCLAIMED&&dist(x,y,state.player.x,state.player.y)>minFromPlayer)return{x,y}}
  return{x:Math.floor(GW/2),y:Math.floor(GH/2)};
}
function spawnEnemies(){
  state.enemies=[];const cfg=STAGES[state.stage];
  const count=1+cfg.minions;for(let i=0;i<count;i++){const c=randomUnclaimedCell(16);const ang=Math.random()*Math.PI*2;const speed=cfg.speed*(i?0.82:1);state.enemies.push({x:(c.x+.5)*CELL,y:(c.y+.5)*CELL,vx:Math.cos(ang)*speed,vy:Math.sin(ang)*speed,speed,r:i?7:11,isBoss:i===0,chase:cfg.chase*(i?1.25:1),shotTimer:cfg.shots?Math.random()*cfg.shots:Infinity,lastX:(c.x+.5)*CELL,lastY:(c.y+.5)*CELL,stuckFor:0})}
}
''',
'''function randomUnclaimedCell(minFromPlayer=10){
  for(let i=0;i<500;i++){const x=3+Math.floor(Math.random()*(GW-6)),y=3+Math.floor(Math.random()*(GH-6));if(getCell(x,y)===UNCLAIMED&&dist(x,y,state.player.x,state.player.y)>minFromPlayer)return{x,y}}
  return{x:Math.floor(GW/2),y:Math.floor(GH/2)};
}
function isSafeBoundaryCell(x,y){
  if(!inGrid(x,y)||getCell(x,y)!==CLAIMED)return false;
  for(const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]){
    const nx=x+dx,ny=y+dy;if(inGrid(nx,ny)&&getCell(nx,ny)===UNCLAIMED)return true;
  }
  return false;
}
function fairRandomSpawnCell(occupied=[],minPlayerDist=16,minEnemyDist=10){
  let best=null,bestScore=-1;
  for(let i=0;i<900;i++){
    const x=3+Math.floor(Math.random()*(GW-6)),y=3+Math.floor(Math.random()*(GH-6));
    if(getCell(x,y)!==UNCLAIMED)continue;
    const playerDist=dist(x,y,state.player.x,state.player.y);
    let enemyDist=999;
    for(const o of occupied)enemyDist=Math.min(enemyDist,dist(x,y,o.x,o.y));
    const score=Math.min(playerDist,enemyDist);
    if(score>bestScore){best={x,y};bestScore=score}
    if(playerDist>=minPlayerDist&&enemyDist>=minEnemyDist)return{x,y};
  }
  return best||randomUnclaimedCell(minPlayerDist);
}
function spawnEnemies(){
  state.enemies=[];const cfg=STAGES[state.stage],occupied=[];
  const count=1+cfg.minions;
  for(let i=0;i<count;i++){
    const isBoss=i===0;
    const c=fairRandomSpawnCell(occupied,isBoss?18:13,isBoss?0:10);occupied.push(c);
    const ang=Math.random()*Math.PI*2,speed=cfg.speed*(isBoss?1:0.82);
    state.enemies.push({x:(c.x+.5)*CELL,y:(c.y+.5)*CELL,vx:Math.cos(ang)*speed,vy:Math.sin(ang)*speed,speed,r:isBoss?11:7,isBoss,chase:cfg.chase*(isBoss?1:1.25),shotTimer:cfg.shots?Math.random()*cfg.shots:Infinity,lastX:(c.x+.5)*CELL,lastY:(c.y+.5)*CELL,stuckFor:0});
  }
  const boss=occupied[0];
  track('fair_spawn_layout',{stage:state.stage,boss_x:boss?.x??null,boss_y:boss?.y??null,minions:cfg.minions,spread_cells:10});
}
''',
'safe boundary and fair random spawn')

rep(Path('game.js'),
'''const input={dirs:new Set(),lastDir:null,capture:false,dash:false,touchDir:null};
function dirVec(d){return d==='up'?[0,-1]:d==='down'?[0,1]:d==='left'?[-1,0]:d==='right'?[1,0]:[0,0]}
''',
'''const input={dirs:new Set(),lastDir:null,capture:false,dash:false,touchDir:null};
let captureNeedsRelease=false;
function dirVec(d){return d==='up'?[0,-1]:d==='down'?[0,1]:d==='left'?[-1,0]:d==='right'?[1,0]:[0,0]}
function disarmCaptureAfterComplete(reason='capture_complete'){
  input.capture=false;
  if(mobileUXActive()){
    captureNeedsRelease=false;
    resetMobileCaptureLock(reason);
  }else{
    captureNeedsRelease=true;
  }
  track('capture_auto_off',{stage:state.stage,reason});
}
''',
'capture release latch')

rep(Path('game.js'),
'''  if(!p.drawing){
    if(target===CLAIMED){
      p.x=nx;p.y=ny;p.trailStart={x:nx,y:ny};p.trailPath=[];
    } else if(target===UNCLAIMED&&capture){
''',
'''  if(!p.drawing){
    if(target===CLAIMED&&isSafeBoundaryCell(nx,ny)){
      p.x=nx;p.y=ny;p.trailStart={x:nx,y:ny};p.trailPath=[];
    } else if(target===UNCLAIMED&&capture){
''',
'boundary-only safe movement')

rep(Path('game.js'),
'''  state.player.drawing=false;state.player.autoRetract=false;state.player.trailPath=[];rebuildVisualLayers();state.lastArea=before;state.area=calcArea();refreshCharacterArea();refreshContainmentPressure('capture',before,beforeCharacter);
  if(mobileUXActive())resetMobileCaptureLock('capture_complete');
''',
'''  state.player.drawing=false;state.player.autoRetract=false;state.player.trailPath=[];rebuildVisualLayers();state.lastArea=before;state.area=calcArea();refreshCharacterArea();refreshContainmentPressure('capture',before,beforeCharacter);
  disarmCaptureAfterComplete('capture_complete');
''',
'capture complete auto-off')

rep(Path('game.js'),
'''  initGrid();spawnEnemies();state.projectiles=[];state.items=[];state.clearMilestone=0;state.stage1EscapeUsed=false;state.stage1EscapePending=false;state.containmentActive=false;state.containmentPct=100;state.containmentStartedAt=0;state.containmentNextPatternAt=0;state.containmentPendingMilestone=false;state.containmentHoldUntil=0;state.stage1RageUntil=0;state.stage1RageRamReadyAt=0;state.stage1RagePendingClear=false;state.timeLeft=STAGES[state.stage].timer;state.shotAcc=0;state.speedBoostUntil=0;state.freezeUntil=0;state.slowUntil=0;state.shield=0;state.dashStamina=100;state.dashExhausted=false;state.stageStartedAt=Date.now();state.mode='playing';state.paused=false;state.lastTs=performance.now();state.moveAcc=0;state.timerAcc=0;
''',
'''  initGrid();captureNeedsRelease=false;spawnEnemies();state.projectiles=[];state.items=[];state.clearMilestone=0;state.stage1EscapeUsed=false;state.stage1EscapePending=false;state.containmentActive=false;state.containmentPct=100;state.containmentStartedAt=0;state.containmentNextPatternAt=0;state.containmentPendingMilestone=false;state.containmentHoldUntil=0;state.stage1RageUntil=0;state.stage1RageRamReadyAt=0;state.stage1RagePendingClear=false;state.timeLeft=STAGES[state.stage].timer;state.shotAcc=0;state.speedBoostUntil=0;state.freezeUntil=0;state.slowUntil=0;state.shield=0;state.dashStamina=100;state.dashExhausted=false;state.stageStartedAt=Date.now();state.mode='playing';state.paused=false;state.lastTs=performance.now();state.moveAcc=0;state.timerAcc=0;
''',
'stage capture latch reset')

rep(Path('game.js'),
'''window.addEventListener('keydown',e=>{if(keyMap[e.code]){input.dirs.add(keyMap[e.code]);input.lastDir=keyMap[e.code];if(state.mode==='playing')e.preventDefault()}if(e.code==='Space'){input.capture=true;stopAutoRetract();if(state.mode==='playing')e.preventDefault()}if(e.code==='ShiftLeft'||e.code==='ShiftRight'){input.dash=true;if(state.mode==='playing')e.preventDefault()}if(e.code==='Escape'&&state.mode==='playing'&&!state.paused)showPause()});
window.addEventListener('keyup',e=>{if(keyMap[e.code])input.dirs.delete(keyMap[e.code]);if(e.code==='Space'){input.capture=false;beginAutoRetract()}if(e.code==='ShiftLeft'||e.code==='ShiftRight')input.dash=false});
window.addEventListener('blur',()=>{input.dirs.clear();input.capture=false;input.dash=false;beginAutoRetract()});
''',
'''window.addEventListener('keydown',e=>{if(keyMap[e.code]){input.dirs.add(keyMap[e.code]);input.lastDir=keyMap[e.code];if(state.mode==='playing')e.preventDefault()}if(e.code==='Space'){if(!captureNeedsRelease){input.capture=true;stopAutoRetract()}if(state.mode==='playing')e.preventDefault()}if(e.code==='ShiftLeft'||e.code==='ShiftRight'){input.dash=true;if(state.mode==='playing')e.preventDefault()}if(e.code==='Escape'&&state.mode==='playing'&&!state.paused)showPause()});
window.addEventListener('keyup',e=>{if(keyMap[e.code])input.dirs.delete(keyMap[e.code]);if(e.code==='Space'){captureNeedsRelease=false;input.capture=false;beginAutoRetract()}if(e.code==='ShiftLeft'||e.code==='ShiftRight')input.dash=false});
window.addEventListener('blur',()=>{input.dirs.clear();captureNeedsRelease=false;input.capture=false;input.dash=false;beginAutoRetract()});
''',
'desktop capture rearm')

rep(Path('game.js'),
'''document.addEventListener('visibilitychange',()=>{if(!document.hidden)return;if(mobileUXActive())resetMobileCaptureLock('visibility_hidden');input.dirs.clear();input.capture=false;input.dash=false;beginAutoRetract();if(state.mode==='playing'&&!state.paused)showPause()});
''',
'''document.addEventListener('visibilitychange',()=>{if(!document.hidden)return;if(mobileUXActive())resetMobileCaptureLock('visibility_hidden');input.dirs.clear();captureNeedsRelease=false;input.capture=false;input.dash=false;beginAutoRetract();if(state.mode==='playing'&&!state.paused)showPause()});
''',
'visibility capture reset')

rep(Path('game.js'),
'''<p class="muted">보스를 작은 영역에 가두면 <b>CONTAINMENT</b>가 발동합니다. 모든 Stage에서 첫 80% 포획 압박 시 PANIC BREAKOUT → 영역 재탈환 → RAGE 추격이 발동할 수 있습니다. Stage 3부터 레이저, Stage 5부터 영역 파괴, Stage 8부터 순간이동이 추가됩니다.</p><p class="muted">본편 Stage 1부터 적탄과 졸개가 등장합니다. 별도 튜토리얼에서 조작을 먼저 익힐 수 있습니다.</p>''',
'''<p class="muted">보스를 작은 영역에 가두면 <b>CONTAINMENT</b>가 발동합니다. 모든 Stage에서 첫 80% 포획 압박 시 PANIC BREAKOUT → 영역 재탈환 → RAGE 추격이 발동할 수 있습니다. Stage 3부터 레이저, Stage 5부터 영역 파괴, Stage 8부터 순간이동이 추가됩니다.</p><p class="muted">안전 상태에서는 점령 영역의 <b>테두리만 이동</b>합니다. CAPTURE를 누른 상태에서만 미점령 영역으로 나가며, 선을 다시 연결하면 CAPTURE가 자동 해제됩니다.</p><p class="muted">본편 Stage 1부터 적탄과 졸개가 등장하며, 보스·졸개 시작 위치는 매 판 공정한 범위에서 랜덤 배치됩니다.</p>''',
'howto movement v2')

rep(Path('index.html'),'<div class="version">v0.13.2 collection 3d access</div>','<div class="version">v0.14.0 movement v2</div>','version label')
rep(Path('config.js'),"VERSION: '0.13.2'","VERSION: '0.14.0'",'config version')
rep(Path('sw.js'),"cmh-core-v0.13.2","cmh-core-v0.14.0",'service worker cache version')

print('v0.14.0 movement v2 + fair random spawn applied')
