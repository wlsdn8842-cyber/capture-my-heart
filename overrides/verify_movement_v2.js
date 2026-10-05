const fs=require('fs'),vm=require('vm');
const path=process.argv[2];
const src=fs.readFileSync(path,'utf8');

function getFn(name){
  const start=src.indexOf(`function ${name}(`);
  if(start<0) throw new Error(`missing function ${name}`);
  const brace=src.indexOf('{',start);let depth=0;
  for(let i=brace;i<src.length;i++){
    if(src[i]==='{')depth++;
    else if(src[i]==='}') {depth--; if(depth===0)return src.slice(start,i+1)}
  }
  throw new Error(`unterminated function ${name}`);
}
function assert(cond,msg){if(!cond)throw new Error(msg)}

function testBoundary(){
  const code=[getFn('isSafeBoundaryCell')].join('\n');
  const GW=8,GH=8,UNCLAIMED=0,CLAIMED=1,grid=new Int8Array(GW*GH).fill(CLAIMED);
  const ctx={GW,GH,UNCLAIMED,CLAIMED,inGrid:(x,y)=>x>=0&&y>=0&&x<GW&&y<GH,getCell:(x,y)=>grid[y*GW+x]};
  vm.createContext(ctx);vm.runInContext(code,ctx);
  assert(ctx.isSafeBoundaryCell(3,3)===false,'claimed interior must not be safe boundary');
  grid[3*GW+4]=UNCLAIMED;
  assert(ctx.isSafeBoundaryCell(3,3)===true,'claimed cell adjacent to unclaimed must be safe boundary');
}

function testMovePlayer(){
  const code=[getFn('isSafeBoundaryCell'),getFn('movePlayer')].join('\n');
  const GW=8,GH=8,UNCLAIMED=0,CLAIMED=1,TRAIL=2,grid=new Int8Array(GW*GH).fill(CLAIMED);
  const state={player:{x:3,y:3,drawing:false,autoRetract:false,trailStart:{x:3,y:3},trailPath:[]}};
  const input={capture:false};let dir='right',captureCalls=0,failCalls=0;
  const ctx={GW,GH,UNCLAIMED,CLAIMED,TRAIL,state,input,grid,
    inGrid:(x,y)=>x>=0&&y>=0&&x<GW&&y<GH,
    getCell:(x,y)=>grid[y*GW+x],setCell:(x,y,v)=>grid[y*GW+x]=v,
    direction:()=>dir,dirVec:d=>d==='right'?[1,0]:d==='left'?[-1,0]:d==='up'?[0,-1]:[0,1],
    stepSafeTransit:()=>false,
    armNearestSafeBoxTransfer:()=>false,
    clearSafeTransit:p=>{p.safeTransitPath=[];p.safeTransitOrigin=null;p.safeTransitTarget=null},
    audio:{beep:()=>{}},failLife:()=>{failCalls++},captureRegion:()=>{captureCalls++}
  };
  vm.createContext(ctx);vm.runInContext(code,ctx);
  ctx.movePlayer();
  assert(state.player.x===3&&state.player.y===3,'safe movement must not enter claimed interior');
  grid[3*GW+5]=UNCLAIMED;ctx.movePlayer();
  assert(state.player.x===4,'safe movement should follow claimed boundary');
  ctx.movePlayer();
  assert(state.player.x===4,'must not leave boundary without capture');
  input.capture=true;ctx.movePlayer();
  assert(state.player.x===5&&state.player.drawing&&grid[3*GW+5]===TRAIL,'capture must allow leaving boundary into unclaimed');
  assert(captureCalls===0&&failCalls===0,'unexpected capture/fail during movement setup');
}

function testDisarm(){
  const code=getFn('disarmCaptureAfterComplete');
  const state={stage:3};const input={capture:true};let resetReason=null;let mobile=false;
  const ctx={state,input,captureNeedsRelease:false,mobileUXActive:()=>mobile,resetMobileCaptureLock:r=>{resetReason=r},track:()=>{}};
  vm.createContext(ctx);vm.runInContext(code,ctx);
  ctx.disarmCaptureAfterComplete('capture_complete');
  assert(input.capture===false,'desktop capture must turn off after completing line');
  assert(ctx.captureNeedsRelease===true,'desktop capture must require Space release before rearm');
  input.capture=true;ctx.captureNeedsRelease=true;mobile=true;ctx.disarmCaptureAfterComplete('capture_complete');
  assert(ctx.captureNeedsRelease===false&&resetReason==='capture_complete','mobile capture lock must reset on completion');
}

function testSpawn(){
  const code=[getFn('randomUnclaimedCell'),getFn('fairRandomSpawnCell'),getFn('spawnEnemies')].join('\n');
  const GW=80,GH=50,CELL=10,UNCLAIMED=0,CLAIMED=1,grid=new Int8Array(GW*GH).fill(UNCLAIMED);
  const state={stage:6,player:{x:40,y:1},enemies:[]};const tracks=[];
  const STAGES=[];STAGES[6]={speed:143,minions:3,chase:.19,shots:1700};
  const ctx={GW,GH,CELL,UNCLAIMED,CLAIMED,grid,state,STAGES,
    getCell:(x,y)=>grid[y*GW+x],dist:(a,b,c,d)=>Math.hypot(a-c,b-d),track:(n,p)=>tracks.push([n,p]),Math};
  vm.createContext(ctx);vm.runInContext(code,ctx);ctx.spawnEnemies();
  assert(state.enemies.length===4,'boss + minion count mismatch');
  const cells=state.enemies.map(e=>({x:e.x/CELL-.5,y:e.y/CELL-.5}));
  assert(Math.hypot(cells[0].x-state.player.x,cells[0].y-state.player.y)>=18,'boss spawned too close to player');
  for(let i=1;i<cells.length;i++){
    assert(Math.hypot(cells[i].x-state.player.x,cells[i].y-state.player.y)>=13,'minion spawned too close to player');
    for(let j=0;j<i;j++)assert(Math.hypot(cells[i].x-cells[j].x,cells[i].y-cells[j].y)>=10,'enemy spawns not sufficiently separated');
  }
  assert(tracks.some(x=>x[0]==='fair_spawn_layout'),'spawn layout analytics missing');
}

try{
  testBoundary();console.log('PASS boundary-only movement helper');
  testMovePlayer();console.log('PASS safe-boundary/capture movement behavior');
  testDisarm();console.log('PASS capture auto-off desktop/mobile behavior');
  testSpawn();console.log('PASS fair random boss/minion spawn behavior');
  console.log('ALL MOVEMENT V2 BEHAVIOR TESTS PASS');
}catch(e){console.error('FAIL',e.message);process.exit(1)}
