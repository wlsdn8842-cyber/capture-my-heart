from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path, old, new, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'stage1 retention patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

# ---------------------------------------------------------------------------
# Stage 1 attempt telemetry + bounded onboarding guard + clear-bank prototype.
# No PII: only random per-attempt IDs, existing anonymous visitor/session IDs,
# timing, stage state and gameplay outcome data are emitted.
# ---------------------------------------------------------------------------
rep(Path('game.js'),
"""  shotAcc:0, continueCredits:1, currentImage:null, stageStartedAt:0,
  unlocked:new Set(), tutorialShown:localStorage.getItem('cmh.tutorial') === '1'
};""",
"""  shotAcc:0, continueCredits:1, currentImage:null, stageStartedAt:0,
  pendingStageStartSource:'direct',
  stageAttemptId:'', stageAttemptStartedAt:0, stageAttemptDeaths:0, stageAttemptFirstDeathTracked:false,
  stageAttemptFirstCaptureTracked:false, stageAttemptCleared:false, stage1AttemptNo:0,
  stage1EntryGuardUntil:0, stage1GuardEndTracked:false,
  unlocked:new Set(), tutorialShown:localStorage.getItem('cmh.tutorial') === '1'
};""",
'state telemetry fields')

marker="function loadSaveData(data){\n"
block=r'''const STAGE1_ATTEMPT_SEQ_KEY='cmh.stage1.attemptSeq.v1';
const STAGE1_LAST_CLEAR_SESSION_KEY='cmh.stage1.lastClear.v1';
const STAGE2_ENTRY_SEEN_KEY='cmh.stage2.entrySeen.v1';
const STAGE1_ENTRY_GUARD={enabled:true,maxMs:15000,bossSpeedScale:.82,chaseScale:.55,suppressProjectiles:true,postGuardShotDelayMs:900};
const CLEAR_BANK_V1={enabled:false,key:'cmh.clearBank.v1',stage1Only:true};

function telemetryId(prefix='a'){return prefix+'_'+Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,9)}
function safeLocalNumber(key){
  try{return Math.max(0,Number(localStorage.getItem(key))||0)}catch(_){return 0}
}
function nextStage1AttemptNo(){
  const n=safeLocalNumber(STAGE1_ATTEMPT_SEQ_KEY)+1;
  try{localStorage.setItem(STAGE1_ATTEMPT_SEQ_KEY,String(n))}catch(_){}
  return n;
}
function stageAttemptElapsedMs(){return Math.max(0,Math.round(now()-(state.stageAttemptStartedAt||now())))}
function stageAttemptMeta(){
  return {
    attempt_id:state.stageAttemptId||'',
    attempt_no:state.stage1AttemptNo||0,
    attempt_elapsed_ms:stageAttemptElapsedMs(),
    attempt_deaths:state.stageAttemptDeaths||0
  };
}
function rememberStage1Clear(){
  const data={attempt_id:state.stageAttemptId||'',attempt_no:state.stage1AttemptNo||0,cleared_at:Date.now()};
  try{sessionStorage.setItem(STAGE1_LAST_CLEAR_SESSION_KEY,JSON.stringify(data))}catch(_){}
  return data;
}
function readStage1Clear(){
  try{return JSON.parse(sessionStorage.getItem(STAGE1_LAST_CLEAR_SESSION_KEY)||'null')}catch(_){return null}
}
function beginStageTelemetry(stage,startSource='direct',fromSave=false){
  state.stageAttemptId=telemetryId('attempt');
  state.stageAttemptStartedAt=now();
  state.stageAttemptDeaths=0;
  state.stageAttemptFirstDeathTracked=false;
  state.stageAttemptFirstCaptureTracked=false;
  state.stageAttemptCleared=false;
  state.stage1EntryGuardUntil=0;
  state.stage1GuardEndTracked=false;
  if(stage===1){
    state.stage1AttemptNo=nextStage1AttemptNo();
    if(STAGE1_ENTRY_GUARD.enabled)state.stage1EntryGuardUntil=now()+STAGE1_ENTRY_GUARD.maxMs;
    track('stage1_attempt_start',{
      attempt_id:state.stageAttemptId,
      attempt_no:state.stage1AttemptNo,
      first_instrumented_attempt:state.stage1AttemptNo===1,
      start_source:startSource,
      from_save:!!fromSave,
      input_mode:mobileUXActive()?'mobile':'keyboard',
      guard_max_ms:STAGE1_ENTRY_GUARD.enabled?STAGE1_ENTRY_GUARD.maxMs:0
    });
  }else state.stage1AttemptNo=0;

  if(stage===2){
    const prev=readStage1Clear();
    let firstInstrumentedEntry=false;
    try{
      firstInstrumentedEntry=localStorage.getItem(STAGE2_ENTRY_SEEN_KEY)!=='1';
      localStorage.setItem(STAGE2_ENTRY_SEEN_KEY,'1');
    }catch(_){}
    track('stage2_entry',{
      start_source:startSource,
      from_save:!!fromSave,
      first_instrumented_entry:firstInstrumentedEntry,
      previous_stage1_attempt_id:prev?.attempt_id||'',
      previous_stage1_attempt_no:Number(prev?.attempt_no)||0
    });
  }
}
function stage1EndEntryGuard(reason='timeout'){
  if(state.stage!==1||state.stage1GuardEndTracked)return;
  state.stage1GuardEndTracked=true;
  state.stage1EntryGuardUntil=0;
  const boss=state.enemies?.find?.(e=>e.isBoss);
  if(boss&&Number.isFinite(boss.shotTimer))boss.shotTimer=Math.max(boss.shotTimer,STAGE1_ENTRY_GUARD.postGuardShotDelayMs);
  track('stage1_guard_end',{...stageAttemptMeta(),reason});
}
function stage1EntryGuardActive(){
  if(state.stage!==1||!STAGE1_ENTRY_GUARD.enabled||state.stageAttemptFirstCaptureTracked)return false;
  if(now()>=state.stage1EntryGuardUntil){
    stage1EndEntryGuard('timeout');
    return false;
  }
  return true;
}
function recordStage1FirstCapture(before,beforeCharacter){
  if(state.stage!==1||tutorial.active||state.stageAttemptFirstCaptureTracked)return;
  const guardWasActive=stage1EntryGuardActive();
  state.stageAttemptFirstCaptureTracked=true;
  const afterCharacter=Number.isFinite(state.characterArea)?state.characterArea:null;
  track('stage1_first_capture',{
    ...stageAttemptMeta(),
    area_before:Number(before.toFixed(2)),
    area_after:Number(state.area.toFixed(2)),
    area_delta:Number(Math.max(0,state.area-before).toFixed(2)),
    character_before:Number.isFinite(beforeCharacter)?Number(beforeCharacter.toFixed(2)):null,
    character_after:Number.isFinite(afterCharacter)?Number(afterCharacter.toFixed(2)):null,
    input_mode:mobileUXActive()?'mobile':'keyboard',
    guard_was_active:guardWasActive
  });
  if(guardWasActive)stage1EndEntryGuard('first_capture');
}
function recordStage1Death(reason){
  if(state.stage!==1||tutorial.active)return;
  state.stageAttemptDeaths=(state.stageAttemptDeaths||0)+1;
  if(state.stageAttemptFirstDeathTracked)return;
  state.stageAttemptFirstDeathTracked=true;
  const p=stageProgressMetric();
  track('stage1_first_death',{
    ...stageAttemptMeta(),
    reason:String(reason||'MISS').slice(0,80),
    area:Number(state.area.toFixed(2)),
    progress_metric:p.kind,
    progress_value:Number(p.value.toFixed(2)),
    lives_after:state.lives
  });
}
function recordStage1Clear(progress){
  if(state.stage!==1||state.stageAttemptCleared)return;
  state.stageAttemptCleared=true;
  const prev=rememberStage1Clear();
  track('stage1_clear',{
    ...stageAttemptMeta(),
    progress_metric:progress.kind,
    progress_value:Number(progress.value.toFixed(2)),
    area:Number(state.area.toFixed(2)),
    score:state.score
  });
  if(CLEAR_BANK_V1.enabled)bankStageClear(progress,prev);
}
function clearBankKey(slot=state.slot){return CLEAR_BANK_V1.key+'.slot.'+slot}
function bankStageClear(progress=stageProgressMetric(),prev=null){
  if(!CLEAR_BANK_V1.enabled)return null;
  if(CLEAR_BANK_V1.stage1Only&&state.stage!==1)return null;
  const data={
    version:1,slot:state.slot,stage:state.stage,nextStage:Math.min(10,state.stage+1),
    score:state.score,lives:Math.max(1,state.lives),bankedAt:Date.now(),
    progress_metric:progress.kind,progress_value:Number(progress.value.toFixed(2)),
    attempt_id:prev?.attempt_id||state.stageAttemptId||''
  };
  try{localStorage.setItem(clearBankKey(),JSON.stringify(data))}catch(_){}
  track('stage_clear_banked',{stage:state.stage,next_stage:data.nextStage,attempt_id:data.attempt_id});
  return data;
}
function readStageClearBank(slot=state.slot){
  try{return JSON.parse(localStorage.getItem(clearBankKey(slot))||'null')}catch(_){return null}
}
function clearStageClearBank(slot=state.slot){try{localStorage.removeItem(clearBankKey(slot))}catch(_){}}
function bankedProgressionAvailable(){
  const b=readStageClearBank();
  return !!(CLEAR_BANK_V1.enabled&&b&&Number(b.stage)===state.stage&&Number(b.nextStage)===state.stage+1);
}
function advanceFromClearBank(){
  const b=readStageClearBank();if(!b)return false;
  if(Number(b.stage)!==state.stage)return false;
  clearStageClearBank();
  state.score=Math.max(state.score,Number(b.score)||0);
  state.lives=Math.max(1,Number(b.lives)||1);
  state.stage=Math.min(10,Number(b.nextStage)||state.stage+1);
  state.pendingStageStartSource='clear_bank';
  saveToSlot(state.slot);
  closeModal();
  startStage(state.stage,false);
  return true;
}

'''
rep(Path('game.js'),marker,block+marker,'telemetry helpers')

