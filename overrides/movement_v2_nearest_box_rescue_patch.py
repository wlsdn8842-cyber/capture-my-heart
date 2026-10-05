from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path, old, new, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'nearest box rescue patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

rep(Path('game.js'),
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
''',
'''function boundaryComponentKeys(x,y){
  const out=new Set();
  if(!isSafeBoundaryCell(x,y))return out;
  const q=[{x,y}];out.add(y*GW+x);
  for(let h=0;h<q.length;h++){
    const cur=q[h];
    for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){
      if(dx===0&&dy===0)continue;
      const nx=cur.x+dx,ny=cur.y+dy,k=ny*GW+nx;
      if(!inGrid(nx,ny)||out.has(k)||getCell(nx,ny)!==CLAIMED||!isSafeBoundaryCell(nx,ny))continue;
      out.add(k);q.push({x:nx,y:ny});
    }
  }
  return out;
}
''',
'8-neighbor boundary component')

rep(Path('game.js'),
'''function findNearestSafeBoundaryPath(x,y){
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
''',
'''function findNearestSafeBoundaryPath(x,y){
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
function findNearestDifferentBoundaryPath(x,y){
  if(!inGrid(x,y)||getCell(x,y)!==CLAIMED)return null;
  const origin=boundaryComponentKeys(x,y),total=GW*GH,prev=new Int32Array(total);prev.fill(-1);
  const startKey=y*GW+x,q=[startKey];prev[startKey]=startKey;
  for(let h=0;h<q.length;h++){
    const k=q[h],cx=k%GW,cy=Math.floor(k/GW);
    if(k!==startKey&&isSafeBoundaryCell(cx,cy)&&!origin.has(k))return reconstructClaimedPath(prev,startKey,k).slice(1);
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
function armNearestSafeBoxTransfer(reason='blocked_move'){
  const p=state.player;
  if(!p||p.drawing||p.autoRetract||(Array.isArray(p.safeTransitPath)&&p.safeTransitPath.length))return false;
  const onBoundary=isSafeBoundaryCell(p.x,p.y);
  const path=onBoundary?findNearestDifferentBoundaryPath(p.x,p.y):findNearestSafeBoundaryPath(p.x,p.y);
  if(!path||!path.length)return false;
  if(input.capture){
    input.capture=false;
    if(mobileUXActive())resetMobileCaptureLock('nearest_box_rescue');else captureNeedsRelease=true;
  }
  p.safeTransitOrigin={x:p.x,y:p.y};
  p.safeTransitPath=path;
  p.safeTransitTarget=path[path.length-1];
  track('safe_box_rescue_start',{stage:state.stage,reason,to_x:p.safeTransitTarget.x,to_y:p.safeTransitTarget.y,distance:path.length});
  toast('SAFE ROUTE → NEAREST BOX',false,850);
  return true;
}
function clearSafeTransit(p=state.player){
''',
'nearest different boundary rescue helpers')

rep(Path('game.js'),
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
'''function movePlayer(){
  const p=state.player;if(p.autoRetract)return;
  if(stepSafeTransit(p))return;
  const d=direction();if(!d)return;

  // Boss breakouts or territory changes can leave the player inside an already-claimed island.
  // On the next move attempt, rescue to the nearest valid boundary automatically.
  if(!p.drawing&&getCell(p.x,p.y)===CLAIMED&&!isSafeBoundaryCell(p.x,p.y)){
    if(armNearestSafeBoxTransfer('interior_stranded'))return;
  }

  const [dx,dy]=dirVec(d),nx=p.x+dx,ny=p.y+dy;
  if(!inGrid(nx,ny)){
    if(!p.drawing)armNearestSafeBoxTransfer('edge_blocked');
    return;
  }
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
      }else{
        armNearestSafeBoxTransfer('direction_blocked');
      }
    } else if(target===UNCLAIMED&&capture){
      p.drawing=true;p.autoRetract=false;clearSafeTransit(p);p.trailStart={x:p.x,y:p.y};p.x=nx;p.y=ny;
      setCell(nx,ny,TRAIL);p.trailPath=[{x:nx,y:ny}];
      audio.beep(520,.06,'square',.025);
    }
    return;
  }
''',
'nearest box rescue movement')

rep(Path('index.html'),
    '<div class="version">v0.14.3 safe path transfer</div>',
    '<div class="version">v0.14.4 nearest box rescue</div>',
    'version label')
rep(Path('config.js'),"VERSION: '0.14.3'","VERSION: '0.14.4'",'config version')
rep(Path('sw.js'),"cmh-core-v0.14.3","cmh-core-v0.14.4",'service worker cache version')

print('v0.14.4 nearest box rescue applied')
