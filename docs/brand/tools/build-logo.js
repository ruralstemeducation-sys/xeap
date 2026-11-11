// Build SEPA logo variants from the Illustrator-exported SVG (page 2, blue on white).
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const [src, out] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const s = fs.readFileSync(src, 'utf8');
const glyph = {};
for (const m of s.matchAll(/<g id="(glyph-[\d-]+)">\s*<path d="([^"]*)"/g)) glyph[m[1]] = m[2].trim();
const uses = [...s.matchAll(/<use xlink:href="#(glyph-[\d-]+)" x="([\d.]+)" y="([\d.]+)"\/>/g)];
const r = n => +(+n).toFixed(3);
const textPaths = uses.filter(u => glyph[u[1]]).map(u => `<path transform="translate(${r(u[2])} ${r(u[3])})" d="${glyph[u[1]]}"/>`).join('');
const symPaths = [...s.matchAll(/<path fill-rule="nonzero"[^>]* d="([^"]*)"/g)].map(m => `<path d="${m[1].trim()}"/>`).join('');
// the "E" of "Education" = glyph-1-0 at baseline 471.4092
const eUse = uses.find(u => u[1] === 'glyph-1-0');

(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.setContent(`<svg xmlns="http://www.w3.org/2000/svg" width="900" height="900"><g id="s">${symPaths}</g><g id="t">${textPaths}</g><g id="e"><path transform="translate(${eUse[2]} ${eUse[3]})" d="${glyph['glyph-1-0']}"/></g></svg>`);
  const bb = await p.evaluate(() => Object.fromEntries(['s','t','e'].map(id => { const q = document.getElementById(id).getBBox(); return [id, {x:q.x,y:q.y,w:q.width,h:q.height}]; })));
  console.log(JSON.stringify(bb));
  const S = bb.s, T = bb.t, X = bb.e.h;
  const f = n => +n.toFixed(2);
  const layouts = {};
  // horizontal: original arrangement
  { const x0 = Math.min(S.x, T.x), y0 = Math.min(S.y, T.y), x1 = Math.max(S.x+S.w, T.x+T.w), y1 = Math.max(S.y+S.h, T.y+T.h);
    layouts.ngang = { vb: [x0, y0, x1-x0, y1-y0], body: `<g>${symPaths}</g><g>${textPaths}</g>` }; }
  // vertical: symbol above wordmark (proportions follow the designer's vertical artboard)
  { const k = 1.154 * T.w / S.w, gap = 0.1016 * T.w;
    const sw = S.w*k, sh = S.h*k, W = Math.max(sw, T.w);
    const sx = (W - sw)/2, tx = (W - T.w)/2, ty = sh + gap;
    layouts.doc = { vb: [0, 0, W, ty + T.h], body:
      `<g transform="translate(${f(sx - S.x*k)} ${f(-S.y*k)}) scale(${f(k*1e4)/1e4})">${symPaths}</g><g transform="translate(${f(tx - T.x)} ${f(ty - T.y)})">${textPaths}</g>` }; }
  layouts['bieu-tuong'] = { vb: [S.x, S.y, S.w, S.h], body: `<g>${symPaths}</g>` };
  const colors = { mau: '#253E93', trang: '#FFFFFF', den: '#000000' };
  const meta = {};
  for (const [ln, L] of Object.entries(layouts)) {
    const vb = L.vb.map(f);
    meta[ln] = { w: vb[2], h: vb[3] };
    for (const [cn, c] of Object.entries(colors)) {
      const name = `sepa-logo-${ln}-${cn}`;
      const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vb.join(' ')}" width="${vb[2]}" height="${vb[3]}"><title>SEPA – STEM Education Promotion Alliance</title><g fill="${c}">${L.body}</g></svg>\n`;
      fs.writeFileSync(path.join(out, name + '.svg'), svg);
      const W = ln === 'bieu-tuong' ? 2048 : 3000, scale = W / vb[2];
      const H = Math.round(vb[3] * scale);
      await p.setViewportSize({ width: W, height: H });
      await p.setContent(`<style>html,body{margin:0;background:transparent}</style><img src="data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}" style="display:block;width:${W}px;height:${H}px">`);
      await p.screenshot({ path: path.join(out, name + '.png'), omitBackground: true, clip: { x: 0, y: 0, width: W, height: H } });
    }
  }
  meta.X = X; meta.ngangSymbolH = S.h;
  fs.writeFileSync(path.join(out, '..', 'meta.json'), JSON.stringify(meta, null, 1));
  await b.close();
})();
