from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path,old,new,label):
 p=root/path;s=p.read_text(encoding='utf-8')
 if old not in s: raise SystemExit('tutorial patch failed: '+label)
 p.write_text(s.replace(old,new,1),encoding='utf-8')

# state + persistence
m="const SETTINGS_KEY = 'cmh.settings';\n"
block="""const TUTORIAL_V2_KEY='cmh.tutorial.v2.status';
const tutorial={active:false,replay:false,step:'move',startedAt:0,moveCells:0,lastX:null,lastY:null,lastArea:0,prevAuto:false,retractArmed:false,retractStarted:false,done:new Set()};
function tutorialStatus(){try{return localStorage.getItem(TUTORIAL_V2_KEY)||''}catch(_){return ''}}
function tutorialRequired(){
  const s=tutorialStatus();if(s==='complete'||s==='skipped')return false;
  try{if(localStorage.getItem('cmh.tutorial')==='1'){tutorialPersist('complete');return false}}catch(_){}
  return true
}
function tutorialPersist(v){try{localStorage.setItem(TUTORIAL_V2_KEY,v)}catch(_){}}
function tutorialCoarse(){return !!window.matchMedia?.('(pointer: coarse)')?.matches}
"""
rep(Path('game.js'),m,m+block,'state')

# NEW GAME flow
old="state.slot=s;state.stage=1;state.score=0;state.lives=3;state.continueCredits=1;loadUnlocked();saveToSlot(s);track('game_start',{slot:s});closeModal();startStage(1,false);"
new="state.slot=s;state.stage=1;state.score=0;state.lives=3;state.continueCredits=1;loadUnlocked();saveToSlot(s);track('game_start',{slot:s});closeModal();if(tutorialRequired())startInteractiveTutorial(false);else startStage(1,false);"
rep(Path('game.js'),old,new,'new game route')

# replay from HOW TO PLAY
old="  </div><button id=\"howClose\" class=\"btn primary\">OK</button>`);$('#howClose').onclick=closeModal;\n}"
new="  </div><div class=\"row\" style=\"margin-top:14px\"><button id=\"tutorialReplayBtn\" class=\"btn secondary\">PLAY TUTORIAL AGAIN</button><button id=\"howClose\" class=\"btn primary\">OK</button></div>`);$('#tutorialReplayBtn').onclick=()=>{closeModal();startInteractiveTutorial(true)};$('#howClose').onclick=closeModal;\n}"
rep(Path('game.js'),old,new,'howto replay')

# legacy popup never interrupts Stage 1 anymore
old="  if(state.stage===1&&!state.tutorialShown){state.paused=true;$('#tutorialOverlay').classList.remove('hidden')}\n"
rep(Path('game.js'),old,"  // Interactive tutorial v2 runs before Stage 1.\n",'legacy popup')

# milestone and LIFE protections
rep(Path('game.js'),"function checkMilestone(){\n","function checkMilestone(){\n  if(tutorial.active)return;\n",'milestone guard')
rep(Path('game.js'),"function failLife(reason='MISS'){\n  if(state.mode!=='playing'||state.paused)return;\n","function failLife(reason='MISS'){\n  if(state.mode!=='playing'||state.paused)return;\n  if(tutorial.active){clearTrail();state.projectiles=[];tutorialTryAgain(reason);return}\n",'life guard')
rep(Path('game.js'),"function showPause(){\n  if(state.mode!=='playing')return;state.paused=true;\n","function showPause(){\n  if(tutorial.active){toast('튜토리얼에서는 저장/일시정지를 사용하지 않습니다.');return}\n  if(state.mode!=='playing')return;state.paused=true;\n",'pause guard')

# tutorial tick after regular movement; no enemies/projectiles exist and time is held at 999.
needle="    if(!state.paused){updateEnemies(dt);updateProjectiles(dt);state.timerAcc+=dt;if(state.timerAcc>=.1){state.timeLeft-=state.timerAcc;state.timerAcc=0;if(state.timeLeft<=0){state.timeLeft=STAGES[state.stage].timer;failLife('TIME UP')}}const danger=dangerCheck();if(window.CMH_CONFIG?.GAMEPLAY?.DANGER_BGM_ENABLED!==false)audio.setDanger(danger)}\n"
guarded="    if(!state.paused&&!tutorial.active){updateEnemies(dt);updateProjectiles(dt);state.timerAcc+=dt;if(state.timerAcc>=.1){state.timeLeft-=state.timerAcc;state.timerAcc=0;if(state.timeLeft<=0){state.timeLeft=STAGES[state.stage].timer;failLife('TIME UP')}}const danger=dangerCheck();if(window.CMH_CONFIG?.GAMEPLAY?.DANGER_BGM_ENABLED!==false)audio.setDanger(danger)}\n    if(tutorial.active&&!state.paused)tutorialTick();\n"
rep(Path('game.js'),needle,guarded,'loop hook')

