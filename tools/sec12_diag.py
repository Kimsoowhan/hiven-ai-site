# -*- coding: utf-8 -*-
"""12번 폴더 개별 구조도 13종 (SVG). 데이터는 hvEM(views7.js)·manuals.json·bg_contact.tsv·sc_renumber_261107.json에서 읽는다."""
import math
from sec12_svg import Canvas, wrap, tw

FOOT = '문서 SEC · 영역 04.00 · D2 · R1 · 작성 Sonnet 5.5 · 2026-11-07 · 작업본(대표님 승인 대기) · 메뉴 번호는 11/07 14:53 확정 배열 기준'
NAVY, RED, DRED, GRAY = '#0b1640', '#c62828', '#7f0000', '#5b6478'
LV = ['#2e7d32', '#558b2f', '#9e9d24', '#f9a825', '#ef6c00', '#e64a19', '#c62828', '#8e0000', '#6a1b9a', '#4a148c', '#1565c0', '#0d47a1']


def cut(s, n):
    s = str(s)
    return s if len(s) <= n else s[:n - 1] + '…'


def first(s, n=34):
    s = str(s)
    for sep in ['. ', '。', '·', ', ', '、']:
        pass
    return cut(s.split('. ')[0], n)


def d01(D):
    em = D['em']; c = Canvas(1600, 1040, '구조도 01 · 위계 — 3단 우선 체계', '최상위 자동화 통합 통제 시스템 ⊃ SC-03 이상징후 및 보안체계(최우선) ⊃ SC-04 침입 예측·예방·대응·조치(하위 실행). 신호는 아래에서 위로, 지시는 위에서 아래로 흐른다.', FOOT)
    c.box(40, 110, 250, 110, '대표님 (폰 · PC)\n최종 판단·긴급 직접 통제', 14, '#fff', RED, bold=True, sw=2)
    c.box(350, 110, 900, 96, em['hier'][0][1] + '\n' + em['hier'][0][2], 15, NAVY, NAVY, '#fff', bold=True)
    c.line(800, 206, 800, 250, NAVY, 2.4)
    c.box(260, 250, 1080, 130, em['hier'][1][1] + '\n' + em['hier'][1][2], 15, RED, DRED, '#fff', bold=True, sw=1.6)
    c.line(800, 380, 800, 430, DRED, 2.4)
    c.box(260, 430, 1080, 118, em['hier'][2][1] + '\n' + em['hier'][2][2], 14, '#ef6c00', '#bf360c', '#fff', bold=True)
    c.line(290, 165, 350, 158, RED, 2.2, None, 'ar', True)
    c.text(320, 150, '보고 · 판단', 11, RED, 700)
    xs = [260, 640, 1020]
    for i, t in enumerate(em['tgt']):
        c.box(xs[i], 610, 320, 120, t[0] + ' — ' + t[1] + '\n' + t[2] + '\n[' + t[3] + ']', 12, '#fff3e0', '#bf360c', align='middle')
        c.line(xs[i] + 160, 548, xs[i] + 160, 610, '#bf360c', 1.8, None, 'ah', True)
    c.box(260, 790, 1080, 100, '사업군 담당 사업부 7(Hi ASI · Hi Coffer · Hi DAM · Hi ICT · Hi Serve · Hi Silver · Hi Trade) + 전사경영부 · 미래전략사업부 + 고객지원\n연계점 S-01~S-11 (신호 ↑ · 지시 ↓), 사업군 접점 C-01~C-30은 별도', 13, '#e8f5e9', '#2e7d32')
    c.line(800, 730, 800, 790, '#2e7d32', 1.8, None, 'ag', True)
    c.box(1370, 110, 200, 250, '★ 제1순위 경로\n' + em['first'][0][1] + '\n\n첫 신호: ' + em['first'][1][1], 12, '#fff', RED, RED, sw=2.2)
    c.line(1370, 235, 1340, 300, RED, 2, None, 'ar')
    c.box(1370, 400, 200, 250, '메뉴 위치\nSC-02 종합 현황\nSC-03 이상징후 및 보안체계\nSC-04 침입 예측·예방·대응·조치\nSC-05~16 기존 화면', 12, '#f3f6ff', NAVY, NAVY, align='start', head='통합관제 대시보드')
    c.box(40, 930, 1520, 60, '각인: ' + em['first'][5][1], 12, '#fff8e1', '#f9a825', '#5d4037')
    return c.svg()


