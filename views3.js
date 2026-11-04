var hvTY13=['위반','지적','지적(자가 발견)','질타','개선요청','유휴','장애'];/* 11/04 15:32 대표님 지시: 심각도 순서(위반 > 지적 > 지적(자가 발견) > 질타 > 개선요청 > 유휴, 장애는 빨간 바탕) */
/* SC-13 모델 통제 상황 — 데이터 연동 경로(대표님 지시 11/04 13:56·13:58): 원천 HiBiz\01_클로_소통(COM)\모델통제(CTL)\모델통제_통합이력.tsv·모델통제_현황.tsv → 게시 /cowork/ctl/model_control_history.tsv·model_control_status.tsv(원천 그대로 복사·푸시) → 화면 10초마다 읽음 */
var hvT13=null,hvLast13=null,hvLastOk13='',hvF13={m:'전체',t:'전체',u:'전체',p:'전체',c:'',x:'',f:'전체'};
/* 11/04 18:00 대표님: Fable 단계 = 대기(안 읽음) · 읽음 · 처리 중 · 처리 완료 — 이력 「Fable 확인」 칸 값은 Fable만 바꾼다 */
var HV_FB=['대기','읽음','처리 중','처리 완료'];var hvTR13={v:[],h:[],s:null,ok:''};
V['SC-13']=function(){
 setTimeout(hvSC13Start,0);
 return '<div id="sc13"><h2>SC-13 모델 통제 상황</h2><p class="lead">Fable · Opus · Sonnet · Haiku(그리고 기록상 모델 미상)의 지시 이행, 대표님 질타·개선요청·지적, 위반, 유휴(멈춤·불이행), 장애 이력입니다. 범위: HiBiz 관련 기록만(Mbiz 시기 기록은 원천 폴더 「보관_Mbiz이전(비반영)」에 보관, 이 화면에 반영하지 않음).</p><div class="sc13-path"><b>데이터 연동 경로</b> ① 원천: HiBiz\\01_클로_소통(COM)\\모델통제(CTL)\\모델통제_통합이력.tsv · 모델통제_현황.tsv (모델별 상세: 모델통제_Fable·Opus·Sonnet·Haiku.md) → ② 게시: hiven-ai-site /cowork/ctl/model_control_history.tsv · model_control_status.tsv (원천 파일을 그대로 복사해 푸시) → ③ 표시: 이 화면이 10초마다 읽음</div><p class="note" id="sc13-st">불러오는 중…</p><div id="sc13-b"></div></div>';
};
function hvSC13Start(){
 if(hvT13){clearInterval(hvT13);hvT13=null}
 hvSC13Load();
 hvT13=setInterval(function(){if(!$('sc13')){clearInterval(hvT13);hvT13=null;return}hvSC13Load()},10000);
}
function hvTsv(t){var L=String(t||'').split(/\r?\n/).filter(function(x){return x.trim()});var h=L.shift();h=h?h.split('\t'):[];return L.map(function(x){return x.split('\t')})}
function hvSC13Load(){
 Promise.all([hvFetch('cowork/ctl/trace_v.tsv','text'),hvFetch('cowork/ctl/trace_h.tsv','text'),hvFetch('cowork/ctl/trace_sum.json','json')]).then(function(t){hvTR13={v:hvTsv(t[0]),h:hvTsv(t[1]),s:t[2],ok:kst()}},function(){});
 Promise.all([hvFetch('cowork/ctl/model_control_history.tsv','text'),hvFetch('cowork/ctl/model_control_status.tsv','text')]).then(function(r){
  if(!$('sc13'))return;
  var T=hvTY13;/* 11/04 15:32 대표님 지시: 심각도 순서 */
  var ev=hvTsv(r[0]).map(function(c){return {no:c[0],date:c[1],hour:c[2],time:c[3],model:c[4],type:c[5],content:c[6],cause:c[7],action:c[8],status:c[9],fable:c[10]||'대기'}});
  var ms=hvTsv(r[1]).map(function(c){var cnt={};T.forEach(function(t){cnt[t]=0});ev.forEach(function(e){if(e.model===c[0]&&cnt[e.type]!=null)cnt[e.type]++});return {name:c[0],role:c[1],assigned:c[2],done:c[3],pending:c[4],counts:cnt,updated:c[5]}});
  hvLast13={types:T,events:ev,models:ms,updated:(ms[0]&&ms[0].updated)||''};hvLastOk13=kst();hvSC13Paint(false);
 },function(e){if($('sc13'))hvSC13Paint(true,e)});
}
function hvSC13Set(k,v){hvF13[k]=v;if(k==='m'||k==='t'||k==='f')hvF13.c='';if(k==='u')hvF13.p='전체';hvPgReset('13');hvSC13Paint(false)}
function hvWk(d){var x=new Date(d+'T00:00:00'),w=(x.getDay()+6)%7,m=new Date(x);m.setDate(x.getDate()-w);var e=new Date(m);e.setDate(m.getDate()+6);var f=function(z){return (z.getMonth()+1)+'/'+z.getDate()};return m.getFullYear()+'-'+pad(m.getMonth()+1)+'-'+pad(m.getDate())+'|'+f(m)+'~'+f(e)+' 주간'}
function hvKey(e,u){if(u==='시간별')return e.hour?(e.date+' '+e.hour+'시|'+e.date.slice(5).replace('-','/')+' '+e.hour+'시'):(e.date+' 99|'+e.date.slice(5).replace('-','/')+' 시각 미기재');if(u==='일별')return e.date+'|'+e.date.slice(5).replace('-','/');if(u==='주간별')return hvWk(e.date);if(u==='연별')return e.date.slice(0,4)+'|'+e.date.slice(0,4)+'년';if(u==='전체')return 'ALL|전체 누적';return e.date.slice(0,7)+'|'+e.date.slice(0,4)+'년 '+(+e.date.slice(5,7))+'월'}
/* 구간(하위) 버튼: 시간별→일, 일별·주간별→월, 월별·연별→연 */
function hvPar(e,u){if(u==='시간별')return hvKey(e,'일별');if(u==='일별'||u==='주간별')return hvKey(e,'월별');if(u==='월별'||u==='연별')return hvKey(e,'연별');return ''}
/* 시점·기간: 일자 선택(시작일~종료일) + 시간 선택(시작~종료, 최소 단위 분) + 빠른 선택. 하루면 시간별, 여러 날이면 일별로 표시 */
function hvDs(x){return x.getFullYear()+'-'+pad(x.getMonth()+1)+'-'+pad(x.getDate())}
function hvHm(e){if(!e.hour)return '';var m=String(e.time||'').match(/(\d{1,2}):(\d{2})/);if(m&&+m[1]===+e.hour)return pad(+m[1])+':'+m[2];return pad(+e.hour)+':00'}
function hvSC13Rng(a,b,ta,tb){hvF13.a=a;hvF13.b=b;hvF13.ta=ta||'00:00';hvF13.tb=tb||'23:59';hvSC13Paint(false)}
function hvSelUI(A,B,D0,D1,TA,TB){var n=new Date(),t=hvDs(n),w=new Date(n);w.setDate(n.getDate()-6);var m=t.slice(0,8)+'01',h=new Date(n.getTime()-3600000),hm=function(z){return pad(z.getHours())+':'+pad(z.getMinutes())};
 var q=[['전체',D0,D1,'00:00','23:59'],['최근 1시간',hvDs(h),t,hm(h),hm(n)],['오늘',t,t,'00:00','23:59'],['최근 7일',hvDs(w),t,'00:00','23:59'],['이번 달',m,t,'00:00','23:59']];var hit=-1;q.forEach(function(x,i){if(hit<0&&A===x[1]&&B===x[2]&&TA===x[3]&&TB===x[4])hit=i});
 return '<div class="sc13-f sc13-l sc13-lw"><span class="sc13-lb w">일자 선택</span><input type="date" class="sc13-d" value="'+A+'" onchange="hvSC13Set(\'a\',this.value)"><span class="sc13-pr">~</span><input type="date" class="sc13-d" value="'+B+'" onchange="hvSC13Set(\'b\',this.value)"></div>'
 +'<div class="sc13-f sc13-l sc13-lw"><span class="sc13-lb w">시간 선택</span><input type="time" step="60" class="sc13-d" value="'+TA+'" onchange="hvSC13Set(\'ta\',this.value||\'00:00\')"><span class="sc13-pr">~</span><input type="time" step="60" class="sc13-d" value="'+TB+'" onchange="hvSC13Set(\'tb\',this.value||\'23:59\')"></div>'
 +'<div class="sc13-f sc13-l sc13-lw"><span class="sc13-lb w">빠른 선택</span>'+q.map(function(x,i){return '<button type="button" class="'+(i===hit?'on':'')+'" onclick="hvSC13Rng(\''+x[1]+'\',\''+x[2]+'\',\''+x[3]+'\',\''+x[4]+'\')">'+x[0]+'</button>'}).join('')+'</div>'}
