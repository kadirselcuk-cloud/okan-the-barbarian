import json, os, sys
from PIL import Image, ImageDraw, ImageOps
src='/home/user/okan-the-barbarian/faces/src'; dst='/home/user/okan-the-barbarian/faces'
det=json.load(open(os.path.join(os.path.dirname(__file__),'face_boxes.json')))
# per-person tweaks: (scale, dx, dy) in units of detected box width
tweak=json.loads(sys.argv[1]) if len(sys.argv)>1 else {}
OW,OH=320,333
tiles=[]
for pid,v in det.items():
    x,y,bw,bh=v['faces'][0]
    s,dx,dy=tweak.get(pid,[1.24,0,0.02])
    cx=x+bw/2+dx*bw; cy=y+bh/2+dy*bw
    w=s*bw; h=w*OH/OW
    im=Image.open(f'{src}/{pid}.jpg').convert('RGB')
    box=(int(cx-w/2),int(cy-h/2),int(cx+w/2),int(cy+h/2))
    # pad if crop leaves the image
    pad=max(0,-box[0],-box[1],box[2]-im.width,box[3]-im.height)
    if pad: im=ImageOps.expand(im,pad,fill=im.getpixel((0,0))); box=tuple(b+pad for b in box)
    c=im.crop(box).resize((OW,OH),Image.LANCZOS)
    c.save(f'{dst}/{pid}.jpg',quality=88)
    m=Image.new('L',(OW,OH),0); ImageDraw.Draw(m).ellipse([0,0,OW-1,OH-1],fill=255)
    t=Image.new('RGB',(OW,OH+20),'#2f8f3a'); t.paste(c,(0,0),m); ImageDraw.Draw(t).text((6,OH+4),pid,fill='white'); tiles.append(t.resize((200,221)))
G=Image.new('RGB',(1000,663),'#2f8f3a')
for k,t in enumerate(tiles): G.paste(t,((k%5)*200,(k//5)*221))
G.save(sys.argv[2] if len(sys.argv) > 2 else '/tmp/crops.png')
