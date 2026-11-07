# 이상징후 및 보안체계 구조도 1.0 생성기 (대표님 11/07 13:58 지시) — 사업부 관계 구조도 2.0과 별개의 도면
# 출력: cowork/ctl/sec_structure.svg (사이트 SC-02·PC 문서가 같은 파일을 쓴다) / 관계 구조도 2.1 작업본(입력 2.0 svg 경로를 인자로)
import sys,re,html
def E(s):return html.escape(s,quote=False)
W,H=1587,1123
o=[]
a=o.append
a('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="Pretendard,Noto Sans KR,Noto Sans CJK KR,sans-serif">'%(W,H,W,H))
a('<defs><marker id="ah" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto-start-reverse"><path d="M0,0 L9,4.5 L0,9 z" fill="#3b4a8c"/></marker><marker id="ar" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#c62828"/></marker></defs>')
a('<rect width="%d" height="%d" fill="#fff"/>'%(W,H))
def T(x,y,s,sz=14,fill='#222',w=400,anchor='middle'):
    a('<text x="%s" y="%s" text-anchor="%s" font-size="%s" font-weight="%s" fill="%s">%s</text>'%(x,y,anchor,sz,w,fill,E(s)))
def R(x,y,w,h,fill,stroke='#0b1640',sw=1,rx=10,dash=None):
    a('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s" stroke="%s" stroke-width="%s"%s/>'%(x,y,w,h,rx,fill,stroke,sw,(' stroke-dasharray="%s"'%dash) if dash else ''))
def L(x1,y1,x2,y2,col='#3b4a8c',sw=1.6,dash=None,mk='ah',both=False):
    a('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"%s marker-end="url(#%s)"%s/>'%(x1,y1,x2,y2,col,sw,(' stroke-dasharray="%s"'%dash) if dash else '',mk,(' marker-start="url(#ah)"' if both else '')))
T(40,48,'HIVEN 통합사업 이상징후 및 보안체계 구조도 1.0 — 3단 우선 체계 · 순환 10단계 · 경보 12단계 · 외부 3순위',26,'#0b1640',700,'start')
T(40,74,'기준: 대표님 지시 2026-11-07 13:39·13:46·13:55·13:58 · 이 도면은 「사업부 관계 구조도 2.0」(7사업군 접점 30건)과 별개의 도면이며 2.1 작업본에서 서로 편입 · 작성 Sonnet 5.5 · 작업본(승인 전)',13,'#555',400,'start')
# 제1순위 접근·침입 경로 표식
R(30,92,320,58,'#fff','#c62828',2.4); T(190,111,'★ 제1순위 접근·침입 경로',13.5,'#c62828',700); T(190,128,'ic 인트로 열쇠(key) 입력 — 불일치·거부·중복 실패',11.5,'#222'); T(190,143,'→ 즉시 보호 단계 전환 (불일치 1회부터)',11.5,'#c62828',700)
L(350,121,363,121,'#c62828',2,None,'ar')
# 1단 최상위
R(363.5,92,860,58,'#0b1640'); T(793.5,118,'① 최상위 · HIVEN 자동화 통합 통제 시스템 (ic.hiven.ai.kr · hiven.ai.kr)',19,'#fff',700)
T(793.5,140,'기존 도면 표기: AICS 자동화 통합 통제 시스템 · 모든 사업·화면·기록을 통제하는 바탕',12.5,'#dfe6ff')
L(793.5,150,793.5,176,'#0b1640',2.2)
# 2단 최우선
R(263.5,176,1060,84,'#c62828','#7f0000',1.5); T(793.5,202,'② 최우선 · HIVEN 통합사업 이상징후 및 보안체계 시스템 (SC-02)',20,'#fff',700)
T(793.5,224,'체제: HIVEN 통합사업 이상징후 및 보안체제 · 단계 1~10 · 경보 12단계 · 3대 매뉴얼(시스템 · 서비스 · 고객지원) · 신호 규격',13,'#ffe0e0')
T(793.5,246,'다른 모든 운영보다 먼저 관리·운영(대응·조치)하는 체계 시스템',13,'#ffe0e0')
L(793.5,260,793.5,296,'#7f0000',2.2)
# 3단 하위 컨테이너
R(30,296,1527,448,'#f5f8ff','#3b4a8c',1.5,16,'8 5')
T(48,322,'③ 하위 종속·실행 · 침입 예측/예방/대응/조치 시스템 (SC-03) — 모든 WEB Site · AI Agent · .app 등 실행 Tools를 전방위로 돌리는 순환',16,'#0b1640',700,'start')
# 대상(왼쪽)
T(185,356,'관측·제어 대상 (주체: HIVEN)',13,'#0b1640',700)
tg=[('WEB Site','hiven.co.kr · hiven.ai.kr · ic.hiven.ai.kr','구현','#2e7d32'),('AI Agent','AICS · HiClo 등','절차 정립','#9e6b00'),('.app','HiCoffer · HIVEN.app · HiClo.app · HiAad.app','절차 정립','#9e6b00')]
for i,(n,d,s,c) in enumerate(tg):
    y=372+i*108
    R(48,y,274,84,'#fff','#3b4a8c',1.4); T(185,y+28,n,19,'#0b1640',700); T(185,y+50,d,11.5,'#555'); R(118,y+58,134,20,c,c,0,10); T(185,y+72,s,12,'#fff',700)
    L(322,y+42,432,520)