function hvAgg(d){
 var U=['전체','시간별','일별','주간별','월별','연별','시점·기간'];if(!hvF13.ta)hvF13.ta='00:00';if(!hvF13.tb)hvF13.tb='23:59';var DS=d.events.map(function(e){return e.date}).sort(),D0=DS[0]||'',D1=DS[DS.length-1]||'';if(!hvF13.a)hvF13.a=D0;if(!hvF13.b)hvF13.b=D1;var SEL=hvF13.u==='시점·기간';if(U.indexOf(hvF13.u)<0)hvF13.u='전체';if(!hvF13.p)hvF13.p='전체';
 var u=hvF13.u,ms=d.models.map(function(m){return m.name}),G={},K=[],PK=[];
 if(u!=='전체'&&!SEL)d.events.forEach(function(e){var q=hvPar(e,u);if(PK.indexOf(q)<0)PK.push(q)});PK.sort();
 if(hvF13.p!=='전체'&&PK.indexOf(hvF13.p)<0)hvF13.p='전체';
 var A=hvF13.a<=hvF13.b?hvF13.a:hvF13.b,B=hvF13.a<=hvF13.b?hvF13.b:hvF13.a;
 var S0=A+' '+hvF13.ta,S1=B+' '+hvF13.tb,FD=hvF13.ta==='00:00'&&hvF13.tb==='23:59',NX=0;
 var ev=d.events.filter(function(e){if(!SEL)return hvF13.p==='전체'||hvPar(e,u)===hvF13.p;var m=hvHm(e);if(!m){var ok=e.date>=A&&e.date<=B;if(ok&&!FD){NX++;return false}return ok}var t=e.date+' '+m;return t>=S0&&t<=S1});
 ev.forEach(function(e){var k=hvKey(e,SEL?(A===B?'시간별':'일별'):u);if(!G[k]){G[k]=[];K.push(k)}G[k].push(e)});
 K.sort();var cum=0,mx=1,rows=K.map(function(k){var a=G[k];cum+=a.length;if(a.length>mx)mx=a.length;return {k:k,a:a,cum:cum}});var ALLCUM=rows.length?rows[rows.length-1].cum:1,PGA=hvPage(rows.slice().reverse(),'13a');
 var g='<h3>기간별 집계 · 누적</h3><div class="sc13-f sc13-l sc13-lw"><span class="sc13-lb w">집계 단위</span>'+U.map(function(x){return '<button type="button" class="'+(u===x?'on':'')+'" onclick="hvSC13Set(\'u\',\''+x+'\')">'+x+'</button>'}).join('')+'</div>'
 +(SEL?hvSelUI(A,B,D0,D1,hvF13.ta,hvF13.tb):'')+(u==='전체'||SEL?'':'<div class="sc13-f sc13-l sc13-lw"><span class="sc13-lb w">구간</span>'+['전체'].concat(PK).map(function(x){var lb=x==='전체'?'전체':x.split('|')[1];return '<button type="button" class="'+(hvF13.p===x?'on':'')+'" onclick="hvSC13Set(\'p\',\''+x+'\')">'+hvEsc(lb)+'</button>'}).join('')+'</div>')
 +'<div class="sc13-f sc13-pr">기간 '+(u==='전체'?(function(){var ds=ev.map(function(e){return e.date}).sort();return ds.length?hvEsc(ds[0].slice(5).replace('-','/'))+' ~ '+hvEsc(ds[ds.length-1].slice(5).replace('-','/'))+' · 전체 누적 '+ds.length+'건</div>':'-</div>'})():'')+(u==='전체'?'':hvEsc(rows.length?rows[0].k.split('|')[1]:'-')+' ~ '+hvEsc(rows.length?rows[rows.length-1].k.split('|')[1]:'-')+' · '+rows.length+'개 구간'+(SEL?' · '+ev.length+'건'+(NX?' · 시각 미기재 '+NX+'건 제외':''):'')+'</div>');
 g+='<div class="tw"><table class="sc13-t sc13-ag"><thead><tr><th>기간</th>'+ms.map(function(m){return '<th>'+hvEsc(m)+'</th>'}).join('')+hvTY13.map(function(x){return '<th>'+hvEsc(x)+'</th>'}).join('')+'<th>합계</th><th>누적</th><th class="sc13-bc">합계 / 누적</th></tr></thead><tbody>';
 PGA.rows.forEach(function(r){var c=function(f){return r.a.filter(f).length},t=function(x){return c(function(e){return e.type===x})};
  g+='<tr><td class="sc13-nw"><b>'+hvEsc(r.k.split('|')[1])+'</b></td>'+ms.map(function(m){var n=c(function(e){return e.model===m});return '<td class="sc13-n">'+(n||'')+'</td>'}).join('')
  +hvTY13.map(function(x){var n=t(x);return '<td class="sc13-n'+(n&&(x==='위반'||x==='장애')?' sc13-hot':'')+'">'+(n||'')+'</td>'}).join('')
  +'<td class="sc13-n"><b>'+r.a.length+'</b></td><td class="sc13-n">'+r.cum+'</td>'
  +'<td class="sc13-bc"><div class="sc13-bar"><i style="width:'+Math.round(r.a.length*100/mx)+'%"></i></div><div class="sc13-bar cum"><i style="width:'+Math.round(r.cum*100/ALLCUM)+'%"></i></div></td></tr>'});
 g+='</tbody></table></div>'+hvPager(PGA,'개 구간','hvSC13Paint')+'<p class="note">막대 위: 그 기간 건수(가장 많은 기간 = 100%) · 막대 아래: 누적 건수(전체 = 100%). 시각이 없는 기록은 시간별에서 「시각 미기재」로 묶습니다.</p>';
 return g+hvTrend(d);
}

