from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path, old, new, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'analytics patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

rep(Path('game.js'),
"function track(name,params={}){ try{window.gtag?.('event',name,params)}catch(_){} }",
"function track(name,params={}){ try{window.gtag?.('event',name,params)}catch(_){} try{window.CMH_ANALYTICS?.track?.(name,params)}catch(_){} }",
'track bridge')

rep(Path('game.js'),
"function showTitle(){\n  state.mode='title';state.paused=false;audio.setDanger(false);gameScreen.classList.add('hidden');titleScreen.classList.remove('hidden');closeModal();refreshTitle();audio.playTitle();\n}",
"function showTitle(){\n  state.mode='title';state.paused=false;audio.setDanger(false);gameScreen.classList.add('hidden');titleScreen.classList.remove('hidden');closeModal();refreshTitle();audio.playTitle();track('title_view',{});\n}",
'title view')

rep(Path('game.js'),
"state.slot=s;state.stage=1;state.score=0;state.lives=3;state.continueCredits=1;loadUnlocked();saveToSlot(s);closeModal();startStage(1,false);",
"state.slot=s;state.stage=1;state.score=0;state.lives=3;state.continueCredits=1;loadUnlocked();saveToSlot(s);track('game_start',{slot:s});closeModal();startStage(1,false);",
'game start')

rep(Path('game.js'),
"} else if(existing){closeModal();loadSaveData(existing)}",
"} else if(existing){track('load_save',{slot:s,stage:existing.stage||1,score:existing.score||0});closeModal();loadSaveData(existing)}",
'load save')

rep(Path('game.js'),
"$('#newGameBtn').onclick=()=>showSlotPicker('new');$('#continueBtn').onclick=()=>{const r=recentSave();if(r)loadSaveData(r)};",
"$('#newGameBtn').onclick=()=>showSlotPicker('new');$('#continueBtn').onclick=()=>{const r=recentSave();if(r){track('continue_game',{slot:r.slot||1,stage:r.stage||1,score:r.score||0});loadSaveData(r)}};",
'continue')

rep(Path('game.js'),
"$('#tutorialOkBtn').onclick=()=>{$('#tutorialOverlay').classList.add('hidden');state.tutorialShown=true;localStorage.setItem('cmh.tutorial','1');state.paused=false;audio.resumeBase()};",
"$('#tutorialOkBtn').onclick=()=>{$('#tutorialOverlay').classList.add('hidden');state.tutorialShown=true;localStorage.setItem('cmh.tutorial','1');track('tutorial_complete',{stage:1});state.paused=false;audio.resumeBase()};",
'tutorial complete')

rep(Path('game.js'),
"if($('#freeContinue'))$('#freeContinue').onclick=()=>{state.continueCredits--;state.lives=1;closeModal();startStage(state.stage,true)};",
"if($('#freeContinue'))$('#freeContinue').onclick=()=>{track('continue_after_game_over',{kind:'free',stage:state.stage});state.continueCredits--;state.lives=1;closeModal();startStage(state.stage,true)};",
'free continue')

rep(Path('game.js'),
"if($('#rewardContinue'))$('#rewardContinue').onclick=async()=>{const ok=await window.CMH_ADS.showRewardedLife();if(ok){state.lives=1;closeModal();startStage(state.stage,true)}else toast('광고가 완료되지 않았습니다',true)};",
"if($('#rewardContinue'))$('#rewardContinue').onclick=async()=>{track('reward_continue_click',{stage:state.stage});const ok=await window.CMH_ADS.showRewardedLife();if(ok){track('continue_after_game_over',{kind:'rewarded',stage:state.stage});state.lives=1;closeModal();startStage(state.stage,true)}else toast('광고가 완료되지 않았습니다',true)};",
'reward continue')

# Ensure analytics client loads before game code.
rep(Path('index.html'),
'  <script src="feedback.js"></script>\n  <script src="game.js"></script>',
'  <script src="analytics.js"></script>\n  <script src="feedback.js"></script>\n  <script src="game.js"></script>',
'analytics script')

rep(Path('index.html'),
'<div class="version">v0.5.3 playfeel beta</div>',
'<div class="version">v0.5.4 analytics beta</div>',
'version label')

print('analytics patch applied')
