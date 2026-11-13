#!/usr/bin/env python3
"""규칙 검사 묶음(판정 138 ② · 147 ③, 11-13 Fable 판정 · Opus 5.5 구현). precheck ⑯ 이 부른다.
점검표 14줄 가운데 「검사 없음」이던 줄을 5 → 6 → 7 → 9 → 10 → 13 차례로 검사한다. 읽기만 하고 원천을 고치지 않는다.
  줄 5  고객 접수 → 분류 → 대장: cs_inbox_raw 원문 해시 64자 · 원본 딱지 · 빈 틀 셋의 머리 칸 · 초안 인용 같음(빈-R2b) · 딱지 다르면 멈춤(빈-R4)
  줄 6  딱지 규칙(데-2): 등록부·원장 구분 칸 = 딱지 여덟 값 + 「점검」(판정 132)
  줄 7  원본 불변·짝 파일: 원천 대장은 뒤에 붙이기만(앞 내용 sha256 이 기준값과 같아야 함) — 기준값 cowork/ctl/source_prefix_base.tsv
  줄 9  정보원 대장: 13칸 · 「마지막 확인」 칸 빈 줄 0
  줄 10 음성 지시 두 칸: voice_original 줄마다 인식 원문·보정문이 있고 이력 번호가 이력에 있음
  줄 13 구성 변경의 Fable 확인: 확인 대기 줄의 원천 해시(앞 16자)가 지금 파일과 같음(다르면 알림 — 확인 전 바뀜)
  147 ③ phrase_scan.json 기준 이력 건수 · trace_sum 기준 이력 건수와 지금 이력 건수의 차이(알림)
출력: 「실패: …」「알림: …」 줄과 마지막 요약 줄. 종료 코드 1 = 실패 있음.
기준값 갱신: 줄 7 은 검사가 통과하면 기준값을 지금 크기로 옮긴다(붙인 줄은 받아들이고, 앞 내용이 바뀌면 실패로 남는다)."""
import os, sys, csv, re, json, hashlib
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(R, 'cowork', 'ctl')
sys.path.insert(0, os.path.join(R, 'tools'))
import ev_pack
bad, note = [], []
def fail(m): bad.append(m); print('실패:', m)
def warn(m): note.append(m); print('알림:', m)
def rows(f):
    p = os.path.join(C, f)
    if not os.path.exists(p): return None, None
    t = list(csv.reader(open(p, encoding='utf-8-sig'), delimiter='\t'))
    return (t[0], t[1:]) if t else ([], [])

# ── 줄 5
h, rs = rows('cs_inbox_raw.tsv')
if h is None: fail('줄5 cs_inbox_raw.tsv 없음')
else:
    for i, r in enumerate(rs, 2):
        if len(r) < 5 or not re.fullmatch(r'[0-9a-f]{64}', r[3].strip()): fail('줄5 cs_inbox_raw %d행 원문 해시가 sha256 64자가 아님' % i)
        elif r[4].strip() not in ev_pack.LABELS + ('원본',): fail('줄5 cs_inbox_raw %d행 원본 딱지 「%s」가 여덟 값·원본 밖' % (i, r[4][:20]))
FR = {'draft_quote_check.tsv': ['초안 번호', '같음/다름'], 'reply_value_label_check.tsv': ['확인 번호', '딱지 같음/다름', '판정(통과/멈춤)'], 'quarantine.tsv': ['번호', '딱지', '상태']}
for f, need in FR.items():
    h, rs = rows(f)
    if h is None: fail('줄5 %s 없음' % f); continue
    miss = [k for k in need if k not in h]
    if miss: fail('줄5 %s 머리 칸 없음: %s' % (f, ','.join(miss))); continue
    for i, r in enumerate(rs, 2):
        r = r + [''] * (len(h) - len(r))
        if f == 'draft_quote_check.tsv' and r[h.index('같음/다름')].strip() not in ('같음', ''): fail('줄5 초안 인용이 원문과 다름(빈-R2b) %d행 %s' % (i, r[0]))
        if f == 'reply_value_label_check.tsv' and r[h.index('딱지 같음/다름')].strip() == '다름' and r[h.index('판정(통과/멈춤)')].strip() != '멈춤': fail('줄5 회신 값 딱지가 다른데 멈춤이 아님(빈-R4) %d행 %s' % (i, r[0]))
        if f == 'quarantine.tsv' and r[h.index('딱지')].strip() and r[h.index('딱지')].strip() not in ev_pack.LABELS: fail('줄5 격리 대장 %d행 딱지 「%s」가 여덟 값 밖' % (i, r[h.index('딱지')][:20]))

# ── 줄 6
h, rs = rows('ev_registry.tsv')
if h is None or '구분' not in h: fail('줄6 ev_registry.tsv 구분 칸 없음')
else:
    k = h.index('구분')
    out = [r[0] for r in rs if r and (len(r) <= k or r[k].strip() not in ev_pack.LABELS)]
    if out: fail('줄6 등록부 구분 칸이 여덟 값·점검 밖 %d줄: %s' % (len(out), ','.join(out[:5])))
h, rs = rows('ev_ledger.tsv')
if h is not None:
    if h[-1:] != ['구분']: fail('줄6 증적 원장 머리줄 끝 칸이 「구분」이 아님')
    for i, r in enumerate(rs, 2):
        if len(r) >= 9 and r[8].strip() not in ev_pack.LABELS: fail('줄6 증적 원장 %d행 구분 「%s」가 여덟 값·점검 밖' % (i, r[8][:20]))

