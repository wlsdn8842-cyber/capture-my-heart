from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path,old,new,label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'boss patterns patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

# Insert boss pattern engine before updateEnemies.
marker="function updateEnemies(dt){\n"
engine=r'''// v0.10.0 BOSS BREAKOUT SYSTEM — telegraphed counterplay when the boss is boxed in.
const BOSS_BREAKOUT_V1={
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
function bossBreakoutCfg(){return BOSS_BREAKOUT_V1[state.stage]||BOSS_BREAKOUT_V1[10]}
function bossInteriorCell(x,y){return x>1&&y>1&&x<GW-2&&y<GH-2}
function bossPlayerSafeCell(x,y){return Math.abs(x-state.player.x)+Math.abs(y-state.player.y)>2}
function bossCellOf(e){return cellAtPixel(e.x,e.y)}
function bossNearestWallRay(e,maxScan=14){
  const c=bossCellOf(e),dirs=[{dx:1,dy:0},{dx:-1,dy:0},{dx:0,dy:1},{dx:0,dy:-1}];
  let best=null;
  for(const d of dirs){
    let first=0;
    for(let s=1;s<=maxScan;s++){
      const x=c.x+d.dx*s,y=c.y+d.dy*s;
      if(!bossInteriorCell(x,y))break;
      const cell=getCell(x,y);
      if(cell===CLAIMED){first=s;break}
      if(cell===TRAIL)break;
    }
    if(first&&(!best||first<best.first))best={...d,first};
  }
  return best;
}
function bossTightPocket(e){
  const c=bossCellOf(e),dirs=[[1,0],[-1,0],[0,1],[0,-1]];let closeWalls=0,sum=0;
  for(const [dx,dy] of dirs){
    let free=0;
    for(let s=1;s<=6;s++){
      const x=c.x+dx*s,y=c.y+dy*s;
      if(!inGrid(x,y)||getCell(x,y)===CLAIMED||getCell(x,y)===TRAIL)break;
      free++;
    }
    sum+=free;if(free<=2)closeWalls++;
  }
  return closeWalls>=3||sum<=6;
}
function bossReopenCells(cells,kind,e){
  const before=state.area,seen=new Set();let opened=0,cx=0,cy=0;
  for(const p of cells){
    if(!p||!bossInteriorCell(p.x,p.y)||!bossPlayerSafeCell(p.x,p.y))continue;
    const k=p.y*GW+p.x;if(seen.has(k))continue;seen.add(k);
    if(getCell(p.x,p.y)!==CLAIMED)continue;
    setCell(p.x,p.y,UNCLAIMED);opened++;cx+=(p.x+.5)*CELL;cy+=(p.y+.5)*CELL;
  }
  if(!opened)return 0;
  rebuildVisualLayers();state.lastArea=before;state.area=calcArea();updateHUD();
  const lost=Math.max(0,before-state.area);
  cx/=opened;cy/=opened;
  const col=kind==='laser'?'#ff405f':'#ff57c9';
  juiceBurst(cx,cy,col,Math.min(30,10+opened*2),kind==='laser'?84:96,520);
  juiceRing(cx,cy,col,10,kind==='laser'?72:92,480,3.2);
  juiceFlash(col,kind==='laser'?.08:.11,180);juiceShake(kind==='laser'?2.8:4.0,150);
  audio.beep(kind==='laser'?270:190,.10,kind==='laser'?'square':'sawtooth',.035);
  track('boss_territory_break',{stage:state.stage,kind,cells:opened,area_lost:Number(lost.toFixed(2))});
  toast(`${kind==='laser'?'LASER BREAK':'BOSS BREAK'} · -${lost.toFixed(1)}%`,true,1150);
  return opened;
}
function bossLaserCells(e,ray,count){
  if(!ray)return[];const c=bossCellOf(e),out=[];
  for(let s=ray.first;s<ray.first+count+2;s++){
    const x=c.x+ray.dx*s,y=c.y+ray.dy*s;
    if(!bossInteriorCell(x,y))break;
    if(getCell(x,y)===CLAIMED)out.push({x,y});
    else if(out.length)break;
    if(out.length>=count)break;
  }
  return out;
}
function bossSmashCells(e,count){
  const ray=bossNearestWallRay(e,12);if(!ray)return[];
  const c=bossCellOf(e),wx=c.x+ray.dx*ray.first,wy=c.y+ray.dy*ray.first;
  const cand=[];
  for(let r=0;r<=3;r++)for(let dy=-r;dy<=r;dy++)for(let dx=-r;dx<=r;dx++){
    if(Math.abs(dx)+Math.abs(dy)!==r)continue;
    const x=wx+dx,y=wy+dy;
    if(bossInteriorCell(x,y)&&bossPlayerSafeCell(x,y)&&getCell(x,y)===CLAIMED)cand.push({x,y});
  }
  return cand.slice(0,count);
}
function bossTeleportTarget(e){
  const from=bossCellOf(e);let best=null;
  for(let i=0;i<360;i++){
    const x=3+Math.floor(Math.random()*(GW-6)),y=3+Math.floor(Math.random()*(GH-6));
    if(getCell(x,y)!==UNCLAIMED)continue;
    const pd=Math.abs(x-state.player.x)+Math.abs(y-state.player.y),bd=Math.abs(x-from.x)+Math.abs(y-from.y);
    if(pd<12||bd<14)continue;
    best={x,y};break;
  }
  return best||randomUnclaimedCell(14);
}
function bossPatternName(e,cfg,reason){
  e.breakoutSeq=(e.breakoutSeq||0)+1;
  if(reason==='siege'&&cfg.destroy)return 'smash';
  if(state.stage<=2)return 'ram';
  if(state.stage<=4)return 'laser';
  if(state.stage<=7)return e.breakoutSeq%2?'laser':'smash';
  const seq=['laser','smash','teleport'];return seq[(e.breakoutSeq-1)%seq.length];
}
function bossBeginPattern(e,kind,reason='trapped'){
  const t=now(),cfg=bossBreakoutCfg(),ray=bossNearestWallRay(e,14);
  if(kind==='laser'&&!ray)kind=cfg.teleport?'teleport':'ram';
  if(kind==='smash'&&!ray)kind=cfg.teleport?'teleport':'ram';
  let target=null;
  if(kind==='teleport')target=bossTeleportTarget(e);
  if((kind==='laser'||kind==='ram'||kind==='smash')&&ray){
    const c=bossCellOf(e),s=ray.first+(kind==='laser'?Math.max(2,cfg.laser):1);
    target={x:clamp(c.x+ray.dx*s,2,GW-3),y:clamp(c.y+ray.dy*s,2,GH-3)};
  }
  const telegraph=kind==='teleport'?900:kind==='smash'?1050:kind==='laser'?900:720;
  e.breakout={kind,reason,started:t,fireAt:t+telegraph,target,ray};
  e.vx*=.18;e.vy*=.18;
  const msg=kind==='teleport'?'WARP!':kind==='smash'?'TERRITORY BREAK!':kind==='laser'?'LASER BREAKOUT!':'BREAKOUT!';
  toast(msg,true,telegraph);
  audio.beep(kind==='teleport'?620:kind==='laser'?420:kind==='smash'?240:330,.08,'triangle',.028);
  track('boss_pattern_start',{stage:state.stage,kind,reason});
}
function bossFirePattern(e){
  const b=e.breakout,cfg=bossBreakoutCfg();if(!b)return;
  const c=bossCellOf(e);let affected=0;
  if(b.kind==='ram'){
    const ray=b.ray||bossNearestWallRay(e,14),dx=ray?.dx||Math.sign(W/2-e.x),dy=ray?.dy||Math.sign(H/2-e.y);
    const sp=(STAGES[state.stage].speed||100)*1.75;e.vx=dx*sp;e.vy=dy*sp;e.ramUntil=now()+1150;
    juiceRing(e.x,e.y,'#ffb24d',8,60,360,3);juiceShake(1.7,90);juiceHaptic(12);
  }else if(b.kind==='laser'){
    affected=bossReopenCells(bossLaserCells(e,b.ray,cfg.laser),'laser',e);
    juiceHaptic([14,18,20]);
  }else if(b.kind==='smash'){
    affected=bossReopenCells(bossSmashCells(e,cfg.destroy),'smash',e);
    juiceHaptic([22,18,28]);
  }else if(b.kind==='teleport'){
    const target=b.target||bossTeleportTarget(e),oldX=e.x,oldY=e.y;
    juiceBurst(oldX,oldY,'#b56cff',18,72,430);juiceRing(oldX,oldY,'#b56cff',8,58,390,2.8);
    e.x=(target.x+.5)*CELL;e.y=(target.y+.5)*CELL;e.lastX=e.x;e.lastY=e.y;e.stuckFor=0;e.bounceHeat=0;
    juiceBurst(e.x,e.y,'#e5a6ff',24,88,480);juiceRing(e.x,e.y,'#e5a6ff',8,70,430,3.2);juiceFlash('#9b4dff',.08,150);juiceShake(2.4,120);juiceHaptic([12,22,12]);
    audio.beep(920,.08,'sine',.028);audio.beep(1380,.10,'sine',.025);
  }
  track('boss_pattern_fire',{stage:state.stage,kind:b.kind,reason:b.reason,affected});
  e.breakout=null;e.trapTime=0;e.bounceHeat=0;e.breakoutReadyAt=now()+cfg.cooldown*1000;
  e.nextSiegeAt=now()+cfg.siegeMs*(.85+Math.random()*.3);
}
function bossUpdatePattern(e,dt){
  if(!e.isBoss)return false;
  const t=now(),cfg=bossBreakoutCfg();
  if(e.breakout){
    if(t>=e.breakout.fireAt)bossFirePattern(e);
    else return true;
  }
  e.breakoutReadyAt=e.breakoutReadyAt||t+3500;
  e.nextSiegeAt=e.nextSiegeAt||t+cfg.siegeMs;
  e.bounceHeat=Math.max(0,(e.bounceHeat||0)-dt*.75);
  const tight=bossTightPocket(e)||(e.bounceHeat||0)>=4.5||(e.stuckFor||0)>.9;
  e.trapTime=tight?(e.trapTime||0)+dt:Math.max(0,(e.trapTime||0)-dt*.65);
  if(t>=e.breakoutReadyAt&&e.trapTime>=cfg.trap){
    bossBeginPattern(e,bossPatternName(e,cfg,'trapped'),'trapped');return true;
  }
  if(cfg.destroy&&state.area>=cfg.siegeArea&&t>=e.nextSiegeAt&&t>=e.breakoutReadyAt){
    bossBeginPattern(e,'smash','siege');return true;
  }
  return false;
}
function drawBossPatternVisual(c,e,t){
  const b=e.breakout;if(!e.isBoss||!b)return;
  const remain=Math.max(0,b.fireAt-t),pulse=.55+.45*Math.sin(t*.028),target=b.target?{x:(b.target.x+.5)*CELL,y:(b.target.y+.5)*CELL}:null;
  c.save();c.globalCompositeOperation='lighter';c.lineCap='round';
  if(b.kind==='laser'&&target){
    c.strokeStyle=`rgba(255,55,85,${.38+.35*pulse})`;c.lineWidth=2+pulse*2;c.setLineDash([8,7]);c.beginPath();c.moveTo(e.x,e.y);c.lineTo(target.x,target.y);c.stroke();c.setLineDash([]);
    c.fillStyle='#ff6682';c.shadowBlur=16;c.shadowColor='#ff315d';c.beginPath();c.arc(target.x,target.y,5+3*pulse,0,Math.PI*2);c.fill();
  }else if(b.kind==='smash'&&target){
    c.strokeStyle=`rgba(255,70,190,${.45+.3*pulse})`;c.lineWidth=3;c.shadowBlur=18;c.shadowColor='#ff46c5';c.beginPath();c.arc(target.x,target.y,24+9*pulse,0,Math.PI*2);c.stroke();
  }else if(b.kind==='teleport'&&target){
    c.strokeStyle=`rgba(190,105,255,${.42+.36*pulse})`;c.lineWidth=3;c.shadowBlur=18;c.shadowColor='#b55cff';
    for(const [x,y] of [[e.x,e.y],[target.x,target.y]]){c.beginPath();c.arc(x,y,16+10*pulse,0,Math.PI*2);c.stroke()}
  }else{
    c.strokeStyle=`rgba(255,178,77,${.45+.35*pulse})`;c.lineWidth=3;c.shadowBlur=16;c.shadowColor='#ffad42';c.beginPath();c.arc(e.x,e.y,18+8*pulse,0,Math.PI*2);c.stroke();
  }
  c.restore();
  c.save();c.fillStyle='#fff';c.font='900 9px system-ui';c.textAlign='center';c.textBaseline='bottom';c.shadowBlur=8;c.shadowColor='#000';
  const label=b.kind==='laser'?'LASER':b.kind==='smash'?'BREAK':b.kind==='teleport'?'WARP':'ESCAPE';c.fillText(`${label} ${(remain/1000).toFixed(1)}`,e.x,e.y-25);c.restore();
}

function updateEnemies(dt){
'''
rep(Path('game.js'),marker,engine,'engine insert')

