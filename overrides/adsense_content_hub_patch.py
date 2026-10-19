from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path, old, new, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'adsense content hub patch failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

index=root/'index.html'
s=index.read_text(encoding='utf-8')
head_bits=[]
if 'name="description"' not in s:
    head_bits.append('<meta name="description" content="Capture My Heart!는 선을 그어 영역을 점령하고 보스 패턴을 피하는 10스테이지 브라우저 아케이드 게임입니다.">')
if 'rel="canonical"' not in s:
    head_bits.append('<link rel="canonical" href="https://wlsdn8842-cyber.github.io/">')
if 'property="og:title"' not in s:
    head_bits.append('<meta property="og:title" content="Capture My Heart!"><meta property="og:description" content="10개 스테이지를 공략하는 브라우저 기반 영역 점령 아케이드 게임."><meta property="og:type" content="website"><meta property="og:url" content="https://wlsdn8842-cyber.github.io/">')
if '"@type":"VideoGame"' not in s:
    head_bits.append('<script type="application/ld+json">{"@context":"https://schema.org","@type":"VideoGame","name":"Capture My Heart!","url":"https://wlsdn8842-cyber.github.io/","gamePlatform":["Web browser","Mobile browser"],"genre":["Arcade","Territory capture"],"description":"선을 그어 영역을 점령하고 보스 패턴을 피하며 10개 스테이지를 진행하는 브라우저 아케이드 게임.","inLanguage":"ko"}</script>')
if head_bits:
    if '</head>' not in s: raise SystemExit('adsense content hub patch failed: head marker')
    s=s.replace('</head>',''.join(head_bits)+'</head>',1)
    index.write_text(s,encoding='utf-8')

rep(Path('index.html'),
    '<button id="settingsBtn" class="chip-btn">⚙ 옵션</button>',
    '<button id="settingsBtn" class="chip-btn">⚙ 옵션</button><a href="info.html" class="chip-btn site-info-link" aria-label="게임 소개와 사이트 정보">ⓘ 게임 정보</a>',
    'title info link')

css=root/'styles.css'
s=css.read_text(encoding='utf-8')
marker='/* v0.13.6 AdSense content hub */'
if marker not in s:
    s += r'''

/* v0.13.6 AdSense content hub */
.site-info-link{display:inline-flex;align-items:center;justify-content:center;text-decoration:none!important}
.site-info-link:visited{color:inherit}
'''
    css.write_text(s,encoding='utf-8')

rep(Path('index.html'),
    '<div class="version">v0.13.5 key mapping</div>',
    '<div class="version">v0.13.6 content hub</div>',
    'version label')
rep(Path('config.js'),"VERSION: '0.13.5'","VERSION: '0.13.6'",'config version')
rep(Path('sw.js'),"cmh-core-v0.13.5","cmh-core-v0.13.6",'service worker cache version')

print('v0.13.6 AdSense content hub applied')
