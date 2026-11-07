V['SC-01']=function(){
 var g='<h2>SC-01 종합 현황</h2><p class="lead">대표님이 한 화면에서 7개 사업군·구동 상태·경보를 봅니다. 숫자를 누르면 해당 화면으로 이동합니다.</p>';
 g+='<div class="grid">'+
  card('AICS 구동','구동 중(11/02)','지난 값 · '+tag('샘플(11/02 스냅샷)','gray'),'SC-05')+
  card('HiClo.app','3.1.2','판정 5분 순환 · '+tag('샘플(11/02 스냅샷)','gray'),'SC-05')+
  card('HIVEN.app','1.6','24시간 시험 관측 중 · '+tag('샘플(11/02 스냅샷)','gray'),'SC-05')+
  card('노트북 저장 주기','60분','30분 자동 예약 · '+tag('샘플(11/02 스냅샷)','gray'),'SC-05')+
  card('7개 사업군','7','정상 5 · 구성 중 2 · '+tag('샘플','smp'),'SC-04')+
  card('경보','2건','주의 2 · 위험 0 · '+tag('샘플','smp'),'SC-12')+'</div>';
 g+='<h3>사업군 한눈에</h3><div class="grid">'+BG.map(function(b){
  return card(b[0]+' · 통제 접점 '+b[3],b[1],tag(b[4],b[5]),'SC-04',function(){return '<p class="note">'+b[2]+' · 시험 데이터(원본에 싣지 않음)</p>'})}).join('')+'</div>';
 g+='<h3>경보 상위</h3>'+tbl(['시각','심각도','대상','내용'],[
  ['08:10',tag('주의','warn'),'HiClo','클로 단계 4(맥박) — 기억 회복 확인 중'],
  ['08:05',tag('주의','warn'),'HiServe','통합 서비스 플랫폼 연계 일부 구성 중']]);
 g+='<p class="note">[샘플(11/02 스냅샷)]은 11/02 08:04:58 노트북 HiClo 판정 파일에서 옮긴 지난 값, [샘플]은 시험용 값입니다. 자동 게시(PR-15)가 연결되면 같은 자리에 실제 값이 들어갑니다.</p>';
 return g};
V['SC-04']=function(){
 var g='<h2>SC-04 사업군 통제</h2><p class="lead">7개 사업군이 AICS 통제 접점(N1~N4)에 어떻게 물려 있는지 봅니다. 사업군 번호와 순서는 고정입니다.</p>';
 g+=tbl(['번호','사업군','역할','통제 접점','상태','L1-A 에이전트 축'],BG.map(function(b){return [b[0],'<b>'+b[1]+'</b>',b[2],b[3],tag(b[4],b[5]),tag('있음','ok')]}));
 g+='<h3>통제 접점 N1~N4</h3>'+tbl(['접점','맡는 일','연결 사업군'],[
  ['N1','체계·기준 발행(분류·전달·정리·구분)','HiDAM'],
  ['N2','금고·에이전트 두뇌 연결','HiCoffer · HiASI'],
  ['N3','서비스·용역 제공 연결','HiServe · HiICT'],
  ['N4','실버·거래 시장 연결','HiSilver · HiTrade']]);
 g+='<h3>연계 현황</h3><div class="grid">'+card('정의된 연계','E01~E43','대표님 확인 뒤 1.0')+card('추가 제안','E44~E63','전사업군 최적화안 0.4')+card('미정 연계','G02','HiTrade 새 연계 1건')+'</div>';
 return g};
V['SC-05']=function(){
 var g='<h2>SC-05 구동 상태</h2><p class="lead">HiClo.app과 HIVEN.app이 노트북에서 실제로 구동되는지, 정지·재개와 저장 주기를 봅니다.</p>';
 g+='<div class="row">'+
 '<div class="card"><div class="k">HiClo.app</div><div class="v">3.1.2 · 구동 중</div><div class="s">판정 08:04:58 · 5분 순환 · '+tag('샘플(11/02 스냅샷)','gray')+'</div></div>'+
 '<div class="card"><div class="k">HIVEN.app</div><div class="v">1.6 · 관측 중</div><div class="s">24시간 시험 11/03 00:50까지 · '+tag('샘플(11/02 스냅샷)','gray')+'</div></div>'+
 '<div class="card"><div class="k">AICS</div><div class="v">정지 아님</div><div class="s">정지·재개는 말 명령(SC-06) · '+tag('샘플(11/02 스냅샷)','gray')+'</div></div></div>';
 g+='<h3>저장 주기</h3>'+tbl(['구분','값','적용'],[['지금','60분','2026-11-02 07:52부터'],['예약','30분','2026-11-03 18:00부터 자동']]);
 g+='<h3>작업 대기열</h3>'+tbl(['작업','내용','결과'],[
  ['JOB-T0372','작업 대기열 시험','종료 코드 0 · 08:10:06 '+tag('통과','ok')],
  ['JOB-W0372','사이트 저장소 위치 확인(읽기 전용)','순환 대기 '+tag('대기','gray')]]);
 g+='<p class="note">구동 여부는 작업 전후로 노트북 판정 파일을 읽어 확인합니다. 이 화면은 읽기 전용입니다.</p>';
 return g};
V['SC-06']=function(){
 var g='<h2>SC-06 말 명령</h2><p class="lead">음성·문자로 말하면 시스템에 반영됩니다. 아래 칸에 문장을 입력하면 해석 결과를 미리 봅니다(시험판은 실제 실행을 하지 않습니다).</p>';
 g+='<input class="cmd" id="cin" placeholder="예) 저장 주기 30분으로 바꿔 / HiClo 정지 / AICS 재개" autocomplete="off"><div class="res" id="cres">입력하면 해석 결과가 여기에 표시됩니다.</div>';
 g+='<h3>지원 명령</h3>'+tbl(['구분','말 예시','처리'],[
  ['저장 주기','저장 주기 30분으로 / 11월 3일 18시부터 30분','즉시 또는 예약 반영'],
  ['HiClo.app','HiClo 시작 · HiClo 정지','작업 대기열로 노트북 실행'],
  ['HIVEN.app','HIVEN 앱 시작 · 정지','작업 대기열로 노트북 실행'],
  ['AICS','AICS 정지 · 재개','정지 표시 파일 생성·삭제'],
  ['폴더 정리·보고','폴더 정리해 · 상태 보고해','HiDAM 정리·전달 체계 확정 뒤 확장']]);
 return g};
