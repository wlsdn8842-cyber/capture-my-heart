from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path,old,new,label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'stage1 emergency escape patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

rep(Path('game.js'),
"  enemies:[], projectiles:[], items:[], area:0, lastArea:0, characterArea:null, characterMaskTotal:0, clearMilestone:0,",
"  enemies:[], projectiles:[], items:[], area:0, lastArea:0, characterArea:null, characterMaskTotal:0, clearMilestone:0, stage1EscapeUsed:false, stage1EscapePending:false,",
'state fields')

rep(Path('game.js'),
"initGrid();spawnEnemies();state.projectiles=[];state.items=[];state.clearMilestone=0;",
"initGrid();spawnEnemies();state.projectiles=[];state.items=[];state.clearMilestone=0;state.stage1EscapeUsed=false;state.stage1EscapePending=false;",
'stage reset')

anchor="""function checkMilestone(){
  if(tutorial.active)return;
  const m=stageProgressMetric(),a=m.value;
  const perfectTarget=m.kind==='character'?100:99;
"""
insert="""function stage1EmergencyTarget(e){
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
  if(!boss||!bossTightPocket(boss))return false;
  const target=stage1EmergencyTarget(boss);
  if(!target)return false;
  state.stage1EscapeUsed=true;state.stage1EscapePending=true;
  const t=now();
  boss.breakout={kind:'stage1_escape',reason:'first_capture',started:t,fireAt:t+820,target,ray:null};
  boss.vx*=.12;boss.vy*=.12;
  toast('PANIC! · BREAKOUT!',true,820);
  audio.beep(350,.08,'triangle',.03);audio.beep(520,.09,'triangle',.024);
  track('boss_pattern_start',{stage:1,kind:'stage1_escape',reason:'first_capture',character_area:Number(m.value.toFixed(2))});
  return true;
}
function checkMilestone(){
  if(tutorial.active)return;
  const m=stageProgressMetric(),a=m.value;
  if(stage1EmergencyEscape(m))return;
  const perfectTarget=m.kind==='character'?100:99;
"""
rep(Path('game.js'),anchor,insert,'milestone emergency hook')

old="""  }else if(b.kind==='teleport'){
    const target=b.target||bossTeleportTarget(e),oldX=e.x,oldY=e.y;
    juiceBurst(oldX,oldY,'#b56cff',18,72,430);juiceRing(oldX,oldY,'#b56cff',8,58,390,2.8);
    e.x=(target.x+.5)*CELL;e.y=(target.y+.5)*CELL;e.lastX=e.x;e.lastY=e.y;e.stuckFor=0;e.bounceHeat=0;
    juiceBurst(e.x,e.y,'#e5a6ff',24,88,480);juiceRing(e.x,e.y,'#e5a6ff',8,70,430,3.2);juiceFlash('#9b4dff',.08,150);juiceShake(2.4,120);juiceHaptic([12,22,12]);
    audio.beep(920,.08,'sine',.028);audio.beep(1380,.10,'sine',.025);
  }
"""
new="""  }else if(b.kind==='stage1_escape'){
    const target=b.target||stage1EmergencyTarget(e),oldX=e.x,oldY=e.y;
    if(target){
      affected=bossReopenCells(stage1EmergencyPocket(target),'escape',e);
      e.x=(target.x+.5)*CELL;e.y=(target.y+.5)*CELL;e.lastX=e.x;e.lastY=e.y;e.stuckFor=0;e.bounceHeat=0;
      const sp=(STAGES[1].speed||100)*1.15,ang=Math.atan2((state.player.y+.5)*CELL-e.y,(state.player.x+.5)*CELL-e.x)+Math.PI;
      e.vx=Math.cos(ang)*sp;e.vy=Math.sin(ang)*sp;
      juiceBurst(oldX,oldY,'#ffb24d',22,88,460);juiceRing(oldX,oldY,'#ffb24d',8,70,420,3);
      juiceBurst(e.x,e.y,'#ffd36a',26,94,500);juiceRing(e.x,e.y,'#ffd36a',8,76,460,3.4);juiceFlash('#ffb24d',.11,170);juiceShake(3.4,150);juiceHaptic([18,20,24]);
      audio.beep(280,.09,'sawtooth',.032);audio.beep(720,.11,'triangle',.026);
    }
    state.stage1EscapePending=false;
  }else if(b.kind==='teleport'){
    const target=b.target||bossTeleportTarget(e),oldX=e.x,oldY=e.y;
    juiceBurst(oldX,oldY,'#b56cff',18,72,430);juiceRing(oldX,oldY,'#b56cff',8,58,390,2.8);
    e.x=(target.x+.5)*CELL;e.y=(target.y+.5)*CELL;e.lastX=e.x;e.lastY=e.y;e.stuckFor=0;e.bounceHeat=0;
    juiceBurst(e.x,e.y,'#e5a6ff',24,88,480);juiceRing(e.x,e.y,'#e5a6ff',8,70,430,3.2);juiceFlash('#9b4dff',.08,150);juiceShake(2.4,120);juiceHaptic([12,22,12]);
    audio.beep(920,.08,'sine',.028);audio.beep(1380,.10,'sine',.025);
  }
"""
rep(Path('game.js'),old,new,'emergency fire branch')

rep(Path('game.js'),
"  const col=kind==='laser'?'#ff405f':'#ff57c9';",
"  const col=kind==='laser'?'#ff405f':kind==='escape'?'#ffb24d':'#ff57c9';",
'emergency color')

rep(Path('game.js'),
"  toast(`${kind==='laser'?'LASER BREAK':'BOSS BREAK'} · -${lost.toFixed(1)}%`,true,1150);",
"  toast(`${kind==='laser'?'LASER BREAK':kind==='escape'?'EMERGENCY BREAK':'BOSS BREAK'} · -${lost.toFixed(1)}%`,true,1150);",
'emergency toast')

rep(Path('game.js'),
"  }else if(b.kind==='teleport'&&target){",
"  }else if((b.kind==='teleport'||b.kind==='stage1_escape')&&target){",'emergency telegraph visual')

rep(Path('game.js'),
"  const label=b.kind==='laser'?'LASER':b.kind==='smash'?'BREAK':b.kind==='teleport'?'WARP':'ESCAPE';",
"  const label=b.kind==='laser'?'LASER':b.kind==='smash'?'BREAK':b.kind==='teleport'?'WARP':b.kind==='stage1_escape'?'PANIC':'ESCAPE';",'emergency telegraph label')

rep(Path('game.js'),
"<small>${state.stage===1?'판정 저용':'판정 미적용'} · ${state.characterMaskTotal} cells</small>",
"<small>${state.stage===1?'판정 적용':'판정 미적용'} · ${state.characterMaskTotal} cells</small>",
'debug typo')

rep(Path('index.html'),
'<div class="version">v0.11.1 stage1 char gate</div>',
'<div class="version">v0.11.2 stage1 escape</div>',
'version label')

print('v0.11.2 Stage 1 emergency escape applied')
