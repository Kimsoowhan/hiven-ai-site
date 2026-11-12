/* 원본 대시보드 = 실측 데이터만 (대표님 지시 11/04 15:53·15:56). 노트북 원천 파일을 모델이 직접 열어 확인한 값만 확인 시각과 함께 싣는다.
   시험·샘플·확인 안 된 값은 원본에 싣지 않는다 → 같은 구성의 시험 페이지 /test/ 에서만 보인다.
   이 파일은 자동 연동이 아니다(금지 4조항: 자동 동기화 금지). 모델이 원천을 다시 확인할 때마다 HVR 값을 고치고 확인 시각을 바꾼다. */
var HVR={
 chk:'2026-11-04 15:56',by:'Opus 5.5',
 src:'HiBiz\\00_클로_기억장치(EMG)\\09_HiClo_앱(APP)\\HiClo_기억상태-261103.json',
 hiclo:{ver:'HiClo.app 3.1.2',last:'2026-11-03 20:54:58',verdict:'경고',miss:258,stage:'혼미(3단계)'},
 hiven:{last:'2026-11-03 03:55:13',note:'HiClo 판정 파일의 HIVEN 관계 신호 시각(HIVEN 단계 「불명확」)'},
 job:{id:'JOB-S0175c',end:'2026-11-03 03:55:13',rc:0,src:'10_작업대기열(JOB)\\02_나감(OUT)\\JOB-S0175c-261102-결과.json'},
 save:{period:60,setAt:'2026-11-02 07:52',sched:'2026-11-03 18:00부터 30분',src:'09_HiClo_앱(APP)\\저장주기.json'},
 issues:[
  ['2026-11-03 20:54:58','경고','HiClo','관측 끊김 258회 연속(지시원장 불명확)'],
  ['2026-11-03 20:54:58','경고','클로','혼미(3단계)'],
  ['2026-11-03 20:54:58','경고','작업기억','GBP_작업기억·단기기억_스냅샷·할일큐 11/02 10:59:48 뒤 갱신 없음'],
  ['2026-11-03 20:54:58','불명확','노드','노드생존·기억회복상태·단기기억기록 불명확']]
};
function hvNo(t){return tag('원천 없음','bad')+(t?' '+t:'')}
/* 11-12 이력 874(13:33 지시 적용): 멈춘 실측은 「확인 안 됨」 대신 정지 · 경과 시간 · 경고 */
function hvStop(ts){var t=ts?new Date(String(ts).replace(' ','T')+'+09:00').getTime():HVST,h=Math.max(0,Math.floor((Date.now()-t)/3600000));return '정지 '+(h>=24?Math.floor(h/24)+'일 ':'')+(h%24)+'시간'}
function hvChkAge(){var d=Math.floor((Date.now()-Date.parse(HVR.chk.replace(' ','T')+':00+09:00'))/86400000);return d>0?d+'일 지남':'오늘'}
/* 261111 N-7: 꼬리말의 「확인 시각」은 노트북 구동·판정 값(HVR)을 마지막으로 확인한 때다. 화면 전체를 그때 확인했다는 뜻으로 읽히지 않게 무엇의 시각인지와 지난 날수를 사실대로 적는다 */
function hvChk(){var m=(typeof hvMeta!=='undefined'&&hvMeta.m)?hvMeta.m.published:'확인 안 됨';return '<p class="note">원본 대시보드는 <b>실측 데이터만</b> 보입니다. 노트북 구동·판정 값의 마지막 확인 시각 '+HVR.chk+'('+hvChkAge()+' · 확인 '+HVR.by+' · 원천 '+HVR.src+') — 그 뒤 다시 확인하지 않았습니다. 게시 자료(이력·생명주기 등) 메타 산출 '+hvEsc(m)+'. 확인되지 않은 값은 「확인 안 됨」으로 표시하고, 시험·샘플 값은 <a href="test/">시험 페이지</a>에서만 봅니다.</p>'}
function hvTestOnly(id,name){return function(){return '<h2>'+id+' '+name+'</h2><div class="grid">'+card('원본 대시보드','실측 데이터 없음','시험 중 · 원본 제외',null,function(){return '<p class="note">이 화면은 아직 시험 중이거나 시험·샘플 값으로 되어 있어 원본에 싣지 않습니다(대표님 지시 11/04 15:56). 시험 화면은 <a href="test/#'+id+'">시험 페이지</a>에서 봅니다. 정확한 일정·체계·대안은 Fable이 일괄 적용합니다(15:57).</p>'})+'</div>'+hvChk()}}
var HVST=Date.parse(HVR.hiclo.last.replace(' ','T')+'+09:00');
function hvAge(){var m=Math.round((Date.now()-HVST)/60000);return m<60?m+'분':Math.floor(m/60)+'시간 '+(m%60)+'분'}

/* SC-01 종합 현황 재설계(대표님 11/04 17:37·17:38): 가장 중요한 4가지 = 장애 · 위험 요소 · 자가 검수 · 조치 결과 + 최우선 장애 경로, 상자 10개.
   장애·위험·자가 검수·조치 결과는 모델통제 이력 게시본(cowork/ctl/model_control_history.tsv)과 지시 추적 교차 검사(trace_sum.json)를 읽어 센다(실측). 구동·경보는 HVR(노트북 원천 확인값). */
var HV_KV={};var hv01={ev:null,sum:null,ok:'',t:0};
/* 장애 경로(확인된 사실만, 근거 기록 번호 표기). 순서 = 심각도(진행 중·재발 위험 우선) */
var HV_PATH=[
 {t:'하위 작업 중단(4회) — 결과 미수신·지연',st:'조치 진행 중',ref:'모델통제 이력 84번 · COM\\작업중단·재개_결함분석_재발방지-261104_0.1_작업.md',
  p:['대표님 새 메시지 도착(16:39:30·16:51:59·16:58:58·17:12:26, 4번 모두 같은 초)','진행 중이던 하위 조사·추출 작업 종료','결과 보고 없음(마지막 보고 1회만 받게 지시한 결함)','대기 장치가 완료만 감시 → 멈춤 14분간 모름, 30분 한도로 대기 종료','초안·매트릭스 지연'],
  r:'중간 저장·감시 장치(완료·멈춤·파일 없음)·재개 카드 적용 → 17:12 4번째 멈춤은 감시 장치가 바로 알렸고 중간 저장분부터 재개, 17:19·17:21·17:25 3건 모두 결과 수신. 남은 것: 새 메시지에 하위 작업이 끝나는 시스템 동작의 원인은 확인 안 됨(관찰 사실만) → 감시·중간 저장으로 계속 대응'},
 {t:'HiClo 판정 멈춤 — 구동 상태 확인 불가',st:'조치 진행 중',ref:'HVR(노트북 HiClo_기억상태-261103.json) · 91_Fable\\AICS_자동화_처리정책_261104.md · 이력 2·6·61번',
  p:['노트북 예약작업 「HiClo 기억 장치」(5분 주기)','11/03 20:56 비활성(무단 재실행 위반 6번 대응으로 정지)','판정 파일 마지막 갱신 11/03 20:54:58 「경고」','관측 끊김 258회 · 클로 혼미(3단계)','대시보드 구동 상태 「확인 안 됨」'],
  r:'자동화 동결·격리(AICS 처리정책 11/04 10:53 승인), 원본 대시보드는 실측만 표시(15:58, 이력 61번 조치 완료). 남은 것: 재가동 여부 결정(조건 4개: 체계 문서 확정·연동 설계 승인·10개 단위 시험·되돌리기 절차) — Fable·대표님 결정 대기'}];
