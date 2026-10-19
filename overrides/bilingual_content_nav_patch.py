from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
base='https://wlsdn8842-cyber.github.io/capture-my-heart/'

site_lang_js="""(()=>{const KEY='cmh.lang.v1';try{const q=new URLSearchParams(location.search).get('lang');if(q==='ko'||q==='en')localStorage.setItem(KEY,q)}catch(_){}document.querySelectorAll('[data-set-lang]').forEach(a=>a.addEventListener('click',()=>{try{localStorage.setItem(KEY,a.dataset.setLang)}catch(_){}}))})();
"""
(root/'site-lang.js').write_text(site_lang_js,encoding='utf-8')

for name in ['info','guide','updates','faq','contact','privacy']:
    p=root/f'{name}.html'
    s=p.read_text(encoding='utf-8')
    canonical=f'<link rel="canonical" href="{base}{name}.html">'
    alt=canonical+f'<link rel="alternate" hreflang="ko" href="{base}{name}.html"><link rel="alternate" hreflang="en" href="{base}en/{name}.html"><link rel="alternate" hreflang="x-default" href="{base}{name}.html">'
    if 'hreflang="en"' not in s:
        s=s.replace(canonical,alt,1)
    switch=f'<span class="site-language" aria-label="Language"><a class="active" data-set-lang="ko" href="{name}.html?lang=ko">한국어</a><a data-set-lang="en" href="en/{name}.html?lang=en">English</a></span>'
    if 'class="site-language"' not in s:
        s=s.replace('</nav></header>',switch+'</nav></header>',1)
    if 'site-lang.js' not in s:
        s=s.replace('</body>','<script src="site-lang.js"></script></body>',1)
    p.write_text(s,encoding='utf-8')

css=root/'site-info.css'
s=css.read_text(encoding='utf-8')
if '/* bilingual site language switch */' not in s:
    s += '''
/* bilingual site language switch */
.site-language{margin-left:auto;display:inline-flex;gap:4px;align-items:center;padding-left:6px}.site-language a{padding:6px 9px!important;font-size:.76rem!important}.site-language a.active{border-color:rgba(255,99,180,.6)!important;background:rgba(255,99,180,.15)!important;color:#fff!important}
@media(max-width:720px){.site-language{width:100%;margin-left:0;justify-content:flex-end;padding-left:0}}
'''
    css.write_text(s,encoding='utf-8')

sitemap=root/'sitemap.xml'
s=sitemap.read_text(encoding='utf-8')
if '/en/info.html' not in s:
    english='''  <url><loc>https://wlsdn8842-cyber.github.io/capture-my-heart/en/info.html</loc><lastmod>2026-10-19</lastmod><priority>0.9</priority></url>
  <url><loc>https://wlsdn8842-cyber.github.io/capture-my-heart/en/guide.html</loc><lastmod>2026-10-19</lastmod><priority>0.9</priority></url>
  <url><loc>https://wlsdn8842-cyber.github.io/capture-my-heart/en/updates.html</loc><lastmod>2026-10-19</lastmod><priority>0.8</priority></url>
  <url><loc>https://wlsdn8842-cyber.github.io/capture-my-heart/en/faq.html</loc><lastmod>2026-10-19</lastmod><priority>0.8</priority></url>
  <url><loc>https://wlsdn8842-cyber.github.io/capture-my-heart/en/contact.html</loc><lastmod>2026-10-19</lastmod><priority>0.7</priority></url>
  <url><loc>https://wlsdn8842-cyber.github.io/capture-my-heart/en/privacy.html</loc><lastmod>2026-10-19</lastmod><priority>0.6</priority></url>
'''
    s=s.replace('</urlset>',english+'</urlset>')
    sitemap.write_text(s,encoding='utf-8')

print('v0.13.7 bilingual content navigation applied')
