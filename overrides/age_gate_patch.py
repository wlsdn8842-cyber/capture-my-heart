from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def replace(path, old, new, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

old_gate='''    <section id="ageGate" class="full-overlay age-gate hidden" aria-modal="true" role="dialog">
      <div class="modal-card compact">
        <h1>Capture My Heart!</h1>
        <p>이 게임에는 성인 취향의 비노골적 팬서비스 일러스트가 포함되어 있습니다.</p>
        <p class="muted">모든 등장 캐릭터는 성인으로 설정되어 있습니다.</p>
        <button id="ageConfirmBtn" class="btn primary">18세 이상입니다</button>
      </div>
    </section>'''
new_gate='''    <section id="ageGate" class="full-overlay age-gate hidden" aria-modal="true" role="dialog" aria-labelledby="ageGateTitle" aria-describedby="ageGateDesc">
      <div class="modal-card compact age-gate-card">
        <div class="age-badge" aria-hidden="true">19+</div>
        <div class="age-kicker">AGE CHECK · 성인 콘텐츠 안내</div>
        <h1 id="ageGateTitle">Capture My Heart!</h1>
        <p id="ageGateDesc" class="age-main-copy"><strong>이 게임은 19세 이상 이용자를 위한 콘텐츠입니다.</strong><br>This game is intended for players aged 19 and over.</p>
        <p>성인 취향의 비노골적 팬서비스 일러스트 및 연출이 포함되어 있습니다.</p>
        <p class="muted">모든 등장 캐릭터는 성인으로 설정되어 있습니다.</p>
        <label class="age-remember"><input id="ageRemember" type="checkbox" checked> <span>이 브라우저에서 30일 동안 다시 묻지 않기</span></label>
        <div class="age-actions">
          <button id="ageConfirmBtn" class="btn primary">19세 이상입니다 · ENTER</button>
          <button id="ageExitBtn" class="btn tertiary">나가기 · LEAVE</button>
        </div>
        <p class="age-note">※ PASS/NICE 등의 본인인증이 아닌 자가 연령 확인 절차입니다.</p>
      </div>
    </section>'''
replace(Path('index.html'),old_gate,new_gate,'age gate markup')

old_func="function ageGate(){const gate=$('#ageGate');if(localStorage.getItem('cmh.age')==='1'){gate.classList.add('hidden');return}gate.classList.remove('hidden');$('#ageConfirmBtn').onclick=()=>{localStorage.setItem('cmh.age','1');gate.classList.add('hidden');audio.playTitle()}}"
new_func=r'''const AGE_PERSIST_KEY='cmh.age19.acceptedAt';
const AGE_SESSION_KEY='cmh.age19.session';
const AGE_REMEMBER_MS=30*24*60*60*1000;
function ageGate(){
  const gate=$('#ageGate'),confirm=$('#ageConfirmBtn'),exit=$('#ageExitBtn'),remember=$('#ageRemember');
  let persisted=false,sessionOk=false;
  try{
    const acceptedAt=Number(localStorage.getItem(AGE_PERSIST_KEY)||0);
    persisted=acceptedAt>0&&(Date.now()-acceptedAt)<AGE_REMEMBER_MS;
    if(acceptedAt&&!persisted)localStorage.removeItem(AGE_PERSIST_KEY);
  }catch(_){}
  try{sessionOk=sessionStorage.getItem(AGE_SESSION_KEY)==='1'}catch(_){}
  if(persisted||sessionOk){gate.classList.add('hidden');document.body.classList.remove('age-gate-open');return}
  gate.classList.remove('hidden');document.body.classList.add('age-gate-open');
  confirm.onclick=()=>{
    try{
      if(remember?.checked)localStorage.setItem(AGE_PERSIST_KEY,String(Date.now()));
      else sessionStorage.setItem(AGE_SESSION_KEY,'1');
      localStorage.removeItem('cmh.age');
    }catch(_){}
    gate.classList.add('hidden');document.body.classList.remove('age-gate-open');
    track('age_gate_confirm',{remember:!!remember?.checked});audio.playTitle();
  };
  exit.onclick=()=>{
    track('age_gate_reject',{});
    gate.innerHTML='<div class="modal-card compact age-gate-card age-denied"><div class="age-badge" aria-hidden="true">19+</div><h1>이용할 수 없습니다</h1><p>19세 미만은 이 게임을 이용할 수 없습니다.</p><p class="muted">This game is only available to players aged 19 and over.</p><button id="ageLeaveNow" class="btn tertiary">페이지 나가기 · LEAVE</button></div>';
    const leave=$('#ageLeaveNow');if(leave)leave.onclick=()=>{try{if(history.length>1)history.back();else location.replace('about:blank')}catch(_){location.replace('about:blank')}};
  };
}'''
replace(Path('game.js'),old_func,new_func,'age gate logic')

css=root/'styles.css'
s=css.read_text(encoding='utf-8')
marker='/* v0.6.8 19+ age gate */'
if marker not in s:
    s += r'''

/* v0.6.8 19+ age gate */
.age-gate{position:fixed!important;z-index:20000!important;background:radial-gradient(circle at 50% 20%,#2b0b38,#07030c 62%)!important;backdrop-filter:none!important;-webkit-backdrop-filter:none!important}
.age-gate-card{width:min(520px,94vw)!important;padding:30px 28px!important;border-color:rgba(255,109,174,.42)!important;box-shadow:0 30px 100px rgba(0,0,0,.78),0 0 44px rgba(255,57,150,.16)!important}
.age-badge{width:72px;height:72px;margin:0 auto 10px;display:grid;place-items:center;border-radius:50%;border:3px solid #ff5ca9;color:#fff;font-weight:950;font-size:1.35rem;letter-spacing:.02em;background:linear-gradient(145deg,#381047,#120819);box-shadow:0 0 24px rgba(255,77,160,.32),inset 0 0 20px rgba(255,255,255,.05)}
.age-kicker{margin:0 0 7px;color:#ff9dcc;font-size:.72rem;font-weight:900;letter-spacing:.15em}
.age-gate-card h1{margin:0 0 16px;font-size:clamp(1.8rem,5vw,2.55rem)}
.age-main-copy{line-height:1.55;margin:0 0 12px}.age-main-copy strong{color:#fff4fa}
.age-remember{display:flex;align-items:flex-start;gap:9px;text-align:left;margin:18px 0 14px;padding:12px 13px;border:1px solid rgba(255,255,255,.12);border-radius:13px;background:rgba(255,255,255,.045);color:#eee1f0;font-size:.86rem;cursor:pointer}.age-remember input{margin-top:2px;accent-color:#ff4da0}
.age-actions{display:grid;gap:9px}.age-actions .btn{width:100%;font-weight:850}.age-note{margin:14px 0 0!important;font-size:.72rem;color:#aa9bb2;line-height:1.45}
.age-denied{padding-top:34px!important}.age-denied .btn{width:100%;margin-top:10px}
body.age-gate-open .title-screen,body.age-gate-open .game-screen{pointer-events:none;user-select:none}
@media(max-width:560px){.age-gate-card{padding:22px 18px!important}.age-badge{width:62px;height:62px}.age-remember{font-size:.78rem}.age-main-copy{font-size:.9rem}}
'''
    css.write_text(s,encoding='utf-8')

index=root/'index.html'
s=index.read_text(encoding='utf-8')
for oldver in ('v0.6.4 visual refresh','v0.6.0 mobile beta','v0.5.8 mobile beta'):
    if oldver in s:
        s=s.replace(oldver,'v0.6.8 19+ age gate',1)
        break
index.write_text(s,encoding='utf-8')
print('v0.6.8 19+ age gate applied')