# 외부 3순위(오른쪽)
T(1402,356,'대응·예방 대상 (외부 연동 시스템)',13,'#0b1640',700)
ex=[('1순위','직접 연계하는 1차 시스템','PG · 은행 · 호스팅/CDN · 메일 · 앱 마켓 · AI 제공처 · 협력사 API','발령 +2단계','#b71c1c'),('2순위','1차 뒤 간접 관계 2차 시스템','VAN·카드망 · 하위 인프라 · SDK · 패키지 공급망 · 통신망','발령 +1단계','#e65100'),('3순위','그 밖의 모든 외부 위험 요소','불특정 접속자 · 봇 · 피싱 · 악성 파일 · 공용망','발령 +0단계','#6d4c41')]
for i,(n,d,e,w,c) in enumerate(ex):
    y=372+i*108
    R(1265,y,277,92,'#fff',c,1.8); R(1265,y,70,92,c,c,0,10); T(1300,y+54,n,17,'#fff',700)
    T(1440,y+22,d,12.5,'#222',700); T(1440,y+42,e[:26],11,'#555');
    if len(e)>26: T(1440,y+57,e[26:],11,'#555')
    T(1440,y+80,w,12,c,700)
    L(1265,y+46,1155,520,'#c62828',1.6,None,'ar')
# 순환 링(가운데)
import math
cx,cy,rx_,ry_=793.5,520,315,125
a('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="none" stroke="#c9d3f5" stroke-width="2" stroke-dasharray="3 5"/>'%(cx,cy,rx_,ry_))
steps=['전방위 관측','관찰','포착','행동제어','보고','조치·응대','후속대응','복구·복호화','전파','개선·예방 복귀']
pts=[]
for i,s in enumerate(steps):
    ang=-math.pi/2+i*2*math.pi/10
    px=cx+rx_*math.cos(ang); py=cy+ry_*math.sin(ang)
    pts.append((px,py))
for i,(px,py) in enumerate(pts):
    qx,qy=pts[(i+1)%10]
    dx,dy=qx-px,qy-py; d=math.hypot(dx,dy)
    L(round(px+dx/d*34,1),round(py+dy/d*24,1),round(qx-dx/d*34,1),round(qy-dy/d*24,1),'#3b4a8c',1.4)
done=['웹 구현','웹 구현','웹 구현','웹 구현','웹 구현','절차','절차','절차','웹 구현(전송)','절차']
for i,((px,py),s) in enumerate(zip(pts,steps)):
    col='#2b5be8' if done[i].startswith('웹') else '#7a869f'
    R(round(px-58,1),round(py-22,1),116,44,col,'#0b1640',1,10)
    T(round(px,1),round(py-3,1),'%d %s'%(i+1,s),12.5,'#fff',700); T(round(px,1),round(py+13,1),done[i],10.5,'#e8edff')
