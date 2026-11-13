V['SC-15']=function(){
 var g='<h2>SC-15 문서 자동 생성</h2><p class="lead">AICS의 첫째 존재 이유입니다. 요구→설계→구현→시험 추적과 활동 연결로 문서를 자동으로 만들고 어긋남을 잡습니다.</p>';
 g+='<div class="grid">'+card('역검증 추적표','25행','통과 17 · 열린 과제 5')+card('개발 원장','32지점','확정 29')+card('문서 버전','최신 1벌','이전 버전은 정리 작업으로 보관')+'</div>';
 g+='<h3>문서 정합 상태(HiDAM 체계 배포 반영)</h3>'+tbl(['문서','버전','반영'],[
  ['연동 설계안','0.7',tag('반영','ok')],['사업군 비즈니스 플랜','0.4',tag('반영','ok')],
  ['분류 정책군','0.2',tag('반영','ok')],['전사업군 최적화안','0.4',tag('반영','ok')],
  ['HiDAM 폴더 안내(33_HiDAM)','-',tag('진행','warn')]]);
 return g};
V['SC-08']=function(){
 var g='<h2>SC-08 체계 및 시스템/서비스</h2><p class="lead">HIVEN의 모든 체계는 HiDAM이 한 곳에서 제정하고 한 곳에서 배포합니다. 사업군은 받아 쓰고 따로 만들지 않습니다.</p>';
 g+=tbl(['체계','대상','발행·배포'],[
  ['전달 체계','음성·문자 지시·보고','HiDAM 단일'],['정리 체계','폴더·파일 정리','HiDAM 단일'],
  ['구분 체계','분류 기준·구분값','HiDAM 단일'],['문서 분류','문서','HiDAM 단일'],
  ['데이터 분류','로우 데이터·파일','HiDAM 단일'],['폴더·라벨','폴더링','HiDAM 단일'],
  ['코드 분류','코드','HiDAM 단일'],['기본 표준','위 전체의 기본값','HiDAM 단일']]);
 return g};
V['SC-14']=function(){
 var g='<h2>SC-14 고객 지원</h2><p class="lead">모든 접점의 문의를 한 번호 체계로 보고 기한 넘김을 막습니다. 개인정보는 표시하지 않고 가린 값·집계만 보입니다.</p>';
 g+='<div class="grid">'+card('HiCoffer','미수신','문의 수집 연결 전 · '+tag('샘플','smp'))+card('HiSilver','미수신','문의 수집 연결 전 · '+tag('샘플','smp'))+card('SLA 준수율','-','수집 시작 전')+'</div>';
 g+='<p class="note">0건과 미수신·미구현은 다르게 표시합니다. 지금은 「미수신」입니다.</p>';
 return g};
V['SC-11']=function(){
 var g='<h2>SC-11 수집·연동</h2><p class="lead">「이 데이터가 왜 안 들어와 있지」를 바로 찾는 화면입니다.</p>';
 g+=tbl(['원천','마지막 수신','상태','받는 방법'],[
  ['노트북 HiClo 판정 파일','08:04:58',tag('정상','ok'),'5분 순환'],
  ['HIVEN.app 순환 결과','08:05',tag('정상','ok'),'5분 순환'],
  ['고객 문의 수집','-',tag('미수신','gray'),'수집기 연결 뒤'],
  ['사이트 게시(PR-15)','-',tag('미구현','gray'),'게시 연결 뒤']]);
 return g};
V['SC-13']=function(){
 var g='<h2>SC-13 검수·품질</h2><p class="lead">자동 검수 결과와 결함을 봅니다.</p>';
 g+='<div class="grid">'+card('HiClo 최종 검수','통과','07:37 · '+tag('샘플(11/02 스냅샷)','gray'))+card('작업 대기열 시험','통과','종료 코드 0 · '+tag('샘플(11/02 스냅샷)','gray'))+card('열린 과제','5건','C-1, C-3~C-6')+'</div>';
 g+='<h3>알려진 위험</h3>'+tbl(['번호','내용','상태'],[
  ['R-01','통제 장치 간 상호 차단(압축 뒤 순환)',tag('개선 필요','warn')],
  ['R-05','시뮬레이션 기준값이 15분 가정',tag('개선 필요','warn')],
  ['R-06','신호 파일 이름 불일치',tag('기록','gray')]]);
 return g};
