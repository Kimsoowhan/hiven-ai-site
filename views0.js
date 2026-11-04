/* 원본 대시보드 = 실측 데이터만 (대표님 지시 11/04 15:53·15:56). 노트북 원천 파일을 모델이 직접 열어 확인한 값만 확인 시각과 함께 싣는다.
   시험·샘플·확인 안 된 값은 원본에 싣지 않는다 → 같은 구성의 시험 페이지 /test/ 에서만 보인다.
   이 파일은 자동 연동이 아니다(금지 4조항: 자동 동기화 금지). 모델이 원천을 다시 확인할 때마다 HVR 값을 고치고 확인 시각을 바꾼다. */
var HVR={
 chk:'2026-11-04 15:56',by:'Opus 5.5',
 src:'HiBiz\\00_클로_기억장치(EMG)\\09_HiClo_앱(APP)\\HiClo_기억상태-261103.json',
 hiclo:{ver:'HiClo.app 3.1.2',last:'2026-11-03 20:54:58',verdict:'경고',miss:258,stage:'혼미(3단계)'},
 hiven:{last:'2026-11-03 03:55:13',note:'HiClo 판정 파일의 HIVEN 관계 신호 시각(HIVEN 단계 「확인 못 함」)'},
 job:{id:'JOB-S0175c',end:'2026-11-03 03:55:13',rc:0,src:'10_작업대기열(JOB)\\02_나감(OUT)\\JOB-S0175c-261102-결과.json'},
 save:{period:60,setAt:'2026-11-02 07:52',sched:'2026-11-03 18:00부터 30분',src:'09_HiClo_앱(APP)\\저장주기.json'},
 issues:[
  ['2026-11-03 20:54:58','경고','HiClo','관측 끊김 258회 연속(지시원장 확인 못 함)'],
  ['2026-11-03 20:54:58','경고','클로','혼미(3단계)'],
  ['2026-11-03 20:54:58','경고','작업기억','GBP_작업기억·단기기억_스냅샷·할일큐 11/02 10:59:48 뒤 갱신 없음'],
  ['2026-11-03 20:54:58','확인 못 함','노드','노드생존·기억회복상태·단기기억기록 확인 못 함']]
};
function hvNo(t){return tag('확인 안 됨','gray')+(t?' '+t:'')}
function hvChk(){return '<p class="note">원본 대시보드는 <b>실측 데이터만</b> 보입니다. 확인 시각 '+HVR.chk+' · 확인 '+HVR.by+' · 원천 '+HVR.src+'. 확인되지 않은 값은 「확인 안 됨」으로 표시하고, 시험·샘플 값은 <a href="test/">시험 페이지</a>에서만 봅니다.</p>'}
function hvTestOnly(id,name){return function(){return '<h2>'+id+' '+name+'</h2><div class="card"><div class="k">원본 대시보드</div><div class="v" style="font-size:19px">실측 데이터 없음</div><div class="s">이 화면은 아직 시험 중이거나 시험·샘플 값으로 되어 있어 원본에 싣지 않습니다(대표님 지시 11/04 15:56). 시험 화면: <a href="test/#'+id+'">시험 페이지</a></div></div>'+hvChk()}}
var HVST=Date.parse(HVR.hiclo.last.replace(' ','T')+'+09:00');
function hvAge(){var m=Math.round((Date.now()-HVST)/60000);return m<60?m+'분':Math.floor(m/60)+'시간 '+(m%60)+'분'}

V['SC-01']=function(){
 var g='<h2>SC-01 종합 현황</h2><p class="lead">노트북 원천에서 확인한 구동 상태와 경보만 봅니다.</p>';
 g+='<div class="grid">'+
  card('HiClo.app 마지막 판정',HVR.hiclo.last.slice(5,16),'판정 「'+HVR.hiclo.verdict+'」 · 그 뒤 '+hvAge()+' 갱신 없음 · '+tag('실측','ok'),'SC-03')+
  card('HiClo.app 지금 구동','확인 안 됨','판정 파일이 '+hvAge()+' 동안 갱신되지 않음 · '+tag('확인 안 됨','gray'),'SC-03')+
  card('HIVEN.app 지금 구동','확인 안 됨','마지막 관계 신호 '+HVR.hiven.last.slice(5,16)+' · '+tag('확인 안 됨','gray'),'SC-03')+
  card('AICS','확인 안 됨','정지·재개 상태 원천 확인 안 됨 · '+tag('확인 안 됨','gray'),'SC-03')+
  card('경보(마지막 판정 기준)',HVR.issues.length+'건','경고 3 · 확인 못 함 1 · '+tag('실측','ok'),'SC-10')+
  card('모델 통제 이력','SC-13','게시본 10초마다 읽음 · '+tag('실측','ok'),'SC-13')+'</div>';
 g+='<h3>경보(HiClo 마지막 판정 '+HVR.hiclo.last+')</h3>'+tbl(['시각','심각도','대상','내용'],HVR.issues.map(function(r){return [r[0].slice(5),tag(r[1],r[1]==='경고'?'warn':'gray'),r[2],r[3]]}));
 return g+hvChk()};
