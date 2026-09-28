from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path,old,new,label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'stage1 char gate patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

anchor="""function checkMilestone(){
  if(tutorial.active)return;
  const a=state.area;
  if(a>=99&&state.clearMilestone<100){state.clearMilestone=100;unlockStage(state.stage);showClearModal(100);return}
  if(a>=90&&state.clearMilestone<90){state.clearMilestone=90;unlockStage(state.stage);showClearModal(90);return}
  if(a>=80&&state.clearMilestone<80){state.clearMilestone=80;unlockStage(state.stage);showClearModal(80)}
}"""
replacement="""function stageProgressMetric(){
  if(state.stage===1&&Number.isFinite(state.characterArea)){
    return {kind:'character',label:'CHAR',value:state.characterArea};
  }
  return {kind:'area',label:'AREA',value:state.area};
}
function checkMilestone(){
  if(tutorial.active)return;
  const m=stageProgressMetric(),a=m.value;
  const perfectTarget=m.kind==='character'?100:99;
  if(a>=perfectTarget&&state.clearMilestone<100){state.clearMilestone=100;unlockStage(state.stage);showClearModal(100);return}
  if(a>=90&&state.clearMilestone<90){state.clearMilestone=90;unlockStage(state.stage);showClearModal(90);return}
  if(a>=80&&state.clearMilestone<80){state.clearMilestone=80;unlockStage(state.stage);showClearModal(80)}
}"""
rep(Path('game.js'),anchor,replacement,'milestone metric')

rep(Path('game.js'),
"$('#stageLabel').textContent=`${state.stage} · ${STAGES[state.stage]?.name||''}`;$('#scoreLabel').textContent=fmtScore(state.score);$('#areaLabel').textContent=`${state.area.toFixed(1)}%`;$('#timeLabel').textContent=Math.max(0,Math.ceil(state.timeLeft));",
"$('#stageLabel').textContent=`${state.stage} · ${STAGES[state.stage]?.name||''}`;$('#scoreLabel').textContent=fmtScore(state.score);const progress=stageProgressMetric();const areaEl=$('#areaLabel');areaEl.textContent=`${progress.value.toFixed(1)}%`;const areaCaption=areaEl?.parentElement?.querySelector('small');if(areaCaption)areaCaption.textContent=progress.label;$('#timeLabel').textContent=Math.max(0,Math.ceil(state.timeLeft));",
'hud metric label')

rep(Path('game.js'),
"$('#progressBar').style.width=`${Math.min(100,state.area)}%`;",
"$('#progressBar').style.width=`${Math.min(100,progress.value)}%`;",
'progress bar metric')

rep(Path('game.js'),
"gameScreen.classList.toggle('hud-clear',state.area>=80);gameScreen.classList.toggle('hud-bonus',state.area>=90);gameScreen.classList.toggle('hud-perfect',state.area>=99);",
"gameScreen.classList.toggle('hud-clear',progress.value>=80);gameScreen.classList.toggle('hud-bonus',progress.value>=90);gameScreen.classList.toggle('hud-perfect',progress.value>=(progress.kind==='character'?100:99));",
'hud threshold metric')

rep(Path('game.js'),
"state.score+=bonusPts;updateHUD();\n  audio.playJingle",
"state.score+=bonusPts;updateHUD();const progress=stageProgressMetric();\n  audio.playJingle",'clear metric local')

rep(Path('game.js'),
'<div><small>AREA</small><strong>${state.area.toFixed(1)}%</strong></div>',
'<div><small>${progress.label}</small><strong>${progress.value.toFixed(1)}%</strong></div>',
'clear card metric')

rep(Path('game.js'),
"track('stage_milestone',{stage:state.stage,area:state.area,milestone:level,score:state.score});",
"track('stage_milestone',{stage:state.stage,area:state.area,character_area:Number.isFinite(state.characterArea)?Number(state.characterArea.toFixed(2)):null,metric:progress.kind,metric_value:Number(progress.value.toFixed(2)),milestone:level,score:state.score});",
'milestone analytics')

rep(Path('game.js'),
"<small>판정 미적용 · ${state.characterMaskTotal} cells</small>",
"<small>${state.stage===1?'판정 저용':'판정 미적용'} · ${state.characterMaskTotal} cells</small>",'debug gate label')

rep(Path('index.html'),
'<div class="version">v0.11.0 mask shadow</div>',
'<div class="version">v0.11.1 stage1 char gate</div>',
'version label')

print('v0.11.1 Stage 1 character gate applied')
