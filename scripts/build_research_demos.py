"""Build the November research report and 30 static pitch concepts. Standard library only."""
from pathlib import Path
import json, html, re
from collections import Counter
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'research/2026-11-07'
DATA = json.loads((RUN / 'leads.json').read_text(encoding='utf-8'))
LEADS = DATA['leads']
E = html.escape

# Exact business links followed from the sources during research (7 Nov 2026).
LINE_LINKS = {
 'do-it-art': 'https://lin.ee/xUsSfDa',
 'asign-graphic': 'https://line.me/ti/p/~@asign2019',
 'johnchaorai-garden': 'https://line.me/R/ti/p/@johnchaorai',
 'nbmedia-sign': 'https://line.me/R/ti/p/@pod2106w',
 'twch-glass-demo': 'https://line.me/ti/p/~noibutdee1971',
 'sky-glass-demo': 'https://line.me/ti/p/l2ZK7PBhJc',
}
for lead in LEADS:
    if lead['slug'] in LINE_LINKS:
        lead['lineUrl'] = LINE_LINKS[lead['slug']]

# Visual directions are proposals, not verified brand palettes.
CATEGORIES = {
 'metal': dict(name='งานเหล็ก–สแตนเลสและกันสาด', en='METAL / MADE TO MEASURE', accent='#F3B544', dark='#202B30', paper='#F5F1E9', title='เส้นสายที่แข็งแรง\nเพื่อบ้านที่เป็นคุณ', sub='เริ่มต้นจากพื้นที่จริง เลือกรูปแบบงาน แล้วคุยรายละเอียดกับช่าง', services=['เหล็กดัดและประตูรั้ว','โครงหลังคาและกันสาด','งานสแตนเลส'], brief=['รูปพื้นที่และจุดติดตั้ง','ความกว้าง × ความสูงโดยประมาณ','ลาย วัสดุ และสีที่สนใจ'], why='แสดงแบบและเงื่อนไขหน้างานก่อนโทร ไม่ต้องมีระบบคำนวณโครงสร้าง', decision='เลือกแบบและนัดสำรวจหน้างาน', difficulty='ง่าย / ดูแลต่ำ', art='metal'),
 'glass': dict(name='กระจกและอลูมิเนียม', en='GLASS / LIGHT / LIVING', accent='#76C8CE', dark='#153E48', paper='#F3F6F2', title='เปิดพื้นที่ให้แสง\nเปิดบ้านให้ลงตัว', sub='ประตู หน้าต่าง และงานกระจก เริ่มคุยจากรูปและขนาดพื้นที่ของคุณ', services=['ประตูและหน้าต่าง','กั้นห้องกระจก','งานติดตั้งตามพื้นที่'], brief=['รูปช่องเปิดหรือห้อง','ขนาดกว้าง × สูง','ประเภทบานและโทนสี'], why='ใช้ภาพชนิดบานและเช็กลิสต์วัดขนาดช่วยขอราคา ไม่ต้องมีระบบออกแบบ', decision='เลือกชนิดบานและส่งขนาดขอราคา', difficulty='ง่าย / ดูแลต่ำ', art='glass'),
 'sofa': dict(name='ซ่อมโซฟาและหุ้มเบาะ', en='RESTORE / REUPHOLSTER / RELIVE', accent='#BD704F', dark='#493B32', paper='#F8F2E9', title='ตัวโปรดตัวเดิม\nความรู้สึกครั้งใหม่', sub='หนังลอก เบาะยุบ หรืออยากเปลี่ยนลุค เริ่มต้นด้วยการส่งรูปให้ช่างประเมิน', services=['ซ่อมโซฟา','เปลี่ยนวัสดุหุ้มเบาะ','เก้าอี้และงานเบาะ'], brief=['รูปเต็มตัวและจุดชำรุด','จำนวนชิ้นและขนาด','พื้นที่รับ–ส่งที่ต้องการ'], why='เทียบอาการและวัสดุจากหน้าเดียว ส่งรูปเข้าช่องทางร้านแล้วประเมินรายชิ้น', decision='ซ่อมหรือหุ้มใหม่ และเตรียมรูปขอราคา', difficulty='ง่าย / ดูแลต่ำ', art='sofa'),
 'sign': dict(name='ป้ายและงานพิมพ์สั่งทำ', en='SMALL BUSINESS / BIG PRESENCE', accent='#D2EE4C', dark='#292943', paper='#F4F3F0', title='ให้ร้านของคุณ\nสะดุดตาตั้งแต่แรกเห็น', sub='เริ่มจากบอกประเภทป้าย ขนาด และจุดใช้งาน เพื่อคุยรายละเอียดได้ตรงงาน', services=['ป้ายไวนิล','สติ๊กเกอร์และฉลาก','ป้ายหน้าร้าน'], brief=['ชนิดงานและขนาด','ไฟล์แบบหรือข้อความ','จำนวนและวันต้องการใช้'], why='รวมประเภทงานและสิ่งที่ต้องส่งเพื่อขอราคา รับไฟล์ผ่านช่องทางร้านเดิม', decision='เลือกวัสดุและส่งบรีฟงานพิมพ์', difficulty='ง่าย / ดูแลต่ำ', art='sign'),
 'cctv': dict(name='ติดตั้งและซ่อมกล้องวงจรปิด', en='SEE CLEAR / PLAN SMART', accent='#9CE6CD', dark='#162D38', paper='#EDF3F1', title='มองเห็นชัดขึ้น\nเริ่มจากวางจุดให้ถูก', sub='บอกลักษณะพื้นที่และปัญหาที่พบ แล้วคุยกับช่างเพื่อเลือกแนวทางที่เหมาะสม', services=['ติดตั้งกล้องวงจรปิด','ตรวจเช็กและซ่อมระบบ','ปรับปรุงจุดติดตั้ง'], brief=['รูปพื้นที่และจุดที่อยากเห็น','จำนวนกล้องเดิมหรือที่สนใจ','ปัญหาที่พบและย่านบริการ'], why='หน้าเดียวช่วยเตรียมข้อมูลสำรวจและโทรปรึกษา ไม่เชื่อมกล้องจริงหรือระบบความปลอดภัย', decision='ติดตั้งใหม่หรือซ่อม และนัดสำรวจ', difficulty='ง่าย / ดูแลต่ำ', art='cctv'),
 'garden': dict(name='จัดสวนและดูแลสวน', en='A LITTLE GREEN / A BETTER EVERYDAY', accent='#B8CA80', dark='#304B3B', paper='#F5F4EA', title='พื้นที่สีเขียว\nที่อยากใช้ทุกวัน', sub='สวนเล็กหรือพื้นที่ดูแลประจำ เริ่มต้นจากรูปพื้นที่และสิ่งที่คุณอยากปรับ', services=['จัดและปรับปรุงสวน','ตัดหญ้าและแต่งต้นไม้','ดูแลสวนตามขอบเขตงาน'], brief=['ภาพรวมพื้นที่และทางเข้า','ขนาดสวนโดยประมาณ','งานรายครั้งหรือดูแลต่อเนื่อง'], why='ภาพสวนและพื้นที่บริการช่วยขอราคา ใช้ข้อมูลถาวรและรับนัดผ่านช่องทางเดิม', decision='เลือกขอบเขตดูแลและส่งรูปสวน', difficulty='ง่าย / ดูแลต่ำ', art='garden'),
}

