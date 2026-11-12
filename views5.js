/* T-W31-01 AICS 원천 연결 1차(M-13~M-16·SC-08, 대표님 규칙 20·21): SC-15·06·07·09·11을 게시 원천(cowork/ctl/aics_*.tsv — tools/gen_aics_src.py 산출)으로 표출. 원천에 없는 값은 「확인 안 됨」. 시험 페이지에서 먼저 확인 뒤 원본에 적용. */
function hv5Tsv(t){var L=t.replace(/\r/g,'').split('\n').filter(function(x){return x.length});return {h:L[0]?L[0].split('\t'):[],r:L.slice(1).map(function(x){return x.split('\t')})}}
function hv5Base(){return (location.pathname.indexOf('/test/')>=0?'../':'')+'cowork/ctl/'}
function hv5(id,name,lead,file,render){return function(){var el='hv5-'+id;setTimeout(function(){hvFetch(hv5Base()+file,'text').then(function(t){var d=hv5Tsv(t),n=document.getElementById(el);if(n)n.innerHTML=render(d)+'<p class="note">원천: cowork/ctl/'+file+' (게시본 실측 · tools/gen_aics_src.py 산출) · 원천에 없는 값은 「확인 안 됨」으로 둡니다.</p>'}).catch(function(e){var n=document.getElementById(el);if(n)n.innerHTML='<p class="note">'+tag('원천 읽기 실패','bad')+' cowork/ctl/'+file+' ('+hvEsc(e.message)+') — 값을 추정하지 않습니다.</p>'})},0);
 return '<h2>'+id+' '+name+'</h2><p class="lead">'+lead+'</p><div id="'+el+'">읽는 중…</div>'}}
V['SC-15']=hv5('SC-15','문서 자동 생성','산출 스크립트가 원천(이력·보고서·상황판)에서 자동으로 만든 게시 문서와 마지막 갱신을 봅니다.','aics_docgen.tsv',function(d){
 var ok=d.r.filter(function(r){return r[3]==='있음'}).length,last=d.r.map(function(r){return r[5]}).sort().pop()||'확인 안 됨';
 return '<div class="grid">'+card('자동 생성 문서',d.r.length+'건','존재 '+ok+' · 없음 '+(d.r.length-ok))+card('마지막 생성',last,'게시 커밋 기준')+card('생성 도구',(new Set(d.r.map(function(r){return r[1]}))).size+'개','tools/gen_*.py')+'</div>'+tbl(['게시 문서','생성 도구','화면','행 수','마지막 갱신','커밋'],d.r.map(function(r){return [r[0],r[1],r[2],r[4]===''?'—':r[4],r[5],r[6]]}))});
V['SC-08']=hv5('SC-08','체계 배포','분류 체계·규칙 문서의 최종본·작업본 판을 노트북 원천 폴더(HV_STD) 목록으로 봅니다.','aics_deploy.tsv',function(d){
 var w=d.r.filter(function(r){return r[3]==='작업본 승인 대기'}).length;
 return '<div class="grid">'+card('분류·규칙 문서',d.r.length+'종','HV_STD_DM_표준_기준')+card('작업본 승인 대기',w+'종','최종화는 Fable')+card('적용 폴더 수·불일치','확인 안 됨','D2(12월) 배포 원장 생성 뒤')+'</div>'+tbl(d.h,d.r.map(function(r){return [r[0],r[1],r[2],r[3]==='작업본 승인 대기'?tag(r[3],'warn'):tag(r[3],'ok'),r[4]]}))});
