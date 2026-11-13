/* 대표 일정 화면(hiven.ai.kr/schedule.html) — 이력 1240~1242·1249, Opus 5.5.
   열쇠: 통합관제(IC)와 같은 열쇠(11-13 17:08 대표님 확정, 일정 전용 열쇠 없음). 통합관제에서 열쇠를 넣은 같은 창이면 그 세션 값(hv_sk2)으로 열고 다시 묻지 않는다.
   열쇠가 맞는지는 암호 묶음(sched.enc.json, ECIES)이 풀리는지로 본다(AES-GCM 인증 실패 = 틀린 열쇠). 묶음이 없거나 다른 잠그는 값으로
   만든 묶음이면 통합관제 열쇠 확인 값(KEYH)과 맞을 때만 그 열쇠의 「잠그는 값」을 보인다(이력 1249). 맞지 않으면 틀린 열쇠로 센다.
   틀린 열쇠는 통합관제(sec.js)와 같은 저장 칸(localStorage hvsec)에 세고 같은 단계로 입력을 멈춘다. 서버로는 보내지 않는다(이력 1243 호출 한도).
   요청: 페이지를 열 때 묶음 1건만 읽고(없어도 다시 읽지 않음), 탭·달·팝업은 추가 요청 없이 그린다. 주기 갱신 없음.
   이 파일과 schedule.html 에는 일정 글자가 없다. 일정은 열쇠로 묶음을 푼 뒤에만 화면에 그려진다. */
(function(){
var H=HVSCH,E=H.esc,$=function(i){return document.getElementById(i)};
var D=null,T=H.today(),TAB='personal',CM=null;

/* ── 열쇠 실패 기록·입력 정지(sec.js 와 같은 단계: 2회 15초 · 3회 30초 · 4~5회 5분 · 6회부터 30분씩) ── */
var G=['관찰','주의','경보','경고','위기'];
function lk(n){return n>=6?1800*Math.min(8,n-5):n>=4?300:n>=3?30:n>=2?15:n>=1?5:0}
function gr(n){return n>=6?4:n>=4?3:n>=3?2:n>=2?1:0}
function ld(){try{return JSON.parse(localStorage.getItem('hvsec')||'{"n":0,"t":0,"u":0,"L":[]}')}catch(e){return {n:0,t:0,u:0,L:[]}}}
function sv(s){try{localStorage.setItem('hvsec',JSON.stringify(s))}catch(e){}}
/* 이력 1243: 호출 한도 보호 — 서버(ic.hiven.ai.kr/__sec)로 보내지 않고 이 단말 기록(hvsec)에만 남긴다 */
function log(g,why,n,kind,st){var s=ld(),e={t:new Date().toISOString(),g:G[g],r:0,n:n,why:why,host:location.host,path:location.pathname,ua:(navigator.userAgent||'').slice(0,90),kind:kind||'열쇠 입력',st:st||''};s.L=(s.L||[]).concat([e]).slice(-200);sv(s)}
function left(){var r=Math.ceil((ld().u-Date.now())/1000);return r>0?r:0}
function fail(){var s=ld();if(Date.now()-s.t>86400000)s.n=0;s.n+=1;s.t=Date.now();s.u=Date.now()+lk(s.n)*1000;sv(s);var g=gr(s.n);log(g,'대표 일정 열쇠 불일치',s.n,'열쇠 입력','거부');return g}
/* 입력 정지 초 세기: 정지 중일 때만 1초 뒤 다시 보는 이 화면 안 시계(네트워크 요청 없음, 이력 1243) */
var gT=null;function guard(){clearTimeout(gT);var i=$('k'),e=$('err'),r=left();if(!i)return;if(r>0){i.disabled=true;e.textContent='보호 단계 · 입력 정지 '+r+'초 남음';gT=setTimeout(guard,1000)}else if(i.disabled){i.disabled=false;e.textContent='열쇠를 다시 입력하십시오.'}}

function show(on){$('intro').classList.toggle('hide',on);$('sch').classList.toggle('hide',!on);$('lockv').innerHTML='';if(!on){$('k').value='';$('view').innerHTML='';$('tabs').innerHTML='';D=null}}
function enter(d){D=d;show(true);$('gen').textContent=d['만든때']||'-';$('today').textContent=T;readHash();draw()}

/* ── 잠그는 값 안내(묶음 없음 = none · 다른 잠그는 값으로 만든 묶음 = other) ── */
function lockv(h,why){var pv=H.pubOf(h);$('err').textContent='';
 $('lockv').innerHTML='<div class="lv"><b class="lv-t">'+(why==='other'?'실린 일정 자료가 이 열쇠의 잠그는 값으로 만들어지지 않았습니다.':'일정 자료가 아직 실리지 않았습니다.')+'</b><div class="lv-k">이 열쇠의 잠그는 값</div><div class="lv-r"><code class="lv-v">'+E(pv||'계산하지 못했습니다')+'</code><button type="button" class="lv-c" data-copy>복사</button></div><div class="lv-n">이 값을 Fable에게 한 번 붙여 주십시오. 공개해도 되는 값이며 이 값으로 열쇠를 알 수는 없습니다.</div><div class="lv-m" aria-live="polite"></div></div>'}
document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('[data-copy]');if(!b)return;var w=b.closest('.lv'),c=w.querySelector('.lv-v'),m=w.querySelector('.lv-m');
 function sel(){var r=document.createRange();r.selectNodeContents(c);var s=window.getSelection();s.removeAllRanges();s.addRange(r);m.textContent='값을 골라 두었습니다. 길게 누르거나 Ctrl+C로 복사하십시오.'}
 if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(c.textContent).then(function(){m.textContent='복사했습니다.'},sel);else sel()});