# ── 줄 7 (원천 대장은 붙이기만)
SRC = ['cs_inbox.tsv', 'cs_tickets.tsv', 'cs_inbox_raw.tsv', 'voice_original.tsv', 'ev_ledger.tsv', 'source_ledger.tsv']
BASE = os.path.join(C, 'source_prefix_base.tsv')
base = {}
if os.path.exists(BASE):
    for r in list(csv.reader(open(BASE, encoding='utf-8'), delimiter='\t'))[1:]:
        if len(r) >= 3: base[r[0]] = (int(r[1]), r[2])
newb, bad7 = {}, 0
for f in SRC:
    p = os.path.join(C, f)
    if not os.path.exists(p): continue
    b = open(p, 'rb').read()
    if f in base:
        n, hx = base[f]
        if len(b) < n or hashlib.sha256(b[:n]).hexdigest() != hx:
            fail('줄7 원천 %s 앞 내용이 기준값(%d바이트 · %s)과 다름 — 붙이기만 허용, 고친 까닭을 이력에 올리고 기준값을 다시 잡아야 함' % (f, n, hx[:12])); bad7 += 1
            newb[f] = base[f]; continue
    newb[f] = (len(b), hashlib.sha256(b).hexdigest())
if not bad7 and newb != base:
    with open(BASE, 'w', encoding='utf-8') as o:
        o.write('원천 파일\t기준 바이트\t앞 내용 sha256\n')
        for f in SRC:
            if f in newb: o.write('%s\t%d\t%s\n' % (f, newb[f][0], newb[f][1]))

# ── 줄 9
h, rs = rows('source_ledger.tsv')
if h is None: fail('줄9 source_ledger.tsv 없음')
else:
    if len(h) != 13 or h[-1] != '마지막 확인': fail('줄9 정보원 대장 머리가 13칸·「마지막 확인」이 아님(%d칸)' % len(h))
    for i, r in enumerate(rs, 2):
        if len(r) != len(h): fail('줄9 정보원 대장 %d행 칸 수 %d' % (i, len(r)))
        elif not r[-1].strip(): fail('줄9 정보원 대장 %d행 「마지막 확인」 빈 칸' % i)

# ── 줄 10
h, rs = rows('voice_original.tsv')
hist = set(l.split('\t', 1)[0] for l in open(os.path.join(C, 'model_control_history.tsv'), encoding='utf-8').read().split('\n')[1:] if l)
if h is None: fail('줄10 voice_original.tsv 없음')
else:
    for i, r in enumerate(rs, 2):
        r = r + [''] * (4 - len(r))
        if not r[2].strip() or not r[3].strip(): fail('줄10 음성 짝 파일 %d행 인식 원문 또는 보정문 칸이 빔' % i)
        mno = re.search(r'\d+', r[0])   # 「(덧붙임) 1060」처럼 앞말이 붙은 번호도 숫자로 읽음
        if not mno or mno.group(0) not in hist: fail('줄10 음성 짝 파일 %d행 이력 번호 %s 가 이력에 없음' % (i, r[0]))

# ── 줄 13
h, rs = rows('fable_confirm_wait.tsv')
if h is not None:
    for r in rs:
        r = r + [''] * (len(h) - len(r))
        m = re.match(r'\s*(\S+\.\w+)\s+([0-9a-f]{16})\s*$', r[3] if len(r) > 3 else '')
        if not m or '대기' not in r[6]: continue
        cand = [os.path.join(R, m.group(1)), os.path.join(C, m.group(1))]
        p = next((x for x in cand if os.path.exists(x)), None)
        if not p: warn('줄13 %s 원천 %s 를 찾지 못함' % (r[0], m.group(1))); continue
        now = hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
        if now != m.group(2): warn('줄13 %s Fable 확인 대기 중 원천 %s 가 바뀜(기록 %s · 지금 %s)' % (r[0], m.group(1), m.group(2), now))

# ── 147 ③
N = len(hist)
try:
    ps = json.load(open(os.path.join(C, 'phrase_scan.json'), encoding='utf-8'))
    if ps.get('hist_rows') != N: warn('147③ phrase_scan.json 기준 이력 %s건 ≠ 지금 이력 %d건(생성기 scan.py 저장소에 없음 · 문구 스캔 다시 내야 함)' % (ps.get('hist_rows'), N))
except Exception as e: warn('147③ phrase_scan.json 읽기 실패 ' + str(e)[:60])
try:
    ts = json.load(open(os.path.join(C, 'trace_sum.json'), encoding='utf-8'))
    m = re.search(r'이력\s*(\d+)건', ts.get('기준', ''))
    tv = sum(1 for _ in open(os.path.join(C, 'trace_v.tsv'), encoding='utf-8')) - 1
    if m and int(m.group(1)) != N: warn('147③ trace_sum 기준 이력 %s건 ≠ 지금 이력 %d건 · trace_v %d줄(python3 tools/gen_trace_sum.py)' % (m.group(1), N, tv))
except Exception as e: warn('147③ trace_sum·trace_v 읽기 실패 ' + str(e)[:60])

print('규칙 검사(줄 5·6·7·9·10·13 · 147③):', '통과' if not bad else '실패 %d건' % len(bad), '· 알림 %d건' % len(note))
sys.exit(1 if bad else 0)
