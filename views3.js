/* SC-13 모델 통제 상황 — 데이터 연동 경로(대표님 지시 11/04 13:56·13:58): 원천 HiBiz\01_클로_소통(COM)\모델통제(CTL)\모델통제_통합이력.tsv·모델통제_현황.tsv → 게시 /cowork/ctl/model_control_history.tsv·model_control_status.tsv(원천 그대로 복사·푸시) → 화면 30초마다 읽음 */
var hvT13=null,hvLast13=null,hvLastOk13='',hvF13={m:'전체',t:'전체',u:'전체',p:'전체'};
V['SC-13']=function(){
 setTimeout(hvSC13Start,0);
 return '<div id="sc13"><h2>SC-13 모델 통제 상황</h2><p class="lead">Fable · Opus · Sonnet · Haiku(그리고 기록상 모델 미상)의 지시 이행, 대표님 질타·개선요청·지적, 위반, 유휴(멈춤·불이행), 장애 이력입니다. 범위: HiBiz 관련 기록만(Mbiz 시기 기록은 원천 폴더 「보관_Mbiz이전(비반영)」에 보관, 이 화면에 반영하지 않음).</p><div class="sc13-path"><b>데이터 연동 경로</b> ① 원천: HiBiz\\01_클로_소통(COM)\\모델통제(CTL)\\모델통제_통합이력.tsv · 모델통제_현황.tsv (모델별 상세: 모델통제_Fable·Opus·Sonnet·Haiku.md) → ② 게시: hiven-ai-site /cowork/ctl/model_control_history.tsv · model_control_status.tsv (원천 파일을 그대로 복사해 푸시) → ③ 표시: 이 화면이 30초마다 읽음</div><p class="note" id="sc13-st">불러오는 중…</p><div id="sc13-b"></div></div>';
};
function hvSC13Start(){
 if(hvT13){clearInterval(hvT13);hvT13=null}
 hvSC13Load();
 hvT13=setInterval(function(){if(!$('sc13')){clearInterval(hvT13);hvT13=null;return}hvSC13Load()},30000);
}
function hvTsv(t){var L=String(t||'').split(/\r?\n/).filter(function(x){return x.trim()});var h=L.shift();h=h?h.split('\t'):[];return L.map(function(x){return x.split('\t')})}
function hvSC13Load(){
 Promise.all([hvFetch('cowork/ctl/model_control_history.tsv','text'),hvFetch('cowork/ctl/model_control_status.tsv','text')]).then(function(r){
  if(!$('sc13'))return;
  var T=['질타','개선요청','지적','지적(자가 발견)','위반','유휴','장애'];
  var ev=hvTsv(r[0]).map(function(c){return {no:c[0],date:c[1],hour:c[2],time:c[3],model:c[4],type:c[5],content:c[6],cause:c[7],action:c[8],status:c[9],fable:c[10]||'대기'}});
  var ms=hvTsv(r[1]).map(function(c){var cnt={};T.forEach(function(t){cnt[t]=0});ev.forEach(function(e){if(e.model===c[0]&&cnt[e.type]!=null)cnt[e.type]++});return {name:c[0],role:c[1],assigned:c[2],done:c[3],pending:c[4],counts:cnt,updated:c[5]}});
  hvLast13={types:T,events:ev,models:ms,updated:(ms[0]&&ms[0].updated)||''};hvLastOk13=kst();hvSC13Paint(false);
 },function(e){if($('sc13'))hvSC13Paint(true,e)});
}
function hvSC13Set(k,v){hvF13[k]=v;if(k==='u')hvF13.p='전체';hvPgReset('13');hvSC13Paint(false)}
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
 +'<div class="sc13-f sc13-pr">기간 '+(u==='전체'?(function(){var ds=ev.map(function(e){return e.date}).sort();return ds.length?hvEsc(ds[0].slice(5).replace('-','/'))+' ~ '+hvEsc(ds[ds.length-1].slice(5).replace('-','/'))+' · 전체 누적 '+ds.length+'건</div>':'-</div>'})():'')+(u==='전체'?'':hvEsc(rows.length?rows[rows.length-1].k.split('|')[1]:'-')+' ~ '+hvEsc(rows.length?rows[0].k.split('|')[1]:'-')+' · '+rows.length+'개 구간'+(SEL?' · '+ev.length+'건'+(NX?' · 시각 미기재 '+NX+'건 제외':''):'')+'</div>');
 g+='<div class="tw"><table class="sc13-t sc13-ag"><thead><tr><th>기간</th>'+ms.map(function(m){return '<th>'+hvEsc(m)+'</th>'}).join('')+'<th>질타</th><th>위반</th><th>유휴</th><th>장애</th><th>개선·지적</th><th>합계</th><th>누적</th><th class="sc13-bc">합계 / 누적</th></tr></thead><tbody>';
 PGA.rows.forEach(function(r){var c=function(f){return r.a.filter(f).length},t=function(x){return c(function(e){return e.type===x})};
  var oth=c(function(e){return /개선요청|지적/.test(e.type)});
  g+='<tr><td class="sc13-nw"><b>'+hvEsc(r.k.split('|')[1])+'</b></td>'+ms.map(function(m){var n=c(function(e){return e.model===m});return '<td class="sc13-n">'+(n||'')+'</td>'}).join('')
  +['질타','위반','유휴','장애'].map(function(x){var n=t(x);return '<td class="sc13-n'+(n?' sc13-hot':'')+'">'+(n||'')+'</td>'}).join('')
  +'<td class="sc13-n">'+(oth||'')+'</td><td class="sc13-n"><b>'+r.a.length+'</b></td><td class="sc13-n">'+r.cum+'</td>'
  +'<td class="sc13-bc"><div class="sc13-bar"><i style="width:'+Math.round(r.a.length*100/mx)+'%"></i></div><div class="sc13-bar cum"><i style="width:'+Math.round(r.cum*100/ALLCUM)+'%"></i></div></td></tr>'});
 g+='</tbody></table></div>'+hvPager(PGA,'개 구간','hvSC13Paint')+'<p class="note">막대 위: 그 기간 건수(가장 많은 기간 = 100%) · 막대 아래: 누적 건수(전체 = 100%). 시각이 없는 기록은 시간별에서 「시각 미기재」로 묶습니다.</p>';
 return g;
}