rep(Path('game.js'),
"""function loadSaveData(data){
  if(!data)return;
  state.slot=data.slot||1;state.stage=clamp(data.stage||1,1,10);state.score=data.score||0;state.lives=data.lives||3;
  state.unlocked=new Set([...(globalData().unlockedStages||[]),...(data.unlocked||[])]);state.continueCredits=1;
  startStage(state.stage,true);
}""",
"""function loadSaveData(data){
  if(!data)return;
  state.slot=data.slot||1;state.stage=clamp(data.stage||1,1,10);state.score=data.score||0;state.lives=data.lives||3;
  state.unlocked=new Set([...(globalData().unlockedStages||[]),...(data.unlocked||[])]);state.continueCredits=1;
  state.pendingStageStartSource='load_save';
  startStage(state.stage,true);
}""",
'load source')

rep(Path('game.js'),
"""      state.slot=s;state.stage=1;state.score=0;state.lives=3;state.continueCredits=1;loadUnlocked();saveToSlot(s);track('game_start',{slot:s});closeModal();if(tutorialRequired())startInteractiveTutorial(false);else startStage(1,false);""",
"""      state.slot=s;state.stage=1;state.score=0;state.lives=3;state.continueCredits=1;state.pendingStageStartSource='new_game';loadUnlocked();saveToSlot(s);track('game_start',{slot:s});closeModal();if(tutorialRequired())startInteractiveTutorial(false);else startStage(1,false);""",
'new game source')

