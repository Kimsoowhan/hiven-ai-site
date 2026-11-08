/* 비상대응 체계를 자동화 통합 통제 시스템 안으로 산입(대표님 11/07 13:33): ① 머리띠 대응 모드에 현재 단계 표시 ② SC-01 종합 현황 맨 위에 비상대응 단계 상자 ③ 화면 핵심 파일 무결성 검사(변조 의심=경보 등급). */
(function(){
 var G=['정상','관찰','관찰','주의','주의','경보','경보','경고','경고','위기'];
 function st(){var s;try{s=JSON.parse(localStorage.getItem('hvsec')||'{}')}catch(e){s={}}var n=s.n||0,l=n>=6?10:n>=4?8:n>=3?6:n>=2?4:n>=1?2:1;if(s.u&&s.u>Date.now())l=Math.max(l,6);return {n:n,l:l,s:s}}
 window.hvEmLevel=function(){return st().l};
 function chip(){var c=document.getElementById('chip-mode');if(!c)return;var x=st();c.innerHTML='<span class="dot '+(x.l>=6?'bad':x.l>=2?'warn':'ok')+'"></span>대응 모드 <b>단계 '+x.l+' '+G[x.l-1]+'</b> · 발령 <b>'+['안심','관심','관심','주의','주의','경계','경고','위험','위기','위기'][x.l-1]+'</b>'+(x.n>=1?' · <b>보호 단계 전환</b>':'')}
 window.hvChip=chip;
 setInterval(chip,3000);chip();
 /* 알람 발생 시(단계 2 이상) SC-01 맨 위: [위기대응 경보체계 가동] 배너 + 단계 상자 깜박임(대표님 11/07 15:19, 구현·구성은 Sonnet 일임) */
 (function(){var k=document.createElement('style');k.textContent='@keyframes hvblink{0%,100%{opacity:1}50%{opacity:.25}}@keyframes hvglow{0%,100%{box-shadow:0 0 0 0 rgba(198,40,40,.0)}50%{box-shadow:0 0 0 6px rgba(198,40,40,.45)}}.hvblink{animation:hvblink 1s steps(2,start) infinite}.hvglow{animation:hvglow 1s ease-in-out infinite}@media (prefers-reduced-motion:reduce){.hvblink,.hvglow{animation:none}}';document.head.appendChild(k)})();
 /* 경보음(사이렌): 단계 2 이상이면 브라우저(PC·모바일)에서 소리·진동. 브라우저 정책상 화면을 한 번 누른 뒤부터 소리가 난다 */
 var SND={ac:null,ack:0,on:true,blocked:false,playing:false,test:0};SND.on=true;/* 켜짐은 시스템이 알람 발생 시 자동, 사용자는 끄기(정지)만 */
 function ac(){if(!SND.ac){try{SND.ac=new (window.AudioContext||window.webkitAudioContext)()}catch(e){}}return SND.ac}
 function unlock(){var c=ac();if(c&&c.state==='suspended'){try{c.resume()}catch(e){}}if(c&&c.state==='running')SND.blocked=false}
 ['pointerdown','click','keydown','touchstart'].forEach(function(n){window.addEventListener(n,unlock,true)});
 function tone(f1,f2,t0,d,vol){var c=SND.ac;var o=c.createOscillator(),g=c.createGain();o.type='square';o.frequency.setValueAtTime(f1,t0);if(f2)o.frequency.linearRampToValueAtTime(f2,t0+d);g.gain.setValueAtTime(0,t0);g.gain.linearRampToValueAtTime(vol,t0+.02);g.gain.setValueAtTime(vol,t0+d-.03);g.gain.linearRampToValueAtTime(0,t0+d);o.connect(g);g.connect(c.destination);o.start(t0);o.stop(t0+d+.02)}
 function cycle(l){var c=ac();if(!c)return false;if(c.state!=='running'){try{c.resume()}catch(e){}SND.blocked=true;return false}SND.blocked=false;var t=c.currentTime+.05;
  if(l>=6){tone(650,1000,t,.55,.18);tone(1000,650,t+.55,.55,.18)}else{tone(880,0,t,.16,.14);tone(880,0,t+.3,.16,.14)}
  try{if(navigator.vibrate)navigator.vibrate(l>=6?[400,150,400]:[200,100,200])}catch(e){}return true}
 function sig(x){return x.l*1000+(x.s.L||[]).length}
 window.hvSirenTest=function(){unlock();SND.test=Date.now()+3500;var n=0,h=setInterval(function(){if(Date.now()>SND.test||n++>4){clearInterval(h);return}cycle(6)},1100);cycle(6)};
 window.hvSirenAck=function(ev){if(ev&&ev.stopPropagation)ev.stopPropagation();SND.ack=sig(st());SND.playing=false;var w=document.getElementById('hvemw');if(w)w.innerHTML=emHtml(st())};
 window.hvSirenToggle=function(ev){if(ev&&ev.stopPropagation)ev.stopPropagation();SND.on=!SND.on;try{localStorage.setItem('hvsound',SND.on?'1':'0')}catch(e){}unlock();var w=document.getElementById('hvemw');if(w)w.innerHTML=emHtml(st());if(window.hvSb)hvSb()};
 var T0=document.title;
 setInterval(function(){var x=st(),al=x.l>=2&&sig(x)>SND.ack;SND.playing=false;
  if(x.l>=2){document.title=(Math.floor(Date.now()/1000)%2?'\u{1F6A8} ':'')+'[위기대응 경보체계 가동] '+T0}else if(document.title!==T0){document.title=T0}
  if(al&&SND.on){SND.playing=cycle(x.l)}},1300);
 /* 기기별 연동(대표님 15:23): 소리 켜기·끄기·확인은 기기마다 따로 저장되고(PC·노트북·폰), 같은 기기의 다른 탭에는 즉시 같이 적용된다. 기기 알림(시스템 알림·진동)과도 연결한다 */
 window.addEventListener('storage',function(e){if(e.key==='hvack'){SND.ack=+e.newValue||0}else return;var w=document.getElementById('hvemw');if(w)w.innerHTML=emHtml(st())});
 try{SND.ack=+localStorage.getItem('hvack')||0}catch(e){}
 var oAck=window.hvSirenAck;window.hvSirenAck=function(ev){oAck(ev);try{localStorage.setItem('hvack',String(SND.ack))}catch(e){}};
 window.hvDevAsk=function(ev){if(ev&&ev.stopPropagation)ev.stopPropagation();unlock();try{if(window.Notification&&Notification.permission==='default')Notification.requestPermission().then(function(){var w=document.getElementById('hvemw');if(w)w.innerHTML=emHtml(st())})}catch(e){}};
 var lastN=0;
 setInterval(function(){var x=st();if(x.l<2||!window.Notification||Notification.permission!=='granted'||!SND.on)return;var g=sig(x);if(g<=SND.ack||g<=lastN)return;lastN=g;try{var n=new Notification('[위기대응 경보체계 가동] 단계 '+x.l+' · '+G[x.l-1],{body:'HIVEN 이상징후 및 보안체계 경보 — 눌러서 확인',tag:'hvalarm',requireInteraction:true,vibrate:[300,150,300],renotify:true});n.onclick=function(){try{window.focus();hvgo('SC-02')}catch(e){}}}catch(e){}},1500);
 function devSt(){var p=window.Notification?Notification.permission:'none';return '이 기기 설정: 소리 '+(SND.on?'켜짐':'꺼짐')+' · 기기 알림 '+(p==='granted'?'허용':p==='denied'?'차단(기기 설정에서 허용)':p==='none'?'지원 안 함':'미허용')+' · 진동 '+(navigator.vibrate?'지원':'미지원')}
 /* 모든 화면 오른쪽 아래 고정: 알람이 울리는 동안만 나타나는 「경보음 끄기」 버튼(기기별 적용, 대표님 15:23·15:24: 켜짐은 시스템 자동, 끄기만) */
 function sb(){var x=st(),al=x.l>=2&&sig(x)>SND.ack,b=document.getElementById('hvsndbtn');if(!al){if(b)b.style.display='none';return}
  if(!b){b=document.createElement('button');b.id='hvsndbtn';b.type='button';b.style.cssText='position:fixed;right:14px;bottom:14px;z-index:9998;border:0;border-radius:999px;padding:11px 18px;font-size:15px;font-weight:700;cursor:pointer;box-shadow:0 2px 12px rgba(0,0,0,.4);background:#fff;color:#c62828;outline:3px solid #c62828';b.onclick=function(ev){hvSirenAck(ev);sb()};document.body.appendChild(b)}
  b.style.display='';b.textContent='\u{1F515} 경보음 끄기';b.title='이 기기의 경보 소리·진동을 끕니다. 단계가 오르거나 새 경보가 생기면 다시 울립니다.'}
 window.hvSb=sb;setInterval(sb,1000);setTimeout(sb,300);
 function emHtml(x){var al=x.l>=2,hi=x.l>=6,c=hi?'#c62828':al?'#ef6c00':'#2e7d32',L=x.s.L||[],e=L[L.length-1];
  var ban=al?'<div id="hvalarm" role="alert" aria-live="assertive" class="'+(hi?'hvglow':'')+'" style="background:'+c+';color:#fff;border-radius:8px;padding:12px 16px;margin:0 0 10px;font-weight:700;font-size:18px;display:flex;align-items:center;gap:10px;cursor:pointer" onclick="hvgo(\'SC-02\')"><span class="hvblink" style="font-size:22px">&#9888;</span><span class="hvblink">[위기대응 경보체계 가동]</span><span style="font-weight:500;font-size:14px;opacity:.95">단계 '+x.l+' · '+G[x.l-1]+' — 침입 경보 기록 '+L.length+'건'+(e?' · 최근 '+e.t.slice(5,16).replace('T',' ')+' '+(e.a||e.g):'')+'</span><span style="margin-left:auto;display:flex;gap:6px;align-items:center;flex-wrap:wrap;font-size:13px;font-weight:600">'+(SND.on?(sig(x)<=SND.ack?'<span>경보음 확인됨</span>':SND.blocked?'<span class="hvblink">화면을 한 번 누르면 경보음이 켜집니다</span>':'<span>\u{1F514} 경보음 울림</span>'):'<span>경보음 꺼짐</span>')+(sig(x)>SND.ack?'<button type="button" onclick="hvSirenAck(event)" style="border:0;border-radius:6px;padding:4px 10px;font-weight:700;cursor:pointer">경보음 끄기</button>':'')+'<button type="button" onclick="hvSirenToggle(event)" style="border:0;border-radius:6px;padding:4px 10px;cursor:pointer">'+(SND.on?'소리 끄기':'소리 켜기')+'</button></span></div>':'';
  var box='<div id="hvem" class="'+(al?'hvblink':'')+'" style="border:2px solid '+c+';'+(al?'background:'+(hi?'#ffebee':'#fff3e0')+';':'')+'border-radius:8px;padding:10px 14px;margin:0 0 12px;cursor:pointer" onclick="hvgo(\'SC-02\')" title="누르면 비상대응 체계(SC-02)"><b style="color:'+c+'">이상징후 및 보안체계 단계 '+x.l+' · '+G[x.l-1]+'</b> <span style="opacity:.8">— 침입 경보(SC-03) 기록 '+L.length+'건 · 최근 경보 '+(e?e.t.slice(5,16).replace('T',' ')+' '+(e.a||e.g):'없음')+' · <b>시험 기간 완화 운영 중(8항목)</b> · 무결성 검사 <span id="hvint">'+(window.hvInt&&window.hvInt.ok!=null?(window.hvInt.ok?'일치':'불일치 '+window.hvInt.bad.length+'건'):'확인 중')+'</span> · 눌러서 HIVEN 통합사업 이상징후 및 보안체계 시스템(SC-02) 보기</span> <button type="button" onclick="event.stopPropagation();hvSirenTest()" style="margin-left:8px;border:1px solid #999;border-radius:6px;background:#fff;padding:2px 8px;cursor:pointer">경보음 시험(3초)</button> <button type="button" onclick="hvDevAsk(event)" style="border:1px solid #999;border-radius:6px;background:#fff;padding:2px 8px;cursor:pointer">기기 알림 허용</button><div style="font-size:12px;opacity:.8;margin-top:4px">'+devSt()+'</div></div>';
  return ban+box}
 window.hvEmHtml=function(){return emHtml(st())};
 var v1=V['SC-01'];if(v1&&!v1._em){V['SC-01']=function(){return '<div id="hvemw">'+emHtml(st())+'</div>'+v1.apply(this,arguments)};V['SC-01']._em=1}
 /* 단계가 바뀌면 SC-01을 다시 그리지 않고 맨 위 상자만 갱신 */
 var lastSig='';setInterval(function(){var w=document.getElementById('hvemw');if(!w)return;var x=st(),sig=x.l+'|'+(x.s.L||[]).length+'|'+SND.ack+'|'+SND.on+'|'+SND.blocked;if(sig!==lastSig){lastSig=sig;w.innerHTML=emHtml(x)}},2000);
 /* 무결성 검사 */
 var res={ok:null,bad:[]};window.hvInt=res;
 function hex(b){return Array.prototype.map.call(new Uint8Array(b),function(x){return ('0'+x.toString(16)).slice(-2)}).join('')}
 function run(){if(!window.crypto||!crypto.subtle)return;fetch('cowork/ctl/integrity.json?'+Date.now(),{cache:'no-store'}).then(function(r){return r.json()}).then(function(m){
  var ks=Object.keys(m.files);return Promise.all(ks.map(function(f){return fetch(f+'?'+Date.now(),{cache:'no-store'}).then(function(r){return r.arrayBuffer()}).then(function(b){return crypto.subtle.digest('SHA-256',b)}).then(function(h){if(hex(h)!==m.files[f])res.bad.push(f)}).catch(function(){res.bad.push(f+'(읽기 실패)')})}))}).then(function(){
  res.ok=!res.bad.length;var e=document.getElementById('hvint');if(e)e.textContent=res.ok?'일치':'불일치 '+res.bad.length+'건';
  if(!res.ok&&window.hvSec){hvSec.log(2,'무결성 불일치(변조 의심): '+res.bad.join(', '),0);var d=document.getElementById('hvsecbar');if(!d){d=document.createElement('div');d.id='hvsecbar';d.setAttribute('role','alert');d.style.cssText='position:fixed;top:0;left:0;right:0;z-index:99999;padding:10px 14px;color:#fff;font:700 14px/1.4 sans-serif;text-align:center;background:#ef6c00';document.body.appendChild(d)}d.textContent='⚠ 침입 경보 · 경보 단계 · 화면 파일 무결성 불일치: '+res.bad.join(', ')}}).catch(function(){})}
 setTimeout(run,2500);setInterval(run,600000);
})();
