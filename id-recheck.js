/* 신분 재확인 한 줄(이력 1255·1256, 정책 11절 신-4 · Opus 5.5) — SC-00 대표님 결재와 SC-17 말 명령에 한 줄씩 올린다.
   원천: cowork/ctl/id_recheck_hold.tsv(tools/id_recheck.py 가 씀). 대표님 말씀 글은 싣지 않고 이력 번호·갈래·상태만 싣는다.
   읽기: 페이지를 열 때 한 번, 그 뒤로는 지시 대장·이력(SC-17 이 이미 읽는 자료)이 바뀐 때에만 한 번 다시 읽는다.
   ic.hiven.ai.kr(Cloudflare)은 부르지 않는다. 1초 확인은 이 페이지 메모리만 보고 네트워크 요청을 만들지 않는다.
   줄을 누르면 근거 표(최신순, 최대 15줄)가 펼쳐진다(추가 요청 없음). */
(function(){
 if(typeof V==='undefined'||typeof hvFetch!=='function')return;
 var R=null,SIG=null,BUSY=false,OPEN={};
 function esc(s){return typeof hvEsc==='function'?hvEsc(s):String(s==null?'':s)}
 function tsv(t){return typeof hvTsv==='function'?hvTsv(t):String(t||'').split(/\r?\n/).filter(function(x){return x.trim()}).slice(1).map(function(x){return x.split('\t')})}
 function get(){if(BUSY)return;BUSY=true;hvFetch('cowork/ctl/id_recheck_hold.tsv','text').then(function(t){R=tsv(t).filter(function(r){return /^IDH-/.test(r[0])});paint()},function(){R=R||[];paint()}).then(function(){BUSY=false})}
 function sig(){var c=window.hvCmdLive;if(!c)return null;var L=c.L||[],H=c.H||[];return L.length+':'+(L[L.length-1]||[]).join('|').length+'/'+H.length}
 setInterval(function(){var s=sig();if(s===null)return;if(SIG===null){SIG=s;return}if(s!==SIG){SIG=s;get()}},1000);
 function sum(){var r=R||[],h=r.filter(function(x){return x[6]==='보류'}),v=r.filter(function(x){return /^무효/.test(x[6])}),p=r.filter(function(x){return /^통과/.test(x[6])});return {h:h,v:v,p:p}}
 function text(){if(R===null)return {t:'신분 재확인 · 읽는 중',c:'#5d6b82',b:'#eef3fa',d:'#dbe3ee'};var s=sum(),t='신분 재확인 · 보류 '+s.h.length+' · 무효 '+s.v.length+' · 통과 '+s.p.length;
  /* 한 줄은 400px 폭에서도 끊기지 않게 짧게 두고, 자세한 까닭은 누르면 펼쳐지는 표에 싣는다 */
  if(s.h.length){var o=s.h[s.h.length-1];return {t:t,c:'#8a3d00',b:'#fff3e0',d:'#ef6c00',ti:'가장 최근 보류 '+o[0]+(o[2]?' · 이력 '+o[2]:'')+' · '+o[3]+' · '+o[4]}}
  if(s.v.length)return {t:t,c:'#8e1c1c',b:'#fdecea',d:'#d64545'};return {t:t,c:'#14264d',b:'#eef3fa',d:'#dbe3ee'}}
 var PG={},N=15;
 function table(k){var all=(R||[]).slice().reverse();if(!all.length)return '<div style="font-size:13px;color:#5d6b82;padding:6px 2px">보류·무효 기록이 없습니다. 재확인 대상 지시가 들어오면 이력 번호와 까닭이 여기에 올라옵니다.</div>';
  var pn=Math.max(1,Math.ceil(all.length/N)),pg=Math.min(PG[k]||1,pn),r=all.slice((pg-1)*N,pg*N);
  var nav='<div style="display:flex;gap:6px;align-items:center;justify-content:center;margin-top:6px;font-size:13px;flex-wrap:wrap"><button type="button" onclick="hvIdhP(\''+k+'\','+(pg-1)+')"'+(pg<=1?' disabled':'')+' style="padding:3px 9px;border:1px solid #dbe3ee;border-radius:6px;background:#fff;font-family:inherit">◀ 이전</button>';
  for(var i=1;i<=pn;i++)nav+='<button type="button" onclick="hvIdhP(\''+k+'\','+i+')" style="padding:3px 8px;border:1px solid #dbe3ee;border-radius:6px;font-family:inherit;'+(i===pg?'background:#14264d;color:#fff;font-weight:700':'background:#fff')+'">'+i+'</button>';
  nav+='<button type="button" onclick="hvIdhP(\''+k+'\','+(pg+1)+')"'+(pg>=pn?' disabled':'')+' style="padding:3px 9px;border:1px solid #dbe3ee;border-radius:6px;background:#fff;font-family:inherit">다음 ▶</button></div>';
  var rows=r.map(function(x){var c=x[6]==='보류'?'#8a3d00':/^무효/.test(x[6])?'#8e1c1c':'#1b5e20';return '<tr style="height:30px">'+[x[0],x[3],x[2],x[4],x[5],x[6],x[7]||'—'].map(function(v,i){return '<td style="padding:5px 7px;border-bottom:1px solid #eef1f6;white-space:nowrap'+(i===5?';color:'+c+';font-weight:700':'')+'">'+esc(v)+'</td>'}).join('')+'</tr>'}).join('');
  for(var j=r.length;j<Math.min(N,all.length>N?N:r.length);j++)rows+='<tr style="height:30px"><td colspan="7"></td></tr>';
  return '<div style="overflow-x:auto;max-width:100%"><table style="border-collapse:collapse;font-size:13px;min-width:560px;width:100%"><tr>'+['보류 번호','지시 때','이력 번호','까닭','갈래','상태','닫은 때'].map(function(h){return '<th style="text-align:left;padding:5px 7px;border-bottom:1px solid #dbe3ee;background:#f0f4fa;white-space:nowrap">'+h+'</th>'}).join('')+'</tr>'+rows+'</table></div>'+(pn>1?nav:'')+'<div style="font-size:12px;color:#5d6b82;margin-top:4px">보류 = 신분 재확인 통과 전이라 실행하지 않은 지시 · 무효 = 60분 안에 통과하지 못한 지시 · 최신순 · 기준: 수행체계 정책 11절 신-2~4</div>'}
 function paint(){['00','17'].forEach(function(k){var e=document.getElementById('hv-idh-'+k);if(!e)return;var x=text(),b=e.querySelector('button');b.textContent=x.t;b.style.color=x.c;b.style.background=x.b;b.style.borderColor=x.d;b.title=(x.ti?x.ti+' · ':'')+'누르면 근거 표가 펼쳐집니다';b.setAttribute('aria-expanded',OPEN[k]?'true':'false');var d=e.querySelector('.idh-t');d.hidden=!OPEN[k];if(OPEN[k])d.innerHTML=table(k)})}
 function line(k){setTimeout(function(){if(R===null)get();else paint()},0);return '<div id="hv-idh-'+k+'" style="margin:0 0 10px"><button type="button" onclick="hvIdhT(\''+k+'\')" style="display:block;width:100%;text-align:left;padding:8px 12px;border:1px solid #dbe3ee;border-radius:10px;font-weight:700;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;cursor:pointer;font-family:inherit" title="누르면 근거 표가 펼쳐집니다">신분 재확인 · 읽는 중</button><div class="idh-t" hidden style="margin-top:6px"></div></div>'}
 window.hvIdhT=function(k){OPEN[k]=!OPEN[k];paint()};
 window.hvIdhP=function(k,p){PG[k]=Math.max(1,p);paint()};
 if(V['SC-00']){var o0=V['SC-00'];V['SC-00']=function(){var h=o0.apply(this,arguments),i=h.indexOf('<div id="al-00">');return i>=0?h.slice(0,i)+line('00')+h.slice(i):line('00')+h}}
 /* SC-17 은 대표님 지시 표부터 나온다(화-3): 지시 표(앞부분) 바로 뒤, cq-16 앞에 둔다 */
 if(V['SC-17']){var o7=V['SC-17'];V['SC-17']=function(){var h=o7.apply(this,arguments),i=h.indexOf('<div id="cq-16">');return i>=0?h.slice(0,i)+line('17')+h.slice(i):h+line('17')}}
})();
