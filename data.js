/* HIVEN AICS 통합관제 대시보드 — 공통 데이터(시험판). [실측]은 노트북 판정 파일 값, [샘플]은 시험용 값 */
var $=function(i){return document.getElementById(i)};
function pad(n){return (n<10?'0':'')+n}
function kst(){var d=new Date();return d.getFullYear()+'-'+pad(d.getMonth()+1)+'-'+pad(d.getDate())+' '+pad(d.getHours())+':'+pad(d.getMinutes())+':'+pad(d.getSeconds())}
var S=[
 ['SC-01','종합 현황'],['SC-04','사업군 통제'],['SC-05','구동 상태'],['SC-16','말 명령'],
 ['SC-14','문서 자동 생성'],['SC-07','체계 배포'],['SC-13','고객 지원'],['SC-10','수집·연동'],
 ['SC-12','검수·품질'],['SC-06','대응·경보'],['SC-11','형상·변경'],
 ['SC-09','통합사업 작업상황'],['SC-15','모델 통제 상황'],['SC-08','베타 배포 모니터링']
];
/* 번호·이름·역할·통제 접점·상태·표시색 */
var BG=[
 ['#1','HiASI','AI에서 ASI로 확장한 에이전트 두뇌','N2','정상','ok'],
 ['#2','HiCoffer','디지털 금고·KEYCOVER (루트 사업)','N2','정상','ok'],
 ['#3','HiDAM','자산 분류 체계, 모든 체계의 단일 발행·배포','N1','정상','ok'],
 ['#4','HiICT','사업기획·ISP·PMO 용역','N3','정상','ok'],
 ['#5','HiServe','통합 서비스 플랫폼(서비스 제공)','N3','구성 중','warn'],
 ['#6','HiSilver','시니어 디지털 유산·엔딩노트','N4','정상','ok'],
 ['#7','HiTrade','AI 에이전트 거래 시장','N4','구성 중','warn']
];
function tag(t,c){return '<span class="tag '+c+'">'+t+'</span>'}
/* 표 표출 기준 통일(대표님 11/04 17:49): 모든 표 한 쪽 5줄 + 같은 쪽 넘김(◀ 이전 · 쪽 번호 · 다음 ▶). tbl 표는 화면 안에서 쪽을 넘김 */
var HV_TB=0;
function tbl(h,rows){var id='tb'+(++HV_TB),P=HV_PG_STD,n=Math.ceil(rows.length/P);
 var s='<div class="tw" id="'+id+'"><table><thead><tr>'+h.map(function(x){return '<th>'+x+'</th>'}).join('')+'</tr></thead><tbody>';
 rows.forEach(function(r,i){s+='<tr'+(i>=P?' style="display:none"':'')+'>'+r.map(function(x){return '<td>'+x+'</td>'}).join('')+'</tr>'});
 s+='</tbody></table></div>';
 return n>1?s+hvTbPager(id,0,n,rows.length):s;
}
function hvTbPager(id,i,n,tot){var P=HV_PG_STD,nums='';for(var j=0;j<n;j++){if(n>9&&Math.abs(j-i)>3&&j!==0&&j!==n-1){if(nums.slice(-1)!=='…')nums+='…';continue}nums+='<button type="button" class="'+(j===i?'on':'')+'" onclick="hvTbGo(\''+id+'\','+j+')">'+(j+1)+'</button>'}
 return '<div class="hv-pg" data-tb="'+id+'"><button type="button" class="hv-pg-a" '+(i<=0?'disabled':'')+' onclick="hvTbGo(\''+id+'\','+(i-1)+')">◀ 이전</button>'+nums+'<button type="button" class="hv-pg-a" '+(i>=n-1?'disabled':'')+' onclick="hvTbGo(\''+id+'\','+(i+1)+')">다음 ▶</button><span class="hv-pg-i">'+(i+1)+'/'+n+'쪽 · '+(i*P+1)+'~'+Math.min(tot,(i+1)*P)+' / 전체 '+tot+'건 · 한 쪽 '+P+'줄</span></div>'}
function hvTbGo(id,i){var w=document.getElementById(id);if(!w)return;var R=w.querySelectorAll('tbody>tr'),P=HV_PG_STD,n=Math.ceil(R.length/P);i=Math.max(0,Math.min(n-1,i));R.forEach(function(r,k){r.style.display=(k>=i*P&&k<(i+1)*P)?'':'none'});var pg=w.nextElementSibling;if(pg&&pg.getAttribute('data-tb')===id)pg.outerHTML=hvTbPager(id,i,n,R.length)}
/* 요약 상자 공통 인터페이스(대표님 11/04 17:27·17:35): 모든 상자는 누르는 버튼. 누르면 상자 묶음 바로 아래에 그 값의 근거 데이터(항목·원천·확인 시각)를 펼치고, 다시 누르면 닫음.
   다른 화면으로 가던 상자는 펼친 내용 안의 「SC-xx에서 자세히」 버튼으로 이동. 근거: det 인자(문자열·함수) → HV_CDET[이름] → 기본(이 화면의 원천). */
