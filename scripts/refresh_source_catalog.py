"""Refresh catalog descriptions from the actual source-enriched pages (sites 42–101)."""
from pathlib import Path
import json
import re
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.links = []
        self.intro = []
        self.in_intro = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'img': self.images.append(a.get('src', ''))
        if tag == 'a': self.links.append(a.get('href', ''))
        if tag == 'p' and 'intro' in a.get('class', '').split(): self.in_intro=True
    def handle_data(self, data):
        if self.in_intro: self.intro.append(data)
    def handle_endtag(self, tag):
        if tag == 'p': self.in_intro=False

def main():
    entries=[]
    for run in ('2026-11-07','2026-11-07-round-2'):
        for lead in json.loads((ROOT/'research'/run/'leads.json').read_text(encoding='utf-8'))['leads']:
            document=(ROOT/lead['slug']/'index.html').read_text(encoding='utf-8')
            if 'data-source-enriched="true"' not in document: continue
            page=Page(); page.feed(document)
            count=len(set(page.images))
            features=[f'รูปจากต้นทาง {count} ภาพ' if count else 'รอรูปที่ตรวจสอบต้นทางได้',
                      'โทรติดต่อร้าน' if any(x.startswith('tel:') for x in page.links) else 'ช่องทางอ้างอิงร้าน',
                      'ข้อมูลติดต่อและแหล่งที่มา']
            update=dict(slug=lead['slug'],feat=features)
            if page.intro: update['desc']=' '.join(page.intro).strip()
            entries.append(update)
    path=ROOT/'catalog.html'
    document=path.read_text(encoding='utf-8')
    document=re.sub(r'// SOURCE_ENRICHED_CATALOG\n.*?// END_SOURCE_ENRICHED_CATALOG\n','',document,flags=re.S)
    code='// SOURCE_ENRICHED_CATALOG\n'+json.dumps(entries,ensure_ascii=False)+'.forEach(update => { const site = SITES.find(s => s.slug === update.slug); if (site) Object.assign(site, update); });\n// END_SOURCE_ENRICHED_CATALOG\n'
    path.write_text(document.replace('const NGROUPS =',code+'const NGROUPS =',1),encoding='utf-8')
    print(f'Updated {len(entries)} source-enriched catalog entries.')

if __name__ == '__main__': main()
