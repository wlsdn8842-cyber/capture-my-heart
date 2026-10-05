from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path, old, new, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'hud audio controls patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

rep(Path('index.html'),
'''        <div class="stat"><small>LIFE</small><strong id="lifeLabel">♥♥♥</strong></div>
        <button id="pauseBtn" class="icon-btn" title="Pause">Ⅱ</button>''',
'''        <div class="stat"><small>LIFE</small><strong id="lifeLabel">♥♥♥</strong></div>
        <div class="hud-actions" aria-label="게임 빠른 설정">
          <button id="pauseBtn" class="icon-btn option-btn" title="옵션 / 일시정지">옵션</button>
          <div class="hud-audio-controls" aria-label="오디오 빠른 설정">
            <button id="bgmToggleBtn" class="hud-audio-btn" type="button" aria-label="배경음 켜기 또는 끄기" aria-pressed="true">♫ BGM</button>
            <input id="hudVolumeRange" class="hud-volume-range" type="range" min="0" max="1" step="0.01" value="0.68" aria-label="배경음 볼륨">
            <span id="hudVolumePct" class="hud-volume-pct">68%</span>
          </div>
        </div>''',
'hud audio controls markup')

rep(Path('game.js'),
"function defaultSettings(){ return {volume:0.68, muted:false, sfx:true}; }",
"function defaultSettings(){ return {volume:0.68, muted:false, sfx:true, bgm:true}; }",
'default bgm setting')

rep(Path('game.js'),
'''  apply(){
    const m=this.muted; const v=this.settings.volume;
    this.base.muted=m; this.danger.muted=m; this.jingle.muted=m;
    this.base.volume=this.dangerOn?Math.min(.18,v*.3):v;
    this.danger.volume=this.dangerOn?v:0;
    this.jingle.volume=v;
  }
  setMuted(value, temporary=false){ this.muted=!!value; if(!temporary){this.settings.muted=this.muted; saveSettings();} this.apply(); updateMusicLabel(); }
  setVolume(v){ this.settings.volume=Math.max(0,Math.min(1,Number(v))); saveSettings(); this.apply(); updateMusicLabel(); }''',
'''  apply(){
    const m=this.muted; const v=this.settings.volume;
    const musicMuted=m||this.settings.bgm===false;
    this.base.muted=musicMuted; this.danger.muted=musicMuted; this.jingle.muted=musicMuted;
    this.base.volume=this.dangerOn?Math.min(.18,v*.3):v;
    this.danger.volume=this.dangerOn?v:0;
    this.jingle.volume=v;
  }
  setMuted(value, temporary=false){ this.muted=!!value; if(!temporary){this.settings.muted=this.muted; saveSettings();} this.apply(); updateMusicLabel(); }
  setBgm(value){ this.settings.bgm=!!value; saveSettings(); this.apply(); updateMusicLabel(); if(this.settings.bgm&&!this.muted)this.resumeBase(); }
  setVolume(v){ this.settings.volume=Math.max(0,Math.min(1,Number(v))); saveSettings(); this.apply(); updateMusicLabel(); }''',
'dedicated bgm toggle')

