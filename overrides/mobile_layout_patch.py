from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
css_path = root / "styles.css"
index_path = root / "index.html"

marker = "/* v0.6.0 mobile-landscape hotfix */"
css = css_path.read_text(encoding="utf-8")

block = r'''

/* v0.6.0 mobile-landscape hotfix */
@media (pointer:coarse), (max-width:800px){
  html,body{
    width:100%;
    height:100%;
    min-height:0;
    overflow:hidden!important;
    overscroll-behavior:none;
  }
  body{position:fixed;inset:0}
  .app-shell{
    width:100%;
    height:100dvh;
    min-height:0!important;
    overflow:hidden;
  }
  .screen{position:fixed;inset:0}
  .title-screen{
    display:flex!important;
    align-items:center;
    justify-content:center;
    overflow:hidden!important;
    padding:0!important;
  }
  .title-stage{
    width:min(100vw,calc(100dvh * 1.776833));
    height:auto!important;
    max-width:100vw;
    max-height:100dvh!important;
    aspect-ratio:1672/941;
    transform:none!important;
    transform-origin:center center!important;
    flex:none;
  }
  .title-stage .title-art{
    object-fit:contain!important;
    object-position:center!important;
  }
  .game-screen{
    height:100dvh;
    min-height:0!important;
    overflow:hidden!important;
    padding:4px max(6px,env(safe-area-inset-right)) max(4px,env(safe-area-inset-bottom)) max(6px,env(safe-area-inset-left));
    justify-content:center;
  }
  .game-topbar{
    flex:0 0 48px;
    width:min(100%,760px)!important;
  }
  .game-frame{
    flex:0 0 auto;
    width:min(calc(100vw - 12px),760px)!important;
    max-height:none;
  }
  .game-bottombar{
    flex:0 0 30px;
    width:min(100%,760px)!important;
  }
  .mobile-controls{
    flex:0 0 auto;
    width:min(100%,760px)!important;
    margin-top:8px;
  }
}

@media (pointer:coarse) and (orientation:portrait), (max-width:800px) and (orientation:portrait){
  .game-screen{
    justify-content:center;
    gap:2px;
  }
  .game-frame{
    width:min(calc(100vw - 12px),calc((100dvh - 260px)*4/3),760px)!important;
  }
  .mobile-controls{
    min-height:120px;
    padding-top:4px;
  }
}

@media (pointer:coarse) and (orientation:landscape), (orientation:landscape) and (max-height:650px){
  html,body,.app-shell{
    height:100dvh!important;
    min-height:0!important;
    overflow:hidden!important;
  }
  .game-screen{
    display:block!important;
    height:100dvh;
    min-height:0!important;
    padding:0 max(4px,env(safe-area-inset-right)) 0 max(4px,env(safe-area-inset-left));
  }

  /* Board uses almost the entire usable browser height. */
  .game-frame{
    position:absolute;
    z-index:10;
    top:6px;
    left:50%;
    transform:translateX(-50%);
    width:min(calc((100dvh - 12px)*4/3),calc(100vw - 220px),1120px)!important;
    max-height:calc(100dvh - 12px)!important;
    margin:0;
  }

  /* HUD overlays the top of the board instead of stealing vertical space. */
  .game-topbar{
    position:absolute;
    z-index:30;
    top:max(8px,env(safe-area-inset-top));
    left:50%;
    transform:translateX(-50%);
    width:min(calc((100dvh - 26px)*4/3),calc(100vw - 238px),1096px)!important;
    height:36px;
    gap:3px;
    padding:2px;
    border-radius:12px;
    background:rgba(13,5,22,.52);
    backdrop-filter:blur(5px);
    -webkit-backdrop-filter:blur(5px);
  }
  .stat{
    min-width:0;
    padding:1px 6px;
    border-radius:9px;
    background:rgba(20,8,30,.46);
  }
  .stat small{font-size:.38rem;line-height:1}
  .stat strong{font-size:.72rem;line-height:1.05}
  .icon-btn{
    width:32px;
    height:32px;
    flex:0 0 32px;
  }

  /* Progress/DASH bar overlays the lower edge of the board. */
  .game-bottombar{
    position:absolute;
    z-index:30;
    left:50%;
    bottom:8px;
    transform:translateX(-50%);
    width:min(calc((100dvh - 26px)*4/3),calc(100vw - 238px),1096px)!important;
    height:24px;
    padding:2px 8px;
    border-radius:10px;
    background:rgba(13,5,22,.52);
    backdrop-filter:blur(5px);
    -webkit-backdrop-filter:blur(5px);
  }
  .music-label{display:none!important}
  .stamina-box{min-width:100px!important}
  .stamina-track{width:64px!important}

  /* Controls live in side gutters and no longer reduce board height. */
  .mobile-controls{
    position:absolute;
    z-index:40;
    inset:0;
    width:auto!important;
    min-height:0!important;
    padding:0!important;
    margin:0!important;
    pointer-events:none;
  }
  .mobile-controls .move-joystick,
  .mobile-controls .mobile-actions{pointer-events:auto}

  .move-joystick{
    position:absolute!important;
    left:max(10px,env(safe-area-inset-left));
    top:50%;
    transform:translateY(-50%);
    width:100px!important;
    height:100px!important;
    flex-basis:100px!important;
  }
  .joystick-knob{
    width:46px!important;
    height:46px!important;
  }

  .mobile-actions{
    position:absolute!important;
    right:max(10px,env(safe-area-inset-right));
    top:50%;
    transform:translateY(-50%);
    display:flex!important;
    flex-direction:column!important;
    align-items:center!important;
    min-width:0!important;
    gap:8px!important;
  }
  .capture-btn{
    width:88px!important;
    height:88px!important;
    flex-basis:88px!important;
    font-size:.75rem!important;
  }
  .dash-btn{
    width:68px!important;
    height:50px!important;
    flex-basis:50px!important;
    font-size:.68rem!important;
  }

  .mini-map{
    width:min(18%,110px)!important;
    min-width:68px!important;
    right:6px!important;
    bottom:34px!important;
  }
  .mini-map.avoid-left{
    left:6px!important;
    right:auto!important;
  }
}
'''

if marker not in css:
    css_path.write_text(css + block, encoding="utf-8")

index = index_path.read_text(encoding="utf-8")
for old in ("v0.5.4 analytics beta", "v0.5.3 playfeel beta", "v0.5 feedback beta"):
    if old in index:
        index = index.replace(old, "v0.6.0 mobile beta", 1)
        break
index_path.write_text(index, encoding="utf-8")

print("v0.6.0 mobile landscape patch applied")
