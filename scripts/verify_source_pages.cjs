// Browser verification and refreshed catalog previews for the 60 researched demos.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');
const root = path.resolve(__dirname, '..');
const leads = ['2026-11-07','2026-11-07-round-2'].flatMap(run =>
  JSON.parse(fs.readFileSync(path.join(root, 'research', run, 'leads.json'), 'utf8')).leads);
(async () => {
  const browser = await chromium.launch({channel:'msedge', headless:true});
  const failures = [], results = [];
  let next=0;
  try {
    await Promise.all(Array.from({length:4}, async () => {
      const page=await browser.newPage();
      page.on('pageerror', e => failures.push(e.message));
      while(next < leads.length) {
        const lead=leads[next++];
        try {
          await page.setViewportSize({width:1440,height:1000});
          const response=await page.goto(`http://127.0.0.1:8765/${lead.slug}/index.html`,{waitUntil:'load'});
          assert.equal(response.status(),200);
          await page.evaluate(() => document.fonts.ready);
          assert.equal(await page.locator('h1').count(),1);
          assert.equal(await page.locator('body').getAttribute('data-source-enriched'),'true','source enrichment missing');
          const text=await page.locator('body').innerText();
          if(lead.phone) assert.ok(text.replace(/[^0-9]/g,'').includes(lead.phone),'phone digits must be visible');
          const broken=await page.locator('img').evaluateAll(imgs=>imgs.filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.src));
          assert.deepEqual(broken,[],'broken images');
          await page.screenshot({path:path.join(root,'catalog-assets',lead.slug+'.jpg'),type:'jpeg',quality:82});
          for(const width of [390,768]) {
            await page.setViewportSize({width,height:844});
            assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`overflow at ${width}`);
            if(width===390) await page.screenshot({path:path.join(root,'catalog-assets',lead.slug+'-m.jpg'),type:'jpeg',quality:82});
          }
          results.push({slug:lead.slug,photos:await page.locator('img').count(),pass:true});
          console.log('PASS '+lead.slug);
        } catch(e) { failures.push(lead.slug+': '+e.message);console.log('FAIL '+lead.slug+': '+e.message); }
      }
      await page.close();
    }));
    const page=await browser.newPage();
    await page.goto('http://127.0.0.1:8765/catalog.html');
    assert.equal(await page.locator('.card').count(),101);
    console.log(JSON.stringify({checked:results.length,withPhotos:results.filter(r=>r.photos>0).length,failures},null,2));
    if(failures.length) process.exitCode=1;
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
