(async()=>{
const limits=[3379,3386,34024,34076,34921,34930,35660,35661,36347,36348,36349];
function gpu(kind,offscreen=false){
 const c=offscreen?new OffscreenCanvas(64,64):document.createElement('canvas');c.width=c.height=64;
 const g=c.getContext(kind);if(!g)return null;
 const d=g.getExtension('WEBGL_debug_renderer_info'),p={};for(const n of limits){let v=g.getParameter(n);p[n]=ArrayBuffer.isView(v)?Array.from(v):v;}
 const shaderPrecision={};for(const type of [35633,35632])for(const precision of [36336,36337,36338,36339,36340,36341]){const v=g.getShaderPrecisionFormat(type,precision);shaderPrecision[type+','+precision]={rangeMin:v.rangeMin,rangeMax:v.rangeMax,precision:v.precision};}
 const extensions=g.getSupportedExtensions();const missing=extensions.filter(e=>!g.getExtension(e));
 const buffer=g.createBuffer();g.bindBuffer(g.ARRAY_BUFFER,buffer);const liveBinding=g.getParameter(g.ARRAY_BUFFER_BINDING)===buffer;g.bindBuffer(g.ARRAY_BUFFER,null);const liveUnbinding=g.getParameter(g.ARRAY_BUFFER_BINDING)===null;
 const s=g.createShader(g.VERTEX_SHADER);g.shaderSource(s,'attribute vec4 position; void main(){gl_Position=position;}');g.compileShader(s);const shaderCompiled=g.getShaderParameter(s,g.COMPILE_STATUS);
 return {maskedRenderer:g.getParameter(g.RENDERER),vendor:d&&g.getParameter(d.UNMASKED_VENDOR_WEBGL),renderer:d&&g.getParameter(d.UNMASKED_RENDERER_WEBGL),limits:p,shaderPrecision,extensions,missing,liveBinding,liveUnbinding,shaderCompiled,native:Function.prototype.toString.call(g.getParameter)};
}
const workerCode='('+function(){const c=new OffscreenCanvas(32,32),g=c.getContext('webgl'),d=g&&g.getExtension('WEBGL_debug_renderer_info');postMessage({ua:navigator.userAgent,platform:navigator.platform,cores:navigator.hardwareConcurrency,languages:navigator.languages,timezone:Intl.DateTimeFormat().resolvedOptions().timeZone,webgl:g?{vendor:d&&g.getParameter(d.UNMASKED_VENDOR_WEBGL),renderer:d&&g.getParameter(d.UNMASKED_RENDERER_WEBGL),maxTexture:g.getParameter(g.MAX_TEXTURE_SIZE)}:null})}.toString()+')();';
const url=URL.createObjectURL(new Blob([workerCode],{type:'text/javascript'}));
const worker=await new Promise((resolve,reject)=>{const w=new Worker(url),t=setTimeout(()=>{w.terminate();reject(Error('Worker timeout'))},10000);w.onmessage=e=>{clearTimeout(t);w.terminate();resolve(e.data)};w.onerror=e=>{clearTimeout(t);reject(Error(e.message))}});URL.revokeObjectURL(url);
const headers=await(await fetch('/headers?fresh='+Date.now(),{cache:'no-store'})).json();
const out={main:{ua:navigator.userAgent,platform:navigator.platform,cores:navigator.hardwareConcurrency,languages:navigator.languages,timezone:Intl.DateTimeFormat().resolvedOptions().timeZone},worker,headers,webgl:gpu('webgl'),webgl2:gpu('webgl2'),offscreen:gpu('webgl',true),webgpu:typeof navigator.gpu,screen:{width:screen.width,height:screen.height,availWidth:screen.availWidth,availHeight:screen.availHeight},rtc:typeof RTCPeerConnection};
document.querySelector('#result').textContent=JSON.stringify(out);document.querySelector('#result').dataset.ready='true';
})().catch(e=>{document.querySelector('#result').textContent=JSON.stringify({error:e.message});document.querySelector('#result').dataset.ready='true'});
