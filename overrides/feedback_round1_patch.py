from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path, old, new, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'feedback round1 patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

rep(Path('game.js'),
'''function showTitle(){
  if(mobileUXActive())resetMobileCaptureLock('title');
  state.mode='title';state.paused=false;audio.setDanger(false);gameScreen.classList.add('hidden');titleScreen.classList.remove('hidden');closeModal();refreshTitle();audio.playTitle();track('title_view',{});
}''',
'''function showTitle(){
  clearEndingAutoReturn();
  if(mobileUXActive())resetMobileCaptureLock('title');
  state.mode='title';state.paused=false;audio.setDanger(false);gameScreen.classList.add('hidden');titleScreen.classList.remove('hidden');closeModal();refreshTitle();audio.playTitle();track('title_view',{});
}''',
'clear ending timer on title')

old_ending='''function showEnding(){
  state.mode='ending';state.paused=true;unlockStage(10);saveGlobal({bestScore:Math.max(globalData().bestScore||0,state.score)});track('game_complete',{score:state.score});
  openModal(`<h2 class="ending-title">♥ ALL STAGES CLEAR ♥</h2><img class="ending-art" src="assets/images/stage10.webp" alt="Final Queen"><p style="text-align:center;font-size:1.2rem">FINAL SCORE <b>${fmtScore(state.score)}</b></p><div class="row"><button id="endingFeedback" class="btn tertiary">💬 FEEDBACK</button><button id="endingGallery" class="btn secondary">GALLERY</button><button id="endingTitle" class="btn primary">TITLE</button></div>`);
  $('#endingFeedback').onclick=()=>window.CMH_FEEDBACK?.show?.('game_complete');$('#endingGallery').onclick=showGallery;$('#endingTitle').onclick=showTitle;
}'''
new_ending='''let endingAutoTimer=null,endingAutoLeft=0;
function clearEndingAutoReturn(){
  if(endingAutoTimer){clearInterval(endingAutoTimer);endingAutoTimer=null}
}
function armEndingAutoReturn(seconds=12){
  clearEndingAutoReturn();endingAutoLeft=seconds;
  const render=()=>{
    const btn=$('#endingTitle'),hint=$('#endingAutoHint');
    if(btn)btn.textContent=`TITLE · ${endingAutoLeft}s`;
    if(hint)hint.textContent=`${endingAutoLeft}초 후 타이틀 화면으로 자동 이동합니다.`;
  };
  render();
  endingAutoTimer=setInterval(()=>{
    endingAutoLeft--;
    if(endingAutoLeft<=0){
      clearEndingAutoReturn();
      track('ending_auto_title',{score:state.score});
      showTitle();
      return;
    }
    render();
  },1000);
}
function showEnding(){
  clearEndingAutoReturn();
  state.mode='ending';state.paused=true;unlockStage(10);saveGlobal({bestScore:Math.max(globalData().bestScore||0,state.score)});track('game_complete',{score:state.score});
  openModal(`<h2 class="ending-title">♥ ALL STAGES CLEAR ♥</h2><img class="ending-art" src="assets/images/stage10.webp" alt="Final Queen"><p style="text-align:center;font-size:1.2rem">FINAL SCORE <b>${fmtScore(state.score)}</b></p><p id="endingAutoHint" class="ending-auto-hint">12초 후 타이틀 화면으로 자동 이동합니다.</p><div class="row ending-actions"><button id="endingFeedback" class="btn tertiary">💬 FEEDBACK</button><button id="endingGallery" class="btn secondary">GALLERY</button><button id="endingTitle" class="btn primary">TITLE · 12s</button></div>`);
  $('#endingFeedback').onclick=()=>{clearEndingAutoReturn();window.CMH_FEEDBACK?.show?.('game_complete')};
  $('#endingGallery').onclick=()=>{clearEndingAutoReturn();showGallery()};
  $('#endingTitle').onclick=()=>{clearEndingAutoReturn();showTitle()};
  armEndingAutoReturn(12);
}'''
rep(Path('game.js'),old_ending,new_ending,'ending auto return')

old_gallery='''function showGallery(){
  const unlocked=new Set(globalData().unlockedStages||[]);
  const cards=[];for(let i=1;i<=10;i++){const ok=unlocked.has(i);cards.push(`<div class="gallery-card ${ok?'':'locked'}" data-stage="${i}"><img src="${stageSrc(i)}" alt="Stage ${i}">${ok?'':'<div class="lock">🔒</div>'}<div class="caption">Stage ${i} · ${STAGES[i].name}</div></div>`)}
  openModal(`<h2>♡ GALLERY</h2><p class="muted">80% 이상 클리어한 스테이지가 해금됩니다.</p><div class="gallery-grid">${cards.join('')}</div><div style="margin-top:14px"><button id="galleryClose" class="btn primary">CLOSE</button></div>`);
  modalLayer.querySelectorAll('.gallery-card:not(.locked)').forEach(c=>c.onclick=()=>{const i=Number(c.dataset.stage);openModal(`<h2>Stage ${i} · ${STAGES[i].name}</h2><img class="ending-art" src="${stageSrc(i)}" alt="stage art"><div style="margin-top:12px"><button id="artBack" class="btn primary">BACK</button></div>`);$('#artBack').onclick=showGallery});
  $('#galleryClose').onclick=closeModal;
}'''
new_gallery='''function showGallery(){
  const unlocked=new Set(globalData().unlockedStages||[]);
  const cards=[];
  for(let i=1;i<=10;i++){
    const ok=unlocked.has(i);
    cards.push(`<button class="gallery-card ${ok?'':'locked'}" data-stage="${i}" type="button" ${ok?'':'disabled'}><img src="${stageSrc(i)}" alt="Stage ${i}">${ok?'':'<div class="lock">🔒</div>'}<div class="caption"><strong>Stage ${i} · ${STAGES[i].name}</strong>${ok?'<span>클릭해서 크게 보기</span>':''}</div></button>`);
  }
  openModal(`<div class="gallery-head"><div><h2>♡ GALLERY</h2><p class="muted">80% 이상 클리어한 스테이지가 해금됩니다. 이미지를 누르면 전체 화면으로 확대됩니다.</p></div><button id="galleryClose" class="btn primary">CLOSE</button></div><div class="gallery-grid">${cards.join('')}</div>`,'gallery-modal-card');
  modalLayer.querySelectorAll('.gallery-card:not(.locked)').forEach(c=>c.onclick=()=>{
    const i=Number(c.dataset.stage);
    track('gallery_art_open',{stage:i});
    showPhotoZoom(stageSrc(i),`Stage ${i} · ${STAGES[i].name}`);
  });
  $('#galleryClose').onclick=closeModal;
}'''
rep(Path('game.js'),old_gallery,new_gallery,'gallery enlargement')

