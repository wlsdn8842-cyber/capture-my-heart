from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
css_path=root/'styles.css'
css=css_path.read_text(encoding='utf-8')
marker='/* v0.8.1 mobile-landscape HUD rail */'

if marker not in css:
    css += r'''

/* v0.8.1 mobile-landscape HUD rail — MOBILE LANDSCAPE ONLY */
@media (pointer:coarse) and (orientation:landscape){
  .game-screen{
    --ux-hud-h:32px;
    --ux-board-h:calc(var(--mobile-vh,100dvh) - var(--ux-hud-h) - 6px);
    --ux-board-w:min(calc(var(--ux-board-h) * 4 / 3),calc(var(--mobile-vw,100vw) - 214px),1120px);
  }

  /* HUD gets its own rail above the board instead of covering the artwork/playfield. */
  .game-topbar{
    position:absolute!important;
    z-index:35!important;
    top:max(2px,env(safe-area-inset-top))!important;
    left:50%!important;
    transform:translateX(-50%)!important;
    width:var(--ux-board-w)!important;
    height:var(--ux-hud-h)!important;
    min-height:var(--ux-hud-h)!important;
    padding:1px 4px!important;
    gap:2px!important;
    box-sizing:border-box!important;
    border-radius:9px!important;
    background:rgba(10,4,17,.94)!important;
    backdrop-filter:blur(7px)!important;
    -webkit-backdrop-filter:blur(7px)!important;
    box-shadow:0 4px 14px rgba(0,0,0,.28)!important;
  }

  .game-topbar .stat{
    min-width:0!important;
    padding:1px 4px!important;
    border-radius:7px!important;
    overflow:hidden!important;
  }
  .game-topbar .stat:first-child{flex:1.28 1 0!important}
  .game-topbar .stat:not(:first-child){flex:1 1 0!important}
  .game-topbar .stat small{
    font-size:.30rem!important;
    line-height:1!important;
    letter-spacing:.08em!important;
  }
  .game-topbar .stat strong{
    font-size:.59rem!important;
    line-height:1.05!important;
    white-space:nowrap!important;
    overflow:hidden!important;
    text-overflow:ellipsis!important;
  }
  .game-topbar .icon-btn{
    width:27px!important;
    height:27px!important;
    flex:0 0 27px!important;
  }

  /* Board begins below the HUD rail, so no status card overlaps the playfield. */
  .game-frame{
    top:calc(var(--ux-hud-h) + 4px)!important;
    width:var(--ux-board-w)!important;
    max-width:none!important;
    max-height:var(--ux-board-h)!important;
  }

  .game-bottombar{
    width:min(calc(var(--ux-board-w) - 10px),1096px)!important;
  }

  /* Keep the two-thumb controls aligned to the slightly narrower board. */
  .mobile-controls{
    grid-template-columns:minmax(0,1fr) var(--ux-board-w) minmax(0,1fr)!important;
  }
}
'''
    css_path.write_text(css,encoding='utf-8')

print('v0.8.1 mobile landscape HUD rail applied')
