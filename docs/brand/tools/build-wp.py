"""Build the WordPress embed (sepa-brand.css + sepa-brand.js) from docs/brand/index.html.

The page on sepa.org.vn only contains:
  <div id="sepa-brand"></div>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/<repo>@<sha>/docs/brand/wp/sepa-brand.css">
  <script src="https://cdn.jsdelivr.net/gh/<repo>@<sha>/docs/brand/wp/sepa-brand.js"></script>
"""
import json, re, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.dirname(HERE)
UPLOADS = 'https://sepa.org.vn/wp-content/uploads/2026/11/'
src = open(os.path.join(BRAND, 'index.html'), encoding='utf-8').read()

# ---- CSS: scope every rule under #sepa-brand, drop dark-theme blocks ----
css = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)

def blocks(s):
    out, i, n = [], 0, len(s)
    while i < n:
        j = s.find('{', i)
        if j < 0: break
        sel = s[i:j].strip(); depth = 1; k = j + 1
        while depth:
            if s[k] == '{': depth += 1
            elif s[k] == '}': depth -= 1
            k += 1
        out.append((sel, s[j+1:k-1])); i = k
    return out

S = '#sepa-brand'
def scope_sel(sel):
    parts = []
    for p in sel.split(','):
        p = p.strip()
        if p in ('body', ':root'): parts.append(S); continue
        if p == '*': parts.append(S + ' *,' + S); continue
        p = p.replace(':root:not([data-lang="en"])', S + ':not([data-lang="en"])').replace(':root[data-lang="en"]', S + '[data-lang="en"]')
        parts.append(p if p.startswith(S) else S + ' ' + p)
    return ','.join(parts)

def scope(s):
    res = []
    for sel, body in blocks(s):
        if sel.startswith('@font-face'): res.append(sel + '{' + body + '}')
        elif sel.startswith('@media'):
            if 'prefers-color-scheme' in sel: continue
            res.append(sel + '{' + scope(body) + '}')
        elif 'data-theme' in sel: continue
        else: res.append(scope_sel(sel) + '{' + body.strip() + '}')
    return '\n'.join(res)

css_out = '@import url("https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap");\n' + scope(css)
css_out += """
#sepa-brand{font-size:16px;line-height:1.65;border-radius:18px;overflow:hidden;margin:8px 0 40px;text-align:left}
#sepa-brand .wrap{padding-left:clamp(16px,4vw,40px);padding-right:clamp(16px,4vw,40px)}
#sepa-brand main.wrap{padding-bottom:8px}
#sepa-brand section{scroll-margin-top:110px}
#sepa-brand h1,#sepa-brand h2,#sepa-brand h3{margin:0;padding:0;border:0;text-transform:none}
#sepa-brand h1{color:#fff}
#sepa-brand h3{color:var(--ink);font-family:var(--f-body);letter-spacing:0}
#sepa-brand p,#sepa-brand li,#sepa-brand td,#sepa-brand dd{font-family:inherit}
#sepa-brand .specimen-a{font-family:var(--f-display)}#sepa-brand .specimen-b{font-family:"Myriad Pro","Be Vietnam Pro",sans-serif}
#sepa-brand img{box-shadow:none;border-radius:0;margin:0}
#sepa-brand .btn,#sepa-brand .chip{text-decoration:none}
#sepa-brand ul.plain li{margin:0}
#sepa-brand footer{margin-top:56px}
"""
open(os.path.join(BRAND, 'wp', 'sepa-brand.css'), 'w', encoding='utf-8').write(css_out)

# ---- Markup ----
body = src[src.index('<header class="mast">'):src.index('<script src="https://cdnjs')]
body = re.sub(r'src="logo/(sepa-logo-[a-z-]+)\.svg"', r'data-svg="\1"', body)
body = body.replace('<image href="logo/sepa-logo-ngang-mau.svg"', '<image data-svg="sepa-logo-ngang-mau"')
body = body.replace('href="sepa-logo-tron-bo.zip" download data-dl="sepa-logo-tron-bo.zip"', 'href="#logo" data-zip')
body = re.sub(r'\n\s*', '\n', body).strip()

