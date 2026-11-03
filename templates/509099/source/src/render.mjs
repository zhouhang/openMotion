import {mixArgs} from './mix.mjs';
import fs from 'node:fs';import path from 'node:path';import {fileURLToPath,pathToFileURL} from 'node:url';import {createRequire} from 'node:module';import {spawn,spawnSync} from 'node:child_process';import crypto from 'node:crypto';
const opts={};for(let i=2;i<process.argv.length;i+=2)opts[process.argv[i]]=process.argv[i+1];
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),out=path.resolve(opts['--instance']);
const plan=JSON.parse(fs.readFileSync(path.join(out,'plan.json'),'utf8')),p=JSON.parse(fs.readFileSync(path.join(out,'resolved.json'),'utf8'));
for(const [name,hash] of Object.entries(plan.frozenFiles||{}))if(crypto.createHash('sha256').update(fs.readFileSync(path.join(root,name))).digest('hex')!==hash)throw Error('模板已变更，必须重新规划');
const require=createRequire(import.meta.url);const {chromium}=require(opts['--playwright-module']||'playwright');
let executable=opts['--browser']||process.env.CHROME_PATH;if(!executable&&process.platform==='win32')executable=['C:/Program Files/Google/Chrome/Application/chrome.exe','C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'].find(fs.existsSync);
const b=await chromium.launch({...(executable?{executablePath:executable}:{}),headless:true,args:['--allow-file-access-from-files']});
try{
const page=await b.newPage({viewport:{width:1280,height:720},deviceScaleFactor:1});const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(path.join(root,'src/index.html')).href);await page.addStyleTag({content:'#play{display:none}'});await page.evaluate(async ({p,plan})=>window.loadAdaptive(p,plan),{p,plan});
const check=Math.floor(plan.totalFrames*.61);await page.evaluate(f=>window.renderFrame(f),check);let a=await page.locator('canvas').screenshot();await page.evaluate(()=>window.renderFrame(0));await page.evaluate(f=>window.renderFrame(f),check);let aa=await page.locator('canvas').screenshot();if(!a.equals(aa))throw Error('独立seek不一致');
const checkpoints=new Set([0,plan.totalFrames-1,check]);for(const s of plan.scenes){for(const f of [s.startFrame,s.startFrame+6,s.startFrame+s.protectedFrames,s.endFrame-1,...s.cueFrames.map(x=>s.startFrame+x)])if(f>=0&&f<plan.totalFrames)checkpoints.add(f);}
fs.mkdirSync(path.join(out,'checks'));const target=path.join(out,'visual.mp4');const enc=spawn('ffmpeg',['-v','error','-f','image2pipe','-vcodec','png','-framerate','24','-i','pipe:0','-an','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',target],{windowsHide:true});let stderr='';enc.stderr.on('data',d=>stderr+=d);const done=new Promise((res,rej)=>{enc.on('error',rej);enc.on('close',n=>n?rej(Error(stderr)):res())});let streamError;enc.stdin.on('error',e=>streamError=e);
for(let f=0;f<plan.totalFrames;f++){await page.evaluate(f=>window.renderFrame(f),f);let buf=await page.locator('canvas').screenshot();if(streamError)throw streamError;if(!enc.stdin.write(buf))await new Promise(r=>enc.stdin.once('drain',r));if(checkpoints.has(f))fs.writeFileSync(path.join(out,'checks',`f-${String(f).padStart(5,'0')}.png`),buf);if(f%240===0)console.log(`render ${f}/${plan.totalFrames}`);}
enc.stdin.end();await done;if(errors.length)throw Error(errors.join('\n'));
const args=mixArgs(plan,p,out);
const mux=spawnSync('ffmpeg',args,{encoding:'utf8',windowsHide:true});if(mux.status!==0)throw Error(mux.stderr);
fs.writeFileSync(path.join(out,'verification.json'),JSON.stringify({frames:plan.totalFrames,duration:plan.duration,seekDeterministic:true,browserErrors:errors,actionRate:1,subtitleCount:plan.captions.length,presenter:p.presenter?'same source/global clock/contain':'none',music:p.music?.mode||'pending',humanContinuousReview:'pending',status:'experimental'},null,2));console.log(path.join(out,'video.mp4'));
}finally{await b.close()}
