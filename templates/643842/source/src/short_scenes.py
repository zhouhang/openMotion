"""短场景合同、原声时钟和落点证据；不调用模型，也不估算词级时间。"""
from pathlib import Path
import math,re,subprocess,json
KINDS={'seed','apple','carrot','milk','grain','bean','cookie','bar','muffin','circle','square','image'}
EDITORIAL={'label-question':(3,3),'document-focus':(1,1),'spotlight':(1,4),'reveal':(1,6),'inspect':(2,4),'fit':(2,2),'reframe':(2,4),'unpack':(3,6),'routine':(2,3),'origin':(3,3),'selection':(3,5),'calendar':(1,1)}
NEW_KINDS={'package','document','sugar','oil','salt','child','plate','loop','sprout','calendar','bottle','rice','oat','corn'}
VARIANTS={'classify','combine','transform','qualify'}|set(EDITORIAL)

def validate_editorial(s,base,media,sha):
 required={'type','id','variant','duration','title','objects','cues','sourceRefs'}
 if not required<=set(s) or set(s)-required-{'note','caption'}:raise ValueError('短图解字段不符；不接受虚设分类或跨页身份')
 if not isinstance(s['id'],str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,39}',s['id']):raise ValueError('场景id无效')
 if isinstance(s['duration'],bool) or not isinstance(s['duration'],(int,float)) or not math.isfinite(s['duration']) or not 3<=s['duration']<=5:raise ValueError('每页必须3–5秒')
 if not isinstance(s['title'],str) or not 1<=len(s['title'])<=16:raise ValueError('短标题限16字')
 if 'note' in s and (not isinstance(s['note'],str) or not 1<=len(s['note'])<=24):raise ValueError('说明限24字')
 if 'caption' in s and (not isinstance(s['caption'],str) or not 1<=len(s['caption'])<=12):raise ValueError('图解落款限12字')
 if s['variant'] in ('label-question','selection','calendar') and 'caption' not in s:raise ValueError('开场、选择与日历需要本期caption，不能硬编码示例文案')
 lo,hi=EDITORIAL[s['variant']]
 if not isinstance(s['objects'],list) or not lo<=len(s['objects'])<=hi:raise ValueError('当前图解对象容量不符')
 r=json.loads(json.dumps(s,ensure_ascii=False));hashes={};ids=[]
 for obj in r['objects']:
  if not isinstance(obj,dict) or set(obj)!={'id','label','kind'}|({'image'} if obj.get('kind')=='image' else set()):raise ValueError('图解对象字段不符')
  if not isinstance(obj['id'],str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,39}',obj['id']) or obj['id'] in ids:raise ValueError('对象id无效或重复')
  ids.append(obj['id'])
  if not isinstance(obj['label'],str) or not 1<=len(obj['label'])<=8 or obj['kind'] not in KINDS|NEW_KINDS:raise ValueError('对象标签或图形类型无效')
  if obj['kind']=='image':
   path=media(obj['image'],base)
   if path.suffix.lower() not in ('.png','.jpg','.jpeg','.webp'):raise ValueError('只接受静态图片')
   hashes[str(path)]=sha(path);obj['imageUrl']=path.as_uri()
 expected=set(ids) if s['variant'] in ('reveal','routine') else {'main'}
 if not isinstance(s['cues'],dict) or set(s['cues'])!=expected:raise ValueError('图解落点键不符')
 count=math.ceil(s['duration']*24)
 for cue in s['cues'].values():
  if not isinstance(cue,dict) or 'frame' not in cue or set(cue)-{'frame','ref','boundary'}:raise ValueError('动作落点字段不符')
  if isinstance(cue['frame'],bool) or not isinstance(cue['frame'],int) or not 0<=cue['frame']<=count-12:raise ValueError('动作落点越界或阅读时间不足')
  if ('ref' in cue)!=('boundary' in cue) or ('ref' in cue and (isinstance(cue['ref'],bool) or not isinstance(cue['ref'],int) or cue['boundary'] not in ('start','end'))):raise ValueError('必须使用真实句级引用')
 if expected=={'main'} and s['cues']['main']['frame']<16:raise ValueError('完整图解动作至少16帧，不能硬切到结果')
 if not isinstance(s['sourceRefs'],list) or any(isinstance(v,bool) or not isinstance(v,int) or v<1 for v in s['sourceRefs']) or len(set(s['sourceRefs']))!=len(s['sourceRefs']):raise ValueError('原文编号无效')
 return r,hashes

