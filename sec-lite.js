/* 하이븐 웹사이트 공통 침입 감시(대표님 지시 11/07 13:01·13:12): 접속 이상 징후를 등급으로 즉시 ic.hiven.ai.kr 통합관제에 전송한다.
   관찰=존재하지 않는 경로 접근(탐색 시도) · 경고=다른 주소에서 이 사이트가 복제 표시됨(피싱 복제) · 경보=다른 사이트 틀(iframe) 안에 삽입됨(클릭 가로채기). */
(function(){try{
 var OK=/(^|\.)(hiven\.co\.kr|hiven\.ai\.kr|hiven\.ai|localhost)$/,ev=[];
 if(!OK.test(location.hostname))ev.push(['경고','복제 의심: 허용 주소가 아닌 '+location.hostname+'에서 표시']);
 try{if(window.top!==window.self)ev.push(['경보','삽입 의심: 다른 사이트 틀 안에서 표시'])}catch(e){ev.push(['경보','삽입 의심: 상위 틀 접근 차단'])}
 if(/404|찾을 수 없|not found/i.test(document.title)||document.documentElement.getAttribute('data-hv404')!==null)ev.push(['관찰','없는 경로 접근: '+location.pathname]);
 ev.forEach(function(x){var b=JSON.stringify({t:new Date().toISOString(),g:x[0],n:0,why:x[1],host:location.host,ua:(navigator.userAgent||'').slice(0,90)});if(navigator.sendBeacon)navigator.sendBeacon('https://ic.hiven.ai.kr/__sec',b)});
 if(ev.some(function(x){return x[0]==='경보'}))document.documentElement.style.display='none';
}catch(e){}})();