rep(Path('game.js'),
"""async function startStage(n,fromSave=false){
  if(mobileUXActive())resetMobileCaptureLock('stage_start');
  state.stage=clamp(n,1,10);state.mode='loading';showGame();closeModal();state.paused=true;updateHUD();toast(`STAGE ${state.stage} · ${STAGES[state.stage].name}`);""",
"""async function startStage(n,fromSave=false){
  if(mobileUXActive())resetMobileCaptureLock('stage_start');
  const startSource=state.pendingStageStartSource||(fromSave?'load_or_continue':'direct');
  state.pendingStageStartSource='direct';
  state.stage=clamp(n,1,10);state.mode='loading';showGame();closeModal();state.paused=true;updateHUD();toast(`STAGE ${state.stage} · ${STAGES[state.stage].name}`);""",
'stage source capture')

rep(Path('game.js'),
"""  initGrid();spawnEnemies();state.projectiles=[];state.items=[];state.clearMilestone=0;state.stage1EscapeUsed=false;state.stage1EscapePending=false;state.containmentActive=false;state.containmentPct=100;state.containmentStartedAt=0;state.containmentNextPatternAt=0;state.containmentPendingMilestone=false;state.containmentHoldUntil=0;state.stage1RageUntil=0;state.stage1RageRamReadyAt=0;state.stage1RagePendingClear=false;state.timeLeft=STAGES[state.stage].timer;state.shotAcc=0;state.speedBoostUntil=0;state.freezeUntil=0;state.slowUntil=0;state.shield=0;state.dashStamina=100;state.dashExhausted=false;state.stageStartedAt=Date.now();state.mode='playing';state.paused=false;state.lastTs=performance.now();state.moveAcc=0;state.timerAcc=0;
  audio.playBase(STAGES[state.stage].music,true);audio.setDanger(false);saveToSlot(state.slot);
  track('stage_start',{stage:state.stage,from_save:!!fromSave});""",
"""  initGrid();spawnEnemies();state.projectiles=[];state.items=[];state.clearMilestone=0;state.stage1EscapeUsed=false;state.stage1EscapePending=false;state.containmentActive=false;state.containmentPct=100;state.containmentStartedAt=0;state.containmentNextPatternAt=0;state.containmentPendingMilestone=false;state.containmentHoldUntil=0;state.stage1RageUntil=0;state.stage1RageRamReadyAt=0;state.stage1RagePendingClear=false;state.timeLeft=STAGES[state.stage].timer;state.shotAcc=0;state.speedBoostUntil=0;state.freezeUntil=0;state.slowUntil=0;state.shield=0;state.dashStamina=100;state.dashExhausted=false;state.stageStartedAt=Date.now();state.mode='playing';state.paused=false;state.lastTs=performance.now();state.moveAcc=0;state.timerAcc=0;
  beginStageTelemetry(state.stage,startSource,fromSave);
  audio.playBase(STAGES[state.stage].music,true);audio.setDanger(false);saveToSlot(state.slot);
  track('stage_start',{stage:state.stage,from_save:!!fromSave,start_source:startSource,attempt_id:state.stageAttemptId||'',attempt_no:state.stage1AttemptNo||0});""",
'stage telemetry start')

