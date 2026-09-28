from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path,old,new,label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'juice v1 patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

marker="function maybeSpawnItem(){if(state.items.length>=2||Math.random()>.34)return;"
juice=r'''// v0.9.1 JUICE V1 — lightweight feedback layer.
const JUICE_V1={
  particles:[],rings:[],flashes:[],
  shakeUntil:0,shakeAmp:0,shakeSeed:0
};
function juiceReducedMotion(){return !!window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches}
function juiceNow(){return performance.now()}
function juiceShake(amount=2,duration=110){
  if(juiceReducedMotion())amount*=.2;
  const t=juiceNow();
  JUICE_V1.shakeAmp=Math.max(JUICE_V1.shakeAmp,amount);
  JUICE_V1.shakeUntil=Math.max(JUICE_V1.shakeUntil,t+duration);
  JUICE_V1.shakeSeed++;
}
function juiceShakeOffset(t=juiceNow()){
  if(t>=JUICE_V1.shakeUntil){JUICE_V1.shakeAmp=0;return{x:0,y:0}}
  const left=Math.max(0,(JUICE_V1.shakeUntil-t)/180);
  const amp=JUICE_V1.shakeAmp*Math.min(1,.25+left);
  return{x:(Math.random()*2-1)*amp,y:(Math.random()*2-1)*amp}
}
function juiceBurst(x,y,color,count=14,power=62,duration=430){
  if(juiceReducedMotion())count=Math.max(4,Math.round(count*.35));
  const t=juiceNow();
  for(let i=0;i<count;i++){
    const a=Math.random()*Math.PI*2,s=power*(.45+Math.random()*.8);
    JUICE_V1.particles.push({
      x,y,vx:Math.cos(a)*s,vy:Math.sin(a)*s,
      born:t,duration:duration*(.78+Math.random()*.45),
      size:1.8+Math.random()*2.8,color,gravity:18+Math.random()*24
    });
  }
}
function juiceRing(x,y,color,r0=8,r1=46,duration=360,width=2.5){
  JUICE_V1.rings.push({x,y,color,r0,r1,born:juiceNow(),duration,width});
}
function juiceFlash(color,alpha=.12,duration=160){
  JUICE_V1.flashes.push({color,alpha,born:juiceNow(),duration});
}
function juiceHaptic(pattern){
  if(juiceReducedMotion())return;
  try{if(window.matchMedia?.('(pointer: coarse)')?.matches)navigator.vibrate?.(pattern)}catch(_){}
}
function juiceTone(freq,dur=.07,type='sine',gain=.025,delay=0){
  if(delay)setTimeout(()=>audio.beep(freq,dur,type,gain),delay);
  else audio.beep(freq,dur,type,gain);
}
function drawJuiceWorld(c,t){
  JUICE_V1.particles=JUICE_V1.particles.filter(p=>t-p.born<p.duration);
  JUICE_V1.rings=JUICE_V1.rings.filter(r=>t-r.born<r.duration);
  JUICE_V1.flashes=JUICE_V1.flashes.filter(f=>t-f.born<f.duration);

  c.save();
  c.globalCompositeOperation='lighter';
  for(const p of JUICE_V1.particles){
    const age=(t-p.born)/1000,k=Math.min(1,(t-p.born)/p.duration),fade=1-k;
    const x=p.x+p.vx*age,y=p.y+p.vy*age+.5*p.gravity*age*age;
    c.globalAlpha=.9*fade;c.shadowBlur=10;c.shadowColor=p.color;c.fillStyle=p.color;
    c.beginPath();c.arc(x,y,p.size*(.65+fade*.5),0,Math.PI*2);c.fill();
  }
  for(const r of JUICE_V1.rings){
    const k=Math.min(1,(t-r.born)/r.duration),ease=1-Math.pow(1-k,3);
    c.globalAlpha=.76*(1-k);c.shadowBlur=14;c.shadowColor=r.color;c.strokeStyle=r.color;c.lineWidth=r.width*(1-k*.45);
    c.beginPath();c.arc(r.x,r.y,r.r0+(r.r1-r.r0)*ease,0,Math.PI*2);c.stroke();
  }
  c.restore();

  for(const f of JUICE_V1.flashes){
    const k=Math.min(1,(t-f.born)/f.duration);
    c.save();c.globalAlpha=f.alpha*(1-k);c.fillStyle=f.color;c.fillRect(0,0,W,H);c.restore();
  }
}
function juicePlayerXY(){
  const p=state.player||{x:GW/2,y:GH/2};
  return{x:(p.x+.5)*CELL,y:(p.y+.5)*CELL}
}
function juiceItemPickup(type,it){
  const pos=it?{x:(it.x+.5)*CELL,y:(it.y+.5)*CELL}:juicePlayerXY();
  const meta=type==='speed'
    ?{color:'#47e9ff',count:18,power:72,shake:1.5,flash:.07,haptic:12}
    :type==='stop'
      ?{color:'#7cbcff',count:20,power:54,shake:1.4,flash:.09,haptic:16}
      :type==='bomb'
        ?{color:'#ff8a45',count:26,power:92,shake:4.2,flash:.16,haptic:[24,18,32]}
        :{color:'#ffe36e',count:22,power:66,shake:2.0,flash:.10,haptic:[10,16,10]};
  juiceBurst(pos.x,pos.y,meta.color,meta.count,meta.power,type==='bomb'?520:430);
  juiceRing(pos.x,pos.y,meta.color,7,type==='bomb'?72:50,type==='bomb'?430:340,type==='bomb'?3.4:2.5);
  if(type==='shield')juiceRing(pos.x,pos.y,'#fff6b0',14,64,520,1.8);
  juiceFlash(meta.color,meta.flash,type==='bomb'?210:150);
  juiceShake(meta.shake,type==='bomb'?170:105);
  juiceHaptic(meta.haptic);
  if(type==='speed'){
    juiceTone(720,.055,'sine',.025);juiceTone(980,.06,'sine',.028,45);juiceTone(1260,.075,'sine',.03,90);
  }else if(type==='stop'){
    juiceTone(540,.075,'triangle',.025);juiceTone(340,.11,'sine',.026,45);
  }else if(type==='bomb'){
    juiceTone(170,.10,'sawtooth',.042);juiceTone(420,.08,'triangle',.032,55);juiceTone(720,.055,'square',.022,105);
  }else{
    juiceTone(820,.07,'sine',.025);juiceTone(1180,.09,'sine',.03,55);juiceTone(1540,.10,'sine',.026,110);
  }
  track('item_pickup',{type,stage:state.stage});
}
function juiceCaptureFX(delta,before,after){
  const p=juicePlayerXY(),big=delta>=8,huge=delta>=15;
  const color=huge?'#ffd868':big?'#ff62b1':'#55eaff';
  juiceBurst(p.x,p.y,color,huge?24:big?16:8,huge?92:big?72:48,huge?520:380);
  juiceRing(p.x,p.y,color,6,huge?70:big?52:34,huge?480:320,huge?3:2);
  if(big){juiceShake(huge?3.5:2.0,huge?150:100);juiceFlash(color,huge?.10:.055,130)}
  if(huge){juiceTone(650,.05,'triangle',.022);juiceTone(940,.07,'sine',.026,50)}
  else if(big)juiceTone(720,.055,'sine',.022);

  const milestones=[
    {v:80,color:'#55eaff',label:'CLEAR',shake:2.4},
    {v:90,color:'#ff5caf',label:'BONUS',shake:3.0},
    {v:99,color:'#ffd85f',label:'PERFECT',shake:4.0}
  ];
  for(const m of milestones){
    if(before<m.v&&after>=m.v){
      juiceBurst(W*.5,H*.5,m.color,m.v===99?34:26,m.v===99?110:86,620);
      juiceRing(W*.5,H*.5,m.color,24,m.v===99?170:132,650,3.5);
      juiceFlash(m.color,m.v===99?.15:.10,230);
      juiceShake(m.shake,m.v===99?190:140);
      juiceHaptic(m.v===99?[18,20,28]:[12,18,12]);
      juiceTone(m.v===80?660:m.v===90?880:1040,.08,'sine',.03);
      juiceTone(m.v===80?880:m.v===90?1160:1420,.10,'sine',.028,65);
      track('juice_milestone',{milestone:m.v,stage:state.stage});
    }
  }
}
function juiceMissFX(reason){
  const p=juicePlayerXY();
  juiceBurst(p.x,p.y,'#ff3f68',18,84,430);
  juiceRing(p.x,p.y,'#ff5577',7,58,340,3);
  juiceFlash('#ff204e',.14,190);juiceShake(5.2,190);juiceHaptic([28,20,24]);
}
function juiceShieldBlockFX(){
  const p=juicePlayerXY();
  juiceBurst(p.x,p.y,'#ffe36e',18,72,420);
  juiceRing(p.x,p.y,'#ffe36e',10,64,390,3);
  juiceRing(p.x,p.y,'#fff8c9',20,78,520,1.5);
  juiceFlash('#ffe36e',.08,150);juiceShake(1.8,95);juiceHaptic([9,14,9]);
  juiceTone(920,.06,'sine',.025);juiceTone(1320,.09,'sine',.025,55);
}

function maybeSpawnItem(){if(state.items.length>=2||Math.random()>.34)return;'''
rep(Path('game.js'),marker,juice,'juice engine insert')

