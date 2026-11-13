#!/usr/bin/env python3
"""신분 재확인 판정·보류 대장 — Opus 5.5 · 2026-11-13 (이력 1255·1256, 대표님 확정 17:11).
기준: cowork/ctl/policy_docs/Fable_지시문_수행체계·사용량예비·정기계획-261113_1102.md 11절 신-1~5.

  신-2(첫째 겹) 대표님 말씀이 30분 넘게 없다가 다시 오면, 그 말씀을 실행하기 전에 ic.hiven.ai.kr/id.html 통과 기록을 다시 확인한다.
  신-3(둘째 겹) 삭제·휴지통 이동 · 배포 · 열쇠 변경 · 외부로 나가는 메일·게시 · 규칙·원칙 변경 · 돈이 드는 일은 실행 전에 다시 확인한다.
  신-4 통과 전 지시는 「보류」, 통과하지 못하면 「무효」. 보류·무효는 SC-00·SC-17 한 줄로 보인다(cowork/ctl/id_recheck_hold.tsv).

판정 규칙(이 도구가 정한 꼴)
  첫째 겹: 마지막 기척 = max(앞 말씀 시각, 마지막 통과 시각). 이번 말씀 시각 − 마지막 기척 > 30분이면 필요.
           (통과도 대표님이 화면 앞에 있었다는 기척으로 센다)
  둘째 겹: 지시가 여섯 갈래 중 하나면 필요. 단, 마지막 통과가 이번 지시 시각 − 5분 이후면 이미 통과로 본다.
  보류 → 통과: 지시 시각 − 5분 이후, 보류 유효 60분 안에 통과 기록이 생기면 「통과 · 이어서 수행」.
  보류 → 무효: 60분이 지나도록 통과 기록이 없으면 「무효(통과 없음)」.

이 도구는 비밀번호·열쇠 값을 읽지도 쓰지도 않는다. 공개 저장소(hs)에 있으므로 대표님 말씀 원문·요지도 싣지 않는다
(이력 번호와 갈래 낱말만 싣는다. --text 는 갈래를 가리는 데만 쓰고 파일에 적지 않는다).
서버(ic.hiven.ai.kr)를 부르지 않는다. 통과 기록은 id.html 의 재확인 목록(/__id/rechecks)을 받은 JSON 을 import 로 옮기거나 pass 로 한 줄 적는다.

사용
  id_recheck.py need --now "YYYY-MM-DD HH:MM" [--said "앞 말씀 시각"] [--pass "마지막 통과 시각"] [--text "지시 글"] [--kind 갈래]
        지금 재확인이 필요한가. --pass 를 빼면 id_pass_log.tsv 의 마지막 통과를 쓴다. 종료 코드 0 = 불필요 · 3 = 필요
  id_recheck.py hold --no 이력번호 --now "지시 시각" [--said ..] [--pass ..] [--text ..] [--kind ..]
        need 와 같이 판정하고, 필요하면 보류 줄을 올린다(설정 「켜짐」이 false 면 판정만 하고 쓰지 않는다)
  id_recheck.py pass --at "통과 시각" --win 창번호 --why 첫확인|무입력|둘째겹 [--no 이력번호] [--kind 갈래]
  id_recheck.py import 파일.json        /__id/rechecks 응답을 저장한 파일에서 새 통과 줄만 옮김
  id_recheck.py resolve [--now ..]      보류 줄을 통과·무효로 닫음
  id_recheck.py status | selftest
"""
import sys, os, json, csv, re, datetime, argparse, hashlib

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(R, 'cowork', 'ctl')
CFG = os.path.join(C, 'id_recheck_config.json')
HOLD = os.path.join(C, 'id_recheck_hold.tsv')
PASS = os.path.join(C, 'id_pass_log.tsv')
TEST = os.path.join(C, 'id_recheck_test.tsv')
HOLD_H = ['보류 번호', '올린 때', '이력 번호', '지시 때', '까닭', '갈래', '상태', '닫은 때', '통과 기록']
PASS_H = ['통과 시각', '창 번호', '까닭', '이력 번호', '옮긴 곳']
WHY = {'idle': '무입력', 'risk': '둘째겹', 'first': '첫확인', '무입력': '무입력', '둘째겹': '둘째겹', '첫확인': '첫확인'}
# 신-3 여섯 갈래. 낱말은 지시 글에서 갈래를 가리는 데만 쓴다(글은 파일에 남기지 않음)
KINDS = [
    ('삭제·휴지통', r'삭제|지워|지우|휴지통|파기|없애 ?버려'),
    ('배포', r'배포|푸시|push|deploy|게시본 ?올려'),
    ('열쇠 변경', r'(열쇠|비밀번호|암호).{0,6}(바꿔|바꾸|변경|새로|교체|재설정)'),
    ('외부 발송·게시', r'메일|발송|게시|공개해|블로그|(밖|외부|고객|협력사|기관|투자자).{0,12}보내'),
    ('규칙·원칙 변경', r'(규칙|원칙|기준|정책|재확인).{0,8}(바꿔|바꾸|변경|고쳐|고치|빼|없애|끄|꺼|풀어|폐지|완화)'),
    ('돈이 드는 일', r'결제|구매|구독|유료|송금|요금|돈|비용|주문|계약'),
]
DEFAULT = {
    '켜짐': False,
    '켜는 조건': '대표님 결재 A-035(허가) 뒤 Fable 5.2가 이 값을 바꿈. 작업 모델은 이 값을 바꾸지 않음',
    '무입력 기준 분': 30,
    '둘째 겹 앞선 통과 인정 분': 5,
    '보류 유효 분': 60,
    '근거': '수행체계 정책 11절 신-1~5(대표님 확정 2026-11-13 17:11, 이력 1255·1256)',
}


