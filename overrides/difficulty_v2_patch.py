from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path, old, new, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'difficulty v2 patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

# Stage curve: Stage 1 starts around the old Stage 6 pressure; 7-10 ramp sharply.
rep(Path('game.js'),
"""const STAGES = [null,
  {name:'Maid Cafe',     music:'assets/audio/stages_1_4.mp3', speed:84,  shots:0,    minions:0, chase:0.018,timer:180, hue:'#ff6aaa'},
  {name:'Racing Girl',   music:'assets/audio/stages_1_4.mp3', speed:91,  shots:3400, minions:0, chase:0.03, timer:175, hue:'#ff6a8b'},
  {name:'Office Lady',   music:'assets/audio/stages_1_4.mp3', speed:98,  shots:3100, minions:0, chase:0.05, timer:170, hue:'#62c6ff'},
  {name:'Miko',          music:'assets/audio/stages_1_4.mp3', speed:105, shots:2800, minions:0, chase:0.06, timer:165, hue:'#ff5f70'},
  {name:'Idol',          music:'assets/audio/stages_5_8.mp3', speed:112, shots:2500, minions:1, chase:0.08, timer:160, hue:'#ff5fcf'},
  {name:'Resort',        music:'assets/audio/stages_5_8.mp3', speed:118, shots:2300, minions:1, chase:0.10, timer:155, hue:'#45dcff'},
  {name:'Wizard',        music:'assets/audio/stages_5_8.mp3', speed:125, shots:2100, minions:1, chase:0.14, timer:150, hue:'#a768ff'},
  {name:'Gothic',        music:'assets/audio/stages_5_8.mp3', speed:132, shots:1900, minions:2, chase:0.18, timer:145, hue:'#e44879'},
  {name:'Kung-fu',       music:'assets/audio/main.mp3',       speed:140, shots:1700, minions:2, chase:0.22, timer:140, hue:'#ffb04e'},
  {name:'Final Queen',   music:'assets/audio/stage10.mp3',    speed:148, shots:1450, minions:3, chase:0.26, timer:135, hue:'#ffd66a'}
""",
"""const STAGES = [null,
  {name:'Maid Cafe',     music:'assets/audio/stages_1_4.mp3', speed:112, shots:2600, minions:1, chase:0.10, timer:180, hue:'#ff6aaa'},
  {name:'Racing Girl',   music:'assets/audio/stages_1_4.mp3', speed:117, shots:2400, minions:1, chase:0.115,timer:175, hue:'#ff6a8b'},
  {name:'Office Lady',   music:'assets/audio/stages_1_4.mp3', speed:123, shots:2200, minions:1, chase:0.13, timer:170, hue:'#62c6ff'},
  {name:'Miko',          music:'assets/audio/stages_1_4.mp3', speed:129, shots:2000, minions:2, chase:0.15, timer:165, hue:'#ff5f70'},
  {name:'Idol',          music:'assets/audio/stages_5_8.mp3', speed:136, shots:1850, minions:2, chase:0.17, timer:160, hue:'#ff5fcf'},
  {name:'Resort',        music:'assets/audio/stages_5_8.mp3', speed:143, shots:1700, minions:3, chase:0.19, timer:155, hue:'#45dcff'},
  {name:'Wizard',        music:'assets/audio/stages_5_8.mp3', speed:150, shots:1500, minions:3, chase:0.21, timer:150, hue:'#a768ff'},
  {name:'Gothic',        music:'assets/audio/stages_5_8.mp3', speed:158, shots:1350, minions:3, chase:0.235,timer:145, hue:'#e44879'},
  {name:'Kung-fu',       music:'assets/audio/main.mp3',       speed:168, shots:1150, minions:4, chase:0.265,timer:140, hue:'#ffb04e'},
  {name:'Final Queen',   music:'assets/audio/stage10.mp3',    speed:180, shots:1000, minions:4, chase:0.30, timer:135, hue:'#ffd66a'}
""",
'stage difficulty curve')