function hvSC13Paint(fail,err){
 var st=$('sc13-st'),b=$('sc13-b');if(!st||!b)return;
 if(fail){st.innerHTML='<span class="tag bad">게시본 없음</span> 마지막 성공 시각 '+(hvLastOk13?hvEsc(hvLastOk13):'없음')+' · 30초 뒤 다시 시도'+(err?' ('+hvEsc(err.message)+')':'');if(!hvLast13){b.innerHTML='<p class="note">cowork/ctl/ 게시본(model_control_history.tsv·model_control_status.tsv)을 읽지 못했습니다.</p>';return}}
 else st.innerHTML='<span class="tag ok">게시본 읽음</span> 확인 '+hvEsc(hvLastOk13)+' · 원천 갱신 '+hvEsc(hvLast13.updated)+' · 10초마다 자동 새로고침';
 var d=hvLast13,T=d.types||[],ev=d.events,g='';
 var dts=ev.map(function(e){return e.date}).sort(),tot=ev.length,open=ev.filter(function(e){return e.status!=='조치 완료'}).length,rb=ev.filter(function(e){return e.type==='질타'}).length,vi=ev.filter(function(e){return e.type==='위반'}).length,jj=ev.filter(function(e){return /^지적/.test(e.type)}).length,fw=ev.filter(function(e){return e.fable==='대기'}).length;
 g+='<div class="grid sc13-cards">'+hvCB('','전체 이력',tot,(dts.length?dts[0].slice(5)+' ~ '+dts[dts.length-1].slice(5):'-')+' 누적')+hvCB('vi','위반',vi,'가장 심각')+hvCB('jj','지적',jj,'자가 발견 포함')+hvCB('rb','대표님 질타',rb,'「질타」 구분')+hvCB('op','조치 진행 중',open,open?'처리 중·결과 미확정':'모두 조치 완료')+hvCB('fw','Fable 확인','대기 '+fw,'읽음 '+ev.filter(function(e){return e.fable==='읽음'}).length+' · 처리 중 '+ev.filter(function(e){return e.fable==='처리 중'}).length+' · 완료 '+ev.filter(function(e){return e.fable==='처리 완료'}).length)+'</div><p class="note">상자를 누르면 아래 「이력」 표에 해당 기록만 보입니다. 한 번 더 누르거나 「전체 보기」를 누르면 해제됩니다.</p>';
 g+=hvX13();
 g+=hvAgg(d);
 g+='<h3>모델별 현황</h3><div class="tw"><table class="sc13-t"><thead><tr><th>모델</th><th>역할</th><th>오늘 배포 작업</th><th>완료</th><th>남은 일</th>'+T.map(function(t){return '<th>'+hvEsc(t)+'</th>'}).join('')+'<th>합계</th></tr></thead><tbody>';
 var PGM=hvPage(d.models,'13m');PGM.rows.forEach(function(m){var c=m.counts||{},s=0;T.forEach(function(t){s+=(+c[t]||0)});
  g+='<tr><td><b>'+hvEsc(m.name)+'</b></td><td>'+hvEsc(m.role)+'</td><td>'+hvEsc(m.assigned)+'</td><td>'+hvEsc(m.done)+'</td><td>'+hvEsc(m.pending)+'</td>'+T.map(function(t){var n=+c[t]||0;return '<td class="sc13-n'+(n&&(t==='위반'||t==='장애')?' sc13-hot':'')+'">'+n+'</td>'}).join('')+'<td class="sc13-n"><b>'+s+'</b></td></tr>'});
 g+='</tbody></table></div>'+hvPager(PGM,'개 모델','hvSC13Paint');
 var ms=['전체'].concat(d.models.map(function(m){return m.name})),ts=['전체'].concat(T);
 g+='<h3>이력</h3><div class="sc13-f sc13-l"><span class="sc13-lb">모델</span>'+ms.map(function(x){return '<button type="button" class="'+(hvF13.m===x?'on':'')+'" onclick="hvSC13Set(\'m\',\''+x+'\')">'+x+'</button>'}).join('')+'</div><div class="sc13-f sc13-l"><span class="sc13-lb">구분</span>'+ts.map(function(x){return '<button type="button" class="'+(hvF13.t===x?'on':'')+'" onclick="hvSC13Set(\'t\',\''+x+'\')">'+x+'</button>'}).join('')+'</div>'+'<div class="sc13-f sc13-l"><span class="sc13-lb">Fable</span>'+['전체'].concat(HV_FB,['조치 완료']).map(function(x){var n=x==='전체'?ev.length:x==='조치 완료'?ev.filter(function(e){return e.status==='조치 완료'}).length:ev.filter(function(e){return e.fable===x}).length;return '<button type="button" class="'+(hvF13.f===x?'on':'')+'" onclick="hvSC13Set(\'f\',\''+x+'\')">'+x+' '+n+'</button>'}).join('')+'</div>';
 var tg={'위반':'v1','지적':'v2','지적(자가 발견)':'v3','질타':'v4','개선요청':'v5','유휴':'v6','장애':'v7'};
 var rows=ev.filter(function(e){return (hvF13.m==='전체'||e.model===hvF13.m)&&(hvF13.t==='전체'||e.type===hvF13.t)&&hvCF(e)&&(hvF13.f==='전체'||(hvF13.f==='조치 완료'?e.status==='조치 완료':e.fable===hvF13.f))}).slice().reverse(),PGH=hvPage(rows,'13h');rows=PGH.rows;
 if(hvF13.c)g+='<div class="sc13-sel"><span class="tag sel">선택: '+hvEsc(HV_CB[hvF13.c])+' '+PGH.tot+'건</span><button type="button" onclick="hvCBgo(\'\')">전체 보기</button></div>';
 g+='<div class="tw" id="sc13-hist"><table class="sc13-t"><thead><tr><th>#</th><th>날짜</th><th>시각</th><th>모델</th><th>구분</th><th>대표님 지시·질타 요지</th><th>원인</th><th>조치</th><th>상태</th><th>Fable</th></tr></thead><tbody>';
 g+=rows.length?rows.map(function(e){return '<tr class="sc13-r" onclick="this.classList.toggle(\'sc13-open\')"><td>'+hvEsc(e.no)+'</td><td class="sc13-nw">'+hvEsc(e.date)+'</td><td class="sc13-nw">'+hvEsc(e.time)+'</td><td><b>'+hvEsc(e.model)+'</b></td><td><span class="tag '+(tg[e.type]||'gray')+'">'+hvEsc(e.type)+'</span></td><td class="sc13-cl"><div title="'+hvEsc(e.content)+'">'+hvEsc(e.content)+'</div></td><td class="sc13-cl"><div title="'+hvEsc(e.cause)+'">'+hvEsc(e.cause)+'</div></td><td class="sc13-cl"><div title="'+hvEsc(e.action)+'">'+hvEsc(e.action)+'</div></td><td><span class="tag '+(e.status==='조치 완료'?'ok':'warn')+'">'+hvEsc(e.status)+'</span></td><td><span class="tag '+({'대기':'gray','읽음':'smp','처리 중':'warn','처리 완료':'ok'}[e.fable]||'gray')+'">'+hvEsc(e.fable)+'</span></td></tr><tr class="sc13-dt"><td colspan="10">'+hvLinkDt(e)+'</td></tr>'}).join(''):'<tr><td colspan="10">해당 이력이 없습니다.</td></tr>';
 g+='</tbody></table></div>'+hvPager(PGH,'건','hvSC13Paint')+'<p class="note">긴 글은 2줄까지 보이고 「…」로 줄입니다. 줄을 누르면 전문과 함께 「연결 지시·처리 결과」(지시 추적 매트릭스)가 펼쳐집니다. 기록 규칙: 질타·개선요청·지적·위반·유휴·장애가 생기면 해당 모델이 즉시 원천(HiBiz\\01_클로_소통(COM)\\모델통제(CTL)\\모델통제_통합이력.tsv·모델별 파일)에 한 줄 추가하고, 게시본에 그대로 반영하며, Fable이 「체크」 때 확인합니다. 자동 실행 장치는 쓰지 않습니다(금지 4조항).</p>';
 g+=hvBan();
 b.innerHTML=g;
 if(!fail&&!hvRe13&&!hvPgAll){hvRe13=true;try{hvPgFit('13','13h','hvSC13Paint')}finally{hvRe13=false}}else if(!fail){hvPgStatic('13')}
}
var hvRe13=false;

