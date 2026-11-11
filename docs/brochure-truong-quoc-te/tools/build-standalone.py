"""Tạo bản HTML một file (ảnh, logo, QR nhúng sẵn) từ index.html.
Chạy: python3 tools/build-standalone.py  (từ thư mục brochure-truong-quoc-te)"""
import base64, pathlib, re

root = pathlib.Path(__file__).resolve().parent.parent
html = (root / "index.html").read_text(encoding="utf-8")
mime = {".jpg": "image/jpeg", ".svg": "image/svg+xml", ".png": "image/png"}

def inline(m):
    path = root / m.group(1)
    data = base64.b64encode(path.read_bytes()).decode()
    return f'src="data:{mime[path.suffix]};base64,{data}"'

out = re.sub(r'src="(img/[^"]+)"', inline, html)
(root / "SEPA-ho-so-gioi-thieu.html").write_text(out, encoding="utf-8")
print("ok", len(out) // 1024, "KB")
