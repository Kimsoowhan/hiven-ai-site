V['SC-05']=function(){
 var g='<h2>SC-05 문서 자동 생성</h2><p class="lead">AICS의 첫째 존재 이유입니다. 요구→설계→구현→시험 추적과 활동 연결로 문서를 자동으로 만들고 어긋남을 잡습니다.</p>';
 g+='<div class="grid">'+card('역검증 추적표','25행','통과·해소 17 · 열린 과제 C-1, C-3~C-6')+card('개발 원장','32지점','확정 29')+card('문서 버전','최신 1벌','이전 버전은 정리 작업으로 보관')+'</div>';
 g+='<h3>문서 정합 상태(HiDAM 체계 배포 반영)</h3>'+tbl(['문서','버전','반영'],[
  ['연동 설계안','0.7',tag('반영','ok')],['사업군 비즈니스 플랜','0.4',tag('반영','ok')],
  ['분류 정책군','0.2',tag('반영','ok')],['전사업군 최적화안','0.4',tag('반영','ok')],
  ['HiDAM 폴더 안내(33_HiDAM)','-',tag('진행','warn')]]);
 return g};
V['SC-06']=function(){
 var g='<h2>SC-06 체계 배포</h2><p class="lead">HIVEN의 모든 체계는 HiDAM이 한 곳에서 제정하고 한 곳에서 배포합니다. 사업군은 받아 쓰고 따로 만들지 않습니다.</p>';
 g+=tbl(['체계','대상','발행·배포'],[
  ['전달 체계','음성·문자 지시·보고','HiDAM 단일'],['정리 체계','폴더·파일 정리','HiDAM 단일'],
  ['구분 체계','분류 기준·구분값','HiDAM 단일'],['문서 분류','문서','HiDAM 단일'],
  ['데이터 분류','로우 데이터·파일','HiDAM 단일'],['폴더·라벨','폴더링','HiDAM 단일'],
  ['코드 분류','코드','HiDAM 단일'],['기본 표준','위 전체의 기본값','HiDAM 단일']]);
 return g};
V['SC-07']=function(){
 var g='<h2>SC-07 고객 지원</h2><p class="lead">모든 접점의 문의를 한 번호 체계로 보고 기한 넘김을 막습니다. 개인정보는 표시하지 않고 가린 값·집계만 보입니다.</p>';
 g+='<div class="grid">'+card('HiCoffer','미수신','문의 수집 연결 전 · '+tag('샘플','smp'))+card('HiSilver','미수신','문의 수집 연결 전 · '+tag('샘플','smp'))+card('SLA 준수율','-','수집 시작 전')+'</div>';
 g+='<p class="note">0건과 미수신·미구현은 다르게 표시합니다. 지금은 「미수신」입니다.</p>';
 return g};
V['SC-08']=function(){
 var g='<h2>SC-08 수집·연동</h2><p class="lead">「이 데이터가 왜 안 들어와 있지」를 바로 찾는 화면입니다.</p>';
 g+=tbl(['원천','마지막 수신','상태','받는 방법'],[
  ['노트북 HiClo 판정 파일','08:04:58',tag('정상','ok'),'5분 순환'],
  ['HIVEN.app 순환 결과','08:05',tag('정상','ok'),'5분 순환'],
  ['고객 문의 수집','-',tag('미수신','gray'),'수집기 연결 뒤'],
  ['사이트 게시(PR-15)','-',tag('미구현','gray'),'게시 연결 뒤']]);
 return g};
V['SC-09']=function(){
 var g='<h2>SC-09 검수·품질</h2><p class="lead">자동 검수 결과와 결함을 봅니다.</p>';
 g+='<div class="grid">'+card('HiClo 최종 검수','통과','07:37 · '+tag('실측','ok'))+card('작업 대기열 시험','통과','종료 코드 0 · '+tag('실측','ok'))+card('열린 과제','5건','C-1, C-3~C-6')+'</div>';
 g+='<h3>알려진 위험</h3>'+tbl(['번호','내용','상태'],[
  ['R-01','통제 장치 간 상호 차단(압축 뒤 순환)',tag('개선 필요','warn')],
  ['R-05','시뮬레이션 기준값이 15분 가정',tag('개선 필요','warn')],
  ['R-06','신호 파일 이름 불일치',tag('기록','gray')]]);
 return g};
