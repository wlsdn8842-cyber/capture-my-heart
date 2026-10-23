import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(__dirname,'..','_site');
const artifacts=path.resolve(__dirname,'..','validation-artifacts');
fs.mkdirSync(artifacts,{recursive:true});
const PORT=4173;
const ORIGIN=`http://127.0.0.1:${PORT}`;

function assert(cond,msg){if(!cond)throw new Error(msg)}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const results=[];
const allEvents=[];
let currentScenario='boot';

function mime(file){
  const ext=path.extname(file).toLowerCase();
  return ({'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.mp3':'audio/mpeg','.mp4':'video/mp4','.webm':'video/webm','.zip':'application/zip','.xml':'application/xml; charset=utf-8','.txt':'text/plain; charset=utf-8'})[ext]||'application/octet-stream';
}

function rewriteTestConfig(){
  const p=path.join(root,'config.js');
  let s=fs.readFileSync(p,'utf8');
  s=s.replace('https://cvfmikycscmfjmooxhni.supabase.co/rest/v1/cmh_analytics_events',ORIGIN+'/__analytics');
  s=s.replace(/FEEDBACK:\s*\{\s*ENABLED:\s*true/,'FEEDBACK: {\n    ENABLED: false');
  s=s.replace(/COLLECTION:\s*\{\s*ENABLED:\s*true/,'COLLECTION: {\n    ENABLED: false');
  fs.writeFileSync(p,s);
}

rewriteTestConfig();
fs.writeFileSync(path.join(artifacts,'mock-events.jsonl'),'');


const server=http.createServer((req,res)=>{
  const u=new URL(req.url,ORIGIN);
  if(req.method==='POST'&&u.pathname==='/__analytics'){
    let body='';
    req.on('data',c=>body+=c);
    req.on('end',()=>{
      try{
        const event=JSON.parse(body||'{}');
        const stored={...event,__scenario:currentScenario,__received_at:new Date().toISOString()};
        allEvents.push(stored);
        fs.appendFileSync(path.join(artifacts,'mock-events.jsonl'),JSON.stringify(stored)+'\n');
        res.writeHead(201,{'Content-Type':'application/json'});res.end('{}');
      }catch(e){res.writeHead(400);res.end(String(e))}
    });
    return;
  }
  if(req.method==='GET'&&u.pathname==='/__events'){
    res.writeHead(200,{'Content-Type':'application/json'});res.end(JSON.stringify(allEvents));return;
  }
  let rel=decodeURIComponent(u.pathname);
  if(rel==='/'||rel==='')rel='/index.html';
  const file=path.normalize(path.join(root,rel));
  if(!file.startsWith(root)){res.writeHead(403);res.end('forbidden');return}
  if(!fs.existsSync(file)||fs.statSync(file).isDirectory()){res.writeHead(404);res.end('not found');return}
  const stat=fs.statSync(file);
  const range=req.headers.range;
  if(range&&/\.(mp4|mp3|webm)$/i.test(file)){
    const m=/bytes=(\d+)-(\d*)/.exec(range);
    if(m){
      const start=Number(m[1]),end=m[2]?Number(m[2]):Math.min(stat.size-1,start+1024*1024);
      res.writeHead(206,{'Content-Type':mime(file),'Content-Length':end-start+1,'Content-Range':`bytes ${start}-${end}/${stat.size}`,'Accept-Ranges':'bytes'});
      fs.createReadStream(file,{start,end}).pipe(res);return;
    }
  }
  res.writeHead(200,{'Content-Type':mime(file),'Content-Length':stat.size,'Cache-Control':'no-store'});
  fs.createReadStream(file).pipe(res);
});
await new Promise((resolve,reject)=>server.listen(PORT,'127.0.0.1',e=>e?reject(e):resolve()));

const browser=await chromium.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required']});

async function makeContext(options={}){
  const context=await browser.newContext({viewport:{width:1280,height:900},...options});
  await context.route('**/*',async route=>{
    const url=route.request().url();
    if(url.startsWith(ORIGIN)||url.startsWith('data:')||url.startsWith('blob:'))await route.continue();
    else await route.abort();
  });
  await context.addInitScript(()=>{
    try{navigator.vibrate=()=>true}catch(_){}
    try{HTMLMediaElement.prototype.play=function(){return Promise.resolve()}}catch(_){}
  });
  return context;
}

async function confirmAge(page){
  const gate=page.locator('#ageGate');
  if(await gate.isVisible().catch(()=>false))await page.locator('#ageConfirmBtn').click();
}

async function gotoHome(page,{tutorialComplete=false}={}){
  await page.goto(ORIGIN+'/?validation=1',{waitUntil:'domcontentloaded'});
  await confirmAge(page);
  if(tutorialComplete){
    await page.evaluate(()=>localStorage.setItem('cmh.tutorial.interactive.v1.status','complete'));
    await page.reload({waitUntil:'domcontentloaded'});
    await confirmAge(page);
  }
  await page.waitForSelector('#titleScreen:not(.hidden)');
}

async function chooseFirstSlot(page){
  await page.waitForSelector('#modalLayer:not(.hidden)');
  const buttons=page.locator('#modalLayer .slot-grid button');
  const count=await buttons.count();
  assert(count>0,'slot picker has no buttons');
  const texts=await buttons.allTextContents();
  let idx=texts.findIndex(t=>/slot\s*1|1번|empty|new/i.test(t));
  if(idx<0)idx=0;
  await buttons.nth(idx).click();
}

async function startNewGame(page){
  await page.locator('#newGameBtn').click();
  await chooseFirstSlot(page);
}

async function holdKey(page,key,ms){
  await page.keyboard.down(key);await sleep(ms);await page.keyboard.up(key);
}

async function captureLoopKeyboard(page,captureKey='Space'){
  await page.keyboard.down(captureKey);
  await holdKey(page,'ArrowDown',240);
  await holdKey(page,'ArrowRight',320);
  await holdKey(page,'ArrowUp',300);
  await page.keyboard.up(captureKey);
}

async function drivePcTutorial(page){
  const overlay=page.locator('#tutorialOverlay');
  await overlay.waitFor({state:'visible'});
  await page.waitForFunction(()=>document.querySelector('#tutorialOverlay')?.textContent?.includes('STEP 1 / 3'));
  await holdKey(page,'ArrowRight',380);
  await page.waitForFunction(()=>document.querySelector('#tutorialOverlay')?.textContent?.includes('STEP 2 / 3'));
  await page.keyboard.down('Space');
  await holdKey(page,'ArrowDown',240);
  await page.waitForFunction(()=>document.querySelector('#tutorialOverlay')?.textContent?.includes('STEP 3 / 3'));
  await holdKey(page,'ArrowRight',320);
  await holdKey(page,'ArrowUp',320);
  await page.keyboard.up('Space');
  await page.waitForFunction(()=>document.querySelector('#tutorialOverlay')?.textContent?.includes('TUTORIAL COMPLETE'),null,{timeout:5000});
  const text=await overlay.textContent();
  assert(text.includes('OPTIONAL TIP'),'RETRACT optional tip not shown');
  assert(!text.includes('STEP 4 / 4'),'old required RETRACT step still visible');
}

async function joystick(page,dir,ms){
  const box=await page.locator('#moveJoystick').boundingBox();
  assert(box,'mobile joystick not visible');
  const cx=box.x+box.width/2,cy=box.y+box.height/2,amp=Math.min(box.width,box.height)*.32;
  const vec={up:[0,-amp],down:[0,amp],left:[-amp,0],right:[amp,0]}[dir];
  await page.mouse.move(cx,cy);
  await page.mouse.down();
  await page.mouse.move(cx+vec[0],cy+vec[1],{steps:3});
  await sleep(ms);
  await page.mouse.up();
}

async function driveMobileTutorial(page){
  await page.waitForFunction(()=>document.querySelector('#tutorialOverlay')?.textContent?.includes('STEP 1 / 3'));
  await joystick(page,'right',420);
  await page.waitForFunction(()=>document.querySelector('#tutorialOverlay')?.textContent?.includes('STEP 2 / 3'));
  await page.locator('#captureTouchBtn').click();
  assert((await page.locator('#captureTouchBtn').textContent()).includes('ON'),'mobile CAPTURE did not lock ON');
  await joystick(page,'down',260);
  await page.waitForFunction(()=>document.querySelector('#tutorialOverlay')?.textContent?.includes('STEP 3 / 3'));
  await joystick(page,'right',340);
  await joystick(page,'up',340);
  await page.waitForFunction(()=>document.querySelector('#tutorialOverlay')?.textContent?.includes('TUTORIAL COMPLETE'),null,{timeout:5000});
  const text=await page.locator('#tutorialOverlay').textContent();
  assert(text.includes('OPTIONAL TIP'),'mobile optional RETRACT tip missing');
  assert(!(await page.locator('#captureTouchBtn').textContent()).includes('ON'),'mobile CAPTURE lock did not reset after capture');
}

async function installSpies(page){
  await page.evaluate(()=>{
    window.__cmhTest={tracks:[],shots:[],retractCalls:0};
    if(window.CMH_ANALYTICS?.track){
      const orig=window.CMH_ANALYTICS.track.bind(window.CMH_ANALYTICS);
      window.CMH_ANALYTICS.track=(name,params={})=>{window.__cmhTest.tracks.push({name,params,t:performance.now()});return orig(name,params)};
    }
    if(typeof window.shoot==='function'){
      const orig=window.shoot;
      window.shoot=function(...args){window.__cmhTest.shots.push(performance.now());return orig.apply(this,args)};
    }
    if(typeof window.beginAutoRetract==='function'){
      const orig=window.beginAutoRetract;
      window.beginAutoRetract=function(...args){window.__cmhTest.retractCalls++;return orig.apply(this,args)};
    }
  });
}

function scenarioEvents(name,eventName=null){
  return allEvents.filter(e=>e.__scenario===name&&(!eventName||e.event_name===eventName));
}
async function waitStored(name,eventName,pred=()=>true,timeout=7000){
  const end=Date.now()+timeout;
  while(Date.now()<end){
    const found=scenarioEvents(name,eventName).find(pred);
    if(found)return found;
    await sleep(80);
  }
  throw new Error(`timeout waiting for ${name} / ${eventName}`);
}
async function flush(page){await page.evaluate(()=>window.CMH_ANALYTICS?.flush?.());await sleep(150)}
async function runtimeTrack(page,name){
  return page.evaluate(n=>window.__cmhTest?.tracks?.find(x=>x.name===n)||null,name);
}
async function waitForShot(page,timeout=4500){
  const end=Date.now()+timeout;
  while(Date.now()<end){
    const shots=await page.evaluate(()=>window.__cmhTest?.shots||[]);
    if(shots.length)return shots[0];
    await sleep(80);
  }
  return null;
}
async function resumePause(page){
  await page.waitForSelector('#modalLayer:not(.hidden)');
  const buttons=page.locator('#modalLayer button');
  const texts=await buttons.allTextContents();
  let idx=texts.findIndex(t=>/resume|continue|계속/i.test(t));
  if(idx<0)idx=0;
  await buttons.nth(idx).click();
  await page.waitForTimeout(200);
}

async function run(name,fn){
  currentScenario=name;
  const start=Date.now();
  try{
    const detail=await fn();
    results.push({name,status:'PASS',ms:Date.now()-start,detail});
    console.log('PASS',name,detail||'');
  }catch(e){
    results.push({name,status:'FAIL',ms:Date.now()-start,error:String(e?.stack||e)});
    console.error('FAIL',name,e);
    throw e;
  }
}

await run('pc_tutorial_guard_first_capture',async()=>{
  const context=await makeContext();
  const page=await context.newPage();
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await gotoHome(page);
  await installSpies(page);
  await startNewGame(page);
  await drivePcTutorial(page);
  await page.screenshot({path:path.join(artifacts,'pc-tutorial-complete.png'),fullPage:true});
  await page.locator('#tutorialGoV2').click();
  const startEv=await waitStored(currentScenario,'stage1_attempt_start');
  assert(startEv.params.first_instrumented_attempt===true,'first instrumented attempt not classified true');
  const attemptId=startEv.params.attempt_id;
  await captureLoopKeyboard(page,'Space');
  const cap=await waitStored(currentScenario,'stage1_first_capture',e=>e.params.attempt_id===attemptId);
  const guard=await waitStored(currentScenario,'stage1_guard_end',e=>e.params.attempt_id===attemptId&&e.params.reason==='first_capture');
  assert(cap.params.attempt_id===guard.params.attempt_id,'attempt ID mismatch between capture and guard end');
  await sleep(650);
  let shots=await page.evaluate(()=>window.__cmhTest?.shots||[]);
  const guardTrack=await runtimeTrack(page,'stage1_guard_end');
  assert(guardTrack,'runtime guard-end track missing');
  assert(shots.every(t=>t-guardTrack.t>=850),'projectile fired too soon after first-capture guard end');
  const firstShot=await waitForShot(page,4500);
  assert(firstShot!==null,'boss did not resume projectile firing after guard');
  assert(firstShot-guardTrack.t>=850,`post-guard projectile delay too short: ${Math.round(firstShot-guardTrack.t)}ms`);
  await flush(page);
  assert(scenarioEvents(currentScenario,'stage1_first_capture').filter(e=>e.params.attempt_id===attemptId).length===1,'duplicate first-capture event');
  assert(errors.length===0,'page errors: '+errors.join(' | '));
  await page.screenshot({path:path.join(artifacts,'pc-stage1-first-capture.png'),fullPage:true});
  await context.close();
  return {attemptId,guardReason:guard.params.reason,postGuardShotMs:Math.round(firstShot-guardTrack.t)};
});

await run('pc_keymap_retract',async()=>{
  const context=await makeContext();
  const page=await context.newPage();
  await gotoHome(page,{tutorialComplete:true});
  await page.locator('#settingsBtn').click();
  await page.locator('#keyMappingBtn').click();
  const row=page.locator('.keymap-row').filter({hasText:'CAPTURE'});
  await row.locator('.keymap-key').first().click();
  await page.keyboard.press('KeyF');
  assert((await row.textContent()).includes('F'),'CAPTURE remap to F not visible');
  await page.locator('#keymapBack').click();
  await page.locator('#settingsClose').click();
  await installSpies(page);
  await startNewGame(page);
  const startEv=await waitStored(currentScenario,'stage1_attempt_start');
  await page.keyboard.down('KeyF');
  await holdKey(page,'ArrowDown',230);
  await page.keyboard.up('KeyF');
  const end=Date.now()+2500;let retracted=false;
  while(Date.now()<end){
    const spy=await page.evaluate(()=>window.__cmhTest||{});
    const toast=await page.locator('#statusToast').textContent().catch(()=>'');
    if((spy.retractCalls||0)>0||String(toast).includes('라인 회수')){retracted=true;break}
    await sleep(80);
  }
  assert(retracted,'mapped CAPTURE release did not trigger RETRACT');
  assert(scenarioEvents(currentScenario,'stage1_first_capture').length===0,'retracted line incorrectly counted as first capture');
  await captureLoopKeyboard(page,'KeyF');
  const cap=await waitStored(currentScenario,'stage1_first_capture',e=>e.params.attempt_id===startEv.params.attempt_id);
  assert(cap.params.input_mode==='keyboard','remapped capture input mode wrong');
  await context.close();
  return {remapped:'F',retract:true,firstCaptureAfterRemap:true};
});

await run('mobile_tutorial_capture_toggle',async()=>{
  const context=await makeContext({viewport:{width:844,height:390},isMobile:true,hasTouch:true,userAgent:'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/125 Mobile Safari/537.36'});
  const page=await context.newPage();
  await gotoHome(page);
  await startNewGame(page);
  await driveMobileTutorial(page);
  await page.screenshot({path:path.join(artifacts,'mobile-tutorial-complete.png'),fullPage:true});
  await page.locator('#tutorialGoV2').click();
  await waitStored(currentScenario,'stage1_attempt_start');
  await page.locator('#captureTouchBtn').click();
  assert((await page.locator('#captureTouchBtn').textContent()).includes('ON'),'mobile Stage 1 CAPTURE did not toggle ON');
  await page.locator('#captureTouchBtn').click();
  assert(!(await page.locator('#captureTouchBtn').textContent()).includes('ON'),'mobile Stage 1 CAPTURE did not toggle OFF');
  await context.close();
  return {tutorial:'MOVE→DRAW→CAPTURE→DONE',captureToggle:true};
});

await run('guard_pause_visibility_timeout',async()=>{
  const context=await makeContext();
  const page=await context.newPage();
  await gotoHome(page,{tutorialComplete:true});
  await installSpies(page);
  await startNewGame(page);
  const startEv=await waitStored(currentScenario,'stage1_attempt_start');
  await sleep(3000);
  await page.locator('#pauseBtn').click();
  await sleep(5000);
  assert(!scenarioEvents(currentScenario,'stage1_guard_end').some(e=>e.params.reason==='timeout'),'guard expired while explicit pause was open');
  await resumePause(page);
  await sleep(2000);
  const other=await context.newPage();
  await other.goto('about:blank');
  await other.bringToFront();
  await sleep(3500);
  await page.bringToFront();
  await sleep(500);
  const hiddenEvents=scenarioEvents(currentScenario,'page_hidden');
  if(await page.locator('#modalLayer').isVisible().catch(()=>false))await resumePause(page);
  await sleep(7500);
  assert(!scenarioEvents(currentScenario,'stage1_guard_end').some(e=>e.params.reason==='timeout'),'guard expired before 15s active play after pause/visibility freeze');
  const timeoutEv=await waitStored(currentScenario,'stage1_guard_end',e=>e.params.attempt_id===startEv.params.attempt_id&&e.params.reason==='timeout',5000);
  const guardTrack=await runtimeTrack(page,'stage1_guard_end');
  const firstShot=await waitForShot(page,4500);
  assert(guardTrack,'timeout guard runtime track missing');
  assert(firstShot!==null,'projectiles did not resume after timeout guard');
  assert(firstShot-guardTrack.t>=850,'projectile resumed before 900ms post-timeout delay');
  await other.close();await context.close();
  return {guardReason:timeoutEv.params.reason,hiddenEventObserved:hiddenEvents.length>0,postGuardShotMs:Math.round(firstShot-guardTrack.t)};
});

await run('continue_load_attempt_linking',async()=>{
  const context=await makeContext();
  const page=await context.newPage();
  await gotoHome(page,{tutorialComplete:true});
  await installSpies(page);
  await startNewGame(page);
  const a1=await waitStored(currentScenario,'stage1_attempt_start');
  assert(a1.params.first_instrumented_attempt===true,'attempt 1 should be first_instrumented_attempt');
  await page.evaluate(()=>{failLife('BROWSER_TEST_A');failLife('BROWSER_TEST_B');failLife('BROWSER_TEST_C')});
  await page.waitForSelector('.game-over-title');
  const end1=await waitStored(currentScenario,'stage1_attempt_end',e=>e.params.attempt_id===a1.params.attempt_id);
  assert(end1.params.outcome==='gameover','gameover attempt outcome wrong');
  assert(scenarioEvents(currentScenario,'stage1_first_death').filter(e=>e.params.attempt_id===a1.params.attempt_id).length===1,'first death duplicated');
  const free=page.locator('#freeContinue');
  assert(await free.isVisible(),'free Continue button missing');
  await free.click();
  const a2=await waitStored(currentScenario,'stage1_attempt_start',e=>e.params.attempt_id!==a1.params.attempt_id);
  assert(a2.params.start_source==='continue_free','Continue start_source wrong');
  assert(a2.params.first_instrumented_attempt===false,'Continue incorrectly classified as first attempt');
  assert(a2.params.attempt_id!==a1.params.attempt_id,'Continue reused attempt ID');
  await sleep(500);
  assert(!scenarioEvents(currentScenario,'stage1_guard_end').some(e=>e.params.attempt_id===a2.params.attempt_id),'Continue attempt guard was not reset');

  await page.evaluate(()=>{failLife('BROWSER_TEST_D');failLife('BROWSER_TEST_E');failLife('BROWSER_TEST_F')});
  await page.waitForSelector('.game-over-title');
  await page.locator('#gameoverLoad').click();
  await chooseFirstSlot(page);
  const a3=await waitStored(currentScenario,'stage1_attempt_start',e=>![a1.params.attempt_id,a2.params.attempt_id].includes(e.params.attempt_id));
  assert(a3.params.start_source==='load_save','Load start_source wrong');
  assert(a3.params.first_instrumented_attempt===false,'Load incorrectly classified as first attempt');

  await page.evaluate(()=>recordStage1Clear({kind:'character',value:80,label:'CHAR'}));
  const clear=await waitStored(currentScenario,'stage1_clear',e=>e.params.attempt_id===a3.params.attempt_id);
  await page.evaluate(()=>startStage(2,false));
  const s2=await waitStored(currentScenario,'stage2_entry');
  assert(s2.params.previous_stage1_attempt_id===clear.params.attempt_id,'Stage 1 clear → Stage 2 attempt link mismatch');
  const end3=await waitStored(currentScenario,'stage1_attempt_end',e=>e.params.attempt_id===a3.params.attempt_id);
  assert(end3.params.outcome==='next_stage','Stage 1 next-stage attempt outcome wrong');
  await context.close();
  return {attempts:[a1.params.attempt_no,a2.params.attempt_no,a3.params.attempt_no],sources:[a1.params.start_source,a2.params.start_source,a3.params.start_source],stage2Linked:true};
});

await run('stage2_10_browser_regression',async()=>{
  const context=await makeContext();
  const page=await context.newPage();
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await gotoHome(page,{tutorialComplete:true});
  await startNewGame(page);
  await waitStored(currentScenario,'stage1_attempt_start');
  await page.evaluate(()=>startStage(2,false));
  await page.waitForFunction(()=>document.querySelector('#stageLabel')?.textContent==='2');

  const beforeArea=parseFloat((await page.locator('#areaLabel').textContent()).replace('%',''))||0;
  const beforeScore=Number((await page.locator('#scoreLabel').textContent()).replace(/[^0-9]/g,''))||0;
  let captured=false;
  for(let i=0;i<3&&!captured;i++){
    await captureLoopKeyboard(page,'Space');
    await sleep(400);
    const area=parseFloat((await page.locator('#areaLabel').textContent()).replace('%',''))||0;
    if(area>beforeArea)captured=true;
  }
  assert(captured,'Stage 2 actual keyboard CAPTURE failed in browser');
  const afterArea=parseFloat((await page.locator('#areaLabel').textContent()).replace('%',''))||0;
  const afterScore=Number((await page.locator('#scoreLabel').textContent()).replace(/[^0-9]/g,''))||0;
  assert(afterArea>beforeArea,'Stage 2 image reveal AREA did not increase');
  assert(afterScore>=beforeScore,'Stage 2 score regressed after capture');
  await page.screenshot({path:path.join(artifacts,'stage2-after-capture.png'),fullPage:true});

  for(let stage=2;stage<=10;stage++){
    await page.evaluate(s=>startStage(s,false),stage);
    await page.waitForFunction(s=>document.querySelector('#stageLabel')?.textContent===String(s),stage);
    assert(await page.locator('#gameCanvas').isVisible(),`Stage ${stage} canvas not visible`);
    await sleep(120);
  }

  await page.evaluate(()=>startStage(2,false));
  await page.waitForFunction(()=>document.querySelector('#stageLabel')?.textContent==='2');
  await page.evaluate(()=>showClearModal(80));
  assert(await page.locator('.clear-review').isVisible(),'80% clear modal missing');
  assert(await page.locator('#clearBonusVideo').count()===0,'80% unexpectedly shows bonus video');
  assert(await page.locator('#bankedNextStage').count()===0,'CLEAR BANK unexpectedly active');
  await page.locator('#keepBtn').click();

  await page.evaluate(()=>showClearModal(90));
  assert(await page.locator('#clearBonusVideo').isVisible(),'90% bonus video element missing');
  const src=await page.locator('#clearBonusVideo').getAttribute('src');
  assert(src?.includes('stage02_service.mp4'),'90% bonus video source wrong');
  assert(await page.locator('#bonusToggleBtn').isVisible(),'90% bonus still/video toggle missing');
  await page.screenshot({path:path.join(artifacts,'stage2-90-bonus.png'),fullPage:true});
  await page.locator('#keepBtn').click();

  await page.evaluate(()=>showClearModal(99));
  const perfectText=await page.locator('#modalLayer').textContent();
  assert(/PERFECT/i.test(perfectText),'99% PERFECT presentation missing');
  assert(await page.locator('#bankedNextStage').count()===0,'CLEAR BANK unexpectedly active at PERFECT');

  assert(errors.length===0,'browser page errors: '+errors.join(' | '));
  await context.close();
  return {stage2Capture:true,stagesSmoke:'2-10',clear80:true,bonus90:true,perfect99:true,clearBank:false};
});

await run('event_storage_schema_and_legacy_compat',async()=>{
  assert(allEvents.length>0,'mock collector stored no analytics events');
  const required=['stage1_attempt_start','stage1_first_capture','stage1_first_death','stage1_clear','stage1_attempt_end','stage1_guard_end','stage2_entry'];
  for(const name of required)assert(allEvents.some(e=>e.event_name===name),`mock storage missing ${name}`);

  const validDevices=new Set(['desktop','mobile','tablet','unknown']);
  for(const e of allEvents){
    assert(/^[a-z0-9_]{1,48}$/.test(e.event_name),`event_name schema mismatch: ${e.event_name}`);
    assert(String(e.visitor_id||'').length>=6&&String(e.visitor_id||'').length<=80,'visitor_id length mismatch');
    assert(String(e.session_id||'').length>=6&&String(e.session_id||'').length<=80,'session_id length mismatch');
    assert(validDevices.has(e.device),'device schema mismatch: '+e.device);
    assert(Buffer.byteLength(JSON.stringify(e.params||{}),'utf8')<=4096,'params exceeds schema limit');
  }

  const perAttempt=new Map();
  for(const e of allEvents.filter(e=>e.params?.attempt_id)){
    const id=e.params.attempt_id;if(!perAttempt.has(id))perAttempt.set(id,[]);
    perAttempt.get(id).push(e);
  }
  for(const [id,evs] of perAttempt){
    for(const single of ['stage1_first_capture','stage1_first_death','stage1_clear','stage1_attempt_end']){
      assert(evs.filter(e=>e.event_name===single).length<=1,`duplicate ${single} for ${id}`);
    }
  }

  const newNames=new Set(['stage1_attempt_start','stage1_first_capture','stage1_first_death','stage1_clear','stage1_attempt_end','stage1_guard_end','stage2_entry','tutorial_optional_tip']);
  const old=allEvents.filter(e=>!newNames.has(e.event_name));
  const metric=e=>({
    sessions:new Set(e.map(x=>x.session_id)).size,
    visitors:new Set(e.map(x=>x.visitor_id)).size,
    gameStarts:new Set(e.filter(x=>x.event_name==='game_start').map(x=>x.session_id)).size,
    deaths:e.filter(x=>x.event_name==='life_lost').length,
    s1Entrants:new Set(e.filter(x=>x.event_name==='stage_start'&&x.stage===1).map(x=>x.session_id)).size,
    s1Clearers:new Set(e.filter(x=>x.event_name==='stage_milestone'&&x.stage===1&&Number(x.params?.milestone)>=80).map(x=>x.session_id)).size
  });
  const a=metric(allEvents),b=metric(old);
  for(const k of Object.keys(a))assert(a[k]===b[k],`legacy dashboard metric changed by additive events: ${k} ${a[k]} vs ${b[k]}`);

  const adminJs=fs.readFileSync(path.join(root,'admin','admin.js'),'utf8');
  const adminSpecific=required.some(n=>adminJs.includes(n));
  assert(adminSpecific===false,'current admin UI unexpectedly contains unreviewed new-event logic');

  fs.writeFileSync(path.join(artifacts,'browser-validation-report.json'),JSON.stringify({generatedAt:new Date().toISOString(),results,eventCount:allEvents.length,eventCounts:Object.fromEntries([...new Set(allEvents.map(e=>e.event_name))].sort().map(n=>[n,allEvents.filter(e=>e.event_name===n).length])),legacyMetrics:a,currentAdminHasSpecificRetentionView:adminSpecific},null,2));
  return {storedEvents:allEvents.length,attempts:perAttempt.size,legacyMetricsStable:true,currentAdminSpecificRetentionView:false};
});

await browser.close();
await new Promise(resolve=>server.close(resolve));

const failed=results.filter(r=>r.status!=='PASS');
console.log(JSON.stringify({results,eventCount:allEvents.length},null,2));
if(failed.length)process.exit(1);
