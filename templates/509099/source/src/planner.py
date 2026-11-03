"""按语义选择场景，以真实字幕边界绑定时钟；不改写或裁短原声。"""
from pathlib import Path
import json, math, re, hashlib, subprocess
FPS=24
RICH={"expansion","route-choice","object-flow","collapse","explode"}
ROOT=Path(__file__).resolve().parent.parent
def frames(t):return math.ceil(float(t)*FPS-1e-8)
def probe(p):
    q=subprocess.run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)],capture_output=True,check=True)
    return json.loads(q.stdout)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_srt(p):
    raw=Path(p).read_text(encoding='utf-8-sig').replace('\r\n','\n');rows=[]
    def sec(v):
        h,m,s=re.split('[:,.]',v)[:3];mill=re.split('[:,.]',v)[3];return int(h)*3600+int(m)*60+int(s)+int(mill)/1000
    for block in re.split(r'\n\s*\n',raw.strip()):
        ls=block.splitlines()
        if len(ls)<3 or '-->' not in ls[1]:raise ValueError('SRT格式无效')
        a,b=ls[1].split('-->');start,end=sec(a.strip()),sec(b.strip().split()[0]);text=' '.join(ls[2:]).strip()
        if not text or end<=start or (rows and start<rows[-1]['end']-.002):raise ValueError('字幕为空、倒序或重叠')
        rows.append({'id':int(ls[0]),'start':start,'end':end,'text':text})
    if len({c['id'] for c in rows})!=len(rows):raise ValueError('字幕ID重复')
    return rows
def check_ownership(segments,captions):
    refs=[v for s in segments for v in s.get('sourceRefs',[])];wanted=[c['id'] for c in captions]
    if refs!=wanted:raise ValueError('sourceRefs必须按原序完整覆盖每条字幕一次；不能遗漏、重复或改序')
def validate_segment(s,cat):
    fields=json.loads((ROOT/'params.schema.json').read_text(encoding='utf-8'))['properties']['segments']['items']['properties']
    if set(s)-set(fields):raise ValueError('未知镜头字段：'+','.join(set(s)-set(fields)))
    if s.get('intent') not in cat:raise ValueError('未实现该语义场景：'+str(s.get('intent')))
    if len(s.get('heading',''))>24 or len(s.get('body',''))>90:raise ValueError('标题最多24字、说明90字；请按语义拆镜头，不能截字')
    body_limits={'opening':36,'demo':48,'recap':36,'grid':48,'chart':48,'metric':48,'overview':48,'brand':54}
    if len(s.get('body',''))>body_limits.get(s['intent'],90):raise ValueError('该场景说明超过可读容量，请缩短或拆场')
    if s['intent'] in ['comparison','steps','questions']:
        items=s.get('items',[]);lo,hi=cat[s['intent']]['items']
        if not lo<=len(items)<=hi or any(not isinstance(x,str) or not x or len(x)>26 for x in items):raise ValueError('条目数量或字数超容量')
    if s.get('cueRefs') and len(s['cueRefs'])!=len(s.get('items',[])):raise ValueError('条目与真实触发字幕数量不一致')
    if s['intent']=='demo' and not 0<=s.get('index',0)<=3:raise ValueError('演示页仅有4种已实现布局')
    if s['intent']=='metric' and not 0<=s.get('index',0)<=2:raise ValueError('指标索引越界')
def rich_check(s):
    kind=s['intent']
    if kind not in RICH:
        if set(s)&{'cueSeconds','triggerRef','triggerSeconds','centerText','resultText','objectText','effectText','granularity','effectTarget','intensity','seed'}:raise ValueError('丰富动效字段只能用于对应新场景')
        return
    for key,limit in [('centerText',12),('resultText',24),('objectText',8),('effectText',12)]:
        if key in s and (not isinstance(s[key],str) or not 1<=len(s[key])<=limit):raise ValueError(key+'文字超容量或为空')
    if kind in {'expansion','route-choice','object-flow'}:
        items=s.get('items',[]);bounds={'expansion':(2,6,6),'route-choice':(2,2,14),'object-flow':(2,5,6)}[kind]
        if not bounds[0]<=len(items)<=bounds[1] or any(not isinstance(x,str) or not 1<=len(x)<=bounds[2] for x in items):raise ValueError('新场景条目数量或文字超容量')
        if not s.get('cueRefs') and not s.get('cueSeconds'):raise ValueError('新场景需明确条目动作时间')
    if len(s.get('body',''))>48:raise ValueError('丰富动效说明最多48字，避免侵入动作区域')
    if kind=='expansion' and not s.get('centerText'):raise ValueError('扩张需centerText')
    if kind=='route-choice' and s.get('answerIndex') not in [0,1]:raise ValueError('路线选择需answerIndex=0或1')
    if kind=='object-flow' and not s.get('objectText'):raise ValueError('传递需objectText')
    if kind in {'collapse','explode'}:
        if not s.get('effectText'):raise ValueError('破坏动效需effectText')
        if s.get('granularity','characters') not in ['characters','tiles'] or s.get('effectTarget','text') not in ['text','card']:raise ValueError('碎片或作用对象无效')
        if not .5<=s.get('intensity',1)<=1.5:raise ValueError('intensity仅允许0.5–1.5')
        if type(s.get('seed',43))!=int or not 0<=s.get('seed',43)<=999999:raise ValueError('seed无效')
    if kind!='object-flow' and ('triggerRef' in s)==('triggerSeconds' in s):raise ValueError('需明确一种触发来源')
    if kind=='object-flow' and ('triggerRef' in s or 'triggerSeconds' in s):raise ValueError('传递使用cueRefs/cueSeconds，不另设触发')

