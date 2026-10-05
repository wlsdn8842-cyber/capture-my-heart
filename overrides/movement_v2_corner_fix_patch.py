from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path, old, new, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'movement v2 corner fix failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

rep(Path('game.js'),
'''function isSafeBoundaryCell(x,y){
  if(!inGrid(x,y)||getCell(x,y)!==CLAIMED)return false;
  for(const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]){
    const nx=x+dx,ny=y+dy;if(inGrid(nx,ny)&&getCell(nx,ny)===UNCLAIMED)return true;
  }
  return false;
}''',
'''function isSafeBoundaryCell(x,y){
  if(!inGrid(x,y)||getCell(x,y)!==CLAIMED)return false;
  for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){
    if(dx===0&&dy===0)continue;
    const nx=x+dx,ny=y+dy;
    if(inGrid(nx,ny)&&getCell(nx,ny)===UNCLAIMED)return true;
  }
  return false;
}''',
'8-neighbor corner boundary')

rep(Path('index.html'),
    '<div class="version">v0.14.0 movement v2</div>',
    '<div class="version">v0.14.1 corner traversal</div>',
    'version label')
rep(Path('config.js'),"VERSION: '0.14.0'","VERSION: '0.14.1'",'config version')
rep(Path('sw.js'),"cmh-core-v0.14.0","cmh-core-v0.14.1",'service worker cache version')

print('v0.14.1 movement v2 corner traversal applied')
