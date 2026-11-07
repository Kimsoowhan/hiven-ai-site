# -*- coding: utf-8 -*-
"""사업군 · 사업부별 구성 · 서비스 구성 연계도(SVG)와 설명 문서(md) 생성."""
from sec12_svg import Canvas, wrap
from sec12_orgs import ORGS
from sec12_diag import FOOT, NAVY, RED, DRED, GRAY, LV, cut

KMAP = {'HiASI': 'HiASI', 'HiCoffer': 'HiCoffer', 'HiDAM': 'HiDAM', 'HiICT': 'HiICT', 'HiServe': 'HiServe', 'HiSilver': 'HiSilver', 'HiTrade': 'HiTrade'}
DISP = {'HiASI': 'Hi ASI', 'HiCoffer': 'Hi Coffer', 'HiDAM': 'Hi DAM', 'HiICT': 'Hi ICT', 'HiServe': 'Hi Serve', 'HiSilver': 'Hi Silver', 'HiTrade': 'Hi Trade'}


def flows(D, o):
    """(IN, OUT): 사업군은 접점 30건에서, 그 밖은 연계점 S 행에서 만든다."""
    IN, OUT = [], []
    k = o['key']
    if k in KMAP:
        for r in D['contacts']:
            a, b = r['사업부A'], r['사업부B']
            if a == k:
                OUT.append((r['번호'], DISP[b], r['주는 것'], r['심각도'], r)); IN.append((r['번호'], DISP[b], r['받는 것'], r['심각도'], r))
            elif b == k:
                IN.append((r['번호'], DISP[a], r['주는 것'], r['심각도'], r)); OUT.append((r['번호'], DISP[a], r['받는 것'], r['심각도'], r))
        IN.sort(key=lambda x: x[0]); OUT.sort(key=lambda x: x[0])
    else:
        ids = set(o['S'])
        for s in D['em']['link']:
            if s[0] in ids or k == 'HIVEN통합':
                IN.append((s[0], s[1], s[2], '', None)); OUT.append((s[0], s[1], s[3] + ' · 외부 접점: ' + s[4], '', None))
    return IN, OUT


def sev_col(s):
    return RED if s == '상' else '#3b4a8c'


