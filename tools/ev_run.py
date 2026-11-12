#!/usr/bin/env python3
"""증적 통합 프레임워크 실행기 (ev_run). 등록된 모든 시험·시뮬레이션·에뮬레이터·점검을 증적과 함께 돌린다.
적용 지점: P0 등록 확인 · P1 시작 게이트(폴더·입력 해시·환경) · P2 실행(표준출력·종료 코드·시각) · P3 사건(실패도 같은 증적) · P4 끝(산출 보존·해시 대조·색인) · P5 원장 기록.
사용:
  ev_run.py run <대상ID> [추가 인자]   등록부(cowork/ctl/ev_registry.tsv)의 명령을 증적과 함께 실행. 종료 코드는 대상의 것을 그대로 돌려줌(증적 대조 실패 시 20)
  ev_run.py check                      등록부 점검: 새 시험·시뮬레이션·에뮬레이터 파일이 등록 없이 있으면 실패(precheck 가 부름)
  ev_run.py list                       등록부 보기
증적 위치: 환경변수 EV_ROOT(기본 /mnt/user-data/outputs/ev3)/<대상ID>/<일련>/ . 훅·예약·설정 변경을 쓰지 않는다."""
import sys, os, csv, glob, time, subprocess, platform, hashlib, shlex
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(HERE)
REG = os.path.join(R, 'cowork', 'ctl', 'ev_registry.tsv')
LED = os.path.join(R, 'cowork', 'ctl', 'ev_ledger.tsv')
EVR = os.environ.get('EV_ROOT', '/mnt/user-data/outputs/ev3')
sys.path.insert(0, HERE)
import ev_pack

HEAD = ['대상ID', '종류', '설명', '실행', '입력', '산출', '실행 위치', '적용 방법', '적용 지점', '상태', '담당', '비고']

def load():
    rows = []
    with open(REG, encoding='utf-8-sig') as f:
        for i, r in enumerate(csv.reader(f, delimiter='\t')):
            if i == 0 or not r:
                continue
            r += [''] * (len(HEAD) - len(r))
            rows.append(dict(zip(HEAD, r)))
    return rows

def sha_file(p):
    return ev_pack.sha(p)