old_collect="function collectCapturedItems(){\n  const left=[];for(const it of state.items){if(getCell(it.x,it.y)===CLAIMED)applyItem(it.type);else left.push(it)}state.items=left;\n}"
new_collect="function collectCapturedItems(){\n  const left=[];for(const it of state.items){if(getCell(it.x,it.y)===CLAIMED)applyItem(it.type,it);else left.push(it)}state.items=left;\n}"
rep(Path('game.js'),old_collect,new_collect,'collect item coords')

old_apply="function applyItem(type){const t=now();if(type==='speed'){state.speedBoostUntil=t+9000;toast('⚡ SPEED UP 9s')}if(type==='stop'){state.freezeUntil=t+5500;toast('❄ BOSS STOP 5.5s')}if(type==='bomb'){state.projectiles=[];state.slowUntil=t+7500;toast('💣 BOMB · 적탄 제거 + SLOW')}if(type==='shield'){state.shield=Math.min(2,state.shield+1);toast('◆ SHIELD +1')}audio.beep(1120,.12,'sine',.04)}"
new_apply="function applyItem(type,it=null){const t=now();if(type==='speed'){state.speedBoostUntil=t+9000;toast('⚡ SPEED UP · 9s')}if(type==='stop'){state.freezeUntil=t+5500;toast('❄ BOSS STOP · 5.5s')}if(type==='bomb'){state.projectiles=[];state.slowUntil=t+7500;toast('✹ SLOW BURST · 적탄 제거 + 7.5s')}if(type==='shield'){state.shield=Math.min(2,state.shield+1);toast('◆ SHIELD +1')}juiceItemPickup(type,it)}"
rep(Path('game.js'),old_apply,new_apply,'item pickup fx')

