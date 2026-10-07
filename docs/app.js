/* ISL live demo: MediaPipe HandLandmarker (CDN, on demand) + 14KB centroid model. All on-device. */
(() => {
"use strict";
const $ = id => document.getElementById(id);
const video=$("video"), canvas=$("overlay"), ctx=canvas.getContext("2d");
const ph=$("ph"), startBtn=$("startBtn"), stopBtn=$("stopBtn"), pill=$("statusPill"), statusTxt=$("statusTxt");
const bigLetter=$("bigLetter"), confFill=$("confFill"), confVal=$("confVal");
const msVal=$("msVal"), fpsVal=$("fpsVal"), stabVal=$("stabVal"), sentence=$("sentence");
const CONN=[[0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],[5,9],[9,10],[10,11],[11,12],[9,13],[13,14],[14,15],[15,16],[13,17],[17,18],[18,19],[19,20],[0,17]];
let landmarker=null, model=null, running=false, stream=null, raf=0, lastT=0, fpsEMA=0;
let lastLetter="-", stable=0, addedFor="", lastVec=null;

function setStatus(txt, cls){ statusTxt.textContent=txt; pill.className="pill"+(cls?" "+cls:""); }
function fitCanvas(){ const r=video.getBoundingClientRect(); const d=Math.min(devicePixelRatio||1,2);
  canvas.width=Math.max(2,r.width*d); canvas.height=Math.max(2,r.height*d); }
addEventListener("resize", ()=>{ if(running) fitCanvas(); });

async function ensureModel(){
  if(model) return model;
  const r=await fetch("centroids.json",{cache:"force-cache"});
  if(!r.ok) throw new Error("centroids.json missing");
  model=await r.json(); return model;
}
async function ensureLandmarker(onProgress){
  if(landmarker) return landmarker;
  const vision=await import("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/vision_bundle.mjs");
  const fileset=await vision.FilesetResolver.forVisionTasks(
    "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm");
  onProgress&&onProgress("downloading hand model…");
  landmarker=await vision.HandLandmarker.createFromOptions(fileset,{
    baseOptions:{modelAssetPath:"https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",delegate:"GPU"},
    runningMode:"VIDEO",numHands:1,minHandDetectionConfidence:.4,minHandPresenceConfidence:.4,minTrackingConfidence:.4});
  return landmarker;
}
function toVec(lm){ const w=lm[0], v=new Float32Array(63);
  for(let i=0;i<21;i++){ v[i*3]=lm[i].x-w.x; v[i*3+1]=lm[i].y-w.y; v[i*3+2]=lm[i].z-w.z; } return v; }
function classify(v){
  const C=model.centroids, L=model.labels, TAU=0.35, n=C.length;
  const d=new Float64Array(n); let best=0, bd=Infinity;
  for(let i=0;i<n;i++){ const c=C[i]; let s=0;
    for(let j=0;j<63;j++){ const e=v[j]-c[j]; s+=e*e; }
    d[i]=s; if(s<bd){bd=s;best=i;} }
  let sum=0; const p=new Float64Array(n);
  for(let i=0;i<n;i++){ p[i]=Math.exp(-(d[i]-bd)/TAU); sum+=p[i]; }
  return {letter:L[best], conf:p[best]/sum};
}
function draw(lm){
  const W=canvas.width,H=canvas.height; ctx.clearRect(0,0,W,H);
  if(!lm) return;
  const px=lm.map(p=>[ (1-p.x)*W, p.y*H ]); // mirrored to match selfie video
  ctx.lineWidth=Math.max(2,W/240); ctx.strokeStyle="#4ade80"; ctx.beginPath();
  for(const [a,b] of CONN){ ctx.moveTo(px[a][0],px[a][1]); ctx.lineTo(px[b][0],px[b][1]); }
  ctx.stroke(); ctx.fillStyle="#f87171";
  for(const [x,y] of px){ ctx.beginPath(); ctx.arc(x,y,Math.max(2.5,W/160),0,7); ctx.fill(); }
}
function loop(){
  if(!running) return;
  const now=performance.now(), dt=now-(lastT||now); lastT=now;
  if(dt>0) fpsEMA=fpsEMA?fpsEMA*.9+(1000/dt)*.1:1000/dt;
  let t0=performance.now();
  try{
    const res=landmarker.detectForVideo(video,now);
    const ms=performance.now()-t0;
    const lm=res&&res.landmarks&&res.landmarks[0];
    draw(lm||null);
    if(lm){
      const v=toVec(lm); lastVec=v;
      const {letter,conf}=classify(v);
      bigLetter.textContent=letter;
      confFill.style.width=Math.round(conf*100)+"%"; confVal.textContent=Math.round(conf*100)+"%";
      msVal.textContent=Math.round(ms)+" ms"; fpsVal.textContent=Math.round(fpsEMA);
      if(letter===lastLetter&&conf>.45){ stable++; } else { stable=0; addedFor=""; }
      lastLetter=letter; stabVal.textContent=stable+"f";
      if(stable>=12&&addedFor!==letter){ sentence.textContent+=letter; addedFor=letter; stable=0; }
      setStatus("tracking","live");
    } else {
      bigLetter.textContent="–"; confFill.style.width="0"; confVal.textContent="0%";
      msVal.textContent=Math.round(ms)+" ms"; fpsVal.textContent=Math.round(fpsEMA);
      stabVal.textContent="–"; lastLetter="-"; stable=0; addedFor="";
      setStatus("no hand","warn");
    }
  }catch(e){ setStatus("error","warn"); }
  raf=requestAnimationFrame(loop);
}
startBtn.onclick=async ()=>{
  startBtn.disabled=true;
  try{
    setStatus("loading camera…");
    stream=await navigator.mediaDevices.getUserMedia({video:{width:{ideal:640},height:{ideal:480},facingMode:"user"},audio:false});
    video.srcObject=stream; await video.play();
    ph.style.display="none"; fitCanvas();
    setStatus("loading AI…"); await ensureModel();
    await ensureLandmarker(t=>setStatus(t));
    running=true; lastT=0; stopBtn.disabled=false;
    setStatus("tracking","live"); loop();
  }catch(e){
    console.error(e); setStatus(location.protocol!=="https:"&&location.hostname!=="localhost"?"needs https":"camera/AI failed","warn");
    startBtn.disabled=false;
  }
};
function stop(){
  running=false; cancelAnimationFrame(raf);
  if(stream){ stream.getTracks().forEach(t=>t.stop()); stream=null; }
  video.srcObject=null; ph.style.display="flex"; ctx.clearRect(0,0,canvas.width,canvas.height);
  stopBtn.disabled=true; startBtn.disabled=false; setStatus("idle");
  bigLetter.textContent="–"; confFill.style.width="0"; confVal.textContent="0%";
  msVal.textContent="–"; fpsVal.textContent="–"; stabVal.textContent="–";
}
stopBtn.onclick=stop;
$("addBtn").onclick=()=>{ if(lastLetter&&lastLetter!=="-") sentence.textContent+=lastLetter; };
$("spaceBtn").onclick=()=>{ sentence.textContent+=" "; };
$("backBtn").onclick=()=>{ sentence.textContent=sentence.textContent.slice(0,-1); };
$("clearBtn").onclick=()=>{ sentence.textContent=""; };
$("speakBtn").onclick=()=>{ const t=sentence.textContent.trim(); if(!t||!("speechSynthesis" in window)) return;
  speechSynthesis.cancel(); const u=new SpeechSynthesisUtterance(t); u.rate=.9; speechSynthesis.speak(u); };
})();
