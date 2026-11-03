"""可选编辑式人物卡片；源素材留在实例，不进入作者包。"""
from pathlib import Path
import math,subprocess,json

FIELDS={'mode','resolution','heading','footer','roleLabel','nameLabel','logo','portraitSize','pageLabels','videos'}
def finite(v):return not isinstance(v,bool) and isinstance(v,(int,float)) and math.isfinite(v)

def validate(setting,base,scenes,duration,media,probe,sha,has_voice):
 if not isinstance(setting,dict) or set(setting)-FIELDS or setting.get('mode')!='editorial-card':raise ValueError('presentation.mode应为editorial-card，禁止未知字段')
 if any(s['type']!='graphic' for s in scenes):raise ValueError('editorial-card仅适配graphic短场景；其余原有场景仍走未设置presentation的原入口')
 if setting.get('resolution','1080p') not in ('720p','1080p'):raise ValueError('输出只支持720p/1080p')
 for key,maximum in [('heading',16),('footer',40),('roleLabel',26),('nameLabel',24)]:
  if key in setting and (not isinstance(setting[key],str) or len(setting[key])>maximum):raise ValueError(key+'超容量')
 labels=setting.get('pageLabels',[])
 if not isinstance(labels,list) or labels and (len(labels)!=len(scenes) or any(not isinstance(v,str) or len(v)>8 for v in labels)):raise ValueError('pageLabels须为空或逐页对应，每项最多8字')
 size=setting.get('portraitSize',[256,356])
 if not isinstance(size,list) or len(size)!=2 or any(isinstance(v,bool) or not isinstance(v,int) for v in size) or not 180<=size[0]<=266 or not 260<=size[1]<=366:raise ValueError('portraitSize范围为宽180–266、高260–366逻辑像素，图片等比cover裁切')
 hashes={}
 if 'logo' in setting:
  p=media(setting['logo'],base)
  if p.suffix.lower() not in ('.png','.jpg','.jpeg','.webp','.svg'):raise ValueError('Logo格式无效')
  hashes[str(p)]=sha(p)
 videos=setting.get('videos',[])
 if not isinstance(videos,list) or len(videos)>64:raise ValueError('videos最多64段')
 automatic=[('at' not in v) for v in videos if isinstance(v,dict)]
 if any(automatic) and not all(automatic):raise ValueError('视频定位须全部自动或全部显式at，不能混用')
 if any(automatic) and not has_voice:raise ValueError('自动匹配人物需要独立narration原声；也可提供明确at')
 for v in videos:
  if not isinstance(v,dict) or 'source' not in v or set(v)-{'source','at','offset','sourceDuration','crop'}:raise ValueError('人物分段字段无效')
  p=media(v['source'],base);meta=probe(p)
  if not any(s['codec_type']=='video' for s in meta['streams']):raise ValueError('人物素材没有视频流')
  offset=v.get('offset',0);span=v.get('sourceDuration',float(meta['format']['duration'])-offset)
  if not finite(offset) or not finite(span) or offset<0 or span<=0 or offset+span>float(meta['format']['duration'])+.002:raise ValueError('人物源区间不足，禁止循环补齐')
  if 'at' in v and (not finite(v['at']) or v['at']<0 or v['at']>=duration):raise ValueError('人物at应位于全片区间')
  crop=v.get('crop','auto')
  if crop!='auto' and (not isinstance(crop,dict) or set(crop)!={'cx','cy','width','height'} or any(not finite(x) or not 0<x<=1 for x in crop.values()) or crop['cx']-crop['width']/2<0 or crop['cx']+crop['width']/2>1 or crop['cy']-crop['height']/2<0 or crop['cy']+crop['height']/2>1):raise ValueError('crop应为auto或位于画面内的归一化cx/cy/width/height')
  hashes[str(p)]=sha(p)
 return hashes

def audio(path,offset=0,span=None):
 import numpy as np
 args=['ffmpeg','-v','error','-ss',str(offset),'-i',str(path)]
 if span is not None:args+=['-t',str(span)]
 return np.frombuffer(subprocess.check_output(args+['-vn','-ac','1','-ar','8000','-f','f32le','-']),np.float32).copy()