def d02(D):
    em = D['em']; c = Canvas(1600, 760, '구조도 02 · 순환 10단계', '전방위 관측에서 시작해 개선·예방 복귀로 다시 1번 관측으로 돌아가는 닫힌 순환. 웹 구현 단계와 절차 단계를 색으로 구분한다.', FOOT)
    L = em['loop']; w, h, gx = 270, 190, 38
    pos = []
    for i in range(10):
        r, k = divmod(i, 5)
        x = 40 + (k if r == 0 else 4 - k) * (w + gx)
        pos.append((x, 120 + r * 290))
    for i, (n, nm, ds, tag) in enumerate(L):
        x, y = pos[i]
        fill = '#e8f5e9' if '웹' in tag else '#fff3e0'
        c.box(x, y, w, h, ds + '\n[' + tag + ']', 12, fill, '#2e7d32' if '웹' in tag else '#ef6c00', align='start', head=n + ' ' + nm, headcol=NAVY)
    for i in range(9):
        (x1, y1), (x2, y2) = pos[i], pos[i + 1]
        if y1 == y2:
            if x2 > x1: c.line(x1 + w, y1 + h / 2, x2, y2 + h / 2)
            else: c.line(x1, y1 + h / 2, x2 + w, y2 + h / 2)
        else:
            c.line(x1 + w / 2, y1 + h, x2 + w / 2, y2)
    x10, y10 = pos[9]; x1, y1 = pos[0]
    c.path('M %s %s L 18 %s L 18 %s L %s %s' % (x10, y10 + h / 2, y10 + h / 2, y1 + h / 2, x1, y1 + h / 2), RED, 2.4, '8 5', 'ar')
    c.text(300, 392, '개선·예방 복귀 → 1번 전방위 관측으로 순환 (형상·변경 이력 기록)', 12, RED, 700)
    c.box(40, 650, 1520, 60, '순환의 시작점은 ic 인트로 열쇠 입력(제1순위 경로). 4번 행동 제어까지는 웹에 구현되어 있고 6번 이후 조치·응대는 절차로 정립되어 있다.', 12, '#fff8e1', '#f9a825', '#5d4037')
    return c.svg()


def d03(D):
    em = D['em']; c = Canvas(1600, 700, '구조도 03 · 경보 12단계와 발령', '관심에서 안심까지 12단계. 단계마다 징후·순환 단계·대응 모드(1~10)·조치·화면 표시를 한 열에 둔다.', FOOT)
    A = em['al12']; x0, cw = 130, 119
    rows = [('징후', 118), ('순환 단계', 40), ('대응 모드', 34), ('조치', 150), ('표시', 60)]
    yy = 150; ys = []
    for nm, h in rows:
        c.box(36, yy, 88, h, nm, 12, '#eef2ff', NAVY, NAVY, bold=True)
        ys.append((yy, h)); yy += h + 6
    for i, a in enumerate(A):
        x = x0 + i * cw
        c.box(x, 108, cw - 4, 36, str(a[0]) + ' ' + a[1], 13, LV[i], LV[i], '#fff', bold=True)
        vals = [a[2], a[3], a[4], a[5], a[6]]
        for (y, h), v in zip(ys, vals):
            c.box(x, y, cw - 4, h, v, 10.5, '#fff', '#b8c0d8', align='start', pad=5)
    c.box(36, 600, 1528, 64, '발령: 외부 연계 순위(1순위 +2단계 · 2순위 +1단계 · 3순위 0)에 따라 같은 징후도 높게 발령한다. 1~6단계는 열쇠 오류 횟수 기준으로 자동 판정(구현), 7단계 긴급부터는 IC·대표님이 판정한다. 시험 기간에도 감지·판정·표시는 완화하지 않는다.', 12, '#fff8e1', '#f9a825', '#5d4037')
    return c.svg()


