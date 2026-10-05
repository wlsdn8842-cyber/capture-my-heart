from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path, old, new, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'safe path transfer patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

rep(Path('game.js'),
    "player:{x:Math.floor(GW/2), y:1, drawing:false, autoRetract:false, safeTransitDir:null, trailStart:{x:Math.floor(GW/2),y:1}, trailPath:[]}",
    "player:{x:Math.floor(GW/2), y:1, drawing:false, autoRetract:false, safeTransitPath:[], safeTransitOrigin:null, safeTransitTarget:null, trailStart:{x:Math.floor(GW/2),y:1}, trailPath:[]}",
    'state player safe path')

rep(Path('game.js'),
    "state.player={x:Math.floor(GW/2),y:1,drawing:false,autoRetract:false,safeTransitDir:null,trailStart:{x:Math.floor(GW/2),y:1},trailPath:[]};",
    "state.player={x:Math.floor(GW/2),y:1,drawing:false,autoRetract:false,safeTransitPath:[],safeTransitOrigin:null,safeTransitTarget:null,trailStart:{x:Math.floor(GW/2),y:1},trailPath:[]};",
    'stage player safe path')

rep(Path('game.js'),
    "state.player={x:px,y:py,drawing:false,autoRetract:false,safeTransitDir:null,trailStart:{x:px,y:py},trailPath:[]};",
    "state.player={x:px,y:py,drawing:false,autoRetract:false,safeTransitPath:[],safeTransitOrigin:null,safeTransitTarget:null,trailStart:{x:px,y:py},trailPath:[]};",
    'tutorial player safe path')

rep(Path('game.js'),
'''function oppositeDir(d){return d==='up'?'down':d==='down'?'up':d==='left'?'right':d==='right'?'left':null}
function safeBoundaryTransferAhead(x,y,dx,dy){
  let nx=x+dx,ny=y+dy,steps=0;
  while(inGrid(nx,ny)&&getCell(nx,ny)===CLAIMED&&steps<Math.max(GW,GH)){
    if(isSafeBoundaryCell(nx,ny))return{x:nx,y:ny,steps:steps+1};
    nx+=dx;ny+=dy;steps++;
  }
  return null;
}
''',
'''function boundaryComponentKeys(x,y){
  const out=new Set();
  if(!isSafeBoundaryCell(x,y))return out;
  const q=[{x,y}];out.add(y*GW+x);
  for(let h=0;h<q.length;h++){
    const cur=q[h];
    for(const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]){
      const nx=cur.x+dx,ny=cur.y+dy,k=ny*GW+nx;
      if(!inGrid(nx,ny)||out.has(k)||getCell(nx,ny)!==CLAIMED||!isSafeBoundaryCell(nx,ny))continue;
      out.add(k);q.push({x:nx,y:ny});
    }
  }
  return out;
}
function reconstructClaimedPath(prev,startKey,endKey){
  const path=[];let k=endKey,guard=GW*GH+4;
  while(k!==startKey&&guard-->0){path.push({x:k%GW,y:Math.floor(k/GW)});k=prev[k]}
  if(k!==startKey)return null;
  path.push({x:startKey%GW,y:Math.floor(startKey/GW)});path.reverse();return path;
}
function findSafeBoundaryPath(x,y,dx,dy){
  const sx=x+dx,sy=y+dy;
  if(!inGrid(sx,sy)||getCell(sx,sy)!==CLAIMED||isSafeBoundaryCell(sx,sy))return null;
  const origin=boundaryComponentKeys(x,y),total=GW*GH,prev=new Int32Array(total);prev.fill(-1);
  const startKey=sy*GW+sx,q=[startKey];prev[startKey]=startKey;
  for(let h=0;h<q.length;h++){
    const k=q[h],cx=k%GW,cy=Math.floor(k/GW);
    if(isSafeBoundaryCell(cx,cy)&&!origin.has(k))return reconstructClaimedPath(prev,startKey,k);
    for(const [mx,my] of [[1,0],[-1,0],[0,1],[0,-1]]){
      const nx=cx+mx,ny=cy+my;
      if(!inGrid(nx,ny)||getCell(nx,ny)!==CLAIMED)continue;
      const nk=ny*GW+nx;
      if(prev[nk]!==-1||origin.has(nk))continue;
      prev[nk]=k;q.push(nk);
    }
  }
  return null;
}
function findNearestSafeBoundaryPath(x,y){
  if(!inGrid(x,y)||getCell(x,y)!==CLAIMED)return null;
  if(isSafeBoundaryCell(x,y))return[];
  const total=GW*GH,prev=new Int32Array(total);prev.fill(-1),startKey=y*GW+x,q=[startKey];prev[startKey]=startKey;
  for(let h=0;h<q.length;h++){
    const k=q[h],cx=k%GW,cy=Math.floor(k/GW);
    if(k!==startKey&&isSafeBoundaryCell(cx,cy))return reconstructClaimedPath(prev,startKey,k).slice(1);
    for(const [mx,my] of [[1,0],[-1,0],[0,1],[0,-1]]){
      const nx=cx+mx,ny=cy+my;
      if(!inGrid(nx,ny)||getCell(nx,ny)!==CLAIMED)continue;
      const nk=ny*GW+nx;
      if(prev[nk]!==-1)continue;
      prev[nk]=k;q.push(nk);
    }
  }
  return null;
}
function clearSafeTransit(p=state.player){
  p.safeTransitPath=[];p.safeTransitOrigin=null;p.safeTransitTarget=null;
}
function stepSafeTransit(p){
  if(!Array.isArray(p.safeTransitPath)||!p.safeTransitPath.length)return false;
  let next=p.safeTransitPath[0];
  if(!next||getCell(next.x,next.y)!==CLAIMED){
    const recovery=findNearestSafeBoundaryPath(p.x,p.y);
    if(recovery&&recovery.length){
      p.safeTransitPath=recovery;p.safeTransitTarget=recovery[recovery.length-1];next=p.safeTransitPath[0];
      track('safe_path_transfer_reroute',{stage:state.stage,remaining:p.safeTransitPath.length});
    }else{
      const o=p.safeTransitOrigin;
      if(o&&inGrid(o.x,o.y)&&getCell(o.x,o.y)===CLAIMED){p.x=o.x;p.y=o.y}
      clearSafeTransit(p);
      track('safe_path_transfer_abort',{stage:state.stage,reason:'route_changed'});
      return true;
    }
  }
  p.safeTransitPath.shift();
  p.x=next.x;p.y=next.y;p.trailStart={x:p.x,y:p.y};p.trailPath=[];
  if(!p.safeTransitPath.length){
    const target=p.safeTransitTarget;
    clearSafeTransit(p);
    track('safe_path_transfer_end',{stage:state.stage,x:p.x,y:p.y,target_x:target?.x??p.x,target_y:target?.y??p.y});
  }
  return true;
}
''',
'safe path helpers')