rep(Path('game.js'),
"""const STAGE1_RAGE_V2={durationMs:3500,speedBoost:1.45,chase:.36,charLossPct:12,ramRetryMs:620};
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
}
""",
"""const BOSS_RAGE_V3={
  1:{durationMs:3500,speedBoost:1.40,chase:.30,reclaimPct:9.6, ramRetryMs:720,chaseCap:.25,multiShot:0},
  2:{durationMs:3500,speedBoost:1.40,chase:.31,reclaimPct:9.8, ramRetryMs:700,chaseCap:.25,multiShot:0},
  3:{durationMs:3800,speedBoost:1.45,chase:.32,reclaimPct:10.0,ramRetryMs:680,chaseCap:.27,multiShot:0},
  4:{durationMs:3800,speedBoost:1.45,chase:.33,reclaimPct:10.2,ramRetryMs:660,chaseCap:.27,multiShot:0},
  5:{durationMs:4200,speedBoost:1.50,chase:.34,reclaimPct:10.5,ramRetryMs:640,chaseCap:.29,multiShot:0},
  6:{durationMs:4200,speedBoost:1.50,chase:.35,reclaimPct:10.8,ramRetryMs:620,chaseCap:.29,multiShot:0},
  7:{durationMs:4600,speedBoost:1.55,chase:.36,reclaimPct:11.0,ramRetryMs:600,chaseCap:.31,multiShot:.30},
  8:{durationMs:5000,speedBoost:1.60,chase:.37,reclaimPct:11.5,ramRetryMs:580,chaseCap:.33,multiShot:.34},
  9:{durationMs:5500,speedBoost:1.68,chase:.38,reclaimPct:12.0,ramRetryMs:560,chaseCap:.35,multiShot:.40},
 10:{durationMs:6000,speedBoost:1.75,chase:.40,reclaimPct:12.5,ramRetryMs:540,chaseCap:.37,multiShot:.45}
};
function bossDifficultyV2Profile(){return BOSS_RAGE_V3[state.stage]||BOSS_RAGE_V3[10]}
function stage1RageActive(){return state.stage1RageUntil>now()}
function stage1RageReclaimCells(target){
  if(!target)return stage1EmergencyPocket(target);
  const rage=bossDifficultyV2Profile(),useCharacter=state.stage===1;
  const decoded=useCharacter?decodeCharacterMask(1):null,mask=decoded?.mask;
  const cand=[];
  for(let y=2;y<GH-2;y++)for(let x=2;x<GW-2;x++){
    if(getCell(x,y)!==CLAIMED)continue;
    const k=idx(x,y),dx=x-target.x,dy=y-target.y;
    cand.push({x,y,k,d2:dx*dx+dy*dy,char:mask?.[k]?1:0});
  }
  cand.sort((a,b)=>a.d2-b.d2);
  const out=[];
  if(useCharacter&&mask){
    const goal=Math.max(1,Math.round((state.characterMaskTotal||decoded.source?.cells||1)*rage.reclaimPct/100));
    let charLoss=0;
    for(const p of cand){out.push({x:p.x,y:p.y});charLoss+=p.char;if(charLoss>=goal||out.length>=2200)break}
  }else{
    const total=(GW-4)*(GH-4),goal=Math.max(1,Math.round(total*rage.reclaimPct/100));
    for(const p of cand){out.push({x:p.x,y:p.y});if(out.length>=goal)break}
  }
  return out.length?out:stage1EmergencyPocket(target);
}
""",
'common rage profiles')

rep(Path('game.js'),
"function containmentPatternDelay(){return Math.max(1150,2800-state.stage*130)}",
"function containmentPatternDelay(){return Math.max(1100,2300-state.stage*110)}",
'containment pattern cadence')
rep(Path('game.js'),
"el.innerHTML='<b>RAGE</b><span>'+(remain/1000).toFixed(1)+'s</span><small>CHASE ×'+STAGE1_RAGE_V2.speedBoost.toFixed(2)+' · RETRAP = RAM</small>';",
"el.innerHTML='<b>RAGE</b><span>'+(remain/1000).toFixed(1)+'s</span><small>CHASE ×'+bossDifficultyV2Profile().speedBoost.toFixed(2)+' · RETRAP = RAM</small>';",
'rage HUD profile')
rep(Path('game.js'),
"state.containmentNextPatternAt=t+(state.stage===1&&!state.stage1EscapeUsed?900:700);",
"state.containmentNextPatternAt=t+(!state.stage1EscapeUsed?900:700);",
'common first-panic containment gate')