T(cx,cy-8,'순환 (루프)',17,'#0b1640',700); T(cx,cy+14,'침입 예측/예방/대응/조치',13,'#0b1640'); T(cx,cy+32,'→ 1번 관측으로 돌아감',12,'#555')
# 수집 박스 (링 아래)
R(603.5,686,380,52,'#fff7e0','#9e6b00',1.4); T(793.5,708,'신호 수집 · ic Worker  POST /__sec',14,'#5d4000',700); T(793.5,727,'{t, g, a, r, n, why, host, ua} → 실시간 로그([침입경보])',11.5,'#5d4000')
# 12단계 막대
T(40,774,'경보 12단계 (관심 → 안심) · 대상 순위 가중: 1순위 +2 · 2순위 +1 · 3순위 +0',16,'#0b1640',700,'start')
nm=['관심','주의','경계','경고','위험','위기','긴급','피해발생','조치','복구/복호화','안정','안심']
cl=['#1565c0','#00838f','#ef9a00','#ef6c00','#c62828','#8e0000','#6a1b9a','#4a148c','#455a64','#2e7d32','#43a047','#1b5e20']
for i,(n,c) in enumerate(zip(nm,cl)):
    x=30+i*(120+8.7)
    R(round(x,1),788,120,48,c,c,0,8); T(round(x+60,1),808,str(i+1),12,'#fff',400); T(round(x+60,1),828,n,15,'#fff',700)
T(40,858,'침입 경보 5등급 연결: 관찰→관심 · 관심→주의 · 심각→경계(복제·삽입·변조 확인 시 경고) · 위험→위험 · 위기→위기 / 긴급~안심은 IC 판정 / 방어태세 단계 1~10과 함께 사용',12.5,'#444',400,'start')
# 편입·연계 띠
T(40,892,'편입·연계 (연계 서비스 플로어 S-01~S-11): 보안체계가 모든 사업군과 연결 — 주는 것: 이상 신호 / 받는 것: 대응·조치',16,'#0b1640',700,'start')
bs=[('Hi ASI','AI Agent'),('Hi Coffer','금고·키'),('Hi DAM','원본 검증'),('Hi ICT','인프라'),('Hi Serve','결제·제휴'),('Hi Silver','지정인 공개'),('Hi Trade','거래'),('전사경영·미래전략','보고·승인'),('고객지원','고객·협력사·지정자')]
for i,(n,d) in enumerate(bs):
    x=30+i*(165+5.6)
    R(round(x,1),906,165,64,'#2b5be8' if i<7 else ('#0b1640' if i==7 else '#455a64'),'#0b1640',1,10); T(round(x+82.5,1),932,n,14.5 if i<7 else 13,'#fff',700); T(round(x+82.5,1),954,d,12,'#dfe6ff')
