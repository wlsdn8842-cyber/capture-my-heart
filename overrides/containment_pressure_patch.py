from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path, old, new, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'containment pressure patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

rep(Path('game.js'),
"  enemies:[], projectiles:[], items:[], area:0, lastArea:0, characterArea:null, characterMaskTotal:0, clearMilestone:0, stage1EscapeUsed:false, stage1EscapePending:false,",
"  enemies:[], projectiles:[], items:[], area:0, lastArea:0, characterArea:null, characterMaskTotal:0, clearMilestone:0, stage1EscapeUsed:false, stage1EscapePending:false, containmentActive:false, containmentPct:100, containmentStartedAt:0, containmentNextPatternAt:0, containmentPendingMilestone:false, containmentHoldUntil:0,",
'containment state fields')

rep(Path('game.js'),
"initGrid();spawnEnemies();state.projectiles=[];state.items=[];state.clearMilestone=0;state.stage1EscapeUsed=false;state.stage1EscapePending=false;",
"initGrid();spawnEnemies();state.projectiles=[];state.items=[];state.clearMilestone=0;state.stage1EscapeUsed=false;state.stage1EscapePending=false;state.containmentActive=false;state.containmentPct=100;state.containmentStartedAt=0;state.containmentNextPatternAt=0;state.containmentPendingMilestone=false;state.containmentHoldUntil=0;",
'containment stage reset')

anchor="""function stageProgressMetric(){
  if(state.stage===1&&Number.isFinite(state.characterArea)){
    return {kind:'character',label:'CHAR',value:state.characterArea};
  }
  return {kind:'area',label:'AREA',value:state.area};
}
"""
block="""function stageProgressMetric(){
  if(state.stage===1&&Number.isFinite(state.characterArea)){
    return {kind:'character',label:'CHAR',value:state.characterArea};
  }
  return {kind:'area',label:'AREA',value:state.area};
}

// v0.12.0 CONTAINMENT PRESSURE — trapping the boss is powerful, not an instant-win answer.
const CONTAINMENT_V1={triggerPct:15,milestoneTriggerPct:25,releasePct:30,speedBoost:1.25,holdMs:1450};
function bossOpenComponent(e){
  if(!e)return null;
  const start=bossCellOf(e),startKey=idx(start.x,start.y);
  let sx=start.x,sy=start.y;
  if(!inGrid(sx,sy)||getCell(sx,sy)!==UNCLAIMED){
    let found=null;
    for(let r=1;r<=4&&!found;r++)for(let dy=-r;dy<=r&&!found;dy++)for(let dx=-r;dx<=r;dx++){
      const x=start.x+dx,y=start.y+dy;
      if(inGrid(x,y)&&getCell(x,y)===UNCLAIMED){found={x,y};break}
    }
    if(!found)return null;sx=found.x;sy=found.y;
  }
  const seen=new Uint8Array(grid.length),q=new Int32Array(grid.length);let qh=0,qt=0;
  const push=(x,y)=>{if(!bossInteriorCell(x,y))return;const k=idx(x,y);if(seen[k]||getCell(x,y)!==UNCLAIMED)return;seen[k]=1;q[qt++]=k};
  push(sx,sy);
  while(qh<qt){const k=q[qh++],x=k%GW,y=(k/GW)|0;push(x+1,y);push(x-1,y);push(x,y+1);push(x,y-1)}
  const total=(GW-4)*(GH-4),pct=total?qt/total*100:100;
  return {cells:qt,pct,total,startKey};
}
function containmentCrossedMilestone(beforeArea,beforeCharacter){
  const current=stageProgressMetric().value;
  const before=state.stage===1&&Number.isFinite(beforeCharacter)?beforeCharacter:beforeArea;
  if(!Number.isFinite(before)||!Number.isFinite(current))return false;
  const perfect=state.stage===1?100:99;
  return (before<80&&current>=80)||(before<90&&current>=90)||(before<perfect&&current>=perfect);
}
function containmentPatternDelay(){return Math.max(1150,2800-state.stage*130)}
function updateContainmentHUD(){
  let el=$('#containmentBadge');
  if(!state.containmentActive){if(el)el.classList.add('hidden');return}
  if(!el){el=document.createElement('div');el.id='containmentBadge';el.className='containment-badge';gameScreen.appendChild(el)}
  el.classList.remove('hidden');
  const hold=state.containmentPendingMilestone?Math.max(0,state.containmentHoldUntil-now()):0;
  el.innerHTML='<b>CONTAINMENT</b><span>'+state.containmentPct.toFixed(1)+'%</span><small>RAGE ×'+CONTAINMENT_V1.speedBoost.toFixed(2)+(hold>0?' · HOLD '+(hold/1000).toFixed(1)+'s':'')+'</small>';
}
function refreshContainmentPressure(reason='update',beforeArea=null,beforeCharacter=null){
  if(tutorial.active)return false;
  const boss=state.enemies.find(e=>e.isBoss);if(!boss)return false;
  const info=bossOpenComponent(boss);if(!info)return false;
  state.containmentPct=info.pct;
  const crossed=reason==='capture'&&containmentCrossedMilestone(beforeArea,beforeCharacter);
  const shouldActivate=info.pct<=CONTAINMENT_V1.triggerPct||(crossed&&info.pct<=CONTAINMENT_V1.milestoneTriggerPct);
  const t=now();
  if(!state.containmentActive&&shouldActivate){
    state.containmentActive=true;state.containmentStartedAt=t;
    state.containmentNextPatternAt=t+(state.stage===1&&!state.stage1EscapeUsed?900:700);
    if(crossed){state.containmentPendingMilestone=true;state.containmentHoldUntil=t+CONTAINMENT_V1.holdMs}
    boss.breakoutReadyAt=Math.min(boss.breakoutReadyAt||t+99999,state.containmentNextPatternAt);
    boss.trapTime=Math.max(boss.trapTime||0,bossBreakoutCfg().trap);
    toast('CONTAINMENT! · '+info.pct.toFixed(1)+'% · BOSS RAGE',true,1250);
    audio.beep(210,.10,'sawtooth',.032);audio.beep(420,.08,'triangle',.024);juiceShake(2.2,120);juiceHaptic([18,22,18]);
    track('boss_containment_start',{stage:state.stage,reason,component_pct:Number(info.pct.toFixed(2)),component_cells:info.cells,crossed_milestone:crossed,metric:stageProgressMetric().kind,metric_value:Number(stageProgressMetric().value.toFixed(2))});
    return true;
  }
  if(state.containmentActive&&info.pct>=CONTAINMENT_V1.releasePct){
    const pending=state.containmentPendingMilestone;
    state.containmentActive=false;state.containmentStartedAt=0;state.containmentNextPatternAt=0;state.containmentPendingMilestone=pending;state.containmentHoldUntil=pending?t:0;
    track('boss_containment_end',{stage:state.stage,reason,component_pct:Number(info.pct.toFixed(2))});
    toast('CONTAINMENT BROKEN · BOSS ESCAPED',false,950);
    return false;
  }
  return state.containmentActive;
}
"""
rep(Path('game.js'),anchor,block,'containment engine')

