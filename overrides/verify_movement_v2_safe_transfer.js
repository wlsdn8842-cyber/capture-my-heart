const fs=require('fs'),vm=require('vm');
const src=fs.readFileSync(process.argv[2],'utf8');

function getFn(name){
  const start=src.indexOf(`function ${name}(`);
  if(start<0)throw new Error(`missing function ${name}`);
  const brace=src.indexOf('{',start);let depth=0;
  for(let i=brace;i<src.length;i++){
    if(src[i]==='{')depth++;
    else if(src[i]==='}'&&--depth===0)return src.slice(start,i+1);
  }
  throw new Error(`unterminated ${name}`);
}
function assert(c,m){if(!c)throw new Error(m)}

const GW=10,GH=11,UNCLAIMED=0,CLAIMED=1,TRAIL=2;
function makeGrid(withDestination=true){
  const g=new Int8Array(GW*GH).fill(CLAIMED);
  g[1*GW+4]=UNCLAIMED;
  if(withDestination)g[8*GW+4]=UNCLAIMED;
  return g;
}
function makeCtx(grid){
  let dir='down';const tracks=[];
  const state={stage:1,mode:'playing',paused:false,player:{x:4,y:2,drawing:false,autoRetract:false,trailStart:{x:4,y:2},trailPath:[],safeTransitDir:null}};
  const input={capture:false,touchDir:null,dirs:new Set(),lastDir:'down'};
  const ctx={GW,GH,UNCLAIMED,CLAIMED,TRAIL,grid,state,input,captureNeedsRelease:false,
    inGrid:(x,y)=>x>=0&&y>=0&&x<GW&&y<GH,
    getCell:(x,y)=>grid[y*GW+x],setCell:(x,y,v)=>grid[y*GW+x]=v,
    direction:()=>dir,dirVec:d=>d==='up'?[0,-1]:d==='down'?[0,1]:d==='left'?[-1,0]:[1,0],
    audio:{beep:()=>{}},failLife:()=>{throw new Error('unexpected failLife')},captureRegion:()=>{throw new Error('unexpected captureRegion')},
    mobileUXActive:()=>false,resetMobileCaptureLock:()=>{},track:(n,p)=>tracks.push([n,p])
  };
  ctx.setDir=d=>{dir=d};ctx.tracks=tracks;
  vm.createContext(ctx);
  vm.runInContext(['isSafeBoundaryCell','oppositeDir','safeBoundaryTransferAhead','movePlayer'].map(getFn).join('\n'),ctx);
  return ctx;
}

try{
  let ctx=makeCtx(makeGrid(true));
  ctx.movePlayer();
  assert(ctx.state.player.y===3,'must enter claimed interior when another boundary exists straight ahead');
  assert(ctx.state.player.safeTransitDir==='down','safe transit direction must lock');

  ctx.setDir('right');ctx.movePlayer();
  assert(ctx.state.player.x===4&&ctx.state.player.y===3,'perpendicular turn must be blocked during safe transfer');

  ctx.setDir('down');
  ctx.movePlayer();ctx.movePlayer();ctx.movePlayer();ctx.movePlayer();
  assert(ctx.state.player.y===7,'must reach destination boundary');
  assert(ctx.state.player.safeTransitDir===null,'safe transfer must end on destination boundary');
  assert(ctx.tracks.some(x=>x[0]==='safe_boundary_transfer_start'),'start analytics missing');
  assert(ctx.tracks.some(x=>x[0]==='safe_boundary_transfer_end'),'end analytics missing');

  ctx=makeCtx(makeGrid(true));
  ctx.movePlayer();ctx.setDir('up');ctx.movePlayer();
  assert(ctx.state.player.y===2&&ctx.state.player.safeTransitDir===null,'reverse must return to origin boundary and end transfer');

  ctx=makeCtx(makeGrid(false));
  ctx.movePlayer();
  assert(ctx.state.player.y===2&&ctx.state.player.safeTransitDir===null,'must not enter claimed interior without a boundary ahead');

  console.log('ALL SAFE BOUNDARY TRANSFER TESTS PASS');
}catch(e){console.error('FAIL',e.message);process.exit(1)}
