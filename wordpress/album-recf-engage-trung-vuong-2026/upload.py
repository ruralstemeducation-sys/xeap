import json, subprocess, glob, os, sys
S=os.environ.get('ALBUM_DIR', os.path.dirname(os.path.abspath(__file__))); API='https://sepa.org.vn/wp-json/wp/v2'
caps=json.load(open(f'{S}/captions.json'))
out=f'{S}/media.json'; done=json.load(open(out)) if os.path.exists(out) else {}
def curl(*a):
    r=subprocess.run(['curl','-sS','--fail-with-body',*a],capture_output=True,text=True)
    if r.returncode: sys.exit(f'ERR {r.stdout[:400]} {r.stderr[:200]}')
    return json.loads(r.stdout)
for i,f in enumerate(sorted(glob.glob(f'{S}/web/*.jpg'))):
    n=os.path.basename(f)
    if n in done: continue
    m=curl('-X','POST',f'{API}/media','-H',f'Content-Disposition: attachment; filename="{n}"','-H','Content-Type: image/jpeg','--data-binary',f'@{f}')
    m=curl('-X','POST',f"{API}/media/{m['id']}",'-H','Content-Type: application/json','-d',json.dumps({'alt_text':caps[i],'caption':caps[i],'title':f'RECF Engage Trưng Vương 2026 – ảnh {i+1:02d}'}))
    s=m['media_details'].get('sizes',{})
    done[n]={'id':m['id'],'full':m['source_url'],'large':s.get('large',s.get('full',{})).get('source_url',m['source_url']),'cap':caps[i]}
    json.dump(done,open(out,'w'),ensure_ascii=False,indent=1); print(i+1,n,m['id'],flush=True)
