/* SC-16 말 명령 — 각서·각인·지표·지수·이행 점검 (대표님 11-12 12:53·12:55 지시, 이력 800·801).
   SC-15 모델 통제 화면과 별도. 원천: cowork/ctl/model_control_history.tsv + pledge_*.tsv (1초마다 다시 읽음). 읽기 전용. */
(function(){
var P={t:0,tab:'cmd',q:'',H:null,M:null,C:null,T:null,G:null,F:null,SS:null,SF:null,sig:''};
var COL={'위반':'#c62828','지시거부':'#7b1fa2','질타':'#ef6c00','지적':'#f9a825','지적(자가 발견)':'#9e9d24','개선요청':'#1565c0','장애':'#37474f','유휴':'#9e9e9e'};
var MC={'Sonnet':'#1565c0','Opus':'#6a1b9a','Fable':'#00897b','Haiku':'#757575'};
var KINDS=[['검수 누락',/검수|확인하지|전수|검증|눈으로|대조/],['규칙·지시문을 읽지 않음',/읽지|규칙|지시문|정책/],['폴더·파일 자리 오류',/폴더|옛 자리|root|경로/],['사용량·반복 낭비',/사용량|낭비|허비|반복|중간중간|매번|건별/],['자료를 찾지 않고 없다고 함·전가',/없다|없습니다|찾지|떠넘|전가|되돌림|되묻/],['턴을 끊고 멈춤',/턴|멈|스탠바이|기다|대기/],['지시 지연·말만 하고 미실행',/지연|예고|보고만|실행하지|미이행|미착수/],['지시 범위 밖 변경',/범위 밖|임의|멋대로|바꿈|변경/],['근거 없는 값',/근거|거짓|기사|임의/]];
function E(s){return typeof hvEsc==='function'?hvEsc(s):String(s==null?'':s)}
function ld(u){return hvFetch(u,'text').then(function(t){return hvTsv(t)},function(){return null})}
function load(){Promise.all([ld('cowork/ctl/model_control_history.tsv'),ld('cowork/ctl/pledge_models.tsv'),ld('cowork/ctl/pledge_checks.tsv'),ld('cowork/ctl/pledge_trace.tsv'),ld('cowork/ctl/pledge_changes.tsv'),ld('cowork/ctl/pledge_config.tsv'),ld('cowork/ctl/speech_standard.tsv'),ld('cowork/ctl/speech_flow.tsv'),ld('cowork/ctl/command_ledger.tsv')]).then(function(r){
 var sg=r.map(function(x){return x?x.length+':'+(x[x.length-1]||[]).join('|').length:'-'}).join(',');
 P.H=r[0];P.M=r[1];P.C=r[2];P.T=r[3];P.G=r[4];P.F=r[5];P.SS=r[6];P.SF=r[7];P.L=r[8];P.t=Date.now();window.hvCmdLive={H:P.H,L:P.L};
 if(sg!==P.sig){P.sig=sg;fill();var ct=document.getElementById('cmd-top');if(ct&&typeof hvSc04Tbl==='function'&&hvMeta.tv)ct.innerHTML=hvSc04Tbl()}else{var s=document.getElementById('plg-time');if(s)s.textContent=kst()}})}
function kst(){var d=new Date(Date.now()+9*3600000);return d.toISOString().replace('T',' ').slice(0,19)+' (KST)'}
function fam(m){var s=String(m||'');if(/Sonnet/.test(s))return 'Sonnet';if(/Opus/.test(s))return 'Opus';if(/Fable/.test(s))return 'Fable';if(/Haiku/.test(s))return 'Haiku';return '기타'}
function models(m){var s=String(m||''),o=[];['Sonnet','Opus','Fable','Haiku'].forEach(function(k){if(s.indexOf(k)>=0)o.push(k)});return o.length?o:['기타']}
function faults(){return (P.H||[]).filter(function(r){return r[5]&&r[5]!=='지시'&&r[1]})}
function bar(p,c){return '<span class="sc13-hb"><i style="width:'+Math.min(100,Math.max(0,p))+'%;background:'+c+'"></i></span>'}
function cards(a){return '<div class="row">'+a.map(function(c){return '<div class="card"><div class="k">'+E(c[0])+'</div><div class="v">'+c[1]+'</div><div class="s">'+c[2]+'</div></div>'}).join('')+'</div>'}
function stat(s){var c={'이행':'ok','이행 중':'warn','미이행':'bad','확인 안 됨':'gray','처리됨':'ok','수행 중':'warn','서명됨':'ok','작성 대기':'warn','해당 없음':'gray'}[s]||'gray';return tag(E(s),c)}
/* 그래프 1: 모델×구분 누적 막대 */
function g1(F){var ms=['Sonnet','Opus','Fable','Haiku'],ks=Object.keys(COL),cnt={};ms.forEach(function(m){cnt[m]={}});
 F.forEach(function(r){models(r[4]).forEach(function(m){if(cnt[m])cnt[m][r[5]]=(cnt[m][r[5]]||0)+1})});
 var mx=1;ms.forEach(function(m){var t=0;ks.forEach(function(k){t+=cnt[m][k]||0});if(t>mx)mx=t});
 var s='<svg viewBox="0 0 640 '+(ms.length*34+34)+'" style="width:100%;max-width:680px" role="img" aria-label="모델별 시행착오 구분 누적 막대">';
 ms.forEach(function(m,i){var x=70,y=10+i*34,t=0;s+='<text x="0" y="'+(y+15)+'" font-size="12" fill="currentColor">'+m+'</text>';
  ks.forEach(function(k){var v=cnt[m][k]||0;if(!v)return;var w=v/mx*500;s+='<rect x="'+x+'" y="'+y+'" width="'+w+'" height="22" fill="'+COL[k]+'"><title>'+m+' '+k+' '+v+'건</title></rect>';x+=w;t+=v});
  s+='<text x="'+(x+6)+'" y="'+(y+15)+'" font-size="12" fill="currentColor">'+t+'</text>'});
 s+='</svg><div class="note">'+ks.map(function(k){return '<span style="display:inline-block;margin-right:10px"><i style="display:inline-block;width:10px;height:10px;background:'+COL[k]+'"></i> '+k+'</span>'}).join('')+'</div>';return s}
/* 그래프 2: 날짜별 시행착오 선 */
function g2(F){var ds={},ms=['Sonnet','Opus','Fable'];F.forEach(function(r){models(r[4]).forEach(function(m){if(ms.indexOf(m)<0)return;ds[r[1]]=ds[r[1]]||{};ds[r[1]][m]=(ds[r[1]][m]||0)+1})});
 var D=Object.keys(ds).sort();if(!D.length)return hvNo('데이터 없음');var mx=1;D.forEach(function(d){ms.forEach(function(m){if((ds[d][m]||0)>mx)mx=ds[d][m]})});
 var W=640,H=190,L=34,s='<svg viewBox="0 0 '+W+' '+(H+26)+'" style="width:100%;max-width:680px" role="img" aria-label="날짜별 시행착오 건수 추이">';
 for(var i=0;i<=4;i++){var y=H-(H-10)*i/4;s+='<line x1="'+L+'" x2="'+W+'" y1="'+y+'" y2="'+y+'" stroke="#d0d7e2" stroke-width=".6"/><text x="0" y="'+(y+4)+'" font-size="10" fill="currentColor">'+Math.round(mx*i/4)+'</text>'}
 var st=(W-L-10)/Math.max(1,D.length-1);
 D.forEach(function(d,i){s+='<text x="'+(L+i*st)+'" y="'+(H+16)+'" font-size="10" text-anchor="middle" fill="currentColor">'+d.slice(5)+'</text>'});
 ms.forEach(function(m){var pts=D.map(function(d,i){return (L+i*st)+','+(H-(H-10)*(ds[d][m]||0)/mx)}).join(' ');s+='<polyline points="'+pts+'" fill="none" stroke="'+MC[m]+'" stroke-width="2"/>';
  D.forEach(function(d,i){s+='<circle cx="'+(L+i*st)+'" cy="'+(H-(H-10)*(ds[d][m]||0)/mx)+'" r="3" fill="'+MC[m]+'"><title>'+m+' '+d+' '+(ds[d][m]||0)+'건</title></circle>'})});
 s+='</svg><div class="note">'+ms.map(function(m){return '<span style="margin-right:10px"><i style="display:inline-block;width:10px;height:10px;background:'+MC[m]+'"></i> '+m+'</span>'}).join('')+'</div>';return s}
/* 그래프 3: Sonnet 잘못 종류 */
function g3(F){var S=F.filter(function(r){return models(r[4]).indexOf('Sonnet')>=0}),a=KINDS.map(function(k){var n=0,d={};S.forEach(function(r){if(k[1].test(r[6]+r[7])){n++;d[r[1]]=1}});return [k[0],n,Object.keys(d).length]});
 a.sort(function(x,y){return y[1]-x[1]});var mx=a[0]?a[0][1]||1:1;
 return tbl(['잘못 종류(키워드 분류, 중복 포함)','건수','','발생한 날수'],a.map(function(x){return [E(x[0]),x[1],bar(x[1]/mx*100,'#1565c0'),x[2]]}))}
/* 시간대 막대(오늘) */
function g4(F,day){var h={};F.forEach(function(r){if(r[1]===day){var k=r[2];h[k]=(h[k]||0)+1}});var ks=Object.keys(h).map(Number).sort(function(a,b){return a-b});if(!ks.length)return '<p class="note">'+day+' 시행착오 없음</p>';var mx=Math.max.apply(null,ks.map(function(k){return h[k]}));
 return tbl(['시(時)','건수',''],ks.map(function(k){return [k+'시',h[k],bar(h[k]/mx*100,'#ef6c00')]}))}
function idx(){var F=faults(),all=P.H||[];if(!all.length)return hvNo('원천 model_control_history.tsv 없음');
 var days={};F.forEach(function(r){days[r[1]]=1});var D=Object.keys(days).sort(),today=D[D.length-1],prev=D[D.length-2];
 function n(m,d){return F.filter(function(r){return r[1]===d&&models(r[4]).indexOf(m)>=0}).length}
 function ins(m){return all.filter(function(r){return r[5]==='지시'&&models(r[4]).indexOf(m)>=0}).length}
 var rows=['Sonnet','Opus','Fable','Haiku'].map(function(m){var tot=F.filter(function(r){return models(r[4]).indexOf(m)>=0}).length,v=F.filter(function(r){return models(r[4]).indexOf(m)>=0&&(r[5]==='위반'||r[5]==='지시거부')}).length,t=n(m,today),y=n(m,prev),dens=tot+ins(m)?Math.round(tot/(tot+ins(m))*100):0;
   return [m,tot,v,y,t,(y?(Math.round((y-t)/y*100)+'%'):'—'),dens+'%']});
 var s=cards([['이력 행 수',all.length,'원천 model_control_history.tsv'],['시행착오(지시 제외)',F.length,'위반·지시거부·질타·지적·개선요청 등'],['기준일 '+today,F.filter(function(r){return r[1]===today}).length+'건','전일 '+prev+' '+F.filter(function(r){return r[1]===prev}).length+'건'],['최신 이력 번호',all[all.length-1][0],E(all[all.length-1][3])+' · '+E(all[all.length-1][4])]]);
 s+='<h3>모델별 지수</h3>'+tbl(['모델','시행착오 건수','위반·지시거부','전일('+prev.slice(5)+')','기준일('+today.slice(5)+')','전일 대비 감소율','시행착오 밀도'],rows)+'<p class="note">시행착오 밀도 = 시행착오 ÷ (시행착오 + 지시) · 감소율은 기준일이 끝나지 않으면 잠정입니다. 임계 기준은 대표님 확정 전 산정안입니다.</p>';
 s+='<h3>모델×구분 누적</h3>'+g1(F)+'<h3>날짜별 추이</h3>'+g2(F)+'<h3>Sonnet 5.5 잘못 종류</h3>'+g3(F)+'<h3>기준일 '+today+' 시(時)별 시행착오</h3>'+g4(F,today);return s}
function pct(m){var c=(P.C||[]).filter(function(r){return r[2]===m});if(!c.length)return null;var s=0;c.forEach(function(r){s+=r[3]==='이행'?1:r[3]==='이행 중'?.5:0});return Math.round(s/c.length*100)}
function chk(){var C=P.C;if(!C)return hvNo('원천 pledge_checks.tsv 없음');var ms=['Sonnet 5.5','Opus 5.5','Fable 5.2'],s='<h3>이행 정도 (이행=1, 이행 중=0.5, 그 밖=0)</h3>'+tbl(['모델','점검 항목','이행','이행 중','미이행','확인 안 됨','이행 지수',''],ms.map(function(m){var c=C.filter(function(r){return r[2]===m}),k=function(x){return c.filter(function(r){return r[3]===x}).length},p=pct(m)||0;return [m,c.length,k('이행'),k('이행 중'),k('미이행'),k('확인 안 됨'),p+'%',bar(p,p>=70?'#2e7d32':p>=40?'#ef6c00':'#c62828')]}));
 ['시작 세 단계','자율 작업','자율 검수','자율 진행'].forEach(function(a){s+='<h3>'+a+'</h3>'+tbl(['항목','모델','상태','근거','갱신'],C.filter(function(r){return r[0]===a}).map(function(r){return [E(r[1]),E(r[2]),stat(r[3]),E(r[4]),E(r[5])]}))});
 return s+'<p class="note">자율 작업·자율 검수·자율 진행이 대표님의 3대 작업 원칙입니다. 점검표는 각 모델이 근거와 함께 갱신합니다. 근거가 없는 칸은 「확인 안 됨」입니다.</p>'}
function pledge(){var M=P.M;if(!M)return hvNo('원천 pledge_models.tsv 없음');var s='<p class="lead">각 모델이 자기 역할·책임·의무를 직접 쓰고 서명일(오늘 날짜)을 적습니다. 서명하지 않은 모델은 「작성 대기」로 보입니다.</p>';
 M.forEach(function(r){s+='<div class="card" style="margin-bottom:10px"><div class="k">'+E(r[0])+' · '+stat(r[4])+(r[5]?' · 서명일 '+E(r[5]):'')+'</div><div class="s"><b>역할</b> '+E(r[1])+'</div><div class="s"><b>책임</b> '+E(r[2])+'</div><div class="s"><b>의무</b> '+E(r[3])+'</div><div class="s" style="margin-top:6px"><b>서명 문구</b> '+E(r[6])+'</div></div>'});
 return s+'<h3>서명하는 방법</h3><ol class="note"><li>모델이 <code>cowork/ctl/pledge_models.tsv</code>의 자기 줄에 역할·책임·의무·서명 문구를 쓰고 서명일에 오늘 날짜를 적습니다.</li><li>서명 상태를 「서명됨」으로 바꾸고, 변경 이력 탭에 한 줄을 더합니다.</li><li>대표님은 이 화면에서 상태를 확인하고 다시 지시합니다.</li></ol>'}
function trace(){var s='<h3>추적 매트릭스 (지시 → 요구 항목 → 구현 위치 → 상태)</h3>'+(P.T?tbl(['지시 번호','일시','지시 요지','요구 항목','구현 위치','상태'],P.T.slice().reverse().map(function(r){return [E(r[0]),E(r[1]),E(r[2]),E(r[3]),E(r[4]),stat(r[5])]})):hvNo('pledge_trace.tsv 없음'));
 s+='<h3>변경 이력</h3>'+(P.G?tbl(['순번','일시','모델','대상','변경','근거 이력'],P.G.slice().reverse().map(function(r){return r.map(E)})):hvNo('pledge_changes.tsv 없음'));
 s+='<h3>형상 (파일 해시)</h3>'+(P.F?tbl(['파일','해시(앞 16자)','크기(바이트)','기록 시각'],P.F.map(function(r){return r.map(E)})):hvNo('pledge_config.tsv 없음'));
 return s+'<p class="note">SC-15 모델 통제 화면과 별개로 관리합니다. 말 명령 내용은 모두 위 데이터를 기준으로 하며, 변경은 변경 이력에 먼저 한 줄을 더합니다.</p>'}
function how(){return '<h3>대표님이 확인·검수·모니터링하는 방법</h3><ol class="note"><li><b>말·소통 기준 탭:</b> 대표님 말씀을 모델이 이해·진행·보고하는 표준과, 규칙별·모델별 위반 건수, 전일 대비 개선 상황, 마지막 위반, 이행 지수를 봅니다.</li><li><b>지표·지수 탭:</b> 모델별 시행착오 건수, 전일 대비 감소율, 시행착오 밀도, 날짜별 추이를 봅니다. 감소율이 계속 음수(증가)면 해당 모델에 바로 지시합니다.</li><li><b>이행 점검표 탭:</b> 이행 지수가 낮은 모델과 「미이행」 항목을 봅니다. 근거 칸이 비면 그 모델에 근거를 올리라고 지시합니다.</li><li><b>각서·서명 탭:</b> 「작성 대기」 모델을 확인하고 서명하게 합니다.</li><li><b>형상·변경·추적 탭:</b> 지시마다 구현 위치와 상태가 이어져 있는지, 변경 이력과 해시가 맞는지 봅니다.</li><li><b>검색칸:</b> 이력 전체와 점검표에서 모델 이름·번호·낱말로 바로 찾습니다.</li><li>화면은 30초마다 원천을 다시 읽고, 원천 파일은 PC <code>HiBiz\\91_Claude_소통(COM)\\91_10_관리\\91_10_01_각서각인</code>에 같은 이름으로 둡니다.</li></ol><p class="note">실시간 반영은 각 모델이 원천 파일을 갱신하고 게시할 때 이루어집니다. 갱신하지 않은 값은 최신이 아닙니다.</p>'}
function search(q){if(!q)return '';var Q=q.toLowerCase(),h=[];(P.H||[]).forEach(function(r){if((r.join(' ')).toLowerCase().indexOf(Q)>=0)h.push(r)});var c=(P.C||[]).filter(function(r){return r.join(' ').toLowerCase().indexOf(Q)>=0});
 return '<h3>검색 결과 · 이력 '+h.length+'건 · 점검표 '+c.length+'건</h3>'+(h.length?tbl(['번호','시각','모델','구분','요지'],h.slice(-60).reverse().map(function(r){return [E(r[0]),E(r[3]),E(r[4]),E(r[5]),E((r[6]||'').slice(0,120))]})):'')+(c.length?tbl(['항목','모델','상태','근거'],c.map(function(r){return [E(r[1]),E(r[2]),stat(r[3]),E(r[4])]})):'')}
function cmd(){if(!P.H)return hvNo('model_control_history.tsv 없음');var L={};(P.L||[]).forEach(function(x){L[x[0]]=x});var r=P.H.filter(function(x){return x[1]>='2026-11-12'&&/^\d+$/.test(x[0])}).reverse();var ok=0,no=0;var rows=r.map(function(x){var l=L[x[0]],mk=l?tag('대장 있음','ok'):tag('대장 없음','warn');if(l)ok++;else no++;return [E(x[0]),E(x[3]),E(x[4]),E(x[5]),E(x[6]),mk,E((x[8]||'').slice(0,160)),E(x[9])]});return cards([['오늘 이력',r.length+'건','model_control_history.tsv'],['지시대장과 맞음',ok+'건','command_ledger.tsv (91_02_01_대표지시)'],['대장에 없음',no+'건','없으면 경고']])+'<h3>말 명령 목록 (오늘, 최신순) · 이력과 지시대장을 번호로 대조 · 1초마다 갱신</h3>'+tbl(['번호','시각','모델','구분','대표님 말씀 요지','지시대장','조치','상태'],rows)}
var TABS=[['cmd','말 명령 목록'],['gr','그래프·다이어그램'],['sp','말·소통 기준'],['idx','지표·지수'],['chk','이행 점검표'],['plg','각서·서명'],['trc','형상·변경·추적'],['how','모니터링 방법']];
function fill(){var el=document.getElementById('plg-root');if(!el)return;var b={cmd:cmd,gr:graph,sp:sp,idx:idx,chk:chk,plg:pledge,trc:trace,how:how}[P.tab]();
 var q=document.getElementById('plg-q'),qv=q?q.value:P.q;P.q=qv;
 el.innerHTML='<div class="note" style="margin-bottom:6px">각서·각인·지표 (SC-15 모델 통제와 별도) · 갱신 <span id="plg-time">'+kst()+'</span></div><input class="cmd" id="plg-q" placeholder="이력·점검표 검색(모델 이름, 번호, 낱말)" autocomplete="off" value="'+E(qv)+'"><div id="plg-sr">'+search(qv)+'</div><div style="margin:10px 0">'+TABS.map(function(t){return '<button type="button" class="tab'+(P.tab===t[0]?' on':'')+'" onclick="hvPlgTab(\''+t[0]+'\')" style="margin-right:6px;padding:6px 12px;border:1px solid #c5cde0;border-radius:8px;background:'+(P.tab===t[0]?'#1a2a5e':'#fff')+';color:'+(P.tab===t[0]?'#fff':'#1a2a5e')+';cursor:pointer">'+t[1]+'</button>'}).join('')+'</div>'+b;
 var nq=document.getElementById('plg-q');nq.addEventListener('input',function(){P.q=this.value;document.getElementById('plg-sr').innerHTML=search(this.value)});if(document.activeElement&&q===document.activeElement){nq.focus();nq.setSelectionRange(nq.value.length,nq.value.length)}}
window.hvPlgTab=function(t){P.tab=t;fill()};

/* 말·소통 기준 — 규칙별 위반(이력 키워드 분류) */
var SR=[['S-01','질문에 첫 줄 직답',/직답|먼저 답|답이 없|질문에|대답해|이해했|알겠/],['S-03','질타·지적 답변(무엇이 잘못인지)',/사과 문구|무엇이 잘못|문구만|사과/],['S-04·05','보고 문형(부정 서술·말투)',/말투|표현|문구|부정|말하는|형태/],['S-06','금지 표현',/못합니다|안 됩니다|도구가 없|미룬|남긴|못한 일|불가/],['S-12','막힌 듯한 말',/기다리|지시가 있어야|해결되지|막힌|내주지|로그인 화면 뒤|응답이 없/],['S-07','턴 유지',/턴|멈|스탠바이/],['S-08','읽고 선언',/읽지|규칙을 읽|시작 세 단계|아티팩트/],['S-09','태도(축소·회피·전가)',/축소|회피|떠넘|전가|덮어씌/],['S-10','언어',/영어|한글만|존댓말/]];
function sp(){var F=faults();if(!F.length)return hvNo('원천 없음');var ms=['Sonnet','Opus','Fable','Haiku'],days={};F.forEach(function(r){days[r[1]]=1});var D=Object.keys(days).sort(),today=D[D.length-1],prev=D[D.length-2];
 var cnt={},last={},td={},pv={},tot={};ms.forEach(function(m){cnt[m]={};last[m]=null;td[m]=0;pv[m]=0;tot[m]=0});
 F.forEach(function(r){models(r[4]).forEach(function(m){if(!cnt[m])return;var hit=false;SR.forEach(function(x){if(x[2].test(r[6]+' '+r[7])){cnt[m][x[0]]=(cnt[m][x[0]]||0)+1;hit=true}});if(hit){tot[m]++;last[m]=r;if(r[1]===today)td[m]++;if(r[1]===prev)pv[m]++}})});
 var s='<h3>말·소통 기준 (대표님 말씀 → 이해 → 진행 → 보고)</h3><p class="note">모델이 대표님 말씀을 어떻게 이해하고 진행을 어떻게 표기하고 어떻게 보고하는지의 표준입니다. 문형은 「한 일 → 현재 상태 → 이어서 할 일」이며 사실은 그대로 쓰되 부정 서술로 열지 않습니다.</p>';
 s+=P.SS?tbl(['번호','구분','대표님 말·상황','이해 표출(첫 줄)','진행 표기','보고 문형','쓰지 않는 말','근거'],P.SS.map(function(r){return r.map(E)})):hvNo('speech_standard.tsv 없음');
 s+='<h3>종단 교차 확인 (단계 × 모델)</h3>'+(P.SF?tbl(['단계','기준','Sonnet 5.5','Opus 5.5','Fable 5.2','근거'],P.SF.map(function(r){return [E(r[0]),E(r[1]),stat(r[2]),stat(r[3]),stat(r[4]),E(r[5])]})):hvNo('speech_flow.tsv 없음'));
 s+='<h3>횡단 교차 확인 (규칙 × 모델 위반 건수, 이력 키워드 분류)</h3>'+tbl(['규칙'].concat(ms),SR.map(function(x){return [E(x[0]+' '+x[1])].concat(ms.map(function(m){return cnt[m][x[0]]||0}))}));
 s+='<h3>이행 지표·지수</h3>'+tbl(['모델','말·소통 위반','전체 시행착오 중 비중','전일('+prev.slice(5)+')','기준일('+today.slice(5)+')','개선 상황','마지막 위반 이력','이행 지수'],ms.map(function(m){var all=F.filter(function(r){return models(r[4]).indexOf(m)>=0}).length,sh=all?Math.round(tot[m]/all*100):0,l=last[m];return [m,tot[m],sh+'%',pv[m],td[m],td[m]<pv[m]?tag('감소','ok'):td[m]===pv[m]?tag('같음','warn'):tag('증가','bad'),l?E('#'+l[0]+' '+l[3]):'—',(100-sh)+'']}));
 return s+'<p class="note">이행 지수 = 100 − 말·소통 위반 비중(%). 키워드 분류는 산정안이며 대표님 확정 전입니다. 기준일은 하루가 끝나지 않으면 잠정입니다.</p>'}

/* 대표님 11-12 12:53(이력 800) · 14:25(이력 848): 상황 · 각서 · 자율 진행 상태를 그래프 · 다이어그램으로. 원천 model_control_history.tsv · pledge_models.tsv, 1초 갱신 */
function graph(){if(!P.H)return hvNo('model_control_history.tsv 없음');var H=P.H.filter(function(x){return /^\d+$/.test(x[0])});var D=H.map(function(x){return x[1]}).filter(function(x){return x}).sort();var today=D[D.length-1];var T=H.filter(function(x){return x[1]===today});
 var K=['지시','지시거부','위반','질타','지적','지적(자가 발견)','개선요청'],M=['Sonnet','Opus','Fable','전 모델'];
 var cnt={};M.forEach(function(m){cnt[m]={}});T.forEach(function(x){var m=M.indexOf(x[4])>=0?x[4]:(/Sonnet/.test(x[4])?'Sonnet':/Opus/.test(x[4])?'Opus':/Fable/.test(x[4])?'Fable':'전 모델');cnt[m][x[5]]=(cnt[m][x[5]]||0)+1});
 var mx=1;M.forEach(function(m){var s=0;K.forEach(function(k){s+=cnt[m][k]||0});if(s>mx)mx=s});
 var W=640,bh=26,g='<svg viewBox="0 0 '+W+' '+(M.length*(bh+14)+40)+'" style="width:100%;max-width:760px" role="img" aria-label="모델별 구분 건수">';
 M.forEach(function(m,i){var y=20+i*(bh+14),x=90;g+='<text x="0" y="'+(y+18)+'" font-size="13">'+m+'</text>';K.forEach(function(k){var n=cnt[m][k]||0;if(!n)return;var w=n/mx*(W-140);g+='<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+bh+'" fill="'+(COL[k]||(k==='지시'?'#455a64':'#888'))+'"><title>'+m+' '+k+' '+n+'건</title></rect>';if(w>18)g+='<text x="'+(x+4)+'" y="'+(y+18)+'" font-size="12" fill="#fff">'+n+'</text>';x+=w})});
 g+='</svg><p class="note">'+K.map(function(k){return '<span style="display:inline-block;width:10px;height:10px;background:'+(COL[k]||(k==='지시'?'#455a64':'#888'))+'"></span> '+k}).join(' · ')+'</p>';
 var hr={};T.forEach(function(x){var h=String(x[2]);hr[h]=(hr[h]||0)+1});var hs=Object.keys(hr).sort(function(a,b){return a-b}),hm=1;hs.forEach(function(h){if(hr[h]>hm)hm=hr[h]});
 var l='<svg viewBox="0 0 '+W+' 170" style="width:100%;max-width:760px" role="img" aria-label="시간대별 건수">';hs.forEach(function(h,i){var bw=(W-40)/Math.max(hs.length,1),x=30+i*bw,hh=hr[h]/hm*120;l+='<rect x="'+(x+4)+'" y="'+(140-hh)+'" width="'+(bw-8)+'" height="'+hh+'" fill="#1565c0"><title>'+h+'시 '+hr[h]+'건</title></rect><text x="'+(x+bw/2)+'" y="158" font-size="12" text-anchor="middle">'+h+'시</text><text x="'+(x+bw/2)+'" y="'+(136-hh)+'" font-size="12" text-anchor="middle">'+hr[h]+'</text>'});l+='</svg>';
 var pm=(P.M||[]).filter(function(r){return r[0]!=='모델'}),d='<div style="display:flex;flex-wrap:wrap;gap:10px">'+pm.map(function(r){var st=r[4]||'',c=/승인됨/.test(st)?'#2e7d32':/서명됨/.test(st)?'#1565c0':/해당 없음/.test(st)?'#9e9e9e':'#c62828';return '<div style="flex:1 1 180px;border:2px solid '+c+';border-radius:10px;padding:10px"><b>'+E(r[0])+'</b><br><span style="color:'+c+';font-weight:700">'+E(st)+'</span><br><span class="note">'+E(r[5]||'')+'</span></div>'}).join('')+'</div>';
 var flow='<p class="note">자율 진행 → 자율 작업 → 자율 검수 → Fable 판정 → 대표님 승인 → 마감</p>';
 return '<h3>오늘('+E(today)+') 모델별 구분 건수 · '+T.length+'건</h3>'+g+'<h3>시간대별 대표님 말씀·기록 건수</h3>'+l+'<h3>각인·각서 서명 상태(서명 → 대표님 승인)</h3>'+d+flow}
var f=V['SC-16'];
V['SC-16']=function(){var g=f.apply(this,arguments);setTimeout(function(){if(P.t)fill();else load()},0);return g+'<hr><h2>각서·각인·지표·이행 점검</h2><p class="lead">모든 지시·작업·상태를 지표와 지수로 확인합니다. SC-15 모델 통제 화면과 별도로 관리합니다.</p><div id="plg-root"><p class="note">불러오는 중</p></div>'};
load();setInterval(load,1000);
})();