def build(p,base):
    allowed={'mode','duration','voiceover','captions','presenter','brand','music','segments','design','presenterLayout'}
    if set(p)-allowed:raise ValueError('未知输入字段：'+','.join(set(p)-allowed))
    cat=json.loads((ROOT/'catalog.json').read_text(encoding='utf-8'))['scenes'];segs=p.get('segments',[])
    if not 1<=len(segs)<=48:raise ValueError('镜头数量必须为1–48')
    for s in segs:
        validate_segment(s,cat);rich_check(s)
    if p.get("presenterLayout","classic") not in ["classic","sidebar"]:raise ValueError("人物布局无效")
    caps=[];source={};mode=p.get('mode')
    if mode=='voiceover':
        voice=(base/p['voiceover']).resolve();meta=probe(voice);audio=[x for x in meta['streams'] if x['codec_type']=='audio']
        if not audio:raise ValueError('口播源没有音轨')
        duration=max(float(meta['format']['duration']),*[float(x.get('duration',0)) for x in audio]);caps=read_srt(base/p['captions']);check_ownership(segs,caps)
        if caps[-1]['end']>duration+.05:raise ValueError('字幕超过完整原声时长')
        source={'voiceover':str(voice),'voiceoverSha256':sha(voice),'subtitleSha256':sha(base/p['captions']),'duration':duration,'hasVideo':any(x['codec_type']=='video' for x in meta['streams']),'audioStart':float(audio[0].get('start_time',0)),'formatStart':float(meta['format'].get('start_time',0))}
        if abs(source['audioStart']-source['formatStart'])>.05:raise ValueError('源音轨与容器起点不一致，须先明确时间基准')
    elif mode=='content':duration=float(p['duration'])
    else:raise ValueError('mode仅支持voiceover或content')
    if not 12<=duration<=180:raise ValueError('本候选声明12–180秒；不能改短源时长绕过限制')
    total=frames(duration);mins=[frames(cat[s['intent']]['min']) for s in segs];maxs=[frames(cat[s['intent']]['max']) for s in segs]
    if caps:
        byid={x['id']:x for x in caps};starts=[0]+[frames(byid[s['sourceRefs'][0]]['start']) for s in segs[1:]];lengths=[b-a for a,b in zip(starts,starts[1:]+[total])]
    else:
        if not sum(mins)<=total<=sum(maxs):raise ValueError('当前选场总容量不够；增加/减少或重组镜头，不拉伸动作或修改完整时长')
        lengths=mins[:];extra=total-sum(mins)
        # 水位分配仅用于无口播内容规划；有SRT时绝不按字数猜台词时间。
        while extra:
            eligible=[i for i in range(len(segs)) if lengths[i]<maxs[i]]
            if not eligible:raise ValueError('可读停留容量不足')
            step=max(1,extra//len(eligible))
            for i in eligible:
                n=min(extra,step,maxs[i]-lengths[i]);lengths[i]+=n;extra-=n
    scenes=[];cursor=0;events=[];byid={x['id']:x for x in caps}
    for i,(s,n,lo,hi) in enumerate(zip(segs,lengths,mins,maxs)):
        info=cat[s['intent']]
        if not lo<=n<=hi:raise ValueError(f'镜头{i+1}真实区间{n/FPS:.3f}秒不满足{lo/FPS}–{hi/FPS}秒；请合并或拆分对应语义段')
        if s.get('supportingRefs') and not set(s['supportingRefs'])<=set(s.get('sourceRefs',[])):raise ValueError('上屏文案依据超出该镜头拥有的字幕')
        cue_refs=s.get('cueRefs',[])
        if cue_refs and not caps:raise ValueError('cueRefs只能引用真实SRT，不接受模拟逐词时码')
        if not set(cue_refs)<=set(s.get('sourceRefs',[])):raise ValueError('动作触发点不属于该段字幕')
        if 'cueSeconds' in s:
            if caps or cue_refs:raise ValueError('cueSeconds仅用于无口播内容，不伪造真实字幕')
            if len(s['cueSeconds'])!=len(s.get('items',[])) or any(not isinstance(v,(int,float)) or not math.isfinite(v) or v<0 for v in s['cueSeconds']):raise ValueError('cueSeconds无效或数量不一致')
            cues=[frames(x) for x in s['cueSeconds']]
        else:cues=[frames(byid[x]['start'])-cursor for x in cue_refs] if cue_refs else [frames(.35+j*.24) for j in range(len(s.get('items',[])))]
        if cues!=sorted(cues) or any(v<0 for v in cues):raise ValueError('动作触发必须有序且在镜头内')
        trigger=None
        if s['intent'] in RICH and s['intent']!='object-flow':
            if caps:
                if 'triggerSeconds' in s or s.get('triggerRef') not in s.get('sourceRefs',[]):raise ValueError('口播丰富动效必须绑定本段真实triggerRef')
                trigger=frames(byid[s['triggerRef']]['start'])-cursor
            else:
                if 'triggerRef' in s or not isinstance(s.get('triggerSeconds'),(int,float)) or not math.isfinite(s['triggerSeconds']):raise ValueError('无口播使用显式triggerSeconds')
                trigger=frames(s['triggerSeconds'])
            if trigger<frames(1):raise ValueError('触发前至少保留1秒阅读窗')
            if cues and trigger<max(cues)+frames(.4):raise ValueError('结论必须晚于条目出现，不能提前选择或遮盖')
        exit_f=frames(info['exit']);protected=frames(info['protected'])
        if cues:protected=max(protected,max(cues)+frames(1.0 if s['intent']=='object-flow' else .4))
        if trigger is not None:protected=max(protected,trigger+frames(2.8 if s['intent'] in {'collapse','explode'} else .85))
        if 'answerRef' in s:
            if s['intent'] in RICH:raise ValueError('新场景使用triggerRef而非answerRef')
            if s['answerRef'] not in byid:raise ValueError('答案依据必须来自真实字幕')
            protected=max(protected,frames(byid[s['answerRef']]['start'])-cursor+frames(.4))
        if protected+exit_f>n:raise ValueError(f'镜头{i+1}动作保护窗与结束冲突；不能提前显示下一句或压缩动作')
        scene={**s,'id':f'shot-{i+1:02}','startFrame':cursor,'endFrame':cursor+n,'durationFrames':n,'protectedFrames':protected,'exitFrames':exit_f,'actionRate':1,'holdFrames':n-protected-exit_f,'cueFrames':cues}
        if 'answerRef' in s:
            if s['answerRef'] not in s.get('sourceRefs',[]) or s.get('answerIndex') not in [0,1]:raise ValueError('答案触发依据无效')
            scene['answerFrame']=frames(byid[s['answerRef']]['start'])-cursor
        if trigger is not None:scene['triggerFrame']=trigger
        scenes.append(scene)
        candidates=sorted(set([cursor+frames(.05)]+[cursor+x for x in cues]+([cursor+trigger] if trigger is not None else [])));event_frames=[]
        for f in candidates:
            if not event_frames or f-event_frames[-1]>=frames(.15):event_frames.append(f)
        for event in event_frames:
            impact=s['intent'] in {'collapse','explode'} and event==cursor+trigger
            tail=frames(.7 if impact else .3)
            if event+tail>cursor+n:raise ValueError('音效尾音超出镜头范围')
            events.append({'scene':scene['id'],'frame':event,'durationFrames':tail,'kind':s['intent'] if impact else 'soft'})
        cursor+=n
    if cursor!=total:raise ValueError('总帧数不一致')
    frozen={n:sha(ROOT/n) for n in ['catalog.json','src/index.html','src/foundation.js','src/product.js','src/adaptive.js','src/planner.py','src/audio.py','src/render.mjs','src/mix.mjs','src/rich.js','params.schema.json','src/font-guard.js','assets/NotoSansSC.ttf','licenses/font-OFL.txt']}
    return {'profile':'product-update-plan/1','version':'0.4.0-rc.5','fps':FPS,'width':1280,'height':720,'totalFrames':total,'duration':total/FPS,'mode':mode,'source':source,'captions':caps,'scenes':scenes,'soundEvents':events,'timingEvidence':'user-srt-sentence-timing' if caps else 'content-only-not-speech-alignment','status':'technical-plan-pending-human-review','frozenFiles':frozen,'inputSha256':hashlib.sha256(json.dumps(p,sort_keys=True,ensure_ascii=False).encode()).hexdigest()}
def save(p,base,out):
    plan=build(p,base);Path(out).write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8');return plan