def d04(D):
    em = D['em']; c = Canvas(1600, 700, '구조도 04 · 외부 연동 대상 순위 1 · 2 · 3', '외부 연계 시스템을 가까운 순서로 3개 순위로 나누고, 순위마다 관측 방식과 발령 가중을 다르게 둔다.', FOOT)
    cols = [('순위', 90), ('정의', 300), ('예시', 420), ('관측 · 대응', 420), ('발령 가중', 220)]
    x = 40; xs = []
    for nm, w in cols:
        c.box(x, 110, w - 6, 34, nm, 13, NAVY, NAVY, '#fff', bold=True); xs.append((x, w - 6)); x += w
    cl = ['#c62828', '#ef6c00', '#5b6478']
    for i, r in enumerate(em['rank']):
        y = 154 + i * 160
        for j, (xx, ww) in enumerate(xs):
            c.box(xx, y, ww, 150, r[j], 15 if j == 0 else 12, cl[i] if j == 0 else '#fff', cl[i], '#fff' if j == 0 else '#222', bold=(j == 0), align='middle' if j in (0, 4) else 'start')
    c.line(20, 160, 20, 620, GRAY, 2)
    c.text(14, 640, '가까움 → 멀음', 11, GRAY, 400, 'start')
    return c.svg()


def d05(D):
    M = D['man']; c = Canvas(1600, 1110, '구조도 05 · 매뉴얼 7종 종단 · 횡단 매트릭스', '세로는 경보 12단계(종단), 가로는 매뉴얼 7종(횡단). 같은 단계에서 7개 매뉴얼이 동시에 하는 일의 첫 문장.', FOOT)
    ms = M['manuals']; x0, cw, y0, rh = 110, 205, 106, 76
    for j, m in enumerate(ms):
        c.box(x0 + j * cw, y0, cw - 4, 44, m['code'] + ' ' + m['name'], 11, NAVY, NAVY, '#fff', bold=True)
    for i, cr in enumerate(M['cross']):
        y = y0 + 48 + i * rh
        c.box(30, y, 76, rh - 4, cr['name'], 12, LV[i], LV[i], '#fff', bold=True)
        for j, r in enumerate(cr['rows']):
            c.box(x0 + j * cw, y, cw - 4, rh - 4, cut(r['do'].split('. ')[0], 80), 10, '#fff', '#c8d0e8', align='start', pad=5)
    return c.svg()


def d06(D):
    M = D['man']; em = M['emergency']; c = Canvas(1600, 900, '구조도 06 · 비상체계 가동 · 해제 흐름', '가동 조건 → 가동 순서 → 상황실 → 소통 → 중대 결정 → 해제. 법정 시한 시계는 알게 된 시각부터 병행한다.', FOOT)
    keys = list(em.keys())

    def g(i): return '\n'.join('· ' + x for x in em[keys[i]])
    spec = [(0, 40, 100), (1, 440, 100), (4, 840, 100), (5, 1240, 100), (6, 840, 340), (7, 440, 340), (2, 40, 340)]
    for idx, x, y in spec:
        c.box(x, y, 340, 220, g(idx), 11.5, '#fff', RED if idx in (0, 2) else NAVY, align='start', head=keys[idx], headcol=RED if idx in (0, 2) else NAVY)
    c.line(380, 210, 440, 210); c.line(780, 210, 840, 210); c.line(1180, 210, 1240, 210)
    c.path('M 1410 320 L 1410 450 L 1180 450'); c.line(840, 450, 780, 450); c.line(440, 450, 380, 450)
    c.box(1240, 340, 320, 220, g(3), 11.5, '#fff8e1', '#f9a825', align='start', head=keys[3], headcol='#5d4037')
    c.line(1400, 340, 1400, 320, '#f9a825', 1.6, '5 4')
    c.box(40, 590, 1520, 110, g(8), 12, '#ffebee', RED, align='start', head=keys[8], headcol=RED)
    c.line(210, 560, 210, 590, RED, 1.8, None, 'ar')
    c.box(40, 730, 1520, 60, '해제: 모든 기준을 충족하고 대표님이 확인한 뒤에만 해제한다. 해제 뒤에도 재침입 대비 감시를 유지한다.', 12, '#e8f5e9', '#2e7d32')
    return c.svg()


