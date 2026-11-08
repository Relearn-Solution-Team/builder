"""Apply the independently researched computer/key/music batch only. No shared generator edits."""
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
import json, tempfile, re, html

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path(tempfile.gettempdir()) / 'source-fourth'
LEADS = [x for x in json.loads((ROOT/'research/2026-11-07-round-2/leads.json').read_text('utf-8'))['leads'] if x['cat'] in ('computer','key','music')]
# Manually curated from the listed source pages, matched Facebook metadata and official LINE profiles.
DATA = {
 'acom-rangsit': dict(title='ซ่อมคอมและเลือกเครื่องมือสอง\nหน้า ม.รังสิต',intro='ACOM รับซ่อมและจำหน่ายคอมพิวเตอร์ โน้ตบุ๊ก และอุปกรณ์ไอที นัดรับเครื่องย่านหลักหก หน้า ม.รังสิต ติดต่อคุณปัทเพื่อแจ้งรุ่นและอาการก่อนนำเครื่องมา',address='หลักหก หน้า ม.รังสิต ปทุมธานี',hours='จันทร์–ศุกร์ 16:30–22:00 น. · เสาร์–อาทิตย์ 10:00–22:00 น.',line='0867128540',services=[('ซ่อมคอมและอุปกรณ์','แจ้งยี่ห้อ รุ่น และอาการเสียให้ร้านประเมินก่อนนำเครื่องเข้าตรวจ'),('คอมและโน้ตบุ๊กมือสอง','มีประกาศจำหน่ายเครื่องมือสอง สอบถามเครื่องที่ยังมีและสภาพจริงก่อนซื้อ'),('อุปกรณ์คอมพิวเตอร์','สอบถามอุปกรณ์และความเข้ากันได้กับเครื่องที่ใช้อยู่')],extra=['https://www.facebook.com/193741720652157','https://shop.line.me/@510pdfla/product/1006416645'],photo='acom-rangsit-product',caption='ภาพสินค้า ACOM จาก LINE SHOPPING · ราคาในภาพเป็นประกาศเดิม กรุณาสอบถามราคาและสต็อกปัจจุบัน',limitations=['Photo is a seller product photograph with promotional overlay; embedded price/stock is historical, not a current offer. Street number not verified.']),
 'bpcomputer': dict(title='จัดสเปก ซ่อม และอัปเกรด\nคอมพิวเตอร์ที่บางใหญ่',intro='BPComputer จำหน่ายคอมประกอบ โน้ตบุ๊ก จอภาพ และอุปกรณ์ต่อพ่วง พร้อมบริการซ่อมและอัปเกรด บอกงานที่ใช้และงบประมาณเพื่อปรึกษาสเปกกับร้าน',address='4/310 หมู่บ้านอาสาเฮ้าส์ 5 ซอย 2 ต.บางใหญ่ อ.บางใหญ่ นนทบุรี',phones=['0917895736','0902254479'],services=[('จัดสเปกคอมพิวเตอร์','คุยงบประมาณและรูปแบบการใช้งาน ทั้งเล่นเกม ทำงาน และใช้งานทั่วไป'),('ซ่อมและอัปเกรด','ส่งรุ่นเครื่องและอาการให้ร้านตรวจความเหมาะสมของอะไหล่ก่อนเปลี่ยน'),('สินค้าไอทีและอุปกรณ์','สอบถามโน้ตบุ๊ก จอภาพ และอุปกรณ์ต่อพ่วง รวมถึงสินค้าที่พร้อมจำหน่าย')],extra=['https://www.facebook.com/108956124601776']),
 'kk-computer-service': dict(title='ซ่อมคอม โน้ตบุ๊ก และปริ้นเตอร์\nบางรักพัฒนา',intro='เคเค คอมพิวเตอร์ ไอที เซอร์วิส อยู่ซอย 13 บางรักพัฒนา บางบัวทอง ข้างร้านก๋วยเตี๋ยววัดดง โทรแจ้งอาการและนัดนำเครื่องเข้าร้านได้โดยตรง',address='117/19 ซอย 13 ข้างร้านก๋วยเตี๋ยววัดดง ต.บางรักพัฒนา อ.บางบัวทอง นนทบุรี 11110',services=[('ซ่อมคอมพิวเตอร์','แจ้งรุ่นและอาการเสียก่อนนำเครื่องมาตรวจ'),('ซ่อมโน้ตบุ๊ก','เตรียมยี่ห้อ รุ่น และรูปอาการบนหน้าจอ เพื่อให้ร้านพิจารณารับงาน'),('ซ่อมปริ้นเตอร์','บอกรุ่นเครื่องพิมพ์และอาการที่พบ เพื่อสอบถามขั้นตอนรับซ่อม')],extra=['https://www.facebook.com/kkcomcctv'],map='https://www.google.com/maps/search/?api=1&query=13.96121507,100.3987331'),
 'breeze-computer': dict(title='คอมพิวเตอร์และไอทีมือสอง\nคุยกับช่างบรีส',intro='ซ่อมคอม by ช่างบรีส ย่านคลอง 13 ธัญบุรี สอบถามงานซ่อม คอมพิวเตอร์ โน้ตบุ๊ก และอะไหล่ไอทีมือสองได้ที่ 085-993-5876 กรุณาโทรนัดก่อนเดินทาง',address='บริเวณชุมสายโทรศัพท์หมู่บ้านซื่อตรง คลอง 13 ต.บึงน้ำรักษ์ อ.ธัญบุรี ปทุมธานี 12110',services=[('งานซ่อมคอมพิวเตอร์','แจ้งรุ่นและอาการเสียให้ช่างพิจารณาก่อนนำเครื่องเข้าตรวจ'),('คอมและโน้ตบุ๊กมือสอง','สอบถามรายการที่มีจำหน่ายและสภาพเครื่องปัจจุบันโดยตรง'),('อะไหล่และสินค้าไอที','ระบุรุ่นเครื่องและอะไหล่ที่ต้องการ เพื่อสอบถามความเข้ากันได้')],limitations=['Original directory blocks direct HTTP retrieval (403); indexed page text confirms phone and location. Directory lists 24-hour opening but not corroborated by business; not advertised as confirmed hours. No identity-matched photograph or logo downloaded.']),
 'pc-rangsit-service': dict(title='ซ่อมพีซีและ MacBook\nรังสิต ข้างฟิวเจอร์พาร์ค',intro='ติดต่อช่างตั้มสำหรับงานซ่อมคอมและโน้ตบุ๊ก เปลี่ยนจอ แบตเตอรี่ คีย์บอร์ด เพิ่มแรมและฮาร์ดดิสก์ เว็บไซต์ระบุออฟฟิศนอกห้างบริเวณรังสิต คลอง 1 ข้างฟิวเจอร์พาร์ค',address='รังสิต คลอง 1 ข้างฟิวเจอร์พาร์ครังสิต ปทุมธานี · โทรนัดจุดรับเครื่องกับช่างตั้ม',hours='เว็บไซต์ระบุเปิดทุกวัน · โทรสอบถามเวลารับเครื่อง',line='0624415936',lineUrl='https://lin.ee/n8dxGDt',services=[('เปลี่ยนอะไหล่โน้ตบุ๊ก','สอบถามงานเปลี่ยนจอ แบตเตอรี่ และคีย์บอร์ดตามรุ่นเครื่อง'),('เพิ่มแรมและพื้นที่เก็บข้อมูล','แจ้งรุ่นและสเปกเดิมก่อนเลือกแรมหรือฮาร์ดดิสก์ที่รองรับ'),('ซ่อม MacBook และ iMac','เว็บไซต์ระบุงานเปิดไม่ติด โดนน้ำ ไม่บูตระบบ และปัญหาเมนบอร์ด')],photo='pc-rangsit-service-work-1',caption='ภาพประกอบบริการซ่อม MacBook จากเว็บไซต์ Mister Service ที่ระบุช่างตั้ม · ไม่ใช่ภาพงานซ่อมที่ยืนยันวันและลูกค้า',limitations=['Business service image includes repair photograph and brand overlay; specific job/customer/date and photograph ownership not independently established. Source also has a mall footer; use appointment location in business article, not footer as confirmed intake address.']),
 'thanakorn-key': dict(title='กุญแจรถยนต์และสมาร์ทคีย์\nติดต่อช่างธนกร',intro='รับทำกุญแจรถยนต์ รีโมท ระบบ Immobilizer และ Keyless Smartkey รวมถึงกุญแจบ้าน แจ้งรุ่นรถ ปีรถ และพื้นที่ให้ช่างธนกรตรวจรายละเอียดก่อนนัด',address='พื้นที่อ้างอิง: บางพลัด–นนทบุรี · โทรยืนยันเขตบริการและจุดนัด',services=[('กุญแจและรีโมทรถยนต์','สอบถามทำเพิ่มหรือกรณีหายหมด พร้อมระบุรุ่นและปีรถ'),('Immobilizer และ Smartkey','แจ้งระบบกุญแจและจำนวนดอกที่เหลือ เพื่อให้ช่างตรวจเงื่อนไขของรุ่นรถ'),('รีโมทชำรุด','แจ้งอาการรีโมทพัง ปุ่มเสีย หรือสตาร์ทไม่ได้ พร้อมรูปประกอบ')],extra=['https://www.facebook.com/102732402067322'],photo='thanakorn-key',caption='ภาพโปรไฟล์ธุรกิจช่างธนกรจาก Facebook ที่จับคู่ชื่อและเบอร์ติดต่อแล้ว'),
 'philung-locksmith': dict(title='กุญแจบ้าน รถ และมอเตอร์ไซค์\nพี่ลุงช่างกุญแจ',intro='บริการช่างกุญแจนอกสถานที่ย่านรามคำแหง พัฒนาการ หัวหมาก บางกะปิ และพื้นที่ใกล้เคียง แจ้งจุดเกิดเหตุและประเภทกุญแจทางโทรศัพท์ก่อนนัดช่าง',address='พื้นที่บริการ: รามคำแหง พัฒนาการ หัวหมาก บางกะปิ ลาดพร้าว คลองตัน ลำสาลี ศรีนครินทร์ และสวนหลวง',hours='แหล่งธุรกิจระบุบริการนอกสถานที่ 24 ชั่วโมง · โทรเช็กคิวช่าง',services=[('เปิดบ้านและปลดล็อก','แจ้งชนิดประตูและกุญแจ รวมถึงจุดนัดให้ช่างประเมิน'),('กุญแจรถยนต์','สอบถามปลดล็อกรถและทำดอกกุญแจรถตามรุ่น'),('กุญแจมอเตอร์ไซค์','มีประกาศรับงานกุญแจมอเตอร์ไซค์หาย แจ้งยี่ห้อและรุ่นก่อนเรียกช่าง')],extra=['https://www.facebook.com/497159130318942']),
 'prayasuren-key': dict(title='รีโมทรถและกุญแจมอเตอร์ไซค์\nรามอินทรา–พระยาสุเรนทร์',intro='ติดต่อช่างรัชหรือช่างใหม่สำหรับกุญแจหาย ทำเพิ่ม และรีโมท Smart Key มีบริการนอกสถานที่ในกรุงเทพฯ และปริมณฑล โทรแจ้งรุ่นรถและจุดนัดก่อนเรียกช่าง',address='พื้นที่บริการ: รามอินทรา พระยาสุเรนทร์ กรุงเทพฯ และปริมณฑล · โทรยืนยันสาขาและจุดนัด',phones=['0858189828','0838555120'],phoneNames=['ช่างรัช','ช่างใหม่'],lineUrl='https://line.me/ti/p/W2n8WMCaYf',hours='ประกาศบริการนอกสถานที่ 24 ชั่วโมง · โทรตรวจสอบคิวและค่าเดินทาง',services=[('รีโมทรถยนต์','รับทำสำรองและกรณีหายหมด รวมถึงระบบ Immobilizer'),('กุญแจมอเตอร์ไซค์','สอบถามกุญแจและรีโมท Smart Key ตามยี่ห้อและรุ่น'),('รีโมทชำรุดและเปิดล็อก','สอบถามเปลี่ยนกรอบรีโมท รวมถึงงานเปิดบ้านและเปิดรถ')],extra=['https://www.facebook.com/104126414518363']),
 'locksmith-thailand': dict(title='กุญแจรถยุโรปและญี่ปุ่น\nLocksmith Thailand',intro='สอบถามงานกุญแจ รีโมท Smart Key และระบบ Immobilizer รวมถึงงานระบบไฟ BMW และ MINI กับ Locksmith Thailand ที่นวมินทร์ 70 ส่งรุ่นรถและอาการให้ร้านประเมินก่อนนัด',address='106/48 ซอยนวมินทร์ 70 แยก 6-1 กรุงเทพฯ',phones=['0845367949','0819130077'],line='poppana',services=[('กุญแจและ Smart Key','สอบถามงานกุญแจหายหรือทำเพิ่มสำหรับรถยุโรปและญี่ปุ่น'),('ระบบ Immobilizer','แจ้งยี่ห้อ รุ่น ปีรถ และจำนวนกุญแจที่ยังมี'),('ระบบไฟ BMW และ MINI','มีประกาศรับซ่อมกล่อง DME / DDE และงานระบบไฟ สอบถามขอบเขตตามอาการ')],extra=['https://www.facebook.com/161436520665200'],limitations=['March 2026 post uses 084-536-7949; December 2025 posts and listing use 081-913-0077. Both displayed with dates; verify preferred number with business. No actual job photo downloaded.']),
 'chang-khaek-key': dict(title='กุญแจช่างแขก ลาดหลุมแก้ว\nรับงานในและนอกสถานที่',intro='ร้านกุญแจช่างแขก รับทำกุญแจสำรอง รีโมทฝังชิพ กุญแจรถยนต์และมอเตอร์ไซค์ พร้อมบริการเปิดบ้าน เปิดรถ และปลดล็อกนอกสถานที่ในปทุมธานีและพื้นที่ใกล้เคียง',address='111/72 หมู่ 4 ต.ลาดหลุมแก้ว อ.ลาดหลุมแก้ว ปทุมธานี 12140',phones=['0817606868','0816967332'],line='0817606868',lineUrl='https://line.me/ti/p/~0817606868',hours='เปิดทุกวัน 24 ชั่วโมง ตามเว็บไซต์ร้าน · โทรเช็กคิวก่อนเข้ารับบริการ',services=[('ทำกุญแจสำรอง','กุญแจบ้าน รถยนต์ และมอเตอร์ไซค์ รวมถึงกุญแจรีโมทฝังชิพ'),('เปิดบ้านและเปิดรถ','แจ้งปัญหาลืมกุญแจหรือกุญแจหาย เพื่อประเมินงานปลดล็อก'),('บริการนอกสถานที่','สอบถามพื้นที่นัด ค่าเดินทาง และคิวช่างก่อนตกลงรับบริการ')],extra=['https://khak-locksmith.yellowpages.co.th/','https://www.facebook.com/khak.locksmith.phathumthani'],photo='chang-khaek-key-work-1',caption='ภาพหน้าร้านกุญแจช่างแขกจากเว็บไซต์ร้าน',gallery=['chang-khaek-key-work-2','chang-khaek-key-work-3','chang-khaek-key-work-4'],map='https://www.google.com/maps/search/?api=1&query=14.053336273841357,100.44290870738028',limitations=['Current business website address differs from mirrored listing 32/3 Soi Khu Khwang 1. Website address and coordinates preferred; call before travel. Mixed-name/phone introduction on mirror excluded.']),
 'sound-accent': dict(title='เรียนดนตรีถึงบ้าน\nหรือเริ่มคลาสออนไลน์',intro='Sound Accent มีคลาสเปียโน ร้องเพลง กีตาร์ เบส กลอง ไวโอลิน และเครื่องเป่า เลือกเรียนเดี่ยวหรือกลุ่มได้ สอบถามครูในพื้นที่และรูปแบบการเรียนผ่าน LINE',address='สอนถึงบ้านในพื้นที่ที่ครูรับงาน และสอนออนไลน์ · สอบถามเขตบริการก่อนนัด',line='@773euimm',lineUrl='https://lin.ee/5R8t5zp',services=[('เปียโนและร้องเพลง','สอบถามคลาสเดี่ยวหรือกลุ่มสำหรับวัยเด็กจนถึงผู้ใหญ่'),('กีตาร์ เบส กลอง และเครื่องดนตรี','แจ้งเครื่องดนตรีที่สนใจและพื้นฐานเดิมเพื่อเลือกครู'),('เรียนที่บ้านหรือออนไลน์','แจ้งพื้นที่ วันเวลา และอุปกรณ์ที่มีเพื่อจัดรูปแบบเรียน')],extra=['https://www.facebook.com/779421515249501','https://line.me/R/ti/p/@773euimm'],limitations=['No public telephone or street address verified. LINE ID resolved from source short link. Multiple campaign LINE links exist; only cited source link used. No actual business/class photo downloaded; Facebook logo only.']),
 'music-mania-tiwanon': dict(title='ดนตรี ร้องเพลง และศิลปะการแสดง\nที่ติวานนท์ 32',intro='Music Mania School Tiwanon สอนร้องเพลง เต้น การแสดง เปียโน กีตาร์ กลอง และรวมวง พร้อมหลักสูตรครูสอนร้องเพลง สอบถามคอร์สและวันเรียนกับโรงเรียนโดยตรง',address='ซอยติวานนท์ 32 แยก 8 ถ.ติวานนท์ ต.บางกระสอ อ.เมืองนนทบุรี นนทบุรี',phones=['0851695161','0924458760'],line='@musicmaniaschool',lineUrl='https://line.me/R/ti/p/@musicmaniaschool',hours='ทุกวัน 09:00–21:00 น. ตามข้อมูลโรงเรียน · สอบถามตารางเรียนก่อนมา',services=[('ร้องเพลงและการแสดง','สอบถามเรียนร้องเพลง เต้น และ Acting ตามเป้าหมายผู้เรียน'),('เครื่องดนตรีและรวมวง','มีวิชาเปียโน กีตาร์ กลอง และ Band'),('หลักสูตรครูสอนร้องเพลง','สอบถามรายละเอียด Vocal Teacher Training และตารางที่เปิดรับ')],extra=['https://www.facebook.com/863765010318929']),
 'pinre-music': dict(title='เรียนดนตรีตามบ้าน\nกับ PINRÉ MUSIC',intro='พินเร่มิวสิค รับสอนเปียโน เบส กีตาร์ อูคูเลเล่ ดนตรีไทย และดนตรีสำหรับเด็ก แจ้งอายุ พื้นฐาน และพื้นที่ที่สะดวกเพื่อสอบถามครูและวันเรียน',address='บริการสอนตามบ้าน กรุงเทพฯ · มีประกาศสอนย่านบางบอน โทรสอบถามพื้นที่',line='paremaii.rnt',lineUrl='https://line.me/ti/p/~paremaii.rnt',hours='ข้อมูลช่องทางระบุทุกวัน 09:00–21:00 น. · ตารางสอนตามนัด',services=[('เปียโนและดนตรีเด็ก','สอบถามแนวทางเรียนให้เหมาะกับวัยและพื้นฐาน'),('กีตาร์ เบส และอูคูเลเล่','เลือกเครื่องดนตรีและบอกเป้าหมายเพื่อปรึกษาครู'),('ดนตรีไทยและคลาสตามบ้าน','แจ้งวิชาที่สนใจ พื้นที่ และวันเวลาที่สะดวก')],extra=['https://www.facebook.com/100179024720589'],limitations=['No physical studio street address verified. Concert poster not used as class photograph. Source prohibits reuse of its videos; no videos downloaded or reused. No actual class photo downloaded; Facebook logo only.']),
 'premuse-music': dict(title='เริ่มเรียนดนตรีที่บางใหญ่\nPremuse Music Studio',intro='มีเปียโน กลอง อูคูเลเล่ ร้องเพลง ไวโอลิน กีตาร์ และทฤษฎีดนตรี พร้อมเตรียมสอบ ABRSM / Trinity โทรปรึกษาวิชาและวัยที่เหมาะสมก่อนนัดเรียน',address='99/59 โครงการ C-Space ถ.แก้วอินทร์ ต.เสาธงหิน อ.บางใหญ่ นนทบุรี 11140',line='@premusemusic',lineUrl='https://lin.ee/AFoKB0E',services=[('เริ่มเรียนดนตรี','เปียโนและกลองเริ่มรับตั้งแต่ 3.5 ปี ร้องเพลงและไวโอลินตั้งแต่ 4 ปี ตามประกาศโรงเรียน'),('กีตาร์และทฤษฎี','กีตาร์รับตั้งแต่ 7 ปี และทฤษฎีดนตรีตั้งแต่ 8 ปี สอบถามความเหมาะสมกับครู'),('เตรียมสอบดนตรี','มีแนวทางเตรียมสอบ ABRSM / Trinity และสอบเข้ามหาวิทยาลัยดนตรี')],extra=['https://www.facebook.com/104046567740096','https://page.line.me/874fhpmr'],limitations=['Street address and public LINE ID verified on official LINE account. No class photograph downloaded; Facebook logo only. Expired September promotion excluded.']),
 'violin-haus': dict(title='ไวโอลิน เปียโน และดนตรีเด็กเล็ก\nพระราม 2 ซอย 33',intro='Violin.Haus Studio มีไวโอลิน เปียโน เชลโล และดนตรีเด็กเล็ก รวมถึงคลาสรวมวงเครื่องสาย Little Sinfonietta ติดต่อสตูดิโอเพื่อเลือกคลาสและนัดทดลองเรียน',address='200/11 พระรามที่ 2 ซอย 33 แขวงบางมด เขตจอมทอง กรุงเทพฯ 10150',phones=['0985184562','0955163263'],line='@218qwclf',lineUrl='https://lin.ee/5nlXRYY',hours='เปิดทุกวันตามประกาศสตูดิโอ · คลาสเรียนต้องนัดล่วงหน้า',services=[('ไวโอลิน เปียโน และเชลโล','แจ้งอายุ เครื่องดนตรี และพื้นฐาน เพื่อสอบถามครูและระดับเรียน'),('ดนตรีเด็กเล็ก','มีแนวคลาส Toddler สำหรับ 0–3 ปี และ Pre-School สำหรับ 3–5 ปี สอบถามรอบปัจจุบัน'),('รวมวงเครื่องสาย','Little Sinfonietta เปิดโอกาสให้นักเรียนฝึกฟังและเล่นดนตรีร่วมกัน')],extra=['https://www.facebook.com/100994035253462','https://line.me/R/ti/p/@218qwclf'],limitations=['Recent post numbers preferred over conflicting directory footer 0818211751. LINE ID resolved from source short link. No actual class photograph downloaded; Facebook logo only. Future concert is not claimed completed.']),
}