L(14,218,14,938,'#c62828',1.6,'6 5','ah'); L(14,938,30,938,'#c62828',1.6,'6 5','ah')
# 범례
y0=1000
a('<g font-size="13" fill="#333">')
a('<rect x="40" y="%d" width="22" height="14" rx="3" fill="#2b5be8"/><text x="70" y="%d">웹 구현(지금 동작)</text>'%(y0-12,y0))
a('<rect x="230" y="%d" width="22" height="14" rx="3" fill="#7a869f"/><text x="260" y="%d">절차 정립 · 구현 보강 예정</text>'%(y0-12,y0))
a('<line x1="470" y1="%d" x2="510" y2="%d" stroke="#3b4a8c" stroke-width="1.6" marker-end="url(#ah)"/><text x="518" y="%d">순환·관측 방향</text>'%(y0-5,y0-5,y0))
a('<line x1="660" y1="%d" x2="700" y2="%d" stroke="#c62828" stroke-width="1.6" marker-end="url(#ar)"/><text x="708" y="%d">외부 대상에서 들어오는 신호</text>'%(y0-5,y0-5,y0))
a('<line x1="920" y1="%d" x2="960" y2="%d" stroke="#c62828" stroke-width="1.6" stroke-dasharray="6 5"/><text x="968" y="%d">② 보안체계 → 사업군 편입 연결</text>'%(y0-5,y0-5,y0))
a('<text x="40" y="%d">외부 대상 예시(PG·은행 등)는 연동 목록이 확정되면 갱신합니다. AI Agent·.app의 실제 신호 송신은 구현 보강 예정이며 신호 규격은 확정되어 있습니다.</text>'%(y0+30))
a('<text x="40" y="%d">대응·조치 상세는 SC-02 화면(ic.hiven.ai.kr)의 표와 HIVEN_비상대응체계_매뉴얼_261107.md가 같은 원천(views7.js hvEM)에서 나옵니다.</text>'%(y0+54))
a('<text x="40" y="%d">3단 순서: ① 최상위 → ② 최우선 → ③ 하위 종속·실행. 관리·운영은 항상 이 순서로 우선 적용합니다(대표님 11/07 13:46).</text>'%(y0+78))
a('<text x="40" y="%d">시험 기간 운영(대표님 11/07 14:06): 대응 강도만 완화(등록부 T-01~T-08), 감지·기록·전송·판정은 불변. 역순환 인지: ① 하위 → ② 최우선 → ③ 최상위 → 대표님(폰), 역정합 검사는 SC-02 화면에서 실시간 대조.</text>'%(y0+102))
a('</g></svg>')
svg='\n'.join(o)
open('cowork/ctl/sec_structure.svg','w',encoding='utf-8').write(svg)
print('sec_structure.svg',len(svg))
# 관계 구조도 2.1 작업본 (입력 2.0 svg 경로 인자)
if len(sys.argv)>2:
    t=open(sys.argv[1],encoding='utf-8').read()
    t=t.replace('width="1587" height="1123" viewBox="0 0 1587 1123"','width="1587" height="1290" viewBox="0 0 1587 1290"',1)
    t=t.replace('<rect width="1587" height="1123" fill="#fff"/>','<rect width="1587" height="1290" fill="#fff"/>',1)
    t=t.replace('HIVEN 사업부 관계 구조도 2.0 —','HIVEN 사업부 관계 구조도 2.1 — 보안체계 편입 ·',1)
    band=[]
    b=band.append
    b('<g>')
    b('<rect x="30" y="1128" width="1527" height="150" rx="14" fill="#fff5f5" stroke="#c62828" stroke-width="1.4" stroke-dasharray="8 5"/>')
    b('<text x="48" y="1156" font-size="16" font-weight="700" fill="#7f0000">보안체계 편입 (2.1 추가) — 위 AICS 자동화 통합 통제 시스템(최상위) 아래 최우선·하위 시스템이 7개 사업군 전부와 연계됩니다</text>')
    b('<rect x="48" y="1172" width="360" height="52" rx="10" fill="#0b1640"/><text x="228" y="1194" text-anchor="middle" font-size="14" font-weight="700" fill="#fff">① 최상위 · HIVEN 자동화 통합 통제 시스템</text><text x="228" y="1213" text-anchor="middle" font-size="11.5" fill="#dfe6ff">(위 도면 맨 위 상자와 같은 시스템)</text>')
    b('<line x1="408" y1="1198" x2="470" y2="1198" stroke="#7f0000" stroke-width="2" marker-end="url(#ah)"/>')
    b('<rect x="472" y="1172" width="420" height="52" rx="10" fill="#c62828"/><text x="682" y="1194" text-anchor="middle" font-size="14" font-weight="700" fill="#fff">② 최우선 · 이상징후 및 보안체계 시스템 (SC-02)</text><text x="682" y="1213" text-anchor="middle" font-size="11.5" fill="#ffe0e0">경보 12단계 · 3대 매뉴얼 · 신호 규격</text>')
    b('<line x1="892" y1="1198" x2="954" y2="1198" stroke="#7f0000" stroke-width="2" marker-end="url(#ah)"/>')
    b('<rect x="956" y="1172" width="430" height="52" rx="10" fill="#2b5be8"/><text x="1171" y="1194" text-anchor="middle" font-size="14" font-weight="700" fill="#fff">③ 하위 · 침입 예측/예방/대응/조치 시스템 (SC-03)</text><text x="1171" y="1213" text-anchor="middle" font-size="11.5" fill="#dfe6ff">관측 → … → 개선·예방 복귀 순환 10단계</text>')
    b('<text x="48" y="1250" font-size="12.5" fill="#444">연계 접점: 사업군 접점 30건(C-01~C-30)과 별도로 보안체계 연계 접점 11건(S-01~S-11)을 둡니다. 상세 구조는 별도 도면 「이상징후 및 보안체계 구조도 1.0」, 표는 SC-02 「편입·연계 서비스 플로어」.</text>')
    b('<text x="48" y="1270" font-size="12.5" fill="#444">외부 연동 시스템 대상은 1순위(직접 연계) · 2순위(간접 관계) · 3순위(그 밖의 위험 요소)로 나뉘며 경보 12단계로 발령합니다. 제1순위 경로: ic 인트로 열쇠 입력(불일치 1회부터 즉시 보호 단계).</text>')
    b('</g></svg>')
    t=t.replace('</svg>','\n'.join(band),1) if t.rstrip().endswith('</svg>') else t
    open(sys.argv[2],'w',encoding='utf-8').write(t)
    print('2.1',len(t))
