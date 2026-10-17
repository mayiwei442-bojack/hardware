"""Generate original Overclock Instrument typography and calibrated panel artwork."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

D=Path(__file__).parent
O=D/'textures';O.mkdir(parents=True,exist_ok=True)
(D/'renders').mkdir(exist_ok=True)
FONT='C:/Windows/Fonts/bahnschrift.ttf'
MONO='C:/Windows/Fonts/consolab.ttf'
INK='#263943';ORANGE='#ff590f';WHITE='#ecf0e9';CYAN='#47cbd7'

# Retain function meanings and authored glyphs, change key print hierarchy.
src=(D.parent/'acid_alloy'/'redesign_keyprints.py').read_text(encoding='utf-8')
src=src.replace("OUT=D/'textures'/'function_v2'", "OUT=D/'textures'")
src=src.replace("c='#161a1e' if idx==1 else '#e6e9dd' if idx in (2,3,4,5,6) else '#d0ef19'", "c='#f3f1e8' if idx==1 or 3<=idx<=6 or idx in (8,9,10) else '#263943'")
src=src.replace("line([(550,128),(628,128)],6);line([(628,128),(628,166)],6)", "text((625,140),'INPUT',27,'rm');line([(120,195),(635,195)],5)")
src=src.replace("f'{idx:02d}',75", "f'K{idx:02d}',56")
src=src[:src.index('sheet=Image.new')]
exec(compile(src,str(D/'keyprint_source.py'),'exec'),{'__file__':str(D/'keyprint_source.py')})
(D/'keyprint_source.py').write_text(src,encoding='utf-8')

S=3072
im=Image.new('RGBA',(S,S));dr=ImageDraw.Draw(im)
def xy(x,y):return ((x+50)/100*S,(50-y)/100*S)
def line(p,c=INK,w=.15):dr.line([xy(*v) for v in p],fill=c,width=max(1,round(w*S/100)))
def txt(x,y,t,h=1.3,c=INK,anchor='mm'):
 dr.text(xy(x,y),t,font=ImageFont.truetype(MONO,round(h*S/100)),fill=c,anchor=anchor)
def circle(x,y,r,c=INK,w=.15):dr.ellipse([xy(x-r,y+r),xy(x+r,y-r)],outline=c,width=max(1,round(w*S/100)))
def rect(x1,y1,x2,y2,c):dr.rectangle([xy(x1,y2),xy(x2,y1)],fill=c)
txt(-32,46,'OC / 03',2.2)
txt(0,46.2,'OVERCLOCK INSTRUMENT',1.5)
txt(32,46,'LAB SERIES',1.4)
txt(0,43.9,'HUMAN INPUT / PRECISION CONTROL',.85)
txt(-28,40.8,'GAIN / PUSH',1.5)
txt(30,43,'VECTOR / XY',1.5)
for angle in range(70,291,10):
 a=math.radians(angle);r=10.2 if angle%30==10 else 9.7
 line([(-28.075+9.1*math.cos(a),28.575+9.1*math.sin(a)),(-28.075+r*math.cos(a),28.575+r*math.sin(a))],ORANGE if angle>=230 else INK,.22)
for x in [-39.1,39.1]:
 line([(x,-34),(x,16)],INK,.12)
 for y in range(-32,17,2):line([(x,y),(x+(.9 if x<0 else -.9)*(1.5 if y%8==0 else 1),y)],INK,.12)
for x in [-45.7,45.7]:
 for y in [-25,-2,7]:
  line([(x-1.1,y),(x+1.1,y)],ORANGE,.35)
  line([(x,y-1.1),(x,y+1.1)],ORANGE,.35)
circle(-28.575,-28.575,7.2);circle(-28.575,-28.575,8.2,w=.08)
for i in range(32):
 a=i*math.tau/32;r=8.8 if i%4==0 else 8.4
 line([(-28.575+7.7*math.cos(a),-28.575+7.7*math.sin(a)),(-28.575+r*math.cos(a),-28.575+r*math.sin(a))],ORANGE if i<8 else INK,.16)
txt(-28.575,-38,'TOUCH / GATE',1.2)
rect(-16,-41,25,-37.9,INK)
txt(4.5,-39.45,'O V E R C L O C K',2.1,WHITE)
txt(0,-47,'OC-013   /   CONTROL ARRAY   /   REV.03',1.25)
txt(-34,-45.5,'CAL.',.9);txt(34,-45.5,'REF.',.9)
im.save(O/'panel_print.png')

im=Image.new('RGBA',(3072,512));dr=ImageDraw.Draw(im)
dr.rectangle((130,95,270,405),fill=ORANGE)
dr.text((340,240),'OVERCLOCK',font=ImageFont.truetype(FONT,172),fill=INK,anchor='lm')
dr.text((348,390),'PRECISION INPUT INSTRUMENT  /  OC-013',font=ImageFont.truetype(MONO,42),fill=INK,anchor='lm')
dr.text((2840,255),'03',font=ImageFont.truetype(FONT,290),fill=INK,anchor='rm')
for i in range(25):
 x=1920+i*19;dr.line((x,330,x,330-(90 if i%5==0 else 42)),fill=INK,width=4)
dr.text((2140,165),'CALIBRATED',font=ImageFont.truetype(MONO,39),fill=INK,anchor='mm')
im.save(O/'case_front_print.png')

im=Image.new('RGBA',(2048,512));dr=ImageDraw.Draw(im)
dr.text((175,140),'SIGNAL / CONTROL',font=ImageFont.truetype(FONT,91),fill=INK,anchor='lm')
dr.text((180,245),'13 INPUTS   /   01 ENCODER   /   XY',font=ImageFont.truetype(MONO,35),fill=INK,anchor='lm')
for i in range(9):
 x=180+i*175;dr.line((x,335,x+120,335),fill=INK,width=5)
dr.line([(180,335),(345,335),(345,285),(510,285),(510,375),(675,375),(675,335),(850,335),(850,285),(1025,285),(1025,375),(1200,375),(1200,335),(1690,335)],fill=ORANGE,width=12)
im.save(O/'case_side_print.png')

im=Image.new('RGBA',(1024,1024));dr=ImageDraw.Draw(im)
dr.rectangle((490,80,534,290),fill=ORANGE)
for i in range(30):
 a=math.tau*i/30;r=360;rr=325 if i%5==0 else 341
 dr.line((512+r*math.cos(a),512+r*math.sin(a),512+rr*math.cos(a),512+rr*math.sin(a)),fill=WHITE,width=7)
dr.text((512,490),'GAIN',font=ImageFont.truetype(MONO,112),fill=WHITE,anchor='mm')
dr.text((512,610),'PUSH',font=ImageFont.truetype(MONO,48),fill=ORANGE,anchor='mm')
im.save(O/'knob_print.png')
im=Image.new('RGBA',(1024,1024));dr=ImageDraw.Draw(im)
dr.ellipse((275,275,749,749),outline=WHITE,width=16)
dr.line((180,512,844,512),fill=WHITE,width=14);dr.line((512,180,512,844),fill=WHITE,width=14)
dr.ellipse((463,463,561,561),fill=ORANGE)
for p,t in [((512,140),'Y'),((884,512),'X')]:dr.text(p,t,font=ImageFont.truetype(MONO,65),fill=WHITE,anchor='mm')
im.save(O/'joystick_print.png')
print('Generated Overclock Instrument: 18 textures.')
