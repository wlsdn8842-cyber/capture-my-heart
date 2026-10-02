from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path,old,new,label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'stage1 rage v2 patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

rep(Path('game.js'),
"containmentPendingMilestone:false, containmentHoldUntil:0,",
"containmentPendingMilestone:false, containmentHoldUntil:0, stage1RageUntil:0, stage1RageRamReadyAt:0, stage1RagePendingClear:false,",
'rage state fields')

rep(Path('game.js'),
"state.containmentPendingMilestone=false;state.containmentHoldUntil=0;",
"state.containmentPendingMilestone=false;state.containmentHoldUntil=0;state.stage1RageUntil=0;state.stage1RageRamReadyAt=0;state.stage1RagePendingClear=false;",
'rage stage reset')

rep(Path('game.js'),
"const CONTAINMENT_V1={triggerPct:15,milestoneTriggerPct:25,releasePct:30,speedBoost:1.25,holdMs:1450};",
"""const CONTAINMENT_V1={triggerPct:15,milestoneTriggerPct:25,releasePct:30,speedBoost:1.25,holdMs:1450};
const STAGE1_RAGE_V2={durationMs:3500,speedBoost:1.45,chase:.36,charLossPct:12,ramRetryMs:620};
function stage1RageActive(){return state.stage===1&&state.stage1RageUntil>now()}
function stage1RageReclaimCells(target){
  if(!target)return stage1EmergencyPocket(target);
  const decoded=decodeCharacterMask(1),mask=decoded?.mask;
  if(!mask)return stage1EmergencyPocket(target);
  const goal=Math.max(1,Math.round((state.characterMaskTotal||decoded.source?.cells||1)*STAGE1_RAGE_V2.charLossPct/100));
  const cand=[];
  for(let y=2;y<GH-2;y++)for(let x=2;x<GW-2;x++){
    if(getCell(x,y)!==CLAIMED)continue;
    const k=idx(x,y),dx=x-target.x,dy=y-target.y;
    cand.push({x,y,k,d2:dx*dx+dy*dy,char:mask[k]?1:0});
  }
  cand.sort((a,b)=>a.d2-b.d2);
  const out=[];let charLoss=0;
  for(const p of cand){
    out.push({x:p.x,y:p.y});
    charLoss+=p.char;
    if(charLoss>=goal)break;
    if(out.length>=2600)break;
  }
  return out.length?out:stage1EmergencyPocket(target);
}""",
'rage config and reclaim')

old_target="""function stage1EmergencyTarget(e){
  let best=null;
  for(let i=0;i<420;i++){
    const x=5+Math.floor(Math.random()*(GW-10)),y=5+Math.floor(Math.random()*(GH-10));
    if(getCell(x,y)!==CLAIMED)continue;
    const pd=Math.abs(x-state.player.x)+Math.abs(y-state.player.y);
    const bc=bossCellOf(e),bd=Math.abs(x-bc.x)+Math.abs(y-bc.y);
    if(pd<16||bd<18)continue;
    best={x,y};break;
  }
  if(best)return best;
  for(let y=5;y<GH-5;y++)for(let x=5;x<GW-5;x++){
    if(getCell(x,y)===CLAIMED&&Math.abs(x-state.player.x)+Math.abs(y-state.player.y)>12)return{x,y};
  }
  return null;
}"""
new_target="""function stage1EmergencyTarget(e){
  const decoded=decodeCharacterMask(1),mask=decoded?.mask,bc=bossCellOf(e);
  const pick=requireChar=>{
    for(let i=0;i<520;i++){
      const x=5+Math.floor(Math.random()*(GW-10)),y=5+Math.floor(Math.random()*(GH-10)),k=idx(x,y);
      if(getCell(x,y)!==CLAIMED)continue;
      if(requireChar&&(!mask||!mask[k]))continue;
      const pd=Math.abs(x-state.player.x)+Math.abs(y-state.player.y),bd=Math.abs(x-bc.x)+Math.abs(y-bc.y);
      if(pd<16||bd<18)continue;
      return{x,y};
    }
    return null;
  };
  const best=pick(true)||pick(false);if(best)return best;
  for(let y=5;y<GH-5;y++)for(let x=5;x<GW-5;x++){
    const k=idx(x,y);
    if(getCell(x,y)===CLAIMED&&Math.abs(x-state.player.x)+Math.abs(y-state.player.y)>12&&(!mask||mask[k]))return{x,y};
  }
  return null;
}"""
rep(Path('game.js'),old_target,new_target,'mask-aware escape target')

