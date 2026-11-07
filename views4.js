/* W28-03(Opus 11/05): SC-15 구분별 변동 추이 그래프 확정 사양(cowork/SC-15_추이그래프_확정사양.md)을 그대로 쓰는 공통 부품.
   SC-15 코드(views3.js hvTrIn)는 건드리지 않고, 같은 눈금·색 면·현재 시점 선·「< 30초 분 시간 일 월 년 >」 한 벌·30초 흐름을 화면별 상태로 그린다. 규칙 54·0-10. */
var hvTG={};
function hvTGin(k,o){var S=hvTG[k]||(hvTG[k]={f:{tu:o.tu||'일',tm:'모델 전체',tc:'구간',th:{},to:hvTRD0}});S.o=o;setTimeout(function(){hvTGdraw(k)},0);return '<h3>'+hvEsc(o.title)+'</h3><div class="hvTGbox" id="hvTG_'+k+'">'+hvTGhtml(k)+'</div>'}
function hvTGhtml(k){var S=hvTG[k];if(!S||!S.o)return '';var o=S.o,F=S.f,d=o.ev||[];
 if(hvTRU.indexOf(F.tu)<0)F.tu='일';
 var ms=['모델 전체'];d.forEach(function(e){if(e.m&&ms.indexOf(e.m)<0)ms.push(e.m)});if(ms.indexOf(F.tm)<0)F.tm='모델 전체';
 var u=F.tu,sub=!!hvTRS[u]&&u!=='일',all=d.filter(function(e){return F.tm==='모델 전체'||e.m===F.tm}),nx=sub?all.filter(function(e){return !e.hm}).length:0;
 var ev=all.filter(function(e){return !sub||e.hm});
 var now=Date.now(),c0=hvTrStep(hvTrFloor(now,u),u,F.to),B=[];for(var i=-hvTRN;i<=hvTRN;i++)B.push(hvTrStep(c0,u,i));
 var nb=hvTrFloor(now,u),nowI=-1;B.forEach(function(b,i){if(b===nb)nowI=i});
 var S2=o.types.map(function(ty){var cum=F.tc==='누적'?ev.filter(function(e){return e.y===ty&&e.t<B[0]}).length:0;
  return {t:ty,v:B.map(function(b){if(b>nb)return null;var n=ev.filter(function(e){return e.y===ty&&e.t>=b&&e.t<hvTrStep(b,u,1)}).length;cum+=n;return F.tc==='누적'?cum:n})}});
 var vis=S2.filter(function(s){return !F.th[s.t]}),mx=1;vis.forEach(function(s){s.v.forEach(function(x){if(x>mx)mx=x})});
 var q=function(x){return String(x).replace(/'/g,"\\'")};
 var btn=function(key,list){return list.map(function(x){return '<button type="button" class="'+(F[key]===x?'on':'')+'" onclick="hvTGset(\''+k+'\',\''+key+'\',\''+q(x)+'\')">'+hvEsc(x)+'</button>'}).join('')};
 var tg='<span style="white-space:nowrap;display:inline-flex;gap:8px">'+hvTRU.map(function(x){var on=u===x;return '<button type="button" class="'+(on?'on':'')+'" style="'+(on?'':'opacity:.45')+'" onclick="hvTGset(\''+k+'\',\'tu\',\''+x+'\')">'+x+'</button>'}).join('')+'</span>';
 var g='<div class="sc13-f sc13-l sc13-lw"><span class="sc13-lb w">모델</span>'+btn('tm',ms)+'</div>'
 +'<div class="sc13-f sc13-l sc13-lw"><span class="sc13-lb w">값</span>'+btn('tc',['구간','누적'])+'</div>'
 +'<div class="sc13-f sc13-l sc13-lw"><span class="sc13-lb w">구분</span>'+o.types.map(function(t){var off=!!F.th[t];return '<button type="button" class="'+(off?'':'on')+'" style="'+(off?'':'background:'+o.colors[t]+';border-color:'+o.colors[t]+';color:#fff')+'" onclick="hvTGtog(\''+k+'\',\''+q(t)+'\')">'+hvEsc(t)+'</button>'}).join('')+'</div>';
 g+='<div style="display:flex;justify-content:flex-end;align-items:center;gap:8px;flex-wrap:wrap;margin:6px 0">'+(F.to!==hvTRD0?'<button type="button" class="on" onclick="hvTGpan(\''+k+'\',0)">현재로</button>':'')+'<span style="white-space:nowrap;display:inline-flex;gap:8px"><button type="button" onclick="hvTGpan(\''+k+'\',-1)">&lt;</button>'+tg+'<button type="button" onclick="hvTGpan(\''+k+'\',1)">&gt;</button></span></div>';
 var bx=document.getElementById('hvTG_'+k);if(bx){bx.style.width='';if(innerWidth>700){var bl=bx.getBoundingClientRect().left;bx.style.width=Math.max(bx.clientWidth,Math.round(innerWidth-64-bl))+'px'}}
 var W=Math.max(320,Math.round((bx&&bx.clientWidth?bx.clientWidth:1000)-2)),H=Math.max(280,Math.min(360,Math.round(W*0.3)+50)),L=58,R=16,T=34,BT=84,pw=W-L-R,ph=H-T-BT,X=function(i){return L+i*pw/(B.length-1)},Y=function(v){return T+ph-v*ph/mx};
 var s='<svg id="hvTGsvg_'+k+'" viewBox="0 0 '+W+' '+H+'" width="100%" style="display:block;font:11px sans-serif;touch-action:pan-y;cursor:grab" role="img" aria-label="'+hvEsc(o.title)+'">';
 var st=1,sq=[1,2,5];for(var ki=0;;ki++){st=sq[ki%3]*Math.pow(10,Math.floor(ki/3));if(mx/st<=5)break}mx=Math.ceil(mx/st)*st;for(var y=0;y<=mx;y+=st)s+='<line x1="'+L+'" x2="'+(W-R)+'" y1="'+Y(y)+'" y2="'+Y(y)+'" stroke="#e3e8f0"/><text x="'+(L-6)+'" y="'+(Y(y)+4)+'" text-anchor="end" fill="#667">'+y+'</text>';
 B.forEach(function(b,i){s+='<line x1="'+X(i)+'" x2="'+X(i)+'" y1="'+T+'" y2="'+(T+ph)+'" stroke="#f1f4f9"/>';if((i-(nowI>=0?nowI:hvTRN))%(W<500?2:1)===0){var ly=T+ph+12;s+='<text x="'+X(i)+'" y="'+ly+'" text-anchor="end" fill="#445" transform="rotate(-40 '+X(i)+' '+ly+')">'+hvTrAx(hvTrLbl(b,u))+'</text>'}});
 if(nowI>=0){var nx2=X(nowI);s+='<line x1="'+nx2+'" x2="'+nx2+'" y1="'+T+'" y2="'+(H-20)+'" stroke="#333" stroke-opacity="0.45" stroke-width="6"/><path d="M'+(nx2-7)+','+(T-16)+' L'+(nx2+7)+','+(T-16)+' L'+nx2+','+(T-2)+' Z" fill="#e00"/><line x1="'+nx2+'" x2="'+nx2+'" y1="2" y2="'+(T-14)+'" stroke="#e00" stroke-width="3"/><text x="'+(nx2+3)+'" y="'+(H-6)+'" text-anchor="end" fill="#e00" font-weight="700">현재 '+hvTrLbl(now,'30초')+'</text>'}
 vis.slice().sort(function(a,b){return Math.max.apply(null,b.v.map(function(x){return x||0}))-Math.max.apply(null,a.v.map(function(x){return x||0}))}).forEach(function(sr){var c=o.colors[sr.t],pts=[],xi=[];sr.v.forEach(function(v,i){if(v!==null){pts.push(X(i)+','+Y(v));xi.push(i)}});
  if(pts.length){s+='<polygon fill="'+c+'" fill-opacity="0.12" stroke="none" points="'+X(xi[0])+','+Y(0)+' '+pts.join(' ')+' '+X(xi[xi.length-1])+','+Y(0)+'"/><polyline fill="none" stroke="'+c+'" stroke-width="2" stroke-opacity="0.9" points="'+pts.join(' ')+'"/>'}
  sr.v.forEach(function(v,i){if(v)s+='<circle cx="'+X(i)+'" cy="'+Y(v)+'" r="3.2" fill="'+c+'"><title>'+hvEsc(hvTrLbl(B[i],u)+' · '+sr.t+' '+v+'건')+'</title></circle>'})});
 s+='</svg>';
 var tot=o.types.map(function(t){var n=all.filter(function(e){return e.y===t}).length;return '<span style="display:inline-block;margin:2px 10px 2px 0;white-space:nowrap"><i style="display:inline-block;width:10px;height:10px;border-radius:2px;background:'+o.colors[t]+';margin-right:4px"></i><b style="color:#333;font-weight:700">'+hvEsc(t)+'</b> '+n+'</span>'}).join('');
 return g+'<div class="tw" style="overflow:hidden">'+s+'</div><p class="note" style="text-align:right">'+tot+'</p><p class="note">'+hvEsc(F.tm)+' · 단위 '+u+' · '+(F.tc==='누적'?'누적':'구간별')+' 건수 · 색 면 = 구분별 건수(구분 버튼으로 켜고 끔) · 빨간 화살표·짙은 회색 선 = 현재 시점 · 30초마다 갱신 · 끌거나 &lt; &gt;로 이동, 「현재로」로 복귀'+(nx?' · 시각 미기재 '+nx+'건은 '+u+' 단위에서 제외':'')+' · '+hvEsc(o.src)+'</p>'}
function hvTGdraw(k){var b=document.getElementById('hvTG_'+k);if(b){b.innerHTML=hvTGhtml(k);hvTGdrag(k)}}
function hvTGset(k,key,v){var F=hvTG[k].f;F[key]=v;if(key==='tu')F.to=hvTRD0;hvTGdraw(k)}
function hvTGtog(k,t){var F=hvTG[k].f;F.th[t]=!F.th[t];hvTGdraw(k)}
function hvTGpan(k,n){var F=hvTG[k].f;F.to=n===0?hvTRD0:F.to+n*Math.ceil(hvTRN/2);hvTGdraw(k)}
function hvTGdrag(k){var s=document.getElementById('hvTGsvg_'+k);if(!s||s._dg)return;s._dg=1;var x0=null,dx=0;
 s.addEventListener('pointerdown',function(e){x0=e.clientX;dx=0;s.setPointerCapture(e.pointerId);s.style.cursor='grabbing'});
 s.addEventListener('pointermove',function(e){if(x0===null)return;dx=e.clientX-x0;s.style.transform='translateX('+dx+'px)'});
 s.addEventListener('pointerup',function(){if(x0===null)return;var w=s.getBoundingClientRect().width,n=Math.round(-dx/(w/(2*hvTRN)));x0=null;s.style.transform='';s.style.cursor='grab';if(n){hvTG[k].f.to+=n;hvTGdraw(k)}})}
setInterval(function(){Object.keys(hvTG).forEach(function(k){if(document.getElementById('hvTG_'+k))hvTGdraw(k)})},30000);
window.addEventListener('resize',function(){Object.keys(hvTG).forEach(function(k){if(document.getElementById('hvTG_'+k))hvTGdraw(k)})});
/* SC-01 장애·조치 변동 추이(A-01): 원천 모델통제 이력 게시본 + action_lifecycle.tsv 3분류(미조치·조치 중·조치 완료), 기준 시각 = 이력 등록 시각 */
var hvTGC01={'미조치':'#c62828','조치 중':'#ef6c00','조치 완료':'#43a047'};
function hvTG01(E,cls){return hvTGin('sc01',{title:'장애·조치 변동 추이',types:['미조치','조치 중','조치 완료'],colors:hvTGC01,tu:'일',
 ev:E.map(function(e){var hm=hvHm(e);return {t:Date.parse(e.date+'T'+(hm||'12:00')+':00+09:00'),hm:hm,y:cls(e),m:e.model}}).filter(function(e){return !isNaN(e.t)}),
 src:'원천 cowork/ctl/model_control_history.tsv(등록 시각) · 3분류 cowork/ctl/action_lifecycle.tsv'})}
/* SC-14 진척 변동 추이(A-02): 원천 cowork/log.tsv(상태 기록 시각) — 승인·반영 / Fable 통과 / 완료·검수 대기 / 그 밖 기록 */
var hvTGC12={'승인·반영':'#43a047','Fable 통과':'#1e88e5','완료·검수 대기':'#f9a825','그 밖 기록':'#8a90a0'};
function hvTG12y(st){st=String(st||'');return /승인/.test(st)?'승인·반영':/통과|G2/.test(st)?'Fable 통과':/완료|검수 대기/.test(st)?'완료·검수 대기':'그 밖 기록'}
function hvTG12(logTxt){var rows=hvTsv(logTxt||''),ev=rows.map(function(c){var m=String(c[0]||'').match(/(?:(\d{4})-)?(\d{1,2})[\/-](\d{1,2})\s+(\d{1,2}):(\d{2})/);if(!m)return null;var hm=pad(+m[4])+':'+m[5];
  return {t:Date.parse((m[1]||'2026')+'-'+pad(+m[2])+'-'+pad(+m[3])+'T'+hm+':00+09:00'),hm:hm,y:hvTG12y(c.length>4?c[3]:c.slice(2).join(' ')),m:c[1]}}).filter(function(e){return e&&!isNaN(e.t)});
 return hvTGin('sc12',{title:'진척 변동 추이',types:['승인·반영','Fable 통과','완료·검수 대기','그 밖 기록'],colors:hvTGC12,tu:'시간',ev:ev,src:'원천 cowork/log.tsv '+ev.length+'건(상태 기록 시각)'})}
