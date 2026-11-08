"""Fetch only the fifteen assigned business profiles; cache outside the repository."""
import concurrent.futures, json, pathlib, tempfile
import requests
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).resolve().parents[1]
CACHE = pathlib.Path(tempfile.gettempdir()) / 'builder-third-source-research'
CACHE.mkdir(exist_ok=True)
LEADS = [x for x in json.loads((ROOT/'research/2026-11-07-round-2/leads.json').read_text(encoding='utf-8'))['leads'] if x['cat'] in ('dress','tattoo','yoga')]

def fetch(x):
    try:
        r=requests.get(x['source'],timeout=35)
        r.encoding='utf-8'
        (CACHE/(x['slug']+'.html')).write_text(r.text,encoding='utf-8')
        s=BeautifulSoup(r.text,'html.parser')
        for t in s(['script','style']): t.decompose()
        (CACHE/(x['slug']+'.txt')).write_text(s.get_text('\n',strip=True),encoding='utf-8')
        return x['slug'],r.status_code,len(r.content),len(s.find_all('img'))
    except Exception as e:return x['slug'],str(e)

def public_profile_assets():
    """Download only each identity-matched Facebook page's own OG profile image."""
    import re, io
    from PIL import Image, ImageOps, ImageDraw
    tiles=[]
    records=[]
    for x in LEADS:
        s=BeautifulSoup((CACHE/(x['slug']+'-facebook.html')).read_text(encoding='utf-8'),'html.parser')
        title=s.select_one('meta[property="og:title"]')['content']
        url=s.select_one('meta[property="og:image"]')['content']
        canonical=s.select_one('meta[property="og:url"]')['content']
        desc=s.select_one('meta[property="og:description"]')['content']
        row={'slug':x['slug'],'profile_url':canonical,'title':title,'description':desc,'image_url':url}
        try:
            r=requests.get(url,timeout=30);r.raise_for_status()
            im=Image.open(io.BytesIO(r.content)).convert('RGB')
            out=ROOT/x['slug']/'assets/source-enrichment';out.mkdir(parents=True,exist_ok=True)
            im.save(out/'facebook-profile.jpg',quality=88)
            row['path']=(out/'facebook-profile.jpg').relative_to(ROOT).as_posix()
            tile=Image.new('RGB',(250,280),'white');tile.paste(ImageOps.contain(im,(250,250)),(0,25));ImageDraw.Draw(tile).text((8,5),x['slug'],fill='black');tiles.append(tile)
            print(x['slug'],im.size,canonical,desc,flush=True)
        except Exception as e: row['error']=str(e);print(x['slug'],str(e),flush=True)
        records.append(row)
    (CACHE/'profiles.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    sheet=Image.new('RGB',(1250,840),'#ddd')
    for i,t in enumerate(tiles):sheet.paste(t,((i%5)*250,(i//5)*280))
    sheet.save(CACHE/'profile-contact-sheet.jpg')

if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for result in pool.map(fetch,LEADS): print(result,flush=True)