$('f').addEventListener('submit',function(e){e.preventDefault();if(left()){guard();return}
 var v=$('k').value;$('lockv').innerHTML='';$('err').textContent='여는 중…';
 H.derive(v).then(function(h){return H.open(h).then(function(d){return {h:h,d:d}})}).then(function(x){
  if(!x.d)return H.check(v).then(function(ok){
   if(!ok||!x.h){var g=fail();guard();$('err').textContent='열쇠가 맞지 않습니다 · 경보 '+G[g]+(left()?' · '+left()+'초 입력 정지':'');$('k').select();return}
   var s=ld();log(0,'대표 일정 열쇠 맞음 · 묶음 '+(x.d===null?'없음':'불일치')+' · 잠그는 값 보임',0,'열쇠 입력','통과');if(s.n){var s2=ld();s2.n=0;s2.u=0;sv(s2)}
   H.setK(x.h);lockv(x.h,x.d===null?'none':'other')});
  var s=ld();log(0,s.n?'대표 일정 열쇠 통과(오류 '+s.n+'회 뒤)':'대표 일정 열쇠 통과',0,'열쇠 입력','통과');if(s.n){var s2=ld();s2.n=0;s2.u=0;sv(s2)}
  try{sessionStorage.setItem('hvsec_ok',String(Date.now()))}catch(e){}
  H.setK(x.h);$('err').textContent='';enter(x.d)})});
$('so').addEventListener('click',function(){H.setK('');show(false)});
/* 통합관제에서 열쇠를 넣은 같은 창이면 그 세션 값으로 열고 다시 묻지 않는다. 세션 값은 열쇠가 맞을 때만 저장되므로
   풀리지 않으면 묶음이 없거나 다른 잠그는 값으로 만든 것이다 → 잠그는 값을 보인다 */
(function(){var h=H.getK();if(!h){guard();return}H.open(h).then(function(d){if(d)enter(d);else{lockv(h,d===null?'none':'other');guard()}})})();

/* ── 팝업(페이지 안, 닫기 단추·바깥 누름·Esc) ── */
var lastFocus=null;
function pop(t,html){ddClose();lastFocus=document.activeElement;$('pop-t').textContent=t;$('pop-b').innerHTML=html;$('pop').classList.remove('hide');$('pop-x').focus()}
function unpop(){if($('pop').classList.contains('hide'))return;$('pop').classList.add('hide');$('pop-b').innerHTML='';if(lastFocus&&lastFocus.focus)lastFocus.focus()}
$('pop-x').addEventListener('click',unpop);
$('pop').addEventListener('click',function(e){if(e.target===this)unpop()});
document.addEventListener('keydown',function(e){if(e.key==='Escape')unpop()});

/* ── 탭(주소 뒤 #personal·#milestone·#wbs·#work·#month·#year) ── */
var TABS=[['personal','대표'],['milestone','Milestone'],['wbs','WBS'],['work','Work'],['month','Month'],['year','Year']];
function readHash(){var h=location.hash.replace('#','');if(TABS.some(function(t){return t[0]===h}))TAB=h}
window.addEventListener('hashchange',function(){readHash();if(D)draw()});
function go(t){if(location.hash!=='#'+t)history.replaceState(null,'','#'+t);TAB=t;draw();window.scrollTo({top:0})}
function draw(){if(!D)return;ddClose();$('tabs').innerHTML=TABS.map(function(t){return '<button type="button" data-t="'+t[0]+'" class="'+(t[0]===TAB?'on':'')+'">'+t[1]+'</button>'}).join('');
 [].forEach.call($('tabs').querySelectorAll('button'),function(b){b.onclick=function(){go(b.getAttribute('data-t'))}});
 $('view').innerHTML=(V[TAB]||V.personal)()+'<div class="ft" style="margin-top:14px">자료 만든 때 '+E(D['만든때']||'-')+' (서울). 원천 표가 바뀌면 묶음을 다시 만들어 올립니다. 이 화면은 열 때 한 번만 읽고 스스로 다시 읽지 않습니다.</div>';if(AFTER[TAB])AFTER[TAB]()}