# Individual proposals, explicitly kept separate from observed facts.
NOTES = [
 ('หลายงานเหล็กในรายการเดียว','ชื่อผู้รับงานและเบอร์เปิดเผย','จัดลายประตูและกันสาดเป็นสองหมวด'),
 ('ระบุโซนพระราม 5 ชัด','งานหลังคาต้องดูพื้นที่จริง','หน้าเฉพาะหลังคาโรงรถพร้อมเช็กลิสต์ภาพ'),
 ('มีทั้งราวบันไดและหลังคา','ระบุช่างตั้มให้ติดต่อโดยตรง','รวมตัวอย่างสแตนเลสแยกจากเหล็กดัด'),
 ('มีบริการมุ้งลวดร่วมกับเหล็กดัด','มีที่อยู่ร้านสำหรับแผนที่','รวมประเภทงานและวิธีเข้าร้าน'),
 ('ประกาศเดิมมีงานหลายหมวด','ช่องทางประกาศเดิมยุติบริการแล้ว','แนวคิดหน้ารวมข้อมูลทดแทนประกาศเก่า หากยังดำเนินงาน'),
 ('มีอัลบั้มและชนิดบานบนเว็บเดิม','มีเบอร์ติดต่อแล้ว','หน้าโปรโมตเฉพาะบานเลื่อน ต้องยืนยันโจทย์เพิ่มก่อน'),
 ('มีชนิดบานให้เลือกหลายแบบ','มีที่ตั้งบางใหญ่','เช็กลิสต์เลือกชนิดบานสำหรับเจ้าของบ้าน'),
 ('ข้อมูลระบุรับงานเอง','มีช่างสองเบอร์แยกกัน','รวมการวัดขนาดและช่องทางนัดดูพื้นที่'),
 ('มีรูปผลงานในเว็บเดิม','วันที่ผลงานที่เห็นเกินช่วงประเมิน','เดโมหน้าเลือกงานกั้นห้อง ใช้เมื่อยืนยันว่าหน้าเดิมยังไม่ตอบโจทย์'),
 ('มีบทความให้ความรู้และ LINE','มีเว็บไซต์ให้คำปรึกษาอยู่แล้ว','เดโมหน้าแคมเปญประตูโดยเฉพาะ ต้องมีเหตุผลเพิ่มก่อนเสนอ'),
 ('รับสั่งทำตามแบบภาพถ่าย','มี Facebook และ LINE สาธารณะ','หน้าแยกซ่อมกับสั่งทำ พร้อมรายการรูปที่ต้องส่ง'),
 ('มีที่ตั้งดอนเมืองชัด','พบช่องทางโทรช่าง','หน้าอาการชำรุดกับวิธีส่งรูปประเมิน'),
 ('มีบริการเปลี่ยนฟองน้ำและหุ้มหนัง','พบ LINE tae086','หน้าเปรียบเทียบขอบเขตเปลี่ยนหนังกับเสริมเบาะ'),
 ('มีตำแหน่งร้านบนถนนพรหมแดน','มี LINE ตามเบอร์ร้าน','รวมจุดรับงานและข้อมูลก่อนขอรับ–ส่ง'),
 ('มีบริการซ่อมหลายชนิดในหน้าเดียว','มี LINE สำหรับประเมิน','จัดหมวดอาการชำรุดกับวัสดุ เพื่อส่งบรีฟสั้นลง'),
 ('แคตตาล็อกและช่องทางพร้อมแล้ว','มีผลงานบนเว็บเดิม','เดโมหน้าป้ายสำหรับร้านเปิดใหม่ ต้องพิสูจน์ประโยชน์เพิ่ม'),
 ('มีข้อมูลไวนิลเฉพาะพื้นที่ไทรน้อย','มี LINE OA ในบทความ','หน้าบรีฟขนาดและจำนวนสำหรับป้ายไวนิล'),
 ('มีทั้งไวนิลและป้ายโลหะ','มี LINE OA เฉพาะร้าน','เดโมหน้าแคมเปญป้ายเปิดร้าน ต้องยืนยันช่องว่างเดิม'),
 ('มีเว็บและเมนูผลงาน','ติดต่อผ่านเบอร์สำนักงานได้','หน้าเฉพาะป้ายหน้าร้าน หากเจ้าของต้องการแคมเปญเพิ่ม'),
 ('มีบริการอะคริลิคและสกรีน','มีลิงก์ LINE เปิดเผย','รวมตัวอย่างวัสดุพร้อมบรีฟขนาดชิ้นงาน'),
 ('มีรายละเอียดงาน CCTV ชัด','รับงานสามจังหวัดเป้าหมาย','หน้ารวมติดตั้งกับซ่อม แต่ต้องได้ช่องทางสาธารณะที่ตรวจยืนยันก่อน'),
 ('มีเบอร์รับงานเดินสาย','มีหน้าพื้นที่นนทบุรี','รวมอาการกล้องและภาพจุดเดินสายสำหรับขอราคา'),
 ('เว็บมีที่อยู่และช่องทางนัดดูงาน','มีข้อมูลซ่อมและติดตั้งแล้ว','เดโมหน้าตรวจเช็กระบบเก่า ต้องพิสูจน์เหตุผลเพิ่มเติม'),
 ('ระบุหน้าร้านถนนสามัคคี','มีช่องทางธุรกิจในผลค้นหา','รวมขั้นตอนสำรวจสำหรับบ้านพัก หลังยืนยันสถานะร้าน'),
 ('มีช่องทางประเมินหน้างาน','มี Facebook และที่ตั้งติวานนท์','หน้าเฉพาะบ้านและร้านเล็กแทนการอ่านรายการสินค้าทั้งหมด'),
 ('ประกาศระบุพื้นที่ท่าอิฐ–บางบัวทอง','มี LINE ของผู้รับงาน','รวมขอบเขตตัดหญ้าและการเก็บเศษ หลังยืนยันรับงานล่าสุด'),
 ('มีบริการดูแลสวนและปลูกต้นไม้','มี LINE OA ในประกาศ','แยกดูแลสวนรายครั้งกับงานปลูกใหม่'),
 ('พบงานเคลียร์พื้นที่และตัดหญ้า','มีเบอร์สาธารณะสำหรับคุยงาน','รวมรูปพื้นที่และการเข้าถึงสำหรับประเมิน'),
 ('มีหลายสไตล์สวนในรายการ','มีบริการบ่อปลาและน้ำตก','หน้าเฉพาะสวนบ้านขนาดเล็ก หลังยืนยันขนาดงานขั้นต่ำ'),
 ('เว็บเดิมมีแพ็กเกจครบ','มีขั้นตอนส่งรูปและ LINE แล้ว','เดโมดูแลสวนรายเดือน ยังไม่มีเหตุผลชัดให้เสนอเพิ่ม'),
]

