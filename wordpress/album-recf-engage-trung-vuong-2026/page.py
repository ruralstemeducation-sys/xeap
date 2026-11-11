import json, subprocess, os, sys, html
S=os.environ.get('ALBUM_DIR', os.path.dirname(os.path.abspath(__file__))); API='https://sepa.org.vn/wp-json/wp/v2'
AUTH=['-b',f'{S}/cj.txt','-H','X-WP-Nonce: '+open(f'{S}/nonce').read().strip()]
med=json.load(open(f'{S}/media.json')); M=[med[k] for k in sorted(med)]
e=html.escape
src=open(f'{S}/p.html').read(); css=src[src.find('<style>')+7:src.find('</style>')]
css+=(" .sepa-pr.sp-album{max-width:1100px}"
 " .sepa-pr .sp-grid.g3c{grid-template-columns:repeat(3,1fr)}"
 " .sepa-pr .sp-sec-intro{color:var(--muted);margin:-4px 0 12px;font-size:15.5px}"
 " .sepa-pr .sp-credit{font-size:13.5px;color:var(--muted);border-top:1px solid var(--line);padding-top:14px;margin-top:30px}"
 " @media (max-width:760px){.sepa-pr .sp-grid.g3c{grid-template-columns:1fr 1fr}}")
def fig(n, wide=False):
    m=M[n-1]; c=e(m['cap'])
    if wide:
        return f'<figure class="sp-fig wide"><a href="{m["full"]}" target="_blank" rel="noopener"><img src="{m["full"]}" alt="{c}" class="wp-image-{m["id"]}" loading="eager"></a><figcaption>{c}</figcaption></figure>'
    return f'<figure><a href="{m["full"]}" target="_blank" rel="noopener"><img src="{m["large"]}" alt="{c}" class="wp-image-{m["id"]}" loading="lazy"></a><figcaption>{c}</figcaption></figure>'
grid=lambda ns: '<div class="sp-grid g3c">'+''.join(fig(n) for n in ns)+'</div>'
POST='https://sepa.org.vn/giai-robotics-recf-engage-trung-vuong-2026.htm'
body=f'''<style>{css}</style>
<article class="sepa-pr sp-album">
<div class="sp-meta"><span class="sp-pill">Album ảnh</span><span>RECF Engage · VRC 2026–2027</span><span class="sp-dot"></span><span>Trường THCS Trưng Vương, Hà Nội · 07–08/11/2026</span></div>
<div class="sp-stats"><div class="sp-stat"><b>25</b><span>đội thi</span></div><div class="sp-stat"><b>~150</b><span>học sinh</span></div><div class="sp-stat"><b>63</b><span>trận xếp hạng</span></div><div class="sp-stat"><b>4</b><span>sân thi đấu</span></div><div class="sp-stat"><b>14</b><span>giám khảo</span></div><div class="sp-stat"><b>22</b><span>ảnh chọn lọc</span></div></div>
<p class="sp-lead">Những khoảnh khắc đáng nhớ tại Giải Robotics RECF Engage khu vực Hà Nội – Trưng Vương 2026, vòng khu vực của Giải Vô địch Robotics Việt Nam (VRC) trong khuôn khổ TECHFEST Việt Nam 2026. Hai ngày thi đấu quy tụ 25 đội học sinh tiểu học và THCS đến từ Hà Nội, Bắc Ninh và Phú Thọ.</p>
{fig(1, True)}
{grid([2,3,5])}
<h2 class="sp-h2">Trên sân thi đấu</h2>
<p class="sp-sec-intro">63 trận xếp hạng theo thể thức liên minh: hai đội ghép cặp ngẫu nhiên, cùng phối hợp để giành điểm cao nhất.</p>
{grid([4,7,8,12,13,14,17,18,22])}
<h2 class="sp-h2">Các đội và robot</h2>
<p class="sp-sec-intro">Thiết kế, chế tạo, lập trình, thử nghiệm và cải tiến: học sinh trực tiếp đưa ra mọi quyết định kỹ thuật.</p>
{grid([6,9,10,11,15,16])}
<h2 class="sp-h2">Thi Solo và phỏng vấn Ban Giám khảo</h2>
<p class="sp-sec-intro">Ban Giám khảo gồm 14 chuyên gia, giảng viên và giáo viên trong nước và quốc tế chấm sổ tay kỹ thuật và phỏng vấn từng đội theo rubric của RECF.</p>
{grid([19,20,21])}
<div class="sp-btns"><a class="sp-btn" href="{POST}">Đọc thông cáo báo chí và kết quả đầy đủ →</a></div>
<p class="sp-credit">Ảnh: SEPA – Liên minh Thúc đẩy Giáo dục STEM. Bấm vào ảnh để xem kích thước lớn. Vui lòng ghi nguồn “SEPA” khi sử dụng lại.</p>
</article>'''
content='<!-- wp:html -->'+body.replace('\n',' ')+'<!-- /wp:html -->'
data={'title':'Album ảnh Giải Robotics RECF Engage khu vực Hà Nội – Trưng Vương 2026',
 'slug':'album-recf-engage-trung-vuong-2026','status':sys.argv[1] if len(sys.argv)>1 else 'draft',
 'content':content,'featured_media':M[0]['id'],
 'excerpt':'22 ảnh chọn lọc từ Giải Robotics RECF Engage khu vực Hà Nội – Trưng Vương 2026 (07–08/11/2026): 25 đội học sinh, 63 trận đấu tại Trường THCS Trưng Vương.'}
pid=open(f'{S}/page_id').read().strip() if os.path.exists(f'{S}/page_id') else ''
r=subprocess.run(['curl','-sS','--fail-with-body',*AUTH,'-X','POST',f'{API}/pages'+(f'/{pid}' if pid else ''),'-H','Content-Type: application/json','--data-binary','@-'],input=json.dumps(data),capture_output=True,text=True)
if r.returncode: sys.exit(r.stdout[:600])
p=json.loads(r.stdout); open(f'{S}/page_id','w').write(str(p['id'])); print(p['id'],p['status'],p['link'])
