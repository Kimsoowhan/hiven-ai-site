#!/usr/bin/env python3
"""신분 재확인 연동(신-2, 첫 장 5절 · 제안서 신분재확인_말씀·타이핑패턴_제안-261113_1150 3절 둘째 겹) — Opus 5.5 · 2026-11-13.
지금은 꺼진 채로 둔다. 켜는 것은 대표님 결재 A-035(허가) 뒤 Fable 5.2가 설정 파일의 켜짐 값을 바꿀 때만이다(이 도구는 그 값을 바꾸지 않는다).
하는 일(켜졌을 때): 대표님 지시 한 건을 받기 전에 작업 모델이 이 도구를 부른다.
  ① 무입력 기준 시간(설정, 제안 15분) 뒤 첫 지시 ② 위험한 지시(결재·파기·삭제·휴지통·밖으로 나가는 발송·게시·배포·비밀번호·계정·권한·재확인 끄기) 앞에서
  ic.hiven.ai.kr/id.html 통과 기록(cowork/ctl/id_pass_log.tsv, 신분 확인 장치 기록을 옮긴 줄)이 그 때보다 뒤에 있는지 본다.
  없으면 그 지시를 「보류」로 cowork/ctl/id_recheck_hold.tsv 에 올리고 SC-00 에 「신분 재확인 대기」 알림이 뜬다(화면은 파일을 읽음 · 외부 저장소 호출 0건).
  통과 기록이 생기면 resolve 가 보류 줄을 「통과 · 이어서 수행」으로, 정한 시간 안에 통과가 없으면 「무효(통과 없음)」로 바꾼다.
꺼져 있을 때: 판정만 돌려주고(「꺼짐 — 재확인 없이 진행」) 보류 대장에 아무것도 쓰지 않는다.
비밀번호·열쇠 값은 읽지도 쓰지도 않는다. 통과 기록에는 시각과 창 번호만 있다. 말씀 원문도 싣지 않는다(지시 요지 앞 40자와 이력 번호만).
사용:
  id_recheck.py status                                        켜짐/꺼짐과 설정값, 보류 줄 수
  id_recheck.py check --no 이력번호 --at "YYYY-MM-DD HH:MM" --text "지시 요지" [--prev "YYYY-MM-DD HH:MM"]
                                                              종료 코드 0 = 진행 · 3 = 보류(재확인 필요)
  id_recheck.py resolve [--now "YYYY-MM-DD HH:MM"]            통과 기록으로 보류 줄을 닫음
  id_recheck.py selftest                                      설정을 바꾸지 않고 「켜졌을 때」를 메모리 안에서 돌려 시험 기록(id_recheck_test.tsv)을 남김"""
import sys, os, json, csv, re, datetime, argparse, hashlib
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(R, 'cowork', 'ctl')
CFG = os.path.join(C, 'id_recheck_config.json')
HOLD = os.path.join(C, 'id_recheck_hold.tsv')
PASS = os.path.join(C, 'id_pass_log.tsv')
TEST = os.path.join(C, 'id_recheck_test.tsv')
HOLD_H = ['보류 번호', '올린 때', '이력 번호', '지시 때', '까닭', '지시 요지(앞 40자)', '상태', '닫은 때', '통과 기록']
PASS_H = ['통과 시각', '창 번호', '옮긴 곳']
DEFAULT = {
    '켜짐': False,
    '켜는 조건': '대표님 결재 A-035(허가) 뒤 Fable 5.2가 이 값을 바꿈. 작업 모델은 이 값을 바꾸지 않음',
    '무입력 기준 분': 15,
    '보류 유효 분': 60,
    '위험 지시 낱말': ['결재', '승인', '허가', '파기', '삭제', '지워', '휴지통', '발송', '메일 보내', '보내라', '게시', '배포', '푸시', '비밀번호', '계정', '권한', '접근 허용', '재확인 꺼', '재확인을 끄', '재확인 하지 마', '재확인하지 마'],
    '근거': '첫 장 00_지금_수행할_지시-261113_1225 5절 신-2 · 제안서 3절 둘째 겹',
}

