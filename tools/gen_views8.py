# -*- coding: utf-8 -*-
"""manuals.json + 작업 전개표 → views8.js (SC-02 뒤에 독립 매뉴얼 7종·비상체계·벤치마킹·작업 전개표를 덧붙인다)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import man_src, man_work
d = man_src.build()
d['work'] = dict(essence=man_work.ESSENCE, rows=man_work.W)
d['renum'] = json.load(open(os.path.join(HERE, '..', 'cowork', 'ctl', 'sc_renumber_261107.json'), encoding='utf-8'))
json.dump(d, open(os.path.join(HERE, '..', 'cowork', 'ctl', 'manuals.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
js = '/* 독립 대응 매뉴얼 7종·비상체계·벤치마킹·작업 전개표 (tools/gen_views8.py 로 생성, 직접 고치지 않는다) */\nvar hvMAN=' + json.dumps(d, ensure_ascii=False) + ';\n'
js += r'''(function(){
var o16=V['SC-02'];if(!o16)return;
function T(h,r){return tbl(h,r)}/* 261111 M-3: 공통 부품 tbl(한 쪽 5줄 · 쪽 넘김) */
/* 261111 H-5: 매뉴얼 코드 M1~M7은 화면에서 「MN-1~MN-7」로 적는다(S14 관제 등급 M0~M3과 글자 겹침 방지). 자료 열쇠(code)·파일 이름은 그대로, 보이는 글자만 바꾼다 */
function mn(s){return String(s).replace(/(^|[^A-Za-z0-9\-])M([1-7])(?![0-9A-Za-z])/g,'$1MN-$2')}
V['SC-02']=function(){
 var o0=o16(),o='',D=hvMAN,i;
 o+='<p class="note"><b>위계</b> 최상위 자동화 통합 통제 시스템 ⊃ <b>SC-02 이상징후 및 보안체계 시스템</b>(최우선) ⊃ <b>SC-03 침입 예측·예방·대응·조치 시스템</b>(SC-02의 하위 실행 시스템). 종합 현황(SC-01) 바로 아래 두 화면이 보안 위계이고, 그 아래는 대표님이 정한 순서(사업군 통제 · 구동 상태 · 대응·경보 · 체계 배포 · 베타 배포 모니터링 · 통합사업 작업상황 · 수집·연동 · 형상·변경 · 검수·품질 · 고객 지원 · 문서 자동 생성 · 모델 통제 상황 · 말 명령)로 SC-04~16에 배열되어 있고, 말 명령이 맨 아래입니다.</p><p class="note"><b>메뉴 번호 안내</b> 대표님 지시(11/07 14:42·14:45·14:50·14:53). 옛 번호 → 새 번호: '+Object.keys(D.renum.map_old_to_new).map(function(k){return k+'→'+D.renum.map_old_to_new[k]}).join(' · ')+'. 11/07 14:42 이전의 이력·기록은 당시 번호 그대로이며 이 대응으로 읽습니다.</p>';
 o+='<h3>현재 발령 단계의 7개 매뉴얼 행동 (실시간)</h3><div id="hvlive" class="note"></div>';
 o+='<h3>독립 대응 매뉴얼 7종 (서비스·고객지원·시스템별, 각각 따로 쓴다)</h3><p class="note">'+D.head['발령권자']+' '+D.head['창구']+' '+D.head['원칙']+'</p>';
 o+=T(['번호','매뉴얼','대상','담당·호출','창구'],D.manuals.map(function(m){return [m.code,m.name,m.target,m.owner,m.channel]}));
 D.manuals.forEach(function(m){
  o+='<h4>'+m.code+' '+m.name+'</h4><p class="note">목적: '+m.purpose+' · 사용 시점: '+m.when+'</p>';
  o+=T(['단계','해야 할 일','안내·응대·보고 문구'],m.steps.map(function(s){return [s.n+' '+s.name,s.do,s.say]}));
  o+='<p class="note"><b>금지·주의</b> '+m.ban.join(' / ')+'</p><p class="note"><b>점검·훈련</b> '+m.drill.join(' / ')+'</p><p class="note"><b>기록 서식</b> '+m.form+'</p>'});
 o+='<h3>종단·횡단 일람 (같은 단계에서 7개 매뉴얼이 동시에 하는 일)</h3><p class="note">종단: 하위 침입 예측·예방·대응·조치(SC-03) → 최우선 이상징후 및 보안체계(SC-02) → 최상위 자동화 통합 통제(대표님 결정). 횡단: 아래 단계별 일람.</p>';
 D.cross.forEach(function(c){o+='<h4>'+c.n+' '+c.name+'</h4><ul>'+c.rows.map(function(r){return '<li><b>'+r.code+'</b> '+r.label+': '+r.do+' ▶ '+r.say+'</li>'}).join('')+'</ul>'});
 o+='<h3>비상체계 가동·해제 기준</h3>';
 for(var k in D.emergency)o+='<h4>'+k+'</h4><ul>'+D.emergency[k].map(function(x){return '<li>'+x+'</li>'}).join('')+'</ul>';
 o+='<h3>확장(B2C → B2B → B2G) 시 보안체계 요구</h3>'+T(['단계','추가되는 요구','보안체계 영향','선행 조건','확인 상태'],D.expand);
 o+='<h3>법정 기한·통지 항목</h3>'+T(['근거','기한·내용','확인 상태'],D.law);
 o+='<h3>조치 후 예측 가능한 피해 → 예방 조치</h3>'+T(['조치','예상되는 피해','예방 조치','근거'],D.damage);
 o+='<h3>후속 요건</h3><ul>'+D.follow.map(function(x){return '<li>'+x+'</li>'}).join('')+'</ul>';
 o+='<h3>사례에서 뽑은 실수와 예방</h3>'+T(['사례','실수','예방','확인 상태'],D.mistakes);
 o+='<h3>벤치마킹 근거</h3>'+T(['출처','핵심','HIVEN 반영','확인 상태'],D.bench);
 o+='<h3>작업 전개표 (본질 → 파생 → 선·후행)</h3><p class="note">'+D.work.essence+'</p>'+T(['번호','구분','작업','선행','후행','상태','증빙'],D.work.rows);
 return o0+mn(o)};
var EM12=['안심','관심','관심','주의','주의','경계','경고','위험','위기','위기'];
function live(){var e=document.getElementById('hvlive');if(!e||!window.hvEmLevel)return;var l=hvEmLevel(),nm=EM12[l-1],D=hvMAN,idx=D.steps.indexOf(nm),h;
 if(nm==='안심'){h='<b>현재 발령: 안심 (평상)</b> — 평상 점검·훈련 항목<ul>'+D.manuals.map(function(m){return '<li><b>'+m.code+'</b> '+m.name+': '+m.drill[0]+'</li>'}).join('')+'</ul>'}
 else{var c=D.cross[idx];h='<b>현재 발령: '+nm+' (단계 '+(idx+1)+' · 대응 모드 '+l+')</b> — 7개 매뉴얼이 지금 해야 할 일<ul>'+c.rows.map(function(r){return '<li><b>'+r.code+'</b> '+r.label+': '+r.do+' ▶ '+r.say+'</li>'}).join('')+'</ul>'}
 e.innerHTML=mn(h)}
setInterval(live,3000);setTimeout(live,300);window.hvManLive=live;
})();
'''
open(os.path.join(HERE, '..', 'views8.js'), 'w', encoding='utf-8').write(js)
print('views8.js', len(js))
