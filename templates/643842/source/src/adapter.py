"""媒体场景准备与渲染。包可只读；用户素材与生成帧均放在独立实例。"""
from pathlib import Path
import argparse,json,subprocess,hashlib,importlib.util,sys,math,shutil,os
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def probe(p):return json.loads(subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)],capture_output=True,check=True).stdout)
def media(ref,base):
 if not isinstance(ref,dict) or set(ref)!={'scope','path'} or ref['scope'] not in ('package','instance'):raise ValueError('素材引用应包含scope和相对path')
 root=ROOT if ref['scope']=='package' else base;rel=Path(ref['path'])
 if rel.is_absolute() or rel.drive:raise ValueError('素材路径必须为相对路径')
 p=(root/rel).resolve()
 if not p.is_relative_to(root.resolve()) or not p.is_file():raise ValueError('素材缺失或路径越界: '+ref['path'])
 return p
def validate(p,base):
 if not {'scenes','duration'}<=set(p) or set(p)-{'scenes','duration','presenter','narration','pacing','presentation'} or p.get('pacing','short') not in ('short','legacy') or isinstance(p['duration'],bool) or not isinstance(p['duration'],(int,float)) or not 3<=p['duration']<=400 or not isinstance(p['scenes'],list) or not 1<=len(p['scenes'])<=(32 if p.get('pacing','short')=='short' else 8):raise ValueError('short为1–32个3–5秒场景；legacy显式重放旧合同，duration为3–400秒')
 resolved=[];hashes={}
 common={'type','heading','description','annotation','credit','focus'}
 for s in p['scenes']:
  if s.get('type')=='graphic':
   import short_scenes
   r,h=short_scenes.validate_scene(s,base,media,sha);resolved.append(r);hashes.update(h);continue
  if s.get('type') in ('opening','ending'):
   kind=s['type'];required={'type','duration','title','credit'}|({'subtitle'} if kind=='opening' else {'items'})
   optional={'style','lead'} if kind=='opening' else {'style','logo','brand','tagline'}
   if not required<=set(s) or set(s)-required-optional:raise ValueError('开头或结尾字段不符')
   for key,limit in [('title',28 if kind=='opening' else 16),('subtitle',32),('credit',90),('lead',6),('brand',12),('tagline',24)]:
    if key in s and (not isinstance(s[key],str) or len(s[key])>limit or (key in ('title','lead','brand') and not s[key].strip())):raise ValueError('开头结尾文案超容量: '+key)
   r=dict(s)
   if kind=='opening':
    choices=('auto','lead-word-zoom-assemble','title-demote-to-label');count=len(''.join(s['title'].split()))
    if s.get('style','auto') not in choices:raise ValueError('未知开场样式')
    selected=('lead-word-zoom-assemble' if count<=12 else 'title-demote-to-label') if s.get('style','auto')=='auto' else s['style']
    if selected=='lead-word-zoom-assemble' and (not s.get('lead') or s['lead'] not in s['title']):raise ValueError('短标题请绑定标题中1–6字的核心词')
    r['variant']=selected;r['selectionReason']=f'标题去空白后{count}字；12字为自动选择边界'
    low,high=5,8
   else:
    if not isinstance(s['items'],list) or not 1<=len(s['items'])<=4 or any(not isinstance(v,str) or not 1<=len(v)<=18 for v in s['items']):raise ValueError('总结需要1–4项，每项最多18字')
    if s.get('style','auto') not in ('auto','list-reveal','ui-to-brand-morph'):raise ValueError('未知结尾样式')
    selected=('ui-to-brand-morph' if 'logo' in s else 'list-reveal') if s.get('style','auto')=='auto' else s['style']
    if 'logo' in s:
     if not s.get('brand'):raise ValueError('Logo收尾须提供品牌名称')
     _,logo_hashes=validate({'pacing':'legacy','duration':6,'scenes':[{'type':'brand','duration':6,'logo':s['logo'],'name':s['brand'],'tagline':'品牌收尾','credit':s['credit']}]},base);hashes.update(logo_hashes);r['_path']=str(media(s['logo'],base))
    if selected=='ui-to-brand-morph' and 'logo' not in s:raise ValueError('品牌变形结尾需要实际Logo，缺失不能伪造')
    r['variant']=selected;r['selectionReason']='有实际Logo与品牌名' if selected=='ui-to-brand-morph' else '采用文字要点总结'
    low,high=(10,12) if selected=='ui-to-brand-morph' else (6,12)
   if isinstance(s['duration'],bool) or not isinstance(s['duration'],(int,float)) or not math.isfinite(s['duration']) or not low<=s['duration']<=high:raise ValueError(f'{r["variant"]}时长为{low}–{high}秒')
   resolved.append(r);continue
  if s.get('type')=='explainer':
   if set(s)-{'type','content','captions','voiceover'} or not {'type','content','captions'}<=set(s):raise ValueError('文字讲解模块字段不符')
   schema=read(ROOT/'explainer-params.schema.json')['properties']['content']['properties']
   if not isinstance(s['content'],dict) or set(s['content'])!=set(schema):raise ValueError('文字讲解须提供完整35项文案')
   for key,value in s['content'].items():
    if not isinstance(value,str) or not 1<=len(value)<=schema[key]['maxLength']:raise ValueError('文字讲解文案超容量: '+key)
   if not isinstance(s['captions'],list) or len(s['captions'])>80:raise ValueError('文字讲解字幕限80条')
   last=0
   for cap in s['captions']:
    if not isinstance(cap,dict) or set(cap)!={'start','end','text'} or not isinstance(cap['text'],str) or not 1<=len(cap['text'])<=32:raise ValueError('字幕字段或字数不符')
    if any(isinstance(cap[k],bool) or not isinstance(cap[k],(int,float)) or not math.isfinite(cap[k]) for k in ['start','end']) or not last<=cap['start']<cap['end']<=1045/24:raise ValueError('字幕时间越界或重叠')
    last=cap['end']
   r=dict(s);r['duration']=1045/24
   if 'voiceover' in s:
    path=media(s['voiceover'],base);meta=probe(path)
    if not any(v['codec_type']=='audio' for v in meta['streams']) or abs(float(meta['format']['duration'])-1045/24)>.06:raise ValueError('讲解原声须为43.54秒，不截短或变速适配')
    hashes[str(path)]=sha(path);r['_path']=str(path)
   resolved.append(r);continue
  kind=s.get('type');allowed={'brand':{'type','duration','logo','name','tagline','credit'},'image':common|{'duration','image'},'image-wall':common|{'duration','images','selectedIndex'},'page-waterfall-wall':{'type','duration','images','columns','speed','heading','description','annotation','credit'},'video':common|{'video','offset','sourceDuration','freezeAt','freezeDuration','audioMode'}}.get(kind)
  if allowed is None or set(s)!=allowed:raise ValueError('场景字段不符: '+str(kind))
  for key,maxlen in [('credit',90),('name',12),('tagline',22),('description',18),('annotation',12)]:
   if key in s and (not isinstance(s[key],str) or len(s[key])>maxlen or (key!='credit' and not s[key])):raise ValueError('文案超容量: '+key)
  if kind!='brand':
   if not isinstance(s['heading'],list) or not 1<=len(s['heading'])<=2 or any(not isinstance(v,str) or not 1<=len(v)<=8 for v in s['heading']):raise ValueError('标题限两行，每行8字')
  if kind not in ('brand','page-waterfall-wall'):
   r=s['focus']
   if not isinstance(r,list) or len(r)!=4 or any(not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v) for v in r) or not 0<=r[0]<1 or not 0<=r[1]<1 or not .04<=r[2]<=1 or not .04<=r[3]<=1 or r[0]+r[2]>1 or r[1]+r[3]>1:raise ValueError('焦点矩形越界或过小')
  if kind in ('image-wall','page-waterfall-wall'):
   low,high=(6,9) if kind=='image-wall' else (12,60)
   if not isinstance(s['images'],list) or not low<=len(s['images'])<=high:raise ValueError(f'图片容量为{low}–{high}张')
   if kind=='image-wall':
    if not isinstance(s['selectedIndex'],int) or isinstance(s['selectedIndex'],bool) or not 0<=s['selectedIndex']<len(s['images']):raise ValueError('选中图片序号越界')
   else:
    if isinstance(s['columns'],bool) or not isinstance(s['columns'],int) or not 4<=s['columns']<=6:raise ValueError('瀑布墙列数为4–6')
    if isinstance(s['speed'],bool) or not isinstance(s['speed'],(int,float)) or not .6<=s['speed']<=1.6:raise ValueError('瀑布墙速度倍率为0.6–1.6')
   low,high=(16,22) if kind=='image-wall' else (12,30)
   if isinstance(s['duration'],bool) or not isinstance(s['duration'],(int,float)) or not low<=s['duration']<=high:raise ValueError(f'场景时长为{low}–{high}秒')
   paths=[media(ref,base) for ref in s['images']]
   for image_path in paths:
    meta=probe(image_path);v=next((v for v in meta['streams'] if v['codec_type']=='video'),None)
    if image_path.suffix.lower() not in ('.jpg','.jpeg','.png','.webp') or v is None or v['width']<1 or v['height']<1:raise ValueError('图片墙只接受可解码静态图片')
    hashes[str(image_path)]=sha(image_path)
   if kind=='page-waterfall-wall' and len({hashes[str(v)] for v in paths})!=len(paths):raise ValueError('瀑布墙输入须为不同图片，不用重复文件凑数量；展示循环由场景负责')
   r=dict(s);r['_paths']=[str(v) for v in paths];resolved.append(r);continue
  field={'brand':'logo','image':'image','video':'video'}[kind];path=media(s[field],base)
  if path.suffix.lower()=='.svg' and kind=='brand':
   import xml.etree.ElementTree as ET
   if path.stat().st_size>2*1024*1024:raise ValueError('SVG超出容量')
   tree=ET.parse(path);node=tree.getroot()
   if node.tag.split('}')[-1]!='svg':raise ValueError('不是SVG')
   for el in node.iter():
    if el.tag.split('}')[-1] in ('script','foreignObject'):raise ValueError('SVG不接受脚本或外部文档')
    for key,value in el.attrib.items():
     if key.split('}')[-1]=='href' and not value.startswith(('#','data:')):raise ValueError('SVG含外部依赖，请先自包含化')
   meta={'streams':[{'codec_type':'video','width':1,'height':1}]}
  else:meta=probe(path)
  v=next((v for v in meta['streams'] if v['codec_type']=='video'),None)
  if v is None or v['width']<1 or v['height']<1:raise ValueError('素材无法解码')
  r=dict(s);r['_path']=str(path);hashes[str(path)]=sha(path)
  if kind in ('brand','image'):
   low,high=(6,10) if kind=='brand' else (8,14)
   if not isinstance(s['duration'],(int,float)) or not math.isfinite(s['duration']) or not low<=s['duration']<=high:raise ValueError('场景时长越界')
  else:
   for key in ['offset','sourceDuration','freezeAt','freezeDuration']:
    if not isinstance(s[key],(int,float)) or not math.isfinite(s[key]):raise ValueError('视频时间必须为有限数字')
   if not 6<=s['sourceDuration']<=12 or not 1<=s['freezeDuration']<=4 or not 1<=s['freezeAt']<=s['sourceDuration']-1 or s['offset']<0:raise ValueError('视频动作窗不满足容量')
   if float(meta['format']['duration'])+1/24<s['offset']+s['sourceDuration']:raise ValueError('视频区间不足，不循环补足')
   if s['audioMode'] not in ('mute','source'):raise ValueError('audioMode仅支持mute/source')
   if s['audioMode']=='source' and not any(v['codec_type']=='audio' for v in meta['streams']):raise ValueError('请求原声但素材没有音轨')
   r['duration']=s['sourceDuration']+s['freezeDuration']
  resolved.append(r)
 total=sum(math.ceil(s['duration']*24) for s in resolved)/24
 if abs(total-p['duration'])>1e-6:raise ValueError('duration须等于场景逐帧取整后的合计时长；不隐式拉伸')
 import short_scenes
 voice=short_scenes.narration(p['narration'],base,total,media,probe) if 'narration' in p else None
 if voice:
  if 'presenter' in p or any(s.get('voiceover') or s.get('audioMode')=='source' for s in resolved):raise ValueError('独立原声、人物原声与素材原声不可重复绑定')
  for path in [voice['path'],voice['srt']]:
   if path:hashes[path]=sha(path)
 short_scenes.sequence(resolved,voice,p.get('pacing','short')=='short')
 if 'presenter' in p:
  import presenter
  setting=presenter.validate(p['presenter'],base,ROOT,total,media,probe)
  if any(s.get('voiceover') or s.get('audioMode')=='source' for s in resolved):raise ValueError('全程口播模式使用唯一原声；讲解配音或素材原声请勿重复绑定')
  for path in [setting['path'],setting['srt']]:
   if path:hashes[path]=sha(path)
 if 'presentation' in p:
  if 'presenter' in p:raise ValueError('presentation人物卡片与旧圆窗presenter不可同时启用')
  import presentation
  hashes.update(presentation.validate(p['presentation'],base,resolved,total,media,probe,sha,bool(voice)))
 return resolved,hashes
