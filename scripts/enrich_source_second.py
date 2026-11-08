"""Apply reviewed business-specific content to only the assigned 15 pages.

Uses the inspected source cache and asset manifest created by source_second_*.py.
Never invokes or changes the shared generators or catalog.
"""
import hashlib, html, json, pathlib, re
from urllib.parse import quote
from bs4 import BeautifulSoup
from source_second_batch import ROOT, CACHE, LEADS

DATA = {
 'ideaplus-sign': dict(
  title='ไวนิล ฉลาก สแตนดี้<br>ครบงานพิมพ์ที่ไอเดียพลัส',
  intro='งานพิมพ์สำหรับร้านค้าและแบรนด์ ตั้งแต่ป้ายหน้าร้าน ฉลากสินค้า ไปจนถึงสแตนดี้ เลือกขนาดและวัสดุให้เหมาะกับงานที่ถนนรัตนาธิเบศร์',
  phones=['097-404-4987','063-184-5351'], line='@ideaplus',
  address='223 ถนนรัตนาธิเบศร์ ตำบลบางกระสอ อำเภอเมืองนนทบุรี นนทบุรี 11000',
  hours='จันทร์–เสาร์ 08:30–17:30 น.', coords='13.861153465746607,100.5050125841984', email='print_idea@hotmail.com',
  services=[('ป้ายไวนิลตามขนาด','พิมพ์ป้ายร้าน ป้ายโฆษณา และแบนเนอร์สำหรับใช้งานในอาคารและกลางแจ้ง'),('ฉลากสินค้าและสติ๊กเกอร์','ฉลาก PVC แบบด้าน เงา หรือใส พร้อมไดคัทตามรูปแบบบรรจุภัณฑ์'),('สแตนดี้และงานพิมพ์ร้านค้า','สแตนดี้ X-stand นามบัตร โบรชัวร์ และบัตรสะสมแต้ม')],
  captions=['สแตนดี้นักฟุตบอล','สติ๊กเกอร์ฉลากไอศกรีม','งานพิมพ์ไวนิลจากเครื่องพิมพ์','สแตนดี้ขนาดเท่าคนจริง'],
  brief=['ขนาดกว้าง × สูง และจำนวนชิ้น','ไฟล์แบบ โลโก้ และวัสดุที่ต้องการ','วันใช้งานและวิธีรับสินค้า'],
  limitations=['Photographs attributed to the business gallery, not independently commissioned or dated.']),
 'nbmedia-sign': dict(
  title='ป้ายไวนิลไทรน้อย<br>ออกแบบและผลิตกับ NB MEDIA',
  intro='ส่งขนาดป้ายและรูปจุดติดตั้งให้ NB MEDIA ประเมิน งานป้ายร้าน ป้ายประชาสัมพันธ์ และป้ายกลางแจ้งในไทรน้อยและพื้นที่ใกล้เคียง',
  phones=['086-983-9259','063-946-2838'], line='@pod2106w', facebook='https://www.facebook.com/Bestinkjet',
  address='ที่ตั้งร้าน 89/21 หมู่ 5 ตำบลไทรน้อย อำเภอไทรน้อย นนทบุรี 11150',
  address_extra='ที่อยู่บริษัท 1/24 หมู่ 5 ตำบลไทรน้อย อำเภอไทรน้อย นนทบุรี 11150',
  map_url='https://maps.app.goo.gl/LajBQgjCBE18UcLK6', map_kind='business_published_maps_link',
  services=[('ป้ายร้านและป้ายเปิดร้าน','ออกแบบและพิมพ์ไวนิลตามขนาดพื้นที่หน้าร้าน'),('ป้ายประชาสัมพันธ์','ป้ายโปรโมชั่น งานกิจกรรม และประกาศสำหรับธุรกิจหรือหน่วยงาน'),('ป้ายกลางแจ้งพร้อมโครง','แจ้งขนาด จุดติดตั้ง และลักษณะพื้นที่เพื่อประเมินโครงและวิธีติดตั้ง')],
  captions=['ป้ายบอกทางริมถนน','ป้ายติดตั้งหน้าอาคาร','ป้ายร้านอาหารกลางแจ้ง','ป้ายไวนิลสำหรับร้านค้า'],
  brief=['ความกว้าง × สูง และจำนวนป้าย','ใช้งานในอาคารหรือกลางแจ้ง','ต้องการเจาะตาไก่ ทำโครง หรือติดตั้ง'],
  limitations=['Website distinguishes shop 89/21 from company address 1/24; retained both with explicit labels.','Opening hours not published on inspected page.']),
 'asign-graphic': dict(
  title='ป้ายไฟและตัวอักษร<br>เอซายน์ กราฟฟิก ปากเกร็ด',
  intro='ผลิตและติดตั้งป้ายตามแบบ ทั้งป้ายไฟ ตัวอักษรโลหะ ไวนิล และสติ๊กเกอร์ ใกล้แยกสวนสมเด็จ บ้านใหม่ ปากเกร็ด',
  phones=['081-256-4225','092-659-1561'],line='@asign2019',email='asign2019@gmail.com',
  address='72/99-100 หมู่ 3 ถนนสะพานนนทบุรี–บางบัวทอง ตำบลบ้านใหม่ อำเภอปากเกร็ด นนทบุรี 11120',
  hours='จันทร์–เสาร์ 08:30–18:00 น.',coords='13.941558758778697,100.54149657281633',
  services=[('ป้ายไฟและอักษรโลหะ','ป้าย LED กล่องไฟ และตัวอักษรซ่อนไฟสำหรับหน้าร้านและสำนักงาน'),('ป้ายไวนิลและป้ายหน้าอาคาร','พิมพ์ไวนิลพร้อมโครง ติดตั้งป้ายภายในและภายนอกอาคาร'),('สติ๊กเกอร์และงานเลเซอร์','ฉลากสินค้า สติ๊กเกอร์ติดกระจก งานตัดตัวอักษรและเลเซอร์อะคริลิค')],
  captions=['ป้ายไฟร้านอาหาร','ป้ายไฟรูปถ้วยกาแฟ','ป้ายหน้าร้านเครื่องดื่ม','งานป้ายและติดตั้งหน้าอาคาร'],
  brief=['ส่งแบบป้ายหรือโลโก้','รูปพื้นที่และขนาดโดยประมาณ','วัสดุ ระบบไฟ และวันติดตั้งที่ต้องการ'],limitations=[]),
 'kongthong-sign': dict(
  title='คงทองโฆษณา บางใหญ่<br>จากป้ายไฟถึงป้ายขนาดใหญ่',
  intro='งานป้ายที่ซอยกันตนา ทั้งป้ายหน้าร้าน ตัวอักษรไฟ สติ๊กเกอร์อิงค์เจ็ท ป้ายทาวเวอร์ และงานหุ้มคอมโพสิท',
  phones=['081-689-7687','02-403-3270'],phone_note='โทรศัพท์สำนักงาน 02-403-3270 ถึง 02-403-3273',line='Kongthongads',
  email='info@kongthong-group.com',facebook='https://www.facebook.com/kongthongadvertising/',
  address='22/4 หมู่ 5 ซอยกันตนา ตำบลบางม่วง อำเภอบางใหญ่ นนทบุรี 11140',
  services=[('ป้ายไฟและป้ายหน้าร้าน','ป้ายกล่องไฟ ตัวอักษร และป้ายสำหรับอาคารธุรกิจ'),('ป้ายทาวเวอร์และป้ายขนาดใหญ่','งานป้ายโฆษณาสำหรับพื้นที่กลางแจ้งและจุดมองเห็นระยะไกล'),('สติ๊กเกอร์และคอมโพสิท','งานพิมพ์อิงค์เจ็ทและหุ้มแผงคอมโพสิทตามพื้นที่ติดตั้ง')],
  captions=['งานภาพโฆษณาขนาดใหญ่','ป้ายประชาสัมพันธ์ข้ามถนน','งานตัวอักษรไฟ','ป้ายโฆษณากลางแจ้ง'],
  brief=['รูปพื้นที่ติดตั้งและขนาดป้าย','ชนิดวัสดุและไฟที่ต้องการ','สถานที่และช่วงเวลาที่สะดวกติดตั้ง'],
  extra_sources=[('https://kongthong-group.com/site/','ผลงานบนเว็บไซต์คงทอง')],limitations=['No published opening hours or verified latitude/longitude; maps searches full published address.']),
 'do-it-art': dict(
  title='Do It Art สวนหลวง<br>ป้าย อะคริลิค และงานสกรีน',
  intro='งานป้ายตามแบบของคุณ ทั้งไวนิล สติ๊กเกอร์ อะคริลิค พลาสวู้ด สเตนเลส และป้ายไฟ ติดต่อคุยรายละเอียดผ่านโทรศัพท์หรือ LINE',
  phones=['089-740-4544'], line_url='https://lin.ee/xUsSfDa',line_label='LINE ร้าน · lin.ee/xUsSfDa',
  area_only='สวนหลวง กรุงเทพฯ',
  services=[('ป้ายไวนิลและสติ๊กเกอร์','สำหรับป้ายโฆษณาและงานพิมพ์ตามแบบ'),('อะคริลิคและพลาสวู้ด','แจ้งแบบ ขนาด และลักษณะชิ้นงานที่ต้องการ'),('ป้ายไฟและสเตนเลส','คุยวัสดุและรายละเอียดจุดติดตั้งกับร้านก่อนขอราคา')],
  brief=['แบบหรือภาพอ้างอิงชิ้นงาน','ขนาด วัสดุ และจำนวน','กำหนดใช้งานและพื้นที่ติดตั้ง'],
  photo_note='ยังไม่มีภาพผลงานที่นำมาแสดงได้ กรุณาขอดูตัวอย่างงานปัจจุบันจากร้านผ่าน LINE',
  limitations=['FindGlocal contact and services read via indexed web page; direct request blocked HTTP 403.','Only Facebook Graph profile image was exposed; download reset/throttled. No attributable work photo downloaded.','Street address, opening hours, and LINE ID not published; only area and LINE short URL verified.']),
 'nc-solution-demo': dict(
  title='NC Solution<br>ตรวจเช็ค ซ่อม และติดตั้ง CCTV',
  intro='ผู้ให้บริการบนเว็บช่าง ระบุงานระบบ CCTV AHD และ IP แก้ไขกล้อง ดูผ่านมือถือ และประเมินงานในกรุงเทพฯ นนทบุรี และปทุมธานี',
  phones=[],area_only='กรุงเทพฯ · นนทบุรี · ปทุมธานี',
  services=[('ตรวจเช็คและซ่อมกล้อง','ตรวจระบบและแก้ปัญหากล้องวงจรปิด CCTV AHD / IP'),('จัดสเปคและติดตั้ง','เลือกอุปกรณ์ตามความต้องการและประเมินที่หน้างาน'),('ดูภาพผ่านมือถือ','ตั้งค่าระบบดูออนไลน์ตามอุปกรณ์และเครือข่ายของพื้นที่')],
  brief=['อาการเสียและรุ่นกล้องเดิม','จำนวนกล้องและรูปจุดติดตั้ง','จังหวัดและอำเภอของหน้างาน'],
  photo_note='ยังไม่มีภาพผลงานของ NC Solution ในประกาศที่ตรวจได้ กรุณาขอรูปจากผู้ให้บริการโดยตรง',
  contact_note='เบอร์โทรและ LINE ไม่เปิดเผยสาธารณะ กรุณาเปิดโปรไฟล์ NC Solution บนเว็บช่างเพื่อดูวิธีติดต่อ',
  limitations=['Contact is behind Webchang phone verification; no OTP, form submission, or contact request performed.','All three img elements are recommended OTHER providers (/92496, /92956, /95285); explicitly excluded.','No public phone, LINE, street address, hours, or precise map verified.']),
 'spthai-cctv-demo': dict(
  title='SP Thai CCTV<br>ตรวจสอบช่องทางก่อนนัดงาน',
  intro='ข้อมูลเดิมระบุบริการกล้องวงจรปิดและเดินสาย LAN ในนนทบุรี เว็บไซต์โดเมนเดิมปัจจุบันใช้ชื่อช่างแจนและเบอร์ติดต่อใหม่ โปรดสอบถามชื่อผู้รับงานก่อนนัดหมาย',
  phones=['062-195-8505'],phone_note='เบอร์บนเว็บไซต์ปัจจุบัน: ช่างแจน · ข้อมูลเดิม SP Thai CCTV ระบุ 065-087-3758',
  area_only='บริการนนทบุรีตามข้อมูลเดิม · กรุณาสอบถามพื้นที่รับงานปัจจุบัน',
  services=[('ติดตั้งและซ่อมกล้อง','เว็บไซต์ปัจจุบันระบุบริการติดตั้ง ตรวจเช็ค และปรับปรุงระบบกล้อง'),('เดินสาย LAN และ Wi-Fi','สอบถามรูปแบบเครือข่ายและพื้นที่หน้างานกับผู้ให้บริการปัจจุบัน'),('ตรวจสอบก่อนนัดหมาย','แจ้งว่าอ้างอิงข้อมูล SP Thai CCTV และยืนยันชื่อผู้รับงานกับเบอร์ที่ใช้งาน')],
  brief=['ชื่อผู้ให้บริการที่ต้องการติดต่อ','พื้นที่และรายละเอียดระบบเดิม','รูปจุดติดตั้งและขอบเขตที่ต้องการ'],
  photo_note='ยังไม่แสดงภาพจากเว็บไซต์ปัจจุบัน เนื่องจากชื่อผู้ให้บริการและเบอร์โทรต่างจากข้อมูลเดิม',
  extra_sources=[('https://www.spthai-cctv.com/','เว็บไซต์โดเมนเดิมปัจจุบัน')],
  limitations=['HTTPS certificate hostname mismatch; public page inspected with certificate checking disabled for this diagnostic read only.','Current domain identifies Chang Jan (ช่างแจน), 062-1958505, not original lead 0650873758; continuity unverified.','Current-domain images excluded to avoid attributing potentially different provider photographs.','No street address, hours, LINE ID, or precise map verified.'],status='source_identity_conflict'),
 'changnon-cctv-demo': dict(
  title='ช่างนนท์ ซีซีทีวี<br>ติดตั้งและดูแลระบบถึงหน้างาน',
  intro='จำหน่าย ติดตั้ง และตรวจเช็คกล้องวงจรปิด พร้อมงานจานดาวเทียม ทีวีดิจิตอล และโซล่าเซลล์ โดย หจก. ช่างนนท์ ซีซีทีวี คอมมิวนิเคชั่น บางบัวทอง',
  phones=['082-756-7899'],line='@changnon',line_url='https://lin.ee/0aE4S9J',
  address='12/12 หมู่ 7 ตำบลบางรักพัฒนา อำเภอบางบัวทอง นนทบุรี 11110',
  services=[('กล้องวงจรปิด CCTV','ออกแบบจุดติดตั้ง เดินสายร้อยท่อ และประเมินหน้างาน'),('ตรวจเช็คและแก้ไขระบบ','แจ้งอาการและรุ่นอุปกรณ์ให้ช่างตรวจรายละเอียดก่อนนัด'),('จานดาวเทียมและโซล่าเซลล์','สอบถามระบบทีวีดิจิตอล จานดาวเทียม และงานโซล่าเซลล์')],
  captions=['กล้องติดตั้งภายนอกอาคาร','กล้องติดตั้งใต้ชายคา','จุดกล้องภายในอาคาร','กล้องภายในพร้อมตัวอย่างภาพ'],
  brief=['รูปพื้นที่และจุดที่ต้องการเฝ้าดู','รุ่นกล้องเดิมและปัญหาที่พบ','ที่อยู่หน้างานและช่วงเวลานัดหมาย'],
  limitations=['Selected installation photo collages contain the business logo, phone, captions and marketing overlays; no raw originals exposed.','No opening hours or exact coordinates verified.']),
 'satpp-service-demo': dict(
  title='SATPP Service สามัคคี<br>กล้องและระบบความปลอดภัย',
  intro='บริการระบบกล้องวงจรปิด สัญญาณกันขโมย ประตูไม้กั้น และเครือข่าย โดยบริษัท พีแอนด์พี อีเล็คโทรนิคส์ จำกัด ปากซอยสามัคคี 50',
  phones=['081-348-8939','081-487-0355'],line='@SATPPSERVICE',
  address='464 ซอยสามัคคี 50 ถนนสามัคคี ตำบลท่าทราย อำเภอเมืองนนทบุรี นนทบุรี 11000',
  hours='จันทร์–ศุกร์ 09:00–19:00 น. (ตามข้อมูลบนเว็บไซต์)',
  services=[('กล้องวงจรปิดและ IP Camera','สอบถามระบบ HIKVISION, DAHUA, EZVIZ และ HI-LOOK'),('ระบบควบคุมทางเข้า','ประตูไม้กั้น Access Control และ Digital Door Lock'),('Network และสัญญาณกันขโมย','ออกแบบระบบเครือข่ายและอุปกรณ์รักษาความปลอดภัยตามสถานที่')],
  brief=['ลักษณะอาคารและรูปพื้นที่','ระบบกล้องหรืออุปกรณ์เดิม','จำนวนจุดที่ต้องการและงบประมาณ'],
  photo_note='ยังไม่สามารถนำรูปผลงานจากเว็บไซต์มาแสดงได้ ติดต่อ SATPP เพื่อขอดูงานติดตั้งที่ใกล้เคียงกับพื้นที่ของคุณ',
  limitations=['Direct website fetches HTTP 403 and web open HTTP 429; contact, hours and services recovered from indexed official website.','No original image URL could be inspected and downloaded; photos unavailable, not verified.','No exact coordinates verified.']),
 'homesat-hd-demo': dict(
  title='HomeSat-HD ติวานนท์<br>วางระบบกล้องสำหรับพื้นที่คุณ',
  intro='ออกแบบ จำหน่าย และติดตั้ง CCTV สำหรับบ้าน ร้านค้า สำนักงาน และโรงงาน โดยบริษัท ริชโปร แอสเซท จำกัด พร้อมเดินสายและตั้งค่าดูผ่านมือถือ',
  phones=['090-557-1049','090-409-5018'],facebook='https://www.facebook.com/Shopcctvtook',
  address='14 ถนนติวานนท์ ท่าทราย เมืองนนทบุรี นนทบุรี 11000',
  address_extra='อีกจุดติดต่อ: 208/5 ถนนพัฒนาการ แขวงประเวศ เขตประเวศ กรุงเทพฯ 10250',
  services=[('ออกแบบระบบกล้อง','เลือก HIKVISION, DAHUA, UNV, EZVIZ หรือ IMOU ให้เหมาะกับการใช้งาน'),('ติดตั้งและเดินระบบ','เดินสาย ติดตั้งเครื่องบันทึก และตั้งค่าดูผ่านมือถือ'),('ประเมินหน้างานและหลังการขาย','ส่งรูปพื้นที่เพื่อคุยแนวทาง ขอใบเสนอราคา และสอบถามเงื่อนไขดูแลระบบ')],
  captions=['ทีมงานในพื้นที่ติดตั้ง','เดินสายภายในตู้ระบบ','จัดระเบียบสายและอุปกรณ์','ตรวจงานระบบและตู้เครือข่าย'],
  brief=['ประเภทอาคารและจำนวนกล้อง','ภาพพื้นที่และแนวเดินสาย','ระบบเดิมและระยะเวลาเก็บภาพที่ต้องการ'],
  extra_sources=[('https://www.homesat-hd.com/','ภาพงานจากเว็บไซต์ HomeSat-HD')],
  limitations=['Source contact page uses แขวง/เขต for Nonthaburi; retained locality without asserting those incorrect administrative prefixes.','Installation photographs confirmed present in official homepage HTML; gallery route inaccessible, so image citations use the inspected homepage.','No opening hours or exact map coordinates verified.']),
 'lungmaew-garden': dict(
  title='ลุงแมว รับจ้างตัดหญ้า<br>จัดสวนและตัดแต่งกิ่งไม้',
  intro='ประกาศบริการในปากเกร็ดและนนทบุรี โซนท่าอิฐ–บางบัวทอง ระบุงานตัดหญ้า จัดสวน ตัดแต่งกิ่งไม้ และเก็บกวาดหลังงาน ติดต่อสอบถามคิวปัจจุบันผ่าน LINE',
  phones=['098-909-5464'],phone_note='เบอร์จากข้อมูลเดิม ยังยืนยันซ้ำไม่ได้ แนะนำติดต่อ LINE ก่อนนัดงาน',
  line='maew.gardening',area_only='ปากเกร็ด นนทบุรี · โซนท่าอิฐ–บางบัวทอง',
  services=[('ตัดหญ้า','ส่งรูปและขนาดพื้นที่เพื่อสอบถามขอบเขตและคิวงาน'),('จัดสวนและตัดแต่งกิ่งไม้','แจ้งชนิดต้นไม้ ความสูง และสภาพพื้นที่ให้ผู้รับงานทราบ'),('เก็บกวาดหลังงาน','สอบถามเรื่องเก็บเศษหญ้าและกิ่งไม้ให้ชัดก่อนตกลงราคา')],
  brief=['รูปปัจจุบันและขนาดสวน','ต้นไม้หรือพื้นที่ที่ต้องดูแล','ตำแหน่งหน้างานและวันสะดวก'],
  photo_note='ยังไม่มีรูปผลงานที่ตรวจที่มาและดาวน์โหลดได้ กรุณาขอดูงานล่าสุดกับลุงแมวทาง LINE',
  limitations=['Kaidee direct/current page returns only a JavaScript shell. Indexed listing dated 2014-09-25 supplies service area and LINE.','Indexed phones masked, ending 273/795; original lead phone 0989095464 could not be corroborated, displayed explicitly as older unverified data.','Facebook returns login-only shell; no source photographs downloaded.','Old listing price excluded; no street address, hours or precise coordinates verified.']),
 'backcliff-garden': dict(
  title='Backcliff Garden<br>จัดสวน ปลูกต้นไม้ ดูแลภูมิทัศน์',
  intro='ประกาศของบริษัท สวนเขาหมาก จำกัด ในท่าแร้ง บางเขน ระบุงานออกแบบสวน ปลูกและขุดล้อมต้นไม้ ตลอดจนดูแลภูมิทัศน์สำนักงานและโครงการ',
  phones=['095-742-3064','089-895-3019'],line='@backcliffgarden',
  contact_note='ประกาศสะกด LINE สองแบบ: @backcliffgarden และ @blackcliffgarden แนะนำโทรยืนยันบัญชีก่อนส่งรายละเอียด',
  area_only='ท่าแร้ง เขตบางเขน กรุงเทพฯ',
  services=[('ออกแบบและจัดสวน','คุยรูปแบบสวนและพื้นที่ใช้งานก่อนประเมินรายละเอียด'),('ปลูกและขุดล้อมต้นไม้','จัดส่งต้นไม้ตามรายการ ปลูก ย้าย และขุดล้อมตามสภาพหน้างาน'),('ดูแลภูมิทัศน์โครงการ','ดูแลสวนสำนักงานและพื้นที่โครงการ รวมถึงตัดหญ้าและตัดแต่งกิ่งไม้')],
  brief=['รูปสวนและรายการต้นไม้','ขนาดพื้นที่และทางเข้าออก','งานครั้งเดียวหรือดูแลต่อเนื่อง'],
  photo_note='ยังไม่สามารถดาวน์โหลดภาพจากประกาศได้ กรุณาขอชมผลงานกับผู้ดูแลก่อนนัดประเมิน',
  limitations=['BaanFinder direct HTTP 403; indexed exact listing supplies company, two phones, area and services.','Listing spells English brand Blackcliffgarden and gives conflicting LINE IDs @backcliffgarden/@blackcliffgarden; shown transparently, no asserted account verification.','No images downloaded; no exact street address, hours or precise map verified.']),
 'sp-landscapethai': dict(
  title='SP Landscapethai<br>สอบถามบริการตัดหญ้าในนนทบุรี',
  intro='ข้อมูลเดิมระบุงานตัดหญ้า ตัดต้นไม้ และดูแลสวนในนนทบุรี โปรดยืนยันชื่อผู้รับงานและพื้นที่บริการก่อนนัดหมาย เนื่องจากเว็บไซต์ปัจจุบันมีข้อมูลติดต่อแตกต่างจากข้อมูลเดิม',
  phones=['094-515-7920'],phone_note='เบอร์ที่ระบุในหน้าบริการเดิม กรุณายืนยันชื่อผู้ให้บริการก่อนนัด',
  area_only='นนทบุรีตามหน้าบริการเดิม',
  services=[('ตัดหญ้า','สอบถามพื้นที่ ขนาด และสภาพหญ้าที่ต้องการดูแล'),('ตัดแต่งต้นไม้','ส่งรูปต้นไม้และบริเวณโดยรอบให้ประเมินก่อนรับงาน'),('ดูแลสวนและเก็บพื้นที่','คุยรอบบริการและการเก็บเศษกิ่งไม้ให้ครบก่อนตกลงราคา')],
  brief=['ยืนยันชื่อผู้รับงานและเบอร์ติดต่อ','รูปพื้นที่และขนาดโดยประมาณ','รายละเอียดเก็บขนเศษหญ้าและกิ่งไม้'],
  photo_note='ยังไม่แสดงรูปจากเว็บไซต์ปัจจุบัน เพราะข้อมูลติดต่อและชื่อธุรกิจไม่ตรงกับบริการเดิม',
  limitations=['Exact legacy category still includes 0945157920 in title/navigation, but current footer lists Maypraew/mahasarakhamtreeshop, 0852094218, LINE @230tviay.','Excluded all current-domain pictures/social links from original SP lead attribution; continuity unverified.','Original phone retained with clear older-source wording; no current contact verification, street address, hours or precise map.'],status='source_identity_conflict'),
 'greenery-landscape': dict(
  title='กรีนเนอรี่แลนด์สเคป<br>สวน ระบบน้ำ และภูมิทัศน์',
  intro='ออกแบบและดูแลสวน ไม้ประดับภายในอาคาร สนามหญ้า ระบบสปริงเกอร์ น้ำตก น้ำพุ และไฟประดับสวน ติดต่อสอบถามงานได้ที่บางกรวย',
  phones=['089-104-2424'],line='golf_kiatwuttinon',
  address='90/41 ถนนบางกรวย–ไทรน้อย ตำบลบางกรวย อำเภอบางกรวย นนทบุรี 11130',
  hours='ไดเรกทอรีระบุ 24 ชั่วโมง · กรุณานัดหมายก่อนเข้าพบ',coords='13.807314641082,100.50720532112',
  services=[('ออกแบบและดูแลสวน','สวนหลายรูปแบบ ไม้ประดับในอาคาร สนามหญ้า และดูแลสวนรายเดือน'),('ระบบรดน้ำและน้ำตก','งานสปริงเกอร์ น้ำตก น้ำพุ และลำธารในสวน'),('งานภูมิทัศน์และไฟสวน','สอบถามงานภูมิทัศน์และระบบไฟประดับตามพื้นที่')],
  captions=['สวนตกแต่งจากประกาศของกรีนเนอรี่แลนด์สเคป'],
  brief=['ภาพพื้นที่และสไตล์สวนที่ชอบ','ขนาดสวนและระบบน้ำเดิม','งานปรับปรุงหรือดูแลรายเดือน'],
  extra_sources=[('https://www.nanagarden.com/product/314499','ภาพจากประกาศกรีนเนอรี่แลนด์สเคป')],
  limitations=['YellowPages main profile has only unrelated recommended-business product photographs; all excluded.','One attributable photograph recovered from NanaGarden seller listing with identical business name and phone, dated 2019-07-11; not claimed as recent.','NanaGarden lists Sai Noi broadly; current contact address and map use YellowPages Bang Kruai listing.','24-hour listing is not independently confirmed as walk-in availability.']),
 'johnchaorai-garden': dict(
  title='johnchaorai<br>จัดสวนและดูแลพื้นที่สีเขียว',
  intro='บริการจัดสวน ดูแลสวนรายเดือน และงานโครงการ พร้อมจัดหาต้นไม้และอุปกรณ์ เริ่มจากส่งรูปพื้นที่ให้ทีมประเมินในกรุงเทพฯ และปริมณฑล',
  phones=['063-863-4826'],line='@johnchaorai',email='aiidea2024@gmail.com',
  hours='จันทร์–เสาร์ 08:00–18:00 น.',area_only='กรุงเทพฯ · นนทบุรี · ปทุมธานี · สมุทรปราการ',
  services=[('ดูแลสวนรายครั้ง','ตัดหญ้า ตัดแต่งไม้พุ่ม เก็บเศษพืช และประเมินปัญหาสวน'),('ดูแลสวนรายเดือน','จัดรอบดูแล รดน้ำ ใส่ปุ๋ย กำจัดวัชพืช และตรวจสุขภาพต้นไม้'),('งานโครงการและต้นไม้ใหญ่','จัดทีมดูแลพื้นที่ส่วนกลาง จัดหาต้นไม้ ปลูก และเคลื่อนย้ายต้นไม้')],
  captions=['ขนส่งต้นไม้ด้วยรถเครน','ทีมงานปลูกต้นไม้','ดูแลต้นไม้ในพื้นที่อาคาร','งานดูแลสวนและต้นไม้'],
  brief=['ส่งรูปพื้นที่ผ่าน LINE','บอกขนาดสวนและรอบดูแลที่ต้องการ','นัดสำรวจและขอรายละเอียดราคา'],
  limitations=['No public street address or exact map coordinates; service area is not presented as a shop location.','Website-published photos are source-attributed; raw camera originals and capture dates not verified.']),
}

