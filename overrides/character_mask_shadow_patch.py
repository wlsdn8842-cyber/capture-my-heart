from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path,old,new,label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'character mask shadow patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

rep(Path('game.js'),
"  enemies:[], projectiles:[], items:[], area:0, lastArea:0, clearMilestone:0,",
"  enemies:[], projectiles:[], items:[], area:0, lastArea:0, characterArea:null, characterMaskTotal:0, clearMilestone:0,",
'state fields')

calc_anchor="function calcArea(){let claimed=0,total=(GW-4)*(GH-4);for(let y=2;y<GH-2;y++)for(let x=2;x<GW-2;x++)if(getCell(x,y)===CLAIMED)claimed++;return claimed/total*100}\n"
calc_block=r'''function calcArea(){let claimed=0,total=(GW-4)*(GH-4);for(let y=2;y<GH-2;y++)for(let x=2;x<GW-2;x++)if(getCell(x,y)===CLAIMED)claimed++;return claimed/total*100}

// v0.11.0 Character Mask Shadow Mode.
// Computes character-only reveal percentage but DOES NOT change clear conditions yet.
const CHARACTER_MASK_CACHE=new Map();
const CHARACTER_MASK_DEBUG_KEY='cmh.characterMask.debug';
function characterMaskDebugEnabled(){
  try{
    const q=new URLSearchParams(location.search).get('maskdebug');
    if(q==='1'){localStorage.setItem(CHARACTER_MASK_DEBUG_KEY,'1');return true}
    if(q==='0'){localStorage.removeItem(CHARACTER_MASK_DEBUG_KEY);return false}
    return localStorage.getItem(CHARACTER_MASK_DEBUG_KEY)==='1';
  }catch(_){return false}
}
function decodeCharacterMask(stage=state.stage){
  if(CHARACTER_MASK_CACHE.has(stage))return CHARACTER_MASK_CACHE.get(stage);
  const src=window.CMH_CHARACTER_MASKS?.stages?.[stage];
  if(!src||src.w!==GW||src.h!==GH||!src.bits){CHARACTER_MASK_CACHE.set(stage,null);return null}
  try{
    const raw=atob(src.bits),bytes=new Uint8Array(raw.length);
    for(let i=0;i<raw.length;i++)bytes[i]=raw.charCodeAt(i);
    const mask=new Uint8Array(GW*GH);
    for(let i=0;i<mask.length;i++)mask[i]=(bytes[i>>3]>>(i&7))&1;
    const out={mask,source:src};CHARACTER_MASK_CACHE.set(stage,out);return out;
  }catch(e){console.warn('Character mask decode failed',e);CHARACTER_MASK_CACHE.set(stage,null);return null}
}
function calcCharacterArea(stage=state.stage){
  const decoded=decodeCharacterMask(stage);if(!decoded)return null;
  let total=0,claimed=0;
  for(let y=2;y<GH-2;y++)for(let x=2;x<GW-2;x++){
    const k=idx(x,y);if(!decoded.mask[k])continue;total++;if(getCell(x,y)===CLAIMED)claimed++;
  }
  if(!total)return null;
  return {percent:claimed/total*100,claimed,total};
}
function refreshCharacterArea(){
  if(tutorial.active){state.characterArea=null;state.characterMaskTotal=0;return null}
  const v=calcCharacterArea(state.stage);
  state.characterArea=v?Number(v.percent):null;state.characterMaskTotal=v?.total||0;return v;
}
function updateCharacterMaskDebugHUD(){
  let el=$('#characterMaskDebug');
  const enabled=characterMaskDebugEnabled(),has=Number.isFinite(state.characterArea);
  if(!enabled||!has){if(el)el.classList.add('hidden');return}
  if(!el){el=document.createElement('div');el.id='characterMaskDebug';el.className='character-mask-debug';gameScreen.appendChild(el)}
  el.classList.remove('hidden');
  el.innerHTML=`<b>MASK SHADOW · Stage ${state.stage}</b><span>AREA ${state.area.toFixed(1)}%</span><span>CHAR ${state.characterArea.toFixed(1)}%</span><small>판정 미적용 · ${state.characterMaskTotal} cells</small>`;
}
'''
rep(Path('game.js'),calc_anchor,calc_block,'mask calculation')