rep(Path('game.js'),
"      affected=bossReopenCells(stage1EmergencyPocket(target),'escape',e);",
"""      const beforeRageChar=Number.isFinite(state.characterArea)?state.characterArea:null;
      affected=bossReopenCells(stage1RageReclaimCells(target),'escape',e);
      const charLost=beforeRageChar===null||!Number.isFinite(state.characterArea)?0:Math.max(0,beforeRageChar-state.characterArea);""",
'character reclaim')

rep(Path('game.js'),
"      e.vx=Math.cos(ang)*sp;e.vy=Math.sin(ang)*sp;\n      juiceBurst(oldX,oldY,'#ffb24d',22,88,460);",
"""      e.vx=Math.cos(ang)*sp;e.vy=Math.sin(ang)*sp;
      const rageNow=now();state.stage1RageUntil=rageNow+STAGE1_RAGE_V2.durationMs;state.stage1RageRamReadyAt=rageNow+480;state.stage1RagePendingClear=false;
      toast('RAGE! · CHAR -'+charLost.toFixed(1)+'% · '+(STAGE1_RAGE_V2.durationMs/1000).toFixed(1)+'s',true,1350);
      track('stage1_rage_start',{stage:1,char_lost:Number(charLost.toFixed(2)),character_area:Number((state.characterArea||0).toFixed(2)),duration_ms:STAGE1_RAGE_V2.durationMs,speed_boost:STAGE1_RAGE_V2.speedBoost});
      juiceBurst(oldX,oldY,'#ffb24d',22,88,460);""",
'rage start')

old_hud="""function updateContainmentHUD(){
  let el=$('#containmentBadge');
  if(!state.containmentActive){if(el)el.classList.add('hidden');return}
  if(!el){el=document.createElement('div');el.id='containmentBadge';el.className='containment-badge';gameScreen.appendChild(el)}
  el.classList.remove('hidden');
  const hold=state.containmentPendingMilestone?Math.max(0,state.containmentHoldUntil-now()):0;
  el.innerHTML='<b>CONTAINMENT</b><span>'+state.containmentPct.toFixed(1)+'%</span><small>RAGE ×'+CONTAINMENT_V1.speedBoost.toFixed(2)+(hold>0?' · HOLD '+(hold/1000).toFixed(1)+'s':'')+'</small>';
}"""
new_hud="""function updateContainmentHUD(){
  let el=$('#containmentBadge'),rage=stage1RageActive();
  if(!state.containmentActive&&!rage){if(el)el.classList.add('hidden');return}
  if(!el){el=document.createElement('div');el.id='containmentBadge';el.className='containment-badge';gameScreen.appendChild(el)}
  el.classList.remove('hidden');
  if(rage){
    const remain=Math.max(0,state.stage1RageUntil-now());
    el.innerHTML='<b>RAGE</b><span>'+(remain/1000).toFixed(1)+'s</span><small>CHASE ×'+STAGE1_RAGE_V2.speedBoost.toFixed(2)+' · RETRAP = RAM</small>';
    return;
  }
  const hold=state.containmentPendingMilestone?Math.max(0,state.containmentHoldUntil-now()):0;
  el.innerHTML='<b>CONTAINMENT</b><span>'+state.containmentPct.toFixed(1)+'%</span><small>RAGE ×'+CONTAINMENT_V1.speedBoost.toFixed(2)+(hold>0?' · HOLD '+(hold/1000).toFixed(1)+'s':'')+'</small>';
}"""
rep(Path('game.js'),old_hud,new_hud,'rage HUD')

old_speed="""    const containmentBoost=e.isBoss&&state.containmentActive?CONTAINMENT_V1.speedBoost:1;
    const speed=e.speed*(slow ? 0.55 : 1)*bal.speed*drawingBossPressure*containmentBoost;
    const effectiveChase=state.player.drawing
      ? Math.min(.24,(e.chase||0)+(e.isBoss?bal.chase:bal.chase*.55)+areaPressure*(e.isBoss?.028:.012))
      : (e.chase||0);
    if(state.player.drawing&&effectiveChase>0){"""