def e(s): return html.escape(str(s),quote=True)
def link(url,label,cls=''):return f'<a class="{cls}" href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(label)} ↗</a>'
def phone_link(phone,cls='btn solid'):
    return f'<a class="{cls}" href="tel:{re.sub(r"[^0-9+]", "", phone)}">โทร {e(phone)} ↗</a>'
def source_records(slug,lead,c):
    raw=json.loads((CACHE/f'{slug}.json').read_text(encoding='utf-8'))
    records=[{'url':r['url'],'type':'facebook' if 'facebook.com' in r['url'] else 'lead_source','access':r.get('http','request_failed'),'limitations':r.get('error'),'reviewed':True} for r in raw]
    if slug in ('do-it-art','backcliff-garden','satpp-service-demo'):
        records[0]['access']='indexed_page_read; direct fetch blocked'
    if slug=='lungmaew-garden': records[0]['access']='indexed legacy listing read; current page JavaScript shell'
    if slug=='spthai-cctv-demo':records.append({'url':'https://www.spthai-cctv.com/','type':'current_domain','access':'200 only with certificate validation disabled for diagnostic read','reviewed':True})
    for url,label in c.get('extra_sources',[]):
        if url not in [r['url'] for r in records]:records.append({'url':url,'type':'supplementary_business_source','label':label,'access':'200','reviewed':True})
    return records

