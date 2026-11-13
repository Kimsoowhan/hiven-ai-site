/* T-W31-01 AICS 원천 연결 1차(M-13~M-16·SC-08, 대표님 규칙 20·21): SC-15·06·07·09·11을 게시 원천(cowork/ctl/aics_*.tsv — tools/gen_aics_src.py 산출)으로 표출. 원천에 없는 값은 「확인 안 됨」. 시험 페이지에서 먼저 확인 뒤 원본에 적용. */
function hv5Tsv(t){var L=t.replace(/\r/g,'').split('\n').filter(function(x){return x.length});return {h:L[0]?L[0].split('\t'):[],r:L.slice(1).map(function(x){return x.split('\t')})}}
function hv5Base(){return (location.pathname.indexOf('/test/')>=0?'../':'')+'cowork/ctl/'}
function hv5(id,name,lead,file,render){return function(){var el='hv5-'+id;setTimeout(function(){hvFetch(hv5Base()+file,'text').then(function(t){var d=hv5Tsv(t),n=document.getElementById(el);if(n)n.innerHTML=render(d)+'<p class="note">원천: cowork/ctl/'+file+' (게시본 실측 · tools/gen_aics_src.py 산출) · 원천에 없는 값은 「확인 안 됨」으로 둡니다.</p>'}).catch(function(e){var n=document.getElementById(el);if(n)n.innerHTML='<p class="note">'+tag('원천 읽기 실패','bad')+' cowork/ctl/'+file+' ('+hvEsc(e.message)+') — 값을 추정하지 않습니다.</p>'})},0);
 return '<h2>'+id+' '+name+'</h2><p class="lead">'+lead+'</p><div id="'+el+'">읽는 중…</div>'}}
/* SC-15 문서 자동 생성(2026-11-13 대표님 18:07~18:11 지시): HiBiz 실측 × 문서 규칙표 대조 결과를 게시 원천(tools/hibiz_doc_check.py 산출)으로 표출. 손으로 적은 값 없음. */
V['SC-15']=function(){var el='hv5-SC-15',B=hv5Base(),F=['aics_docfolder.tsv','aics_doccheck.tsv','doc_rules.tsv','doc_life.tsv','aics_docgen.tsv','aics_docsync.tsv','aics_scmap.tsv'];
 setTimeout(function(){Promise.all(F.map(function(f){return hvFetch(B+f,'text').then(hv5Tsv)})).then(function(D){var fo=D[0],ck=D[1],ru=D[2],li=D[3],ge=D[4],sy=D[5],sm=D[6],n=document.getElementById(el);if(!n)return;
  function S(r,i){return r.reduce(function(a,x){return a+(+x[i]||0)},0)}
  var when=(fo.r[0]||[])[6]||'확인 안 됨',bad=S(ck.r,4),al=ck.r.filter(function(r){return r[3]==='얼럿'}),aln=S(al,4);
  var h='<div class="grid">'+card('HiBiz 실측',when,'1층 폴더 '+fo.r.length+'개')+card('폴더 · 파일',S(fo.r,1).toLocaleString()+' · '+S(fo.r,2).toLocaleString(),'실측 전체')+card('규칙에 어긋난 것',bad.toLocaleString()+'건','검사 '+ck.r.length+'가지')+card('얼럿',aln.toLocaleString()+'건','정리할 것')+'</div>';
  if(aln>0)h+='<p class="note">'+tag('얼럿','bad')+' '+al.filter(function(r){return +r[4]>0}).map(function(r){return hvEsc(r[1])+' '+r[4]+'건'}).join(' · ')+' — 처리가 끝나 다시 실측하면 사라집니다.</p>';
  else h+='<p class="note">'+tag('정상','ok')+' 얼럿 없음</p>';
  var ls=sy.r[sy.r.length-1]||[];h+='<h3>실측 싱크 (SC-15 목록 = Dell XPS 15 HiBiz)</h3><p class="note">'+(+ls[8]>0?tag('얼럿','bad')+' 새로 생긴 파일 중 규칙 밖 '+ls[8]+'건':tag('맞음','ok')+' 앞 실측 뒤 규칙 밖으로 새로 생긴 파일 없음')+' · 목록 지문 '+hvEsc(String(ls[2]||'').slice(0,16))+'…</p>'+tbl(['실측 시각','기기','파일 수','폴더 수','새로 생김','없어짐','바뀜','새로 생긴 것 중 규칙 밖','어긋난 건수'],sy.r.slice().reverse().map(function(r){return [r[0],r[1],r[3],r[4],r[5],r[6],r[7],r[8],r[9]]}));
  h+='<h3>검사 결과 (규칙 대조)</h3>'+tbl(['검사','무엇을 보는가','규칙','등급','어긋난 건수','폴더별(번호:건수)','처리'],ck.r.map(function(r){return [r[0],r[1],r[2],tag(r[3],r[3]==='얼럿'?'bad':(r[3]==='주의'?'warn':'ok')),r[4],r[5],r[6]]}));
  h+='<h3>폴더별 실측과 색인 자동 생성</h3>'+tbl(['1층 폴더','폴더 수','파일 수','어긋난 건수','얼럿','색인 자동 생성본'],fo.r.map(function(r){return [r[0],r[1],r[2],r[3],+r[4]>0?tag(r[4],'bad'):r[4],r[5]]}));
  var smb=sm.r.filter(function(r){return r[13]!=='맞음'}).length;h+='<h3>화면 × 문서 × 폴더 × 분류 연결표 (SC-00~SC-17)</h3><p class="note">흐름: 들어오는 것(SC-17 말 명령 · SC-16 모델 통제 · SC-05~14 사업군 · SC-01 · SC-03 · SC-04) → SC-02 종합 현황 → SC-00 대표님 결재 → SC-15 문서 자동 생성 → HiBiz 폴더 · HiDAM · GS 인증. 화면을 실제로 열어 읽는 원천을 잰 값입니다. 맞지 않는 줄 '+smb+'건.</p>'+tbl(['화면','이름','흐름 자리','게시 원천(데이터 문서)','행 수','만드는 도구(코드)','마지막 갱신','근거','HiBiz 원천 폴더','HiDAM 분류','문서 규칙','대조'],sm.r.map(function(r){return [r[0],r[1],r[2],r[4],r[6]||'—',r[7],r[8]||'—',r[9],r[10],r[11],r[12],tag(r[13],r[13]==='맞음'?'ok':(r[13]==='손으로 쓰는 원천'?'warn':'bad'))]}));
  h+='<h3>문서 규칙표 (DR)</h3>'+tbl(ru.h,ru.r);
  h+='<h3>문서 생애 절차 (생성 → 파기)</h3>'+tbl(li.h,li.r);
  h+='<h3>통합관제 게시 문서 (산출 도구가 만든 것, 커밋 기준)</h3>'+tbl(['게시 문서','생성 도구','화면','행 수','마지막 갱신','커밋'],ge.r.map(function(r){return [r[0],r[1],r[2],r[4]===''?'—':r[4],r[5],r[6]]}));
  n.innerHTML=h+'<p class="note">원천: cowork/ctl/aics_docfolder.tsv · aics_doccheck.tsv · doc_rules.tsv · doc_life.tsv · aics_docgen.tsv (tools/hibiz_doc_check.py · tools/gen_aics_src.py 산출). 파일마다의 줄은 비공개 「HiBiz 전체 펼침표」에 있습니다. 잇는 곳: HiDAM 자산원장(14_10_11) · GS 인증(14_13_GS인증).</p>'}).catch(function(e){var n=document.getElementById(el);if(n)n.innerHTML='<p class="note">'+tag('원천 읽기 실패','bad')+' ('+hvEsc(e.message)+') — 값을 추정하지 않습니다.</p>'})},0);
 return '<h2>SC-15 문서 자동 생성</h2><p class="lead">HiBiz 폴더를 실측해 문서 규칙표와 대조합니다. 폴더별 색인을 자동으로 만들고, 규칙에 어긋난 것과 맨 위에 남은 옛 판을 얼럿으로 띄웁니다.</p><div id="'+el+'">읽는 중…</div>'};
