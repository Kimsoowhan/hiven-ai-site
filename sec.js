/* 침입 경보 체계(대표님 지시 11/07 13:01): 열쇠 오류 1회 이상을 모두 등급화해 즉시 경보·기록·전송한다.
   등급: 관찰(1회) < 관심(2회) < 심각(3회) < 위험(4~5회) < 위기(6회 이상 · 우회/변조 감지). 3회부터 잠금(30초·5분·30분).
   전송: ic.hiven.ai.kr/__sec 로 즉시 전송(Cloudflare 작업자 실시간 로그). 이 화면의 기록은 이 단말에 남는 사본이다. */
var hvSec=(function(){
 var G=['관찰','관심','심각','위험','위기'],C=['#1565c0','#00838f','#ef6c00','#c62828','#6a1b9a'],LK=[0,0,30,300,1800];
 function ld(){try{return JSON.parse(localStorage.getItem('hvsec')||'{"n":0,"t":0,"u":0,"L":[]}')}catch(e){return {n:0,t:0,u:0,L:[]}}}
 function sv(s){try{localStorage.setItem('hvsec',JSON.stringify(s))}catch(e){}}
 function gr(n){return n>=6?4:n>=4?3:n>=3?2:n>=2?1:0}
 function send(ev){try{var b=JSON.stringify(ev);if(navigator.sendBeacon)navigator.sendBeacon('https://ic.hiven.ai.kr/__sec',b);else fetch('https://ic.hiven.ai.kr/__sec',{method:'POST',mode:'no-cors',body:b,keepalive:true})}catch(e){}}
 function bar(g,msg){var d=document.getElementById('hvsecbar');if(!d){d=document.createElement('div');d.id='hvsecbar';d.setAttribute('role','alert');d.style.cssText='position:fixed;top:0;left:0;right:0;z-index:99999;padding:10px 14px;color:#fff;font:700 14px/1.4 sans-serif;text-align:center';document.body.appendChild(d)}
  d.style.background=C[g];d.textContent='⚠ 침입 경보 · '+G[g]+' 단계 · '+msg}
 function log(g,why,n){var s=ld(),e={t:new Date().toISOString(),g:G[g],n:n,why:why,host:location.host,ua:(navigator.userAgent||'').slice(0,90)};s.L.push(e);if(s.L.length>200)s.L=s.L.slice(-200);sv(s);send(e);return e}
 function lock(){var s=ld(),r=Math.ceil((s.u-Date.now())/1000);return r>0?r:0}
 function fail(why){var s=ld();if(Date.now()-s.t>86400000)s.n=0;s.n++;s.t=Date.now();var g=gr(s.n);if(LK[g])s.u=Date.now()+LK[g]*1000*(s.n>=6?Math.min(8,s.n-5):1);sv(s);log(g,why||'열쇠 오류',s.n);bar(g,'열쇠 오류 '+s.n+'회'+(lock()?' · '+lock()+'초 잠금':''));return g}
 var k0=window.keyOk;
 window.keyOk=function(v){var r=lock();if(r){var g=gr(ld().n);bar(g,'잠금 중 · '+r+'초 뒤 다시 시도');setTimeout(function(){var e=document.getElementById('err');if(e)e.textContent='잠금 중입니다. '+r+'초 뒤 다시 시도하세요.'},0);return false}
  var ok=k0(v);if(ok){try{sessionStorage.setItem('hvsec_ok',String(Date.now()))}catch(e){}var s=ld();if(s.n){log(0,'정상 입장(오류 '+s.n+'회 뒤 해제)',0);s.n=0;s.u=0;sv(s)}var b=document.getElementById('hvsecbar');if(b)b.remove()}
  else{var g2=fail('열쇠 오류');setTimeout(function(){var e=document.getElementById('err');if(e)e.textContent='열쇠가 맞지 않습니다. 경보 '+G[g2]+' 단계로 기록되었습니다.'+(lock()?' '+lock()+'초 잠금.':'')},0)}return ok};
 /* 우회 감지: 열쇠 확인 없이 입장 표식만 있는 경우 */
 try{if(sessionStorage.getItem('hv_in')==='1'&&!sessionStorage.getItem('hvsec_ok')){sessionStorage.removeItem('hv_in');var s0=ld();s0.n=Math.max(s0.n,6);s0.t=Date.now();sv(s0);log(4,'우회 의심: 열쇠 확인 없는 입장 표식',s0.n);window.addEventListener('DOMContentLoaded',function(){bar(4,'우회 입장 시도 감지 · 입장 표식 폐기')})}}catch(e){}
 window.addEventListener('storage',function(e){if(e.key==='hvsec'||e.key==='hv_in')log(4,'저장소 변조 의심: '+e.key,ld().n)});
 if(!window.hvSecNav){window.hvSecNav=1;S.push(['SC-15','침입 예측·예방·대응·조치 시스템'])}
 V['SC-15']=function(){var s=ld(),g=gr(s.n),L=s.L.slice().reverse().slice(0,15);
  var tb='<table class="tb"><thead><tr><th>시각</th><th>등급</th><th>오류수</th><th>내용</th></tr></thead><tbody>'+(L.length?L.map(function(e){return '<tr><td>'+e.t.slice(5,16).replace('T',' ')+'</td><td><b style="color:'+C[G.indexOf(e.g)]+'">'+e.g+'</b></td><td>'+e.n+'</td><td>'+e.why+'</td></tr>'}).join(''):'<tr><td colspan="4">이 단말에 기록된 경보가 없습니다.</td></tr>')+'</tbody></table>';
  var df=[['관찰','열쇠 오류 1회','즉시 경보 띠 · 기록 · 전송'],['관심','오류 2회','경보 띠 · 기록 · 전송'],['심각','오류 3회','30초 잠금 · 경보 · 전송'],['위험','오류 4~5회','5분 잠금 · 경보 · 전송'],['위기','오류 6회 이상 · 우회/변조 감지','30분(누적 배수, 최대 4시간) 잠금 · 입장 표식 폐기 · 전송']].map(function(r,i){return '<tr><td><b style="color:'+C[i]+'">'+r[0]+'</b></td><td>'+r[1]+'</td><td>'+r[2]+'</td></tr>'}).join('');
  return '<h2>SC-15 침입 예측/예방/대응/조치 시스템 (침입 경보)</h2><p class="note">HIVEN 통합사업 이상징후 및 보안체계 시스템(SC-16)의 하위 실행 시스템입니다.</p><p class="lead">열쇠 오류 1회 이상을 모두 등급으로 기록하고 즉시 경보합니다. 현재 이 단말: <b style="color:'+C[g]+'">'+(s.n?G[g]+' 단계 · 연속 오류 '+s.n+'회':'정상')+'</b>'+(lock()?' · 잠금 '+lock()+'초':'')+'</p>'
   +'<h3>등급 기준과 즉시 대응</h3><table class="tb"><thead><tr><th>등급</th><th>조건</th><th>즉시 대응</th></tr></thead><tbody>'+df+'</tbody></table>'
   +'<h3>최근 경보(이 단말, 최신순)</h3>'+tb
   +'<h3>벤치마킹 근거(11/07 조사)</h3><table class="tb"><thead><tr><th>사례</th><th>핵심</th><th>우리 반영</th></tr></thead><tbody>'
   +'<tr><td>국가 사이버위기경보(국정원·KISA, 5단계)</td><td>정상·관심·주의·경계·심각의 단계별 경보와 대응</td><td>관찰~위기 5등급, 등급별 즉시 대응 표</td></tr>'
   +'<tr><td>NIST SP 800-53 AC-7</td><td>연속 로그인 실패 횟수 제한과 초과 시 잠금</td><td>3회부터 잠금, 단계마다 길어짐</td></tr>'
   +'<tr><td>OWASP 인증 실패 대응</td><td>실패를 모두 기록하고 점진적으로 지연·차단</td><td>1회부터 기록·경보, 누적 배수 잠금</td></tr>'
   +'<tr><td>NIST SP 800-61 사고 대응 주기</td><td>탐지→분석→격리→복구→사후 기록</td><td>감지·경보·잠금·해제 기록·이력 보존</td></tr>'
   +'</tbody></table>'
   +'<p class="note">전송 경로: ic.hiven.ai.kr 작업자 실시간 로그(모든 단말의 경보가 모임). 열쇠 확인은 화면 안내 수준이므로 접속 자체의 차단은 Cloudflare 접근 통제와 함께 쓴다.</p>'}
 return {fail:fail,log:log,grade:gr}
})();
