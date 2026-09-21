from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
js_path=root/'game.js'
css_path=root/'styles.css'
index_path=root/'index.html'
js=js_path.read_text(encoding='utf-8')

if 'v0.6.4 arcade readability refresh' in js:
    print('visual refresh already applied')
    raise SystemExit(0)

pattern=r"function drawWorld\(c\)\{.*?\n\}\n\nfunction renderMiniMap\(cam\)\{"
m=re.search(pattern,js,flags=re.S)
if not m:
    raise SystemExit('visual refresh patch failed: drawWorld block not found')

replacement=r'''// v0.6.4 arcade readability refresh — visual-only helpers.
function drawProjectileVisual(c,p){
  const a=Math.atan2(p.vy,p.vx),tail=10+p.r*1.4;
  c.save();
  c.globalCompositeOperation='lighter';
  c.strokeStyle='rgba(255,72,112,.42)';c.lineWidth=Math.max(2,p.r*.9);c.lineCap='round';
  c.beginPath();c.moveTo(p.x-Math.cos(a)*tail,p.y-Math.sin(a)*tail);c.lineTo(p.x,p.y);c.stroke();
  c.shadowBlur=18;c.shadowColor='#ff315d';c.fillStyle='#fff1f5';c.beginPath();c.arc(p.x,p.y,p.r+1.4,0,Math.PI*2);c.fill();
  c.fillStyle='#ff416b';c.beginPath();c.arc(p.x,p.y,Math.max(1.8,p.r*.58),0,Math.PI*2);c.fill();
  c.restore();
}
function drawEnemyVisual(c,e,t){
  const hue=e.isBoss?STAGES[state.stage].hue:'#ff6d83';
  c.save();c.translate(e.x,e.y);
  if(e.isBoss){
    const pulse=1+Math.sin(t*.006+state.stage)*.075,spin=t*.00045*(1+state.stage*.035);
    c.save();c.rotate(spin);c.globalAlpha=.36;c.strokeStyle=hue;c.lineWidth=2.2;c.shadowBlur=22;c.shadowColor=hue;
    c.beginPath();
    for(let k=0;k<16;k++){const a=k/16*Math.PI*2,r=e.r*(k%2?1.18:1.62)*pulse,xx=Math.cos(a)*r,yy=Math.sin(a)*r;k?c.lineTo(xx,yy):c.moveTo(xx,yy)}
    c.closePath();c.stroke();c.restore();
    c.shadowBlur=22;c.shadowColor=hue;c.fillStyle='rgba(8,3,14,.88)';c.strokeStyle='#fff';c.lineWidth=2.2;
    c.beginPath();c.arc(0,0,e.r*1.12,0,Math.PI*2);c.fill();c.stroke();
    c.fillStyle=hue;c.globalAlpha=.95;c.beginPath();c.arc(0,0,e.r*.72,0,Math.PI*2);c.fill();
    const vl=Math.hypot(e.vx,e.vy)||1,dx=e.vx/vl,dy=e.vy/vl,px=-dy,py=dx;
    c.fillStyle='#fff';c.shadowBlur=8;c.shadowColor='#fff';
    for(const s of [-1,1]){c.beginPath();c.arc(dx*2+px*s*3.2,dy*2+py*s*3.2,1.7,0,Math.PI*2);c.fill()}
    c.shadowBlur=0;c.globalAlpha=.82;c.fillStyle='#fff';c.font='900 8px system-ui';c.textAlign='center';c.textBaseline='bottom';c.fillText('BOSS',0,-e.r*1.65);
  }else{
    const spin=-t*.0012;c.rotate(spin);c.shadowBlur=14;c.shadowColor='#ff4769';c.fillStyle='#d92f55';c.strokeStyle='#ffd3dd';c.lineWidth=1.8;
    c.beginPath();for(let k=0;k<8;k++){const a=k/8*Math.PI*2,r=e.r*(k%2?0.55:1.12),xx=Math.cos(a)*r,yy=Math.sin(a)*r;k?c.lineTo(xx,yy):c.moveTo(xx,yy)}c.closePath();c.fill();c.stroke();
    c.fillStyle='#fff';c.beginPath();c.arc(0,0,1.8,0,Math.PI*2);c.fill();
  }
  c.restore();
}
function drawPlayerVisual(c,p,t){
  const px=(p.x+.5)*CELL,py=(p.y+.5)*CELL;
  const retract=p.autoRetract,draw=p.drawing&&!retract;
  const col=retract?'#ffd45d':draw?'#ff4fa3':'#42e6ff';
  const pulse=1+Math.sin(t*.012)*.10;
  c.save();c.translate(px,py);
  c.globalCompositeOperation='lighter';c.globalAlpha=.28;c.fillStyle=col;c.beginPath();c.arc(0,0,13*pulse,0,Math.PI*2);c.fill();
  c.globalCompositeOperation='source-over';c.globalAlpha=.72;c.strokeStyle=col;c.lineWidth=2;c.beginPath();c.arc(0,0,10.5*pulse,0,Math.PI*2);c.stroke();
  if(input.dash&&direction()&&!p.autoRetract){
    const vec={up:[0,-1],down:[0,1],left:[-1,0],right:[1,0]}[direction()]||[0,0];
    c.strokeStyle='rgba(110,231,255,.75)';c.lineWidth=2;c.lineCap='round';
    for(let i=-1;i<=1;i++){c.beginPath();c.moveTo(-vec[0]*(13+i*2)+vec[1]*i*3,-vec[1]*(13+i*2)-vec[0]*i*3);c.lineTo(-vec[0]*(23+i*2)+vec[1]*i*3,-vec[1]*(23+i*2)-vec[0]*i*3);c.stroke()}
  }
  c.rotate(Math.PI/4+t*.0014);
  c.shadowBlur=18;c.shadowColor=col;c.fillStyle='#fff';c.strokeStyle=col;c.lineWidth=2.5;c.beginPath();c.rect(-5.2,-5.2,10.4,10.4);c.fill();c.stroke();
  c.rotate(-Math.PI/4-t*.0014);
  c.fillStyle=col;c.beginPath();c.arc(0,0,2.5,0,Math.PI*2);c.fill();
  if(state.shield){c.strokeStyle='#ffe36c';c.lineWidth=2;c.shadowColor='#ffe36c';c.beginPath();c.arc(0,0,15,0,Math.PI*2);c.stroke()}
  c.restore();
}
function drawWorld(c){
  const t=performance.now();
  c.fillStyle='#000';c.fillRect(0,0,W,H);if(state.currentImage)c.drawImage(state.currentImage,0,0,W,H);c.drawImage(fogCanvas,0,0);c.drawImage(safeCanvas,0,0);
  c.save();const pulse=.78+.22*Math.sin(t*.014);c.shadowBlur=16;c.shadowColor='#ff2790';
  for(let y=0;y<GH;y++)for(let x=0;x<GW;x++)if(getCell(x,y)===TRAIL){
    c.fillStyle=`rgba(255,54,151,${.72+.18*pulse})`;c.fillRect(x*CELL+.5,y*CELL+.5,CELL-1,CELL-1);
    c.fillStyle='rgba(255,238,248,.92)';c.fillRect(x*CELL+2.5,y*CELL+2.5,CELL-5,CELL-5);
  }c.restore();
  for(const it of state.items){const x=(it.x+.5)*CELL,y=(it.y+.5)*CELL;c.save();c.shadowBlur=15;c.shadowColor='#ffe36e';c.fillStyle='rgba(10,6,20,.86)';c.beginPath();c.arc(x,y,11.5,0,Math.PI*2);c.fill();c.strokeStyle='#ffe36e';c.lineWidth=1.8;c.stroke();c.fillStyle='#fff';c.font='bold 12px system-ui';c.textAlign='center';c.textBaseline='middle';c.fillText(it.type==='speed'?'⚡':it.type==='stop'?'❄':it.type==='bomb'?'✹':'◆',x,y);c.restore()}
  for(const p of state.projectiles)drawProjectileVisual(c,p);
  state.enemies.forEach(e=>drawEnemyVisual(c,e,t));
  drawPlayerVisual(c,state.player,t);
}

function renderMiniMap(cam){'''
js=js[:m.start()]+replacement+js[m.end():]

