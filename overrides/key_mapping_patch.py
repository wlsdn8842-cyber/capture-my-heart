from pathlib import Path
import sys
root=Path(sys.argv[1])

def rep(path,old,new,label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'missing {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

rep(Path('index.html'),
'''          <button id="settingsBtn" class="chip-btn">⚙ SETTINGS</button>''',
'''          <button id="settingsBtn" class="chip-btn">⚙ 옵션</button>''',
'main option label')

rep(Path('game.js'),
'''function showSettings(){''',
'''const KEYMAP_STORAGE_KEY='cmh.keymap.v1';
const KEYMAP_ACTIONS=[
  {id:'up',label:'위',defaults:['ArrowUp','KeyW']},
  {id:'down',label:'아래',defaults:['ArrowDown','KeyS']},
  {id:'left',label:'왼쪽',defaults:['ArrowLeft','KeyA']},
  {id:'right',label:'오른쪽',defaults:['ArrowRight','KeyD']},
  {id:'capture',label:'CAPTURE',defaults:['Space','']},
  {id:'dash',label:'DASH',defaults:['ShiftLeft','ShiftRight']},
  {id:'option',label:'옵션',defaults:['Escape','']}
];
function defaultKeyBindings(){return Object.fromEntries(KEYMAP_ACTIONS.map(a=>[a.id,[...a.defaults]]))}
function loadKeyBindings(){
  const fallback=defaultKeyBindings();
  try{
    const raw=JSON.parse(localStorage.getItem(KEYMAP_STORAGE_KEY)||'{}');
    for(const a of KEYMAP_ACTIONS){
      const arr=Array.isArray(raw?.[a.id])?raw[a.id].filter(v=>typeof v==='string').slice(0,2):null;
      if(arr){while(arr.length<2)arr.push('');fallback[a.id]=arr}
    }
  }catch(_){}
  return fallback;
}
let keyBindings=loadKeyBindings(),keyMappingCapture=null;
function saveKeyBindings(){try{localStorage.setItem(KEYMAP_STORAGE_KEY,JSON.stringify(keyBindings))}catch(_){}}
function keyActionLabel(id){return KEYMAP_ACTIONS.find(a=>a.id===id)?.label||id}
function keyDisplayName(code){
  const names={ArrowUp:'↑',ArrowDown:'↓',ArrowLeft:'←',ArrowRight:'→',Space:'SPACE',ShiftLeft:'L SHIFT',ShiftRight:'R SHIFT',ControlLeft:'L CTRL',ControlRight:'R CTRL',AltLeft:'L ALT',AltRight:'R ALT',Escape:'ESC',Enter:'ENTER',Backspace:'BACKSPACE',Delete:'DELETE'};
  if(names[code])return names[code];
  if(/^Key[A-Z]$/.test(code))return code.slice(3);
  if(/^Digit[0-9]$/.test(code))return code.slice(5);
  if(/^Numpad/.test(code))return code.replace('Numpad','NUM ');
  return code||'추가';
}
function keyBindingAction(code){
  if(!code)return null;
  for(const a of KEYMAP_ACTIONS)if((keyBindings[a.id]||[]).includes(code))return a.id;
  return null;
}
function keyBindingSummary(id){return (keyBindings[id]||[]).filter(Boolean).map(keyDisplayName).join(' / ')||'미지정'}
function movementKeySummary(){return `↑ ${keyBindingSummary('up')} · ↓ ${keyBindingSummary('down')} · ← ${keyBindingSummary('left')} · → ${keyBindingSummary('right')}`}
function findKeyConflict(code,action,slot){
  for(const a of KEYMAP_ACTIONS)for(let i=0;i<2;i++)if(!(a.id===action&&i===slot)&&keyBindings[a.id]?.[i]===code)return{action:a.id,slot:i};
  return null;
}
function forbiddenMappingEvent(e){
  const blocked=new Set(['F5','F11','F12','Tab','MetaLeft','MetaRight','ContextMenu']);
  const modifierOnly=new Set(['ControlLeft','ControlRight','AltLeft','AltRight','ShiftLeft','ShiftRight']);
  if(blocked.has(e.code))return true;
  if((e.ctrlKey||e.altKey||e.metaKey)&&!modifierOnly.has(e.code))return true;
  return false;
}
function resetMappedKeyboardState(){
  if(typeof pressedKeyboardCodes!=='undefined')pressedKeyboardCodes.clear();
  input.dirs.clear();
  if(!(mobileUXActive()&&typeof mobileCaptureLocked!=='undefined'&&mobileCaptureLocked))input.capture=false;
  input.dash=false;
}
function setKeyBinding(action,slot,code){
  const conflict=findKeyConflict(code,action,slot);
  if(conflict){toast(`${keyDisplayName(code)} 키는 이미 ${keyActionLabel(conflict.action)}에 사용 중입니다.`,true,1600);return false}
  keyBindings[action][slot]=code;saveKeyBindings();resetMappedKeyboardState();return true;
}
function showKeyMapping(){
  keyMappingCapture=null;
  const rows=KEYMAP_ACTIONS.map(a=>`<div class="keymap-row"><span class="keymap-action">${a.label}</span><div class="keymap-slots">${[0,1].map(i=>`<button class="keymap-key" type="button" data-key-action="${a.id}" data-key-slot="${i}">${keyDisplayName(keyBindings[a.id]?.[i])}</button>`).join('')}</div></div>`).join('');
  openModal(`<h2>⌨ 키맵핑</h2><p class="muted">바꾸려는 키를 누른 뒤 새 키를 입력하세요. 같은 키를 두 기능에 중복 지정할 수 없습니다.</p><div class="keymap-grid">${rows}</div><p id="keymapHint" class="keymap-hint">PC 키보드 설정입니다. 모바일 조작은 변경되지 않습니다.</p><div class="row keymap-actions"><button id="keymapReset" class="btn tertiary">기본값 복원</button><button id="keymapBack" class="btn primary">← 옵션</button></div>`,'keymap-modal-card');
  modalLayer.querySelectorAll('.keymap-key').forEach(btn=>btn.onclick=()=>{
    keyMappingCapture={action:btn.dataset.keyAction,slot:Number(btn.dataset.keySlot),button:btn};
    modalLayer.querySelectorAll('.keymap-key').forEach(b=>b.classList.remove('listening'));btn.classList.add('listening');btn.textContent='키를 눌러주세요…';
    const hint=$('#keymapHint');if(hint)hint.textContent='새 키를 누르면 바로 저장됩니다.';
  });
  $('#keymapReset').onclick=()=>{keyBindings=defaultKeyBindings();saveKeyBindings();resetMappedKeyboardState();toast('키맵핑 기본값을 복원했습니다.',false,1200);showKeyMapping()};
  $('#keymapBack').onclick=()=>{keyMappingCapture=null;showSettings()};
}
function handleKeyMappingCapture(e){
  if(!keyMappingCapture)return;
  e.preventDefault();e.stopPropagation();e.stopImmediatePropagation();
  if(forbiddenMappingEvent(e)){toast('브라우저/시스템 예약키는 등록할 수 없습니다.',true,1500);return}
  const {action,slot}=keyMappingCapture;
  if(setKeyBinding(action,slot,e.code)){
    track('key_mapping_change',{action,slot:slot+1,code:e.code});
    keyMappingCapture=null;showKeyMapping();
  }
}
document.addEventListener('keydown',handleKeyMappingCapture,true);

function showSettings(){''',
'key mapping helpers')

rep(Path('game.js'),
'''  openModal(`<h2>⚙ SETTINGS</h2><div class="settings-grid">
    <div class="setting-line"><label>BGM / SFX</label><input id="volRange" type="range" min="0" max="1" step="0.01" value="${s.volume}"><span id="volPct">${Math.round(s.volume*100)}%</span></div>
    <div class="toggle"><span>BGM</span><input id="bgmCheck" type="checkbox" ${s.bgm!==false?'checked':''}></div>
    <div class="toggle"><span>Mute All</span><input id="muteCheck" type="checkbox" ${audio.muted?'checked':''}></div>
    <div class="toggle"><span>Simple SFX</span><input id="sfxCheck" type="checkbox" ${s.sfx?'checked':''}></div>
  </div><div style="margin-top:16px"><button id="settingsClose" class="btn primary">CLOSE</button></div>`);''',
'''  openModal(`<h2>⚙ 옵션</h2><div class="settings-grid">
    <div class="setting-line"><label>BGM / SFX</label><input id="volRange" type="range" min="0" max="1" step="0.01" value="${s.volume}"><span id="volPct">${Math.round(s.volume*100)}%</span></div>
    <div class="toggle"><span>BGM</span><input id="bgmCheck" type="checkbox" ${s.bgm!==false?'checked':''}></div>
    <div class="toggle"><span>Mute All</span><input id="muteCheck" type="checkbox" ${audio.muted?'checked':''}></div>
    <div class="toggle"><span>Simple SFX</span><input id="sfxCheck" type="checkbox" ${s.sfx?'checked':''}></div>
    <button id="keyMappingBtn" class="btn secondary settings-keymap-btn">⌨ 키맵핑</button>
  </div><div style="margin-top:16px"><button id="settingsClose" class="btn primary">닫기</button></div>`);''',
'korean options and key mapping button')

rep(Path('game.js'),
'''  $('#sfxCheck').onchange=e=>{audio.settings.sfx=e.target.checked;saveSettings()};
  $('#settingsClose').onclick=closeModal;''',
'''  $('#sfxCheck').onchange=e=>{audio.settings.sfx=e.target.checked;saveSettings()};
  $('#keyMappingBtn').onclick=showKeyMapping;
  $('#settingsClose').onclick=closeModal;''',
'key mapping settings binding')

rep(Path('game.js'),
'''    <button id="pauseSettings" class="btn tertiary">SETTINGS</button>''',
'''    <button id="pauseSettings" class="btn tertiary">옵션</button>''',
'pause option label')

rep(Path('game.js'),
'''    <p><span class="kbd">WASD / ↑↓←→</span> 안전영역 이동</p>
    <p><span class="kbd">SPACE</span>를 누른 채 안전영역 밖으로 나가 선을 긋습니다. <b>SPACE를 놓으면 방금 그은 선을 따라 자동으로 안전지대까지 후퇴</b>합니다.</p>
    <p><span class="kbd">SHIFT</span>를 누르면 스태미나를 사용해 짧게 DASH합니다.</p>''',
'''    <p><span class="kbd">${movementKeySummary()}</span> 안전영역 이동</p>
    <p><span class="kbd">${keyBindingSummary('capture')}</span>를 누른 채 안전영역 밖으로 나가 선을 긋습니다. <b>키를 놓으면 방금 그은 선을 따라 자동으로 안전지대까지 후퇴</b>합니다.</p>
    <p><span class="kbd">${keyBindingSummary('dash')}</span>를 누르면 스태미나를 사용해 짧게 DASH합니다.</p>''',
'dynamic howto key labels')

rep(Path('game.js'),
'''    <p>모바일은 화면 아래 <b>조이스틱 + CAPTURE + DASH</b> 버튼을 사용합니다.</p><p class="muted">⚙ SETTINGS에서 BGM/SFX 음량과 Mute를 조절할 수 있습니다.</p>''',
'''    <p>모바일은 화면 아래 <b>조이스틱 + CAPTURE + DASH</b> 버튼을 사용합니다.</p><p class="muted">⚙ 옵션에서 BGM/SFX와 <b>키맵핑</b>을 변경할 수 있습니다.</p>''',
'howto option copy')

rep(Path('game.js'),
'''  if(tutorial.step==='move'){label='STEP 1 / 4';title='MOVE';text=coarse?'왼쪽 조이스틱으로 3칸 이상 이동하세요':'Arrow Keys / WASD · 3칸 이상 이동하세요';hint='먼저 안전영역 위에서 이동을 익힙니다.'}
  else if(tutorial.step==='draw'){label='STEP 2 / 4';title='DRAW THE LINE';text=coarse?'1. TAP CAPTURE → 2. MOVE':'HOLD SPACE + MOVE';hint=coarse?'CAPTURE는 한 번 탭하면 잠깁니다. 안전영역 밖으로 이동하세요.':'안전영역 밖으로 선을 2칸 이상 그리세요.'}
  else if(tutorial.step==='capture'){label='STEP 3 / 4';title='CONNECT BACK';text='선을 안전영역에 다시 연결하세요';hint='라인을 닫으면 영역이 실제로 공개됩니다.'}
  else if(tutorial.step==='retract'){label='STEP 4 / 4';title=coarse?'TAP TO RETREAT':'RELEASE TO RETREAT';text=tutorial.retractArmed?(coarse?'CAPTURE를 다시 탭하세요':'NOW RELEASE SPACE'):(coarse?'1. TAP CAPTURE → 2. MOVE':'HOLD SPACE + MOVE로 짧게 선을 그리세요');hint=coarse?'CAPTURE를 다시 탭하면 방금 그은 선을 따라 안전지대로 후퇴합니다.':'버튼을 놓으면 방금 그은 선을 따라 안전지대로 후퇴합니다.'}
  else{label='TUTORIAL COMPLETE ♥';title='READY?';text='80% = CLEAR · 90% = BONUS · 99%+ = PERFECT';hint=coarse?'TIP · DASH 버튼으로 빠르게 이동':'TIP · SHIFT = DASH';ready=true}
''',
'''  if(tutorial.step==='move'){label='STEP 1 / 4';title='MOVE';text=coarse?'왼쪽 조이스틱으로 3칸 이상 이동하세요':movementKeySummary()+' · 3칸 이상 이동하세요';hint='먼저 안전영역 위에서 이동을 익힙니다.'}
  else if(tutorial.step==='draw'){label='STEP 2 / 4';title='DRAW THE LINE';text=coarse?'1. TAP CAPTURE → 2. MOVE':'HOLD '+keyBindingSummary('capture')+' + MOVE';hint=coarse?'CAPTURE는 한 번 탭하면 잠깁니다. 안전영역 밖으로 이동하세요.':'안전영역 밖으로 선을 2칸 이상 그리세요.'}
  else if(tutorial.step==='capture'){label='STEP 3 / 4';title='CONNECT BACK';text='선을 안전영역에 다시 연결하세요';hint='라인을 닫으면 영역이 실제로 공개됩니다.'}
  else if(tutorial.step==='retract'){label='STEP 4 / 4';title=coarse?'TAP TO RETREAT':'RELEASE TO RETREAT';text=tutorial.retractArmed?(coarse?'CAPTURE를 다시 탭하세요':'NOW RELEASE '+keyBindingSummary('capture')):(coarse?'1. TAP CAPTURE → 2. MOVE':'HOLD '+keyBindingSummary('capture')+' + MOVE로 짧게 선을 그리세요');hint=coarse?'CAPTURE를 다시 탭하면 방금 그은 선을 따라 안전지대로 후퇴합니다.':'버튼을 놓으면 방금 그은 선을 따라 안전지대로 후퇴합니다.'}
  else{label='TUTORIAL COMPLETE ♥';title='READY?';text='80% = CLEAR · 90% = BONUS · 99%+ = PERFECT';hint=coarse?'TIP · DASH 버튼으로 빠르게 이동':'TIP · '+keyBindingSummary('dash')+' = DASH';ready=true}
''',
'tutorial mapped key labels')

rep(Path('game.js'),
'''// Input wiring
const keyMap={ArrowUp:'up',KeyW:'up',ArrowDown:'down',KeyS:'down',ArrowLeft:'left',KeyA:'left',ArrowRight:'right',KeyD:'right'};
window.addEventListener('keydown',e=>{if(keyMap[e.code]){input.dirs.add(keyMap[e.code]);input.lastDir=keyMap[e.code];if(state.mode==='playing')e.preventDefault()}if(e.code==='Space'){input.capture=true;stopAutoRetract();if(state.mode==='playing')e.preventDefault()}if(e.code==='ShiftLeft'||e.code==='ShiftRight'){input.dash=true;if(state.mode==='playing')e.preventDefault()}if(e.code==='Escape'&&state.mode==='playing'&&!state.paused)showPause()});
window.addEventListener('keyup',e=>{if(keyMap[e.code])input.dirs.delete(keyMap[e.code]);if(e.code==='Space'){input.capture=false;beginAutoRetract()}if(e.code==='ShiftLeft'||e.code==='ShiftRight')input.dash=false});
window.addEventListener('blur',()=>{input.dirs.clear();input.capture=false;input.dash=false;beginAutoRetract()});''',
'''// Input wiring — v0.13.5 user key mapping
const pressedKeyboardCodes=new Set();
function anyMappedKeyPressed(action){return (keyBindings[action]||[]).some(code=>code&&pressedKeyboardCodes.has(code))}
function syncMappedDirections(){
  input.dirs.clear();
  for(const code of pressedKeyboardCodes){const action=keyBindingAction(code);if(['up','down','left','right'].includes(action))input.dirs.add(action)}
}
window.addEventListener('keydown',e=>{
  if(keyMappingCapture)return;
  const action=keyBindingAction(e.code);if(!action)return;
  pressedKeyboardCodes.add(e.code);
  if(['up','down','left','right'].includes(action)){input.dirs.add(action);input.lastDir=action}
  else if(action==='capture'){input.capture=true;stopAutoRetract()}
  else if(action==='dash')input.dash=true;
  else if(action==='option'&&!e.repeat&&state.mode==='playing'&&!state.paused)showPause();
  if(state.mode==='playing')e.preventDefault();
});
window.addEventListener('keyup',e=>{
  const action=keyBindingAction(e.code);pressedKeyboardCodes.delete(e.code);
  if(['up','down','left','right'].includes(action))syncMappedDirections();
  if(action==='capture'&&!anyMappedKeyPressed('capture')){if(!(mobileUXActive()&&typeof mobileCaptureLocked!=='undefined'&&mobileCaptureLocked)){input.capture=false;beginAutoRetract()}}
  if(action==='dash'&&!anyMappedKeyPressed('dash'))input.dash=false;
});
window.addEventListener('blur',()=>{pressedKeyboardCodes.clear();input.dirs.clear();input.capture=false;input.dash=false;beginAutoRetract()});''',
'mapped input wiring')

css=root/'styles.css';s=css.read_text(encoding='utf-8')
if '/* v0.13.5 key mapping */' not in s:
    s += r'''

/* v0.13.5 key mapping */
.settings-keymap-btn{width:100%;margin-top:4px;font-weight:900}
.keymap-grid{display:grid;gap:8px;margin:14px 0}.keymap-row{display:grid;grid-template-columns:92px 1fr;gap:10px;align-items:center;padding:8px 10px;border:1px solid rgba(255,255,255,.1);border-radius:13px;background:rgba(255,255,255,.035)}.keymap-action{font-weight:900;color:#f6dcef}.keymap-slots{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}.keymap-key{min-height:36px;border:1px solid rgba(77,230,255,.25);border-radius:10px;background:rgba(77,230,255,.07);color:#e7fbff;font-size:.72rem;font-weight:900;cursor:pointer}.keymap-key:hover{background:rgba(77,230,255,.14)}.keymap-key.listening{border-color:#ffd45d;background:rgba(255,212,93,.13);color:#fff3b5;box-shadow:0 0 16px rgba(255,212,93,.16)}.keymap-hint{min-height:22px;margin:8px 0 12px;color:#d7c4dc;font-size:.76rem}.keymap-actions{margin-top:10px}
@media (max-width:560px){.keymap-row{grid-template-columns:72px 1fr;padding:7px}.keymap-action{font-size:.72rem}.keymap-key{min-height:34px;font-size:.62rem}.keymap-modal-card{padding:18px!important}}
'''
    css.write_text(s,encoding='utf-8')

rep(Path('index.html'),'<div class="version">v0.13.4 hud audio controls</div>','<div class="version">v0.13.5 key mapping</div>','version')
rep(Path('config.js'),"VERSION: '0.13.4'","VERSION: '0.13.5'",'config')
rep(Path('sw.js'),"cmh-core-v0.13.4","cmh-core-v0.13.5",'sw')
print('v0.13.5 key mapping applied')
