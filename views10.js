/* views10.js — SC-18 Stakeholder · SC-19 이해관계자 및 협력사 · SC-20 이용약관 및 정책(탭 넷) · SC-21 계약(대표님 2026-11-13 18:22~18:57 확정 번호, Fable 지시 · Opus 5.5)
   + 원천 미연결 화면 이음(SC-03 · SC-04 · SC-06 · SC-07 · SC-11, 이음 설계 3~7절 가운데 저장소 안 자료로 되는 것만).
   값은 모두 게시 원천(cowork/ctl/*.tsv · cowork/publish_meta.json)에서 읽는다. 원천에 없는 값은 「확인 안 됨」, 0건은 원천 대장이 0줄일 때만 0건.
   SC-18~21 원천은 tools/gen_ext.py가 HiBiz 41~44 대장(작업 사본)에서 낸다. 열쇠 판정 · 잠금 · 경보 동작은 건드리지 않는다(읽기만).
   화면을 열 때 원천을 한 번 읽는다(주기 읽기 없음 · ic.hiven.ai.kr 호출 없음). */
(function(){
var NA='확인 안 됨';
function E(s){return typeof hvEsc==='function'?hvEsc(s):String(s==null?'':s)}
function B(){return typeof hv5Base==='function'?hv5Base():((location.pathname.indexOf('/test/')>=0?'../':'')+'cowork/ctl/')}
function T(t){return typeof hv5Tsv==='function'?hv5Tsv(t):(function(){var L=String(t).replace(/\r/g,'').split('\n').filter(function(x){return x.length});return {h:L[0]?L[0].split('\t'):[],r:L.slice(1).map(function(x){return x.split('\t')})}})()}
/* 여러 원천을 한 번에 읽어 그린다. 하나라도 못 읽으면 값을 추정하지 않고 실패를 적는다 */
/* 탭 · 갈래 · 칸을 바꿀 때는 화면 전체를 다시 그려(render) 보존 기록 접기(views9.js hvSweep, 기준선 앞 날짜를 단 줄)가 같은 규칙으로 다시 돌게 한다. 이때만 막 읽은 원천을 다시 쓴다(새로 읽지 않음) */
var CA={},RE=false;
function sw(){var mn=document.getElementById('main');if(mn&&typeof hvSweep==='function'){mn.setAttribute('data-sw','0');hvSweep()}}
function fill(el,draw,D){var n=document.getElementById(el);if(!n)return;n.innerHTML=draw(D);if(typeof hvTbAuto==='function')hvTbAuto(n);sw()}
/* OPT: 아직 만들어지지 않았을 수 있는 원천(파일 이름 → 머리글). 못 읽으면 지어내지 않고 머리글만 있는 0줄(none:1)로 둔다 */
var OPT={'charter_ledger.tsv':['번호','문서','판','상태','자리(HiBiz)','잇는 화면','비고'],'charter_purpose.tsv':['항','묶음','목적 사업','하기 전에 필요한 절차','판']};
function load(el,files,draw){var re=RE&&CA[el];RE=false;setTimeout(function(){if(re){fill(el,draw,CA[el]);return}Promise.all(files.map(function(f){var q=hvFetch(B()+f,'text').then(T);return OPT[f]?q.catch(function(){return {h:OPT[f].slice(),r:[],none:1}}):q})).then(function(D){CA[el]=D;fill(el,draw,D)}).catch(function(e){var n=document.getElementById(el);if(n)n.innerHTML='<p class="note">'+tag('원천 읽기 실패','bad')+' '+files.map(function(f){return 'cowork/ctl/'+f}).join(' · ')+' ('+E(e&&e.message)+') — 값을 추정하지 않습니다.</p>'})},0)}
function redraw(){RE=true;if(typeof render==='function'&&typeof cur!=='undefined')render(cur)}
function flow(id){var a=[[id,''],['SC-02','종합 현황'],['SC-00','대표님 결재'],['SC-15','문서 자동 생성']];
 return '<p class="note hv10-flow"><b>흐름</b> '+a.map(function(x,i){return '<button type="button" onclick="hvgo(\''+x[0]+'\')" style="margin:2px;padding:2px 9px;border:1px solid #9fb0cf;border-radius:7px;background:'+(i?'#fff':'#e3ecfa')+';cursor:pointer;white-space:nowrap"><b>'+x[0]+'</b>'+(x[1]?' '+x[1]:' 이 화면')+'</button>'}).join(' → ')+'</p>'}
function src(files,tool,folder){return '<p class="note"><b>원천</b> '+files.map(function(f){return 'cowork/ctl/'+f}).join(' · ')+' · 만드는 도구 '+tool+(folder?' · HiBiz 원천 폴더 '+folder:'')+' · 화면을 열 때 한 번 읽음 · 원천에 없는 값은 「'+NA+'」</p>'}
function rows(d){return d.r.map(function(r){return d.h.map(function(_,i){return E(r[i]==null?'':r[i])})})}
/* 「확인 안 됨」으로 남은 칸: [줄 번호, 칸 이름] */
function naCells(d){var o=[];d.r.forEach(function(r){d.h.forEach(function(h,i){if(String(r[i]||'').indexOf(NA)>=0)o.push([r[0],h])})});return o}
function naList(o){return o.map(function(x){return x[0]+' '+x[1]}).join(' · ')}
function open(st){return !/조치 완료|해제|끝남|완료/.test(String(st||''))}
function col(d,name){for(var i=0;i<d.h.length;i++)if(d.h[i].indexOf(name)===0)return i;return -1}
function days(s){var m=String(s||'').match(/(20\d\d)-(\d\d)-(\d\d)/);if(!m)return null;return Math.floor((Date.parse(m[1]+'-'+m[2]+'-'+m[3]+'T00:00:00+09:00')-Date.now())/86400000)}
function alertBox(items){if(!items.length)return '<div class="card" style="margin:8px 0;border-left:4px solid #17703d"><div class="k">'+tag('얼럿 없음','ok')+' 열린 얼럿 0건</div></div>';
 return '<div class="card hv10-al" style="margin:8px 0;border-left:4px solid #c62828"><div class="k">'+tag('얼럿','bad')+' '+items.length+'가지</div><ul class="note" style="margin:4px 0 0 18px;padding:0">'+items.map(function(x){return '<li>'+x+'</li>'}).join('')+'</ul></div>'}
function head(id,name,lead){return '<h2>'+id+' '+name+'</h2><p class="lead">'+lead+'</p>'}

/* ───── SC-18 Stakeholder ───── */
var F18=['ext_stakeholder.tsv','ext_stakeholder_alerts.tsv'];
V['SC-18']=function(){load('hv10-18',F18,function(D){var s=D[0],a=D[1],si=col(a,'상태'),op=a.r.filter(function(r){return open(r[si])}),na=naCells(s),al=[];
  if(op.length)al.push('끝나지 않은 받은 얼럿 '+op.length+'건: '+op.map(function(r){return E(r[0]+' '+(r[2]||'')+' '+(r[3]||''))}).join(' · ')+' — 대처 순서대로 처리하고 결재가 필요하면 SC-00');
  if(na.length)al.push('「'+NA+'」으로 남은 기준 '+na.length+'칸: '+E(naList(na))+' — 41_HIVEN_Stakeholder(STK) 대장에서 채움');
  var h='<div class="grid">'+card('Stakeholder',s.r.length+'곳','시스템과 맞닿은 곳',null,function(){return tbl(['번호','이름','우리가 기대는 것'],s.r.map(function(r){return [E(r[0]),E(r[1]),E(r[2])]}))})
   +card('받은 얼럿',a.r.length+'건',a.r.length?'원천 대장 기준':'받은 얼럿 없음(0건)')
   +card('끝나지 않은 얼럿',op.length+'건',op.length?tag('조치 필요','bad'):tag('없음','ok'))
   +card('「'+NA+'」 기준',na.length+'칸','채워야 할 기준',null,function(){return na.length?tbl(['번호','칸'],na.map(function(x){return [E(x[0]),E(x[1])]})):'<p class="note">없음</p>'})+'</div>';
  h+=alertBox(al);
  h+='<h3>Stakeholder 목록</h3>'+tbl(s.h.map(E),rows(s));
  h+='<h3>받은 얼럿과 대처(최신순)</h3>'+(a.r.length?tbl(a.h.map(E),rows({h:a.h,r:a.r.slice().reverse()})):tbl(a.h.map(E),[])+'<p class="note">받은 얼럿 없음(0건) — 대장(41_10_관리)에 줄이 생기면 여기에 최신순으로 보입니다.</p>');
  return h+src(F18,'tools/gen_ext.py','41_HIVEN_Stakeholder(STK)')});
 return head('SC-18','Stakeholder','시스템과 맞닿은 곳(Cloudflare · GitHub · Anthropic)이 먼저 띄운 얼럿과 대처를 봅니다. 고객 지원(SC-01 · SC-14)은 고객 → 우리, 이 화면은 바깥 기반 → 우리 방향입니다.')+flow('SC-18')+'<div id="hv10-18" class="hv-nosw">읽는 중…</div>'};

/* ───── SC-19 이해관계자 및 협력사 ───── */
var F19=['ext_partner.tsv','ext_sla_mou.tsv'];
V['SC-19']=function(){load('hv10-19',F19,function(D){var p=D[0],m=D[1],gi=col(p,'갈래'),ki=col(p,'기한'),pt=p.r.filter(function(r){return /협력사/.test(r[gi])}),st=p.r.filter(function(r){return /이해관계자/.test(r[gi])}),na=naCells(p).concat(naCells(m)),al=[];
  var mk=col(m,'기한'),due=p.r.filter(function(r){var d=days(r[ki]);return d!==null&&d>=0&&d<=7}).concat(m.r.filter(function(r){var d=days(r[mk]);return d!==null&&d>=0&&d<=7}));
  if(due.length)al.push('기한 7일 안 '+due.length+'건: '+due.map(function(r){return E(r[0])}).join(' · '));
  if(na.length)al.push('「'+NA+'」으로 남은 기준 '+na.length+'칸: '+E(naList(na))+' — 42_HIVEN_이해관계자_협력사(PTN) 대장에서 채움');
  function part(list,name){return '<h3>'+name+' ('+list.length+'곳)</h3>'+(list.length?tbl(p.h.map(E),rows({h:p.h,r:list})):tbl(p.h.map(E),[])+'<p class="note">'+name+' 0곳</p>')}
  var h='<div class="grid">'+card('협력사',pt.length+'곳','계약보다 앞선 준비')+card('이해관계자',st.length+'곳','공고·기관')+card('협의 · SLA · MOU',m.r.length+'건',m.r.length?'원천 대장 기준':'진행 중 협의 없음(0건)')
   +card('「'+NA+'」 기준',na.length+'칸','채워야 할 기준',null,function(){return na.length?tbl(['번호','칸'],na.map(function(x){return [E(x[0]),E(x[1])]})):'<p class="note">없음</p>'})+'</div>';
  h+=alertBox(al);
  h+=part(pt,'협력사')+part(st,'이해관계자');
  h+='<h3>협의 · SLA · MOU</h3>'+tbl(m.h.map(E),rows(m))+(m.r.length?'':'<p class="note">진행 중인 협의 · SLA · MOU 없음(0건). 합의되면 SC-21 계약 대장에 새 줄을 만들고 번호로 잇습니다.</p>');
  return h+src(F19,'tools/gen_ext.py','42_HIVEN_이해관계자_협력사(PTN)')});
 return head('SC-19','이해관계자 및 협력사','계약보다 앞서 선행돼야 하는 것(특허 · 도메인 · 메일 · 인증, 협의 · SLA · MOU)을 협력사와 이해관계자 갈래로 나눠 봅니다.')+flow('SC-19')+'<div id="hv10-19" class="hv-nosw">읽는 중…</div>'};

/* ───── SC-20 이용약관 및 정책 (탭 넷: 화면 안 단추로 전환, 원천은 한 번만 읽음. 대표님 18:45~18:57 지시 · sc_structure.tsv · DR-19) ───── */
var F20=['policy_list.tsv','member_ledger.tsv','beta_ledger.tsv','pip_ledger.tsv','charter_ledger.tsv','charter_purpose.tsv'],T20={tab:'ch',D:null,cg:'',cp:0};/* 대표님 19:31(이력 1317): 탭 다섯, 정관이 맨 앞 */
var TABS20=[['ch','정관'],['pl','이용약관 및 정책'],['mem','회원관리'],['beta','무료 베타 버전 관리'],['pi','개인정보 처리']];
function ids(s,p){return (String(s||'').match(new RegExp(p+'-\\d+','g'))||[])}
/* 맞물림: 한 줄(회원 · 설치) → 동의한 약관 판(PL) · 개인정보 묶음(PI). 없는 번호 · 빈 번호는 어긋남 */
function link(d,name,plN,piN){var c1=col(d,'동의한 약관'),c2=col(d,'동의한 개인정보'),c3=col(d,'개인정보 묶음'),o=[];
 d.r.forEach(function(r){var pl=ids(r[c1],'PL').concat(c2>=0?ids(r[c2],'PL'):[]),pi=ids(r[c3],'PI');pl.forEach(function(x){if(!plN[x])o.push(name+' '+r[0]+' → '+x+' 없음')});pi.forEach(function(x){if(!piN[x])o.push(name+' '+r[0]+' → '+x+' 없음')});if(!pl.length||!pi.length)o.push(name+' '+r[0]+' → PL·PI 번호 없음')});return o}
function draw20(){var D=T20.D;if(!D)return '';var pl=D[0],me=D[1],be=D[2],pi=D[3],ch=D[4],cp=D[5],plN={},piN={};pl.r.forEach(function(r){plN[r[0]]=1});pi.r.forEach(function(r){piN[r[0]]=1});
 var miss=link(me,'회원',plN,piN).concat(link(be,'설치',plN,piN));
 var ret=col(pi,'보유 기간'),des=col(pi,'파기 방법'),cl=col(pi,'방침·약관의 근거'),dr19=pi.r.filter(function(r){return [ret,des,cl].some(function(i){return i<0||!r[i]||String(r[i]).indexOf(NA)>=0})});
 var si=col(pl,'시행 여부'),plNa=pl.r.filter(function(r){return String(r[si]||'').indexOf(NA)>=0}),al=[];
 if(plNa.length)al.push('시행 여부 「'+NA+'」 약관·정책 '+plNa.length+'건: '+plNa.map(function(r){return E(r[0])}).join(' · '));
 if(dr19.length)al.push('DR-19 어긋남(보유 기간 · 파기 방법 · 근거 조항 가운데 「'+NA+'」) 개인정보 묶음 '+dr19.length+'줄: '+dr19.map(function(r){return E(r[0])}).join(' · '));
 if(miss.length)al.push('맞물림 어긋남 '+miss.length+'건: '+E(miss.join(' · ')));
 var h='<div class="grid">'+card('정관',ch.r.length+'건',ch.none?'정관 대장 만들기 전(0건)':'정관 대장')+card('약관 · 정책',pl.r.length+'건','PL 번호')+card('회원',me.r.length+'명',me.r.length?'회원 관리 대장':'회원 0명(베타 배포 전)')+card('베타 설치',be.r.length+'건',be.r.length?'베타 설치 대장':'베타 설치 기록 0건')+card('개인정보 묶음',pi.r.length+'묶음','PI 번호')+card('DR-19 어긋남',dr19.length+'줄',dr19.length?tag('채울 것','bad'):tag('없음','ok'))+'</div>';
 h+=alertBox(al);
 h+='<div style="margin:10px 0">'+TABS20.map(function(t){var on=T20.tab===t[0];return '<button type="button" class="tab'+(on?' on':'')+'" data-t20="'+t[0]+'" onclick="hv10Tab20(\''+t[0]+'\')" style="margin:0 6px 6px 0;padding:6px 12px;border:1px solid #c5cde0;border-radius:8px;background:'+(on?'#1a2a5e':'#fff')+';color:'+(on?'#fff':'#1a2a5e')+';cursor:pointer;white-space:nowrap">'+t[1]+'</button>'}).join('')+'</div>';
 /* PDF 인쇄본 버튼(대표님 11-13 20:12, 이력 1329): 정관 · 이용약관 및 정책 · 개인정보 처리 탭에서 문서 전체를 PDF로 연다. */
 var PDF20={ch:['정관 초안 0.3 · 8쪽','dl/HIVEN_정관_초안-261113_0.3_작업.pdf'],pl:['HiCoffer 이용약관 1.0','dl/HiCoffer_이용약관-261030_1.0.pdf'],pi:['HiCoffer 개인정보처리방침 1.0','dl/HiCoffer_개인정보처리방침-261030_1.0.pdf']}[T20.tab];
 if(PDF20)h+='<div style="margin:0 0 12px"><a class="hv10-pdf" href="/'+encodeURI(PDF20[1])+'?v=20261113p1" target="_blank" rel="noopener" style="display:inline-block;padding:8px 16px;border-radius:8px;background:#1a2a5e;color:#fff;font-weight:700;text-decoration:none;white-space:nowrap">PDF 인쇄본</a> <span class="note" style="margin-left:8px;white-space:nowrap">'+E(PDF20[0])+'</span></div>';
 var lines=me.r.length+be.r.length;
 h+='<p class="note"><b>맞물림</b> 회원 한 줄 · 설치 한 줄 → 동의한 약관 판(PL 번호) · 개인정보 묶음(PI 번호). 지금 회원 '+me.r.length+'명 · 베타 설치 기록 '+be.r.length+'건'+(lines?' · 어긋남 '+miss.length+'건':' — 맞물림을 볼 줄이 아직 없습니다(베타 배포 전)')+'.</p>';
 if(T20.tab==='ch')h+=charter(ch,cp);
 else if(T20.tab==='pl')h+='<h3>이용약관 및 정책</h3>'+tbl(pl.h.map(E),rows(pl))+src(['policy_list.tsv'],'tools/gen_ext.py','44_HIVEN_이용약관_정책(PCY)\\44_10_관리');
 else if(T20.tab==='mem')h+='<h3>회원관리</h3>'+tbl(me.h.map(E),rows(me))+(me.r.length?'':'<p class="note">회원 0명(베타 배포 전). 가입이 생기면 회원 한 줄마다 동의한 약관 판(PL)과 개인정보 묶음(PI)을 적습니다.</p>')+src(['member_ledger.tsv'],'tools/gen_ext.py','44_HIVEN_이용약관_정책(PCY)\\44_21_회원관리');
 else if(T20.tab==='beta')h+='<h3>무료 베타 버전 관리</h3>'+tbl(be.h.map(E),rows(be))+(be.r.length?'':'<p class="note">베타 설치 기록 0건(0.1.27에는 바깥으로 보내는 기능이 없음). 설치 기록이 생기면 한 줄마다 기기 · 저장 매체와 동의한 약관 판(PL) · 개인정보 묶음(PI)을 적습니다. 카드 번호는 두지 않습니다.</p>')+src(['beta_ledger.tsv'],'tools/gen_ext.py','44_HIVEN_이용약관_정책(PCY)\\44_22_무료_베타_버전_관리');
 else h+='<h3>개인정보 처리</h3>'+tbl(pi.h.map(E),rows(pi))+'<p class="note">DR-19: 개인정보가 든 문서 · 기록은 이 대장에 한 줄이 있고 보유 기간 · 파기 방법 · 방침의 근거 조항이 적혀 있어야 합니다. 문서 생애 절차의 보존(L6) · 파기(L7)는 이 대장의 보유 기간을 따릅니다.</p>'+src(['pip_ledger.tsv'],'tools/gen_ext.py','44_HIVEN_이용약관_정책(PCY)\\44_20_개인정보_처리');
 return h}
window.hv10Tab20=function(t){T20.tab=t;redraw()};
/* 정관 탭(대표님 19:35, 이력 1318): 요약 버튼 넷(정관 판 · 목적 사업 · 등록·신고가 필요한 사업 · 묶음 수, 누르면 그 표) + 정관 대장 + 목적 사업 표.
   목적 사업 표만 항 번호순(1→40), 한 쪽 15줄 쪽 넘김, 묶음 버튼으로 거름. 원천 charter_ledger.tsv · charter_purpose.tsv(Fable 작성 대장) */
var CP_PG=15;
function cpNo(r){return +String(r[0]).replace(/\D/g,'')||0}
function cpTbl(h,L,pg,n){var a=pg*CP_PG,s='<div class="tw hv10-cp"><table><thead><tr>'+h.map(function(x){return '<th>'+E(x)+'</th>'}).join('')+'</tr></thead><tbody>'+L.slice(a,a+CP_PG).map(function(r){return '<tr>'+h.map(function(_,i){return '<td>'+E(r[i]==null?'':r[i])+'</td>'}).join('')+'</tr>'}).join('')+'</tbody></table></div>';
 var b='';for(var j=0;j<n;j++)b+='<button type="button" class="'+(j===pg?'on':'')+'" onclick="hv10Cp('+j+')">'+(j+1)+'</button>';
 return s+'<div class="hv-pg"><button type="button" class="hv-pg-a" '+(pg<=0?'disabled':'')+' onclick="hv10Cp('+(pg-1)+')">◀ 이전</button>'+b+'<button type="button" class="hv-pg-a" '+(pg>=n-1?'disabled':'')+' onclick="hv10Cp('+(pg+1)+')">다음 ▶</button><span class="hv-pg-i">'+(pg+1)+'/'+n+'쪽 · '+(a+1)+'~'+Math.min(L.length,a+CP_PG)+' / 전체 '+L.length+'항 · 한 쪽 '+CP_PG+'줄</span></div>'}
function charter(ch,cp){var gi=col(cp,'묶음'),pi=col(cp,'하기 전에'),vi=col(cp,'판'),G=[],all=cp.r.slice().sort(function(a,b){return cpNo(a)-cpNo(b)});
 all.forEach(function(r){if(G.indexOf(r[gi])<0)G.push(r[gi])});if(T20.cg&&G.indexOf(T20.cg)<0)T20.cg='';
 var reg=all.filter(function(r){var v=String(r[pi]==null?'':r[pi]).trim();return v&&v!=='-'}),ver=ch.r.filter(function(r){return /정관/.test(r[1]||'')}).map(function(r){return r[2]})[0]||((all[0]||[])[vi])||NA;
 var L=T20.cg?all.filter(function(r){return r[gi]===T20.cg}):all,n=Math.max(1,Math.ceil(L.length/CP_PG));if(T20.cp>=n)T20.cp=n-1;if(T20.cp<0)T20.cp=0;
 var h='<h3>정관</h3><div class="grid">'+card('정관 판',E(ver),'정관 대장 '+ch.r.length+'줄',null,function(){return tbl(ch.h.map(E),rows(ch))})
  +card('목적 사업',all.length+'항','항 번호순',null,function(){return tbl(cp.h.map(E),rows({h:cp.h,r:all}))})
  +card('등록·신고가 필요한 사업',reg.length+'건','하기 전 절차가 있는 항',null,function(){return tbl(cp.h.map(E),rows({h:cp.h,r:reg}))})
  +card('묶음',G.length+'묶음','목적 사업 묶음',null,function(){return tbl(['묶음','항 수','등록·신고 필요'],G.map(function(g){return [E(g),all.filter(function(r){return r[gi]===g}).length,reg.filter(function(r){return r[gi]===g}).length]}))})+'</div>';
 h+='<h3>정관 대장</h3>'+tbl(ch.h.map(E),rows({h:ch.h,r:ch.r.slice().reverse()}))+(ch.r.length?'':'<p class="note">정관 대장 0건'+(ch.none?' — 원천 cowork/ctl/charter_ledger.tsv가 아직 게시되지 않았습니다':'')+'.</p>');
 h+='<h3>정관 목적 사업 ('+(T20.cg?E(T20.cg)+' · '+L.length+'항':'전체 '+all.length+'항')+' · 항 번호순)</h3><div style="margin:6px 0 8px">'+[''].concat(G).map(function(g){var on=T20.cg===g;return '<button type="button" class="tab'+(on?' on':'')+'" data-cg="'+E(g)+'" onclick="hv10Cg(this.getAttribute(\'data-cg\'))" style="margin:0 6px 6px 0;padding:5px 10px;border:1px solid #c5cde0;border-radius:8px;background:'+(on?'#1a2a5e':'#fff')+';color:'+(on?'#fff':'#1a2a5e')+';cursor:pointer;white-space:nowrap;max-width:100%;overflow:hidden;text-overflow:ellipsis">'+(g?E(g):'전체')+'</button>'}).join('')+'</div>';
 h+=(all.length?cpTbl(cp.h,L,T20.cp,n):tbl(cp.h.map(E),[])+'<p class="note">목적 사업 0항'+(cp.none?' — 원천 cowork/ctl/charter_purpose.tsv가 아직 게시되지 않았습니다':'')+'.</p>');
 return h+src(['charter_ledger.tsv','charter_purpose.tsv'],'Fable 작성 대장(만드는 도구 없음)','44_HIVEN_이용약관_정책(PCY)\\44_11_정관')}
window.hv10Cg=function(g){T20.cg=g||'';T20.cp=0;redraw()};
window.hv10Cp=function(i){T20.cp=i;redraw()};
V['SC-20']=function(){load('hv10-20',F20,function(D){T20.D=D;return draw20()});
 return head('SC-20','이용약관 및 정책','고객 지원(SC-01)의 바탕인 정관 · 이용약관 · 정책을 탭 다섯(정관 · 이용약관 및 정책 · 회원관리 · 무료 베타 버전 관리 · 개인정보 처리)으로 봅니다. 회원 한 줄 · 설치 한 줄이 동의한 약관 판(PL)과 개인정보 묶음(PI)을 가리켜 넷이 번호로 맞물립니다.')+flow('SC-20')+'<div id="hv10-20" class="hv-nosw">읽는 중…</div>'};

/* ───── SC-21 계약 (대표님 19:22 지시: 계약은 열 갈래 = 사업군 일곱 · HIVEN 통합 · HIVE 그룹 · HIVE 홀딩스.
   화면 위에 열 갈래 요약 버튼, 누르면 그 갈래의 계약 표. 갈래 원천 cowork/ctl/ctr_category.tsv(Fable 작성 대장) · 계약 원천 ext_contract.tsv(tools/gen_ext.py)) ───── */
var F21=['ext_contract.tsv','ctr_category.tsv'],T21={g:null,D:null};
/* 계약 한 줄이 어느 갈래인가: 「갈래」 칸이 있으면 그 칸, 없으면 줄 안에 갈래 번호(CT-xx)나 계약 폴더 이름이 있는지로 가른다(지어 넣지 않음) */
function c21of(c,k,r){var gi=col(c,'갈래'),txt=gi>=0?String(r[gi]||''):r.join('\t'),ni=col(k,'갈래 번호'),gn=col(k,'갈래'),fi=col(k,'계약 폴더');
 for(var i=0;i<k.r.length;i++){var x=k.r[i];if((x[ni]&&txt.indexOf(x[ni])>=0)||(fi>=0&&x[fi]&&txt.indexOf(x[fi])>=0)||(gi>=0&&x[gn]&&txt.trim()===x[gn]))return x[ni]}return null}
function draw21(){var D=T21.D;if(!D)return '';var c=D[0],k=D[1],ni=col(k,'갈래 번호'),gn=col(k,'갈래'),ci=col(k,'계약 건수'),si=col(k,'상태'),ki=col(c,'기간'),na=naCells(c),al=[];
 var by={},none=[];c.r.forEach(function(r){var g=c21of(c,k,r);if(g)(by[g]=by[g]||[]).push(r);else none.push(r)});
 var exp=c.r.filter(function(r){var d=days(String(r[ki]||'').split(/~|∼/).pop());return d!==null&&d>=0&&d<=30});
 var mis=k.r.filter(function(x){return String(+x[ci])!==String((by[x[ni]]||[]).length)});
 if(exp.length)al.push('만료 30일 안 '+exp.length+'건: '+exp.map(function(r){return E(r[0])}).join(' · '));
 if(none.length)al.push('갈래를 가를 수 없는 계약 '+none.length+'건: '+none.map(function(r){return E(r[0])}).join(' · ')+' — 계약 대장 줄에 갈래 번호(CT-xx)를 적음');
 if(mis.length)al.push('갈래 대장의 계약 건수와 계약 대장 줄 수가 다른 갈래 '+mis.length+'개: '+mis.map(function(x){return E(x[ni]+' '+x[gn]+' '+x[ci]+'≠'+(by[x[ni]]||[]).length)}).join(' · '));
 if(na.length)al.push('「'+NA+'」으로 남은 기준 '+na.length+'칸: '+E(naList(na)));
 var h='<div class="grid">'+card('맺은 계약',c.r.length+'건',c.r.length?'원천 대장 기준':'맺은 계약 없음(0건)',null,function(){return tbl(c.h.map(E),rows(c))})
  +card('계약 갈래',k.r.length+'갈래','사업군 일곱 · 통합 · 그룹 · 홀딩스',null,function(){return tbl(k.h.map(E),rows(k))})
  +card('만료 30일 안',exp.length+'건',exp.length?tag('갱신 결재','bad'):tag('없음','ok'))
  +card('앞선 협의','SC-19','협의 · SLA · MOU','SC-19')+'</div>';
 h+=alertBox(al);
 h+='<h3>계약 갈래 (열 갈래 · 누르면 그 갈래의 계약 표)</h3><style>.hv10-cg{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;margin:8px 0 12px}@media (max-width:640px){.hv10-cg{grid-template-columns:repeat(2,minmax(0,1fr))}}</style><div class="hv10-cg">'
  +k.r.map(function(x){var on=T21.g===x[ni],n=(by[x[ni]]||[]).length;return '<button type="button" class="hv10-cgb'+(on?' on':'')+'" onclick="hv10Ct(\''+E(x[ni])+'\')" style="text-align:left;padding:8px 10px;border:1px solid '+(on?'#16234d':'#c5cde0')+';border-radius:9px;background:'+(on?'#16234d':'#fff')+';color:'+(on?'#fff':'#1a2a5e')+';cursor:pointer;min-width:0">'
   +'<div style="font-size:11.5px;opacity:.8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'+E(x[ni])+' · '+E(x[col(k,'구분')])+'</div><div style="font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'+E(x[gn])+'</div><div style="font-size:12px;white-space:nowrap">'+n+'건</div></button>'}).join('')+'</div>';
 var g=T21.g&&k.r.filter(function(x){return x[ni]===T21.g})[0];
 if(!g)h+='<h3>계약 대장 전체 (최신순 · '+c.r.length+'건)</h3>'+tbl(c.h.map(E),rows({h:c.h,r:c.r.slice().reverse()}))+'<p class="note">'+(c.r.length?'':'맺은 계약 0건. ')+'갈래 버튼을 누르면 그 갈래의 계약 표만 봅니다.</p>';
 else{var L=(by[g[ni]]||[]).slice().reverse();
  h+='<h3>'+E(g[ni]+' '+g[gn])+' 계약 (최신순)</h3>'+tbl(['항목','값'],k.h.map(function(x,i){return [E(x),E(g[i])]}).filter(function(x,i){return i!==ni&&i!==gn}))
   +tbl(c.h.map(E),rows({h:c.h,r:L}))+(L.length?'':'<p class="note">'+E(g[gn])+' 계약 0건 ('+E(g[si]||NA)+'). 협의가 끝나면 SC-19의 줄은 그대로 두고 계약 대장에 새 줄을 만들어 갈래 번호 '+E(g[ni])+'와 PT · SLA 번호로 잇습니다.</p>')}
 if(none.length)h+='<h3>갈래를 가를 수 없는 계약</h3>'+tbl(c.h.map(E),rows({h:c.h,r:none.slice().reverse()}));
 return h+src(F21,'tools/gen_ext.py(계약 대장) · Fable 작성 대장(갈래, 만드는 도구 없음)','43_HIVEN_계약(CTR)')}
window.hv10Ct=function(g){T21.g=(T21.g===g?null:g);redraw()};
V['SC-21']=function(){load('hv10-21',F21,function(D){T21.D=D;return draw21()});
 return head('SC-21','계약','계약을 열 갈래(사업군 일곱 · HIVEN 통합 · HIVE 그룹 · HIVE 홀딩스)로 나눠 계약 업체 · 계약서 · 기간 · 갱신 · 조건을 봅니다.')+flow('SC-21')+'<div id="hv10-21" class="hv-nosw">읽는 중…</div>'};

/* ───── SC-09 배포 모니터링(대표님 18:56 · 19:06 지시): 플랫폼 넷 × 베타 · 상용화 여덟 칸 판 → 칸을 누르면 그 플랫폼 상세(베타는 베타1 · 2 · 3 탭, 상용화는 별도 탭).
   판의 값은 cowork/ctl/deploy_matrix.tsv에서만 읽는다. 지금 있는 베타1 관문 · 사건 표(views6.js SC-09b1)는 「PC › 베타 › 베타1」 상세로 내림 ───── */
var D9={M:null,p:null,st:null},PF=['PC (Windows 10·11)','Android','macOS','iPhone'];
function m9rows(){var M=D9.M;if(!M)return [];var pi=col(M,'플랫폼'),gi=col(M,'갈래'),si=col(M,'단계');return M.r.map(function(r){return {p:r[pi],g:/상용/.test(r[gi])?'상용화':'베타',st:r[si],r:r}})}
function m9pick(list){for(var i=0;i<list.length;i++)if(!/^준비 전/.test(list[i].r[col(D9.M,'상태')]||''))return list[i];return list[0]}
function m9cell(p,g){var L=m9rows().filter(function(x){return x.p===p&&x.g===g}),M=D9.M,vi=col(M,'판'),ti=col(M,'상태'),x=L.length?m9pick(L):null,on=D9.p===p&&x&&D9.st===x.st;
 var st=x?(x.r[ti]||NA):'준비 전',ready=/^준비 전/.test(st)||!x;
 return '<button type="button" class="hv10-dm'+(on?' on':'')+'" onclick="hv10Dm(\''+E(p).replace(/'/g,"\\'")+'\',\''+(x?E(x.st):'')+'\')" style="text-align:left;padding:8px 10px;border:1px solid '+(ready?'#c5cde0':'#2a52be')+';border-radius:9px;background:'+(on?'#16234d':ready?'#f5f7fb':'#fff')+';color:'+(on?'#fff':'#1a2a5e')+';cursor:pointer;min-width:0">'
  +'<div style="font-size:11.5px;opacity:.8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'+E(p)+'</div><div style="font-weight:800">'+g+(x&&g==='베타'?' · '+E(x.st):'')+'</div>'
  +'<div style="font-size:12px">판 '+(x?E(x.r[vi]||NA):NA)+'</div><div style="font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'+(ready?tag('준비 전','gray'):tag(E(st),'warn'))+'</div></button>'}
function m9detail(){var p=D9.p;if(!p)return '<p class="note">칸을 누르면 그 플랫폼의 상세(베타는 베타1 · 2 · 3 탭, 상용화는 별도 탭)가 열립니다.</p>';
 var L=m9rows().filter(function(x){return x.p===p}),M=D9.M,cur9=L.filter(function(x){return x.st===D9.st})[0]||L[0];if(!cur9)return '<p class="note">'+E(p)+' 줄이 원천에 없습니다.</p>';
 var h='<h3>'+E(p)+' › '+cur9.g+(cur9.g==='베타'?' › '+E(cur9.st):'')+'</h3><div style="margin:6px 0 10px">'+L.map(function(x){var on=x===cur9;return '<button type="button" class="tab'+(on?' on':'')+'" onclick="hv10Dm(\''+E(p).replace(/'/g,"\\'")+'\',\''+E(x.st)+'\')" style="margin:0 6px 6px 0;padding:6px 12px;border:1px solid #c5cde0;border-radius:8px;background:'+(on?'#1a2a5e':'#fff')+';color:'+(on?'#fff':'#1a2a5e')+';cursor:pointer;white-space:nowrap">'+E(x.st)+'</button>'}).join('')+'</div>';
 h+=tbl(M.h.map(E),[M.h.map(function(_,i){return E(cur9.r[i]==null?'':cur9.r[i])})]);
 var src9=cur9.r[col(M,'관문·사건 원천')]||'';
 if(/deploy_beta1_gates/.test(src9)&&typeof V['SC-09b1']==='function')h+=V['SC-09b1']();
 else h+='<p class="note">'+(/^준비 전/.test(cur9.r[col(M,'상태')]||'')?'준비 전 — ':'')+'이 칸의 관문 · 사건 원천이 아직 없습니다(deploy_matrix.tsv 「관문·사건 원천」 칸 '+E(src9||'-')+'). 원천이 생기면 이 자리에 관문 · 배포 뒤 사건을 보입니다.</p>';
 return h}
function draw09(){if(!D9.M)return '';var M=D9.M,ti=col(M,'상태'),act=M.r.filter(function(r){return !/^준비 전/.test(r[ti]||'')}).length;
 var h='<div class="grid">'+card('플랫폼 × 갈래','8칸','플랫폼 넷 × 베타 · 상용화')+card('진행 중인 칸',act+'칸',act?'준비 전 아닌 단계':'모두 준비 전')+card('원천 줄',M.r.length+'줄','deploy_matrix.tsv')+'</div>';
 h+='<style>.hv10-dmg{display:grid;grid-template-rows:repeat(2,auto);grid-auto-flow:column;grid-auto-columns:minmax(0,1fr);gap:8px;margin:8px 0 12px}@media (max-width:640px){.hv10-dmg{grid-template-rows:none;grid-auto-flow:row;grid-template-columns:repeat(2,minmax(0,1fr))}}</style>';
 h+='<div class="hv10-dmg">'+PF.map(function(p){return m9cell(p,'베타')+m9cell(p,'상용화')}).join('')+'</div>';
 h+='<div id="hv10-09d">'+m9detail()+'</div>';
 return h}
window.hv10Dm=function(p,st){D9.p=p;D9.st=st;redraw()};
V['SC-09']=function(){load('hv10-09',['deploy_matrix.tsv'],function(D){D9.M=D[0];return draw09()});
 var fl=[['SC-08','체계 및 시스템/서비스'],['SC-09','배포 모니터링'],['SC-20','무료 베타 버전 관리 · 회원관리'],['SC-02','종합 현황'],['SC-00','대표님 결재'],['SC-15','문서 자동 생성']];
 return '<h2>SC-09 배포 모니터링</h2><p class="lead">HiCoffer를 플랫폼 넷(PC · Android · macOS · iPhone) × 베타 · 상용화로 나눠 봅니다. 칸을 누르면 그 플랫폼의 상세가 열립니다.</p><div id="hv10-09" class="hv-nosw">읽는 중…</div>'
  +'<p class="note hv10-flow"><b>흐름</b> '+fl.map(function(x,i){return '<button type="button" onclick="hvgo(\''+x[0]+'\')" style="margin:2px;padding:2px 9px;border:1px solid #9fb0cf;border-radius:7px;background:'+(i===1?'#e3ecfa':'#fff')+';cursor:pointer;white-space:nowrap"><b>'+x[0]+'</b> '+x[1]+'</button>'}).join(' → ')+'</p>'
  +src(['deploy_matrix.tsv'],'Fable 작성 대장(만드는 도구 없음)','12_HIVEN_HiCoffer\\12_08_시범테스트')};

/* ───── 원천 미연결 화면 이음 ───── */
var OLD='옛 값(2026-11-04 옮겨 적음)';
function oldTag(){return tag('옮겨 적은 옛 값','gray')}
/* SC-03: 맨 위에 지금 발령 단계와 근거(어느 기록에서) · 서버 기준 단계 · 원천 표기 */
if(V['SC-03']){var o03=V['SC-03'];V['SC-03']=function(){var g=String(o03.apply(this,arguments)),l=(typeof hvEmLevel==='function')?hvEmLevel():null,n=null;try{n=(JSON.parse(localStorage.getItem('hvsec')||'{}').n)||0}catch(e){n=null}
 var top='<h3>지금 발령 단계와 근거</h3>'+tbl(['기준','단계','근거(원천)','상태'],[
   ['이 기기',l===null?NA:'단계 '+l,'이 브라우저 저장소 「hvsec」의 열쇠 오류 수'+(n===null?'':' '+n+'회')+' (sec2.js 계산식)',l===null?tag(NA,'gray'):tag('이 기기 기록만','warn')],
   ['서버 기준',NA,'ic 서버 침입 기록의 저장소 사본(cowork/ctl/sec_log.tsv · sec_level.tsv) 없음',tag('서버 기준 단계 확인 안 됨','bad')]])
  +'<p class="note">다른 기기에서 난 침입과 서버만 받은 이상 접속은 아직 단계에 들어가지 않습니다(서버 기록 사본을 만드는 도구 전). 침입 기록 자세히: <button type="button" onclick="hvgo(\'SC-04\')" style="padding:2px 9px;border:1px solid #9fb0cf;border-radius:7px;background:#fff;cursor:pointer"><b>SC-04</b> 침입 예측·예방·대응·조치</button></p>'
  +'<p class="note"><b>원천</b> 발령 단계 = 이 기기 브라우저 저장소(서버 값 아님) · 매뉴얼 7종 = cowork/ctl/manuals.json(tools/gen_views8.py가 views8.js에 구워 넣음) · 체계 표 = 코드 안 값(views7.js hvEM, 원천 파일 없음) · 흐름 SC-03 → SC-02 → SC-00(단계 6 이상) → SC-15</p>';
 g=g.replace('대응·경보 · 체계 배포 · 베타 배포 모니터링','대응·경보 · 체계 및 시스템/서비스 · 배포 모니터링');/* 대표님 19:06 · 19:08 이름 바꿈(views8.js 위계 안내 글) */
 var i=g.indexOf('</h2>');return i>=0?g.slice(0,i+5)+top+g.slice(i+5):top+g}}

/* SC-08 체계 및 시스템/서비스(대표님 19:08 이름 · 19:09 내용): 서비스의 바탕(체계 · 시스템 · 앱 · 협업 프로그램)을 cowork/ctl/svc_base.tsv에서만 읽는다.
   갈래 단추로 전환, 작업본 판이 있으면 「작업본 승인 대기」, 「독립 화면」 줄은 그 화면으로 가는 길. 앞의 분류·규칙 문서 판 표(views5.js · aics_deploy.tsv)는 「체계」 갈래 아래에 그대로 둔다 */
var o08=V['SC-08'],D8={tab:null,d:null};
/* 대표님 19:31(이력 1317): 묶음 순서 고정 — 조직 · 체계 · 시스템 · 앱 · 협업 프로그램. 0줄이어도 버튼은 두고 0건. 원천에 이 밖의 묶음이 있으면 뒤에 붙임 */
var G8=['조직','체계','시스템','앱','협업 프로그램'];
function g8(d){var o=G8.slice();d.r.forEach(function(r){if(o.indexOf(r[0])<0)o.push(r[0])});return o}
function t8(d,g){var wi=col(d,'작업본'),si=col(d,'잇는 화면');return tbl(d.h.map(E),d.r.filter(function(r){return r[0]===g}).map(function(r){return d.h.map(function(_,i){var v=E(r[i]==null?'':r[i]);
  if(i===wi&&r[i]&&!/^-?$/.test(r[i].trim()))v+=' '+tag('작업본 승인 대기','warn');
  if(i===si)v=v.replace(/(SC-\d\d)\(독립 화면\)/g,function(_,x){return x+' '+tag('독립 화면','sel')+' <button type="button" onclick="hvgo(\''+x+'\')" style="padding:1px 8px;border:1px solid #9fb0cf;border-radius:7px;background:#fff;cursor:pointer;white-space:nowrap">'+x+'로 가기</button>'});
  return v})}))}
function draw08(){var d=D8.d;if(!d)return '';var G=g8(d);if(!D8.tab||G.indexOf(D8.tab)<0)D8.tab=G[0];var wi=col(d,'작업본');
 var h='<div class="grid">'+G.map(function(g){var n=d.r.filter(function(r){return r[0]===g}),w=n.filter(function(r){return r[wi]&&!/^-?$/.test(r[wi].trim())}).length;return card(E(g),n.length+'건',w?'작업본 승인 대기 '+w+'건':'작업본 없음',null,function(){return t8(d,g)})}).join('')+'</div>';
 h+='<div style="margin:10px 0">'+G.map(function(g){var on=D8.tab===g;return '<button type="button" class="tab'+(on?' on':'')+'" onclick="hv10Tab08(\''+E(g)+'\')" style="margin:0 6px 6px 0;padding:6px 12px;border:1px solid #c5cde0;border-radius:8px;background:'+(on?'#1a2a5e':'#fff')+';color:'+(on?'#fff':'#1a2a5e')+';cursor:pointer;white-space:nowrap">'+E(g)+'</button>'}).join('')+'</div>';
 var n8=d.r.filter(function(r){return r[0]===D8.tab}).length;h+='<h3>'+E(D8.tab)+' ('+n8+'건)</h3>'+t8(d,D8.tab)+(n8?'':'<p class="note">'+E(D8.tab)+' 0건 — 원천 svc_base.tsv에 첫 칸이 「'+E(D8.tab)+'」인 줄이 아직 없습니다.</p>');
 if(D8.tab==='체계'&&o08)h+=String(o08()).replace(/<h2>[\s\S]*?<\/h2>/,'<h3>분류 · 규칙 문서 판(노트북 원천 폴더 HV_STD)</h3>');
 return h+src(['svc_base.tsv'],'Fable 작성 대장(만드는 도구 없음)'+(D8.tab==='체계'?' · 아래 판 표 aics_deploy.tsv(tools/gen_aics_src.py)':''),'')}
window.hv10Tab08=function(g){D8.tab=g;redraw()};
V['SC-08']=function(){load('hv10-08',['svc_base.tsv'],function(D){D8.d=D[0];return draw08()});
 return head('SC-08','체계 및 시스템/서비스','서비스의 바탕이 되는 것(조직 · 체계 · 시스템 · 앱 · 협업 프로그램)을 다섯 묶음으로 모아 봅니다. 작업본 판이 있으면 승인 대기로 표시합니다.')+flow('SC-08')+'<div id="hv10-08" class="hv-nosw">읽는 중…</div>'};

/* SC-06: HVR 값은 지어내지 않고 「옮겨 적은 옛 값」과 잰 때를 붙인다. 지금 구동은 원천(run_signal.tsv)이 없어 「확인 안 됨」 */
if(typeof HVR!=='undefined'){
V['SC-06']=function(){
 var g='<h2>SC-06 구동 상태</h2><p class="lead">HiClo.app · HIVEN.app · AICS가 실제로 돌고 있는지 봅니다. 구동 신호 원천(cowork/ctl/run_signal.tsv)이 아직 없어 지금 구동은 「'+NA+'」이고, 아래 값은 '+HVR.chk+'에 노트북 원천을 보고 코드에 옮겨 적은 옛 값입니다.</p>';
 g+='<div class="grid">'+card('HiClo.app 지금 구동',NA,'마지막 판정 '+HVR.hiclo.last.slice(5,16)+' · '+hvStop(HVR.hiclo.last)+' · '+oldTag())+card('HIVEN.app 지금 구동',NA,'마지막 관계 신호 '+HVR.hiven.last.slice(5,16)+' · '+oldTag())+card('AICS',NA,'정지·재개 원천 없음')+'</div>';
 g+=tbl(['대상','지금 구동','마지막 신호(옛 값)','잰 때','원천'],[
  ['HiClo.app',tag(NA,'gray'),E(HVR.hiclo.last)+' · '+E(HVR.hiclo.verdict)+' · '+hvStop(HVR.hiclo.last),E(HVR.chk)+' '+E(HVR.by),E(HVR.src)+' '+oldTag()],
  ['HIVEN.app',tag(NA,'gray'),E(HVR.hiven.last),E(HVR.chk)+' '+E(HVR.by),E(HVR.hiven.note)+' '+oldTag()],
  ['AICS',tag(NA,'gray'),NA,'-','원천 없음']]);
 g+='<h3>저장 주기('+OLD+')</h3>'+tbl(['구분','값','원천'],[['설정',HVR.save.period+'분 ('+HVR.save.setAt+' 설정)',E(HVR.save.src)+' '+oldTag()],['예약',E(HVR.save.sched),'같은 파일 '+oldTag()],['실제 적용 여부',tag(NA,'gray'),'적용 기록 없음']]);
 g+='<h3>작업 대기열 마지막 결과('+OLD+')</h3>'+tbl(['작업','끝난 시각','결과','원천'],[[E(HVR.job.id),E(HVR.job.end),'종료 코드 '+HVR.job.rc+' '+oldTag(),E(HVR.job.src)]]);
 g+='<p class="note"><b>원천</b> 코드 안 값 views0.js HVR(잰 때 '+HVR.chk+' · '+HVR.by+' · 노트북 HiClo 판정 파일을 보고 옮겨 적음, '+hvChkAge()+') · 구동 신호 원천 cowork/ctl/run_signal.tsv 없음 → 지금 구동 「'+NA+'」 · HiClo 판정 원천 정지는 경보 AL-001(SC-07) · 흐름 SC-06 → SC-02 → SC-00 → SC-15</p>';
 return g+hvChk()};

/* SC-07: 경보 원장(alerts.tsv)을 위로 — 미조치 · 조치 중 · 해제 · 규칙별 건수. HVR 4줄은 옛 값으로 접어 둔다 */
V['SC-07']=function(){
 var g='<h2>SC-07 대응·경보</h2><p class="lead">모든 경보를 한 원장(cowork/ctl/alerts.tsv)으로 모아 규칙(CR) · 등급 · 조치 상태로 봅니다.</p>';
 var A=(typeof hvMeta!=='undefined')?hvMeta.al:null;
 if(A&&A.r){var si=col(A,'상태'),ri=col(A,'규칙'),cnt=function(re){return A.r.filter(function(r){return re.test(r[si]||'')}).length},nU=cnt(/미조치/),nI=cnt(/조치 중/),nD=A.r.length-nU-nI,by={};A.r.forEach(function(r){var k=r[ri]||NA;by[k]=(by[k]||0)+1});
  g+='<div class="grid">'+card('미조치',nU+'건',nU?tag('조치 필요','bad'):tag('없음','ok'))+card('조치 중',nI+'건','alerts.tsv')+card('해제 · 조치 완료',nD+'건','alerts.tsv')+card('규칙',Object.keys(by).length+'가지','CR 번호별',null,function(){return tbl(['규칙','건수'],Object.keys(by).sort().map(function(k){return [E(k),by[k]]}))})+'</div>';
  g+='<h3>규칙별 건수</h3>'+tbl(['규칙','건수'],Object.keys(by).sort().map(function(k){return [E(k),by[k]]}));
 }else g+='<div class="grid">'+card('경보 원장',hvMeta&&hvMeta.t?NA:'불러오는 중','cowork/ctl/alerts.tsv')+'</div>';
 g+=hvAlertLedger();
 g+='<details style="margin:12px 0"><summary style="cursor:pointer;font-weight:700">'+OLD+' — 2026-11-03 HiClo 판정 경보 4줄 · 클로 단계</summary>'
  +'<div class="grid">'+card('클로 단계',E(HVR.hiclo.stage),'판정 '+HVR.hiclo.last.slice(5,16)+' · '+oldTag())+card('대응 모드',NA,'원천 없음')+'</div>'
  +tbl(['시각','심각도','대상','내용','원천'],HVR.issues.map(function(r){return [r[0].slice(5),tag(r[1],r[1]==='경고'?'warn':'gray'),E(r[2]),E(r[3]),oldTag()]}))
  +'<p class="note">이 줄들은 HiClo 판정 파일 값을 '+HVR.chk+'에 코드(views0.js HVR)에 옮겨 적은 옛 값입니다. 지금 경보는 위 원장에 쌓입니다(AL-001 HiClo 원천 정지).</p></details>';
 g+='<p class="note"><b>원천</b> cowork/ctl/alerts.tsv(만드는 도구 tools/gen_alerts.py · 페이지가 열릴 때와 30초마다 미리 읽음, views0.js hvMetaLoad) · 접힌 표는 코드 안 옛 값(HVR) · 흐름 SC-07 → SC-02 → SC-00 → SC-15</p>';
 return g+hvChk()};

/* SC-11: 노트북 원천 세 줄은 옛 값 표시, 게시 원천은 publish_meta.json, 원천 신선도 표는 source_freshness.tsv(손으로 쓰는 원천)를 열 때 한 번 읽음 */
V['SC-11']=function(){
 var g='<h2>SC-11 수집·연동</h2><p class="lead">원천마다 마지막으로 언제 들어왔는지 봅니다 — 「이 데이터가 왜 안 들어와 있지」를 찾는 화면입니다.</p>';
 g+=tbl(['원천','마지막 수신','상태','확인'],[
  ['노트북 HiClo 판정 파일',E(HVR.hiclo.last),tag('끊김','bad')+' '+hvStop(HVR.hiclo.last),OLD+' · '+oldTag()],
  ['HIVEN.app 관계 신호',E(HVR.hiven.last),tag(NA,'gray'),OLD+' · '+oldTag()],
  ['작업 대기열 결과',E(HVR.job.end),tag('끊김','bad')+' 이후 결과 없음',OLD+' · '+oldTag()],
  ['모델 통제 이력(SC-16)','게시본','10초마다 읽음(views3.js)','게시본 model_control_history.tsv'],
  ['통합사업 작업상황(SC-10)','게시본','30초마다 읽음(views2.js)','게시본 progress.json'],
  ['HiCoffer Cloud 묶음(IF-4 · IF-5)',tag(NA,'gray'),tag('원천 없음','bad')+' 수신 경로 구현 전','자리만']]);
 g+='<p class="note">노트북 원천 세 줄은 '+HVR.chk+'에 코드(views0.js HVR)에 옮겨 적은 옛 값입니다('+hvChkAge()+'). 지금 수신 여부는 그 원천을 다시 잴 때까지 「'+NA+'」입니다.</p>';
 g+=hvMetaTbl();
 g+='<h3>원천 신선도(저장소 파일별 마지막 갱신)</h3><div id="hv10-11">읽는 중…</div>';
 load('hv10-11',['source_freshness.tsv'],function(D){var d=D[0];return tbl(d.h.map(E),rows(d))+'<p class="note">원천 cowork/ctl/source_freshness.tsv '+d.r.length+'줄 · '+tag('손으로 쓰는 원천','warn')+' 만드는 도구 없음(이음 설계 7절 gen_freshness.py 전) · 화면을 열 때 한 번 읽음</p>'});
 g+='<p class="note"><b>원천</b> cowork/publish_meta.json(만드는 도구 tools/gen_meta.py · 페이지가 열릴 때와 30초마다 미리 읽음, views0.js hvMetaLoad) · cowork/ctl/source_freshness.tsv · 위 표 노트북 세 줄은 코드 안 옛 값(HVR) · 흐름 SC-11 → SC-02 → SC-00 → SC-15</p>';
 return g+hvChk()};
}

/* 늦게 붙는 이음(sec.js가 뒤에 읽혀 SC-04를 정의하므로 페이지를 다 읽은 뒤 감쌈). SC-04의 열쇠 판정 · 잠금 · 경보 · 서버 호출은 그대로 두고 원천 표기만 맨 위에 더한다 */
function hvV10Late(){if(typeof hvIsTest==='function'&&hvIsTest())return;var o04=V['SC-04'];if(!o04||o04._v10)return;
 V['SC-04']=function(){var g=String(o04.apply(this,arguments));
  var top='<p class="note"><b>원천</b> 통합 경보 = ic.hiven.ai.kr 서버 침입 기록(/__sec/list, 화면을 열 때 · 통합관제 로그인 상태에서만) · 단말 경보 = 이 브라우저 저장소 「hvsec」 · 신뢰 기기 = ic 서버 등록부(/__dev/list) · 저장소 사본(cowork/ctl/sec_log.tsv · trusted_devices.tsv) 없음 → '+tag('서버 기준 단계 확인 안 됨','bad')+' · 흐름 SC-04 → SC-03 → SC-02 → SC-00 → SC-15</p>';
  var i=g.indexOf('</h2>');return i>=0?g.slice(0,i+5)+top+g.slice(i+5):top+g};V['SC-04']._v10=1;
 if(typeof cur!=='undefined'&&cur==='SC-04'&&typeof render==='function'&&document.getElementById('main')&&document.getElementById('main').innerHTML)render(cur)}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',hvV10Late);else hvV10Late();
})();
