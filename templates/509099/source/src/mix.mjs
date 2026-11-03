import path from 'node:path';import fs from 'node:fs';
export function mixArgs(plan,p,out){
const args=['-v','error','-i',path.join(out,'visual.mp4')];let index=1,filter=[],maps=['-map','0:v'];
if(p.presenter){args.push('-i',p.presenter);const sidebar=p.presenterLayout==='sidebar';filter.push(`[${index}:v]fps=24,scale=${sidebar?'280:158':'384:216'},tpad=stop_mode=clone:stop_duration=0.041667[p];[0:v][p]overlay=${sidebar?'975:391':'864:150'}:repeatlast=0[v]`);maps=['-map','[v]'];index++;}
const labels=[];if(plan.mode==='voiceover'){args.push('-i',path.join(out,'voiceover.wav'));filter.push(`[${index++}:a]apad=whole_dur=${plan.duration}[voice]`);labels.push('[voice]');}
if(fs.existsSync(path.join(out,'music.wav'))){args.push('-i',path.join(out,'music.wav'));filter.push(`[${index++}:a]volume=0.15[music]`);labels.push('[music]');}
args.push('-i',path.join(out,'sfx.wav'));labels.push(`[${index++}:a]`);filter.push(`${labels.join('')}amix=inputs=${labels.length}:duration=longest:normalize=0,alimiter=limit=0.95:latency=1[a]`);
args.push('-filter_complex',filter.join(';'),...maps,'-map','[a]','-c:v',p.presenter?'libx264':'copy',...(p.presenter?['-crf','19','-pix_fmt','yuv420p']:[]),'-c:a','aac','-b:a','192k','-t',String(plan.duration),'-movflags','+faststart',path.join(out,'video.mp4'));
return args;}
