#!/usr/bin/env python3
"""증빙 자동보존 도구 (ev_pack). 시험·작업·결재 등 모든 일의 증적을 해시와 함께 묶어 보존한다.
사용:
  ev_pack.py init  <증적폴더> <일감ID> <설명> [구분]  증적 폴더와 인수기록·해시목록 틀 만들기(시험 시작 전 점검에서 필수)
                                                    구분 = 딱지 여덟 값 + 「점검」(판정 132) 가운데 하나. 주면 해시목록 「구분」 칸에 줄마다 적힘
  ev_pack.py add   <증적폴더> <라벨> <파일...>      파일을 증적 폴더에 복사, 원본 시각·크기·sha256 기록, 인수기록 한 줄 추가
  ev_pack.py verify <증적폴더>                      해시목록과 실제 파일 대조(바뀐 것·빠진 것 보고)
  ev_pack.py index <증적폴더>                       GS 증빙 색인(증빙번호·내용·파일·해시) 만들기
"""
import sys, os, hashlib, shutil, time, csv

# 판정 132(11-13 Fable): 구분 칸 값 = 데-2 딱지 여덟 값 + 「점검」(129 인정). 등록부·원장·해시목록이 같은 값을 쓴다
LABELS = ('실측', '에뮬레이터 실측', '시뮬레이션(실측 아님)', '합성(시험 입력)', '보충(모델 계산)', '추정', '확인 안 됨', '격리(변조·오염·오류 의심)', '점검')

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()

def now():
    return time.strftime('%Y-%m-%dT%H:%M:%S')

MAN = '해시목록.tsv'
LOG = '인수기록.tsv'

def init(d, jid, desc, kind=''):
    if kind and kind not in LABELS:
        print('구분 값이 딱지 여덟 값·점검 밖:', kind); sys.exit(4)
    os.makedirs(d, exist_ok=True)
    for n, head in ((MAN, '증빙번호\t보존시각\t라벨\t파일\t크기\t원본수정시각\tsha256' + ('\t구분' if kind else '') + '\n'),
                    (LOG, '시각\t일감\t행위\t대상\t행위자\t메모\n')):
        p = os.path.join(d, n)
        if not os.path.exists(p):
            open(p, 'w', encoding='utf-8').write(head)
    open(os.path.join(d, LOG), 'a', encoding='utf-8').write(f'{now()}\t{jid}\t증적 보존 가동\t{d}\tSonnet\t{desc}' + (f' · 구분={kind}' if kind else '') + '\n')
    print('init ok', d)

def kind_of(d):
    """해시목록 머리에 「구분」 칸이 있으면 인수기록의 「구분=」 값을 돌려줌(없으면 빈 값 · 옛 폴더는 그대로)."""
    try:
        head = open(os.path.join(d, MAN), encoding='utf-8').readline().rstrip('\n').split('\t')
    except FileNotFoundError:
        return ''
    if '구분' not in head:
        return ''
    for l in open(os.path.join(d, LOG), encoding='utf-8'):
        if '증적 보존 가동' in l and ' · 구분=' in l:
            return l.rstrip('\n').rsplit(' · 구분=', 1)[1]
    return '확인 안 됨'

def nextno(d):
    p = os.path.join(d, MAN)
    n = 0
    for i, l in enumerate(open(p, encoding='utf-8')):
        if i:
            n += 1
    return n + 1

def add(d, label, files):
    sub = os.path.join(d, label)
    os.makedirs(sub, exist_ok=True)
    kind = kind_of(d)
    man = open(os.path.join(d, MAN), 'a', encoding='utf-8')
    n = nextno(d)
    for src in files:
        dst = os.path.join(sub, os.path.basename(src))
        if os.path.exists(dst):
            print('덮어쓰기 금지: 이미 있음', dst); sys.exit(3)
        shutil.copy2(src, dst)
        os.chmod(dst, 0o444)
        st = os.stat(src)
        a, b = sha(src), sha(dst)
        if a != b:
            print('복사 불일치', src); sys.exit(2)
        rel = os.path.relpath(dst, d)
        man.write(f'EV-{n:05d}\t{now()}\t{label}\t{rel}\t{st.st_size}\t{time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(st.st_mtime))}\t{a}' + (f'\t{kind}' if kind else '') + '\n')
        n += 1
    man.close()
    open(os.path.join(d, LOG), 'a', encoding='utf-8').write(f'{now()}\t-\t보존 {len(files)}건\t{label}\tSonnet\t원본·사본 sha256 일치\n')
    print('add ok', len(files))

def verify(d):
    bad = 0
    for i, row in enumerate(csv.reader(open(os.path.join(d, MAN), encoding='utf-8'), delimiter='\t')):
        if i == 0 or not row:
            continue
        p = os.path.join(d, row[3])
        if not os.path.exists(p):
            print('빠짐', row[0], row[3]); bad += 1
        elif sha(p) != row[6]:
            print('바뀜', row[0], row[3]); bad += 1
    print('verify', '통과' if not bad else f'문제 {bad}건')
    open(os.path.join(d, LOG), 'a', encoding='utf-8').write(f'{now()}\t-\t해시 대조\t{d}\tSonnet\t{"통과" if not bad else f"문제 {bad}건"}\n')
    return bad

def index(d):
    out = os.path.join(d, 'GS증빙색인.tsv')
    with open(out, 'w', encoding='utf-8') as o:
        o.write('증빙번호\t라벨\t파일\tsha256\t보존시각\n')
        for i, row in enumerate(csv.reader(open(os.path.join(d, MAN), encoding='utf-8'), delimiter='\t')):
            if i and row:
                o.write('\t'.join([row[0], row[2], row[3], row[6], row[1]]) + '\n')
    print('index ok', out)

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(1)
    c = a[0]
    if c == 'init': init(a[1], a[2], a[3], a[4] if len(a) > 4 else '')
    elif c == 'add': add(a[1], a[2], a[3:])
    elif c == 'verify': sys.exit(1 if verify(a[1]) else 0)
    elif c == 'index': index(a[1])
    else: print(__doc__)
