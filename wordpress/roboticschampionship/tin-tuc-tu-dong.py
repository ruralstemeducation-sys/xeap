"""Trang Tin tức của roboticschampionship.vn tự lấy bài từ sepa.org.vn (chuyên mục Robotics) mỗi lần có người mở trang."""
# Cài lại: RC_AUTH="robotics:<mật khẩu ứng dụng>" python3 tin-tuc-tu-dong.py --write   (không lưu mật khẩu vào repo)
import json, os, sys, base64, time, urllib.request, html

API = 'https://sepa.org.vn/wp-json/wp/v2/posts?categories=186,411&per_page=12&_embed=wp:featuredmedia&_fields=id,date,link,title,excerpt,_links,_embedded'

# Bản dự phòng hiển thị sẵn (khi trình duyệt chặn script hoặc sepa không phản hồi) – lấy bài mới nhất lúc cài
req = urllib.request.Request(API, headers={'User-Agent': 'sepa-maint'})
posts = json.loads(urllib.request.urlopen(req, timeout=60).read().decode())[:6]

def strip(s):
    import re
    return html.unescape(re.sub(r'<[^>]+>', ' ', s)).replace('[…]', '').strip()

def card(p):
    m = (p.get('_embedded') or {}).get('wp:featuredmedia') or [{}]
    sizes = (m[0].get('media_details') or {}).get('sizes') or {}
    img = (sizes.get('sepa-card') or sizes.get('medium_large') or sizes.get('large') or {}).get('source_url') or m[0].get('source_url') or ''
    d = p['date'][:10]; d = f'{d[8:10]}/{d[5:7]}/{d[0:4]}'
    ex = strip(p['excerpt']['rendered']); ex = ex[:200].rsplit(' ', 1)[0] + '…' if len(ex) > 200 else ex
    t = html.escape(strip(p['title']['rendered'])); link = html.escape(p['link'])
    im = f'<img src="{html.escape(img)}" alt="" loading="lazy">' if img else '<span class="noimg"></span>'
    return f'<article class="nc"><a class="th" href="{link}">{im}</a><div class="bd"><time>{d}</time><h3><a href="{link}">{t}</a></h3><p>{html.escape(ex)}</p><a class="more" href="{link}">Đọc tiếp →</a></div></article>'

CSS = '''<style>
.vrcn{max-width:1180px;margin:0 auto;padding:8px 20px 72px;color:#10233e;font-size:17px;line-height:1.6}
.vrcn .lead{color:#667085;margin:0 0 28px;font-size:1.1rem}
.vrcn .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:22px}
.vrcn .nc{border:1px solid #dce5ef;border-radius:18px;background:#fff;overflow:hidden;box-shadow:0 10px 28px rgba(6,47,105,.06);display:flex;flex-direction:column}
.vrcn .th{display:block;aspect-ratio:16/9;background:#e8eef6}
.vrcn .th img{width:100%;height:100%;object-fit:cover;display:block}
.vrcn .noimg{display:block;height:100%;background:linear-gradient(135deg,#041d42,#0a407f)}
.vrcn .bd{padding:18px 20px 22px}
.vrcn time{font-size:.74rem;color:#ef0017;font-weight:800;letter-spacing:.06em}
.vrcn h3{color:#062f69;line-height:1.3;margin:6px 0 8px;font-size:1.12rem}
.vrcn h3 a{color:inherit;text-decoration:none}
.vrcn p{color:#667085;margin:0;font-size:.95rem;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.vrcn .more{display:inline-block;margin-top:12px;color:#c80016;font-weight:800;text-decoration:none}
.vrcn .foot{margin-top:28px}
.vrcn .foot a{color:#c80016}
</style>'''

JS = r'''<script>
(function () {
  var grid = document.getElementById('vrcn-grid');
  if (!grid || !window.fetch) return;
  var API = '%s';
  function txt(h) { var d = document.createElement('div'); d.innerHTML = h || ''; return (d.textContent || '').replace(/\[…\]|\[&hellip;\]/g, '').trim(); }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text) e.textContent = text; return e; }
  function card(p) {
    var m = (p._embedded && p._embedded['wp:featuredmedia'] && p._embedded['wp:featuredmedia'][0]) || {};
    var s = (m.media_details && m.media_details.sizes) || {};
    var img = (s['sepa-card'] || s.medium_large || s.large || {}).source_url || m.source_url || '';
    var a = el('article', 'nc'), th = el('a', 'th'); th.href = p.link;
    if (img) { var i = el('img'); i.src = img; i.alt = ''; i.loading = 'lazy'; th.appendChild(i); } else th.appendChild(el('span', 'noimg'));
    var bd = el('div', 'bd'), dt = p.date.slice(0, 10).split('-');
    bd.appendChild(el('time', '', dt[2] + '/' + dt[1] + '/' + dt[0]));
    var h = el('h3'), ha = el('a', '', txt(p.title.rendered)); ha.href = p.link; h.appendChild(ha); bd.appendChild(h);
    var ex = txt(p.excerpt.rendered); if (ex.length > 200) ex = ex.slice(0, ex.lastIndexOf(' ', 200)) + '…';
    bd.appendChild(el('p', '', ex));
    var mo = el('a', 'more', 'Đọc tiếp →'); mo.href = p.link; bd.appendChild(mo);
    a.appendChild(th); a.appendChild(bd); return a;
  }
  fetch(API, { credentials: 'omit' }).then(function (r) { return r.ok ? r.json() : null; }).then(function (ps) {
    if (!ps || !ps.length) return;
    grid.innerHTML = '';
    ps.forEach(function (p) { grid.appendChild(card(p)); });
  }).catch(function () {});
})();
</script>''' % API

content = ('<!-- wp:html -->\n' + CSS + '\n<div class="vrcn">\n<p class="lead">Tin mới nhất về Giải Vô địch Robotics Việt Nam 2026–2027, tự động cập nhật từ SEPA.</p>\n'
           '<div class="grid" id="vrcn-grid">\n' + '\n'.join(card(p) for p in posts) + '\n</div>\n'
           '<p class="foot">Xem thêm tin robotics tại <a href="https://sepa.org.vn/category/tin-tuc-vi/robotics">sepa.org.vn</a>.</p>\n</div>\n' + JS + '\n<!-- /wp:html -->')

if '--write' in sys.argv:
    auth = 'Basic ' + base64.b64encode(os.environ['RC_AUTH'].encode()).decode()
    for i in range(5):
        try:
            r = urllib.request.Request('https://roboticschampionship.vn/wp-json/wp/v2/pages/22', data=json.dumps({'content': content}).encode(), method='POST',
                                       headers={'Authorization': auth, 'Content-Type': 'application/json', 'User-Agent': 'sepa-maint'})
            with urllib.request.urlopen(r, timeout=90) as resp:
                print('OK', json.load(resp)['link']); break
        except urllib.error.HTTPError as e:
            print('HTTP', e.code, e.read()[:300]); raise
        except Exception as e:
            print('retry', e); time.sleep(4)
else:
    print(len(content), 'chars;', len(posts), 'fallback posts')