new_speed="""    const rageChase=e.isBoss&&stage1RageActive();
    const pressureBoost=rageChase?STAGE1_RAGE_V2.speedBoost:(e.isBoss&&state.containmentActive?CONTAINMENT_V1.speedBoost:1);
    const speed=e.speed*(slow ? 0.55 : 1)*bal.speed*drawingBossPressure*pressureBoost;
    const effectiveChase=rageChase
      ? STAGE1_RAGE_V2.chase
      : state.player.drawing
        ? Math.min(.24,(e.chase||0)+(e.isBoss?bal.chase:bal.chase*.55)+areaPressure*(e.isBoss?.028:.012))
        : (e.chase||0);
    if((state.player.drawing||rageChase)&&effectiveChase>0){"""
rep(Path('game.js'),old_speed,new_speed,'rage chase and speed')

old_pattern="""  if(e.breakout){
    if(t>=e.breakout.fireAt)bossFirePattern(e);
    else return true;
  }
  e.breakoutReadyAt=e.breakoutReadyAt||t+3500;"""
new_pattern="""  if(e.breakout){
    if(t>=e.breakout.fireAt)bossFirePattern(e);
    else return true;
  }
  if(stage1RageActive()&&bossTightPocket(e)&&t>=state.stage1RageRamReadyAt){
    state.stage1RageRamReadyAt=t+STAGE1_RAGE_V2.ramRetryMs;
    bossBeginPattern(e,'ram','stage1_rage_retrap');
    track('stage1_rage_retrap',{stage:1,remaining_ms:Math.max(0,Math.round(state.stage1RageUntil-t))});
    return true;
  }
  e.breakoutReadyAt=e.breakoutReadyAt||t+3500;"""
rep(Path('game.js'),old_pattern,new_pattern,'rage retrap RAM')

rep(Path('game.js'),
"  if(stage1EmergencyEscape(m))return;\n  if(state.containmentPendingMilestone&&now()<state.containmentHoldUntil)return;",
"""  if(stage1EmergencyEscape(m))return;
  if(stage1RageActive()&&a>=80){state.stage1RagePendingClear=true;return}
  if(state.stage1RagePendingClear&&!stage1RageActive())state.stage1RagePendingClear=false;
  if(state.containmentPendingMilestone&&now()<state.containmentHoldUntil)return;""",
'rage clear lock')

rep(Path('game.js'),
"if(state.containmentPendingMilestone&&now()>=state.containmentHoldUntil)checkMilestone();state.timerAcc+=dt;",
"if(state.containmentPendingMilestone&&now()>=state.containmentHoldUntil)checkMilestone();if(state.stage1RagePendingClear&&!stage1RageActive())checkMilestone();state.timerAcc+=dt;",
'rage clear retry')

rep(Path('game.js'),
"<p class=\"muted\">보스를 작은 영역에 가두면 <b>CONTAINMENT</b>가 발동해 보스가 25% 빨라지고 BREAKOUT 압박이 빨라집니다. Stage 3부터 레이저, Stage 5부터 영역 파괴, Stage 8부터 순간이동이 추가됩니다.</p>",
"<p class=\"muted\">보스를 작은 영역에 가두면 <b>CONTAINMENT</b>가 발동합니다. Stage 1 첫 포획은 캐릭터 영역을 되찾고 3.5초 RAGE 추격을 시작합니다. Stage 3부터 레이저, Stage 5부터 영역 파괴, Stage 8부터 순간이동이 추가됩니다.</p>",
'rage howto')

rep(Path('index.html'),
'<div class="version">v0.12.1 complete collection</div>',
'<div class="version">v0.12.2 stage1 rage v2</div>',
'version label')

# Final build versions are advanced here because collection_reward_patch intentionally owns v0.12.1.
config=root/'config.js';s=config.read_text(encoding='utf-8')
if "VERSION: '0.12.1'" not in s: raise SystemExit('stage1 rage v2 patch failed: config version')
config.write_text(s.replace("VERSION: '0.12.1'","VERSION: '0.12.2'",1),encoding='utf-8')

sw=root/'sw.js';s=sw.read_text(encoding='utf-8')
if "cmh-core-v0.12.1" not in s: raise SystemExit('stage1 rage v2 patch failed: sw version')
sw.write_text(s.replace("cmh-core-v0.12.1","cmh-core-v0.12.2",1),encoding='utf-8')

print('v0.12.2 Stage 1 RAGE v2 applied')
