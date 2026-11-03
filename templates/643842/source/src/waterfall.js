// 倾斜图片平面采用透视投影；文字单独在正面绘制，不接受墙面变换。
const waterfallTextures=new Map();
function waterfallTexture(url){
 if(waterfallTextures.has(url))return waterfallTextures.get(url);
 const img=loaded.get(url),w=280,h=Math.round(Math.max(175,Math.min(300,w*img.naturalHeight/img.naturalWidth))),tex=document.createElement('canvas');tex.width=w;tex.height=h;
 const ctx=tex.getContext('2d',{willReadFrequently:true}),k=Math.max(w/img.naturalWidth,h/img.naturalHeight);
 ctx.beginPath();ctx.roundRect(0,0,w,h,13);ctx.clip();ctx.fillStyle='#F8F5F0';ctx.fillRect(0,0,w,h);ctx.drawImage(img,(w-img.naturalWidth*k)/2,(h-img.naturalHeight*k)/2,img.naturalWidth*k,img.naturalHeight*k);
 waterfallTextures.set(url,tex);return tex;
}
function waterfallProject(x,y,t){
 const ay=-.31,ax=.22,az=-.14;
 const xx=x*Math.cos(ay),z=-x*Math.sin(ay),yy=y*Math.cos(ax)-z*Math.sin(ax),zz=y*Math.sin(ax)+z*Math.cos(ax),px=xx*Math.cos(az)-yy*Math.sin(az),py=xx*Math.sin(az)+yy*Math.cos(az),k=1550/(1550+zz);
 return [830+px*k+240*Math.sin(t*.34-.7),350+py*k];
}
function waterfallCards(s,t){
 const cards=[],cols=s.columns,pitch=232;
 for(let col=0;col<cols;col++){
  const list=s.imageUrls.map((url,index)=>({url,index})).filter(v=>v.index%cols===col).map(v=>({...v,tex:waterfallTexture(v.url)}));
  let period=list.reduce((sum,v)=>sum+v.tex.height*214/280+18,0),cursor=0;
  const rate=(col%2===0?1:-1)*(48+col*8)*s.speed,travel=t*rate+col*89;
  for(const item of list){
   const h=item.tex.height*214/280,origin=((cursor+travel+650)%period+period)%period-650;
   for(let repeat=-1;repeat<=Math.ceil(1500/period)+1;repeat++){
    const y=origin+repeat*period;if(y>750||y+h< -750)continue;
    const x=(col-(cols-1)/2)*pitch-107,quad=[[x,y],[x+214,y],[x+214,y+h],[x,y+h]].map(([a,b])=>waterfallProject(a,b,t));
    if(Math.max(...quad.map(p=>p[0]))<380||Math.min(...quad.map(p=>p[0]))>1320||Math.max(...quad.map(p=>p[1]))<80||Math.min(...quad.map(p=>p[1]))>650)continue;
    cards.push({...item,x,y,w:214,h,quad});
   }
   cursor+=h+18;
  }
 }
 return cards;
}
// 将小块纹理映射到透视三角面，避免把整张图片硬拉成矩形。
function waterfallTriangle(tex,source,target){
 const [a,b,d]=source,[p,q,r]=target,det=(b[0]-a[0])*(d[1]-a[1])-(d[0]-a[0])*(b[1]-a[1]);
 const aa=((q[0]-p[0])*(d[1]-a[1])-(r[0]-p[0])*(b[1]-a[1]))/det,cc=((r[0]-p[0])*(b[0]-a[0])-(q[0]-p[0])*(d[0]-a[0]))/det;
 const bb=((q[1]-p[1])*(d[1]-a[1])-(r[1]-p[1])*(b[1]-a[1]))/det,dd=((r[1]-p[1])*(b[0]-a[0])-(q[1]-p[1])*(d[0]-a[0]))/det;
 c.save();c.beginPath();const cx=(p[0]+q[0]+r[0])/3,cy=(p[1]+q[1]+r[1])/3;
 target.forEach(([x,y],i)=>{const dx=x-cx,dy=y-cy,k=1.8/Math.max(1,Math.hypot(dx,dy));i?c.lineTo(x+dx*k,y+dy*k):c.moveTo(x+dx*k,y+dy*k)});c.closePath();c.clip();
 c.transform(aa,bb,cc,dd,p[0]-aa*a[0]-cc*a[1],p[1]-bb*a[0]-dd*a[1]);c.drawImage(tex,0,0);c.restore();
}
function waterfallTile(card,t){
 const {tex,x,y,w,h,quad}=card;
 c.save();c.beginPath();quad.forEach((p,i)=>i?c.lineTo(...p):c.moveTo(...p));c.closePath();c.clip();
 const n=3;
 for(let row=0;row<n;row++)for(let col=0;col<n;col++){
  const uv=[[col/n,row/n],[(col+1)/n,row/n],[(col+1)/n,(row+1)/n],[col/n,(row+1)/n]],src=uv.map(([u,v])=>[u*tex.width,v*tex.height]),dst=uv.map(([u,v])=>waterfallProject(x+u*w,y+v*h,t));
  waterfallTriangle(tex,[src[0],src[1],src[2]],[dst[0],dst[1],dst[2]]);waterfallTriangle(tex,[src[0],src[2],src[3]],[dst[0],dst[2],dst[3]]);
 }
 c.restore();
}
function waterfallScene(s,t){
 const cards=waterfallCards(s,t),visible=q(t,0,1.2)*(1-q(t,s.duration-1.2,s.duration));
 group(visible,()=>{clip(380,93,900,548,()=>{for(const card of cards)waterfallTile(card,t)});});
 // 月白渐隐层隔开阅读区与运动区，保持标题和来源始终清晰。
 const fade=c.createLinearGradient(350,0,610,0);fade.addColorStop(0,'#F8F5F0');fade.addColorStop(1,'#F8F5F000');c.fillStyle=fade;c.fillRect(350,93,260,548);
 group(q(t,.6,1.4),()=>{s.heading.forEach((v,i)=>txt(v,78,255+i*61,46,ink,600));txt(s.description,78,368,22);txt(s.imageUrls.length+' 张素材 / '+s.columns+' 列流动',78,416,16);});
 group(q(t,2.2,3)*(1-q(t,s.duration-2,s.duration-1.4)),()=>{
  // 瀑布墙只保留主题文字，不绘制机器人及连线。
  txt(s.annotation,78,535,23,ink,600);
 });
}
