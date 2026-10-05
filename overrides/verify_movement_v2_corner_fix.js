const fs=require('fs'),vm=require('vm');
const path=process.argv[2];
const src=fs.readFileSync(path,'utf8');

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
function assert(cond,msg){if(!cond)throw new Error(msg)}

const GW=7,GH=7,UNCLAIMED=0,CLAIMED=1;
function makeCtx(){
  const grid=new Int8Array(GW*GH).fill(CLAIMED);
  const ctx={GW,GH,UNCLAIMED,CLAIMED,grid,
    inGrid:(x,y)=>x>=0&&y>=0&&x<GW&&y<GH,
    getCell:(x,y)=>grid[y*GW+x]};
  vm.createContext(ctx);vm.runInContext(getFn('isSafeBoundaryCell'),ctx);
  return ctx;
}

try{
  let ctx=makeCtx();
  assert(ctx.isSafeBoundaryCell(3,3)===false,'deep claimed interior must stay blocked');

  ctx=makeCtx();
  ctx.grid[3*GW+4]=UNCLAIMED;
  assert(ctx.isSafeBoundaryCell(3,3)===true,'orthogonal boundary must remain traversable');

  ctx=makeCtx();
  ctx.grid[4*GW+4]=UNCLAIMED;
  assert(ctx.isSafeBoundaryCell(3,3)===true,'diagonal-only corner boundary must be traversable');

  console.log('ALL MOVEMENT V2 CORNER TESTS PASS');
}catch(e){console.error('FAIL',e.message);process.exit(1)}