old="""function updateHUD(){
  $('#stageLabel').textContent=`${state.stage} · ${STAGES[state.stage]?.name||''}`;$('#scoreLabel').textContent=fmtScore(state.score);$('#areaLabel').textContent=`${state.area.toFixed(1)}%`;$('#timeLabel').textContent=Math.max(0,Math.ceil(state.timeLeft));$('#lifeLabel').textContent='♥'.repeat(Math.max(0,state.lives))+(state.shield?` ◆${state.shield}`:'');$('#progressBar').style.width=`${Math.min(100,state.area)}%`;const sb=$('#staminaBar');if(sb)sb.style.width=`${clamp(state.dashStamina,0,100)}%`;const sl=$('#staminaLabel');if(sl)sl.textContent=state.dashExhausted?'RECOVER':'DASH';updateMusicLabel();
}"""
new="""function updateHUD(){
  $('#stageLabel').textContent=`${state.stage} · ${STAGES[state.stage]?.name||''}`;$('#scoreLabel').textContent=fmtScore(state.score);$('#areaLabel').textContent=`${state.area.toFixed(1)}%`;$('#timeLabel').textContent=Math.max(0,Math.ceil(state.timeLeft));$('#lifeLabel').textContent='♥'.repeat(Math.max(0,state.lives))+(state.shield?` ◆${state.shield}`:'');$('#progressBar').style.width=`${Math.min(100,state.area)}%`;const sb=$('#staminaBar');if(sb)sb.style.width=`${clamp(state.dashStamina,0,100)}%`;const sl=$('#staminaLabel');if(sl)sl.textContent=state.dashExhausted?'RECOVER':'DASH';
  const hue=STAGES[state.stage]?.hue||'#ff4da0';document.documentElement.style.setProperty('--stage-hue',hue);gameScreen.classList.toggle('hud-clear',state.area>=80);gameScreen.classList.toggle('hud-bonus',state.area>=90);gameScreen.classList.toggle('hud-perfect',state.area>=99);gameScreen.classList.toggle('hud-time-danger',state.timeLeft<25);updateMusicLabel();
}"""
if old not in js:
    raise SystemExit('visual refresh patch failed: updateHUD block not found')
