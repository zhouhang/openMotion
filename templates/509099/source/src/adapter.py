import argparse,json,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
from planner import save
from audio import prepare
ROOT=Path(__file__).resolve().parent.parent
def main():
    p=argparse.ArgumentParser();p.add_argument('operation',choices=['plan','render']);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--playwright-module');p.add_argument('--browser');p.add_argument('--diagnostic',action='store_true');a=p.parse_args()
    data=json.loads(a.inputs.read_text(encoding='utf-8-sig'));base=a.inputs.resolve().parent
    if a.out.exists():raise ValueError('输出目录已存在；使用新路径')
    a.out.mkdir(parents=True);plan=save(data,base,a.out/'plan.json')
    (a.out/'inputs.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    if a.operation=='plan':print(a.out/'plan.json');return
    if data.get('music',{}).get('mode','pending')=='pending' and not a.diagnostic:raise ValueError('配乐待明确绑定；诊断输出需--diagnostic，不冒充最终混音')
    prepare(plan,data,base,a.out)
    resolved=json.loads(json.dumps(data))
    if resolved.get('presenter'):
        resolved['presenter']=str((base/resolved['presenter']).resolve())
        if plan['mode']!='voiceover' or Path(resolved['presenter'])!=Path(plan['source']['voiceover']):raise ValueError('当前人物仅支持与口播同一源，不能引入未声明的同步偏移')
        if not plan['source'].get('hasVideo'):raise ValueError('人物源没有视频流')
    if resolved.get('design',{}).get('images'):
        for i,name in enumerate(resolved['design']['images']):
            if name:
                image=(base/name).resolve()
                if not image.is_file():raise ValueError('演示图片缺失')
                resolved['design']['images'][i]=image.as_uri()
    (a.out/'resolved.json').write_text(json.dumps(resolved,ensure_ascii=False,indent=2),encoding='utf-8')
    cmd=['node',str(ROOT/'src/render.mjs'),'--instance',str(a.out.resolve())]
    for name in ['playwright_module','browser']:
        if getattr(a,name):cmd+=['--'+name.replace('_','-'),getattr(a,name)]
    subprocess.run(cmd,check=True)
if __name__=='__main__':
    try:main()
    except Exception as e:print(str(e),file=sys.stderr);raise SystemExit(2)
