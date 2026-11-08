"""Source inspection for the 15 first-batch sign/CCTV/garden pages. No shared writes."""
import concurrent.futures, json, os, pathlib, re, tempfile
import requests
from bs4 import BeautifulSoup
ROOT = pathlib.Path(__file__).resolve().parents[1]
CACHE = pathlib.Path(tempfile.gettempdir()) / 'builder-source-second'
CACHE.mkdir(exist_ok=True)
LEADS = [x for x in json.loads((ROOT/'research/2026-11-07/leads.json').read_text(encoding='utf-8'))['leads'] if x['cat'] in ('sign','cctv','garden')]
def inspect(x):
    slug=x['slug']; urls=list(dict.fromkeys([x['source']] + ([x['facebook']] if x.get('facebook') else [])))
    results=[]
    for i,url in enumerate(urls):
        try:
            r=requests.get(url,timeout=35,headers={'User-Agent':'Mozilla/5.0'})
            r.encoding=r.apparent_encoding if 'charset' not in r.headers.get('content-type','') else r.encoding
            soup=BeautifulSoup(r.text,'html.parser')
            (CACHE/f'{slug}-{i}.html').write_text(r.text,encoding='utf-8')
            images=[dict(n.attrs) for n in soup.select('img')]
            metas=[dict(n.attrs) for n in soup.select('meta[property="og:image"]')]
            for n in soup.select('script,style,nav'): n.decompose()
            txt=soup.get_text(' ',strip=True)
            (CACHE/f'{slug}-{i}.txt').write_text(txt,encoding='utf-8')
            results.append({'url':url,'final_url':r.url,'http':r.status_code,'text':txt[:24000],'images':images[:100],'og':metas,'links':[dict(n.attrs) for n in soup.select('a[href]') if any(s in n.get('href','') for s in ['map','contact','facebook','line.me','lin.ee','gallery'])][:35]})
        except Exception as e: results.append({'url':url,'error':str(e)})
    (CACHE/f'{slug}.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    return slug,[(r.get('http',r.get('error')),len(r.get('text','')),len(r.get('images',[]))) for r in results]
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        for result in pool.map(inspect,LEADS): print(result,flush=True)
