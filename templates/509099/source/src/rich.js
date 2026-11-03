// 参数化语义动作；所有状态只由整数输出帧和固定种子推导。
window.richKinds=['expansion','route-choice','object-flow','collapse','explode'];
const rc={bg:'#f6f4ef',ink:'#262626',muted:'#595959',purple:'#218c00',green:'#218c00',red:'#434343'};
const rq=x=>Math.max(0,Math.min(1,x)),re=x=>1-Math.pow(1-rq(x),3),rl=(a,b,t)=>a+(b-a)*t;
function rb(x,y,w,h,col='#f0f0f0',r=14){c.fillStyle=col;c.beginPath();c.roundRect(x,y,w,h,r);c.fill()}
function rt(s,x,y,z=25,col=rc.ink,align='left'){c.font=`500 ${z}px TemplateNoto`;c.textAlign=align;c.fillStyle=col;c.fillText(s,x,y);c.textAlign='left'}
function rline(x,y,X,Y,col=rc.purple,w=2){c.strokeStyle=col;c.lineWidth=w;c.beginPath();c.moveTo(x,y);c.lineTo(X,Y);c.stroke()}
function rring(x,y,r,col=rc.purple,w=2){c.strokeStyle=col;c.lineWidth=w;c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.stroke()}
function rpaper(x,y,label,scale=1){c.save();c.translate(x,y);c.scale(scale,scale);rb(-38,-49,76,98,rc.ink,7);for(let i=0;i<3;i++)rline(-22,-20+i*17,22,-20+i*17,'#bfbfbf',4);c.restore();if(label)rt(label,x,y+78,20,rc.muted,'center')}
function rcheck(x,y,p){c.strokeStyle=rc.green;c.lineWidth=6;c.lineCap='round';c.beginPath();c.moveTo(x-12,y);if(p<.35)c.lineTo(x-12+10*p/.35,y+10*p/.35);else{c.lineTo(x-2,y+10);c.lineTo(x-2+22*rq((p-.35)/.65),y+10-27*rq((p-.35)/.65))}c.stroke()}
function rshow(p,fn){if(p<=0)return;c.save();c.globalAlpha*=rq(p);fn();c.restore()}
function rcard(x,y,w,h,label,col=rc.purple){rb(x,y,w,h);rb(x,y,4,h,col,2);rt(label,x+16,y+h/2+8,label.length>4?18:23)}
function rfit(label,x,y,max,size=29){c.font=`500 ${size}px TemplateNoto`;while(c.measureText(label).width>max&&size>19){size--;c.font=`500 ${size}px TemplateNoto`}rt(label,x,y,size)}
function rExpand(s,t){const nodes=s.items,n=nodes.length;const positions=n<=4?[[150,285],[660,285],[150,470],[660,470]]:[[150,273],[655,270],[120,432],[660,435],[290,540],[530,540]];
 rshow(re(t/.6),()=>{rpaper(425,360,s.centerText,1.5)});
 nodes.forEach((v,i)=>{let p=re(t-s.cueFrames[i]/24),[x,y]=positions[i],xx=rl(425,x,p),yy=rl(360,y,p);rshow(p,()=>{rline(425,360,xx+65,yy+24,t>=s.triggerFrame/24?rc.red:'#bfbfbf');rcard(xx,yy,145,49,v,t>=s.triggerFrame/24?rc.red:rc.purple)})});
 let z=re((t-s.triggerFrame/24)/.55);if(z){rring(425,360,75+z*85,rc.red);rring(425,360,85+z*85,'#8c8c8c',1);rshow(z,()=>{rb(273,316,304,97,'#f6f4efee');rt(s.resultText||s.centerText,425,375,29,rc.red,'center')})}
}
function rRoute(s,t){let a=re((t-s.triggerFrame/24)/.65),chosen=s.answerIndex;
 s.items.forEach((label,i)=>{let x=80+i*425,tx=i===chosen?285:(i===0?-295:1030);x=rl(x,tx,a);let p=re((t-s.cueFrames[i]/24)/.5);rshow(p,()=>{rb(x,245,350,295,i===chosen&&a?'#e5ffd8':'#f0f0f0',22);rt(i?'B':'A',x+25,285,19,i===chosen?rc.green:rc.muted);rfit(label,x+25,335,300);if(i===chosen){rpaper(x+93,421,'',.75);rline(x+140,421,x+230,421,rc.green,3);rring(x+267,421,32,rc.green);rt('人',x+267,430,25,rc.green,'center')}else{for(let j=0;j<3;j++){rring(x+65+j*100,421,25,'#8c8c8c');if(j<2)rline(x+91+j*100,421,x+139+j*100,421,rc.muted)}}rb(x+25,490,300,4,i===chosen?rc.green:rc.purple,2)})});
 rshow(a,()=>{rt(s.resultText||s.items[chosen],465,590,27,rc.green,'center');rcheck(810,580,a)});
}
function rFlow(s,t){const n=s.items.length,xs=s.items.map((_,i)=>135+i*670/(n-1)),radius=n>3?49:67;
 s.items.forEach((label,i)=>{rring(xs[i],365,radius,i===n-1?rc.green:'#8c8c8c');rt(String(i+1).padStart(2,'0'),xs[i],269,17,rc.muted,'center');rt(label,xs[i],487,n>3?23:28,rc.ink,'center');if(i<n-1){let z=re((t-s.cueFrames[i+1]/24)/.8);rline(xs[i]+radius+6,365,rl(xs[i]+radius+6,xs[i+1]-radius-6,z),365,rc.green,3)}});
 if(t>=s.cueFrames[0]/24){let active=0;for(let i=1;i<n;i++)if(t>=s.cueFrames[i]/24)active=i;const p=active?re((t-s.cueFrames[active]/24)/.85):re((t-s.cueFrames[0]/24)/.55);let x=active?rl(xs[active-1],xs[active],p):xs[0];rshow(active?1:p,()=>rpaper(x,365,s.objectText,n>3?.72:.92));
 if(active===n-1){const z=re((t-s.cueFrames[n-1]/24-.35)/.55);rshow(z,()=>{rring(xs[n-1],365,radius+z*18,rc.green,3);rcheck(xs[n-1],365,z);rb(240,548,460,52,'#e5ffd8',26);rt(s.resultText||s.items[n-1],470,583,24,rc.green,'center')})}}
}
// 文字/卡片栅格化后按整字或图像瓦片运动；不依赖外部图像或物理引擎。
const shardCache=new Map();
function rShardSource(s){let key=[s.effectText,s.granularity,s.effectTarget].join('|');if(shardCache.has(key))return shardCache.get(key);
 const src=document.createElement('canvas');src.width=840;src.height=170;const g=src.getContext('2d');let size=84;do{g.font=`700 ${size}px TemplateNoto`;if(g.measureText(s.effectText).width<=770)break;size--}while(size>36);
 const w=g.measureText(s.effectText).width,x=(840-w)/2;if(s.effectTarget==='card'){g.fillStyle='#e5ffd8';g.beginPath();g.roundRect(0,0,840,170,16);g.fill()}g.textBaseline='middle';g.fillStyle=rc.ink;g.fillText(s.effectText,x,85);
 let parts=[];if(s.granularity==='tiles'||s.effectTarget==='card'){for(let row=0;row<4;row++)for(let col=0;col<12;col++){let sx=col*70,sy=Math.floor(row*42.5),h=Math.ceil(42.5),data=g.getImageData(sx,sy,70,h).data;if(data.some((v,i)=>i%4===3&&v))parts.push({sx,sy,w:70,h})}}
 else{let offset=x;for(const char of s.effectText){let cw=g.measureText(char).width;parts.push({sx:Math.floor(offset),sy:0,w:Math.ceil(cw)+1,h:170});offset+=cw}}
 let result={src,parts};shardCache.set(key,result);return result;
}
function rHash(seed,index){let x=(seed+index*374761393)|0;x=Math.imul(x^(x>>>13),1274126177);return ((x^(x>>>16))>>>0)/4294967296}
function rBreak(s,t){const {src,parts}=rShardSource(s),dt=t-s.triggerFrame/24,force=s.intensity||1,seed=s.seed??43;
 if(dt<0){c.save();const en=re(t/.55);c.globalAlpha=en;c.translate(470,360+18*(1-en));c.scale(en,en);c.drawImage(src,-420,-85);c.restore();rt(s.effectText,470,565,22,rc.muted,'center');return}
 // 破坏前短暂蓄力；动作窗保护包含蓄力和落定，不整体拉慢。
 if(s.intent==='explode'&&dt<.14){let k=1-.09*Math.sin(Math.PI*dt/.28);c.save();c.translate(470,360);c.scale(k,k);c.drawImage(src,-420,-85);c.restore();return}
 let u=Math.max(0,Math.min(2.66,dt-(s.intent==='explode'?.14:0)));
 for(let i=0;i<parts.length;i++){let p=parts[i],random=rHash(seed,i),r2=rHash(seed+51,i),age=Math.max(0,u-(s.intent==='collapse'?random*.25:0));let ox=50+p.sx+p.w/2,oy=275+p.sy+p.h/2,x=ox,y=oy,rot=0;
 if(s.intent==='collapse'){x+=Math.sin(random*15)*age*38*force;y+=180*age*age;rot=(random-.5)*age*2.4*force}
 else{let angle=Math.atan2(oy-360,ox-470)+(r2-.5)*1.1,speed=(130+random*160)*force;x+=Math.cos(angle)*speed*age;y+=Math.sin(angle)*speed*age+90*age*age;rot=(r2-.5)*age*4*force}
 // 明确运动边界，文字碎片不会侵入标题、字幕或人物窗口。
 const floor=580-p.h/2;if(y>floor){let hitAge=Math.sqrt(Math.max(0,(floor-oy)/180));let b=Math.max(0,age-hitAge);y=floor-Math.abs(Math.sin(b*9))*Math.exp(-b*5)*18;rot*=1-Math.exp(-age*3)*.2}
 x=Math.max(40+p.w/2,Math.min(900-p.w/2,x));y=Math.max(225+p.h/2,Math.min(floor,y));c.save();c.translate(x,y);c.rotate(rot);c.drawImage(src,p.sx,p.sy,p.w,p.h,-p.w/2,-p.h/2,p.w,p.h);c.restore();
 }
 if(s.intent==='explode'&&u<.4){c.save();c.globalAlpha=(1-u/.4)*.7;rring(470,360,30+u*420,rc.red,3);c.restore()}
}
window.paintRich=function(s,t,inputs){c.fillStyle=rc.bg;c.fillRect(0,0,1280,720);const panel=inputs.presenter?(inputs.presenterLayout==='sidebar'?940:820):1200,scale=Math.min(1,panel/940);
 c.save();c.translate((panel-940*scale)/2,206*(1-scale));c.scale(scale,scale);c.beginPath();c.rect(30,206,880,397);c.clip();for(let i=0;i<9;i++)rline(50,205+i*46,915,205+i*46,'#d9d9d9',1);
 if(s.intent==='expansion')rExpand(s,t);else if(s.intent==='route-choice')rRoute(s,t);else if(s.intent==='object-flow')rFlow(s,t);else rBreak(s,t);c.restore();
 rt(s.label||({expansion:'关系扩张','route-choice':'路线选择','object-flow':'对象传递',collapse:'坍塌 / 内容失去支撑',explode:'炸裂 / 内容向外分散'}[s.intent]),55,68,15,rc.purple);
 let size=39;c.font=`700 ${size}px TemplateNoto`;while(c.measureText(s.heading||'').width>panel-100&&size>22){size--;c.font=`700 ${size}px TemplateNoto`}rt(s.heading||'',55,132,size);if(s.body)wrapped(s.body,57,174,20,panel-110,rc.muted,1.35);rt(inputs.brand||'',55,623,12,rc.muted);
};
