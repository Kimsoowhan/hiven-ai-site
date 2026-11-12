# -*- coding: utf-8 -*-
"""12번 폴더 후처리: PDF 변환 · 폴더안내 · 90_규격표(문서분류대장·폴더연계표·정합검사결과·SEC 코드등록·폴더표 0.4) · 03_STD 복사본.
gen_sec12.py 의 main() 뒤에 호출된다."""
import os, re, csv, json, glob, hashlib, shutil, subprocess

BOM = '\ufeff'
PC_PREFIX = r'C:\Users\marty\Documents\HiBiz' + '\\'
AREAS = {'00', '00.01', '00.02', '00.03', '00.04', '00.05', '01', '02', '03', '04', '04.00', '04.01', '04.02', '04.03', '04.05', '04.30', '04.90', '05', '06', '07', '07.04', '08', '08.01', '09', '10', '97'}
KIND_FMT = {'svg': '벡터 그림(SVG)', 'pdf': '인쇄용 그림(PDF)', 'md': '문서(MD)', 'tsv': '표(TSV)', 'json': '기록(JSON)', 'txt': '텍스트(TXT)'}
FOLDER_USE = [
    ('01_정책(POL)', 'POL', '정책·기준 문서(이상징후·보안체계 정책, 시험 기간 완화 표준)', 'PCY', 'HID의 00_기준원칙에 해당'),
    ('02_설정안(SET)', 'SET', '설정·배열 안(경보 12단계 발령 설정안, SC 메뉴 배열 설정안)', 'SET', ''),
    ('03_계획설계(PLN)', 'PLN', '구조도 13종·사업군 사업부별 연계도 10종(SVG·PDF)과 설명, 작업 전개표, 확장 로드맵', 'PLN·DES', ''),
    ('04_보고검토(RPT)', 'RPT', '벤치마킹·법정 기한·피해→예방·실수 예방 보고서', 'RPT', ''),
    ('05_매뉴얼(MAN)', 'MAN', '매뉴얼 M1~M7, 종횡단 일람, 비상체계 가동·해제 기준', 'MAN', ''),
    ('06_자료(DAT)', 'DAT', '데이터 원장(접점 C-01~C-30, 연계점 S-01~S-11, 사업군·사업부 요소, IN/OUT, 12단계×7매뉴얼)', 'REG·SRC', ''),
    ('07_관리기록(LOG)', 'LOG', '지시·작업 기록, SC 번호 재배정 기록', 'LOG', 'HID의 70_작업기록(LOG)에 해당'),
    ('90_규격표', '규격', '문서분류대장(해시), 폴더연계표, 정합검사결과, SEC 코드등록, 폴더표 0.4', 'REG·STD', 'HID의 90_규격표와 같은 위치'),
]


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def wr(p, text, bom=True):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8', newline='\n').write((BOM if bom else '') + text)


def tsv_text(head, rows):
    f = lambda x: str(x).replace('\t', ' ').replace('\n', ' ')
    return '\n'.join(['\t'.join(head)] + ['\t'.join(f(c) for c in r) for r in rows]) + '\n'