# Tutorial keeps real flood-fill/reveal, but exits before score/items/milestones.
needle="  const delta=Math.max(0,state.area-before), points=Math.round(gained*(10+state.stage*2)*(1+Math.min(.8,delta/35)));\n"
rep(Path('game.js'),needle,"  if(tutorial.active){audio.beep(740,.09,'triangle',.04);updateHUD();return}\n"+needle,'capture no score')

# controller inserted before preloadNext
controller=r'''function tutorialRender(){
  const o=$('#tutorialOverlay'),coarse=tutorialCoarse();if(!o)return;
  let title='',text='',hint='',label='',ready=false;
  if(tutorial.step==='move'){label='STEP 1 / 4';title='MOVE';text=coarse?'왼쪽 조이스틱으로 3칸 이상 이동하세요':'Arrow Keys / WASD · 3칸 이상 이동하세요';hint='먼저 안전영역 위에서 이동을 익힙니다.'}
  else if(tutorial.step==='draw'){label='STEP 2 / 4';title='DRAW THE LINE';text=coarse?'CAPTURE를 누른 채 + MOVE':'HOLD SPACE + MOVE';hint='안전영역 밖으로 선을 2칸 이상 그리세요.'}
  else if(tutorial.step==='capture'){label='STEP 3 / 4';title='CONNECT BACK';text='선을 안전영역에 다시 연결하세요';hint='라인을 닫으면 영역이 실제로 공개됩니다.'}
  else if(tutorial.step==='retract'){label='STEP 4 / 4';title='RELEASE TO RETREAT';text=tutorial.retractArmed?(coarse?'이제 CAPTURE에서 손을 떼세요':'NOW RELEASE SPACE'):(coarse?'CAPTURE + MOVE로 짧게 선을 그리세요':'HOLD SPACE + MOVE로 짧게 선을 그리세요');hint='버튼을 놓으면 방금 그은 선을 따라 안전지대로 후퇴합니다.'}
  else{label='TUTORIAL COMPLETE ♥';title='READY?';text='80% = CLEAR · 90% = BONUS · 99%+ = PERFECT';hint=coarse?'TIP · DASH 버튼으로 빠르게 이동':'TIP · SHIFT = DASH';ready=true}
  o.innerHTML='<button id="tutorialSkipV2" class="tutorial-skip-v2">SKIP TUTORIAL</button><div class="tutorial-live-v2"><small>'+label+'</small><h2>'+title+'</h2><p>'+text+'</p><em>'+hint+'</em><button id="tutorialGoV2" class="btn primary '+(ready?'':'hidden')+'">'+(tutorial.replay?'BACK TO TITLE':'START STAGE 1')+'</button></div>';
  o.classList.add('interactive-v2');o.classList.remove('hidden');$('#tutorialSkipV2').onclick=showTutorialSkipConfirm;$('#tutorialGoV2').onclick=tutorialPrimary;
  if(ready)$('#tutorialSkipV2').classList.add('hidden');
}
function tutorialStepDone(step){if(tutorial.done.has(step))return;tutorial.done.add(step);track('tutorial_step_complete',{step});audio.beep(880,.08,'triangle',.035);toast('GOOD! ♥',false,650)}
function tutorialSet(step,delay=0){const f=()=>{if(!tutorial.active)return;tutorial.step=step;if(step==='retract'){tutorial.retractArmed=false;tutorial.retractStarted=false}tutorialRender()};delay?setTimeout(f,delay):f()}
function tutorialReset(){const step=tutorial.step;initTutorialGrid();state.enemies=[];state.projectiles=[];state.items=[];state.score=0;state.lives=3;state.timeLeft=999;state.clearMilestone=0;tutorial.lastX=state.player.x;tutorial.lastY=state.player.y;tutorial.lastArea=state.area;tutorial.prevAuto=false;tutorial.step=step;updateHUD();tutorialRender()}
function tutorialTryAgain(reason){if(!tutorial.active)return;if(tutorial.step==='capture')tutorial.step='draw';toast('TRY AGAIN · '+reason,true,950);setTimeout(()=>{if(tutorial.active)tutorialReset()},220)}
function tutorialTick(){
  if(!tutorial.active)return;state.timeLeft=999;state.score=0;state.items=[];const p=state.player;
  const moved=tutorial.lastX===null?0:Math.abs(p.x-tutorial.lastX)+Math.abs(p.y-tutorial.lastY);
  if(tutorial.step==='move'&&p.drawing){clearTrail();toast('먼저 이동부터 해볼게요',false,650);tutorial.lastX=state.player.x;tutorial.lastY=state.player.y}
  else if(moved){tutorial.moveCells+=moved;tutorial.lastX=p.x;tutorial.lastY=p.y}
  if(tutorial.step==='move'&&tutorial.moveCells>=3){tutorialStepDone('move');tutorialSet('draw',450)}
  else if(tutorial.step==='draw'&&p.drawing&&(p.trailPath?.length||0)>=2){tutorialStepDone('draw');tutorial.lastArea=state.area;tutorialSet('capture',300)}
  else if(tutorial.step==='capture'){
    if(state.area>tutorial.lastArea+.01){tutorialStepDone('capture');toast('AREA CAPTURED! ♥',false,800);tutorialSet('retract',550)}
    else if(p.autoRetract)tutorial.retractStarted=true;
    else if(tutorial.retractStarted&&!p.drawing){tutorial.retractStarted=false;toast('TRY AGAIN · 선을 안전영역에 연결하세요',true,850);tutorialSet('draw',350)}
  }else if(tutorial.step==='retract'){
    if(!tutorial.retractArmed&&p.drawing&&(p.trailPath?.length||0)>=2){tutorial.retractArmed=true;tutorialRender()}
    if(tutorial.retractArmed&&p.autoRetract)tutorial.retractStarted=true;
    if(tutorial.retractStarted&&!p.autoRetract&&!p.drawing){tutorialStepDone('retract');tutorialFinish()}
  }
  tutorial.prevAuto=p.autoRetract;
}
function tutorialFinish(){tutorial.step='ready';state.paused=true;if(!tutorial.replay)tutorialPersist('complete');const d=Math.max(0,Math.round((performance.now()-tutorial.startedAt)/1000));track('tutorial_complete',{duration_seconds:d,replay:!!tutorial.replay});tutorialRender()}
function tutorialPrimary(){if(!tutorial.active||tutorial.step!=='ready')return;const replay=tutorial.replay;tutorial.active=false;state.paused=false;$('#tutorialOverlay').classList.add('hidden');input.dirs.clear();input.capture=false;input.dash=false;if(replay)showTitle();else startStage(1,false)}
function showTutorialSkipConfirm(){if(!tutorial.active||tutorial.step==='ready')return;state.paused=true;openModal('<h2>Skip tutorial?</h2><p>You can replay it later from HOW TO PLAY.</p><div class="slot-grid"><button id="tutorialContinueV2" class="btn secondary">CONTINUE TUTORIAL</button><button id="tutorialSkipConfirmV2" class="btn tertiary">SKIP</button></div>');$('#tutorialContinueV2').onclick=()=>{closeModal();state.paused=false;state.lastTs=performance.now()};$('#tutorialSkipConfirmV2').onclick=()=>{closeModal();tutorialSkip()}}
function tutorialSkip(){const replay=tutorial.replay,d=Math.max(0,Math.round((performance.now()-tutorial.startedAt)/1000));track('tutorial_skip',{step:tutorial.step,duration_seconds:d,replay:!!replay});if(!replay)tutorialPersist('skipped');tutorial.active=false;state.paused=false;$('#tutorialOverlay').classList.add('hidden');input.dirs.clear();input.capture=false;input.dash=false;if(replay)showTitle();else startStage(1,false)}
function initTutorialGrid(){
  grid.fill(CLAIMED);
  const x0=Math.floor(GW*.22),x1=Math.ceil(GW*.78),y0=Math.floor(GH*.22),y1=Math.ceil(GH*.78);
  for(let y=y0;y<=y1;y++)for(let x=x0;x<=x1;x++)setCell(x,y,UNCLAIMED);
  const px=Math.floor((x0+x1)/2),py=y0-1;
  state.player={x:px,y:py,drawing:false,autoRetract:false,trailStart:{x:px,y:py},trailPath:[]};
  state.area=calcArea();state.lastArea=state.area;rebuildVisualLayers();
}
async function startInteractiveTutorial(replay=false){
  tutorial.active=true;tutorial.replay=!!replay;tutorial.step='move';tutorial.startedAt=performance.now();tutorial.moveCells=0;tutorial.lastX=null;tutorial.lastY=null;tutorial.lastArea=0;tutorial.retractArmed=false;tutorial.retractStarted=false;tutorial.done=new Set();if(replay)track('tutorial_replay',{});track('tutorial_start',{replay:!!replay});
  state.stage=1;state.mode='loading';showGame();closeModal();state.paused=true;try{state.currentImage=await loadImage(stageSrc(1))}catch(e){tutorial.active=false;return showTitle()}initTutorialGrid();state.enemies=[];state.projectiles=[];state.items=[];state.score=0;state.lives=3;state.timeLeft=999;state.clearMilestone=0;state.shield=0;state.dashStamina=100;state.dashExhausted=false;state.mode='playing';state.paused=false;state.lastTs=performance.now();state.moveAcc=0;state.timerAcc=0;audio.playBase(STAGES[1].music,true);audio.setDanger(false);tutorial.lastX=state.player.x;tutorial.lastY=state.player.y;tutorialRender();updateHUD();cancelAnimationFrame(state.frameId);state.frameId=requestAnimationFrame(loop)
}
'''
marker="function preloadNext(){if(state.stage<10)loadImage(stageSrc(state.stage+1)).catch(()=>{});}\n"
rep(Path('game.js'),marker,controller+'\n'+marker,'controller')