# Hook pattern update and bounce heat into the current balanced enemy loop.
old="  for(const e of state.enemies){\n    const drawingBossPressure=e.isBoss&&state.player.drawing"
new="  for(const e of state.enemies){\n    if(e.isBoss&&bossUpdatePattern(e,dt))continue;\n    const drawingBossPressure=e.isBoss&&state.player.drawing"
rep(Path('game.js'),old,new,'pattern update hook')

old="    if(bounced){const vl=Math.hypot(e.vx,e.vy)||1;e.vx=e.vx/vl*speed;e.vy=e.vy/vl*speed}\n"
new="    if(bounced){if(e.isBoss)e.bounceHeat=(e.bounceHeat||0)+1.25;const vl=Math.hypot(e.vx,e.vy)||1;e.vx=e.vx/vl*speed;e.vy=e.vy/vl*speed}\n"
rep(Path('game.js'),old,new,'bounce heat hook')

# Add telegraphs above boss but below player, so attacks are readable.
old="  state.enemies.forEach(e=>drawEnemyVisual(c,e,t));\n  drawPlayerVisual(c,state.player,t);\n"
new="  state.enemies.forEach(e=>drawEnemyVisual(c,e,t));\n  state.enemies.forEach(e=>drawBossPatternVisual(c,e,t));\n  drawPlayerVisual(c,state.player,t);\n"
rep(Path('game.js'),old,new,'pattern visual hook')

# Explain stage pattern progression in HOW TO PLAY. Sound hint from v0.9.0 is the stable anchor.
old='<p class="muted">⚙ SETTINGS에서 BGM/SFX 음량과 Mute를 조절할 수 있습니다.</p><p class="muted">Stage 1은 튜토리얼이라 보스가 탄을 쏘지 않습니다. Stage 2부터 적탄이 등장합니다.</p>'
new='<p class="muted">⚙ SETTINGS에서 BGM/SFX 음량과 Mute를 조절할 수 있습니다.</p><p class="muted">보스를 좁은 곳에 가두면 BREAKOUT 패턴이 발동합니다. Stage 3부터 레이저, Stage 5부터 영역 파괴, Stage 8부터 순간이동이 추가됩니다.</p><p class="muted">Stage 1은 튜토리얼이라 보스가 탄을 쏘지 않습니다. Stage 2부터 적탄이 등장합니다.</p>'
rep(Path('game.js'),old,new,'howto breakout hint')

rep(Path('index.html'),'<div class="version">v0.9.1 juice v1</div>','<div class="version">v0.10.0 boss breakout</div>','version label')

print('v0.10.0 boss breakout system applied')