# ---- Vector sources (blue); other colours are derived by swapping the fill ----
svgs = {k: open(os.path.join(BRAND, 'logo', 'sepa-logo-%s-mau.svg' % k), encoding='utf-8').read().strip()
        for k in ('ngang', 'doc', 'bieu-tuong')}

js = r"""/* SEPA brand guidelines – WordPress embed. Built by docs/brand/tools/build-wp.py */
(function(){
var host=document.getElementById('sepa-brand'); if(!host) return;
var UP=%(up)s, SVG=%(svgs)s, COL={mau:'#253E93',trang:'#FFFFFF',den:'#000000'};
host.innerHTML=%(markup)s;
function svgText(name){var m=name.match(/^sepa-logo-(ngang|doc|bieu-tuong)-(mau|trang|den)$/);return SVG[m[1]].replace('fill="#253E93"','fill="'+COL[m[2]]+'"')}
var urls={};
function svgUrl(name){if(!urls[name])urls[name]=URL.createObjectURL(new Blob([svgText(name)],{type:'image/svg+xml'}));return urls[name]}
function hydrate(scope){scope.querySelectorAll('[data-svg]').forEach(function(el){var u=svgUrl(el.getAttribute('data-svg'));if(el.tagName.toLowerCase()==='image')el.setAttribute('href',u);else el.src=u})}
var lang='vi';
function T(vi,en){return lang==='en'?en:vi}
var layouts=[
 {key:'ngang',vi:'Logo ngang',en:'Horizontal logo',hvi:'Phiên bản chính, dùng cho hầu hết trường hợp',hen:'Primary version, for most uses'},
 {key:'doc',vi:'Logo dọc',en:'Stacked logo',hvi:'Khung vuông hoặc khung đứng: poster, standee, áo',hen:'Square or tall spaces: posters, standees, shirts'},
 {key:'bieu-tuong',vi:'Biểu tượng',en:'Symbol',hvi:'Ảnh đại diện, favicon, huy hiệu, không gian rất nhỏ',hen:'Avatars, favicons, badges, very small spaces'}];
var colors=[
 {key:'mau',vi:'Màu xanh',en:'Blue',stage:'on-white',uvi:'nền trắng, nền sáng',uen:'white or light backgrounds'},
 {key:'trang',vi:'Trắng',en:'White',stage:'on-blue',uvi:'nền tối, nền xanh',uen:'dark or blue backgrounds'},
 {key:'den',vi:'Đen',en:'Black',stage:'on-light',uvi:'in đơn sắc',uen:'one-colour printing'}];
function renderVariants(){
 var html='';
 layouts.forEach(function(l){
  html+='<div class="variant"><div class="variant-head"><h3>'+T(l.vi,l.en)+'</h3><span class="note">'+T(l.hvi,l.hen)+'</span></div><div class="tiles">';
  colors.forEach(function(c){
   var f='sepa-logo-'+l.key+'-'+c.key;
   html+='<div class="tile"><div class="stage '+c.stage+'"><img data-svg="'+f+'" alt="'+T(l.vi,l.en)+' – '+T(c.vi,c.en)+'"></div>'+
    '<div class="tile-foot"><span><span class="tile-name">'+T(c.vi,c.en)+'</span><br><span class="note">'+T(c.uvi,c.uen)+'</span></span>'+
    '<span class="dl"><a class="chip" href="#" data-svgdl="'+f+'">SVG</a><a class="chip" href="'+UP+f+'.png" download="'+f+'.png">PNG</a></span></div></div>';
  });
  html+='</div></div>';
 });
 var v=host.querySelector('#variants'); v.innerHTML=html; hydrate(v);
}
function setLang(l,save){
 lang=l==='en'?'en':'vi'; host.setAttribute('data-lang',lang); host.setAttribute('lang',lang);
 host.querySelectorAll('.lang button').forEach(function(b){b.setAttribute('aria-pressed',String(b.getAttribute('data-lang')===lang))});
 renderVariants();
 if(save){try{localStorage.setItem('sepa-lang',lang)}catch(e){}}
}
var start='';
try{start=localStorage.getItem('sepa-lang')||''}catch(e){}
if(!start){var pl=(document.documentElement.lang||navigator.language||'vi');start=/^vi/i.test(pl)?'vi':'en'}
hydrate(host); setLang(start,false);
host.querySelectorAll('.lang button').forEach(function(b){b.addEventListener('click',function(){setLang(b.getAttribute('data-lang'),true)})});
var toastEl=host.querySelector('#toast'),tt;
function toast(m){toastEl.textContent=m;toastEl.classList.add('show');clearTimeout(tt);tt=setTimeout(function(){toastEl.classList.remove('show')},2400)}
function save(blob,name){var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(a.href);a.remove()},1500)}
function loadZip(){return window.JSZip?Promise.resolve(window.JSZip):new Promise(function(ok,no){var s=document.createElement('script');s.src='https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js';s.onload=function(){ok(window.JSZip)};s.onerror=no;document.head.appendChild(s)})}
var busy=false;
function zipAll(){
 if(busy)return; busy=true; toast(T('Đang đóng gói logo…','Packing the logos…'));
 loadZip().then(function(JSZip){
  var z=new JSZip(), jobs=[fetch(UP+'sepa-logo-goc.pdf').then(function(r){if(!r.ok)throw 0;return r.blob()}).then(function(b){z.file('sepa-logo-goc.pdf',b)})];
  layouts.forEach(function(l){colors.forEach(function(c){var f='sepa-logo-'+l.key+'-'+c.key;z.file(f+'.svg',svgText(f));
   jobs.push(fetch(UP+f+'.png').then(function(r){if(!r.ok)throw 0;return r.blob()}).then(function(b){z.file(f+'.png',b)}))})});
  return Promise.all(jobs).then(function(){return z.generateAsync({type:'blob'})});
 }).then(function(b){save(b,'sepa-logo-tron-bo.zip');toast(T('Đã tải sepa-logo-tron-bo.zip','Downloaded sepa-logo-tron-bo.zip'))})
 .catch(function(){toast(T('Chưa tạo được gói .zip, bạn có thể tải từng file bên dưới','Could not build the .zip; you can download files one by one below'))})
 .then(function(){busy=false});
}
host.addEventListener('click',function(e){
 var z=e.target.closest('[data-zip]'); if(z){e.preventDefault();zipAll();return}
 var s=e.target.closest('[data-svgdl]'); if(s){e.preventDefault();var f=s.getAttribute('data-svgdl');save(new Blob([svgText(f)],{type:'image/svg+xml'}),f+'.svg');return}
 var c=e.target.closest('[data-copy]');
 if(c){var v=c.getAttribute('data-copy');var ok=function(){toast(T('Đã sao chép ','Copied ')+v)};
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(v).then(ok,function(){sel(c)})}else sel(c)}
});
function sel(btn){var r=document.createRange();r.selectNodeContents(btn.parentNode.firstChild);var s=getSelection();s.removeAllRanges();s.addRange(r);toast(T('Đã chọn mã màu, nhấn Ctrl+C để sao chép','Colour code selected, press Ctrl+C to copy'))}
})();
""" % {'up': json.dumps(UPLOADS), 'svgs': json.dumps(svgs), 'markup': json.dumps(body, ensure_ascii=False)}
open(os.path.join(BRAND, 'wp', 'sepa-brand.js'), 'w', encoding='utf-8').write(js)
print('ok', len(css_out), len(js))
