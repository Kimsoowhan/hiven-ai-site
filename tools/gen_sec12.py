# -*- coding: utf-8 -*-
"""12_통합사업_이상징후_및_보안체계(SEC) 폴더 일체 생성기 (대표님 2026-11-07 14:39 8번째 지시).
사용: python3 tools/gen_sec12.py <출력 폴더>   (출력 폴더 아래에 12 폴더, 03_STD 반영 파일 폴더 std_out이 만들어진다)
원천: hvEM(views7.js) · cowork/ctl/manuals.json · bg_contact.tsv · sc_renumber_261107.json · tools/man_*.py · tools/sec12_*.py"""
import os, sys, json, csv, re, hashlib, subprocess, shutil, tempfile, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
import man_src, man_work
from sec12_orgs import ORGS
import sec12_diag, sec12_org

MANJ = os.path.join(ROOT, 'cowork', 'ctl', 'manuals.json'); MANJ_BAK = open(MANJ, 'rb').read()
OUTDIR = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/sec12')
FOLDER = '12_통합사업_이상징후_및_보안체계(SEC)'
BASE = os.path.join(OUTDIR, FOLDER)
STD = os.path.join(OUTDIR, 'std_out')
DATE, VER = '261107', '1.0_작업'
SUB = ['01_정책(POL)', '02_설정안(SET)', '03_계획설계(PLN)', '04_보고검토(RPT)', '05_매뉴얼(MAN)', '06_자료(DAT)', '07_관리기록(LOG)', '90_규격표']


def nm(name, ext): return '%s-%s_%s.%s' % (name, DATE, VER, ext)


