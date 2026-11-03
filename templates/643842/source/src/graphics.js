// 原创短场景：同一组实体贯穿分类、组合、变形与判断；全部状态由整数帧计算。
(()=>{
 const C={ink:'#424B50',paper:'#F8F5F0',green:'#B2C9B2',mint:'#C6E3E1',gold:'#D9C08F',red:'#B97965',line:'#CBD6D1'};
 const phase=(f,a,b)=>{const p=clamp((f-a)/Math.max(1,b-a));return p*p*(3-2*p)};
 let regions=[];
 function region(id,label,x,y,w,h,role='graphic'){regions.push({id,label,role,bounds:[x-w/2,y-h/2,x+w/2,y+h/2]})}
 function label(value,x,y,size=28,alpha=1){if(alpha<=0)return;c.save();c.globalAlpha*=alpha;c.textAlign='center';txt(value,x,y,size,C.ink,600);c.restore();region('label:'+value,value,x,y-size*.4,Math.max(20,value.length*size),size*1.2,'label')}
 function ellipse(x,y,rx,ry,color){c.fillStyle=color;c.beginPath();c.ellipse(x,y,rx,ry,0,0,Math.PI*2);c.fill()}
 function poly(points,color){c.fillStyle=color;c.beginPath();points.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.closePath();c.fill()}
 function stroke(points,width=3,color=C.ink){c.strokeStyle=color;c.lineWidth=width;c.lineCap='round';c.lineJoin='round';c.beginPath();points.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.stroke()}
 function icon(o,x,y,size,alpha=1,rotation=0){
  if(alpha<.02)return;c.save();c.globalAlpha*=alpha;c.translate(x,y);c.rotate(rotation);c.scale(size/100,size/100);
  const foodImage=window.MOTION_FOOD_ICON_IMAGES?.get(o.kind);
  if(foodImage){contain(foodImage,-50,-50,100,100)}else if(o.kind==='image'){const im=loaded.get(o.imageUrl);contain(im,-50,-50,100,100)}
  else if(o.kind==='seed'){
   for(const [px,py,rot] of [[-21,9,-.5],[14,13,.5],[0,-15,.12]]){c.save();c.translate(px,py);c.rotate(rot);ellipse(0,0,18,32,'#90A58B');ellipse(0,-2,11,24,'#C4D1B0');stroke([[0,-18],[0,17]],1.6,'#83997D');c.restore()}
  }else if(o.kind==='apple'){
   c.fillStyle=C.red;c.beginPath();c.moveTo(0,-31);c.bezierCurveTo(31,-58,61,-21,43,15);c.bezierCurveTo(30,45,12,51,0,43);c.bezierCurveTo(-17,53,-40,28,-46,2);c.bezierCurveTo(-59,-29,-21,-56,0,-31);c.fill();stroke([[0,-30],[8,-52]],4);c.save();c.rotate(-.4);ellipse(23,-36,20,9,C.green);c.restore();
  }else if(o.kind==='carrot'){
   poly([[-27,-26],[24,-30],[1,48]],'#CE9D73');stroke([[-9,-3],[6,-5]],2,'#AD815B');stroke([[-3,17],[7,14]],2,'#AD815B');stroke([[0,-29],[-15,-50]],7,C.green);stroke([[0,-29],[3,-55]],7,'#91AA8E');stroke([[0,-29],[23,-48]],7,C.green);
  }else if(o.kind==='milk'){
   poly([[-31,-29],[17,-29],[17,47],[-31,47]],'#F1F0ED');poly([[17,-29],[36,-20],[36,47],[17,47]],C.mint);poly([[-31,-29],[-17,-49],[8,-49],[17,-29]],'#D1DECE');poly([[8,-49],[26,-40],[36,-20],[17,-29]],C.green);poly([[-31,1],[17,1],[17,21],[-31,21]],C.mint);ellipse(-7,12,8,10,C.paper);
  }else if(o.kind==='grain'){
   stroke([[0,49],[0,-44]],3);for(let i=0;i<5;i++){c.save();c.translate(0,-33+i*16);c.rotate(-.55);ellipse(-12,0,14,6,C.gold);c.rotate(1.1);ellipse(12,0,14,6,C.gold);c.restore()}
  }else if(o.kind==='bean'){
   c.save();c.rotate(-.4);ellipse(0,0,29,44,'#C4AD87');stroke([[-6,-27],[-11,0],[-4,28]],2,'#A79071');c.restore();
  }else if(o.kind==='cookie'){
   cookie(1);
  }else if(o.kind==='bar'){
   box(-47,-29,94,58,12,C.gold);for(let i=0;i<12;i++)ellipse(-35+(i%4)*23,-16+Math.floor(i/4)*16,5,2.5,'#AF906B');
  }else if(o.kind==='muffin'){
   poly([[-36,-6],[36,-6],[25,45],[-25,45]],C.gold);ellipse(-25,-12,24,22,'#CEAB7F');ellipse(0,-24,29,28,'#CEAB7F');ellipse(25,-12,24,22,'#CEAB7F');stroke([[-12,8],[-9,35]],2,'#B39168');stroke([[12,8],[9,35]],2,'#B39168');
  }else if(o.kind==='package'){
   box(-36,-48,72,96,9,C.mint);box(-36,-48,72,12,5,C.green);box(-36,34,72,14,5,C.green);ellipse(0,-4,22,22,C.paper);for(let i=0;i<3;i++)stroke([[-10,-12+i*8],[10,-12+i*8]],2,C.green);
  }else if(o.kind==='document'){
   box(-37,-48,74,96,5,C.paper);poly([[16,-48],[37,-27],[16,-27]],C.mint);for(let i=0;i<4;i++)stroke([[-23,-12+i*14],[i===3?5:23,-12+i*14]],3,i===1?C.green:C.line);
  }else if(o.kind==='sugar'){
   poly([[-37,6],[-10,-10],[15,6],[-12,23]],'#FDFBF6');poly([[-37,6],[-12,23],[-12,47],[-37,30]],'#DCDAD0');poly([[-12,23],[15,6],[15,30],[-12,47]],'#ECEADF');poly([[-5,-20],[19,-35],[43,-20],[19,-4]],'#FDFBF6');poly([[-5,-20],[19,-4],[19,20],[-5,4]],'#DCDAD0');poly([[19,-4],[43,-20],[43,4],[19,20]],'#ECEADF');
  }else if(o.kind==='oil'){
   box(-17,-48,34,15,4,C.green);box(-25,-34,50,82,12,C.gold);box(-25,-23,50,17,3,'#E9D9B5');ellipse(0,16,10,16,C.paper);
  }else if(o.kind==='salt'){
   poly([[-28,-24],[28,-24],[38,46],[-38,46]],'#E5E5DC');box(-29,-36,58,14,5,C.green);for(let i=0;i<3;i++)ellipse(-14+i*14,-30,2,2,C.paper);box(-18,-1,36,22,6,C.paper);
  }else if(o.kind==='bottle'){
   box(-19,-48,38,16,4,C.green);box(-30,-32,60,80,12,C.mint);box(-23,-4,46,28,6,C.paper);ellipse(0,10,6,6,C.green);
  }else if(o.kind==='child'){
   ellipse(0,-22,23,26,'#DDC5A4');c.fillStyle=C.ink;c.beginPath();c.arc(0,-30,24,Math.PI,Math.PI*2);c.fill();ellipse(-7,-22,1.5,2,C.ink);ellipse(7,-22,1.5,2,C.ink);stroke([[-4,-11],[4,-11]],1.5);box(-23,6,46,38,15,C.mint);stroke([[-22,17],[-35,34]],9,C.mint);stroke([[22,17],[35,34]],9,C.mint);stroke([[-11,42],[-14,55]],10,C.ink);stroke([[11,42],[14,55]],10,C.ink);
  }else if(o.kind==='plate'){
   ellipse(0,0,49,39,C.paper);c.strokeStyle=C.line;c.lineWidth=3;c.beginPath();c.ellipse(0,0,39,30,0,0,Math.PI*2);c.stroke();poly([[-23,-15],[0,-24],[3,21],[-23,15]],C.green);ellipse(20,2,12,17,C.gold);
  }else if(o.kind==='loop'){
   c.strokeStyle=C.green;c.lineWidth=10;c.beginPath();c.arc(0,0,33,-.6,4.8);c.stroke();poly([[5,-43],[29,-31],[6,-20]],C.green);
  }else if(o.kind==='sprout'){
   ellipse(0,43,45,7,'#D3C4A8');stroke([[0,40],[0,-9]],4,C.ink);c.save();c.rotate(-.5);ellipse(-18,-7,23,11,C.green);c.rotate(1);ellipse(16,-9,25,12,C.green);c.restore();
  }else if(o.kind==='calendar'){
   box(-45,-38,90,83,9,C.paper);box(-45,-38,90,24,6,C.green);stroke([[-23,-47],[-23,-29]],5);stroke([[23,-47],[23,-29]],5);for(let i=0;i<9;i++)box(-30+i%3*23,-2+Math.floor(i/3)*14,13,8,2,i%3===1?C.mint:C.line);
  }else if(o.kind==='corn'){
   ellipse(0,-3,22,43,C.gold);for(let i=0;i<18;i++)ellipse(-11+i%3*11,-32+Math.floor(i/3)*12,3.5,4.5,'#EBDDAB');poly([[-30,12],[-8,24],[0,48],[-20,36]],C.green);poly([[30,-2],[9,23],[0,48],[22,33]],'#95B09A');
  }else if(o.kind==='rice'||o.kind==='oat'){
   for(let i=0;i<9;i++){c.save();c.translate(-27+i%3*26,-27+Math.floor(i/3)*26);c.rotate((i%3-1)*.6);ellipse(0,0,o.kind==='rice'?6:10,15,o.kind==='rice'?'#D8C6A7':C.gold);if(o.kind==='oat')stroke([[0,-10],[0,10]],1,'#B69D73');c.restore()}
  }else if(o.kind==='square'){box(-39,-39,78,78,15,C.mint)}else ellipse(0,0,42,42,C.green);
  c.restore();region(o.id,o.label,x,y,size*1.15,size*1.15);
 }
 function cookie(alpha){
  c.save();c.globalAlpha*=alpha;const pts=Array.from({length:48},(_,i)=>{const a=i/48*Math.PI*2,r=47+1.6*Math.cos(a*12);return [Math.cos(a)*r,Math.sin(a)*r]});poly(pts,C.gold);
  c.strokeStyle='#C3A67C';c.lineWidth=1;c.beginPath();c.arc(0,0,40,0,Math.PI*2);c.stroke();
  for(let i=0;i<15;i++){const a=i*2.399,r=8+Math.sqrt(i)*7;ellipse(Math.cos(a)*r,Math.sin(a)*r,2.2,1.5,'#AC8C65')}c.restore();
 }
 function groups(s){return s.groups.map((g,i)=>({...g,x:160+(i+.5)*960/s.groups.length,y:430}))}
 function grouped(s,o){const gs=groups(s),g=gs.find(v=>v.id===o.group),members=s.objects.filter(v=>v.group===g.id),k=members.findIndex(v=>v.id===o.id),spread=Math.min(110,260/members.length);return {x:g.x+(k-(members.length-1)/2)*spread,y:g.y,size:members.length===1?145:Math.min(145,spread*.98)}}
 function inBowl(s,o){const i=s.objects.findIndex(v=>v.id===o.id),step=Math.min(34,210/Math.max(1,s.objects.length-1));return {x:640+(i-(s.objects.length-1)/2)*step,y:398+(i%2)*17,size:54}}
 function plates(s,alpha){
  if(alpha<=0)return;c.save();c.globalAlpha=alpha;for(const g of groups(s)){ellipse(g.x,g.y+50,128,35,'#C6E3E145');c.strokeStyle=C.line;c.lineWidth=2;c.beginPath();c.ellipse(g.x,g.y+50,128,35,0,0,Math.PI);c.stroke();label(g.label,g.x,572,30)}c.restore();
 }
 function mixture(s,alpha=1,morph=0){
  c.save();c.globalAlpha=alpha;c.translate(640,420);c.scale(2.8,2.8);
  const bowl=[[-50,-25],[-30,-33],[0,-35],[30,-33],[50,-25],[48,-5],[39,22],[24,40],[0,45],[-24,40],[-39,22],[-48,-5]];
  const pts=bowl.map((v,i)=>{const a=-Math.PI+i/12*Math.PI*2;return [lerp(v[0],Math.cos(a)*47,morph),lerp(v[1],Math.sin(a)*47,morph)]});
  // 同一轮廓由碗变成成品外形；图形的身份不随页面重建。
  const col='#'+[0,1,2].map(i=>Math.round(lerp(parseInt(C.mint.slice(1+i*2,3+i*2),16),parseInt(C.gold.slice(1+i*2,3+i*2),16),morph)).toString(16).padStart(2,'0')).join('');c.fillStyle=col;c.beginPath();const last=pts.at(-1),first=pts[0];c.moveTo((last[0]+first[0])/2,(last[1]+first[1])/2);pts.forEach((p,i)=>{const n=pts[(i+1)%pts.length];c.quadraticCurveTo(p[0],p[1],(p[0]+n[0])/2,(p[1]+n[1])/2)});c.closePath();c.fill();
  if(morph<1){c.save();c.globalAlpha*=1-morph;ellipse(0,-25,49,9,'#D8E6DF');c.restore()}
  if(morph>.45)cookie((morph-.45)/.55);
  c.restore();region(s.product.id,s.product.label,640,420,300,300);
 }
 function renderClassify(s,f){
  plates(s,1);
  for(let i=0;i<s.objects.length;i++){
   const o=s.objects[i],to=grouped(s,o),cue=s.cues[o.group].frame,p=phase(f,cue-14,cue),x=160+(i+.5)*960/s.objects.length,y=250+Math.sin(i*1.7)*28;
   icon(o,lerp(x,to.x,p),lerp(y,to.y,p)-Math.sin(p*Math.PI)*55,lerp(112,to.size,p),1,(1-p)*Math.sin(i+1)*.12);
  }
 }
 function renderCombine(s,f){
  const end=s.cues.main.frame,p=phase(f,Math.max(10,end-40),end),show=phase(f,2,13);plates(s,1-phase(f,5,20));mixture(s,show,0);
  for(const o of s.objects){const a=grouped(s,o),b=inBowl(s,o);icon(o,lerp(a.x,b.x,p),lerp(a.y,b.y,p)-Math.sin(p*Math.PI)*125,lerp(a.size,b.size,p),1,(1-p)*Math.sin(p*Math.PI)*.3)}
 }
 function renderTransform(s,f){
  const end=s.cues.main.frame,p=phase(f,end-25,end);
  if(p>=1){icon(s.product,640,420,280);return;}
  if(s.product.kind==='cookie')mixture(s,1,p);else{mixture(s,1-p,0);c.save();c.beginPath();c.arc(640,420,220*p,0,Math.PI*2);c.clip();icon(s.product,640,420,280);c.restore();}
  for(const o of s.objects){const a=inBowl(s,o);icon(o,lerp(a.x,640,p),lerp(a.y,420,p),lerp(a.size,12,p),1-p)}
 }
 function renderQualify(s,f){
  const move=phase(f,0,14),check=phase(f,s.cues.input.frame-7,s.cues.input.frame),question=phase(f,s.cues.main.frame-9,s.cues.main.frame);
  icon(s.product,lerp(640,880,move),lerp(420,410,move),lerp(280,265,move));
  const intro=phase(f,4,17);c.save();c.globalAlpha=intro;ellipse(345,410,155,155,'#C6E3E140');c.restore();
  const cols=Math.ceil(Math.sqrt(s.objects.length)),rows=Math.ceil(s.objects.length/cols),step=Math.min(130,260/Math.max(cols,rows));s.objects.forEach((o,i)=>icon(o,345+(i%cols-(cols-1)/2)*step,405+(Math.floor(i/cols)-(rows-1)/2)*step,Math.min(82,step*.7),intro));
  if(check>0){c.save();c.globalAlpha=check;ellipse(476,292,28,28,C.green);stroke([[462,292],[473,303],[490,282]],4,C.paper);c.restore();}
  label(s.labels.input,345,625,31,intro);
  if(question>0){c.save();c.globalAlpha=question;ellipse(1018,295,55,55,C.paper);c.strokeStyle=C.line;c.lineWidth=2;c.beginPath();c.arc(1018,295,55,0,Math.PI*2);c.stroke();c.textAlign='center';txt('?',1018,320,64,C.ink,600);c.restore();}
  label(s.labels.result,880,625,31,question);
 }
 function question(x,y,p,size=62){if(p<=0)return;c.save();c.globalAlpha*=p;ellipse(x,y,size*.65,size*.65,C.paper);label('?',x,y+size*.32,size);c.restore()}
 function editorial(s,f){
  const a=s.objects,variant=s.variant,end=s.cues.main?.frame||24,p=phase(f,Math.max(0,end-30),end),n=a.length;
  if(variant==='label-question'){
   const q=phase(f,end-16,end);icon(a[0],lerp(640,350,p),420,lerp(245,215,p));label(a[0].label,lerp(640,350,p),589,30);icon(a[1],lerp(640,900,p),418,150,p);icon(a[2],1005,500,115,p);question(882,273,q);label(s.caption,900,610,32,q);
  }else if(variant==='document-focus'){
   icon(a[0],640,400,lerp(150,310,p),1,-.12*(1-p));label(a[0].label,640,598,35,p);
  }else if(variant==='spotlight'){
   if(n===1){for(let i=0;i<7;i++){const t=i/7*Math.PI*2;ellipse(640+Math.cos(t)*lerp(215,145,p),415+Math.sin(t)*lerp(160,115,p),5,9,C.gold)}icon(a[0],640,415,lerp(155,260,p));label(a[0].label,640,610,32,p)}
   else{a.forEach((o,i)=>{const x=240+i*800/(n-1),size=i?lerp(120,180,p):lerp(250,155,p);icon(o,x,410,size,i?lerp(.25,1,p):1);label(o.label,x,595,30)});c.strokeStyle=C.green;c.lineWidth=5;c.beginPath();c.arc(240+800/(n-1),410,lerp(170,119,p),-.8,Math.PI*1.8);c.stroke()}
  }else if(variant==='reveal'){
   const cols=n>3?3:n,rows=Math.ceil(n/cols);a.forEach((o,i)=>{const q=phase(f,s.cues[o.id].frame-14,s.cues[o.id].frame),x=640+(i%cols-(cols-1)/2)*(n>3?310:320),y=rows===1?413:315+Math.floor(i/cols)*210;ellipse(x,y+65,95,17,'#C6E3E145');icon(o,x,y+70*(1-q),n===1?270:n>3?120:175,q,(1-q)*.18);label(o.label,x,y+(n===1?195:128),30,q)});
  }else if(variant==='inspect'){
   a.forEach((o,i)=>{const t=(i-(n-1)/2)*.55,q=phase(f,end-26+i*5,end),x=640+Math.sin(t)*480,y=410+Math.cos(t)*15;icon(o,lerp(640,x,q),lerp(370,y,q),lerp(60,165,q),q);label(o.label,x,595,32,q)});
  }else if(variant==='fit'){
   icon(a[0],lerp(430,480,p),400,lerp(220,260,p));icon(a[1],lerp(900,830,p),410,175);label(a[0].label,480,608,32,p);label(a[1].label,830,608,32,p);question(980,305,p,65);
  }else if(variant==='reframe'){
   a.forEach((o,i)=>{const x=i===0?lerp(640,270,p):n===4?560+(i-1)*250:680+(i-1)*280;icon(o,x,410,i===0?lerp(245,140,p):175,i===0?lerp(1,.5,p):p);label(o.label,x,595,30,i===0?lerp(1,.6,p):p)});question(lerp(770,370,p),310,1-p*.8,47);
  }else if(variant==='unpack'){
   icon(a[0],640,400,240,1-p);a.slice(1).forEach((o,i)=>{const angle=(i/(n-1))*Math.PI*2-Math.PI/2,x=640+Math.cos(angle)*300,y=405+Math.sin(angle)*150;icon(o,lerp(640,x,p),lerp(400,y,p),150,p);label(o.label,x,y+105,29,p)});
  }else if(variant==='routine'){
   a.forEach((o,i)=>{const q=phase(f,s.cues[o.id].frame-15,s.cues[o.id].frame),x=n===2?470+i*390:320+i*320;icon(o,x,420+55*(1-q),i===0?245:i===1?125:165,q);label(o.label,x,610,31,q)});
  }else if(variant==='origin'){
   a.forEach((o,i)=>{const q=phase(f,end-36+i*12,end-24+i*12),x=300+i*340;icon(o,x,lerp(460,410,q),lerp(110,190,q),q,i===0?(1-q)*-.3:0);label(o.label,x,600,31,q)});
  }else if(variant==='selection'){
   ellipse(640,480,178,112,'#F8F5F0');c.strokeStyle=C.line;c.lineWidth=3;c.beginPath();c.ellipse(640,480,156,92,0,0,Math.PI*2);c.stroke();a.forEach((o,i)=>{const x=230+i*820/(n-1),q=phase(f,end-28+i*3,end+i*3),selected=i<2;icon(o,selected?lerp(x,590+i*100,q):x,selected?lerp(258,480,q):258,selected?lerp(115,95,q):115,selected?1:.7);if(!selected)label(o.label,x,350,26,.7)});label(s.caption,640,625,32,p);
  }else if(variant==='calendar'){
   icon(a[0],lerp(640,240,p),lerp(410,420,p),lerp(240,110,p),1-p*.6);
   const x0=490,y0=295,w=620,h=270;box(x0,y0,w,h,18,C.paper);box(x0,y0,w,42,14,C.green);const progress=phase(f,10,end),count=Math.floor(progress*21);for(let i=0;i<21;i++){const x=x0+48+i%7*86,y=y0+84+Math.floor(i/7)*75;box(x-25,y-21,50,43,8,i<count?C.mint:'#EEEDE5');if(i<count){stroke([[x-10,y],[x-2,y+7],[x+12,y-9]],3,C.ink)}}label(s.caption,800,625,38,phase(f,end-12,end));
  }
  if(s.note)label(s.note,640,684,22,phase(f,8,24));
 }
 function draw(s,f){
  regions=[];pale();c.textAlign='left';c.textBaseline='alphabetic';
  txt(s.title,78,112,46,C.ink,600);region('title:'+s.id,s.title,78+s.title.length*23,91,s.title.length*46,60,'label');
  if(s.variant==='classify')renderClassify(s,f);else if(s.variant==='combine')renderCombine(s,f);else if(s.variant==='transform')renderTransform(s,f);else if(s.variant==='qualify')renderQualify(s,f);else editorial(s,f);
 }
 // 透明舞台逐帧独立绘制；不复用会累积透明历史的转场Canvas。
 window.graphicScene=function(s,f){
  const index=inputs.scenes.indexOf(s),prev=inputs.scenes[index-1];
  c.save();
  if(!s.carryFrom&&prev?.type==='graphic'&&f<12){
   // 同样12帧的先退后进，任意一帧只绘制一个页面，避免内容重叠。
   if(f<6){c.globalAlpha=1-phase(f,0,6);draw(prev,prev.endFrame-prev.startFrame-1)}
   else{c.globalAlpha=phase(f,6,12);draw(s,f)}
  }else draw(s,f);
  c.restore();
  window.motionRegions=regions;window.motionState={scene:s.id,variant:s.variant,frame:s.startFrame+f,sourceRefs:s.sourceRefs,regions};
 };
 window.pickMotionObject=(x,y)=>(window.motionRegions||[]).filter(v=>x>=v.bounds[0]&&x<=v.bounds[2]&&y>=v.bounds[1]&&y<=v.bounds[3]).sort((a,b)=>(a.bounds[2]-a.bounds[0])*(a.bounds[3]-a.bounds[1])-(b.bounds[2]-b.bounds[0])*(b.bounds[3]-b.bounds[1]))[0]||null;
})();