# CSS appended; overlay remains transparent enough to see and interact with board.
css=root/'styles.css';s=css.read_text(encoding='utf-8')
if '/* v0.7.1 tutorial v2 */' not in s:
 s += r'''
/* v0.7.1 tutorial v2 */
.tutorial-overlay.interactive-v2{background:linear-gradient(180deg,rgba(3,1,8,.16),rgba(3,1,8,.02) 62%,rgba(3,1,8,.2));backdrop-filter:none;pointer-events:none;align-items:flex-start;padding:12px}.tutorial-live-v2{width:min(470px,72%);padding:12px 16px;border-radius:16px;background:rgba(25,8,37,.9);border:1px solid rgba(255,110,185,.42);box-shadow:0 12px 36px rgba(0,0,0,.48),0 0 24px rgba(255,60,155,.14);text-align:center}.tutorial-live-v2 small{color:#ff9dcc;font-weight:900;letter-spacing:.14em}.tutorial-live-v2 h2{margin:2px 0 4px;font-size:1.15rem}.tutorial-live-v2 p{margin:0;color:#f3e9f4}.tutorial-live-v2 em{display:block;margin-top:5px;color:#cab8cd;font-size:.72rem;font-style:normal}.tutorial-live-v2 .btn{margin-top:9px;pointer-events:auto}.tutorial-skip-v2{position:absolute;right:10px;top:10px;z-index:3;border:1px solid rgba(255,255,255,.2);border-radius:999px;padding:6px 9px;background:rgba(7,4,14,.78);color:#eee;font-size:.6rem;font-weight:850;cursor:pointer;pointer-events:auto}@media(max-width:800px),(pointer:coarse){.tutorial-overlay.interactive-v2{padding:5px}.tutorial-live-v2{width:min(64%,430px);padding:7px 10px}.tutorial-live-v2 h2{font-size:.82rem}.tutorial-live-v2 p{font-size:.65rem}.tutorial-live-v2 em{font-size:.52rem}.tutorial-live-v2 small{font-size:.46rem}.tutorial-skip-v2{right:5px;top:5px;font-size:.48rem;padding:4px 6px}}
'''
 css.write_text(s,encoding='utf-8')

# Visible build label after visual/age patches.
index=root/'index.html';s=index.read_text(encoding='utf-8')
for old in ('v0.6.8 19+ age gate','v0.6.4 visual refresh'):
 if old in s: s=s.replace(old,'v0.7.1 interactive tutorial',1);break
index.write_text(s,encoding='utf-8')

print('v0.7.1 interactive tutorial v2 applied')
