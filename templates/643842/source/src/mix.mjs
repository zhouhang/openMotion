import path from 'node:path';import fs from 'node:fs';
export function mixArgs(plan,p,out){
const args=['-v','error','-i',path.join(out,'visual.mp4')];let index=1,filter=[],maps=['-map','0:v'];
// 人物已按全局整数帧在Canvas内裁切和排版；混音阶段只合成唯一原声与既有音效。
const labels=[];if(plan.mode==='voiceover'){args.push('-i',path.join(out,'voiceover.wav'));filter.push(`[${index++}:a]apad=whole_dur=${plan.duration}[voice]`);labels.push('[voice]');}
if(fs.existsSync(path.join(out,'music.wav'))){args.push('-i',path.join(out,'music.wav'));filter.push(`[${index++}:a]volume=0.15[music]`);labels.push('[music]');}
args.push('-i',path.join(out,'sfx.wav'));labels.push(`[${index++}:a]`);filter.push(`${labels.join('')}amix=inputs=${labels.length}:duration=longest:normalize=0${Number.isFinite(plan.masterGainDb)?',volume='+plan.masterGainDb+'dB':''},alimiter=limit=0.95:latency=1[a]`);
args.push('-filter_complex',filter.join(';'),...maps,'-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-t',String(plan.duration),'-movflags','+faststart',path.join(out,'video.mp4'));
return args;}