def art(cat, accent, dark):
    """Original code-native illustrations; never presented as a shop's portfolio."""
    grid='<defs><pattern id="g" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="white" stroke-opacity=".08"/></pattern></defs><rect width="800" height="640" fill="url(#g)"/>'
    scenes={
      'metal': '<path d="M110 410V230L420 100 710 242V410" fill="none" stroke="currentColor" stroke-width="12"/><path d="M110 230L420 285 710 242M420 285V515M110 410L420 515 710 410M185 206L490 273M268 170L574 262M348 134L654 249" fill="none" stroke="currentColor" stroke-width="5"/><path d="M164 427V290L354 324V491M190 295V436M225 301V448M260 307V460M295 313V472M329 319V484" stroke="white" stroke-opacity=".65" stroke-width="6" fill="none"/>',
      'glass': '<path d="M145 180L490 105 675 210V455L330 535 145 420Z" fill="currentColor" fill-opacity=".12" stroke="currentColor" stroke-width="4"/><path d="M145 180L330 285 675 210M330 285V535M490 105V350M145 420L490 350 675 455M250 155L440 260V510M375 130L560 235V483" fill="none" stroke="white" stroke-width="6"/><path d="M355 320L464 294V466L355 491Z" fill="currentColor" fill-opacity=".3" stroke="currentColor" stroke-width="5"/><path d="M530 290L620 270M530 313L620 293" stroke="white" stroke-opacity=".4" stroke-width="4"/>',
      'sofa': '<ellipse cx="410" cy="493" rx="280" ry="44" fill="black" fill-opacity=".15"/><path d="M180 383V253Q180 217 220 217H584Q624 217 624 253V383" fill="currentColor"/><rect x="147" y="339" width="510" height="129" rx="36" fill="currentColor"/><rect x="180" y="332" width="215" height="71" rx="17" fill="white" fill-opacity=".25"/><rect x="408" y="332" width="215" height="71" rx="17" fill="white" fill-opacity=".25"/><rect x="130" y="311" width="65" height="137" rx="23" fill="currentColor" stroke="white" stroke-opacity=".4" stroke-width="3"/><rect x="607" y="311" width="65" height="137" rx="23" fill="currentColor" stroke="white" stroke-opacity=".4" stroke-width="3"/><path d="M185 466V493M618 466V493M402 240V320" stroke="white" stroke-width="6"/><rect x="222" y="258" width="105" height="76" rx="14" fill="white" fill-opacity=".18" transform="rotate(-12 222 258)"/><path d="M670 311V131M625 174L670 130 718 174" stroke="white" stroke-width="4" fill="none"/>',
      'sign': '<path d="M157 226L420 165 666 225V480L420 544 157 480Z" fill="white" fill-opacity=".08" stroke="white" stroke-opacity=".45" stroke-width="3"/><path d="M157 226L420 285 666 225V318L420 377 157 318Z" fill="currentColor"/><text x="272" y="320" fill="'+dark+'" font-family="sans-serif" font-size="55" font-weight="900" transform="rotate(4 272 320)">HELLO.</text><path d="M210 354V478L366 516V392M454 394V509L607 471V357" stroke="white" stroke-width="7" fill="none"/><path d="M530 108L560 82M573 154H610M501 95V62" stroke="currentColor" stroke-width="7"/><rect x="82" y="376" width="97" height="136" rx="4" fill="currentColor" transform="rotate(-8 82 376)"/><path d="M102 403L155 395M105 423L158 415M108 443L145 437" stroke="'+dark+'" stroke-width="6"/>',
      'cctv': '<path d="M285 350L240 450H132V479H285L350 374" stroke="white" stroke-width="16" stroke-linejoin="round" fill="none"/><path d="M205 213L498 149 664 222 606 354 327 410 176 326Z" fill="currentColor"/><path d="M498 149L461 290 606 354 664 222Z" fill="white" fill-opacity=".15" stroke="white" stroke-width="3"/><ellipse cx="560" cy="257" rx="53" ry="64" transform="rotate(22 560 257)" fill="'+dark+'"/><ellipse cx="560" cy="257" rx="26" ry="32" transform="rotate(22 560 257)" fill="white" fill-opacity=".3"/><circle cx="569" cy="244" r="9" fill="white"/><path d="M647 320L746 368M635 346L708 423M615 366L655 455" stroke="currentColor" stroke-width="3" stroke-dasharray="8 10"/><path d="M90 125V85H130M670 85H710V125M710 495V535H670M130 535H90V495" stroke="white" stroke-opacity=".4" stroke-width="3" fill="none"/>',
      'garden': '<ellipse cx="410" cy="493" rx="285" ry="50" fill="currentColor" fill-opacity=".16"/><path d="M140 439L420 362 700 445 421 537Z" fill="currentColor" fill-opacity=".35"/><path d="M270 466L430 420 570 460 410 507Z" fill="white" fill-opacity=".55"/><path d="M226 407V220M574 430V280" stroke="white" stroke-width="8"/><path d="M225 340C91 338 110 163 225 164C350 154 352 335 225 340M573 350C476 353 477 229 574 229C673 230 672 352 573 350" fill="currentColor"/><path d="M225 272L188 237M225 299L266 255M574 307L603 280" stroke="'+dark+'" stroke-opacity=".4" stroke-width="4"/><path d="M345 405V285M345 340Q278 338 298 285Q347 282 345 340M345 364Q410 357 399 305Q347 305 345 364" fill="currentColor" stroke="white" stroke-opacity=".45" stroke-width="3"/><path d="M320 408H373L365 450H328Z" fill="white" fill-opacity=".8"/>',
    }
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 640" role="img" aria-label="ภาพประกอบแนวคิด ไม่ใช่ผลงานร้าน" style="color:{accent}">{grid}{scenes[cat]}</svg>'

