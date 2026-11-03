"""独立音效按输出帧编排，旁白和音乐使用全局时钟。"""
import wave,array,math,random,subprocess,json,sys
from pathlib import Path
def synth(plan,out):
    sr=48000;count=math.ceil(plan['duration']*sr);samples=array.array('f',[0])*count;rng=random.Random(43)
    for event in plan['soundEvents']:
        start=round(event['frame']/24*sr);seconds=event['durationFrames']/24;length=round(seconds*sr);sm=0
        for j in range(min(length,count-start)):
            u=j/sr;sm=.88*sm+.12*rng.uniform(-1,1)
            if event['kind']=='collapse':v=(sm*.15+math.sin(2*math.pi*85*u)*.035)*math.exp(-u*6)*min(1,u/.008)
            elif event['kind']=='explode':v=(sm*.24+math.sin(2*math.pi*65*u)*.05)*math.exp(-u*8)*min(1,u/.006)
            else:v=sm*.055*math.sin(math.pi*u/seconds)**2
            samples[start+j]+=v
    pcm=array.array('h');
    for v in samples:
        n=round(max(-.98,min(.98,v))*32767);pcm.extend([n,n])
    if sys.byteorder!='little':pcm.byteswap()
    with wave.open(str(out),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes(pcm.tobytes())
def prepare(plan,inputs,base,out):
    synth(plan,out/'sfx.wav');report={'music':inputs.get('music',{}).get('mode','pending'),'voiceoverSamples':None}
    if plan['mode']=='voiceover':
        subprocess.run(['ffmpeg','-v','error','-i',plan['source']['voiceover'],'-map','0:a:0','-af','aresample=48000:async=1:first_pts=0','-ac','2','-c:a','pcm_s16le',str(out/'voiceover.wav')],check=True)
        with wave.open(str(out/'voiceover.wav'),'rb') as w:
            count=w.getnframes();raw=w.readframes(count);rate=w.getframerate()
        samples=array.array('h');samples.frombytes(raw)
        if not any(samples):raise ValueError('原声解码为全零，拒绝冒充口播成功')
        report['voiceoverSamples']=count;report['voiceoverDuration']=count/rate;report['voiceoverPeak']=max(abs(x) for x in samples)/32768
        if abs(count/rate-plan['source']['duration'])>.06:raise ValueError('解码原声时长与计划时钟不一致')
    music=inputs.get('music',{'mode':'pending'})
    if music.get('mode')=='track':
        src=(base/music['path']).resolve();q=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(src)],capture_output=True,check=True);duration=float(json.loads(q.stdout)['format']['duration']);offset=float(music.get('offset',0))
        if offset<0 or duration-offset<plan['duration']:raise ValueError('配乐不足完整片长，不循环或静默截断')
        subprocess.run(['ffmpeg','-v','error','-ss',str(offset),'-i',str(src),'-t',str(plan['duration']),'-ac','2','-ar','48000','-c:a','pcm_s16le',str(out/'music.wav')],check=True)
    elif music.get('mode') not in ['none','pending']:raise ValueError('music.mode仅支持track/none/pending')
    (out/'audio-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