rep(Path('game.js'),
"state.player.drawing=false;state.player.autoRetract=false;state.player.trailPath=[];rebuildVisualLayers();state.lastArea=before;state.area=calcArea();refreshCharacterArea();",
"state.player.drawing=false;state.player.autoRetract=false;state.player.trailPath=[];rebuildVisualLayers();state.lastArea=before;state.area=calcArea();refreshCharacterArea();refreshContainmentPressure('capture',before,beforeCharacter);",
'capture containment refresh')

rep(Path('game.js'),
"  if(!boss||!bossTightPocket(boss))return false;",
"  if(!boss||(!bossTightPocket(boss)&&!state.containmentActive))return false;",
'stage1 containment trigger')

rep(Path('game.js'),
"  state.stage1EscapeUsed=true;state.stage1EscapePending=true;",
"  state.stage1EscapeUsed=true;state.stage1EscapePending=true;state.containmentPendingMilestone=false;state.containmentHoldUntil=0;",
'stage1 clears hold')

rep(Path('game.js'),
"  if(stage1EmergencyEscape(m))return;\n  const perfectTarget=m.kind==='character'?100:99;",
"  if(stage1EmergencyEscape(m))return;\n  if(state.containmentPendingMilestone&&now()<state.containmentHoldUntil)return;\n  if(state.containmentPendingMilestone){state.containmentPendingMilestone=false;state.containmentHoldUntil=0}\n  const perfectTarget=m.kind==='character'?100:99;",
'containment clear hold')

rep(Path('game.js'),
"rebuildVisualLayers();state.lastArea=before;state.area=calcArea();refreshCharacterArea();updateHUD();",
"rebuildVisualLayers();state.lastArea=before;state.area=calcArea();refreshCharacterArea();refreshContainmentPressure('boss_break');updateHUD();",
'boss break containment refresh')