def validate_scene(s,base,media,sha):
 if isinstance(s,dict) and isinstance(s.get('variant'),str) and s['variant'] in EDITORIAL:return validate_editorial(s,base,media,sha)
 required={'type','id','variant','duration','title','groups','objects','product','cues','sourceRefs'}
 if not isinstance(s,dict) or not required<=set(s) or set(s)-required-{'carryFrom','labels'}:raise ValueError('graphic字段不完整或包含未知字段')
 if s['variant'] not in VARIANTS:raise ValueError('未知图形表达动作')
 if not isinstance(s['id'],str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,39}',s['id']):raise ValueError('场景id须为稳定英文标识')
 if isinstance(s['duration'],bool) or not isinstance(s['duration'],(int,float)) or not math.isfinite(s['duration']) or not 3<=s['duration']<=5:raise ValueError('短场景必须为3–5秒，不能用装饰运动重置停留时长')
 if not isinstance(s['title'],str) or not 1<=len(s['title'])<=16:raise ValueError('短场景只使用一个1–16字标题')
 if not isinstance(s['groups'],list) or not 2<=len(s['groups'])<=4:raise ValueError('分类容量2–4组')
 def named(v,extra):
  if not isinstance(v,dict) or set(v)!={'id','label'}|extra:raise ValueError('图形对象字段不符')
  if not isinstance(v['id'],str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,39}',v['id']):raise ValueError('对象id不符')
  if not isinstance(v['label'],str) or not 1<=len(v['label'])<=8:raise ValueError('图形标签最多8字')
 for g in s['groups']:named(g,set())
 gids=[g['id'] for g in s['groups']]
 if len(set(gids))!=len(gids):raise ValueError('分组id重复')
 if not isinstance(s['objects'],list) or not 3<=len(s['objects'])<=9:raise ValueError('图形容量3–9个对象')
 hashes={};r=json.loads(json.dumps(s,ensure_ascii=False))
 if not isinstance(r['product'],dict) or any(not isinstance(obj,dict) for obj in r['objects']):raise ValueError('图形对象必须是带稳定id的对象记录')
 for obj in r['objects']+[r['product']]:
  product=obj is r['product'];extra={'kind'}|(set() if product else {'group'})|({'image'} if obj.get('kind')=='image' else set());named(obj,extra)
  if obj['kind'] not in KINDS or (not product and obj['group'] not in gids):raise ValueError('图形类型或分类归属无效')
  if obj['kind']=='image':
   path=media(obj['image'],base)
   if path.suffix.lower() not in ('.png','.jpg','.jpeg','.webp'):raise ValueError('图形图片只接受静态图片')
   hashes[str(path)]=sha(path);obj['imageUrl']=path.as_uri()
 ids=[o['id'] for o in r['objects']]+[r['product']['id']]
 if len(ids)!=len(set(ids)):raise ValueError('图形对象id重复')
 if any(not any(o['group']==g for o in r['objects']) for g in gids):raise ValueError('分类不能是空容器')
 if any(sum(o['group']==g for o in r['objects'])>3 for g in gids):raise ValueError('每个分类最多3个图形，不能堆叠图标凑容量')
 expected=set(gids) if s['variant']=='classify' else ({'input','main'} if s['variant']=='qualify' else {'main'})
 if s['variant']=='qualify':
  if not isinstance(s.get('labels'),dict) or set(s['labels'])!={'input','result'} or any(not isinstance(v,str) or not 1<=len(v)<=8 for v in s['labels'].values()):raise ValueError('判断场景需要两个最多8字的图形标签')
 if not isinstance(s['cues'],dict) or set(s['cues'])!=expected:raise ValueError('必须绑定当前动作的全部落点')
 count=math.ceil(s['duration']*24)
 for cue in s['cues'].values():
  if not isinstance(cue,dict) or 'frame' not in cue or set(cue)-{'frame','ref','boundary'}:raise ValueError('落点应包含frame，可用ref和boundary引用真实SRT边界')
  if isinstance(cue['frame'],bool) or not isinstance(cue['frame'],int) or not 0<=cue['frame']<=count-12:raise ValueError('落点越界或不足0.5秒阅读停留')
  if ('ref' in cue)!=('boundary' in cue) or ('ref' in cue and (isinstance(cue['ref'],bool) or not isinstance(cue['ref'],int) or cue['boundary'] not in ('start','end'))):raise ValueError('落点引用需要真实SRT编号和start/end')
 if s['variant'] in ('combine','transform') and s['cues']['main']['frame']<24:raise ValueError('组合或变形必须保留至少1秒完整动作窗')
 if s['variant']=='qualify' and not 10<=s['cues']['input']['frame']<s['cues']['main']['frame']-11:raise ValueError('判断反转须先呈现输入，再给结果判断')
 if not isinstance(s['sourceRefs'],list) or any(isinstance(v,bool) or not isinstance(v,int) or v<1 for v in s['sourceRefs']) or len(set(s['sourceRefs']))!=len(s['sourceRefs']):raise ValueError('sourceRefs必须为唯一的原文编号')
 return r,hashes

def transcript(path):
 def seconds(s):
  h,m,tail=s.strip().replace(',','.').split(':');return int(h)*3600+int(m)*60+float(tail)
 rows=[]
 for block in re.split(r'\n\s*\n',Path(path).read_text(encoding='utf-8-sig').replace('\r','').strip()):
  lines=block.splitlines()
  if len(lines)<3 or '-->' not in lines[1]:raise ValueError('SRT需要真实编号与时间范围')
  a,b=lines[1].split('-->');row={'id':int(lines[0]),'start':seconds(a),'end':seconds(b),'text':' '.join(lines[2:])}
  if row['end']<=row['start'] or (rows and (row['start']<rows[-1]['start'] or row['id']<=rows[-1]['id'])):raise ValueError('SRT编号或时间顺序异常')
  rows.append(row)
 return rows

