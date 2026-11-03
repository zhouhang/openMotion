// 参考公开动作配方独立实现；开头按标题长度，结尾按真实Logo选择。
function measured(s,size=44,weight=600){c.font=weight+' '+size+'px TemplateNoto';return c.measureText(s).width}
function fitSize(s,max,preferred,weight=600){return Math.min(preferred,preferred*max/Math.max(1,measured(s,preferred,weight)))}
function centered(s,y,size=44,weight=600){txt(s,640-measured(s,size,weight)/2,y,size,ink,weight)}
function leadOpening(s,t){
 const p=q(t,.85,2.1),size=fitSize(s.title,1060,58),idx=s.title.indexOf(s.lead),prefix=s.title.slice(0,idx),suffix=s.title.slice(idx+s.lead.length),left=640-measured(s.title,size)/2;
 const leadSize=lerp(fitSize(s.lead,1000,148),size,p),leadX=lerp(640-measured(s.lead,leadSize)/2,left+measured(prefix,size),p),baseline=lerp(358,326,p);
 group(q(t,0,.35),()=>txt(s.lead,leadX,baseline,leadSize,ink,600));
 group(q(t,1.25,2.15),()=>{txt(prefix,left-25*(1-p),326+10*(1-p),size,ink,600);txt(suffix,left+measured(prefix+s.lead,size)+25*(1-p),326+10*(1-p),size,ink,600)});
 group(q(t,2.1,2.8),()=>centered(s.subtitle,405,fitSize(s.subtitle,1000,27,500),500));
}
function demoteOpening(s,t){
 // 长标题先以可读的一整行呈现，再沿同一基线缩回页眉，避免两行汇合时互相压叠。
 const chars=Array.from(s.title),size=fitSize(s.title,1060,56),rows=[s.title];
 const p=q(t,2.5,3.9),font=lerp(size,16,p),finalLeft=78;let offset=0;
 group(q(t,0,.65),()=>{for(let ri=0;ri<rows.length;ri++){
  const value=rows[ri],start=640-measured(value,size)/2,baseline=rows.length===1?305:272+ri*72;
  Array.from(value).forEach((ch,i)=>{const sourceX=start+measured(Array.from(value).slice(0,i).join(''),size),targetX=finalLeft+measured(chars.slice(0,offset+i).join(''),16);txt(ch,lerp(sourceX,targetX,p),lerp(baseline,58,p),font,ink,600)});offset+=Array.from(value).length;
 }});
 group(q(t,.7,1.3)*(1-q(t,2.5,3.2)),()=>centered(s.subtitle,rows.length>1?452:405,fitSize(s.subtitle,1050,25,500),500));
 group(q(t,3.5,4.3),()=>{rule(78,80,1124);txt(s.subtitle,78,278,fitSize(s.subtitle,1100,33,500),ink,500)});
}
function summaryRows(s,t,morph=false){
 const gather=morph?q(t,3.6,4.6):0,opacity=morph?1-q(t,4.2,4.7):1,drift=morph?0:8*q(t,1.5,6);
 group(opacity,()=>{centered(s.title,160,fitSize(s.title,1080,38));s.items.forEach((value,i)=>{
  const start=.35+i*.5,p=q(t,start,start+.7),bounce=5*Math.sin(Math.max(0,t-start)*15)*Math.exp(-Math.max(0,t-start)*6),y=lerp(212+i*91-drift+22*(1-p)+bounce,294,gather),x=lerp(140,290,gather),w=lerp(1000,700,gather);
  group(p,()=>{surface(x,y,w,70);txt(String(i+1).padStart(2,'0'),x+25,y+44,18);txt(value,x+90,y+45,27,ink,600)});
 })});
}
function brandMorphEnding(s,t){
 summaryRows(s,t,true);
 const contract=q(t,5.1,6.3),unfold=q(t,6.3,7.5),w=lerp(lerp(720,160,contract),330,unfold),h=lerp(72,250,unfold),x=640-w/2,y=330-h/2;
 group(q(t,4.25,4.7),()=>{
  surface(x,y,w,h);
  group(1-q(t,5,5.55),()=>{const font=fitSize(s.title,w-80,27),tw=measured(s.title,font);txt(s.title,640-tw/2,340,font,ink,600);line(640+tw/2+9,313,640+tw/2+9,345,ink,2)});
  group(q(t,6.5,7.4),()=>{clip(x+12,y+12,w-24,h-24,()=>contain(loaded.get(s.logoUrl),640-100*unfold,330-100*unfold,200*unfold,200*unfold))});
 });
 const font=fitSize(s.brand,1000,44),left=640-measured(s.brand,font)/2;
 Array.from(s.brand).forEach((ch,i)=>{const p=q(t,7.35+i*.045,8.05+i*.045);group(p,()=>txt(ch,left+measured(Array.from(s.brand).slice(0,i).join(''),font)+28*(1-p),510+14*(1-p),font,ink,600))});
 group(q(t,8.1,8.65),()=>centered(s.tagline||'',559,fitSize(s.tagline||'',1060,22,500),500));
}
function bookendScene(s,t){
 if(s.type==='opening'){
  // 只在最后短淡出，长标题结束处保留页眉供下一素材模块接续。
  const opacity=s.variant==='title-demote-to-label'?1:1-q(t,s.duration-.35,s.duration);
  group(opacity,()=>s.variant==='lead-word-zoom-assemble'?leadOpening(s,t):demoteOpening(s,t));
 }else if(s.variant==='ui-to-brand-morph')brandMorphEnding(s,t);
 else{summaryRows(s,t);if(s.brand)group(q(t,2.5,3.2),()=>centered(s.brand,622,20,500));}
}
