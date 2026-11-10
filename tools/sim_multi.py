# -*- coding: utf-8 -*-
"""HIVEN 다중화 서비스 시뮬레이션 (Fable 5.2 · 2026-11-11)
설계안: HIVEN_다중화_서비스_프로토콜_플로우_통제_설계안-261111_0.1_작업 (2장 프로토콜, 5장 통제 규칙)
값은 모두 시뮬레이션이며 실측이 아니다. 원본 대시보드에 올리지 않는다."""
import random, json, collections, os, sys
SEED = 261111
DAYS = 30
OS_LIST = ['Windows', 'macOS', 'Android-삼성', 'Android-샤오미', 'iPhone', 'Linux']
OS_W = [46, 10, 18, 9, 14, 3]
ALLOWED = {'no', 'type', 'day', 'member', 'device', 'os', 'cap', 'pkg', 'org', 'ver', 'ticket', 'body'}
BODY_BANNED = ('path', 'filename', 'key_value', 'content')


def build(rng):
    members = []
    mid = 0

    def dev(pkg, org=None):
        o = rng.choices(OS_LIST, OS_W)[0]
        cap = rng.choices(['A', 'B', 'C'], [70, 24, 6])[0]
        if o == 'Android-샤오미':
            cap = rng.choices(['A', 'B', 'C'], [35, 55, 10])[0]
        return {'id': 'D%05d' % rng.randrange(10 ** 5), 'os': o, 'cap': cap, 'slots': rng.randint(1, 8), 'ver': '0.2.2'}

    for _ in range(300):
        mid += 1
        members.append({'id': 'M%05d' % mid, 'pkg': '개인', 'org': None, 'devs': [dev('개인')]})
    for _ in range(40):
        mid += 1
        members.append({'id': 'M%05d' % mid, 'pkg': '기기 추가', 'org': None, 'devs': [dev('기기 추가') for _ in range(rng.randint(2, 5))]})
    for t in range(4):
        n = rng.randint(15, 40)
        for _ in range(n):
            mid += 1
            members.append({'id': 'M%05d' % mid, 'pkg': '팀', 'org': 'T%02d' % (t + 1), 'devs': [dev('팀')]})
    for _ in range(120):
        mid += 1
        members.append({'id': 'M%05d' % mid, 'pkg': '기관', 'org': 'G01', 'devs': [dev('기관')]})
    return members