def narration(setting,base,duration,media,probe):
 if not isinstance(setting,dict) or 'source' not in setting or set(setting)-{'source','offset','sourceDuration','srt','gainDb'}:raise ValueError('narration需要source及可选offset/sourceDuration/srt/gainDb')
 path=media(setting['source'],base);meta=probe(path)
 if not any(v['codec_type']=='audio' for v in meta['streams']):raise ValueError('原声输入没有音轨')
 offset=setting.get('offset',0)
 if isinstance(offset,bool) or not isinstance(offset,(int,float)) or not math.isfinite(offset) or offset<0:raise ValueError('原声offset必须为非负秒数')
 span=setting.get('sourceDuration',float(meta['format']['duration'])-offset);gain=setting.get('gainDb',0)
 if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in [span,gain]) or span<=0 or not -12<=gain<=0:raise ValueError('原声区间或音量无效，gainDb只允许-12至0')
 if offset+span>float(meta['format']['duration'])+.002 or abs(math.ceil(span*24)/24-duration)>1e-6:raise ValueError('原声区间不足或与场景总帧数不符，禁止变速补足')
 sr=media(setting['srt'],base) if 'srt' in setting else None
 return dict(path=str(path),offset=offset,span=span,gainDb=gain,srt=str(sr) if sr else None,rows=transcript(sr) if sr else [])

def sequence(scenes,voice,short=True):
 position=0;previous=None;ids=[];ownership=[];cues=[];pages=[]
 rows={r['id']:r for r in voice['rows']} if voice else {}
 for s in scenes:
  length=math.ceil(s['duration']*24)
  if short and length>120:raise ValueError('新制作页面不得超过5秒；旧长场景仅可显式pacing=legacy重放')
  if short and s['type']!='graphic':raise ValueError('新制作使用完整3–5秒graphic场景；旧动作窗不得直接截成短页')
  if s['type']=='graphic':
   if s['id'] in ids:raise ValueError('场景id重复')
   ids.append(s['id'])
   if 'carryFrom' in s:
    if not previous or previous.get('id')!=s['carryFrom'] or (previous.get('variant'),s['variant']) not in [('classify','combine'),('combine','transform'),('transform','qualify')]:raise ValueError('跨页接续必须引用相邻且已声明兼容的动作')
    if previous['objects']!=s['objects'] or previous['groups']!=s['groups'] or previous['product']!=s['product']:raise ValueError('跨页对象身份、图片、标签或分类改变，拒绝伪连续')
   for ref in s['sourceRefs']:
    if not voice or ref not in rows:raise ValueError('原文归属引用缺少对应SRT')
    if rows[ref]['end']<=voice['offset']+position/24 or rows[ref]['start']>=voice['offset']+(position+length)/24:raise ValueError('原文引用与场景没有实际时间交集')
   ownership.extend(s['sourceRefs'])
   for key,cue in s['cues'].items():
    target=voice['offset']+(position+cue['frame'])/24 if voice else (position+cue['frame'])/24
    entry={'scene':s['id'],'cue':key,'frame':position+cue['frame'],'sourceTime':target,'basis':'design'}
    if 'ref' in cue:
     if not voice or cue['ref'] not in rows or cue['ref'] not in s['sourceRefs']:raise ValueError('动作落点没有本场原文依据')
     actual=rows[cue['ref']][cue['boundary']]
     if abs(actual-target)>1/24+.002:raise ValueError('落点未对齐真实句子边界；不可伪装词级对齐')
     entry.update(basis='SRT sentence '+cue['boundary'],ref=cue['ref'],actualSourceTime=actual,errorSeconds=target-actual)
    cues.append(entry)
   pages.append({'id':s['id'],'variant':s['variant'],'startFrame':position,'endFrame':position+length,'duration':length/24,'carryFrom':s.get('carryFrom'),'lastLandingFrame':max(c['frame'] for c in s['cues'].values()),'sourceRefs':s['sourceRefs']})
  position+=length;previous=s
 if voice and rows and short:
  selected=[r['id'] for r in voice['rows'] if r['end']>voice['offset'] and r['start']<voice['offset']+voice['span']]
  if ownership!=selected:raise ValueError('所选原文须全部按序归属且不得重复；不能只写少数关键词')
 return {'pacing':'short' if short else 'legacy','maxPageSeconds':5 if short else None,'pages':pages,'cueEvidence':cues,'sourceUnits':ownership,'alignment':'referenced sentence boundaries; design cues separately labelled; no claimed word alignment' if rows else 'design timing only; no measured source alignment','status':'structural-pass-source-unrecorded-human-review-pending' if voice and not rows else 'structural-pass-semantic-human-review-pending'}

def prepare_audio(v,out,duration):
 subprocess.run(['ffmpeg','-v','error','-ss',str(v['offset']),'-i',v['path'],'-t',str(v['span']),'-map','0:a:0','-af',f'aresample=48000,apad=whole_dur={duration},atrim=duration={duration}','-ac','2','-c:a','pcm_s16le',str(out/'voiceover.wav')],check=True)
