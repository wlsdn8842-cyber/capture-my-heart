from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path, old, new, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'safe boundary transfer patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

rep(Path('game.js'),
    "player:{x:Math.floor(GW/2), y:1, drawing:false, autoRetract:false, trailStart:{x:Math.floor(GW/2),y:1}, trailPath:[]}",
    "player:{x:Math.floor(GW/2), y:1, drawing:false, autoRetract:false, safeTransitDir:null, trailStart:{x:Math.floor(GW/2),y:1}, trailPath:[]}",
    'state player safe transit')

rep(Path('game.js'),
    "state.player={x:Math.floor(GW/2),y:1,drawing:false,autoRetract:false,trailStart:{x:Math.floor(GW/2),y:1},trailPath:[]};",
    "state.player={x:Math.floor(GW/2),y:1,drawing:false,autoRetract:false,safeTransitDir:null,trailStart:{x:Math.floor(GW/2),y:1},trailPath:[]};",
    'stage player safe transit')

rep(Path('game.js'),
    "state.player={x:px,y:py,drawing:false,autoRetract:false,trailStart:{x:px,y:py},trailPath:[]};",
    "state.player={x:px,y:py,drawing:false,autoRetract:false,safeTransitDir:null,trailStart:{x:px,y:py},trailPath:[]};",
    'tutorial player safe transit')

rep(Path('game.js'),
'''function isSafeBoundaryCell(x,y){
  if(!inGrid(x,y)||getCell(x,y)!==CLAIMED)return false;
  for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){
    if(dx===0&&dy===0)continue;
    const nx=x+dx,ny=y+dy;
    if(inGrid(nx,ny)&&getCell(nx,ny)===UNCLAIMED)return true;
  }
  return false;
}
''',
'''function isSafeBoundaryCell(x,y){
  if(!inGrid(x,y)||getCell(x,y)!==CLAIMED)return false;
  for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){
    if(dx===0&&dy===0)continue;
    const nx=x+dx,ny=y+dy;
    if(inGrid(nx,ny)&&getCell(nx,ny)===UNCLAIMED)return true;
  }
  return false;
}
function oppositeDir(d){return d==='up'?'down':d==='down'?'up':d==='left'?'right':d==='right'?'left':null}
function safeBoundaryTransferAhead(x,y,dx,dy){
  let nx=x+dx,ny=y+dy,steps=0;
  while(inGrid(nx,ny)&&getCell(nx,ny)===CLAIMED&&steps<Math.max(GW,GH)){
    if(isSafeBoundaryCell(nx,ny))return{x:nx,y:ny,steps:steps+1};
    nx+=dx;ny+=dy;steps++;
  }
  return null;
}
''',
'transfer helpers')

rep(Path('game.js'),
'''  if(!p.drawing){
    if(target===CLAIMED&&isSafeBoundaryCell(nx,ny)){
      p.x=nx;p.y=ny;p.trailStart={x:nx,y:ny};p.trailPath=[];
    } else if(target===UNCLAIMED&&capture){
      p.drawing=true;p.autoRetract=false;p.trailStart={x:p.x,y:p.y};p.x=nx;p.y=ny;
      setCell(nx,ny,TRAIL);p.trailPath=[{x:nx,y:ny}];
      audio.beep(520,.06,'square',.025);
    }
    return;
  }
''',
'''  if(!p.drawing){
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
'safe transfer movement')

rep(Path('game.js'),
"function clearTrail(){for(let i=0;i<grid.length;i++)if(grid[i]===TRAIL)grid[i]=UNCLAIMED;const p=state.player;p.x=p.trailStart.x;p.y=p.trailStart.y;p.drawing=false;p.autoRetract=false;p.trailPath=[];if(mobileUXActive())resetMobileCaptureLock('line_reset');rebuildVisualLayers()}",
"function clearTrail(){for(let i=0;i<grid.length;i++)if(grid[i]===TRAIL)grid[i]=UNCLAIMED;const p=state.player;p.x=p.trailStart.x;p.y=p.trailStart.y;p.drawing=false;p.autoRetract=false;p.safeTransitDir=null;p.trailPath=[];if(mobileUXActive())resetMobileCaptureLock('line_reset');rebuildVisualLayers()}",
'clear safe transit on line reset')

rep(Path('index.html'),
    '<div class="version">v0.14.1 corner traversal</div>',
    '<div class="version">v0.14.2 safe boundary transfer</div>',
    'version label')
rep(Path('config.js'),"VERSION: '0.14.1'","VERSION: '0.14.2'",'config version')
rep(Path('sw.js'),"cmh-core-v0.14.1","cmh-core-v0.14.2",'service worker cache version')

print('v0.14.2 safe boundary transfer applied')