var V={},AFTER={};
/* ── ① 개인 일정: 얼럿 띠 · 월 달력 · 목록 ── */
var WD=['일','월','화','수','목','금','토'];
function ceo(){return (D.ceo||[]).slice().sort(function(a,b){return a[1]<b[1]?-1:a[1]>b[1]?1:0})}
function evColor(r){if(H.cancelled(r)||H.finished(r))return '#9aa5b5';var lv=H.level(H.dday(r[1],T));return lv?H.LC[lv]:'#3f51b5'}
function alertBand(){var A=H.alerts(D.ceo,T),n=H.next(D.ceo,T),h='';
 if(!A.length)h='<div class="al none"><b class="t">7일 안에 든 일정 없음</b>'+(n?'<span>가장 가까운 일정 · '+E(n.r[1])+' '+E(n.r[2])+' · '+H.dtxt(n.d)+'</span>':'')+'</div>';
 else h=A.map(function(x){var r=x.r;return '<div class="al '+x.lv+'"><b class="d">'+H.dtxt(x.d)+'</b><span class="st-b">'+H.LV[x.lv]+'</span><span class="t">'+E(r[2])+'</span><span>'+E(r[1])+' · '+E(r[3])+' · '+E(r[4])+'</span><span class="w">해야 할 일 · '+E(r[5])+'</span></div>'}).join('');
 return '<div class="box"><div class="k">기한 알림 · 오늘 '+T+' 기준(서울) · 7일·3일·1일 전과 기한 지남</div><div class="alb">'+h+'</div><div class="lg"><span><i style="background:'+H.LC.past+'"></i>기한 지남</span><span><i style="background:'+H.LC.d1+'"></i>1일 안(D-DAY·D-1)</span><span><i style="background:'+H.LC.d3+'"></i>3일 안(D-2·D-3)</span><span><i style="background:'+H.LC.d7+'"></i>7일 안(D-4~D-7)</span><span><i style="background:#3f51b5"></i>그 밖</span><span><i style="background:#9aa5b5"></i>취소·끝남(알림에서 뺌)</span></div></div>'}
function calendar(){if(!CM)CM=T.slice(0,7);var y=+CM.slice(0,4),m=+CM.slice(5,7),first=new Date(Date.UTC(y,m-1,1)),sw=first.getUTCDay(),start=Date.UTC(y,m-1,1)/86400000-sw;
 var by={};ceo().forEach(function(r){(by[r[1]]=by[r[1]]||[]).push(r)});
 var h='<div class="calh"><span class="m">'+y+'년 '+m+'월</span><button type="button" data-cm="-1">◀ 이전 달</button><button type="button" data-cm="0">오늘</button><button type="button" data-cm="1">다음 달 ▶</button></div><div class="cal">'+WD.map(function(w,i){return '<div class="wd'+(i===0?' su':i===6?' sa':'')+'">'+w+'</div>'}).join('');
 for(var i=0;i<42;i++){var ds=new Date((start+i)*86400000).toISOString().slice(0,10),inm=+ds.slice(5,7)===m,ev=by[ds]||[],dw=i%7;
  if(i===35&&!inm)break;
    ev=dayOrder(ev);var n=ev.length;
  h+='<div class="c'+(inm?'':' out')+(ds===T?' td':'')+(n?' has':'')+(dw===0?' su':dw===6?' sa':'')+'"'+(n?' role="button" tabindex="0" data-day="'+ds+'" aria-label="'+ds+' 일정 '+n+'건'+(n>1?' · 초점을 두면 그날 일정이 펼쳐짐':'')+'"'+(n>1?' aria-haspopup="true" aria-expanded="false"':''):'')+'><span class="dn"><span>'+(+ds.slice(8))+'</span>'+(n>1?'<b class="more" aria-hidden="true">+'+(n-1)+'</b>':'')+'</span>'+(n?'<span class="ev'+(H.cancelled(ev[0])?' cx':'')+'"><i style="background:'+evColor(ev[0])+'"></i><span>'+E(ev[0][2])+'</span></span>':'')+'</div>'}
 return '<div class="box">'+h+'</div><div class="ft">날짜 칸을 누르면 그날 일정 내용이 뜹니다. 칸에는 첫 일정과 남은 건수(+2 꼴)만 보이며, 두 건 이상인 날짜에 마우스를 올리거나 초점을 두면 그날 일정이 칸 아래로 펼쳐집니다(터치 화면은 한 번 누르면 펼쳐지고 한 번 더 누르면 내용이 뜹니다). 취소된 일정은 흐리게·줄을 그어 보입니다.</div></div>'}
function dayPop(ds){var ev=dayEv(ds);if(!ev.length)return;
 pop(ds+' ('+WD[new Date(H.dnum(ds)*86400000).getUTCDay()]+') 일정 '+ev.length+'건',ev.map(function(r){var d=H.dday(r[1],T);return '<div class="it'+(H.cancelled(r)?' cx':'')+'"><div class="tt"><b>'+E(r[2])+'</b></div><dl><dt>번호</dt><dd>'+E(r[0])+'</dd><dt>구분</dt><dd>'+E(r[3])+'</dd><dt>상태</dt><dd>'+E(r[4])+'</dd><dt>해야 할 일</dt><dd>'+E(r[5])+'</dd><dt>근거</dt><dd>'+E(r[6])+'</dd><dt>남은 날</dt><dd>'+(H.cancelled(r)?'취소(알림 없음)':H.dtxt(d))+'</dd></dl></div>'}).join(''))}