var HVCD={},HVCDn=0,HVCDo='',HV_CDET={};/* 17:51 SC-01은 상자 1~10 순서 목록표를 상시 표출하므로 기본 펼침 없음 */
function hvIsTest(){return /\/test\//.test(location.pathname)}
function card(k,v,s,to,det){var id='cd'+(++HVCDn),key=(typeof cur!=='undefined'?cur:'')+'|'+k;HVCD[id]={k:k,v:v,s:s,to:to,det:det,key:key};
 var on=HVCDo===key;if(on)setTimeout(function(){hvCardPanel(id)},0);
 return '<button type="button" class="card cbtn'+(on?' on':'')+'" data-cd="'+id+'" aria-expanded="'+(on?'true':'false')+'" onclick="hvCardOpen(\''+id+'\')"><span class="k">'+k+'</span><span class="v">'+v+'</span><span class="s">'+(s||'')+'</span></button>';
}
function hvCardOpen(id){var c=HVCD[id];if(!c)return;if(HVCDo===c.key){HVCDo='';hvCardClose();return}HVCDo=c.key;hvCardPanel(id)}
function hvCardClose(){document.querySelectorAll('.cd-panel').forEach(function(x){x.remove()});document.querySelectorAll('.cbtn.on').forEach(function(x){x.classList.remove('on');x.setAttribute('aria-expanded','false')})}
function hvCardPanel(id){var c=HVCD[id],b=document.querySelector('[data-cd="'+id+'"]');if(!c||!b)return;hvCardClose();b.classList.add('on');b.setAttribute('aria-expanded','true');
 var gr=b.parentElement,d=c.det;if(typeof d==='function')d=d();if(d==null&&HV_CDET[c.k])d=HV_CDET[c.k]();
 if(d==null)d='<p class="note">'+(hvIsTest()?'<b>시험 데이터</b> — 이 값은 시험·샘플 값이며 원본 대시보드에는 싣지 않습니다(대표님 지시 11/04 15:56). 세부 항목 목록 없음.':'이 상자의 세부 항목 목록은 원천에 없습니다. 원천·확인 시각은 화면 아래 안내를 따릅니다.')+'</p>';
 var p=document.createElement('div');p.className='cd-panel';
 p.innerHTML='<div class="cd-h"><span class="tag sel">'+c.k+'</span><b class="cd-v">'+c.v+'</b><button type="button" class="cd-x" onclick="HVCDo=\'\';hvCardClose()">닫기</button></div>'+(c.s?'<div class="cd-s">'+c.s+'</div>':'')+'<div class="cd-b">'+d+'</div>'+(c.to?'<div class="cd-go"><button type="button" onclick="HVCDo=\'\';hvgo(\''+c.to+'\')">'+c.to+'에서 자세히 ▶</button></div>':'');
 gr.parentNode.insertBefore(p,gr.nextSibling)}
var V={};
/* 공통 표 규칙(대표님 11/04 14:29~14:33 지시): 모든 표는 ① 맨 위가 가장 최근(최신순) ② 한 쪽 줄 수는 화면 크기에 맞춰 자동 계산(폰·태블릿·PC 공통: 화면 높이에서 머리글·필터 몫을 뺀 뒤 기준 줄 높이(폰 58·PC 44)로 나눔, 같은 화면의 모든 표가 같은 줄 수, 최대 15줄(대표님 11/04 14:41 지시: 15줄을 넘지 않음), 최소 4줄) ③ 표 아래 「◀ 이전 · 쪽 번호 · 다음 ▶」 토글(현재 쪽/전체 쪽 표시). 창 크기·방향이 바뀌면 다시 계산해 다시 그린다. */
var HV_PG_MAX=15,HV_PG_MIN=4,HV_PG_STD=5,hvPgS={},hvRowH={};/* 17:49 대표님: 모든 표 한 쪽 5줄로 통일 */
/* 11/04 14:45·15:08 대표님 지시: 한 쪽 줄 수는 화면마다 기준 표(SC-15=이력, SC-09=진척도)의 영역 전체(제목·필터·표 머리·줄·쪽 번호)가
   창 높이 안에 고정되게 실측으로 정한다. 어느 쪽을 펴도 영역이 창을 넘지 않는 가장 큰 줄 수(1~15), 같은 화면의 모든 표는 같은 줄 수.
   표 영역 높이는 고정(마지막 쪽에서 줄이 적어도 쪽 번호 위치가 움직이지 않음). 창 크기·방향이 바뀌면 다시 잰다. */
var hvPgFix={},hvPgAll=null;
function hvPgN(key){var sc=key.slice(0,2);if(hvPgAll===sc)return 9999;return HV_PG_STD;var f=hvPgFix[sc];if(f&&f.vk===innerWidth+'x'+innerHeight)return f.n;var h=window.innerHeight||800,rh=(window.innerWidth<700?58:44),free=h-(window.innerWidth<700?230:280);return Math.max(HV_PG_MIN,Math.min(HV_PG_MAX,Math.floor(free/rh)))}
function hvPgFit(sc,ref,fn){return;/* 17:49 표 5줄 통일로 화면 높이 실측 계산 중지 */var vk=innerWidth+'x'+innerHeight,f=hvPgFix[sc];if(f&&f.vk===vk){hvPgStatic(sc);return}
 hvPgAll=sc;try{window[fn](false)}finally{hvPgAll=null}
 var pg=document.querySelector('.hv-pg[data-pg="'+ref+'"]'),tw=pg&&pg.previousElementSibling,tb=tw&&tw.querySelector('tbody');
 if(!tb||tb.rows.length<2){hvPgFix[sc]={vk:vk,n:hvPgN('x'),tw:0};window[fn](false);return}
 var hd=tw;while(hd&&hd.tagName!=='H3')hd=hd.previousElementSibling;
 var top=(hd||tw).getBoundingClientRect().top,tr=tb.getBoundingClientRect(),twr=tw.getBoundingClientRect(),pr=pg.getBoundingClientRect();
 var hs=[].filter.call(tb.rows,function(r){return !r.classList.contains('sc13-dt')}).map(function(r){return r.getBoundingClientRect().height}),body=tr.height;/* 펼침 줄(sc13-dt)은 줄 수 계산에서 뺌 — 11/04 17:33 */
 var chrome=(pr.bottom-top)-body,avail=innerHeight-16-chrome;
 function nFor(av){for(var k=HV_PG_MAX;k>=1;k--){var ok=true;for(var i=0;i<hs.length;i++){var sm=0;for(var j=i;j<Math.min(i+k,hs.length);j++)sm+=hs[j];if(sm>av){ok=false;break}if(i+k>=hs.length)break}if(ok)return k}return 1}
 hvPgFix[sc]={vk:vk,n:nFor(avail),avail:Math.max(avail,0),head:tr.top-twr.top,foot:twr.bottom-tr.bottom};
 /* 실제 화면(쪽 번호 줄바꿈 포함)으로 모든 쪽을 다시 재서, 넘치면 넘친 만큼 표 영역 높이를 줄이고 줄 수를 다시 계산 */
 var cur=+hvPgS[ref]||0;
 for(var guard=0;guard<6;guard++){var fx=hvPgFix[sc],worst=0;hvPgS[ref]=0;window[fn](false);
  var P0=document.querySelector('.hv-pg[data-pg="'+ref+'"]');if(!P0)break;var np=Math.ceil(hs.length/fx.n);
  for(var q=0;q<np;q++){hvPgS[ref]=q;window[fn](false);var P=document.querySelector('.hv-pg[data-pg="'+ref+'"]'),T=P.previousElementSibling,H=T;while(H&&H.tagName!=='H3')H=H.previousElementSibling;var ov=P.getBoundingClientRect().bottom-(H||T).getBoundingClientRect().top-(innerHeight-8);if(ov>worst)worst=ov}
  if(worst<=0)break;fx.avail=Math.max(0,fx.avail-Math.ceil(worst));fx.n=nFor(fx.avail)}
 hvPgS[ref]=cur;window[fn](false)}
/* 쪽이 2개 이상인 표는 표 영역 높이를 고정 */
function hvPgStatic(sc){var f=hvPgFix[sc];if(!f||!f.avail)return;document.querySelectorAll('.hv-pg[data-pg^="'+sc+'"]').forEach(function(p){var tw=p.previousElementSibling;if(!tw)return;var many=p.querySelectorAll('button:not(.hv-pg-a)').length>1;tw.style.minHeight=many?Math.round(f.head+f.avail+f.foot)+'px':''})}
function hvPage(list,key){var n0=hvPgN(key),n=Math.max(1,Math.ceil(list.length/n0)),i=Math.min(Math.max(0,+hvPgS[key]||0),n-1);hvPgS[key]=i;return {rows:list.slice(i*n0,(i+1)*n0),i:i,n:n,tot:list.length,key:key,per:n0}}
function hvPgGo(key,i,fn){hvPgS[key]=i;if(typeof window[fn]==='function')window[fn](false)}
function hvPgReset(pre){for(var k in hvPgS)if(k.indexOf(pre)===0)hvPgS[k]=0}
/* 그린 뒤 실제 줄 높이를 재서 다음 계산에 쓴다(표마다 data-pg 속성으로 연결) */
function hvPgMeasure(){return false;var ch=false;document.querySelectorAll('.hv-pg[data-pg]').forEach(function(p){var k=p.getAttribute('data-pg'),t=p.previousElementSibling&&p.previousElementSibling.querySelector('tbody');if(!t||!t.rows.length)return;var rh=t.getBoundingClientRect().height/t.rows.length;if(rh>10&&Math.abs((hvRowH[k]||0)-rh)>2){hvRowH[k]=rh;ch=true}});return ch}
var hvRsT=null;window.addEventListener('resize',function(){clearTimeout(hvRsT);hvRsT=setTimeout(function(){['hvSC12Paint','hvSC13Paint'].forEach(function(f){if(typeof window[f]==='function')window[f](false)})},200)});
function hvPager(pg,unit,fn){var PP=pg.per||HV_PG_MAX,a=pg.tot?pg.i*PP+1:0,b=Math.min(pg.tot,(pg.i+1)*PP),nums='';
 for(var j=0;j<pg.n;j++){if(pg.n>9&&Math.abs(j-pg.i)>3&&j!==0&&j!==pg.n-1){if(nums.slice(-1)!=='…')nums+='…';continue}nums+='<button type="button" class="'+(j===pg.i?'on':'')+'" onclick="hvPgGo(\''+pg.key+'\','+j+',\''+fn+'\')">'+(j+1)+'</button>'}
 return '<div class="hv-pg" data-pg="'+pg.key+'"><button type="button" class="hv-pg-a" '+(pg.i<=0?'disabled':'')+' onclick="hvPgGo(\''+pg.key+'\','+(pg.i-1)+',\''+fn+'\')">◀ 이전</button>'+nums+'<button type="button" class="hv-pg-a" '+(pg.i>=pg.n-1?'disabled':'')+' onclick="hvPgGo(\''+pg.key+'\','+(pg.i+1)+',\''+fn+'\')">다음 ▶</button><span class="hv-pg-i">'+(pg.i+1)+'/'+pg.n+'쪽 · '+a+'~'+b+' / 전체 '+pg.tot+unit+' · 최신순 · 한 쪽 '+PP+'줄(모든 표 통일)</span></div>'}
var cur='SC-01';
/* 열쇠 확인(샘플 인트로: 화면 안내용이며 서버 보안이 아님) */
var KEY=[111,110,108,121,111,117];
function hk2en(v){var M={'ㅂ':'q','ㅈ':'w','ㄷ':'e','ㄱ':'r','ㅅ':'t','ㅛ':'y','ㅕ':'u','ㅑ':'i','ㅐ':'o','ㅔ':'p','ㅁ':'a','ㄴ':'s','ㅇ':'d','ㄹ':'f','ㅎ':'g','ㅗ':'h','ㅓ':'j','ㅏ':'k','ㅣ':'l','ㅋ':'z','ㅌ':'x','ㅊ':'c','ㅍ':'v','ㅠ':'b','ㅜ':'n','ㅡ':'m','ㅃ':'q','ㅉ':'w','ㄸ':'e','ㄲ':'r','ㅆ':'t','ㅒ':'o','ㅖ':'p'},C=['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'],V=['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ'],T=['','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'],X={'ㅘ':'ㅗㅏ','ㅙ':'ㅗㅐ','ㅚ':'ㅗㅣ','ㅝ':'ㅜㅓ','ㅞ':'ㅜㅔ','ㅟ':'ㅜㅣ','ㅢ':'ㅡㅣ','ㄳ':'ㄱㅅ','ㄵ':'ㄴㅈ','ㄶ':'ㄴㅎ','ㄺ':'ㄹㄱ','ㄻ':'ㄹㅁ','ㄼ':'ㄹㅂ','ㄽ':'ㄹㅅ','ㄾ':'ㄹㅌ','ㄿ':'ㄹㅍ','ㅀ':'ㄹㅎ','ㅄ':'ㅂㅅ'},o='';for(var i=0;i<v.length;i++){var c=v.charCodeAt(i),j=[];if(c>=44032&&c<=55203){var n=c-44032;j=[C[Math.floor(n/588)],V[Math.floor(n%588/28)],T[n%28]];}else j=[v.charAt(i)];for(var k=0;k<j.length;k++){var u=X[j[k]]||j[k];for(var m=0;m<u.length;m++){var h=u.charAt(m);o+=(M[h]||h);}}}return o;}
function keyOk(v){v=hk2en(String(v||'').trim()).toLowerCase();if(v.length!==KEY.length)return false;for(var i=0;i<KEY.length;i++){if(v.charCodeAt(i)!==KEY[i])return false;}return true;}
function sget(){try{return sessionStorage.getItem('hv_in')==='1'}catch(e){return false}}
function sset(x){try{x?sessionStorage.setItem('hv_in','1'):sessionStorage.removeItem('hv_in')}catch(e){}}
