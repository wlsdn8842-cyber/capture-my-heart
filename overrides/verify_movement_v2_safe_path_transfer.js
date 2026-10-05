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

const GW=12,GH=12,UNCLAIMED=0,CLAIMED=1,TRAIL=2;
const grid=new Int8Array(GW*GH).fill(CLAIMED);

// Origin pocket near top-left, target pocket lower-right and not aligned.
grid[1*GW+2]=UNCLAIMED;
grid[9*GW+9]=UNCLAIMED;

const state={stage:1,player:{
  x:2,y:2,drawing:false,autoRetract:false,
  safeTransitPath:[],safeTransitOrigin:null,safeTransitTarget:null,
  trailStart:{x:2,y:2},trailPath:[]
}};
const input={capture:false,touchDir:null,dirs:new Set(),lastDir:'down'};
let dir='down';const tracks=[];
const ctx={GW,GH,UNCLAIMED,CLAIMED,TRAIL,grid,state,input,captureNeedsRelease:false,
  inGrid:(x,y)=>x>=0&&y>=0&&x<GW&&y<GH,
  getCell:(x,y)=>grid[y*GW+x],setCell:(x,y,v)=>grid[y*GW+x]=v,
  direction:()=>dir,
  dirVec:d=>d==='up'?[0,-1]:d==='down'?[0,1]:d==='left'?[-1,0]:[1,0],
  audio:{beep:()=>{}},
  failLife:()=>{throw new Error('unexpected failLife')},
  captureRegion:()=>{throw new Error('unexpected captureRegion')},
  mobileUXActive:()=>false,resetMobileCaptureLock:()=>{},
  track:(n,p)=>tracks.push([n,p])
};

vm.createContext(ctx);
const names=[
  'isSafeBoundaryCell','boundaryComponentKeys','reconstructClaimedPath',
  'findSafeBoundaryPath','findNearestSafeBoundaryPath','clearSafeTransit',
  'stepSafeTransit','movePlayer'
];
vm.runInContext(names.map(getFn).join('\n'),ctx);

try{
  const path=ctx.findSafeBoundaryPath(2,2,0,1);
  assert(path&&path.length>4,'must find a safe path to a non-aligned boundary');
  const end=path[path.length-1];
  assert(ctx.isSafeBoundaryCell(end.x,end.y),'path must end on another boundary');
  assert(path.some(p=>p.x!==2),'path must be able to curve instead of requiring one straight line');

  ctx.movePlayer();
  assert(state.player.safeTransitPath.length>0,'moving into safe interior should arm the safe path');
  assert(tracks.some(x=>x[0]==='safe_path_transfer_start'),'safe path start analytics missing');

  dir=null;
  let guard=200;
  while(state.player.safeTransitPath.length&&guard-->0)ctx.movePlayer();
  assert(guard>0,'safe path auto-move did not complete');
  assert(ctx.isSafeBoundaryCell(state.player.x,state.player.y),'auto transfer must finish on a boundary');
  assert(tracks.some(x=>x[0]==='safe_path_transfer_end'),'safe path end analytics missing');

  assert(src.includes('function drawSafeTransitPath('),'safe path visual function missing');
  assert(src.includes('#ffd54a'),'safe path must use distinct gold color');
  assert(src.includes('drawSafeTransitPath(c,t)'),'safe path visual must be rendered in the world');

  console.log('ALL SAFE PATH TRANSFER TESTS PASS');
}catch(e){console.error('FAIL',e.message);process.exit(1)}
