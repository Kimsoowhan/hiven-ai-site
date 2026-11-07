/* T-W37-02 SC-07 베타 배포 모니터링(14:50 대표님 지시로 창 안에서 베타 1·2·3 구분, 베타 1이 현재 실측 원천)(대표님 규칙 20·21·29·54): 게이트 O-01~O-11 + 배포 후 장애·문의·확인 사건 3분류(미조치·조치 중·조치 완료) + 변동 추이 그래프(공통 부품 hvTGin). 원천 cowork/ctl/deploy_beta1_gates.tsv · deploy_beta1_events.tsv — 실측만, 배포 전에는 사건 0건 그대로 표출 */
V['SC-07b1']=function(){var el='hv14';setTimeout(function(){Promise.all([hvFetch(hv5Base()+'deploy_beta1_gates.tsv','text'),hvFetch(hv5Base()+'deploy_beta1_events.tsv','text')]).then(function(a){var G=hv5Tsv(a[0]),E=hv5Tsv(a[1]),n=document.getElementById(el);if(!n)return;
 var pass=G.r.filter(function(r){return /^통과/.test(r[2])}).length,ready=G.r.filter(function(r){return r[2]==='준비 완료'}).length,fail=G.r.length-pass-ready;
 var c3=function(k){return E.r.filter(function(r){return r[5]===k}).length};
 var gd=function(f){return function(){return tbl(['게이트','항목','결과','근거'],G.r.filter(f).map(function(r){return r.slice(0,4).map(hvEsc)}))}},ed=function(k){return function(){var x=E.r.filter(function(r){return r[5]===k});return x.length?tbl(['#','날짜','시각','구분','내용','조치'],x.map(function(r){return [r[0],r[1],r[2],r[3],r[4],r[6]].map(hvEsc)})):'<p class="note">원천 cowork/ctl/deploy_beta1_events.tsv — '+k+' 0건</p>'}};
 var g='<div class="grid">'+card('게이트 통과',pass+'/'+G.r.length,'준비 완료 '+ready+' · 미통과 '+fail,null,gd(function(r){return /^통과/.test(r[2])}))+card('배포 상태',E.r.length?'배포 후':'배포 전','배포 가능 승인 1회 뒤 게시',null,gd(function(r){return r[2]==='준비 완료'}))+card('미조치',c3('미조치')+'건','배포 후 사건',null,ed('미조치'))+card('조치 중',c3('조치 중')+'건','배포 후 사건',null,ed('조치 중'))+card('조치 완료',c3('조치 완료')+'건','배포 후 사건',null,ed('조치 완료'))+'</div>';
 var ST=['감지','경고·알람','조치 착수','조치 중','해제','보고서 이관','통제 확인'],sc={'미조치':2,'조치 중':4,'조치 완료':7};
 g+='<h3>백오피스 흐름(감지 → 통제 확인)</h3>'+tbl(ST,[ST.map(function(x,i){return E.r.filter(function(r){return (sc[r[5]]||1)>i}).length+'건'})]);
 g+='<h3>게이트 O-01~O-11</h3>'+tbl(['게이트','항목','결과','근거','실측 시각'],G.r.map(function(r){return r.map(hvEsc)}));
 g+=hvTGin('sc14',{title:'배포 후 장애·조치 변동 추이',types:['미조치','조치 중','조치 완료'],colors:(typeof hvTGC01!=='undefined'?hvTGC01:null),tu:'일',ev:E.r.map(function(r){var hm=(r[2]||'').slice(0,5);return {t:Date.parse(r[1]+'T'+(hm||'12:00')+':00+09:00'),hm:hm,y:r[5],m:r[3]}}).filter(function(e){return !isNaN(e.t)}),src:'원천 cowork/ctl/deploy_beta1_events.tsv(사건 시각)'});
 g+='<h3>배포 후 사건</h3>'+(E.r.length?tbl(['#','날짜','시각','구분','내용','3분류','조치','근거'],E.r.slice().reverse().map(function(r){return r.map(hvEsc)})):'<p class="note">사건 0건 — 배포 전. 게시 뒤 O-10 확인 3항목과 접수 건이 이 표에 쌓입니다.</p>');
 n.innerHTML=g+'<p class="note">원천: cowork/ctl/deploy_beta1_gates.tsv · deploy_beta1_events.tsv(실측만)</p>'})},0);
 return '<p class="lead">HiCoffer PC 베타 1의 게이트와 배포 후 장애·문의·조치를 봅니다.</p><div id="'+el+'">읽는 중…</div>'};

/* 14:50 대표님 지시: 메뉴 이름은 「베타 배포 모니터링」, 창 안에서 베타 1·2·3으로 구분한다. 베타 1만 실측 원천(deploy_beta1_*.tsv)이 있고, 베타 2·3은 시작 전이라 실측 0건으로 표시한다. */
var hvBetaSel=1;
window.hvBetaPick=function(n){hvBetaSel=n;var m=document.getElementById('hvbeta');if(m)m.innerHTML=hvBetaBody()};
function hvBetaBody(){var n=hvBetaSel;if(n===1)return V['SC-07b1']();
 var P={2:['2026-12','HiCoffer PC 베타 2','베타 1 안정화 결과를 반영한 두 번째 무료 베타'],3:['2027-01','HiCoffer PC 베타 3','상용화 직전 마지막 무료 베타']}[n];
 return '<p class="lead">'+P[1]+' — 예정 '+P[0]+' ('+P[2]+')</p><div class="grid">'+card('게이트 통과','0/0','베타 '+n+' 게이트 표는 시작 전',null)+card('배포 상태','배포 전','베타 1 상용화 전 단계를 건너뛰지 않음',null)+'</div><p class="note">베타 '+n+'은 아직 시작 전이라 실측 원천(deploy_beta'+n+'_gates.tsv · deploy_beta'+n+'_events.tsv)이 없습니다. 시작 시 베타 1과 같은 구성(게이트 O-01~O-11 · 배포 후 사건 3분류 · 변동 추이)으로 이 창에 쌓입니다. 시험·거짓 값은 넣지 않습니다.</p>'}
V['SC-07']=function(){return '<h2>SC-07 베타 배포 모니터링</h2><div class="sc12-f" style="display:flex;gap:6px;margin:6px 0 10px">'+[1,2,3].map(function(n){return '<button type="button" class="'+(hvBetaSel===n?'on':'')+'" style="padding:6px 16px;border:1px solid var(--line,#c8d0e0);border-radius:8px;background:'+(hvBetaSel===n?'#16234d':'#fff')+';color:'+(hvBetaSel===n?'#fff':'#16234d')+';font-weight:700" onclick="hvBetaPick('+n+')">베타 '+n+'</button>'}).join('')+'</div><div id="hvbeta">'+hvBetaBody()+'</div>'};