# Tutorial: three required steps. RETRACT becomes an optional tip on the ready screen.
rep(Path('game.js'),
"""  if(tutorial.step==='move'){label='STEP 1 / 4';title='MOVE';text=coarse?'왼쪽 조이스틱으로 3칸 이상 이동하세요':movementKeySummary()+' · 3칸 이상 이동하세요';hint='먼저 안전영역 위에서 이동을 익힙니다.'}
  else if(tutorial.step==='draw'){label='STEP 2 / 4';title='DRAW THE LINE';text=coarse?'1. TAP CAPTURE → 2. MOVE':'HOLD '+keyBindingSummary('capture')+' + MOVE';hint=coarse?'CAPTURE는 한 번 탭하면 잠깁니다. 안전영역 밖으로 이동하세요.':'안전영역 밖으로 선을 2칸 이상 그리세요.'}
  else if(tutorial.step==='capture'){label='STEP 3 / 4';title='CONNECT BACK';text='선을 안전영역에 다시 연결하세요';hint='라인을 닫으면 영역이 실제로 공개됩니다.'}
  else if(tutorial.step==='retract'){label='STEP 4 / 4';title=coarse?'TAP TO RETREAT':'RELEASE TO RETREAT';text=tutorial.retractArmed?(coarse?'CAPTURE를 다시 탭하세요':'NOW RELEASE '+keyBindingSummary('capture')):(coarse?'1. TAP CAPTURE → 2. MOVE':'HOLD '+keyBindingSummary('capture')+' + MOVE로 짧게 선을 그리세요');hint=coarse?'CAPTURE를 다시 탭하면 방금 그은 선을 따라 안전지대로 후퇴합니다.':'버튼을 놓으면 방금 그은 선을 따라 안전지대로 후퇴합니다.'}
  else{label='TUTORIAL COMPLETE ♥';title='READY?';text='80% = CLEAR · 90% = BONUS · 99%+ = PERFECT';hint=coarse?'TIP · DASH 버튼으로 빠르게 이동':'TIP · '+keyBindingSummary('dash')+' = DASH';ready=true}""",
"""  if(tutorial.step==='move'){label='STEP 1 / 3';title='MOVE';text=coarse?'왼쪽 조이스틱으로 3칸 이상 이동하세요':movementKeySummary()+' · 3칸 이상 이동하세요';hint='먼저 안전영역 위에서 이동을 익힙니다.'}
  else if(tutorial.step==='draw'){label='STEP 2 / 3';title='DRAW THE LINE';text=coarse?'1. TAP CAPTURE → 2. MOVE':'HOLD '+keyBindingSummary('capture')+' + MOVE';hint=coarse?'CAPTURE는 한 번 탭하면 잠깁니다. 안전영역 밖으로 이동하세요.':'안전영역 밖으로 선을 2칸 이상 그리세요.'}
  else if(tutorial.step==='capture'){label='STEP 3 / 3';title='CONNECT BACK';text='선을 안전영역에 다시 연결하세요';hint='라인을 닫으면 영역이 실제로 공개됩니다.'}
  else{label='TUTORIAL COMPLETE ♥';title='READY?';text='80% = CLEAR · 90% = BONUS · 99%+ = PERFECT';hint=coarse?'OPTIONAL TIP · CAPTURE를 다시 탭하면 그은 선을 따라 후퇴 · DASH로 빠르게 이동':'OPTIONAL TIP · '+keyBindingSummary('capture')+'를 놓으면 그은 선을 따라 후퇴 · '+keyBindingSummary('dash')+' = DASH';ready=true}""",
'tutorial three steps')