def git_head():
    try:
        return subprocess.run(['git', '-C', R, 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
    except Exception:
        return ''

def run(tid, extra):
    rows = {r['대상ID']: r for r in load()}
    if tid not in rows:
        print('P0 실패: 등록부에 없는 대상 — 등록 없이 돌리지 않음', tid); return 3
    r = rows[tid]
    if r['적용 방법'] != 'ev_run':
        print('P0 실패: 적용 방법이 ev_run 이 아님', r['적용 방법']); return 3
    rid = time.strftime('%y%m%d_%H%M%S')
    d = os.path.join(EVR, tid, rid)
    ev_pack.init(d, tid, f'{r["설명"]} · 실행 증적 자동 가동')
    out = os.path.join(d, '산출_원본')          # 대상이 쓰는 자리(보존 사본과 별도)
    os.makedirs(out, exist_ok=True)
    # P1 시작: 환경·입력 해시
    env = os.path.join(d, '환경기록.tsv')
    with open(env, 'w', encoding='utf-8') as f:
        f.write('항목\t값\n')
        for k, v in [('기록시각', ev_pack.now()), ('대상', tid), ('OS', platform.platform()), ('Python', sys.version.split()[0]),
                     ('저장소 커밋', git_head()), ('실행 위치', r['실행 위치']), ('명령', r['실행']), ('추가 인자', ' '.join(extra)),
                     ('증적 도구 sha256', sha_file(os.path.abspath(__file__))), ('EV_ROOT', EVR)]:
            f.write(f'{k}\t{v}\n')
    ins = [os.path.join(R, x.strip()) for x in r['입력'].split(',') if x.strip()]
    miss = [x for x in ins if not os.path.exists(x)]
    ev_pack.add(d, '시작_환경', [env])
    if ins:
        ev_pack.add(d, '시작_입력', [x for x in ins if os.path.exists(x)])
    if miss:
        open(os.path.join(d, ev_pack.LOG), 'a', encoding='utf-8').write(f'{ev_pack.now()}\t{tid}\t입력 없음\t{";".join(miss)}\tSonnet\t사건\n')
    # P2 실행
    cmd = r['실행'].replace('{OUT}', out)
    t0 = time.time(); s0 = ev_pack.now()
    p = subprocess.run(cmd + ((' ' + ' '.join(shlex.quote(x) for x in extra)) if extra else ''), shell=True, cwd=R, capture_output=True, text=True)
    s1 = ev_pack.now()
    log = os.path.join(d, '실행기록.txt')
    with open(log, 'w', encoding='utf-8') as f:
        f.write(f'시작 {s0}\n끝 {s1}\n걸린 초 {time.time()-t0:.1f}\n종료 코드 {p.returncode}\n명령 {cmd}\n--- 표준출력\n{p.stdout}\n--- 표준오류\n{p.stderr}\n')
    ev_pack.add(d, '실행', [log])
    # P3 사건: 실패도 같은 증적(원-5)
    if p.returncode != 0:
        open(os.path.join(d, ev_pack.LOG), 'a', encoding='utf-8').write(f'{ev_pack.now()}\t{tid}\t사건: 종료 코드 {p.returncode}\t{log}\tSonnet\t실패도 통과와 같이 보존\n')
    # P4 끝: 산출 보존·대조·색인
    outs = [os.path.join(dp, fn) for dp, _, fs in os.walk(out) for fn in fs]
    if outs:
        ev_pack.add(d, '끝_산출', outs)
    bad = ev_pack.verify(d)
    ev_pack.index(d)
    # P5 원장
    man = os.path.join(d, ev_pack.MAN)
    n = sum(1 for _ in open(man, encoding='utf-8')) - 1
    if not os.path.exists(LED):
        open(LED, 'w', encoding='utf-8').write('시각\t대상ID\t일련\t종료코드\t증빙수\t대조\t증적 폴더\t해시목록 sha256\n')
    open(LED, 'a', encoding='utf-8').write(f'{ev_pack.now()}\t{tid}\t{rid}\t{p.returncode}\t{n}\t{"통과" if not bad else "문제"}\t{d}\t{sha_file(man)}\n')
    print(f'ev_run {tid} 종료 코드 {p.returncode} · 증빙 {n}건 · 대조 {"통과" if not bad else "문제"} · {d}')
    sys.stdout.write(p.stdout[-400:])
    return 20 if bad else p.returncode

def check():
    rows = load(); fail = 0
    names = ' '.join(r['실행'] + ' ' + r['입력'] for r in rows)
    pats = ['tools/sim_*.py', 'tools/emu_*.py', 'tools/test_*.py', 'tools/*_sim.py', 'tools/*_emu.py']
    for pat in pats:
        for f in sorted(glob.glob(os.path.join(R, pat))):
            rel = os.path.relpath(f, R)
            if rel not in names:
                print('실패: 시험·시뮬레이션·에뮬레이터 파일이 증적 등록부에 없음 —', rel, '(cowork/ctl/ev_registry.tsv 에 행을 추가해야 함)'); fail += 1
    ledger = open(LED, encoding='utf-8').read() if os.path.exists(LED) else ''
    for r in rows:
        for k in ('대상ID', '종류', '실행 위치', '적용 방법', '상태', '담당'):
            if not r[k].strip():
                print('실패:', r['대상ID'] or '(이름 없음)', '칸 비어 있음 —', k); fail += 1
        if r['상태'].startswith('적용') and r['적용 방법'] == 'ev_run' and ('\t' + r['대상ID'] + '\t') not in ledger:
            print('알림:', r['대상ID'], '적용 상태이나 증적 원장에 실행 기록 없음')
        if r['상태'].startswith('계획'):
            print('알림:', r['대상ID'], '계획 상태 —', r['비고'][:80])
    print('ev_run check', '통과' if not fail else f'실패 {fail}건', f'(대상 {len(rows)}건)')
    return 1 if fail else 0

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(1)
    if a[0] == 'run' and len(a) >= 2: sys.exit(run(a[1], a[2:]))
    elif a[0] == 'check': sys.exit(check())
    elif a[0] == 'list':
        for r in load(): print(r['대상ID'], '|', r['종류'], '|', r['상태'], '|', r['설명'])
    else: print(__doc__)