rep(Path('game.js'),
'''  openModal(`<h2>⚙ SETTINGS</h2><div class="settings-grid">
    <div class="setting-line"><label>BGM / SFX</label><input id="volRange" type="range" min="0" max="1" step="0.01" value="${s.volume}"><span id="volPct">${Math.round(s.volume*100)}%</span></div>
    <div class="toggle"><span>Mute</span><input id="muteCheck" type="checkbox" ${audio.muted?'checked':''}></div>
    <div class="toggle"><span>Simple SFX</span><input id="sfxCheck" type="checkbox" ${s.sfx?'checked':''}></div>
  </div><div style="margin-top:16px"><button id="settingsClose" class="btn primary">CLOSE</button></div>`);
  $('#volRange').oninput=e=>{audio.setVolume(e.target.value);$('#volPct').textContent=`${Math.round(e.target.value*100)}%`};
  $('#muteCheck').onchange=e=>audio.setMuted(e.target.checked);
  $('#sfxCheck').onchange=e=>{audio.settings.sfx=e.target.checked;saveSettings()};''',
'''  openModal(`<h2>⚙ SETTINGS</h2><div class="settings-grid">
    <div class="setting-line"><label>BGM / SFX</label><input id="volRange" type="range" min="0" max="1" step="0.01" value="${s.volume}"><span id="volPct">${Math.round(s.volume*100)}%</span></div>
    <div class="toggle"><span>BGM</span><input id="bgmCheck" type="checkbox" ${s.bgm!==false?'checked':''}></div>
    <div class="toggle"><span>Mute All</span><input id="muteCheck" type="checkbox" ${audio.muted?'checked':''}></div>
    <div class="toggle"><span>Simple SFX</span><input id="sfxCheck" type="checkbox" ${s.sfx?'checked':''}></div>
  </div><div style="margin-top:16px"><button id="settingsClose" class="btn primary">CLOSE</button></div>`);
  $('#volRange').oninput=e=>{audio.setVolume(e.target.value);$('#volPct').textContent=`${Math.round(e.target.value*100)}%`};
  $('#bgmCheck').onchange=e=>audio.setBgm(e.target.checked);
  $('#muteCheck').onchange=e=>audio.setMuted(e.target.checked);
  $('#sfxCheck').onchange=e=>{audio.settings.sfx=e.target.checked;saveSettings()};''',
'settings bgm toggle sync')

rep(Path('game.js'),
"function updateMusicLabel(){const label=$('#musicLabel');if(!label)return;label.textContent=`${audio.muted?'🔇':'♫'} ${state.mode==='playing'?STAGES[state.stage]?.name:'Capture My Heart!'}`}",
'''function updateHudAudioControls(){
  const bgm=$('#bgmToggleBtn'),range=$('#hudVolumeRange'),pct=$('#hudVolumePct');
  const audible=audio.settings.bgm!==false&&!audio.muted;
  if(bgm){bgm.textContent=audible?'♫ BGM':'🔇 BGM';bgm.classList.toggle('off',!audible);bgm.setAttribute('aria-pressed',String(audible));bgm.title=audible?'배경음 끄기':'배경음 켜기'}
  if(range&&document.activeElement!==range)range.value=String(audio.settings.volume);
  if(pct)pct.textContent=`${Math.round(audio.settings.volume*100)}%`;
}
function updateMusicLabel(){const label=$('#musicLabel');if(label)label.textContent=`${audio.muted||audio.settings.bgm===false?'🔇':'♫'} ${state.mode==='playing'?STAGES[state.stage]?.name:'Capture My Heart!'}`;updateHudAudioControls()}''',
'hud audio status sync')