rep(Path('game.js'),
"""  else if(tutorial.step==='capture'){
    if(state.area>tutorial.lastArea+.01){tutorialStepDone('capture');toast('AREA CAPTURED! ♥',false,800);tutorialSet('retract',550)}
    else if(p.autoRetract)tutorial.retractStarted=true;
    else if(tutorial.retractStarted&&!p.drawing){tutorial.retractStarted=false;toast('TRY AGAIN · 선을 안전영역에 연결하세요',true,850);tutorialSet('draw',350)}
  }else if(tutorial.step==='retract'){
    if(!tutorial.retractArmed&&p.drawing&&(p.trailPath?.length||0)>=2){tutorial.retractArmed=true;tutorialRender()}
    if(tutorial.retractArmed&&p.autoRetract)tutorial.retractStarted=true;
    if(tutorial.retractStarted&&!p.autoRetract&&!p.drawing){tutorialStepDone('retract');tutorialFinish()}
  }""",
"""  else if(tutorial.step==='capture'){
    if(state.area>tutorial.lastArea+.01){tutorialStepDone('capture');toast('AREA CAPTURED! ♥',false,800);track('tutorial_optional_tip',{tip:'retract'});tutorialFinish()}
    else if(p.autoRetract)tutorial.retractStarted=true;
    else if(tutorial.retractStarted&&!p.drawing){tutorial.retractStarted=false;toast('TRY AGAIN · 선을 안전영역에 연결하세요',true,850);tutorialSet('draw',350)}
  }""",
'tutorial finish after capture')

# First successful Stage 1 capture ends the bounded guard and gets a dedicated event.
rep(Path('game.js'),
"""  if(tutorial.active){audio.beep(740,.09,'triangle',.04);updateHUD();return}
  const delta=Math.max(0,state.area-before), points=Math.round(gained*(10+state.stage*2)*(1+Math.min(.8,delta/35)));""",
"""  if(tutorial.active){audio.beep(740,.09,'triangle',.04);updateHUD();return}
  recordStage1FirstCapture(before,beforeCharacter);
  const delta=Math.max(0,state.area-before), points=Math.round(gained*(10+state.stage*2)*(1+Math.min(.8,delta/35)));""",
'first capture event')

# 80% Stage 1 clear event + optional clear-bank prototype (disabled by default).
rep(Path('game.js'),
"""  if(a>=80&&state.clearMilestone<80){state.clearMilestone=80;unlockStage(state.stage);showClearModal(80)}""",
"""  if(a>=80&&state.clearMilestone<80){state.clearMilestone=80;unlockStage(state.stage);if(state.stage===1)recordStage1Clear(m);showClearModal(80)}""",
'Stage 1 clear event')