V['SC-08']=hv5('SC-08','체계 배포','분류 체계·규칙 문서의 최종본·작업본 판을 노트북 원천 폴더(HV_STD) 목록으로 봅니다.','aics_deploy.tsv',function(d){
 var w=d.r.filter(function(r){return r[3]==='작업본 승인 대기'}).length;
 return '<div class="grid">'+card('분류·규칙 문서',d.r.length+'종','HV_STD_DM_표준_기준')+card('작업본 승인 대기',w+'종','최종화는 Fable')+card('적용 폴더 수·불일치','확인 안 됨','D2(12월) 배포 원장 생성 뒤')+'</div>'+tbl(d.h,d.r.map(function(r){return [r[0],r[1],r[2],r[3]==='작업본 승인 대기'?tag(r[3],'warn'):tag(r[3],'ok'),r[4]]}))});
V['SC-14']=hv5('SC-14','고객 지원','고객 지원 사례 원장(접수·첫 응답·종결·응답 기한)을 봅니다.','aics_cs_cases.tsv',function(d){
 return '<div class="grid">'+card('접수 사례',d.r.length+'건','HiCoffer PC 베타1 배포 전(11월 말)')+card('접수 채널','assist@hiven.ai.kr','앱 내 신고는 베타2',null,function(){return tbl(['채널','상태','근거'],[['이메일 assist@hiven.ai.kr','운영','기존'],['앱 안 접수','베타2','기존 표기'],['챗봇(SC-C01~C28)','구현 전 — 값 확인 안 됨','기준서 1.1']])})+card('응답 기한 규칙','확인 안 됨','응답 기한 문구는 승인 뒤 반영(게이트 O-07은 「접수 채널」 항목이라 이 규칙과 별개 · 원천 deploy_beta1_gates.tsv)')/* 판정 147 ③(11-13): 「O-07 미통과」 글이 원천 결과와 달라 고침 */+'</div>'+hv5Eight(d)+'<h3>접수 원장</h3>'+(d.r.length?tbl(d.h,d.r.slice().reverse().map(function(r){return r.map(hvEsc)})):'<p class="note">원장 열: '+d.h.join(' · ')+' — 접수되면 이 원장에 행이 추가되고 이 화면에 바로 보입니다. 사례 번호 형식 CASE-서비스-주제-번호 · 갈래 가·나·다 · 종결 방식 챗봇·사람·통제 · 이름·경로·내용 칸은 두지 않습니다.</p>')});
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