capture_line="  const delta=Math.max(0,state.area-before), points=Math.round(gained*(10+state.stage*2)*(1+Math.min(.8,delta/35)));\n"
capture_new=capture_line+"  juiceCaptureFX(delta,before,state.area);\n"
rep(Path('game.js'),capture_line,capture_new,'capture juice hook')

old_shield="  if(state.shield>0){state.shield--;clearTrail();toast(`◆ SHIELD! ${reason}`,true);audio.beep(260,.14,'sawtooth',.04);return}"
new_shield="  if(state.shield>0){state.shield--;juiceShieldBlockFX();clearTrail();toast(`◆ SHIELD! ${reason}`,true);audio.beep(260,.14,'sawtooth',.04);return}"
rep(Path('game.js'),old_shield,new_shield,'shield block fx')

old_miss="  state.lives--;clearTrail();state.projectiles=[];audio.beep(150,.25,'sawtooth',.05);toast(`MISS · ${reason}`,true,1800);updateHUD();track('life_lost',{stage:state.stage,reason_lives:state.lives});"
new_miss="  state.lives--;juiceMissFX(reason);clearTrail();state.projectiles=[];audio.beep(150,.25,'sawtooth',.05);toast(`MISS · ${reason}`,true,1800);updateHUD();track('life_lost',{stage:state.stage,reason,lives:state.lives});"
rep(Path('game.js'),old_miss,new_miss,'miss fx')

old_world_start="function drawWorld(c){\n  const t=performance.now();"
new_world_start="function drawWorld(c){\n  const t=performance.now(),shake=juiceShakeOffset(t);c.save();c.translate(shake.x,shake.y);"
rep(Path('game.js'),old_world_start,new_world_start,'world shake start')

old_world_end="  state.enemies.forEach(e=>drawEnemyVisual(c,e,t));\n  drawPlayerVisual(c,state.player,t);\n}\n\nfunction renderMiniMap(cam){"
new_world_end="  state.enemies.forEach(e=>drawEnemyVisual(c,e,t));\n  drawPlayerVisual(c,state.player,t);\n  drawJuiceWorld(c,t);c.restore();\n}\n\nfunction renderMiniMap(cam){"
rep(Path('game.js'),old_world_end,new_world_end,'world juice render')

rep(Path('index.html'),'<div class=\"version\">v0.9.0 balance v1</div>','<div class=\"version\">v0.9.1 juice v1</div>','version label')

print('v0.9.1 juice v1 applied')