def d07(D):
    em = D['em']; st = em['std']; c = Canvas(1600, 900, '구조도 07 · 시험 기간 역순환 · 역정합', '시험 기간에는 대응 강도만 낮추고, 불변 7원칙을 지키며, 등록부에 있는 완화만 허용한다. 화면은 표준과 실제 값을 11행으로 거꾸로 대조한다.', FOOT)
    c.box(36, 106, 1528, 60, st['why'], 12, '#fff8e1', '#f9a825', '#5d4037', align='start')
    for i, (a, b) in enumerate(st['inv']):
        c.box(36, 180 + i * 62, 520, 56, a + ': ' + b, 11, '#fff', RED if i < 4 else NAVY, align='start', pad=6)
    c.text(36, 172, '불변 7원칙', 12, NAVY, 700, 'start')
    c.text(600, 172, '완화 등록부(허용되는 완화)', 12, NAVY, 700, 'start')
    for i, r in enumerate(st['reg'][:11]):
        c.box(600, 180 + i * 38, 940, 34, ' · '.join(str(x) for x in r[:4]), 10.5, '#fff', '#b8c0d8', align='start', pad=6)
    c.box(36, 640, 1528, 170, '흐름\n① 표준(불변 7) → ② 등록부(T-xx)에 없으면 완화 불가 → ③ 화면에 완화 중 표시(SC-02 · SC-03 · SC-04) → ④ 역정합 검사: 표준 값 ↔ 실제 적용 값 11행 대조(화면 SC-03) → ⑤ 종료는 대표님 지시로만 → ⑥ 등록부 항목 전부 운영 기준값으로 되돌림 → ⑦ 되돌림 검사 통과 후 종료 기록', 12, '#f3f6ff', NAVY, align='start')
    return c.svg()


def d08(D):
    M = D['man']; c = Canvas(1600, 860, '구조도 08 · 법정 통지 시한 시계', '알게 된 시각을 0으로 두고 HIVEN 내부 시계(1 · 6 · 24 · 72시간 설계값)와 법정 기한을 한 축에 놓는다. 확인 상태를 색으로 구분한다.', FOOT)
    X0, X1 = 80, 1500
    def px(h): return X0 + (X1 - X0) * (math.log(1 + h) / math.log(1 + 72))
    c.line(X0, 190, X1 + 20, 190, NAVY, 3, None, 'ah')
    for h, lb, col in [(0, '알게 된 시각', RED), (1, '1시간\n상황실 가동', NAVY), (6, '6시간\n1차 판정·초기 공지', NAVY), (24, '24시간\n정보통신망법 신고(언론 요약)', '#ef6c00'), (72, '72시간\n개인정보보호법 통지·신고', RED)]:
        x = px(h); c.line(x, 150, x, 200, col, 2, None, None)
        for k, ln in enumerate(lb.split('\n')): c.text(x, 135 - (len(lb.split('\n')) - 1 - k) * 15, ln, 11.5, col, 700 if k == 0 else 400)
    c.text(X0, 240, 'HIVEN 내부 시계 1 · 6 · 24 · 72시간은 설계값(대표님 확정 필요)', 11.5, GRAY, 400, 'start')
    for i, (a, b, s) in enumerate(M['law']):
        y = 270 + i * 76
        col = '#2e7d32' if s.startswith('원문') else '#ef6c00' if ('요약' in s) else GRAY
        c.box(40, y, 360, 70, a, 11.5, '#fff', col, bold=True, align='start')
        c.box(406, y, 880, 70, cut(b, 170), 10.5, '#fff', col, align='start')
        c.box(1292, y, 270, 70, s, 11, '#f7f7f7', col, col, bold=True)
    return c.svg()