rep(Path('game.js'),
'''function movePlayer(){
  const p=state.player;if(p.autoRetract)return;
  const d=direction();if(!d)return;
  const [dx,dy]=dirVec(d),nx=p.x+dx,ny=p.y+dy;
  if(!inGrid(nx,ny))return;
  const target=getCell(nx,ny), capture=input.capture;

  if(!p.drawing){
    if(p.safeTransitDir){
      const reverse=oppositeDir(p.safeTransitDir);
      if(d!==p.safeTransitDir&&d!==reverse)return;
      if(target!==CLAIMED)return;
      p.x=nx;p.y=ny;p.trailStart={x:nx,y:ny};p.trailPath=[];
      if(isSafeBoundaryCell(nx,ny)){
        const travelDir=p.safeTransitDir;p.safeTransitDir=null;
        track('safe_boundary_transfer_end',{stage:state.stage,direction:travelDir,x:nx,y:ny});
      }
      return;
    }
    if(target===CLAIMED&&isSafeBoundaryCell(nx,ny)){
      p.x=nx;p.y=ny;p.trailStart={x:nx,y:ny};p.trailPath=[];
    } else if(target===CLAIMED&&isSafeBoundaryCell(p.x,p.y)){
      const destination=safeBoundaryTransferAhead(p.x,p.y,dx,dy);
      if(destination){
        if(input.capture){
          input.capture=false;
          if(mobileUXActive())resetMobileCaptureLock('safe_transfer');else captureNeedsRelease=true;
        }
        p.safeTransitDir=d;p.x=nx;p.y=ny;p.trailStart={x:nx,y:ny};p.trailPath=[];
        track('safe_boundary_transfer_start',{stage:state.stage,direction:d,to_x:destination.x,to_y:destination.y,distance:destination.steps});
      }
    } else if(target===UNCLAIMED&&capture){
      p.drawing=true;p.autoRetract=false;p.safeTransitDir=null;p.trailStart={x:p.x,y:p.y};p.x=nx;p.y=ny;
      setCell(nx,ny,TRAIL);p.trailPath=[{x:nx,y:ny}];
      audio.beep(520,.06,'square',.025);
    }
    return;
  }
''',
'''function movePlayer(){
  const p=state.player;if(p.autoRetract)return;
  if(stepSafeTransit(p))return;
  const d=direction();if(!d)return;
  const [dx,dy]=dirVec(d),nx=p.x+dx,ny=p.y+dy;
  if(!inGrid(nx,ny))return;
  const target=getCell(nx,ny), capture=input.capture;

  if(!p.drawing){
    if(target===CLAIMED&&isSafeBoundaryCell(nx,ny)){
      p.x=nx;p.y=ny;p.trailStart={x:nx,y:ny};p.trailPath=[];
    } else if(target===CLAIMED&&isSafeBoundaryCell(p.x,p.y)){
      const path=findSafeBoundaryPath(p.x,p.y,dx,dy);
      if(path&&path.length){
        if(input.capture){
          input.capture=false;
          if(mobileUXActive())resetMobileCaptureLock('safe_path_transfer');else captureNeedsRelease=true;
        }
        p.safeTransitOrigin={x:p.x,y:p.y};
        p.safeTransitPath=path;
        p.safeTransitTarget=path[path.length-1];
        track('safe_path_transfer_start',{stage:state.stage,direction:d,to_x:p.safeTransitTarget.x,to_y:p.safeTransitTarget.y,distance:path.length});
      }
    } else if(target===UNCLAIMED&&capture){
      p.drawing=true;p.autoRetract=false;clearSafeTransit(p);p.trailStart={x:p.x,y:p.y};p.x=nx;p.y=ny;
      setCell(nx,ny,TRAIL);p.trailPath=[{x:nx,y:ny}];
      audio.beep(520,.06,'square',.025);
    }
    return;
  }
''',
'safe path movement')

