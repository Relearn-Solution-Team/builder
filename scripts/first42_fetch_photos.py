"""Fetch only explicitly selected business images; raw page cache stays in OS temp."""
import concurrent.futures
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path(sys.argv[1])
LEADS = {x['slug']: x for x in json.loads((ROOT/'research/2026-11-07/leads.json').read_text(encoding='utf-8'))['leads'][:15]}

class Images(HTMLParser):
    def __init__(self):
        super().__init__(); self.images = []; self.meta = {}
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta': self.meta[a.get('property')] = a.get('content', '')
        if tag == 'img':
            u = a.get('data-src', a.get('src', ''))
            if not any(k in u for k in ['icon','logo','Logo','themes/','data:','modules/']):
                item = (u, a.get('alt', ''))
                if item not in self.images: self.images.append(item)

# Index selections refer to business-owned galleries, never directory recommendation cards.
SELECT = {'damrat-glass':[0], 'lattapon-glass':[28,30,37], 'changnun-glass':[3,4,6],
          'sky-glass-demo':[7,8,9], 'twch-glass-demo':[0],
          'lerdwilai-furniture':[2,3,7], 'phitchayaphat-sofa':[3,4,8]}
jobs = []
for slug, indexes in SELECT.items():
    cache_slug = 'lerdwilai-home' if slug == 'lerdwilai-furniture' else slug
    source = 'https://www.lerdwilaifurniture.com/' if slug == 'lerdwilai-furniture' else LEADS[slug]['source']
    p = Images(); p.feed((CACHE/(cache_slug+'.html')).read_text(encoding='utf-8'))
    for i in indexes:
        u, alt = p.images[i]
        jobs.append((slug, urllib.parse.urljoin(LEADS[slug]['source'],u), alt,
                     source, 'business_website_image'))
for slug in ['kamron-furniture','wuttikorn-metal','changpan-metal','tharathorn-sofa','thongsuk-furniture']:
    p=Images(); p.feed((CACHE/(slug+'-facebook.html')).read_text(encoding='utf-8'))
    jobs.append((slug,p.meta['og:image'],p.meta['og:image:alt'],
                 LEADS[slug].get('facebook') or 'https://www.facebook.com/616092731886397/','facebook_profile_image'))

def fetch(job):
    slug,url,alt,source,kind=job
    try:
        url=html.unescape(url)
        safe=urllib.parse.quote(url,safe=':/?=&%+,;@!~*()[]')
        r=urllib.request.urlopen(urllib.request.Request(safe,headers={'User-Agent':'Mozilla/5.0'}),timeout=35)
        data=r.read(); mime=r.headers.get_content_type()
        if not mime.startswith('image/'): raise ValueError(mime)
        ext={'image/jpeg':'.jpg','image/png':'.png','image/webp':'.webp'}.get(mime,'.img')
        name=slug+'-'+hashlib.sha256(url.encode()).hexdigest()[:9]+ext
        (CACHE/name).write_bytes(data)
        return dict(slug=slug,temporary_file=name,image_url=url,source=source,alt=alt,
                    kind=kind,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
    except Exception as e:return dict(slug=slug,image_url=url,error=str(e))

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
    result=list(pool.map(fetch,jobs))
(CACHE/'downloaded.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
for x in result:print(x['slug'],x.get('temporary_file',x.get('error')),x.get('bytes',''))
