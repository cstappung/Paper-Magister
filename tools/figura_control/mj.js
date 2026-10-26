// Convierte una lista de LaTeX (JSON en argv[2]) a SVG de MathJax con glifos en linea.
const {mathjax} = require('mathjax-full/js/mathjax.js');
const {TeX} = require('mathjax-full/js/input/tex.js');
const {SVG} = require('mathjax-full/js/output/svg.js');
const {liteAdaptor} = require('mathjax-full/js/adaptors/liteAdaptor.js');
const {RegisterHTMLHandler} = require('mathjax-full/js/handlers/html.js');
const {AllPackages} = require('mathjax-full/js/input/tex/AllPackages.js');
const adaptor = liteAdaptor(); RegisterHTMLHandler(adaptor);
const doc = mathjax.document('', {InputJax: new TeX({packages: AllPackages}), OutputJax: new SVG({fontCache: 'none'})});
const items = JSON.parse(require('fs').readFileSync(process.argv[2],'utf8'));
const out = {};
for (const [k, tex] of Object.entries(items)) {
  const node = doc.convert(tex, {display: true});
  const svg = adaptor.firstChild(node);
  out[k] = {viewBox: adaptor.getAttribute(svg,'viewBox'), inner: adaptor.innerHTML(svg)};
}
process.stdout.write(JSON.stringify(out));