def W(rel, text, binary=False):
    p = os.path.join(BASE, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    if binary: open(p, 'wb').write(text)
    else: open(p, 'w', encoding='utf-8', newline='\n').write(text)
    return rel


def ext_em():
    js = tempfile.mktemp(suffix='.js')
    open(js, 'w').write('''const vm=require('vm'),fs=require('fs');
const ctx={document:{getElementById(){return null},querySelector(){return null}},V:{},S:[],localStorage:{getItem(){return null},setItem(){}},setInterval(){},setTimeout(){},console,hvgo(){}};
ctx.window=ctx;vm.createContext(ctx);vm.runInContext(fs.readFileSync(process.argv[2],'utf8')+';this.__em=hvEM',ctx);
process.stdout.write(JSON.stringify(ctx.__em));''')
    return json.loads(subprocess.check_output(['node', js, os.path.join(ROOT, 'views7.js')]))


def tsv_rows(path):
    return list(csv.DictReader(open(path, encoding='utf-8'), delimiter='\t'))


def T(h, rows):
    f = lambda x: str(x).replace('|', '/').replace('\n', ' ')
    return '\n'.join(['| ' + ' | '.join(h) + ' |', '|' + '---|' * len(h)] + ['| ' + ' | '.join(f(x) for x in r) + ' |' for r in rows]) + '\n'


HEAD = '문서 SEC · 작성 Sonnet 5.5 · 2026-11-07 · 상태: 작업본(대표님 승인 대기) · 메뉴 번호는 11/07 14:53 확정 배열 기준'
files = []   # (rel, 문서종류, 영역, D, R, 원천, 화면연결)


def reg(rel, kind, area, d, r, src, scr): files.append((rel, kind, area, d, r, src, scr))


def main():
    shutil.rmtree(OUTDIR, ignore_errors=True)
    for s in SUB: os.makedirs(os.path.join(BASE, s), exist_ok=True)
    os.makedirs(STD, exist_ok=True)
    em = ext_em()
    M = man_src.build()
    M['work'] = dict(essence=man_work.ESSENCE, rows=man_work.W)
    ren = json.load(open(os.path.join(ROOT, 'cowork', 'ctl', 'sc_renumber_261107.json'), encoding='utf-8'))
    contacts = tsv_rows(os.path.join(ROOT, 'cowork', 'ctl', 'bg_contact.tsv'))
    pairs = {}
    for r in contacts:
        k = tuple(sorted([r['사업부A'], r['사업부B']], key=lambda x: ['HiASI', 'HiCoffer', 'HiDAM', 'HiICT', 'HiServe', 'HiSilver', 'HiTrade'].index(x)))
        pairs.setdefault(k, []).append(r['번호'])
    D = dict(em=em, man=M, ren=ren, contacts=contacts, pairs=pairs, sev={r['번호']: r['심각도'] for r in contacts})
    assert len(contacts) == 30 and len(pairs) == 20, (len(contacts), len(pairs))

    # ---------------- 03 계획설계: 구조도 13종 ----------------
    for name, fn in sec12_diag.DIAGRAMS:
        svg = fn(D); rel = '03_계획설계(PLN)/구조도/' + nm(name, 'svg')
        W(rel, svg); reg(rel, 'DES', '04.00', 'D2', 'R1', 'tools/sec12_diag.py', 'SC-02·SC-03')
    # ---------------- 03: 사업군·사업부 연계도 10곳 ----------------
    for i, o in enumerate(ORGS, 1):
        base = '연계도%02d_%s' % (i, o['key'])
        rel = '03_계획설계(PLN)/연계도/' + nm(base, 'svg')
        W(rel, sec12_org.diagram(D, o, i)); reg(rel, 'DES', '04.00', 'D2', 'R1', 'tools/sec12_org.py', 'SC-04·SC-02')
        rel = '03_계획설계(PLN)/연계도/' + nm(base + '_설명', 'md')
        W(rel, sec12_org.doc(D, o, i)); reg(rel, 'DES', '04.00', 'D2', 'R1', 'tools/sec12_org.py', 'SC-04·SC-02')

    # ---------------- 01 정책 ----------------
    p = ['# HIVEN 통합사업 이상징후 및 보안체계 정책 1.0', '', HEAD, '',
         '## 1. 위계', '', T(['순위', '체계', '내용'], em['hier']),
         '메뉴 위치: 통합관제 대시보드 SC-01 종합 현황 바로 아래 SC-02(이상징후 및 보안체계), 그 아래 SC-03(침입 예측·예방·대응·조치)이며 기존 화면은 SC-04~SC-16에 배열됩니다(대표님 11/07 14:42·14:45·14:50·14:53).', '',
         '## 2. 제1순위 접근·침입 경로', '', T(['항목', '내용'], em['first']),
         '## 3. 적용 범위', '', T(['구분', '대상'], em['scope']),
         '## 4. 순환 10단계', '', T(['번호', '단계', '내용', '구현 상태'], em['loop']),
         '## 5. 대응 모드 1~10', '', T(['모드', '구분', '의미', '징후', '시스템 조치', '서비스 조치', '고객지원 조치'], em['lv']),
         '## 6. 책임', '', '발령권자와 대행 규칙은 대표님 확정이 필요한 설계값입니다(비상체계 4번). 긴급(7단계) 이상은 대표님이 직접 통제합니다.', '',
         '## 7. 연계 문서', '', '시험 기간 완화 표준(01_정책), 경보 12단계 발령 설정안(02_설정안), 독립 대응 매뉴얼 7종과 비상체계(05_매뉴얼), 구조도 13종과 사업군·사업부 연계도 10곳(03_계획설계).', '']
    rel = W('01_정책(POL)/' + nm('이상징후_보안체계_정책', 'md'), '\n'.join(p)); reg(rel, 'PCY', '04.00', 'D2', 'R1', 'views7.js hvEM', 'SC-02')
    s = ['# 시험 기간 완화 표준 1.0', '', HEAD, '', '## 1. 사유', '', em['std']['why'], '', '## 2. 불변 7원칙', '', T(['원칙', '내용'], em['std']['inv']),
         '## 3. 완화 등록부', '', T(['번호', '항목', '완화값', '운영 기준값', '사유', '종료'], em['std']['reg']),
         '## 4. 역정합 검사', '', '화면 SC-02는 표준 값과 실제 적용 값을 11행으로 거꾸로 대조해 일치 여부를 표시합니다. 등록부에 없는 완화는 하지 않습니다.', '',
         '## 5. 종료', '', '시험 기간 종료는 대표님 지시로만 합니다. 종료하면 등록부 항목 전부를 운영 기준값으로 되돌리고 되돌림 검사를 마칩니다.', '']
    rel = W('01_정책(POL)/' + nm('시험기간_완화_표준', 'md'), '\n'.join(s)); reg(rel, 'PCY', '04.00', 'D2', 'R1', 'views7.js hvEM.std', 'SC-02')

    # ---------------- 02 설정안 ----------------
    s = ['# 경보 12단계 발령 설정안 1.0', '', HEAD, '', '## 1. 12단계', '', T(['번호', '단계', '징후', '순환 단계', '대응 모드', '조치', '표시'], em['al12']),
         '## 2. 외부 연동 대상 순위', '', T(['순위', '정의', '예시', '관측 · 대응', '발령 가중'], em['rank']),
         '## 3. 평시~복구 플로어', '', T(['구분', '단계', '순환 단계', '내용', '외부 순위 관측', '기록'], em['floor']),
         '## 4. 연계점 S-01~S-11', '', T(['번호', '연계 대상', '이상 신호', '조치', '외부 접점(순위)', '현재'], em['link'])]
    rel = W('02_설정안(SET)/' + nm('경보12단계_발령_설정안', 'md'), '\n'.join(s)); reg(rel, 'SET', '04.00', 'D2', 'R1', 'views7.js hvEM', 'SC-02·SC-03')
    s = ['# SC 메뉴 배열 설정안 1.0', '', HEAD, '', '대표님 지시 11/07 14:42·14:45·14:50·14:53. 통합관제 대시보드(ic.hiven.ai.kr · hiven.ai.kr)의 메뉴 배열입니다.', '',
         T(['새 번호', '화면'], [[k, v] for k, v in ren['names'].items()]), '## 옛 번호 → 새 번호', '', T(['옛 번호(11/07 14:42 이전)', '새 번호'], list(ren['map_old_to_new'].items())),
         '11/07 14:42 이전의 이력·기록(모델통제 통합이력, 형상·변경 이력 등)은 당시 번호 그대로이며 위 대응표로 읽습니다. SC-08 베타 배포 모니터링은 창 안에서 베타 1·2·3을 구분합니다(베타 1만 실측 원천 있음).', '']
    rel = W('02_설정안(SET)/' + nm('SC메뉴_배열_설정안', 'md'), '\n'.join(s)); reg(rel, 'SET', '04.00', 'D2', 'R1', 'cowork/ctl/sc_renumber_261107.json', 'SC-01~SC-16')

    # ---------------- 03: 작업 전개표, 확장 로드맵 ----------------
    s = ['# 작업 전개표 1.0 (본질 → 파생 → 선·후행)', '', HEAD, '', M['work']['essence'], '', T(['번호', '구분', '작업', '선행', '후행', '상태', '증빙'], M['work']['rows'])]
    rel = W('03_계획설계(PLN)/' + nm('작업_전개표', 'md'), '\n'.join(s)); reg(rel, 'PLN', '04.00', 'D2', 'R1', 'tools/man_work.py', 'SC-02')
    s = ['# B2C → B2B → B2G 확장 로드맵 1.0', '', HEAD, '', T(['규모', '추가되는 요구', '보안체계 영향', '선행 조건', '확인 상태'], M['expand'])]
    rel = W('03_계획설계(PLN)/' + nm('확장_로드맵_B2C_B2B_B2G', 'md'), '\n'.join(s)); reg(rel, 'PLN', '04.00', 'D2', 'R1', 'tools/man_src.py', 'SC-02')
    # 연계 총괄 문서
    rows = []
    for o in ORGS:
        IN, OUT = sec12_org.flows(D, o)
        rows.append([o['no'], o['name'], o['org'], o['folder'], len(IN), len(OUT), ' · '.join(o['S']), ' · '.join(o['cs']), '; '.join(x[0] for x in o['elems'])])
    s = ['# 사업군 · 사업부 구성 · 서비스 구성 연계 총괄 1.0', '', HEAD, '',
         '사업군 7 + 별도 사업부 2 + 통합(HV) = 10곳. 각 곳의 연계도(svg/pdf)와 설명(md)은 같은 폴더에 있습니다. 접점 수는 접점 30건 기준(사업군) 또는 연계점 S 기준(그 밖)입니다.', '',
         T(['번호', '사업군·사업부', '조직 코드', '폴더', '받는 것(IN)', '주는 것(OUT)', '보안 연계점', '적용 매뉴얼', '구성 요소'], rows),
         '## 접점 30건 (20쌍)', '', T(['쌍', '접점'], [[a + ' ↔ ' + b, ' · '.join(v)] for (a, b), v in pairs.items()]),
         '검증: 접점 30건 = 쌍 20개, 심각도 상 %d건 · 중 %d건.' % (sum(1 for r in contacts if r['심각도'] == '상'), sum(1 for r in contacts if r['심각도'] == '중')), '']
    rel = W('03_계획설계(PLN)/연계도/' + nm('연계도00_총괄', 'md'), '\n'.join(s)); reg(rel, 'PLN', '04.00', 'D2', 'R1', 'bg_contact.tsv·tools/sec12_orgs.py', 'SC-04')

    # ---------------- 04 보고검토 ----------------
    rel = W('04_보고검토(RPT)/' + nm('벤치마킹_근거', 'md'), '\n'.join(['# 벤치마킹 근거 %d건 1.0' % len(M['bench']), '', HEAD, '', T(['출처', '핵심', 'HIVEN 반영', '확인 상태'], M['bench'])])); reg(rel, 'RPT', '08.01', 'D1', 'R2', 'tools/man_bench.py', 'SC-02')
    rel = W('04_보고검토(RPT)/' + nm('법정_기한_통지_항목표', 'md'), '\n'.join(['# 법정 기한 · 통지 항목표 1.0', '', HEAD, '', T(['근거', '기한 · 내용', '확인 상태'], M['law']), '언론·미러 요약만 확인한 항목은 법령 원문 대조가 필요하며, 적용 여부가 확인되지 않은 항목은 「확인 안 됨」입니다.', ''])); reg(rel, 'RPT', '07.04', 'D1', 'R2', 'tools/man_bench.py', 'SC-02')
    rel = W('04_보고검토(RPT)/' + nm('조치후_피해_예방표', 'md'), '\n'.join(['# 조치 후 예측 피해 → 예방 조치 1.0', '', HEAD, '', T(['조치', '예상 피해', '예방 조치', '근거'], M['damage'])])); reg(rel, 'RPT', '04.00', 'D2', 'R1', 'tools/man_bench.py', 'SC-02')
    rel = W('04_보고검토(RPT)/' + nm('사례_실수_예방표', 'md'), '\n'.join(['# 사례에서 뽑은 실수와 예방 1.0', '', HEAD, '', T(['사례', '실수', '예방', '확인 상태'], M['mistakes']), '## 후속 요건', ''] + ['- ' + x for x in M['follow']] + [''])); reg(rel, 'RPT', '08.01', 'D1', 'R2', 'tools/man_bench.py', 'SC-02')

    # ---------------- 05 매뉴얼 ----------------
    tmp = tempfile.mkdtemp(); subprocess.check_call([sys.executable, os.path.join(HERE, 'man_src.py'), tmp], stdout=subprocess.DEVNULL)
    for f in sorted(os.listdir(tmp)):
        txt = open(os.path.join(tmp, f), encoding='utf-8').read()
        m = re.match(r'HIVEN_(M\d)_(.+)_261107\.md', f)
        if m: name = '%s_%s' % (m.group(1), m.group(2))
        else: name = '종횡단_일람_작업전개'
        rel = W('05_매뉴얼(MAN)/' + nm(name, 'md'), txt); reg(rel, 'MAN', '04.00', 'D2', 'R1', 'tools/man_src.py', 'SC-02')
    s = ['# 비상체계 가동 · 해제 기준 1.0', '', HEAD, ''] + sum([['## ' + k, ''] + ['- ' + x for x in v] + [''] for k, v in M['emergency'].items()], [])
    rel = W('05_매뉴얼(MAN)/' + nm('비상체계_가동_해제_기준', 'md'), '\n'.join(s)); reg(rel, 'MAN', '04.00', 'D2', 'R1', 'tools/man_src.py', 'SC-02·SC-06')

    # ---------------- 06 자료 (정합 데이터) ----------------
    def tsv(rel, head, rows, src, scr, d='D2', r='R1', area='00.05'):
        W(rel, '\n'.join('\t'.join(str(x).replace('\t', ' ').replace('\n', ' ') for x in row) for row in [head] + rows) + '\n'); reg(rel, 'REG', area, d, r, src, scr)
    keys = list(contacts[0].keys())
    tsv('06_자료(DAT)/' + nm('접점_C01_C30_데이터표', 'tsv'), keys, [[r[k] for k in keys] for r in contacts], 'cowork/ctl/bg_contact.tsv', 'SC-04')
    tsv('06_자료(DAT)/' + nm('보안연계점_S01_S11', 'tsv'), ['번호', '연계 대상', '이상 신호', '조치', '외부 접점(순위)', '현재'], em['link'], 'views7.js hvEM.link', 'SC-02·SC-03')
    rows = []
    for o in ORGS:
        for n, d_, s_ in o['elems']: rows.append([o['no'], o['name'], o['org'], '구성 요소', n, d_, s_])
        for n, d_, s_ in o['service']: rows.append([o['no'], o['name'], o['org'], '서비스 플로어', n, d_, s_])
        for d_, ar, dd, rr, bs in o['data']: rows.append([o['no'], o['name'], o['org'], '데이터 분류', d_, '영역 %s · %s · %s' % (ar, dd, rr), 'HIVEN 설계(승인 전)'])
        rows.append([o['no'], o['name'], o['org'], '고객지원 매뉴얼', ' · '.join(o['cs']), o['customer'], 'HIVEN 설계(승인 전)'])
        rows.append([o['no'], o['name'], o['org'], '보안체계 연계', ' · '.join(o['S']), o['sec'], 'S-01~S-11'])
    tsv('06_자료(DAT)/' + nm('사업군_사업부_요소_대장', 'tsv'), ['번호', '사업군·사업부', '조직 코드', '구분', '이름', '내용', '근거·판정'], rows, 'tools/sec12_orgs.py', 'SC-04')
    rows = []
    for o in ORGS:
        IN, OUT = sec12_org.flows(D, o)
        for r in IN: rows.append([o['name'], 'IN', r[0], r[1], r[2], r[3]])
        for r in OUT: rows.append([o['name'], 'OUT', r[0], r[1], r[2], r[3]])
    tsv('06_자료(DAT)/' + nm('데이터플로어_IN_OUT_대장', 'tsv'), ['사업군·사업부', '방향', '접점', '상대', '내용', '심각도'], rows, 'bg_contact.tsv·hvEM.link', 'SC-04')
    rows = []
    for i, st in enumerate(M['steps']):
        for cr in M['cross'][i]['rows']: rows.append([i + 1, st, cr['code'], cr['label'], cr['do'], cr['say']])
    tsv('06_자료(DAT)/' + nm('경보12단계_매뉴얼7종_행동표', 'tsv'), ['단계번호', '단계', '매뉴얼', '이름', '해야 할 일', '안내 문구'], rows, 'cowork/ctl/manuals.json', 'SC-02')
    tsv('06_자료(DAT)/' + nm('SC번호_대응표', 'tsv'), ['옛 번호', '새 번호', '새 화면 이름'], [[k, v, ren['names'][v]] for k, v in ren['map_old_to_new'].items()], 'cowork/ctl/sc_renumber_261107.json', 'SC-01~SC-16')

    # ---------------- 07 관리기록 ----------------
    chain = [
        ('13:39~13:58', '상하 체계(자동화 통합 통제 → 이상징후·보안체계 → 침입 예측/예방/대응/조치), 외부 연동 대상 순위, 경보 12단계, 구조도', '구조도 1.0, SC-02·SC-03 화면', '완료'),
        ('14:03', '제1순위 접근·침입 경로(ic 인트로 열쇠) 각인', '화면·구조도 01', '완료'),
        ('14:06', '시험 기간 완화 표준(불변 7원칙, 등록부, 역정합)', '01_정책 시험기간_완화_표준', '완료'),
        ('14:10', '서비스(고객용·관리자용)와 고객지원 독립 매뉴얼, 본질·파생 작업 전개', '05_매뉴얼 M1~M7', '완료'),
        ('14:12', '벤치마킹 선행(절차·행위·후속 요건·피해·예방)', '04_보고검토', '완료(원문 확인 표시)'),
        ('14:21', '5번째 마지막 엄중 지시: 자동화 통합 통제 시스템에 귀속하는 최상의 보안체계, B2C→B2B→B2G 대비', '확장 로드맵', '완료'),
        ('14:27', '7번째: 원패스, 종단↔횡단 통제, 웹 실시간 적용, 재정합', 'SC-02 실시간 패널', '완료'),
        ('14:39', '8번째: 모든 구조도 개별 수립, 사업군·사업부별 구성·서비스 구성 연계도, 12번 폴더, HiDAM 분류 정합, 91번 기록, 검사표 1회', '이 폴더 전체', '완료(결과표 제출)'),
        ('14:42', 'SC-02 최상위 승격, 기존 메뉴 하위', 'SC 메뉴 배열 설정안', '완료'),
        ('14:45', 'SC-03 침입 예측·예방·대응·조치, 기존 메뉴 두 칸 하위', 'SC 메뉴 배열 설정안', '완료'),
        ('14:50', '지정 순서 배열, SC 베타 배포 모니터링 창 안에서 베타 1·2·3 구분', 'SC 메뉴 배열 설정안', '완료'),
        ('14:53', '대응·경보를 SC-06으로, 말 명령을 SC-16 맨 아래로', 'SC 메뉴 배열 설정안', '완료(ic 라이브 확인)'),
        ('14:54', '실제 사이트 반영 확인 후 폴더 구조도·사업군별 연계도 생성 완수·정립', '이 폴더 전체', '진행 후 결과표')]
    tsv('07_관리기록(LOG)/' + nm('지시_작업기록', 'tsv'), ['시각(11/07)', '지시 요지', '반영 위치', '결과'], [list(x) for x in chain], '대표님 지시 14:39 규칙', 'SC-14', 'D2', 'R0', '00.03')
    W('07_관리기록(LOG)/' + nm('SC번호_재배정_기록', 'json'), json.dumps(ren, ensure_ascii=False, indent=1)); reg('07_관리기록(LOG)/' + nm('SC번호_재배정_기록', 'json'), 'LOG', '00.03', 'D2', 'R0', 'cowork/ctl/sc_renumber_261107.json', 'SC-11')
    return D


if __name__ == '__main__':
    D = main()
    import sec12_post
    CK = sec12_post.run(BASE, STD, files, D, ORGS, FOLDER, DATE, VER, nm)
    for a, b, c in CK: print(b, a, c)
    open(MANJ, 'wb').write(MANJ_BAK)  # man_src.build()가 덮어쓴 manuals.json을 원래대로 복원(원천 파일은 건드리지 않는다)
    json.dump(files, open(os.path.join(OUTDIR, '_files.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('files', len(files))
