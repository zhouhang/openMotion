// 随包免费食物插画。许可与署名见 food-library.json 及 licenses/OPENMOJI-*。
(()=>{
 const scriptUrl=document.currentScript.src;
 const names=['corn','milk','carrot','egg','sweet-potato','cake','drink'];
 const urls=Object.freeze(Object.fromEntries(names.map(name=>[name,new URL('../assets/food/openmoji/'+name+'.svg',scriptUrl).href])));
 const images=new Map();let ready=null;
 window.MOTION_FOOD_ICON_IMAGES=images;
 window.loadFoodIconLibrary=function(){
  if(!ready)ready=Promise.all(Object.entries(urls).map(([name,url])=>new Promise((resolve,reject)=>{
   const im=new Image();im.onload=()=>{images.set(name,im);resolve()};im.onerror=()=>reject(Error('随包食物插画缺失或无法解码: '+name));im.src=url;
  })));
  return ready;
 };
})();
