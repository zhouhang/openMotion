// 0.4.0：从通用表达目标重新设计8类场景；不保留旧输入框、浏览器UI或原片镜头函数。
const studio={ink:'#262626',muted:'#595959',mint:'#218c00',blue:'#63fe13',gold:'#218c00',surface:'#f0f0f0',bg:'#f6f4ef'};
const baseDesign={brand:'微光工作室',tagline:'把重要的事情，表达清楚',opening:'让目标清晰，让证据说话',summary:'先有明确目标，再用证据完成判断',slides:[
{title:'明确目标',subtitle:'先描述希望发生的变化',prompt:'目标需要可理解、可检查',bg:'#f0f0f0',accent:'#63fe13'},
{title:'整理证据',subtitle:'把已有材料放在合适位置',prompt:'区分已知事实与待验证问题',bg:'#f0f0f0',accent:'#218c00'},
{title:'检查差距',subtitle:'让每一步变化有据可查',prompt:'依据实际数据比较，不补造结论',bg:'#f0f0f0',accent:'#218c00'},
{title:'形成交付',subtitle:'用一份清楚的结果结束本轮',prompt:'以实际完成情况确认下一步',bg:'#f0f0f0',accent:'#218c00'}],
chart:{title:'逐阶段比较前后变化',labels:['准备','采集','整理','核对','修订','交付'],previous:[25,38,45,56,65,72],current:[32,43,57,64,76,86]},metrics:[{name:'资料覆盖率',unit:'%',previous:65,current:84},{name:'核对完成率',unit:'%',previous:72,current:90},{name:'反馈处理率',unit:'%',previous:60,current:78}],images:['','','','']};
let projectDesign=structuredClone(baseDesign),evidenceImages=[null,null,null,null];
window.prepareProduct=async function(inputs){projectDesign=structuredClone(inputs.design||baseDesign);if(!inputs.design)projectDesign.brand=inputs.brand||baseDesign.brand;
 evidenceImages=await Promise.all(projectDesign.images.map(src=>src?new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>reject(Error('证据图片无法读取'));im.src=src}):null));
};
function pCenter(value,x,y,size=26,color=studio.ink){c.save();c.textAlign='center';text(value,x,y,size,color,500);c.restore()}
function pFit(value,x,y,maxWidth,size=40,color=studio.ink){let z=size;while(z>18){c.font=`600 ${z}px TemplateNoto`;if(c.measureText(value).width<=maxWidth)break;z--}text(value,x,y,z,color,600)}
function pLines(value,x,y,width,size=24,color=studio.muted){c.font=`400 ${size}px TemplateNoto`;const rows=[''];for(const ch of value){const i=rows.length-1;if(c.measureText(rows[i]+ch).width>width)rows.push(ch);else rows[i]+=ch}if(rows.length>3)throw Error('新场景文字超过可读布局，请缩短或拆场');rows.forEach((s,i)=>text(s,x,y+i*size*1.45,size,color))}
function pShow(progress,draw){if(progress<=0)return;c.save();c.globalAlpha*=clamp(progress);draw();c.restore()}
function pHeader(kicker,title,subtitle=''){text(kicker,24,51,17,studio.mint,600);pFit(title,24,110,1070,42);if(subtitle)pLines(subtitle,26,151,1050,22)}
function pArc(x,y,r,start,end,col,width=2){c.beginPath();c.arc(x,y,r,start,end);c.strokeStyle=col;c.lineWidth=width;c.stroke()}
function pImage(image,x,y,w,h){const k=Math.min(w/image.width,h/image.height);c.drawImage(image,x+(w-image.width*k)/2,y+(h-image.height*k)/2,image.width*k,image.height*k)}
function focusObjective(t,s){text(projectDesign.brand,26,51,20,studio.mint,600);text('目标聚焦',940,51,17,studio.muted);const p=ease(t/1.1),gap=lerp(140,0,p),x=160-gap,y=210-gap*.25,w=800+gap*2,h=245+gap*.5;
 const corners=[[x,y,1,1],[x+w,y,-1,1],[x,y+h,1,-1],[x+w,y+h,-1,-1]];for(const [xx,yy,dx,dy] of corners){line(xx,yy,xx+dx*48,yy,studio.mint,4);line(xx,yy,xx,yy+dy*48,studio.mint,4)}
 pShow(p,()=>pLines(s.heading||projectDesign.opening,200,302+(1-p)*22,720,38,studio.ink));const q=ease((t-1.4)/1.1);pShow(q,()=>{line(300,411,300+q*530,411,studio.blue,3);pCenter(s.body||projectDesign.tagline,560,525,27,studio.muted)});
}
function evidenceStage(t,s){const i=s.index||0,d=projectDesign.slides[i],p=ease(t/.9);pHeader('证据展台 · '+String(i+1).padStart(2,'0'),s.heading||d.title,s.body||d.subtitle);
 c.save();c.translate(0,18*(1-p));c.globalAlpha=p;box(80,202,960,310,18,d.bg);line(80,205,80+960*p,205,d.accent,4);
 if(evidenceImages[i])pImage(evidenceImages[i],100,220,920,270);
 else{for(let j=0;j<4;j++){const q=ease((t-.35-j*.23)/.8),labels=['目的','材料','检查','结果'];pShow(q,()=>{
 if(i===0){const a=j*Math.PI/2-Math.PI/4,x=560+Math.cos(a)*220,y=350+Math.sin(a)*86;line(560,350,lerp(560,x,q),lerp(350,y,q),d.accent,2);box(x-82,y-22,164,44,10,studio.surface);pCenter(labels[j],x,y+8,23)}
 else if(i===1){const x=195+j*190,y=lerp(440,270,q);box(x,y,155,148,12,studio.surface);text('材料 '+(j+1),x+20,y+43,23);line(x+20,y+73,x+130,y+73,d.accent,4);line(x+20,y+98,x+105,y+98,studio.muted,2)}
 else if(i===2){const y=245+j*51;box(160,y,800*q,37,7,studio.surface);text(labels[j],185,y+27,22);line(410,y+19,410+430*q,y+19,d.accent,5);pCenter('已核对',915,y+27,20,d.accent)}
 else{const x=170+j*225,y=385-j*29;box(x,y,175,54,10,studio.surface);pCenter(labels[j],x+87,y+35,24);if(j<3)line(x+175,y+27,x+220,y-2,d.accent,3)}
 })}if(i===0){dot(560,350,30,d.accent);pCenter('目标',560,358,22,studio.ink)}text('抽象示意 · 可替换自有证据图片',106,485,17,studio.muted)}
 c.restore();pShow(ease((t-1.4)/.8),()=>pLines(d.prompt,85,567,950,23,studio.muted));
}
function gatherHighlights(t,s){pHeader('要点归并',s.heading||'把四项证据，收进一个判断');projectDesign.slides.forEach((d,i)=>{const z=ease((t-.4-i*.24)/.85),x=lerp(60,700,z),y=lerp(230+i*76,325,z);pShow(1-z*.9,()=>{box(x,y,350,52,10,studio.surface);text(d.title,x+18,y+35,25)});pShow(z,()=>box(665,230+i*35,285*z,8,4,d.accent))});
 pShow(ease((t-1.2)/1.0),()=>{box(620,400,400,156,18,'#e5ffd8');pLines(s.body||projectDesign.summary,652,445,335,26,studio.mint)});
}
function quadrantMap(t,s){pHeader('四象限定位',s.heading||'每项材料，各有位置',s.body||'');const cells=[[35,200],[585,200],[35,388],[585,388]];line(560,190,560,570,'#bfbfbf',2);line(22,378,1098,378,'#bfbfbf',2);
 projectDesign.slides.forEach((d,i)=>{const q=ease((t-.15-i*.2)/1.0),[tx,ty]=cells[i],x=lerp(310,tx,q),y=lerp(300,ty,q);pShow(q,()=>{box(x,y,500,161,14,d.bg);dot(x+28,y+30,6,d.accent);text(String(i+1).padStart(2,'0'),x+46,y+37,17,d.accent);if(evidenceImages[i]){pImage(evidenceImages[i],x+270,y+22,205,112);pFit(d.title,x+23,y+82,225,29);pLines(d.subtitle,x+23,y+115,230,18)}else{pFit(d.title,x+23,y+83,450,30);pLines(d.subtitle,x+23,y+121,450,20)}})});
}
function stageDeltas(t,s){const d=projectDesign.chart;pHeader('差值轨迹',s.heading||d.title,s.body||'每行独立比较上一轮与当前值，不计算综合分');const left=230,right=890,top=220;
 for(let tick=0;tick<=100;tick+=25){let x=left+(right-left)*tick/100;line(x,196,x,544,'#d9d9d9');pCenter(String(tick),x,578,16,studio.muted)}
 d.labels.forEach((label,i)=>{let y=top+i*57,p=ease((t-.2-i*.2)/1.25),old=left+d.previous[i]/100*(right-left),now=left+d.current[i]/100*(right-left),moving=lerp(old,now,p);text(label,26,y+8,25);line(old,y,moving,y,studio.mint,5);pArc(old,y,7,0,Math.PI*2,studio.muted,2);dot(moving,y,9,studio.mint);pShow(p,()=>text(d.previous[i].toFixed(1)+' → '+d.current[i].toFixed(1),925,y+8,21,studio.mint))});
}
function metricLocator(t,s){const m=projectDesign.metrics[s.index||0],p=ease((t-.15)/1.6),value=lerp(m.previous,m.current,p);pHeader('指标游标',s.heading||m.name,s.body||'上一轮与当前值使用同一把刻度尺');const x=550,top=210,bottom=532,toY=v=>bottom-(bottom-top)*v/100;
 line(x,top,x,bottom,'#8c8c8c',3);for(let tick=0;tick<=100;tick+=10){let y=toY(tick);line(x-12,y,x+12,y,'#8c8c8c');if(tick%20===0)text(String(tick),x+28,y+6,16,studio.muted)}
 const a=toY(m.previous),b=toY(value);line(285,a,x-20,a,studio.muted,2);box(80,a-36,205,72,12,studio.surface);text('上一轮',97,a-8,17,studio.muted);text(m.previous.toFixed(1)+m.unit,97,a+22,27);
 line(x+20,b,785,b,studio.mint,3);box(785,b-42,260,84,13,'#e5ffd8');text('当前',802,b-12,18,studio.mint);text(value.toFixed(1)+m.unit,802,b+25,35,studio.mint);dot(x,b,9,studio.mint);pShow(ease((t-1.8)/.6),()=>{const diff=m.current-m.previous;pCenter('变化 '+(diff>=0?'+':'')+diff.toFixed(1)+' 个百分点',550,595,25,studio.mint)});
}
function metricConstellation(t,s){pHeader('三指标关系图',s.heading||'放在一起观察，分别理解变化',s.body||'三项百分比独立呈现，不代表综合评分');const hub=[560,365],tips=[[560,210],[270,490],[850,490]],p=ease((t-.2)/1.7);
 tips.forEach(([x,y],i)=>{line(...hub,x,y,'#8c8c8c',2);const m=projectDesign.metrics[i];pCenter(m.name,x,y+(i===0?-28:42),25);pCenter(m.current.toFixed(1)+m.unit,x,y+(i===0?-1:70),23,studio.mint)});
 for(const [key,col,alpha] of [['previous','#8c8c8c',.16],['current',studio.mint,.22]]){c.beginPath();tips.forEach(([x,y],i)=>{const m=projectDesign.metrics[i],value=key==='current'?lerp(m.previous,m.current,p):m.previous,q=value/100,xx=lerp(hub[0],x,q),yy=lerp(hub[1],y,q);i?c.lineTo(xx,yy):c.moveTo(xx,yy)});c.closePath();c.save();c.globalAlpha=alpha;c.fillStyle=col;c.fill();c.restore();c.strokeStyle=col;c.lineWidth=2;c.stroke()}
 dot(...hub,4,studio.blue);text('上一轮轮廓',25,590,17,studio.muted);text('当前轮廓',195,590,17,studio.mint);
}
function signatureEnd(t,s){const p=ease(t/1.0),q=ease((t-1)/1.0);text('本期落款',28,51,17,studio.muted);c.save();c.beginPath();c.rect(160,180,800*p,180);c.clip();pFit(projectDesign.brand,180,300,780,73,studio.ink);c.restore();line(180,337,180+740*q,337,studio.mint,4);
 pShow(q,()=>pLines(s.heading||projectDesign.tagline,185,405+(1-q)*15,750,31,studio.mint));pShow(ease((t-1.7)/.8),()=>pLines(s.body||projectDesign.summary,185,510,760,23,studio.muted));
}
const productPainters={opening:focusObjective,demo:evidenceStage,recap:gatherHighlights,grid:quadrantMap,chart:stageDeltas,metric:metricLocator,overview:metricConstellation,brand:signatureEnd};
window.productKinds=Object.keys(productPainters);
window.paintProduct=function(s,t,inputs){c.fillStyle=studio.bg;c.fillRect(0,0,1280,720);const width=inputs.presenter?(inputs.presenterLayout==='sidebar'?940:820):1280,k=Math.min(1,width/1120),left=(width-1120*k)/2,top=12+(620-620*k)/2;
 c.save();c.translate(left,top);c.scale(k,k);productPainters[s.intent](t,s);c.restore();};