/* ── 펼침 창(이력 1269, 11-13 17:41 대표님 말씀): 한 날짜에 일정이 2건 이상이면 마우스를 올렸을 때 그 칸 바로 아래로 그날 일정 전부를 한 줄씩.
   화면 아래·오른쪽 끝에서 모자라면 위·왼쪽으로 뒤집는다. 칸과 창이 1px 겹쳐 붙고 닫기는 0.16초 늦춰 칸→창으로 옮길 때 닫히지 않는다.
   터치: 한 번 누르면 펼침, 펼친 칸을 한 번 더 누르거나 창의 줄을 누르면 기존 팝업, 바깥을 누르면 닫힘. 키보드: 초점에 펼침, Esc 닫힘, Enter 기존 팝업.
   네트워크 요청 없음(묶음에서 이미 푼 자료만 씀). ── */
function dayOrder(L){return L.filter(function(r){return !H.cancelled(r)}).concat(L.filter(H.cancelled))}
function dayEv(ds){return dayOrder(ceo().filter(function(r){return r[1]===ds}))}
var DD=null,DDa=null,DDt=null;
function ddEl(){if(DD)return DD;DD=document.createElement('div');DD.id='dd';DD.className='hide';DD.setAttribute('role','group');document.body.appendChild(DD);
 DD.addEventListener('pointerenter',function(e){if(e.pointerType==='mouse')clearTimeout(DDt)});
 DD.addEventListener('pointerleave',function(e){if(e.pointerType==='mouse')ddLater()});
 DD.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('[data-pop]');if(b){var ds=b.getAttribute('data-pop');ddClose();dayPop(ds)}});
 return DD}
function ddHTML(ds){var ev=dayEv(ds);
 return '<div class="dd-h"><b>'+E(ds)+' ('+WD[new Date(H.dnum(ds)*86400000).getUTCDay()]+')</b><span>일정 '+ev.length+'건</span></div><ul>'+ev.map(function(r){var cx=H.cancelled(r);
  return '<li><button type="button" tabindex="-1" class="dd-i'+(cx?' cx':'')+'" data-pop="'+E(ds)+'" title="'+E(r[2])+'"><i style="background:'+evColor(r)+'"></i><span class="dd-n">'+E(r[2])+'</span><b class="dd-d">'+(cx?'취소':H.dtxt(H.dday(r[1],T)))+'</b><span class="dd-m">'+E(r[3])+' · '+E(r[4])+'</span></button></li>'}).join('')+'</ul><div class="dd-f">줄을 누르면 그날 일정 내용이 뜹니다</div>'}
function ddOpen(a,ds){clearTimeout(DDt);var p=ddEl();if(DDa&&DDa!==a){DDa.classList.remove('dd-on');DDa.setAttribute('aria-expanded','false')}
 DDa=a;a.classList.add('dd-on');a.setAttribute('aria-expanded','true');a.setAttribute('aria-controls','dd');
 p.innerHTML=ddHTML(ds);ddPlace()}
/* 자리 잡기: 칸 바로 아래, 모자라면 위로. 오른쪽 끝을 넘으면 칸 오른쪽 끝에 맞춰 왼쪽으로 */
function ddPlace(){var p=DD,a=DDa;if(!p||!a)return;p.className='';p.style.maxHeight='';p.style.top='0px';p.style.left='0px';
 var r=a.getBoundingClientRect(),vw=document.documentElement.clientWidth,vh=window.innerHeight,M=8,
  w=Math.min(Math.max(r.width,vw<=520?240:280),340,vw-M*2);p.style.width=w+'px';
 var h=p.offsetHeight,below=vh-r.bottom-M,above=r.top-M,up=h>below&&above>below,av=Math.max(120,up?above:below),hh=Math.min(h,av);
 if(h>av)p.style.maxHeight=av+'px';
 var L=r.left;if(L+w>vw-M)L=r.right-w;if(L<M)L=M;if(L+w>vw-M)L=vw-M-w;
 p.style.top=Math.round(up?r.top+1-hh:r.bottom-1)+'px';p.style.left=Math.round(L)+'px';
 p.className=(up?'up':'')+(L<r.left-.5?' lf':'')}