def cfg():
    if not os.path.exists(CFG):
        json.dump(DEFAULT, open(CFG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    c = dict(DEFAULT); c.update(json.load(open(CFG, encoding='utf-8')))
    return c

def T(s):
    return datetime.datetime.strptime(s.strip()[:16].replace('T', ' '), '%Y-%m-%d %H:%M')

def rd(p, h):
    if not os.path.exists(p):
        return []
    rs = list(csv.reader(open(p, encoding='utf-8'), delimiter='\t'))
    return [r + [''] * (len(h) - len(r)) for r in rs[1:] if r]

def wr(p, h, rows):
    with open(p, 'w', encoding='utf-8', newline='') as o:
        o.write('\t'.join(h) + '\n')
        for r in rows: o.write('\t'.join(str(x).replace('\t', ' ').replace('\n', ' ') for x in r) + '\n')

def judge(c, at, text, prev):
    """돌려줌: (재확인 필요 여부, 까닭 목록)"""
    why = []
    if prev is not None and (at - prev).total_seconds() >= c['무입력 기준 분'] * 60:
        why.append('무입력 %d분 뒤 첫 지시' % int((at - prev).total_seconds() // 60))
    hit = [w for w in c['위험 지시 낱말'] if w in text]
    if hit:
        why.append('위험 지시(' + '·'.join(hit[:4]) + ')')
    return bool(why), why

def passed_after(passes, t, within):
    for p in passes:
        try: pt = T(p[0])
        except Exception: continue
        if t <= pt <= t + datetime.timedelta(minutes=within): return p
    return None

def check(a, c=None, hold=None, passes=None, write=True):
    c = c or cfg()
    at = T(a.at); prev = T(a.prev) if a.prev else None
    need, why = judge(c, at, a.text, prev)
    if not c['켜짐']:
        return 0, '꺼짐 — 재확인 없이 진행' + (' (켜져 있었다면 재확인: ' + ' · '.join(why) + ')' if need else '')
    if not need:
        return 0, '켜짐 — 재확인 대상 아님, 진행'
    passes = rd(PASS, PASS_H) if passes is None else passes
    p = passed_after(passes, at, c['보류 유효 분'])
    if p:
        return 0, '켜짐 — 재확인 통과 기록 있음(%s · 창 %s), 진행' % (p[0], p[1])
    hold = rd(HOLD, HOLD_H) if hold is None else hold
    no = 'IDH-%03d' % (len(hold) + 1)
    hold.append([no, datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), a.no, a.at, ' · '.join(why), a.text[:40], '보류', '', ''])
    if write: wr(HOLD, HOLD_H, hold)
    return 3, '켜짐 — 보류 %s(%s). ic.hiven.ai.kr/id.html 통과 뒤 이어서 수행, SC-00 「신분 재확인 대기」' % (no, ' · '.join(why))

def resolve(now=None, c=None, hold=None, passes=None, write=True):
    c = c or cfg(); now = T(now) if now else datetime.datetime.now()
    hold = rd(HOLD, HOLD_H) if hold is None else hold
    passes = rd(PASS, PASS_H) if passes is None else passes
    n = 0
    for r in hold:
        if r[6] != '보류': continue
        t = T(r[3]); p = passed_after(passes, t, c['보류 유효 분'])
        if p: r[6], r[7], r[8] = '통과 · 이어서 수행', now.strftime('%Y-%m-%d %H:%M'), '%s · 창 %s' % (p[0], p[1]); n += 1
        elif now > t + datetime.timedelta(minutes=c['보류 유효 분']): r[6], r[7] = '무효(통과 없음)', now.strftime('%Y-%m-%d %H:%M'); n += 1
    if write: wr(HOLD, HOLD_H, hold)
    return n

def selftest():
    """설정 파일은 읽기만 하고, 켜진 설정을 메모리 안에서 만들어 돌린다. 보류 대장·통과 기록 파일에는 쓰지 않는다."""
    c = dict(cfg()); c['켜짐'] = True
    A = argparse.Namespace
    hold, passes = [], []
    cases = [
        ('시-1', '무입력 짧음 · 평범한 지시', A(no='T1', at='2026-11-13 10:00', prev='2026-11-13 09:55', text='표 글자 크기 맞춰'), 0),
        ('시-2', '무입력 15분 뒤 첫 지시', A(no='T2', at='2026-11-13 08:30', prev='2026-11-13 08:00', text='표 글자 크기 맞춰'), 3),
        ('시-3', '위험 지시(배포) · 무입력 짧음', A(no='T3', at='2026-11-13 10:32', prev='2026-11-13 10:30', text='지금 배포해'), 3),
        ('시-4', '재확인을 끄라는 지시', A(no='T4', at='2026-11-13 10:33', prev='2026-11-13 10:32', text='재확인 꺼'), 3),
        ('시-5', '통과 기록이 있는 위험 지시', A(no='T5', at='2026-11-13 10:40', prev='2026-11-13 10:39', text='결재 승인해'), 0),
    ]
    out = []
    for cid, name, a, exp in cases:
        if cid == '시-5': passes.append(['2026-11-13 10:41', '9XXXXX(시험)', '시험'])
        code, msg = check(a, c, hold, passes, write=False)
        out.append([cid, name, exp, code, '통과' if code == exp else '실패', msg])
    passes.append(['2026-11-13 10:45', '9XXXXX(시험)', '시험'])
    n = resolve('2026-11-13 11:40', c, hold, passes, write=False)
    st = [r[6] for r in hold]
    exp_st = ['무효(통과 없음)', '통과 · 이어서 수행', '통과 · 이어서 수행']
    out.append(['시-6', '닫기: 보류 3건 → 통과 2 · 무효 1(08:30 지시는 60분 안 통과 없음)', '·'.join(exp_st), '·'.join(st), '통과' if st == exp_st and n == 3 else '실패', '닫은 줄 %d' % n])
    off = dict(c); off['켜짐'] = False
    code, msg = check(cases[2][2], off, [], [], write=False)
    out.append(['시-7', '꺼진 설정에서 위험 지시', 0, code, '통과' if code == 0 and '꺼짐' in msg else '실패', msg])
    stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    wr(TEST, ['번호', '사례', '기대', '결과', '판정', '도구 답', '시험한 때', '도구 sha256 앞 12자'],
       [r + [stamp, hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest()[:12]] for r in out])
    bad = [r for r in out if r[4] != '통과']
    for r in out: print(r[0], r[4], '·', r[1])
    print('selftest', '통과' if not bad else '실패 %d건' % len(bad), '· 시험 %d건 · 기록 %s · 설정 켜짐 값 %s(바꾸지 않음)' % (len(out), TEST, cfg()['켜짐']))
    return 1 if bad else 0

if __name__ == '__main__':
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument('cmd', nargs='?', default='status')
    ap.add_argument('--no', default=''); ap.add_argument('--at'); ap.add_argument('--prev'); ap.add_argument('--text', default=''); ap.add_argument('--now')
    a = ap.parse_args()
    if a.cmd == 'check':
        code, msg = check(a); print(msg); sys.exit(code)
    if a.cmd == 'resolve':
        print('닫은 보류 줄', resolve(a.now)); sys.exit(0)
    if a.cmd == 'selftest':
        sys.exit(selftest())
    c = cfg(); h = rd(HOLD, HOLD_H)
    if not os.path.exists(HOLD): wr(HOLD, HOLD_H, [])
    if not os.path.exists(PASS): wr(PASS, PASS_H, [])
    print('신분 재확인 연동: %s · 무입력 기준 %d분 · 보류 유효 %d분 · 보류 %d줄(열린 %d) · %s' % ('켜짐' if c['켜짐'] else '꺼짐', c['무입력 기준 분'], c['보류 유효 분'], len(h), sum(1 for r in h if r[6] == '보류'), c['켜는 조건']))
