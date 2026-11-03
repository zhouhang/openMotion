// 编辑式舞台：保留原场景的时间与方法，人物、标注和Logo由实例提供。
(()=>{
 const baseRender=window.renderFrame,baseLoad=window.loadAdaptive;
 let settings=null,layoutPlan=null,logo=null;const cache=new Map();
 const scratch=document.createElement('canvas');
 function label(value,x,y,size,weight=400,color='#424B50'){
  if(!value)return;c.save();c.font=weight+' '+size+'px TemplateNoto';c.textAlign='left';c.textBaseline='alphabetic';c.fillStyle=color;
  c.fillText(value,x,y+c.measureText(value).actualBoundingBoxAscent);c.restore();
 }
 function fit(image,x,y,w,h){const scale=Math.min(w/image.width,h/image.height);c.drawImage(image,x+(w-image.width*scale)/2,y+(h-image.height*scale)/2,image.width*scale,image.height*scale)}
 function load(url){return new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>reject(Error('编辑式素材无法读取'));im.src=url})}
 async function portrait(f){if(!settings.frameBase)return null;if(!cache.has(f))cache.set(f,await load(settings.frameBase+String(f).padStart(5,'0')+'.jpg'));while(cache.size>32)cache.delete(cache.keys().next().value);return cache.get(f)}
 window.loadAdaptive=async(p,pl)=>{
  settings=null;cache.clear();await baseLoad(p,pl);settings=p.presentation||null;layoutPlan=pl;logo=null;
  if(settings?.logoUrl)logo=await load(settings.logoUrl);
  if(settings){
   window.verifyLicensedFont({items:[settings.heading||'',settings.footer||'',settings.roleLabel||'',settings.nameLabel||'',...(settings.pageLabels||[])]},pl);
   const capacity=[['heading',16,1100],['footer',15,1152],['roleLabel',20,258],['nameLabel',14,258]];
   for(const [key,size,width] of capacity){c.font='500 '+size+'px TemplateNoto';if(c.measureText(settings[key]||'').width>width)throw Error('标注实际字宽超容量: '+key)}
  }
 };
 window.renderFrame=async function(f){
  c.lineCap='butt';c.lineJoin='miter';c.globalAlpha=1;c.globalCompositeOperation='source-over';c.setLineDash([]);
  if(!settings)return baseRender(f);
  if(!Number.isInteger(f)||f<0||f>=layoutPlan.totalFrames)throw Error('编辑式整数帧越界');
  const original=pale;
  try{pale=function(){c.clearRect(0,0,1280,720)};await baseRender(f)}finally{pale=original}
  const ratio=canvas.width/1280,top=Math.round(160*ratio),side=Math.round(128*ratio);
  for(const left of [0,Math.round(1152*ratio)]){
   const pixels=c.getImageData(left,top,side,canvas.height-top).data;
   for(let a=3;a<pixels.length;a+=4)if(pixels[a]>16)throw Error('编辑式内容超出舞台容量，请缩短标签、调整场景或使用原版式；帧 '+f);
  }
  scratch.width=canvas.width;scratch.height=canvas.height;scratch.getContext('2d').drawImage(canvas,0,0);
  original();const k=canvas.width/1280;
  c.drawImage(scratch,128*k,160*k,1024*k,560*k,64,194,816,446);
  const s=inputs.scenes.find(v=>f>=v.startFrame&&f<v.endFrame),i=inputs.scenes.indexOf(s);
  c.save();
  if(logo){c.save();c.beginPath();c.arc(80,52,16,0,Math.PI*2);c.clip();fit(logo,64,36,32,32);c.restore()}
  label(settings.heading||'',logo?106:64,44,17,500,'#748B84');
  label(String(i+1).padStart(2,'0')+' / '+(settings.pageLabels?.[i]||'内容讲解'),1042,44,16,400,'#748B84');
  line(64,83,1216,83,'#CADBD2');line(64,656,1216,656,'#CADBD2');label(settings.footer||'',64,678,15,400,'#748B84');
  c.globalAlpha=ease((f-s.startFrame+1)/10);label(s.title,64,124,36,650);c.globalAlpha=1;
  const px=910+Math.floor((1-ease(f/24/.65))*16),py=178;
  box(px,py,306,464,36,'#DDECE5');line(px+26,py+420,px+280,py+420,'#BED2C7');
  label(settings.roleLabel||'',px+24,py+391,20,500);label(settings.nameLabel||'',px+24,py+435,14,400,'#748B84');
  const im=await portrait(f),[w,h]=settings.portraitSize||[256,356],x=px+(306-w)/2,y=py+16+(366-h)/2;
  if(im){c.save();c.beginPath();c.roundRect(x,y,w,h,30);c.clip();c.drawImage(im,x,y,w,h);c.restore()}
  else{box(x,y,w,h,30,'#C8DED3');label('人物素材输入区',px+60,py+170,22,500);label('示意 · 未提供人物',px+64,py+207,16,400,'#748B84')}
  c.restore();
 };
})();
