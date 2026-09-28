from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path, old, new, label, allow_already=None):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old in s:
        p.write_text(s.replace(old,new,1),encoding='utf-8')
        return
    if allow_already and allow_already in s:
        return
    raise SystemExit(f'collection reward patch failed: {label}')

rep(Path('game.js'),
'''  openModal(`<h2 class="ending-title">♥ ALL STAGES CLEAR ♥</h2><img class="ending-art" src="assets/images/stage10.webp" alt="Final Queen"><p style="text-align:center;font-size:1.2rem">FINAL SCORE <b>${fmtScore(state.score)}</b></p><p id="endingAutoHint" class="ending-auto-hint">12초 후 타이틀 화면으로 자동 이동합니다.</p><div class="row ending-actions"><button id="endingFeedback" class="btn tertiary">💬 FEEDBACK</button><button id="endingGallery" class="btn secondary">GALLERY</button><button id="endingTitle" class="btn primary">TITLE · 12s</button></div>`);
  $('#endingFeedback').onclick=()=>{clearEndingAutoReturn();window.CMH_FEEDBACK?.show?.('game_complete')};
  $('#endingGallery').onclick=()=>{clearEndingAutoReturn();showGallery()};
  $('#endingTitle').onclick=()=>{clearEndingAutoReturn();showTitle()};
''',
'''  openModal(`<h2 class="ending-title">♥ ALL STAGES CLEAR ♥</h2><img class="ending-art" src="assets/images/stage10.webp" alt="Final Queen"><p style="text-align:center;font-size:1.2rem">FINAL SCORE <b>${fmtScore(state.score)}</b></p><div class="ending-collection"><button id="endingCollection" class="btn primary">📩 MY COMPLETE COLLECTION 받기</button><small>Stage 1~10 완주 이미지를 한 번에 저장하세요.</small></div><p id="endingAutoHint" class="ending-auto-hint">12초 후 타이틀 화면으로 자동 이동합니다.</p><div class="row ending-actions"><button id="endingFeedback" class="btn tertiary">💬 FEEDBACK</button><button id="endingGallery" class="btn secondary">GALLERY</button><button id="endingTitle" class="btn primary">TITLE · 12s</button></div>`);
  $('#endingCollection').onclick=()=>{clearEndingAutoReturn();track('collection_reward_click',{score:state.score});window.CMH_COLLECTION?.show?.({score:state.score})};
  $('#endingFeedback').onclick=()=>{clearEndingAutoReturn();window.CMH_FEEDBACK?.show?.('game_complete')};
  $('#endingGallery').onclick=()=>{clearEndingAutoReturn();showGallery()};
  $('#endingTitle').onclick=()=>{clearEndingAutoReturn();showTitle()};
''',
'ending collection CTA',
allow_already="id=\"endingCollection\"")

rep(Path('index.html'),
'''  <script src="feedback.js"></script>
  <script src="character_masks.js"></script>''',
'''  <script src="feedback.js"></script>
  <script src="collection.js"></script>
  <script src="character_masks.js"></script>''',
'collection script',
allow_already='<script src="collection.js"></script>')

rep(Path('index.html'),
'<div class="version">v0.12.0 containment pressure</div>',
'<div class="version">v0.12.1 complete collection</div>',
'version label',
allow_already='v0.12.1 complete collection')

# Build-time final config: keep public endpoint/configuration with the game bundle.
config=root/'config.js'
s=config.read_text(encoding='utf-8')
if "VERSION: '0.12.0'" in s:
    s=s.replace("VERSION: '0.12.0'", "VERSION: '0.12.1'", 1)
elif "VERSION: '0.12.1'" not in s:
    raise SystemExit('collection reward patch failed: config version')
if 'COLLECTION:' not in s:
    anchor='''  ANALYTICS: {'''
    block='''  COLLECTION: {
    ENABLED: true,
    ENDPOINT: 'https://cvfmikycscmfjmooxhni.supabase.co/functions/v1/cmh-collection-request',
    CONSENT_VERSION: 'cmh-marketing-email-v1-2026-09-29'
  },
  ANALYTICS: {'''
    if anchor not in s:
        raise SystemExit('collection reward patch failed: config collection anchor')
    s=s.replace(anchor,block,1)
config.write_text(s,encoding='utf-8')

# Force service worker refresh and include collection pages in the offline core.
sw=root/'sw.js'
s=sw.read_text(encoding='utf-8')
s=s.replace("cmh-core-v0.12.0","cmh-core-v0.12.1")
if "'collection.js'" not in s:
    old="'analytics.js','feedback.js','character_masks.js'"
    new="'analytics.js','feedback.js','collection.js','collection.html','character_masks.js'"
    if old not in s:
        raise SystemExit('collection reward patch failed: service worker core anchor')
    s=s.replace(old,new,1)
sw.write_text(s,encoding='utf-8')

print('v0.12.1 complete collection applied')
