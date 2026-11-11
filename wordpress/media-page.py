import json,subprocess,sys
S='.'; API='https://sepa.org.vn/wp-json/wp/v2'
AUTH=['-b','cj.txt','-H','X-WP-Nonce: '+open('nonce').read().strip(),'-H','Content-Type: application/json']
def call(method,path,data=None):
    r=subprocess.run(['curl','-sS','--fail-with-body',*AUTH,'-X',method,API+path,'--data-binary','@-'],input=json.dumps(data or {}),capture_output=True,text=True)
    if r.returncode: sys.exit(r.stdout[:500])
    return json.loads(r.stdout)
src=open('p.html').read(); css=src[src.find('<style>')+7:src.find('</style>')]
css+=' .sepa-pr.sp-album{max-width:1100px} .sepa-pr .sp-credit{font-size:13.5px;color:var(--muted);border-top:1px solid var(--line);padding-top:14px;margin-top:34px}'
head=f'''<style>{css}</style><article class="sepa-pr sp-album"><div class="sp-meta"><span class="sp-pill">Media</span><span>Thư viện ảnh sự kiện SEPA</span></div><p class="sp-lead">Hình ảnh từ các giải đấu, trại hè, khóa học và chương trình STEM do SEPA tổ chức và đồng hành. Chọn một album để xem toàn bộ ảnh của sự kiện.</p></article>'''
foot='''<article class="sepa-pr sp-album"><p class="sp-credit">Ảnh thuộc bản quyền SEPA – Liên minh Thúc đẩy Giáo dục STEM. Báo chí và đối tác sử dụng lại vui lòng ghi nguồn “SEPA”. Cần ảnh gốc độ phân giải cao, liên hệ <a href="mailto:sepa@sepa.org.vn">sepa@sepa.org.vn</a>.</p></article>'''
content=('<!-- wp:html -->'+head+'<!-- /wp:html -->\n\n<!-- wp:html --><div class="sepa-pr sp-album" style="max-width:1100px;margin:0 auto">[sepa_media_albums]</div><!-- /wp:html -->\n\n<!-- wp:html -->'+foot+'<!-- /wp:html -->')
pg=call('POST','/pages',{'title':'Media – Thư viện ảnh sự kiện','slug':'media','status':'publish','content':content,
  'featured_media':24098,'excerpt':'Thư viện ảnh các sự kiện, giải đấu và chương trình giáo dục STEM của SEPA.'})
print('media',pg['id'],pg['link']); open('media_id','w').write(str(pg['id']))
al=call('POST','/pages/24120',{'parent':pg['id'],'date':'2026-11-08T17:00:00'})
print('album',al['link'])
