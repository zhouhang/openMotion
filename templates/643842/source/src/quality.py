"""时间维度辅助审片。参考huashu-motion的帧差诊断思路，独立实现；不是语义评分。"""
from pathlib import Path
import json,subprocess,statistics,math,argparse

def activity(a,b):
 delta=[abs(x-y) for x,y in zip(a,b)];tiles=[0]*48
 for i,v in enumerate(delta):tiles[(i//96//9)*8+(i%96//12)]+=v
 return sum(delta)/len(delta),max(tiles)/108

def inspect(instance,video=None):
 instance=Path(instance).resolve();plan=json.loads((instance/'plan.json').read_text(encoding='utf-8'));video=Path(video).resolve() if video else instance/'video.mp4'
 process=subprocess.Popen(['ffmpeg','-v','error','-i',str(video),'-vf','scale=96:54,format=gray','-f','rawvideo','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE);frames=[]
 while True:
  data=process.stdout.read(96*54)
  if not data:break
  if len(data)!=96*54:raise ValueError('审片解码帧不完整')
  frames.append(data)
 err=process.stderr.read();code=process.wait()
 if code:raise ValueError(err.decode(errors='replace'))
 if len(frames)!=plan['totalFrames']:raise ValueError('审片帧数与计划不同')
 def difference(a,b):return sum(abs(x-y) for x,y in zip(a,b))/len(a)
 levels=[activity(a,b) for a,b in zip(frames,frames[1:])];diff=[v[0] for v in levels];local=[v[1] for v in levels];pops=[];cuts=[]
 for i in range(1,len(frames)-1):
  if min(diff[i-1],diff[i])>6 and difference(frames[i-1],frames[i+1])<min(diff[i-1],diff[i])/3:pops.append(i)
 for i,value in enumerate(diff):
  neighbourhood=diff[max(0,i-6):i]+diff[i+1:i+7];normal=statistics.median(neighbourhood) if neighbourhood else 0
  if value>14 and value>4*(normal+1) and not any(abs(i+1-p)<2 for p in pops):cuts.append(i+1)
 holds=[];begin=None
 for i,v in enumerate(diff+[math.inf]):
  still=v<.25 and i<len(local) and local[i]<1
  if still and begin is None:begin=i
  elif not still and begin is not None:
   if i-begin>=24:
    for page in plan.get('graphicPages',[]):
     a=max(begin,page['startFrame']);b=min(i,page['endFrame'])
     landing=page['startFrame']+page['lastLandingFrame']
     for lo,hi,meaning in [(a,min(b,landing),'review-before-landing'),(max(a,landing),b,'planned-reading-hold')]:
      if hi-lo>=12:holds.append({'scene':page['id'],'start':round(lo/24,3),'end':round(hi/24,3),'seconds':round((hi-lo)/24,3),'interpretation':meaning})
   begin=None
 curve=[round(statistics.mean(diff[i:i+24]),3) for i in range(0,len(diff),24)]
 result={'frames':len(frames),'pacing':plan.get('pacing','legacy'),'pageDurations':[v['duration'] for v in plan.get('graphicPages',[])],'allShortPagesWithin3to5':all(3<=v['duration']<=5 for v in plan.get('graphicPages',[])) if plan.get('graphicPages') else None,'singleFramePops':[p/24 for p in pops],'hardCuts':[p/24 for p in cuts],'lowMotionIntervals':holds,'motionPerSecond':curve,'localMotionPerSecond':[round(statistics.mean(local[i:i+24]),3) for i in range(0,len(local),24)],'method':'96x54 grayscale global difference plus strongest of 8x6 local tiles, avoiding dilution of small object changes; assists review only','limits':'不能判断信息是否讲清楚；低变化可能是合理阅读，持续装饰也可能毫无意义。3–5秒是本模板路线约束，不是所有影片的通用规律。','humanSemanticAndContinuousReview':'pending'}
 (instance/'temporal-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 maximum=max(curve+[1]);points=' '.join(f'{40+i*720/max(1,len(curve)-1):.1f},{190-v/maximum*145:.1f}' for i,v in enumerate(curve))
 (instance/'motion-curve.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="240" viewBox="0 0 800 240"><rect width="800" height="240" fill="#F8F5F0"/><text x="40" y="27" font-family="sans-serif" font-size="17" fill="#424B50">Motion change per second / diagnostic, not a quality score</text><path d="M40 45 V190 H760" fill="none" stroke="#CBD6D1"/><polyline points="{points}" fill="none" stroke="#718E81" stroke-width="3"/></svg>',encoding='utf-8')
 return result

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('instance');ap.add_argument('--video');a=ap.parse_args();r=inspect(a.instance,a.video);print(json.dumps({'frames':r['frames'],'pageDurations':r['pageDurations'],'pops':len(r['singleFramePops']),'continuousReview':'pending'},ensure_ascii=False))
