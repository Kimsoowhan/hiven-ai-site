/* 침입 경보 체계(대표님 지시 11/07 13:01): 열쇠 오류 1회 이상을 모두 등급화해 즉시 경보·기록·전송한다.
   등급: 관찰(1회) < 관심(2회) < 심각(3회) < 위험(4~5회) < 위기(6회 이상 · 우회/변조 감지). 3회부터 잠금(30초·5분·30분).
   전송: ic.hiven.ai.kr/__sec 로 즉시 전송(Cloudflare 작업자 실시간 로그). 이 화면의 기록은 이 단말에 남는 사본이다. */
var hvSec=(function(){
 var G=['관찰','관심','심각','위험','위기'],C=['#1565c0','#00838f','#ef6c00','#c62828','#6a1b9a'],LK=[0,0,30,300,1800],rj=0,lastBad='';
 function lk(n){return n>=6?1800*Math.min(8,n-5):n>=4?300:n>=3?30:n>=2?15:n>=1?5:0}
 function hs(v){var h=0,i;v=String(v||'');for(i=0;i<v.length;i++)h=(h*31+v.charCodeAt(i))|0;return h+':'+v.length}
 function ld(){try{return JSON.parse(localStorage.getItem('hvsec')||'{"n":0,"t":0,"u":0,"L":[]}')}catch(e){return {n:0,t:0,u:0,L:[]}}}
 function sv(s){try{localStorage.setItem('hvsec',JSON.stringify(s))}catch(e){}}
 var A12=['관심','주의','경계','위험','위기'];function al(g,why){return g==2&&/복제|삽입|프레임|변조|우회/.test(why||'')?'경고':A12[g]}
 function gr(n){return n>=6?4:n>=4?3:n>=3?2:n>=2?1:0}
 function send(ev){try{var b=JSON.stringify(ev);if(navigator.sendBeacon)navigator.sendBeacon('https://ic.hiven.ai.kr/__sec',b);else fetch('https://ic.hiven.ai.kr/__sec',{method:'POST',mode:'no-cors',body:b,keepalive:true})}catch(e){}}
 function bar(g,msg){var d=document.getElementById('hvsecbar');if(!d){d=document.createElement('div');d.id='hvsecbar';d.setAttribute('role','alert');d.style.cssText='position:fixed;top:0;left:0;right:0;z-index:99999;padding:10px 14px;color:#fff;font:700 14px/1.4 sans-serif;text-align:center';document.body.appendChild(d)}
  d.style.background=C[g];d.textContent='⚠ 침입 경보 · '+G[g]+' 단계 · '+msg}
 function log(g,why,n){var s=ld(),e={t:new Date().toISOString(),g:G[g],a:al(g,why),r:0,n:n,why:why,host:location.host,ua:(navigator.userAgent||'').slice(0,90)};s.L.push(e);if(s.L.length>200)s.L=s.L.slice(-200);sv(s);send(e);return e}
 function lock(){var s=ld(),r=Math.ceil((s.u-Date.now())/1000);return r>0?r:0}
 function fail(why,extra){var s=ld();if(Date.now()-s.t>86400000)s.n=0;s.n+=1+(extra||0);s.t=Date.now();var g=gr(s.n);s.u=Date.now()+lk(s.n)*1000;sv(s);log(g,why||'열쇠 불일치',s.n);bar(g,'보호 단계 전환 · 열쇠 불일치 '+s.n+'회'+(lock()?' · '+lock()+'초 입력 정지':''));guard();return g}
 function guard(){var i=document.getElementById('k'),e=document.getElementById('err'),r=lock();if(!i)return;if(r>0){i.disabled=true;if(e)e.textContent='보호 단계 · 입력 정지 '+r+'초 남음'}else if(i.disabled){i.disabled=false;rj=0;if(e&&/보호 단계/.test(e.textContent))e.textContent='보호 단계 유지 중 · 열쇠를 다시 입력하세요.'}}
 setInterval(guard,1000);
 var k0=window.keyOk;
 window.keyOk=function(v){var r=lock();if(r){var g=gr(ld().n);rj++;log(g,'입력 정지 중 재시도 거부 '+rj+'회',ld().n);bar(g,'보호 단계 · 입력 정지 중 재시도 거부 · '+r+'초 뒤 다시 시도');if(rj%3===0)fail('입력 정지 중 재시도 반복(중복 실패)');setTimeout(function(){var e=document.getElementById('err');if(e)e.textContent='보호 단계 · 입력 정지 중입니다. '+lock()+'초 뒤 다시 시도하세요.'},0);return false}
  var ok=k0(v);if(ok){try{sessionStorage.setItem('hvsec_ok',String(Date.now()))}catch(e){}rj=0;lastBad='';var s=ld();if(s.n){log(0,'정상 입장(오류 '+s.n+'회 뒤 보호 단계 해제)',0);s.n=0;s.u=0;sv(s)}var b=document.getElementById('hvsecbar');if(b)b.remove()}
  else{var h=hs(v),dup=(lastBad===h);lastBad=h;var g2=fail(dup?'열쇠 불일치 · 같은 열쇠 반복(중복 실패)':'열쇠 불일치',dup?1:0);setTimeout(function(){var e=document.getElementById('err');if(e)e.textContent='열쇠가 맞지 않습니다. 보호 단계로 전환되었습니다 · 경보 '+G[g2]+(lock()?' · '+lock()+'초 입력 정지':'')},0)}return ok};
 try{var s9=ld();if(s9.n&&Date.now()-s9.t<86400000)window.addEventListener('DOMContentLoaded',function(){bar(gr(s9.n),'보호 단계 유지 중 · 열쇠 불일치 '+s9.n+'회 기록');guard()})}catch(e){}
 /* 우회 감지: 열쇠 확인 없이 입장 표식만 있는 경우 */
 try{if(sessionStorage.getItem('hv_in')==='1'&&!sessionStorage.getItem('hvsec_ok')){sessionStorage.removeItem('hv_in');var s0=ld();s0.n=Math.max(s0.n,6);s0.t=Date.now();sv(s0);log(4,'우회 의심: 열쇠 확인 없는 입장 표식',s0.n);window.addEventListener('DOMContentLoaded',function(){bar(4,'우회 입장 시도 감지 · 입장 표식 폐기')})}}catch(e){}
 window.addEventListener('storage',function(e){if(e.key==='hvsec'||e.key==='hv_in')log(4,'저장소 변조 의심: '+e.key,ld().n)});
 if(!window.hvSecNav){window.hvSecNav=1;S.push(['SC-03','침입 예측·예방·대응·조치 시스템'])}
 V['SC-03']=function(){var s=ld(),g=gr(s.n),L=s.L.slice().reverse().slice(0,15);
  var tb='<table class="tb"><thead><tr><th>시각</th><th>등급</th><th>오류수</th><th>발령</th><th>내용</th></tr></thead><tbody>'+(L.length?L.map(function(e){return '<tr><td>'+e.t.slice(5,16).replace('T',' ')+'</td><td><b style="color:'+C[G.indexOf(e.g)]+'">'+e.g+'</b></td><td>'+e.n+'</td><td>'+(e.a||al(G.indexOf(e.g),e.why))+'</td><td>'+e.why+'</td></tr>'}).join(''):'<tr><td colspan="5">이 단말에 기록된 경보가 없습니다.</td></tr>')+'</tbody></table>';
  var df=[['관찰','열쇠 불일치 1회','즉시 보호 단계 전환 · 5초 입력 정지 · 경보 띠 · 기록 · 전송'],['관심','불일치 2회','15초 입력 정지 · 경보 · 기록 · 전송'],['심각','불일치 3회','30초 입력 정지 · 경보 · 전송'],['위험','불일치 4~5회','5분 입력 정지 · 경보 · 전송'],['위기','불일치 6회 이상 · 우회/변조 감지','30분(누적 배수, 최대 4시간) 입력 정지 · 입장 표식 폐기 · 전송']].map(function(r,i){return '<tr><td><b style="color:'+C[i]+'">'+r[0]+'</b></td><td>'+r[1]+'</td><td>'+r[2]+'</td></tr>'}).join('');
  return '<h2>SC-03 침입 예측/예방/대응/조치 시스템 (침입 경보)</h2><p class="note">HIVEN 통합사업 이상징후 및 보안체계 시스템(SC-02)의 하위 실행 시스템입니다.</p><p class="lead">열쇠 오류 1회 이상을 모두 등급으로 기록하고 즉시 경보합니다. 현재 이 단말: <b style="color:'+C[g]+'">'+(s.n?G[g]+' 단계 · 연속 오류 '+s.n+'회':'정상')+'</b>'+(lock()?' · 잠금 '+lock()+'초':'')+'</p>'
   +'<h3>제1순위 접근·침입 경로 (절대 원칙)</h3><p class="note">ic.hiven.ai.kr 인트로의 열쇠(key) 입력이 첫 경로입니다. 반복 입력 · 불일치 · 거부 · 중복 실패가 나오면 시스템을 즉시 보호 단계로 전환합니다. 입력 정지 중 재시도는 「거부」로 기록하고 3회 반복하면 실패 1회로 더하며, 같은 열쇠를 반복하면 「중복 실패」로 기록해 1회를 더합니다. 이 작은 대응 하나가 뚫리면 자동화 통합 통제 시스템 전체가 뚫립니다(대표님 11/07 14:03).</p>'
   +'<p class="note"><b>시험 기간 완화 운영 중</b> — 입력 정지 시간과 열쇠 표기 허용이 운영 기준값보다 낮게 설정되어 있습니다(대표님이 언제 어디서든 폰으로 확인하기 위함). 감지·기록·전송·12단계 판정은 완화하지 않습니다. 등록부·해제 기준·역정합 검사는 SC-02 「시험 기간 완화 운영 표준」을 보십시오.</p>'
   +'<h3>등급 기준과 즉시 대응</h3><table class="tb"><thead><tr><th>등급</th><th>조건</th><th>즉시 대응</th></tr></thead><tbody>'+df+'</tbody></table>'
   +'<h3>최근 경보(이 단말, 최신순)</h3>'+tb
   +'<h3>벤치마킹 근거(11/07 조사)</h3><table class="tb"><thead><tr><th>사례</th><th>핵심</th><th>우리 반영</th></tr></thead><tbody>'
   +'<tr><td>국가 사이버위기경보(국정원·KISA, 5단계)</td><td>정상·관심·주의·경계·심각의 단계별 경보와 대응</td><td>관찰~위기 5등급, 등급별 즉시 대응 표</td></tr>'
   +'<tr><td>NIST SP 800-53 AC-7</td><td>연속 로그인 실패 횟수 제한과 초과 시 잠금</td><td>3회부터 잠금, 단계마다 길어짐</td></tr>'
   +'<tr><td>OWASP 인증 실패 대응</td><td>실패를 모두 기록하고 점진적으로 지연·차단</td><td>1회부터 기록·경보, 누적 배수 잠금</td></tr>'
   +'<tr><td>NIST SP 800-61 사고 대응 주기</td><td>탐지→분석→격리→복구→사후 기록</td><td>감지·경보·잠금·해제 기록·이력 보존</td></tr>'
   +'</tbody></table>'
   +'<p class="note">전송 경로: ic.hiven.ai.kr 작업자 실시간 로그(모든 단말의 경보가 모임). 열쇠 확인은 화면 안내 수준이므로 접속 자체의 차단은 Cloudflare 접근 통제와 함께 쓴다.</p>'}
 return {al:al,fail:fail,log:log,grade:gr,lk:lk}
})();
