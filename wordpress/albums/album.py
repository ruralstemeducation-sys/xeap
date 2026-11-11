"""Generic album builder: python3 album.py cfg.json [draft|publish]
cfg: slug, title, date, excerpt, meta_left, meta_right, lead, stats[[n,label]], link[text,url],
     dir, photos[[file, caption, rotate]], cover (1-based), sections[[heading,intro,[idx...]]] (idx 1-based)"""
import json,subprocess,sys,os,html
from PIL import Image, ImageOps
import pillow_heif; pillow_heif.register_heif_opener()
S=os.environ.get('ALBUM_DIR', os.path.dirname(os.path.abspath(__file__))); API='https://sepa.org.vn/wp-json/wp/v2'
cfg=json.load(open(sys.argv[1])); status=sys.argv[2] if len(sys.argv)>2 else 'draft'
AUTH=['-b',f'{S}/cj.txt','-H','X-WP-Nonce: '+open(f'{S}/nonce').read().strip()]
def curl(*a,inp=None):
    r=subprocess.run(['curl','-sS','--fail-with-body',*AUTH,*a],input=inp,capture_output=True,text=True)
    if r.returncode: sys.exit('ERR '+r.stdout[:500])
    return json.loads(r.stdout)
state_f=f"{S}/ev/{cfg['slug']}.state.json"; st=json.load(open(state_f)) if os.path.exists(state_f) else {'media':{}}
os.makedirs(f"{S}/ev/{cfg['slug']}-web",exist_ok=True)
for i,(fn,cap,rot) in enumerate(cfg['photos'],1):
    key=str(i)
    if key in st['media']: continue
    im=ImageOps.exif_transpose(Image.open(os.path.join(cfg['dir'],fn))).convert('RGB')
    if rot: im=im.rotate(-rot,expand=True)
    im.thumbnail((2048,2048),Image.LANCZOS)
    name=f"{cfg['slug']}-{i:02d}.webp"; out=f"{S}/ev/{cfg['slug']}-web/{name}"; im.save(out,'WEBP',quality=80,method=6)
    m=curl('-X','POST',f'{API}/media','-H',f'Content-Disposition: attachment; filename="{name}"','-H','Content-Type: image/webp','--data-binary',f'@{out}')
    m=curl('-X','POST',f"{API}/media/{m['id']}",'-H','Content-Type: application/json','--data-binary','@-',
           inp=json.dumps({'alt_text':cap,'caption':cap,'title':f"{cfg['short']} – ảnh {i:02d}"}))
    sz=m['media_details'].get('sizes',{})
    st['media'][key]={'id':m['id'],'full':m['source_url'],'large':sz.get('large',sz.get('full',{})).get('source_url',m['source_url']),'cap':cap}
    json.dump(st,open(state_f,'w'),ensure_ascii=False,indent=1); print('up',i,m['id'],flush=True)
M=st['media']; e=html.escape
src=open(f'{S}/p.html').read(); css=src[src.find('<style>')+7:src.find('</style>')]
css+=(" .sepa-pr.sp-album{max-width:1100px} .sepa-pr .sp-grid.g3c{grid-template-columns:repeat(3,1fr)}"
 " .sepa-pr .sp-sec-intro{color:var(--muted);margin:-4px 0 12px;font-size:15.5px}"
 " .sepa-pr .sp-credit{font-size:13.5px;color:var(--muted);border-top:1px solid var(--line);padding-top:14px;margin-top:30px}"
 " .sepa-pr .sp-stats.sc3{grid-template-columns:repeat(3,1fr)} .sepa-pr .sp-stats.sc4{grid-template-columns:repeat(4,1fr)} .sepa-pr .sp-stats.sc5{grid-template-columns:repeat(5,1fr)}"
 " @media (max-width:760px){.sepa-pr .sp-grid.g3c{grid-template-columns:1fr 1fr} .sepa-pr .sp-stats.sc4{grid-template-columns:repeat(2,1fr)} .sepa-pr .sp-stats.sc5{grid-template-columns:repeat(3,1fr)}}")
def fig(n,wide=False):
    m=M[str(n)]; c=e(m['cap'])
    if wide: return f'<figure class="sp-fig wide"><a href="{m["full"]}" target="_blank" rel="noopener"><img src="{m["full"]}" alt="{c}" class="wp-image-{m["id"]}" loading="eager"></a><figcaption>{c}</figcaption></figure>'
    return f'<figure><a href="{m["full"]}" target="_blank" rel="noopener"><img src="{m["large"]}" alt="{c}" class="wp-image-{m["id"]}" loading="lazy"></a><figcaption>{c}</figcaption></figure>'
grid=lambda ns:'<div class="sp-grid g3c">'+''.join(fig(n) for n in ns)+'</div>'
stats=''.join(f'<div class="sp-stat"><b>{e(str(a))}</b><span>{e(b)}</span></div>' for a,b in cfg['stats']+[[len(cfg['photos']),'ảnh chọn lọc']])
secs=''
for h,intro,ns in cfg['sections']:
    secs+=(f'<h2 class="sp-h2">{e(h)}</h2>' if h else '')+(f'<p class="sp-sec-intro">{e(intro)}</p>' if intro else '')+grid(ns)
btn=f'<div class="sp-btns"><a class="sp-btn" href="{cfg["link"][1]}">{e(cfg["link"][0])} →</a></div>' if cfg.get('link') else ''
body=(f'<style>{css}</style><article class="sepa-pr sp-album"><div class="sp-meta"><span class="sp-pill">Album ảnh</span><span>{e(cfg["meta_left"])}</span><span class="sp-dot"></span><span>{e(cfg["meta_right"])}</span></div>'
 f'<div class="sp-stats sc{len(cfg["stats"])+1}">{stats}</div><p class="sp-lead">{e(cfg["lead"])}</p>{fig(cfg["cover"],True)}{secs}{btn}'
 '<p class="sp-credit">Ảnh: SEPA – Liên minh Thúc đẩy Giáo dục STEM. Bấm vào ảnh để xem kích thước lớn. Vui lòng ghi nguồn “SEPA” khi sử dụng lại.</p></article>')
data={'title':'Album ảnh '+cfg['title'],'slug':cfg['slug'],'status':status,'parent':int(open(f'{S}/media_id').read()),
      'date':cfg['date'],'content':'<!-- wp:html -->'+body+'<!-- /wp:html -->','featured_media':M[str(cfg['cover'])]['id'],'excerpt':cfg['excerpt']}
pid=st.get('page')
p=curl('-X','POST',f'{API}/pages'+(f'/{pid}' if pid else ''),'-H','Content-Type: application/json','--data-binary','@-',inp=json.dumps(data))
st['page']=p['id']; json.dump(st,open(state_f,'w'),ensure_ascii=False,indent=1); print('page',p['id'],p['status'],p['link'])