function ddClose(){clearTimeout(DDt);if(DD&&!DD.classList.contains('hide')){DD.className='hide';DD.innerHTML=''}if(DDa){DDa.classList.remove('dd-on');DDa.setAttribute('aria-expanded','false');DDa=null}}
function ddLater(){clearTimeout(DDt);DDt=setTimeout(ddClose,160)}
/* 바깥 누름(터치 포함)에 닫는다 */
document.addEventListener('pointerdown',function(e){if(DDa&&!(DD&&DD.contains(e.target))&&!DDa.contains(e.target))ddClose()},true);
/* 페이지·띠 그림이 굴러가면(키보드 초점 이동의 부드러운 굴림 포함) 칸을 따라 다시 자리 잡고, 칸이 화면 밖으로 나가면 닫는다. 창 안 굴림은 그대로 */
var ddRaf=0;function ddFollow(){ddRaf=0;if(!DDa)return;var r=DDa.getBoundingClientRect();if(!DDa.isConnected||r.bottom<0||r.top>window.innerHeight||r.right<0||r.left>document.documentElement.clientWidth)ddClose();else ddPlace()}
window.addEventListener('scroll',function(e){if(DDa&&!(DD&&e.target&&e.target.nodeType===1&&DD.contains(e.target))&&!ddRaf)ddRaf=requestAnimationFrame(ddFollow)},true);
window.addEventListener('resize',function(){if(DDa&&!ddRaf)ddRaf=requestAnimationFrame(ddFollow)});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&DDa){var a=DDa;ddClose();if(a.focus)a.focus()}},true);
/* 날짜 칸·개인 일정 점 하나에 붙이기. 일정 1건인 곳은 예전 그대로(누름·Enter → 팝업) */
function bindDay(c){var ds=c.getAttribute('data-day'),n=dayEv(ds).length,pt='';
 c.onclick=function(){if(n>1&&pt&&pt!=='mouse'&&DDa!==c){ddOpen(c,ds);return}ddClose();dayPop(ds)};
 c.onkeydown=function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();ddClose();dayPop(ds)}};
 c.addEventListener('pointerdown',function(e){pt=e.pointerType||''});
 if(n<2)return;
 c.addEventListener('pointerenter',function(e){if(e.pointerType==='mouse')ddOpen(c,ds)});
 c.addEventListener('pointerleave',function(e){if(e.pointerType==='mouse')ddLater()});
 c.addEventListener('focus',function(){var kv=true;try{kv=c.matches(':focus-visible')}catch(x){}if(kv&&$('pop').classList.contains('hide'))ddOpen(c,ds)});
 c.addEventListener('blur',function(e){if(DDa===c&&!(e.relatedTarget&&DD&&DD.contains(e.relatedTarget))&&!c.matches(':hover'))ddLater()})}
function ceoTable(){return '<div class="box"><div class="k">일정 목록 · 날짜순</div><div class="scr"><table class="st"><tr><th>번호</th><th>날짜</th><th>남은 날</th><th>일정</th><th>구분</th><th>상태</th><th>해야 할 일</th><th>근거</th></tr>'+ceo().map(function(r){var d=H.dday(r[1],T);return '<tr class="'+(H.cancelled(r)?'cx':'')+'"><td class="n">'+E(r[0])+'</td><td class="n"><button type="button" class="pre" data-day="'+E(r[1])+'">'+E(r[1])+'</button></td><td class="n">'+(H.cancelled(r)?'—':H.dtxt(d))+'</td><td>'+E(r[2])+'</td><td class="n">'+E(r[3])+'</td><td class="n">'+E(r[4])+'</td><td>'+E(r[5])+'</td><td>'+E(r[6])+'</td></tr>'}).join('')+'</table></div></div>'}
V.personal=function(){return alertBand()+'<div>'+calendar()+ceoTable()};
AFTER.personal=function(){var v=$('view');
 [].forEach.call(v.querySelectorAll('[data-cm]'),function(b){b.onclick=function(){var k=+b.getAttribute('data-cm');if(!k)CM=T.slice(0,7);else{var y=+CM.slice(0,4),m=+CM.slice(5,7)-1+k;CM=new Date(Date.UTC(y,m,1)).toISOString().slice(0,7)}draw()}});
 [].forEach.call(v.querySelectorAll('.cal [data-day]'),bindDay);
 [].forEach.call(v.querySelectorAll('.st [data-day]'),function(c){c.onclick=function(){dayPop(c.getAttribute('data-day'))}})};
/* ── 띠 그림 공통: 가로축 2026-11-01 ~ 2027-07-31, 하루 4px ── */
var G0=H.dnum('2026-11-01'),G1=H.dnum('2027-08-01'),PX=4,LW=132,GW=(G1-G0)*PX;
var MONS=[];(function(){for(var y=2026,m=11;y<2027||m<=7;){MONS.push(y+'-'+('0'+m).slice(-2));m++;if(m>12){m=1;y++}}})();
function mEnd(y,m){return Date.UTC(y,m,1)/86400000-1}
/* 날짜 글을 날 수로: YYYY-MM-DD 그대로 · YYYY-MM 은 그달 첫날(끝이면 그달 마지막 날) · YYYY 는 그해 첫날·마지막 날. 그 밖(미정 등)은 없음 */
function pd(s,end){s=String(s||'').trim();var m;
 if((m=/^(\d{4})-(\d\d)-(\d\d)/.exec(s)))return H.dnum(m[0]);
 if((m=/^(\d{4})-(\d\d)$/.exec(s)))return end?mEnd(+m[1],+m[2]):Date.UTC(+m[1],+m[2]-1,1)/86400000;
 if((m=/^(\d{4})$/.exec(s)))return end?mEnd(+m[1],12):Date.UTC(+m[1],0,1)/86400000;
 return null}
