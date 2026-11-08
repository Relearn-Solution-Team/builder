"""Download only manually selected images from each business's own content."""
import concurrent.futures, hashlib, io, json, pathlib, tempfile
from urllib.parse import urljoin
import requests
from PIL import Image, ImageOps, ImageDraw
from source_second_batch import ROOT, CACHE

# Indexes were reviewed in the source DOM. Webchang's three images are all
# recommended OTHER providers, and YellowPages recommendations are excluded.
SELECTIONS = {
    'ideaplus-sign': ('ideaplus-sign', [29,30,31,34]),
    'nbmedia-sign': ('nbmedia-sign', [3,4,5,6]),
    'asign-graphic': ('asign-graphic', [48,49,50,54]),
    'kongthong-sign': ('kong-home', [7,4,11,17]),
    'changnon-cctv-demo': ('changnon-cctv-demo', [55,56,57,58]),
    'homesat-hd-demo': ('home-gallery', [29,30,31,32]),
    'greenery-landscape': ('green-nana', [1]),
    'johnchaorai-garden': ('johnchaorai-garden', [5,6,7,10]),
}
def download(task):
    slug,key,idx,seq=task
    data=json.loads((CACHE/f'{key}.json').read_text(encoding='utf-8'))
    data=data[0] if isinstance(data,list) else data
    node=data['images'][idx]
    url=urljoin(data.get('final_url',data['url']),node.get('data-src') or node['src'])
    try:
        r=requests.get(url,timeout=40,headers={'User-Agent':'Mozilla/5.0','Referer':data['url']});r.raise_for_status()
        im=ImageOps.exif_transpose(Image.open(io.BytesIO(r.content))).convert('RGB')
        original_size=list(im.size)
        if min(im.size)<120: raise ValueError('Too small to be a useful business photo')
        im.thumbnail((1600,1600))
        dest=ROOT/slug/'assets'/f'source-second-{seq}.webp';dest.parent.mkdir(exist_ok=True)
        im.save(dest,'WEBP',quality=87)
        return {'slug':slug,'path':dest.relative_to(ROOT).as_posix(),'source_page':data['url'],'image_url':url,'source_alt':node.get('alt',''),'original_dimensions':original_size,'dimensions':list(im.size),'original_sha256':hashlib.sha256(r.content).hexdigest(),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'selection':'Business-owned website gallery or matching seller listing; excludes recommendations','visually_reviewed':False}
    except Exception as e:return {'slug':slug,'image_url':url,'error':str(e)}

if __name__=='__main__':
    tasks=[(slug,key,idx,seq) for slug,(key,indices) in SELECTIONS.items() for seq,idx in enumerate(indices,1)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        results=list(pool.map(download,tasks))
    (CACHE/'downloads.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    good=[r for r in results if 'path' in r]
    sheet=Image.new('RGB',(1000,200*((len(good)+3)//4)),'white');draw=ImageDraw.Draw(sheet)
    for j,r in enumerate(good):
        im=Image.open(ROOT/r['path']);im.thumbnail((242,166));x=(j%4)*250;y=(j//4)*200;sheet.paste(im,(x,y));draw.text((x,y+168),r['slug'][:24],fill='black');draw.text((x,y+182),pathlib.Path(r['path']).name,fill='black')
    sheet.save(CACHE/'contact-sheet.jpg')
    print(json.dumps([{'slug':r['slug'],'result':r.get('path',r.get('error'))} for r in results],indent=2))
