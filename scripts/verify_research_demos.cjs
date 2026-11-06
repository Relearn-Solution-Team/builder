// Optional local QA: npm install --no-save --prefix <temporary-dir> playwright
// Set PLAYWRIGHT_MODULE_PATH to that directory's node_modules/playwright.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(root, 'research/2026-11-07/leads.json'), 'utf8'));
const base = process.env.DEMO_BASE_URL || 'http://127.0.0.1:8765';

(async () => {
  const browser = await chromium.launch({headless: true, ...(process.env.QA_BROWSER_EXECUTABLE ? {executablePath: process.env.QA_BROWSER_EXECUTABLE} : {})});
  try {
    assert.equal(data.leads.length, 30);
    const counts = Object.values(data.leads.reduce((m, x) => (m[x.cat] = (m[x.cat] || 0) + 1, m), {}));
    assert.equal(counts.length, 6); assert.ok(counts.every(n => n === 5));
    const errors = [];
    // Bounded workers test every page at both actual viewports.
    let next = 0;
    await Promise.all(Array.from({length: 3}, async () => {
      const page = await browser.newPage();
      page.on('pageerror', error => errors.push(error.message));
      for (;;) {
        const lead = data.leads[next++]; if (!lead) break;
        await page.setViewportSize({width:1440,height:1000});
        const response = await page.goto(`${base}/${lead.slug}/index.html`, {waitUntil:'networkidle'});
        assert.equal(response.status(), 200, lead.slug);
        await page.evaluate(() => document.fonts.ready);
        assert.equal(await page.locator('h1').count(), 1);
        assert.ok((await page.locator('body').innerText()).includes('ไม่ใช่เว็บไซต์ทางการ'));
        assert.equal(await page.locator('meta[name=robots]').getAttribute('content'), 'noindex,nofollow');
        assert.ok(await page.locator('h1').evaluate(el => getComputedStyle(el).fontFamily.includes('Noto Sans Thai')));
        assert.ok(await page.locator('body').evaluate(el => getComputedStyle(el).fontFamily.includes('Sarabun')));
        for (const link of await page.locator('a[href^="#"]').evaluateAll(els => els.map(el => el.getAttribute('href')))) {
          assert.ok(await page.locator(link).count(), `${lead.slug}: missing ${link}`);
        }
        for (const href of await page.locator('a[href^="tel:"]').evaluateAll(els => els.map(el=>el.getAttribute('href')))) {
          assert.equal(href, `tel:${lead.phone}`);
        }
        if (lead.slug === data.leads[0].slug) {
          await page.evaluate(() => {Object.defineProperty(navigator, 'clipboard', {configurable:true,value:undefined});});
          await page.locator('#copy').click();
          assert.equal(await page.locator('#copy-fallback').isVisible(), true);
          assert.ok((await page.locator('#copy-fallback').inputValue()).includes('พื้นที่: [ระบุ]'));
        }
        // Return to the hero after interaction checks.
        await page.evaluate(() => scrollTo({top:0,behavior:'instant'}));
        await page.screenshot({path:path.join(root,'catalog-assets',`${lead.slug}.jpg`),type:'jpeg',quality:82});
        await page.setViewportSize({width:390,height:844});
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1);
        assert.equal(overflow,false,`${lead.slug}: mobile overflow`);
        await page.screenshot({path:path.join(root,'catalog-assets',`${lead.slug}-m.jpg`),type:'jpeg',quality:82});
        console.log(`PASS ${lead.slug}: desktop + mobile`);
      }
      await page.close();
    }));
    const page = await browser.newPage({viewport:{width:1440,height:1000}});
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(`${base}/catalog.html`,{waitUntil:'networkidle'});
    assert.equal(await page.locator('.card').count(),71);
    await page.locator('[data-cat="metal"].chip').click();
    assert.equal(await page.locator('.group:not(.hide) .card').count(),5);
    await page.locator('#q').fill('ส.วุฒิกร');
    assert.equal(await page.locator('.group:not(.hide) .card:not(.hide)').count(),1);
    await page.locator('[data-preview="wuttikorn-metal"]').first().click();
    assert.ok((await page.locator('#ifr').getAttribute('src')).includes('wuttikorn-metal'));
    await page.keyboard.press('Escape');
    assert.ok(!(await page.locator('#modal').getAttribute('class')).includes('on'));
    await page.setViewportSize({width:390,height:844});
    await page.locator('[data-preview="wuttikorn-metal"]').first().click();
    await page.locator('#mseg button[data-mode="m"]').click();
    const frameBox = await page.locator('#frame').boundingBox();
    assert.ok(frameBox.x >= 0 && frameBox.x + frameBox.width <= 391, 'mobile preview fits viewport');
    await page.keyboard.press('Escape');
    const brokenImages = await page.locator('img').evaluateAll(images => images.filter(img => img.complete && img.naturalWidth === 0).map(img=>img.src));
    assert.deepEqual(brokenImages, []);
    const reportResponse=await page.goto(`${base}/research/2026-11-07/index.html`,{waitUntil:'networkidle'});
    assert.equal(reportResponse.status(),200);
    assert.equal(await page.locator('article').count(),30);
    await page.setViewportSize({width:390,height:844});
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
    assert.deepEqual(errors,[]);
    console.log('PASS catalog count/filter/search/preview/Escape, research dashboard, and zero browser errors.');
  } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
