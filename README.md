# builder — Website demos for SME pitches

Source-enriched pages are marked with `data-source-enriched="true"`. The two
legacy demo builders preserve those pages instead of replacing researched contact
details and photos with category templates. Source audits live in
`research/source-audit-*.json`; they distinguish fetched business sources from
unavailable sources and document photo provenance. A link to a source is not
evidence that every image on that source belongs to the business: directory
recommendations must be excluded.

After editing enriched pages, run `python scripts/refresh_source_catalog.py` and
`node scripts/verify_source_pages.cjs` with `PLAYWRIGHT_MODULE_PATH` pointing to
Playwright and a local server on port 8765. The latter checks visible contact
numbers, image loading, desktop/mobile layouts, and refreshes catalog screenshots.

**Start here: open `catalog.html`** — a catalog of every demo with live preview.

Single-file HTML homepage demos (Noto Sans Thai headings, Sarabun body) made to pitch websites to small Thai businesses. Open `<folder>/index.html` in a browser.

| Folder | Business | Area | Note |
|---|---|---|---|
| `rubberpu4u` | แร้วแต่ปุ๊ Tyres | วงศ์สว่าง บางซื่อ | Tyres, suspension, brakes |
| `chanaphai-air` | ชนะภัยแอร์ | ร่มเกล้า มีนบุรี | Aircon cleaning: prices, area, warranty |
| `jaroon-air` | Jaroon AIR Repair and service | กทม. / นนทบุรี / ปทุมธานี | Business not found online; lead data only |
| `neat-tidy` | Neat & Tidy Cleaning Service | กทม.–ปริมณฑล | Business not found online; lead data only |
| `kept-sofa` | KEPT by กล้ากิจจ์ กรุ๊ป | บางแค | Sofa-cleaning campaign landing page |
| `zebra-detailing` | ZEBRA Car & Detailing | ปากเกร็ด นนทบุรี | Coating / film / detailing packages |
| `pat-carcare` | P.A.T CAR CARE Service | ลาดพร้าว 71 / นาคนิวาส | Neighbourhood car care |
| `perfectgirl-bkk` | PerfectGirl BKK | ประเสริฐมนูกิจ 39 | Nails & lashes |
| `exclusive-nails` | Exclusive nails studio | บรมราชชนนี / ปิ่นเกล้า | Nails & lashes |
| `changprapa` | ช่างประปา (changprapa) | กทม. | Plumbing by symptom |
| `tt-service-nonthaburi` | TT Service Nonthaburi | นนทบุรี | "ช่างประปานนทบุรี" landing page |
| `arichi-pet-salon` | Arichi pet salon | โยธินพัฒนา 3 | Pet grooming: house rules, checklist, LINE booking |
| `meerak-grooming` | โรงพยาบาลสัตว์มีรัก (grooming) | เมืองทองธานี | Grooming-only page of a vet hospital |
| `flower-stylist` | Flower Stylist | พระราม 3–นราธิวาสฯ | Wreaths & garlands with order builder |
| `you-deserve-flowers` | You Deserve Flowers | รามอินทรา 40 | Bouquets by occasion × budget |
| `cartoon-cake` | Cartoon Cake พระราม 2 | พระราม 2 ซ.43 | Cake gallery by theme + LINE order builder |
| `maysa-bakehome` | Maysa.Bakehome | ลาดกระบัง | Home bakery & café, LINE ordering |
| `mafueang-carcare` | มะเฟืองคาร์แคร์ | ร่มเกล้า มีนบุรี | Seat & carpet cleaning |
| `zebra-interior` | ZEBRA · ดูแลภายในรถ | ปากเกร็ด | 2nd ZEBRA page: interior-care packages |
| `be-my-craft` | Be My Craft By Kru Kate | ลาดกระบัง | Corporate workshop catalog + quote builder |
| `bougainvillea-soap` | Bougainvillea Soap | ตลิ่งชัน | Soap-making course comparison |
| `pornasarin-curtain` | พรอัสรินทร์ดีไซน์ | อ้อมน้อย กระทุ่มแบน | Curtains: window-size sender with live curtain preview |
| `sp-lucky-curtain` | ผ้าม่าน S.P lucky design | ซ.กำนันแม้น กทม. | Curtains: real jobs filtered by style × tone |
| `ntchemical-termite` | Ntchemical กำจัดปลวก | ธัญบุรี ปทุมธานี | Termite control: method quiz + annual-visit calendar |
| `pp-services-termite` | PP Services กำจัดปลวก | ประชาอุทิศ 90 | Termite control: tappable house cross-section |
| `noppon-transport` | นพพรขนส่ง | รังสิต–ลำลูกกา–ดอนเมือง | Movers: vehicle-by-load picker, furniture assembly |
| `carmove-setthawut` | CARMOVE เศรษฐวุฒิ | ลาดกระบัง | Movers: dorm move vs booth quote builder, job log |
| `chang-u-washer` | ช่างยู ล้างเครื่องซักผ้า | กทม.–ปริมณฑล | Washer cleaning: before/after slider, machine picker |
| `nong-kul-service` | น้องกุล ล้าง ซ่อม เครื่องซักผ้า | ปทุมธานี–นนทบุรี | Washer repair: area checker, coin-op section |
| `praipom-makeup` | ปลายผม แต่งหน้า | ศาลายา | Makeup: look picker + start-time planner |
| `panda-aui-makeup` | Panda Aui | สมุทรปราการ | Bridal hair & makeup: lookbook + wedding-day timeline |
| `pconscape` | PCONSCAPE | กทม. | Graduation photographer: package comparator, film-strip gallery |
| `panwadee-photography` | Panwadee Photography | กทม.–รังสิต | Graduation photographer: rehearsal + day planner |
| `tham-massage` | ธรรม นวดเพื่อสุขภาพ | บางบัวทอง | Thai massage: real 11-course prices, course picker |
| `chorcher-massage` | ฌ.เฌอ นวดเพื่อสุขภาพ | บิ๊กซี ลาดพร้าว | Massage & grey-hair plucking estimator, mall map |
| `est1981-barberclub` | Est.1981 Barberclub | ลำลูกกาคลองสอง | Barber: style → barber → time booking ticket |
| `oldhead-studio` | Oldhead Studio | ศาลายา | Hair studio: "we've moved" banner, lookbook |
| `kitchen-twobaby` | Kitchen_Twobaby | พระราม 2 | Snack box: budget-per-head set builder for corporate buyers |
| `onemore-homemade` | ONE MORE Homemade | อารีย์ | Snack box vs food-support order builder |
| `siam-sneaker-care` | Siam Sneaker Care | บางพลี | Brand-name shoe & bag spa: mail-in steps, estimate helper |
| `pjt-shoe-spa` | PJT บ้านสปารองเท้า | เมืองนครปฐม | Shoe spa + laundry: live open/closed sign |

