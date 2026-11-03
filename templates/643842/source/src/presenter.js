// 可选全程口播层；关闭时沿用原渲染，不改变旧模块的几何与声音。
(()=>{
 const baseRender=window.renderFrame,baseLoad=window.loadAdaptive,cache=new Map();
 const scratch=document.createElement('canvas');scratch.width=1280;scratch.height=720;
 const sc=scratch.getContext('2d',{willReadFrequently:true});
 let layout=null,planning=false,rects=null;
 const realTrace=trace;
 trace=function(x1,y1,x2,y2,t,a,b){
  if(rects&&c.globalAlpha>.08&&t>=a)rects.push([Math.min(x1,x2)-20,Math.min(y1,y2)-22,Math.max(x1,x2)+20,Math.max(y1,y2)+22]);
  return realTrace(x1,y1,x2,y2,t,a,b);
 };
 const realText=c.fillText.bind(c);
 c.fillText=function(value,x,y,...rest){
  if(rects&&c.globalAlpha>.08){
   const m=c.measureText(String(value)),size=parseFloat(c.font.match(/([\d.]+)px/)?.[1]||24),a=m.actualBoundingBoxAscent||size*.85,d=m.actualBoundingBoxDescent||size*.2;
   let left=x;if(c.textAlign==='center')left-=m.width/2;else if(['right','end'].includes(c.textAlign))left-=m.width;
   let top=y-a;if(c.textBaseline==='top')top=y;else if(c.textBaseline==='middle')top=y-size/2;
   const matrix=c.getTransform(),points=[[left,top],[left+m.width,top],[left,top+a+d],[left+m.width,top+a+d]].map(([px,py])=>matrix.transformPoint({x:px,y:py}));
   const xs=points.map(p=>p.x),ys=points.map(p=>p.y),r=[Math.min(...xs)-8,Math.min(...ys)-8,Math.max(...xs)+8,Math.max(...ys)+8];
   if(r[2]>0&&r[0]<1280&&r[3]>0&&r[1]<720)rects.push(r);
  }
  return realText(value,x,y,...rest);
 };
 function mediaRects(s){
  if(s.type==='graphic')return (window.motionRegions||[]).filter(v=>v.role==='graphic').map(v=>v.bounds);
  if(s.type==='image')return [[512,125,1210,585]];
  if(s.type==='video')return [[450,125,1220,580]];
  if(s.type==='image-wall')return [[66,128,1214,615]];
  if(s.type==='page-waterfall-wall')return [[368,83,1280,650]];
  if(s.type==='brand')return [[240,150,1040,530]];
  if(s.type==='ending')return [[130,195,1150,590]];
  if(s.type==='explainer')return [[530,125,1200,550]];
  return [];
 }
 function collision(p,r){const dx=Math.max(r[0]-p.x,0,p.x-r[2]),dy=Math.max(r[1]-p.y,0,p.y-r[3]);return dx*dx+dy*dy<(p.r+10)**2;}
 function transformed(r,p){return [r[0]*p.scale+p.dx,r[1]*p.scale+p.dy,r[2]*p.scale+p.dx,r[3]*p.scale+p.dy];}
 function makeLayout(){
  planning=true;const pages=[];let previous=null;
  for(const s of inputs.scenes){
   const unique=new Map(),frameRects=[];
   // 逐帧记录真实字形边界，覆盖未来的入场、聚焦、退出，不只检查静帧。
   for(let f=s.startFrame;f<s.endFrame;f++){
    rects=[];baseRender(f);const rs=rects.concat(mediaRects(s));frameRects.push(rs);
    for(const r of rs)unique.set(r.map(v=>Math.round(v/2)*2).join(','),r);
   }
   rects=null;const occupied=[...unique.values()],protectedRects=occupied.concat([[0,0,1280,93],[0,580,1280,645]]);
   const choices=[];
   for(const radius of [96,84,72]){
    for(const x of [130,260,390,510,640,770,890,1020,1150])for(const y of [195,290,390,480]){
     const p={x,y,r:radius,scale:1,dx:0,dy:0,mode:'natural-space'};
     if(x-radius<24||x+radius>1256||y-radius<96||y+radius>570||protectedRects.some(r=>collision(p,r)))continue;
     const continuity=previous?Math.hypot(x-previous.x,y-previous.y)*.12:0;
     choices.push({...p,score:(96-radius)*20+continuity+Math.min(x,1280-x)*.05});
    }
    if(choices.length)break;
   }
   let chosen=choices.sort((a,b)=>a.score-b.score)[0];
   if(!chosen){
    const weights=occupied.map(r=>({r,w:Math.min(100000,(r[2]-r[0])*(r[3]-r[1]))}));
    const left=weights.filter(v=>(v.r[0]+v.r[2])/2<640).reduce((n,v)=>n+v.w,0),right=weights.filter(v=>(v.r[0]+v.r[2])/2>=640).reduce((n,v)=>n+v.w,0),lane=right>left*1.2?'left':'right';
    const weight=weights.reduce((n,v)=>n+v.w,0)||1,cy=weights.reduce((n,v)=>n+(v.r[1]+v.r[3])/2*v.w,0)/weight;
    chosen={x:lane==='left'?130:1150,y:cy<340?470:220,r:96,scale:.78,dx:lane==='left'?270:12,dy:32,mode:'reserved-side-lane',lane};
   }
   // 所有帧核对实际文字、主素材与全局字幕，失败立即阻止输出。
   let collisions=0;
   for(const rs of frameRects)if(rs.some(r=>collision(chosen,transformed(r,chosen)))||collision(chosen,[0,580,1280,645]))collisions++;
   if(collisions)throw Error('人物布局发生遮挡: '+s.type+' / '+collisions);
   pages.push({...chosen,startFrame:s.startFrame,endFrame:s.endFrame,type:s.type,checkedFrames:frameRects.length,collisions,occupiedRects:occupied.length,reason:chosen.mode==='natural-space'?'整页全部帧均有可容纳圆窗的留白':'留白不足，等比收拢页面，给人物预留独立侧边'});previous=chosen;
  }
  planning=false;rects=null;
  return {pages,policy:'whole-scene actual text + conservative primary-media bounds; caption/header exclusion; stable per-page anchor; uniform reflow when needed',transitions:'safe scene-boundary placement; smooth travel only within a verified free side lane',width:1280,height:720,checkedFrames:pages.reduce((n,p)=>n+p.checkedFrames,0),collisions:0,captionBand:[580,645],status:'technical-pass-human-review-pending'};
 }
 async function imageAt(f){
  if(cache.has(f))return cache.get(f);
  const img=await new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>reject(Error('人物帧缺失: '+f));im.src=inputs.presenter.frameBase+String(f).padStart(5,'0')+'.jpg'});
  cache.set(f,img);while(cache.size>32)cache.delete(cache.keys().next().value);return img;
 }
 function placement(f){
  const i=layout.pages.findIndex(p=>f>=p.startFrame&&f<p.endFrame),p=layout.pages[Math.max(0,i)],prior=layout.pages[i-1];
  // 相同侧边独立通道中的位置变化可以安全平移；其它页面切换直接就位，避免穿过内容。
  if(prior&&f-p.startFrame<12&&p.mode==='reserved-side-lane'&&prior.mode===p.mode&&prior.lane===p.lane){const t=ease((f-p.startFrame)/12);return {...p,y:lerp(prior.y,p.y,t)}}return p;
 }
 function captions(f){
  const cap=inputs.presenter.captions.find(v=>f/24>=v.start&&f/24<v.end);if(!cap)return;
  c.font='500 24px TemplateNoto';const lines=[];let line='';
  for(const ch of Array.from(cap.text)){if(c.measureText(line+ch).width>1120){lines.push(line);line=ch}else line+=ch}if(line)lines.push(line);
  if(lines.length>2)throw Error('全局字幕超过两行容量，请拆分SRT');
  c.save();c.fillStyle='#F8F5F0';c.globalAlpha=.96;c.fillRect(48,582,1184,62);c.globalAlpha=1;c.fillStyle=ink;c.textAlign='center';c.textBaseline='alphabetic';lines.forEach((line,i)=>c.fillText(line,640,lines.length===1?624:606+i*29));c.restore();
 }
 window.renderFrame=function(f){
  if(!inputs?.presenter||planning)return baseRender(f);
  if(!Number.isInteger(f)||f<0||f>=inputs.presenter.frameCount)throw Error('人物帧越界');
  if(!layout)layout=makeLayout();
  return imageAt(f).then(img=>{
   baseRender(f);const p=placement(f);
   if(p.scale!==1){sc.clearRect(0,0,1280,720);sc.drawImage(canvas,0,0);pale();c.drawImage(scratch,p.dx,p.dy,1280*p.scale,720*p.scale);}
   c.save();c.shadowColor='#424B5025';c.shadowBlur=12;c.fillStyle='#F8F5F0';c.beginPath();c.arc(p.x,p.y,p.r+4,0,Math.PI*2);c.fill();c.shadowBlur=0;
   c.beginPath();c.arc(p.x,p.y,p.r,0,Math.PI*2);c.clip();c.drawImage(img,p.x-p.r,p.y-p.r,p.r*2,p.r*2);c.restore();captions(f);
  });
 };
 window.loadAdaptive=async(p,pl)=>{layout=null;cache.clear();await baseLoad(p,pl);window.presenterLayoutReport=layout;};
})();