function hvSC13Paint(fail,err){
 var st=$('sc13-st'),b=$('sc13-b');if(!st||!b)return;
 if(fail){st.innerHTML='<span class="tag bad">게시본 없음</span> 마지막 성공 시각 '+(hvLastOk13?hvEsc(hvLastOk13):'없음')+' · 30초 뒤 다시 시도'+(err?' ('+hvEsc(err.message)+')':'');if(!hvLast13){b.innerHTML='<p class="note">cowork/ctl/ 게시본(model_control_history.tsv·model_control_status.tsv)을 읽지 못했습니다.</p>';return}}
 else st.innerHTML='<span class="tag ok">게시본 읽음</span> 확인 '+hvEsc(hvLastOk13)+' · 원천 갱신 '+hvEsc(hvLast13.updated)+' · 30초마다 자동 새로고침';
 var d=hvLast13,T=d.types||[],ev=d.events,g='';
 var dts=ev.map(function(e){return e.date}).sort(),tot=ev.length,open=ev.filter(function(e){return e.status!=='조치 완료'}).length,rb=ev.filter(function(e){return e.type==='질타'}).length,vi=ev.filter(function(e){return e.type==='위반'||e.type==='유휴'}).length,fw=ev.filter(function(e){return e.fable==='대기'}).length;
 g+='<div class="grid">'+card('전체 이력',tot+'건',(dts.length?dts[0]+' ~ '+dts[dts.length-1]:'-')+' 누적')+card('대표님 질타',rb+'건','「질타」 구분')+card('위반·유휴',vi+'건','지시 불이행·멈춤 포함')+card('조치 진행 중',open+'건',open?'W1·W4·W7 등에서 처리 예정':'모두 조치 완료')+card('Fable 확인 대기',fw+'건','「체크」 때 판정')+'</div>';
 g+=hvAgg(d);
 g+='<h3>모델별 현황</h3><div class="tw"><table class="sc13-t"><thead><tr><th>모델</th><th>역할</th><th>오늘 배포 작업</th><th>완료</th><th>남은 일</th>'+T.map(function(t){return '<th>'+hvEsc(t)+'</th>'}).join('')+'<th>합계</th></tr></thead><tbody>';
 var PGM=hvPage(d.models,'13m');PGM.rows.forEach(function(m){var c=m.counts||{},s=0;T.forEach(function(t){s+=(+c[t]||0)});
  g+='<tr><td><b>'+hvEsc(m.name)+'</b></td><td>'+hvEsc(m.role)+'</td><td>'+hvEsc(m.assigned)+'</td><td>'+hvEsc(m.done)+'</td><td>'+hvEsc(m.pending)+'</td>'+T.map(function(t){var n=+c[t]||0;return '<td class="sc13-n'+(n&&(t==='질타'||t==='위반'||t==='유휴')?' sc13-hot':'')+'">'+n+'</td>'}).join('')+'<td class="sc13-n"><b>'+s+'</b></td></tr>'});
 g+='</tbody></table></div>'+hvPager(PGM,'개 모델','hvSC13Paint');
 var ms=['전체'].concat(d.models.map(function(m){return m.name})),ts=['전체'].concat(T);
 g+='<h3>이력</h3><div class="sc13-f sc13-l"><span class="sc13-lb">모델</span>'+ms.map(function(x){return '<button type="button" class="'+(hvF13.m===x?'on':'')+'" onclick="hvSC13Set(\'m\',\''+x+'\')">'+x+'</button>'}).join('')+'</div><div class="sc13-f sc13-l"><span class="sc13-lb">구분</span>'+ts.map(function(x){return '<button type="button" class="'+(hvF13.t===x?'on':'')+'" onclick="hvSC13Set(\'t\',\''+x+'\')">'+x+'</button>'}).join('')+'</div>';
 var tg={'질타':'bad','위반':'bad','유휴':'bad','지적':'warn','지적(자가 발견)':'warn','개선요청':'gray','장애':'warn'};
 var rows=ev.filter(function(e){return (hvF13.m==='전체'||e.model===hvF13.m)&&(hvF13.t==='전체'||e.type===hvF13.t)}).slice().reverse(),PGH=hvPage(rows,'13h');rows=PGH.rows;
 g+='<div class="tw"><table class="sc13-t"><thead><tr><th>#</th><th>날짜</th><th>시각</th><th>모델</th><th>구분</th><th>대표님 지시·질타 요지</th><th>원인</th><th>조치</th><th>상태</th><th>Fable</th></tr></thead><tbody>';
 g+=rows.length?rows.map(function(e){return '<tr><td>'+hvEsc(e.no)+'</td><td class="sc13-nw">'+hvEsc(e.date)+'</td><td class="sc13-nw">'+hvEsc(e.time)+'</td><td><b>'+hvEsc(e.model)+'</b></td><td><span class="tag '+(tg[e.type]||'gray')+'">'+hvEsc(e.type)+'</span></td><td>'+hvEsc(e.content)+'</td><td>'+hvEsc(e.cause)+'</td><td>'+hvEsc(e.action)+'</td><td><span class="tag '+(e.status==='조치 완료'?'ok':'warn')+'">'+hvEsc(e.status)+'</span></td><td>'+hvEsc(e.fable)+'</td></tr>'}).join(''):'<tr><td colspan="10">해당 이력이 없습니다.</td></tr>';
 g+='</tbody></table></div>'+hvPager(PGH,'건','hvSC13Paint')+'<p class="note">기록 규칙: 질타·개선요청·지적·위반·유휴·장애가 생기면 해당 모델이 즉시 원천(HiBiz\\01_클로_소통(COM)\\모델통제(CTL)\\모델통제_통합이력.tsv·모델별 파일)에 한 줄 추가하고, 게시본에 그대로 반영하며, Fable이 「체크」 때 확인합니다. 자동 실행 장치는 쓰지 않습니다(금지 4조항).</p>';
 g+=hvBan();
 b.innerHTML=g;
 if(!fail&&hvPgMeasure()&&!hvRe13){hvRe13=true;hvSC13Paint(false);hvRe13=false}
}
var hvRe13=false;
