/* 통합관제 첫 화면 「대표 일정」 얼럿 한 줄(이력 1240~1243, Opus 5.5) — 기존 화면은 그대로 두고 SC-00 안내 글 바로 아래(결재함 위)에 한 줄만 더한다.
   ① 열쇠가 맞으면(통합관제 입장) 같은 열쇠로 일정 암호 열쇠를 뽑아 이 창의 sessionStorage hv_sk 에 둔다(「나오기」에 지움).
   ② 일정 묶음(sched.enc.json)은 이 페이지를 연 뒤 SC-00 을 처음 그릴 때 한 번만 읽는다. 주기 갱신·서버 호출 없음(호출 한도 보호).
   ③ 줄을 누르면 schedule.html 로 간다. */
(function(){
 if(typeof HVSCH==='undefined')return;
 var k0=window.keyOk;
 if(typeof k0==='function')window.keyOk=function(v){var p=k0(v);Promise.resolve(p).then(function(ok){if(ok)return HVSCH.derive(v).then(function(h){if(h){HVSCH.setK(h);RES=null}})}).catch(function(){});return p};
 var so=document.getElementById('so');if(so)so.addEventListener('click',function(){HVSCH.setK('');RES=null});
 var RES=null;/* 한 번 푼 결과를 이 페이지 안에서 다시 씀 */
 function line(){var h=HVSCH.getK();if(!h)return Promise.resolve({t:'열쇠를 다시 넣으면 대표 일정 알림이 보입니다 · 일정 화면 열기',c:'#5d6b82',b:'#eef3fa'});
  if(RES)return Promise.resolve(RES);
  return HVSCH.open(h).then(function(d){if(d===null)return {t:'대표 일정 묶음이 아직 실리지 않음 · 일정 화면 열기',c:'#5d6b82',b:'#eef3fa'};if(!d)return {t:'대표 일정 열쇠가 맞지 않음 · 일정 화면에서 다시 열기',c:'#8e1c1c',b:'#fdecea'};
   var T=HVSCH.today(),A=HVSCH.alerts(d.ceo,T),n={past:0,d1:0,d3:0,d7:0};A.forEach(function(x){n[x.lv]++});var nx=HVSCH.next(d.ceo,T),top=A[0]||nx;
   var lv=A.length?A[0].lv:null;
   RES={t:'대표 일정 · 7일 안 '+A.length+'건(지남 '+n.past+' · 1일 '+n.d1+' · 3일 '+n.d3+' · 7일 '+n.d7+')'+(top?' · 가장 가까운 일정 '+top.r[1]+' '+top.r[2]+' '+HVSCH.dtxt(HVSCH.dday(top.r[1],T)):' · 다가오는 일정 없음'),c:lv?HVSCH.LC[lv]:'#14264d',b:lv?'#fff8e1':'#eef3fa'};return RES})}
 function paint(){var e=document.getElementById('hv-sched-line');if(!e)return;line().then(function(x){e.textContent=x.t;e.style.color=x.c;e.style.background=x.b;e.style.borderColor=x.c})}
 if(typeof V!=='undefined'&&V['SC-00']){var o=V['SC-00'];V['SC-00']=function(){setTimeout(paint,0);var L='<a id="hv-sched-line" href="/schedule.html#personal" style="display:block;margin:0 0 10px;padding:8px 12px;border:1px solid #dbe3ee;border-radius:10px;font-weight:700;font-size:14px;text-decoration:none;white-space:nowrap;overflow:hidden;text-overflow:ellipsis" title="대표 일정 화면 열기">대표 일정 · 읽는 중</a>',h=o(),i=h.indexOf('<div id="al-00">');return i>=0?h.slice(0,i)+L+h.slice(i):L+h}}
})();