def run():
    rng = random.Random(SEED)
    members = build(rng)
    free_users = 500           # 무료: 메시지를 보내지 않는다
    ev = []
    no = [0]
    tk = [0]
    reconciled = set()         # (device) 정합이 끝난 기기
    multi = {}                 # 회원·팀·기관별 기기 수
    for m in members:
        multi[m['id']] = len(m['devs'])
    orgsize = collections.Counter(m['org'] for m in members if m['org'])

    def emit(day, m, d, typ, body, ticket=None):
        no[0] += 1
        ev.append({'no': no[0], 'type': typ, 'day': day, 'member': m['id'], 'device': d['id'], 'os': d['os'], 'cap': d['cap'],
                   'pkg': m['pkg'], 'org': m['org'], 'ver': d['ver'], 'ticket': ticket, 'body': body})

    def ticket(day, m, d, case, lane, auto=False, close=None):
        tk[0] += 1
        t = 'S%06d' % tk[0]
        emit(day, m, d, 'PR-09', {'case': case, 'lane': lane, 'close': close or ('챗봇' if lane == '가' else '사람' if lane == '나' else '통제'),
                                  'minutes': rng.randint(1, 8) if lane == '가' else rng.randint(30, 900), 'auto': auto}, t)
        return t

    injected = []
    beta_trial = set(m['id'] for m in rng.sample([m for m in members if m['pkg'] == '개인'], 60))  # 복구(되돌리기) 체험
    undo_used = collections.Counter()
    victim = rng.choice([m for m in members if m['pkg'] == '개인'])
    team_bad = 'T02'
    for day in range(1, DAYS + 1):
        if day == 12:
            injected.append({'id': '㉡', 'day': 12, 'what': '판 0.2.3이 Android-샤오미에서 갱신 실패 급증', 'rule': 'CR-01'})
        for m in members:
            for d in m['devs']:
                # 첫날: 가입·등록
                if day == 1:
                    emit(day, m, d, 'PR-11', {'state': '구독', 'devices': len(m['devs'])})
                    emit(day, m, d, 'PR-01', {'how': '무늬 읽기', 'result': '등록', 'known': True, 'devices': len(m['devs'])})
                # 매체 꽂음 → 색인 → 판정
                if rng.random() < 0.35:
                    slot = rng.randint(1, d['slots'])
                    emit(day, m, d, 'PR-02', {'slot': slot, 'registered': rng.random() < 0.9, 'scan': '이상 없음'})
                    emit(day, m, d, 'PR-03', {'assets': rng.randint(200, 60000), 'gb': rng.randint(1, 900), 'sec': rng.randint(20, 5000), 'unread': rng.randint(0, 40)})
                    sy_div = rng.randint(0, 12)
                    emit(day, m, d, 'PR-04', {'DUP-A': rng.randint(0, 3000), 'DUP-B': rng.randint(0, 400), 'DUP-C': rng.randint(0, 200), 'VER': rng.randint(0, 150),
                                               'SET': rng.randint(0, 6), 'DRV': rng.randint(0, 120), 'SY-최신': rng.randint(0, 80), 'SY-갈라짐': sy_div, 'SY-묶음엇갈림': rng.randint(0, 4)})
                    pend = max(0.0, rng.gauss(4.5, 1.6))
                    emit(day, m, d, 'PR-12', {'high': round(100 - pend - rng.uniform(3, 9), 1), 'fixed': round(rng.uniform(1, 6), 1), 'pending': round(pend, 1)})
                    if rng.random() < 0.6:
                        auto_n = rng.randint(0, 60)
                        emit(day, m, d, 'PR-05', {'assets': auto_n + sy_div, 'auto': auto_n, 'chosen': sy_div, 'edition': rng.randint(2, 40)})
                        reconciled.add(d['id'])
                # 미러링 (정합이 끝난 기기만)
                if d['id'] in reconciled and rng.random() < 0.45:
                    pair = rng.choices(['기기↔매체', '매체↔매체', '기기↔기기'], [70, 22, 8])[0]
                    if pair == '기기↔기기' and len(m['devs']) < 2 and not m['org']:
                        pair = '기기↔매체'
                    mism = 1 if rng.random() < 0.012 else 0
                    halted = False
                    if day == 21 and m['org'] == team_bad and rng.random() < 0.5:
                        halted = True
                    emit(day, m, d, 'PR-06', {'pair': pair, 'trigger': rng.choices(['꽂음', '바뀜', '때', '누름'], [35, 35, 20, 10])[0], 'count': rng.randint(1, 4000), 'mismatch': mism, 'halted': halted})
                # 복구(원복)
                if rng.random() < 0.02:
                    res = rng.choices(['성공', '일부', '실패'], [97.5, 1.7, 0.8])[0]
                    if day == 9 and rng.random() < 0.004:
                        res = '실패'
                    t = None
                    if res != '성공':
                        t = ticket(day, m, d, 'CASE-COF-RS-0002', '나', auto=True)
                    emit(day, m, d, 'PR-07', {'kind': '원복', 'result': res, 'edition': rng.randint(1, 40), 'left': None, 'limit': False}, t)
                # 복구(되돌리기) — 베타 체험 회원
                if m['id'] in beta_trial and rng.random() < 0.12:
                    undo_used[m['id']] += 1
                    left = max(0, 5 - undo_used[m['id']])
                    emit(day, m, d, 'PR-07', {'kind': '되돌리기', 'result': '성공', 'edition': rng.randint(1, 10), 'left': left, 'limit': undo_used[m['id']] >= 5})
                # 키 사건
                if rng.random() < 0.5:
                    r = '성공' if rng.random() < 0.985 else '실패'
                    emit(day, m, d, 'PR-08', {'key': rng.choice(['기기 관리 키', '금고 키']), 'result': r})
                if rng.random() < 0.0015:
                    t = ticket(day, m, d, 'CASE-COF-KY-0002', '나')
                    emit(day, m, d, 'PR-08', {'key': '금고 키', 'result': '바꾸기 요청'}, t)
                # 지원(일반)
                if rng.random() < 0.012:
                    case = rng.choice(['CASE-COF-IN-0001', 'CASE-COF-DU-0003', 'CASE-COF-SY-0001', 'CASE-COF-MR-0002', 'CASE-COF-SB-0001', 'CASE-COF-KY-0001'])
                    ticket(day, m, d, case, rng.choices(['가', '나'], [78, 22])[0])
                # 갱신: 12일째 0.2.3 배포
                if day in (12, 13) and d['ver'] == '0.2.2' and rng.random() < 0.5:
                    fail_p = 0.42 if d['os'] == 'Android-샤오미' else 0.02
                    if rng.random() < fail_p:
                        emit(day, m, d, 'PR-10', {'from': '0.2.2', 'to': '0.2.3', 'result': rng.choice(['실패', '되돌림'])})
                    else:
                        emit(day, m, d, 'PR-10', {'from': '0.2.2', 'to': '0.2.3', 'result': '성공'})
                        d['ver'] = '0.2.3'
        # 일부러 넣는 사고
        if day == 9:
            pick = rng.sample([m for m in members if m['pkg'] in ('개인', '팀')], 3)
            for m in pick:
                d = m['devs'][0]
                t = ticket(day, m, d, 'CASE-COF-RS-0002', '나', auto=True)
                emit(day, m, d, 'PR-07', {'kind': '원복', 'result': '실패', 'edition': 7, 'left': None, 'limit': False}, t)
            injected.append({'id': '㉠', 'day': 9, 'what': '복구(원복) 실패 3건', 'rule': 'CR-04'})
        if day == 18:
            d0 = victim['devs'][0]
            ghost = {'id': 'D99999', 'os': 'Android-샤오미', 'cap': 'C', 'slots': 1, 'ver': '0.2.3'}
            emit(day, victim, ghost, 'PR-01', {'how': '무늬 읽기', 'result': '등록', 'known': False, 'devices': 2})
            for _ in range(7):
                emit(day, victim, ghost, 'PR-08', {'key': '금고 키', 'result': '연속 실패'})
            ticket(day, victim, d0, 'CASE-COF-DV-0001', '다')
            injected.append({'id': '㉢', 'day': 18, 'what': '한 회원에 모르는 기기 등록 + 키 연속 실패 7번', 'rule': 'CR-02·CR-03'})
        if day == 21:
            injected.append({'id': '㉣', 'day': 21, 'what': '팀 T02에서 대량 삭제 뒤 자동 미러링', 'rule': 'CR-06'})
        if day == 25:
            for m in rng.sample(members, 34):
                ticket(day, m, m['devs'][0], 'CASE-COF-KY-0001', rng.choice(['가', '나']))
            injected.append({'id': '㉤', 'day': 25, 'what': '키 분실 사례(CASE-COF-KY-0001) 접수 급증', 'rule': 'CR-07'})
        if day == 27:
            m = rng.choice(members); d = m['devs'][0]
            emit(day, m, d, 'PR-03', {'assets': 10, 'gb': 1, 'sec': 5, 'unread': 0, 'path': '(시뮬레이션: 경로가 든 잘못된 메시지)'})
            injected.append({'id': '㉥', 'day': 27, 'what': '규칙을 어긴 메시지(경로가 든 것) 1건', 'rule': 'CR-08'})
    return members, ev, injected, free_users, multi, orgsize


