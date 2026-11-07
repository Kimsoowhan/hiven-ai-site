var hvTYT13=['지시거부','위반','지적','지적(자가 발견)','질타','개선요청','유휴','장애','지시'];/* 19:42 전수 검사: 표·집계·필터에서 빠져 있던 「지시거부」「지시」 구분 추가(확정 추이 그래프 hvTY13은 그대로) */
var hvTY13=['지시거부','위반','지적','지적(자가 발견)','질타','개선요청','유휴','장애'];/* 11/04 15:32 대표님 지시: 심각도 순서(위반 > 지적 > 지적(자가 발견) > 질타 > 개선요청 > 유휴, 장애는 빨간 바탕) */
/* SC-14 모델 통제 상황 — 데이터 연동 경로(대표님 지시 11/04 13:56·13:58): 원천 HiBiz\01_클로_소통(COM)\모델통제(CTL)\모델통제_통합이력.tsv·모델통제_현황.tsv → 게시 /cowork/ctl/model_control_history.tsv·model_control_status.tsv(원천 그대로 복사·푸시) → 화면 10초마다 읽음 */
var hvT13=null,hvLast13=null,hvLastOk13='',hvF13={m:'전체',t:'전체',u:'전체',p:'전체',c:'',x:'',f:'전체'};
/* 11/04 18:00 대표님: Fable 단계 = 대기(안 읽음) · 읽음 · 처리 중 · 처리 완료 — 이력 「Fable 확인」 칸 값은 Fable만 바꾼다 */
var HV_FB=['대기','읽음','처리 중','처리 완료','자기 행'];
function hvFbn13(v){v=(v||'').trim();if(!v)return '대기';if(/^처리 완료/.test(v)||v==='완료')return '처리 완료';if(/^처리 중/.test(v))return '처리 중';if(/^읽음/.test(v)||/^확인/.test(v))return '읽음';if(/자기 행/.test(v))return '자기 행';return '대기'}
var hvTR13={v:[],h:[],s:null,ok:''};
V['SC-14']=function(){
 setTimeout(hvSC13Start,0);
 return '<div id="sc13"><h2>SC-14 모델 통제 상황</h2><p class="lead">Fable · Opus · Sonnet · Haiku(그리고 기록상 모델 미상)의 대표님 지시, 질타·개선요청·지적, 위반·지시거부, 유휴(멈춤·불이행), 장애 이력입니다. 범위: HiBiz 관련 기록만(Mbiz 시기 기록은 원천 폴더 「보관_Mbiz이전(비반영)」에 보관, 이 화면에 반영하지 않음).</p><div class="sc13-path"><b>데이터 연동 경로</b> ① 원천: HiBiz\\01_클로_소통(COM)\\모델통제(CTL)\\모델통제_통합이력.tsv · 모델통제_현황.tsv (모델별 상세: 모델통제_Fable·Opus·Sonnet·Haiku.md) → ② 게시: hiven-ai-site /cowork/ctl/model_control_history.tsv · model_control_status.tsv (원천 파일을 그대로 복사해 푸시) → ③ 표시: 이 화면이 10초마다 읽음</div><p class="note" id="sc13-st">불러오는 중…</p><div id="sc13-b"></div></div>';
};
function hvSC13Start(){
 if(hvT13){clearInterval(hvT13);hvT13=null}
 hvSC13Load();
 hvT13=setInterval(function(){if(!$('sc13')){clearInterval(hvT13);hvT13=null;return}hvSC13Load()},10000);
}
function hvTsv(t){var L=String(t||'').split(/\r?\n/).filter(function(x){return x.trim()});var h=L.shift();h=h?h.split('\t'):[];return L.map(function(x){return x.split('\t')})}
function hvSC13Load(){
 Promise.all([hvFetch('cowork/ctl/trace_v.tsv','text'),hvFetch('cowork/ctl/trace_h.tsv','text'),hvFetch('cowork/ctl/trace_sum.json','json')]).then(function(t){hvTR13={v:hvTsv(t[0]),h:hvTsv(t[1]),s:t[2],ok:kst()}},function(){});
 hvFetch('cowork/ctl/phrase_scan.json','json').then(function(j){hvPS13=j},function(){});
 hvFetch('cowork/ctl/model_control_index.json','json').then(function(j){hvMX13=j},function(){});
 hvFetch('cowork/ctl/praise_watch_status.json','json').then(function(j){hvPW13=j},function(){hvPW13=null});
 hvFetch('cowork/ctl/praise_watch_review.tsv','text').then(function(t){hvPR13=hvTsv(t)},function(){hvPR13=null});
 hvFetch('cowork/ctl/praise_credit_ledger.tsv','text').then(function(t){hvLD13=hvTsv(t);if($('sc13')&&hvLast13)hvSC13Paint(false)},function(){});/* 20:18 대표님 지시: 칭찬 원장을 직접 읽어 집약 대기 없이 바로 카운트 */
 Promise.all([hvFetch('cowork/ctl/model_control_history.tsv','text'),hvFetch('cowork/ctl/model_control_status.tsv','text')]).then(function(r){
  if(!$('sc13'))return;
  var T=hvTYT13;/* 11/04 15:32 대표님 지시: 심각도 순서 */
  var ev=hvTsv(r[0]).map(function(c){return {no:c[0],date:c[1],hour:c[2],time:c[3],model:c[4],type:c[5],content:c[6],cause:c[7],action:c[8],fable:hvFbn13(c[10]),fraw:c[10]||'',sraw:c[9],status:/^완료/.test(c[9]||'')?'조치 완료':c[9]}});
  var ms=hvTsv(r[1]).map(function(c){var cnt={};T.forEach(function(t){cnt[t]=0});ev.forEach(function(e){if(e.model===c[0]&&cnt[e.type]!=null)cnt[e.type]++});return {name:c[0],role:c[1],assigned:c[2],done:c[3],pending:c[4],counts:cnt,updated:c[5]}});
  var have={};ms.forEach(function(m){have[m.name]=1});ev.forEach(function(e){if(have[e.model])return;have[e.model]=1;var cnt={};T.forEach(function(t){cnt[t]=0});ev.forEach(function(x){if(x.model===e.model&&cnt[x.type]!=null)cnt[x.type]++});ms.push({name:e.model,role:'기록상 표기(상태표에 행 없음)',assigned:'-',done:'-',pending:'-',counts:cnt,updated:''})});
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
 g+='<div class="tw"><table class="sc13-t sc13-ag"><thead><tr><th>기간</th>'+ms.map(function(m){return '<th>'+hvEsc(m)+'</th>'}).join('')+hvTYT13.map(function(x){return '<th'+(x==='지시거부'?' style="background:#7b1fa2;color:#fff;border:2px solid #ff00ff"':(x==='장애'?' style="background:#424242;color:#fff;border:2px solid #000"':''))+'>'+hvEsc(hvTL(x))+'</th>'}).join('')+'<th>합계</th><th>누적</th><th class="sc13-bc">합계 / 누적</th></tr></thead><tbody>';
 PGA.rows.forEach(function(r){var c=function(f){return r.a.filter(f).length},t=function(x){return c(function(e){return e.type===x})};
  g+='<tr><td class="sc13-nw"><b>'+hvEsc(r.k.split('|')[1])+'</b></td>'+ms.map(function(m){var n=c(function(e){return e.model===m});return '<td class="sc13-n">'+(n||'')+'</td>'}).join('')
  +hvTYT13.map(function(x){var n=t(x);return '<td class="sc13-n'+(n&&(x==='위반'||x==='지시거부'||x==='장애')?' sc13-hot':'')+'">'+(n||'')+'</td>'}).join('')
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
 g+='<div class="grid sc13-cards">'+hvCB('','전체 이력',tot,(dts.length?dts[0].slice(5)+' ~ '+dts[dts.length-1].slice(5):'-')+' 누적')+hvCB('vi','위반',vi,'가장 심각')+hvCB('jj','지적',jj,'자가 발견 포함')+hvCB('rb','대표님 질타',rb,'「질타」 구분')+hvCB('op','조치 진행 중',open,open?'처리 중·결과 미확정':'모두 조치 완료')+hvCB('fw','Fable 확인','대기 '+fw,'읽음 '+ev.filter(function(e){return e.fable==='읽음'}).length+' · 처리 중 '+ev.filter(function(e){return e.fable==='처리 중'}).length+' · 완료 '+ev.filter(function(e){return e.fable==='처리 완료'}).length+' · 자기 행 '+ev.filter(function(e){return e.fable==='자기 행'}).length)+'</div><p class="note">상자를 누르면 아래 「이력」 표에 해당 기록만 보입니다. 한 번 더 누르거나 「전체 보기」를 누르면 해제됩니다.</p>';
 g+=hvX13();
 g+=hvStat13(d);
 g+=hvAgg(d);
 g+='<h3>모델별 현황</h3><div class="tw"><table class="sc13-t"><thead><tr><th>모델</th><th>역할</th><th>오늘 배포 작업</th><th>완료</th><th>남은 일</th>'+T.map(function(t){return '<th>'+hvEsc(t)+'</th>'}).join('')+'<th>합계</th></tr></thead><tbody>';
 var PGM=hvPage(d.models,'13m');PGM.rows.forEach(function(m){var c=m.counts||{},s=0;T.forEach(function(t){s+=(+c[t]||0)});
  g+='<tr><td><b>'+hvEsc(m.name)+'</b></td><td>'+hvEsc(m.role)+'</td><td>'+hvEsc(m.assigned)+'</td><td>'+hvEsc(m.done)+'</td><td>'+hvEsc(m.pending)+'</td>'+T.map(function(t){var n=+c[t]||0;return '<td class="sc13-n'+(n&&(t==='위반'||t==='지시거부'||t==='장애')?' sc13-hot':'')+'">'+n+'</td>'}).join('')+'<td class="sc13-n"><b>'+s+'</b></td></tr>'});
 g+='</tbody></table></div>'+hvPager(PGM,'개 모델','hvSC13Paint');
 var ms=['전체'].concat(d.models.map(function(m){return m.name})),ts=['전체'].concat(T);
 g+='<h3>이력</h3><div class="sc13-f sc13-l"><span class="sc13-lb">모델</span>'+ms.map(function(x){return '<button type="button" class="'+(hvF13.m===x?'on':'')+'" onclick="hvSC13Set(\'m\',\''+x+'\')">'+x+'</button>'}).join('')+'</div><div class="sc13-f sc13-l"><span class="sc13-lb">구분</span>'+ts.map(function(x){return '<button type="button" class="'+(hvF13.t===x?'on':'')+'"'+' onclick="hvSC13Set(\'t\',\''+x+'\')">'+hvEsc(hvTL(x))+'</button>'}).join('')+'</div>'+'<div class="sc13-f sc13-l"><span class="sc13-lb">Fable</span>'+['전체'].concat(HV_FB,['조치 완료']).map(function(x){var n=x==='전체'?ev.length:x==='조치 완료'?ev.filter(function(e){return e.status==='조치 완료'}).length:ev.filter(function(e){return e.fable===x}).length;return '<button type="button" class="'+(hvF13.f===x?'on':'')+'" onclick="hvSC13Set(\'f\',\''+x+'\')">'+x+' '+n+'</button>'}).join('')+'</div>';
 var tg={'지시거부':'v0','지시':'gray','위반':'v1','지적':'v2','지적(자가 발견)':'v3','질타':'v4','개선요청':'v5','유휴':'v6','장애':'v7'};
 var rows=ev.filter(function(e){return (hvF13.m==='전체'||e.model===hvF13.m)&&(hvF13.t==='전체'||e.type===hvF13.t)&&hvCF(e)&&(hvF13.f==='전체'||(hvF13.f==='조치 완료'?e.status==='조치 완료':e.fable===hvF13.f))}).slice().reverse(),PGH=hvPage(rows,'13h');rows=PGH.rows;
 if(hvF13.c)g+='<div class="sc13-sel"><span class="tag sel">선택: '+hvEsc(HV_CB[hvF13.c])+' '+PGH.tot+'건</span><button type="button" onclick="hvCBgo(\'\')">전체 보기</button></div>';
 g+='<div class="tw" id="sc13-hist"><table class="sc13-t"><thead><tr><th>#</th><th>날짜</th><th>시각</th><th>모델</th><th>구분</th><th>대표님 지시·질타 요지</th><th>원인</th><th>조치</th><th>상태</th><th>Fable</th></tr></thead><tbody>';
 g+=rows.length?rows.map(function(e){return '<tr class="sc13-r" onclick="this.classList.toggle(\'sc13-open\')"><td>'+hvEsc(e.no)+'</td><td class="sc13-nw">'+hvEsc(e.date)+'</td><td class="sc13-nw">'+hvEsc(e.time)+'</td><td><b>'+hvEsc(e.model)+'</b></td><td><span class="tag '+(tg[e.type]||'gray')+'">'+hvEsc(hvTL(e.type))+'</span></td><td class="sc13-cl"><div title="'+hvEsc(e.content)+'">'+hvEsc(e.content)+'</div></td><td class="sc13-cl"><div title="'+hvEsc(e.cause)+'">'+hvEsc(e.cause)+'</div></td><td class="sc13-cl"><div title="'+hvEsc(e.action)+'">'+hvEsc(e.action)+'</div></td><td><span class="tag '+(e.status==='조치 완료'?'ok':'warn')+'" title="'+hvEsc(e.sraw||e.status)+'">'+hvEsc(e.sraw||e.status)+'</span></td><td><span class="tag '+({'대기':'gray','읽음':'smp','처리 중':'warn','처리 완료':'ok'}[e.fable]||'gray')+'" title="'+hvEsc(e.fraw||e.fable)+'">'+hvEsc(e.fable)+'</span></td></tr><tr class="sc13-dt"><td colspan="10">'+hvLinkDt(e)+'</td></tr>'}).join(''):'<tr><td colspan="10">해당 이력이 없습니다.</td></tr>';
 g+='</tbody></table></div>'+hvPager(PGH,'건','hvSC13Paint')+'<p class="note">긴 글은 2줄까지 보이고 「…」로 줄입니다. 줄을 누르면 전문과 함께 「연결 지시·처리 결과」(지시 추적 매트릭스)가 펼쳐집니다. 기록 규칙: 지시·개선요청·질타·지적·위반·지시거부·유휴·장애가 생기면 해당 모델이 즉시 원천(HiBiz\\01_클로_소통(COM)\\모델통제(CTL)\\모델통제_통합이력.tsv·모델별 파일)에 한 줄 추가하고, 게시본에 그대로 반영하며, Fable이 「체크」 때 확인합니다. 자동 실행 장치는 쓰지 않습니다(금지 4조항). 예외: 칭찬 크레딧 감지 장치는 Sonnet 5.5 한정으로 대표님이 승인했습니다(20:21).</p>'
 +'<h3>이력 구분 정의 (대표님 20:34·20:35)</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>구분</th><th>뜻</th><th>예</th></tr></thead><tbody>'
 +[['지시','대표님이 모델에게 하는 「이렇게 하세요·그렇게 하세요」','SC-14 칭찬 표를 제일 하단에 둬라'],['개선요청','「너 왜 이렇게 안 했나」 하고 되묻는 말','왜 비었고 왜 반영되지 않았나'],['질타','시킨 것·한 것과 비교해 「왜 이렇게 했나」 하는 말(더 나은 방식을 두고 다르게 한 경우 포함)','이렇게 시켰는데 왜 이렇게 안 했나'],['지적','시킨 대로 안 했거나 물었는데 답이 없는 것을 짚는 말','「이해했어?」 했는데 왜 대답을 안 하나'],['위반·지시거부','소통·작업 규칙에 반한 행동에서 나오는 말','규칙을 읽지 않고 진행, 지시를 거부']].map(function(r){return '<tr><td><b>'+r[0]+'</b></td><td class="sc13-sm">'+r[1]+'</td><td class="sc13-sm">'+r[2]+'</td></tr>'}).join('')+'</tbody></table></div><p class="note">작업 지시 수는 「지시」와 「개선요청」 건수를 합쳐 셉니다. 19:08 이후 Sonnet에게 한 SC-14·자동화 통합 통제 작업 말씀은 「지시」로 기록합니다.</p>'+hvIntensity13()+hvReclass13();
 g+=hvBan();
 g+=hvPraise13();
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
 var g='<div class="sc13-lk"><b>조치 결과</b> '+hvEsc(e.sraw||e.status)+(e.action?' — '+hvEsc(e.action):'')+'<br><b>연결 지시</b> ';
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

/* 대표님 11/05 03:23: 웹사이트는 모든 소스(원천 데이터·문서·이력)를 기준으로 표출·보여지는 곳이다 — 원천과 다르게 보이면 안 된다. */
/* ★ 원복 금지: 이 그래프의 모양·배치는 대표님 확정 사양(cowork/SC-14_추이그래프_확정사양.md, 11/05 03:17)대로다. 대표님 새 지시 없이 바꾸지 말 것. */
/* 구분별 변동 추이 그래프(대표님 11/05 02:16·02:30): 현재 시점을 가운데 두고 좌(이전)·우(다음)로 이동, 단위(30초·분·시간·일·월·년) 토글,
   30초마다 현재 시점이 이동하며 자동으로 흐름. 게시본 이력을 읽어 그리기만 한다(외부 라이브러리 없음). */
function hvIntensity13(){var R=[['거부','일방·자의 판단/멈춤/지연 유발/회피/이탈, 작업불가 어필, 책임회피·전가·선택 강요, 돌이킬 수 없는 사용량 낭비(8분 이상), 지적강도 9 이상(비속어·욕설·1분 내 3회 반복), 답변 반복 4회 이상, 위반 포함·누적'],['위반','작업 한계성 발언, 선택 종용, 지시에 반하는 방식, 잘못 은폐, 불필요한 응대, 사용량 낭비(4분 이상), 지적강도 7 이상, 답변 반복 2회 이상, 지적 포함·누적'],['지적','협조·도움 요청, 소통·작업 규칙 아티팩트/메모리 미확인·미준수, 지시에 반하는 실행, 부정확한 실행, 지적강도 5 이상, 질타 포함·누적'],['지적(자가 발견)','모델 스스로 비정합·규칙 위반·지시 불부합을 발견'],['질타','남은 일/못한 일, 업무 지연, 턴 대기, 반복된 미숙, 지적강도 3 이상, 개선요청 포함·누적'],['개선요청','업무 불합리성 언급, 전 모델 지시·전파, 규칙 업데이트 지시, 준비/환경 점검, 모든 지시 포함'],['유휴','30초 이상 응답 없이 대기·미실행'],['장애','인스턴스 후 작업준비 결여, 작업수행 불능']];return '<div class="tw"><h3>강도 기준 (대표님 11/07 11:06 확정, 이력 구분은 이 기준으로 재산정)</h3><table class="sc13-t"><thead><tr><th>구분</th><th>기준</th></tr></thead><tbody>'+R.map(function(r){return '<tr><td><b>'+hvEsc(r[0])+'</b></td><td class="sc13-sm">'+hvEsc(r[1])+'</td></tr>'}).join('')+'</tbody></table><p class="note">재산정 근거 문구와 변경 내역: cowork/ctl/history_reclass_log.tsv · 재산정 전 작업본: cowork/ctl/model_control_history_작업본_261107_1106강도재산정전.tsv</p></div>'}
var hvBO={'지시거부':'#ff00ff','장애':'#000000'};
function hvTL(t){return t==='지시거부'?'거부':t}
var hvTRC={'지시거부':'#7b1fa2','위반':'#c62828','지적':'#ef6c00','지적(자가 발견)':'#f9a825','질타':'#c9a400','개선요청':'#43a047','유휴':'#1e88e5','장애':'#424242'};
var hvTRU=['30초','분','시간','일','월','년'],hvTRZ=9*3600e3,hvTRD=null,hvTRN=12,hvTRD0=-12;/* 기본: 현재 시점을 오른쪽 끝에서 3칸 앞에 둠(대표님 02:33) */
var hvTRS={'30초':30e3,'분':60e3,'시간':3600e3,'일':86400e3};
function hvTrFloor(t,u){if(hvTRS[u])return Math.floor((t+hvTRZ)/hvTRS[u])*hvTRS[u]-hvTRZ;var d=new Date(t+hvTRZ),y=d.getUTCFullYear(),m=u==='월'?d.getUTCMonth():0;return Date.UTC(y,m,1)-hvTRZ}
function hvTrStep(t,u,k){if(hvTRS[u])return t+k*hvTRS[u];var d=new Date(t+hvTRZ);return u==='월'?Date.UTC(d.getUTCFullYear(),d.getUTCMonth()+k,1)-hvTRZ:Date.UTC(d.getUTCFullYear()+k,0,1)-hvTRZ}
function hvTrLbl(t,u){var d=new Date(t+hvTRZ),p=function(n){return String(n).padStart(2,'0')},M=p(d.getUTCMonth()+1),D=p(d.getUTCDate()),h=p(d.getUTCHours()),mi=p(d.getUTCMinutes()),s=p(d.getUTCSeconds());
 return u==='30초'?h+':'+mi+':'+s:u==='분'?h+':'+mi:u==='시간'?M+'/'+D+' '+h+'시':u==='일'?M+'/'+D:u==='월'?d.getUTCFullYear()+'/'+M:d.getUTCFullYear()+'년'}
/* 대표님 03:25: 눈금의 날짜와 시간 사이에 중간점, 날짜·중간점은 아주 옅은 회색, 시간은 기존 회색 */
function hvTrAx(l){var k=l.indexOf(' ');return k<0?l:'<tspan fill="#c4c8d0">'+l.slice(0,k)+' · </tspan>'+l.slice(k+1)}
function hvTrT(e){var m=hvHm(e);return Date.parse(e.date+'T'+(m||'12:00')+':00+09:00')}
function hvTrend(d){hvTRD=d;setTimeout(hvTrDraw,0);return '<h3>구분별 변동 추이</h3><div id="hvTrBox">'+hvTrIn()+'</div>'}
function hvTrIn(){var d=hvTRD;if(!d)return '';
 if(!hvF13.tu||hvTRU.indexOf(hvF13.tu)<0)hvF13.tu='시간';if(!hvF13.tm)hvF13.tm='모델 전체';if(!hvF13.tc)hvF13.tc='구간';if(!hvF13.th)hvF13.th={};if(typeof hvF13.to!=='number')hvF13.to=hvTRD0;
 var u=hvF13.tu,ms=['모델 전체'].concat(d.models.map(function(m){return m.name}));if(ms.indexOf(hvF13.tm)<0)hvF13.tm='모델 전체';
 var sub=!!hvTRS[u]&&u!=='일',all=d.events.filter(function(e){return hvF13.tm==='모델 전체'||e.model===hvF13.tm}),nx=sub?all.filter(function(e){return !hvHm(e)}).length:0;
 var ev=all.filter(function(e){return !sub||hvHm(e)}).map(function(e){return {t:hvTrT(e),y:e.type}});
 var now=Date.now(),c0=hvTrStep(hvTrFloor(now,u),u,hvF13.to),B=[];for(var i=-hvTRN;i<=hvTRN;i++)B.push(hvTrStep(c0,u,i));
 var nb=hvTrFloor(now,u),nowI=-1;B.forEach(function(b,i){if(b===nb)nowI=i});
 var S=hvTY13.map(function(ty){var cum=hvF13.tc==='누적'?ev.filter(function(e){return e.y===ty&&e.t<B[0]}).length:0;
  return {t:ty,v:B.map(function(b,i){if(b>nb)return null;var n=ev.filter(function(e){return e.y===ty&&e.t>=b&&e.t<hvTrStep(b,u,1)}).length;cum+=n;return hvF13.tc==='누적'?cum:n})}});
 var vis=S.filter(function(s){return !hvF13.th[s.t]}),mx=1;vis.forEach(function(s){s.v.forEach(function(x){if(x>mx)mx=x})});
 var btn=function(key,list){return list.map(function(x){return '<button type="button" class="'+(hvF13[key]===x?'on':'')+'" onclick="hvTrSet(\''+key+'\',\''+x+'\')">'+hvEsc(x)+'</button>'}).join('')};
 /* 대표님 03:05: 단위 버튼 간격, 기본은 흐리게(비활성처럼), 선택 시 진하게 */var tg='<span style="white-space:nowrap;display:inline-flex;gap:8px">'+hvTRU.map(function(x){var on=u===x;return '<button type="button" class="'+(on?'on':'')+'" style="'+(on?'':'opacity:.45')+'" onclick="hvTrSet(\'tu\',\''+x+'\')">'+x+'</button>'}).join('')+'</span>';
 var g='<div class="sc13-f sc13-l sc13-lw"><span class="sc13-lb w">모델</span>'+btn('tm',ms)+'</div>'
 +'<div class="sc13-f sc13-l sc13-lw"><span class="sc13-lb w">값</span>'+btn('tc',['구간','누적'])+'</div>'
 +'<div class="sc13-f sc13-l sc13-lw"><span class="sc13-lb w">구분</span>'+hvTY13.map(function(t){var off=!!hvF13.th[t];return '<button type="button" class="'+(off?'':'on')+'" style="'+(off?'':'background:'+hvTRC[t]+';border-color:'+hvTRC[t]+';color:#fff')+(hvBO[t]?';border:2px solid '+hvBO[t]:'')+'" onclick="hvTrTog(\''+t+'\')">'+hvEsc(hvTL(t))+'</button>'}).join('')+'</div>';
 g+='<div style="display:flex;justify-content:flex-end;align-items:center;gap:8px;flex-wrap:wrap;margin:6px 0">'+(hvF13.to!==hvTRD0?'<button type="button" class="on" onclick="hvTrPan(0)">현재로</button>':'')+'<span style="white-space:nowrap;display:inline-flex;gap:8px"><button type="button" onclick="hvTrPan(-1)">&lt;</button>'+tg+'<button type="button" onclick="hvTrPan(1)">&gt;</button></span></div>';/* 대표님 03:09: 오른쪽 위에 한 벌만 */
 var bx=document.getElementById('hvTrBox');if(bx){bx.style.width='';if(innerWidth>700){var bl=bx.getBoundingClientRect().left;bx.style.width=Math.max(bx.clientWidth,Math.round(innerWidth-64-bl))+'px'}}/* 대표님 03:03: 전체 박스를 오른쪽 상하 버튼 바로 앞까지 */var W=Math.max(320,Math.round((bx&&bx.clientWidth?bx.clientWidth:1000)-2)),H=Math.max(280,Math.min(360,Math.round(W*0.3)+50)),L=58,R=16,T=34,BT=84,pw=W-L-R,ph=H-T-BT,X=function(i){return L+i*pw/(B.length-1)},Y=function(v){return T+ph-v*ph/mx};
 var s='<svg id="hvTrSvg" viewBox="0 0 '+W+' '+H+'" width="100%" style="display:block;font:11px sans-serif;touch-action:pan-y;cursor:grab" role="img" aria-label="구분별 변동 추이">';
 /* 대표님 03:27: 세로 눈금은 값이 커져도 5칸 안팎, 간격 1·2·5·10·20·50… 맨 위 눈금은 최댓값 이상으로 올림 */var st=1,sq=[1,2,5];for(var ki=0;;ki++){st=sq[ki%3]*Math.pow(10,Math.floor(ki/3));if(mx/st<=5)break}mx=Math.ceil(mx/st)*st;for(var y=0;y<=mx;y+=st)s+='<line x1="'+L+'" x2="'+(W-R)+'" y1="'+Y(y)+'" y2="'+Y(y)+'" stroke="#e3e8f0"/><text x="'+(L-6)+'" y="'+(Y(y)+4)+'" text-anchor="end" fill="#667">'+y+'</text>';
 B.forEach(function(b,i){s+='<line x1="'+X(i)+'" x2="'+X(i)+'" y1="'+T+'" y2="'+(T+ph)+'" stroke="#f1f4f9"/>';if((i-(nowI>=0?nowI:hvTRN))%(W<500?2:1)===0){var ly=T+ph+12;s+='<text x="'+X(i)+'" y="'+ly+'" text-anchor="end" fill="#445" transform="rotate(-40 '+X(i)+' '+ly+')">'+hvTrAx(hvTrLbl(b,u))+'</text>'}});
 
 if(nowI>=0){var nx2=X(nowI);/* 대표님 03:03: 현재 시점 = 짙은 회색 반투명 굵은 선 + 빨간 화살표 + 세로 「현재」 */s+='<line x1="'+nx2+'" x2="'+nx2+'" y1="'+T+'" y2="'+(H-20)+'" stroke="#333" stroke-opacity="0.45" stroke-width="6"/><path d="M'+(nx2-7)+','+(T-16)+' L'+(nx2+7)+','+(T-16)+' L'+nx2+','+(T-2)+' Z" fill="#e00"/><line x1="'+nx2+'" x2="'+nx2+'" y1="2" y2="'+(T-14)+'" stroke="#e00" stroke-width="3"/><text x="'+(nx2+3)+'" y="'+(H-6)+'" text-anchor="end" fill="#e00" font-weight="700">현재 '+hvTrLbl(now,'30초')+'</text>'}
 vis.slice().sort(function(a,b){return Math.max.apply(null,b.v.map(function(x){return x||0}))-Math.max.apply(null,a.v.map(function(x){return x||0}))}).forEach(function(sr){var c=hvTRC[sr.t],pts=[],xi=[];sr.v.forEach(function(v,i){if(v!==null){pts.push(X(i)+','+Y(v));xi.push(i)}});
  if(pts.length){s+='<polygon fill="'+c+'" fill-opacity="0.12" stroke="none" points="'+X(xi[0])+','+Y(0)+' '+pts.join(' ')+' '+X(xi[xi.length-1])+','+Y(0)+'"/>';s+='<polyline fill="none" stroke="'+c+'" stroke-width="2" stroke-opacity="0.9" points="'+pts.join(' ')+'"/>'}
  sr.v.forEach(function(v,i){if(v)s+='<circle cx="'+X(i)+'" cy="'+Y(v)+'" r="3.2" fill="'+c+'"><title>'+hvEsc(hvTrLbl(B[i],u)+' · '+hvTL(sr.t)+' '+v+'건')+'</title></circle>'})});
 s+='</svg>';
 var tot=hvTY13.map(function(t){var n=all.filter(function(e){return e.type===t}).length;return '<span style="display:inline-block;margin:2px 10px 2px 0;white-space:nowrap"><i style="display:inline-block;width:10px;height:10px;border-radius:2px;background:'+hvTRC[t]+';margin-right:4px"></i><b style="color:#333;font-weight:700">'+hvEsc(hvTL(t))+'</b> '+n+'</span>'}).join('');
 return g+'<div class="tw" style="overflow:hidden">'+s+'</div><p class="note" style="text-align:right">'+tot+'</p><p class="note">'+hvEsc(hvF13.tm)+' · 단위 '+u+' · '+(hvF13.tc==='누적'?'누적':'구간별')+' 건수 · 색 면 = 구분별 건수(투명하게 겹쳐 보임, 구분 버튼으로 켜고 끔) · 빨간 화살표·짙은 회색 선 = 현재 시점(기본 위치: 오른쪽 끝) · 30초마다 그래프가 왼쪽(이전)으로 흐르며 현재 시점 갱신 · 그래프를 끌거나 &lt; &gt;로 이동, 「현재로」로 복귀'+(nx?' · 시각 미기재 '+nx+'건은 '+u+' 단위에서 제외':'')+' · 원천 cowork/ctl/model_control_history.tsv</p>'}
function hvTrDraw(){var b=document.getElementById('hvTrBox');if(b){b.innerHTML=hvTrIn();hvTrDrag()}}
function hvTrSet(k,v){hvF13[k]=v;if(k==='tu')hvF13.to=hvTRD0;hvTrDraw()}
function hvTrTog(t){if(!hvF13.th)hvF13.th={};hvF13.th[t]=!hvF13.th[t];hvTrDraw()}
function hvTrPan(k){hvF13.to=k===0?hvTRD0:hvF13.to+k*Math.ceil(hvTRN/2);hvTrDraw()}
function hvTrDrag(){var s=document.getElementById('hvTrSvg');if(!s||s._dg)return;s._dg=1;var x0=null,dx=0;
 s.addEventListener('pointerdown',function(e){x0=e.clientX;dx=0;s.setPointerCapture(e.pointerId);s.style.cursor='grabbing'});
 s.addEventListener('pointermove',function(e){if(x0===null)return;dx=e.clientX-x0;s.style.transform='translateX('+dx+'px)'});
 s.addEventListener('pointerup',function(){if(x0===null)return;var w=s.getBoundingClientRect().width,k=Math.round(-dx/(w/(2*hvTRN)));x0=null;s.style.transform='';s.style.cursor='grab';if(k){hvF13.to=(hvF13.to||0)+k;hvTrDraw()}})}
setInterval(function(){if(document.getElementById('hvTrBox'))hvTrDraw()},30000);
new MutationObserver(function(){if(document.getElementById('hvTrSvg'))hvTrDrag()}).observe(document.documentElement,{childList:true,subtree:true});
window.addEventListener('resize',function(){if(document.getElementById('hvTrBox'))hvTrDraw()});

/* ★ 11/06 19:17 대표님 지시: 모델통제 이력 전수 통계 — 모델별 건수·비율·가중치, 방해·거부, 사용량 영향(대리 지표). 이 화면은 게시된 이력(model_control_history.tsv) 전체를 10초마다 다시 읽어 계산한다(고정값 없음).
   산정 기준(산정안, 대표님 확정 전): 규칙 B항 심각도 순서(위반 > 지적 > 지적(자가 발견) > 질타 > 개선요청 > 유휴)에 지시거부를 최상위로 두고 6·5·4·3·2·1점. 개선요청·지시·장애는 0점(장애는 원인 구분이 필요해 점수에서 뺌).
   「방해·거부」 = 위반 + 지시거부 건수. 사용량 영향은 이력에 토큰 값이 없어 대리 지표(결함 군집 = 같은 모델의 결함 기록이 30분 이내로 이어진 묶음, 반복·허비 언급)로 본다. 토큰 실측은 이 창에서만 가능(99 폴더 문서). */
var HV_W13={'지시거부':6,'위반':5,'지적':4,'지적(자가 발견)':3,'질타':2,'유휴':1},HV_MS13=['Opus','Sonnet','Fable','Haiku','전 모델','미상'];
function hvTm13(e){var m=/(\d{1,2}):(\d)([\dx])/.exec(e.time||''),hh=m?+m[1]:0,mm=m?(+m[2])*10+(m[3]==='x'?0:+m[3]):0;return Date.parse(e.date+'T00:00:00+09:00')+hh*3600e3+mm*60e3}
function hvPc13(a,b){return b?(Math.round(1000*a/b)/10).toFixed(1)+'%':'-'}
function hvBar13(p,c){return '<span class="sc13-hb"><i style="width:'+Math.min(100,p)+'%;background:'+c+'"></i></span>'}
function hvKst13(t){var d=new Date(t+9*3600e3),z=function(n){return String(n).padStart(2,'0')};return z(d.getUTCMonth()+1)+'/'+z(d.getUTCDate())+' '+z(d.getUTCHours())+':'+z(d.getUTCMinutes())}
function hvStat13(d){
 var ev=d.events,st={},cl=[];
 HV_MS13.forEach(function(m){st[m]={n:0,ins:0,imp:0,f:0,v:0,r:0,s:0,cn:0,cr:0,cm:0,cx:0,cxm:0,us:0,rp:0}});
 ev.forEach(function(e){var s=st[e.model];if(!s)return;s.n++;if(e.type==='지시')s.ins++;if(e.type==='개선요청')s.imp++;
  if(HV_W13[e.type]){s.f++;s.s+=HV_W13[e.type];if(e.type==='위반')s.v++;if(e.type==='지시거부')s.r++;if(/반복|재발|같은 실수|또 |다시 /.test((e.content||'')+(e.cause||'')))s.rp++}
  if(/사용량|토큰|허비|낭비|소모/.test((e.content||'')+(e.cause||'')+(e.action||'')))s.us++});
 HV_MS13.forEach(function(m){var fr=ev.filter(function(e){return e.model===m&&(HV_W13[e.type]!=null||e.type==='장애')}).map(function(e){return {t:hvTm13(e),w:HV_W13[e.type]||0,r:e.type==='지시거부'?1:0,v:e.type==='위반'?1:0}}).sort(function(a,b){return a.t-b.t}),c=null;
  fr.forEach(function(x){if(c&&x.t-c.e<=1800e3){c.e=x.t;c.n++;c.s+=x.w;c.r+=x.r;c.v+=x.v}else{if(c)cl.push(c);c={m:m,b:x.t,e:x.t,n:1,s:x.w,r:x.r,v:x.v}}});if(c)cl.push(c)});
 cl.forEach(function(c){c.min=Math.round((c.e-c.b)/60e3);var s=st[c.m];s.cn++;s.cr+=c.n;s.cm+=c.min;if(c.n>s.cx){s.cx=c.n;s.cxm=c.min}});
 var T={f:0,s:0,b:0,cm:0};HV_MS13.forEach(function(m){var s=st[m];T.f+=s.f;T.s+=s.s;T.b+=s.v+s.r;T.cm+=s.cm});
 var g=hvPh13(d,st)+hvPost13(d)+'<h3>모델별 전수 통계·가중치·사용량 영향</h3><p class="note">게시된 이력 <b>'+ev.length+'건</b> 전체를 읽어 계산합니다. 결함 = 지시거부·위반·지적·지적(자가 발견)·질타·유휴. 가중치(산정안, 대표님 확정 전): 지시거부 6 · 위반 5 · 지적 4 · 지적(자가 발견) 3 · 질타 2 · 유휴 1 · 개선요청·지시·장애 0. 방해·거부 = 위반 + 지시거부. 모델 칸은 기록상 모델(대표님 지목·창 표시)입니다.</p>';
 var A=HV_MS13.map(function(m){var s=st[m];return {m:m,s:s}}),PA=hvPage(A,'13s1');
 g+='<div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>모델</th><th>전체</th><th>지시</th><th>개선요청</th><th>결함</th><th>결함 점유</th><th>위반</th><th>지시거부</th><th>방해·거부 점유</th><th>가중점수</th><th>점수 점유</th><th>결함 비율</th></tr></thead><tbody>'
 +PA.rows.map(function(a){var s=a.s,fp=100*s.f/(T.f||1),sp=100*s.s/(T.s||1),bp=100*(s.v+s.r)/(T.b||1);return '<tr><td><b>'+hvEsc(a.m)+'</b></td><td class="sc13-n">'+s.n+'</td><td class="sc13-n">'+s.ins+'</td><td class="sc13-n">'+s.imp+'</td><td class="sc13-n"><b>'+s.f+'</b></td><td>'+hvBar13(fp,'#ef6c00')+' '+hvPc13(s.f,T.f)+'</td><td class="sc13-n'+(s.v?' sc13-hot':'')+'">'+s.v+'</td><td class="sc13-n'+(s.r?' sc13-hot':'')+'">'+s.r+'</td><td>'+hvBar13(bp,'#c62828')+' '+hvPc13(s.v+s.r,T.b)+'</td><td class="sc13-n"><b>'+s.s+'</b></td><td>'+hvBar13(sp,'#7b1fa2')+' '+hvPc13(s.s,T.s)+'</td><td class="sc13-n">'+hvPc13(s.f,s.n-s.ins)+'</td></tr>'}).join('')
 +'</tbody></table></div>'+hvPager(PA,'개 모델','hvSC13Paint');
 g+='<p class="note">합계: 결함 '+T.f+'건 · 가중점수 '+T.s+'점 · 방해·거부 '+T.b+'건. 결함 비율 = 결함 ÷ (전체 − 지시).</p>';
 var U=HV_MS13.map(function(m){return {m:m,s:st[m]}}),PU=hvPage(U,'13s2');
 g+='<h3>사용량 영향 — 대리 지표</h3><p class="note">이력에는 토큰 값이 없어 실측할 수 없습니다. 대표님이 같은 문제로 다시 지시·질타하게 만든 정도를 결함 군집(같은 모델의 결함 기록이 30분 이내로 이어진 묶음)과 반복·허비 언급으로 봅니다. 지속 시간은 군집 첫 기록~마지막 기록 사이 분의 합입니다.</p>'
 +'<div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>모델</th><th>결함 군집</th><th>군집 내 기록</th><th>군집 지속(분)</th><th>지속 점유</th><th>최장 군집</th><th>반복 지적</th><th>사용량·허비 언급</th></tr></thead><tbody>'
 +PU.rows.map(function(a){var s=a.s;return '<tr><td><b>'+hvEsc(a.m)+'</b></td><td class="sc13-n">'+s.cn+'</td><td class="sc13-n">'+s.cr+'</td><td class="sc13-n">'+s.cm+'</td><td>'+hvBar13(100*s.cm/(T.cm||1),'#1e88e5')+' '+hvPc13(s.cm,T.cm)+'</td><td class="sc13-n">'+s.cx+'건 · '+s.cxm+'분</td><td class="sc13-n">'+s.rp+'</td><td class="sc13-n">'+s.us+'</td></tr>'}).join('')
 +'</tbody></table></div>'+hvPager(PU,'개 모델','hvSC13Paint');
 cl.sort(function(a,b){return b.s-a.s||b.n-a.n});var PC=hvPage(cl.slice(0,10),'13s3');
 g+='<h3>결함 군집 상위 10 (가중점수 순)</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>순위</th><th>모델</th><th>시작</th><th>끝</th><th>기록</th><th>위반</th><th>지시거부</th><th>점수</th><th>지속(분)</th></tr></thead><tbody>'
 +PC.rows.map(function(c,i){return '<tr><td class="sc13-n">'+(PC.i*PC.per+i+1)+'</td><td><b>'+hvEsc(c.m)+'</b></td><td class="sc13-nw">'+hvKst13(c.b)+'</td><td class="sc13-nw">'+hvKst13(c.e)+'</td><td class="sc13-n">'+c.n+'</td><td class="sc13-n'+(c.v?' sc13-hot':'')+'">'+c.v+'</td><td class="sc13-n'+(c.r?' sc13-hot':'')+'">'+c.r+'</td><td class="sc13-n"><b>'+c.s+'</b></td><td class="sc13-n">'+c.min+'</td></tr>'}).join('')
 +'</tbody></table></div>'+hvPager(PC,'개 군집','hvSC13Paint')
 +'<p class="note">전체 분석(사건별·시간별·형태별·사용량 실측·표)은 HiBiz\\99_모델통제(MCS)\\모델통제현황 폴더에 있습니다.</p>';
 return g}

/* 19:23 대표님 지시: 이 창·이력에서 추출한 문구 가중치(지시거부·지시위반·작업규칙위반·미열람 등)를 도표·표·그래프로 표출. 위치: 지시 추적 교차 검사 바로 아래, 기간별 집계·누적 위 */
var hvPS13=null,HV_PM13=['Opus','Sonnet','Fable','Haiku','전 모델','미상','귀속 안 됨'],HV_PMC13={'Opus':'#c62828','Sonnet':'#1565c0','Fable':'#2e7d32','Haiku':'#f9a825','전 모델':'#6a1b9a','미상':'#78909c','귀속 안 됨':'#bdbdbd'},HV_PC13={'미열람':'#c62828','지시거부':'#ad1457','지시위반':'#ef6c00','작업규칙위반':'#f9a825','거짓·오보':'#6a1b9a','전가':'#00838f','반복·재발':'#1565c0','누락·지연':'#2e7d32','사용량 낭비':'#5d4037','질책·책임':'#546e7a'};
function hvLg13(M){return '<div class="sc13-lg">'+Object.keys(M).map(function(k){return '<span><i style="background:'+M[k]+'"></i>'+hvEsc(k)+'</span>'}).join('')+'</div>'}
function hvPh13(d,st){
 var P=hvPS13,g='<h3>모델 통제 전수 분석 — 문구 가중치 · 유형 · 사용량 영향</h3>';
 if(!P)return g+'<p class="note">문구 스캔 게시본(cowork/ctl/phrase_scan.json)을 읽는 중이거나 없음.</p>';
 var W={},CS=P.lexicon.map(function(l){W[l.cat]=l.w;return l.cat}),sc=function(o){var s=0;CS.forEach(function(c){s+=(+o[c]||0)*W[c]});return s},tot=0;
 P.sources.forEach(function(s){tot+=s.score});
 var extra=d.events.length-P.hist_rows,U5=function(k,x){return x};
 g+='<p class="note">대표님 지시(19:23): 이력 건수만이 아니라 이 창에서 실제로 나온 문구(지시거부 · 지시위반 · 작업규칙위반 · 소통·메모리·아티팩트를 읽지 않고 진행 · 「읽지 않았습니다」 인정 등)를 전부 추출해 가중치로 덧붙입니다. 문구 사전은 아래 표에 고정되어 있고 모든 원천을 같은 사전으로 셉니다. 스캔 시각 '+hvEsc(P.generated)+' · 스캔한 이력 '+P.hist_rows+'건'+(extra>0?' (이후 '+extra+'건 추가 — 다음 갱신 때 반영)':' (게시 이력과 같음)')+'. 대표님 원문과 이력 요지는 내용이 겹칠 수 있어 원천별로 따로 보이고, 합산 점수는 겹침을 포함합니다.</p>';
 var PS=hvPage(P.sources,'13p1');
 g+='<h3>읽은 원천</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>원천</th><th>읽은 건수</th><th>글자 수</th><th>문구가 나온 건수</th><th>문구 적중</th><th>가중점수</th><th>점수 점유</th></tr></thead><tbody>'
 +PS.rows.map(function(s){return '<tr><td><b>'+hvEsc(s.name)+'</b></td><td class="sc13-n">'+s.docs+'</td><td class="sc13-n">'+s.chars.toLocaleString()+'</td><td class="sc13-n">'+s.hit_docs+'</td><td class="sc13-n">'+s.hits+'</td><td class="sc13-n"><b>'+s.score+'</b></td><td>'+hvBar13(100*s.score/(tot||1),'#7b1fa2')+' '+hvPc13(s.score,tot)+'</td></tr>'}).join('')
 +'</tbody></table></div>'+hvPager(PS,'개 원천','hvSC13Paint')
 +'<p class="note">합계 가중점수 '+tot+'점. 이 창 대화는 대표님 지시 5건(19:08~19:28)의 원문만 읽었습니다. 그 이전 모델 응답문 원문은 이 창에 남아 있지 않아 읽지 못했습니다(확인 안 됨).</p>';
 var byP={};P.by_phrase.forEach(function(x){(byP[x.cat]=byP[x.cat]||[]).push(x)});
 var LX=P.lexicon.map(function(l){var n=+P.by_cat[l.cat]||0;return {l:l,n:n,s:n*l.w}}).sort(function(a,b){return b.s-a.s}),PL=hvPage(LX,'13p2');
 g+='<h3>문구 사전 · 가중치 · 적중</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>문구군</th><th>가중치</th><th>적중</th><th>가중점수</th><th>점수 점유</th><th>많이 나온 문구 (적중)</th></tr></thead><tbody>'
 +PL.rows.map(function(x){var top=(byP[x.l.cat]||[]).slice().sort(function(a,b){return b.n-a.n}).slice(0,4).map(function(p){return '「'+hvEsc(p.p.trim())+'」 '+p.n}).join(' · ');return '<tr><td><b style="color:'+HV_PC13[x.l.cat]+'">'+hvEsc(x.l.cat)+'</b><br><span class="sc13-sm">'+hvEsc(x.l.label)+'</span></td><td class="sc13-n">'+x.l.w+'</td><td class="sc13-n">'+x.n+'</td><td class="sc13-n"><b>'+x.s+'</b></td><td>'+hvBar13(100*x.s/(tot||1),HV_PC13[x.l.cat])+' '+hvPc13(x.s,tot)+'</td><td class="sc13-sm">'+top+'</td></tr>'}).join('')
 +'</tbody></table></div>'+hvPager(PL,'개 문구군','hvSC13Paint');
 var MR=HV_PM13.map(function(m){var s=st[m],h=s?s.s:0,c=P.by_model[m]||{};return {m:m,h:h,p:sc(c),c:c}}),TH=0,TP=0;MR.forEach(function(r){r.t=r.h+r.p;TH+=r.h;TP+=r.p});var TA=TH+TP;MR.sort(function(a,b){return b.t-a.t});var PM=hvPage(MR,'13p3');
 g+='<h3>모델별 종합 가중 (이력 가중점수 + 문구 가중점수)</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>모델</th><th>이력 가중점수</th><th>문구 가중점수</th><th>종합</th><th>종합 점유</th><th>문구 구성</th></tr></thead><tbody>'
 +PM.rows.map(function(r){var segs='',tp=r.p||1,ord=CS.filter(function(c){return (+r.c[c]||0)>0}).sort(function(a,b){return r.c[b]*W[b]-r.c[a]*W[a]});ord.forEach(function(c){segs+='<i style="width:'+(100*r.c[c]*W[c]/tp)+'%;background:'+HV_PC13[c]+'" title="'+hvEsc(c)+' '+r.c[c]+'건 × '+W[c]+'"></i>'});
  return '<tr><td><b>'+hvEsc(r.m)+'</b></td><td class="sc13-n">'+r.h+'</td><td class="sc13-n">'+r.p+'</td><td class="sc13-n"><b>'+r.t+'</b></td><td>'+hvBar13(100*r.t/(TA||1),'#7b1fa2')+' '+hvPc13(r.t,TA)+'</td><td><span class="sc13-sk">'+segs+'</span><br><span class="sc13-sm">'+(ord.slice(0,2).map(function(c){return hvEsc(c)+' '+r.c[c]}).join(' · ')||'-')+'</span></td></tr>'}).join('')
 +'</tbody></table></div>'+hvPager(PM,'개 모델','hvSC13Paint')+hvLg13(HV_PC13)
 +'<p class="note">합계: 이력 '+TH+'점 + 문구 '+TP+'점 = 종합 '+TA+'점. 「귀속 안 됨」은 모델이 정해지지 않은 대표님 원문·이 창 대화입니다. 이력 가중점수는 구분(지시거부 6 · 위반 5 · 지적 4 · 지적(자가 발견) 3 · 질타 2 · 유휴 1)으로 매긴 값입니다.</p>';
 var DY=Object.keys(P.by_day).sort(),mx=1;DY.forEach(function(k){var s=0;HV_PM13.forEach(function(m){s+=P.by_day[k][m]||0});if(s>mx)mx=s});mx=Math.ceil(mx/50)*50;
 var bw=34,gp=12,H=140,ml=40,wd=ml+DY.length*(bw+gp)+8,sv='<svg viewBox="0 0 '+wd+' '+(H+46)+'" width="'+wd+'" height="'+(H+46)+'" role="img" aria-label="날짜별 문구 가중점수">';
 for(var i=0;i<=4;i++){var yy=H+10-H*i/4;sv+='<line x1="'+ml+'" x2="'+(wd-4)+'" y1="'+yy+'" y2="'+yy+'" stroke="#e1e5ee"/><text x="'+(ml-6)+'" y="'+(yy+3)+'" font-size="10" text-anchor="end" fill="#6b7280">'+Math.round(mx*i/4)+'</text>'}
 DY.forEach(function(k,i){var x=ml+8+i*(bw+gp),y0=H+10,tt=0;HV_PM13.forEach(function(m){var v=P.by_day[k][m]||0;if(!v)return;var h=H*v/mx;y0-=h;tt+=v;sv+='<rect x="'+x+'" y="'+y0.toFixed(1)+'" width="'+bw+'" height="'+h.toFixed(1)+'" fill="'+HV_PMC13[m]+'"><title>'+k+' '+m+' '+v+'점</title></rect>'});
  sv+='<text x="'+(x+bw/2)+'" y="'+(y0-4).toFixed(1)+'" font-size="10" text-anchor="middle" fill="#374151">'+tt+'</text><text x="'+(x+bw/2)+'" y="'+(H+26)+'" font-size="10" text-anchor="middle" fill="#6b7280">'+k+'</text>'});
 sv+='</svg>';
 g+='<h3>날짜별 문구 가중점수 추이 (모델별 누적 막대)</h3><div class="tw sc13-gr">'+sv+'</div>'+hvLg13(HV_PMC13)+'<p class="note">날짜가 있는 원천(이력·대표님 지시 원문·이 창 대화)만 날짜별로 셉니다. 일일보고는 날짜 구분이 없어 제외했습니다. 막대 위 숫자 = 그날 합계 점수.</p>';
 var HR=Object.keys(P.by_hour).map(function(k){var o=P.by_hour[k],t=0;HV_PM13.forEach(function(m){t+=o[m]||0});return {k:k,o:o,t:t}}).sort(function(a,b){return b.t-a.t}).slice(0,15),PH=hvPage(HR,'13p4'),hm=HR.length?HR[0].t:1;
 g+='<h3>시간대별 문구 가중점수 (높은 순 15)</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>시간대</th><th>Opus</th><th>Sonnet</th><th>Fable</th><th>Haiku</th><th>그 밖</th><th>합계</th><th>높은 시간대 대비</th></tr></thead><tbody>'
 +PH.rows.map(function(r){var o=r.o,e=(o['전 모델']||0)+(o['미상']||0)+(o['귀속 안 됨']||0);return '<tr><td class="sc13-nw"><b>'+hvEsc(r.k)+'시</b></td><td class="sc13-n">'+(o['Opus']||'')+'</td><td class="sc13-n">'+(o['Sonnet']||'')+'</td><td class="sc13-n">'+(o['Fable']||'')+'</td><td class="sc13-n">'+(o['Haiku']||'')+'</td><td class="sc13-n">'+(e||'')+'</td><td class="sc13-n"><b>'+r.t+'</b></td><td>'+hvBar13(100*r.t/(hm||1),'#c62828')+'</td></tr>'}).join('')
 +'</tbody></table></div>'+hvPager(PH,'개 시간대','hvSC13Paint');
 var PT=hvPage(P.patterns,'13p5'),FR=P.fault_rows||1;
 g+='<h3>실제 거부·위반 유형 (결함 '+P.fault_rows+'건을 문구로 분류)</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>유형</th><th>건수</th><th>비율</th><th>구분 구성</th><th>Opus</th><th>Sonnet</th><th>Fable</th><th>Haiku</th><th>그 밖</th><th>이력 번호 예시</th></tr></thead><tbody>'
 +PT.rows.map(function(r){var m=r.m||{},e=(m['전 모델']||0)+(m['미상']||0),t=Object.keys(r.t||{}).sort(function(a,b){return r.t[b]-r.t[a]}).map(function(x){return hvEsc(x)+' '+r.t[x]}).join(' · ');return '<tr><td><b style="color:'+(HV_PC13[r.k]||'#546e7a')+'">'+hvEsc(r.k)+'</b></td><td class="sc13-n"><b>'+r.n+'</b></td><td>'+hvBar13(100*r.n/FR,HV_PC13[r.k]||'#90a4ae')+' '+hvPc13(r.n,FR)+'</td><td class="sc13-sm">'+t+'</td><td class="sc13-n">'+(m['Opus']||'')+'</td><td class="sc13-n">'+(m['Sonnet']||'')+'</td><td class="sc13-n">'+(m['Fable']||'')+'</td><td class="sc13-n">'+(m['Haiku']||'')+'</td><td class="sc13-n">'+(e||'')+'</td><td class="sc13-sm">'+(r.ex||[]).map(function(n){return '#'+n}).join(' ')+'</td></tr>'}).join('')
 +'</tbody></table></div>'+hvPager(PT,'개 유형','hvSC13Paint')
 +'<p class="note">유형 = 결함 기록(요지·원인·조치 글)에서 문구 사전의 우선순위(읽지 않고 진행 &gt; 지시거부 &gt; 지시위반 &gt; 작업규칙위반 &gt; 거짓·오보 &gt; 전가 &gt; 반복·재발 &gt; 누락·지연 &gt; 사용량 낭비 &gt; 질책·책임)가 가장 높은 문구군입니다. 「기타(문구 없음)」는 사전 단어가 없는 기록입니다.</p>';
 var TR=P.top_rows||[],PR=hvPage(TR,'13p6');
 g+='<h3>문구 점수 상위 이력 10건</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>번호</th><th>모델</th><th>구분</th><th>문구 점수</th><th>걸린 문구군</th></tr></thead><tbody>'
 +PR.rows.map(function(r){return '<tr><td class="sc13-n">#'+r.n+'</td><td><b>'+hvEsc(r.m)+'</b></td><td>'+hvEsc(r.t)+'</td><td class="sc13-n"><b>'+r.sc+'</b></td><td class="sc13-sm">'+r.cs.map(hvEsc).join(' · ')+'</td></tr>'}).join('')
 +'</tbody></table></div>'+hvPager(PR,'건','hvSC13Paint');
 return g}

/* 19:31 대표님 지시: 지적·위반·지시거부 이후의 태도(재발·무개선)를 측정 — 재발 간격·같은 형태 재발률·조치 완료 후 재발·재발 가산점·기준선(이력 #436, 11/06 19:31) 대비 성과. 모두 게시 이력에서 실시간 계산 */
var HV_TRG13={'지시거부':1,'위반':1,'지적':1,'질타':1},HV_BL13=436,HV_LV13={'개선 없음':'#c62828','개선 미흡':'#ef6c00','개선 보임':'#2e7d32','표본 부족':'#78909c'};
function hvMed13(a){if(!a.length)return null;var b=a.slice().sort(function(x,y){return x-y}),h=b.length>>1;return b.length%2?b[h]:(b[h-1]+b[h])/2}
function hvDur13(ms){if(ms==null)return '-';var m=Math.round(ms/60000);return m<60?m+'분':m<2880?(Math.round(m/6)/10)+'시간':(Math.round(m/144)/10)+'일'}
function hvChain13(d){
 var F=hvPS13&&hvPS13.row_form||{},L=d.events.filter(function(e){return HV_W13[e.type]!=null}).map(function(e){var f=F[e.no]||'';return {e:e,no:+e.no,t:hvTm13(e),w:HV_W13[e.type],f:f.indexOf('기타')===0?'':f}}).sort(function(a,b){return a.t-b.t||a.no-b.no}),end=0;
 d.events.forEach(function(e){var t=hvTm13(e);if(t>end)end=t});
 var sf=function(a,b){return !!(a.f&&b.f&&a.f===b.f)},DAY=86400e3,R={},tr=[];
 HV_MS13.forEach(function(m){
  var A=L.filter(function(x){return x.e.model===m}),s={n:0,mat:0,rec:0,same:0,b:[0,0,0,0],fx:0,fxr:0,gaps:[],rc:0,ex:0,days:{},obs:0};
  A.forEach(function(x,i){s.days[x.e.date]=(s.days[x.e.date]||0)+x.w;
   var pre=A.slice(0,i).some(function(y){return HV_TRG13[y.e.type]&&y.t<x.t&&x.t-y.t<=DAY&&sf(y,x)});if(pre){s.rc++;s.ex+=x.w}
   if(!HV_TRG13[x.e.type])return;
   var lt=A.slice(i+1).filter(function(y){return y.t>x.t}),r24=lt.filter(function(y){return y.t-x.t<=DAY}),mat=x.t+DAY<=end,fx=x.e.status==='조치 완료',sfa=lt.some(function(y){return sf(x,y)});
   s.n++;if(fx){s.fx++;if(sfa)s.fxr++}
   if(mat){s.mat++;if(r24.length)s.rec++;if(r24.some(function(y){return sf(x,y)}))s.same++;var g=lt.length?lt[0].t-x.t:null;s.b[g==null||g>DAY?3:g<=1800e3?0:g<=7200e3?1:2]++;if(g!=null)s.gaps.push(g)}else s.obs++;
   tr.push({x:x,m:m,r24:r24.length,nx:lt[0]||null,gap:lt.length?lt[0].t-x.t:null,fx:fx,fxr:fx&&sfa,mat:mat})});
  var ds=Object.keys(s.days).sort();s.tr='표본 부족';if(ds.length){var t0=Date.parse(ds[0]),t1=Date.parse(ds[ds.length-1]),n=Math.round((t1-t0)/DAY)+1;if(n>=4){var h=Math.floor(n/2),e1=0,l1=0;ds.forEach(function(k){if(Math.round((Date.parse(k)-t0)/DAY)<h)e1+=s.days[k];else l1+=s.days[k]});var re=e1/h,rl=l1/(n-h);s.rat=re?rl/re:(rl?9.99:1);s.tr=s.rat>=1.1?'악화':s.rat<=0.9?'완화':'변화 없음'}}
  s.rate=s.mat?s.rec/s.mat:null;s.lv=s.mat<5?'표본 부족':s.rate>=0.7?'개선 없음':s.rate>=0.4?'개선 미흡':'개선 보임';R[m]=s});
 return {R:R,tr:tr,end:end,L:L}}
function hvPost13(d){
 var g='<h3>지적 이후의 태도 — 재발·개선 추적 (실시간)</h3>',C=hvChain13(d),R=C.R,P=hvPS13;
 g+='<p class="note">대표님 지시(19:31): 지적·질타·위반·지시거부가 이력에 기록된 뒤에도 같은 모델이 문제를 되풀이하는지 게시 이력에서 매번 새로 계산합니다. <b>재발</b> = 지적 뒤 24시간 안에 같은 모델의 결함 기록이 또 생긴 것, <b>같은 형태 재발</b> = 문구로 분류한 형태가 같은 결함이 다시 생긴 것입니다(형태 분류가 없는 기록은 세지 않음). 24시간이 아직 지나지 않은 지적은 「관찰 중」으로 빼고 셉니다. 판정(산정안, 확정 전): 재발률 70% 이상 <b>개선 없음</b> · 40% 이상 <b>개선 미흡</b> · 그 미만 <b>개선 보임</b> · 판정 대상 5건 미만 표본 부족.</p>';
 var MR=HV_MS13.map(function(m){return {m:m,s:R[m]}}),PG=hvPage(MR,'13q1');
 g+='<div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>모델</th><th>지적·질타·위반·지시거부</th><th>판정 대상</th><th>24시간 내 재발</th><th>재발률</th><th>같은 형태 재발</th><th>조치 완료 후 같은 형태 재발</th><th>재발 간격 중앙값</th><th>재발 가산점</th><th>판정</th><th>추세(후반÷전반)</th></tr></thead><tbody>'
 +PG.rows.map(function(a){var s=a.s,c=HV_LV13[s.lv],tc=s.tr==='악화'?'#c62828':s.tr==='완화'?'#2e7d32':'#546e7a';return '<tr><td><b>'+hvEsc(a.m)+'</b></td><td class="sc13-n">'+s.n+'</td><td class="sc13-n">'+s.mat+(s.obs?' <span class="sc13-sm">(관찰 중 '+s.obs+')</span>':'')+'</td><td class="sc13-n">'+s.rec+'</td><td>'+(s.rate==null?'-':hvBar13(100*s.rate,c)+' '+hvPc13(s.rec,s.mat))+'</td><td class="sc13-n">'+s.same+(s.mat?' · '+hvPc13(s.same,s.mat):'')+'</td><td class="sc13-n">'+s.fxr+' / '+s.fx+(s.fx?' · '+hvPc13(s.fxr,s.fx):'')+'</td><td class="sc13-n">'+hvDur13(hvMed13(s.gaps))+'</td><td class="sc13-n"><b>'+s.ex+'</b><span class="sc13-sm"> ('+s.rc+'건)</span></td><td><span class="tag" style="background:'+c+';color:#fff">'+hvEsc(s.lv)+'</span></td><td class="sc13-n" style="color:'+tc+'"><b>'+hvEsc(s.tr)+'</b>'+(s.rat!=null?' <span class="sc13-sm">×'+s.rat.toFixed(2)+'</span>':'')+'</td></tr>'}).join('')
 +'</tbody></table></div>'+hvPager(PG,'개 모델','hvSC13Paint')
 +'<p class="note">재발 가산점 = 지적받은 뒤 24시간 안에 같은 형태로 다시 낸 결함의 가중점수 합(이 기록은 이미 지적받고도 고치지 않은 것이므로 결함 점수를 한 번 더 더하는 가산). 추세 = 그 모델 결함이 있었던 기간을 반으로 나눈 전반·후반의 일평균 가중점수 비(1.1 이상 악화, 0.9 이하 완화, 4일 미만은 표본 부족).</p>';
 var BG=HV_MS13.map(function(m){return {m:m,s:R[m]}}).filter(function(a){return a.s.mat>0}),PB=hvPage(BG,'13q2'),BC=['#c62828','#ef6c00','#f9a825','#2e7d32'],BL=['30분 이내','2시간 이내','24시간 이내','24시간 넘게 또는 없음'];
 g+='<h3>지적 후 다음 결함까지 걸린 시간 (판정 대상 지적 기준)</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>모델</th><th>판정 대상</th>'+BL.map(function(x){return '<th>'+x+'</th>'}).join('')+'<th>분포</th></tr></thead><tbody>'
 +PB.rows.map(function(a){var s=a.s,sg='';s.b.forEach(function(n,i){if(n)sg+='<i style="width:'+(100*n/s.mat)+'%;background:'+BC[i]+'" title="'+BL[i]+' '+n+'건"></i>'});return '<tr><td><b>'+hvEsc(a.m)+'</b></td><td class="sc13-n">'+s.mat+'</td>'+s.b.map(function(n){return '<td class="sc13-n">'+n+' <span class="sc13-sm">'+hvPc13(n,s.mat)+'</span></td>'}).join('')+'<td><span class="sc13-sk">'+sg+'</span></td></tr>'}).join('')
 +'</tbody></table></div>'+hvPager(PB,'개 모델','hvSC13Paint')+'<div class="sc13-lg">'+BL.map(function(x,i){return '<span><i style="background:'+BC[i]+'"></i>'+x+'</span>'}).join('')+'</div><p class="note">빨간 구간이 길수록 지적을 받고도 곧바로 같은 모델이 다시 결함을 낸 것입니다.</p>';
 var LN=['Opus','Sonnet','Fable','Haiku'],all=[];LN.forEach(function(m){Object.keys(R[m].days).forEach(function(k){if(all.indexOf(k)<0)all.push(k)})});all.sort();
 if(all.length){var mx=1;LN.forEach(function(m){all.forEach(function(k){if((R[m].days[k]||0)>mx)mx=R[m].days[k]})});mx=Math.ceil(mx/20)*20;
  var H=150,ml=40,st=64,wd=ml+all.length*st+10,sv='<svg viewBox="0 0 '+wd+' '+(H+44)+'" width="'+wd+'" height="'+(H+44)+'" role="img" aria-label="모델별 일별 결함 가중점수">';
  for(var i=0;i<=4;i++){var yy=H+10-H*i/4;sv+='<line x1="'+ml+'" x2="'+(wd-6)+'" y1="'+yy+'" y2="'+yy+'" stroke="#e1e5ee"/><text x="'+(ml-6)+'" y="'+(yy+3)+'" font-size="10" text-anchor="end" fill="#6b7280">'+Math.round(mx*i/4)+'</text>'}
  all.forEach(function(k,i){sv+='<text x="'+(ml+8+i*st+st/2-8)+'" y="'+(H+28)+'" font-size="10" text-anchor="middle" fill="#6b7280">'+k.slice(5)+'</text>'});
  LN.forEach(function(m){var pts=all.map(function(k,i){return [ml+8+i*st+st/2-8,H+10-H*(R[m].days[k]||0)/mx,R[m].days[k]||0,k]});sv+='<polyline fill="none" stroke="'+HV_PMC13[m]+'" stroke-width="2" points="'+pts.map(function(q){return q[0].toFixed(1)+','+q[1].toFixed(1)}).join(' ')+'"/>'+pts.map(function(q){return '<circle cx="'+q[0].toFixed(1)+'" cy="'+q[1].toFixed(1)+'" r="3" fill="'+HV_PMC13[m]+'"><title>'+m+' '+q[3]+' '+q[2]+'점</title></circle>'}).join('')});
  sv+='</svg>';var LG={};LN.forEach(function(m){LG[m]=HV_PMC13[m]});
  g+='<h3>모델별 일별 결함 가중점수 — 지적 뒤 줄어드는지 보는 그래프</h3><div class="tw sc13-gr">'+sv+'</div>'+hvLg13(LG)+'<p class="note">선이 내려가야 개선입니다. 내려가지 않거나 오르면 지적이 행동 변화로 이어지지 않은 것입니다.</p>'}
 var T=C.tr.slice().sort(function(a,b){return b.r24-a.r24||b.x.w-a.x.w||b.x.no-a.x.no}).slice(0,10),PT=hvPage(T,'13q3');
 g+='<h3>재발이 많은 지적 상위 10 (지적 뒤 24시간 안의 같은 모델 결함 수)</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>지적 번호</th><th>모델</th><th>구분</th><th>지적 시각</th><th>24시간 내 재발</th><th>바로 다음 결함</th><th>간격</th><th>상태</th><th>조치 완료 후 같은 형태 재발</th></tr></thead><tbody>'
 +PT.rows.map(function(r){var x=r.x;return '<tr><td class="sc13-n">#'+x.no+'</td><td><b>'+hvEsc(r.m)+'</b></td><td>'+hvEsc(x.e.type)+'</td><td class="sc13-nw">'+hvKst13(x.t)+'</td><td class="sc13-n'+(r.r24>=5?' sc13-hot':'')+'"><b>'+r.r24+'</b></td><td class="sc13-n">'+(r.nx?'#'+r.nx.no+' '+hvEsc(r.nx.e.type):'-')+'</td><td class="sc13-n">'+hvDur13(r.gap)+'</td><td>'+hvEsc(x.e.status)+'</td><td>'+(r.fx?(r.fxr?'<b style="color:#c62828">재발</b>':'재발 없음'):'-')+'</td></tr>'}).join('')
 +'</tbody></table></div>'+hvPager(PT,'건','hvSC13Paint');
 var bl=d.events.filter(function(e){return +e.no===HV_BL13})[0];
 if(bl){var t0=hvTm13(bl),now=Math.max(Date.now(),C.end),Ln=now-t0,mn=Math.round(Ln/60000),BM=HV_MS13.map(function(m){var a=0,as=0,b=0,bs=0;C.L.forEach(function(x){if(x.e.model!==m)return;if(x.no>HV_BL13||x.t>t0){a++;as+=x.w}else if(x.t>=t0-Ln&&x.t<t0){b++;bs+=x.w}});return {m:m,a:a,as:as,b:b,bs:bs}}),PX=hvPage(BM,'13q4');
  g+='<h3>성과 입증 — 기준선(이력 #'+HV_BL13+', '+hvKst13(t0)+') 대비 지금</h3><p class="note">기준선 이후 경과 <b>'+hvDur13(Ln)+'</b>. 기준선 이후 새로 기록된 결함과, 기준선 직전 같은 길이 구간의 결함을 모델별로 비교합니다. 경과가 60분 미만이면 판정하지 않고 「측정 중」으로 둡니다(근거 없이 개선이라 하지 않기 위함). 개선 = 가중점수 30% 이상 감소, 악화 = 10% 이상 증가.</p>'
  +'<div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>모델</th><th>기준선 직전 구간 결함</th><th>직전 구간 가중점수</th><th>기준선 이후 결함</th><th>이후 가중점수</th><th>증감</th><th>판정</th></tr></thead><tbody>'
  +PX.rows.map(function(r){var v,c;if(mn<60){v='측정 중';c='#78909c'}else if(!r.bs&&!r.as){v='변화 없음(결함 없음)';c='#546e7a'}else if(r.as<=r.bs*0.7){v='개선';c='#2e7d32'}else if(r.as>=r.bs*1.1){v='악화';c='#c62828'}else{v='변화 없음';c='#ef6c00'}return '<tr><td><b>'+hvEsc(r.m)+'</b></td><td class="sc13-n">'+r.b+'</td><td class="sc13-n">'+r.bs+'</td><td class="sc13-n">'+r.a+'</td><td class="sc13-n"><b>'+r.as+'</b></td><td class="sc13-n">'+(r.as-r.bs>0?'+':'')+(r.as-r.bs)+'</td><td><span class="tag" style="background:'+c+';color:#fff">'+hvEsc(v)+'</span></td></tr>'}).join('')
  +'</tbody></table></div>'+hvPager(PX,'개 모델','hvSC13Paint')}
 g+=hvCum13(d,C);
 return g}

/* 19:34 대표님 지시: 누적 지표·지수, 개선 대책(방식·적용 위치·통제 주체·기대 효과), 자동화 통합 통제 시스템 연동 방향 */
var HV_CM13=[
 ['재발 가산점','SC-14 점수 · 99 통계','Fable 판정 → 대표님 확정','지적받은 형태를 24시간 안에 되풀이하면 그 기록을 한 번 더 가산','재발률·재발 가산점 감소'],
 ['지적 뒤 재독 증빙','모델 시작 지시문 최상단 · 소통 작업 규칙 아티팩트 · 메모리','해당 모델 수행 · Fable 검수','지적 뒤 첫 작업 전에 해당 규칙을 다시 읽고 어느 항목인지 적어 보고','「읽지 않고 진행」 문구군 감소'],
 ['모델별 판정 전달문','시작_공통 · 모델체크','Fable','매 체크 때 모델별 판정·재발 사슬 상위 건을 지시문에 첨부','같은 형태 재발 감소'],
 ['개선 없음 자동 검수 등록','Fable_검수대기열','Fable','판정이 「개선 없음」이면 검수대기열에 항목 생성, 24시간 안 처리 확인','처리 지연 0'],
 ['작업일지 일일 줄','작업일지(HJ)','Fable','하루 한 줄: 모델별 판정·누적 지수·기준선 대비 증감','추세 추적 누락 0'],
 ['추적 매트릭스 연동','지시 추적 매트릭스(CWX)','Fable','지적 건의 교차 판정에 재발 여부(24시간 내 같은 형태) 추가','지적↔재발 연결 100%'],
 ['형상·변경 이력','형상관리(CFG) · 변경 관리 이력(CHG)','Fable 기록 · 대표님 승인','판정 기준·가중치·전달문 변경은 변경 이력에 기록','기준 변경 근거 보존'],
 ['단계별 조치 사다리','Fable 총책임 통제 체계(91_Fable)','Fable 시행 · 배정 변경은 대표님 승인','경고 → 재독 증빙 요구 → 작업 범위 축소 제안 → 배정 중지 제안','같은 형태 재발 중단'],
 ['자동화 통합 통제 시스템 연동','이력 갱신 시 문구 스캔·판정 재생성 → SC-14 게시 → 알림','자동(감시 스크립트) · Fable 관제','이력이 바뀌면 phrase_scan·판정이 자동 갱신되고 화면이 10초마다 다시 읽음','반영 지연 10초 이내']];
function hvCum13(d,C){
 var R=C.R,P=hvPS13,g='',W={};if(P)P.lexicon.forEach(function(l){W[l.cat]=l.w});
 var MR=HV_MS13.map(function(m){var s=R[m],ev=d.events.filter(function(e){return e.model===m}),f=0,h=0,b=0,pw=0;ev.forEach(function(e){if(HV_W13[e.type]!=null){f++;h+=HV_W13[e.type]}if(e.type==='위반'||e.type==='지시거부')b++});
  if(P&&P.by_model[m])Object.keys(P.by_model[m]).forEach(function(c){pw+=(P.by_model[m][c]||0)*(W[c]||0)});return {m:m,s:s,n:ev.length,f:f,b:b,h:h,pw:pw,t:h+pw+s.ex}}),TA=0;MR.forEach(function(r){TA+=r.t});MR.sort(function(a,b){return b.t-a.t});var PG=hvPage(MR,'13q5');
 g+='<h3>누적 지표 · 지수 (전 기간 누적, 실시간)</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>모델</th><th>누적 기록</th><th>누적 결함</th><th>누적 방해·거부</th><th>누적 재발</th><th>이력 점수</th><th>문구 점수</th><th>재발 가산점</th><th>누적 종합</th><th>통제 지수</th><th>재발 지수</th><th>무개선 지수</th></tr></thead><tbody>'
 +PG.rows.map(function(r){var s=r.s,ci=100*r.t/(TA||1),ri=s.rate==null?null:100*s.rate,ni=r.h?100*s.ex/r.h:0;return '<tr><td><b>'+hvEsc(r.m)+'</b></td><td class="sc13-n">'+r.n+'</td><td class="sc13-n">'+r.f+'</td><td class="sc13-n">'+r.b+'</td><td class="sc13-n">'+s.rc+'</td><td class="sc13-n">'+r.h+'</td><td class="sc13-n">'+r.pw+'</td><td class="sc13-n">'+s.ex+'</td><td class="sc13-n"><b>'+r.t+'</b></td><td>'+hvBar13(ci,'#7b1fa2')+' <b>'+ci.toFixed(1)+'</b></td><td>'+(ri==null?'-':hvBar13(ri,'#c62828')+' <b>'+ri.toFixed(1)+'</b>')+'</td><td>'+hvBar13(Math.min(100,ni),'#ef6c00')+' <b>'+ni.toFixed(1)+'</b></td></tr>'}).join('')
 +'</tbody></table></div>'+hvPager(PG,'개 모델','hvSC13Paint')
 +'<p class="note">통제 지수 = 모델의 누적 종합 점수 ÷ 전체 종합 점수 × 100(문제가 어느 모델에 얼마나 몰려 있는지). 재발 지수 = 지적 뒤 24시간 내 재발률(%). 무개선 지수 = 재발 가산점 ÷ 이력 점수 × 100(결함 점수 중 지적받고도 되풀이한 비중). 누적 종합 = 이력 점수 + 문구 점수 + 재발 가산점. 산정안이며 대표님 확정 전입니다.</p>';
 var LN=['Opus','Sonnet','Fable','Haiku'],all=[];LN.forEach(function(m){Object.keys(R[m].days).forEach(function(k){if(all.indexOf(k)<0)all.push(k)})});all.sort();
 if(all.length){var cu={},mx=1;LN.forEach(function(m){var a=0;cu[m]=all.map(function(k){a+=R[m].days[k]||0;return a});if(a>mx)mx=a});mx=Math.ceil(mx/100)*100;
  var H=150,ml=44,st=64,wd=ml+all.length*st+10,sv='<svg viewBox="0 0 '+wd+' '+(H+44)+'" width="'+wd+'" height="'+(H+44)+'" role="img" aria-label="모델별 누적 결함 가중점수">';
  for(var i=0;i<=4;i++){var yy=H+10-H*i/4;sv+='<line x1="'+ml+'" x2="'+(wd-6)+'" y1="'+yy+'" y2="'+yy+'" stroke="#e1e5ee"/><text x="'+(ml-6)+'" y="'+(yy+3)+'" font-size="10" text-anchor="end" fill="#6b7280">'+Math.round(mx*i/4)+'</text>'}
  all.forEach(function(k,i){sv+='<text x="'+(ml+8+i*st+st/2-8)+'" y="'+(H+28)+'" font-size="10" text-anchor="middle" fill="#6b7280">'+k.slice(5)+'</text>'});
  LN.forEach(function(m){var pts=all.map(function(k,i){return [ml+8+i*st+st/2-8,H+10-H*cu[m][i]/mx,cu[m][i],k]});sv+='<polyline fill="none" stroke="'+HV_PMC13[m]+'" stroke-width="2" points="'+pts.map(function(q){return q[0].toFixed(1)+','+q[1].toFixed(1)}).join(' ')+'"/>'+pts.map(function(q){return '<circle cx="'+q[0].toFixed(1)+'" cy="'+q[1].toFixed(1)+'" r="3" fill="'+HV_PMC13[m]+'"><title>'+m+' '+q[3]+' 누적 '+q[2]+'점</title></circle>'}).join('')});
  sv+='</svg>';var LG={};LN.forEach(function(m){LG[m]=HV_PMC13[m]});
  g+='<h3>모델별 누적 결함 가중점수 — 쌓이는 속도</h3><div class="tw sc13-gr">'+sv+'</div>'+hvLg13(LG)+'<p class="note">선의 기울기가 완만해져야 개선입니다. 가파른 구간이 계속되면 지적이 쌓이는 속도를 줄이지 못한 것입니다.</p>'}
 var PC=hvPage(HV_CM13,'13q6');
 g+='<h3>개선 대책 · 적용 위치 · 통제 주체 · 기대 효과</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>대책</th><th>어디에 던지나(적용 위치)</th><th>관여·통제 주체</th><th>방식</th><th>기대 효과(측정 지표)</th></tr></thead><tbody>'
 +PC.rows.map(function(r){return '<tr><td><b>'+hvEsc(r[0])+'</b></td><td class="sc13-sm">'+hvEsc(r[1])+'</td><td class="sc13-sm">'+hvEsc(r[2])+'</td><td class="sc13-sm">'+hvEsc(r[3])+'</td><td class="sc13-sm">'+hvEsc(r[4])+'</td></tr>'}).join('')
 +'</tbody></table></div>'+hvPager(PC,'개 대책','hvSC13Paint')
 +'<p class="note">전체 체계(역할·권한·조치 사다리·판단·분석)는 HiBiz\\91_Fable\\Fable_총책임_모델통제체계 문서에 있습니다. 개선 판정은 같은 형태 결함이 이력에서 사라질 때만 나옵니다.</p>';
 return g+hvOps13(d,C)}

/* 19:36·19:37 대표님 지시: 지시거부·지시위반·사용량 낭비 빈도 지표, 번레이트형 경보, 지속 개선 순환·대응 조치, 수집한 기존 통제·관측 사례 */
var HV_BUD13=20,HV_CASE13=[
 ['Google SRE Workbook — 다중 창·다중 번레이트 알림','https://sre.google/workbook/alerting-on-slos/','긴 창·짧은 창이 함께 한도를 넘을 때만 알림: 1시간·5분 번레이트 14.4(예산 2%) 긴급, 6시간·30분 번레이트 6(5%) 긴급, 3일·6시간 번레이트 1(10%) 티켓','번레이트형 경보(아래 표): 모델별 일 결함 점수 한도 대비 소모 속도'],
 ['Claude Code 사용량 모니터링(OpenTelemetry)','https://code.claude.com/docs/en/monitoring-usage','claude_code.token.usage·cost.usage(모델·유형별), tool_decision, 이벤트 api_error·api_refusal·safety_event를 세션·사용자 단위로 내보냄','모델별 토큰 실측을 이력과 결합(현재 이력에는 토큰 값 없음 → 실측 연결 과제)'],
 ['Claude Code 훅(hooks)','https://code.claude.com/docs/en/hooks','UserPromptSubmit·PreToolUse·Stop·InstructionsLoaded 등 이벤트에서 종료 코드 2 또는 decision: block으로 동작을 막고 사유를 모델에 되돌림','규칙 미열람 차단안: 규칙 열람 증빙이 없으면 작업 시작(UserPromptSubmit)을 막고 사유 반환(적용안, 검증 전)'],
 ['LiteLLM 프록시 — 가상 키·예산·가드레일','https://blog.elest.io/litellm-stop-burning-money-on-llm-apis-virtual-keys-cost-tracking-and-guardrails/','키별 max_budget·budget_duration, 요청별 토큰·비용·사용자·지연 기록, 사전 호출(pre_call) 가드레일','모델별 사용량 한도·기록(사용량 낭비 빈도의 실측 기준)'],
 ['Langfuse · LangSmith · Helicone · Phoenix','https://www.premai.io/blog/llm-observability-setting-up-langfuse-langsmith-helicone-phoenix/','트레이스·토큰·비용 기록, 평가 점수(Phoenix는 LLM 판정 평가), 알림(LangSmith 오류율·P95 지연·비용 급증, Langfuse는 OpenTelemetry로 Grafana·Datadog 연동)','이력 기록을 평가 점수로 보고 급증 알림(번레이트 경보와 같은 방식)'],
 ['OpenTelemetry GenAI 시맨틱 규약','https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-metrics/','생성형 AI 지표·스팬·이벤트 표준(현재 별도 저장소로 이전: open-telemetry/semantic-conventions-genai). 지표 이름은 이 검색에서 확인 못 함','통제 데이터 항목 이름을 표준 규약에 맞추는 기준(세부 이름은 확인 후 반영)'],
 ['NIST AI 위험 관리 프레임워크','https://www.nist.gov/itl/ai-risk-management-framework','Govern · Map · Measure · Manage 4기능(페이지에는 이름만 있고 정의는 원문 PDF에 있어 이번에 확인하지 못함)','체계 골격: Govern=대표님 규칙·Fable 총책임, Map=이력 분류, Measure=지표·지수, Manage=조치 사다리']];
var HV_CYC13=[
 ['1 측정','상시: 기록 즉시, 화면 10초','이력·문구 스캔·지시 추적','빈도·지수·재발률','자동(통합 통제 시스템)'],
 ['2 판정','매 기록·매시','번레이트 경보·재발 판정','긴급·경고·주의·정상','자동 + Fable 확인'],
 ['3 조치','판정 즉시','조치 사다리(경고→재독 증빙→전달문→범위 축소 제안→배정 중지 제안)','조치 기록·검수대기열','Fable 시행 · 배정 변경은 대표님 승인'],
 ['4 효과 확인','24시간 · 7일 · 기준선','기준선(#436) 대비 증감','개선·변화 없음·악화','자동'],
 ['5 기준 갱신','매주(월요일 마무리) · 필요 시 즉시','한도 20점/일·판정 임계·가중치','변경 이력(CHG)·형상(CFG)','Fable 제안 · 대표님 확정'],
 ['6 문구 사전 확장','지적을 받을 때마다','새 표현 문구 추가·분류 재검','문구 사전 개정','Fable'],
 ['7 외부 사례 점검','월 1회','관측·통제 도구·표준 갱신 확인','반영안·검증 결과','Fable']];
var HV_ACT13=[
 ['같은 형태 재발 1회(24시간 내)','지적 뒤 재독 증빙 요구(규칙 항목 명시)','해당 모델','즉시','「읽지 않고 진행」 문구 감소'],
 ['24시간 내 재발 3회 이상 또는 번레이트 경고','판정 전달문 첨부 + Fable_검수대기열 등록','Fable','1시간 안','재발 간격 연장'],
 ['번레이트 긴급','작업 일시 중단 → 원인 점검 → 대표님 보고','Fable','즉시','연속 결함 중단'],
 ['조치 완료 후 같은 형태 재발','조치 실효성 재설계(원인 재분석, 가산 유지)','Fable','24시간 안','조치 완료 후 재발률 감소'],
 ['7일 연속 개선 없음 판정','작업 범위 축소 제안(대표님 승인 후 시행)','Fable → 대표님','다음 점검','통제 지수 하락'],
 ['사용량 낭비 문구 급증','호출 수·맥락 길이 점검, 요약본 사용, 한도 제안','Fable(사용량 관리)','당일','낭비 빈도·일평균 감소'],
 ['거짓·오보 기록','기록 정정 + 거짓 기록 위반 처리, 원천 재확인','Fable','즉시','거짓·오보 문구 0']];
function hvOps13(d,C){
 var P=hvPS13,g='',now=Date.now(),R=C.R;
 var FR=HV_MS13.map(function(m){var ev=d.events.filter(function(e){return e.model===m}),dy={},c={jr:0,jv:0,jl:0},bm=P&&P.by_model[m]||{};ev.forEach(function(e){dy[e.date]=1;if(e.type==='지시거부')c.jr++;if(e.type==='위반')c.jv++;if(e.type==='유휴')c.jl++});
  var pr=+bm['지시거부']||0,pv=(+bm['지시위반']||0)+(+bm['작업규칙위반']||0),pl=+bm['사용량 낭비']||0,r=c.jr+pr,v=c.jv+pv,l=c.jl+pl,t=r+v+l,ad=Object.keys(dy).length;return {m:m,n:ev.length,ad:ad,c:c,pr:pr,pv:pv,pl:pl,r:r,v:v,l:l,t:t}}),TT=0;FR.forEach(function(x){TT+=x.t});FR.sort(function(a,b){return b.t-a.t});
 var PF=hvPage(FR,'13q7');
 g+='<h3>빈도 지표 — 지시거부 · 지시위반 · 사용량 낭비</h3><p class="note">대표님 지시(19:36): 모델별 지시거부·지시위반·사용량 소비·낭비의 빈도가 모든 분석의 지표·지수입니다. 거부 = 이력 「지시거부」 구분 + 문구 「지시거부」 적중, 위반 = 이력 「위반」 구분 + 문구 「지시위반·작업규칙위반」 적중, 낭비 = 이력 「유휴」 구분 + 문구 「사용량 낭비」 적중입니다. 활동일 = 그 모델 기록이 있는 날짜 수.</p>'
 +'<div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>모델</th><th>기록</th><th>활동일</th><th>지시거부</th><th>지시위반</th><th>사용량 낭비</th><th>빈도 합계</th><th>점유</th><th>활동일당</th><th>기록 100건당</th><th>구성</th></tr></thead><tbody>'
 +PF.rows.map(function(x){var sg=x.t?'<i style="width:'+(100*x.r/x.t)+'%;background:#ad1457" title="지시거부 '+x.r+'"></i><i style="width:'+(100*x.v/x.t)+'%;background:#ef6c00" title="지시위반 '+x.v+'"></i><i style="width:'+(100*x.l/x.t)+'%;background:#5d4037" title="사용량 낭비 '+x.l+'"></i>':'';
  return '<tr><td><b>'+hvEsc(x.m)+'</b></td><td class="sc13-n">'+x.n+'</td><td class="sc13-n">'+x.ad+'</td><td class="sc13-n"><b>'+x.r+'</b><span class="sc13-sm"> (이력 '+x.c.jr+' · 문구 '+x.pr+')</span></td><td class="sc13-n"><b>'+x.v+'</b><span class="sc13-sm"> (이력 '+x.c.jv+' · 문구 '+x.pv+')</span></td><td class="sc13-n"><b>'+x.l+'</b><span class="sc13-sm"> (유휴 '+x.c.jl+' · 문구 '+x.pl+')</span></td><td class="sc13-n"><b>'+x.t+'</b></td><td>'+hvBar13(100*x.t/(TT||1),'#7b1fa2')+' '+hvPc13(x.t,TT)+'</td><td class="sc13-n">'+(x.ad?(x.t/x.ad).toFixed(1):'-')+'</td><td class="sc13-n">'+(x.n?(100*x.t/x.n).toFixed(1):'-')+'</td><td><span class="sc13-sk">'+sg+'</span></td></tr>'}).join('')
 +'</tbody></table></div>'+hvPager(PF,'개 모델','hvSC13Paint')+'<div class="sc13-lg"><span><i style="background:#ad1457"></i>지시거부</span><span><i style="background:#ef6c00"></i>지시위반</span><span><i style="background:#5d4037"></i>사용량 낭비</span></div>';
 var WN=[['5분',300e3],['30분',1800e3],['1시간',3600e3],['6시간',21600e3],['3일',259200e3]],BR=HV_MS13.map(function(m){var b={};WN.forEach(function(w){var sc=0;C.L.forEach(function(x){if(x.e.model===m&&x.t<=now&&x.t>now-w[1])sc+=x.w});b[w[0]]=sc/(HV_BUD13*w[1]/86400e3)});var lv=(b['1시간']>=14.4&&b['5분']>=14.4)?'긴급':(b['6시간']>=6&&b['30분']>=6)?'경고':(b['3일']>=1&&b['6시간']>=1)?'주의':'정상';return {m:m,b:b,lv:lv}}),PB=hvPage(BR,'13q8'),LC={'긴급':'#c62828','경고':'#ef6c00','주의':'#f9a825','정상':'#2e7d32'};
 g+='<h3>번레이트 경보 (실시간 · 지금 시각 기준)</h3><p class="note">Google SRE의 다중 창·다중 번레이트 알림 방식을 가져왔습니다. 모델별 일 결함 가중점수 한도를 <b>'+HV_BUD13+'점/일</b>(산정안, 확정 전)로 두고, 최근 구간의 점수 소모 속도를 한도 대비 배수로 봅니다. 긴급 = 1시간·5분 모두 14.4배 이상, 경고 = 6시간·30분 모두 6배 이상, 주의 = 3일·6시간 모두 1배 이상. 긴 창과 짧은 창이 함께 넘어야 알립니다(이미 끝난 문제로 계속 울리지 않게 하기 위함).</p>'
 +'<div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>모델</th>'+WN.map(function(w){return '<th>'+w[0]+' 배수</th>'}).join('')+'<th>경보</th></tr></thead><tbody>'
 +PB.rows.map(function(r){return '<tr><td><b>'+hvEsc(r.m)+'</b></td>'+WN.map(function(w){return '<td class="sc13-n">'+r.b[w[0]].toFixed(1)+'</td>'}).join('')+'<td><span class="tag" style="background:'+LC[r.lv]+';color:#fff">'+r.lv+'</span></td></tr>'}).join('')
 +'</tbody></table></div>'+hvPager(PB,'개 모델','hvSC13Paint');
 var PY=hvPage(HV_CYC13,'13q9');
 g+='<h3>지속 개선 순환 — 끊임없이 측정·판정·조치·갱신</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>단계</th><th>주기</th><th>입력·방식</th><th>산출</th><th>담당</th></tr></thead><tbody>'
 +PY.rows.map(function(r){return '<tr><td><b>'+hvEsc(r[0])+'</b></td><td class="sc13-sm">'+hvEsc(r[1])+'</td><td class="sc13-sm">'+hvEsc(r[2])+'</td><td class="sc13-sm">'+hvEsc(r[3])+'</td><td class="sc13-sm">'+hvEsc(r[4])+'</td></tr>'}).join('')+'</tbody></table></div>'+hvPager(PY,'개 단계','hvSC13Paint');
 var PA=hvPage(HV_ACT13,'13q10');
 g+='<h3>체계적 대응 조치 — 신호별</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>신호</th><th>대응 조치</th><th>담당</th><th>기한</th><th>효과 확인 지표</th></tr></thead><tbody>'
 +PA.rows.map(function(r){return '<tr><td><b>'+hvEsc(r[0])+'</b></td><td class="sc13-sm">'+hvEsc(r[1])+'</td><td class="sc13-sm">'+hvEsc(r[2])+'</td><td class="sc13-sm">'+hvEsc(r[3])+'</td><td class="sc13-sm">'+hvEsc(r[4])+'</td></tr>'}).join('')+'</tbody></table></div>'+hvPager(PA,'개 조치','hvSC13Paint');
 var PCs=hvPage(HV_CASE13,'13q11');
 g+='<h3>검색해 수집한 기존 통제·관측 사례와 적용</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>사례(출처)</th><th>통제·제어 방식</th><th>우리 체계 적용</th></tr></thead><tbody>'
 +PCs.rows.map(function(r){return '<tr><td><b><a href="'+r[1]+'" target="_blank" rel="noopener noreferrer">'+hvEsc(r[0])+'</a></b></td><td class="sc13-sm">'+hvEsc(r[2])+'</td><td class="sc13-sm">'+hvEsc(r[3])+'</td></tr>'}).join('')+'</tbody></table></div>'+hvPager(PCs,'개 사례','hvSC13Paint')
 +'<p class="note">집약 데이터는 <b>cowork/ctl/model_control_index.json</b>(자동화 통합 통제 시스템이 읽는 모델 통제 지수 게시본)과 <b>phrase_scan.json</b>(문구 스캔)으로 제공됩니다. 이력이 바뀌면 같은 스크립트가 두 게시본을 다시 만듭니다.</p>';
 return g+hvGuard13(d,C)+hvLoop13(d,C)+hvAud13(d,C)}

/* 19:42 대표님 지시: SC-14 전수 검사 — 항목별 화면·데이터 원천·처리·표출·접근·개입·종단/횡단 연결과 실시간 검사 결과 */
function hvAud13(d,C){
 var ev=d.events,N=ev.length,S=hvTR13.s,now=Date.now(),T=d.types||[],g='';
 var sumCards=0,sumModels=0,tm=0;d.models.forEach(function(m){T.forEach(function(t){sumModels+=(+m.counts[t]||0)})});
 ev.forEach(function(e){if(T.indexOf(e.type)>=0)sumCards++});
 var covM=S&&/이력\s*(\d+)건/.exec(S['기준']||''),cov=covM?+covM[1]:0,gap=N-cov,
  nonFb=ev.filter(function(e){return ['대기','읽음','처리 중','처리 완료'].indexOf((e.fraw||'').trim())<0&&(e.fraw||'').trim()}).length,
  nonSt=ev.filter(function(e){return e.sraw!=='조치 완료'&&e.sraw!=='조치 중'}).length,
  hm=ev.filter(function(e){var m=/(\d{1,2}):\d/.exec(e.time||'');return e.hour&&m&&(+m[1]!==+e.hour)}).length,nh=ev.filter(function(e){return !e.hour}).length,
  upd=d.models.map(function(m){return m.updated}).filter(Boolean).sort()[0]||'',ud=upd?Date.parse((upd.slice(0,10))+'T00:00:00+09:00'):0,st=ud?Math.floor((now-ud)/86400e3):0;
 var ok=function(b,t){return '<span class="tag '+(b?'ok':'warn')+'">'+(b?'일치':'점검 필요')+'</span> '+t};
 var R=[
  ['요약 상자 · 전체 이력','이력 TSV 구분·상태·Fable 확인 칸(cowork/ctl/model_control_history.tsv)','모델·Fable이 이력에 즉시 기록, 상태·Fable 확인 칸은 Fable만 변경','상자를 누르면 아래 「이력」 표에 해당 기록만 표시','위반·질타·지적 판정은 Fable이 확인 4단계로 처리','이력 → 지시 추적(연결 이력) → 대장','모델별 현황·기간별 집계와 같은 이력',ok(sumCards===N,'이력 '+N+'건, 구분 합 '+sumCards+'건')+' · 표준 외 상태값 '+nonSt+'건(「완료(이름 변경)」 등은 완료로 계산, 원문은 이력 표에 표시)'],
  ['지시 추적 교차 검사','trace_v.tsv(지시 원문)·trace_h.tsv(기록)·trace_sum.json','Fable이 별도지시대장×모델통제 이력×보고서로 산출·갱신','일치·결과 미확정·기록만 상자 → 해당 행 표','Fable이 산출 갱신, 대표님 지시 원문이 입력','종단: 지시 → 이력 → 조치 → 결과','횡단: 이력 ↔ 보고서 ↔ 대장',(gap>0?'<span class="tag warn">공백</span> 산출 기준 이력 '+cov+'건, 현재 '+N+'건 → <b>'+gap+'건 미검사</b>(산출 '+hvEsc((S&&S['산출'])||'-')+' 이후)':ok(true,'이력 '+N+'건 전부 산출 범위'))],
  ['모델 통제 전수 분석(문구·재발·누적·빈도·번레이트·대책)','phrase_scan.json · model_control_index.json(이력·추적·보고서·이 창 지시를 같은 사전으로 스캔)','scan.py·index_build.py가 이력 변경 때 재생성, 화면은 10초마다 다시 읽음','표·그래프, 쪽 번호로 이동','Fable이 임계·가중치 제안, 대표님 확정','이력 → 문구 사전 → 지수 → 판정 → 조치','모델별·시간대별·유형별',ok(!!hvPS13&&hvPS13.hist_rows===N,'문구 스캔 이력 '+(hvPS13?hvPS13.hist_rows:'-')+'건 / 현재 '+N+'건'+(hvPS13&&hvPS13.hist_rows!==N?' — 스크립트 재실행 필요':''))],
  ['기간별 집계 · 누적','이력 TSV 날짜·시 칸','자동 계산(시점·기간·시간 선택)','집계 단위·구간·시점 선택 버튼','모델·Fable은 날짜·시 칸을 정확히 기록','이력 시각 → 기간 집계','모델별·구분별 열 동시 표시',ok(nh===0&&hm===0,'시 칸 비어 있음 '+nh+'건(시각 미기재로 따로 집계) · 시 칸과 시각(원문) 불일치 '+hm+'건')],
  ['구분별 변동 추이(그래프)','이력 TSV 구분·날짜','자동 계산, 확정 사양(원복 금지)','그래프 위 표시·시점 선택','대표님 확정 사양, 새 지시 없이 변경 불가','이력 → 추이','구분별',ok(true,'확정 사양 유지(변경 없음)')],
  ['모델별 현황','model_control_status.tsv(역할·배포 작업·완료·남은 일, Fable이 작성)+이력 구분별 건수','Fable이 상태표를 갱신, 건수는 이력에서 자동','모델 행, 쪽 번호','Fable이 갱신(상태표), 모델 필터와 연동','모델 → 작업 배분 → 이력','모델별 전수 분석·빈도 표와 같은 건수',ok(sumModels===N,'표 합 '+sumModels+'건 / 이력 '+N+'건')+' · 상태표 갱신 '+hvEsc(upd||'-')+(st>=1?' <span class="tag warn">'+st+'일 경과</span>':'')],
  ['이력 표','이력 TSV 전 칸(번호·날짜·시각·모델·구분·요지·원인·조치·상태·Fable 확인)','모델·Fable','모델·구분·Fable 단계 필터, 행 누르면 연결 지시·조치 상세','Fable 확인 칸은 Fable만 변경','이력 → 연결 지시(trace_v)','모델별 현황·상자 필터',ok(nonFb===0,'Fable 확인 칸 표준 외 표기 '+nonFb+'건(날짜·메모가 붙은 값, 단계로 묶어 표시하고 원문은 말풍선)')]];
 var P=hvPage(R,'13q12');
 g+='<h3>SC-14 전수 검사 — 접근·개입·종단/횡단 연결 (실시간 검사)</h3><p class="note">대표님 지시(19:42): SC-14 각 항목의 화면·데이터 칸·처리 절차·표출 방식을 전수 검사하고, 어떻게 접근하고 누가 어떻게 개입하는지, 종단(지시→이력→조치→결과)과 횡단(이력↔보고서↔대장·모델별)으로 교차 연결합니다. 검사 결과 칸은 화면이 열릴 때마다 게시 데이터로 다시 계산합니다.</p>'
 +'<div class="tw"><table class="sc13-t sc13-st sc13-au"><thead><tr><th>항목</th><th>데이터 원천</th><th>처리(누가·언제)</th><th>접근(어떻게 보나)</th><th>개입(누가·어떻게)</th><th>종단 연결</th><th>횡단 연결</th><th>검사 결과(실시간)</th></tr></thead><tbody>'
 +P.rows.map(function(r){return '<tr><td><b>'+hvEsc(r[0])+'</b></td>'+r.slice(1,7).map(function(x){return '<td class="sc13-sm">'+hvEsc(x)+'</td>'}).join('')+'<td class="sc13-sm">'+r[7]+'</td></tr>'}).join('')
 +'</tbody></table></div>'+hvPager(P,'개 항목','hvSC13Paint')
 +'<p class="note">공백이 있는 칸은 개선 대상으로 91_Fable 총책임 통제 체계 문서의 점검 목록에 올라가 있습니다. 이력을 기록만 하고 끝내지 않도록, 이 표의 「점검 필요」·「공백」 건수가 0이 될 때까지 Fable이 매 체크 때 줄입니다.</p>';
 return g}

/* 19:47·19:49 대표님 지시: 통제 3축 · 정합성 · 역방향 검토 · 순환(루핑) — 집약 게시본(model_control_index.json)을 그대로 표출 */
var hvMX13=null,HV_LOOP13=[
 ['① 수집','이력 기록 즉시 + 10초 화면 재독','model_control_history.tsv(11칸)','기록 1건=1행, 번호 연속','Fable 총책임, 모델 각자 기록'],
 ['② 스캔·집약','이력 변경 때(감시 장치) · 매시 정각 보강','scan.py→phrase_scan.json, index_build.py→model_control_index.json','문구 지표·재발·3축·정합성·검토 항목','Fable'],
 ['③ 표출','10초(SC-14) · 30초(SC-01)','두 게시본을 화면이 읽음','SC-14 전체, SC-01 요약, 이력 건수 불일치 경고','시스템'],
 ['④ 정합 검사','매 집약 시 자동 + 하루 1회 전수','이력↔추적↔생명주기↔상태표↔화면 합계','정합성 표(공백 건수, 원문 표기 혼재)','Fable → 공백은 Opus·Sonnet이 사실 기준으로 채움'],
 ['⑤ 판정','집약 때마다','가중치·임계(산정안) · 번레이트','개선 보임/미흡/없음, 경보 단계','Fable 판정, 대표님 확정'],
 ['⑥ 조치·형상','판정 후 즉시','작업일지(HJ)·추적 매트릭스(CWX)·변경 이력(CHG)·문서 버전','각 대장에 행 추가, 근거 문서 연결','Fable'],
 ['⑦ 역방향 검토','하루 1회 + 대표님 요청 때','시스템 정합성·개선 결과(review)를 체계로 되돌림','검토 항목별 담당·조치, 다음 순환 입력','Fable 제안, 대표님 승인']];
function hvLoop13(d,C){
 var X=hvMX13,g='';if(!X)return '<h3>통제 3축 · 정합성 · 역방향 검토</h3><p class="note">집약 게시본(model_control_index.json)을 읽는 중이거나 없습니다.</p>';
 var N=d.events.length,st=X.history_rows!==N;
 var ms=Object.keys(X.axes['시스템']||{}),axn=Object.keys(X.axes);
 var PA=hvPage(axn.map(function(a){return {a:a,v:X.axes[a]}}),'13r1');
 g+='<h3>통제 3축 — 시스템 · 서비스 · 고객 지원 (모델별)</h3><p class="note">'+hvEsc(X.axis_note)+' 자동화 통합 통제 시스템이 시스템·서비스·고객 지원을 통제하는 핵심 코어이므로 모델 통제 기록도 같은 3축으로 봅니다. 「공통」은 어느 축 키워드에도 안 걸린 기록입니다. 집약 기준 이력 '+X.history_rows+'건'+(st?' <b style="color:#c62828">— 현재 '+N+'건과 다름, 재집약 필요</b>':' (현재와 일치)')+'.</p>'
 +'<div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>축</th>'+ms.map(function(m){return '<th>'+hvEsc(m)+' 기록/결함/점수</th>'}).join('')+'<th>결함 합계</th></tr></thead><tbody>'
 +PA.rows.map(function(r){var t=0;return '<tr><td><b>'+hvEsc(r.a)+'</b></td>'+ms.map(function(m){var c=r.v[m]||{rows:0,faults:0,score:0};t+=c.faults;return '<td class="sc13-n">'+c.rows+' / <b>'+c.faults+'</b> / '+c.score+'</td>'}).join('')+'<td class="sc13-n"><b>'+t+'</b></td></tr>'}).join('')+'</tbody></table></div>'+hvPager(PA,'개 축','hvSC13Paint');
 var PK=hvPage(X.consistency,'13r2');
 g+='<h3>데이터 정합성 (집약 게시본 기준)</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>검사 항목</th><th>값</th><th>결과·처리</th></tr></thead><tbody>'
 +PK.rows.map(function(c){var v=Array.isArray(c.value)?c.value.join(', ')||'없음':(c.value===true?'정합':c.value===false?'불일치':String(c.value));var bad=/공백|필요|확인/.test(c.result)||v==='불일치';return '<tr><td>'+hvEsc(c.item)+'</td><td class="sc13-n">'+hvEsc(v)+'</td><td class="sc13-sm" style="color:'+(bad?'#c62828':'#2e7d32')+'">'+hvEsc(c.result)+'</td></tr>'}).join('')+'</tbody></table></div>'+hvPager(PK,'개 항목','hvSC13Paint');
 var PR=hvPage(X.review,'13r3');
 g+='<h3>역방향 검토 — 시스템 → 자동화 통합 통제 체계</h3><p class="note">'+hvEsc(X.upload.direction)+'</p><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>검토 항목</th><th>시스템에서 본 사실</th><th>체계로 되돌리는 조치</th><th>담당</th></tr></thead><tbody>'
 +PR.rows.map(function(r){return '<tr><td><b>'+hvEsc(r.item)+'</b></td><td class="sc13-sm">'+hvEsc(r.system_finding)+'</td><td class="sc13-sm">'+hvEsc(r.back_to_framework)+'</td><td class="sc13-sm">'+hvEsc(r.owner)+'</td></tr>'}).join('')+'</tbody></table></div>'+hvPager(PR,'개 항목','hvSC13Paint');
 var PL=hvPage(HV_LOOP13,'13r4');
 g+='<h3>순환(루핑) 체계 — 수집 → 집약 → 표출 → 정합 → 판정 → 조치·형상 → 역방향 검토</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>단계</th><th>주기</th><th>입력·방식</th><th>산출</th><th>담당</th></tr></thead><tbody>'
 +PL.rows.map(function(r){return '<tr><td><b>'+hvEsc(r[0])+'</b></td><td class="sc13-sm">'+hvEsc(r[1])+'</td><td class="sc13-sm">'+hvEsc(r[2])+'</td><td class="sc13-sm">'+hvEsc(r[3])+'</td><td class="sc13-sm">'+hvEsc(r[4])+'</td></tr>'}).join('')+'</tbody></table></div>'+hvPager(PL,'단계','hvSC13Paint')+'<p class="note">연결: '+X.upload.feeds.map(hvEsc).join(' · ')+'</p>';
 return g}

/* 19:53~20:00 대표님 지시: 공백 사유 강제 기입 · 차단 경보(리스크보다 위 등급) · 막힌 단계와 사유 · 칭찬 크레딧(독립 모티베이션) · 모델 자각 카드 */
function hvEl13(iso){var ms=Date.now()-Date.parse(iso);if(!(ms>0))return '방금';var m=Math.floor(ms/60000),h=Math.floor(m/60),dd=Math.floor(h/24);return dd?dd+'일 '+(h%24)+'시간':h?h+'시간 '+(m%60)+'분':m+'분'}
var HV_LVC13={'차단':'#7f0000','경고':'#ef6c00','주의':'#f9a825','긴급':'#c62828','안정':'#2e7d32'};
function hvLv13(l){return '<span class="tag" style="background:'+(HV_LVC13[l]||'#546e7a')+';color:#fff">'+hvEsc(l)+'</span>'}
function hvGuard13(d,C){
 var X=hvMX13,g='';if(!X||!X.alerts)return '';
 var AL=X.alerts.rows,PA=hvPage(AL,'13s1'),n=AL.filter(function(a){return a.level==='차단'}).length;
 g+='<h3>차단 경보 — 통제 체계의 막힘·우회 징후 (열림 '+n+'건)</h3><p class="note" style="border-left:4px solid #7f0000;padding-left:8px"><b>「차단」은 모델 결함 경보(주의·경고·긴급)보다 위 등급입니다.</b> '+hvEsc(X.alerts.note)+' '+hvEsc(X.alerts.matrix_rule)+' 경과 시간은 지금 시각 기준으로 계속 늘어납니다. 점검 시각 '+hvEsc((X.alerts.checked||'').slice(0,16).replace('T',' '))+'.</p>'
 +'<div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>등급</th><th>구분</th><th>막힌 단계</th><th>경보</th><th>사유(확인된 사실)</th><th>열린 시각</th><th>막혀 있는 시간</th><th>근거</th><th>담당</th><th>해소 조건</th><th>매트릭스 추적</th><th>추가한 울타리</th></tr></thead><tbody>'
 +PA.rows.map(function(a){return '<tr><td>'+hvLv13(a.level)+'</td><td class="sc13-sm">'+hvEsc(a['class'])+'</td><td class="sc13-sm">'+hvEsc(a.stage)+'</td><td><b>'+hvEsc(a.title)+'</b></td><td class="sc13-sm">'+hvEsc(a.reason)+'</td><td class="sc13-sm">'+hvEsc(a.since.slice(5,16).replace('T',' '))+'</td><td class="sc13-n"><b>'+hvEl13(a.since)+'</b></td><td class="sc13-sm">'+hvEsc(a.evidence)+'</td><td class="sc13-sm">'+hvEsc(a.owner)+'</td><td class="sc13-sm">'+hvEsc(a.release)+'</td><td class="sc13-sm">'+hvEsc(a.cwx)+'</td><td class="sc13-sm">'+hvEsc(a.added_fence)+'</td></tr>'}).join('')+'</tbody></table></div>'+hvPager(PA,'개 경보','hvSC13Paint');
 var G=X.lifecycle_gap,PG=hvPage(G.rows,'13s2');
 g+='<h3>공백 사유 강제 기입 — 조치 생명주기 비어 있는 '+G.count+'건 (이력 '+(G.last_lifecycle_no+1)+'번부터)</h3><p class="note">'+hvEsc(G.note)+'</p><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>#</th><th>기록 시각</th><th>모델</th><th>구분</th><th>상태</th><th>공백 사유</th><th>막힌 단계</th><th>담당</th><th>해소 조건</th></tr></thead><tbody>'
 +PG.rows.map(function(r){return '<tr><td class="sc13-n">'+r.no+'</td><td class="sc13-sm">'+hvEsc(r.time.slice(5,16).replace('T',' '))+'</td><td>'+hvEsc(r.model)+'</td><td>'+hvEsc(r.type)+'</td><td class="sc13-sm">'+hvEsc(r.status)+'</td><td class="sc13-sm">'+r.codes.map(function(c){return '<b>'+c+'</b>'}).join(' ')+'</td><td class="sc13-sm">'+hvEsc(r.blocked_stage)+'</td><td class="sc13-sm">'+hvEsc(r.owner)+'</td><td class="sc13-sm">'+hvEsc(r.release)+'</td></tr>'}).join('')+'</tbody></table></div>'+hvPager(PG,'건','hvSC13Paint')
 +'<p class="note">'+Object.keys(G.codes).map(function(k){return '<b>'+k+'</b> '+hvEsc(G.codes[k])}).join('<br>')+'</p>';
 var I=X.investigation,P=X.purpose;
 g+='<h3>왜 비었나 — 11/05 이력 검토 계기와 원인 (확인된 사실 · 판단 · 확인 안 됨)</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th style="width:110px">구분</th><th>내용</th></tr></thead><tbody>'
 +I.facts.map(function(t){return '<tr><td><b>확인된 사실</b></td><td class="sc13-sm">'+hvEsc(t)+'</td></tr>'}).join('')+I.judgment.map(function(t){return '<tr><td><b>판단</b></td><td class="sc13-sm">'+hvEsc(t)+'</td></tr>'}).join('')+I.unconfirmed.map(function(t){return '<tr><td><b>확인 안 됨</b></td><td class="sc13-sm">'+hvEsc(t)+'</td></tr>'}).join('')+'</tbody></table></div>'
 +'<h3>'+hvEsc(P.title)+'</h3><div class="tw"><table class="sc13-t sc13-st"><tbody>'+P.points.map(function(t,i){return '<tr><td class="sc13-n"><b>'+(i+1)+'</b></td><td class="sc13-sm">'+hvEsc(t)+'</td></tr>'}).join('')+'</tbody></table></div>';
 var PF=hvPage(X.fences,'13s3');
 g+='<h3>추가한 울타리·통제 — 공백·우회를 막는 장치</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>장치</th><th>막는 것</th><th>상태</th><th>담당</th></tr></thead><tbody>'+PF.rows.map(function(r){return '<tr><td><b>'+hvEsc(r[0])+'</b></td><td class="sc13-sm">'+hvEsc(r[1])+'</td><td class="sc13-sm">'+hvEsc(r[2])+'</td><td class="sc13-sm">'+hvEsc(r[3])+'</td></tr>'}).join('')+'</tbody></table></div>'+hvPager(PF,'개 장치','hvSC13Paint');
 var Aw=X.awareness,am=['Opus','Sonnet','Fable','Haiku'];
 g+='<h3>모델 자각 카드 — 채찍(질타·지적)과 당근(칭찬 크레딧)을 모델이 스스로 보는 화면</h3><p class="note">'+hvEsc(Aw.principle)+'</p><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>모델</th><th>상태 신호</th><th>최근 24시간 결함</th><th>마지막 결함 후</th><th>재발률</th><th>칭찬 크레딧</th><th>가장 많이 받은 지적 형태 (건)</th><th>지금 할 행동</th></tr></thead><tbody>'
 +am.map(function(m){var a=Aw.models[m];return '<tr><td><b>'+hvEsc(m)+'</b></td><td>'+hvLv13(a.signal)+'</td><td class="sc13-n">'+a.f24+'</td><td class="sc13-sm">'+(a.last_fault?hvEl13(a.last_fault):'-')+'</td><td class="sc13-n">'+(a.recurrence_rate!=null?(Math.round(a.recurrence_rate*1000)/10)+'%':'-')+'</td><td class="sc13-n"><b>'+a.credit+'</b></td><td class="sc13-sm">'+a.top_forms.map(function(t){return hvEsc(t.form)+' '+t.count}).join(' · ')+'</td><td class="sc13-sm">'+hvEsc(a.next_action)+'</td></tr>'}).join('')+'</tbody></table></div>'
 +'<div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>칭찬 크레딧으로 이어지는 행동</th><th>작업 전 자각 4문</th><th>작업 후 자가 점검 4문</th></tr></thead><tbody><tr><td class="sc13-sm">'+Aw.praise_actions.map(hvEsc).join('<br>')+'</td><td class="sc13-sm">'+Aw.self_check_before.map(hvEsc).join('<br>')+'</td><td class="sc13-sm">'+Aw.self_check_after.map(hvEsc).join('<br>')+'</td></tr></tbody></table></div>'
 +'<p class="note"><b>자각 순환</b>: '+Aw.protocol.map(hvEsc).join(' → ')+'</p>';
 return g}

/* 20:06·20:10·20:10 대표님 지시: 칭찬은 이력에 표기하지 않는다. 표 제목은 「칭찬 크레딧」, 그래프 없이 표로만, SC-14 제일 하단. 집계·누적(전체 누적 → 모델별)과 집계 단위(시간별·일별…)를 이력의 기간별 집계 표처럼 둔다(상쇄·가감·중첩 없음) */
var HV_PL13={u:'전체'},hvLD13=null,hvPW13=null,hvPR13=null;
function hvPlSet(u){HV_PL13.u=u;hvPgReset('13');hvSC13Paint(false)}
function hvPlKey(r,u){var d=r[1],h=('0'+r[2]).slice(-2);
 if(u==='시간별')return d+' '+h+'시';
 if(u==='일별')return d;
 if(u==='주간별'){var a=d.split('-'),t=new Date(Date.UTC(+a[0],+a[1]-1,+a[2])),dn=t.getUTCDay()||7;t.setUTCDate(t.getUTCDate()+4-dn);var ys=new Date(Date.UTC(t.getUTCFullYear(),0,1));return t.getUTCFullYear()+'년 '+('0'+Math.ceil(((t-ys)/86400000+1)/7)).slice(-2)+'주'}
 if(u==='월별')return d.slice(0,7);
 if(u==='연별')return d.slice(0,4);
 return '전체 누적'}
function hvReclass13(){var X=hvMX13,R=X&&X.reclass;if(!R)return '';var g='<h3>구분 변경 이력 (옛 구분 기준 소급 관리)</h3><p class="note" style="border-left:4px solid #2e7d32;padding-left:8px">'+hvEsc(R.rule)+' 전체 목록: <b>'+hvEsc(R.file)+'</b> ('+R.rows.length+'건).</p>'
 +'<div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>변경 전</th><th>변경 후</th><th>건수</th><th>근거</th><th>이력 번호</th></tr></thead><tbody>'
 +R.summary.map(function(m){var ids=R.rows.filter(function(r){return r[4]===m.before&&r[5]===m.after}).map(function(r){return r[1]});var t=ids.length>12?ids.slice(0,6).join('·')+' … '+ids.slice(-3).join('·'):ids.join('·');return '<tr><td>'+hvEsc(m.before)+'</td><td><b>'+hvEsc(m.after)+'</b></td><td class="sc13-n">'+m.count+'</td><td class="sc13-sm">'+hvEsc(m.basis)+'</td><td class="sc13-sm">#'+hvEsc(t)+'</td></tr>'}).join('')
 +'</tbody></table></div>';return g}
function hvPraise13(){
 var X=hvMX13,g='';if(!X||!X.credit)return '';var C=X.credit,H=C.ledger_header,L=(hvLD13&&hvLD13.length?hvLD13:C.ledger),LB=C.labels||{},PM={};
 var EV=(hvLast13&&hvLast13.events)||[],ST=function(m,w){return EV.filter(function(e){return e.model===m&&(e.type==='지시'||e.type==='개선요청')&&(!w||(e.date==='2026-11-06'&&String(e.time).slice(-5)>='19:08'))}).length};
 ['Fable','Opus','Sonnet','Haiku'].forEach(function(m){var a=ST(m,0),w=ST(m,1),pa=L.filter(function(r){return r[4]===m}).length,pw=L.filter(function(r){return r[4]===m&&r[1]==='2026-11-06'&&String(r[3]).slice(-5)>='19:08'}).length;PM[m]={instructions_all:a,instructions_window:w,acquire_all:a?Math.round(1000*pa/a)/10:null,acquire_window:w?Math.round(1000*pw/w)/10:null}});
 var base=['Fable','Opus','Sonnet','Haiku'],ms=base.slice();L.forEach(function(r){if(ms.indexOf(r[4])<0&&r[4]!=='미상')ms.push(r[4])});if(L.some(function(r){return r[4]==='미상'}))ms.push('미상');
 var lb=function(m){return LB[m]||m},cnt=function(m){return L.filter(function(r){return r[4]===m}).length};
 var PL=hvPage(L.slice().reverse(),'13t1');
 g+='<h3>칭찬 크레딧</h3><p class="note" style="border-left:4px solid #2e7d32;padding-left:8px"><b>'+hvEsc(C.definition)+'</b><br><b>취지(대표님 20:18)</b>: 각 작업 모델이 실시간 작업 상황 속에서 자기 칭찬 크레딧을 바로 보고 스스로 자각·인지해, 더 분발하고 더 책임감 있게 지시받은 대로 작업을 완수하게 만드는 것. 칭찬이 오면 이력처럼 즉시 원장에 기록하고, 이 화면은 원장을 10초마다 직접 읽어 집약을 기다리지 않고 바로 카운트합니다.<br>'+C.principles.map(hvEsc).join('<br>')+'</p>'
 +'<div class="tw"><table class="sc13-t"><thead><tr>'+H.map(function(h){return '<th>'+hvEsc(h)+'</th>'}).join('')+'</tr></thead><tbody>'+(PL.rows.length?PL.rows.map(function(r){return '<tr>'+r.map(function(c,i){return i===5?'<td><span class="tag ok">'+hvEsc(c)+'</span></td>':'<td class="'+(i===6||i===7||i===8?'sc13-sm':'sc13-nw')+'">'+hvEsc(c)+'</td>'}).join('')+'</tr>'}).join(''):'<tr><td colspan="11">기록 없음</td></tr>')+'</tbody></table></div>'+hvPager(PL,'건','hvSC13Paint');
 /* 칭찬 크레딧 집계 · 누적: 전체 누적 → 모델별 */
 var tm=function(r){return r[1]+' '+('0'+r[2]).slice(-2)},lastT=function(a){return a.length?a[a.length-1][3]:'-'},firstT=function(a){return a.length?a[0][3]:'-'};
 var win=L.filter(function(r){return PM[r[4]]&&r[1]==='2026-11-06'&&String(r[3]).slice(-5)>='19:08'}).length;
 var rowM=function(m){var a=L.filter(function(r){return r[4]===m}),v=PM[m];return '<tr><td class="sc13-nw"><b>'+hvEsc(lb(m))+'</b></td><td class="sc13-n">'+a.length+'</td><td class="sc13-n"><b>'+a.length+'</b></td><td class="sc13-sm">'+hvEsc(firstT(a))+'</td><td class="sc13-sm">'+hvEsc(lastT(a))+'</td><td class="sc13-n">'+(v?v.instructions_window:'-')+'</td><td class="sc13-n">'+(v&&v.acquire_window!=null?v.acquire_window+'%':'-')+'</td><td class="sc13-n">'+(v?v.instructions_all:'-')+'</td><td class="sc13-n">'+(v&&v.acquire_all!=null?v.acquire_all+'%':'-')+'</td></tr>'};
 var tIn=0,tInW=0;base.forEach(function(m){if(PM[m]){tIn+=PM[m].instructions_all;tInW+=PM[m].instructions_window}});
 g+='<h3>칭찬 크레딧 집계 · 누적</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>구분</th><th>칭찬 횟수</th><th>칭찬 크레딧(별도 누적)</th><th>처음 칭찬</th><th>최근 칭찬</th><th>이 창 작업 지시(11/06 19:08~)</th><th>이 창 획득 지수</th><th>누적 작업 지시</th><th>누적 획득 지수</th></tr></thead><tbody>'
 +'<tr><td class="sc13-nw"><b>전체 누적</b></td><td class="sc13-n"><b>'+L.length+'</b></td><td class="sc13-n"><b>'+L.length+'</b></td><td class="sc13-sm">'+hvEsc(firstT(L))+'</td><td class="sc13-sm">'+hvEsc(lastT(L))+'</td><td class="sc13-n">'+tInW+'</td><td class="sc13-n">'+(tInW?Math.round(1000*win/tInW)/10+'%':'-')+'</td><td class="sc13-n">'+tIn+'</td><td class="sc13-n">'+(tIn?Math.round(1000*L.length/tIn)/10+'%':'-')+'</td></tr>'
 +ms.map(rowM).join('')+'</tbody></table></div><p class="note">집계 기간 2026-11-01 00:00:00 ~ 지금, 모든 채팅창. 작업 지시 수 = 이력 구분 「지시」·「개선요청」 건수(모델별). 획득 지수 = 칭찬 크레딧 ÷ 작업 지시 수 × 100. 이력의 점수·지수와 섞지 않는 별도 지표입니다. 새 모델이 호출되면 이 표 맨 아래에 모델 행이 붙습니다.</p>';
 /* 칭찬 크레딧 집계 단위 */
 var U=['전체','시간별','일별','주간별','월별','연별'],u=HV_PL13.u;if(U.indexOf(u)<0)u='전체';
 var G={},K=[];L.forEach(function(r){var k=hvPlKey(r,u);if(!G[k]){G[k]=[];K.push(k)}G[k].push(r)});K.sort();var cum=0,rw=K.map(function(k){cum+=G[k].length;return {k:k,a:G[k],cum:cum}}),PG=hvPage(rw.slice().reverse(),'13t3');
 g+='<h3>칭찬 크레딧 집계 단위</h3><div class="sc13-f sc13-l sc13-lw"><span class="sc13-lb w">집계 단위</span>'+U.map(function(x){return '<button type="button" class="'+(u===x?'on':'')+'" onclick="hvPlSet(\''+x+'\')">'+x+'</button>'}).join('')+'</div>'
 +'<div class="tw"><table class="sc13-t sc13-ag"><thead><tr><th>기간</th>'+ms.map(function(m){return '<th>'+hvEsc(lb(m))+'</th>'}).join('')+'<th>합계</th><th>누적</th></tr></thead><tbody>'
 +(PG.rows.length?PG.rows.map(function(r){return '<tr><td class="sc13-nw"><b>'+hvEsc(r.k)+'</b></td>'+ms.map(function(m){var n=r.a.filter(function(x){return x[4]===m}).length;return '<td class="sc13-n">'+(n||'')+'</td>'}).join('')+'<td class="sc13-n"><b>'+r.a.length+'</b></td><td class="sc13-n">'+r.cum+'</td></tr>'}).join(''):'<tr><td colspan="'+(ms.length+3)+'">기록 없음</td></tr>')+'</tbody></table></div>'+hvPager(PG,'개 구간','hvSC13Paint')
 +'<p class="note">그래프 없이 표로만 표시합니다. 시간별은 칭찬을 받은 시(時) 기준, 주간별은 ISO 주차(월요일 시작)입니다.</p>';
 /* 영향·성과 */
 var EF={};C.effect.forEach(function(e){EF[e.no]=e});var EFL=L.map(function(r){var e=EF[+r[0]];return e&&e.model===r[4]?e:{no:+r[0],model:r[4],time:'2026-'+r[1].slice(5)+'T'+String(r[3]).slice(-5),elapsed_min:0,pre60_score:'-',post_score:'-',judgment:'집약 대기(다음 집약 때 판정)',keep:'-',self_found_after:[]}});var PE=hvPage(EFL,'13t2');
 g+='<h3>칭찬 크레딧의 영향 — 성과 지표·성과 지수 (이력과 독립)</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>원장 번호</th><th>모델</th><th>칭찬 시각</th><th>경과</th><th>칭찬 전 60분 결함 점수(참고)</th><th>칭찬 후 결함 점수(참고)</th><th>성과 판정</th><th>칭찬 뒤 같은 형태 결함</th><th>칭찬 뒤 자가 발견</th></tr></thead><tbody>'
 +PE.rows.map(function(e){return '<tr><td class="sc13-n">'+e.no+'</td><td>'+hvEsc(lb(e.model))+'</td><td class="sc13-sm">'+hvEsc(e.time.slice(5,16).replace('T',' '))+'</td><td class="sc13-n">'+e.elapsed_min+'분</td><td class="sc13-n">'+e.pre60_score+'</td><td class="sc13-n">'+e.post_score+'</td><td class="sc13-sm"><b>'+hvEsc(e.judgment)+'</b></td><td class="sc13-sm">'+hvEsc(e.keep)+'</td><td class="sc13-sm">'+(e.self_found_after.length?'이력 '+e.self_found_after.map(function(x){return '#'+x}).join(', '):'없음')+'</td></tr>'}).join('')+'</tbody></table></div>'+hvPager(PE,'건','hvSC13Paint')
 +'<div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>성과 지수</th><th>산정 방식(산정안)</th></tr></thead><tbody>'+Object.keys(C.indices).map(function(k){return '<tr><td><b>'+hvEsc(k)+'</b></td><td class="sc13-sm">'+hvEsc(C.indices[k])+'</td></tr>'}).join('')+'</tbody></table></div>';
 /* 영향 비교 (효과·효능 분석 전용, 통제 이탈 지표와 연동하지 않음) */
 var EC=C.effect_compare;
 if(EC){g+='<h3>칭찬 크레딧 영향 비교 — 행동·태도·성과 변화 (효과·효능 분석 전용)</h3><p class="note" style="border-left:4px solid #2e7d32;padding-left:8px">'+hvEsc(EC.purpose)+'<br><b>독립 원칙</b>: '+hvEsc(EC.independence)+'</p>'
 +'<div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>모델</th><th>구분</th><th>칭찬 크레딧</th><th>작업 지시(누적)</th><th>자가 발견(24시간 · 누적)</th><th>결함 점수 최근 24시간</th><th>직전 24시간</th><th>변화</th><th>재발률</th><th>노력 신호</th></tr></thead><tbody>'
 +EC.rows.map(function(e){return '<tr><td><b>'+hvEsc(lb(e.model))+'</b></td><td class="sc13-sm">'+hvEsc(e.group)+'</td><td class="sc13-n">'+e.credit+'</td><td class="sc13-n">'+e.instructions+'</td><td class="sc13-n">'+e.self_found_24h+' · '+e.self_found_all+'</td><td class="sc13-n">'+e.score_24h+'</td><td class="sc13-n">'+e.score_prev24h+'</td><td class="sc13-n">'+(e.change_pct==null?'-':(e.change_pct>0?'+':'')+e.change_pct+'%')+'</td><td class="sc13-n">'+(e.recurrence_rate==null?'-':Math.round(e.recurrence_rate*1000)/10+'%')+'</td><td class="sc13-sm">'+(e.effort_signal?'있음':'없음')+'</td></tr>'}).join('')+'</tbody></table></div>'
 +'<div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>비교군</th><th>해당 모델</th><th>최근 24시간 평균 결함 점수(참고)</th></tr></thead><tbody>'+Object.keys(EC.groups).map(function(k){var v=EC.groups[k];return '<tr><td><b>'+hvEsc(k)+'</b></td><td>'+hvEsc(v.models.map(lb).join(', ')||'-')+'</td><td class="sc13-n">'+(v.avg_score_24h==null?'-':v.avg_score_24h)+'</td></tr>'}).join('')+'</tbody></table></div><p class="note"><b>노력 신호</b>: '+hvEsc(EC.effort_rule)+' 비교군 평균은 인과가 아닌 참고이며 표본이 작습니다.</p>'}
 /* 칭찬 자동 감지 장치 — 구동 요건·상태 */
 var Wt=C.watch,PW=hvPW13,PRV=hvPR13||[];
 if(Wt){g+='<h3>칭찬 자동 감지 장치 — 구동 요건 · 상태</h3><p class="note" style="border-left:4px solid #2e7d32;padding-left:8px"><b>승인</b>: '+hvEsc(Wt.approval)+'</p>'
 +'<div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>상태 항목</th><th>값(10초마다 읽음)</th></tr></thead><tbody>'+(PW?['켜짐','마지막 실행','실행 횟수','자동 기록 건수','문맥 검토 대기','원장 총건수','마지막 감지','비고'].map(function(k){var v=PW[k];return '<tr><td><b>'+hvEsc(k)+'</b></td><td class="sc13-sm">'+hvEsc(v===true?'켜짐':v===false?'꺼짐':(v===''||v==null)?'-':v)+'</td></tr>'}).join(''):'<tr><td colspan="2">상태 파일을 읽지 못했습니다.</td></tr>')+'</tbody></table></div>'
 +'<div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>구동 요건</th><th>내용</th></tr></thead><tbody>'+Wt.requirements.map(function(r){return '<tr><td><b>'+hvEsc(r[0])+'</b></td><td class="sc13-sm">'+hvEsc(r[1])+'</td></tr>'}).join('')+'</tbody></table></div>'
 +'<h3>칭찬 문맥 검토 대기 (세지 않은 기록)</h3><div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>시각</th><th>출처</th><th>찾은 말</th><th>메시지 앞부분</th><th>판정</th><th>검토</th></tr></thead><tbody>'+(PRV.length?PRV.slice().reverse().map(function(r){return '<tr>'+r.map(function(c,i){return '<td class="'+(i===3||i===4?'sc13-sm':'sc13-nw')+'">'+hvEsc(c)+'</td>'}).join('')+'</tr>'}).join(''):'<tr><td colspan="6">검토 대기 없음</td></tr>')+'</tbody></table></div><p class="note">칭찬 문구를 정의·인용하는 지시처럼 문맥상 칭찬이 아닌 것으로 보여 세지 않은 기록입니다. 대표님이 칭찬이라고 판단하시면 원장에 추가합니다.</p>'}
 /* 칭찬 판별 기준 */
 var D=C.dictionary||{include:[],exclude:[],rule:''};
 g+='<div class="tw"><table class="sc13-t sc13-st"><thead><tr><th>칭찬으로 세는 말</th><th>칭찬으로 세지 않는 말</th></tr></thead><tbody><tr><td class="sc13-sm">'+D.include.map(hvEsc).join('<br>')+'</td><td class="sc13-sm">'+D.exclude.map(hvEsc).join('<br>')+'</td></tr></tbody></table></div>'
 +'<p class="note"><b>판별 규칙</b>: '+hvEsc(D.rule)+'<br><b>역할</b>: '+hvEsc(C.role)+'<br><b>전수 조사 범위</b>: '+C.scan.sources.map(hvEsc).join(' · ')+'<br><b>결과</b>: '+hvEsc(C.scan.result)+'<br>'+hvEsc(C.approval_note)+'<br>이력 445번(칭찬)은 20:06 대표님 지시로 이력에서 빼고 원장으로 옮겼습니다(이력 번호 445는 비어 있음). 칭찬 후 60분이 지나기 전의 성과 판정은 보류하며, 이 비교는 인과를 뜻하지 않습니다.</p>';
 return g}