function xs(d){return (Math.max(G0,Math.min(G1,d))-G0)*PX}
function lanes(items){var L=[];items.forEach(function(it){var x0=xs(it.a),x1=Math.max(xs(it.b+1),x0+6),w=Math.max(x1,x0+(it.lab||'').length*11.5+8),k=0;while(L[k]!=null&&L[k]>x0-4)k++;L[k]=w;it.k=k;it.x0=x0;it.x1=x1});return Math.max(1,L.length)}
function head(){return '<div class="g-row hd"><div class="lb">갈래</div><div class="ln" style="width:'+GW+'px">'+MONS.map(function(mo){var a=pd(mo);return '<div style="left:'+xs(a)+'px">'+mo.slice(2).replace('-','.')+'</div>'}).join('')+'</div></div>'}
function grid(){return MONS.map(function(mo){return '<div class="g-grid" style="left:'+xs(pd(mo))+'px"></div>'}).join('')}
function nowLine(top){var t=H.dnum(T);if(t<G0||t>=G1)return '';return '<div class="now" style="left:'+(LW+xs(t)+PX/2)+'px">'+(top?'<span>오늘 '+T.slice(5)+'</span>':'')+'</div>'}
function row(label,items,title){var n=lanes(items),h=n*20+10;
 return '<div class="g-row"><div class="lb"'+(title?' title="'+E(title)+'"':'')+'>'+label+'</div><div class="ln" style="width:'+GW+'px;height:'+h+'px">'+grid()+items.map(function(it){var top=5+it.k*20;
  if(it.pt)return '<span class="pt'+(it.cls?' '+it.cls:'')+'" style="left:'+xs(it.a)+'px;top:'+(top+2)+'px;background:'+(it.col||'')+'" '+(it.tip?'title="'+E(it.tip)+'"':'')+(it.day?' data-day="'+it.day+'"':'')+(it.n>1?' role="button" tabindex="0" aria-haspopup="true" aria-expanded="false" aria-label="'+it.day+' 개인 일정 '+it.n+'건"':'')+'></span>'+(it.lab?'<span class="tx" style="left:'+(xs(it.a)+9)+'px;top:'+top+'px">'+E(it.lab)+'</span>':'');
  return '<div class="bar '+(it.cls||'')+'" style="left:'+it.x0+'px;width:'+(it.x1-it.x0)+'px;top:'+(top+1)+'px" title="'+E(it.tip)+'"></div><span class="tx" style="left:'+(it.x0+4)+'px;top:'+top+'px">'+E(it.lab)+'</span>'}).join('')+'</div></div>'}
function chart(rows,legend){return '<div class="scr"><div class="gt" style="width:'+(LW+GW)+'px">'+head()+rows.join('')+nowLine(true)+'</div></div>'+(legend?'<div class="lg">'+legend+'</div>':'')}
function stCls(s){return /끝남|완료/.test(s)?'done':/진행/.test(s)?'go':''}
/* 같은 날 일정이 여러 건이면 점 하나로 묶고(가장 급한 색) 건수를 붙인다 — 마우스 올림·초점·터치로 달력과 같은 펼침 창(이력 1269) */
function personalRow(){var by={},ord=[];(D.ceo||[]).filter(function(r){return !H.cancelled(r)&&H.dnum(r[1])!=null}).forEach(function(r){if(!by[r[1]]){by[r[1]]=[];ord.push(r[1])}by[r[1]].push(r)});
 var it=ord.map(function(ds){var L=by[ds],r=L.slice().sort(function(a,b){return urg(a)-urg(b)})[0],a=H.dnum(ds),n=L.length;
  return {a:a,b:a,pt:1,col:evColor(r),cls:n>1?'many':'',n:n,tip:n>1?'':ds+' · '+r[2]+' · '+(H.finished(r)?r[4]:H.dtxt(H.dday(ds,T))),day:ds,lab:n>1?n+'건':''}});
 return row('대표 개인 일정',it,'개인 일정 날짜(취소는 뺌). 점을 누르면 그날 내용, 여러 건인 점은 마우스를 올리면 펼쳐짐')}
function urg(r){if(H.cancelled(r)||H.finished(r))return 9;var lv=H.level(H.dday(r[1],T));return lv?{past:0,d1:1,d3:2,d7:3}[lv]:4}
function bindDots(){[].forEach.call($('view').querySelectorAll('.gt [data-day]'),bindDay)}