/* 11/04 17:27·17:28 대표님 지시: 요약 상자 버튼화 + 지시 추적 매트릭스 종단·횡단 교차 검사 결과값 표시 */
var HV_CB={'':'전체 이력',vi:'위반',jj:'지적',rb:'대표님 질타',op:'조치 진행 중',fw:'Fable 확인 대기'};/* 상자 값 = 대기(안 읽음) 건수 */
function hvCF(e){var c=hvF13.c;if(!c)return true;if(c==='vi')return e.type==='위반';if(c==='jj')return /^지적/.test(e.type);if(c==='rb')return e.type==='질타';if(c==='op')return e.status!=='조치 완료';if(c==='fw')return e.fable==='대기';return true}
function hvCB(k,lb,n,sub){var on=hvF13.c===k;return '<button type="button" class="card sc13-cb'+(on?' on':'')+(k==='vi'&&n?' hot':'')+(k==='fw'?' lsky':'')+(k===''?' navy':'')+'" aria-pressed="'+(on?'true':'false')+'" onclick="hvCBgo(\''+k+'\')"><span class="k">'+lb+'</span><span class="v">'+n+'건</span><span class="s">'+sub+'</span></button>'}
function hvCBgo(k){hvF13.c=(hvF13.c===k?'':k);hvF13.m='전체';hvF13.t='전체';hvF13.f='전체';hvPgReset('13h');hvSC13Paint(false);var h=$('sc13-hist');if(h&&hvF13.c){var y=h.getBoundingClientRect().top+scrollY-120;scrollTo({top:y,behavior:'smooth'})}}
function hvLinkDt(e){var k='이력'+e.no,L=hvTR13.v.filter(function(r){return (r[6]||'').split('; ').indexOf(k)>=0}),H=hvTR13.h.filter(function(r){return r[0]===k})[0];
 var g='<div class="sc13-lk"><b>조치 결과</b> '+hvEsc(e.status)+(e.action?' — '+hvEsc(e.action):'')+'<br><b>연결 지시</b> ';
 if(!hvTR13.ok)return g+'지시 추적 매트릭스 게시본을 읽지 못함</div>';
 g+=L.length?L.map(function(r){var t=r[3]||'';return '<span class="sc13-ln">#'+hvEsc(r[0])+' '+hvEsc(r[2])+' · '+hvEsc(t.slice(0,70))+(t.length>70?'…':'')+' → '+hvEsc(r[10])+' · <b>'+hvEsc(r[12])+'</b></span>'}).join(''):'<span class="sc13-ln">'+hvEsc(H?H[8]:'연결 없음')+'</span>';
 return g+'</div>'}