def d09(D):
    M = D['man']; c = Canvas(1600, 860, '구조도 09 · B2C → B2B → B2G 확장 요구', 'HIVEN의 모든 사업과 서비스는 B2C에서 B2B, B2G로 넓어진다. 규모가 바뀌어도 기틀은 같고 보안체계에 추가되는 요구만 늘어난다.', FOOT)
    labs = ['규모 · 대상', '추가되는 요구', '보안체계 영향', '선행 조건', '확인 상태']
    cw = 480
    for j, e in enumerate(M['expand']):
        x = 40 + j * (cw + 40)
        c.box(x, 110, cw, 46, e[0], 17, [NAVY, '#1565c0', '#6a1b9a'][j], NAVY, '#fff', bold=True)
        for k in range(1, 5):
            c.box(x, 164 + (k - 1) * 150, cw, 144, e[k], 11.5, '#fff', '#b8c0d8', align='start', head=labs[k] if k > 0 else '', headcol=NAVY)
        if j < 2: c.line(x + cw + 2, 133, x + cw + 38, 133, RED, 2.4, None, 'ar')
    return c.svg()


def d10(D):
    pairs = D['pairs']; c = Canvas(1600, 1180, '구조도 10 · 사업군 · 사업부 관계와 접점 30건', '9개 사업부(사업군 담당 7 + 전사경영부 + 미래전략사업부), 접점 C-01~C-30(20쌍)과 AICS 통제선. 전사경영부 · 미래전략사업부는 접점이 없고 S-10으로 연결된다.', FOOT)
    c.box(400, 100, 800, 60, 'AICS 자동화 통합 통제 시스템 → SC-03 이상징후 및 보안체계 → SC-04 침입 예측·예방·대응·조치', 14, NAVY, NAVY, '#fff', bold=True)
    c.box(40, 100, 330, 60, '전사경영부 (S-10)', 14, '#eef2ff', NAVY, bold=True, dash='6 4')
    c.box(1230, 100, 330, 60, '미래전략사업부 (S-10)', 14, '#eef2ff', NAVY, bold=True, dash='6 4')
    cx, cy = 800, 640
    order = ['Hi Coffer', 'Hi ASI', 'Hi DAM', 'Hi Trade', 'Hi Silver', 'Hi Serve', 'Hi ICT']
    P = {}
    for i, n in enumerate(order):
        a = -math.pi / 2 + i * 2 * math.pi / 7
        P[n] = (cx + 640 * math.cos(a), cy + 410 * math.sin(a))
    kmap = {'HiASI': 'Hi ASI', 'HiCoffer': 'Hi Coffer', 'HiDAM': 'Hi DAM', 'HiICT': 'Hi ICT', 'HiServe': 'Hi Serve', 'HiSilver': 'Hi Silver', 'HiTrade': 'Hi Trade'}
    for (a, b), ids in pairs.items():
        pa, pb = P[kmap[a]], P[kmap[b]]
        col = RED if any(D['sev'][i] == '상' for i in ids) else '#3b4a8c'
        c.line(pa[0], pa[1], pb[0], pb[1], col, 2.4 if col == RED else 1.6, None, None)
    for k, ((a, b), ids) in enumerate(pairs.items()):
        pa, pb = P[kmap[a]], P[kmap[b]]
        t = 0.5 + 0.13 * ((k % 3) - 1)
        mx, my = pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t
        lab = 'C-' + ' · '.join(i[2:] for i in ids); wd = tw(lab, 10.5) + 10
        c.rect(mx - wd / 2, my - 9, wd, 17, '#fff', '#c8d0e8', 0.8, 4)
        c.text(mx, my + 4, lab, 10.5, '#222', 700)
    for n, (x, y) in P.items():
        root = n == 'Hi Coffer'
        c.box(x - 85, y - 32, 170, 64, n + (' (Root)' if root else '') + '\n사업군 담당', 14, '#0b1640' if root else '#fff', NAVY, '#fff' if root else NAVY, bold=True, sw=2)
        c.rect(x - 85, y - 32, 14, 14, RED, RED, 1, 3)
    c.box(40, 1100, 1520, 50, '빨간 선: 심각도 상 접점이 포함된 쌍 · 파란 선: 중 접점만 · 모서리 빨간 점: AICS 통제선 대상 · 접점 30건 = 쌍 20개 (상 14건 · 중 16건). 접점 목록은 06_자료의 접점 데이터표와 같다.', 12, '#fff8e1', '#f9a825', '#5d4037', align='start')
    return c.svg()