rep(Path('game.js'),
"  track('boss_pattern_fire',{stage:state.stage,kind:b.kind,reason:b.reason,affected});\n  e.breakout=null;e.trapTime=0;e.bounceHeat=0;e.breakoutReadyAt=now()+cfg.cooldown*1000;\n  e.nextSiegeAt=now()+cfg.siegeMs*(.85+Math.random()*.3);",
"  track('boss_pattern_fire',{stage:state.stage,kind:b.kind,reason:b.reason,affected});\n  e.breakout=null;e.trapTime=0;e.bounceHeat=0;refreshContainmentPressure('pattern_fire');\n  e.breakoutReadyAt=now()+(state.containmentActive?containmentPatternDelay():cfg.cooldown*1000);\n  state.containmentNextPatternAt=e.breakoutReadyAt;\n  e.nextSiegeAt=now()+cfg.siegeMs*(.85+Math.random()*.3);",
'containment pattern cooldown')

rep(Path('game.js'),
"  e.breakoutReadyAt=e.breakoutReadyAt||t+3500;\n  e.nextSiegeAt=e.nextSiegeAt||t+cfg.siegeMs;",
"  e.breakoutReadyAt=e.breakoutReadyAt||t+3500;\n  e.nextSiegeAt=e.nextSiegeAt||t+cfg.siegeMs;\n  if(state.containmentActive&&!(state.stage===1&&!state.stage1EscapeUsed)&&t>=Math.max(e.breakoutReadyAt||0,state.containmentNextPatternAt||0)){\n    bossBeginPattern(e,bossPatternName(e,cfg,'containment'),'containment');return true;\n  }",
'containment repeated pressure')

rep(Path('game.js'),
"    const speed=e.speed*(slow ? 0.55 : 1)*bal.speed*drawingBossPressure;",
"    const containmentBoost=e.isBoss&&state.containmentActive?CONTAINMENT_V1.speedBoost:1;\n    const speed=e.speed*(slow ? 0.55 : 1)*bal.speed*drawingBossPressure*containmentBoost;",
'containment speed boost')

rep(Path('game.js'),
"gameScreen.classList.toggle('hud-time-danger',state.timeLeft<25);updateCharacterMaskDebugHUD();updateMusicLabel();",
"gameScreen.classList.toggle('hud-time-danger',state.timeLeft<25);updateCharacterMaskDebugHUD();updateContainmentHUD();updateMusicLabel();",
'containment hud hook')

rep(Path('game.js'),
"    if(!state.paused&&!tutorial.active){updateEnemies(dt);updateProjectiles(dt);state.timerAcc+=dt;",
"    if(!state.paused&&!tutorial.active){updateEnemies(dt);updateProjectiles(dt);if(state.containmentPendingMilestone&&now()>=state.containmentHoldUntil)checkMilestone();state.timerAcc+=dt;",
'containment held milestone retry')


rep(Path('game.js'),
"<p class=\"muted\">보스를 좁은 곳에 가두면 BREAKOUT 패턴이 발동합니다. Stage 3부터 레이저, Stage 5부터 영역 파괴, Stage 8부터 순간이동이 추가됩니다.</p>",
"<p class=\"muted\">보스를 작은 영역에 가두면 <b>CONTAINMENT</b>가 발동해 보스가 25% 빨라지고 BREAKOUT 압박이 빨라집니다. Stage 3부터 레이저, Stage 5부터 영역 파괴, Stage 8부터 순간이동이 추가됩니다.</p>",
'containment howto')

rep(Path('index.html'),
'<div class="version">v0.11.2 stage1 escape</div>',
'<div class="version">v0.12.0 containment pressure</div>',
'version label')

css=root/'styles.css';s=css.read_text(encoding='utf-8')
if '/* v0.12.0 containment pressure */' not in s:
    s+=r'''
/* v0.12.0 containment pressure */
.containment-badge{position:absolute;z-index:51;left:50%;top:88px;transform:translateX(-50%);display:flex;align-items:center;gap:8px;padding:6px 11px;border:1px solid rgba(255,84,90,.72);border-radius:999px;background:rgba(30,4,9,.91);box-shadow:0 0 24px rgba(255,45,73,.25);font-size:.62rem;color:#fff;pointer-events:none;white-space:nowrap;animation:containmentPulse .65s ease-in-out infinite alternate}.containment-badge b{color:#ff6478;letter-spacing:.06em}.containment-badge span{font-weight:900;color:#ffd45f}.containment-badge small{color:#ffc1ca}@keyframes containmentPulse{from{transform:translateX(-50%) scale(.98);filter:brightness(.95)}to{transform:translateX(-50%) scale(1.025);filter:brightness(1.18)}}@media(pointer:coarse),(max-width:800px){.containment-badge{top:62px;padding:4px 7px;font-size:.49rem;gap:5px}.containment-badge small{display:none}}
'''
    css.write_text(s,encoding='utf-8')

print('v0.12.0 containment pressure applied')
