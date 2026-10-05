from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')

def rep(path, old, new, label):
    p=root/path
    s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'collection reliability hotfix failed: {label}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

rep(Path('index.html'),
    '<div class="version">v0.13.0 difficulty v2</div>',
    '<div class="version">v0.13.1 collection reliability</div>',
    'version label')

rep(Path('config.js'),
    "VERSION: '0.13.0'",
    "VERSION: '0.13.1'",
    'config version')

rep(Path('sw.js'),
    "cmh-core-v0.13.0",
    "cmh-core-v0.13.1",
    'service worker cache version')

print('v0.13.1 collection reliability hotfix applied')