rep(Path('game.js'),
"""function stage1EmergencyTarget(e){
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
}
function stage1EmergencyPocket(target){
  if(!target)return[];
  const out=[];
  for(let dy=-3;dy<=3;dy++)for(let dx=-3;dx<=3;dx++){
    if(dx*dx+dy*dy>10)continue;
    const x=target.x+dx,y=target.y+dy;
    if(bossInteriorCell(x,y))out.push({x,y});
  }
  return out;
}
function stage1EmergencyEscape(m){
  if(state.stage!==1||state.stage1EscapeUsed||state.stage1EscapePending||m.kind!=='character'||m.value<80)return false;
  const boss=state.enemies.find(e=>e.isBoss);
  if(!boss||(!bossTightPocket(boss)&&!state.containmentActive))return false;
  const target=stage1EmergencyTarget(boss);
  if(!target)return false;
  state.stage1EscapeUsed=true;state.stage1EscapePending=true;state.containmentPendingMilestone=false;state.containmentHoldUntil=0;
  const t=now();
  boss.breakout={kind:'stage1_escape',reason:'first_capture',started:t,fireAt:t+820,target,ray:null};
  boss.vx*=.12;boss.vy*=.12;
  toast('PANIC! · BREAKOUT!',true,820);
  audio.beep(350,.08,'triangle',.03);audio.beep(520,.09,'triangle',.024);
  track('boss_pattern_start',{stage:1,kind:'stage1_escape',reason:'first_capture',character_area:Number(m.value.toFixed(2))});
  return true;
}
""",
"""function stage1EmergencyTarget(e){
  const useCharacter=state.stage===1,decoded=useCharacter?decodeCharacterMask(1):null,mask=decoded?.mask,bc=bossCellOf(e);
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
  const best=(useCharacter?pick(true):null)||pick(false);if(best)return best;
  for(let y=5;y<GH-5;y++)for(let x=5;x<GW-5;x++){
    const k=idx(x,y);
    if(getCell(x,y)===CLAIMED&&Math.abs(x-state.player.x)+Math.abs(y-state.player.y)>12&&(!useCharacter||!mask||mask[k]))return{x,y};
  }
  return null;
}
function stage1EmergencyPocket(target){
  if(!target)return[];
  const out=[];
  for(let dy=-3;dy<=3;dy++)for(let dx=-3;dx<=3;dx++){
    if(dx*dx+dy*dy>10)continue;
    const x=target.x+dx,y=target.y+dy;
    if(bossInteriorCell(x,y))out.push({x,y});
  }
  return out;
}
function stage1EmergencyEscape(m){
  if(state.stage1EscapeUsed||state.stage1EscapePending||m.value<80)return false;
  const boss=state.enemies.find(e=>e.isBoss);
  if(!boss||(!bossTightPocket(boss)&&!state.containmentActive))return false;
  const target=stage1EmergencyTarget(boss);
  if(!target)return false;
  state.stage1EscapeUsed=true;state.stage1EscapePending=true;state.containmentPendingMilestone=false;state.containmentHoldUntil=0;
  const t=now();
  boss.breakout={kind:'stage1_escape',reason:'first_capture',started:t,fireAt:t+820,target,ray:null};
  boss.vx*=.12;boss.vy*=.12;
  toast('PANIC! · BREAKOUT!',true,820);
  audio.beep(350,.08,'triangle',.03);audio.beep(520,.09,'triangle',.024);
  track('boss_pattern_start',{stage:state.stage,kind:'stage1_escape',reason:'first_capture',metric:m.kind,metric_value:Number(m.value.toFixed(2))});
  return true;
}
""",
'common panic escape')

rep(Path('game.js'),
"""const BALANCE_V1={
  1:{speed:1.00,chase:0.000,shotClock:1.00},
  2:{speed:0.98,chase:0.012,shotClock:0.86},
  3:{speed:0.97,chase:0.018,shotClock:0.84},
  4:{speed:1.07,chase:0.032,shotClock:0.98},
  5:{speed:0.99,chase:0.034,shotClock:0.82},
  6:{speed:1.00,chase:0.042,shotClock:0.87},
  7:{speed:1.02,chase:0.050,shotClock:0.90},
  8:{speed:1.03,chase:0.058,shotClock:0.92},
  9:{speed:1.04,chase:0.066,shotClock:0.92},
 10:{speed:1.05,chase:0.074,shotClock:0.92}
};
""",
"""const BALANCE_V1={
  1:{speed:1.00,chase:0.000,shotClock:1.00},
  2:{speed:1.00,chase:0.005,shotClock:1.00},
  3:{speed:1.00,chase:0.010,shotClock:1.00},
  4:{speed:1.00,chase:0.015,shotClock:1.00},
  5:{speed:1.00,chase:0.020,shotClock:1.00},
  6:{speed:1.00,chase:0.025,shotClock:1.00},
  7:{speed:1.00,chase:0.030,shotClock:1.00},
  8:{speed:1.00,chase:0.035,shotClock:1.00},
  9:{speed:1.00,chase:0.040,shotClock:1.00},
 10:{speed:1.00,chase:0.045,shotClock:1.00}
};
""",
'balance profile v2')