rep(Path('game.js'),
"function clearTrail(){for(let i=0;i<grid.length;i++)if(grid[i]===TRAIL)grid[i]=UNCLAIMED;const p=state.player;p.x=p.trailStart.x;p.y=p.trailStart.y;p.drawing=false;p.autoRetract=false;p.safeTransitDir=null;p.trailPath=[];if(mobileUXActive())resetMobileCaptureLock('line_reset');rebuildVisualLayers()}",
"function clearTrail(){for(let i=0;i<grid.length;i++)if(grid[i]===TRAIL)grid[i]=UNCLAIMED;const p=state.player;p.x=p.trailStart.x;p.y=p.trailStart.y;p.drawing=false;p.autoRetract=false;clearSafeTransit(p);p.trailPath=[];if(mobileUXActive())resetMobileCaptureLock('line_reset');rebuildVisualLayers()}",
'clear safe path on line reset')

rep(Path('game.js'),
'''function drawPlayerVisual(c,p,t){
  const px=(p.x+.5)*CELL,py=(p.y+.5)*CELL;
  const retract=p.autoRetract,draw=p.drawing&&!retract;
  const col=retract?'#ffd45d':draw?'#ff4fa3':'#42e6ff';
''',
'''function drawSafeTransitPath(c,t){
  const p=state.player,path=p?.safeTransitPath;
  if(!Array.isArray(path)||!path.length)return;
  const pulse=.72+.22*Math.sin(t*.012),target=p.safeTransitTarget||path[path.length-1];
  c.save();
  c.lineCap='round';c.lineJoin='round';
  c.setLineDash([7,5]);c.lineDashOffset=-(t*.03)%12;
  c.strokeStyle=`rgba(255,213,74,${pulse})`;c.lineWidth=3.2;
  c.shadowBlur=14;c.shadowColor='#ffd54a';
  c.beginPath();c.moveTo((p.x+.5)*CELL,(p.y+.5)*CELL);
  for(const q of path)c.lineTo((q.x+.5)*CELL,(q.y+.5)*CELL);
  c.stroke();
  if(target){
    c.setLineDash([]);c.fillStyle='rgba(255,213,74,.22)';
    c.strokeStyle='#ffe682';c.lineWidth=2;
    c.beginPath();c.arc((target.x+.5)*CELL,(target.y+.5)*CELL,7+Math.sin(t*.015)*1.5,0,Math.PI*2);c.fill();c.stroke();
  }
  c.restore();
}
function drawPlayerVisual(c,p,t){
  const px=(p.x+.5)*CELL,py=(p.y+.5)*CELL;
  const retract=p.autoRetract,draw=p.drawing&&!retract,transfer=Array.isArray(p.safeTransitPath)&&p.safeTransitPath.length>0;
  const col=transfer?'#ffd54a':retract?'#ffd45d':draw?'#ff4fa3':'#42e6ff';
''',
'safe path visual')

rep(Path('game.js'),
'''  }c.restore();
  for(const it of state.items){''',
'''  }c.restore();
  drawSafeTransitPath(c,t);
  for(const it of state.items){''',
'render safe path visual')

rep(Path('index.html'),
    '<div class="version">v0.14.2 safe boundary transfer</div>',
    '<div class="version">v0.14.3 safe path transfer</div>',
    'version label')
rep(Path('config.js'),"VERSION: '0.14.2'","VERSION: '0.14.3'",'config version')
rep(Path('sw.js'),"cmh-core-v0.14.2","cmh-core-v0.14.3",'service worker cache version')

print('v0.14.3 safe path transfer applied')
