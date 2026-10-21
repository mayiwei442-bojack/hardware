"""Acid Alloy instrument pictograms, based on local config.rs CODEX_KEYS."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json

D=Path(__file__).parent
OUT=D/'textures';OUT.mkdir(exist_ok=True)
FONT='C:/Windows/Fonts/bahnschrift.ttf'
MONO='C:/Windows/Fonts/consolab.ttf'
order=[3,4,8,9,10,11,12,13,14,15,5,6,7]
labels=['ATTN','NEW CHAT','CHAT 1','CHAT 2','CHAT 3','CHAT 4','COMMAND','APPROVE','REJECT','TERMINAL','VOICE','SIDE CHAT','MODEL']
meanings=['下一个需要关注的会话','新建会话','最近会话 1','最近会话 2','最近会话 3','最近会话 4','命令菜单','批准请求','拒绝请求','打开终端','语音输入','打开侧边会话','模型选择']
icons=['告警雷达','新建窗口','会话槽 1','会话槽 2','会话槽 3','会话槽 4','指令轨道','闭合闸门','截断闸门','代码光标','声波采样','分支会话','芯片选择器']
rows=[]
for idx,(sw,label) in enumerate(zip(order,labels),1):
 im=Image.new('RGBA',(768,768));d=ImageDraw.Draw(im)
 c='#f3f1e8' if idx==1 or 3<=idx<=6 or idx in (8,9,10) else '#263943'
 clear=3<=idx<=6
 def line(p,w=13):d.line(p,fill=c,width=w,joint='curve')
 def box(b,w=13):d.rectangle(b,outline=c,width=w)
 def arc(b,a,z,w=13):d.arc(b,a,z,fill=c,width=w)
 def text(p,t,size,anchor='mm',font=MONO):d.text(p,t,font=ImageFont.truetype(font,size),fill=c,anchor=anchor)
 text((123,142),f'K{idx:02d}',56,'lm',FONT)
 text((625,140),'INPUT',27,'rm');line([(120,195),(635,195)],5)
 if clear:
  # Keep the switch stem and activity LED visible through the central area.
  box((105,515,235,600),8);line([(130,600),(130,621),(160,600)],8)
  for n in range(idx-2):d.rectangle((121+n*26,540,133+n*26,574),fill=c)
  text((615,565),label,48,'rm')
 else:
  if idx==1:
   arc((245,215,525,495),35,315);arc((278,248,492,462),55,295,7)
   line([(385,227),(385,365),(463,405)],12)
   d.ellipse((367,347,403,383),fill=c)
   line([(525,254),(525,319)],16);d.ellipse((517,337,533,353),fill=c)
  elif idx==2:
   line([(261,451),(261,260),(443,260)],15)
   line([(302,493),(502,493),(502,356)],15)
   line([(440,240),(440,360)],16);line([(380,300),(500,300)],16)
  elif idx==7:
   for y,w in [(265,135),(355,205),(445,165)]:
    line([(288,y),(288+w,y)],15);box((238,y-15,268,y+15),8)
   line([(525,260),(551,285),(525,310)],9)
  elif idx==8:
   line([(248,255),(248,445),(320,445)],14)
   line([(520,255),(520,445),(448,445)],14)
   line([(248,355),(520,355)],18)
   line([(350,410),(384,444),(442,386)],14)
  elif idx==9:
   line([(248,255),(248,445),(320,445)],14)
   line([(520,255),(520,445),(448,445)],14)
   line([(248,355),(326,355)],18);line([(442,355),(520,355)],18)
   line([(352,285),(416,425)],22)
  elif idx==10:
   line([(265,263),(355,355),(265,447)],20)
   line([(390,444),(520,444)],20)
   line([(237,225),(535,225)],7)
  elif idx==11:
   for x,h in [(252,60),(296,120),(340,205),(384,290),(428,205),(472,120),(516,60)]:line([(x,355-h/2),(x,355+h/2)],17)
   line([(242,505),(315,505)],7);d.ellipse((503,490,525,512),fill=c)
  elif idx==12:
   box((244,240,360,325),11);box((420,405,536,490),11)
   line([(302,325),(302,445),(420,445)],14)
   line([(302,355),(458,355),(458,300)],14)
   line([(432,326),(458,300),(484,326)],12)
  elif idx==13:
   box((290,260,478,448),13)
   for pos in [322,384,446]:
    line([(pos,229),(pos,260)],10);line([(pos,448),(pos,479)],10)
    line([(259,pos-30),(290,pos-30)],10);line([(478,pos-30),(509,pos-30)],10)
   line([(334,331),(370,355),(334,379)],12);line([(397,379),(438,379)],12)
   line([(535,280),(556,305),(535,330)],8)
  line([(132,548),(635,548)],6)
  text((384,611),label,53 if len(label)<9 else 46)
 im.save(OUT/f'key_{sw:02d}.png')
 rows.append({'number':f'{idx:02d}','object':f'SW{sw:02d}_Cap','label':label,'function':meanings[idx-1],'pictogram':icons[idx-1]})
(D/'keyprint_mapping.json').write_text(json.dumps({'source':'device/app/src/config.rs:1153-1167 CODEX_KEYS','profile':'Codex; configurable, Claude Code preset differs','keys':rows},ensure_ascii=False,indent=2),encoding='utf-8')
