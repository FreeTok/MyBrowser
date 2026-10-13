async function hash(x){return [...new Uint8Array(await crypto.subtle.digest('SHA-256',x))].map(x=>x.toString(16).padStart(2,'0')).join('')}
async function render(kind,offscreen=false){
 let c=offscreen?new OffscreenCanvas(256,128):document.createElement('canvas');c.width=256;c.height=128;
 let gl=c.getContext(kind,{preserveDrawingBuffer:true,antialias:true});if(!gl)return {available:false};
 const is2=kind==='webgl2';
 const shaders=is2?['#version 300 es\nin vec2 p;out vec2 v;void main(){v=p;gl_Position=vec4(p,0.0,1.0);}', '#version 300 es\nprecision highp float;in vec2 v;out vec4 color;void main(){float t=sin(v.x*19.39)*cos(v.y*27.71);color=vec4(fract(t*0.731),fract(t*2.179),sin(t*3.77)*0.5+0.5,1.0);}']:['attribute vec2 p;varying vec2 v;void main(){v=p;gl_Position=vec4(p,0.0,1.0);}','precision highp float;varying vec2 v;void main(){float t=sin(v.x*19.39)*cos(v.y*27.71);gl_FragColor=vec4(fract(t*0.731),fract(t*2.179),sin(t*3.77)*0.5+0.5,1.0);}'];
 let p=gl.createProgram();for(let i=0;i<2;i++){let s=gl.createShader(i?gl.FRAGMENT_SHADER:gl.VERTEX_SHADER);gl.shaderSource(s,shaders[i]);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));gl.attachShader(p,s)}
 gl.linkProgram(p);if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(p));gl.useProgram(p);
 let b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-0.83,-0.71,0.99,-0.51,-0.41,0.91]),gl.STATIC_DRAW);
 let loc=gl.getAttribLocation(p,'p');gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,2,gl.FLOAT,false,0,0);
 gl.clearColor(0.1,0.2,0.3,1);gl.clear(gl.COLOR_BUFFER_BIT);gl.drawArrays(gl.TRIANGLES,0,3);gl.finish();
 let hashes=[];for(let i=0;i<3;i++){let pixels=new Uint8Array(256*128*4);gl.readPixels(0,0,256,128,gl.RGBA,gl.UNSIGNED_BYTE,pixels);hashes.push(await hash(pixels))}
 let encoded=offscreen?await hash(await (await c.convertToBlob()).arrayBuffer()):await hash(new TextEncoder().encode(c.toDataURL()));
 let ext=gl.getExtension('WEBGL_debug_renderer_info');return {available:true,hashes,encoded,error:gl.getError(),vendor:ext?gl.getParameter(ext.UNMASKED_VENDOR_WEBGL):null,renderer:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):null,maskedRenderer:gl.getParameter(gl.RENDERER),context:gl.getContextAttributes(),samples:gl.getParameter(gl.SAMPLES),extensions:gl.getSupportedExtensions()};
}
async function workerRender(){
 const code=hash.toString()+';'+render.toString()+';('+async function(){try{postMessage({ua:navigator.userAgent,cores:navigator.hardwareConcurrency,languages:navigator.languages,timezone:Intl.DateTimeFormat().resolvedOptions().timeZone,render:await render('webgl',true)})}catch(e){postMessage({error:String(e)})}}.toString()+')()';
 const url=URL.createObjectURL(new Blob([code],{type:'text/javascript'}));try{return await new Promise((resolve,reject)=>{const w=new Worker(url),t=setTimeout(()=>{w.terminate();reject(Error('Worker timeout'))},30000);w.onmessage=e=>{clearTimeout(t);w.terminate();resolve(e.data)};w.onerror=e=>{clearTimeout(t);w.terminate();reject(Error(e.message))}})}finally{URL.revokeObjectURL(url)}
}
(async()=>{try{let result={gl1:await render('webgl'),gl2:await render('webgl2'),offscreen:await render('webgl',true),worker:await workerRender()};document.querySelector('#result').textContent=JSON.stringify(result);document.querySelector('#result').dataset.ready='true'}catch(e){document.querySelector('#result').textContent=JSON.stringify({error:String(e)});document.querySelector('#result').dataset.ready='true'}})();