function hvXgo(k){hvF13.x=(hvF13.x===k?'':k);hvPgReset('13x');hvSC13Paint(false)}
var HV_XS={'결과 미확정(조치 진행 중)':'결과 미확정','지시만(기록 없음)':'지시만','기록만(지시 연결 없음)':'기록만','자체 기록(지시 아님)':'자체 기록','범위 밖(11/04 이전, 채팅 원문 미보유)':'범위 밖','조치 결과 없음':'결과 없음'};
function hvX13(){var S=hvTR13.s;if(!S)return '<h3>지시 추적 교차 검사</h3><p class="note">지시 추적 매트릭스 게시본(cowork/ctl/trace_*.tsv)을 읽는 중이거나 없음</p>';
 var O=['일치','결과 미확정(조치 진행 중)','조치 결과 없음','지시만(기록 없음)','해당 없음'],OH=['일치','기록만(지시 연결 없음)','자체 기록(지시 아님)','범위 밖(11/04 이전, 채팅 원문 미보유)'],SH=HV_XS;
 var bt=function(dir,lst,cnt){return lst.map(function(x){var n=cnt[x]||0,k=dir+'|'+x,bad=n&&/지시만|기록만|결과 없음/.test(x),mid=n&&/미확정/.test(x);return '<button type="button" class="'+(hvF13.x===k?'on':'')+(bad?' bad':mid?' mid':'')+'" onclick="hvXgo(\''+k+'\')">'+hvEsc(SH[x]||x)+' '+n+'</button>'}).join('')};
 var g='<h3>지시 추적 교차 검사</h3><div class="sc13-f sc13-pr">'+hvEsc(S['기준'])+' · 산출 '+hvEsc(S['산출']||'')+'</div>'
 +'<div class="sc13-f sc13-l sc13-lw"><span class="sc13-lb w">종단</span>'+bt('v',O,S['종단'])+'</div>'
 +'<div class="sc13-f sc13-l sc13-lw"><span class="sc13-lb w">횡단</span>'+bt('h',OH,S['횡단'])+'</div>'
 +'<p class="note">종단 = 지시 1건마다 기록 → 조치 → 결과 → 처리까지 이어졌는지. 횡단 = 이력·대장 1건마다 어느 지시에서 왔는지 거꾸로 확인. 숫자 버튼을 누르면 해당 건만 펼칩니다.</p>';
 if(hvF13.x){var p=hvF13.x.split('|'),dir=p[0],j=p.slice(1).join('|'),A=(dir==='v'?hvTR13.v.filter(function(r){return r[12]===j}):hvTR13.h.filter(function(r){return r[8]===j})).slice().reverse(),PG=hvPage(A,'13x');
  g+='<div class="sc13-sel"><span class="tag sel">'+(dir==='v'?'종단':'횡단')+': '+hvEsc(SH[j]||j)+' '+A.length+'건</span><button type="button" onclick="hvXgo(\'\')">닫기</button></div><div class="tw"><table class="sc13-t"><thead><tr>'
  +(dir==='v'?'<th>#</th><th>시각</th><th>지시 원문</th><th>연결 이력</th><th>연결 대장</th><th>조치 결과</th><th>처리 경과</th><th>판정</th>':'<th>기록</th><th>날짜</th><th>구분</th><th>요지</th><th>상태</th><th>연결 지시</th><th>판정</th>')+'</tr></thead><tbody>'
  +(PG.rows.length?PG.rows.map(function(r){return '<tr class="sc13-r" onclick="this.classList.toggle(\'sc13-open\')">'+(dir==='v'?'<td>'+hvEsc(r[0])+'</td><td class="sc13-nw">'+hvEsc(r[2])+'</td><td class="sc13-cl"><div>'+hvEsc(r[3])+'</div></td><td>'+hvEsc(r[6])+'</td><td>'+hvEsc(r[5])+'</td><td class="sc13-cl"><div>'+hvEsc(r[8])+'</div></td><td class="sc13-cl"><div>'+hvEsc(r[9]||r[7])+'</div></td><td class="sc13-nw">'+hvEsc(r[10])+'</td>':'<td class="sc13-nw">'+hvEsc(r[0])+'</td><td class="sc13-nw">'+hvEsc(r[2])+'</td><td class="sc13-nw">'+hvEsc(r[3])+'</td><td class="sc13-cl"><div>'+hvEsc(r[4])+'</div></td><td class="sc13-cl"><div>'+hvEsc(r[6])+'</div></td><td>'+hvEsc(r[7])+'</td><td class="sc13-nw">'+hvEsc(SH[r[8]]||r[8])+'</td>')+'</tr>'}).join(''):'<tr><td colspan="8">해당 건이 없습니다.</td></tr>')
  +'</tbody></table></div>'+hvPager(PG,'건','hvSC13Paint')}
 return g}

