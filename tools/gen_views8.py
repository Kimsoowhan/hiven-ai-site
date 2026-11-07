# -*- coding: utf-8 -*-
"""manuals.json + 작업 전개표 → views8.js (SC-16 뒤에 독립 매뉴얼 7종·비상체계·벤치마킹·작업 전개표를 덧붙인다)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import man_src, man_work
d = man_src.build()
d['work'] = dict(essence=man_work.ESSENCE, rows=man_work.W)
json.dump(d, open(os.path.join(HERE, '..', 'cowork', 'ctl', 'manuals.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
js = '/* 독립 대응 매뉴얼 7종·비상체계·벤치마킹·작업 전개표 (tools/gen_views8.py 로 생성, 직접 고치지 않는다) */\nvar hvMAN=' + json.dumps(d, ensure_ascii=False) + ';\n'
js += r'''(function(){
var o16=V['SC-16'];if(!o16)return;
function T(h,r){return '<table class="tb"><thead><tr>'+h.map(function(x){return '<th>'+x+'</th>'}).join('')+'</tr></thead><tbody>'+r.map(function(c){return '<tr>'+c.map(function(x){return '<td>'+x+'</td>'}).join('')+'</tr>'}).join('')+'</tbody></table>'}
V['SC-16']=function(){
 var o=o16(),D=hvMAN,i;
 o+='<h3>현재 발령 단계의 7개 매뉴얼 행동 (실시간)</h3><div id="hvlive" class="note"></div>';
 o+='<h3>독립 대응 매뉴얼 7종 (서비스·고객지원·시스템별, 각각 따로 쓴다)</h3><p class="note">'+D.head['발령권자']+' '+D.head['창구']+' '+D.head['원칙']+'</p>';
 o+=T(['번호','매뉴얼','대상','담당·호출','창구'],D.manuals.map(function(m){return [m.code,m.name,m.target,m.owner,m.channel]}));
 D.manuals.forEach(function(m){
  o+='<h4>'+m.code+' '+m.name+'</h4><p class="note">목적: '+m.purpose+' · 사용 시점: '+m.when+'</p>';
  o+=T(['단계','해야 할 일','안내·응대·보고 문구'],m.steps.map(function(s){return [s.n+' '+s.name,s.do,s.say]}));
  o+='<p class="note"><b>금지·주의</b> '+m.ban.join(' / ')+'</p><p class="note"><b>점검·훈련</b> '+m.drill.join(' / ')+'</p><p class="note"><b>기록 서식</b> '+m.form+'</p>'});
 o+='<h3>종단·횡단 일람 (같은 단계에서 7개 매뉴얼이 동시에 하는 일)</h3><p class="note">종단: 하위 침입 예측/예방/대응/조치(SC-15) → 최우선 이상징후 및 보안체계(SC-16) → 최상위 자동화 통합 통제(대표님 결정). 횡단: 아래 단계별 일람.</p>';
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
 return o};
var EM12=['안심','관심','관심','주의','주의','경계','경고','위험','위기','위기'];
function live(){var e=document.getElementById('hvlive');if(!e||!window.hvEmLevel)return;var l=hvEmLevel(),nm=EM12[l-1],D=hvMAN,idx=D.steps.indexOf(nm),h;
 if(nm==='안심'){h='<b>현재 발령: 안심 (평상)</b> — 평상 점검·훈련 항목<ul>'+D.manuals.map(function(m){return '<li><b>'+m.code+'</b> '+m.name+': '+m.drill[0]+'</li>'}).join('')+'</ul>'}
 else{var c=D.cross[idx];h='<b>현재 발령: '+nm+' (단계 '+(idx+1)+' · 대응 모드 '+l+')</b> — 7개 매뉴얼이 지금 해야 할 일<ul>'+c.rows.map(function(r){return '<li><b>'+r.code+'</b> '+r.label+': '+r.do+' ▶ '+r.say+'</li>'}).join('')+'</ul>'}
 e.innerHTML=h}
setInterval(live,3000);setTimeout(live,300);window.hvManLive=live;
})();
'''
open(os.path.join(HERE, '..', 'views8.js'), 'w', encoding='utf-8').write(js)
print('views8.js', len(js))