def run(base, std, files, D, ORGS, FOLDER, DATE, VER, nm):
    """files: gen_sec12.files (rel, 종류, 영역, D, R, 원천, 화면) — 이 함수가 PDF 등을 추가 등록한다."""
    # 1) SVG -> PDF
    for rel in [f[0] for f in list(files) if f[0].endswith('.svg')]:
        src = os.path.join(base, rel); pdf = src[:-4] + '.pdf'
        subprocess.check_call(['rsvg-convert', '-f', 'pdf', src, '-o', pdf])
        k = next(f for f in files if f[0] == rel)
        files.append((rel[:-4] + '.pdf', k[1], k[2], k[3], k[4], k[5], k[6]))
    # 2) 폴더안내 (루트)
    n_by = {}
    for f in files: n_by[f[0].split('/')[0]] = n_by.get(f[0].split('/')[0], 0) + 1
    n_by['90_규격표'] = 5
    g = [FOLDER + ' 폴더 안내 (2026-11-07, 작업본, 대표님 승인 대기)',
         '이 폴더는 HIVEN 통합사업 이상징후 및 보안체계(SC-03)와 침입 예측·예방·대응·조치 시스템(SC-04)의 구조도, 사업군·사업부별 구성·서비스 구성 연계도, 매뉴얼 7종, 정책·설정안, 데이터 원장, 관리 기록을 한곳에 두는 정본 위치입니다.', '',
         '위계: 최상위 자동화 통합 통제 시스템 ⊃ SC-03 이상징후 및 보안체계 시스템(최우선) ⊃ SC-04 침입 예측·예방·대응·조치 시스템', '']
    for fo, code, use, ccs, hid in FOLDER_USE:
        g.append('%-22s %s (파일 %d개)' % (fo, use, n_by.get(fo, 0)))
    g += ['',
          '하위 구분: 03_계획설계(PLN) 안에 구조도 / 연계도 두 폴더를 둔다. 구조도는 SVG와 PDF를 짝으로 둔다.',
          '파일 이름: 이름-YYMMDD_x.x[_작업].확장자 (NM-1, 띄어쓰기·특수문자 없음). 작성 상태는 _작업(작업본)이며 대표님 승인 후 확정본으로 바꾼다.',
          '분류: 문서 종류는 CCS 코드(PCY·SET·PLN·RPT·MAN·REG·LOG·DES), 데이터 영역·기밀 D·보존 R은 90_규격표의 문서분류대장에 파일마다 적는다. 해시(sha256)도 같이 적는다.',
          '화면 연결: SC-03·SC-04·SC-05·SC-07 등 통합관제 대시보드 번호는 2026-11-07 14:53 확정 배열 기준이며, 옛 번호 대응은 06_자료의 SC번호_대응표로 읽는다.',
          '코드: SEC = 이 폴더의 약어(SECurity). 03_기준_명명분류(STD)에 SEC_코드등록과 폴더표 0.4를 함께 둔다.',
          '확인 상태: 법령·벤치마킹 일부는 언론·미러 요약만 확인했고, 내부 시한(1·6·24·72시간)과 발령권자 대행 규칙은 설계값으로 대표님 확정이 필요하다. 각 문서의 확인 상태 열을 따른다.']
    wr(os.path.join(base, '폴더안내-%s.txt' % DATE), '\n'.join(g) + '\n')
    files.append(('폴더안내-%s.txt' % DATE, 'MAN', '04.00', 'D2', 'R1', '대표님 지시 14:39 (c)', 'SC-03'))
    # 3) 코드 등록 · 폴더표 0.4 (90_규격표 + std_out)
    stdscan = '/mnt/user-data/uploads/HiBiz/03_기준_명명분류(STD)'
    hits = 0
    if os.path.isdir(stdscan):
        for p in glob.glob(stdscan + '/*'):
            try: hits += len(re.findall(r'(?<![A-Za-z])SEC(?![A-Za-z])', open(p, encoding='utf-8-sig', errors='ignore').read()))
            except Exception: pass
    code_head = ['코드', '대상', '뜻', '종류', '근거', '충돌 검사', '상태', '등록 시각']
    code_row = ['SEC', '12_통합사업_이상징후_및_보안체계', 'SECurity(이상징후 및 보안체계)', 'HiBiz 폴더 약어(영문 대문자 3자)',
                'CCS 0.1 C-1·C-2·C-4, HID 선례(11번 신설과 같은 방식)',
                '2026-11-07 03_STD 폴더 안 파일 본문 검색에서 단독 사용 %d건(HID_코드등록 포함), 예약 HG·HGS와 다름, 옛 2글자 코드와 다름, 폴더 번호 12는 11(HID)과 20(통합사업) 사이 빈 번호' % hits,
                '작업본(대표님 승인 대기)', '2026-11-07 15:00']
    codef = 'SEC_코드등록-%s_%s.tsv' % (DATE, VER)
    wr(os.path.join(base, '90_규격표', codef), tsv_text(code_head, [code_row]))
    wr(os.path.join(std, codef), tsv_text(code_head, [code_row]))
    t04 = ['폴더표 0.4 SEC 반영본 — 12_통합사업_이상징후_및_보안체계(SEC) 신설 (2026-11-07, 작업본, 대표님 승인 대기)',
           '대상: 03_기준_명명분류(STD) 폴더표 0.3 · 04_형상관리(CFG) 경로표',
           '범위: 12번 폴더(SEC)만. 11_하이브그룹_아이덴티티(HID)와 21_브랜드_지식재산(BIP)은 그대로 둔다.', '',
           '1. 추가 행: 12_통합사업_이상징후_및_보안체계(SEC) | 코드 SEC | HIVEN 통합사업 이상징후 및 보안체계(SC-03)·침입 예측·예방·대응·조치(SC-04) 구조도·연계도·매뉴얼·정책·원장 | 최상위 자동화 통합 통제 시스템에 귀속 | 상태: 작업본(승인 대기)',
           '2. 코드 규칙: SEC는 새 코드이므로 등록부에 등록(C-4) — 03_STD\\%s (작업본)' % codef,
           '3. 1단 폴더 수: 24개 → 25개(0.3 기준, 24_마케팅(MKT)은 계속 미사용)',
           '4. 경로표: 12 폴더 경로와 90_규격표의 문서분류대장·폴더연계표를 등록 — 04_형상관리(CFG) 쪽 반영은 04_CFG 목록이 부분 확인 상태라 승인 후 맞춘다(확인 안 됨)',
           '5. 정합성: 12번은 기존 번호에서 비어 있음(11 → 20 사이), 충돌 없음',
           '6. 분류 기준: 문서 종류는 CCS, 영역은 데이터 분류 영역(주로 04.00 그룹통합, 경보 기록은 00.03), 기밀 D2, 보존 R1. 사업군·사업부 범주 중 신설 전인 것은 04.00을 임시 영역으로 쓴다.',
           '7. 대표님 확인 필요: 폴더 번호 12 사용, 코드 SEC 확정, 전사경영부·미래전략사업부·HIVEN통합 데이터 영역 확정']
    t04f = '폴더표_0.4_SEC반영-%s_%s.txt' % (DATE, VER)
    wr(os.path.join(base, '90_규격표', t04f), '\n'.join(t04) + '\n'); wr(os.path.join(std, t04f), '\n'.join(t04) + '\n')
    # 4) 폴더연계표
    rows = []
    for fo, code, use, ccs, hid in FOLDER_USE:
        cnt = 4 if fo == '90_규격표' else len([f for f in files if f[0].startswith(fo + '/')])
        rows.append([fo, code, use, ccs, hid or '-', cnt])
    rows.append(['(루트)', '-', '폴더안내 1개', 'MAN', 'HID의 폴더안내와 같은 위치', 1])
    wr(os.path.join(base, '90_규격표', '폴더연계표-%s_%s.tsv' % (DATE, VER)), tsv_text(['폴더', '코드', '용도', '허용 문서 종류(CCS)', 'HID 선례 대응', '파일 수(대장 제외)'], rows))
    # 5) 정합검사결과 (대장 만들기 전, 대장 외 파일 대상)
    ck = []
    def chk(name, ok, detail): ck.append((name, 'PASS' if ok else 'FAIL', detail))
    chk('접점 C-01~C-30 수', len(D['contacts']) == 30, '%d행' % len(D['contacts']))
    chk('접점 쌍 수(사업부 7개 중 2개씩)', len(D['pairs']) == 20, '%d쌍' % len(D['pairs']))
    sset = set(s for o in ORGS for s in o['S'])
    allS = {'S-%02d' % i for i in range(1, 12)}
    chk('연계점 S-01~S-11이 사업군·사업부 연계도에 모두 쓰임', allS <= sset, '누락 %s' % sorted(allS - sset))
    steps = D['man']['steps']; cross = D['man']['cross']
    chk('경보 12단계 × 매뉴얼 7종 = 84칸', len(steps) == 12 and all(len(c['rows']) == 7 for c in cross) and len(cross) == 12, '단계 %d, 칸 %d' % (len(steps), sum(len(c['rows']) for c in cross)))
    m = D['ren']['map_old_to_new']
    chk('SC 번호 대응 일대일(16개)', len(m) == 16 and sorted(m.values()) == ['SC-%02d' % i for i in range(1, 17)], '%d건' % len(m))
    names = D['ren']['names']
    stale = []
    texts = {}
    for f in files:
        if f[0].endswith(('.md', '.svg', '.txt', '.tsv')):
            p = os.path.join(base, f[0])
            if os.path.exists(p): texts[f[0]] = open(p, encoding='utf-8-sig').read()
    for rel, t in texts.items():
        if 'SC번호_' in rel or 'SC메뉴_배열' in rel or '구조도13' in rel or '지시_작업기록' in rel: continue
        for sid in names:
            for sid2, nn in names.items():
                if sid != sid2 and (sid + ' ' + nn) in t: stale.append((rel, sid + ' ' + nn))
    chk('문서 안 SC 번호와 화면 이름이 14:53 배열과 어긋난 곳', not stale, '%d곳 %s' % (len(stale), stale[:3]))
    bad_nm = [f[0] for f in files if not re.match(r'^[^\s]+\.[a-z0-9]+$', os.path.basename(f[0])) or re.search(r'[\s&%#@!$^*+=<>?|\\"]', os.path.basename(f[0]))]
    chk('파일 이름 규칙(NM-1) 위반', not bad_nm, '%d개 %s' % (len(bad_nm), bad_nm[:3]))
    nover = [f[0] for f in files if not re.search(r'-\d{6}(_\d+\.\d+(_작업)?)?\.[a-z0-9]+$', os.path.basename(f[0]))]
    chk('이름에 날짜(YYMMDD) 없음', not nover, '%d개 %s' % (len(nover), nover[:3]))
    dep = max(len(f[0].split('/')) for f in files)
    chk('폴더 깊이 4 이하(12 폴더 기준 파일 포함 단계)', dep <= 4, '최대 %d단계' % dep)
    longest = max(len(PC_PREFIX + FOLDER + '\\' + f[0].replace('/', '\\')) for f in files) 
    chk('PC 전체 경로 240자 이하', longest <= 240, '최장 %d자' % longest)
    svgs = [f[0] for f in files if f[0].endswith('.svg')]
    chk('SVG마다 PDF 짝', all(os.path.exists(os.path.join(base, s[:-4] + '.pdf')) for s in svgs), 'SVG %d / PDF %d' % (len(svgs), len([f for f in files if f[0].endswith('.pdf')])))
    badcls = [f[0] for f in files if f[2] not in AREAS or f[3] not in ('D0', 'D1', 'D2', 'D3', 'D4') or f[4] not in ('R0', 'R1', 'R2', 'R3', 'R4')]
    chk('분류 값(영역·D·R)이 분류 체계 안에 있음', not badcls, '%d개 %s' % (len(badcls), badcls[:3]))
    miss = [f[0] for f in files if not os.path.exists(os.path.join(base, f[0]))]
    chk('대장에 올린 파일이 실제로 있음', not miss, '누락 %d' % len(miss))
    ccs_ok = {'SET', 'PLN', 'STD', 'RPT', 'PRP', 'PCY', 'DES', 'MAN', 'LOG', 'REG', 'TLS', 'SRC', 'ALL'}
    chk('문서 종류가 CCS 코드 안에 있음', all(f[1] in ccs_ok for f in files), '종류 %s' % sorted(set(f[1] for f in files)))
    chk('SEC 코드 충돌(03_STD 본문 검색)', hits == 0, '%d건' % hits)
    body = ['# 정합검사 결과 1.0', '', '문서 SEC · 작성 Sonnet 5.5 · 2026-11-07 · 작업본(대표님 승인 대기). 생성기(tools/gen_sec12.py → sec12_post.py)가 자동으로 검사한 결과입니다.', '',
            '| 검사 | 결과 | 내용 |', '|---|---|---|'] + ['| %s | %s | %s |' % (a, b, c.replace('|', '/')) for a, b, c in ck] + ['',
            '검사하지 못하는 것(확인 안 됨): 사업군·사업부 데이터 영역 확정, 법령 원문 대조(언론·미러 요약 항목), PC 사본 해시 비교는 배치 후 별도 대조.']
    wr(os.path.join(base, '90_규격표', '정합검사결과-%s_%s.md' % (DATE, VER)), '\n'.join(body) + '\n', bom=False)
    # 6) 대장에 90 파일 등록 후 문서분류대장 (대장 자신 제외)
    for fn, kind in [(codef, 'REG'), (t04f, 'STD'), ('폴더연계표-%s_%s.tsv' % (DATE, VER), 'REG'), ('정합검사결과-%s_%s.md' % (DATE, VER), 'REG')]:
        files.append(('90_규격표/' + fn, kind, '00.05', 'D2', 'R1', 'tools/sec12_post.py', 'SC-03'))
    led = []
    for f in sorted(files):
        p = os.path.join(base, f[0]); ext = f[0].rsplit('.', 1)[-1]
        led.append([f[0].rsplit('/', 1)[0] if '/' in f[0] else '(루트)', os.path.basename(f[0]), f[1], KIND_FMT.get(ext, ext), f[2], f[3], f[4], os.path.getsize(p), sha(p), f[5], f[6]])
    wr(os.path.join(base, '90_규격표', '문서분류대장-%s_%s.tsv' % (DATE, VER)),
       tsv_text(['폴더', '파일명', '문서 종류(CCS)', '파일 형식', '데이터 영역', '기밀(D)', '보존(R)', '바이트', 'sha256', '원천', 'SC 화면 연결'], led))
    return ck