FONT='<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@500;600;700;800;900&family=Sarabun:wght@400;500;600;700&display=swap" rel="stylesheet">'
CSS='''*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:100px}body{margin:0;background:var(--paper);color:var(--dark);font:17px/1.75 Sarabun,sans-serif}h1,h2,h3,nav,.btn,.eyebrow{font-family:'Noto Sans Thai',sans-serif}h1,h2,h3,p{margin:0}a{color:inherit}button,select{font:inherit}a,button,select,summary{touch-action:manipulation}a:focus-visible,button:focus-visible,summary:focus-visible,select:focus-visible{outline:3px solid var(--accent);outline-offset:5px}.wrap{width:min(1180px,90%);margin:auto}.notice{background:var(--accent);color:var(--dark);padding:9px 5%;text-align:center;font-size:13px;font-weight:600}.notice a{margin-left:12px}.skip{position:fixed;left:20px;top:-100px;z-index:100;background:white;padding:12px}.skip:focus{top:12px}nav{border-bottom:1px solid #89928b40;position:sticky;top:0;z-index:10;background:var(--paper)}nav .wrap{display:flex;min-height:82px;gap:24px;align-items:center;justify-content:space-between}.brand{display:flex;gap:12px;align-items:center;font-size:18px;font-weight:800;text-decoration:none;max-width:48%;line-height:1.35}.monogram{display:grid;place-items:center;flex-shrink:0;background:var(--dark);color:var(--paper);width:43px;height:43px;border-radius:50%;font:700 14px Sarabun}.menu{display:flex;gap:25px;font-size:14px}.menu a{text-decoration:none}.btn{display:inline-flex;align-items:center;justify-content:center;gap:14px;border:1px solid var(--dark);border-radius:3px;padding:13px 23px;text-decoration:none;font-weight:700;font-size:15px;cursor:pointer;background:transparent;color:var(--dark);transition:transform .2s}.btn:hover{transform:translateY(-3px)}.solid{background:var(--dark);color:var(--paper)}.eyebrow{font-size:11px;letter-spacing:2px;font-weight:700;text-transform:uppercase}.eyebrow::before{content:'';display:inline-block;width:23px;height:2px;background:var(--accent);vertical-align:middle;margin-right:10px}.hero{padding:70px 0 75px}.hero-grid{display:grid;grid-template-columns:1.05fr 1fr;align-items:center;gap:50px}h1{font-size:clamp(36px,4.6vw,65px);font-weight:700;line-height:1.26;letter-spacing:-1.5px;margin:25px 0}.hero .intro{max-width:490px;font-size:18px;opacity:.8}.actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:30px}.location{font-size:14px;margin-top:28px;opacity:.7}.visual{background:var(--dark);border-radius:var(--radius,3px);position:relative;isolation:isolate;overflow:hidden}.visual svg{display:block;width:100%;padding:20px 0}.visual-top{display:flex;justify-content:space-between;padding:30px 40px 0;color:var(--paper);font-size:10px;letter-spacing:2px}.visual-bottom{border-top:1px solid #ffffff24;display:flex;justify-content:space-between;margin:0 25px;padding:15px 0;color:var(--paper);font-size:12px}.visual::after{content:'';position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at 70% 20%,#ffffff15,transparent 65%)}.strip{background:var(--dark);color:var(--paper)}.strip .wrap{display:grid;grid-template-columns:repeat(3,1fr);gap:30px;padding:24px 0}.strip small{display:block;opacity:.55;font-size:10px;letter-spacing:2px}.strip strong{font-weight:500;font-size:15px}.section{padding:85px 0}.section-head{display:flex;justify-content:space-between;gap:25px;align-items:end;margin-bottom:35px}.section-head p{max-width:345px;font-size:15px;opacity:.7}h2{font-size:clamp(28px,3vw,43px);line-height:1.3;font-weight:600;margin-top:15px;letter-spacing:-.6px}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.service{border-top:1px solid var(--dark);padding:24px 20px 25px 0}.service .number{font:500 12px Sarabun;opacity:.5}.service h3{font-size:21px;margin:33px 0 12px}.service p{font-size:15px;opacity:.75}.service a{display:inline-block;margin-top:24px;font-size:14px;text-underline-offset:6px}.panel{display:grid;grid-template-columns:.9fr 1.1fr;gap:60px;padding:45px;background:var(--dark);color:var(--paper);border-radius:var(--radius,3px)}.panel h2{max-width:410px}.panel p{margin-top:20px;opacity:.75;font-size:15px}.panel select{width:100%;background:transparent;color:var(--paper);border:0;border-bottom:1px solid #ffffff70;padding:12px 2px;margin-top:12px;border-radius:0}.panel option{color:#222;background:#fff}.panel label{display:block;font-size:14px}.brief-list{padding:0;list-style:none;counter-reset:steps}.brief-list li{padding:14px 0;border-bottom:1px solid #ffffff25;font-size:16px;counter-increment:steps}.brief-list li::before{content:'0' counter(steps);margin-right:20px;color:var(--accent);font-size:12px}.panel .btn{background:var(--accent);border-color:var(--accent);color:var(--dark);margin-top:16px}.caption{font-size:12px!important;opacity:.65}.samples{padding-top:0}.sample{background:var(--dark);color:var(--paper);border-radius:var(--radius,3px);overflow:hidden}.sample svg{width:100%;display:block;height:210px}.sample:nth-child(2) svg{transform:scaleX(-1)}.sample:nth-child(3) svg{transform:scale(.85)}.sample div{padding:18px;border-top:1px solid #ffffff25}.sample h3{font-size:16px}.sample p{font-size:12px;opacity:.6}.process{background:color-mix(in srgb,var(--dark) 5%,var(--paper));border-block:1px solid #89928b30}.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:35px}.steps b{display:block;font:500 40px Sarabun;color:var(--dark);opacity:.35}.steps h3{font-size:19px;margin:10px 0}.steps p{font-size:15px;opacity:.75}.faq{display:grid;grid-template-columns:.8fr 1.2fr;gap:65px}details{border-bottom:1px solid #89928b60;padding:18px 0}summary{cursor:pointer;font-weight:600}details p{font-size:15px;opacity:.75;margin-top:15px}.contact{padding:55px;background:var(--accent);display:grid;grid-template-columns:1fr 1fr;gap:40px;border-radius:var(--radius,3px)}.contact .eyebrow::before{background:var(--dark)}.contact h2{font-size:35px}.contact p{margin-top:15px;font-size:15px}.contact-links{display:flex;flex-direction:column;justify-content:center;gap:12px}.contact-links .btn{justify-content:space-between}.contact small{font-size:12px}.footer{padding:35px 0 95px;font-size:12px;opacity:.7}.footer .wrap{display:flex;justify-content:space-between;gap:25px}.mobile-cta{display:none}.toast{min-height:24px;font-size:13px;margin-top:10px;line-height:1.5}.theme-sofa{--radius:80px 3px 3px 3px}.theme-garden{--radius:110px 110px 3px 3px}.theme-sign h1{font-weight:900}.theme-sign .visual{border-radius:50% 50% 4px 4px}.theme-glass .visual{border-radius:130px 3px 3px 3px}.theme-cctv .visual{border-radius:18px}.theme-metal .visual{box-shadow:12px 12px 0 var(--accent)}@media(max-width:850px){.menu{display:none}.brand{max-width:65%;font-size:16px}nav .btn{padding:10px 14px;font-size:12px}.hero{padding:38px 0 45px}.hero-grid{grid-template-columns:1fr;gap:35px}h1{font-size:clamp(35px,8vw,57px)}.visual{max-width:600px;width:100%;margin:auto}.visual svg{max-height:420px}.section{padding:55px 0}.section-head{display:block}.section-head p{margin-top:20px}.cards{gap:15px}.panel{grid-template-columns:1fr;gap:25px;padding:30px}.faq{grid-template-columns:1fr;gap:25px}.contact{grid-template-columns:1fr;padding:30px}.footer .wrap{display:block}.mobile-cta{display:flex;position:fixed;bottom:0;left:0;right:0;background:var(--paper);border-top:1px solid #89928b50;padding:10px 5% max(10px,env(safe-area-inset-bottom));z-index:20;gap:12px}.mobile-cta .btn{flex:1;padding:10px;font-size:13px}.strip .wrap{gap:15px}.strip strong{font-size:12px}.sample svg{height:160px}.samples{padding-top:0}}@media(max-width:560px){.cards,.steps{grid-template-columns:1fr}.service{padding:20px 0}.service h3{margin-top:15px}.sample{display:grid;grid-template-columns:40% 60%;align-items:center;border-radius:3px}.sample svg{height:145px}.sample div{border-top:0}.strip .wrap{grid-template-columns:1fr}.strip .wrap>div{display:flex;justify-content:space-between;gap:20px}.hero .intro{font-size:17px}.notice{font-size:11px}.eyebrow{font-size:9px;letter-spacing:1.4px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important}}'''

