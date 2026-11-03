(()=>{
const templateDefaults={"text01": "复杂的任务，怎么做？", "text02": "三个小步骤", "text03": "看任务信息", "text04": "看证据与反馈", "text05": "看方案是否适合", "text06": "先看主要信息", "text07": "再关注条件与约束", "text08": "排在前面的信息", "text09": "通常优先关注", "text10": "信息顺序示意", "text11": "任务信息", "text12": "证据与反馈", "text13": "主要信息", "text14": "条件 / 约束", "text15": "留意真实反馈", "text16": "结合任务信息关注约束", "text17": "信息相互补充", "text18": "方案是否适合", "text19": "执行风险", "text20": "范围与条件", "text21": "一次做多少", "text22": "逐项判断", "text23": "行动，从一个小样开始", "text24": "认识问题", "text25": "学会选择", "text26": "理解每次行动的依据", "text27": "小步行动指南", "text28": "图形示意 · 方法演示", "text29": "信息", "text30": "证据", "text31": "适合", "text32": "结合任务信息", "text33": "关注条件约束", "text34": "行动，", "text35": "从一个小样开始。"};
let templateInputs=null;
function copy(key){return (templateInputs?.content||templateDefaults)[key]??templateDefaults[key]}
const robotPixels=[".......DD.......", ".......DD.......", ".......DD.......", "...DDDDDDDDDD...", "..DPPPPPPPPPPD..", "..DPPPPPPPPPPD..", "DDDDDDDPPDDDDDDD", "DDDDPPDDDDPPDDDD", "DDDDPDDPPDPDDDDD", "DDDDDDDPPDDDDDDD", "..DPPPDDDDPPPD..", "..DDDDDDDDDDDD..", "......DDDD......", "..DDDMMPPMMDDD..", "..DDDMMMMMMDDD..", "..DDDDDDDDDDDD..", "....DDD..DDD....", "....DDD..DDD...."];
// 本期内容与时间轴独立创作；共用既有渲染入口及月白渐变。
const ink='#424B50', muted=ink;
const q=(t,a,b)=>ease((t-a)/(b-a));
let currentPlan;
function group(a,fn){if(a<=0)return;c.save();c.globalAlpha=clamp(a);fn();c.restore()}
function txt(s,x,y,size=24,col=ink,weight=500){text(s,x,y,size,col,weight)}
function rule(x,y,w){line(x,y,x+w,y,'#cbd6d1',1)}
function surface(x,y,w,h){c.save();c.shadowColor='#424b5012';c.shadowBlur=22;c.shadowOffsetY=8;box(x,y,w,h,16,moonwhiteGradient('surface',x,w));c.restore()}
function robot(x,y,settle=1){
 const left=Math.round(x-16),top=Math.round(y-18)+(settle<.6?-2:0),colors={D:ink,P:'#F8F5F0',M:'#E8F4F0'};
 for(let r=0;r<robotPixels.length;r++)for(let k=0;k<16;k++){const color=colors[robotPixels[r][k]];if(color){c.fillStyle=color;c.fillRect(left+k*2,top+r*2,2,2)}}
}
function annotation(x1,y1,x2,y2,t,start,end){const p=q(t,start,end),x=lerp(x1,x2,p),y=lerp(y1,y2,p);line(x1,y1,x,y,ink,2);robot(x,y,q(t,end,end+.4))}
function stage(t,a,b,fn){const alpha=q(t,a,a+.35)*(b>43?1:1-q(t,b-.3,b));group(alpha,()=>fn(t-a))}
function heading(k,title,sub){txt(k,78,164,18);txt(title,78,228,44,ink,600);txt(sub,78,275,23)}
function subline(s,x,y,w,p){group(p,()=>{txt(s,x,y+12*(1-p),25);rule(x,y+24,w)})}
const allText=[copy('text01'),copy('text02'),copy('text03'),copy('text04'),copy('text05'),copy('text06'),copy('text07'),copy('text08'),copy('text09'),copy('text10'),copy('text11'),copy('text12'),copy('text13'),copy('text14'),copy('text15'),copy('text16'),copy('text17'),copy('text18'),copy('text19'),copy('text20'),copy('text21'),copy('text22'),copy('text23'),copy('text24'),copy('text25'),copy('text26'),copy('text27'),copy('text28'),'01 / INGREDIENTS','02 / NUTRITION','03 / SUITABILITY',copy('text29'),copy('text30'),copy('text31')];
const legacyLoad=async(p,plan)=>{templateInputs=p;currentPlan=plan;await document.fonts.load('600 44px TemplateNoto');await document.fonts.ready;window.verifyLicensedFont({items:Object.values(templateInputs.content||templateDefaults)},plan);render(0)};
const render=function(frame){
 const t=frame/24;pale();c.textAlign='left';c.textBaseline='alphabetic';
 txt(copy('text27'),78,58,16);txt(copy('text28'),1013,58,14);rule(78,80,1124);
 stage(t,-.35,2.7,()=>{
  txt(copy('text01'),78,226,48,ink,600);txt(copy('text02'),78,278,26);
  [copy('text11'),copy('text12'),copy('text18')].forEach((s,i)=>{const p=q(t,.15+i*.28,.7+i*.28);group(p,()=>{surface(552+i*211,250+20*(1-p),188,180);txt('0'+(i+1),575+i*211,294,18);txt(s,575+i*211,356,22,ink,600)})});
 });
 stage(t,2.7,11.266,u=>{
  heading('01 / INGREDIENTS',copy('text03'),copy('text06'));
  group(q(u,6.2,6.6),()=>txt(copy('text07'),78,318,22));
  surface(546,139,637,374);txt(copy('text10'),578,182,15);rule(578,199,570);
  subline(copy('text08'),578,249,418,q(u,1.7,2.1));
  group(q(u,1.7,2.1),()=>{box(578,281,365*q(u,1.7,2.6),32,6,'#E8F4F0');txt(copy('text09'),593,304,21)});
  subline(copy('text13'),578,365,418,q(u,4.5,4.9));subline(copy('text14'),578,441,418,q(u,6.2,6.6));
  if(u>1.7)annotation(578,331,1061,331,u,1.7,3.6);
 });
 stage(t,11.266,19.5,u=>{
  heading('02 / NUTRITION',copy('text04'),copy('text17'));
  const split=q(u,1.6,2.3);
  surface(546,164,300,326);surface(866,164,317,326);
  txt(copy('text12'),570,213,24,ink,600);txt(copy('text11'),891,213,24,ink,600);
  rule(570,235,250);rule(891,235,267);
  group(q(u,1.83,2.2),()=>{box(569,277,252,50,9,'#E8F4F0');txt(copy('text15'),587,310,25)});
  group(q(u,3.23,3.7),()=>txt(copy('text32'),891,310,24));
  group(q(u,4.7,5.1),()=>txt(copy('text33'),891,353,24));
  if(u>3.23){const p=q(u,3.23,4.5);line(697,403,697,427,ink,2);line(697,427,697+328*p,427,ink,2);robot(697+328*p,427,q(u,4.5,4.9));}
 });
 stage(t,19.5,27.366,u=>{
  heading('03 / SUITABILITY',copy('text05'),copy('text22'));
  const items=[copy('text19'),copy('text20'),copy('text21')];
  items.forEach((s,i)=>{const starts=[2.3,3.9,6.0],p=q(u,starts[i],starts[i]+.45);surface(546,137+i*124,637,104);txt('0'+(i+1),573,195+i*124,17);group(p,()=>txt(s,634,201+i*124,29,ink,600));});
  if(u>2.3){let i=u>=6?2:u>=3.9?1:0;const st=[2.3,3.9,6][i];annotation(1033,189+i*124,1139,189+i*124,u,st,st+.65)}
 });
 stage(t,27.366,44,u=>{
  txt(copy('text34'),78,215,46,ink,600);txt(copy('text35'),78,281,42,ink,600);
  const items=[copy('text24'),copy('text25'),copy('text26')];
  const starts=[3.4,5.37,8.434];
  items.forEach((s,i)=>{const p=q(u,starts[i],starts[i]+.5);group(p,()=>{surface(546,153+i*127+12*(1-p),637,100);txt('0'+(i+1),574,209+i*127,17);txt(s,631,215+i*127,27,ink,600)})});
  if(u>8){annotation(546,555,1183,555,u,8,11.7)}
 });
 // 字幕使用源SRT句子时间；按自然短语换行，不制造逐词落点。
 const cap=currentPlan.captions.find(v=>t>=v.start&&t<v.end);
 rule(78,604,1124);
 [copy('text29'),copy('text30'),copy('text31')].forEach((s,i)=>{const active=t>=[2.7,11.266,19.5][i];group(active?1:.4,()=>txt('0'+(i+1)+' '+s,78+i*118,638,15))});
 if(cap){c.font='500 27px TemplateNoto';c.textAlign='center';txt(cap.text,640,689,27);c.textAlign='left';}
};

window.explainerRuntime={render(frame,p){templateInputs=p;currentPlan={captions:p.captions};render(frame)}};
})();