var hvMX01=null,hvMX01t=0;
function hvMx01Get(){if(!hvMX01||Date.now()-hvMX01t>30000){hvMX01t=Date.now();hvFetch('cowork/ctl/model_control_index.json','json').then(function(j){hvMX01=j;if(cur==='SC-01'&&$('sc01'))render('SC-01')},function(){})}}
function hvEl01(iso){var ms=Date.now()-Date.parse(iso);if(!(ms>0))return '방금';var m=Math.floor(ms/60000),h=Math.floor(m/60),dd=Math.floor(h/24);return dd?dd+'일 '+(h%24)+'시간':h?h+'시간 '+(m%60)+'분':m+'분'}
function hvAlert01(){
 hvMx01Get();var X=hvMX01;if(!X||!X.alerts)return '';
 var B=X.alerts.rows.filter(function(a){return a.level==='차단'});if(!B.length)return '';
 return '<div style="border:2px solid #7f0000;background:#fff5f5;border-radius:8px;padding:10px 14px;margin:10px 0"><b style="color:#7f0000">차단 경보 '+B.length+'건 열림 — 통제 체계의 막힘·우회 징후(모델 결함 경보보다 위 등급)</b>'
 +tbl(['경보','막힌 단계','사유','막혀 있는 시간','담당'],B.map(function(a){return [hvEsc(a.title),hvEsc(a.stage),hvEsc(a.reason),'<b>'+hvEl01(a.since)+'</b>',hvEsc(a.owner)]}))
 +'<p class="note">해소 조건·매트릭스 추적·울타리는 <a href="#" onclick="hvgo(\'SC-15\');return false">SC-15</a>.</p></div>'}
function hvMcs01(N){
 hvMx01Get();var X=hvMX01;if(!X)return '<h3>모델 통제 요약</h3><p class="note">집약 게시본을 읽는 중입니다.</p>';
 var ms=Object.keys(X.models),st=X.history_rows!==N,ax=Object.keys(X.axes);
 return '<h3>모델 통제 요약 (자동화 통합 통제 체계 → 시스템)</h3>'+(st?'<p class="note" style="color:#c62828"><b>집약 게시본 이력 '+X.history_rows+'건 ≠ 현재 '+N+'건 — 재집약 필요</b></p>':'')
 +tbl(['모델','상태 신호','통제 지수','재발률','판정','거부/위반/낭비','칭찬 크레딧','시스템','서비스','고객 지원'],ms.map(function(m){var o=X.models[m],f=o.frequency||{},a=function(k){var v=X.axes[k]&&X.axes[k][m];return v?v.faults:0},r=o.recurrence||{};var aw=(X.awareness&&X.awareness.models[m])||null,cr=(X.credit&&X.credit.models[m])||{credit:0};return [hvEsc(m),aw?aw.signal:'-',(o.index&&o.index.control!=null?o.index.control:'-'),(r.rate!=null?Math.round(r.rate*1000)/10+'%':'-'),tag(hvEsc(r.judgment||'-'),/없음/.test(r.judgment||'')?'bad':/미흡/.test(r.judgment||'')?'warn':'ok'),(f['지시거부']?f['지시거부']['합계']:0)+' / '+(f['지시위반']?f['지시위반']['합계']:0)+' / '+(f['사용량 낭비']?f['사용량 낭비']['합계']:0),cr.credit,a('시스템'),a('서비스'),a('고객 지원')]}))
 +'<p class="note">전체 표·정합성·역방향 검토는 <a href="#" onclick="hvgo(\'SC-15\');return false">SC-15</a>. 집약 기준 이력 '+X.history_rows+'건.</p>'}
function hv01Load(){Promise.all([hvFetch('cowork/ctl/model_control_history.tsv','text'),hvFetch('cowork/ctl/trace_sum.json','json').catch(function(){return null}),hvFetch('cowork/ctl/action_lifecycle.tsv','text').catch(function(){return ''}),hvFetch('cowork/ctl/action_lifecycle.json','json').catch(function(){return null}),hvFetch('cowork/ctl/qa_checks.tsv','text').catch(function(){return ''}),hvFetch('cowork/progress.json','json').catch(function(){return null})]).then(function(r){hv01.lc=hvTsv(r[2]);hv01.lcs=r[3];hv01.qa=hvTsv(r[4]);hv01.pg=r[5];
 hv01.ev=hvTsv(r[0]).map(function(c){return {no:c[0],date:c[1],time:c[3],model:c[4],type:c[5],content:c[6],cause:c[7],action:c[8],status:c[9]}});hv01.sum=r[1];hv01.ok=kst();hv01.t=Date.now();if(cur==='SC-01'&&$('sc01'))render('SC-01')},function(){})}
