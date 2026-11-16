#!/usr/bin/env python3
"""Chuyển các trang WordPress của roboticschampionship.vn (bản sao lưu) sang trang tĩnh.

Chạy một lần:  python3 satellites/tools/import-roboticschampionship.py
Đầu vào : satellites/backup/roboticschampionship.vn/{pages,posts}.json  (đã gồm bản sửa 11/2026)
Đầu ra  : satellites/content/roboticschampionship.vn/{shell.html, pages/*.html}
Sau đó sửa trực tiếp các file trong pages/ – không cần chạy lại script này.
"""
import json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
BK = ROOT / 'backup' / 'roboticschampionship.vn'
OUT = ROOT / 'content' / 'roboticschampionship.vn'
(OUT / 'pages').mkdir(parents=True, exist_ok=True)

items = {p['slug'] or str(p['id']): p for p in json.load(open(BK / 'pages.json')) + json.load(open(BK / 'posts.json'))}

NAV = ('<nav id="vrc-nav" class="vrc-nav">'
       '<a href="/">Trang chủ</a><a href="/gioi-thieu/">Giới thiệu</a><a href="/chuong-trinh/">Chương trình</a>'
       '<a href="/vrc2026/">Giải Quốc gia</a><a href="/tai-lieu/">Tài liệu</a><a href="/tin-tuc/">Tin tức</a>'
       '<a href="/lien-he/">Liên hệ</a><a class="vrc-header-cta" href="/dang-ky-doi-thi/">Đăng ký đội thi</a></nav>')


def unwrap(raw):
    return re.sub(r'^\s*<!-- wp:html -->|<!-- /wp:html -->\s*$', '', raw.strip()).strip()


def fix_links(s):
    s = re.sub(r'<nav id="vrc-nav" class="vrc-nav">.*?</nav>', NAV, s, flags=re.S)
    s = s.replace('<a class="vrc-brand" href="#">', '<a class="vrc-brand" href="/">')
    s = re.sub(r'href="(?:https?://roboticschampionship\.vn)?/?([a-z0-9-]+)\.html"', r'href="/\1/"', s)
    s = re.sub(r'href="https?://roboticschampionship\.vn(/[^"]*)"', r'href="\1"', s)
    return s


def meta(title, desc):
    return '<!--meta ' + json.dumps({'title': title, 'description': desc}, ensure_ascii=False) + ' -->\n'


# 1. Khung chung lấy từ trang Giải Quốc gia
vrc = fix_links(unwrap(items['vrc2026']['content']['raw']))
head, rest = vrc.split('<main', 1)
_, tail = rest.split('</main>', 1)
head = re.sub(r'<title>.*?</title>', '<title>{{title}}</title>', head, flags=re.S)
head = re.sub(r'<meta name="description"[^>]*>', '', head)
head = head.replace('<title>{{title}}</title>', '<title>{{title}}</title>\n<meta name="description" content="{{description}}">\n{{head}}')
shell = head + '<main class="vrc-inner-page" id="vrc-gt" data-lang="vi">\n{{content}}\n</main>' + tail
(OUT / 'shell.html').write_text(shell)

# 2. Trang là tài liệu HTML đầy đủ → giữ nguyên, chỉ sửa menu
DESC = {
    'vrc2026': ('Giải Quốc gia', 'Lộ trình mùa giải 2026–2027: vòng khu vực, Chung kết Quốc gia và sự kiện quốc tế.'),
    'dang-ky-doi-thi': ('Đăng ký đội thi', 'Cách đăng ký đội RECF Engage, Achieve, Inspire tại Việt Nam và chương trình tài trợ mã đội.'),
    'gioi-thieu': ('Giới thiệu', 'Giới thiệu Giải Vô địch Robotics Việt Nam (VRC) do NSSC và SEPA đồng tổ chức.'),
    # recf-achieve: trang WordPress đang chứa nhầm nội dung Inspire → viết lại tay trong pages/recf-achieve.html
    'recf-inspire': ('RECF Inspire', 'RECF Inspire – chương trình thi đấu robotics bậc cao đẳng, đại học.'),
    'crest-awards': ('CREST Awards', 'CREST Awards – chứng nhận dự án STEM của Hiệp hội Khoa học Anh dành cho các đội VRC.'),
}
def source(p):
    # Trang dựng bằng Elementor: nội dung thật nằm trong các widget HTML của _elementor_data
    m = p.get('meta') or {}
    if m.get('_elementor_edit_mode') == 'builder' and m.get('_elementor_data'):
        out = []
        def walk(nodes):
            for e in nodes:
                if e.get('widgetType') == 'html':
                    out.append(e.get('settings', {}).get('html', ''))
                walk(e.get('elements', []))
        walk(json.loads(m['_elementor_data']))
        if out:
            return '\n'.join(out)
    return p['content']['raw']


for slug, (title, desc) in DESC.items():
    s = fix_links(unwrap(source(items[slug])))
    if '<!doctype' in s[:300].lower():
        s = re.sub(r'<title>.*?</title>', f'<title>{title} | Vietnam Robotics Championship</title>', s, flags=re.S)
        body = s
    elif 'vrc-site-header' in s:
        # có header/footer riêng nhưng thiếu <head>
        s = re.sub(r'^(<p></p>\s*)?', '', s)
        s = re.sub(r'<meta charset[^>]*>|<meta name="viewport"[^>]*>|<title>.*?</title>', '', s, flags=re.S)
        body = ('<!doctype html>\n<html lang="vi"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1">'
                f'<title>{title} | Vietnam Robotics Championship</title></head><body>\n{s}\n</body></html>')
    else:
        body = s  # chỉ là nội dung → bọc trong khung chung khi dựng
    (OUT / 'pages' / f'{slug}.html').write_text(meta(title, desc) + body)

print('xong:', sorted(p.name for p in (OUT / 'pages').iterdir()))