V['SC-14']=hv5('SC-14','고객 지원','고객 지원 사례 원장(접수·첫 응답·종결·응답 기한)을 봅니다.','aics_cs_cases.tsv',function(d){
 return '<div class="grid">'+card('접수 사례',d.r.length+'건','HiCoffer PC 베타1 배포 전(11월 말)')+card('접수 채널','assist@hiven.ai.kr','앱 내 신고는 베타2',null,function(){return tbl(['채널','상태','근거'],[['이메일 assist@hiven.ai.kr','운영','기존'],['앱 안 접수','베타2','기존 표기'],['챗봇(SC-C01~C28)','구현 전 — 값 확인 안 됨','기준서 1.1']])})+card('응답 기한 규칙','확인 안 됨','게이트 O-07 미통과 — 문구 승인 뒤 반영')+'</div>'+hv5Eight(d)+'<h3>접수 원장</h3>'+(d.r.length?tbl(d.h,d.r.slice().reverse().map(function(r){return r.map(hvEsc)})):'<p class="note">원장 열: '+d.h.join(' · ')+' — 접수되면 이 원장에 행이 추가되고 이 화면에 바로 보입니다. 사례 번호 형식 CASE-서비스-주제-번호 · 갈래 가·나·다 · 종결 방식 챗봇·사람·통제 · 이름·경로·내용 칸은 두지 않습니다.</p>')});
/* 261111 H-4: 여덟 숫자 버튼(사용자·기기·키·정합·미러링·복구·지원·갱신) — 자리만. 값은 원천이 생길 때까지 「확인 안 됨」(지원 접수 건수만 원장 실측). 숫자·경보 조건의 가정값은 test/sim.html에만 둔다 */
var HV5_E8=[
 ['사용자','설치·가입·구독·종료·탈퇴, 기능 등급 분포, 무료→회원→구독 전환·4주 유지','PR-11 구독 상태 · CR-10'],
 ['기기','기기 등록·해제, 매체 꽂음·등록(회원 기기 — 통합관제 접속 신뢰 기기와 다른 표)','PR-01·PR-02 · LNK-E01~E03'],
 ['키','키 사건(연속 실패·바꾸기·분실 3단계)','PR-08 · CR-02·CR-03 · IF-7'],
 ['정합','색인 보고, 중복·정합 판정, 최종본 확정','PR-03~PR-05 · SYN-E01·E02'],
 ['미러링','미러링 실행, 해시 불일치, 자동 미러링 멈춤','PR-06 · SYN-E03~E05 · CR-05·CR-06'],
 ['복구','복구(되돌리기)·복구(원복) 실행, 실패·일부, 한도','PR-07 · LED-E01~E04 · CR-04'],
 ['지원','지원 접수·종결·넘김(갈래 가·나·다)','PR-09 · CR-07 · FL-7'],
 ['갱신','갱신 성공·실패(판·운영체제 계열별)','PR-10 · CR-01 · FL-8']];
function hv5Eight(d){var na=function(){return typeof hvNo==='function'?hvNo():tag('확인 안 됨','gray')};
 return '<h3>여덟 숫자(사용자 · 기기 · 키 · 정합 · 미러링 · 복구 · 지원 · 갱신)</h3><div class="grid">'+HV5_E8.map(function(x){var real=x[0]==='지원';
  return card(x[0],real?d.r.length+'건':'확인 안 됨',real?'접수 원장 실측':'원천 연결 전',null,function(){return tbl(['항목','값','원천·근거'],[
   ['보는 것',x[1],'다중화 설계안 0.1 5장 · 기준서 1.1 8장'],
   ['지금 값',real?d.r.length+'건(접수 원장 줄 수)':na(),real?'cowork/ctl/aics_cs_cases.tsv':'원천 없음 — 기기·Cloud에서 오는 수신 경로 구현 전'],
   ['실릴 메시지·사건·규칙',x[2],'다중화 설계안 0.1 2·5장 · 정립서 15.3'],
   ['경보 조건 값',na()+' 베타 2차 실측으로 정함','설계안의 값은 가정'],
   ['시험 값','<a href="test/sim.html">시험 페이지(시뮬레이션 — 실측 아님)</a>','cowork/ctl/sim_multi_result.json']])})}).join('')+'</div><p class="note">여덟 칸은 자리만 만든 것입니다. 원천이 연결되기 전에는 숫자를 싣지 않습니다(지원 = 접수 원장 줄 수만 실측).</p>'}