rep(Path('game.js'),
"""  track('stage_milestone',{stage:state.stage,area:state.area,character_area:Number.isFinite(state.characterArea)?Number(state.characterArea.toFixed(2)):null,metric:progress.kind,metric_value:Number(progress.value.toFixed(2)),milestone:level,score:state.score});""",
"""  track('stage_milestone',{stage:state.stage,area:state.area,character_area:Number.isFinite(state.characterArea)?Number(state.characterArea.toFixed(2)):null,metric:progress.kind,metric_value:Number(progress.value.toFixed(2)),milestone:level,score:state.score,attempt_id:state.stageAttemptId||'',attempt_no:state.stage1AttemptNo||0});""",
'milestone attempt metadata')

# Preserve Stage 2-10 values, but soften only Stage 1 during the bounded entry guard.
rep(Path('game.js'),
"""  for(const e of state.enemies){
    if(e.isBoss&&bossUpdatePattern(e,dt))continue;
    const drawingBossPressure=e.isBoss&&state.player.drawing""",
"""  const entryGuard=stage1EntryGuardActive();
  for(const e of state.enemies){
    if(e.isBoss&&bossUpdatePattern(e,dt))continue;
    const drawingBossPressure=e.isBoss&&state.player.drawing""",
'entry guard enemy hook')

rep(Path('game.js'),
"""    const speed=e.speed*(slow ? 0.55 : 1)*bal.speed*drawingBossPressure*pressureBoost;
    const effectiveChase=rageChase
      ? rage.chase
      : state.player.drawing
        ? Math.min(e.isBoss?rage.chaseCap:.24,(e.chase||0)+(e.isBoss?bal.chase:bal.chase*.55)+areaPressure*(e.isBoss?.028:.012))
        : (e.chase||0);""",
"""    let speed=e.speed*(slow ? 0.55 : 1)*bal.speed*drawingBossPressure*pressureBoost;
    let effectiveChase=rageChase
      ? rage.chase
      : state.player.drawing
        ? Math.min(e.isBoss?rage.chaseCap:.24,(e.chase||0)+(e.isBoss?bal.chase:bal.chase*.55)+areaPressure*(e.isBoss?.028:.012))
        : (e.chase||0);
    if(entryGuard&&e.isBoss){speed*=STAGE1_ENTRY_GUARD.bossSpeedScale;effectiveChase*=STAGE1_ENTRY_GUARD.chaseScale}""",
'bounded boss pressure scale')

rep(Path('game.js'),
"""    if(e.isBoss&&cfg.shots){
      e.shotTimer-=dt*1000*bal.shotClock;
      if(e.shotTimer<=0){e.shotTimer=cfg.shots*(.8+Math.random()*.45);shoot(e)}
    }""",
"""    if(e.isBoss&&cfg.shots){
      if(entryGuard&&STAGE1_ENTRY_GUARD.suppressProjectiles){
        e.shotTimer=Math.max(e.shotTimer,STAGE1_ENTRY_GUARD.postGuardShotDelayMs);
      }else{
        e.shotTimer-=dt*1000*bal.shotClock;
        if(e.shotTimer<=0){e.shotTimer=cfg.shots*(.8+Math.random()*.45);shoot(e)}
      }
    }""",
'bounded projectile guard')

# Death instrumentation preserves the existing life_lost event and adds attempt metadata.
rep(Path('game.js'),
"""  state.lives--;juiceMissFX(reason);clearTrail();state.projectiles=[];audio.beep(150,.25,'sawtooth',.05);toast(`MISS · ${reason}`,true,1800);updateHUD();track('life_lost',{stage:state.stage,reason,lives:state.lives});""",
"""  state.lives--;recordStage1Death(reason);juiceMissFX(reason);clearTrail();state.projectiles=[];audio.beep(150,.25,'sawtooth',.05);toast(`MISS · ${reason}`,true,1800);updateHUD();track('life_lost',{stage:state.stage,reason,lives:state.lives,attempt_id:state.stageAttemptId||'',attempt_no:state.stage1AttemptNo||0,attempt_elapsed_ms:stageAttemptElapsedMs()});""",
'death attempt metadata')