V['SC-07']=function(){
 var g='<h2>SC-07 대응·경보</h2><p class="lead">장애·고객·연동 대응이 어느 모드로 어디까지 왔는지 봅니다.</p>';
 g+='<div class="grid">'+card('대응 모드','상시','상시 · 임시 · 긴급 · 비상')+card('클로 단계','4단계','기억 회복 확인 중 · '+tag('샘플(11/02 스냅샷)','gray'))+card('복구','해당 없음','진행 중인 복구 없음')+'</div>';
 g+='<h3>대응 흐름</h3>'+tbl(['단계','내용'],[['1','감지(하트비트·판정)'],['2','기억 회복(MEM-R) 확인'],['3','단계 한 칸씩 복귀'],['4','통제 개입안(최후 방안)']]);
 return g};
V['SC-12']=function(){
 var g='<h2>SC-12 형상·변경</h2><p class="lead">바뀐 것과 기준선, 문서 상태를 봅니다.</p>';
 g+=tbl(['규칙 rev','일시','내용'],[
  ['34','11/02 08:11','AICS 구동 전제 · 작업 순서 정리'],
  ['33','11/02 08:03','HiDAM 체계 배포 · 저장 주기 60분'],
  ['32','11/02 07:57','음성·문자 전달 체계']]);
 return g};

/* SC-10 통합사업관리 작업상황 v2 — /cowork/progress.json · reports/index.json · log.tsv 를 30초마다 읽어 표시. 저장소에 올라온(푸시된) 시점이 기준. 외부 라이브러리 없음. */
var hvT=null,hvLast=null,hvLastOk='',hvOpen={};
function hvEsc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function hvFetch(u,type){return fetch(u+'?v='+Date.now(),{cache:'no-store'}).then(function(r){if(!r.ok)throw new Error(r.status);return type==='json'?r.json():r.text()})}
V['SC-10']=function(){
 setTimeout(hvSC12Start,0);
 return '<div id="sc12"><h2>SC-10 통합사업 작업상황</h2><p class="lead">CoWork 진행상황 게시본입니다. 원본: HiBiz\\01_클로_소통(COM)\\ · 이 화면은 게시된(푸시된) 시점의 값이며 30초마다 다시 읽습니다. <span id="sc12-st">읽는 중…</span></p><div id="sc12-b"></div></div>'};