/* 구분별 변동 추이 그래프(대표님 11/05 02:16·02:23): 현재 시점이 가운데, 좌 = 이전·우 = 다음. 단위(30초·분·시간·일·월·년)를 양 끝에서 고르고,
   ◀ ▶로 좌우 이동, 30초마다 현재 시점이 오른쪽으로 흐르며 칸이 자동으로 이어진다. 게시본 이력을 읽어 그리기만 한다(외부 라이브러리 없음). */
var hvTRC={'위반':'#c62828','지적':'#ef6c00','지적(자가 발견)':'#f9a825','질타':'#6a1b9a','개선요청':'#1565c0','유휴':'#78909c','장애':'#000000'};
var hvTRU=['30초','분','시간','일','월','년'],hvTRN=25,hvTRd=null,hvTRt=null;
function hvTrMs(e){var m=hvHm(e);var s=e.date+'T'+(m||'00:00')+':00+09:00';var t=Date.parse(s);return isNaN(t)?null:{t:t,exact:!!m}}
function hvTrK(t){var d=new Date(t+9*3600000);return {y:d.getUTCFullYear(),mo:d.getUTCMonth(),d:d.getUTCDate(),h:d.getUTCHours(),mi:d.getUTCMinutes(),s:d.getUTCSeconds()}}
function hvTrStart(t,u){var k=hvTrK(t),Z=function(y,mo,d,h,mi,s){return Date.UTC(y,mo,d,h,mi,s)-9*3600000};
 if(u==='30초')return Z(k.y,k.mo,k.d,k.h,k.mi,k.s<30?0:30);if(u==='분')return Z(k.y,k.mo,k.d,k.h,k.mi,0);if(u==='시간')return Z(k.y,k.mo,k.d,k.h,0,0);if(u==='일')return Z(k.y,k.mo,k.d,0,0,0);if(u==='월')return Z(k.y,k.mo,1,0,0,0);return Z(k.y,0,1,0,0,0)}
