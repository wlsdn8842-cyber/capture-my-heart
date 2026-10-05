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

const GW=14,GH=12,UNCLAIMED=0,CLAIMED=1;
const grid=new Int8Array(GW*GH).fill(CLAIMED);

// Origin box near player, one near target to the right, one farther lower-right.
grid[1*GW+2]=UNCLAIMED;
grid[3*GW+9]=UNCLAIMED;
grid[9*GW+11]=UNCLAIMED;

const state={stage:1,player:{
  x:2,y:2,drawing:false,autoRetract:false,
  safeTransitPath:[],safeTransitOrigin:null,safeTransitTarget:null,
  trailStart:{x:2,y:2},trailPath:[]
}};
const input={capture:false};
const tracks=[];
const ctx={GW,GH,UNCLAIMED,CLAIMED,grid,state,input,captureNeedsRelease:false,
  inGrid:(x,y)=>x>=0&&y>=0&&x<GW&&y<GH,
  getCell:(x,y)=>grid[y*GW+x],
  mobileUXActive:()=>false,resetMobileCaptureLock:()=>{},
  track:(n,p)=>tracks.push([n,p]),
  toast:()=>{}
};
vm.createContext(ctx);
const names=[
  'isSafeBoundaryCell','boundaryComponentKeys','reconstructClaimedPath',
  'findNearestSafeBoundaryPath','findNearestDifferentBoundaryPath',
  'clearSafeTransit','armNearestSafeBoxTransfer'
];
vm.runInContext(names.map(getFn).join('\n'),ctx);

try{
  const path=ctx.findNearestDifferentBoundaryPath(2,2);
  assert(path&&path.length,'must find another boundary box');
  const end=path[path.length-1];
  const near=Math.hypot(end.x-9,end.y-3),far=Math.hypot(end.x-11,end.y-9);
  assert(near<far,'must choose the nearest different box, not a farther one');

  const armed=ctx.armNearestSafeBoxTransfer('blocked_move');
  assert(armed===true,'blocked move must arm nearest-box rescue');
  assert(state.player.safeTransitPath.length>0,'nearest-box rescue path missing');
  assert(tracks.some(x=>x[0]==='safe_box_rescue_start'),'nearest-box rescue analytics missing');

  // Simulate boss/territory change leaving player inside claimed interior.
  ctx.clearSafeTransit(state.player);
  state.player.x=6;state.player.y=6;
  assert(ctx.isSafeBoundaryCell(6,6)===false,'test player should be inside claimed interior');
  const interiorArmed=ctx.armNearestSafeBoxTransfer('interior_stranded');
  assert(interiorArmed===true,'interior stranded player must be rescued to nearest boundary');
  assert(state.player.safeTransitPath.length>0,'interior rescue path missing');

  console.log('ALL NEAREST BOX RESCUE TESTS PASS');
}catch(e){console.error('FAIL',e.message);process.exit(1)}