rep(Path('game.js'),
"""const BOSS_BREAKOUT_V1={
  1:{trap:1.85,cooldown:9.5,laser:0,destroy:0,teleport:false,siegeArea:999,siegeMs:999999},
  2:{trap:1.65,cooldown:8.7,laser:0,destroy:0,teleport:false,siegeArea:999,siegeMs:999999},
  3:{trap:1.55,cooldown:9.2,laser:2,destroy:0,teleport:false,siegeArea:999,siegeMs:999999},
  4:{trap:1.35,cooldown:8.4,laser:3,destroy:0,teleport:false,siegeArea:999,siegeMs:999999},
  5:{trap:1.30,cooldown:8.2,laser:3,destroy:5,teleport:false,siegeArea:55,siegeMs:19000},
  6:{trap:1.20,cooldown:7.6,laser:3,destroy:6,teleport:false,siegeArea:50,siegeMs:17000},
  7:{trap:1.10,cooldown:7.0,laser:4,destroy:7,teleport:false,siegeArea:45,siegeMs:15500},
  8:{trap:1.00,cooldown:6.8,laser:4,destroy:8,teleport:true,siegeArea:42,siegeMs:14500},
  9:{trap:.92,cooldown:6.2,laser:4,destroy:9,teleport:true,siegeArea:38,siegeMs:13000},
 10:{trap:.82,cooldown:5.8,laser:5,destroy:10,teleport:true,siegeArea:34,siegeMs:11500}
};
""",
"""const BOSS_BREAKOUT_V1={
  1:{trap:1.25,cooldown:7.8,laser:0,destroy:0, teleport:false,siegeArea:999,siegeMs:999999},
  2:{trap:1.20,cooldown:7.5,laser:0,destroy:0, teleport:false,siegeArea:999,siegeMs:999999},
  3:{trap:1.15,cooldown:7.2,laser:2,destroy:0, teleport:false,siegeArea:999,siegeMs:999999},
  4:{trap:1.10,cooldown:6.9,laser:3,destroy:0, teleport:false,siegeArea:999,siegeMs:999999},
  5:{trap:1.05,cooldown:6.6,laser:3,destroy:5, teleport:false,siegeArea:52, siegeMs:17000},
  6:{trap:1.00,cooldown:6.3,laser:3,destroy:6, teleport:false,siegeArea:48, siegeMs:15500},
  7:{trap:.92, cooldown:5.8,laser:4,destroy:7, teleport:false,siegeArea:43, siegeMs:13500},
  8:{trap:.84, cooldown:5.2,laser:4,destroy:8, teleport:true, siegeArea:39, siegeMs:12000},
  9:{trap:.76, cooldown:4.6,laser:5,destroy:10,teleport:true, siegeArea:35, siegeMs:10000},
 10:{trap:.68, cooldown:4.0,laser:6,destroy:12,teleport:true, siegeArea:31, siegeMs:8500}
};
""",
'breakout ramp v2')

