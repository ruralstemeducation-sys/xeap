import json, subprocess, os, sys, html
S=os.environ.get('ALBUM_DIR', os.path.dirname(os.path.abspath(__file__))); API='https://sepa.org.vn/wp-json/wp/v2'
med=json.load(open(f'{S}/media.json')); items=[med[k] for k in sorted(med)]
e=html.escape
imgs=''.join(f'''<!-- wp:image {{"id":{m['id']},"sizeSlug":"large","linkDestination":"media"}} -->
<figure class="wp-block-image size-large"><a href="{m['full']}"><img src="{m['large']}" alt="{e(m['cap'])}" class="wp-image-{m['id']}"/></a><figcaption class="wp-element-caption">{e(m['cap'])}</figcaption></figure>
<!-- /wp:image -->
''' for m in items)
content=f'''<!-- wp:paragraph -->
<p>Ngày 07–08/11/2026, Trường THCS Trưng Vương (26 Hàng Bài, Hoàn Kiếm, Hà Nội) phối hợp cùng SEPA và NSSC tổ chức <strong>Giải Robotics RECF Engage khu vực Hà Nội – Trưng Vương 2026</strong>, vòng khu vực của Giải Vô địch Robotics Việt Nam (VRC) mùa giải 2026–2027, trong khuôn khổ TECHFEST Việt Nam 2026.</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul class="wp-block-list"><!-- wp:list-item --><li><strong>25 đội</strong> học sinh tiểu học và THCS đến từ Hà Nội, Bắc Ninh và Phú Thọ, khoảng 150 học sinh</li><!-- /wp:list-item -->
<!-- wp:list-item --><li><strong>63 trận</strong> xếp hạng trên 4 sân, cùng phần chấm sổ tay kỹ thuật và phỏng vấn của 14 giám khảo</li><!-- /wp:list-item -->
<!-- wp:list-item --><li><strong>Vô địch:</strong> liên minh FCG_San Hô Trắng (TH&amp;THCS FPT Cầu Giấy) – Doraemonster (Archimedes)</li><!-- /wp:list-item -->
<!-- wp:list-item --><li><strong>Giải Xuất sắc:</strong> Doraemonster (khối Tiểu học) và TV-GOLDEN GEARS – THCS Trưng Vương (khối THCS)</li><!-- /wp:list-item --></ul>
<!-- /wp:list -->

<!-- wp:heading -->
<h2 class="wp-block-heading">Album ảnh</h2>
<!-- /wp:heading -->

<!-- wp:gallery {{"columns":3,"imageCrop":true,"linkTo":"media","sizeSlug":"large"}} -->
<figure class="wp-block-gallery has-nested-images columns-3 is-cropped">{imgs}</figure>
<!-- /wp:gallery -->

<!-- wp:paragraph {{"fontSize":"small"}} -->
<p class="has-small-font-size">Ảnh: SEPA. Bấm vào ảnh để xem kích thước đầy đủ. Vui lòng ghi nguồn SEPA khi sử dụng lại.</p>
<!-- /wp:paragraph -->'''
body={'title':'Album ảnh: Giải Robotics RECF Engage khu vực Hà Nội – Trưng Vương 2026',
 'slug':'album-recf-engage-trung-vuong-2026','status':sys.argv[1] if len(sys.argv)>1 else 'draft',
 'content':content,'featured_media':items[0]['id'],
 'excerpt':'Album ảnh Giải Robotics RECF Engage khu vực Hà Nội – Trưng Vương 2026: 25 đội học sinh, 63 trận đấu, ngày 07–08/11/2026 tại Trường THCS Trưng Vương.'}
pid=open(f'{S}/page_id').read().strip() if os.path.exists(f'{S}/page_id') else ''
r=subprocess.run(['curl','-sS','--fail-with-body','-X','POST',f'{API}/pages'+(f'/{pid}' if pid else ''),'-H','Content-Type: application/json','--data-binary','@-'],input=json.dumps(body),capture_output=True,text=True)
if r.returncode: sys.exit(r.stdout[:600])
p=json.loads(r.stdout); open(f'{S}/page_id','w').write(str(p['id'])); print(p['id'],p['status'],p['link'])
