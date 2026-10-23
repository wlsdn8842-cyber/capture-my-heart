const fs=require('fs'),vm=require('vm');
const src=fs.readFileSync(process.argv[2],'utf8');
function assert(c,m){if(!c)throw new Error(m)}
function getFn(name){
  const start=src.indexOf(`function ${name}(`);
  if(start<0)throw new Error('missing function '+name);
  const brace=src.indexOf('{',start);let depth=0;
  for(let i=brace;i<src.length;i++){
    if(src[i]==='{')depth++;
    else if(src[i]==='}'&&--depth===0)return src.slice(start,i+1);
  }
  throw new Error('unterminated '+name);
}
try{
  assert(src.includes("const STAGE1_ENTRY_GUARD={enabled:true,maxMs:15000"),'Stage 1 entry guard must be enabled in dev with 15s cap');
  assert(src.includes("bossSpeedScale:.82"),'Stage 1 guard boss speed scale missing');
  assert(src.includes("chaseScale:.55"),'Stage 1 guard chase scale missing');
  assert(src.includes("suppressProjectiles:true"),'Stage 1 projectile suppression missing');
  assert(src.includes("const CLEAR_BANK_V1={enabled:false"),'clear bank must remain disabled by default');
  assert(src.includes("track('stage1_attempt_start'"),'Stage 1 attempt instrumentation missing');
  assert(src.includes("track('stage1_first_capture'"),'first capture instrumentation missing');
  assert(src.includes("track('stage1_first_death'"),'first death instrumentation missing');
  assert(src.includes("track('stage1_clear'"),'Stage 1 clear instrumentation missing');
  assert(src.includes("track('stage2_entry'"),'Stage 2 entry instrumentation missing');
  assert(src.includes("attempt_id:state.stageAttemptId"),'attempt correlation id missing');
  assert(src.includes("start_source:startSource"),'start source instrumentation missing');

  const tutorialTick=getFn('tutorialTick');
  assert(tutorialTick.includes("tutorialStepDone('capture')"),'capture tutorial completion marker missing');
  assert(tutorialTick.includes("tutorialFinish()"),'tutorial must finish after first successful capture');
  assert(!tutorialTick.includes("tutorialSet('retract'"),'retract must not remain a required tutorial step');
  const tutorialRender=getFn('tutorialRender');
  assert(tutorialRender.includes('OPTIONAL TIP'),'optional retract tip missing');
  assert(tutorialRender.includes('STEP 3 / 3'),'tutorial should be three required steps');

  assert(src.includes("if(entryGuard&&e.isBoss)"),'Stage 1 boss pressure guard missing');
  assert(src.includes("if(entryGuard&&STAGE1_ENTRY_GUARD.suppressProjectiles)"),'Stage 1 shot guard missing');
  assert(src.includes("state.stage===1"),'Stage 1-only guard missing');
  assert(src.includes("{name:'Racing Girl',   music:'assets/audio/stages_1_4.mp3', speed:117, shots:2400, minions:1, chase:0.115,timer:175"),'Stage 2 difficulty changed unexpectedly');
  assert(src.includes("{name:'Final Queen',   music:'assets/audio/stage10.mp3',    speed:180, shots:1000, minions:4, chase:0.30, timer:135"),'Stage 10 difficulty changed unexpectedly');

  assert(src.includes("KEYMAP_STORAGE_KEY='cmh.keymap.v1'"),'PC key mapping compatibility missing');
  assert(src.includes('mobileCaptureLocked'), 'mobile capture compatibility missing');
  assert(src.includes("perfectTarget=m.kind==='character'?100:99"),'existing PERFECT logic changed unexpectedly');

  const ctx={state:{stage:1,stageAttemptFirstCaptureTracked:false,stage1EntryGuardUntil:15000,stage1GuardEndTracked:false,stageAttemptStartedAt:0,stageAttemptId:'a_test',stage1AttemptNo:1},
    STAGE1_ENTRY_GUARD:{enabled:true,maxMs:15000,bossSpeedScale:.82,chaseScale:.55,suppressProjectiles:true,postGuardShotDelayMs:900},
    now:()=>1000,track:()=>{}};
  vm.createContext(ctx);
  vm.runInContext(getFn('stage1EntryGuardActive'),ctx);
  assert(ctx.stage1EntryGuardActive()===true,'guard should be active before first capture and before 15s');

  console.log('ALL STAGE1 RETENTION DEV TESTS PASS');
}catch(e){console.error('FAIL',e.message);process.exit(1)}
