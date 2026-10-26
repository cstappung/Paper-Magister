const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
(async () => {
  const [,, inp, out, w, h] = process.argv;
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' + '-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: +(process.argv[6]||1) });
  const svg = fs.readFileSync(inp, 'utf8');
  await p.setContent(`<html><body style="margin:0;background:#fff">${svg.replace(/<\?xml[^>]*>/,'')}</body></html>`);
  await p.evaluate(()=>{const s=document.querySelector('svg'); s.setAttribute('width','100%'); s.removeAttribute('height');});
  await p.screenshot({ path: out, timeout: 120000, animations: 'disabled' });
  await b.close();
})();