rep(Path('game.js'),
"""  }else if(b.kind==='stage1_escape'){
    const target=b.target||stage1EmergencyTarget(e),oldX=e.x,oldY=e.y;
    if(target){
      const beforeRageChar=Number.isFinite(state.characterArea)?state.characterArea:null;
      affected=bossReopenCells(stage1RageReclaimCells(target),'escape',e);
      const charLost=beforeRageChar===null||!Number.isFinite(state.characterArea)?0:Math.max(0,beforeRageChar-state.characterArea);
      e.x=(target.x+.5)*CELL;e.y=(target.y+.5)*CELL;e.lastX=e.x;e.lastY=e.y;e.stuckFor=0;e.bounceHeat=0;
      const sp=(STAGES[1].speed||100)*1.15,ang=Math.atan2((state.player.y+.5)*CELL-e.y,(state.player.x+.5)*CELL-e.x)+Math.PI;
      e.vx=Math.cos(ang)*sp;e.vy=Math.sin(ang)*sp;
      const rageNow=now();state.stage1RageUntil=rageNow+STAGE1_RAGE_V2.durationMs;state.stage1RageRamReadyAt=rageNow+480;state.stage1RagePendingClear=false;
      toast('RAGE! · CHAR -'+charLost.toFixed(1)+'% · '+(STAGE1_RAGE_V2.durationMs/1000).toFixed(1)+'s',true,1350);
      track('stage1_rage_start',{stage:1,char_lost:Number(charLost.toFixed(2)),character_area:Number((state.characterArea||0).toFixed(2)),duration_ms:STAGE1_RAGE_V2.durationMs,speed_boost:STAGE1_RAGE_V2.speedBoost});
      juiceBurst(oldX,oldY,'#ffb24d',22,88,460);juiceRing(oldX,oldY,'#ffb24d',8,70,420,3);
      juiceBurst(e.x,e.y,'#ffd36a',26,94,500);juiceRing(e.x,e.y,'#ffd36a',8,76,460,3.4);juiceFlash('#ffb24d',.11,170);juiceShake(3.4,150);juiceHaptic([18,20,24]);
      audio.beep(280,.09,'sawtooth',.032);audio.beep(720,.11,'triangle',.026);
    }
    state.stage1EscapePending=false;
""",
"""  }else if(b.kind==='stage1_escape'){
    const target=b.target||stage1EmergencyTarget(e),oldX=e.x,oldY=e.y;
    if(target){
      const rage=bossDifficultyV2Profile(),beforeMetric=stageProgressMetric();
      affected=bossReopenCells(stage1RageReclaimCells(target),'escape',e);
      const afterMetric=stageProgressMetric(),metricLost=Math.max(0,beforeMetric.value-afterMetric.value);
      e.x=(target.x+.5)*CELL;e.y=(target.y+.5)*CELL;e.lastX=e.x;e.lastY=e.y;e.stuckFor=0;e.bounceHeat=0;
      const sp=(STAGES[state.stage].speed||100)*1.15,ang=Math.atan2((state.player.y+.5)*CELL-e.y,(state.player.x+.5)*CELL-e.x)+Math.PI;
      e.vx=Math.cos(ang)*sp;e.vy=Math.sin(ang)*sp;
      const rageNow=now();state.stage1RageUntil=rageNow+rage.durationMs;state.stage1RageRamReadyAt=rageNow+480;state.stage1RagePendingClear=false;
      toast('RAGE! · '+beforeMetric.label+' -'+metricLost.toFixed(1)+'% · '+(rage.durationMs/1000).toFixed(1)+'s',true,1350);
      track('boss_rage_start',{stage:state.stage,metric:beforeMetric.kind,metric_lost:Number(metricLost.toFixed(2)),duration_ms:rage.durationMs,speed_boost:rage.speedBoost});
      juiceBurst(oldX,oldY,'#ffb24d',22,88,460);juiceRing(oldX,oldY,'#ffb24d',8,70,420,3);
      juiceBurst(e.x,e.y,'#ffd36a',26,94,500);juiceRing(e.x,e.y,'#ffd36a',8,76,460,3.4);juiceFlash('#ffb24d',.11,170);juiceShake(3.4,150);juiceHaptic([18,20,24]);
      audio.beep(280,.09,'sawtooth',.032);audio.beep(720,.11,'triangle',.026);
    }
    state.stage1EscapePending=false;
""",
'common rage fire')

rep(Path('game.js'),
"""  if(stage1RageActive()&&bossTightPocket(e)&&t>=state.stage1RageRamReadyAt){
    state.stage1RageRamReadyAt=t+STAGE1_RAGE_V2.ramRetryMs;
    bossBeginPattern(e,'ram','stage1_rage_retrap');
    track('stage1_rage_retrap',{stage:1,remaining_ms:Math.max(0,Math.round(state.stage1RageUntil-t))});
    return true;
  }
""",
"""  if(stage1RageActive()&&bossTightPocket(e)&&t>=state.stage1RageRamReadyAt){
    const rage=bossDifficultyV2Profile();
    state.stage1RageRamReadyAt=t+rage.ramRetryMs;
    bossBeginPattern(e,'ram','boss_rage_retrap');
    track('boss_rage_retrap',{stage:state.stage,remaining_ms:Math.max(0,Math.round(state.stage1RageUntil-t))});
    return true;
  }
""",
'common rage retrap')
rep(Path('game.js'),
"if(state.containmentActive&&!(state.stage===1&&!state.stage1EscapeUsed)&&t>=Math.max(e.breakoutReadyAt||0,state.containmentNextPatternAt||0)){",
"if(state.containmentActive&&state.stage1EscapeUsed&&t>=Math.max(e.breakoutReadyAt||0,state.containmentNextPatternAt||0)){",
'common containment post-panic')