def diagram(D, o, idx):
    IN, OUT = flows(D, o)
    nrow = max(len(IN), len(OUT), len(o['elems']) * 1.6, 6)
    bot = int(215 + min(640, max(420, nrow * 60)))
    y0 = bot + 36; PH = 330
    c = Canvas(1600, y0 + PH + 44, '연계도 %02d · %s — 구성 · 서비스 구성 연계' % (idx, o['name']), '%s · 조직 코드 %s · %s · 정의: %s' % (o['no'], o['org'], o['kind'], o['defn']), FOOT)
    # 상단 통제선
    c.box(40, 110, 470, 54, 'AICS 자동화 통합 통제 시스템 (통제선%s)' % ('' if o['key'] not in ('전사경영부', '미래전략사업부') else ' 없음 · S-10으로 연결'), 12, NAVY, NAVY, '#fff', bold=True)
    c.box(560, 110, 480, 54, 'SC-02 이상징후 및 보안체계 — 12단계 · 매뉴얼 7종', 12, RED, DRED, '#fff', bold=True)
    c.box(1090, 110, 470, 54, 'SC-03 침입 예측·예방·대응·조치 — 연계점 ' + ' · '.join(o['S']), 12, '#ef6c00', '#bf360c', '#fff', bold=True)
    c.line(510, 137, 560, 137, NAVY, 2); c.line(1040, 137, 1090, 137, RED, 2)
    # 데이터 플로어
    top = 215
    c.text(40, 196, '데이터 플로어 — 받는 것 (IN)', 13, '#2e7d32', 700, 'start')
    c.text(1090, 196, '데이터 플로어 — 주는 것 (OUT)', 13, '#c62828', 700, 'start')
    for col_x, rows, ccol, mk in [(40, IN, '#2e7d32', 'ag'), (1090, OUT, '#c62828', 'ar')]:
        n = max(1, len(rows)); rh = min(70, (bot - top) / n)
        for i, r in enumerate(rows):
            y = top + i * rh
            tag = (r[0] + ' ' + ('↔ ' if r[4] else '') + r[1] + (' [' + r[3] + ']' if r[3] else '') + ': ' + r[2])
            c.box(col_x, y, 470, rh - 5, tag, 11.5, '#fff', sev_col(r[3]) if r[3] else ccol, align='start', pad=6)
            if col_x == 40: c.line(510, y + (rh - 5) / 2, 560, 420, ccol, 1.2, None, mk)
            else: c.line(1040, 420, 1090, y + (rh - 5) / 2, ccol, 1.2, None, mk)
    if not IN:
        c.box(40, top, 470, 60, '접점 없음 (관계 구조도 2.0)', 12, '#f7f7f7', GRAY)
    # 중앙: 조직 상자 + 구성 요소
    c.box(560, 215, 480, 150, o['name'] + '\n' + o['ko'] + ' · 폴더 ' + o['folder'] + '\n' + o['kind'], 14, NAVY, NAVY, '#fff', bold=True)
    c.text(560, 392, '구성 요소', 13, NAVY, 700, 'start')
    el = o['elems']; eh = min(100, (bot - 402) / max(1, len(el)))
    for i, (n, d, src) in enumerate(el):
        c.box(560, 402 + i * eh, 480, eh - 6, n + ': ' + d + ' [' + src + ']', 12, '#eef2ff', '#3b4a8c', align='start', pad=8)
    # 하단 3 패널
    sv = '\n'.join('· ' + a + ': ' + b + ' [' + s + ']' for a, b, s in o['service'])
    c.box(40, y0, 500, PH, sv + '\n\n고객 접점: ' + o['customer'], 13, '#fff', '#2e7d32', align='start', head='서비스 플로어', headcol='#2e7d32')
    cs = D['man']['manuals']; cmap = {m['code']: m for m in cs}
    keys = [3, 5, 8, 11]
    lines = []
    for code in o['cs']:
        m = cmap[code]; lines.append('· ' + code + ' ' + m['name'] + ' — ' + m['channel'])
    lines.append('')
    for code in o['cs'][:1]:
        m = cmap[code]
        for kk, lab in [(1, '주의'), (5, '위기'), (7, '피해발생'), (10, '안정')]:
            s = m['steps'][kk]; lines.append('▶ ' + s['name'] + ': ' + cut(s['say'], 46))
    c.box(570, y0, 520, PH, '\n'.join(lines), 13, '#fff', RED, align='start', head='고객지원 응대 연계 (매뉴얼 ' + ' · '.join(o['cs']) + ')', headcol=RED)
    dt = '\n'.join('· ' + a + ' / 영역 ' + b + ' / ' + c_ + ' / ' + d_ + ' [' + e + ']' for a, b, c_, d_, e in o['data'])
    c.box(1120, y0, 440, PH, '보안체계 연계: ' + o['sec'] + '\n\n데이터 분류(영역 · D · R)\n' + dt, 13, '#fff', '#bf360c', align='start', head='보안체계 연계 · 데이터 분류', headcol='#bf360c')
    return c.svg()


