from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv)>1 else "_site")
p = root / "index.html"
s = p.read_text(encoding="utf-8")
marker = "ca-pub-6414931308880829"
snippet = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6414931308880829" crossorigin="anonymous"></script>'

if marker not in s:
    if "</head>" not in s:
        raise SystemExit("adsense verify patch failed: </head> not found")
    s = s.replace("</head>", "  " + snippet + "\n</head>", 1)

s = s.replace("v0.6.0 mobile beta", "v0.6.1 adsense verify")
p.write_text(s, encoding="utf-8")
print("v0.6.1 AdSense verification snippet applied")