rep(Path('game.js'),
"$('#newGameBtn').onclick=()=>showSlotPicker('new');$('#continueBtn').onclick=()=>{const r=recentSave();if(r){track('continue_game',{slot:r.slot||1,stage:r.stage||1,score:r.score||0});loadSaveData(r)}};$('#loadBtn').onclick=()=>showSlotPicker('load');$('#galleryBtn').onclick=showGallery;const collectionReopenBtn=$('#collectionReopenBtn');if(collectionReopenBtn)collectionReopenBtn.onclick=()=>openReopenCollection('title');$('#settingsBtn').onclick=showSettings;$('#howToBtn').onclick=showHowTo;$('#feedbackBtn').onclick=()=>window.CMH_FEEDBACK?.show?.('title');$('#pauseBtn').onclick=showPause;",
"$('#newGameBtn').onclick=()=>showSlotPicker('new');$('#continueBtn').onclick=()=>{const r=recentSave();if(r){track('continue_game',{slot:r.slot||1,stage:r.stage||1,score:r.score||0});loadSaveData(r)}};$('#loadBtn').onclick=()=>showSlotPicker('load');$('#galleryBtn').onclick=showGallery;const collectionReopenBtn=$('#collectionReopenBtn');if(collectionReopenBtn)collectionReopenBtn.onclick=()=>openReopenCollection('title');$('#settingsBtn').onclick=showSettings;$('#howToBtn').onclick=showHowTo;$('#feedbackBtn').onclick=()=>window.CMH_FEEDBACK?.show?.('title');$('#pauseBtn').onclick=showPause;const bgmToggleBtn=$('#bgmToggleBtn');if(bgmToggleBtn)bgmToggleBtn.onclick=()=>{const on=audio.settings.bgm!==false&&!audio.muted;if(on)audio.setBgm(false);else{if(audio.muted)audio.setMuted(false);audio.setBgm(true)}};const hudVolumeRange=$('#hudVolumeRange');if(hudVolumeRange)hudVolumeRange.oninput=e=>audio.setVolume(e.target.value);",
'hud audio event bindings')

css=root/'styles.css'
s=css.read_text(encoding='utf-8')
marker='/* v0.13.4 HUD audio controls */'
if marker not in s:
    s += r'''

/* v0.13.4 HUD audio controls */
.hud-actions{margin-left:6px;display:flex;align-items:center;gap:7px;min-width:0;white-space:nowrap}
.option-btn{width:auto!important;min-width:54px!important;padding:0 11px!important;font-size:.72rem!important;font-weight:900!important;letter-spacing:.02em!important}
.hud-audio-controls{height:38px;display:flex;align-items:center;gap:7px;padding:4px 9px;border:1px solid rgba(255,255,255,.13);border-radius:999px;background:rgba(255,255,255,.04);box-shadow:inset 0 1px rgba(255,255,255,.05)}
.hud-audio-btn{height:28px;min-width:70px;padding:0 9px;border:1px solid rgba(77,240,255,.28);border-radius:999px;background:rgba(77,240,255,.08);color:#dffcff;font-size:.68rem;font-weight:900;cursor:pointer;white-space:nowrap}
.hud-audio-btn:hover{background:rgba(77,240,255,.14)}
.hud-audio-btn.off{border-color:rgba(255,110,145,.28);background:rgba(255,78,120,.07);color:#ffc3d2}
.hud-volume-range{width:96px;min-width:64px;accent-color:#ff64b1;cursor:pointer}
.hud-volume-pct{width:34px;text-align:right;color:#d8c6de;font-size:.58rem;font-weight:850;font-variant-numeric:tabular-nums}
@media (max-width:800px),(pointer:coarse){
  .hud-actions{margin-left:2px!important;gap:3px!important}
  .option-btn{min-width:38px!important;padding:0 5px!important;font-size:.48rem!important}
  .hud-audio-controls{height:27px!important;gap:3px!important;padding:1px 4px!important}
  .hud-audio-btn{height:23px!important;min-width:42px!important;padding:0 4px!important;font-size:.42rem!important}
  .hud-volume-range{width:48px!important;min-width:42px!important}
  .hud-volume-pct{display:none!important}
}
@media (pointer:coarse) and (orientation:portrait){
  .hud-audio-controls{max-width:96px!important}
  .hud-volume-range{width:43px!important;min-width:40px!important}
}
'''
    css.write_text(s,encoding='utf-8')

rep(Path('index.html'),
    '<div class="version">v0.13.3 mobile rotation recovery</div>',
    '<div class="version">v0.13.4 hud audio controls</div>',
    'version label')
rep(Path('config.js'),"VERSION: '0.13.3'","VERSION: '0.13.4'",'config version')
rep(Path('sw.js'),"cmh-core-v0.13.3","cmh-core-v0.13.4",'service worker cache version')

print('v0.13.4 HUD audio controls applied')
