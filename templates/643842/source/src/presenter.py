"""全局口播准备：本地YuNet人脸框、平滑方形裁切、原声及SRT共用源时钟。"""
from pathlib import Path
import json,subprocess,hashlib,math,re,bisect,wave

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')

def validate(setting,base,root,duration,media,probe):
 if not isinstance(setting,dict) or set(setting)-{'source','offset','sourceDuration','srt'} or 'source' not in setting:raise ValueError('presenter需要source，可选offset/sourceDuration/srt')
 path=media(setting['source'],base);meta=probe(path);v=next((s for s in meta['streams'] if s['codec_type']=='video'),None)
 if v is None or not any(s['codec_type']=='audio' for s in meta['streams']):raise ValueError('口播视频须含实际画面与原声')
 offset=setting.get('offset',0)
 if isinstance(offset,bool) or not isinstance(offset,(int,float)) or not math.isfinite(offset):raise ValueError('offset必须是有限秒数')
 span=setting.get('sourceDuration',float(meta['format']['duration'])-offset)
 if any(isinstance(n,bool) or not isinstance(n,(int,float)) or not math.isfinite(n) for n in (offset,span)) or offset<0 or not 5<=span<=180:raise ValueError('本版全程口播支持5–180秒，offset不得为负')
 if abs(math.ceil(span*24)/24-duration)>1e-6:raise ValueError('画面总帧数须与口播原声区间向上取整到24fps一致，不拉伸人声')
 if offset+span>float(meta['format']['duration'])+.001:raise ValueError('口播源区间不足')
 sr=media(setting['srt'],base) if 'srt' in setting else None
 return dict(path=str(path),offset=offset,span=span,meta=meta,srt=str(sr) if sr else None)

def parse_srt(path,offset,span):
 def seconds(s):
  h,m,tail=s.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(tail)
 rows=[]
 for block in re.split(r'\n\s*\n',Path(path).read_text(encoding='utf-8-sig').replace('\r','').strip()):
  lines=block.splitlines();i=next((i for i,line in enumerate(lines) if '-->' in line),None)
  if i is None:continue
  pair=lines[i].split('-->');start=seconds(pair[0].strip());end=seconds(pair[1].strip().split()[0]);text=' '.join(lines[i+1:]).strip()
  if start>=end or (rows and start<rows[-1]['sourceStart']):raise ValueError('SRT时间顺序不符')
  if end>offset and start<offset+span and text:rows.append(dict(start=max(0,start-offset),end=min(span,end-offset),text=text,sourceStart=start,sourceEnd=end))
 return rows

