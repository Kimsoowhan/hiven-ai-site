function hvgo(id){cur=id;render(id);window.scrollTo({top:0})}
function hvgoHist(){hvgo('SC-13');var n=0;var t=setInterval(function(){n++;var e=[].slice.call(document.querySelectorAll('#main p,#main h3')).filter(function(x){return /^막대 위/.test(x.textContent.trim())&&x.closest('#sc13')})[0];if(e){clearInterval(t);e.scrollIntoView({block:'start'})}else if(n>40){clearInterval(t)}},100)}
function parse(t){
 t=String(t||'').trim();
 if(!t)return '입력하면 해석 결과가 여기에 표시됩니다.';
 var m=t.match(/저장\s*주기.*?(\d+)\s*분/);
 if(m){var a=t.match(/(\d+)\s*월\s*(\d+)\s*일.*?(\d+)\s*시/);
  return a?('해석: '+a[1]+'월 '+a[2]+'일 '+a[3]+'시부터 저장 주기 '+m[1]+'분 (예약 반영)'):('해석: 저장 주기를 '+m[1]+'분으로 즉시 변경');}
 var tg=/HiClo|히클로/i.test(t)?'HiClo.app':(/HIVEN\s*앱|하이븐\s*앱|HIVEN\.app/i.test(t)?'HIVEN.app':(/AICS/i.test(t)?'AICS':null));
 if(tg){
  if(/정지|멈|스톱|stop/i.test(t))return '해석: '+tg+' 정지';
  if(/시작|재개|켜|start|resume/i.test(t))return '해석: '+tg+' '+(tg==='AICS'?'재개':'시작');
 }
 return '해석하지 못했습니다. 체계 문서가 확정되면 이 문장도 처리 범위에 들어옵니다.';
}
function render(id){
 $('nav').innerHTML=S.map(function(s){return '<button type="button" class="'+(s[0]===id?'on':'')+'" onclick="hvgo(\''+s[0]+'\')"><b>'+s[0]+'</b>'+s[1]+'</button>'}).join('');
 $('main').innerHTML=(V[id]||V['SC-01'])();
 $('upd').textContent=kst();
 $('ftxt').textContent='데이터 신선도 · 시험판';
 if(id==='SC-04'){$('cin').addEventListener('input',function(){$('cres').textContent=parse(this.value)});}
}
function show(on){
 $('intro').classList.toggle('hide',on);
 $('app').classList.toggle('hide',!on);
 if(on){render(cur);}else{$('k').value='';$('err').textContent='';window.scrollTo({top:0});}
}
$('f').addEventListener('submit',function(e){
 e.preventDefault();
 if(keyOk($('k').value)){sset(true);show(true);}
 else{$('err').textContent='열쇠가 맞지 않습니다. 다시 입력하세요.';$('k').select();}
});
$('so').addEventListener('click',function(){sset(false);show(false);});

(function(){
 var btn=$('hk'),pn=$('hkp');
 function esc(t){return String(t==null?'':t).replace(/[&<>]/g,function(m){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[m]})}
 function row(k,v){return '<dt>'+esc(k)+'</dt><dd>'+esc(v)+'</dd>'}
 function load(u){return fetch(u+'?v='+Date.now(),{cache:'no-store'}).then(function(r){if(!r.ok)throw new Error(r.status);return r.json()}).catch(function(){return null})}
 function draw(){
  pn.innerHTML='<h4>훅 불러옴 상태</h4><div>확인 중…</div>';
  Promise.all([load('cowork/ctl/praise_hook_state.json'),load('cowork/ctl/praise_watch_status.json')]).then(function(r){
   var h=r[0],w=r[1],o='<h4>훅 불러옴 상태</h4><dl>';
   o+=row('훅 적재',h?(h['적재']?'불러옴':'불러오지 않음'):'상태 파일을 읽지 못함');
   if(h){o+=row('모듈',h['모듈']);o+=row('확인 창 답',h['확인 창 답']);o+=row('기록 시각',h['기록 시각']);}
   o+=row('감시 장치',w?(w['켜짐']?'켜짐':'꺼짐'):'상태 파일을 읽지 못함');
   if(w){o+=row('마지막 실행',w['마지막 실행']);o+=row('원장 총건수',w['원장 총건수']);o+=row('문맥 검토 대기',w['문맥 검토 대기']);}
   o+='</dl><div class="nt">이 버튼은 상태를 보여 줄 뿐 훅을 켜지 못합니다. 훅은 Claude 앱의 불러오기 확인 창에서 대표님이 「불러옴」을 고르실 때만 켜집니다. 켜려면 Claude에게 「불러오기 확인 창을 다시 띄워라」라고 지시하십시오. 그 동안에도 감시 장치(15초 점검)가 칭찬을 기록합니다.</div>';
   o+='<button type="button" id="hkc">닫기</button>';
   pn.innerHTML=o;$('hkc').addEventListener('click',close);
  });
 }
 function close(){pn.hidden=true;btn.setAttribute('aria-expanded','false')}
 btn.addEventListener('click',function(){if(pn.hidden){pn.hidden=false;btn.setAttribute('aria-expanded','true');draw();}else close();});
 document.addEventListener('keydown',function(e){if(e.key==='Escape')close()});
 $('so').addEventListener('click',close);
})();
show(sget());
setInterval(function(){if(!$('app').classList.contains('hide'))$('upd').textContent=kst()},30000);
