/* 비상대응 체계를 자동화 통합 통제 시스템 안으로 산입(대표님 11/07 13:33): ① 머리띠 대응 모드에 현재 단계 표시 ② SC-01 종합 현황 맨 위에 비상대응 단계 상자 ③ 화면 핵심 파일 무결성 검사(변조 의심=심각 경보). */
(function(){
 var G=['정상','관찰','관찰','관심','관심','심각','심각','위험','위험','위기'];
 function st(){var s;try{s=JSON.parse(localStorage.getItem('hvsec')||'{}')}catch(e){s={}}var n=s.n||0,l=n>=6?10:n>=4?8:n>=3?6:n>=2?4:n>=1?2:1;if(s.u&&s.u>Date.now())l=Math.max(l,6);return {n:n,l:l,s:s}}
 window.hvEmLevel=function(){return st().l};
 function chip(){var c=document.getElementById('chip-mode');if(!c)return;var x=st();c.innerHTML='<span class="dot '+(x.l>=6?'bad':x.l>=2?'warn':'ok')+'"></span>대응 모드 <b>단계 '+x.l+' '+G[x.l-1]+'</b> · 발령 <b>'+['안심','관심','관심','주의','주의','경계','경고','위험','위기','위기'][x.l-1]+'</b>'+(x.n>=1?' · <b>보호 단계 전환</b>':'')}
 setInterval(chip,3000);chip();
 var v1=V['SC-01'];if(v1&&!v1._em){V['SC-01']=function(){var x=st(),c=x.l>=6?'#c62828':x.l>=2?'#ef6c00':'#2e7d32';
  return '<div id="hvem" style="border:2px solid '+c+';border-radius:8px;padding:10px 14px;margin:0 0 12px;cursor:pointer" onclick="hvgo(\'SC-16\')" title="누르면 비상대응 체계(SC-16)"><b style="color:'+c+'">이상징후 및 보안체계 단계 '+x.l+' · '+G[x.l-1]+'</b> <span style="opacity:.8">— 침입 경보(SC-15) 기록 '+((x.s.L||[]).length)+'건 · 최근 경보 '+(function(){var L=x.s.L||[],e=L[L.length-1];return e?e.t.slice(5,16).replace('T',' ')+' '+(e.a||e.g):'없음'})()+' · <b>시험 기간 완화 운영 중(8항목)</b> · 무결성 검사 <span id="hvint">확인 중</span> · 눌러서 HIVEN 통합사업 이상징후 및 보안체계 시스템(SC-16) 보기</span></div>'+v1.apply(this,arguments)};V['SC-01']._em=1}
 /* 무결성 검사 */
 var res={ok:null,bad:[]};window.hvInt=res;
 function hex(b){return Array.prototype.map.call(new Uint8Array(b),function(x){return ('0'+x.toString(16)).slice(-2)}).join('')}
 function run(){if(!window.crypto||!crypto.subtle)return;fetch('cowork/ctl/integrity.json?'+Date.now(),{cache:'no-store'}).then(function(r){return r.json()}).then(function(m){
  var ks=Object.keys(m.files);return Promise.all(ks.map(function(f){return fetch(f+'?'+Date.now(),{cache:'no-store'}).then(function(r){return r.arrayBuffer()}).then(function(b){return crypto.subtle.digest('SHA-256',b)}).then(function(h){if(hex(h)!==m.files[f])res.bad.push(f)}).catch(function(){res.bad.push(f+'(읽기 실패)')})}))}).then(function(){
  res.ok=!res.bad.length;var e=document.getElementById('hvint');if(e)e.textContent=res.ok?'일치':'불일치 '+res.bad.length+'건';
  if(!res.ok&&window.hvSec){hvSec.log(2,'무결성 불일치(변조 의심): '+res.bad.join(', '),0);var d=document.getElementById('hvsecbar');if(!d){d=document.createElement('div');d.id='hvsecbar';d.setAttribute('role','alert');d.style.cssText='position:fixed;top:0;left:0;right:0;z-index:99999;padding:10px 14px;color:#fff;font:700 14px/1.4 sans-serif;text-align:center;background:#ef6c00';document.body.appendChild(d)}d.textContent='⚠ 침입 경보 · 심각 단계 · 화면 파일 무결성 불일치: '+res.bad.join(', ')}}).catch(function(){})}
 setTimeout(run,2500);setInterval(run,600000);
})();