# Clear-bank recovery UI is fully wired but impossible to trigger while the feature flag is false.
rep(Path('game.js'),
"""  const continueButton=adEnabled?'<button id="rewardContinue" class="btn secondary">WATCH AD · LIFE +1</button>':state.continueCredits>0?'<button id="freeContinue" class="btn secondary">CONTINUE · TEST CREDIT</button>':'';
  openModal(`<div class="game-over-title">GAME OVER</div><p style="text-align:center">Stage ${state.stage} · ${fmtScore(state.score)} pts</p><div class="slot-grid">${continueButton}<button id="gameoverFeedback" class="btn tertiary">💬 한줄 피드백</button><button id="gameoverLoad" class="btn tertiary">LOAD SAVE</button><button id="gameoverTitle" class="btn primary">TITLE</button></div>`);""",
"""  const continueButton=adEnabled?'<button id="rewardContinue" class="btn secondary">WATCH AD · LIFE +1</button>':state.continueCredits>0?'<button id="freeContinue" class="btn secondary">CONTINUE · TEST CREDIT</button>':'';
  const bankedButton=bankedProgressionAvailable()?'<button id="bankedNextStage" class="btn primary">NEXT STAGE · CLEAR SAVED</button>':'';
  openModal(`<div class="game-over-title">GAME OVER</div><p style="text-align:center">Stage ${state.stage} · ${fmtScore(state.score)} pts</p><div class="slot-grid">${bankedButton}${continueButton}<button id="gameoverFeedback" class="btn tertiary">💬 한줄 피드백</button><button id="gameoverLoad" class="btn tertiary">LOAD SAVE</button><button id="gameoverTitle" class="btn primary">TITLE</button></div>`);""",
'clear bank UI')

rep(Path('game.js'),
"""  if($('#freeContinue'))$('#freeContinue').onclick=()=>{track('continue_after_game_over',{kind:'free',stage:state.stage});state.continueCredits--;state.lives=1;closeModal();startStage(state.stage,true)};
  if($('#rewardContinue'))$('#rewardContinue').onclick=async()=>{track('reward_continue_click',{stage:state.stage});const ok=await window.CMH_ADS.showRewardedLife();if(ok){track('continue_after_game_over',{kind:'rewarded',stage:state.stage});state.lives=1;closeModal();startStage(state.stage,true)}else toast('광고가 완료되지 않았습니다',true)};""",
"""  if($('#bankedNextStage'))$('#bankedNextStage').onclick=()=>{track('clear_bank_continue',{stage:state.stage});advanceFromClearBank()};
  if($('#freeContinue'))$('#freeContinue').onclick=()=>{track('continue_after_game_over',{kind:'free',stage:state.stage});state.pendingStageStartSource='continue_free';state.continueCredits--;state.lives=1;closeModal();startStage(state.stage,true)};
  if($('#rewardContinue'))$('#rewardContinue').onclick=async()=>{track('reward_continue_click',{stage:state.stage});const ok=await window.CMH_ADS.showRewardedLife();if(ok){track('continue_after_game_over',{kind:'rewarded',stage:state.stage});state.pendingStageStartSource='continue_rewarded';state.lives=1;closeModal();startStage(state.stage,true)}else toast('광고가 완료되지 않았습니다',true)};""",
'continue source and bank recovery')

rep(Path('game.js'),
"""  const run=()=>startStage(state.stage,false);""",
"""  const run=()=>{clearStageClearBank();state.pendingStageStartSource='next_stage';startStage(state.stage,false)};""",
'next stage source')

# Dev-only build label. This branch is not deployed automatically.
rep(Path('index.html'),
    '<div class="version">v0.13.7 bilingual</div>',
    '<div class="version">v0.13.8-dev stage1 retention</div>',
    'dev version label')
rep(Path('config.js'),"VERSION: '0.13.7'","VERSION: '0.13.8-dev'",'dev config version')
rep(Path('sw.js'),"cmh-core-v0.13.7","cmh-core-v0.13.8-dev",'dev sw cache version')

print('v0.13.8-dev Stage 1 retention patch applied')