js=js.replace(old,new,1)
js=js.replace("'use strict';","'use strict';\n// v0.6.4 arcade readability refresh",1)
js_path.write_text(js,encoding='utf-8')

index=index_path.read_text(encoding='utf-8')
index=index.replace('<span class="threshold t80">80</span><span class="threshold t90">90</span><span class="threshold t100">100</span>',
                    '<span class="threshold t80"><b>80</b><em>CLEAR</em></span><span class="threshold t90"><b>90</b><em>BONUS</em></span><span class="threshold t100"><b>99</b><em>PERFECT</em></span>',1)
for oldver in ('v0.6.1 adsense verify','v0.6.0 mobile beta','v0.5.8 mobile beta'):
    if oldver in index:
        index=index.replace(oldver,'v0.6.4 visual refresh',1);break
index_path.write_text(index,encoding='utf-8')

css=css_path.read_text(encoding='utf-8')
css += r'''

/* v0.6.4 arcade readability refresh */
:root{--stage-hue:#ff4da0}
.game-screen{background:radial-gradient(circle at 50% -10%,color-mix(in srgb,var(--stage-hue) 22%,#21102d),#08050f 62%)}
.game-frame{border:1px solid color-mix(in srgb,var(--stage-hue) 46%,rgba(255,255,255,.2));box-shadow:0 22px 76px rgba(0,0,0,.62),0 0 34px color-mix(in srgb,var(--stage-hue) 18%,transparent),inset 0 0 0 1px rgba(255,255,255,.04)}
.game-topbar{position:relative;padding:5px 7px;border:1px solid rgba(255,255,255,.1);border-radius:18px;background:linear-gradient(180deg,rgba(17,8,26,.88),rgba(9,5,16,.72));box-shadow:0 8px 30px rgba(0,0,0,.24),inset 0 1px rgba(255,255,255,.07)}
.game-topbar:before{content:"";position:absolute;left:18px;right:18px;bottom:0;height:1px;background:linear-gradient(90deg,transparent,var(--stage-hue),transparent);opacity:.55}
.stat{border-color:rgba(255,255,255,.1);background:linear-gradient(180deg,rgba(255,255,255,.055),rgba(255,255,255,.018));box-shadow:none}
.stat small{color:#bfaec8;font-weight:800}.stat strong{font-variant-numeric:tabular-nums;text-shadow:0 0 12px rgba(255,255,255,.06)}
.game-topbar .stat:nth-child(1) strong{color:#ffd7ec}.game-topbar .stat:nth-child(3){border-color:color-mix(in srgb,var(--stage-hue) 34%,rgba(255,255,255,.1));background:color-mix(in srgb,var(--stage-hue) 9%,rgba(15,7,25,.72))}.game-topbar .stat:nth-child(3) strong{color:#fff;text-shadow:0 0 14px var(--stage-hue)}
.game-screen.hud-time-danger .game-topbar .stat:nth-child(4){border-color:rgba(255,65,88,.55);animation:cmhHudPulse .8s ease-in-out infinite alternate}.game-screen.hud-time-danger #timeLabel{color:#ff8b9b}
.game-screen.hud-bonus .game-topbar .stat:nth-child(3){box-shadow:0 0 18px color-mix(in srgb,var(--stage-hue) 24%,transparent)}
.game-bottombar{padding:5px 8px;border:1px solid rgba(255,255,255,.08);border-radius:14px;background:rgba(12,6,20,.62);backdrop-filter:blur(7px)}
.progress-wrap{height:10px;background:rgba(255,255,255,.08);border-color:rgba(255,255,255,.12)}
.progress-bar{background:linear-gradient(90deg,#35e3ff 0%,var(--stage-hue) 72%,#ffd764 100%);box-shadow:0 0 16px color-mix(in srgb,var(--stage-hue) 42%,transparent)}
.threshold{top:-24px;transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;line-height:.86;color:#cdbed3;pointer-events:none}.threshold b{font-size:.5rem}.threshold em{font-size:.39rem;font-style:normal;font-weight:900;letter-spacing:.08em;opacity:.78}.t100{right:auto;left:99%}.game-screen.hud-clear .t80,.game-screen.hud-bonus .t90,.game-screen.hud-perfect .t100{color:#fff;text-shadow:0 0 8px var(--stage-hue)}
.stamina-box{padding:4px 7px;border-radius:10px;background:rgba(255,255,255,.035)}
.stamina-track{background:rgba(255,255,255,.08);height:7px}.stamina-bar{background:linear-gradient(90deg,#46f0ff,#8a6cff,var(--stage-hue))}
.mini-map{border:1px solid color-mix(in srgb,var(--stage-hue) 45%,rgba(255,255,255,.2))!important;border-radius:11px!important;box-shadow:0 8px 24px rgba(0,0,0,.32),0 0 18px color-mix(in srgb,var(--stage-hue) 18%,transparent)!important}
.icon-btn{border-color:rgba(255,255,255,.13);background:rgba(255,255,255,.045)}
@keyframes cmhHudPulse{from{box-shadow:0 0 0 rgba(255,65,88,0)}to{box-shadow:0 0 16px rgba(255,65,88,.34)}}
@media(max-width:800px),(pointer:coarse){.game-topbar{padding:2px 3px;border-radius:12px}.game-bottombar{padding:2px 6px}.threshold{top:-20px}.threshold em{display:none}}
@media(pointer:coarse) and (orientation:landscape),(orientation:landscape) and (max-height:650px){.game-topbar{background:rgba(10,5,18,.58)!important}.game-bottombar{background:rgba(10,5,18,.58)!important}.threshold{top:-14px}.threshold b{font-size:.38rem}.threshold em{display:none}}
'''
css_path.write_text(css,encoding='utf-8')
print('v0.6.4 arcade readability refresh applied')