def prepare(setting,base,out,root,frames,voice,media,probe):
 import numpy as np
 from PIL import Image,ImageOps
 config=dict(setting);config.pop('videos',None)
 config.update(resolution=setting.get('resolution','1080p'),portraitSize=setting.get('portraitSize',[256,356]))
 if 'logo' in config:config['logoUrl']=media(config.pop('logo'),base).as_uri()
 videos=setting.get('videos',[])
 if not videos:return config,{'mode':'no-presenter','warning':'人物输入区仅为明确示意，不冒充真人'}
 import cv2
 reference=audio(out/'voiceover.wav') if voice else None
 clips=[]
 for number,item in enumerate(videos):
  path=media(item['source'],base);meta=probe(path);vs=next(s for s in meta['streams'] if s['codec_type']=='video');offset=item.get('offset',0);span=item.get('sourceDuration',float(meta['format']['duration'])-offset)
  at=item.get('at');score=None
  if at is None:
   a=audio(path,offset,span);n=len(reference);m=len(a);count=1<<(n+m-2).bit_length()
   match=np.fft.irfft(np.fft.rfft(reference,count)*np.fft.rfft(a[::-1],count),count)[:n+m-1]
   lag=int(np.argmax(match)-(m-1));lo=max(0,lag);ao=max(0,-lag);length=min(n-lo,m-ao)
   if length<min(m,8000)*.8:raise ValueError('人物语音没有足够匹配区间')
   score=float(np.corrcoef(reference[lo:lo+length],a[ao:ao+length])[0,1])
   if not math.isfinite(score) or score<.95:raise ValueError('人物语音与原声匹配不足95%，请提供正确分段或明确at')
   at=lag/8000
  cap=cv2.VideoCapture(str(path));detection=[];sample_count=0
  if item.get('crop','auto')=='auto':
   detector=cv2.FaceDetectorYN.create(str(root/'assets/face_detection_yunet_2026may.onnx'),'',(640,360),.7,.3,5000)
   for t in np.arange(.1,span,.5):
    cap.set(cv2.CAP_PROP_POS_MSEC,(offset+t)*1000);ok,im=cap.read();sample_count+=1
    if not ok:continue
    scaled=cv2.resize(im,(640,round(im.shape[0]*640/im.shape[1])));detector.setInputSize((scaled.shape[1],scaled.shape[0]));faces=detector.detect(scaled)[1]
    if faces is not None:
     f=max(faces,key=lambda x:x[2]*x[3]);detection.append([float(t),*[float(x)*vs['width']/640 for x in f[:4]]])
   if len(detection)/max(1,sample_count)<.8:raise ValueError('人脸检测覆盖不足80%，请提供可复核的明确crop；不能冒充跟踪成功')
   times=[v[0] for v in detection]
   if max([times[0],span-times[-1]]+[b-a for a,b in zip(times,times[1:])])>2:raise ValueError('超过两秒失去人脸，须检查素材')
   x,y,w,h=np.median(np.array([r[1:] for r in detection]),axis=0);height=min(vs['height'],h*2.4);width=min(vs['width'],height*768/1056);cx=x+w/2;cy=y+h*.8
   x=max(0,min(vs['width']-width,cx-width/2));y=max(0,min(vs['height']-height,cy-height/2))
  else:
   crop=item['crop'];width=crop['width']*vs['width'];height=crop['height']*vs['height'];x=crop['cx']*vs['width']-width/2;y=crop['cy']*vs['height']-height/2
  cap.release();clips.append({'source':str(path),'offset':offset,'span':span,'at':at,'correlation':score,'crop':[round(x),round(y),round(width),round(height)],'detectionSamples':len(detection),'sampleCount':sample_count})
 duration=frames/24
 if any(b['at']<a['at']+a['span']-.06 for a,b in zip(clips,clips[1:])):raise ValueError('人物分段重叠或顺序不符')
 gaps=[max(0,clips[0]['at']),max(0,duration-clips[-1]['at']-clips[-1]['span'])]+[max(0,b['at']-a['at']-a['span'])/2 for a,b in zip(clips,clips[1:])]
 if max(gaps)>.25:raise ValueError('人物画面存在超过0.25秒的未覆盖区间，拒绝冻帧或循环补长')
 folder=out/'editorial-presenter';folder.mkdir();cuts=[(a['at']+a['span']+b['at'])/2 for a,b in zip(clips,clips[1:])]
 caps=[cv2.VideoCapture(v['source']) for v in clips];rates=[v.get(cv2.CAP_PROP_FPS) for v in caps];indices=[-1]*len(clips);images=[None]*len(clips)
 scale=1.5 if config['resolution']=='1080p' else 1;pw,ph=[round(v*scale) for v in config['portraitSize']]
 yy,xx=np.mgrid[:ph,:pw];protect=np.exp(-(((xx-pw*.5)/(pw*.38))**4+((yy-ph*.48)/(ph*.49))**4)*1.8)[:,:,None]
 for f in range(frames):
  t=f/24;i=sum(t>=cut for cut in cuts);clip=clips[i];local=max(0,min(clip['span']-1/rates[i],t-clip['at']));index=round((clip['offset']+local)*rates[i])
  while indices[i]<index:
   ok,im=caps[i].read()
   if not ok:raise ValueError('人物视频提前结束；禁止用长冻帧掩盖缺失')
   images[i]=im;indices[i]+=1
  x,y,w,h=clip['crop'];patch=Image.fromarray(cv2.cvtColor(images[i][y:y+h,x:x+w],cv2.COLOR_BGR2RGB));patch=ImageOps.fit(patch,(pw,ph),method=Image.Resampling.LANCZOS)
  arr=np.array(patch,dtype=np.float32);gray=cv2.cvtColor(arr.astype(np.uint8),cv2.COLOR_RGB2GRAY)[:,:,None];muted=(arr*.45+gray*.55)*.88+np.array([232,244,240])[None,None,:]*.12;muted=cv2.GaussianBlur(muted.astype(np.float32),(0,0),2.3*scale)
  patch=Image.fromarray((arr*protect+muted*(1-protect)).clip(0,255).astype(np.uint8));patch.save(folder/f'{f:05d}.jpg',quality=94)
 for cap in caps:cap.release()
 config['frameBase']=folder.as_uri()+'/';config['frameCount']=frames
 return config,{'mode':'auto-waveform' if any(v['correlation'] is not None for v in clips) else 'explicit-at','clips':clips,'maxPauseExtension':max(gaps),'frames':frames,'cropMethod':'per-clip median face localization or explicit fixed crop; not motion tracking','humanLipSyncReview':'pending'}