function hvSC12Start(){
 if(hvT){clearInterval(hvT);hvT=null}
 hvSC12Load();
 hvT=setInterval(function(){if(!$('sc12')){clearInterval(hvT);hvT=null;return}hvSC12Load()},30000);
}
function hvSC12Load(){
 Promise.all([
  hvFetch('cowork/progress.json','json').then(function(d){return {ok:1,d:d}},function(e){return {ok:0,e:e}}),
  hvFetch('cowork/reports/index.json','json').then(function(d){return {ok:1,d:d}},function(e){return {ok:0,e:e}}),
  hvFetch('cowork/log.tsv','text').then(function(d){return {ok:1,d:d}},function(e){return {ok:0,e:e}})
 ]).then(function(r){
  if(!$('sc12'))return;
  if(r[0].ok&&r[0].d&&Array.isArray(r[0].d.items)){hvLast={p:r[0].d,rep:r[1],log:r[2]};hvLastOk=kst();hvSC12Paint(false)}
  else hvSC12Paint(true,r[0].e);
 });
}
function hvStage(sc){return sc>=100?'s100':sc>=90?'s90':sc>=70?'s70':sc>=30?'s30':'s0'}
function hvDue(due){
 var m=String(due||'').match(/^(\d+)\/(\d+)(?:~(\d+))?/);if(!m)return null;
 return new Date(2026,+m[1]-1,m[3]?+m[3]:+m[2],18,0,0);
}
function hvSC12Paint(fail,err){
 var st=$('sc12-st'),b=$('sc12-b');if(!st||!b)return;
 if(fail){
  st.innerHTML='<span class="tag bad">게시본 없음</span> 마지막 성공 시각 '+(hvLastOk?hvEsc(hvLastOk):'없음')+' · 30초 뒤 다시 시도'+(err?' ('+hvEsc(err.message)+')':'');
  if(!hvLast){b.innerHTML='<p class="note">cowork/progress.json 을 읽지 못했습니다. 게시본이 아직 올라가지 않았거나 경로·형식이 다릅니다. 아래 금지 4조항은 고정 표시입니다.</p>'+hvBan();return}
 }else st.innerHTML='<span class="tag ok">게시본 읽음</span> 확인 '+hvEsc(hvLastOk)+' · 30초마다 자동 새로고침';
 var p=hvLast.p,it=p.items,now=new Date(),g='';
 var wait=0,pass=0;it.forEach(function(x){if(x.score>=70&&x.score<90)wait++;if(x.score>=90&&x.score<100)pass++});
 var md=p.models||{};
 var ms=['Opus','Sonnet'].map(function(k){return '<span><b>'+k+'</b> '+(md[k]==null?'-':hvEsc(md[k])+'%')+'</span>'}).join('');
 var T12=function(a){return tbl(['#','일','담당','상태','진척도'],a.map(function(x){return ['<b>'+hvEsc(x.id)+'</b>',hvEsc(x.title),hvEsc(x.owner),hvEsc(x.status),hvEsc(x.score)+'%']}))+'<p class="note">원천 cowork/progress.json(COM 진행상황판 게시본) · 갱신 '+hvEsc(p.updated||'-')+'</p>'};
 g+='<div class="grid">'+card('주간 진척도',hvEsc(p.week)+'%','전체 '+it.length+'건 평균 · 화 18:00 마감',null,function(){return T12(it)})+card('모델별 진척도','<span class="sc12-ms">'+ms.replace(/<span>/g,'<span class="sc12-m">')+'</span>','담당 W# 평균 · '+hvEsc(String(p.updated||'확인 안 됨').slice(5,16).replace('T',' '))+' 값',null,function(){return tbl(['모델','진척도','담당 W#'],['Opus','Sonnet'].map(function(k){var a=it.filter(function(x){return x.owner===k});return [k,(md[k]==null?'-':hvEsc(md[k])+'%'),a.map(function(x){return hvEsc(x.id)+' '+hvEsc(x.score)+'%'}).join(' · ')||'-']}))+'<p class="note">원천 cowork/progress.json · 갱신 '+hvEsc(p.updated||'-')+' — 이 시각의 값이며 그 뒤 다시 내지 않았습니다(상황판 원천은 노트북). Haiku는 11/04 20:01 배제되었고, 표의 Haiku 값은 배제 전 담당(W8, 11/04 19:41 승인) 값입니다(원천 cowork/ctl/model_control_status.tsv).</p>'})+card('완료·검수 대기',wait+'건','Fable 통과 '+pass+'건 · 승인 반영 '+it.filter(function(x){return x.score>=100}).length+'건',null,function(){return '<h4>완료·검수 대기(70~89%)</h4>'+T12(it.filter(function(x){return x.score>=70&&x.score<90}))+'<h4>Fable 통과(90~99%) · 승인 반영(100%)</h4>'+T12(it.filter(function(x){return x.score>=90}))})+card('마지막 갱신',hvEsc(String(p.updated||'-').replace('T',' ').replace(/:\d\d(\+.*)?$/,'')),'progress.json updated',null,function(){return tbl(['항목','값'],[['원천','HiBiz\\01_클로_소통(COM)\\CoWork_진행상황판 → 게시 cowork/progress.json'],['갱신(updated)',hvEsc(p.updated||'-')],['이 화면이 읽은 시각',hvEsc(hvLastOk||'-')],['읽는 주기','30초']])})+'</div>';
 /* SC-10 6단 막대(계층규칙 2.0 4장, T-W19-05 Opus 워크 0006): T·TT·W·WW·M·MM — 원천 progress.json six(tools/gen_six.py 산출) */
 g+='<h3>계층 진척(6단: T · TT · W · WW · M · MM)</h3>'+(Array.isArray(p.six)?'<div class="sc12-six">'+p.six.map(function(x){var v=Math.max(0,Math.min(100,+x.v||0));return '<div class="sc12-sx"><b>'+hvEsc(x.k)+'</b><div class="sc12-bar"><i class="'+hvStage(v)+'" style="width:'+v+'%"></i></div><span class="sc12-n">'+v+'%</span><span class="sc12-d">'+hvEsc(x.s)+'</span></div>'}).join('')+'</div><p class="note">원천 cowork/progress.json six · T=태스크 완료 비율 · TT=현재 워크 TT 완료 비율 · W=W# 평균 · WW·M·MM=Fable 집계 · 갱신 '+hvEsc(p.updated||'-')+'</p>':hvNo('progress.json six 없음'));
 g+='<h3>W1~W'+it.length+' 진척도</h3><div class="tw"><table class="sc12-t"><thead><tr><th>#</th><th>일</th><th>담당</th><th>마감</th><th>상태</th><th class="sc12-bc">진척도</th><th>태스크</th><th>산출물</th><th>자가검수</th><th>Fable 판정</th><th>승인</th></tr></thead><tbody>';
 var tg={'대기':'smp','진행 가능':'gray','진행 중':'warn','완료·검수 대기':'ok','Fable 통과':'ok','통과':'ok','완료·승인':'ok','승인·반영':'ok','재작업':'bad','위반':'bad'};
 var PG12=hvPage(it.slice().reverse(),'12w');PG12.rows.forEach(function(x){
  var d=hvDue(x.due),od=d&&now>d&&x.score<70,tk=x.tasks||[],dn=tk.filter(function(t){return /완료|검수|통과/.test(t.status)}).length,k=tg[x.status];
  g+='<tr'+(od?' class="sc12-od"':'')+'><td><b>'+hvEsc(x.id)+'</b></td><td>'+hvEsc(x.title)+'<div class="sc12-d">난이도 '+hvEsc(x.difficulty||'-')+'</div></td><td>'+hvEsc(x.owner)+'</td><td>'+hvEsc(x.due)+(od?' <span class="tag bad">기한 지남</span>':'')+'</td><td>'+(k?'<span class="tag '+k+'">'+hvEsc(x.status)+'</span>':hvEsc(x.status))+'</td>'
  +'<td class="sc12-bc"><div class="sc12-bar"><i class="'+hvStage(x.score)+'" style="width:'+Math.max(0,Math.min(100,+x.score||0))+'%"></i></div><span class="sc12-n">'+hvEsc(x.score)+'</span></td>'
  +'<td>'+(tk.length?'<div class="sc12-bar sm"><i class="s70" style="width:'+Math.round(dn*100/tk.length)+'%"></i></div><span class="sc12-n">'+dn+'/'+tk.length+'</span>':'<span class="sc12-n">-</span>')+'</td>'
  +'<td class="sc12-o">'+hvEsc(x.output||'-')+'</td><td>'+hvEsc(x.self_check||'-')+'</td><td>'+hvEsc(x.fable||'-')+'</td><td>'+hvEsc(x.approved||'-')+'</td></tr>';
 });
 g+='</tbody></table></div>'+hvPager(PG12,'건','hvSC12Paint')+'<p class="note"><span class="sc12-lg"><i class="s0"></i>0 대기</span><span class="sc12-lg"><i class="s30"></i>30 진행 중</span><span class="sc12-lg"><i class="s70"></i>70 완료·검수 대기</span><span class="sc12-lg"><i class="s90"></i>90 Fable 통과</span><span class="sc12-lg"><i class="s100"></i>100 승인·반영</span> · 마감 지난 미완은 빨간 테두리</p>';
 g+=hvTG12(hvLast.log&&hvLast.log.ok?hvLast.log.d:'');/* W28-03 A-02 */
 g+='<h3>일일보고</h3>';
 var R=hvLast.rep;
 if(!R.ok||!Array.isArray(R.d))g+='<p class="note">reports/index.json 을 읽지 못했습니다.</p>';
 else if(!R.d.length)g+='<p class="note">아직 게시된 일일보고가 없습니다.</p>';
 else{
  g+='<div class="sc12-rp">';
  R.d.slice().sort(function(a,c){return String(c.date||'').localeCompare(String(a.date||''))||String(c.file||'').localeCompare(String(a.file||''))}).forEach(function(r){
   var f=String(r.file||''),okf=/^[0-9A-Za-z가-힣._-]+$/.test(f),op=!!hvOpen[f];
   g+='<div class="sc12-r"><button type="button" class="sc12-rh" title="'+hvEsc((r.date||'-')+' · '+(r.model||'-')+' · '+(r.title||f))+'" '+(okf?'onclick="hvRep(this)" data-f="'+hvEsc(f)+'"':'disabled')+'><b>'+hvEsc(r.date||'-')+'</b> · '+hvEsc(r.model||'-')+' · '+hvEsc(r.title||f)+'</button><pre class="sc12-rb'+(op?'':' hide')+'">'+(op?'읽는 중…':'')+'</pre></div>';
  });
  g+='</div>';
 }
 g+='<h3>변경 로그 (최근 30줄)</h3>';
 var L=hvLast.log;
 if(!L.ok)g+='<p class="note">log.tsv 를 읽지 못했습니다.</p>';
 else{
  var ln=String(L.d).split(/\r?\n/).filter(function(x){return x.trim()}).slice(1).slice(-30).reverse();
  g+=ln.length?tbl(['시각','모델','W#','상태','메모'],ln.map(function(x){var c=x.split('\t');while(c.length<5)c.push('');return c.slice(0,5).map(hvEsc)})):'<p class="note">변경 기록이 아직 없습니다.</p>';
 }
 g+=hvBan();
 b.innerHTML=g;
 if(!fail&&!hvRe12&&!hvPgAll){hvRe12=true;try{hvPgFit('12','12w','hvSC12Paint')}finally{hvRe12=false}}else if(!fail){hvPgStatic('12')}
 Object.keys(hvOpen).forEach(function(f){if(hvOpen[f]){var h=b.querySelector('.sc12-rh[data-f="'+f.replace(/"/g,'')+'"]');if(h)hvRepLoad(h)}});
}
function hvBan(){return '<h3>금지 4조항 (전 모델 · 위반 시 즉시 중단)</h3><ol class="sc12-ban"><li>작업이 끝나기 전에 대화를 종료하지 않는다.</li><li>막히면 보고하고 기다린다(추측 진행 금지).</li><li>대표님께 일을 넘기지 않는다.</li><li>자동 실행·예약작업·훅·외부 설정(Cloudflare·GitHub·사이트 설정) 생성·변경 금지. 파일 이름 변경·복사·이동·삭제 금지. 산출물은 새 파일로 저장.</li></ol>'}
function hvRep(btn){
 var f=btn.getAttribute('data-f'),pre=btn.nextElementSibling;
 if(hvOpen[f]){hvOpen[f]=false;pre.classList.add('hide');return}
 hvOpen[f]=true;pre.classList.remove('hide');hvRepLoad(btn);
}
function hvRepLoad(btn){
 var f=btn.getAttribute('data-f'),pre=btn.nextElementSibling;
 hvFetch('cowork/reports/'+encodeURIComponent(f),'text').then(function(t){pre.textContent=t},function(e){pre.textContent='읽지 못했습니다 ('+e.message+')'});
}

var hvRe12=false;