/* ── ② Milestone 탭: MM 줄(달 상자) + WBS(막대)를 갈래별 한 줄 ── */
function wbs(){return D.wbs||[]}
function wbsItem(r){var a=pd(r[3]),b=pd(r[4],true);return {r:r,a:a,b:b}}
V.milestone=function(){var order=[],by={};function add(g,it){if(!by[g]){by[g]=[];order.push(g)}by[g].push(it)}
 (D.ms||[]).filter(function(r){return r[0]==='MM'}).forEach(function(r){var a=pd(r[2]);if(a==null){add(r[3],{none:1,lab:r[1]+' '+r[4]+' · '+r[2]});return}add(r[3],{a:a,b:pd(r[2],true),cls:'mm',lab:r[4].length>16?r[4].slice(0,16)+'…':r[4],tip:r[1]+' · '+r[3]+' · '+r[4]+' · '+r[5]})});
 wbs().forEach(function(r){var w=wbsItem(r);if(w.a==null){add(r[1],{none:1,lab:r[0]+' '+r[2]+' · 시작 '+r[3]+' · 끝 '+r[4]});return}
  if(w.b==null){add(r[1],{a:w.a,b:w.a,pt:1,cls:'op',lab:r[0]+' ~미정',tip:r[0]+' · '+r[2]+' · '+r[3]+' ~ '+r[4]});return}
  add(r[1],{a:w.a,b:w.b,cls:stCls(r[6]),lab:r[0],tip:r[0]+' · '+r[2]+' · '+r[3]+' ~ '+r[4]+' · '+r[6]})});
 var none=[];var rows=[personalRow()].concat(order.map(function(g){var it=by[g].filter(function(x){if(x.none){none.push(g+' · '+x.lab);return false}return true});return row(E(g),it)}));
 return '<div class="box"><div class="k">하이븐 전체 일정 · 2026-11 ~ 2027-07 · 갈래별 한 줄 · 빨간 세로선 = 오늘</div>'+chart(rows,'<span><i style="background:#c5d3f0;border-radius:3px"></i>Month(MM) Milestone</span><span><i style="background:#3f51b5;border-radius:3px"></i>WBS 일(예정·계획)</span><span><i style="background:#2d9cdb;border-radius:3px"></i>WBS 진행 중</span><span><i style="background:#1f9d55;border-radius:3px"></i>WBS 끝남</span><span><i style="background:#fff;border:2px solid #3f51b5"></i>시작만 정해짐(끝 미정)</span><span>막대에 마우스를 올리면 내용이 보입니다</span>')+(none.length?'<div class="nod"><b>때가 정해지지 않아 그림에 없는 일</b><br>'+none.map(E).join('<br>')+'</div>':'')+'</div>'};
AFTER.milestone=bindDots;

/* ── ③ WBS: 갈래별 묶음 표 + 가로 막대(시작~끝) + 선행 ── */
function preds(s){return String(s||'').split(/[·,\s]+/).filter(function(x){return /^W-[A-Z]\d+$/.test(x)})}
V.wbs=function(){var order=[],by={};wbs().forEach(function(r){if(!by[r[1]]){by[r[1]]=[];order.push(r[1])}by[r[1]].push(r)});
 var rows=[];order.forEach(function(g){rows.push('<div class="g-row"><div class="lb" style="background:#f0f4fa">'+E(g)+'</div><div class="ln" style="width:'+GW+'px;background:#f7f9fc"></div></div>');
  by[g].forEach(function(r){var w=wbsItem(r),p=preds(r[5]),pl=p.length?' ← '+p.join(' · '):'',it;
   if(w.a==null)it={a:G0,b:G0,pt:1,col:'transparent',lab:'미정'+pl,tip:r[0]+' · 시작 '+r[3]+' · 끝 '+r[4]};
   else if(w.b==null)it={a:w.a,b:w.a,pt:1,cls:'op',lab:r[3]+' ~ 미정'+pl,tip:r[0]+' · '+r[2]};
   else it={a:w.a,b:w.b,cls:stCls(r[6]),lab:pl.replace(/^ /,''),tip:r[0]+' · '+r[2]+' · '+r[3]+' ~ '+r[4]+' · '+r[6]};
   if(it.cls!=='op'&&w.a!=null&&w.b!=null){it.lab='';}
   var ex=w.a!=null&&w.b!=null&&pl?'<span class="tx" style="left:'+(xs(w.b+1)+6)+'px;top:5px;color:#5d6b82">'+E(pl.replace(/^ /,''))+'</span>':'';
   var h=row('<a href="#wbs" data-go="'+E(r[0])+'" style="color:inherit;text-decoration:none">'+E(r[0])+'</a>',[it],r[2]);rows.push(ex?h.replace(/<\/div><\/div>$/,ex+'</div></div>'):h)})});
 var tb=order.map(function(g){return '<tr><th colspan="7" style="background:#e3ecfa">'+E(g)+'</th></tr>'+by[g].map(function(r){var p=preds(r[5]);return '<tr id="w-'+E(r[0])+'"><td class="n"><b>'+E(r[0])+'</b></td><td>'+E(r[2])+'</td><td class="n">'+E(r[3])+'</td><td class="n">'+E(r[4])+'</td><td class="n">'+(p.length?p.map(function(x){return '<button type="button" class="pre" data-go="'+E(x)+'">← '+E(x)+'</button>'}).join(''):E(r[5]))+'</td><td class="n">'+E(r[6])+'</td><td>'+E(r[7])+'</td></tr>'}).join('')}).join('');
 return '<div class="box"><div class="k">HIVEN WBS · 시작~끝 막대 · 「← 번호」 = 먼저 끝나야 하는 일(선행) · 「미정」은 막대를 그리지 않음</div>'+chart(rows,'<span><i style="background:#3f51b5;border-radius:3px"></i>예정·계획</span><span><i style="background:#2d9cdb;border-radius:3px"></i>진행 중</span><span><i style="background:#1f9d55;border-radius:3px"></i>끝남</span><span><i style="background:#fff;border:2px solid #3f51b5"></i>시작만 정해짐(끝 미정)</span><span>달만 적힌 때는 그달 첫날~마지막 날로 그림</span>')+'</div><div class="box"><div class="k">WBS 표 · 갈래별 · 선행 번호를 누르면 그 줄로 감</div><div class="scr"><table class="st"><tr><th>번호</th><th>일</th><th>시작</th><th>끝</th><th>선행</th><th>상태</th><th>근거</th></tr>'+tb+'</table></div></div>'};
