"""Build round-two pitch concepts only after its research report exists."""
from pathlib import Path
from copy import deepcopy
import json, re, html
import build_research_demos as shared
from research_round2 import CATEGORIES, ROOT, RUN

E=html.escape

def illustration(cat, accent, dark):
    art={
      'dress': '<path d="M361 119Q400 91 439 119L454 185 512 223 470 288 448 274 459 349 564 530Q400 577 236 530L341 349 352 274 330 288 288 223 346 185Z" fill="currentColor"/><path d="M361 119Q400 164 439 119M346 185Q400 228 454 185M341 349Q400 370 459 349M373 369L340 534M400 375V546M426 370L461 535" stroke="'+dark+'" stroke-opacity=".4" stroke-width="4" fill="none"/><path d="M400 106V77Q399 54 421 54Q444 54 444 74M400 106L300 157H500Z" stroke="white" stroke-opacity=".65" stroke-width="4" fill="none"/><path d="M179 285L184 297 196 302 184 307 179 319 174 307 162 302 174 297ZM603 164L611 183 630 191 611 199 603 218 595 199 576 191 595 183Z" fill="white" fill-opacity=".6"/>',
      'tattoo': '<circle cx="400" cy="310" r="205" stroke="currentColor" stroke-width="1" fill="none" opacity=".3"/><path d="M400 515V250M400 400Q268 408 249 312Q356 286 400 400M400 450Q528 460 550 365Q441 337 400 450" stroke="currentColor" stroke-width="5" fill="none"/><path d="M400 172C335 75 260 198 352 249C245 301 342 382 400 296C463 382 554 297 448 249C538 196 465 75 400 172Z" stroke="currentColor" stroke-width="5" fill="none"/><path d="M400 201C367 144 319 207 369 246C318 282 370 325 400 277C430 327 480 282 431 246C479 206 435 143 400 201Z" stroke="white" stroke-width="3" fill="none"/><circle cx="400" cy="245" r="14" fill="currentColor"/><path d="M400 515Q341 519 322 555M400 515Q458 518 477 555M145 235H198M171 208V261M606 464H659M632 437V490" stroke="white" stroke-opacity=".6" stroke-width="3" fill="none"/><path d="M260 327L386 394M539 377L411 446" stroke="white" stroke-opacity=".4" stroke-width="2"/>',
      'yoga': '<circle cx="448" cy="224" r="125" fill="currentColor" fill-opacity=".25"/><path d="M167 443Q393 415 643 443L607 515Q392 550 151 510Z" fill="currentColor" fill-opacity=".5"/><ellipse cx="399" cy="469" rx="164" ry="32" fill="'+dark+'"/><path d="M396 445Q320 479 292 443Q287 424 323 406L361 387 370 302Q398 283 427 304L444 387 485 409Q522 426 505 445Q479 472 406 445" stroke="white" stroke-width="8" fill="none" stroke-linecap="round"/><circle cx="399" cy="248" r="31" fill="currentColor"/><path d="M372 315L338 367 297 344M426 315L462 367 504 344" stroke="currentColor" stroke-width="12" fill="none" stroke-linecap="round"/><path d="M116 219C135 174 177 144 224 137M117 249C165 216 183 254 225 218M580 123L654 169M601 105L667 145" stroke="white" stroke-opacity=".3" stroke-width="3" fill="none"/>',
      'computer': '<rect x="181" y="146" width="438" height="304" rx="17" fill="none" stroke="currentColor" stroke-width="10"/><rect x="204" y="169" width="392" height="254" rx="3" fill="currentColor" fill-opacity=".1"/><path d="M181 450L113 503Q108 522 135 522H665Q693 522 687 503L619 450M355 483H445" stroke="currentColor" stroke-width="8" stroke-linecap="round" fill="none"/><rect x="334" y="231" width="132" height="132" rx="8" fill="currentColor"/><rect x="362" y="260" width="77" height="77" rx="5" fill="'+dark+'"/><path d="M350 207V231M382 207V231M414 207V231M446 207V231M350 363V388M382 363V388M414 363V388M446 363V388M309 247H334M309 280H334M309 312H334M309 345H334M466 247H491M466 280H491M466 312H491M466 345H491" stroke="white" stroke-width="5"/><circle cx="567" cy="193" r="5" fill="white"/>',
      'key': '<circle cx="329" cy="229" r="106" stroke="currentColor" stroke-width="35" fill="none"/><circle cx="329" cy="229" r="40" stroke="white" stroke-opacity=".5" stroke-width="3" fill="none"/><path d="M400 306L591 497 542 546 507 511 538 480 500 442 469 473 434 438 465 407 375 317Z" fill="currentColor"/><path d="M392 310L554 471" stroke="'+dark+'" stroke-opacity=".3" stroke-width="5"/><rect x="157" y="367" width="115" height="142" rx="20" stroke="white" stroke-opacity=".6" stroke-width="4" fill="none"/><path d="M183 367V330Q214 284 246 330V367" stroke="white" stroke-opacity=".6" stroke-width="6" fill="none"/><circle cx="215" cy="425" r="12" fill="white" fill-opacity=".6"/><path d="M215 434V464M544 154H619M582 117V192" stroke="white" stroke-opacity=".45" stroke-width="4"/>',
      'music': '<path d="M174 243L574 155Q625 164 625 207L586 384H174Z" fill="currentColor" fill-opacity=".8"/><path d="M174 243L574 155M174 243L575 214 586 384M174 384H586V459H174Z" stroke="white" stroke-opacity=".7" stroke-width="4" fill="none"/><path d="M195 388V454M219 388V454M243 388V454M267 388V454M291 388V454M315 388V454M339 388V454M363 388V454M387 388V454M411 388V454M435 388V454M459 388V454M483 388V454M507 388V454M531 388V454M555 388V454M197 459V536M559 459V536" stroke="white" stroke-opacity=".7" stroke-width="4"/><path d="M211 389V423M236 389V423M284 389V423M309 389V423M334 389V423M382 389V423M407 389V423M455 389V423M480 389V423M505 389V423M553 389V423" stroke="'+dark+'" stroke-width="10"/><path d="M481 106V75L531 64V95" stroke="currentColor" stroke-width="5" fill="none"/><ellipse cx="471" cy="109" rx="12" ry="8" fill="currentColor"/><ellipse cx="520" cy="98" rx="12" ry="8" fill="currentColor"/>',
    }
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 640" role="img" aria-label="ภาพวาดเดโม ไม่ใช่ผลงานหรือภาพจริงของร้าน" style="color:{accent}"><defs><pattern id="g" width="45" height="45" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="white" opacity=".13"/></pattern></defs><rect width="800" height="640" fill="url(#g)"/><circle cx="402" cy="313" r="277" fill="white" opacity=".025"/>{art[cat]}</svg>'

EXTRA_CSS='''
.round-two .visual{border-radius:160px 160px 8px 8px;box-shadow:14px 14px 0 color-mix(in srgb,var(--accent) 30%,transparent)}
.round-two nav .wrap>.btn{white-space:nowrap;flex-shrink:0}
.round-two .visual-top{padding:52px 65px 0}.round-two .visual svg{padding:0 0 5px}.round-two .hero{padding:60px 0 85px}.round-two h1{font-weight:800}.round-two .brand .monogram{border-radius:12px}.round-two .service .number{color:var(--dark);opacity:.6}.round-two .panel{border-radius:8px}.round-two .sample{border-radius:100px 100px 8px 8px}.round-two .sample div{padding:22px}.round-two .contact{border-radius:8px}.round-two .contact h2{font-size:32px}.theme-tattoo .visual{border-radius:3px;outline:1px solid var(--accent);outline-offset:-12px}.theme-key .visual,.theme-computer .visual{border-radius:12px}.theme-music .visual{border-radius:140px 8px 8px 8px}.round-two .research-note{border-block:1px solid #89928b40;padding:15px 0;font-size:14px}.round-two .research-note span{display:block;opacity:.7;font-size:12px}@media(max-width:850px){.round-two .hero{padding:35px 0 55px}.round-two .visual-top{padding:48px 55px 0}.round-two .visual svg{max-height:360px}.round-two .contact h2{font-size:28px}}@media(max-width:560px){.round-two .sample{border-radius:8px}}
'''

def build_homepage(x, i):
    c=deepcopy(CATEGORIES[x['cat']])
    # Visitor copy describes the proposed experience; research notes stay in the report.
    c['sub']=CATEGORIES[x['cat']]['sub']
    document=shared.page(x,i,category=c,illustrator=illustration)
    document=document.replace('research/2026-11-07/', 'research/2026-11-07-round-2/')
    document=document.replace('class="theme-', 'class="round-two theme-',1)
    document=document.replace('</style>',EXTRA_CSS+'</style>',1)
    document=document.replace('เริ่มจากรูปพื้นที่<br>แล้วคุยกันให้ชัด','เริ่มจากสิ่งที่สนใจ<br>แล้วคุยรายละเอียดกัน')
    document=document.replace('YOUR SPACE, YOUR NEXT CHAPTER','YOUR IDEA, YOUR NEXT STEP')
    document=document.replace('BUILT AROUND YOUR SPACE','MADE FOR YOUR NEXT STEP')
    document=document.replace('ข้อมูลนิดเดียว<br>คุยงานได้ตรงขึ้น','เตรียมข้อมูลนิดเดียว<br>คุยรายละเอียดได้ตรงขึ้น')
    document=document.replace('เพื่อให้ร้านตรวจขอบเขตงานและประเมินราคา','เพื่อสอบถามรายละเอียดและความเหมาะสมกับทางร้าน')
    document=document.replace('เตรียมรูป ขนาดโดยประมาณ และพื้นที่ที่ต้องการรับบริการ',E(c['brief'][0]+' / '+c['brief'][1]))
    document=document.replace('ยืนยันวัสดุ วิธีทำ และความจำเป็นในการดูหน้างาน','สอบถามรายละเอียด ราคา และความพร้อมให้บริการกับร้าน')
    document=document.replace('จากไอเดีย สู่รายละเอียดที่ชัดเจน','จากความสนใจ สู่การนัดที่ชัดเจน')
    document=document.replace('พื้นที่: [ระบุ]\\nขนาด/จำนวน: [ระบุ]\\nรายละเอียดและรูป: [แนบเอง]', 'ข้อมูลเบื้องต้น: [ระบุ]\\nวันเวลาที่สะดวก: [ระบุ]\\nสิ่งที่สนใจเพิ่มเติม: [ระบุ]')
    document=document.replace('ราคาเริ่มต้นเท่าไหร่?','มีราคาและเงื่อนไขอย่างไร?')
    document=document.replace('ตามขนาด วัสดุ และพื้นที่จริง','ตามรูปแบบบริการและข้อมูลของคุณ')
    document=document.replace('รูปพื้นที่','ข้อมูลที่สนใจ')
    return document

def dashboard(data):
    lead_cards=''
    for x in data['leads']:
        c=CATEGORIES[x['cat']]
        score=x['score']
        lead_cards+=f'''<article id="{x['slug']}" data-cat="{x['cat']}" data-query="{E((x['name']+' '+x['area']).lower())}"><div class="label">{E(c['name'])} · {'ตัดออกจากการเสนอขายรอบนี้' if x['status']=='excluded' else 'สำรองรอตรวจสอบ'}</div><h3>{E(x['name'])}</h3><p class="area">{E(x['area'])}</p><p><b>พบ:</b> {E(x['fact'])}</p><details><summary>วันที่ หลักฐาน และคะแนน</summary><p>{E(x['activityNote'])}</p><p>{E(x['gap'])}</p><p>คะแนนชั่วคราว A/B/C/D/E: {'/'.join(str(score[k]) for k in ['activity','gap','fit','assets','contact'])} = {score['total']}/100 · หลักฐานต่ำ · ยังไม่ผ่าน</p><p>{E(x['missing'])}</p></details><p><b>แนวคิดเสนอ:</b> {E(x['proposal'])}</p><div class="actions"><a class="btn solid" href="../../{x['slug']}/index.html">เปิดเดโม ↗</a><a class="btn" href="{E(x['source'])}" target="_blank" rel="noopener noreferrer">หลักฐาน ↗</a></div></article>'''
    css='''*{box-sizing:border-box}body{margin:0;color:#213E3B;background:#F7F5EF;font:16px/1.8 Sarabun,sans-serif}h1,h2,h3,.btn{font-family:'Noto Sans Thai',sans-serif}h1{font-size:clamp(35px,5vw,62px);line-height:1.25;margin:20px 0}h2{font-size:25px}h3{font-size:23px;margin:12px 0}a{color:inherit}.wrap{width:min(1200px,90%);margin:auto}header{padding:65px 0 35px}.eyebrow{font-size:12px;letter-spacing:2px}header p{max-width:850px}.stats{display:flex;gap:50px;padding:20px 0 40px}.stats b{display:block;font-size:38px}.toolbar{padding:20px;background:#E9ECE4;display:flex;gap:12px;flex-wrap:wrap;border-radius:8px}input,select{font:inherit;padding:12px;border:1px solid #A4B7AF;border-radius:4px;min-width:0}input{flex:1}input:focus-visible,select:focus-visible,a:focus-visible,summary:focus-visible{outline:3px solid #607F76;outline-offset:3px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:24px;padding:30px 0}article{background:#fff;border:1px solid #DADED5;border-radius:8px;padding:28px;scroll-margin-top:20px}article p{font-size:15px}.area{opacity:.7}.label{font-size:12px;color:#755632}summary{cursor:pointer}details{border-block:1px solid #DADED5;padding:12px 0}.actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:22px}.btn{display:inline-flex;text-decoration:none;border:1px solid #213E3B;border-radius:3px;padding:10px 18px;font-size:14px}.solid{background:#213E3B;color:#fff}footer{padding:30px 0 55px;font-size:13px}#empty{display:none}@media(max-width:720px){.grid{grid-template-columns:1fr}.stats{gap:30px}.stats b{font-size:30px}.toolbar{flex-direction:column}article{padding:22px}h3{font-size:21px}}'''
    out=f'''<!doctype html><html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>SME Research รอบ 2 — 6 × 5 | 7 พ.ย. 2569</title>{shared.FONT}<style>{css}</style></head><body><div class="wrap"><header><div class="eyebrow">SME FIELD NOTES / ROUND TWO / 07 NOV 2026</div><h1>อีก 30 กิจการ<br>ก่อนเริ่มบทสนทนา</h1><p>6 ประเภทใหม่ ประเภทละ 5 แห่ง ในกรุงเทพฯ และปริมณฑล รายงานนี้แยกสิ่งที่อ่านพบจากข้อเสนอออกแบบอย่างชัดเจน</p><p><b>ยังไม่มีร้านที่ผ่านหลักฐานครบทุกข้อ</b> รายชื่อหลักจึงมี 0 ราย ขาดเป้าหมาย 30 ราย เดโมด้านล่างเป็นแนวคิดศึกษา สีและภาพวาดไม่ใช่อัตลักษณ์ที่ร้านยืนยัน</p><div class="actions"><a class="btn solid" href="REPORT.md">อ่านรายงานวิจัยฉบับเต็ม ↗</a><a class="btn" href="leads.json">ข้อมูล JSON ↗</a><a class="btn" href="../../catalog.html">คาตาล็อกทั้งหมด ↗</a></div></header><div class="stats"><div><b>30</b>ผู้สมัครสำรวจ</div><div><b>6</b>ประเภทใหม่</div><div><b>0</b>ผ่านครบเกณฑ์</div></div><div class="toolbar"><input id="q" type="search" aria-label="ค้นหาร้านหรือพื้นที่" placeholder="ค้นหาร้านหรือพื้นที่"><select id="cat" aria-label="เลือกประเภทธุรกิจ"><option value="all">ทุกประเภท</option>{''.join(f'<option value="{k}">{E(c["name"])}</option>' for k,c in CATEGORIES.items())}</select></div><p id="result" role="status" aria-live="polite">พบ 30 รายการ</p><main class="grid">{lead_cards}</main><p id="empty">ไม่พบรายการที่ตรงกับการค้นหา</p><footer>ภาพวาดใหม่สำหรับเดโม ไม่มีการนำรูปหรือคลิปนักเรียนมาใช้ · ไม่ได้ติดต่อกิจการ · ไม่รับประกันยอดขายหรือความสนใจซื้อ</footer></div><script>const q=document.getElementById('q'),cat=document.getElementById('cat');function filter(){{let count=0;document.querySelectorAll('article').forEach(card=>{{const show=(cat.value==='all'||cat.value===card.dataset.cat)&&card.dataset.query.includes(q.value.trim().toLowerCase());card.hidden=!show;if(show)count++;}});document.getElementById('result').textContent='พบ '+count+' รายการ';document.getElementById('empty').style.display=count?'none':'block';}}q.addEventListener('input',filter);cat.addEventListener('change',filter);</script></body></html>'''
    (RUN/'index.html').write_text(out,encoding='utf-8')

def update_catalog(leads):
    path=ROOT/'catalog.html';text=path.read_text(encoding='utf-8')
    text=re.sub(r'// NOVEMBER_2026_ROUND2\n.*?// END_NOVEMBER_2026_ROUND2\n','',text,flags=re.S)
    additions=[]
    for x in leads:
        c=CATEGORIES[x['cat']]
        additions.append(dict(slug=x['slug'],name=x['name'],cat=x['cat'],area=x['area'],src='concept',desc=x['proposal']+' · รายชื่อสำรวจ ยังไม่ผ่านคัดกรอง',feat=['รอบ 2','หน้าแรก HTML','ภาพวาดเดโม'],pal=[c['accent'],c['dark'],c['paper']],thumb=x['slug']+'.jpg'))
    code='// NOVEMBER_2026_ROUND2\nSITES.push(...'+json.dumps(additions,ensure_ascii=False)+');\n'
    for obj,mapping in [('CATS',{k:c['name'] for k,c in CATEGORIES.items()}),('CAT_LABEL',{k:c['en'].split(' / ')[0]+' · '+c['name'] for k,c in CATEGORIES.items()}),('CAT_META',{k:dict(ic='↗',g=[c['accent'],c['dark']],d=c['name']+' — 5 แนวคิดรอยืนยันหลักฐาน') for k,c in CATEGORIES.items()})]:
        code+='Object.assign('+obj+','+json.dumps(mapping,ensure_ascii=False)+');\n'
    code+='// END_NOVEMBER_2026_ROUND2\n'
    text=text.replace('const NGROUPS =',code+'const NGROUPS =',1)
    text=text.replace('รวมเว็บไซต์ตัวอย่าง 71 หน้า','รวมเว็บไซต์ตัวอย่าง 101 หน้า')
    if 'รายงานรอบ 2' not in text:
        text=text.replace('<body>','<body>\n<div style="background:#DED5C7;color:#213E3B;text-align:center;padding:12px 5%;font-size:14px">เพิ่มอีก 30 เดโมใหม่ · ผู้สมัครยังไม่ผ่านหลักฐานครบ <a href="research/2026-11-07-round-2/index.html" style="text-decoration:underline">รายงานรอบ 2 ↗</a></div>',1)
    path.write_text(text,encoding='utf-8')

def main():
    assert (RUN/'REPORT.md').exists(), 'Finish research first.'
    data=json.loads((RUN/'leads.json').read_text(encoding='utf-8'))
    for i,x in enumerate(data['leads']):
        assert 'proposal' in x and 'score' in x, 'Research enrichment is missing.'
        folder=ROOT/x['slug'];folder.mkdir(exist_ok=True)
        (folder/'index.html').write_text(build_homepage(x,i),encoding='utf-8')
    dashboard(data);update_catalog(data['leads'])
    print('Built 30 round-two homepage concepts, research dashboard, and catalog entries (101 total).')

if __name__=='__main__': main()