function hv01T(a,cols){var r=a.slice().reverse(),more=false;return a.length?tbl(['#','시각','구분','내용','조치','상태'],r.map(function(e){return [e.no,hvEsc(e.time),hvEsc(e.type),hvEsc(e.content),hvEsc(e.action),tag(hvEsc(e.status),hvStDone(e.status)?'ok':'warn')]}))+(more?'<p class="note">'+r.length+'건 중 최신 15건 — 전체는 <a href="#" onclick="hvgo(\'SC-15\');return false">SC-15</a>에서 「조치 진행 중」 상자를 누르면 봅니다.</p>':''):'<p class="note">해당 없음</p>'}
V['SC-01']=function(){
 if(!hv01.ev||Date.now()-hv01.t>30000)setTimeout(hv01Load,0);/* 화면을 열 때마다(30초 지나면) 게시본을 다시 읽음 */
 var E=hv01.ev||[],L=!hv01.ev,S=hv01.sum,done=function(e){return hvStDone(e.status)};
 var fa=E.filter(function(e){return e.type==='장애'}),faO=fa.filter(function(e){return !done(e)});
 var vi=E.filter(function(e){return e.type==='위반'}),viO=vi.filter(function(e){return !done(e)}),warn=HVR.issues.filter(function(r){return r[1]==='경고'});
 var se=E.filter(function(e){return e.type==='지적(자가 발견)'}),sx=S?S['종단']||{}:{},sh=S?S['횡단']||{}:{};
 var dn=E.filter(done),op=E.filter(function(e){return !done(e)});
 var nf=faO.length+1/* HiClo 판정 멈춤(시스템) */,nr=warn.length+viO.length;
 var g='<div id="sc01"><h2>SC-01 종합 현황</h2><p class="lead">가장 중요한 장애 상태(경고) · 위험 요소(예측) · 자가 검수(예방) · 조치 중 · 조치 완료(검수)와 구동 상태를 봅니다. 상자를 누르면 그 근거가 아래에 펼쳐집니다.</p>'+hvAlert01();
 var LC=hv01.lc||[],lcM={};LC.forEach(function(x){lcM[x[0]]=x});var QA=hv01.qa||[],qaBad=QA.filter(function(x){return x[2]!=='통과'});
 var it=(hv01.pg&&hv01.pg.items)||[],now=new Date(),late=it.filter(function(x){var d=typeof hvDue==='function'?hvDue(x.due):null;return d&&x.score<100&&(d-now)<24*3600000});
 var c3=function(k){return E.filter(function(e){return (lcM[e.no]?lcM[e.no][5]:(done(e)?'조치 완료':'조치 중'))===k})},nM=c3('미조치'),nI=c3('조치 중'),nD=c3('조치 완료');
 var RISK=[['하위 작업 중단 재발','새 메시지 도착 때 진행 중 하위 작업 종료(4회 관찰)','감시 장치·중간 저장으로 대응 중 — 원인(시스템) 확인 안 됨','이력 84'],['기록 번호 중복','같은 세션 서명의 다른 흐름이 동시 기록','기록 직전 최신본 받기·중복 검사','이력 78'],['구동 상태 판단 불가 지속','HiClo 판정 파일 '+hvAge()+' 갱신 없음','재가동 결정 전까지 「확인 안 됨」 표시','HVR'],['보고서 이관 지연','일일보고 마지막 갱신 '+((hv01.lcs&&hv01.lcs['보고서 기준'])?Object.keys(hv01.lcs['보고서 기준']).filter(function(k){return k.indexOf('일일보고')===0}).map(function(k){return hv01.lcs['보고서 기준'][k]}).sort().pop():'확인 안 됨')+' — 이후 조치는 보고서에 아직 안 넘어감','해제 건 보고서 일괄 이관','조치 생명주기 6단계']];
 var tb3=function(a){return hv01T(a)};
 g+='<h3>핵심 현황</h3><div class="grid sc01-key sc01-4">'+
  hvCc(card('장애 상태(경고)',L?'…':nf+'건 진행 중',L?'불러오는 중':'해제 '+(fa.length-faO.length)+' · 경로 아래',null,function(){return '<p class="note">지금 일어난 장애입니다. 진행 중 = 모델통제 이력 「장애」 중 조치 미완료 '+faO.length+'건 + HiClo 판정 멈춤(시스템) 1건. 경로는 아래 「장애 경로」.</p><h4>진행 중</h4>'+tb3(faO)+'<h4>해제됨</h4>'+tb3(fa.filter(done))}),'c-red')+
  hvCc(card('위험 요소(예측)',L?'…':(nr+RISK.length+late.length)+'건',L?'불러오는 중':'경고 '+warn.length+' · 위반 '+viO.length+' · 재발 '+RISK.length,null,function(){return '<p class="note">앞으로 장애로 번질 수 있는 것입니다(예측).</p><h4>HiClo 마지막 판정 「경고」(원천 '+HVR.src+')</h4>'+tbl(['시각','심각도','대상','내용'],warn.map(function(r){return [r[0].slice(5),tag(r[1],'warn'),r[2],r[3]]}))+'<h4>조치가 끝나지 않은 위반</h4>'+tb3(viO)+'<h4>재발·지연 위험</h4>'+tbl(['위험','징후','대응','근거'],RISK)+'<h4>24시간 안 마감·미완료 작업(SC-09)</h4>'+(late.length?tbl(['#','일','담당','마감','진척도'],late.map(function(x){return [hvEsc(x.id),hvEsc(x.title),hvEsc(x.owner),hvEsc(x.due),hvEsc(x.score)+'%']})):'<p class="note">해당 없음</p>')}),'c-org')+
  hvCc(card('자가 검수(예방)',L?'…':se.length+'건 발견',L?'불러오는 중':'미확정 '+(sx['결과 미확정(조치 진행 중)']||0)+' · 이상 '+qaBad.length,null,function(){return '<p class="note">문제가 생기기 전에 막는 점검입니다(예방).</p><h4>예방 검사 결과</h4>'+(QA.length?tbl(['검사','마지막 실행','결과','근거'],QA.map(function(x){return [hvEsc(x[0]),hvEsc(x[1]),tag(hvEsc(x[2]),x[2]==='통과'?'ok':'warn'),hvEsc(x[3])]})):'<p class="note">검사 기록 게시본 없음</p>')+'<h4>지시 추적 교차 검사(산출 '+hvEsc(S?S['산출']:'확인 안 됨')+')</h4>'+tbl(['교차 검사','건수','뜻'],[['종단 일치',sx['일치']||0,'지시 → 기록 → 조치 → 결과가 이어짐'],['종단 결과 미확정',sx['결과 미확정(조치 진행 중)']||0,'조치 진행 중(남은 일)'],['종단 지시만(누락)',sx['지시만(기록 없음)']||0,'지시는 있는데 기록 없음'],['횡단 기록만(누락)',sh['기록만(지시 연결 없음)']||0,'기록은 있는데 지시 연결 없음']])+'<h4>모델이 스스로 찾은 문제</h4>'+tb3(se)}),'c-org')+
  hvCc(card('조치 중(검수)',L?'…':(nM.length+nI.length)+'건',L?'불러오는 중':'미조치 '+nM.length+' · 조치 중 '+nI.length,null,function(){return '<p class="note">아직 끝나지 않은 조치입니다(미조치 포함). 산출 '+hvEsc(hv01.lcs?hv01.lcs['산출']:'확인 안 됨')+'.</p><h4>미조치 '+nM.length+'건</h4>'+tb3(nM)+'<h4>조치 중 '+nI.length+'건</h4>'+tb3(nI)}),'c-yel')+
  hvCc(card('조치 완료(해소)',L?'…':nD.length+'/'+E.length+'건',L?'불러오는 중':'보고서 이관 '+LC.filter(function(x){return x[11]!=='아니오'&&x[11]!=='대기'}).length+' · 확인 '+LC.filter(function(x){return x[12]!=='대기'}).length,null,function(){return '<p class="note">조치 완료(해제) 뒤 보고서 이관·통제(Fable) 확인 단계까지 봅니다.</p>'+tb3(nD)}),'c-grn')+
  '</div><div class="grid sc01-key sc01-6">'+
  hvCc(card('경보',HVR.issues.length+'건','경고 3 · 불명확 1','SC-06'),'c-red2')+
  card('AICS','원천 없음','상태를 기록하는 원천 파일 없음 · '+tag('경고','bad'),'SC-05')+card('HIVEN.app 구동',hvStop(HVR.hiven.last),'신호 '+HVR.hiven.last.slice(5,16),'SC-05')+card('HiClo.app 판정',HVR.hiclo.last.slice(5,16),'「'+HVR.hiclo.verdict+'」 · '+tag('실측','ok'),'SC-05')+card('HiClo.app 구동','확인 안 됨',hvAge().replace(/ \d+분$/,'')+' 갱신 없음','SC-05')+card('모델통제 이력',L?'…':E.length+'건',(function(){var d=E.map(function(e){return e.date}).sort();return d.length?d[0].slice(5)+' ~ '+d[d.length-1].slice(5)+' 누적':'-'})(),'SC-15').replace('class="card cbtn','class="card cbtn sky')+
  '</div>';
 /* 18:08 대표님: 조치 생명주기·장애 경로는 가장 많이 보는 부분 → 상자 바로 밑 */
 var ST=['1 감지','2 경고·알람','3 조치 착수','4 조치 중','5 해제','6 보고서 이관','7 통제 확인'],SN=ST.map(function(x,i){return LC.filter(function(r){return r[6+i]!=='아니오'&&r[6+i]!=='대기'}).length});
 g+='<h3>조치 생명주기(백오피스 흐름)</h3><ol class="sc01-flow sc01-lc">'+ST.map(function(x,i){return '<li><b>'+x.slice(2)+'</b> '+(L?'…':SN[i])+'</li>'}).join('')+'</ol><p class="note">감지(이력 기록) → 경고·알람(대시보드 표출) → 조치 착수 → 조치 중 → 해제(조치 완료) → 보고서 이관(일일보고·검수대기열·별도지시대장에 이력 번호 기재) → 통제 확인(Fable 「체크」·자동화 통합 통제 시스템). 숫자 = 그 단계까지 온 건수. 보고서 기준 '+hvEsc(hv01.lcs?JSON.stringify(hv01.lcs['보고서 기준']).replace(/[{}"]/g,'').replace(/,/g,' · '):'확인 안 됨')+'.</p>';
 g+='<h3>장애 경로(심각도 순)</h3>'+HV_PATH.map(function(x,i){return '<div class="sc01-path"><div class="sc01-ph"><span class="tag '+(i?'warn':'bad')+'">'+(i+1)+'순위</span><b>'+hvEsc(x.t)+'</b><span class="tag warn">'+hvEsc(x.st)+'</span></div><ol class="sc01-flow">'+x.p.map(function(s){return '<li>'+hvEsc(s)+'</li>'}).join('')+'</ol><div class="sc01-r"><b>조치 결과</b> '+hvEsc(x.r)+'</div><div class="note">근거: '+hvEsc(x.ref)+'</div></div>'}).join('');
 /* 17:49·17:50·17:52 대표님: 상자 1~10 순서대로 아래에 표(같은 표 기준 5줄·쪽 넘김). 데이터가 아직 연동되지 않은 표도 미리 구성해 두고 「연동 전」으로 자리 확보 */
 var NC='<span class="tag gray">연동 전</span>';
 var T10=function(n,t,h,rows,src){return '<div class="sc01-tb'+(n===11?' sky':'')+'">'+(t==='모델통제 이력'?'<h3 role="link" tabindex="0" title="SC-15 구분별 변동 추이 그래프로 이동" onclick="hvgoHist()" onkeydown="if(event.key===\'Enter\')hvgoHist()" style="cursor:pointer">'+t+'</h3>':'<h3>'+(n===11?'':'#'+n+'. ')+t+'</h3>')+''+tbl(h,rows.length?rows:[h.map(function(x,i){return i?(i===1?'데이터 연동 전 — 연동되면 여기에 표출':''):NC})])+'<p class="note">'+src+'</p></div>'};
 var rv=function(a){return a.slice().reverse()},cls=function(e){return lcM[e.no]?lcM[e.no][5]:(done(e)?'조치 완료':'조치 중')},stg=function(e){return lcM[e.no]?lcM[e.no][13]:'-'};
 var ER=function(e){return [hvEsc(e.no),hvEsc(e.time),tag(hvEsc(e.status),done(e)?'ok':'warn'),hvEsc(e.content),hvEsc(e.action)]};
 g+=(L?'':hvTG01(E,cls));/* W28-03 A-01 */
 g+='<h3 class="sc01-tbh">상자별 표(#1~#10 상자 순서 + 모델통제 이력)</h3>';
 g+=T10(1,'장애 상태(경고)',['#','시각','상태','내용','조치'],L?[]:[['시스템','11-03 20:54',tag('조치 진행 중','warn'),'HiClo 판정 멈춤 — 구동 상태 확인 불가','자동화 동결·원본 실측만 표시, 재가동 결정 대기']].concat(rv(faO).map(ER),rv(fa.filter(done)).map(ER)),'진행 중 먼저, 그다음 해제 · 원천 모델통제 이력 게시본 + HVR');
 g+=T10(2,'위험 요소(예측)',['구분','위험','징후·내용','대응','근거'],L?[]:warn.map(function(r){return ['경보','HiClo '+hvEsc(r[2]),hvEsc(r[3]),'재가동 결정 전까지 「확인 안 됨」','판정 '+r[0].slice(5)]}).concat(rv(viO).map(function(e){return ['위반','#'+hvEsc(e.no),hvEsc(e.content),hvEsc(e.action),'이력 '+hvEsc(e.no)]}),RISK.map(function(x){return ['재발·지연',hvEsc(x[0]),hvEsc(x[1]),hvEsc(x[2]),hvEsc(x[3])]}),late.map(function(x){return ['마감 임박',hvEsc(x.id),hvEsc(x.title)+' '+hvEsc(x.score)+'%','마감 '+hvEsc(x.due),'SC-09']})),'경보 → 미조치 위반 → 재발·지연 → 24시간 안 마감');
 g+=T10(3,'자가 검수(예방)',['구분','검사·항목','결과','근거·조치','시각'],L?[]:QA.map(function(x){return ['예방 검사',hvEsc(x[0]),tag(hvEsc(x[2]),x[2]==='통과'?'ok':'warn'),hvEsc(x[3]),hvEsc(x[1])]}).concat(S?[['교차 검사','지시 추적 종단·횡단',(sx['결과 미확정(조치 진행 중)']||0)+'건 미확정 · 누락 '+((sx['지시만(기록 없음)']||0)+(sh['기록만(지시 연결 없음)']||0)),'일치 '+(sx['일치']||0)+' · 횡단 일치 '+(sh['일치']||0),hvEsc(S['산출'])]]:[],rv(se).map(function(e){return ['자가 발견','#'+hvEsc(e.no)+' '+hvEsc(e.content),tag(hvEsc(e.status),done(e)?'ok':'warn'),hvEsc(e.action),hvEsc(e.time)]})),'원천 qa_checks.tsv · trace_sum.json · 모델통제 이력');
 g+=T10(4,'조치 중(검수)',['#','3분류','현재 단계','내용','조치'],L?[]:rv(nM).concat(rv(nI)).map(function(e){var c=cls(e);return [hvEsc(e.no),tag(c,c==='조치 완료'?'ok':c==='미조치'?'bad':'warn'),hvEsc(stg(e)),hvEsc(e.content),hvEsc(e.action)]}),'미조치 → 조치 중 순 · 원천 action_lifecycle.tsv');
 g+=T10(5,'조치 완료(해소)',['#','3분류','현재 단계','내용','조치'],L?[]:rv(nD).map(function(e){var c=cls(e);return [hvEsc(e.no),tag(c,c==='조치 완료'?'ok':c==='미조치'?'bad':'warn'),hvEsc(stg(e)),hvEsc(e.content),hvEsc(e.action)]}),'해제 최신순 · 현재 단계 = 해제 / 보고서 이관 / 통제 확인 · 원천 action_lifecycle.tsv');
 g+=T10(6,'경보',['시각','심각도','대상','내용'],HVR.issues.map(function(r){return [r[0].slice(5),tag(r[1],r[1]==='경고'?'warn':'gray'),r[2],r[3]]}),'원천 '+HVR.src+' · 확인 '+HVR.chk);
 g+=T10(7,'AICS',['항목','값','원천'],HV_KV['AICS'](),'정지·재개 상태 원천이 생기면 여기에 표출');
 g+=T10(8,'HIVEN.app 구동',['항목','값','원천'],HV_KV['HIVEN.app 지금 구동'](),'구동 신호 원천 연동 시 표출');
 g+=T10(9,'HiClo.app 판정',['항목','값','원천'],HV_KV['HiClo.app 마지막 판정'](),'원천 '+HVR.src);
 g+=T10(10,'HiClo.app 구동',['항목','값','원천'],HV_KV['HiClo.app 지금 구동'](),'판정 파일이 다시 갱신되면 「구동」으로 바뀜');
 g+=T10(11,'모델통제 이력',['#','시각','모델','구분','내용','상태'],L?[]:rv(E).map(function(e){return [hvEsc(e.no),hvEsc(e.time),hvEsc(e.model),hvEsc(e.type),hvEsc(e.content),tag(hvEsc(e.status),done(e)?'ok':'warn')]}),'최신순 · 상세·필터는 SC-15');
 g+=hvMcs01(E.length)+hvSum4()+hvMismatch(E.length,LC.length);
 return g+'<p class="note">핵심 4가지는 모델통제 이력 게시본을 읽은 값입니다(읽은 시각 '+hvEsc(hv01.ok||'불러오는 중')+'). 장애 경로는 기록·문서로 확인한 사실만 적었습니다.</p>'+hvChk()+'</div>'};
V['SC-04']=function(){
 var g='<h2>SC-04 사업군 통제</h2><p class="lead">7개 사업군 × 조치 생명주기 7단계 건수를 원천 ctl/bg_lifecycle.tsv로 봅니다(0건도 실측값).</p>';
 g+=hvBg7();
 g+=hvContact();
 g+='<h3>통제 접점(고정 정의)</h3>'+tbl(['번호','사업군','역할','통제 접점'],BG.map(function(b){return [b[0],'<b>'+b[1]+'</b>',b[2],b[3]]}));
 return g+hvChk()};
V['SC-05']=function(){
 var g='<h2>SC-05 구동 상태</h2><p class="lead">HiClo.app·HIVEN.app·AICS가 노트북에서 실제로 구동되는지, 원천 파일로 확인한 값만 봅니다.</p>';
 g+='<div class="grid">'+card('HiClo.app 지금 구동',hvStop(HVR.hiclo.last),'마지막 판정 '+HVR.hiclo.last.slice(5,16)+' · '+tag('실측','ok'))+card('HIVEN.app 지금 구동','확인 안 됨','마지막 관계 신호 '+HVR.hiven.last.slice(5,16))+card('AICS','확인 안 됨','정지·재개 상태 원천 확인 안 됨')+'</div>';
 g+='<p class="note">아래 값은 모두 '+HVR.chk+'에 노트북 원천을 확인한 값입니다('+hvChkAge()+'). 그 뒤로 원천이 멈춰 있습니다(정지 경고).</p><h3>저장 주기(설정 파일 값 · '+HVR.chk.slice(5)+' 확인)</h3>'+tbl(['구분','값','원천'],[['설정',HVR.save.period+'분 ('+HVR.save.setAt+' 설정)',HVR.save.src],['예약',HVR.save.sched,'같은 파일'],['실제 적용 여부',hvNo(),'적용 기록 확인 안 됨']]);
 g+='<h3>작업 대기열(마지막 결과 · '+HVR.chk.slice(5)+' 확인)</h3>'+tbl(['작업','끝난 시각','결과','원천'],[[HVR.job.id,HVR.job.end,'종료 코드 '+HVR.job.rc+' '+tag('실측','ok'),HVR.job.src]]);
 return g+hvChk()};
V['SC-16']=function(){return hvSc04()+'<input id="cin" type="hidden"><span id="cres" hidden></span>'};
V['SC-14']=hvTestOnly('SC-14','문서 자동 생성');
V['SC-07']=function(){return '<h2>SC-07 체계 배포</h2><div class="grid">'+card('원본 대시보드','실측 데이터 없음','연동 단계 D2',null,function(){return '<p class="note">분류 체계·규칙 문서 배포 현황(문서·버전·배포 시각·적용 폴더 수·불일치 수)은 D2(12월)에 원천 ctl/deploy.tsv를 만든 뒤 표출합니다(AICS 재설계안 2.0 6-2). 시험 화면은 <a href="test/#SC-07">시험 페이지</a>.</p>'})+'</div>'+hvChk()};
V['SC-13']=hvTestOnly('SC-13','고객 지원');
V['SC-10']=function(){
 var g='<h2>SC-10 수집·연동</h2><p class="lead">원천별 마지막 수신 시각을 원천 파일로 확인한 값만 봅니다.</p>';
 g+=tbl(['원천','마지막 수신','상태','확인'],[
  ['노트북 HiClo 판정 파일',HVR.hiclo.last,tag('끊김','bad')+' '+hvAge()+' 갱신 없음','실측('+HVR.chk.slice(5)+' 확인)'],
  ['HIVEN.app 관계 신호',HVR.hiven.last,hvNo(),'HiClo 판정 파일 기준'],
  ['작업 대기열 결과',HVR.job.end,tag('끊김','bad')+' 이후 결과 없음','실측('+HVR.chk.slice(5)+' 확인)'],
  ['모델 통제 이력(SC-15)','게시본',tag('정상','ok')+' 10초마다 읽음','실측'],
  ['통합사업 작업상황(SC-09)','게시본',tag('정상','ok')+' 30초마다 읽음','실측'],
  ['HiCoffer Cloud 묶음(IF-4 · IF-5)',hvNo(),hvNo()+' 수신 경로 구현 전','자리만 — 추적 열쇠값(TRC) 11칸 자료 형식 확정 전']]);
 g+='<p class="note">위 표의 노트북 원천 세 줄(HiClo 판정 · HIVEN.app 신호 · 작업 대기열)은 '+HVR.chk+' 확인값입니다('+hvChkAge()+'). 「HiCoffer Cloud 묶음」은 통합 서비스 구조 설계안의 IF-4(HiCoffer ↔ Cloud)·IF-5(Cloud ↔ 통합관제) 수신 자리이며 값은 원천이 생기면 채웁니다.</p>';
 g+=hvMetaTbl();
 return g+hvChk()};
V['SC-12']=hvTestOnly('SC-12','검수·품질');
V['SC-06']=function(){
 var g='<h2>SC-06 대응·경보</h2><p class="lead">HiClo 마지막 판정 기준 경보와 클로 단계만 봅니다.</p>';
 g+='<div class="grid">'+card('클로 단계',HVR.hiclo.stage,'판정 '+HVR.hiclo.last.slice(5,16)+' · 옛 값')+card('지금 단계',hvStop(HVR.hiclo.last),hvAge()+' 갱신 없음 · '+tag('불명확','gray'))+card('대응 모드',"확인 안 됨",'원천 확인 안 됨')+'</div>';
 g+=hvAlertLedger();
 g+='<h3>경보 — 2026-11-03 판정값(옛 값)</h3>'+tbl(['시각','심각도','대상','내용'],HVR.issues.map(function(r){return [r[0].slice(5),tag(r[1],r[1]==='경고'?'warn':'gray'),r[2],r[3]]}))+'<p class="note">이 네 줄은 2026-11-03 20:54 HiClo 판정 파일의 값을 '+HVR.chk+'에 확인해 코드에 적어 둔 옛 값입니다(지금 값 아님 · '+hvAge()+' 갱신 없음). 새 경보는 위 경보 원장에 쌓입니다.</p>';
 return g+hvChk()};
/* 261111 M-1: 경보 원장(cowork/ctl/alerts.tsv). 통제 규칙 CR-01~10 경보가 실릴 자리. 머리글만 있고 자료 0줄이면 「0건」이 아니라 「원천 연결 전」으로 보인다 */
function hvAlertLedger(){var h='<h3>경보 원장(실측 원천에서 모델 호출 때마다 갱신)</h3>';
 if(!hvMeta.t)return h+'<p class="note">불러오는 중</p>';if(!hvMeta.al)return h+hvNo('원천 ctl/alerts.tsv 없음');
 var H=hvMeta.al.h,R=hvMeta.al.r.slice().reverse();
 return h+(R.length?tbl(H,R.map(function(r){return r.map(hvEsc)})):tbl(H,[H.map(function(x,i){return i===0?tag('확인 안 됨','gray'):i===1?'경보를 만드는 원천 연결 전 — 연결되면 여기에 최신순으로 표출':''})]))
 +'<p class="note">원천 cowork/ctl/alerts.tsv · '+R.length+'줄. 열은 초안입니다(추적 열쇠값 TRC 11칸 자료 형식 확정 전). 경보 조건 값(실패율·횟수·배수)은 「확인 안 됨(베타 2차 실측으로 정함)」이며 시뮬레이션에 쓴 가정값은 <a href="test/sim.html">시험 페이지</a>에만 둡니다.</p>'}
V['SC-11']=hvTestOnly('SC-11','형상·변경');
/* 머리띠(상단 칩): 원본은 실측만 — 대응 모드는 원천 없음, 데이터 신선도는 HiClo 마지막 판정 기준, 갱신은 원천 확인 시각 */
function hvHdr(){try{var c=document.getElementById('chip-mode');if(c)var hh=Math.floor((Date.now()-HVST)/3600000);c.innerHTML='<span class="dot" style="background:#d32f2f"></span>대응 모드 <b>판정 정지 '+(hh>=24?Math.floor(hh/24)+'일 ':'')+(hh%24)+'시간</b>';c.title='노트북 HiClo 판정 원천이 '+new Date(HVST).toLocaleString('ko-KR')+' 뒤 멈춤 — 결재 A-002';var f=document.getElementById('ftxt');if(f)f.textContent='판정 '+Math.floor((Date.now()-HVST)/3600000)+'시간 끊김';f.parentNode.title='데이터 신선도: 노트북 HiClo 판정 파일 마지막 갱신 뒤 지난 시간(실측)';var u=document.getElementById('upd');if(u)u.textContent=(hvMeta.m?'게시 '+hvMeta.m.published:HVR.chk+' (원천 확인)')}catch(e){}}
function hvWrap(){var o=render;render=function(id){o(id);hvHdr()};hvHdr();setInterval(hvHdr,5000)}

/* 상자별 근거 데이터(원본 실측) — 이름이 같은 상자는 어느 화면에서든 같은 근거를 보인다 */
function hvKV(rows){return tbl(['항목','값','원천'],rows)}
HV_KV['HiClo.app 마지막 판정']=function(){return ([['판정 시각',HVR.hiclo.last,HVR.src],['판정',HVR.hiclo.verdict,'같은 파일'],['관측 끊김',HVR.hiclo.miss+'회 연속','같은 파일'],['클로 단계',HVR.hiclo.stage,'같은 파일'],['그 뒤 경과',hvAge()+' 갱신 없음','확인 시각 '+HVR.chk]])}
HV_KV['HiClo.app 지금 구동']=function(){return ([['버전',HVR.hiclo.ver,HVR.src],['마지막 판정',HVR.hiclo.last+' 「'+HVR.hiclo.verdict+'」','같은 파일'],['판정 주기','5분 순환(정상이면 5분마다 갱신)','설계'],['그 뒤 경과',hvAge()+' 갱신 없음','확인 시각 '+HVR.chk],['판단','지금 구동 여부 확인 안 됨 — 판정 파일이 멈춤','—'],['참고','HiClo 예약작업은 11/03 20:56 비활성(AICS 처리정책 11/04 승인)','91_Fable\\AICS_자동화_처리정책_261104.md']])}
HV_KV['HIVEN.app 지금 구동']=function(){return ([['마지막 관계 신호',HVR.hiven.last,HVR.src],['설명',HVR.hiven.note,'같은 파일'],['판단','지금 구동 여부 확인 안 됨','별도 프로세스 기록 없음']])}
HV_KV['AICS']=function(){return ([['정지·재개 상태','원천 없음','상태를 기록하는 원천 파일 없음 — 경고'],['처리 정책','삭제 없이 비활성·격리, 「실측」 표시는 실제 연동 때만(11/04 10:53 승인)','91_Fable\\AICS_자동화_처리정책_261104.md'],['과거 화면','11/02 08:04 스냅샷 값을 「구동 중」으로 표시했던 것은 거짓 표시(모델통제 이력 2번)','SC-15']])}
HV_CDET['경보(마지막 판정 기준)']=function(){return tbl(['시각','심각도','대상','내용'],HVR.issues.map(function(r){return [r[0].slice(5),tag(r[1],r[1]==='경고'?'warn':'gray'),r[2],r[3]]}))+'<p class="note">원천 '+HVR.src+' · 확인 '+HVR.chk+'</p>'}
HV_CDET['모델 통제 이력']=function(){return '<p class="note">원천 HiBiz\\01_클로_소통(COM)\\모델통제(CTL)\\모델통제_통합이력.tsv → 게시 /cowork/ctl/model_control_history.tsv. 위반·지적·질타·조치 진행 중 등 상자별 목록과 지시 추적 교차 검사는 SC-15에서 봅니다.</p>'}
HV_KV['클로 단계']=function(){return ([['단계',HVR.hiclo.stage,HVR.src],['판정 시각',HVR.hiclo.last,'같은 파일'],['판정',HVR.hiclo.verdict+' · 관측 끊김 '+HVR.hiclo.miss+'회','같은 파일']])}
HV_KV['지금 단계']=function(){return ([['지금 단계',hvStop(HVR.hiclo.last),'판정 파일이 '+hvAge()+' 갱신 없음 — 경고'],['마지막으로 확인된 단계',HVR.hiclo.stage+' ('+HVR.hiclo.last+')',HVR.src]])}
HV_KV['대응 모드']=function(){return ([['대응 모드','원천 없음','대응 모드를 기록한 원천 파일 없음 — 경고'],['확인',HVR.chk+' · '+HVR.by,'—']])}

/* SC-01 줄인 이름(한 줄 규칙 25번)도 같은 근거를 보임 */

;['HiClo.app 마지막 판정','HiClo.app 지금 구동','HIVEN.app 지금 구동','AICS','클로 단계','지금 단계','대응 모드'].forEach(function(k){HV_CDET[k]=function(){return hvKV(HV_KV[k]())}});
HV_CDET['경보']=HV_CDET['경보(마지막 판정 기준)'];HV_CDET['HIVEN.app 구동']=HV_CDET['HIVEN.app 지금 구동'];HV_CDET['HiClo.app 구동']=HV_CDET['HiClo.app 지금 구동'];HV_CDET['모델통제 이력']=HV_CDET['모델 통제 이력'];
HV_CDET['HiClo.app 판정']=function(){return hvKV(HV_KV['HiClo.app 마지막 판정']())};

/* 18:16 상자 색 계열(성격 구별) */
function hvCc(h,c){return h.replace('class="card cbtn','class="card cbtn '+c)}

/* W19-3(AICS 재설계안 2.0) — 게시 메타·사업군 7단계·지시 추적 표출. 모델이 푸시한 게시본을 읽기만 한다(자동 실행 장치 아님). */
var hvMeta={m:null,bg:null,tv:null,t:0};
function hvMetaLoad(){Promise.all([hvFetch('cowork/publish_meta.json','json').catch(function(){return null}),hvFetch('cowork/ctl/bg_lifecycle.tsv','text').catch(function(){return null}),hvFetch('cowork/ctl/trace_v.tsv','text').catch(function(){return null}),hvFetch('cowork/ctl/bg_contact.tsv','text').catch(function(){return null}),hvFetch('cowork/ctl/bg_source.tsv','text').catch(function(){return null}),hvFetch('cowork/ctl/alerts.tsv','text').catch(function(){return null})]).then(function(r){hvMeta.al=r[5]===null?null:(function(t){var L=String(t).replace(/\r/g,'').split('\n').filter(function(x){return x.length});return {h:L[0]?L[0].split('\t'):[],r:L.slice(1).map(function(x){return x.split('\t')})}})(r[5]);hvMeta.m=r[0];hvMeta.bg=r[1]===null?null:hvTsv(r[1]);hvMeta.tv=r[2]===null?null:hvTsv(r[2]);hvMeta.ct=r[3]===null?null:hvTsv(r[3]);hvMeta.src=r[4]===null?null:hvTsv(r[4]);hvMeta.t=Date.now();if(['SC-01','SC-04','SC-16','SC-10','SC-06'].indexOf(cur)>=0&&!hvMeta._r){hvMeta._r=1;render(cur)}else if(['SC-01','SC-04','SC-16','SC-10'].indexOf(cur)>=0)render(cur);hvHdr()},function(){})}
/* T-W19-04 접점표(Opus 워크 0006): 사업부 설정안 6장 연동표 TSV 5권 → ctl/bg_contact.tsv · 결정 묶음 B-1(대표님 승인 11/05 03:54) — 심각도 상=경고 상자 즉시, 중·하=목록, 해제=조치 완료+Fable 처리 완료 */
function hvContact(){
 if(!hvMeta.t)return '';
 var g='<h3>접점 판정 기준(결정 B-1 확정)</h3>'+tbl(['항목','확정값'],[['7단계','감지 → 경고·알람 → 조치 착수 → 조치 중 → 해제 → 보고서 이관 → 통제 확인(원천 ctl/bg_lifecycle.tsv 1파일)'],['심각도','<b>상</b>(경보 기준에 「즉시」) = 경고 상자 즉시 반영 · <b>중</b>(「경고」)·<b>하</b> = 목록'],['해제','조치 완료 + Fable 확인 「처리 완료」일 때만']]);
 if(hvMeta.src===null)g+='<h3>사업군별 감지 원천·경고 기준</h3>'+hvNo('원천 ctl/bg_source.tsv 없음');
 else g+='<h3>사업군별 감지 원천·경고 기준</h3>'+tbl(['사업군','감지 원천','경고 기준','연동 접점'],hvMeta.src.map(function(x){return ['<b>'+hvEsc(x[0])+'</b>',hvEsc(x[1]),hvEsc(x[2]),hvEsc(x[3])+'건']}));
 if(hvMeta.ct===null)return g+'<h3>사업군 연동 접점표</h3>'+hvNo('원천 ctl/bg_contact.tsv 없음');
 var C=hvMeta.ct,hi=C.filter(function(x){return x[9]==='상'}).length;
 g+='<h3>사업군 연동 접점표 · '+C.length+'건(상 '+hi+' · 중 '+(C.length-hi)+')</h3>'+tbl(['번호','사업부','AICS 접점','감지 신호','경보 기준','심각도'],C.map(function(x){return ['<span style="white-space:nowrap">'+hvEsc(x[0])+'</span>','<b>'+hvEsc(x[2])+'</b> → '+hvEsc(x[3]),hvEsc(x[6]),hvEsc(x[7]),hvEsc(x[8]),tag(x[9],x[9]==='상'?'bad':'warn')]}));
 return g+'<p class="note">원천 사업부 설정안 6장 연동표 TSV 5권(HiASI 2.0·HiDAM 1.0·HiICT 2.0·HiServe 1.0·HiTrade 1.0) → ctl/bg_contact.tsv · 실제 감지 건은 ctl/bg_lifecycle.tsv(위 7×7)에 기록됩니다.</p><p class="note">보안체계 연계 접점 11건(S-01~S-11)은 위 30건과 별도이며 <a href="#" onclick="hvgo(\'SC-02\');return false">SC-02 「편입·연계 서비스 플로어」</a>에 있습니다.</p>'}
function hvBg7(){var S=['감지','경고·알람','조치 착수','조치 중','해제','보고서 이관','통제 확인'];
 if(!hvMeta.t)return '<p class="note">불러오는 중</p>';if(hvMeta.bg===null)return tbl(['사업군','상태'],BG.map(function(b){return [b[1],hvNo('원천 ctl/bg_lifecycle.tsv 없음')]}));
 var rows=BG.map(function(b){var mine=hvMeta.bg.filter(function(x){return x[1]===b[1]});var c=[mine.length,mine.filter(function(x){return x[6]}).length,mine.filter(function(x){return x[7]}).length,mine.filter(function(x){return x[9]==='조치 중'}).length,mine.filter(function(x){return x[10]}).length,mine.filter(function(x){return x[12]}).length,mine.filter(function(x){return x[13]&&x[13]!=='대기'}).length];return ['<b>'+b[1]+'</b>'].concat(c)});
 return tbl(['사업군'].concat(S),rows)+'<p class="note">원천 ctl/bg_lifecycle.tsv · 게시 '+hvEsc(hvMeta.m?hvMeta.m.published:'확인 안 됨')+' · 실제 건은 사업부 설정안 6장(AICS 접점) 확정 뒤 기록됩니다.</p>'}
function hvSc04(){var g='<h2>SC-16 말 명령</h2><p class="lead">대표님 지시(음성·글)가 해석되어 별도지시대장·모델통제 이력에 빠짐없이 들어갔는지 봅니다. 원본은 표출만 하고 명령 입력·실행은 하지 않습니다(입력은 <a href="test/#SC-16">시험 페이지</a>).</p>';
 if(!hvMeta.t)return g+'<p class="note">불러오는 중</p>';if(!hvMeta.tv)return g+hvNo('원천 ctl/trace_v.tsv 없음')+hvChk();
 return g+'<div id="cmd-top">'+hvSc04Tbl()+'</div>'+hvChk()}
/* 11-12 14:15 대표님 질타(이력 840): 맨 위 표가 11-05(S122)에서 멈춤 → trace_v.tsv(11-04~11-05 추적 매트릭스) 위에 그 뒤의 대표님 말씀을 이력·지시대장에서 실시간으로 이어 붙인다 */
function hvSc04Tbl(){var CUT='2026-11-12';/* 데이터 보존 규칙(이력 875): 화면은 현행(11-12 새 체계 이후)만, 이전은 보존 영역(접힘) */var OLD=hvMeta.tv.filter(function(x){return String(x[1]||'')<CUT}),R=hvMeta.tv.filter(function(x){return String(x[1]||'')>=CUT}).slice().reverse().map(function(x){return [hvEsc(x[0]),hvEsc((x[1]||'').slice(5)+' '+(x[2]||'')),hvEsc(x[3]),hvEsc(x[4]),hvEsc(x[5]||x[6]||'—'),hvEsc(x[12]||'')]});
 var live=[],c=window.hvCmdLive;if(c&&c.H){var L={};(c.L||[]).forEach(function(x){L[x[0]]=1});var last=0;hvMeta.tv.forEach(function(x){String(x[6]||'').replace(/#(\d+)/g,function(m,n){if(+n>last)last=+n})});
  live=c.H.filter(function(x){return /^\d+$/.test(x[0])&&+x[0]>last&&/^대표님/.test(x[6]||'')}).reverse().map(function(x){return ['#'+hvEsc(x[0]),hvEsc((x[1]||'').slice(5)+' '+String(x[3]||'').replace(/^\d+\/\d+ /,'')),hvEsc(x[6]),hvEsc(x[5]),L[x[0]]?'지시대장 #'+hvEsc(x[0]):'이력 #'+hvEsc(x[0]),L[x[0]]?'일치':tag('대장 없음','warn')]})}
 return tbl(['순번','시각','지시 요지','구분','등록 위치','교차 판정'],live.concat(R))+'<p class="note">현행 '+(live.length+R.length)+'건(원천 command_ledger.tsv · trace_v.tsv · 이력, 1초 갱신)</p><details style="margin:6px 0"><summary class="note" style="cursor:pointer">보존 기록 '+OLD.length+'건(11-11 이전, 데이터 보존 규칙 — 현행 아님)</summary>'+tbl(['순번','시각','지시 요지','구분','등록 위치'],OLD.slice().reverse().map(function(x){return [hvEsc(x[0]),hvEsc((x[1]||'').slice(5)+' '+(x[2]||'')),hvEsc(x[3]),hvEsc(x[4]),hvEsc(x[5]||x[6]||'—')]}))+'</details>'}
function hvMetaTbl(){if(!hvMeta.m)return '<h3>게시 원천</h3>'+hvNo('publish_meta.json 없음');
 return '<h3>게시 원천(파일별)</h3>'+tbl(['파일','노트북 원천','화면','건수','게시 파일 시각'],hvMeta.m.files.map(function(f){return [hvEsc(f.file),hvEsc(f.source),hvEsc(f.screen),f.rows===null?'—':f.rows,hvEsc(f.mtime)]}))+'<p class="note">게시 '+hvEsc(hvMeta.m.published)+' · '+hvEsc(hvMeta.m.by)+' · 이력 '+hvMeta.m.history_rows+'건 / 생명주기 '+hvMeta.m.lifecycle_rows+'건</p>'}
function hvMismatch(h,l){var m=hvMeta.m;var bad=(m&&m.consistent===false)||(h&&l&&h!==l);return bad?'<p class="note" style="color:#c62828;font-weight:700">원천 불일치 · 재산출 필요 — 이력 '+h+'건 / 생명주기 '+l+'건</p>':''}
function hvSum4(){var m=hvMeta.m;return '<h3>요약(설계서 1.18 구성)</h3>'+tbl(['구분','상태','원천'],[['고객 지원 요약',tag('D2','gray')+' 사례 원천 구축 전','cases.tsv(12월)'],['자동화 작업 요약','마지막 결과 '+HVR.job.id+' · '+HVR.job.end.slice(5,16)+' · 종료 코드 '+HVR.job.rc,HVR.job.src],['L3 사안',tag('D2','gray')+' 원천 없음','—'],['데이터 수신 상태',m?('게시 '+hvEsc(m.published)+' · 원천 파일 '+m.files.length+'개'):hvNo(),'publish_meta.json']])}
hvMetaLoad();setInterval(hvMetaLoad,30000);
/* W28-03 A-03(Opus 11/05): 원본 13화면 모두 같은 안내(hvChk) — SC-09·SC-15에 빠져 있던 것 보충(시험 페이지는 views0을 읽지 않으므로 영향 없음) */
(function(){['SC-09','SC-15'].forEach(function(id){var f=V[id];if(f&&!f._chk){V[id]=function(){return f.apply(this,arguments)+hvChk()};V[id]._chk=1}})})();
