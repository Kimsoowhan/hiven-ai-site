/* HIVEN AICS 관리자 대시보드 — 공통 데이터(시험판). [실측]은 노트북 판정 파일 값, [샘플]은 시험용 값 */
var $=function(i){return document.getElementById(i)};
function pad(n){return (n<10?'0':'')+n}
function kst(){var d=new Date();return d.getFullYear()+'-'+pad(d.getMonth()+1)+'-'+pad(d.getDate())+' '+pad(d.getHours())+':'+pad(d.getMinutes())+':'+pad(d.getSeconds())}
var S=[
 ['SC-01','종합 현황'],['SC-02','사업군 통제'],['SC-03','구동 상태'],['SC-04','말 명령'],
 ['SC-05','문서 자동 생성'],['SC-06','체계 배포'],['SC-07','고객 지원'],['SC-08','수집·연동'],
 ['SC-09','검수·품질'],['SC-10','대응·경보'],['SC-11','형상·변경'],
 ['SC-12','통합사업 작업상황']
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
var cur='SC-01';
/* 열쇠 확인(샘플 인트로: 화면 안내용이며 서버 보안이 아님) */
var KEY=[104,105,98,105,122];
function keyOk(v){v=String(v||'').trim();if(v.length!==KEY.length)return false;for(var i=0;i<KEY.length;i++){if(v.charCodeAt(i)!==KEY[i])return false;}return true;}
function sget(){try{return sessionStorage.getItem('hv_in')==='1'}catch(e){return false}}
function sset(x){try{x?sessionStorage.setItem('hv_in','1'):sessionStorage.removeItem('hv_in')}catch(e){}}