V['SC-10']=function(){
 var g='<h2>SC-10 대응·경보</h2><p class="lead">장애·고객·연동 대응이 어느 모드로 어디까지 왔는지 봅니다.</p>';
 g+='<div class="grid">'+card('대응 모드','상시','상시 · 임시 · 긴급 · 비상')+card('클로 단계','4단계','기억 회복 확인 중 · '+tag('실측','ok'))+card('복구','해당 없음','진행 중인 복구 없음')+'</div>';
 g+='<h3>대응 흐름</h3>'+tbl(['단계','내용'],[['1','감지(하트비트·판정)'],['2','기억 회복(MEM-R) 확인'],['3','단계 한 칸씩 복귀'],['4','통제 개입안(최후 방안)']]);
 return g};
V['SC-11']=function(){
 var g='<h2>SC-11 형상·변경</h2><p class="lead">바뀐 것과 기준선, 문서 상태를 봅니다.</p>';
 g+=tbl(['규칙 rev','일시','내용'],[
  ['34','11/02 08:11','AICS 구동 전제 · 작업 순서 정리'],
  ['33','11/02 08:03','HiDAM 체계 배포 · 저장 주기 60분'],
  ['32','11/02 07:57','음성·문자 전달 체계']]);
 return g};

/* SC-12 통합사업관리 작업상황 — 01_클로_소통(COM)\CoWork_진행상황판 사본(/cowork/board.md)을 읽어 표시. 저장소에 올라온 시점이 기준. */
V['SC-12']=function(){
 setTimeout(hvCowork,0);
 return '<h2>SC-12 통합사업관리 작업상황</h2><p class="lead">CoWork 진행상황판(COM)의 게시본입니다. 원본: HiBiz\\01_클로_소통(COM)\\CoWork_진행상황판-261104.md · <span id="cw-upd">읽는 중…</span></p><div id="cw"></div>'};
function hvMdTables(md){
 var out=[],lines=md.split(/\r?\n/),i=0;
 while(i<lines.length){
  if(/^\|/.test(lines[i])&&i+1<lines.length&&/^\|[\s:|-]+\|$/.test(lines[i+1])){
   var head=lines[i].split('|').slice(1,-1).map(function(s){return s.trim()}),rows=[];i+=2;
   while(i<lines.length&&/^\|/.test(lines[i])){rows.push(lines[i].split('|').slice(1,-1).map(function(s){return s.trim()}));i++}
   var t=i-rows.length-3;while(t>=0&&!/^#/.test(lines[t]))t--;
   out.push({title:t>=0?lines[t].replace(/^#+\s*/,''):'',head:head,rows:rows});
  }else i++;
 }
 return out;
}
function hvEsc(s){return String(s).replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c]})}
function hvCowork(){
 var el=$('cw'),up=$('cw-upd');if(!el)return;
 fetch('/cowork/board.md?v='+Date.now(),{cache:'no-store'}).then(function(r){
  if(!r.ok)throw new Error(r.status);up.textContent='게시 시각 '+(r.headers.get('last-modified')?new Date(r.headers.get('last-modified')).toLocaleString('ko-KR'):'확인 안 됨');return r.text();
 }).then(function(md){
  var T=hvMdTables(md),g='';
  var st={'대기':'smp','승인 대기':'warn','진행 중':'warn','완료·검수 대기':'ok','통과':'ok','위반':'bad','완료':'ok'};
  T.forEach(function(t){
   g+='<h3 style="margin:18px 0 6px">'+hvEsc(t.title)+'</h3><div style="overflow:auto"><table><thead><tr>'+t.head.map(function(h){return '<th>'+hvEsc(h)+'</th>'}).join('')+'</tr></thead><tbody>';
   t.rows.forEach(function(r){g+='<tr>'+r.map(function(c,j){var k=st[c];return '<td>'+(k?'<span class="tag '+k+'">'+hvEsc(c)+'</span>':hvEsc(c))+'</td>'}).join('')+'</tr>'});
   g+='</tbody></table></div>';
  });
  var m=md.match(/## 금지 4조항[\s\S]*?(?=\n## )/);
  if(m)g+='<p class="note" style="white-space:pre-wrap;margin-top:14px">'+hvEsc(m[0])+'</p>';
  el.innerHTML=g||'<p class="note">표를 찾지 못했습니다.</p>';
 }).catch(function(e){up.textContent='읽기 실패 '+e.message;el.innerHTML='<p class="note">/cowork/board.md 를 읽지 못했습니다. 게시본이 아직 올라가지 않았거나 경로가 다릅니다.</p>'});
}