def doc(D, o, idx):
    IN, OUT = flows(D, o)
    cm = {m['code']: m for m in D['man']['manuals']}
    L = []
    a = L.append
    a('# 연계도 %02d · %s — 구성 · 서비스 구성 연계 설명' % (idx, o['name']))
    a('')
    a('문서 SEC · 작성 Sonnet 5.5 · 2026-11-07 · 상태: 작업본(대표님 승인 대기) · 도면: 같은 이름의 svg/pdf · 영역 04.00 · D2 · R1')
    a('')
    a('| 항목 | 내용 |'); a('|---|---|')
    a('| 번호·구분 | %s · %s |' % (o['no'], o['kind']))
    a('| 조직 코드 | %s |' % o['org'])
    a('| 폴더 | %s |' % o['folder'])
    a('| 정의 | %s |' % o['defn'])
    a('| 보안체계 연계점 | %s |' % ' · '.join(o['S']))
    a('| 적용 매뉴얼 | %s |' % ' · '.join(c + ' ' + cm[c]['name'] for c in o['cs']))
    a('')
    a('## 1. 구성 요소'); a('')
    a('| 요소 | 내용 | 근거 |'); a('|---|---|---|')
    for n, d, s in o['elems']: a('| %s | %s | %s |' % (n, d, s))
    a('')
    a('## 2. 데이터 플로어')
    a('')
    if o['key'] in KMAP:
        a('접점 번호는 사업부 관계 구조도 2.0의 C-01~C-30과 같고, 감지 신호·경보 기준·해제 기준은 AICS 경보 기준표(접점 데이터표)의 값입니다.')
        a('')
        for lab, rows in [('받는 것 (IN)', IN), ('주는 것 (OUT)', OUT)]:
            a('### %s' % lab); a('')
            a('| 접점 | 상대 | 내용 | 심각도 | AICS 접점 | 감지 신호 | 경보 기준 | 해제 기준 |'); a('|---|---|---|---|---|---|---|---|')
            for r in rows:
                x = r[4]; a('| %s | %s | %s | %s | %s | %s | %s | %s |' % (r[0], r[1], r[2], r[3], x['AICS 접점'], x['감지 신호'], x['경보 기준'], x['해제 기준']))
            a('')
    else:
        a('이 사업부는 사업군 접점(C-01~C-30)이 없고, 보안체계 연계점으로만 연결됩니다.'); a('')
        a('| 연계점 | 대상 | 보내는 신호 | 받는 조치 · 외부 접점 |'); a('|---|---|---|---|')
        for r in IN: a('| %s | %s | %s | %s |' % (r[0], r[1], r[2], [x for x in OUT if x[0] == r[0]][0][2]))
        a('')
    a('## 3. 서비스 플로어'); a('')
    a('| 서비스 | 내용 | 근거 접점 |'); a('|---|---|---|')
    for n, d, s in o['service']: a('| %s | %s | %s |' % (n, d, s))
    a('')
    a('고객 접점: ' + o['customer']); a('')
    a('## 4. 고객지원 응대 연계 (경보 12단계)'); a('')
    a('| 단계 | ' + ' | '.join(c for c in o['cs']) + ' |'); a('|---|' + '---|' * len(o['cs']))
    for i, st in enumerate(D['man']['steps']):
        a('| %d %s | ' % (i + 1, st) + ' | '.join(cm[c]['steps'][i]['do'].replace('|', '/') for c in o['cs']) + ' |')
    a('')
    a('안내·응대 문구는 각 매뉴얼의 12단계 표(05_매뉴얼)를 따릅니다.'); a('')
    a('## 5. 보안체계 연계'); a(''); a(o['sec']); a('')
    a('| 연계점 | 대상 | 이상 신호 | 조치 | 외부 접점(순위) | 현재 |'); a('|---|---|---|---|---|---|')
    for s in D['em']['link']:
        if s[0] in o['S'] or o['key'] == 'HIVEN통합': a('| ' + ' | '.join(s) + ' |')
    a('')
    a('## 6. 데이터 분류 (Hi DAM 영역 14 · D0~D4 · R0~R4)'); a('')
    a('| 데이터 | 영역 | 데이터 등급 | 보존 등급 | 판정 근거 |'); a('|---|---|---|---|---|')
    for d_, ar, dd, rr, bs in o['data']: a('| %s | %s | %s | %s | %s |' % (d_, ar, dd, rr, 'HIVEN 설계(대표님 승인 전)' if bs == '설계' else bs))
    a('')
    a('신규 사업군(Hi DAM · Hi Serve · Hi Trade)의 영역 범주는 영역 04에 아직 없어 「04.00 그룹통합」을 임시로 씁니다. 범주 신설은 Hi DAM 영역 14 개정에서 정합니다.'); a('')
    a('## 7. 화면 연결'); a('')
    a('SC-02 이상징후 및 보안체계(매뉴얼·종횡단·연계점) · SC-03 침입 예측·예방·대응·조치(경보 기록) · SC-04 사업군 통제(접점 30건) · SC-06 대응·경보 · SC-11 형상·변경(조치 이력)'); a('')
    a('## 8. 확장 (B2C → B2B → B2G)'); a(''); a(o['expand']); a('')
    a('## 9. 확인 상태'); a('')
    a('구성 요소와 정의는 사업구조 확정서 1.2·관계 구조도 2.0·사업군(부) 설명 원문입니다. 서비스 플로어의 고객 접점, 고객지원 매뉴얼 지정, 데이터 분류는 HIVEN 설계값이며 대표님 승인 전입니다. 원문에 없는 항목은 「확인 안 됨」으로 적었습니다.')
    a('')
    return '\n'.join(L)
