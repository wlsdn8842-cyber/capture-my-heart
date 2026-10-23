const fs=require('fs'),vm=require('vm');
const src=fs.readFileSync(process.argv[2],'utf8');

function assert(c,m){if(!c)throw new Error(m)}
function getFn(name){
  const start=src.indexOf(`function ${name}(`);
  if(start<0)throw new Error(`missing function ${name}`);
  const brace=src.indexOf('{',start);let depth=0;
  for(let i=brace;i<src.length;i++){
    if(src[i]==='{')depth++;
    else if(src[i]==='}'&&--depth===0)return src.slice(start,i+1);
  }
  throw new Error(`unterminated function ${name}`);
}

try{
  // Static compatibility and scope checks.
  assert(src.includes("const STAGE1_ENTRY_GUARD={enabled:true,maxMs:15000"),'Stage 1 entry guard must be enabled in dev with 15s cap');
  assert(src.includes("bossSpeedScale:.82"),'Stage 1 guard boss speed scale missing');
  assert(src.includes("chaseScale:.55"),'Stage 1 guard chase scale missing');
  assert(src.includes("suppressProjectiles:true"),'Stage 1 projectile suppression missing');
  assert(src.includes("const CLEAR_BANK_V1={enabled:false"),'clear bank must remain disabled by default');

  for(const e of ['stage1_attempt_start','stage1_first_capture','stage1_first_death','stage1_clear','stage1_attempt_end','stage2_entry']){
    assert(src.includes(`track('${e}'`),`${e} instrumentation missing`);
  }
  assert(src.includes("attempt_id:state.stageAttemptId"),'attempt correlation id missing');
  assert(src.includes("start_source:startSource"),'stage start source instrumentation missing');

  const tutorialTick=getFn('tutorialTick');
  assert(tutorialTick.includes("tutorialStepDone('capture')"),'capture tutorial completion marker missing');
  assert(tutorialTick.includes("tutorialFinish()"),'tutorial must finish after first successful capture');
  assert(!tutorialTick.includes("tutorialSet('retract'"),'retract must not remain a required tutorial step');
  const tutorialRender=getFn('tutorialRender');
  assert(tutorialRender.includes('OPTIONAL TIP'),'optional retract tip missing');
  assert(tutorialRender.includes('STEP 3 / 3'),'tutorial should have three required steps');

  assert(src.includes("if(entryGuard&&e.isBoss)"),'Stage 1 boss pressure guard missing');
  assert(src.includes("if(entryGuard&&STAGE1_ENTRY_GUARD.suppressProjectiles)"),'Stage 1 projectile guard missing');
  assert(src.includes("{name:'Racing Girl',   music:'assets/audio/stages_1_4.mp3', speed:117, shots:2400, minions:1, chase:0.115,timer:175"),'Stage 2 difficulty changed unexpectedly');
  assert(src.includes("{name:'Final Queen',   music:'assets/audio/stage10.mp3',    speed:180, shots:1000, minions:4, chase:0.30, timer:135"),'Stage 10 difficulty changed unexpectedly');

  assert(src.includes("KEYMAP_STORAGE_KEY='cmh.keymap.v1'"),'PC key mapping compatibility missing');
  assert(src.includes('mobileCaptureLocked'),'mobile CAPTURE compatibility missing');
  assert(src.includes("perfectTarget=m.kind==='character'?100:99"),'existing PERFECT logic changed unexpectedly');

  // Behavioral checks for the bounded Stage 1 entry guard.
  const events=[];let clock=1000;
  const ctx={
    state:{
      stage:1,area:4.5,characterArea:3.2,stageAttemptFirstCaptureTracked:false,
      stage1EntryGuardUntil:16000,stage1GuardEndTracked:false,stage1GuardPausedAt:0,paused:false,
      stageAttemptStartedAt:500,stageAttemptId:'attempt_1',stage1AttemptNo:1,stageAttemptEnded:false,stageAttemptCleared:false,
      stageAttemptDeaths:0,stageAttemptFirstDeathTracked:false,
      enemies:[{isBoss:true,shotTimer:100}]
    },
    STAGE1_ENTRY_GUARD:{enabled:true,maxMs:15000,bossSpeedScale:.82,chaseScale:.55,suppressProjectiles:true,postGuardShotDelayMs:900},
    tutorial:{active:false},
    now:()=>clock,
    track:(n,p)=>events.push([n,p]),
    mobileUXActive:()=>false,
    document:{visibilityState:'visible'}
  };
  vm.createContext(ctx);
  vm.runInContext([
    getFn('stageAttemptElapsedMs'),
    getFn('stageAttemptMeta'),
    getFn('stage1EndEntryGuard'),
    getFn('stage1SuspendEntryGuard'),
    getFn('stage1ResumeEntryGuard'),
    getFn('stage1EntryGuardActive'),
    getFn('recordStage1FirstCapture')
  ].join('\n'),ctx);

  assert(ctx.stage1EntryGuardActive()===true,'guard should be active before first capture and before 15s');
  ctx.recordStage1FirstCapture(1.0,null);
  assert(ctx.state.stageAttemptFirstCaptureTracked===true,'first capture was not recorded');
  assert(ctx.state.stage1GuardEndTracked===true,'guard did not end on first capture');
  assert(ctx.state.enemies[0].shotTimer>=900,'post-guard shot delay not applied');
  assert(events.some(x=>x[0]==='stage1_first_capture'),'first capture event missing');
  assert(events.some(x=>x[0]==='stage1_guard_end'&&x[1].reason==='first_capture'),'guard end reason should be first_capture');

  events.length=0;clock=20000;
  ctx.state.stageAttemptFirstCaptureTracked=false;
  ctx.state.stage1GuardEndTracked=false;
  ctx.state.stage1EntryGuardUntil=16000;
  assert(ctx.stage1EntryGuardActive()===false,'guard must expire after the 15s hard cap');
  assert(events.some(x=>x[0]==='stage1_guard_end'&&x[1].reason==='timeout'),'timeout guard event missing');

  // Pause/background time must not consume the active 15s guard.
  events.length=0;clock=1000;
  ctx.state.stageAttemptFirstCaptureTracked=false;
  ctx.state.stage1GuardEndTracked=false;
  ctx.state.stage1EntryGuardUntil=16000;
  ctx.state.stage1GuardPausedAt=0;
  ctx.state.paused=false;
  assert(ctx.stage1EntryGuardActive()===true,'guard should start active for pause test');
  ctx.stage1SuspendEntryGuard('pause');
  assert(ctx.state.stage1GuardPausedAt===1000,'guard pause timestamp missing');
  clock=13000;ctx.state.paused=false;
  assert(ctx.stage1EntryGuardActive()===true,'paused wall time incorrectly consumed the guard');
  assert(ctx.state.stage1EntryGuardUntil===28000,'guard deadline was not shifted by paused duration');
  clock=27999;
  assert(ctx.stage1EntryGuardActive()===true,'guard ended before 15s of active play');
  clock=28001;
  assert(ctx.stage1EntryGuardActive()===false,'guard did not end after 15s of active play');

  // Clear bank is prepared but OFF. It must not affect current progression.
  const storage=new Map();
  const bankCtx={
    state:{slot:1,stage:1,score:123,lives:2,stageAttemptId:'a'},
    CLEAR_BANK_V1:{enabled:false,key:'cmh.clearBank.v1',stage1Only:true},
    stageProgressMetric:()=>({kind:'area',value:80}),
    localStorage:{
      setItem:(k,v)=>storage.set(k,v),
      getItem:k=>storage.get(k)||null,
      removeItem:k=>storage.delete(k)
    },
    track:()=>{}
  };
  vm.createContext(bankCtx);
  vm.runInContext([
    getFn('clearBankKey'),
    getFn('bankStageClear'),
    getFn('readStageClearBank'),
    getFn('bankedProgressionAvailable')
  ].join('\n'),bankCtx);
  assert(bankCtx.bankStageClear()===null,'disabled clear bank must not write');
  assert(storage.size===0,'disabled clear bank wrote local storage');
  assert(bankCtx.bankedProgressionAvailable()===false,'disabled clear bank became available');

  console.log('ALL STAGE1 RETENTION DEV TESTS PASS');
}catch(e){
  console.error('FAIL',e.message);
  process.exit(1);
}
