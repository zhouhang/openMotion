const robotPixels=[".......DD.......", ".......DD.......", ".......DD.......", "...DDDDDDDDDD...", "..DPPPPPPPPPPD..", "..DPPPPPPPPPPD..", "DDDDDDDPPDDDDDDD", "DDDDPPDDDDPPDDDD", "DDDDPDDPPDPDDDDD", "DDDDDDDPPDDDDDDD", "..DPPPDDDDPPPD..", "..DDDDDDDDDDDD..", "......DDDD......", "..DDDMMPPMMDDD..", "..DDDMMMMMMDDD..", "..DDDDDDDDDDDD..", "....DDD..DDD....", "....DDD..DDD...."];
// 图片与视频帧先就绪，统一从整数帧绘制；不依赖浏览器实时视频时钟。
const ink='#424B50';let inputs,plan;const loaded=new Map();
const q=(t,a,b)=>ease((t-a)/(b-a));
function txt(s,x,y,size=24,col=ink,weight=500){text(s,x,y,size,col,weight)}
function group(a,fn){if(a<=0)return;c.save();c.globalAlpha=clamp(a);fn();c.restore()}
function rule(x,y,w){line(x,y,x+w,y,'#cbd6d1',1)}
function surface(x,y,w,h){c.save();c.shadowColor='#424b5019';c.shadowBlur=22;c.shadowOffsetY=8;box(x,y,w,h,18,moonwhiteGradient('surface',x,w));c.restore()}
function clip(x,y,w,h,fn){c.save();c.beginPath();c.roundRect(x,y,w,h,16);c.clip();fn();c.restore()}
function contain(img,x,y,w,h){const k=Math.min(w/img.naturalWidth,h/img.naturalHeight),dw=img.naturalWidth*k,dh=img.naturalHeight*k;c.drawImage(img,x+(w-dw)/2,y+(h-dh)/2,dw,dh)}
function robot(x,y){const colors={D:ink,P:'#F8F5F0',M:'#E8F4F0'},left=Math.round(x-16),top=Math.round(y-18);for(let r=0;r<robotPixels.length;r++)for(let k=0;k<16;k++){const color=colors[robotPixels[r][k]];if(color){c.fillStyle=color;c.fillRect(left+k*2,top+r*2,2,2)}}}
function trace(x1,y1,x2,y2,t,a,b){const p=q(t,a,b),x=lerp(x1,x2,p),y=lerp(y1,y2,p);line(x1,y1,x,y,ink,2);robot(x,y)}
function corners(x,y,w,h,p=1){const l=18*p;c.strokeStyle=ink;c.lineWidth=2;c.beginPath();for(const [a,b,sx,sy] of [[x,y,1,1],[x+w,y,-1,1],[x,y+h,1,-1],[x+w,y+h,-1,-1]]){c.moveTo(a+sx*l,b);c.lineTo(a,b);c.lineTo(a,b+sy*l)}c.stroke()}
function heading(lines,desc){lines.forEach((s,i)=>txt(s,78,216+i*61,46,ink,600));txt(desc,78,lines.length>1?330:278,22)}
function imagePose(img,rect,view,z){const [x,y,w,h]=view,[rx,ry,rw,rh]=rect,iw=img.naturalWidth,ih=img.naturalHeight,s0=Math.min(w/iw,h/ih),s1=Math.min(w/(rw*iw*1.18),h/(rh*ih*1.18)),s=lerp(s0,s1,z),cx=lerp(iw/2,(rx+rw/2)*iw,z),cy=lerp(ih/2,(ry+rh/2)*ih,z),dx=x+w/2-cx*s,dy=y+h/2-cy*s;
 c.drawImage(img,dx,dy,iw*s,ih*s);return [dx+rx*iw*s,dy+ry*ih*s,rw*iw*s,rh*ih*s];}