rep(Path('game.js'),
"  state.area=0;state.lastArea=0;rebuildVisualLayers();",
"  state.area=0;state.lastArea=0;refreshCharacterArea();rebuildVisualLayers();",
'init grid character area')

rep(Path('game.js'),
"function captureRegion(){\n  const before=state.area;",
"function captureRegion(){\n  const before=state.area,beforeCharacter=Number.isFinite(state.characterArea)?state.characterArea:null;",
'capture before char')

rep(Path('game.js'),
"state.lastArea=before;state.area=calcArea();\n  if(mobileUXActive())resetMobileCaptureLock('capture_complete');",
"state.lastArea=before;state.area=calcArea();refreshCharacterArea();\n  if(mobileUXActive())resetMobileCaptureLock('capture_complete');",
'capture refresh char')

rep(Path('game.js'),
"  juiceCaptureFX(delta,before,state.area);\n  state.score+=points;",
"  juiceCaptureFX(delta,before,state.area);\n  if(Number.isFinite(state.characterArea))track('character_mask_shadow',{stage:state.stage,area:Number(state.area.toFixed(2)),character_area:Number(state.characterArea.toFixed(2)),character_delta:beforeCharacter===null?null:Number((state.characterArea-beforeCharacter).toFixed(2))});\n  state.score+=points;",
'capture shadow analytics')

rep(Path('game.js'),
"rebuildVisualLayers();state.lastArea=before;state.area=calcArea();updateHUD();",
"rebuildVisualLayers();state.lastArea=before;state.area=calcArea();refreshCharacterArea();updateHUD();",
'boss destruction refresh')

rep(Path('game.js'),
"  const hue=STAGES[state.stage]?.hue||'#ff4da0';document.documentElement.style.setProperty('--stage-hue',hue);gameScreen.classList.toggle('hud-clear',state.area>=80);gameScreen.classList.toggle('hud-bonus',state.area>=90);gameScreen.classList.toggle('hud-perfect',state.area>=99);gameScreen.classList.toggle('hud-time-danger',state.timeLeft<25);updateMusicLabel();",
"  const hue=STAGES[state.stage]?.hue||'#ff4da0';document.documentElement.style.setProperty('--stage-hue',hue);gameScreen.classList.toggle('hud-clear',state.area>=80);gameScreen.classList.toggle('hud-bonus',state.area>=90);gameScreen.classList.toggle('hud-perfect',state.area>=99);gameScreen.classList.toggle('hud-time-danger',state.timeLeft<25);updateCharacterMaskDebugHUD();updateMusicLabel();",
'debug hud hook')

rep(Path('game.js'),
"initTutorialGrid();state.enemies=[];state.projectiles=[];state.items=[];state.score=0;",
"initTutorialGrid();state.characterArea=null;state.characterMaskTotal=0;state.enemies=[];state.projectiles=[];state.items=[];state.score=0;",
'tutorial mask off')

rep(Path('index.html'),
'  <script src="feedback.js"></script>\n  <script src="game.js"></script>',
'  <script src="feedback.js"></script>\n  <script src="character_masks.js"></script>\n  <script src="game.js"></script>',
'load character mask data')

rep(Path('index.html'),'<div class="version">v0.10.0 boss breakout</div>','<div class="version">v0.11.0 mask shadow</div>','version label')

css=root/'styles.css';s=css.read_text(encoding='utf-8')
if '/* v0.11.0 character mask shadow */' not in s:
    s+=r'''
/* v0.11.0 character mask shadow — debug only */
.character-mask-debug{position:absolute;z-index:50;left:50%;top:54px;transform:translateX(-50%);display:flex;align-items:center;gap:9px;padding:6px 10px;border:1px solid rgba(255,217,91,.55);border-radius:999px;background:rgba(7,4,12,.9);box-shadow:0 0 20px rgba(255,210,80,.16);font-size:.62rem;color:#f4ecf5;pointer-events:none;white-space:nowrap}.character-mask-debug b{color:#ffd85f}.character-mask-debug span:nth-of-type(2){color:#7ff2ff;font-weight:900}.character-mask-debug small{color:#aa9db0}@media(pointer:coarse),(max-width:800px){.character-mask-debug{top:38px;gap:5px;padding:4px 7px;font-size:.48rem}.character-mask-debug small{display:none}}
'''
    css.write_text(s,encoding='utf-8')

print('v0.11.0 character mask shadow mode applied')
