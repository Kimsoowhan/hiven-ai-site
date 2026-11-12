function hvgo(id){cur=id;render(id);window.scrollTo({top:0})}
function hvgoHist(){hvgo('SC-16');var n=0;var t=setInterval(function(){n++;var e=[].slice.call(document.querySelectorAll('#main p,#main h3')).filter(function(x){return /^막대 위/.test(x.textContent.trim())&&x.closest('#sc13')})[0];if(e){clearInterval(t);e.scrollIntoView({block:'start'})}else if(n>40){clearInterval(t)}},100)}
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
 S.sort(function(a,b){var ka=a[0]==='SC-00'?'0':a[0]==='SC-01'?'1':a[0],kb=b[0]==='SC-00'?'0':b[0]==='SC-01'?'1':b[0];return ka<kb?-1:ka>kb?1:0});/* 16:43 대표님 지시: 고객 지원(SC-01)이 최상위, 맨 위 *//* 11-13 01:51 대표님 지시(이력 1052): SC-00 대표님 결재가 맨 최상위, SC-01 고객 지원 대응·응대는 그 바로 아래 *//* 14:42 대표님 지시: 메뉴는 번호순, SC-03 이상징후 및 보안체계가 종합 현황 바로 아래 */
 $('nav').innerHTML=S.map(function(s){return '<button type="button" class="'+(s[0]===id?'on':'')+'" onclick="hvgo(\''+s[0]+'\')"><b>'+s[0]+'</b><span class="nl">'+({'SC-03':'이상징후 및 보안<br>체계 시스템','SC-04':'침입 예측·예방·대응·<br>조치 시스템'}[s[0]]||s[1])+'</span></button>'}).join('');
 $('main').innerHTML=(V[id]||V['SC-02'])();
 $('upd').textContent=kst();
 $('ftxt').textContent='데이터 신선도 · 시험판';
 if(id==='SC-17'){$('cin').addEventListener('input',function(){$('cres').textContent=parse(this.value)});}
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

show(sget());
setInterval(function(){if(!$('app').classList.contains('hide'))$('upd').textContent=kst()},30000);
