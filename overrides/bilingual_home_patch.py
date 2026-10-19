from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path, old, new, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'bilingual home patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

rep(Path('index.html'),
'''          <button id="settingsBtn" class="chip-btn">⚙ 옵션</button><a href="info.html" class="chip-btn site-info-link" aria-label="게임 소개와 사이트 정보">ⓘ 게임 정보</a>
          <button id="howToBtn" class="chip-btn">? HOW TO PLAY</button>
          <button id="feedbackBtn" class="chip-btn">💬 FEEDBACK</button>
          <a class="chip-btn" href="privacy.html" target="_blank" rel="noopener">PRIVACY</a>''',
'''          <button id="settingsBtn" class="chip-btn">⚙ 옵션</button><a id="siteInfoLink" href="info.html" class="chip-btn site-info-link" aria-label="게임 소개와 사이트 정보">ⓘ 게임 정보</a>
          <button id="howToBtn" class="chip-btn">? HOW TO PLAY</button>
          <button id="feedbackBtn" class="chip-btn">💬 FEEDBACK</button>
          <a id="privacyLink" class="chip-btn" href="privacy.html" target="_blank" rel="noopener">PRIVACY</a>
          <span class="title-language" aria-label="Language"><button id="langKoBtn" class="chip-btn lang-chip" type="button">한국어</button><button id="langEnBtn" class="chip-btn lang-chip" type="button">English</button></span>''',
'language controls')

rep(Path('game.js'),
"const COLLECTION_REOPEN_KEY='cmh.collection.reopen.v1';",
'''const UI_LANG_KEY='cmh.lang.v1';
let uiLang='ko';
function preferredUiLanguage(){
  try{
    const q=new URLSearchParams(location.search).get('lang');
    if(q==='ko'||q==='en'){localStorage.setItem(UI_LANG_KEY,q);return q}
    const saved=localStorage.getItem(UI_LANG_KEY);
    if(saved==='ko'||saved==='en')return saved;
  }catch(_){}
  return 'ko';
}
function contentHref(name){return uiLang==='en'?'en/'+name+'.html':name+'.html'}
function applyUiLanguage(){
  document.documentElement.lang=uiLang;
  const settings=$('#settingsBtn');if(settings)settings.textContent=uiLang==='en'?'⚙ OPTIONS':'⚙ 옵션';
  const pause=$('#pauseBtn');if(pause)pause.textContent=uiLang==='en'?'OPTIONS':'옵션';
  const info=$('#siteInfoLink');if(info){info.textContent=uiLang==='en'?'ⓘ GAME INFO':'ⓘ 게임 정보';info.href=contentHref('info')}
  const privacy=$('#privacyLink');if(privacy)privacy.href=contentHref('privacy');
  const ko=$('#langKoBtn'),en=$('#langEnBtn');
  if(ko)ko.classList.toggle('active',uiLang==='ko');
  if(en)en.classList.toggle('active',uiLang==='en');
}
function setUiLanguage(lang){
  if(lang!=='ko'&&lang!=='en')return;
  uiLang=lang;
  try{localStorage.setItem(UI_LANG_KEY,lang)}catch(_){}
  applyUiLanguage();
  track('language_change',{lang});
}
function initUiLanguage(){uiLang=preferredUiLanguage();applyUiLanguage()}

const COLLECTION_REOPEN_KEY='cmh.collection.reopen.v1';''',
'language state')

rep(Path('game.js'),
"$('#newGameBtn').onclick=()=>showSlotPicker('new');$('#continueBtn').onclick=()=>{const r=recentSave();if(r){track('continue_game',{slot:r.slot||1,stage:r.stage||1,score:r.score||0});loadSaveData(r)}};$('#loadBtn').onclick=()=>showSlotPicker('load');$('#galleryBtn').onclick=showGallery;const collectionReopenBtn=$('#collectionReopenBtn');if(collectionReopenBtn)collectionReopenBtn.onclick=()=>openReopenCollection('title');$('#settingsBtn').onclick=showSettings;$('#howToBtn').onclick=showHowTo;$('#feedbackBtn').onclick=()=>window.CMH_FEEDBACK?.show?.('title');$('#pauseBtn').onclick=showPause;",
"$('#newGameBtn').onclick=()=>showSlotPicker('new');$('#continueBtn').onclick=()=>{const r=recentSave();if(r){track('continue_game',{slot:r.slot||1,stage:r.stage||1,score:r.score||0});loadSaveData(r)}};$('#loadBtn').onclick=()=>showSlotPicker('load');$('#galleryBtn').onclick=showGallery;const collectionReopenBtn=$('#collectionReopenBtn');if(collectionReopenBtn)collectionReopenBtn.onclick=()=>openReopenCollection('title');$('#settingsBtn').onclick=showSettings;$('#howToBtn').onclick=showHowTo;$('#feedbackBtn').onclick=()=>window.CMH_FEEDBACK?.show?.('title');$('#pauseBtn').onclick=showPause;$('#langKoBtn').onclick=()=>setUiLanguage('ko');$('#langEnBtn').onclick=()=>setUiLanguage('en');",
'language binding')

rep(Path('game.js'),
"loadUnlocked();refreshTitle();ageGate();initAnalytics();window.CMH_ADS?.init?.();registerSW();updateMusicLabel();",
"loadUnlocked();initUiLanguage();refreshTitle();ageGate();initAnalytics();window.CMH_ADS?.init?.();registerSW();updateMusicLabel();",
'language init')

css=root/'styles.css'
s=css.read_text(encoding='utf-8')
if '/* v0.13.7 bilingual */' not in s:
    s += '''
/* v0.13.7 bilingual */
.title-language{display:inline-flex;gap:4px;align-items:center}.lang-chip{min-width:auto!important}.lang-chip.active{border-color:rgba(255,107,187,.7)!important;background:rgba(255,88,174,.18)!important;color:#fff!important;box-shadow:0 0 12px rgba(255,88,174,.14)}
@media(max-width:560px){.title-language{gap:2px}.lang-chip{padding-left:7px!important;padding-right:7px!important}}
'''
    css.write_text(s,encoding='utf-8')

rep(Path('index.html'),'<div class="version">v0.13.6 content hub</div>','<div class="version">v0.13.7 bilingual</div>','version')
rep(Path('config.js'),"VERSION: '0.13.6'","VERSION: '0.13.7'",'config')
rep(Path('sw.js'),"cmh-core-v0.13.6","cmh-core-v0.13.7",'sw')
print('v0.13.7 bilingual home applied')