Content that could not be verified (some prices, reviews, portfolio photos) is marked on each page as demo sample content.

Prompts used: `PROMPT_RESEARCH.md` (lead research), `PROMPT_CREATE_WEB.md` (site build).

## Research and concepts — 7 November 2026

Added **30 exploratory homepage concepts in 6 new categories**, five businesses each: metalwork, glass/aluminium, sofa repair, signage, CCTV, and gardening. This batch expanded the catalog from 41 to 71 pages.

**0 of the 30 candidates passed every research gate.** Recent activity could not be verified to the required standard. These concepts are not a qualified sales list. Some candidates have existing service sites and remain excluded until a concrete additional need is established. No business was contacted.

- [Research dashboard](research/2026-11-07/index.html)
- [Thai research report, limitations, provisional scores, and verification priorities](research/2026-11-07/REPORT.md)
- [Structured candidate data](research/2026-11-07/leads.json)

The new pages use original SVG illustrations, not shop portfolio photos. Their proposed palettes have not been verified against Facebook branding. Unverified prices, testimonials, customer counts, and booking availability are omitted. Map links are searches rather than verified pins. Contact details must be reconfirmed before outreach.

Regenerate this batch with `python scripts/build_research_demos.py`. Serve locally with `python -m http.server 8765 --bind 127.0.0.1`, then open `http://127.0.0.1:8765/catalog.html`.

## Research and concepts — round two, 7 November 2026

Added another **30 new businesses across 6 categories**, five each: dress rental, tattoo studios, yoga/pilates studios, computer repair, locksmiths, and music instruction. The catalog now contains **101 pages**.

Research finished before the homepage build. **0/30 candidates met every required evidence gate**: directory dates sometimes conflict with search excerpts, and recent activity could not be confirmed on first-party channels. There are 28 reserves and 2 excluded candidates; all 30 demos are explicitly exploratory concepts. No businesses were contacted.

- [Round-two research dashboard with category and text filters](research/2026-11-07-round-2/index.html)
- [Thai research report, dated observations, source links, scores, and limits](research/2026-11-07-round-2/REPORT.md)
- [Structured round-two research data](research/2026-11-07-round-2/leads.json)

Run `python scripts/research_round2.py` to regenerate the report, then `python scripts/build_round2_demos.py` for the websites. These builders preserve both catalog batches. Demos use original SVG artwork and proposed palettes; they do not reuse student videos or claim unverified shop prices, reviews, or availability.

Browser QA uses `scripts/verify_research_demos.cjs` with Playwright installed in an external tooling directory. Set `PLAYWRIGHT_MODULE_PATH` to that Playwright module and, if needed, `QA_BROWSER_EXECUTABLE` to an installed Chromium executable. Set `RESEARCH_PATH=research/2026-11-07-round-2` to verify the second batch; the default verifies the first batch. The script checks desktop/mobile pages and interactions and refreshes their catalog screenshots. A local server at port 8765 must be running.
