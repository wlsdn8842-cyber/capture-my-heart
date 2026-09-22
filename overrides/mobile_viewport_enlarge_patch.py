from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
css_path=root/'styles.css'
css=css_path.read_text(encoding='utf-8')
marker='/* v0.8.2 mobile viewport enlarge tuning */'

if marker not in css:
    css += r'''

/* v0.8.2 mobile viewport enlarge tuning — MOBILE ONLY / DESKTOP FREEZE */
@media (pointer:coarse) and (orientation:portrait){
  .game-screen{
    gap:1px!important;
    padding:max(1px,env(safe-area-inset-top)) 1px max(2px,env(safe-area-inset-bottom))!important;
  }
  .game-topbar{
    flex:0 0 40px!important;height:40px!important;width:calc(100% - 2px)!important;padding:1px!important;
  }
  .game-topbar .stat{padding:1px 2px!important}
  .game-topbar .stat small{font-size:.35rem!important}
  .game-topbar .stat strong{font-size:.64rem!important}
  .game-topbar .icon-btn{width:30px!important;height:30px!important;flex:0 0 30px!important}
  .game-frame{
    width:min(calc(var(--mobile-vw,100vw) - 2px),calc((var(--mobile-vh,100dvh) - 184px) * 1.22),760px)!important;
    aspect-ratio:1.22/1!important;
    max-height:calc(var(--mobile-vh,100dvh) - 184px)!important;
    margin:0 auto!important;
  }
  .game-bottombar{
    width:min(calc(var(--mobile-vw,100vw) - 4px),760px)!important;height:20px!important;min-height:20px!important;
    padding:0 4px!important;margin:0 auto!important;
  }
  .progress-shell{height:7px!important}
  .stamina-box{min-width:82px!important;gap:3px!important;font-size:.46rem!important}
  .stamina-track{width:54px!important;height:6px!important}
  .mobile-controls{
    width:min(calc(var(--mobile-vw,100vw) - 4px),760px)!important;min-height:98px!important;height:98px!important;
    padding:1px max(6px,env(safe-area-inset-right)) max(1px,env(safe-area-inset-bottom)) max(6px,env(safe-area-inset-left))!important;
    margin:0 auto!important;
  }
  .move-joystick{width:94px!important;height:94px!important;flex-basis:94px!important}
  .joystick-knob{width:44px!important;height:44px!important}
  .capture-btn{width:80px!important;height:80px!important;flex-basis:80px!important;font-size:.66rem!important}
  .dash-btn{width:68px!important;height:44px!important;flex-basis:44px!important;font-size:.60rem!important}
  .mobile-actions{gap:5px!important}
  .mini-map{width:min(17%,82px)!important;min-width:58px!important;bottom:23px!important}
}

@media (pointer:coarse) and (orientation:landscape){
  .game-screen{
    --ux-hud-h:30px;
    --ux-board-h:calc(var(--mobile-vh,100dvh) - var(--ux-hud-h) - 4px);
    --ux-board-w:min(calc(var(--ux-board-h) * 1.46),calc(var(--mobile-vw,100vw) - 202px),1180px);
    padding:0 max(1px,env(safe-area-inset-right)) 0 max(1px,env(safe-area-inset-left))!important;
  }
  .game-topbar{
    height:var(--ux-hud-h)!important;min-height:var(--ux-hud-h)!important;width:var(--ux-board-w)!important;padding:1px 3px!important;
  }
  .game-topbar .stat{padding:0 3px!important}
  .game-topbar .stat small{font-size:.28rem!important}
  .game-topbar .stat strong{font-size:.56rem!important}
  .game-topbar .icon-btn{width:25px!important;height:25px!important;flex:0 0 25px!important}
  .game-frame{
    top:calc(var(--ux-hud-h) + 3px)!important;width:var(--ux-board-w)!important;max-width:none!important;
    max-height:var(--ux-board-h)!important;aspect-ratio:1.46/1!important;
  }
  .game-bottombar{
    width:min(calc(var(--ux-board-w) - 6px),1168px)!important;height:20px!important;bottom:3px!important;padding:0 5px!important;
  }
  .mobile-controls{grid-template-columns:minmax(0,1fr) var(--ux-board-w) minmax(0,1fr)!important}
  .move-joystick{margin-right:4px!important;width:100px!important;height:100px!important;flex-basis:100px!important}
  .joystick-knob{width:46px!important;height:46px!important}
  .mobile-actions{margin-left:4px!important;gap:9px!important}
  .capture-btn{width:92px!important;height:92px!important;flex-basis:92px!important}
  .dash-btn{width:74px!important;height:58px!important;flex-basis:58px!important}
  .mini-map{width:min(14%,92px)!important;min-width:60px!important;bottom:24px!important}
}
'''
    css_path.write_text(css,encoding='utf-8')

print('v0.8.2 mobile viewport enlarge tuning applied')