def judge(members, ev, injected, multi):
    alerts = []
    inv = collections.OrderedDict((k, 0) for k in ['IN-01', 'IN-02', 'IN-03', 'IN-04', 'IN-05', 'IN-06', 'IN-07', 'IN-08'])
    pkg_of = {m['id']: m['pkg'] for m in members}
    by_day = collections.defaultdict(list)
    for e in ev:
        by_day[e['day']].append(e)
    reconciled = set()
    case_hist = collections.defaultdict(lambda: collections.Counter())
    limit_hit = set()
    for day in sorted(by_day):
        E = by_day[day]
        upd = collections.defaultdict(lambda: [0, 0])
        keyfail = collections.Counter(); unknown = set(); mism = collections.Counter(); pend = []
        for e in E:
            b = e['body']
            if set(e) - ALLOWED or any(k in b for k in BODY_BANNED):
                inv['IN-01'] += 1
                alerts.append({'day': day, 'rule': 'CR-08', 'grade': '위험', 'what': '원본·경로·키 값 칸이 든 메시지 (IN-01)', 'target': e['device']})
                continue
            if e['pkg'] == '무료':
                inv['IN-02'] += 1
            t = e['type']
            if t == 'PR-02' and not (1 <= b['slot'] <= 8):
                inv['IN-06'] += 1
            if t == 'PR-05':
                reconciled.add(e['device'])
            if t == 'PR-06':
                if e['device'] not in reconciled:
                    inv['IN-04'] += 1
                if b['pair'] == '기기↔기기' and multi.get(e['member'], 1) < 2 and not e['org']:
                    inv['IN-07'] += 1
                if b['mismatch']:
                    mism[e['device']] += b['mismatch']
                if b['halted']:
                    alerts.append({'day': day, 'rule': 'CR-06', 'grade': '경계', 'what': '자동 미러링 멈춤(대량 변경)', 'target': e['org'] or e['member']})
            if t == 'PR-07':
                if b['kind'] == '원복' and b['result'] != '성공':
                    if not e['ticket']:
                        inv['IN-03'] += 1
                    alerts.append({'day': day, 'rule': 'CR-04', 'grade': '주의', 'what': '복구(원복) ' + b['result'], 'target': e['member']})
                if b['kind'] == '되돌리기':
                    if e['member'] in limit_hit and b['result'] != '성공':
                        inv['IN-05'] += 1
                    if b['limit']:
                        limit_hit.add(e['member'])
            if t == 'PR-08' and b['result'] in ('실패', '연속 실패'):
                keyfail[e['member']] += 1
            if t == 'PR-01' and b.get('known') is False:
                unknown.add(e['member'])
            if t == 'PR-09':
                if not b.get('case'):
                    inv['IN-08'] += 1
                case_hist[b['case']][day] += 1
            if t == 'PR-10':
                k = (b['to'], e['os'])
                upd[k][0] += 1
                if b['result'] != '성공':
                    upd[k][1] += 1
            if t == 'PR-12':
                pend.append(b['pending'])
        for (ver, os_), (n, f) in upd.items():
            if n >= 10 and f / n > 0.20:
                alerts.append({'day': day, 'rule': 'CR-01', 'grade': '경고', 'what': '갱신 실패율 %d%% (%d건 가운데 %d건) — 판 %s' % (round(100 * f / n), n, f, ver), 'target': os_})
        for mem, n in keyfail.items():
            if n >= 5:
                alerts.append({'day': day, 'rule': 'CR-02', 'grade': '경계', 'what': '키 연속 실패 %d번' % n, 'target': mem})
                if mem in unknown:
                    alerts.append({'day': day, 'rule': 'CR-03', 'grade': '위험', 'what': '모르는 기기 등록 + 키 연속 실패', 'target': mem})
        for dev, n in mism.items():
            if n >= 3:
                alerts.append({'day': day, 'rule': 'CR-05', 'grade': '주의', 'what': '미러링 해시 불일치 %d건' % n, 'target': dev})
        for case, c in case_hist.items():
            today = c[day]
            prev = [c[x] for x in range(max(1, day - 7), day)]
            avg = (sum(prev) / len(prev)) if prev else 0
            if today >= 10 and today > 3 * max(avg, 0.5):
                alerts.append({'day': day, 'rule': 'CR-07', 'grade': '경계', 'what': '접수 %d건 (앞 7일 하루 평균 %.1f건)' % (today, avg), 'target': case})
        if pend and sum(pend) / len(pend) > 10:
            alerts.append({'day': day, 'rule': 'CR-09', 'grade': '주의', 'what': '판정 대기 비율 %.1f%%' % (sum(pend) / len(pend)), 'target': '전체'})
    # 넣은 사고를 잡았는가
    caught = []
    for j in injected:
        rules = j['rule'].split('·')
        hit = [a for a in alerts if a['day'] in (j['day'], j['day'] + 1) and a['rule'] in rules]
        caught.append({'id': j['id'], 'day': j['day'], 'what': j['what'], 'rule': j['rule'], 'caught': bool(hit), 'alerts': len(hit)})
    inj_keys = set()
    for j in injected:
        for r in j['rule'].split('·'):
            inj_keys.add((j['day'], r)); inj_keys.add((j['day'] + 1, r))
    extra = [a for a in alerts if (a['day'], a['rule']) not in inj_keys]
    return alerts, inv, caught, extra


