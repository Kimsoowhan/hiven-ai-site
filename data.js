/* HIVEN AICS 관리자 대시보드 — 공통 데이터(시험판). [실측]은 노트북 판정 파일 값, [샘플]은 시험용 값 */
var $=function(i){return document.getElementById(i)};
function pad(n){return (n<10?'0':'')+n}
function kst(){var d=new Date();return d.getFullYear()+'-'+pad(d.getMonth()+1)+'-'+pad(d.getDate())+' '+pad(d.getHours())+':'+pad(d.getMinutes())+':'+pad(d.getSeconds())}
var S=[
 ['SC-01','종합 현황'],['SC-02','사업군 통제'],['SC-03','구동 상태'],['SC-04','말 명령'],
 ['SC-05','문서 자동 생성'],['SC-06','체계 배포'],['SC-07','고객 지원'],['SC-08','수집·연동'],
 ['SC-09','검수·품질'],['SC-10','대응·경보'],['SC-11','형상·변경'],
 ['SC-12','통합사업 작업상황'],['SC-13','모델 통제 상황']
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
function tbl(h,rows){
 var s='<div class="tw"><table><thead><tr>'+h.map(function(x){return '<th>'+x+'</th>'}).join('')+'</tr></thead><tbody>';
 rows.forEach(function(r){s+='<tr>'+r.map(function(x){return '<td>'+x+'</td>'}).join('')+'</tr>'});
 return s+'</tbody></table></div>';
}
function card(k,v,s,to){
 return '<div class="card'+(to?' link" onclick="hvgo(\''+to+'\')"':'"')+'><div class="k">'+k+'</div><div class="v">'+v+'</div><div class="s">'+(s||'')+'</div></div>';
}
var V={};
/* 공통 표 규칙(대표님 11/04 14:29~14:32 지시): 모든 표는 ① 맨 위가 가장 최근(최신순) ② 한 화면 14줄(2주 단위)까지만 표출 ③ 표 아래 「◀ 이전 · 쪽 번호 · 다음 ▶」 토글로 넘김(현재 쪽/전체 쪽 표시). 모든 화면 공통 인터페이스. */
var HV_PG=14,hvPgS={};
function hvPage(list,key){var n=Math.max(1,Math.ceil(list.length/HV_PG)),i=Math.min(Math.max(0,+hvPgS[key]||0),n-1);hvPgS[key]=i;return {rows:list.slice(i*HV_PG,(i+1)*HV_PG),i:i,n:n,tot:list.length,key:key}}
function hvPgGo(key,i,fn){hvPgS[key]=i;if(typeof window[fn]==='function')window[fn](false)}
function hvPgReset(pre){for(var k in hvPgS)if(k.indexOf(pre)===0)hvPgS[k]=0}
function hvPager(pg,unit,fn){var a=pg.tot?pg.i*HV_PG+1:0,b=Math.min(pg.tot,(pg.i+1)*HV_PG),nums='';
 for(var j=0;j<pg.n;j++){if(pg.n>9&&Math.abs(j-pg.i)>3&&j!==0&&j!==pg.n-1){if(nums.slice(-1)!=='…')nums+='…';continue}nums+='<button type="button" class="'+(j===pg.i?'on':'')+'" onclick="hvPgGo(\''+pg.key+'\','+j+',\''+fn+'\')">'+(j+1)+'</button>'}
 return '<div class="hv-pg"><button type="button" class="hv-pg-a" '+(pg.i<=0?'disabled':'')+' onclick="hvPgGo(\''+pg.key+'\','+(pg.i-1)+',\''+fn+'\')">◀ 이전</button>'+nums+'<button type="button" class="hv-pg-a" '+(pg.i>=pg.n-1?'disabled':'')+' onclick="hvPgGo(\''+pg.key+'\','+(pg.i+1)+',\''+fn+'\')">다음 ▶</button><span class="hv-pg-i">'+(pg.i+1)+'/'+pg.n+'쪽 · '+a+'~'+b+' / 전체 '+pg.tot+unit+' · 최신순 · 한 쪽 '+HV_PG+unit+'(2주 단위)</span></div>'}
var cur='SC-01';
/* 열쇠 확인(샘플 인트로: 화면 안내용이며 서버 보안이 아님) */
var KEY=[104,105,98,105,122];
function keyOk(v){v=String(v||'').trim();if(v.length!==KEY.length)return false;for(var i=0;i<KEY.length;i++){if(v.charCodeAt(i)!==KEY[i])return false;}return true;}
function sget(){try{return sessionStorage.getItem('hv_in')==='1'}catch(e){return false}}
function sset(x){try{x?sessionStorage.setItem('hv_in','1'):sessionStorage.removeItem('hv_in')}catch(e){}}
