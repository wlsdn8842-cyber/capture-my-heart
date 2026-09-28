from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path,old,new,label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'balance v1 patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

old_update=r'''function updateEnemies(dt){
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
}'''

new_update=r'''// v0.9.0 balance v1 — less projectile spam, more readable boss pressure.
const BALANCE_V1={
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
function balanceV1Profile(){return BALANCE_V1[state.stage]||BALANCE_V1[10]}
function updateEnemies(dt){
  const cfg=STAGES[state.stage], frozen=now()<state.freezeUntil, slow=now()<state.slowUntil;
  if(frozen)return;
  const bal=balanceV1Profile();
  const areaPressure=Math.max(0,Math.min(1,(state.area-35)/60));
  for(const e of state.enemies){
    const drawingBossPressure=e.isBoss&&state.player.drawing
      ? (1+Math.min(.22,(state.stage-1)*.012+areaPressure*.11))
      : 1;
    const speed=e.speed*(slow ? 0.55 : 1)*bal.speed*drawingBossPressure;
    const effectiveChase=state.player.drawing
      ? Math.min(.24,(e.chase||0)+(e.isBoss?bal.chase:bal.chase*.55)+areaPressure*(e.isBoss?.028:.012))
      : (e.chase||0);
    if(state.player.drawing&&effectiveChase>0){
      const tx=(state.player.x+.5)*CELL,ty=(state.player.y+.5)*CELL,dx=tx-e.x,dy=ty-e.y,len=Math.hypot(dx,dy)||1;
      const tvx=dx/len*speed,tvy=dy/len*speed;
      e.vx=e.vx*(1-effectiveChase)+tvx*effectiveChase;
      e.vy=e.vy*(1-effectiveChase)+tvy*effectiveChase;
      const vl=Math.hypot(e.vx,e.vy)||1;e.vx=e.vx/vl*speed;e.vy=e.vy/vl*speed
    }
    let nx=e.x+e.vx*dt,ny=e.y+e.vy*dt,bounced=false;
    let c=cellAtPixel(nx,e.y),cell=getCell(c.x,c.y);
    if(cell===TRAIL){failLife('보스가 라인을 끊었습니다');return}
    if(cell===CLAIMED){e.vx*=-1;e.vy+=(Math.random()-.5)*speed*.28;bounced=true;nx=e.x+e.vx*dt}
    c=cellAtPixel(e.x,ny);cell=getCell(c.x,c.y);
    if(cell===TRAIL){failLife('보스가 라인을 끊었습니다');return}
    if(cell===CLAIMED){e.vy*=-1;e.vx+=(Math.random()-.5)*speed*.28;bounced=true;ny=e.y+e.vy*dt}
    if(bounced){const vl=Math.hypot(e.vx,e.vy)||1;e.vx=e.vx/vl*speed;e.vy=e.vy/vl*speed}
    e.x=clamp(nx,CELL*2.5,W-CELL*2.5);e.y=clamp(ny,CELL*2.5,H-CELL*2.5);
    const moved=dist(e.x,e.y,e.lastX??e.x,e.lastY??e.y);e.stuckFor=moved<.35?(e.stuckFor||0)+dt:0;e.lastX=e.x;e.lastY=e.y;
    if(e.stuckFor>1.15){
      const cx=W/2-e.x,cy=H/2-e.y,base=Math.atan2(cy,cx)+(Math.random()-.5)*.8;
      e.vx=Math.cos(base)*speed;e.vy=Math.sin(base)*speed;e.stuckFor=0
    }
    if(state.player.drawing&&dist(e.x,e.y,(state.player.x+.5)*CELL,(state.player.y+.5)*CELL)<e.r+8){failLife('보스 충돌');return}
    if(e.isBoss&&cfg.shots){
      e.shotTimer-=dt*1000*bal.shotClock;
      if(e.shotTimer<=0){e.shotTimer=cfg.shots*(.8+Math.random()*.45);shoot(e)}
    }
  }
}'''

rep(Path('game.js'),old_update,new_update,'enemy balance block')

old_shoot="if(state.stage>=7&&Math.random()<.32){const ang=Math.atan2(dy,dx)+(.3*(Math.random()>.5?1:-1));state.projectiles.push({x:e.x,y:e.y,vx:Math.cos(ang)*s,vy:Math.sin(ang)*s,r:3})}"
new_shoot="if(state.stage>=7&&Math.random()<.25){const ang=Math.atan2(dy,dx)+(.3*(Math.random()>.5?1:-1));state.projectiles.push({x:e.x,y:e.y,vx:Math.cos(ang)*s,vy:Math.sin(ang)*s,r:3})}"
rep(Path('game.js'),old_shoot,new_shoot,'late multishot smoothing')

old_hint='<p class="muted">Stage 1은 튜토리얼이라 보스가 탄을 쏘지 않습니다. Stage 2부터 적탄이 등장합니다.</p>'
new_hint='<p class="muted">⚙ SETTINGS에서 BGM/SFX 음량과 Mute를 조절할 수 있습니다.</p><p class="muted">Stage 1은 튜토리얼이라 보스가 탄을 쏘지 않습니다. Stage 2부터 적탄이 등장합니다.</p>'
rep(Path('game.js'),old_hint,new_hint,'sound settings discoverability')

rep(Path('index.html'),'<div class="version">v0.8.3 feedback UX</div>','<div class="version">v0.9.0 balance v1</div>','version label')

print('v0.9.0 balance v1 applied')
