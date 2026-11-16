#!/usr/bin/env node
// Dựng các site vệ tinh tĩnh từ bài viết trên sepa.org.vn.
// Chạy: node satellites/build.mjs [domain ...]   → kết quả ở satellites/dist/<domain>/
// Không cần thư viện ngoài (Node 18+).

import { readFile, writeFile, mkdir, rm, cp, access, readdir } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = dirname(fileURLToPath(import.meta.url));
const DIST = join(ROOT, 'dist');
const config = JSON.parse(await readFile(join(ROOT, 'sites.json'), 'utf8'));
const API = `${config.source.replace(/\/$/, '')}/wp-json/wp/v2`;
const HOME_COUNT = 12;
const MAX_POSTS = 300;

const T = {
  vi: { news: 'Tin tức', all: 'Xem tất cả tin', about: 'Giới thiệu', empty: 'Chưa có bài viết.',
        by: 'Một chương trình của', read: 'Đọc bài', notFound: 'Không tìm thấy trang',
        notFoundText: 'Trang bạn tìm có thể đã được chuyển sang website SEPA.', home: 'Về trang chủ',
        search: 'Tìm trên sepa.org.vn', locale: 'vi-VN' },
  en: { news: 'News', all: 'All news', about: 'About', empty: 'No posts yet.',
        by: 'A programme of', read: 'Read', notFound: 'Page not found',
        notFoundText: 'The page you are looking for may have moved to the SEPA website.', home: 'Back to home',
        search: 'Search sepa.org.vn', locale: 'en-GB' },
};

// ---------- Lấy dữ liệu ----------

async function getJSON(url, { allow404 = false } = {}) {
  for (let attempt = 1; ; attempt++) {
    const res = await fetch(url, { headers: { 'User-Agent': 'sepa-satellite-builder' } });
    if (allow404 && (res.status === 404 || res.status === 400)) return null;
    if (res.ok) return { data: await res.json(), totalPages: Number(res.headers.get('x-wp-totalpages') || 1) };
    if (attempt >= 3) throw new Error(`${res.status} ${url}`);
    await new Promise((r) => setTimeout(r, 2000 * attempt));
  }
}

async function fetchPosts(query) {
  const fields = 'id,date,modified,link,title,excerpt,_links,_embedded';
  const out = [];
  for (let page = 1; out.length < MAX_POSTS; page++) {
    const url = `${API}/posts?${query}&per_page=100&page=${page}&_embed=wp:featuredmedia&_fields=${fields}`;
    const res = await getJSON(url, { allow404: page > 1 });
    if (!res) break;
    out.push(...res.data);
    if (page >= res.totalPages) break;
  }
  return out;
}

// Taxonomy "Hiển thị trên site" (snippet 39). Chưa bật trên web thì bỏ qua.
let siteTermsCache;
async function siteTermId(slug) {
  if (siteTermsCache === undefined) {
    const res = await getJSON(`${API}/sepa_site?per_page=100&_fields=id,slug`, { allow404: true });
    siteTermsCache = res ? res.data : null;
  }
  return siteTermsCache?.find((t) => t.slug === slug)?.id;
}

async function postsForSite(site) {
  const f = site.filter || {};
  const queries = [];
  if (f.site) {
    const id = await siteTermId(f.site);
    if (id) queries.push(`sepa_site=${id}`);
  }
  if (f.categories?.length) queries.push(`categories=${f.categories.join(',')}`);
  if (f.tags?.length) queries.push(`tags=${f.tags.join(',')}`);

  const byId = new Map();
  for (const q of queries) for (const p of await fetchPosts(q)) byId.set(p.id, p);
  return [...byId.values()].sort((a, b) => b.date.localeCompare(a.date)).map(normalize);
}

function normalize(p) {
  const media = p._embedded?.['wp:featuredmedia']?.[0];
  const sizes = media?.media_details?.sizes || {};
  const img = sizes['sepa-card'] || sizes.medium_large || sizes.large || sizes.medium;
  return {
    id: p.id,
    date: p.date,
    modified: p.modified,
    link: p.link,
    title: p.title.rendered,
    excerpt: truncate(decode(stripTags(p.excerpt.rendered)), 220),
    image: img?.source_url || media?.source_url || '',
    imageAlt: media?.alt_text || '',
  };
}

// ---------- Tiện ích ----------

