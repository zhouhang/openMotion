let adaptivePlan=null,adaptiveInputs=null;
function fitted(s,x,y,size,max,color,weight=500){while(size>22){c.font=`${weight} ${size}px TemplateNoto`;if(c.measureText(s).width<=max)break;size--;}text(s,x,y,size,color,weight);}
function wrapped(s,x,y,size,max,color,leading=1.55){c.font=`400 ${size}px TemplateNoto`;let lines=[''];for(const ch of s){let last=lines.length-1;if(c.measureText(lines[last]+ch).width>max)lines.push(ch);else lines[last]+=ch;}if(lines.length>4)throw Error('说明超过可读布局，请拆分镜头');lines.forEach((v,i)=>text(v,x,y+i*size*leading,size,color));}
function neutral(s,local){let dark=['problem','warning'].includes(s.tone);if(dark){c.fillStyle='#f6f4ef';c.fillRect(0,0,1280,720)}else pale();const ink=dark?'#262626':'#262626',muted=dark?'#595959':'#595959';let enter=ease(local/.65);c.save();c.globalAlpha=enter;text(s.label||'观点与表达',60,90,13,dark?'#218c00':'#218c00',600);fitted(s.heading||'',60,184+(1-enter)*18,44,750,ink,700);c.restore();
if(s.body){c.save();c.globalAlpha*=enter;wrapped(s.body,62,245,23,735,muted);c.restore();}
if(s.intent==='comparison'){
 s.items.forEach((v,i)=>{const q=ease((local-(s.cueFrames[i]||0)/24)/.4);c.save();c.globalAlpha=q;const x=60+i*390,y=335+(1-q)*18;box(x,y,365,164,17,dark?'#ffffff':'#fff');const answered=s.answerFrame!==undefined&&local>=s.answerFrame/24&&s.answerIndex===i;box(x,y,365,5,0,answered?'#63fe13':dark?'#bfbfbf':'#d9d9d9');text(i===0?'A':'B',x+24,y+42,16,'#595959',600);wrapped(v,x+24,y+90,24,315,ink,1.35);c.restore();});
}else if(['steps','questions'].includes(s.intent)){
 s.items.forEach((v,i)=>{let q=ease((local-(s.cueFrames[i]||0)/24)/.4);c.save();c.globalAlpha=q;const y=310+i*56+(1-q)*12;box(62,y,748,47,12,dark?'#ffffff':'#fff');dot(89,y+23,13,dark?'#e5ffd8':'#e5ffd8');text(s.intent==='questions'?'?':String(i+1),84,y+29,14,'#218c00',600);fitted(v,118,y+31,23,665,ink,500);c.restore();});
}else{
 const q=ease((local-.25)/.65);c.save();c.globalAlpha=q;box(62,365,748,137,18,dark?'#ffffff':'#fff');text(s.tone==='warning'?'充分，但要收敛':'先把问题说清，再决定怎样做',88,424,26,dark?'#218c00':'#218c00',600);text(s.label||'本期观点 · 与完整口播同步',89,466,14,muted);c.restore();}
text(adaptiveInputs.brand||'思考与交付',62,618,12,muted);}
function paintScene(s,local){if(window.richKinds.includes(s.intent))return window.paintRich(s,local,adaptiveInputs);if(window.productKinds.includes(s.intent))return window.paintProduct(s,local,adaptiveInputs);return neutral(s,local);}
window.loadAdaptive=async function(inputs,plan){
 adaptiveInputs=inputs;adaptivePlan=plan;
 const loaded=await document.fonts.load('16px TemplateNoto');await document.fonts.ready;
 if(!loaded.length||loaded.some(f=>f.status!=='loaded'))throw Error('随包授权字体未加载，禁止系统字体回退');
 window.verifyLicensedFont(inputs,plan);await window.prepareProduct(inputs);
 window.verifyLicensedFont({design:projectDesign},plan);
};
window.renderFrame=function(frame){if(!adaptivePlan)throw Error('先加载已校验计划');let f=Math.min(adaptivePlan.totalFrames-1,Math.max(0,frame)),s=adaptivePlan.scenes.find(s=>s.startFrame<=f&&f<s.endFrame);if(!s)throw Error('计划有空隙');let localF=f-s.startFrame;
// protectedFrames以前保持每帧原速；之后仅延长可读停留，不整体拉伸动作。
let local=Math.min(localF,s.protectedFrames)/24;paintScene(s,local);
const next=adaptivePlan.scenes[adaptivePlan.scenes.indexOf(s)+1];if(next&&localF>=s.durationFrames-s.exitFrames){c.save();c.globalAlpha=ease((localF-(s.durationFrames-s.exitFrames))/s.exitFrames);paintScene(next,0);c.restore();}
if(adaptiveInputs.presenter){if(adaptiveInputs.presenterLayout==='sidebar'){box(975,391,280,158,8,'#f0f0f0');text(adaptiveInputs.brand||'本期内容',978,100,20,'#595959');text('原视频',978,580,14,'#595959');}else{box(856,128,400,267,15,'#f0f0f0');text('原视频',871,427,14,'#595959');}}
// 句级字幕跟随原始SRT，不推测句内关键词时间。
const t=f/24,cap=adaptivePlan.captions.find(x=>x.start<=t&&t<x.end);if(cap){box(35,645,1210,55,13,'#101827e8');c.save();c.textAlign='center';fitted(cap.text,640,681,29,1150,'#fff',500);c.restore();}
return {frame:f,scene:s.id,localFrame:Math.min(localF,s.protectedFrames),actionRate:1};};
window.pause=()=>{};
