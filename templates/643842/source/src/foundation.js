// 新基础绘制层：通用几何与文字，不包含旧产品UI或旧镜头函数。
// 固定适合离线逐帧输出的绘制路径，避免加速图片缓存随绘制历史切换。
const canvas=document.getElementById('film'),c=canvas.getContext('2d',{willReadFrequently:true});
const clamp=value=>value<=0?0:value>=1?1:value;
const ease=value=>{const q=1-clamp(value);return 1-q*q*q};
const lerp=(start,end,progress)=>start+(end-start)*progress;
function text(value,x,y,size,color='#262626',weight=400){c.font=[weight,size+'px','TemplateNoto'].join(' ');c.fillStyle=color;c.fillText(String(value),x,y)}
function box(x,y,width,height,radius,color){c.beginPath();c.roundRect(x,y,width,height,radius);c.fillStyle=color;c.fill()}
function line(x1,y1,x2,y2,color,width=1){c.beginPath();c.moveTo(x1,y1);c.lineTo(x2,y2);c.lineWidth=width;c.strokeStyle=color;c.stroke()}
function dot(x,y,radius,color){c.beginPath();c.arc(x,y,radius,0,Math.PI*2);c.fillStyle=color;c.fill()}
function pale(){c.fillStyle='#f6f4ef';c.fillRect(0,0,1280,720)}