const stripTags = (s) => s.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
const decode = (s) => s
  .replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(+n))
  .replace(/&#x([0-9a-f]+);/gi, (_, n) => String.fromCodePoint(parseInt(n, 16)))
  .replace(/&nbsp;/g, ' ').replace(/&hellip;/g, '…').replace(/&quot;/g, '"')
  .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const truncate = (s, n) => {
  s = s.replace(/\s*(\[…\]|\[&hellip;\]|…)\s*$/, '');
  return s.length <= n ? s : s.slice(0, s.lastIndexOf(' ', n)) + '…';
};
const fmtDate = (iso, locale) => new Date(iso).toLocaleDateString(locale, { day: '2-digit', month: '2-digit', year: 'numeric' });
const exists = (p) => access(p).then(() => true, () => false);

// ---------- Giao diện ----------

function layout(site, { title, description, path, body }) {
  const t = T[site.lang];
  const url = `https://${site.domain}${path}`;
  const fullTitle = title ? `${title} | ${site.name}` : site.name;
  return `<!doctype html>
<html lang="${site.lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(fullTitle)}</title>
<meta name="description" content="${esc(description || site.tagline)}">
<link rel="canonical" href="${url}">
<meta property="og:type" content="website">
<meta property="og:title" content="${esc(fullTitle)}">
<meta property="og:description" content="${esc(description || site.tagline)}">
<meta property="og:url" content="${url}">
${site.ogImage ? `<meta property="og:image" content="${esc(site.ogImage)}">` : ''}
<link rel="alternate" type="application/rss+xml" title="${esc(site.name)}" href="/feed.xml">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/style.css">
<style>:root{--brand:${site.color}}</style>
</head>
<body>
<header class="top"><div class="wrap">
  <a class="brand" href="/">${esc(site.name)}</a>
  <nav><a href="/tin-tuc/">${t.news}</a>${site.hasAbout ? `<a href="/gioi-thieu/">${t.about}</a>` : ''}</nav>
</div></header>
<main>
${body}
</main>
<footer class="foot"><div class="wrap">
  <p><strong>${esc(site.name)}</strong> · ${t.by} <a href="https://sepa.org.vn/">SEPA – Liên minh Thúc đẩy Giáo dục STEM</a></p>
</div></footer>
</body>
</html>
`;
}

function card(p, t) {
  return `<article class="card">
  <a href="${esc(p.link)}" class="thumb">${p.image
    ? `<img src="${esc(p.image)}" alt="${esc(p.imageAlt)}" loading="lazy" decoding="async">`
    : '<span class="noimg"></span>'}</a>
  <div class="body">
    <time datetime="${p.date}">${fmtDate(p.date, t.locale)}</time>
    <h3><a href="${esc(p.link)}">${p.title}</a></h3>
    <p>${esc(p.excerpt)}</p>
  </div>
</article>`;
}

const grid = (posts, t) => posts.length
  ? `<div class="grid">\n${posts.map((p) => card(p, t)).join('\n')}\n</div>`
  : `<p class="empty">${t.empty}</p>`;

function favicon(site) {
  const letter = esc(site.name.trim()[0].toUpperCase());
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="${site.color}"/><text x="32" y="44" font-family="Arial,sans-serif" font-size="34" font-weight="700" fill="#fff" text-anchor="middle">${letter}</text></svg>\n`;
}

function rss(site, posts) {
  const items = posts.slice(0, 30).map((p) => `<item><title>${esc(decode(p.title))}</title><link>${esc(p.link)}</link><guid>${esc(p.link)}</guid><pubDate>${new Date(p.date).toUTCString()}</pubDate><description>${esc(p.excerpt)}</description></item>`).join('\n');
  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>${esc(site.name)}</title><link>https://${site.domain}/</link><description>${esc(site.tagline)}</description><language>${site.lang}</language>
${items}
</channel></rss>
`;
}

// ---------- Dựng từng site ----------

async function write(dir, file, content) {
  const p = join(dir, file);
  await mkdir(dirname(p), { recursive: true });
  await writeFile(p, content);
}

async function buildRedirect(site, dir) {
  const to = site.to.replace(/\/$/, '');
  await write(dir, '_redirects', `/* ${to}/:splat 301\n`);
  await write(dir, 'index.html', `<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=${to}/"><link rel="canonical" href="${to}/"><a href="${to}/">${to}</a>\n`);
  console.log(`✓ ${site.domain} → chuyển hướng ${to}`);
}

// Site có giao diện riêng: content/<domain>/shell.html + pages/*.html (+ news-card.html, extra.css)
// Mỗi trang mở đầu bằng <!--meta {"title": "...", "description": "..."} -->.
// Trang là tài liệu HTML đầy đủ (có <!doctype>) giữ nguyên; trang chỉ có nội dung thì bọc trong shell.html.
// Chỗ {{news:6}} / {{news:all}} được thay bằng thẻ tin lấy từ sepa.org.vn.
async function buildCustom(site, dir, contentDir) {
  const t = T[site.lang];
  const posts = await postsForSite(site);
  const shell = await readFile(join(contentDir, 'shell.html'), 'utf8');
  const cardTpl = (await exists(join(contentDir, 'news-card.html'))) ? (await readFile(join(contentDir, 'news-card.html'), 'utf8')).trim() : null;
  const extraCss = (await exists(join(contentDir, 'extra.css'))) ? await readFile(join(contentDir, 'extra.css'), 'utf8') : '';
  const fill = (tpl, map) => tpl.replace(/\{\{(\w+)\}\}/g, (m, k) => (k in map ? map[k] : m));

  const newsHtml = (n) => {
    const list = n === 'all' ? posts : posts.slice(0, Number(n));
    if (!list.length) return `<p class="empty">${t.empty}</p>`;
    if (!cardTpl) return grid(list, t);
    return `<div class="${site.newsGrid || 'vrc-news-grid'}">\n` + list.map((p) => fill(cardTpl, {
      link: esc(p.link), title: p.title, excerpt: esc(p.excerpt), iso: p.date, date: fmtDate(p.date, t.locale),
      imageTag: p.image ? `<img src="${esc(p.image)}" alt="${esc(p.imageAlt)}" loading="lazy" decoding="async">` : '<span class="sat-noimg"></span>',
    })).join('\n') + '\n</div>';
  };

  const headExtra = (path, title, desc) => [
    `<link rel="canonical" href="https://${site.domain}${path}">`,
    `<meta property="og:type" content="website">`,
    `<meta property="og:title" content="${esc(title)}">`,
    `<meta property="og:description" content="${esc(desc)}">`,
    `<meta property="og:url" content="https://${site.domain}${path}">`,
    `<link rel="icon" href="/favicon.svg" type="image/svg+xml">`,
    `<link rel="alternate" type="application/rss+xml" title="${esc(site.name)}" href="/feed.xml">`,
    extraCss ? `<style>${extraCss}</style>` : '',
  ].filter(Boolean).join('\n');

  const render = (raw, path) => {
    const m = raw.match(/^<!--meta (\{.*?\}) -->\s*/);
    const meta = m ? JSON.parse(m[1]) : {};
    let body = m ? raw.slice(m[0].length) : raw;
    body = body.replace(/\{\{news:(\d+|all)\}\}/g, (_, n) => newsHtml(n));
    const title = meta.title ? `${meta.title} | ${site.name}` : `${site.name} 2026–2027`;
    const desc = meta.description || site.tagline;
    if (/^\s*<!doctype/i.test(body)) {
      if (!/<meta name="description"/.test(body)) body = body.replace('</head>', `<meta name="description" content="${esc(desc)}">\n</head>`);
      return body.replace('</head>', headExtra(path, title, desc) + '\n</head>');
    }
    return fill(shell, { title: esc(title), description: esc(desc), head: headExtra(path, title, desc), content: body });
  };

  const urls = [];
  const pagesDir = join(contentDir, 'pages');
  for (const f of (await readdir(pagesDir)).filter((f) => f.endsWith('.html')).sort()) {
    const slug = f.replace(/\.html$/, '');
    const path = slug === 'home' ? '/' : `/${slug}/`;
    await write(dir, slug === 'home' ? 'index.html' : `${slug}/index.html`, render(await readFile(join(pagesDir, f), 'utf8'), path));
    urls.push(path);
  }
  await write(dir, '404.html', render(`<!--meta {"title": "${t.notFound}"} -->
<section class="vrc-page-hero"><div class="vrc-container"><h1>${t.notFound}</h1><p>${t.notFoundText}</p></div></section>
<section class="vrc-section"><div class="vrc-container"><a class="vrc-btn vrc-btn--primary" href="/">${t.home}</a></div></section>`, '/404'));

  await writeCommon(site, dir, contentDir, urls, posts);
  console.log(`✓ ${site.domain}: ${urls.length} trang, ${posts.length} bài (giao diện riêng)`);
}

async function writeCommon(site, dir, contentDir, urls, posts) {
  const today = new Date().toISOString().slice(0, 10);
  await write(dir, 'sitemap.xml', `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map((u) => `<url><loc>https://${site.domain}${u}</loc><lastmod>${today}</lastmod></url>`).join('\n')}
</urlset>
`);
  await write(dir, 'robots.txt', `User-agent: *\nAllow: /\nSitemap: https://${site.domain}/sitemap.xml\n`);
  await write(dir, 'feed.xml', rss(site, posts));
  await write(dir, 'favicon.svg', favicon(site));
  await cp(join(ROOT, 'template', '_headers'), join(dir, '_headers'));
  const redirectsFile = join(contentDir, '_redirects');
  if (await exists(redirectsFile)) await cp(redirectsFile, join(dir, '_redirects'));
}

async function buildNews(site, dir) {
  const t = T[site.lang];
  const contentDir = join(ROOT, 'content', site.domain);
  if (await exists(join(contentDir, 'shell.html'))) return buildCustom(site, dir, contentDir);
  const aboutFile = join(contentDir, 'gioi-thieu.html');
  const introFile = join(contentDir, 'intro.html');
  site.hasAbout = await exists(aboutFile);
  const intro = (await exists(introFile)) ? await readFile(introFile, 'utf8') : '';

  const posts = await postsForSite(site);

  // Trang chủ
  await write(dir, 'index.html', layout(site, { path: '/', body: `
<section class="hero"><div class="wrap">
  <h1>${esc(site.name)}</h1>
  <p class="tagline">${esc(site.tagline)}</p>
  ${intro}
</div></section>
<section class="wrap list">
  <h2>${t.news}</h2>
  ${grid(posts.slice(0, HOME_COUNT), t)}
  ${posts.length > HOME_COUNT ? `<p class="more"><a class="btn" href="/tin-tuc/">${t.all}</a></p>` : ''}
</section>` }));

  // Toàn bộ tin
  await write(dir, 'tin-tuc/index.html', layout(site, { title: t.news, path: '/tin-tuc/', body: `
<section class="wrap list">
  <h1>${t.news}</h1>
  ${grid(posts, t)}
</section>` }));

  // Giới thiệu (nếu có file content/<domain>/gioi-thieu.html)
  if (site.hasAbout) {
    await write(dir, 'gioi-thieu/index.html', layout(site, { title: t.about, path: '/gioi-thieu/', body: `
<section class="wrap prose">
  <h1>${t.about}</h1>
  ${await readFile(aboutFile, 'utf8')}
</section>` }));
  }

  // 404: đường dẫn cũ của WordPress
  await write(dir, '404.html', layout(site, { title: t.notFound, path: '/404', body: `
<section class="wrap prose center">
  <h1>${t.notFound}</h1>
  <p>${t.notFoundText}</p>
  <p><a class="btn" href="/">${t.home}</a> <a class="btn ghost" href="https://sepa.org.vn/?s=">${t.search}</a></p>
</section>` }));

  const urls = ['/', '/tin-tuc/', ...(site.hasAbout ? ['/gioi-thieu/'] : [])];
  await cp(join(ROOT, 'template', 'style.css'), join(dir, 'style.css'));
  // sitemap, RSS, favicon, _headers, _redirects (vd. bài cũ trên WordPress → bài trên sepa)
  await writeCommon(site, dir, contentDir, urls, posts);

  console.log(`✓ ${site.domain}: ${posts.length} bài`);
}

const only = process.argv.slice(2);
const sites = config.sites.filter((s) => !only.length || only.includes(s.domain));
if (!sites.length) throw new Error(`Không có site nào khớp: ${only.join(', ')}`);

for (const site of sites) {
  const dir = join(DIST, site.domain);
  await rm(dir, { recursive: true, force: true });
  await mkdir(dir, { recursive: true });
  if (site.type === 'redirect') await buildRedirect(site, dir);
  else await buildNews(site, dir);
}