function brandScene(s,t){
 const arrive=q(t,0,1),shrink=q(t,3.1,4.4),img=loaded.get(s.logoUrl);
 group(1-shrink,()=>surface(250,160+55*(1-arrive),780,358));
 const x=lerp(330,78,shrink),y=lerp(221+45*(1-arrive),111,shrink),size=lerp(188,48,shrink);
 contain(img,x,y,size,size);
 txt(s.name,lerp(567,146,shrink),lerp(305,146,shrink),lerp(56,27,shrink),ink,600);
 group(1-q(t,3.1,3.7),()=>txt(s.tagline,567,358,23));
 if(t>1)trace(lerp(330,78,shrink),lerp(457,184,shrink),lerp(950,286,shrink),lerp(457,184,shrink),t,1,2.5);
 group(q(t,4.5,5),()=>{txt(s.tagline,78,326,40,ink,600)});
}
function imageScene(s,t){
 heading(s.heading,s.description);const img=loaded.get(s.imageUrl),enter=q(t,0,.9),zoom=q(t,2.1,3.3)*(1-q(t,s.duration-1.8,s.duration-.8));
 let focusBox;c.save();c.translate(0,35*(1-enter));surface(520,133,682,444);
 clip(520,133,682,444,()=>{const roi=imagePose(img,s.focus,[520,133,682,444],zoom);focusBox=roi;group(q(t,3.3,3.8)*(1-q(t,s.duration-1.9,s.duration-1.4)),()=>{corners(...roi,q(t,3.3,4.1));});});c.restore();
 // 单图聚焦仅保留焦点边框与文字，不绘制延伸连线和末端机器人。
 group(q(t,4,4.5)*(1-q(t,s.duration-1.9,s.duration-1.4)),()=>txt(s.annotation,78,475,25,ink,600));
 txt(zoom>.5?'局部聚焦':'完整画面',540,613,16);
}
function videoScene(s,f){
 const t=f/24,freeze=s.freezeAt,pause=s.freezeDuration,paused=t>=freeze&&t<freeze+pause;
 const mapped=t<freeze?t:t<freeze+pause?freeze:t-pause,idx=Math.min(s.frames.length-1,Math.max(0,Math.floor(mapped*24+1e-6)));
 const img=loaded.get(s.frames[idx]),enter=q(t,0,.7),zoom=q(t,freeze,freeze+.5)*(1-q(t,freeze+pause-.5,freeze+pause));
 let focusBox;heading(s.heading,s.description);c.save();c.translate(30*(1-enter),20*(1-enter));surface(464,144,738,415);
 clip(464,144,738,415,()=>{
  // 视频默认完整等比显示；停帧时围绕明确焦点作轻推近。
  const iw=img.naturalWidth,ih=img.naturalHeight,k=Math.min(738/iw,415/ih)*(1+.16*zoom),cx=lerp(iw/2,(s.focus[0]+s.focus[2]/2)*iw,zoom*.18),cy=lerp(ih/2,(s.focus[1]+s.focus[3]/2)*ih,zoom*.18),dx=833-cx*k,dy=351.5-cy*k;
  c.drawImage(img,dx,dy,iw*k,ih*k);
  if(paused){const r=[dx+s.focus[0]*iw*k,dy+s.focus[1]*ih*k,s.focus[2]*iw*k,s.focus[3]*ih*k];focusBox=r;group(q(t,freeze+.15,freeze+.6),()=>corners(...r));}
 });
 box(482,160,paused?118:90,31,15,'#EEF7F2');txt(paused?'暂停观察':'播放中',495,182,16);
 c.restore();
 line(464,592,1202,592,'#cbd6d1',3);line(464,592,464+738*idx/(s.frames.length-1),592,ink,3);
 txt(mapped.toFixed(1)+'s / '+s.sourceDuration.toFixed(1)+'s',464,623,15);
 if(paused){trace(78,426,focusBox[0],focusBox[1]+focusBox[3]/2,t,freeze+.15,freeze+.8);group(q(t,freeze+.4,freeze+.9),()=>txt(s.annotation,78,475,25,ink,600));}
 group(q(t,freeze+pause,freeze+pause+.4)*(1-q(t,freeze+pause+.8,freeze+pause+1.2)),()=>txt('继续播放',78,426,25,ink,600));
}
// 图片始终等比缩放；缩略图裁切与完整图之间用同一图像连续变换。
function wallSlot(i,n){const rows=Math.ceil(n/3),w=(1124-36)/3,h=rows===2?220:142,row=Math.floor(i/3),count=Math.min(3,n-row*3);return [78+(3-count)*(w+18)/2+(i%3)*(w+18),144+row*(h+18),w,h]}
function wallPose(s,t){const lift=q(t,3.8,5.4)*(1-q(t,s.duration-3,s.duration-2)),z=q(t,7,8.4)*(1-q(t,s.duration-4,s.duration-3));return {lift,z}}
function wallPhoto(img,slot,lift,z,focus){
 const hero=[520,133,682,444],v=slot.map((x,i)=>lerp(x,hero[i],lift)),[x,y,w,h]=v,iw=img.naturalWidth,ih=img.naturalHeight;
 const cover=Math.max(slot[2]/iw,slot[3]/ih),fit=Math.min(hero[2]/iw,hero[3]/ih),detail=Math.min(w/(focus[2]*iw*1.25),h/(focus[3]*ih*1.25));
 const k=lerp(lerp(cover,fit,lift),detail,z),dw=iw*k,dh=ih*k;
 let dx=x+w/2-lerp(iw/2,(focus[0]+focus[2]/2)*iw,z)*k,dy=y+h/2-lerp(ih/2,(focus[1]+focus[3]/2)*ih,z)*k;
 // 局部靠近图片边缘时夹紧平移，避免放大后露出空边。
 if(z>0){dx=dw>=w?Math.max(x+w-dw,Math.min(x,dx)):x+(w-dw)/2;dy=dh>=h?Math.max(y+h-dh,Math.min(y,dy)):y+(h-dh)/2}
 surface(...v);let roi=[dx+focus[0]*iw*k,dy+focus[1]*ih*k,focus[2]*iw*k,focus[3]*ih*k];
 clip(...v,()=>{c.drawImage(img,dx,dy,dw,dh);group(z,()=>corners(...roi))});return {v,roi};
}
function wallScene(s,t){
 const {lift,z}=wallPose(s,t),n=s.imageUrls.length,chosen=s.selectedIndex;
 const appear=i=>q(t,i*.11,.65+i*.11);
 for(let i=0;i<n;i++)if(i!==chosen)group(appear(i)*(1-.94*lift),()=>{const slot=wallSlot(i,n);slot[1]+=25*(1-appear(i));wallPhoto(loaded.get(s.imageUrls[i]),slot,0,0,s.focus)});
 // 左侧说明仅在主体前移后出现，图片墙阶段不被大标题遮挡。
 group(q(t,4.6,5.4)*(1-q(t,s.duration-3.4,s.duration-3)),()=>{box(60,118,425,503,20,moonwhiteGradient('surface',60,425));heading(s.heading,s.description)});
 let pose;group(appear(chosen),()=>{const slot=wallSlot(chosen,n);slot[1]+=25*(1-appear(chosen));pose=wallPhoto(loaded.get(s.imageUrls[chosen]),slot,lift,z,s.focus)});
 const selection=q(t,2.8,3.5)*(1-q(t,3.8,4.4));
 group(selection,()=>{corners(...pose.v);trace(78,626,pose.v[0]+32,pose.v[1]+pose.v[3]-26,t,2.8,3.6)});
 group(q(t,8.4,8.8)*(1-q(t,s.duration-4.3,s.duration-4)),()=>{const x=Math.max(538,Math.min(1180,pose.roi[0])),y=Math.max(153,Math.min(557,pose.roi[1]+pose.roi[3]/2));trace(78,426,x,y,t,8.4,9.5);txt(s.annotation,78,475,25,ink,600)});
 group(1-lift,()=>txt(t<s.duration-2?'从一组素材中，找到叙述的重点':'回到全貌，重点仍在原位',78,126,23,ink,600));
 group(lift,()=>txt(z>.5?'局部细节 · 同一张照片':'完整画面 · 保持原始比例',520,613,16));
}
window.loadAdaptive=async(p,pl)=>{
 inputs=p;plan=pl;await window.loadFoodIconLibrary();await document.fonts.load('600 46px TemplateNoto');await document.fonts.ready;
 const urls=[...new Set(p.scenes.flatMap(s=>s.type==='graphic'?[...s.objects,s.product].filter(v=>v?.imageUrl).map(v=>v.imageUrl):['explainer','opening'].includes(s.type)?[]:s.type==='ending'?(s.logoUrl?[s.logoUrl]:[]):s.type==='brand'?[s.logoUrl]:s.type==='image'?[s.imageUrl]:['image-wall','page-waterfall-wall'].includes(s.type)?s.imageUrls:s.frames))];
 await Promise.all(urls.map(url=>new Promise((resolve,reject)=>{const img=new Image();img.onload=()=>{loaded.set(url,img);resolve()};img.onerror=()=>reject(Error('素材加载失败: '+url));img.src=url})));
 const visible=['从一组素材中，找到叙述的重点','回到全貌，重点仍在原位','局部细节 · 同一张照片','完整画面 · 保持原始比例','媒体场景 · 可复用演示','品牌落款','标识完整保留，收拢为角标','可替换 Logo / PNG · SVG · JPG','局部聚焦','完整画面','暂停观察','播放中','继续播放',...p.scenes.flatMap(s=>[s.name,s.tagline,...s.heading||[],s.description,s.annotation,s.credit].filter(Boolean))];
 for(const s of p.scenes)if(s.type==='page-waterfall-wall'){visible.push(s.imageUrls.length+' 张素材 / '+s.columns+' 列流动');s.imageUrls.forEach(waterfallTexture)}
 for(const s of p.scenes)if(s.type==='explainer')visible.push(...Object.values(s.content),...s.captions.map(v=>v.text),'01 / INGREDIENTS','02 / NUTRITION','03 / SUITABILITY');
 for(const s of p.scenes)if(['opening','ending'].includes(s.type))visible.push(...[s.title,s.subtitle,s.lead,s.brand,s.tagline,...s.items||[]].filter(Boolean));
 for(const s of p.scenes)if(s.type==='graphic')visible.push(s.title,...(s.groups||[]).map(v=>v.label),...s.objects.map(v=>v.label),s.product?.label,s.note||'',s.caption||'',...Object.values(s.labels||{}));
 if(p.presenter)visible.push(...p.presenter.captions.map(v=>v.text));
 window.verifyLicensedFont({items:visible},pl);await window.renderFrame(0);
};
window.renderFrame=function(frame){
 if(!inputs)throw Error('请先加载实例参数');pale();c.textAlign='left';c.textBaseline='alphabetic';
 const s=inputs.scenes.find(s=>frame>=s.startFrame&&frame<s.endFrame)||inputs.scenes.at(-1),local=frame-s.startFrame,t=local/24;
 if(s.type==='graphic'){window.graphicScene(s,local);return;}
 if(s.type==='explainer'){window.explainerRuntime.render(local,s);return;}
 if(s.type==='opening'||s.type==='ending'){bookendScene(s,t);rule(78,652,1124);txt(s.credit,78,684,12);return;}
 const openingContext=inputs.scenes.filter(v=>v.type==='opening'&&v.startFrame<s.startFrame).at(-1)?.title;
 txt(inputs.scenes.find(v=>v.type==='brand')?.name||openingContext||s.heading.join(' / '),78,58,16);txt(String(inputs.scenes.indexOf(s)+1).padStart(2,'0')+' / '+String(inputs.scenes.length).padStart(2,'0'),1120,58,16);rule(78,80,1124);
 if(s.type==='brand')brandScene(s,t);else if(s.type==='image')imageScene(s,t);else if(s.type==='image-wall')wallScene(s,t);else if(s.type==='page-waterfall-wall')waterfallScene(s,t);else videoScene(s,local);
 // 明确保留来源署名；原媒体不因裁切与暂停而被重新标为模板作者作品。
 rule(78,652,1124);txt(s.credit,78,684,12);
};