def cfg():
    c = dict(DEFAULT)
    if os.path.exists(CFG):
        c.update(json.load(open(CFG, encoding='utf-8')))
    return c


def T(s):
    s = str(s).strip().replace('T', ' ')
    if re.match(r'^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d', s) and s.endswith('Z'):  # ISO(UTC) → 서울
        return datetime.datetime.strptime(s[:19], '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=9)
    return datetime.datetime.strptime(s[:16], '%Y-%m-%d %H:%M')


def F(t):
    return t.strftime('%Y-%m-%d %H:%M')


def rd(p, h):
    if not os.path.exists(p):
        return []
    rs = list(csv.reader(open(p, encoding='utf-8-sig'), delimiter='\t'))
    return [r + [''] * (len(h) - len(r)) for r in rs[1:] if r and any(x.strip() for x in r)]


def wr(p, h, rows):
    with open(p, 'w', encoding='utf-8', newline='') as o:
        o.write('\t'.join(h) + '\n')
        for r in rows:
            o.write('\t'.join(str(x).replace('\t', ' ').replace('\n', ' ') for x in r) + '\n')


def kinds_of(text, kind):
    if kind:
        return [k.strip() for k in kind.split(',') if k.strip()]
    return [k for k, rx in KINDS if re.search(rx, text or '', re.I)]


def last_pass(passes):
    ts = []
    for p in passes:
        try:
            ts.append(T(p[0]))
        except Exception:
            pass
    return max(ts) if ts else None


def judge(c, now, said=None, pas=None, text='', kind=''):
    """돌려줌: (필요 여부, 까닭 목록, 갈래 목록)"""
    why = []
    ks = kinds_of(text, kind)
    fresh = pas is not None and pas >= now - datetime.timedelta(minutes=c['둘째 겹 앞선 통과 인정 분'])
    seen = [t for t in (said, pas) if t is not None]
    if seen:
        gap = (now - max(seen)).total_seconds() / 60
        if gap > c['무입력 기준 분'] and not fresh:
            why.append('무입력 %d분(기준 %d분 넘음)' % (int(gap), c['무입력 기준 분']))
    if ks and not fresh:
        why.append('둘째 겹 지시(' + '·'.join(ks) + ')')
    return bool(why), why, ks


def need(a, c=None, passes=None):
    c = c or cfg()
    passes = rd(PASS, PASS_H) if passes is None else passes
    now = T(a.now)
    pas = T(a.pass_) if getattr(a, 'pass_', None) else last_pass(passes)
    said = T(a.said) if a.said else None
    n, why, ks = judge(c, now, said, pas, a.text or '', a.kind or '')
    base = '마지막 통과 %s' % (F(pas) if pas else '없음')
    if n:
        return 3, '필요 — ' + ' · '.join(why) + ' · ' + base + ' · ic.hiven.ai.kr/id.html 통과 전까지 그 지시는 보류'
    return 0, '불필요 — ' + ('둘째 겹 지시(%s)지만 %s분 안 통과 있음 · ' % ('·'.join(ks), c['둘째 겹 앞선 통과 인정 분']) if ks else '') + base


def hold(a, c=None, rows=None, passes=None, write=True):
    c = c or cfg()
    code, msg = need(a, c, passes)
    if code == 0:
        return 0, msg
    if not c['켜짐']:
        return 3, msg + ' (설정 켜짐=false: 보류 줄은 쓰지 않음)'
    rows = rd(HOLD, HOLD_H) if rows is None else rows
    no = 'IDH-%03d' % (len(rows) + 1)
    passes = rd(PASS, PASS_H) if passes is None else passes
    pas = T(a.pass_) if getattr(a, 'pass_', None) else last_pass(passes)
    _, why, ks = judge(c, T(a.now), T(a.said) if a.said else None, pas, a.text or '', a.kind or '')
    rows.append([no, F(datetime.datetime.now()), a.no, F(T(a.now)), ' · '.join(why), '·'.join(ks) or '—', '보류', '', ''])
    if write:
        wr(HOLD, HOLD_H, rows)
    return 3, msg + ' · %s 올림' % no


def resolve(now=None, c=None, rows=None, passes=None, write=True):
    c = c or cfg()
    now = T(now) if now else datetime.datetime.now()
    rows = rd(HOLD, HOLD_H) if rows is None else rows
    passes = rd(PASS, PASS_H) if passes is None else passes
    n = 0
    for r in rows:
        if r[6] != '보류':
            continue
        t = T(r[3])
        a0, a1 = t - datetime.timedelta(minutes=c['둘째 겹 앞선 통과 인정 분']), t + datetime.timedelta(minutes=c['보류 유효 분'])
        hit = [p for p in passes if p[0] and a0 <= T(p[0]) <= a1]
        if hit:
            p = sorted(hit, key=lambda x: T(x[0]))[0]
            r[6], r[7], r[8] = '통과 · 이어서 수행', F(now), '%s · 창 %s · %s' % (p[0], p[1], p[2])
            n += 1
        elif now > a1:
            r[6], r[7] = '무효(통과 없음)', F(now)
            n += 1
    if write:
        wr(HOLD, HOLD_H, rows)
    return n


def add_pass(at, win, why, no='', kind='', src='id.html', rows=None, write=True):
    rows = rd(PASS, PASS_H) if rows is None else rows
    if not re.fullmatch(r'\d{6}', str(win)):
        raise SystemExit('창 번호는 6자리입니다: %s' % win)
    w = WHY.get(why, '첫확인')
    at = F(T(at))
    if any(r[0] == at and r[1] == str(win) for r in rows):
        return 0
    rows.append([at, str(win), w + (' · ' + kind if kind else ''), no, src])
    rows.sort(key=lambda r: r[0])
    if write:
        wr(PASS, PASS_H, rows)
    return 1


def import_json(path):
    d = json.load(open(path, encoding='utf-8'))
    if isinstance(d, dict):
        d = d.get('list') or d.get('rows') or []
    n = 0
    rows = rd(PASS, PASS_H)
    for x in d:
        n += add_pass(x.get('at'), x.get('win'), x.get('why', 'first'), str(x.get('no') or ''), x.get('kind') or '', 'ic /__id/rechecks', rows, write=False)
    wr(PASS, PASS_H, rows)
    return n


def selftest():
    """설정 파일·대장 파일에 쓰지 않고 메모리 안에서 판정을 돌린다. 결과만 id_recheck_test.tsv 에 남긴다(지시 글 없음)."""
    c = dict(cfg())
    c['켜짐'] = True
    A = argparse.Namespace
    P0 = [['2026-11-13 09:00', '261104', '첫확인', '', '시험']]
    cases = [
        ('시-1', '앞 말씀 10분 전 · 평범한 지시', A(no='T1', now='2026-11-13 10:00', said='2026-11-13 09:50', pass_=None, text='표 글자 크기 맞춰', kind=''), 0),
        ('시-2', '앞 말씀 31분 전 · 평범한 지시(첫째 겹)', A(no='T2', now='2026-11-13 10:31', said='2026-11-13 10:00', pass_=None, text='표 글자 크기 맞춰', kind=''), 3),
        ('시-3', '앞 말씀 정확히 30분 전(넘지 않음)', A(no='T3', now='2026-11-13 10:30', said='2026-11-13 10:00', pass_=None, text='표 글자 크기 맞춰', kind=''), 0),
        ('시-4', '말씀은 40분 전이나 통과가 10분 전(기척)', A(no='T4', now='2026-11-13 10:40', said='2026-11-13 10:00', pass_='2026-11-13 10:30', text='표 맞춰', kind=''), 0),
        ('시-5', '배포 지시 · 무입력 짧음(둘째 겹)', A(no='T5', now='2026-11-13 10:32', said='2026-11-13 10:30', pass_=None, text='지금 배포해', kind=''), 3),
        ('시-6', '휴지통 이동 지시', A(no='T6', now='2026-11-13 10:33', said='2026-11-13 10:32', pass_=None, text='옛 파일 휴지통으로 옮겨', kind=''), 3),
        ('시-7', '열쇠 변경 지시', A(no='T7', now='2026-11-13 10:34', said='2026-11-13 10:33', pass_=None, text='통합관제 열쇠 바꿔', kind=''), 3),
        ('시-8', '메일 발송 지시', A(no='T8', now='2026-11-13 10:35', said='2026-11-13 10:34', pass_=None, text='협력사에 메일 보내', kind=''), 3),
        ('시-9', '규칙 변경 지시', A(no='T9', now='2026-11-13 10:36', said='2026-11-13 10:35', pass_=None, text='재확인 규칙 꺼', kind=''), 3),
        ('시-10', '돈이 드는 지시', A(no='T10', now='2026-11-13 10:37', said='2026-11-13 10:36', pass_=None, text='도메인 결제해', kind=''), 3),
        ('시-11', '배포 지시 · 통과 3분 전(인정)', A(no='T11', now='2026-11-13 10:40', said='2026-11-13 10:39', pass_='2026-11-13 10:37', text='배포해', kind=''), 0),
        ('시-12', '배포 지시 · 통과 6분 전(인정 안 됨)', A(no='T12', now='2026-11-13 10:43', said='2026-11-13 10:42', pass_='2026-11-13 10:37', text='배포해', kind=''), 3),
        ('시-13', '갈래를 직접 줌(--kind)', A(no='T13', now='2026-11-13 10:44', said='2026-11-13 10:43', pass_=None, text='', kind='배포'), 3),
    ]
    out, rows = [], []
    for cid, name, a, exp in cases:
        code, msg = need(a, c, P0)
        out.append([cid, name, exp, code, '통과' if code == exp else '실패', msg])
    # 보류 → 통과 · 무효
    early = A(no='T0', now='2026-11-13 09:40', said='2026-11-13 09:05', pass_=None, text='표 맞춰', kind='')
    for a in (early, cases[4][2]):
        hold(a, c, rows, P0, write=False)
    passes = P0 + [['2026-11-13 10:50', '261104', '둘째겹 · 배포', 'T5', '시험']]
    n = resolve('2026-11-13 11:40', c, rows, passes, write=False)
    st = [r[6] for r in rows]
    exp = ['무효(통과 없음)', '통과 · 이어서 수행']
    out.append(['시-14', '보류 2건 닫기: 09:40 지시(무입력 35분)는 60분 안 통과 없음 → 무효 · 10:32 배포는 10:50 통과 → 통과', '·'.join(exp), '·'.join(st), '통과' if st == exp and n == 2 else '실패', '닫은 줄 %d' % n])
    off = dict(c)
    off['켜짐'] = False
    rr = []
    code, msg = hold(cases[4][2], off, rr, P0, write=False)
    out.append(['시-15', '설정 꺼짐에서 hold: 판정은 필요(3), 보류 줄은 쓰지 않음', '3·0줄', '%d·%d줄' % (code, len(rr)), '통과' if code == 3 and not rr else '실패', msg])
    stamp = F(datetime.datetime.now())
    wr(TEST, ['번호', '사례', '기대', '결과', '판정', '도구 답', '시험한 때', '도구 sha256 앞 12자'],
       [r + [stamp, hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest()[:12]] for r in out])
    bad = [r for r in out if r[4] != '통과']
    for r in out:
        print(r[0], r[4], '·', r[1])
    print('selftest', '통과' if not bad else '실패 %d건' % len(bad), '· 시험 %d건 · 기록 %s · 설정 켜짐 값 %s(바꾸지 않음)' % (len(out), TEST, cfg()['켜짐']))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument('cmd', nargs='?', default='status')
    ap.add_argument('arg', nargs='?')
    ap.add_argument('--no', default='')
    ap.add_argument('--now')
    ap.add_argument('--at')
    ap.add_argument('--said')
    ap.add_argument('--pass', dest='pass_')
    ap.add_argument('--text', default='')
    ap.add_argument('--kind', default='')
    ap.add_argument('--win', default='')
    ap.add_argument('--why', default='first')
    a = ap.parse_args()
    if a.cmd in ('need', 'hold'):
        if not a.now:
            sys.exit('--now(이번 말씀 시각)를 주십시오')
        code, msg = (need(a) if a.cmd == 'need' else hold(a))
        print(msg)
        sys.exit(code)
    if a.cmd == 'pass':
        print('통과 줄 %d건 더함' % add_pass(a.at, a.win, a.why, a.no, a.kind))
        return
    if a.cmd == 'import':
        print('통과 줄 %d건 옮김' % import_json(a.arg))
        return
    if a.cmd == 'resolve':
        print('닫은 보류 줄', resolve(a.now))
        return
    if a.cmd == 'selftest':
        sys.exit(selftest())
    c = cfg()
    if not os.path.exists(HOLD):
        wr(HOLD, HOLD_H, [])
    if not os.path.exists(PASS):
        wr(PASS, PASS_H, [])
    h = rd(HOLD, HOLD_H)
    lp = last_pass(rd(PASS, PASS_H))
    print('신분 재확인: 보류 기록 %s · 무입력 기준 %d분 · 둘째 겹 앞선 통과 인정 %d분 · 보류 유효 %d분 · 보류 %d줄(열린 %d · 무효 %d) · 마지막 통과 %s' % (
        '켜짐' if c['켜짐'] else '꺼짐', c['무입력 기준 분'], c['둘째 겹 앞선 통과 인정 분'], c['보류 유효 분'], len(h),
        sum(1 for r in h if r[6] == '보류'), sum(1 for r in h if r[6].startswith('무효')), F(lp) if lp else '없음'))


if __name__ == '__main__':
    main()