old_items="""  for(const it of state.items){const x=(it.x+.5)*CELL,y=(it.y+.5)*CELL;c.save();c.shadowBlur=15;c.shadowColor='#ffe36e';c.fillStyle='rgba(10,6,20,.86)';c.beginPath();c.arc(x,y,11.5,0,Math.PI*2);c.fill();c.strokeStyle='#ffe36e';c.lineWidth=1.8;c.stroke();c.fillStyle='#fff';c.font='bold 12px system-ui';c.textAlign='center';c.textBaseline='middle';c.fillText(it.type==='speed'?'⚡':it.type==='stop'?'❄':it.type==='bomb'?'✹':'◆',x,y);c.restore()}"""
new_items="""  for(const it of state.items){
    const x=(it.x+.5)*CELL,y=(it.y+.5)*CELL;
    const meta=it.type==='speed'
      ?{icon:'⚡',label:'SPD',color:'#47e9ff'}
      :it.type==='stop'
        ?{icon:'❄',label:'STOP',color:'#7cbcff'}
        :it.type==='bomb'
          ?{icon:'✹',label:'SLOW',color:'#ff8a45'}
          :{icon:'◆',label:'SHIELD',color:'#ffe36e'};
    c.save();
    c.shadowBlur=18;c.shadowColor=meta.color;
    c.fillStyle='rgba(8,5,18,.9)';c.beginPath();c.arc(x,y,13,0,Math.PI*2);c.fill();
    c.strokeStyle=meta.color;c.lineWidth=2.3;c.stroke();
    c.fillStyle='#fff';c.font='bold 12px system-ui';c.textAlign='center';c.textBaseline='middle';c.fillText(meta.icon,x,y-1);
    const labelY=y+18,labelW=meta.label.length>4?36:30;
    c.shadowBlur=8;c.fillStyle='rgba(4,3,10,.88)';c.strokeStyle=meta.color;c.lineWidth=1;
    c.beginPath();c.roundRect(x-labelW/2,labelY-5,labelW,10,5);c.fill();c.stroke();
    c.shadowBlur=0;c.fillStyle=meta.color;c.font='900 7px system-ui';c.textBaseline='middle';c.fillText(meta.label,x,labelY);
    c.restore();
  }"""
rep(Path('game.js'),old_items,new_items,'item visual distinction')

rep(Path('index.html'),'<div class="version">v0.7.2 interactive tutorial</div>','<div class="version">v0.8.3 feedback UX</div>','version label')

css_path=root/'styles.css'
css=css_path.read_text(encoding='utf-8')
marker='/* v0.8.3 feedback round1 UX */'
if marker not in css:
    css += r'''

/* v0.8.3 feedback round1 UX */
.modal-card.gallery-modal-card{width:min(1180px,97vw);max-height:94vh;padding:18px}
.gallery-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-bottom:12px}
.gallery-head h2{margin-bottom:4px}
.gallery-head p{margin:0}
.gallery-grid{grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}
.gallery-card{appearance:none;color:#fff;text-align:left;padding:0;cursor:zoom-in;box-shadow:0 10px 28px rgba(0,0,0,.28);transition:transform .14s ease,border-color .14s ease,box-shadow .14s ease}
.gallery-card:not(.locked):hover{transform:translateY(-2px);border-color:rgba(255,105,181,.5);box-shadow:0 14px 34px rgba(0,0,0,.38),0 0 22px rgba(255,70,160,.12)}
.gallery-card img{object-fit:contain;background:#050208}
.gallery-card .caption{display:flex;align-items:flex-end;justify-content:space-between;gap:8px;padding:26px 10px 9px}
.gallery-card .caption strong{font-size:.78rem}.gallery-card .caption span{font-size:.6rem;color:#ffb9da;white-space:nowrap}
.gallery-card.locked{cursor:not-allowed;opacity:.7}
.ending-auto-hint{text-align:center;color:#cfbdd3;font-size:.75rem;margin:8px 0 12px}
@media(max-width:760px){
  .modal-card.gallery-modal-card{width:98vw;padding:10px}
  .gallery-head{align-items:center}.gallery-head p{font-size:.7rem}
  .gallery-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
  .gallery-card .caption{padding:22px 7px 7px}.gallery-card .caption span{display:none}
}
@media(max-width:460px){
  .gallery-grid{grid-template-columns:1fr}
  .gallery-head{position:sticky;top:-10px;z-index:3;padding:8px 0;background:linear-gradient(#1e0b2b 78%,transparent)}
  .gallery-card .caption strong{font-size:.82rem}
  .ending-actions{flex-direction:column}
}
'''
    css_path.write_text(css,encoding='utf-8')

print('v0.8.3 feedback round1 UX applied')