def page(lead, index):
    c=CATEGORIES[lead['cat']]
    variants={
      'metal':['#F3B544','#E0AA66','#BEC8BF','#D4B982','#A8C7CE'],
      'glass':['#76C8CE','#A2CCD1','#A4C2A8','#C1CFDC','#A5C5D3'],
      'sofa':['#BD704F','#D2AD89','#C7B493','#CEA893','#BAA77B'],
      'sign':['#D2EE4C','#F2BE82','#D8BEEC','#B4CEE9','#E2C7AD'],
      'cctv':['#9CE6CD','#A4C8E7','#BBCBD9','#9ACDC5','#B7CECE'],
      'garden':['#B8CA80','#C5CC8C','#A5C69A','#C2D574','#CCD4A5'],
    }[lead['cat']]
    accent=c['accent'] if index%5==0 else variants[index%5]
    illustration=art(lead['cat'],accent,c['dark'])
    target=lead.get('facebook') or lead['source']
    phone=lead['phone']
    call=f'<a class="btn solid" href="tel:{phone}">โทรคุยรายละเอียด <span>↗</span></a>' if phone else f'<a class="btn solid" href="{E(target)}" target="_blank" rel="noopener noreferrer">ดูช่องทางต้นทาง <span>↗</span></a>'
    line=lead.get('lineUrl')
    social=f'<a class="btn" href="{E(line or target)}" target="_blank" rel="noopener noreferrer">{"ทัก LINE ของร้าน" if line else "เปิดช่องทางอ้างอิง"} <span>↗</span></a>'
    cards=''.join(f'<article class="service"><span class="number">0{i+1} / SERVICE CONCEPT</span><h3>{E(s)}</h3><p>{E(c["brief"][i])} เพื่อให้ร้านตรวจขอบเขตงานและประเมินราคา</p><a href="#brief">เตรียมข้อมูลขอราคา ↗</a></article>' for i,s in enumerate(c['services']))
    samples=''.join(f'<article class="sample">{illustration}<div><h3>{E(s)}</h3><p>ภาพประกอบแนวคิด · รอรูปผลงานจากร้าน</p></div></article>' for s in c['services'])
    title=E(c['title']).replace('\n','<br>')
    return f'''<!DOCTYPE html><html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{E(lead['name'])} | แนวคิดเว็บไซต์ตัวอย่าง</title><meta name="description" content="เดโมหน้าแรกสำหรับ {E(lead['name'])} — แนวคิดการนำเสนอบริการและการขอราคา ไม่ใช่เว็บไซต์ทางการ">{FONT}<style>:root{{--accent:{accent};--dark:{c['dark']};--paper:{c['paper']}}}{CSS}</style></head>
<body class="theme-{lead['cat']}"><a class="skip" href="#main">ข้ามไปเนื้อหา</a><div class="notice">เว็บไซต์ตัวอย่างเสนอแนวคิด · ไม่ใช่เว็บไซต์ทางการ · โทนสีและภาพประกอบรอร้านยืนยัน <a href="../research/2026-11-07/index.html#{lead['slug']}">ดูหลักฐานวิจัย ↗</a></div>
<nav aria-label="เมนูหลัก"><div class="wrap"><a class="brand" href="#main"><span class="monogram" aria-hidden="true">{index+1:02}</span><span>{E(lead['name'])}</span></a><div class="menu"><a href="#services">บริการ</a><a href="#ideas">แนวทางงาน</a><a href="#contact">ติดต่อ</a></div><a class="btn" href="#brief">เริ่มคุยเรื่องงาน ↗</a></div></nav>
<main id="main"><section class="hero"><div class="wrap hero-grid"><div><div class="eyebrow">{c['en']}</div><h1>{title}</h1><p class="intro">{E(c['sub'])}</p><div class="actions"><a class="btn solid" href="#brief">เตรียมข้อมูลขอราคา <span>↗</span></a><a class="btn" href="#services">สำรวจบริการ <span>↓</span></a></div><p class="location">⌖ {E(lead['area'])}</p></div><div class="visual"><div class="visual-top"><span>DESIGN STUDY / {index+1:02}</span><span>{lead['cat'].upper()}</span></div>{illustration}<div class="visual-bottom"><span>ภาพประกอบ ไม่ใช่ผลงานจริง</span><span>BUILT AROUND YOUR SPACE ↗</span></div></div></div></section>
<div class="strip"><div class="wrap"><div><small>01 / SERVICE</small><strong>{E(c['services'][0])}</strong></div><div><small>02 / ESTIMATE</small><strong>ประเมินตามขอบเขตงานจริง</strong></div><div><small>03 / CONNECT</small><strong>คุยรายละเอียดกับทางร้าน</strong></div></div></div>
<section class="section" id="services"><div class="wrap"><div class="section-head"><div><div class="eyebrow">THE RIGHT START</div><h2>เลือกงานที่คุณกำลังมองหา</h2></div><p>หมวดบริการด้านล่างเป็นโครงสร้างที่เสนอสำหรับเว็บตัวอย่าง ขอบเขตรับงานจริงต้องยืนยันกับร้าน</p></div><div class="cards">{cards}</div></div></section>
<section class="section" style="padding-top:0" id="brief"><div class="wrap"><div class="panel"><div><div class="eyebrow">LET’S MAKE IT CLEAR</div><h2>ข้อมูลนิดเดียว<br>คุยงานได้ตรงขึ้น</h2><p>เตรียมรายการนี้ไว้ให้ร้านตรวจรายละเอียด ยังไม่ใช่การจองหรือยืนยันราคา</p><label for="kind" style="margin-top:24px">คุณสนใจงานแบบไหน?</label><select id="kind">{''.join(f'<option>{E(s)}</option>' for s in c['services'])}</select></div><div><ol class="brief-list">{''.join(f'<li>{E(s)}</li>' for s in c['brief'])}</ol><button class="btn" id="copy" type="button">คัดลอกข้อความเตรียมคุยงาน <span>↗</span></button><p class="caption">คัดลอกไว้ส่งเองผ่านช่องทางร้าน ไม่มีการส่งข้อความอัตโนมัติ</p><div class="toast" id="copy-status" role="status" aria-live="polite"></div><textarea id="copy-fallback" readonly hidden aria-label="ข้อความสำหรับคัดลอก" style="width:100%;min-height:140px;margin-top:12px"></textarea></div></div></div></section>
<section class="section samples" id="ideas"><div class="wrap"><div class="section-head"><div><div class="eyebrow">A PLACE FOR REAL WORK</div><h2>พื้นที่สำหรับผลงานของร้าน</h2></div><p>เมื่อร้านส่งรูปมา สามารถแทนภาพประกอบเหล่านี้ด้วยผลงานจริง พร้อมรายละเอียดงานที่ตรวจสอบแล้ว</p></div><div class="cards">{samples}</div></div></section>
<section class="section process"><div class="wrap"><div class="section-head"><div><div class="eyebrow">A SIMPLE NEXT STEP</div><h2>จากไอเดีย สู่รายละเอียดที่ชัดเจน</h2></div></div><div class="steps"><article><b>01</b><h3>ส่งรูปและบอกโจทย์</h3><p>เตรียมรูป ขนาดโดยประมาณ และพื้นที่ที่ต้องการรับบริการ</p></article><article><b>02</b><h3>คุยขอบเขตกับร้าน</h3><p>ยืนยันวัสดุ วิธีทำ และความจำเป็นในการดูหน้างาน</p></article><article><b>03</b><h3>ตกลงก่อนเริ่มงาน</h3><p>ขอรายละเอียดราคา วันนัด และเงื่อนไขจากร้านโดยตรง</p></article></div></div></section>
<section class="section"><div class="wrap faq"><div><div class="eyebrow">GOOD TO KNOW</div><h2>ก่อนเริ่ม<br>คุยรายละเอียด</h2></div><div><details><summary>ราคาเริ่มต้นเท่าไหร่?</summary><p>ยังไม่มีราคาที่ตรวจยืนยันสำหรับเดโมนี้ กรุณาส่งข้อมูลให้ร้านประเมินตามขนาด วัสดุ และพื้นที่จริง</p></details><details><summary>รับงานในพื้นที่ของฉันหรือไม่?</summary><p>พบข้อมูลพื้นที่อ้างอิง: {E(lead['area'])} โปรดยืนยันเขตบริการและค่าเดินทางกับร้านก่อนนัดหมาย</p></details><details><summary>ภาพและบริการในหน้านี้เป็นของจริงทั้งหมดหรือไม่?</summary><p>นี่คือแนวคิดเว็บไซต์ ภาพวาดและหมวดจัดวางเป็นตัวอย่าง ไม่ใช่ผลงานหรือข้อเสนอที่ร้านอนุมัติ ชื่อและช่องทางธุรกิจอ้างอิงจากข้อมูลสาธารณะ ณ 7 พฤศจิกายน 2569</p></details></div></div></section>
<section class="section" id="contact" style="padding-top:0"><div class="wrap"><div class="contact"><div><div class="eyebrow">YOUR SPACE, YOUR NEXT CHAPTER</div><h2>เริ่มจากรูปพื้นที่<br>แล้วคุยกันให้ชัด</h2><p>{E(lead['name'])}<br>{E(lead['area'])}</p><p>ราคา · วันนัด · ขอบเขตงาน<br>ยืนยันกับร้านก่อนตัดสินใจ</p></div><div class="contact-links">{call}{social}<a class="btn" href="https://www.google.com/maps/search/?api=1&amp;query={E(quote(lead['name']+' '+lead['area']))}" target="_blank" rel="noopener noreferrer">ค้นหาตำแหน่งบนแผนที่ <span>↗</span></a><small>ลิงก์ค้นหาแผนที่ ไม่ใช่พิกัดที่ยืนยันแล้ว · ช่องทางติดต่อควรตรวจซ้ำก่อนใช้งาน</small></div></div></div></section></main>
<footer class="footer"><div class="wrap"><span>{E(lead['name'])} / WEBSITE CONCEPT 2026<br>โทนสีเป็นข้อเสนอ ไม่ได้ยืนยันจาก Facebook · ภาพวาดสร้างสำหรับเดโม</span><span><a href="../catalog.html">กลับคาตาล็อก ↗</a> · <a href="../research/2026-11-07/index.html#{lead['slug']}">แหล่งข้อมูล ↗</a></span></div></footer><div class="mobile-cta">{call}<a class="btn" href="#brief">เตรียมข้อมูล ↗</a></div>
<script>document.getElementById('copy').addEventListener('click',async()=>{{const message='สวัสดีครับ/ค่ะ สนใจงาน '+document.getElementById('kind').value+'\\nพื้นที่: [ระบุ]\\nขนาด/จำนวน: [ระบุ]\\nรายละเอียดและรูป: [แนบเอง]\\nขอสอบถามขอบเขต ราคา และวันนัดที่สะดวก';const status=document.getElementById('copy-status');const fallback=document.getElementById('copy-fallback');try{{if(!navigator.clipboard)throw new Error('clipboard unavailable');await navigator.clipboard.writeText(message);fallback.hidden=true;status.textContent='คัดลอกแล้ว — เปิดช่องทางร้านและวางข้อความได้ด้วยตัวเอง';}}catch(error){{fallback.hidden=false;fallback.value=message;fallback.focus();fallback.select();status.textContent='กรุณาคัดลอกข้อความจากช่องด้านล่าง';}}}});</script></body></html>'''