def main():
    downloads=json.loads((CACHE/'downloads.json').read_text(encoding='utf-8'))
    audit=[]
    for lead in LEADS:
        slug=lead['slug'];c=DATA[slug];dest=ROOT/slug/'index.html';old=dest.read_text(encoding='utf-8');soup=BeautifulSoup(old,'html.parser')
        head=str(soup.head);head=re.sub(r'<title>.*?</title>',f'<title>{e(lead["name"])} | {e(c["services"][0][0])}</title>',head,flags=re.S)
        head=re.sub(r'<meta[^>]+name="description"[^>]*>',f'<meta name="description" content="{e(c["intro"])}">',head)
        extra_css='''
        .hero .visual,.theme-sign .visual{border-radius:8px}.source-hero{margin:0;background:var(--dark);color:var(--paper)}.source-hero img{display:block;width:100%;height:410px;object-fit:contain;background:var(--dark)}.source-hero figcaption{padding:14px 20px;font-size:13px}.source-hero a{display:block;margin-top:4px;color:inherit}.hero-contact{margin-top:20px}.hero-contact a{font-size:20px;font-weight:700}.hero-facts{padding:38px;color:var(--paper)}.hero-facts h2{font-size:27px}.hero-facts p{margin-top:16px}.source-gallery{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}.source-gallery figure{margin:0;min-width:0}.source-gallery img{width:100%;height:310px;object-fit:contain;background:var(--dark);display:block;border-radius:5px}.source-gallery figcaption{font-size:14px;margin-top:9px}.source-gallery a{font-size:12px}.contact address{font-style:normal;font-size:17px;margin-top:16px}.contact-links a{overflow-wrap:anywhere}.source-links{display:flex;flex-wrap:wrap;gap:12px 24px;margin-top:20px}.source-links a{font-size:14px}.contact-note{font-size:14px;line-height:1.65}.availability{border-left:3px solid var(--accent);padding:24px;background:#ffffff80}.location{opacity:1}.photo-age{font-size:13px;margin-top:10px}.footer{opacity:1}.hero h1{font-size:clamp(32px,4.1vw,57px)}.brand,.contact,.hero-grid>div{min-width:0}.wrap{overflow-wrap:anywhere}.notice{font-size:12px}.section-head p{opacity:1}.source-info{margin-top:28px;border-top:1px solid #89928b60;padding-top:15px}.contact h2{font-size:30px}.panel{gap:35px}@media(max-width:560px){.source-gallery{grid-template-columns:1fr}.source-gallery img{height:280px}.source-hero img{height:320px}.hero-facts{padding:28px}.hero-contact a{font-size:18px}.footer .wrap>span{display:block;margin-bottom:12px}.notice{padding:7px 5%}.contact .btn{font-size:14px;padding:12px}.source-links{display:block}.source-links a{display:block;margin:10px 0}}
        '''
        head=head.replace('</head>',f'<style>{extra_css}</style></head>')
        photos=[dict(d) for d in downloads if d['slug']==slug and d.get('path')]
        for j,p in enumerate(photos):
            p['caption']=c['captions'][j];p['visually_reviewed']=True;p['verification']='Source attribution and visible photo content reviewed; photographer, copyright permission and capture date not independently verified.'
            p['selection']='Manually selected within business gallery or matching seller listing; recommendation photos excluded.'
            p['local_derivative']='Resized to max 1600px and converted to WebP; source composition, branding, captions preserved.'
        phones=''.join(phone_link(p) for p in c['phones'])
        line_url=c.get('line_url') or ('https://line.me/R/ti/p/'+c['line'] if c.get('line','').startswith('@') else 'https://line.me/ti/p/~'+c['line'] if c.get('line') else '')
        line_label=('LINE '+c['line']) if c.get('line') else c.get('line_label','')
        address=c.get('address',c.get('area_only',''))
        map_url=c.get('map_url');map_kind=c.get('map_kind')
        if c.get('coords'):map_url='https://www.google.com/maps/search/?api=1&query='+c['coords'];map_kind='source_published_coordinates'
        elif c.get('address') and not map_url:map_url='https://www.google.com/maps/search/?api=1&query='+quote(lead['name']+' '+c['address']);map_kind='address_search_not_verified_pin'
        cta=phone_link(c['phones'][0]) if c['phones'] else link(lead['source'],'เปิดโปรไฟล์ NC Solution','btn solid')
        subcta=link(line_url,line_label,'btn') if line_url else '<a class="btn" href="#contact">ช่องทางติดต่อ ↓</a>'
        gallery=''
        if photos:
            p=photos[0];hero=f'<figure class="source-hero"><img src="assets/{pathlib.Path(p["path"]).name}" alt="{e(p["caption"])} — {e(lead["name"])}" width="{p["dimensions"][0]}" height="{p["dimensions"][1]}" fetchpriority="high"><figcaption>{e(p["caption"])}{link(p["source_page"],"ดูภาพบนแหล่งต้นทาง")}</figcaption></figure>'
            for p in photos:
                gallery+=f'<figure><a href="assets/{pathlib.Path(p["path"]).name}" target="_blank" rel="noopener"><img src="assets/{pathlib.Path(p["path"]).name}" alt="{e(p["caption"])} — {e(lead["name"])}" width="{p["dimensions"][0]}" height="{p["dimensions"][1]}" loading="lazy"></a><figcaption>{e(p["caption"])}<br>{link(p["source_page"],"แหล่งภาพต้นทาง")}</figcaption></figure>'
            gallery=f'<div class="source-gallery">{gallery}</div>'
        else:
            hero=f'<div class="hero-facts"><div class="eyebrow">{e(lead["name"])}</div><h2>{e(c["services"][0][0])}</h2><p>{e(address)}</p><p>{e(c.get("photo_note",""))}</p><div class="actions">{cta}</div></div>'
            gallery=f'<p class="availability">{e(c["photo_note"])}</p>'
        services=''.join(f'<article class="service"><span class="number">0{j+1}</span><h3>{e(title)}</h3><p>{e(txt)}</p><a href="#contact">สอบถามรายละเอียด ↗</a></article>' for j,(title,txt) in enumerate(c['services']))
        contact_links=phones
        if line_url:contact_links+=link(line_url,line_label,'btn')
        facebook=c.get('facebook',lead.get('facebook'))
        if facebook:contact_links+=link(facebook,'Facebook ของธุรกิจ','btn')
        if c.get('email'):contact_links+=f'<a class="btn" href="mailto:{e(c["email"])}">{e(c["email"])}</a>'
        if not contact_links:contact_links=link(lead['source'],'วิธีติดต่อ NC Solution บนเว็บช่าง','btn solid')
        if map_url:contact_links+=link(map_url,'เปิดแผนที่จากพิกัดต้นทาง' if c.get('coords') else 'เปิดแผนที่ร้าน' if c.get('map_url') else 'ค้นหาแผนที่จากที่อยู่','btn')
        if map_kind=='address_search_not_verified_pin':contact_links+='<small>แผนที่ค้นหาจากที่อยู่ที่เผยแพร่ กรุณายืนยันจุดนัดหมายกับร้าน</small>'
        sources=[(lead['source'],'ข้อมูลบริการและติดต่อ')]+c.get('extra_sources',[])
        if facebook:sources.append((facebook,'Facebook'))
        source_html=''.join(link(u,label) for u,label in sources)
        body=f'''<body class="theme-{lead['cat']}" data-source-enriched="true">
<a class="skip" href="#main">ข้ามไปเนื้อหา</a><div class="notice">เว็บไซต์ตัวอย่าง · ไม่ใช่เว็บไซต์ทางการของธุรกิจ</div>
<nav aria-label="เมนูหลัก"><div class="wrap"><a class="brand" href="#main">{e(lead['name'])}</a><div class="menu"><a href="#services">บริการ</a><a href="#ideas">ภาพจากธุรกิจ</a><a href="#contact">ติดต่อ</a></div><a class="btn" href="#contact">สอบถามงาน ↗</a></div></nav>
<main id="main"><section class="hero"><div class="wrap hero-grid"><div><div class="eyebrow">{e(lead['name'])} / {e(lead['area'])}</div><h1>{c['title']}</h1><p class="intro">{e(c['intro'])}</p><div class="actions">{cta}{subcta}</div><p class="location">⌖ {e(address)}</p>{('<p class="contact-note">'+e(c['phone_note'])+'</p>') if c.get('phone_note') else ''}</div><div class="visual">{hero}</div></div></section>
<section class="section" id="services"><div class="wrap"><div class="section-head"><div><div class="eyebrow">บริการของ {e(lead['name'])}</div><h2>เลือกงานที่ต้องการสอบถาม</h2></div><p>ส่งรายละเอียดและรูปพื้นที่ เพื่อคุยขอบเขต วัสดุ และวันนัดกับผู้ให้บริการโดยตรง</p></div><div class="cards">{services}</div></div></section>
<section class="section samples" id="ideas"><div class="wrap"><div class="section-head"><div><div class="eyebrow">{e(lead['name'])}</div><h2>{'ภาพจากธุรกิจ' if photos else 'สอบถามตัวอย่างงาน'}</h2></div><p>{'ภาพที่ธุรกิจเผยแพร่บนเว็บไซต์หรือประกาศของตนเอง เปิดลิงก์ใต้ภาพเพื่อดูต้นทาง' if photos else 'ขอภาพงานที่ใกล้เคียงกับสิ่งที่คุณต้องการก่อนตกลงรายละเอียด'}</p></div>{gallery}{'<p class="photo-age">ภาพจากประกาศปี 2562 ใช้ดูแนวทางงาน กรุณาขอผลงานล่าสุดก่อนตัดสินใจ</p>' if slug=='greenery-landscape' else ''}</div></section>
<section class="section" id="brief"><div class="wrap"><div class="panel"><div><div class="eyebrow">เตรียมรายละเอียด</div><h2>คุยงานให้ตรง<br>ตั้งแต่ครั้งแรก</h2><p>ส่งข้อมูลให้ {e(lead['name'])} ประเมิน และตกลงราคา กำหนดงาน รวมถึงเงื่อนไขก่อนเริ่ม</p></div><div><ol class="brief-list">{''.join('<li>'+e(t)+'</li>' for t in c['brief'])}</ol><a class="btn" href="#contact">ติดต่อสอบถาม ↗</a></div></div></div></section>
<section class="section" id="contact"><div class="wrap"><div class="contact"><div><div class="eyebrow">ติดต่อ {e(lead['name'])}</div><h2>{e(lead['name'])}</h2><address>{e(address)}</address>{'<p>'+e(c['address_extra'])+'</p>' if c.get('address_extra') else ''}<p><strong>เวลาติดต่อ</strong><br>{e(c.get('hours','ยังไม่พบเวลาทำการที่เผยแพร่ กรุณาสอบถามก่อนเข้าพบ'))}</p>{'<p class="contact-note">'+e(c['phone_note'])+'</p>' if c.get('phone_note') else ''}{'<p class="contact-note">'+e(c['contact_note'])+'</p>' if c.get('contact_note') else ''}</div><div class="contact-links">{contact_links}</div></div><div class="source-info"><p>ข้อมูลและภาพจากแหล่งที่ธุรกิจเผยแพร่</p><div class="source-links">{source_html}</div><p class="photo-age">ตรวจข้อมูล 8 พฤศจิกายน 2569 · โปรดยืนยันราคา คิวงาน และรายละเอียดกับผู้ให้บริการ</p></div></div></section></main>
<footer class="footer"><div class="wrap"><span>{e(lead['name'])} · เว็บไซต์ตัวอย่าง</span><span><a href="../catalog.html">กลับคาตาล็อก ↗</a></span></div></footer><div class="mobile-cta">{cta}<a class="btn" href="#contact">ข้อมูลติดต่อ ↓</a></div></body>'''
        dest.write_text('<!DOCTYPE html><html lang="th">'+head+'\n'+body+'</html>\n',encoding='utf-8')
        status=c.get('status','enriched_with_source_photos' if photos else 'enriched_photos_unavailable')
        records=source_records(slug,lead,c)
        facts={'phones':c['phones'],'phone_note':c.get('phone_note'),'line_id':c.get('line'),'line_url':line_url or None,'address':c.get('address'),'area_only':c.get('area_only'),'address_extra':c.get('address_extra'),'hours':c.get('hours'),'email':c.get('email'),'maps_url':map_url,'map_kind':map_kind,'coordinates':c.get('coords'),'services':[s[0] for s in c['services']]}
        audit.append({'slug':slug,'category':lead['cat'],'name':lead['name'],'inspected_at':'2026-11-08','page_inspected':True,'body_marker':'data-source-enriched="true"','sources':records,'photos':[p['path'] for p in photos],'photo_provenance':photos,'photo_verified':bool(photos),'photo_verification_scope':'Identifiable source attribution and visual content, not independent authorship, licensing, freshness or business approval.','facts':facts,'fact_provenance':[{'fields':['services','phones','line_id','address','hours','coordinates'],'source':lead['source'],'qualification':'Only fields present in facts; see limitations for older, indexed or conflicting values.'}],'status':status,'limitations':c['limitations']})
        print(slug,status,len(photos),flush=True)
    (ROOT/'research/source-audit-second.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