AFTER.wbs=function(){[].forEach.call($('view').querySelectorAll('[data-go]'),function(b){b.onclick=function(e){e.preventDefault();var t=$('w-'+b.getAttribute('data-go'));if(!t)return;t.scrollIntoView({block:'center',behavior:'smooth'});t.classList.add('hl');setTimeout(function(){t.classList.remove('hl')},1800)}})};
/* ── ④ Work · ⑤ Month · ⑥ Year 탭(탭 이름은 영어, 이력 1274. ms('워크')는 자료의 층 값이라 그대로) ── */
function msTable(rows,cap){return '<div class="box"><div class="k">'+cap+'</div><div class="scr"><table class="st"><tr><th>층</th><th>번호</th><th>때</th><th>갈래</th><th>일정·마일스톤</th><th>상태</th><th>근거</th></tr>'+(rows.length?rows.map(function(r){return '<tr><td class="n">'+E(r[0])+'</td><td class="n"><b>'+E(r[1])+'</b></td><td>'+E(r[2])+'</td><td class="n">'+E(r[3])+'</td><td>'+E(r[4])+'</td><td>'+E(r[5])+'</td><td>'+E(r[6])+'</td></tr>'}).join(''):'<tr><td colspan="7">줄 없음</td></tr>')+'</table></div></div>'}
function ms(layer){return (D.ms||[]).filter(function(r){return r[0]===layer})}
V.work=function(){var sm=D.sm||[],order=[],by={};sm.forEach(function(r){if(!by[r[0]]){by[r[0]]=[];order.push(r[0])}by[r[0]].push(r)});
 return msTable(ms('WW'),'WW(Work 10개 단위)')+msTable(ms('워크'),'Work')+'<div class="box"><div class="k">일정 대장 · 구분별</div><div class="scr"><table class="st"><tr><th>번호</th><th>때</th><th>일</th><th>끝난 기준</th><th>담당</th><th>상태</th><th>근거</th></tr>'+order.map(function(g){return '<tr><th colspan="7" style="background:#e3ecfa">'+E(g)+'</th></tr>'+by[g].map(function(r){return '<tr><td class="n"><b>'+E(r[1])+'</b></td><td>'+E(r[2])+'</td><td>'+E(r[3])+'</td><td>'+E(r[4])+'</td><td>'+E(r[5])+'</td><td>'+E(r[6])+'</td><td>'+E(r[7])+'</td></tr>'}).join('')}).join('')+'</table></div></div>'};
V.month=function(){var R=ms('MM'),order=[],by={};R.forEach(function(r){if(!by[r[2]]){by[r[2]]=[];order.push(r[2])}by[r[2]].push(r)});
 return order.map(function(m){var a=pd(m),cur=a!=null&&H.dnum(T)>=a&&H.dnum(T)<=pd(m,true);return '<div class="box"'+(cur?' style="border:2px solid var(--sky)"':'')+'><div class="k">'+E(m)+(cur?' · 이번 달':'')+' · '+by[m].length+'줄</div><div class="scr"><table class="st"><tr><th>번호</th><th>갈래</th><th>마일스톤</th><th>상태</th><th>근거</th></tr>'+by[m].map(function(r){return '<tr><td class="n">'+E(r[1])+'</td><td class="n"><b>'+E(r[3])+'</b></td><td>'+E(r[4])+'</td><td class="n">'+E(r[5])+'</td><td>'+E(r[6])+'</td></tr>'}).join('')+'</table></div></div>'}).join('')||'<div class="box">줄 없음</div>'};
V.year=function(){return msTable(ms('Y'),'Year(Y) · 해 단위')};
window.HVSCHV={V:V,AFTER:AFTER,pop:pop,draw:draw,go:go,data:function(){return D},today:function(){return T}};
})();