def prepare(input_path,out):
 input_path=Path(input_path).resolve();base=input_path.parent;out=Path(out).resolve()
 if out.exists():raise ValueError('输出实例已存在，请另存')
 p=read(input_path);scenes,hashes=validate(p,base);out.mkdir(parents=True)
 total=0;events=[];audio_scenes=[];captions=[]
 for i,s in enumerate(scenes):
  s['startFrame']=total;s['endFrame']=total+math.ceil(s['duration']*24);s['duration']=(s['endFrame']-total)/24
  path=Path(s.pop('_path')) if '_path' in s else None
  if s['type']=='graphic':
   local=[]
   for cue in s['cues'].values():events.append({'frame':total+cue['frame'],'durationFrames':10,'kind':'soft','gain':.35})
  elif s['type'] in ('opening','ending'):
   local=[]
   if path:s['logoUrl']=path.as_uri()
  elif s['type']=='explainer':
   local=[]
   for event in read(ROOT/'explainer-contracts.json')['soundEvents']:events.append(dict(event,frame=total+event['frame']))
   captions.extend(dict(cap,start=total/24+cap['start'],end=total/24+cap['end']) for cap in s['captions'])
   if path:audio_scenes.append((s,str(path),i))
  elif s['type']=='brand':s['logoUrl']=path.as_uri();local=[1,3.1,4.4]
  elif s['type']=='image':s['imageUrl']=path.as_uri();local=[0,2.1,3.3,s['duration']-1.8]
  elif s['type']=='image-wall':s['imageUrls']=[Path(v).as_uri() for v in s.pop('_paths')];local=[0,2.8,3.8,7,8.4,s['duration']-4,s['duration']-2]
  elif s['type']=='page-waterfall-wall':s['imageUrls']=[Path(v).as_uri() for v in s.pop('_paths')];local=[0,1.2,3,6,s['duration']-1.2]
  else:
   frames=out/f'video-{i:02}';frames.mkdir();count=math.ceil(s['sourceDuration']*24)
   subprocess.run(['ffmpeg','-v','error','-i',str(path),'-ss',str(s['offset']),'-t',str(s['sourceDuration']),'-vf','fps=24,scale=960:540:force_original_aspect_ratio=decrease,setsar=1','-frames:v',str(count),'-q:v','2',str(frames/'%05d.jpg')],check=True)
   files=sorted(frames.glob('*.jpg'))
   if len(files)!=count:raise ValueError('视频帧数不足，拒绝静默补帧')
   s['frames']=[f.as_uri() for f in files];local=[0,s['freezeAt'],s['freezeAt']+.3,s['freezeAt']+s['freezeDuration']]
   if s['audioMode']=='source':audio_scenes.append((s,str(path),i))
  for t in local:
   event={'frame':total+round(t*24),'durationFrames':12,'kind':'paper' if t==0 else 'tap'}
   if s['type']=='page-waterfall-wall' and t!=0:event['gain']=0
   events.append(event)
  total=s['endFrame']
 duration=total/24
 plan={'duration':duration,'fps':24,'totalFrames':total,'mode':'voiceover' if audio_scenes else 'content','captions':captions,'scenes':[{'id':s['type'],'startFrame':s['startFrame'],'endFrame':s['endFrame'],'protectedFrames':24,'cueFrames':([0,65,270,468,657,1044] if s['type']=='explainer' else [12,48,72,96,120])} for s in scenes],'soundEvents':events,'frozenFiles':{str(f.relative_to(ROOT)).replace('\\','/'):sha(f) for f in (ROOT/'src').glob('*') if f.is_file()},'assetHashes':hashes}
 resolved={'scenes':scenes,'music':{'mode':'none'},'assets':hashes}
 import short_scenes
 voice=short_scenes.narration(p['narration'],base,duration,media,probe) if 'narration' in p else None
 pacing_report=short_scenes.sequence(scenes,voice,p.get('pacing','short')=='short');dump(out/'pacing-check.json',pacing_report)
 plan['pacing']=p.get('pacing','short');plan['graphicPages']=pacing_report['pages']
 for s,ps in zip(scenes,plan['scenes']):
  if s['type']=='graphic':ps.update(id=s['id'],cueFrames=sorted({cue['frame'] for cue in s['cues'].values()}))
 if voice:
  short_scenes.prepare_audio(voice,out,duration);plan['mode']='voiceover';plan['captions']=[];plan['masterGainDb']=voice['gainDb']
  plan['source']={'path':voice['path'],'offset':voice['offset'],'duration':voice['span'],'sha256':hashes[voice['path']]};resolved['narration']={'offset':voice['offset'],'duration':voice['span'],'subtitleMode':'none','gainDb':voice['gainDb']}
  dump(out/'content-evidence.json',{'source':plan['source'],'sourceUnits':[r for r in voice['rows'] if r['id'] in pacing_report['sourceUnits']],'cues':pacing_report['cueEvidence'],'subtitlesRendered':False})
 if audio_scenes:
  args=['ffmpeg','-v','error'];filters=[];labels=[]
  for idx,(s,path,i) in enumerate(audio_scenes):
   if s['type']=='explainer':
    delay=round(s['startFrame']/24*48000);args+=['-i',path]
    filters.append(f'[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={s["duration"]},atrim=duration={s["duration"]},asetpts=PTS-STARTPTS,adelay={delay}S|{delay}S,apad=whole_dur={duration}[v{idx}]');labels.append(f'[v{idx}]');continue
   args+=['-i',path];offset=s['offset'];freeze=s['freezeAt'];length=s['sourceDuration'];delay=round(s['startFrame']/24*1000)
   filters += [f'[{idx}:a]asplit=2[a{idx}][b{idx}]',f'[a{idx}]atrim=start={offset}:end={offset+freeze},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,apad=pad_dur={s["freezeDuration"]}[p{idx}]',f'[b{idx}]atrim=start={offset+freeze}:end={offset+length},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[q{idx}]',f'[p{idx}][q{idx}]concat=n=2:v=0:a=1,adelay={delay}|{delay},apad=whole_dur={duration}[v{idx}]'];labels.append(f'[v{idx}]')
  filters.append(''.join(labels)+f'amix=inputs={len(labels)}:normalize=0:duration=longest[out]')
  subprocess.run(args+['-filter_complex',';'.join(filters),'-map','[out]','-t',str(duration),'-c:a','pcm_s16le',str(out/'voiceover.wav')],check=True)
 if 'presenter' in p:
  import presenter
  setting=presenter.validate(p['presenter'],base,ROOT,duration,media,probe)
  resolved['presenter'],track=presenter.prepare(setting,out,ROOT,total)
  plan['mode']='voiceover';plan['captions']=resolved['presenter']['captions']
  if plan['captions']:
   for s in scenes:
    if s['type']=='explainer':s['captions']=[]
 if 'presentation' in p:
  import presentation
  resolved['presentation'],report=presentation.prepare(p['presentation'],base,out,ROOT,total,voice,media,probe)
  plan['output']={'width':1920,'height':1080} if resolved['presentation']['resolution']=='1080p' else {'width':1280,'height':720}
  dump(out/'editorial-presenter.json',report)
 spec=importlib.util.spec_from_file_location('sfx',ROOT/'src/audio.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.synth(plan,out/'sfx.wav')
 dump(out/'plan.json',plan);dump(out/'resolved.json',resolved);dump(out/'media-contract-check.json',{'assets':hashes,'mediaAudio':'unique presenter original audio' if 'presenter' in resolved else ('source with silent freeze gap' if audio_scenes else 'explicitly muted'),'duration':duration,'frames':total,'sourceLoops':False,'focus':'presenter uses local face localization; other media uses explicitly bound focus rectangles' if 'presenter' in resolved else '人工绑定的归一化矩形，不声称自动识别或目标跟踪'})
 print(out)
def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True);p=sub.add_parser('plan');p.add_argument('inputs');p.add_argument('instance');r=sub.add_parser('render');r.add_argument('instance');r.add_argument('--playwright-module',default='playwright');r.add_argument('--browser');a=ap.parse_args()
 if a.cmd=='plan':prepare(a.inputs,a.instance)
 else:
  instance=Path(a.instance).resolve();plan=read(instance/'plan.json')
  for p,h in plan['assetHashes'].items():
   if sha(p)!=h:raise ValueError('原素材已变更，须重新规划')
  command=['node',str(ROOT/'src/render.mjs'),'--instance',str(instance),'--playwright-module',a.playwright_module]
  if a.browser:command+=['--browser',a.browser]
  subprocess.run(command,check=True)
  if plan.get('pacing')=='short':
   import quality
   quality.inspect(instance)
if __name__=='__main__':main()