def d11(D):
    em = D['em']; L = em['link']; n = len(L); rh = 74
    c = Canvas(1600, 150 + n * rh + 120, '구조도 11 · 데이터 플로어 총괄 (신호 ↑ · 지시 ↓)', '11개 연계점(S-01~S-11)에서 올라오는 이상 신호는 ic Worker가 모으고, SC-04이 감지·식별하며, SC-03가 12단계로 판정해 대표님께 보고한다. 내려가는 조치는 같은 연계점으로 돌아간다.', FOOT)
    yb = 112; hb = n * rh + 12
    c.box(560, yb, 260, hb, 'ic Worker 수집\n/__sec\n신호 수신 로그\n(S-09)', 14, '#e3f2fd', '#1565c0', '#0d47a1', bold=True)
    c.box(850, yb, 220, hb, 'SC-04\n감지 · 식별 · 격리\n순환 10단계', 14, '#fff3e0', '#bf360c', '#bf360c', bold=True)
    c.box(1100, yb, 220, hb, 'SC-03\n12단계 판정\n매뉴얼 7종 행동\n대표님 보고', 14, RED, DRED, '#fff', bold=True)
    c.line(820, yb + hb / 2, 850, yb + hb / 2); c.line(1070, yb + hb / 2, 1100, yb + hb / 2)
    c.text(36, yb + 10, '발생원 · 신호 ↑', 12, NAVY, 700, 'start'); c.text(1346, yb + 10, '조치 · 외부 접점 ↓', 12, NAVY, 700, 'start')
    for i, r in enumerate(L):
        y = yb + 18 + i * rh
        c.box(36, y, 500, rh - 8, r[0] + ' ' + r[1] + ': ' + r[2], 10.5, '#fff', '#2e7d32', align='start', pad=6)
        c.line(536, y + (rh - 8) / 2, 560, y + (rh - 8) / 2, '#2e7d32', 1.4, None, 'ag')
        c.box(1346, y, 218, rh - 8, r[3] + '\n외부 접점: ' + r[4] + ' [' + r[5] + ']', 10, '#fff', '#c62828', align='start', pad=6)
        c.line(1346, y + (rh - 8) / 2, 1320, y + (rh - 8) / 2, RED, 1.4, None, 'ar')
    c.box(36, 150 + n * rh + 20, 1528, 70, '데이터 분류: 경보 기록은 영역 00.03 · D2 · R1, 고객 정보가 섞이는 신고 기록은 D3 이상으로 분리한다. 증거 보존 해시와 복원 해시는 형상·변경 이력(SC-12)에 남긴다.', 12, '#f3f6ff', NAVY, align='start')
    return c.svg()


def d12(D):
    M = D['man']; ms = {m['code']: m for m in M['manuals']}; c = Canvas(1600, 1000, '구조도 12 · 서비스 플로어 · 고객지원 응대', '문의 · 신고 · 피해 접수가 창구로 들어와 고객지원 매뉴얼 4종이 응대하고, 상황실이 서비스(고객용 · 관리자용)와 시스템 매뉴얼을 움직인다.', FOOT)
    g = [('M4', '고객 · 사용자'), ('M5', '지정인 · 선지정인'), ('M6', '협력사 · 이해관계자'), ('M7', '오프라인 관리자')]
    for i, (code, nm) in enumerate(g):
        y = 120 + i * 120
        c.box(40, y, 250, 100, nm + '\n' + ms[code]['target'], 12, '#fff', '#2e7d32', bold=False)
        c.box(380, y, 260, 100, code + ' ' + ms[code]['name'] + '\n' + ms[code]['channel'], 11, '#e8f5e9', '#2e7d32', '#1b5e20')
        c.line(290, y + 50, 380, y + 50, '#2e7d32', 1.8, None, 'ag')
        c.line(640, y + 50, 740, 360, '#2e7d32', 1.6, None, 'ag')
    c.box(740, 270, 280, 180, '상황실 (1인 체제)\n대표님 직접 통제\n창구 일원화: 고객 assist@hiven.ai.kr\n투자·협력·후원 contact@hiven.co.kr', 12, RED, DRED, '#fff', bold=True)
    for i, code in enumerate(['M2', 'M3', 'M1']):
        y = 120 + i * 150
        c.box(1130, y, 430, 130, code + ' ' + ms[code]['name'] + '\n대상: ' + ms[code]['target'] + '\n담당: ' + ms[code]['owner'], 12, '#fff', NAVY, NAVY, align='start')
        c.line(1020, 360, 1130, y + 65, NAVY, 1.6)
    c.text(36, 640, '12단계 안내 문구 (고객 · 사용자 매뉴얼 M4 기준)', 13, NAVY, 700, 'start')
    st = ms['M4']['steps']; w = 124
    for i, s in enumerate(st):
        c.box(36 + i * (w + 3), 652, w, 230, cut(s['say'], 70), 9.5, '#fff', LV[i], align='start', pad=5, head=str(s['n']) + ' ' + s['name'], headcol=LV[i])
    c.box(36, 900, 1524, 70, '응대 원칙: 확인된 사실만 안내하고, 사칭 2차 피해(피싱 문자 · 전화) 경고를 함께 낸다. 법정 통지 항목은 법정 기한표를 따른다.', 12, '#fff8e1', '#f9a825', '#5d4037', align='start')
    return c.svg()


