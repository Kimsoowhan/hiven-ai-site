function hvgo(id){cur=id;render(id);window.scrollTo({top:0})}
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
show(sget());
setInterval(function(){if(!$('app').classList.contains('hide'))$('upd').textContent=kst()},30000);