def prepare(setting,out,root,frames):
 import cv2,numpy as np
 source=setting['path'];offset=setting['offset'];span=setting['span'];folder=out/'presenter';folder.mkdir();detect=folder/'detect';detect.mkdir()
 subprocess.run(['ffmpeg','-v','error','-ss',str(offset),'-i',source,'-t',str(span),'-vf','fps=3,scale=640:-2','-q:v','3',str(detect/'%05d.jpg')],check=True)
 model=root/'assets/face_detection_yunet_2026may.onnx';detector=cv2.FaceDetectorYN.create(str(model),'',(640,360),.8,.3,5000);found=[];missing=[];previous=None;raw=[]
 for index,file in enumerate(sorted(detect.glob('*.jpg'))):
  im=cv2.imdecode(np.frombuffer(file.read_bytes(),dtype=np.uint8),1);h,w=im.shape[:2];detector.setInputSize((w,h));faces=detector.detect(im)[1]
  if faces is None:missing.append(index);continue
  candidates=[v for v in faces if v[2]>24 and v[3]>24]
  if not candidates:missing.append(index);continue
  if previous is None:candidates.sort(key=lambda v:v[2]*v[3],reverse=True)
  else:candidates.sort(key=lambda v:((v[0]+v[2]/2)/w-previous[0])**2+((v[1]+v[3]/2)/h-previous[1])**2)
  face=candidates[0];cx=(face[0]+face[2]/2)/w;cy=(face[1]+face[3]/2)/h;side=2.05*max(face[2]/w,face[3]/h*h/w);previous=(cx,cy)
  # side以图像宽度为基准，保留头发、下巴；不做非等比变形。
  value=[cx,cy-.04*face[3]/h,side];found.append([index/3,*value]);raw.append({'t':index/3,'bbox':[float(v) for v in face[:4]],'imageSize':[w,h],'confidence':float(face[-1])})
 total=len(list(detect.glob('*.jpg')))
 if not found or len(found)/max(1,total)<.8:raise ValueError('人脸检测覆盖不足80%，须检查素材或提供更清晰单人口播；不伪装自动裁切成功')
 times=[v[0] for v in found];gaps=[times[0],span-times[-1]]+[b-a for a,b in zip(times,times[1:])]
 if max(gaps)>2:raise ValueError('连续两秒以上无法确认人脸，须人工复核后再制作')
 values=np.array([v[1:] for v in found]);smooth=[]
 for i in range(len(values)):
  med=np.median(values[max(0,i-2):i+3],axis=0)
  if smooth:
   prior=np.array(smooth[-1]);med=prior*.65+med*.35
   for k in [0,1]:
    if abs(med[k]-prior[k])<.0015:med[k]=prior[k]
  smooth.append(med.tolist())
 meta=setting['meta'];vs=next(v for v in meta['streams'] if v['codec_type']=='video');w=960;h=round(vs['height']/vs['width']*w/2)*2
 command=['ffmpeg','-v','error','-ss',str(offset),'-i',source,'-t',str(span),'-vf',f'fps=24,scale={w}:{h},tpad=stop_mode=clone:stop_duration=0.041667','-frames:v',str(frames),'-f','rawvideo','-pix_fmt','bgr24','pipe:1']
 process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE);nbytes=w*h*3;crop_rows=[]
 for f in range(frames):
  chunks=[];remaining=nbytes
  while remaining:
   part=process.stdout.read(remaining)
   if not part:raise ValueError('口播解码帧不足，拒绝循环或长时间补帧')
   chunks.append(part);remaining-=len(part)
  im=np.frombuffer(b''.join(chunks),dtype=np.uint8).reshape(h,w,3);t=f/24;i=max(0,min(len(times)-1,bisect.bisect_right(times,t)-1));j=min(i+1,len(times)-1);p=0 if i==j else max(0,min(1,(t-times[i])/(times[j]-times[i])))
  cx,cy,size=(np.array(smooth[i])*(1-p)+np.array(smooth[j])*p).tolist();side=round(size*w);px=cx*w;py=cy*h;side=max(80,min(side,min(w,h)));px=max(side/2,min(w-side/2,px));py=max(side/2,min(h-side/2,py))
  patch=cv2.getRectSubPix(im,(side,side),(float(px),float(py)));patch=cv2.resize(patch,(240,240),interpolation=cv2.INTER_AREA);success,encoded=cv2.imencode('.jpg',patch,[cv2.IMWRITE_JPEG_QUALITY,93])
  if not success:raise ValueError('人物裁切编码失败')
  (folder/f'{f:05d}.jpg').write_bytes(encoded.tobytes());crop_rows.append({'frame':f,'cx':px/w,'cy':py/h,'sidePixels':side,'scaledSource':[w,h]})
 stderr=process.stderr.read();code=process.wait()
 if code:raise ValueError(stderr.decode(errors='replace'))
 subprocess.run(['ffmpeg','-v','error','-ss',str(offset),'-i',source,'-t',str(span),'-map','0:a:0','-af',f'aresample=48000:async=1:first_pts=0,apad=whole_dur={frames/24},atrim=duration={frames/24}','-ac','2','-c:a','pcm_s16le',str(out/'voiceover.wav')],check=True)
 caps=parse_srt(setting['srt'],offset,span) if setting['srt'] else []
 report={'detector':'local OpenCV YuNet','modelSha256':hashlib.sha256(model.read_bytes()).hexdigest(),'detectedSamples':len(found),'totalSamples':total,'coverage':len(found)/max(1,total),'maxGapSeconds':max(gaps),'rawDetections':raw,'crops':crop_rows,'source':source,'sourceSha256':hashlib.sha256(Path(source).read_bytes()).hexdigest(),'offset':offset,'sourceDuration':span,'outputDuration':frames/24,'fps':24,'frames':frames,'sampleOnly':offset!=0 or abs(span-float(meta['format']['duration']))>.05,'continuousHumanReview':'pending','cropRule':'smoothed square around face; headroom/chin margin; circular clipping at composition; no identity recognition'}
 dump(out/'presenter-track.json',report)
 return {'frameBase':folder.as_uri()+'/','frameCount':frames,'captions':caps,'sourceClock':{'offset':offset,'duration':span,'fps':24},'layout':'auto-circle'},report