def d13(D):
    ren = D['ren']; nm = ren['names']; c = Canvas(1600, 900, '구조도 13 · 통합관제 대시보드 SC 메뉴 구성', '11/07 14:53 확정 배열. 맨 위는 종합 현황, SC-03 · SC-04이 보안 위계, 맨 아래는 말 명령.', FOOT)
    grp = {1: ('관제', NAVY), 2: ('보안 위계 ① 최우선', RED), 3: ('보안 위계 ② 하위 실행', '#ef6c00'), 4: ('사업', '#2e7d32'), 5: ('사업', '#2e7d32'), 6: ('대응', '#ef6c00'), 7: ('배포', '#1565c0'), 8: ('배포', '#1565c0')}
    for i in range(1, 17):
        k = 'SC-%02d' % i; name = nm[k]
        gl, col = grp.get(i, ('운영', '#5b6478'))
        y = 100 + (i - 1) * 46
        c.box(40, y, 620, 40, k + '  ' + name.split('(구')[0], 14, '#fff' if i > 3 else col, col, '#222' if i > 3 else '#fff', bold=True, align='start', pad=12)
        c.box(670, y, 160, 40, gl, 11, '#f7f7f7', col, col, bold=True)
    c.line(350, 100 + 46 + 40, 350, 100 + 46 * 2, RED, 1.6, None, 'ar')
    c.text(870, 120, '번호 변경 대응표 (옛 → 새)', 13, NAVY, 700, 'start')
    inv = ren['map_old_to_new']
    for j, (o, n) in enumerate(sorted(inv.items())):
        col = j % 2; r = j // 2
        c.box(870 + col * 340, 132 + r * 40, 330, 34, o + ' → ' + n + '  ' + nm[n].split('(구')[0], 11.5, '#fff', '#b8c0d8', align='start', pad=8)
    c.box(870, 470, 670, 200, '위계: 최상위 자동화 통합 통제 시스템 ⊃ SC-03 이상징후 및 보안체계 시스템 ⊃ SC-04 침입 예측·예방·대응·조치 시스템\n\n11/07 14:42 이전의 이력·기록은 당시 번호 그대로이며 이 대응표로 읽는다. SC-09 베타 배포 모니터링은 창 안에서 베타 1 · 2 · 3으로 구분한다.', 12, '#fff8e1', '#f9a825', '#5d4037', align='start')
    return c.svg()


DIAGRAMS = [
    ('구조도01_위계_3단우선체계', d01), ('구조도02_순환10단계', d02), ('구조도03_경보12단계_발령', d03), ('구조도04_외부연동대상_순위', d04),
    ('구조도05_매뉴얼7종_종횡단', d05), ('구조도06_비상체계_가동해제', d06), ('구조도07_시험기간_역정합', d07), ('구조도08_법정통지_시한시계', d08),
    ('구조도09_확장_B2C_B2B_B2G', d09), ('구조도10_사업군_사업부_접점', d10), ('구조도11_데이터플로어_총괄', d11), ('구조도12_서비스플로어_고객지원', d12),
    ('구조도13_SC메뉴_구성', d13),
]