V['SC-13']=hv5('SC-13','검수·품질','자동 검수 기록과 결함 대장(모델통제 이력의 위반·지적·자가 발견·장애)을 봅니다.','aics_qa.tsv',function(d){
 var q=d.r.filter(function(r){return r[0]==='자동 검수'}),f=d.r.filter(function(r){return r[0]==='결함'}),done=f.filter(function(r){return hvStDone(r[5])}).length;
 return '<div class="grid">'+card('자동 검수',q.length+'종','통과 '+q.filter(function(r){return r[3]==='통과'}).length)+card('결함 대장',f.length+'건','조치 완료 '+done+' · 그 밖 '+(f.length-done))+card('최근 결함',(f[f.length-1]||['','확인 안 됨'])[1]?'#'+f[f.length-1][1]:'확인 안 됨',(f[f.length-1]||[])[2]||'')+'</div><h3>결함 대장(최신순)</h3>'+tbl(['번호','시각','모델·구분','내용','상태'],f.slice().reverse().map(function(r){return ['#'+r[1],r[2],r[3],hvEsc(r[4]),r[5]]}))+'<h3>자동 검수</h3>'+tbl(['검사','마지막 실행','결과'],q.map(function(r){return [r[1],r[2],r[3]]}))+hv5Cls()});
/* 261111: 분류 품질 세 숫자 자리(PR-12 · CLS-E01 · CR-09) — 값은 「확인 안 됨」 */
function hv5Cls(){var na=function(){return typeof hvNo==='function'?hvNo():tag('확인 안 됨','gray')};
 return '<h3>분류 품질(자리만)</h3><div class="grid">'+[['확신 비율','판정이 확신으로 끝난 비율'],['고친 비율','사용자가 판정을 고친 비율'],['판정 대기 비율','보류함에 남은 비율']].map(function(x){
  return card(x[0],'확인 안 됨','원천 연결 전',null,function(){return tbl(['항목','값','원천·근거'],[['보는 것',x[1],'다중화 설계안 0.1 PR-12 · 정립서 15.3 CLS-E01'],['지금 값',na(),'원천 없음 — 기기에서 오는 집계 수신 경로 구현 전'],['경보 조건 값',na()+' 베타 2차 실측으로 정함','CR-09(설계안의 값은 가정)'],['시험 값','<a href="test/sim.html">시험 페이지(시뮬레이션 — 실측 아님)</a>','—']])})}).join('')+'</div>'}
V['SC-12']=hv5('SC-12','형상·변경','게시 저장소(hiven.ai.kr)의 변경 기록(커밋)을 최신순으로 봅니다.','aics_changes.tsv',function(d){
 return '<div class="grid">'+card('최근 변경',(d.r[0]||['','확인 안 됨'])[1],(d.r[0]||[''])[0]+' · 커밋 시각')+card('기록 범위',d.r.length+'건','최근 커밋')+card('기준선','확인 안 됨','DOCGEN 기준선 원장은 D2')+'</div>'+tbl(d.h,d.r.map(function(r){return [r[0],r[1],hvEsc(r[2]),r[3]||'—']}))+'<p class="note">시각 칸은 적어 넣은 시각이 아니라 저장소의 커밋 시각(한국 시각)입니다. 바꾸기 전 값 대조표: cowork/ctl/aics_changes_timefix.tsv</p>'+hv5Ver()});
/* 261111: 판 셋 자리(정립서 15.3 HDA-R3) — 값은 「확인 안 됨」 */
function hv5Ver(){var na=function(){return typeof hvNo==='function'?hvNo():tag('확인 안 됨','gray')};
 return '<h3>판 셋(정책 판 · 앱 판 · 보호 규칙 판 — 자리만)</h3>'+tbl(['판','적는 형식','지금 값','원천'],[['정책 판','HiDAM-STD-판 번호',na(),'원천 없음 — 배포된 기기의 원장 줄에서 받음(구현 전)'],['앱 판','HDA-판 번호',na(),'같음'],['보호 규칙 판','AAD-R-날짜',na(),'같음']])+'<p class="note">판은 셋을 따로 셉니다(정립서 15.3 HDA-R3). 맞는 짝 표(NC-08)와 최종본 확정(PR-05)의 해시·판 번호도 이 자리에 실립니다. 지금은 저장소 파일 해시(SC-02 무결성)만 실측입니다.</p>'}
