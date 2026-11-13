#!/usr/bin/env python3
"""HiBiz 맨 위 파일 0 검사(판정 138 ③, 11-13 Fable 판정 · Opus 5.5 새로 만듦). 읽기만 한다.
규칙(HiBiz 폴더 규칙 5 · 11-12 12:00·12:09): 폴더 root에는 어떤 파일도 두지 않는다. 모든 폴더의 맨 위 00번은 색인이다.
검사: ① HiBiz 맨 위에 파일 0 ② 맨 위 폴더(NN_…) 바로 아래에 파일 0 ③ 맨 위 폴더마다 NN_00 색인 폴더가 있음
      ④ (--deep) 하위 폴더를 가진 2층 폴더(NN_dd_…) 바로 아래 파일 0 — 알림으로만 셈
사용: python3 tools/index_root_check.py [HiBiz 경로] [--deep]
      경로를 주지 않으면 환경 변수 HIBIZ_ROOT, 없으면 /mnt/user-data/uploads/HiBiz(PC 폴더를 받아 둔 사본)를 읽는다.
      경로가 없으면 「확인 안 됨」을 찍고 종료 코드 2(precheck 는 알림으로 받음).
종료 코드: 0 통과 · 1 맨 위 파일 있음(①②) · 2 읽을 폴더 없음"""
import os, re, sys
a = [x for x in sys.argv[1:] if not x.startswith('--')]
DEEP = '--deep' in sys.argv
root = a[0] if a else os.environ.get('HIBIZ_ROOT', '/mnt/user-data/uploads/HiBiz')
if not os.path.isdir(root):
    print('맨 위 파일 검사: 확인 안 됨 — 폴더 없음', root); sys.exit(2)
IGN = {'desktop.ini', 'Thumbs.db', '.DS_Store'}   # 운영체제가 저절로 만드는 파일은 셈에서 뺌(이름을 따로 적음)
def files(d):
    try: return sorted(f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f)))
    except OSError: return []
bad, warn, sys_f = [], [], []
top = files(root)
for f in top:
    (sys_f if f in IGN else bad).append(('HiBiz 맨 위', f))
dirs = sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)))
for d in dirs:
    p = os.path.join(root, d)
    for f in files(p):
        (sys_f if f in IGN else bad).append((d, f))
    m = re.match(r'(\d{2})_', d)
    subs = sorted(x for x in os.listdir(p) if os.path.isdir(os.path.join(p, x)))
    if m and not any(x.startswith(m.group(1) + '_00') for x in subs):
        warn.append((d, '%s_00 색인 폴더 없음' % m.group(1)))
    if DEEP:
        for s in subs:
            sp = os.path.join(p, s)
            if any(os.path.isdir(os.path.join(sp, x)) for x in os.listdir(sp)):
                for f in files(sp):
                    if f not in IGN: warn.append((d + '/' + s, '하위 폴더가 있는 2층 폴더 맨 위 파일 ' + f))
for w, f in bad: print('실패: 맨 위 파일 —', w, '/', f)
for w, m_ in warn: print('알림:', w, '—', m_)
print('맨 위 파일 검사: %s · 읽은 곳 %s · 맨 위 폴더 %d · 맨 위 파일 %d · 색인 폴더 없음 %d · 운영체제 파일 %d(셈에서 뺌)%s' % (
    '통과' if not bad else '실패', root, len(dirs), len(bad), sum(1 for _, m_ in warn if '색인' in m_), len(sys_f),
    ' · 2층 알림 %d' % sum(1 for _, m_ in warn if '2층' in m_) if DEEP else ''))
sys.exit(1 if bad else 0)
