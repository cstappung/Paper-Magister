// Pasa figuras/setup/setup-export.svg a PNG (x2) y PDF con Chromium.
// Uso: node tools/figura_setup/render.js
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const dir = path.join(__dirname, '..', '..', 'figuras', 'setup');
  const svg = fs.readFileSync(path.join(dir, 'setup-export.svg'), 'utf8');
  const W = parseInt(svg.match(/width="(\d+)"/)[1], 10);
  const H = parseInt(svg.match(/height="(\d+)"/)[1], 10);
  const html = `<html><body style="margin:0">${svg}</body></html>`;
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: W, height: H }, deviceScaleFactor: 2 });
  await page.setContent(html);
  await page.screenshot({ path: path.join(dir, 'setup.png'),
    clip: { x: 0, y: 0, width: W, height: H } });
  await page.pdf({ path: path.join(dir, 'setup.pdf'),
    width: `${W}px`, height: `${H}px`, printBackground: true,
    pageRanges: '1' });
  await browser.close();
  console.log('ok');
})();