V['SC-02']=function(){
 var g='<h2>SC-02 사업군 통제</h2><p class="lead">7개 사업군 번호·이름·통제 접점(고정 정의)만 봅니다. 사업군별 운영 상태는 실측 원천이 없어 싣지 않습니다.</p>';
 g+=tbl(['번호','사업군','역할','통제 접점','운영 상태'],BG.map(function(b){return [b[0],'<b>'+b[1]+'</b>',b[2],b[3],hvNo()]}));
 return g+hvChk()};
V['SC-03']=function(){
 var g='<h2>SC-03 구동 상태</h2><p class="lead">HiClo.app·HIVEN.app·AICS가 노트북에서 실제로 구동되는지, 원천 파일로 확인한 값만 봅니다.</p>';
 g+='<div class="row">'+
 '<div class="card"><div class="k">HiClo.app</div><div class="v">지금 구동: 확인 안 됨</div><div class="s">'+HVR.hiclo.ver+' · 마지막 판정 '+HVR.hiclo.last+' 「'+HVR.hiclo.verdict+'」 · 그 뒤 '+hvAge()+' 갱신 없음(5분 순환이면 갱신되어야 함) · '+tag('실측','ok')+'</div></div>'+
 '<div class="card"><div class="k">HIVEN.app</div><div class="v">지금 구동: 확인 안 됨</div><div class="s">마지막 관계 신호 '+HVR.hiven.last+' · '+HVR.hiven.note+'</div></div>'+
 '<div class="card"><div class="k">AICS</div><div class="v">확인 안 됨</div><div class="s">정지·재개 상태를 보여 주는 원천 파일 확인 안 됨</div></div></div>';
 g+='<h3>저장 주기(설정 파일 값)</h3>'+tbl(['구분','값','원천'],[['설정',HVR.save.period+'분 ('+HVR.save.setAt+' 설정)',HVR.save.src],['예약',HVR.save.sched,'같은 파일'],['실제 적용 여부',hvNo(),'적용 기록 확인 안 됨']]);
 g+='<h3>작업 대기열(마지막 결과)</h3>'+tbl(['작업','끝난 시각','결과','원천'],[[HVR.job.id,HVR.job.end,'종료 코드 '+HVR.job.rc+' '+tag('실측','ok'),HVR.job.src]]);
 return g+hvChk()};
V['SC-04']=function(){return hvTestOnly('SC-04','말 명령')()+'<input id="cin" type="hidden"><span id="cres" hidden></span>'};
V['SC-05']=hvTestOnly('SC-05','문서 자동 생성');
V['SC-06']=hvTestOnly('SC-06','체계 배포');
V['SC-07']=hvTestOnly('SC-07','고객 지원');
V['SC-08']=function(){
 var g='<h2>SC-08 수집·연동</h2><p class="lead">원천별 마지막 수신 시각을 원천 파일로 확인한 값만 봅니다.</p>';
 g+=tbl(['원천','마지막 수신','상태','확인'],[
  ['노트북 HiClo 판정 파일',HVR.hiclo.last,tag('끊김','bad')+' '+hvAge()+' 갱신 없음','실측'],
  ['HIVEN.app 관계 신호',HVR.hiven.last,hvNo(),'HiClo 판정 파일 기준'],
  ['작업 대기열 결과',HVR.job.end,tag('끊김','bad')+' 이후 결과 없음','실측'],
  ['모델 통제 이력(SC-13)','게시본',tag('정상','ok')+' 10초마다 읽음','실측'],
  ['통합사업관리 작업상황(SC-12)','게시본',tag('정상','ok')+' 30초마다 읽음','실측']]);
 return g+hvChk()};
V['SC-09']=hvTestOnly('SC-09','검수·품질');
V['SC-10']=function(){
 var g='<h2>SC-10 대응·경보</h2><p class="lead">HiClo 마지막 판정 기준 경보와 클로 단계만 봅니다.</p>';
 g+='<div class="grid">'+card('클로 단계',HVR.hiclo.stage,'마지막 판정 '+HVR.hiclo.last+' · '+tag('실측','ok'))+card('지금 단계','확인 안 됨','판정 '+hvAge()+' 갱신 없음 · '+tag('확인 안 됨','gray'))+card('대응 모드',"확인 안 됨",'원천 확인 안 됨')+'</div>';
 g+='<h3>경보</h3>'+tbl(['시각','심각도','대상','내용'],HVR.issues.map(function(r){return [r[0].slice(5),tag(r[1],r[1]==='경고'?'warn':'gray'),r[2],r[3]]}));
 return g+hvChk()};
V['SC-11']=hvTestOnly('SC-11','형상·변경');