function hvTrAdd(t,u,n){var k=hvTrK(t),Z=function(y,mo,d,h,mi,s){return Date.UTC(y,mo,d,h,mi,s)-9*3600000};
 if(u==='30초')return t+n*30000;if(u==='분')return t+n*60000;if(u==='시간')return t+n*3600000;if(u==='일')return Z(k.y,k.mo,k.d+n,0,0,0);if(u==='월')return Z(k.y,k.mo+n,1,0,0,0);return Z(k.y+n,0,1,0,0,0)}
function hvTrLb(t,u){var k=hvTrK(t),p2=function(x){return (x<10?'0':'')+x};
 if(u==='30초')return p2(k.h)+':'+p2(k.mi)+':'+p2(k.s);if(u==='분')return p2(k.h)+':'+p2(k.mi);if(u==='시간')return p2(k.mo+1)+'/'+p2(k.d)+' '+p2(k.h)+'시';if(u==='일')return p2(k.mo+1)+'/'+p2(k.d);if(u==='월')return k.y+'/'+p2(k.mo+1);return k.y+'년'}
function hvTrend(d){hvTRd=d;if(!hvTRt)hvTRt=setInterval(function(){var el=document.getElementById('hvtr');if(!el){clearInterval(hvTRt);hvTRt=null;return}if(!hvF13.toff)el.innerHTML=hvTrBody()},30000);
 return '<h3>구분별 변동 추이</h3><div id="hvtr">'+hvTrBody()+'</div>'}
