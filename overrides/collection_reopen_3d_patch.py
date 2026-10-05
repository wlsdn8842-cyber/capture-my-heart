from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path, old, new, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'collection reopen 3d patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

rep(Path('index.html'),
'''          <button id="galleryBtn" class="chip-btn">♡ GALLERY</button>
          <button id="settingsBtn" class="chip-btn">⚙ SETTINGS</button>''',
'''          <button id="galleryBtn" class="chip-btn">♡ GALLERY</button>
          <button id="collectionReopenBtn" class="chip-btn hidden">📩 MY COLLECTION</button>
          <button id="settingsBtn" class="chip-btn">⚙ SETTINGS</button>''',
'title collection button')

rep(Path('game.js'),
'''function refreshTitle(){
  const r=recentSave(), c=$('#continueBtn'), summary=$('#saveSummary');''',
'''const COLLECTION_REOPEN_KEY='cmh.collection.reopen.v1';
const COLLECTION_REOPEN_MS=72*60*60*1000;
function collectionReopenData(){
  try{
    const raw=localStorage.getItem(COLLECTION_REOPEN_KEY);if(!raw)return null;
    const d=JSON.parse(raw),expiresAt=Number(d?.expiresAt||0),completedAt=Number(d?.completedAt||0),score=Number(d?.score||0);
    if(!expiresAt||Date.now()>=expiresAt){localStorage.removeItem(COLLECTION_REOPEN_KEY);return null}
    return{completedAt,expiresAt,score};
  }catch(_){return null}
}
function grantCollectionReopen(score=0){
  const completedAt=Date.now(),expiresAt=completedAt+COLLECTION_REOPEN_MS,data={completedAt,expiresAt,score:Number(score||0)};
  try{localStorage.setItem(COLLECTION_REOPEN_KEY,JSON.stringify(data))}catch(_){}
  return data;
}
function collectionReopenLabel(d){
  const ms=Math.max(0,Number(d?.expiresAt||0)-Date.now()),hours=Math.max(1,Math.ceil(ms/3600000));
  return hours>=48?`${Math.ceil(hours/24)}일 남음`:hours>=24?'1일 남음':`${hours}시간 남음`;
}
function openReopenCollection(source='title'){
  const d=collectionReopenData();
  if(!d){toast('컬렉션 다시 받기 기간이 만료되었습니다.');refreshTitle();return}
  track('collection_reopen_click',{source,remaining_hours:Math.max(0,Math.ceil((d.expiresAt-Date.now())/3600000))});
  window.CMH_COLLECTION?.show?.({score:d.score||0});
}

function refreshTitle(){
  const r=recentSave(), c=$('#continueBtn'), summary=$('#saveSummary');''',
'collection reopen helpers')

rep(Path('game.js'),
'''  } else {
    summary.innerHTML='<strong>💾 NO SAVE DATA</strong><span>NEW GAME으로 시작하세요</span>';
  }
}''',
'''  } else {
    summary.innerHTML='<strong>💾 NO SAVE DATA</strong><span>NEW GAME으로 시작하세요</span>';
  }
  const collectionBtn=$('#collectionReopenBtn'),collectionData=collectionReopenData();
  if(collectionBtn){
    collectionBtn.classList.toggle('hidden',!collectionData);
    if(collectionData)collectionBtn.textContent=`📩 MY COLLECTION · ${collectionReopenLabel(collectionData)}`;
  }
}''',
'title collection visibility')

rep(Path('game.js'),
'''  openModal(`<div class="gallery-head"><div><h2>♡ GALLERY</h2><p class="muted">80% 이상 클리어한 스테이지가 해금됩니다. 이미지를 누르면 전체 화면으로 확대됩니다.</p></div><button id="galleryClose" class="btn primary">CLOSE</button></div><div class="gallery-grid">${cards.join('')}</div>`,'gallery-modal-card');''',
'''  const collectionData=collectionReopenData();
  const collectionCta=collectionData?`<div class="ending-collection"><button id="galleryCollectionBtn" class="btn primary">📩 MY COLLECTION · ${collectionReopenLabel(collectionData)}</button><small>Stage 10 완주 후 3일 동안 다시 받을 수 있습니다.</small></div>`:'';
  openModal(`<div class="gallery-head"><div><h2>♡ GALLERY</h2><p class="muted">80% 이상 클리어한 스테이지가 해금됩니다. 이미지를 누르면 전체 화면으로 확대됩니다.</p></div><button id="galleryClose" class="btn primary">CLOSE</button></div>${collectionCta}<div class="gallery-grid">${cards.join('')}</div>`,'gallery-modal-card');''',
'gallery collection CTA')

rep(Path('game.js'),
'''  $('#galleryClose').onclick=closeModal;
}''',
'''  const galleryCollectionBtn=$('#galleryCollectionBtn');if(galleryCollectionBtn)galleryCollectionBtn.onclick=()=>openReopenCollection('gallery');
  $('#galleryClose').onclick=closeModal;
}''',
'gallery collection binding')

rep(Path('game.js'),
'''  state.mode='ending';state.paused=true;unlockStage(10);saveGlobal({bestScore:Math.max(globalData().bestScore||0,state.score)});track('game_complete',{score:state.score});''',
'''  state.mode='ending';state.paused=true;unlockStage(10);saveGlobal({bestScore:Math.max(globalData().bestScore||0,state.score)});grantCollectionReopen(state.score);track('game_complete',{score:state.score});''',
'grant 72h on completion')

rep(Path('game.js'),
'''$('#newGameBtn').onclick=()=>showSlotPicker('new');$('#continueBtn').onclick=()=>{const r=recentSave();if(r){track('continue_game',{slot:r.slot||1,stage:r.stage||1,score:r.score||0});loadSaveData(r)}};$('#loadBtn').onclick=()=>showSlotPicker('load');$('#galleryBtn').onclick=showGallery;$('#settingsBtn').onclick=showSettings;''',
'''$('#newGameBtn').onclick=()=>showSlotPicker('new');$('#continueBtn').onclick=()=>{const r=recentSave();if(r){track('continue_game',{slot:r.slot||1,stage:r.stage||1,score:r.score||0});loadSaveData(r)}};$('#loadBtn').onclick=()=>showSlotPicker('load');$('#galleryBtn').onclick=showGallery;const collectionReopenBtn=$('#collectionReopenBtn');if(collectionReopenBtn)collectionReopenBtn.onclick=()=>openReopenCollection('title');$('#settingsBtn').onclick=showSettings;''',
'title collection binding')

rep(Path('index.html'),
    '<div class="version">v0.13.1 collection reliability</div>',
    '<div class="version">v0.13.2 collection 3d access</div>',
    'version label')
rep(Path('config.js'),"VERSION: '0.13.1'","VERSION: '0.13.2'",'config version')
rep(Path('sw.js'),"cmh-core-v0.13.1","cmh-core-v0.13.2",'service worker cache version')

print('v0.13.2 collection 3-day reopen applied')
