"""Apply curated business-specific content to the assigned fifteen pages only.

Research and downloaded-asset metadata are cached by enrich_third_sources.py.
Never invokes or modifies the shared page generator or catalog.
"""
import json, re, html, hashlib
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
from enrich_third_sources import ROOT, CACHE, LEADS

# All text below is deliberately short. Prices and dated offers are omitted.
CONTENT = {
 'two-nice-dress': dict(tag='2NICE / SALAYA', headline='สีที่ใช่ ไซซ์ที่พอดี\nสำหรับวันพิเศษของคุณ', intro='เช่าชุดราตรี ชุดเพื่อนเจ้าสาว และตัดชุดออกงาน พร้อมบริการปรับแก้ไซซ์ที่ศาลายา', phone='0922432465', line='ลิงก์ LINE ของ 2NiceDress', line_url='https://lin.ee/XsQiLSr', address='19/30 หมู่ 3 ต.ศาลายา อ.พุทธมณฑล จ.นครปฐม · ติดทางออก Makro ศาลายา ถนนสาย 5', hours='ทุกวัน 10:00–21:00 น.', services=[('เช่าชุดราตรี','เลือกชุดออกงานตามโทนสีและโอกาสที่ใช้'),('ชุดเพื่อนเจ้าสาว','ส่งธีมสีและจำนวนผู้ใส่เพื่อสอบถามชุดที่พร้อมให้เช่า'),('ตัดชุดและปรับไซซ์','นัดลองชุดและสอบถามรายละเอียดการปรับแก้กับร้าน')], palette=['#f5c435','#243d44','#fffaf0'], kind='logo', gap='Only the authentic rainbow business logo was downloadable; no portfolio photo verified. Website www.2nicedress.com timed out. LINE ID not exposed by the supplied short link.'),
 't-wardrobe': dict(tag='T. WARDROBE / NONTHABURI', headline='เดรสสั้น ปาร์ตี้ หรือทริปถัดไป\nเลือกชุดให้เข้ากับแพลนของคุณ', intro='เช่าชุดออกงาน ชุดเก็บตัวนางงาม และชุดไปเที่ยว นัดรับนนทบุรีหรือสอบถามการจัดส่ง', phone='', address='126 กรุงเทพ–นนทบุรี 8 นนทบุรี 11000', hours='', services=[('ชุดออกงานและปาร์ตี้','เลือกเดรสสั้นและชุดปาร์ตี้จากแบบที่ร้านมี'),('ชุดเก็บตัวนางงาม','ส่งรูปแบบที่สนใจและวันที่ใช้งานให้ร้านเช็กคิวชุด'),('เช่าชุดไปเที่ยว','สอบถามการส่งและวันคืนชุดก่อนยืนยันการเช่า')], palette=['#ecc1c3','#463c37','#fcf8ed'], kind='logo', gap='Public profile logo downloaded. No business phone or LINE ID found in the business-owned section; recommendation contacts excluded. Portfolio CDN URLs returned 404.'),
 'red-carpet-dress': dict(tag='RED CARPET / LAT PHRAO 128', headline='ชุดราตรีสั้นหรือยาว\nพร้อมสำหรับงานของคุณ', intro='เช่า–ขายชุดราตรี พร้อมบริการแก้ไซซ์และสอบถามเครื่องประดับที่เข้ากับชุด ที่เมแฟร์เพลส ลาดพร้าว 128', phone='0624535191', address='อาคารเมแฟร์เพลส 1/1 ปากซอยลาดพร้าว 128 แขวงพลับพลา เขตวังทองหลาง กรุงเทพฯ 10320', hours='อังคาร–อาทิตย์ 12:30–19:00 น. · โทรนัดก่อนเดินทาง', services=[('ชุดราตรีสั้น–ยาว','เช่าและซื้อชุดสำหรับงานเลี้ยงหรืองานแต่ง'),('ปรับแก้ไซซ์','แจ้งสัดส่วนและนัดลองกับร้านก่อนวันใช้งาน'),('แต่งหน้าและทำผม','สอบถามคิวบริการและเครื่องประดับที่เหมาะกับลุคของคุณ')], palette=['#db4766','#352b2a','#fff7f2'], kind='logo', gap='Logo only; directory photo URL returned 404. Conflicting published prices omitted. Monday hours not listed; no assumption of closure.'),
 'sra-sisters': dict(tag='SRA SISTERS / BNN PARK', headline='ราตรีเรียบหรู\nในแบบของศราซิสเตอร์', intro='เช่าและตัดชุดราตรี พร้อมเลือกเครื่องประดับ กระเป๋า และรองเท้า สอบถามนัดลองสาขา BNN Park ราชพฤกษ์', phone='0988782028', line='@sra.sisters', line_url='https://line.me/R/ti/p/%40sra.sisters', address='สาขาราชพฤกษ์ โครงการ BNN Park นนทบุรี', hours='', services=[('เช่า–ตัดชุดราตรี','ส่งแบบและโอกาสใช้งานเพื่อปรึกษาการเลือกชุด'),('ชุดเพื่อนเจ้าสาว','สอบถามแบบและโทนสีสำหรับกลุ่มเพื่อนเจ้าสาว'),('เครื่องประดับให้เข้าชุด','เลือกกระเป๋า รองเท้า และเครื่องประดับกับร้าน')], palette=['#c5a46a','#302722','#fbf7ef'], kind='profile_photo', extra='https://www.weddinglist.co.th/vendor/srasisters/', gap='Phone and LINE are brand-level Weddinglist contacts, not independently confirmed as a dedicated BNN Park branch number. Photos belong to the named SRA Sisters vendor gallery; exact branch and authorship not established. Hours unavailable.'),
 'my-moment-dress': dict(tag='MY MOMENT / PRADIT MANUTHAM 15', headline='ชุดสำหรับโมเมนต์สำคัญ\nของคุณและคนในครอบครัว', intro='เช่า–ขายชุดราตรี ชุดแม่เจ้าสาว และชุดแม่เจ้าบ่าว ที่ประดิษฐ์มนูธรรม 15 ใกล้ Central Eastville', phone='0929802956', line='@mymomentdress', line_url='https://page.line.me/jlx0725s', address='เลขที่ 2 ซอยประดิษฐ์มนูธรรม 15 เขตลาดพร้าว กรุงเทพฯ 10230', hours='ทุกวัน 11:30–21:00 น. · ตาม LINE ของร้าน', services=[('ชุดราตรีและชุดออกงาน','บอกวันงานและโทนสีเพื่อสอบถามชุดที่สนใจ'),('ชุดแม่เจ้าสาว–แม่เจ้าบ่าว','เลือกชุดให้เข้ากับบทบาทและบรรยากาศของงาน'),('นัดชมและลองชุด','โทรนัดก่อนเข้าร้าน มีข้อมูลที่จอดรถใน LINE ของร้าน')], palette=['#c6a043','#1e2860','#faf8f1'], kind='logo', extra='https://page.line.me/jlx0725s', gap='Authentic logo only; official LINE showcase exposes no product images. Official LINE hours preferred over conflicting directory hours.'),
 'magic-art-tattoo': dict(tag='MAGIC ART / ช่างนัฐ', headline='ออกแบบ แก้ไข ต่อเติม\nรอยสักกับช่างนัฐ', intro='Magic Art Tattoo ย่านบางใหญ่ รับออกแบบและแก้ทับรอยเดิม ส่งรูปและขนาดที่ต้องการให้ช่างประเมินก่อนนัด', phone='', address='ถนนหมู่บ้านลิสา อ.บางใหญ่ จ.นนทบุรี 11110', hours='', services=[('ออกแบบรอยสัก','คุยแนวทางและตำแหน่งที่ต้องการกับช่างนัฐ'),('แก้ไขและสักทับ','ส่งภาพรอยเดิมให้ช่างดูความเป็นไปได้ก่อนนัด'),('ต่อเติมงานเดิม','ปรึกษาขนาดและการเชื่อมงานใหม่กับรอยสักเดิม')], palette=['#c49a36','#272423','#faf5e9'], kind='profile_photo', gap='Actual group/event photograph is the page profile image; not represented as a portfolio close-up or a studio-interior photo. No verified phone, LINE ID, exact unit number, or hours found.'),
 'por-tattoo-shop': dict(tag='POR TATTOO / BANG BUA THONG', headline='สักใหม่ แก้งาน ต่อเติม\nคุยกับช่างปอที่บางบัวทอง', intro='Portattooshop รับสักลาย แก้ไขและต่อเติมงานสัก พร้อมจำหน่ายอุปกรณ์สักลาย', phone='0897951119', line='portattoo / Portattooshop99', address='18/71 หมู่ 5 ต.โสนลอย อ.บางบัวทอง จ.นนทบุรี 11110', hours='จันทร์–อังคาร และพฤหัสบดี–อาทิตย์ 11:00–21:30 น. · พุธ 11:00–20:30 น.', services=[('สักลาย','ส่งภาพอ้างอิง ขนาด และตำแหน่งให้ช่างปอประเมิน'),('แก้ไข–ต่อเติมงานสัก','ส่งภาพรอยสักเดิมเพื่อคุยแนวทางแก้งาน'),('อุปกรณ์สักลาย','สอบถามรายการและอุปกรณ์ที่ร้านมีจำหน่าย')], palette=['#dc4b3e','#2b2523','#fff8f1'], kind='logo', extra='https://www.thaithurkic.com/ร้านสักลาย-portattooshop-ช่างปอสักลาย-089-795-1119', gap='Authentic logo includes contact digits but no portfolio photo retrieved. LINE IDs corroborated in a secondary business listing; availability not tested.'),
 '338-tattoo': dict(tag='338 / PRIVATE TATTOO', headline='รอยสักของคุณ\nเริ่มจากการนัดคุยกับ 338', intro='สตูดิโอสักส่วนตัว รับจองคิวล่วงหน้า ส่งแนวลาย ขนาด และตำแหน่งที่ต้องการเพื่อคุยรายละเอียด', phone='0839730151', line='coalamr', address='105/6 ซอยอรุณอัมรินทร์ราชปักษี แขวงอรุณอัมรินทร์ เขตบางกอกน้อย กรุงเทพฯ 10700', hours='ข้อมูลเวลา 13:00–23:00 น. · กรุณาจองคิวก่อน', services=[('งานสักแบบนัดหมาย','ติดต่อสตูดิโอเพื่อเลือกวันและเวลาที่สะดวก'),('ลาย Blackwork','ส่งแนวทางลายดำและขนาดให้สตูดิโอประเมิน'),('ปรึกษาก่อนจอง','คุยตำแหน่ง รายละเอียด และราคาก่อนยืนยันคิว')], palette=['#a6a398','#232522','#f7f6f0'], kind='logo', extra='https://japantattoo.jp/?p=2859', other='https://bangkok.worldplaces.me/review/24935102-338-tattoo.html', gap='Authentic black-and-white wordmark, not portfolio photo. Secondary listings disagree on closing time (20:00 versus 23:00); appointment confirmation required. LINE ID from secondary listing.'),
 'bstyle-ink': dict(tag='B.STYLE INK / RAMA II', headline='ออกแบบลายใหม่\nหรือแก้รอยเดิมกับ B.Style', intro='รับสักร่างกาย ออกแบบและแก้ไขลายสัก ย่านหมู่บ้านดีเค พระราม 2 ใกล้สนามบอล', phone='0989984093', address='หมู่บ้านดีเค พระราม 2 · ซอยพระยามนธาตุราชศรีพิจิตร์ แยก 14 คลองบางบอน กรุงเทพฯ 10150', hours='', services=[('ออกแบบลายสัก','ส่งรูปอ้างอิงและบอกแนวที่สนใจ'),('งานสักร่างกาย','คุยขนาดและตำแหน่งกับช่างก่อนนัด'),('แก้ไขลายเดิม','ส่งภาพรอยเดิมเพื่อประเมินแนวทางแก้ไข')], palette=['#bc5a39','#292421','#faf4ee'], kind='photo_collage', extra='https://www.wongnai.com/businesses/2413794vh-b-style-ink-tattoo', gap='Official profile uses a tattoo-photo promotional collage; individual originals/authorship unavailable. Wongnai photos returned 403 and were not used. Hours and LINE not verified.'),
 '28-tattoo-art': dict(tag='28 TATTOO ART / FAI CHAI', headline='ออกแบบและแก้ไขรอยสัก\nใกล้แยกไฟฉาย', intro='28 Tattoo Art รับออกแบบรอยสักและแก้ไขงานเดิม ที่จรัญสนิทวงศ์ 31 หลัง 7-Eleven หน้า Supalai Loft', phone='0802236919', line='wowwow..ttom', address='307/95 จรัญสนิทวงศ์ 31 แขวงบางขุนศรี เขตบางกอกน้อย กรุงเทพฯ 10700 · หลัง 7-Eleven หน้า Supalai Loft แยกไฟฉาย', hours='ทุกวัน 09:30–24:00 น. · สอบถามคิวก่อนเข้าร้าน', services=[('ออกแบบรอยสัก','ส่งแนวลาย ขนาด และตำแหน่งที่ต้องการ'),('แก้ไขงานสัก','ให้ช่างดูภาพรอยเดิมก่อนประเมินงาน'),('ติดต่อจองคิว','โทรหรือค้นหา LINE ID wowwow..ttom เพื่อสอบถามวันว่าง')], palette=['#d0b047','#25251f','#fcf9eb'], kind='logo', gap='Official black-and-gold logo only; no actual tattoo portfolio photo downloadable. LINE and hours read from the business profile in search results; direct directory open blocked.'),
 'honey-yoga': dict(tag='HONEY YOGA / BANG KRANG', headline='โยคะเช้าหรือเย็น\nเลือกเวลาที่ลงตัวกับคุณ', intro='ฝึกโยคะกับ Honey Yoga ที่บางกร่าง นนทบุรี มีคลาสตั้งแต่ Beginner ถึง Advanced และอุปกรณ์ประกอบการฝึก', phone='0894914222', line='เพิ่มเพื่อนด้วยเบอร์ 0894914222', address='96/100 หมู่ 10 ซอยวัดโบสถ์–ดอนพรหม ต.บางกร่าง อ.เมือง จ.นนทบุรี 11000', hours='รอบเช้า 10:15–11:15 น. · รอบเย็น 19:15–20:15 น. สอบถามวันเรียนล่าสุด', services=[('คลาสสำหรับผู้เริ่มต้น','สอบถามระดับคลาสที่เหมาะกับประสบการณ์ของคุณ'),('โยคะหลากสไตล์','มีข้อมูล Balance Flow และการฝึกพร้อมอุปกรณ์'),('รอบเช้าและรอบเย็น','โทรเช็กตารางและจองคลาสก่อนเดินทาง')], palette=['#dc8d81','#344d43','#faf7ed'], kind='profile_photo', gap='Real outdoor group photograph from the official profile; not a studio-interior image. Post-photo CDN URLs returned 404. Published class times are examples, not a live schedule.'),
 'v-workout-studio': dict(tag='V-WORKOUT / PILATES STUDIO', headline='พิลาทิส โยคะ\nเลือกสาขาที่ใกล้คุณ', intro='V-workout Pilates Studio มีพิลาทิส Reformer, Ladder Barrel, Chair และ Cadillac พร้อมโยคะและ Inside Flow', phone='0925246226', line='-workoutpilates', address='พระราม 5: PTT Station ถนนนครอินทร์ นนทบุรี · แจ้งวัฒนะ: ปั๊มบางจาก เมืองทอง ถนนแจ้งวัฒนะขาออก', hours='', services=[('Pilates Reformer','สอบถามคลาสและรูปแบบการฝึกที่เหมาะกับคุณ'),('อุปกรณ์พิลาทิสหลากหลาย','มีข้อมูล Ladder Barrel, Chair และ Cadillac'),('โยคะและ Inside Flow','เลือกสาขาพระราม 5 หรือแจ้งวัฒนะ แล้วเช็กตารางกับสตูดิโอ')], palette=['#16a4c5','#164661','#f1f9fb'], kind='logo', extra='https://www.gowabi.com/en/provider/v-workout-pilates-studio', gap='Real branded studio photos downloaded from this business GoWabi gallery. Exact photographed branch not established. Recent post booking phone preferred over older directory footer 02-497-6641. LINE appears literally as -workoutpilates; not silently corrected. Hours unavailable.'),
 'yogitiq-studio': dict(tag='YOGITIQ / SATHU PRADIT 58', headline='ฝึกโยคะกับครูสาว\nที่สาธุประดิษฐ์ 58', intro='โยคีทีค โยคะ สตูดิโอ มีคลาสพื้นฐาน กลุ่ม ส่วนตัว และขั้นสูง พร้อมการฝึกยืดเหยียดและใช้กล้ามเนื้อ', phone='0855529564', address='ชั้น 2 Serene Trilingual International School สาธุประดิษฐ์ 58 แยก 26 (ซอยลีเพลส) ยานนาวา กรุงเทพฯ 10120 · มีที่จอดรถ', hours='จันทร์–ศุกร์ 18:00–21:00 น. · เสาร์–อาทิตย์ 09:00–11:00 น. โทรเช็กคลาสก่อน', services=[('โยคะพื้นฐาน','สอบถามคลาสเริ่มต้นและการฝึกหายใจกับครูสาว'),('กลุ่มและส่วนตัว','เลือกเรียนตามระดับและเวลาที่สะดวก'),('โยคะขั้นสูง','สอบถามตารางและความเหมาะสมก่อนเข้าคลาส')], palette=['#e9a6a9','#087b7d','#f4fbf8'], kind='logo', gap='Authentic teal-and-pink profile logo only. Class and event photo URLs unavailable; Halloween/AI-permitted event artwork deliberately excluded. LINE label has no readable ID; no ID invented.'),
 'punn-yoga': dict(tag='PUNN YOGA / PANYA INDRA', headline='พื้นฐาน ยืดเหยียด หรือโฟลว์\nฝึกกับปัญญ์โยคะ', intro='PUNN Yoga มี Basic, Stretching, Vinyasa Flow, Pranayama และ Handstand สอบถามการฝึกที่เหมาะกับคุณ', phone='0894454644', line='Jenny4454644', address='Panya Sport Complex ตรงข้ามสนามกอล์ฟปัญญา รามอินทรา · ข้อมูลติดต่อ 48/7 หมู่บ้านปัญญาอินทรา P.6 กรุงเทพฯ', hours='', services=[('Basic และ Stretching','เริ่มจากพื้นฐานและการยืดเหยียด'),('Vinyasa Flow และ Pranayama','สอบถามคลาสเคลื่อนไหวต่อเนื่องและการฝึกลมหายใจ'),('Advance และ Handstand','คุยประสบการณ์และเป้าหมายกับครูก่อนเลือกคลาส')], palette=['#d7c3a5','#655643','#fbf8f0'], kind='logo', extra='https://www.findyoga.net/studio/13529-punn-yoga-khan-na-yao', gap='Real practice photographs from named FindYoga studio gallery; original photographer/ownership not provided. Directory listing and post venue differ; both displayed with their roles, no unverified map pin asserted. Hours unavailable.'),
 'kaya-yoga': dict(tag='KAYA / LASALLE 48', headline='โยคะและพิลาทิส\nในสตูดิโอย่านลาซาล 48', intro='Kaya Yoga & Pilates เปิดสอนโยคะกลุ่มและส่วนตัว พร้อมพิลาทิส Reformer แบบเดี่ยวและคู่', phone='0642926561', address='ซอยลาซาล 48 กรุงเทพฯ', hours='เคยประกาศรอบเย็น 19:15–20:15 น. · โทรสอบถามตารางปัจจุบัน', services=[('โยคะกลุ่ม','สอบถามตารางและระดับคลาสก่อนเข้าฝึก'),('โยคะส่วนตัว','คุยเป้าหมายและเวลาที่สะดวกกับครู'),('Pilates Reformer','สอบถามการฝึกแบบเดี่ยวหรือคู่')], palette=['#f2a62e','#314e70','#fff8ed'], kind='promotional_artwork', gap='Official profile image contains a photographic yoga pose over paint effects; promotional artwork, not documentary studio or class photograph. Portfolio CDN unavailable. Last readable post 2026-02-15; evening time from older 2025 post explicitly described as historical. No exact street number or LINE ID found.'),
}