rep(Path('game.js'),
"""    const rageChase=e.isBoss&&stage1RageActive();
    const pressureBoost=rageChase?STAGE1_RAGE_V2.speedBoost:(e.isBoss&&state.containmentActive?CONTAINMENT_V1.speedBoost:1);
    const speed=e.speed*(slow ? 0.55 : 1)*bal.speed*drawingBossPressure*pressureBoost;
    const effectiveChase=rageChase
      ? STAGE1_RAGE_V2.chase
      : state.player.drawing
        ? Math.min(.24,(e.chase||0)+(e.isBoss?bal.chase:bal.chase*.55)+areaPressure*(e.isBoss?.028:.012))
        : (e.chase||0);
""",
"""    const rage=bossDifficultyV2Profile(),rageChase=e.isBoss&&stage1RageActive();
    const pressureBoost=rageChase?rage.speedBoost:(e.isBoss&&state.containmentActive?CONTAINMENT_V1.speedBoost:1);
    const speed=e.speed*(slow ? 0.55 : 1)*bal.speed*drawingBossPressure*pressureBoost;
    const effectiveChase=rageChase
      ? rage.chase
      : state.player.drawing
        ? Math.min(e.isBoss?rage.chaseCap:.24,(e.chase||0)+(e.isBoss?bal.chase:bal.chase*.55)+areaPressure*(e.isBoss?.028:.012))
        : (e.chase||0);
""",
'v2 chase caps and rage')

rep(Path('game.js'),
"function shoot(e){\n  const px=(state.player.x+.5)*CELL,py=(state.player.y+.5)*CELL,dx=px-e.x,dy=py-e.y,len=Math.hypot(dx,dy)||1,s=150+state.stage*8;state.projectiles.push({x:e.x,y:e.y,vx:dx/len*s,vy:dy/len*s,r:4});if(state.stage>=7&&Math.random()<.25){const ang=Math.atan2(dy,dx)+(.3*(Math.random()>.5?1:-1));state.projectiles.push({x:e.x,y:e.y,vx:Math.cos(ang)*s,vy:Math.sin(ang)*s,r:3})}\n}",
"function shoot(e){\n  const px=(state.player.x+.5)*CELL,py=(state.player.y+.5)*CELL,dx=px-e.x,dy=py-e.y,len=Math.hypot(dx,dy)||1,s=150+state.stage*8,rage=bossDifficultyV2Profile();state.projectiles.push({x:e.x,y:e.y,vx:dx/len*s,vy:dy/len*s,r:4});if(rage.multiShot>0&&Math.random()<rage.multiShot){const ang=Math.atan2(dy,dx)+(.3*(Math.random()>.5?1:-1));state.projectiles.push({x:e.x,y:e.y,vx:Math.cos(ang)*s,vy:Math.sin(ang)*s,r:3})}\n}",
'dynamic multishot')

rep(Path('game.js'),
"<p class=\"muted\">보스를 작은 영역에 가두면 <b>CONTAINMENT</b>가 발동합니다. Stage 1 첫 포획은 캐릭터 영역을 되찾고 3.5초 RAGE 추격을 시작합니다. Stage 3부터 레이저, Stage 5부터 영역 파괴, Stage 8부터 순간이동이 추가됩니다.</p><p class=\"muted\">Stage 1은 튜토리얼이라 보스가 탄을 쏘지 않습니다. Stage 2부터 적탄이 등장합니다.</p>",
"<p class=\"muted\">보스를 작은 영역에 가두면 <b>CONTAINMENT</b>가 발동합니다. 모든 Stage에서 첫 80% 포획 압박 시 PANIC BREAKOUT → 영역 재탈환 → RAGE 추격이 발동할 수 있습니다. Stage 3부터 레이저, Stage 5부터 영역 파괴, Stage 8부터 순간이동이 추가됩니다.</p><p class=\"muted\">본편 Stage 1부터 적탄과 졸개가 등장합니다. 별도 튜토리얼에서 조작을 먼저 익힐 수 있습니다.</p>",
'howto difficulty v2')

rep(Path('index.html'),'<div class="version">v0.12.4 service scenes HQ</div>','<div class="version">v0.13.0 difficulty v2</div>','version label')
rep(Path('config.js'),"VERSION: '0.12.4'","VERSION: '0.13.0'",'config version')
rep(Path('sw.js'),"cmh-core-v0.12.4","cmh-core-v0.13.0",'cache version')

print('v0.13.0 difficulty v2 applied')
