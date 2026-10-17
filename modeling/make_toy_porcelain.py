from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math
P=Path(__file__).parent
FONT='C:/Windows/Fonts/bahnschrift.ttf';MONO='C:/Windows/Fonts/consolab.ttf'
for variant in ['rebel_toy','electric_porcelain']:
 D=P/variant;O=D/'textures';O.mkdir(parents=True,exist_ok=True);(D/'renders').mkdir(exist_ok=True)
 toy=variant=='rebel_toy'
 ink='#20205e' if toy else '#123b9b';accent='#ff3984' if toy else '#24c8da';white='#fff1c9' if toy else '#eef9ff'
 src=(P/'acid_alloy/redesign_keyprints.py').read_text(encoding='utf-8')
 src=src.replace("OUT=D/'textures'/'function_v2'","OUT=D/'textures'")
 src=src.replace("c='#161a1e' if idx==1 else '#e6e9dd' if idx in (2,3,4,5,6) else '#d0ef19'", "c='#fff1c9' if idx in (2,3,4,5,6,9,10,12) else '#20205e'" if toy else "c='#eef9ff' if idx in (1,3,4,5,6,10) else '#123b9b'")
 src=src.replace("line([(550,128),(628,128)],6);line([(628,128),(628,166)],6)","d.ellipse((542,95,626,179),outline=c,width=10);line([(555,153),(611,117)],8)" if toy else "line([(550,115),(628,115),(628,175)],5);line([(565,130),(613,130),(613,175)],3)")
 src=src.replace("line([(132,548),(635,548)],6)","line([(132,550),(255,540),(386,555),(510,540),(635,548)],9)" if toy else "line([(132,548),(635,548)],4);line([(155,565),(612,565)],2)")
 src=src[:src.index('sheet=Image.new')]
 exec(compile(src,str(D/'keyprint_source.py'),'exec'),{'__file__':str(D/'keyprint_source.py')})
 (D/'keyprint_source.py').write_text(src,encoding='utf-8')
 S=3072;im=Image.new('RGBA',(S,S));dr=ImageDraw.Draw(im)
 def xy(x,y):return ((x+50)/100*S,(50-y)/100*S)
 def line(p,c=ink,w=.18):dr.line([xy(*v) for v in p],fill=c,width=max(1,round(w*S/100)),joint='curve')
 def txt(x,y,t,h=1.3,c=ink):dr.text(xy(x,y),t,font=ImageFont.truetype(FONT if toy else MONO,round(h*S/100)),fill=c,anchor='mm')
 def circ(x,y,r,c=ink,w=.18):dr.ellipse([xy(x-r,y+r),xy(x+r,y-r)],outline=c,width=max(1,round(w*S/100)))
 def rect(a,b,c,d,col):dr.rectangle([xy(a,d),xy(c,b)],fill=col)
 if toy:
  txt(-32,46,'RT / 04',2.3);txt(0,46,'SERIOUSLY UN-SERIOUS.',1.8);txt(33,46,'PLAY HARD',1.8)
  txt(-28,40.5,'TWIST IT!',1.8);txt(30,43,'GO WILD / XY',1.5)
  for x in [-45.5,45.5]:
   for y in [-28,-21,-1,6]:
    line([(x-1.2,y+1.7),(x+1.1,y+.4),(x-1,y-.6),(x+1.2,y-1.8)],accent,.55)
  for x in [-39.2,39.2]:
   for y in range(-32,16,4):
    circ(x,y,.45,ink,.3)
  for a in range(80,281,25):
   a=math.radians(a);line([(-28.075+9.2*math.cos(a),28.575+9.2*math.sin(a)),(-28.075+10.3*math.cos(a),28.575+10.3*math.sin(a))],ink,.45)
  circ(-28.575,-28.575,7.5,accent,.65)
  for a in range(0,360,45):
   a=math.radians(a);line([(-28.575+8.5*math.cos(a),-28.575+8.5*math.sin(a)),(-28.575+9.3*math.cos(a),-28.575+9.3*math.sin(a))],ink,.4)
  txt(-28.575,-39.2,'POKE HERE',1.5)
  txt(3,-39.5,'REBEL / TOY',2.8)
  txt(0,-47,'NOT A BORING MACHINE.  /  13 WAYS TO PLAY',1.4)
 else:
  txt(-32,46,'EP / 02',2);txt(0,46,'ELECTRIC PORCELAIN',1.6);txt(33,46,'GLAZE / 02',1.3)
  txt(-28,40.5,'ROTARY / 01',1.4);txt(30,43,'VECTOR / XY',1.4)
  for x in [-45.5,45.5]:
   for y in [-27,-20,0,7]:
    line([(x,y-2),(x-1.2,y-1),(x,y),(x+1.2,y+1),(x,y+2)],ink,.22)
    circ(x,y,.3,accent,.2)
  for x in [-39.1,39.1]:
   line([(x,-34),(x,-19),(x+.6,-18),(x+.6,15)],ink,.1)
   for y in [-32,-22,-12,-2,8,15]:
    line([(x,y),(x+1.1,y),(x+1.1,y+1.5)],ink,.16);circ(x+1.1,y+1.5,.26,accent,.16)
  for r in [9.2,9.55]:
   pts=[(-28.075+r*math.cos(math.radians(a)),28.575+r*math.sin(math.radians(a))) for a in range(80,281)]
   line(pts,ink,.11)
  for a in range(80,281,20):
   a=math.radians(a);circ(-28.075+10*math.cos(a),28.575+10*math.sin(a),.22,ink,.2)
  circ(-28.575,-28.575,7.5,ink,.18);circ(-28.575,-28.575,8.2,ink,.1)
  for a in range(0,360,30):
   a=math.radians(a);x=-28.575+8.7*math.cos(a);y=-28.575+8.7*math.sin(a)
   line([(x-.35,y),(x,y+.35),(x+.35,y),(x,y-.35),(x-.35,y)],ink,.13)
  txt(-28.575,-39.2,'TOUCH / GATE',1.25);txt(4,-39.5,'ELECTRIC / PORCELAIN',1.65)
  txt(0,-47,'COBALT CIRCUITS    /    HUMAN CONNECTION',1.15)
 im.save(O/'panel_print.png')
 im=Image.new('RGBA',(3072,512));dr=ImageDraw.Draw(im)
 if toy:
  dr.rounded_rectangle((140,75,1990,425),radius=65,fill=white)
  dr.text((245,225),'REBEL / TOY',font=ImageFont.truetype(FONT,195),fill=ink,anchor='lm')
  dr.text((255,365),'GOOD TOYS. BAD ATTITUDE.',font=ImageFont.truetype(MONO,43),fill=ink,anchor='lm')
  for row in range(4):
   for col in range(5):
    if (row+col)%2==0:dr.rectangle((2160+col*90,80+row*90,2250+col*90,170+row*90),fill=white)
 else:
  dr.text((230,225),'ELECTRIC PORCELAIN',font=ImageFont.truetype(FONT,145),fill=ink,anchor='lm')
  dr.text((242,365),'EP-013  /  COBALT CIRCUIT COLLECTION',font=ImageFont.truetype(MONO,39),fill=ink,anchor='lm')
  for y in [65,85,435,455]:dr.line((130,y,2930,y),fill=ink,width=3)
  for x in [2660,2760,2860]:
   dr.line([(x,180),(x+35,230),(x,280),(x-35,230),(x,180)],fill=ink,width=7)
 im.save(O/'case_front_print.png')
 im=Image.new('RGBA',(2048,512));dr=ImageDraw.Draw(im)
 if toy:
  dr.text((170,160),'PRESS YOUR LUCK.',font=ImageFont.truetype(FONT,110),fill=white,anchor='lm')
  dr.line([(180,330),(380,280),(510,370),(720,270),(850,365),(1080,285),(1250,345),(1770,300)],fill='#ffdb30',width=25)
  dr.text((180,440),'RT-013 / KEEP PLAYING',font=ImageFont.truetype(MONO,40),fill=white,anchor='lm')
 else:
  for j in range(4):
   pts=[(x,135+j*65+28*math.sin(x/105)) for x in range(120,1920,4)]
   dr.line(pts,fill=ink,width=6)
  for x in range(240,1900,320):
   dr.ellipse((x-17,190,x+17,224),fill=accent)
  dr.text((1024,438),'CIRCUITS IN GLAZE / 02',font=ImageFont.truetype(MONO,38),fill=ink,anchor='mm')
 im.save(O/'case_side_print.png')
 im=Image.new('RGBA',(1024,1024));dr=ImageDraw.Draw(im)
 if toy:
  dr.polygon([(492,85),(640,310),(550,310),(605,460),(390,250),(488,250)],fill=ink)
  dr.text((512,630),'TWIST!',font=ImageFont.truetype(FONT,150),fill=ink,anchor='mm')
  dr.arc((165,165,859,859),20,160,fill=ink,width=22)
 else:
  for r,w in [(350,10),(320,5)]:dr.ellipse((512-r,512-r,512+r,512+r),outline=white,width=w)
  dr.line((512,100,512,300),fill=accent,width=30)
  dr.text((512,510),'ROTARY',font=ImageFont.truetype(MONO,95),fill=white,anchor='mm')
  dr.text((512,630),'01',font=ImageFont.truetype(MONO,60),fill=accent,anchor='mm')
 im.save(O/'knob_print.png')
 im=Image.new('RGBA',(1024,1024));dr=ImageDraw.Draw(im)
 if toy:
  dr.line([(250,400),(350,510),(250,620)],fill=ink,width=45)
  dr.line([(774,400),(674,510),(774,620)],fill=ink,width=45)
  dr.text((512,290),'MOVE',font=ImageFont.truetype(FONT,130),fill=ink,anchor='mm')
  dr.text((512,730),'ME!',font=ImageFont.truetype(FONT,135),fill=ink,anchor='mm')
 else:
  for a in range(0,360,90):
   a=math.radians(a);cx=512+120*math.cos(a);cy=512+120*math.sin(a)
   dr.ellipse((cx-170,cy-170,cx+170,cy+170),outline=ink,width=13)
  dr.ellipse((470,470,554,554),fill=accent)
  dr.text((512,855),'XY',font=ImageFont.truetype(MONO,75),fill=ink,anchor='mm')
 im.save(O/'joystick_print.png')
 print(variant+': 18 artwork textures')