function hvTrBody(){var d=hvTRd;if(!d)return '';
 if(!hvF13.tu||hvTRU.indexOf(hvF13.tu)<0)hvF13.tu='시간';if(!hvF13.tm)hvF13.tm='모델 전체';if(!hvF13.tc)hvF13.tc='구간';if(!hvF13.th)hvF13.th={};if(!hvF13.toff)hvF13.toff=0;
 var u=hvF13.tu,ms=['모델 전체'].concat(d.models.map(function(m){return m.name}));if(ms.indexOf(hvF13.tm)<0)hvF13.tm='모델 전체';
 var now=Date.now(),half=Math.floor(hvTRN/2),c0=hvTrAdd(hvTrStart(now,u),u,hvF13.toff),B=[];for(var i=-half;i<=half;i++)B.push(hvTrAdd(c0,u,i));var Bend=hvTrAdd(B[B.length-1],u,1);
 var fine=(u==='30초'||u==='분'||u==='시간');
 var ev=d.events.filter(function(e){return hvF13.tm==='모델 전체'||e.model===hvF13.tm}).map(function(e){var x=hvTrMs(e);return x?{e:e,t:x.t,exact:x.exact}:null}).filter(function(x){return x&&(x.exact||!fine)});
 var nx=d.events.length-ev.length;
 var S=hvTY13.map(function(ty){var base=hvF13.tc==='누적'?ev.filter(function(x){return x.e.type===ty&&x.t<B[0]}).length:0,c=base;
  return {t:ty,v:B.map(function(b,i){var e2=i<B.length-1?B[i+1]:Bend;var n=ev.filter(function(x){return x.e.type===ty&&x.t>=b&&x.t<e2}).length;c+=n;return b>now?null:(hvF13.tc==='누적'?c:n)})}});
 var vis=S.filter(function(s){return !hvF13.th[s.t]}),mx=1;vis.forEach(function(s){s.v.forEach(function(x){if(x!==null&&x>mx)mx=x})});
 var ub=function(){return hvTRU.map(function(x){return '<button type="button" class="'+(u===x?'on':'')+'" onclick="hvTrSet(\'tu\',\''+x+'\')">'+x+'</button>'}).join('')};
 var btn=function(key,list){return list.map(function(x){return '<button type="button" class="'+(hvF13[key]===x?'on':'')+'" onclick="hvTrSet(\''+key+'\',\''+x+'\')">'+hvEsc(x)+'</button>'}).join('')};
 var g='<div class="sc13-f sc13-l sc13-lw"><span class="sc13-lb w">모델</span>'+btn('tm',ms)+'</div>'
 +'<div class="sc13-f sc13-l sc13-lw"><span class="sc13-lb w">값</span>'+btn('tc',['구간','누적'])+'</div>'
 +'<div class="sc13-f sc13-l sc13-lw"><span class="sc13-lb w">구분</span>'+hvTY13.map(function(t){var off=!!hvF13.th[t];return '<button type="button" class="'+(off?'':'on')+'" style="'+(off?'':'background:'+hvTRC[t]+';border-color:'+hvTRC[t]+';color:#fff')+'" onclick="hvTrTog(\''+t+'\')">'+hvEsc(t)+'</button>'}).join('')+'</div>';
 var W=1000,H=290,L=34,R=40,T=28,B2=40,pw=W-L-R,ph=H-T-B2,X=function(i){return L+i*pw/(B.length-1)},Y=function(v){return T+ph-v*ph/mx};
 var s='<svg viewBox="0 0 '+W+' '+H+'" width="100%" style="min-width:640px;font:11px sans-serif;display:block" role="img" aria-label="구분별 변동 추이">';
 var step=Math.max(1,Math.ceil(mx/5));for(var y=0;y<=mx;y+=step)s+='<line x1="'+L+'" x2="'+(W-R)+'" y1="'+Y(y)+'" y2="'+Y(y)+'" stroke="#e3e8f0"/><text x="'+(L-6)+'" y="'+(Y(y)+4)+'" text-anchor="end" fill="#667">'+y+'</text>';
 var ni=-1;B.forEach(function(b,i){var e2=i<B.length-1?B[i+1]:Bend;if(now>=b&&now<e2)ni=i});
 s+='<rect x="'+L+'" y="'+T+'" width="'+(ni>=0?X(ni)-L:(B[0]>now?0:pw))+'" height="'+ph+'" fill="#f4f7fc"/>';
 if(ni>=0)s+='<line x1="'+X(ni)+'" x2="'+X(ni)+'" y1="'+T+'" y2="'+(T+ph)+'" stroke="#16234d" stroke-width="1.6" stroke-dasharray="4 3"/><text x="'+X(ni)+'" y="'+(T-10)+'" text-anchor="middle" fill="#16234d" font-weight="700">현재 '+hvTrLb(now,u==='30초'?'30초':u==='분'?'30초':u)+'</text>';
 B.forEach(function(b,i){if(i%4===0||i===ni)s+='<text x="'+X(i)+'" y="'+(H-B2+16)+'" text-anchor="middle" fill="'+(i===ni?'#16234d':'#556')+'"'+(i===ni?' font-weight="700"':'')+'>'+hvTrLb(b,u)+'</text>'});
 vis.forEach(function(sr){var c=hvTRC[sr.t],pts=[];sr.v.forEach(function(v,i){if(v!==null)pts.push(X(i)+','+Y(v))});if(pts.length)s+='<polyline fill="none" stroke="'+c+'" stroke-width="2.2" points="'+pts.join(' ')+'"/>';
  sr.v.forEach(function(v,i){if(v)s+='<circle cx="'+X(i)+'" cy="'+Y(v)+'" r="3.2" fill="'+c+'"><title>'+hvEsc(hvTrLb(B[i],u)+' · '+sr.t+' '+v+'건')+'</title></circle>'})});
 s+='</svg>';
 var nav='<div class="sc13-f sc13-l" style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;justify-content:space-between"><span style="display:flex;gap:4px;flex-wrap:wrap">'+ub()+'</span>'
 +'<span style="display:flex;gap:4px"><button type="button" onclick="hvTrMove(-'+half+')">◀◀</button><button type="button" onclick="hvTrMove(-1)">◀ 이전</button><button type="button" class="'+(hvF13.toff?'':'on')+'" onclick="hvTrMove(0)">현재</button><button type="button" onclick="hvTrMove(1)">다음 ▶</button><button type="button" onclick="hvTrMove('+half+')">▶▶</button></span>'
 +'<span style="display:flex;gap:4px;flex-wrap:wrap">'+ub()+'</span></div>';
 var tot=hvTY13.map(function(t){var n=ev.filter(function(x){return x.e.type===t&&x.t>=B[0]&&x.t<Bend}).length;return '<span style="display:inline-block;margin:2px 10px 2px 0;white-space:nowrap"><i style="display:inline-block;width:10px;height:10px;border-radius:2px;background:'+hvTRC[t]+';margin-right:4px"></i>'+hvEsc(t)+' '+n+'</span>'}).join('');
 return g+nav+'<div class="tw" style="overflow-x:auto">'+s+'</div><p class="note">'+tot+'</p><p class="note">'+hvEsc(hvF13.tm)+' · '+u+' 단위 '+B.length+'칸(현재 시점 가운데 · 왼쪽 이전 · 오른쪽 다음) · '+(hvF13.toff?'이동 중(자동 흐름 멈춤 — 「현재」를 누르면 다시 흐름)':'30초마다 현재 시점이 오른쪽으로 흐르며 자동 갱신')+' · '+(hvF13.tc==='누적'?'누적 건수':'구간별 건수')+(fine&&nx?' · 시각 미기재 '+nx+'건은 일·월·년 단위에서 보임':'')+' · 원천 cowork/ctl/model_control_history.tsv</p>'}
function hvTrSet(k,v){hvF13[k]=v;if(k==='tu')hvF13.toff=0;var el=document.getElementById('hvtr');if(el)el.innerHTML=hvTrBody()}
function hvTrTog(t){if(!hvF13.th)hvF13.th={};hvF13.th[t]=!hvF13.th[t];var el=document.getElementById('hvtr');if(el)el.innerHTML=hvTrBody()}
function hvTrMove(n){hvF13.toff=n===0?0:(hvF13.toff||0)+n;var el=document.getElementById('hvtr');if(el)el.innerHTML=hvTrBody()}