def fragment(markup):
    return BeautifulSoup(markup, 'html.parser')

def run():
    audit=[]
    jobs=dict(json.loads((CACHE/'download-jobs.json').read_text('utf8')))
    photo_urls=json.loads((CACHE/'photo-urls.json').read_text('utf8'))
    for lead in LEADS:
        slug=lead['slug']; d=DATA[slug]; path=ROOT/slug/'index.html'
        soup=BeautifulSoup(path.read_text('utf8'),'html.parser')
        soup.body['data-source-enriched']='true'
        soup.h1.clear()
        for n,line in enumerate(d['title'].split('\n')):
            if n:soup.h1.append(soup.new_tag('br'))
            soup.h1.append(line)
        soup.select_one('.hero .intro').string=d['intro']
        soup.select_one('.hero .location').string=d['address']
        phones=d.get('phones',[lead['phone']] if lead['phone'] else [])
        services=d['services']
        for n,card in enumerate(soup.select('#services .service')):
            card.h3.string=services[n][0];card.p.string=services[n][1]
            card.select_one('.number').string=f'0{n+1} / '+('LESSON' if lead['cat']=='music' else 'SERVICE')
            card.a.string='สอบถามรายละเอียด ↗';card.a['href']='#contact'
        # Select options and copy brief use practical visitor questions.
        select=soup.select_one('#kind');select.clear()
        for name,_ in services:
            option=soup.new_tag('option');option.string=name;select.append(option)
        brief={'computer':['ยี่ห้อ รุ่น และสเปกเครื่อง','อาการที่พบและภาพหน้าจอ','วันและจุดที่สะดวกนำเครื่องมาตรวจ'],'key':['ประเภทกุญแจ หรือยี่ห้อ รุ่น และปีรถ','กุญแจหายทั้งหมดหรือมีดอกสำรอง','พื้นที่นัดและเวลาที่ต้องการให้ช่างตรวจสอบ'],'music':['อายุผู้เรียนและเครื่องดนตรีที่สนใจ','พื้นฐานและเป้าหมายการเรียน','พื้นที่ รูปแบบเรียน และวันเวลาที่สะดวก']}[lead['cat']]
        for li,txt in zip(soup.select('.brief-list li'),brief):li.string=txt
        services_head=soup.select_one('#services .section-head p')
        if services_head:services_head.string='เลือกหัวข้อที่ต้องการ แล้วติดต่อเพื่อสอบถามรายละเอียดและคิวที่ว่าง'
        contact=soup.select_one('#contact .contact');contact.clear()
        info=soup.new_tag('div');contact.append(info)
        info.append(fragment('<div class="eyebrow">CONTACT</div>'))
        h=soup.new_tag('h2');h.string='ติดต่อ'+('โรงเรียน' if lead['cat']=='music' else 'ร้านและช่าง');info.append(h)
        p=soup.new_tag('p');p.string=lead['name'];info.append(p)
        p=soup.new_tag('p');p['class']='verified-address';p.string=d['address'];info.append(p)
        p=soup.new_tag('p');p.string=d.get('hours','โทรสอบถามเวลาเปิดและนัดหมายก่อนเดินทาง');info.append(p)
        if slug=='locksmith-thailand':
            p=soup.new_tag('p');p.string='084-536-7949 (โพสต์ มี.ค. 2569) · 081-913-0077 (โพสต์ ธ.ค. 2568) กรุณายืนยันเบอร์ที่ใช้รับงาน';info.append(p)
        links=soup.new_tag('div');links['class']='contact-links';contact.append(links)
        def link(label,url,solid=False):
            a=soup.new_tag('a',href=url);a['class']='btn solid' if solid else 'btn';a.string=label
            if url.startswith('http'):a['target']='_blank';a['rel']='noopener noreferrer'
            links.append(a)
        for n,phone in enumerate(phones):
            digits=phone[:3]+'-'+phone[3:6]+'-'+phone[6:]
            label=d.get('phoneNames',[])
            link('โทร '+digits+(' · '+label[n] if n<len(label) else ''),'tel:'+phone,n==0)
        lineurl=d.get('lineUrl',lead.get('lineUrl'))
        if d.get('line') or lineurl:
            lineurl=lineurl or 'https://line.me/ti/p/~'+d['line']
            link('LINE '+d.get('line','เพิ่มเพื่อนเพื่อสอบถาม'),lineurl,not phones)
        sources=[dict(url=lead['source'],kind='business listing / source article',inspection='Business-specific contact, services and location inspected; not merely lead metadata.')]
        for url in d.get('extra',[]):sources.append(dict(url=url,kind='matched business social / website / official LINE',inspection='Read directly; Facebook identity and profile image matched by og:title.'))
        sourceurl=next((u for u in d.get('extra',[]) if 'facebook.com' in u),lead['source'])
        link('เปิดเว็บไซต์ร้าน' if slug=='chang-khaek-key' else 'เปิดข้อมูล'+('โรงเรียน' if lead['cat']=='music' else 'ธุรกิจ'),d['extra'][0] if slug=='chang-khaek-key' else sourceurl)
        mapurl=d.get('map')
        if mapurl:link('เปิดแผนที่ตามพิกัดที่เผยแพร่',mapurl)
        elif lead['cat']!='music' or slug in ('music-mania-tiwanon','premuse-music','violin-haus'):
            from urllib.parse import quote
            link('ค้นหาตำแหน่งบนแผนที่','https://www.google.com/maps/search/?api=1&query='+quote(lead['name']+' '+d['address']))
        note=soup.new_tag('small');note.string='กรุณายืนยันคิว ราคา และจุดนัดกับธุรกิจก่อนเดินทาง';links.append(note)
        # Visible phone numbers everywhere a telephone CTA occurs.
        for a in soup.select('a[href^="tel:"]'):
            digits=a['href'][4:]
            if not any(char.isdigit() for char in a.get_text()):a.string='โทร '+digits[:3]+'-'+digits[3:6]+'-'+digits[6:]
        for a in soup.select('a[href^="https://lin.ee/"]'):
            if d.get('line') and a.get_text().strip().startswith(('แชต','ทัก','LINE','ติดต่อ')):a.string='LINE '+d['line']
        assets=[];photos=[];photo_records=[]
        assetdir=ROOT/slug/'assets';assetdir.mkdir(exist_ok=True)
        def asset(key,kind):
            source=CACHE/(key+'.jpg')
            if not source.exists():return None
            dest=assetdir/('source-fourth-'+('brand' if kind=='brand' else key)+'.webp')
            with Image.open(source) as im:
                im=im.convert('RGB');im.thumbnail((1400,1400));im.save(dest,'WEBP',quality=88)
                width,height=im.size
            rel=dest.relative_to(ROOT).as_posix();assets.append(rel)
            if kind=='photo':photos.append(rel)
            source_url=jobs.get(key) or photo_urls.get(key)
            if key==d.get('photo') and slug=='acom-rangsit':source_url=photo_urls.get('acom-rangsit-product')
            photo_records.append(dict(path=rel,type=kind,source_image_url=source_url,identity='Matched business name/contact/source context; visually inspected.',width=width,height=height))
            return dest.relative_to(ROOT/slug).as_posix()
        primary=None
        if d.get('photo'):primary=asset(d['photo'],'photo')
        brand=None
        if (CACHE/(slug+'.jpg')).exists() and d.get('photo')!=slug:
            brand=asset(slug,'graphic' if slug=='philung-locksmith' else 'brand')
        primary=primary or brand
        visual=soup.select_one('.hero .visual')
        if visual:
            visual.clear()
            if primary:
                im=soup.new_tag('img',src=primary,alt=(d.get('caption') if photos else 'ภาพแบรนด์จากช่องทางธุรกิจ '+lead['name']));im['class']='source-hero '+('photo' if photos else 'brand');im['fetchpriority']='high';im['decoding']='async';visual.append(im)
                cap=soup.new_tag('p');cap['class']='source-caption';cap.string=d.get('caption','ภาพจากช่องทางของร้าน · Facebook · โลโก้/กราฟิกธุรกิจ');visual.append(cap)
            else:
                visual.append(fragment('<div class="source-facts"><div class="eyebrow">ติดต่อช่างโดยตรง</div><h2>'+html.escape(lead['name'])+'</h2><p>โทร 085-993-5876</p><p>คลอง 13 · บึงน้ำรักษ์ · ธัญบุรี</p><p>โทรแจ้งรุ่นและอาการ แล้วนัดก่อนเดินทาง</p></div>'))
        gallery=soup.select_one('#ideas');gallery.clear()
        wrap=soup.new_tag('div');wrap['class']='wrap';gallery.append(wrap)
        if photos:
            heading='ภาพจากช่องทางธุรกิจ';text='ภาพจากแหล่งที่ระบุด้านล่าง รายละเอียดและราคาในภาพอาจเป็นประกาศเดิม'
        else:
            heading='ก่อนติดต่อ '+lead['name'];text='เตรียมข้อมูลเหล่านี้เพื่อให้คุยรายละเอียดและนัดหมายได้ตรงขึ้น'
        wrap.append(fragment('<div class="section-head"><div><div class="eyebrow">'+('FROM THE BUSINESS' if photos else 'PLAN YOUR VISIT')+'</div><h2>'+html.escape(heading)+'</h2></div><p>'+html.escape(text)+'</p></div>'))
        if d.get('gallery'):
            cards=soup.new_tag('div');cards['class']='cards';wrap.append(cards)
            for key,cap in zip(d['gallery'],['บริการนอกสถานที่ของช่างแขก','ภาพกุญแจรถจากเว็บไซต์ร้าน','ภาพรีโมทรถจากเว็บไซต์ร้าน']):
                src=asset(key,'photo');cards.append(fragment('<figure class="source-photo"><img loading="lazy" decoding="async" src="'+src+'" alt="'+cap+'"><figcaption>'+cap+'</figcaption></figure>'))
        elif photos:
            wrap.append(fragment('<p>'+html.escape(d.get('caption','ภาพจากช่องทางธุรกิจ'))+'</p>'))
        else:
            wrap.append(fragment('<div class="cards">'+''.join('<article class="service"><span class="number">0'+str(i+1)+'</span><h3>'+html.escape(txt)+'</h3><p>'+html.escape(services[i][1])+'</p></article>' for i,txt in enumerate(brief))+'</div>'))
        wrap.append(fragment('<p class="source-note">ข้อมูลและภาพอ้างอิง: <a target="_blank" rel="noopener noreferrer" href="'+html.escape(lead['source'],quote=True)+'">ข้อมูลธุรกิจ</a>'+''.join(' · <a target="_blank" rel="noopener noreferrer" href="'+html.escape(u,quote=True)+'">'+('เว็บไซต์ร้าน' if 'yellowpages' in u else 'LINE Official' if 'line.me' in u else 'ร้านค้า LINE' if 'shop.line' in u else 'Facebook')+'</a>' for u in d.get('extra',[]))+'</p>'))
        # Remove obsolete claims about all imagery being invented placeholders.
        for detail in soup.select('details'):
            if detail.summary and 'ภาพและบริการ' in detail.summary.get_text():
                detail.summary.string='ข้อมูลและภาพในหน้านี้มาจากไหน?';detail.p.string='ชื่อ บริการ และช่องทางติดต่ออ้างอิงจากข้อมูลธุรกิจสาธารณะ ภาพแต่ละภาพระบุที่มาไว้ในหน้าเว็บ นี่คือเว็บไซต์ตัวอย่าง โปรดยืนยันราคา คิว และรายละเอียดล่าสุดกับธุรกิจโดยตรง'
        foot=soup.select_one('.footer .wrap > span')
        if foot:foot.clear();foot.append(lead['name']+' / WEBSITE CONCEPT 2026');foot.append(soup.new_tag('br'));foot.append('ข้อมูลจากช่องทางธุรกิจสาธารณะ · เว็บไซต์ตัวอย่าง ไม่ใช่เว็บไซต์ทางการ')
        for a in soup.select('nav a[href="#ideas"]'):a.string='ภาพและข้อมูล' if photos else 'ก่อนติดต่อ'
        style=soup.new_tag('style');style.string='.visual>.source-hero{max-width:none}.source-hero{display:block;width:100%;height:430px;object-fit:contain;background:#fff}.source-hero.photo{object-fit:contain;background:#18252b}.source-caption{padding:16px 22px;color:var(--paper);font-size:13px;line-height:1.6}.source-facts{padding:48px 32px;color:var(--paper)}.source-facts p{margin-top:22px}.source-photo{margin:0}.source-photo img{display:block;width:100%;aspect-ratio:1;object-fit:contain;background:white}.source-photo figcaption,.source-note{font-size:14px;margin-top:14px}.verified-address{max-width:44ch}.contact-links .btn{overflow-wrap:anywhere}.source-note a{text-underline-offset:4px}@media(max-width:600px){.source-hero{height:330px}.source-caption{padding:14px 18px}.contact-links .btn{white-space:normal}}';soup.head.append(style)
        path.write_text(str(soup),'utf8')
        limitations=d.get('limitations',[]).copy()
        if not photos and slug!='breeze-computer':limitations.append('Actual business photographs unavailable: directory image CDN returned HTTP 404; Facebook provided only a matched brand/profile graphic. Logo/graphic is not counted as a photograph.')
        limitations.append('Public provenance does not establish republication permission or business approval. No stock, AI, or recommended-business images used.')
        if 'hours' not in d:limitations.append('Business opening hours not independently verified; visitor asked to call.')
        if not d.get('map'):limitations.append('Map is a labelled name/address search, not a verified place pin.')
        audit.append(dict(slug=slug,category=lead['cat'],inspected=True,checked_at='2026-11-08',sources=sources,photos=photos,assets=assets,photo_details=photo_records,status='enriched_with_source_photo' if photos else 'enriched_photo_gap',limitations=limitations,verified_contact=dict(phones=phones,line_id=d.get('line'),line_url=lineurl,address=d['address'],hours=d.get('hours')),page_body_marker=True))
        print(slug, 'written',len(photos),'photos',flush=True)
    (ROOT/'research/source-audit-fourth.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n','utf8')

if __name__=='__main__':run()