KIND_LABELS={'logo':'โลโก้จากโปรไฟล์ Facebook ของร้าน','profile_photo':'ภาพจากโปรไฟล์ Facebook ของร้าน','photo_collage':'ภาพรวมผลงานในโปรไฟล์ Facebook ของร้าน','promotional_artwork':'ภาพประชาสัมพันธ์จากโปรไฟล์ Facebook ของร้าน'}

def frag(markup): return BeautifulSoup(markup,'html.parser')
def esc(v): return html.escape(v,quote=True)
def phone_display(p): return p[:3]+'-'+p[3:6]+'-'+p[6:] if p else ''
def link(url,label,classes=''):
    return f'<a class="{classes}" href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)} ↗</a>'
def replace_text(tag,text):
    tag.clear();tag.append(text)

def main():
    profiles={x['slug']:x for x in json.loads((CACHE/'profiles.json').read_text(encoding='utf-8'))}
    extras=json.loads((CACHE/'extra-photos.json').read_text(encoding='utf-8'))
    audit=[]
    for lead in LEADS:
        slug=lead['slug']; c=CONTENT[slug]; p=profiles[slug]
        path=ROOT/slug/'index.html'; s=BeautifulSoup(path.read_text(encoding='utf-8'),'html.parser')
        s.body['data-source-enriched']='true'
        s.title.string=lead['name']+' | '+c['services'][0][0]+' · '+lead['area']
        s.select_one('meta[name="description"]')['content']=c['intro']
        replace_text(s.select_one('.notice'),'เว็บไซต์ตัวอย่าง · ไม่ใช่เว็บไซต์ทางการของร้าน')
        s.select_one('.notice').append(frag(' · '+link(p['profile_url'],'ดูช่องทางร้าน')))
        source_urls=list(dict.fromkeys([lead['source'],p['profile_url']]+[c[k] for k in ('extra','other','line_url') if c.get(k)]))
        actual=[x for x in extras if x['slug']==slug]
        hero_path=actual[0]['path'] if actual else p['path']
        hero_label=('ภาพชุดจากแกลเลอรี SRA Sisters' if slug=='sra-sisters' else 'ภาพสตูดิโอจาก GoWabi' if slug=='v-workout-studio' else 'ภาพการฝึกจากแกลเลอรี PUNN Yoga' if slug=='punn-yoga' else KIND_LABELS[c['kind']])
        h=s.select_one('.hero h1');h.clear();h.append(frag('<span class="business-name">'+esc(lead['name'])+'</span>'+esc(c['headline']).replace('\n','<br>')))
        replace_text(s.select_one('.hero .eyebrow'),c['tag'])
        replace_text(s.select_one('.hero .intro'),c['intro'])
        replace_text(s.select_one('.hero .location'),'⌖ '+c['address'])
        hero=s.select_one('.visual');hero.clear()
        contain=' logo-visual' if not actual and c['kind']=='logo' else ''
        hero['class']=['visual','source-visual']+(['logo-visual'] if contain else [])
        hero.append(frag(f'<img class="business-hero" src="{esc(str(Path(hero_path).relative_to(slug)).replace(chr(92),"/"))}" alt="{esc(lead["name"]+" — "+hero_label)}" fetchpriority="high" width="900" height="900"><div class="source-caption">{esc(hero_label)} · '+link(c.get('extra',p['profile_url']) if actual else p['profile_url'],'ดูต้นทาง')+'</div>'))
        first=s.select_one('.hero .actions a');first['href']='#contact';replace_text(first,'ติดต่อ / นัดหมาย ↗')
        # Visible identity in navigation, without a repeated category monogram.
        mono=s.select_one('.monogram, .brand-image');mono.clear();mono['class']=['brand-image']
        mono.append(frag(f'<img src="assets/source-enrichment/facebook-profile.jpg" width="44" height="44" alt="โปรไฟล์ {esc(lead["name"])}">'))
        # Replace the research/proposal strip with practical visitor information.
        strip=s.select_one('.strip .wrap')
        if strip:
            strip.clear()
            for label,value in [('ติดต่อ',phone_display(c['phone']) or 'ส่งข้อความผ่าน Facebook'),('พื้นที่',lead['area']),('นัดหมาย',c['hours'] or 'สอบถามวันและเวลาที่สะดวกกับร้าน')]:
                strip.append(frag(f'<div><small>{label}</small><strong>{esc(value)}</strong></div>'))
        for note in s.select('.research-note'):note.decompose()
        head=s.select_one('#services .section-head');head.clear();head.append(frag('<div><div class="eyebrow">SERVICES</div><h2>บริการของ '+esc(lead['name'])+'</h2></div><p>เลือกบริการที่สนใจ แล้วติดต่อร้านเพื่อนัดหมาย</p>'))
        cards=s.select_one('#services .cards');cards.clear()
        for n,(title,body) in enumerate(c['services'],1):cards.append(frag(f'<article class="service"><span class="number">0{n}</span><h3>{esc(title)}</h3><p>{esc(body)}</p><a href="#contact">สอบถามบริการนี้ ↗</a></article>'))
        brief=s.select_one('#brief');replace_text(brief.select_one('h2'),'เตรียมรายละเอียดก่อนนัดหมาย')
        replace_text(brief.select_one('.eyebrow'),'YOUR APPOINTMENT')
        replace_text(brief.select_one('.panel p'),'เลือกบริการ พร้อมบอกวันและเวลาที่สะดวก แล้วส่งข้อความให้ร้าน')
        select=brief.select_one('select');select.clear()
        for title,_ in c['services']:select.append(frag('<option>'+esc(title)+'</option>'))
        brief.select_one('.brief-list').clear()
        checklist={'dress':['วันที่ใช้ชุดและธีมสี','สัดส่วนโดยประมาณและแบบชุดที่ชอบ','วันลองชุดและการรับ–คืน'], 'tattoo':['รูปอ้างอิงหรืองานสักเดิม','ขนาดและตำแหน่งที่ต้องการ','วันเวลาที่สะดวกเข้าร้าน'], 'yoga':['ประสบการณ์และคลาสที่สนใจ','วันเวลาที่สะดวกฝึก','เรียนกลุ่มหรือส่วนตัว']}[lead['cat']]
        for item in checklist:brief.select_one('.brief-list').append(frag('<li>'+esc(item)+'</li>'))
        # No invented portfolio cards. Only actual downloaded gallery images.
        ideas=s.select_one('#ideas');ideas.clear()
        gallery_title='ชมชุดและบรรยากาศ' if lead['cat']=='dress' else 'ภาพการฝึกและสตูดิโอ' if lead['cat']=='yoga' else 'รู้จักร้านผ่านช่องทางจริง'
        ideas.append(frag('<div class="wrap"><div class="section-head"><div><div class="eyebrow">'+esc(lead['name'])+'</div><h2>'+gallery_title+'</h2></div><p>'+('สอบถามแบบหรือคลาสที่สนใจจากภาพกับร้านโดยตรง' if actual else 'ดูภาพและอัปเดตเพิ่มเติมจาก Facebook ของร้าน')+'</p></div><div class="source-gallery"></div></div>'))
        g=ideas.select_one('.source-gallery')
        if actual:
            for n,a in enumerate(actual,1):
                image_path=Path(a['path']).relative_to(slug).as_posix()
                g.append(frag(f'<figure><img src="{image_path}" alt="{esc(lead["name"])} — ภาพจากแกลเลอรีธุรกิจ {n}" loading="lazy" width="840" height="840"><figcaption>{esc(lead["name"])} · '+link(a.get('source',c.get('extra',p['profile_url'])),'ดูภาพต้นทาง')+'</figcaption></figure>'))
        else:
            g.append(frag('<div class="profile-update"><p>'+esc(KIND_LABELS[c['kind']])+'แสดงอยู่ด้านบน</p>'+link(p['profile_url'],'ดูรูปและอัปเดตของ '+lead['name'],'btn')+'</div>'))
        # Keep the useful appointment steps and remove proposal/evidence-gate prose.
        replace_text(s.select_one('.process h2'),'สอบถามและนัดหมายกับร้าน')
        faq=s.select_one('.faq')
        for surplus in faq.select('details')[2:]:surplus.decompose()
        details=faq.select('details')
        replace_text(details[0].select_one('summary'),'สอบถามราคาและวันนัดอย่างไร?')
        replace_text(details[0].select_one('p'),'ส่งรายละเอียดบริการที่สนใจและวันเวลาที่สะดวกให้ร้านประเมินราคาและแจ้งคิวโดยตรง')
        replace_text(details[1].select_one('summary'),'เดินทางไปที่ไหน?')
        replace_text(details[1].select_one('p'),c['address']+' กรุณานัดหมายกับร้านก่อนเดินทาง')
        contact=s.select_one('#contact .contact');contact.clear()
        readable_phone=phone_display(c['phone'])
        left='<div><div class="eyebrow">CONTACT '+esc(lead['name'])+'</div><h2>สอบถามบริการ<br>และนัดหมาย</h2><p class="business-contact-name">'+esc(lead['name'])+'</p>'
        if c['phone']:left+='<p>โทร <a href="tel:'+c['phone']+'">'+readable_phone+'</a></p>'
        if c.get('line'):left+='<p>LINE: '+esc(c['line'])+'</p>'
        if not c['phone']:
            left+='<p>Facebook: '+('NutCombotattoo' if slug=='magic-art-tattoo' else 'T. Wardrobe เช่าชุดออกงาน ชุดเก็บตัวนางงาม ชุดไปเที่ยว')+'</p>'
        if slug=='sra-sisters':left+='<p>เบอร์ติดต่อแบรนด์ · สอบถามนัดสาขา BNN Park</p>'
        left+='<p><strong>ที่ตั้ง</strong><br>'+esc(c['address'])+'</p>'
        if c['hours']:left+='<p><strong>เวลา / คลาส</strong><br>'+esc(c['hours'])+'</p>'
        left+='</div>'
        right='<div class="contact-links">'
        if c['phone']:right+=f'<a class="btn solid" href="tel:{c["phone"]}">โทร {readable_phone} ↗</a>'
        if c.get('line_url'):right+=link(c['line_url'],'LINE: '+c['line'],'btn')
        right+=link(p['profile_url'],'Facebook: '+lead['name'],'btn')
        if slug=='two-nice-dress':right+=link('https://maps.app.goo.gl/V8qDyofyEFK1TmXQ6','แผนที่ที่ร้านระบุ','btn')
        if slug=='honey-yoga':right+=link('https://maps.app.goo.gl/4yXNC3FfPawGBEqE8','แผนที่ที่ร้านระบุ','btn')
        if slug=='v-workout-studio':
            right+=link('https://maps.app.goo.gl/VLfY7Kj4459wtJ2o9','แผนที่พระราม 5','btn')+link('https://maps.app.goo.gl/r6184xtiA639JNQD7','แผนที่แจ้งวัฒนะ','btn')
        right+='</div>';contact.append(frag(left+right))
        mobile=s.select_one('.mobile-cta a')
        if c['phone']:
            mobile['href']='tel:'+c['phone'];replace_text(mobile,'โทร '+readable_phone+' ↗')
            for attr in ('target','rel'):
                if attr in mobile.attrs:del mobile[attr]
        else:
            mobile['href']=p['profile_url'];replace_text(mobile,'ทัก Facebook ↗')
        # Every phone CTA shows digits, including fixed mobile controls.
        for a in s.select('a[href^="tel:"]'):replace_text(a,'โทร '+phone_display(a['href'].split(':',1)[1])+' ↗')
        # Replace misleading generator labels throughout visitor-facing copy.
        for t in list(s.find_all(string=True)):
            if t.parent.name in ('script','style'):continue
            value=str(t)
            value=value.replace('เตรียมข้อมูลขอราคา','รายละเอียดก่อนนัด').replace('พื้นที่สำหรับผลงานของร้าน','ภาพจากร้าน').replace('แนวคิดเว็บไซต์','เว็บไซต์ตัวอย่าง').replace('คัดลอกข้อความเตรียมคุยงาน','คัดลอกข้อความนัดหมาย').replace('คัดลอกไว้ส่งเองผ่านช่องทางร้าน ไม่มีการส่งข้อความอัตโนมัติ','คัดลอกแล้วเปิดแชตร้านเพื่อส่งข้อความนัดหมาย')
            if value!=str(t):t.replace_with(value)
        for a in contact.select('a[href*="maps.app.goo.gl"]'):
            if a['href'] not in source_urls:source_urls.append(a['href'])
        foot=s.select_one('footer .wrap');foot.clear()
        foot.append(frag('<span>'+esc(lead['name'])+' · เว็บไซต์ตัวอย่าง<br>ข้อมูลติดต่อและภาพอ้างอิงจากช่องทางธุรกิจ</span><span class="source-links">'+ ' · '.join(link(url,'Facebook ของร้าน' if url==p['profile_url'] else 'LINE ของร้าน' if url==c.get('line_url') else 'แหล่งข้อมูลบริการ') for url in source_urls)+'</span>'))
        accent,dark,paper=c['palette']
        css=f'''\n/* Third batch: identity colors sampled visually from this business profile. */
:root{{--accent:{accent};--dark:{dark};--paper:{paper}}}
.business-name{{display:block;font-size:clamp(21px,2.3vw,31px);letter-spacing:0;margin-bottom:20px;line-height:1.4}}
.brand-image{{display:block;flex:0 0 44px;height:44px}}.brand-image img{{display:block;width:44px;height:44px;object-fit:contain;border-radius:6px;background:white}}
.round-two .source-visual{{border-radius:8px;box-shadow:12px 12px 0 color-mix(in srgb,var(--accent) 38%,transparent);outline:none;background:white}}
.source-visual::after{{display:none}}.business-hero{{display:block;width:100%;height:auto;aspect-ratio:1;object-fit:contain;background:white}}
.source-visual.logo-visual .business-hero{{padding:36px}}.source-caption{{font-size:12px;color:#333;background:#fff;padding:14px 18px;line-height:1.6}}
.source-gallery{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}}.source-gallery figure{{margin:0;background:white;border:1px solid #89928b40;border-radius:6px;overflow:hidden}}
.source-gallery img{{display:block;width:100%;height:320px;object-fit:contain;background:#f5f3ef}}.source-gallery figcaption{{padding:14px;font-size:13px;line-height:1.6}}
.profile-update{{grid-column:1/-1;border-block:1px solid #89928b40;padding:25px 0}}.profile-update p{{margin-bottom:18px}}
.source-links{{max-width:640px}}.source-links a{{display:inline-block;margin-bottom:7px}}.contact p,.source-caption,.source-links,.location{{overflow-wrap:anywhere}}
.contact a{{text-underline-offset:4px}}.strip strong{{line-height:1.6}}h1{{font-size:clamp(32px,3.5vw,51px)}}
@media(max-width:560px){{.source-gallery{{grid-template-columns:1fr}}.source-gallery img{{height:auto;max-height:480px}}.source-visual.logo-visual .business-hero{{padding:22px}}.business-name{{font-size:22px}}}}
'''
        if slug=='two-nice-dress':css+='\n.notice{background:linear-gradient(90deg,#f7d33e,#b7d6b0,#c5b8df);color:#243d44}.hero .business-name{color:#19764d}\n'
        s.style.string=s.style.get_text().split('/* Third batch: identity colors')[0]+css
        path.write_text(str(s),encoding='utf-8')
        asset_records=[{'path':p['path'],'source_page':p['profile_url'],'download_url':p['image_url'],'kind':c['kind'],'identity_evidence':p['title'],'label':KIND_LABELS[c['kind']],'authorship':'Business-profile association verified; original photographer and reuse license not established.'}]
        for a in actual:asset_records.append({'path':a['path'],'source_page':a.get('source',c.get('extra')),'download_url':a['url'],'kind':'business_gallery_photo','identity_evidence':'Photo in the gallery explicitly named '+lead['name']+'; visually inspected, recommendation images excluded.','authorship':'Original photographer and exact branch not established.'})
        for asset in asset_records:
            local=ROOT/asset['path']
            asset['sha256']=hashlib.sha256(local.read_bytes()).hexdigest()
            with Image.open(local) as image:asset['dimensions']=list(image.size)
        audit.append({'slug':slug,'category':lead['cat'],'inspected':True,'date':'2026-11-08','sources':source_urls,'photos':[a['path'] for a in asset_records],'photo_provenance':asset_records,'status':'enriched_with_business_gallery' if actual else 'enriched_with_profile_photo' if c['kind']=='profile_photo' else 'enriched_with_profile_visual_photo_gap','contact':{k:c.get(k,'') for k in ('phone','line','line_url','address','hours')},'services':[x[0] for x in c['services']],'palette':c['palette'],'palette_basis':'Visual interpretation of the downloaded individual business profile, not an official brand specification.','limitations':[c['gap'],'Direct lead-directory request returned 403; where available, web reader/search results supplied business-owned profile content. Social profile metadata and downloaded image identity matched; social timeline not accessible.','Publication/reuse permission and original image authorship not established. No stock images, generated artwork, or unrelated recommendations used.']})
        print(slug,'ready',len(asset_records),'assets',flush=True)
    (ROOT/'research/source-audit-third.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
