from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
css_path = root / "styles.css"
index_path = root / "index.html"

marker = "/* v0.5.9 mobile-viewport hotfix */"
css = css_path.read_text(encoding="utf-8")

block = r'''

/* v0.5.9 mobile-viewport hotfix */
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
  .game-topbar{
    position:absolute;
    z-index:20;
    top:max(2px,env(safe-area-inset-top));
    left:50%;
    transform:translateX(-50%);
    width:min(calc(100vw - 300px),840px)!important;
    height:40px;
    gap:3px;
  }
  .stat{
    min-width:0;
    padding:2px 7px;
    border-radius:10px;
  }
  .stat small{font-size:.42rem}
  .stat strong{font-size:.78rem}
  .icon-btn{
    width:36px;
    height:36px;
    flex:0 0 36px;
  }
  .game-frame{
    position:absolute;
    top:44px;
    left:50%;
    transform:translateX(-50%);
    width:min(calc((100dvh - 76px)*4/3),calc(100vw - 300px),1120px)!important;
    margin:0;
  }
  .game-bottombar{
    position:absolute;
    z-index:20;
    left:50%;
    bottom:2px;
    transform:translateX(-50%);
    width:min(calc((100dvh - 76px)*4/3),calc(100vw - 300px),1120px)!important;
    height:26px;
  }
  .music-label{display:none!important}
  .mobile-controls{
    position:absolute;
    z-index:21;
    inset:44px 8px 28px;
    width:auto!important;
    min-height:0!important;
    padding:0 4px max(4px,env(safe-area-inset-bottom))!important;
    margin:0!important;
    align-items:flex-end;
    pointer-events:none;
  }
  .mobile-controls .move-joystick,
  .mobile-controls .mobile-actions{pointer-events:auto}
  .move-joystick{
    width:104px!important;
    height:104px!important;
    flex-basis:104px!important;
  }
  .joystick-knob{
    width:48px!important;
    height:48px!important;
  }
  .mobile-actions{
    min-width:154px!important;
    gap:6px!important;
  }
  .capture-btn{
    width:84px!important;
    height:84px!important;
    flex-basis:84px!important;
    font-size:.76rem!important;
  }
  .dash-btn{
    width:64px!important;
    height:54px!important;
    flex-basis:64px!important;
  }
  .mini-map{
    width:min(20%,118px)!important;
    min-width:70px!important;
    right:6px!important;
    bottom:6px!important;
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
for old in ("v0.5.3 playfeel beta", "v0.5 feedback beta"):
    if old in index:
        index = index.replace(old, "v0.5.9 mobile beta", 1)
        break
index_path.write_text(index, encoding="utf-8")

print("v0.5.9 mobile viewport patch applied")