def main(out):
    members, ev, injected, free_users, multi, orgsize = run()
    alerts, inv, caught, extra = judge(members, ev, injected, multi)
    types = collections.Counter(e['type'] for e in ev)
    daily = collections.OrderedDict()
    for d in range(1, DAYS + 1):
        daily[d] = collections.Counter()
    for e in ev:
        daily[e['day']][e['type']] += 1
    devs = [d for m in members for d in m['devs']]
    res = {
        'label': '시뮬레이션(실측 아님)', 'made': '2026-11-11', 'seed': SEED, 'days': DAYS,
        'scale': {'무료(메시지 없음)': free_users, '개인 구독': sum(1 for m in members if m['pkg'] == '개인'), '기기 추가': sum(1 for m in members if m['pkg'] == '기기 추가'),
                  '팀': len([o for o in orgsize if o.startswith('T')]), '기관': len([o for o in orgsize if o.startswith('G')]), '회원': len(members), '기기': len(devs),
                  '매체 자리': sum(d['slots'] for d in devs)},
        'os': dict(collections.Counter(d['os'] for d in devs)), 'cap': dict(collections.Counter(d['cap'] for d in devs)),
        'events': len(ev), 'types': dict(sorted(types.items())),
        'daily': [{'day': d, 'total': sum(c.values()), **{k: c.get(k, 0) for k in ['PR-06', 'PR-07', 'PR-08', 'PR-09', 'PR-10']}} for d, c in daily.items()],
        'injected': caught, 'alerts': alerts, 'alerts_by_rule': dict(sorted(collections.Counter(a['rule'] for a in alerts).items())),
        'extra_alerts': extra, 'extra_by_rule': dict(sorted(collections.Counter(a['rule'] for a in extra).items())),
        'invariants': inv, 'free_messages': sum(1 for e in ev if e['pkg'] == '무료'),
    }
    json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('사건', len(ev), '· 경보', len(alerts), '· 넣은 사고', len(caught), '· 잡은 것', sum(1 for c in caught if c['caught']), '· 그 밖의 경보', len(extra), '· 어김', dict(inv))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'cowork', 'ctl', 'sim_multi_result.json')))
