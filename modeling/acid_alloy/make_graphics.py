"""Original vector-style surface artwork, rasterized for packed Blender textures."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

OUT=Path(__file__).parent/'textures';OUT.mkdir(exist_ok=True)
FONT='C:/Windows/Fonts/bahnschrift.ttf'
MONO='C:/Windows/Fonts/consolab.ttf'
ACID='#d0ef19'; DARK='#161a1e'; PURPLE='#843bde'; WHITE='#e6e9dd'

S=3072
im=Image.new('RGBA',(S,S),(0,0,0,0));d=ImageDraw.Draw(im)
def xy(x,y):return ((x+50)/100*S,(50-y)/100*S)
def line(points,fill=DARK,w=.18):d.line([xy(*p) for p in points],fill=fill,width=max(1,round(w*S/100)),joint='curve')
def text(x,y,t,h=1.3,fill=DARK,anchor='mm',font=FONT):
    d.text(xy(x,y),t,font=ImageFont.truetype(font,round(h*S/100)),fill=fill,anchor=anchor)
def circle(x,y,r,fill=DARK,w=.16):
    d.ellipse([xy(x-r,y+r),xy(x+r,y-r)],outline=fill,width=max(1,round(w*S/100)))
text(-34,45.9,'AA / 01',2.0)
text(0,46,'EXPERIMENTAL CONTROL SYSTEM',1.1)
text(34,46,'SER. 013',1.15)
text(-5,-39.85,'ACID  /  ALLOY',2.5)
text(1,-47.25,'OPENMICRO     /     LIVE INPUT LAB     /     13 : 01 : 01',1.15)
text(-28.575,-37.3,'TOUCH / GATE',1.15)
circle(-28.575,-28.575,7.1)
circle(-28.575,-28.575,7.8,w=.1)
for i in range(24):
    a=i*math.tau/24
    r=8.6 if i%3==0 else 8.1
    line([(-28.575+7.5*math.cos(a),-28.575+7.5*math.sin(a)),(-28.575+r*math.cos(a),-28.575+r*math.sin(a))],w=.18)
text(-28,-16,'GATE',1.2)
text(-28,40.5,'TUNE / PUSH',1.3)
text(29.5,43,'VECTOR / XY',1.2)
for x,y in [(-45.7,-29),(-45.7,-21),(-45.7,0),(-45.7,8),(45.7,-29),(45.7,-21),(45.7,0),(45.7,8)]:
    line([(x-1,y+1.5),(x+1,y),(x-1,y-1.5)],w=.4)
for x in [-39.3,39.3]:
    line([(x,-34),(x,-20)],w=.15)
    line([(x,-15),(x,15)],w=.15)
    for y in range(-32,16,4):line([(x,y),(x+(.8 if x<0 else -.8),y)],w=.12)
for a in range(80,281,20):
    a=math.radians(a);line([(-28.075+9.3*math.cos(a),28.575+9.3*math.sin(a)),(-28.075+10.0*math.cos(a),28.575+10.0*math.sin(a))],w=.25)
im.save(OUT/'panel_print.png')

im=Image.new('RGBA',(3072,512),(0,0,0,0));d=ImageDraw.Draw(im)
d.text((220,230),'ACID / ALLOY',font=ImageFont.truetype(FONT,180),fill=ACID,anchor='lm')
d.text((210,390),'EXPERIMENTAL CONTROL SYSTEM',font=ImageFont.truetype(MONO,38),fill=WHITE,anchor='lm')
d.text((2840,260),'01',font=ImageFont.truetype(FONT,310),fill=ACID,anchor='rm')
for i in range(14):
    x=1840+i*30;d.rectangle((x,150,x+(8 if i%3 else 18),345),fill=PURPLE)
im.save(OUT/'case_front_print.png')

im=Image.new('RGBA',(2048,512),(0,0,0,0));d=ImageDraw.Draw(im)
d.text((200,190),'NO SIGNAL. NO LIMIT.',font=ImageFont.truetype(FONT,100),fill=WHITE,anchor='lm')
d.text((205,325),'AA-013  /  LIVE INPUT LAB',font=ImageFont.truetype(MONO,45),fill=ACID,anchor='lm')
for i in range(4):
    x=1610+i*78;d.polygon([(x,110),(x+45,110),(x-35,370),(x-80,370)],fill=ACID)
im.save(OUT/'case_side_print.png')

order=[3,4,8,9,10,11,12,13,14,15,5,6,7]
names=['TRIGGER','HOLD','CH.01','CH.02','CH.03','CH.04','BANK','ENTER','CUT','EXEC','VOICE','BURST','SEND']
for index,(num,label) in enumerate(zip(order,names),1):
    im=Image.new('RGBA',(768,768),(0,0,0,0));d=ImageDraw.Draw(im)
    color=DARK if num==3 else WHITE if num==4 or 8<=num<=11 else ACID
    if 8<=num<=11:
        d.text((95,155),f'{index:02d}',font=ImageFont.truetype(FONT,120),fill=color,anchor='lm')
        d.line([(80,595),(620,595)],fill=color,width=7)
        d.text((610,650),label,font=ImageFont.truetype(MONO,48),fill=color,anchor='rm')
    else:
        d.text((365,320),f'{index:02d}',font=ImageFont.truetype(FONT,305),fill=color,anchor='mm')
        d.text((610,610),label,font=ImageFont.truetype(MONO,44),fill=color,anchor='rm')
        d.line([(120,500),(610,500)],fill=color,width=6)
    im.save(OUT/f'key_{num:02d}.png')

im=Image.new('RGBA',(1024,1024),(0,0,0,0));d=ImageDraw.Draw(im)
d.rounded_rectangle((470,55,554,290),radius=20,fill=DARK)
d.arc((260,260,764,764),20,320,fill=DARK,width=20)
d.text((512,540),'TUNE',font=ImageFont.truetype(MONO,105),fill=DARK,anchor='mm')
im.save(OUT/'knob_print.png')
im=Image.new('RGBA',(1024,1024),(0,0,0,0));d=ImageDraw.Draw(im)
d.ellipse((220,260,760,800),outline=ACID,width=35)
d.line((490,180,490,400),fill=ACID,width=35)
d.line((390,285,590,285),fill=ACID,width=35)
d.text((520,580),'XY',font=ImageFont.truetype(MONO,145),fill=WHITE,anchor='mm')
im.save(OUT/'joystick_print.png')
print('Created 18 original surface artwork textures.')