def report():
    counts=Counter(x['status'] for x in LEADS)
    text=f'''# วิจัยลูกค้าเว็บไซต์ SME — 7 พฤศจิกายน 2569

พื้นที่: กรุงเทพฯ และปริมณฑล · เป้าหมาย 6 ประเภท × 5 กิจการ = 30 กิจการ

**ผ่านจริง 0 / 30 — ขาด 30 กิจการ** ผู้สมัครเพื่อสำรวจ {counts['reserve']} ราย และไม่รวมในเป้าหมายขายรอบนี้ {counts['excluded']} ราย ไม่มีการติดต่อร้านหรือยืนยันความสนใจซื้อ

ตรวจช่วง 90 วัน 9 ส.ค.–7 พ.ย. 2569; 60 วัน 8 ก.ย.–7 พ.ย.; 30 วัน 8 ต.ค.–7 พ.ย. ไม่ขยายช่วงหรือพื้นที่ และไม่นับวันเก็บข้อมูลของเสิร์ชเอนจินเป็นวันที่โพสต์ ไม่มีจำนวนโพสต์หรือรีวิวที่ตรวจนับได้จริงครบเกณฑ์ จึงใช้ “ตรวจไม่ได้” แทนเลขศูนย์

ข้อจำกัด: Facebook ต้นทางที่ทดลองเปิด 9 รายติด throttling/blocked; ไดเรกทอรีบางหน้าเปิดไม่ได้หรือเป็นประกาศเก่า ไม่ได้ตรวจรีวิว Google Maps แบบลงวันที่ จึงไม่ใช้รีวิวเป็นหลักฐาน A ยังไม่ได้ตรวจการแสดงผลเว็บของร้านบนมือถือ จึงไม่มีข้อสรุปเรื่องความสวย ความเร็ว หรือ usability ของเว็บเดิม

รายการเดิมใน README/catalog เป็นรายการห้ามซ้ำ ได้ค้นพบผู้สมัครมากกว่า 30 ราย และไม่นับหลายสาขา/เพจเดียวกันซ้ำ แต่ยังยืนยันความเป็นเจ้าของที่อาจร่วมกันไม่ได้ทุกราย เดโมใหม่ 30 หน้าเป็นแนวคิดสำรวจ ไม่ใช่รายชื่อหลักที่ผ่านคัดกรอง

แพ็กเกจเสนอขาย: 999 บาท หน้าเดียว รองรับมือถือ บริการ ราคา (หลังร้านยืนยัน) ผลงาน แผนที่ โทร/LINE ลูกค้าส่งข้อมูลและรูป แก้ 1 รอบ ไม่มีหลังบ้าน ไม่รวมระบบสต็อก ชำระเงิน สมาชิก หรือจองคิวสด ต้องตกลงค่าโดเมน/โฮสติ้งก่อนเสนอจริง

## 1. เลือกประเภทธุรกิจก่อนคัดร้าน

| ประเภท | เหตุผลที่เหมาะกับแพ็กเกจ | การตัดสินใจของลูกค้า | เนื้อหาหลัก | ผลิต/ดูแล | ผ่านจริง |
|---|---|---|---|---|---|
'''
    for c in CATEGORIES.values():
        text+=f'| {c["name"]} | {c["why"]} | {c["decision"]} | บริการ ภาพตัวอย่าง ข้อมูลก่อนขอราคา พื้นที่ โทร/LINE | {c["difficulty"]} | 0/5 |\n'
    text+='''
ใช้แม่แบบต่อประเภทได้เพราะเนื้อหาไม่เปลี่ยนทุกวัน เว็บเริ่มต้นมีประโยชน์ในการส่งข้อมูลก่อนขอราคาเอง ต่อยอดเพิ่มรูปผลงานหรือหน้าแคมเปญได้เมื่อมีโจทย์จริง แต่ไม่รวมงานเพิ่มในราคาเริ่มต้น

## 2. รายชื่อหลัก

ไม่มีร้านผ่านเงื่อนไขบังคับ A+B+C ครบ จึงไม่มีตารางเป้าหมายหลัก และไม่ใช้คะแนนชดเชยหลักฐานที่ขาด

## 3. ห้าอันดับแรกสำหรับตรวจสอบต่อ (ยังไม่ควรเริ่มเสนอขาย)

| ลำดับ | ร้าน | เหตุผลตรวจต่อ | ข้อเสนอหนึ่งประโยค | ต้องยืนยัน | แนวทางเว็บ |
|---|---|---|---|---|---|
| 1 | ส.วุฒิกร การช่าง | ขอบเขตงานและเบอร์ผู้รับงานชัด แต่ยังอ่านโพสต์ไม่ได้ | รวมลายงานเหล็กกับสิ่งที่ต้องส่งก่อนนัดช่าง | โพสต์/ผลงาน 60 วัน รูปที่ใช้ได้ เว็บปัจจุบัน เขตบริการ | เว็บใหม่ หากยังไม่มีหน้ารวมที่ตอบโจทย์ |
| 2 | คำรณเฟอร์นิเจอร์ | รับสั่งทำตามภาพและมีช่องทางธุรกิจ | แยกซ่อมกับสั่งทำแล้วส่งรูปให้ร้านประเมินได้ง่าย | กิจกรรมล่าสุด รูปก่อนหลัง บริการรับส่ง และเว็บเดิม | เว็บใหม่หลังยืนยันช่องว่าง |
| 3 | Do It Art | งานวัสดุหลายประเภทและมี LINE สาธารณะ | รวมวัสดุและเช็กลิสต์บรีฟป้ายในลิงก์เดียว | ผลงานล่าสุด ราคาเริ่มต้น ชื่อช่องทางร้านและสิทธิ์รูป | เว็บใหม่หรือหน้ารวมบริการ |
| 4 | Backcliff Garden | บริการรายครั้งกับงานปลูกใหม่อาจแยกสื่อสารได้ | ให้ลูกค้าเลือกขอบเขตและเตรียมรูปสวนก่อนขอราคา | โพสต์ล่าสุด เปิดกิจการอยู่ พื้นที่รับงานและเว็บเดิม | เว็บใหม่หลังยืนยัน |
| 5 | ช่างนัน อลูมิเนียม | มีช่างติดต่อสองรายและงานหลายชนิด | รวมชนิดบานกับขนาดที่ต้องส่งก่อนประเมิน | กิจกรรมล่าสุด หน้าเดิมขาดอะไรจริง และการรับข้อมูลของช่างแต่ละราย | หน้าโปรโมตเพิ่มเฉพาะเมื่อมีเหตุผลชัด |

ลำดับข้างต้นเป็นลำดับตรวจสอบเชิงวิจัย ไม่ใช่คะแนนโอกาสซื้อ ไม่ใช่คำแนะนำให้ติดต่อทันที และไม่สร้างตัวอย่างเสมือนเจ้าของเห็นชอบ

## 4. รายชื่อสำรองและกิจการที่ไม่รวมในเป้าหมายขายรอบนี้

คะแนนชั่วคราวแยก A/25, B/30, C/25, D/10, E/10: A=0 เพราะยังไม่มีหลักฐานผ่าน; B ให้เฉพาะช่องว่างระดับข้อมูลที่เห็น (ไม่ใช่ความต้องการซื้อ); C ประเมินความเหมาะของงานหน้าเดียว; D ให้เฉพาะรูป/ข้อมูลที่พบ ไม่ยืนยันสิทธิ์นำรูปมาใช้; E ช่องทางสาธารณะ คะแนนไม่สามารถยกระดับรายชื่อสำรองเป็นรายชื่อหลักได้

'''
    for cat,c in CATEGORIES.items():
        text+=f'### {c["name"]}\n\n'
        text+='| ร้าน/พื้นที่/แหล่งข้อมูล | ข้อเท็จจริงและกิจกรรม | สถานะเว็บ/ช่องว่างที่ตรวจได้ | ข้อเสนอและเหตุผลเฉพาะ | ติดต่อ | คะแนน A/B/C/D/E = รวม | สถานะ/ความมั่นใจ |\n|---|---|---|---|---|---|---|\n'
        for i,x in enumerate(LEADS):
            if x['cat']!=cat: continue
            a,b,proposal=NOTES[i]
            hosted=not any(v in x['source'] for v in ['thaithurkic','yellowpages','pantipmarket','findglocal','webchang','kaidee','baanfinder'])
            gap=('พบเว็บเดิม มีบริการและช่องทางติดต่อ; ยังไม่พิสูจน์ช่องว่างที่ทำให้ต้องซื้อหน้าใหม่' if hosted else 'ช่องทางที่ตรวจเป็นไดเรกทอรี/แคตตาล็อก ไม่พบเว็บอิสระจากหน้านั้น แต่ยังสรุปว่าไม่มีเว็บไม่ได้; ต้องตรวจหน้ารวมบริการเพิ่มเติม')
            if x['status']=='excluded': gap='พบเว็บหรือหน้าบริการเดิมพร้อมข้อมูลสำคัญ ยังไม่มีเหตุผลที่ยืนยันได้ว่าหน้าใหม่ช่วยอะไร จึงตัดจากรายชื่อเสนอขายรอบนี้'
            score=[0,0 if x['status']=='excluded' else 10,20,5 if hosted else 2,8 if x['phone'] else 2]
            x['score']={'activity':score[0],'gap':score[1],'fit':score[2],'assets':score[3],'contact':score[4],'total':sum(score),'provisional':True}
            x['proposal']=proposal;x['reasons']=[a,b];x['gap']=gap
            text+=f'| **{x["name"]}** — {x["area"]}<br>[หลักฐาน]({x["source"]})'+(f'<br>[Facebook]({x["facebook"]})' if x.get('facebook') else '')+f'<br>[เดโม](../../{x["slug"]}/index.html) | {x["fact"]}<br>กิจกรรม: ยังยืนยัน A ไม่ได้; วันที่/จำนวนโพสต์และรีวิวตรวจไม่ได้ | {gap} | **การประเมิน:** ① {a} ② {b}<br>**เสนอแบบมีเงื่อนไข:** {proposal}; คาดว่าช่วยให้เตรียมข้อมูลก่อนทักร้านได้ ต้องยืนยันบริการจริงและรูปก่อนใช้ | {x["phone"] or "ยังไม่พบเบอร์สาธารณะที่ยืนยันได้"} | '+ '/'.join(map(str,score))+f' = **{sum(score)}**<br>A ขาดวันล่าสุด; B ยังไม่ยืนยัน; C ปิดงานผ่านแชตได้; D ข้อมูลจำกัด; E ตามช่องทางที่พบ | {"ไม่รวมเป้าหมายขายรอบนี้" if x["status"]=="excluded" else "สำรองรอตรวจ A+B"} / ต่ำ |\n'
    text+='''
### ผู้สมัครเพิ่มเติมที่ตัดออกก่อนทำเดโม

- [KOJARAT METALWORKS](https://kojarat.com/): มีหน้าบริการ ราคา และช่องทางขอราคาเฉพาะอยู่แล้ว ยังไม่มีเหตุผลเสนอเพิ่ม
- [ช่างต้นคอมเซอร์วิส](https://toncomservice.com/areas/nonthaburi/cctv): มีหน้า CCTV เฉพาะนนทบุรี พร้อมราคาและข้อมูลติดต่อ
- [JPL Aluminium](https://www.jplaluminium.com/): มีหน้าแนะนำบริการและช่องทางติดต่อครบ ไม่ได้พิสูจน์ช่องว่าง
- [Shabby Chic Gardens](https://shabbychicgardens.com/): มีเว็บผลงานและข้อมูลแนะนำกิจการอยู่แล้ว
- [BangkokGardening](https://www.thaithurkic.com/รับจ้างตัดหญ้า-ต้นไม้-bangkokgardening): ไดเรกทอรีระบุปิด ต้องยืนยันสถานะก่อน จึงไม่นำมาเป็นเดโมหรือเป้าหมาย

### สิ่งที่ยังตรวจไม่ได้และขั้นตอนยกระดับหลักฐาน

สำหรับทุกราย ต้องเปิดโพสต์ต้นทางและบันทึกลิงก์/วันจริงให้ผ่าน A หรือบันทึกรีวิว 3 วันต่างกันใน 90 วัน ตรวจเว็บปัจจุบันทุกช่องทางให้เห็น B แบบเฉพาะเจาะจง ยืนยันบริการ พื้นที่ เบอร์ ผู้รับผิดชอบ ราคา และสิทธิ์รูป หากเว็บเดิมตอบโจทย์อยู่แล้วให้ตัดออก ไม่ใช้เดโมเป็นข้ออ้างว่าร้านต้องซื้อ

เดโมใช้ Noto Sans Thai สำหรับหัวข้อ และ Sarabun สำหรับเนื้อหา ใช้ภาพ SVG ที่เขียนใหม่ ไม่ใช่ผลงานร้าน ไม่อ้างอิงสี Facebook ที่เปิดตรวจไม่ได้ ไม่มีรีวิว ตัวเลขลูกค้า การรับประกัน หรือราคาแต่งขึ้น แผนที่เป็นลิงก์ค้นหาไม่ใช่พิกัดยืนยัน ไม่รับประกันยอดขาย อันดับ Google หรือความสนใจซื้อ
'''
    (RUN/'REPORT.md').write_text(text,encoding='utf-8')
    (RUN/'leads.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def report_html():
    blocks=''
    for cat,c in CATEGORIES.items():
        blocks+=f'<section><h2>{E(c["name"])}</h2><div class="research-grid">'
        for x in [v for v in LEADS if v['cat']==cat]:
            blocks+=f'<article id="{x["slug"]}"><small>{"ไม่รวมเป้าหมายขายรอบนี้" if x["status"]=="excluded" else "สำรองรอตรวจสอบ"} · ความมั่นใจต่ำ</small><h3>{E(x["name"])}</h3><p>{E(x["area"])}</p><p><b>ข้อเท็จจริง:</b> {E(x["fact"])}</p><p><b>กิจกรรมล่าสุด:</b> ยังยืนยันเกณฑ์ A ไม่ได้ วันที่/จำนวนตรวจไม่ได้</p><p><b>สถานะเว็บ:</b> {E(x["gap"])}</p><p><b>การประเมิน:</b> {E(" / ".join(x["reasons"]))}</p><p><b>ข้อเสนอ:</b> {E(x["proposal"])}</p><p>คะแนนชั่วคราว A/B/C/D/E: {" / ".join(str(x["score"][k]) for k in ["activity","gap","fit","assets","contact"])} = {x["score"]["total"]}/100 (ไม่ผ่านเงื่อนไขหลักฐาน)</p><p>ติดต่อสาธารณะ: {E(x["phone"] or "ยังตรวจไม่ได้")}</p><div class="actions"><a class="btn" href="{E(x["source"])}" rel="noopener noreferrer" target="_blank">หลักฐาน ↗</a><a class="btn solid" href="../../{x["slug"]}/index.html">เปิดเดโม ↗</a></div></article>'
        blocks+='</div></section>'
    out=f'''<!doctype html><html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>ผลวิจัย SME 6 × 5 | 7 พ.ย. 2569</title>{FONT}<style>:root{{--dark:#203C35;--paper:#F5F4ED;--accent:#C9DD9B}}{CSS}.research-grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}article{{background:#fff;padding:28px;border:1px solid #ddd;border-radius:10px;scroll-margin-top:20px}}article p{{font-size:15px;margin-top:12px}}article small{{color:#76562b}}article h3{{margin-top:12px}}section{{margin:50px 0}}section h2{{margin-bottom:25px}}.research-grid .actions{{margin-top:20px}}@media(max-width:750px){{.research-grid{{grid-template-columns:1fr}}}}</style></head><body><div class="wrap"><header style="padding-top:55px"><div class="eyebrow">RESEARCH NOTES / 07 NOV 2026</div><h1>ค้นพบ 30 กิจการ<br>ยังผ่านครบเกณฑ์ 0 กิจการ</h1><p>6 ประเภท × 5 กิจการ · กรุงเทพฯ และปริมณฑล · ขาดเป้าหมายที่ผ่านจริง 30 ราย</p><p style="margin-top:20px">หลักฐานความเคลื่อนไหว 60/90 วันยังยืนยันไม่ครบ รายชื่อเหล่านี้เป็นผู้สมัครสำรองหรือกิจการที่ยังไม่มีเหตุผลชัดให้เสนอเว็บเพิ่ม เดโมเป็นการศึกษาแนวทางออกแบบ ไม่ใช่เว็บไซต์ทางการหรือการยืนยันความต้องการซื้อ</p><div class="actions"><a class="btn solid" href="REPORT.md">อ่านรายงานฉบับเต็ม ↗</a><a class="btn" href="leads.json">ข้อมูลพร้อมคะแนน JSON ↗</a><a class="btn" href="../../catalog.html">คาตาล็อกทั้งหมด ↗</a></div></header>{blocks}<footer class="footer">ช่วงประเมิน 9 ส.ค.–7 พ.ย. 2569 · ไม่ส่งข้อความถึงร้าน · ไม่รับประกันผลขาย</footer></div></body></html>'''
    (RUN/'index.html').write_text(out,encoding='utf-8')

def catalog():
    path=ROOT/'catalog.html';text=path.read_text(encoding='utf-8')
    text = re.sub(r'// NOVEMBER_2026_CONCEPTS\n.*?(?=const NGROUPS =)', '', text, flags=re.S)
    additions=[]
    for x in LEADS:
        c=CATEGORIES[x['cat']]
        additions.append(dict(slug=x['slug'],name=x['name'],cat=x['cat'],area=x['area'],src='concept',desc=x['proposal']+' · แนวคิดรอยืนยันข้อมูล ไม่ใช่ร้านที่ผ่านคัดกรอง',feat=['เดโมหน้าแรก','ข้อมูลรอตรวจสอบ','ภาพวาดประกอบ'],pal=[c['accent'],c['dark'],c['paper']],thumb=f'{x["slug"]}.jpg'))
    code='// NOVEMBER_2026_CONCEPTS\nSITES.push(...'+json.dumps(additions,ensure_ascii=False)+');\n'
    code+='Object.assign(CATS,'+json.dumps({k:v['name'] for k,v in CATEGORIES.items()},ensure_ascii=False)+');\n'
    code+='Object.assign(CAT_LABEL,'+json.dumps({k:v['en'].split(' / ')[0]+' · '+v['name'] for k,v in CATEGORIES.items()},ensure_ascii=False)+');\n'
    code+='Object.assign(CAT_META,'+json.dumps({k:dict(ic='↗',g=[v['accent'],v['dark']],d=v['name']+' — 5 เดโมสำรวจ ยังไม่ผ่านเกณฑ์หลักฐานล่าสุด') for k,v in CATEGORIES.items()},ensure_ascii=False)+');\n'
    text=text.replace('const NGROUPS =',code+'const NGROUPS =',1)
    text=text.replace('catalog-assets/${s.slug}.jpg','catalog-assets/${s.thumb || s.slug + ".jpg"}')
    text=text.replace('catalog-assets/${s.thumb || s.slug + "-m.jpg"}','catalog-assets/${s.slug}-m.jpg')
    text=text.replace("s.src === 'real' ? 'ข้อมูลจริงจากร้าน' : 'ข้อมูลจาก lead'","s.src === 'concept' ? 'เดโม · ยังไม่ผ่านคัดกรอง' : s.src === 'real' ? 'ข้อมูลจริงจากร้าน' : 'ข้อมูลจาก lead'")
    text=text.replace('รวมเว็บไซต์ตัวอย่าง 41 ธุรกิจ','รวมเว็บไซต์ตัวอย่าง 71 หน้า')
    if 'เพิ่ม 30 เดโมใน 6 ประเภท' not in text: text=text.replace('<body>','<body>\n<div style="background:#203C35;color:#EDF3E5;text-align:center;padding:12px 5%;font-size:14px">เพิ่ม 30 เดโมใน 6 ประเภท · หลักฐานยังไม่ผ่านครบเกณฑ์ <a href="research/2026-11-07/index.html" style="text-decoration:underline">อ่านผลวิจัย 7 พ.ย. 2569 ↗</a></div>',1)
    path.write_text(text,encoding='utf-8')

def main():
    assert len(LEADS)==30 and all(v==5 for v in Counter(x['cat'] for x in LEADS).values())
    report();report_html()
    for i,x in enumerate(LEADS):
        folder=ROOT/x['slug'];folder.mkdir(exist_ok=True)
        (folder/'index.html').write_text(page(x,i),encoding='utf-8')
        c=CATEGORIES[x['cat']]
        # Catalog thumbnails are rendered by verify_research_demos.cjs.
    catalog()
    print('Generated research report, 30 static homepages, and catalog entries.')

if __name__=='__main__': main()
