import sys,glob,os
from PIL import Image, ImageOps, ImageDraw
import pillow_heif; pillow_heif.register_heif_opener()
d,out=sys.argv[1],sys.argv[2]
fs=sorted(f for f in glob.glob(d+'/*') if f.lower().endswith(('.jpg','.jpeg','.heic','.png','.webp')))
th=[]
for i,f in enumerate(fs,1):
    im=ImageOps.exif_transpose(Image.open(f)).convert('RGB'); im.thumbnail((400,300))
    c=Image.new('RGB',(400,320),'white'); c.paste(im,((400-im.width)//2,0))
    ImageDraw.Draw(c).text((4,304),f'{i}: {os.path.basename(f)[:40]}',fill='black'); th.append(c)
for k in range(0,len(th),20):
    sh=Image.new('RGB',(2000,320*4),'white')
    for j,c in enumerate(th[k:k+20]): sh.paste(c,((j%5)*400,(j//5)*320))
    sh.save(f'{out}{k//20}.jpg',quality=78)
print(len(fs))
