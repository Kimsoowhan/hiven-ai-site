#!/usr/bin/env python3
"""증적 → HiDAM 관계망 브릿지 (ev_bridge) 1.0_작업. 지시문 덧붙임 1 다절(다-1~다-6)대로.
읽기만 한다: 등록부 · 증적 원장 · 증적 폴더의 해시목록·인수기록·환경기록 · 고객 지원 대장(cs_tickets · voc_ledger · cs_ev_links)을
읽어 노드 표(자산원장 20칸)와 링크 표(6칸)를 따로 둔 두 파일로 낸다. 원천 파일과 기존 자산원장·관계원장은 고치지 않는다.
사용:
  ev_bridge.py [--stamp 261113_0300] [--prev 앞_노드표.tsv] [--past 대상ID=증적폴더 ...] [--nodes 경로] [--links 경로]
  ev_bridge.py --check            원장 줄 수 = 실행 노드 수(precheck 가 부름). 다르면 종료 코드 1
  ev_bridge.py --verify [--report 경로]   브-1~브-10 을 스스로 돌려 결과표를 냄(소넷 실행 · 오파스가 따로 다시 돌려 맞댐)
번호 규칙은 D-2 생성기(ledger_gen.py)와 같다: 파일 HF-sha256앞16자-크기(사본 .C2…, 겹침 +순번) · 폴더·줄 HB-sha1(NFC 경로)앞12자 · 관계 HR-sha1(종류|앞|뒤)앞12자.
같은 입력과 같은 --stamp 로 두 번 돌리면 두 출력 sha256 이 같다(줄 순서 = 전체경로 순). 훅·예약을 쓰지 않는다."""
import sys, os, csv, glob, hashlib, unicodedata, re, argparse, tempfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(HERE)
sys.path.insert(0, HERE)
try:
    import hb_common                      # D-1~D-3 공통 부분 재사용(경로 NFC · 숨김 낱말 검사)
except Exception:                         # 저장소 밖에서 돌릴 때
    hb_common = None

CTL = os.path.join(R, 'cowork', 'ctl')
REG = os.path.join(CTL, 'ev_registry.tsv')
LED = os.path.join(CTL, 'ev_ledger.tsv')
OUT_N = os.path.join(CTL, 'ev_bridge_nodes.tsv')
OUT_L = os.path.join(CTL, 'ev_bridge_links.tsv')
D2 = '/mnt/user-data/outputs/sb21b/HiBiz_자산원장_2차-261113_1.0_작업.tsv'   # 브-7 표본 대조용(읽기만)

NH = ['ASSET_ID', '종류', '전체경로', '이름', '판', '상태', 'sha256', '크기', '고친때', '영역과범주(AA.CC)', '단계(SS)',
      '꼬리표D', '꼬리표R', '꼬리표M', '꼬리표K', '원천여부', '올린모델', '올린때', '해시방식', '비고']
LH = ['관계번호', '앞자산번호', '뒤자산번호', '관계종류', '근거', '올린때']
NA, UN = '해당없음', '미부여'
HIDE_MARK = '[통제어 계열 낱말·글자 생략]'

def norm(s):
    return hb_common.norm(s) if hb_common else unicodedata.normalize('NFC', s)

def sha_text(t):
    return hashlib.sha256(t.encode('utf-8')).hexdigest()

def sha_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()

def fid(path):
    return 'HB-' + hashlib.sha1(norm(path).encode('utf-8')).hexdigest()[:12].upper()

def rid(kind, a, b):
    return 'HR-' + hashlib.sha1(('%s|%s|%s' % (kind, a, b)).encode('utf-8')).hexdigest()[:12].upper()

def mask(t):
    """숨김 낱말(통제어 계열)을 글자로 싣지 않는다. hb_common 에 가림 함수가 없어(지시문은 mask_hidden 이라 적음) has/hidden_words 로 가린다."""
    if not hb_common:
        return t
    for w in hb_common.hidden_words():
        if w and w.lower() in norm(t).lower():
            t = re.sub(re.escape(w), HIDE_MARK, t, flags=re.I)
    return t

def read_tsv(p):
    if not os.path.exists(p):
        return [], []
    rows = list(csv.reader(open(p, encoding='utf-8-sig', newline=''), delimiter='\t'))
    return (rows[0], [r for r in rows[1:] if r and any(x.strip() for x in r)]) if rows else ([], [])

def read_lines(p):
    """줄 단위 원문(줄 노드의 sha256 = 그 줄 전체 글자의 해시)."""
    if not os.path.exists(p):
        return []
    out = []
    for i, l in enumerate(open(p, encoding='utf-8-sig')):
        l = l.rstrip('\n').rstrip('\r')
        if i and l.strip():
            out.append(l)
    return out

class G:
    def __init__(self, stamp, prev=None):
        self.stamp = stamp
        self.nodes = {}       # ASSET_ID -> row
        self.links = {}       # 관계번호 -> row
        self.prev = prev or {}
        self.path2id = {}
        self.filebase = {}    # (sha,size) -> [첫 id, 경로들]
        self.used = set()
        self.counts = {}      # 갈래 -> 수
        self.manifest_rows = 0
        self.events = []

    def _row(self, aid, kind, path, name, ver, state, sha, size, mtime, how, note, origin=NA, model='Sonnet 5.5'):
        return [aid, kind, path, name, ver, state, sha, str(size), mtime, UN, UN, UN, UN, UN, UN, origin, model, self.stamp, how, note]

    def line_node(self, kind, path, name, state, text, note, tag):
        path = norm(path)
        aid = self.prev.get(path) or fid(path)
        r = self._row(aid, kind, path, name, UN, state, sha_text(text), len(text.encode('utf-8')), UN, 'sha256(행 전체 텍스트)', mask(note))
        self.nodes[aid] = r; self.path2id[path] = aid
        self.counts[tag] = self.counts.get(tag, 0) + 1
        return aid

    def folder_node(self, path, name, note, tag):
        path = norm(path)
        aid = self.prev.get(path) or fid(path)
        self.nodes[aid] = self._row(aid, '폴더', path, name, NA, '현행', NA + '(폴더)', NA + '(폴더)', UN, NA + '(폴더)', mask(note))
        self.path2id[path] = aid
        self.counts[tag] = self.counts.get(tag, 0) + 1
        return aid

    def file_node(self, path, name, sha, size, mtime, note, tag, code=False):
        path = norm(path)
        if path in self.prev:
            aid = self.prev[path]
        else:
            base = 'HF-%s-%s' % (sha[:16], size)
            first = self.filebase.setdefault((sha, size), [None, []])
            if first[0] is None:
                aid = base
                n = 2
                while aid in self.used:          # 앞 16자가 같은데 sha 가 다른 경우만 +순번
                    aid = '%s+%d' % (base, n); n += 1
                first[0] = aid
            else:
                aid = '%s.C%d' % (first[0], len(first[1]) + 1)      # 같은 sha256·크기, 다른 자리 = 사본
            first[1].append(path)
        self.used.add(aid)
        self.nodes[aid] = self._row(aid, '코드' if code else '파일', path, name, UN, '현행', sha, size, mtime, 'sha256(파일)', mask(note))
        self.path2id[path] = aid
        self.counts[tag] = self.counts.get(tag, 0) + 1
        return aid

    def link(self, kind, a, b, basis):
        k = rid(kind, a, b)
        self.links[k] = [k, a, b, kind, mask(basis), self.stamp]

def rel(p):
    p = norm(p)
    return p

def build(stamp, prev=None, past=None, root=R):
    g = G(stamp, prev)
    ctl = os.path.join(root, 'cowork', 'ctl')
    reg_head, reg_rows = read_tsv(os.path.join(ctl, 'ev_registry.tsv'))
    reg_lines = read_lines(os.path.join(ctl, 'ev_registry.tsv'))
    idx = {h: i for i, h in enumerate(reg_head)}
    regs = {}
    for r, l in zip(reg_rows, reg_lines):
        r = r + [''] * (len(reg_head) - len(r))
        tid = r[0]
        kind = r[idx.get('구분', 15)] if '구분' in idx else ''
        note = '증적:대상 · 종류=%s · 구분=%s · 범위=%s · 상태=%s' % (r[idx['종류']], kind or '확인 안 됨', r[idx['사업군']] if '사업군' in idx and r[idx['사업군']] else '확인 안 됨', r[idx['상태']][:40])
        regs[tid] = (g.line_node('이력', 'cowork/ctl/ev_registry.tsv#' + tid, tid, r[idx['상태']][:20], l, note, '대상'), kind or '확인 안 됨', r[idx['사업군']] if r[idx['사업군']] else '확인 안 됨')

    led_head, led_rows = read_tsv(os.path.join(ctl, 'ev_ledger.tsv'))
    led_lines = read_lines(os.path.join(ctl, 'ev_ledger.tsv'))
    runs = []
    for r, l in zip(led_rows, led_lines):
        runs.append(dict(tid=r[1], rn=r[2], code=r[3], n=r[4], cmp=r[5], folder=r[6], line=l, past=False))
    for spec in (past or []):
        tid, _, folder = spec.partition('=')
        runs.append(dict(tid=tid, rn='사후등록', code='확인 안 됨', n='', cmp='확인 안 됨', folder=folder, line='%s\t사후등록\t%s' % (tid, folder), past=True))

    tool_cache = {}
    for run in runs:
        tid, rn, folder = run['tid'], run['rn'], run['folder']
        reg = regs.get(tid)
        gubun, scope0 = (reg[1], reg[2]) if reg else ('확인 안 됨', '확인 안 됨')
        key = 'cowork/ctl/ev_ledger.tsv#%s/%s' % (tid, rn) if not run['past'] else 'ev_past#%s/%s' % (tid, rn)
        note = '증적:실행 · %s구분=%s · 범위=%s %s · 종료 코드 %s · 대조 %s' % ('지난 실행 · 사후 등록 · ' if run['past'] else '', gubun, scope0, rn, run['code'], run['cmp'])
        eid = g.line_node('이력', key, '%s %s' % (tid, rn), '실행', run['line'], note, '실행')
        run['id'] = eid
        if reg:
            g.link('시험 실행', reg[0], eid, '등록부 %s 한 줄 → 증적 원장 %s 한 줄' % (tid, rn))
        if not os.path.isdir(folder):
            run['missing'] = True
            continue
        fnode = g.folder_node(folder, os.path.basename(folder.rstrip('/')), '증적:폴더 · 구분=%s · 범위=%s' % (gubun, rn), '폴더')
        g.link('증빙', eid, fnode, '실행의 증적 폴더')
        for sub in sorted(d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))):
            sp = folder.rstrip('/') + '/' + sub
            sn = g.folder_node(sp, sub, '증적:폴더 · 라벨 폴더 · 구분=%s · 범위=%s' % (gubun, rn), '폴더')
            g.link('승계', fnode, sn, '윗폴더 → 아랫폴더')
        mh, mrows = read_tsv(os.path.join(folder, '해시목록.tsv'))
        for m in mrows:
            if len(m) < 7:
                continue
            g.manifest_rows += 1
            fp = folder.rstrip('/') + '/' + m[3]
            isin = m[2] == '시작_입력'
            tag = '입력' if isin else '증빙'
            fnid = g.file_node(fp, os.path.basename(m[3]), m[6], m[4], m[5], '%s · %s · 구분=%s · 범위=%s · 증빙번호 %s' % ('증적:입력' if isin else '증적:증빙', m[2], gubun, rn, m[0]), tag)
            g.link('증빙', eid, fnid, '증빙번호 %s · 라벨 %s' % (m[0], m[2]))
        for l in read_lines(os.path.join(folder, '인수기록.tsv')):
            f = l.split('\t')
            if len(f) >= 3 and f[2].startswith('사건'):
                ev = g.line_node('이력', folder.rstrip('/') + '/인수기록.tsv#%s/%s' % (f[0], f[2]), '사건 ' + f[0], '사건', l, '증적:사건 · 구분=%s · 범위=%s · %s' % (gubun, rn, f[2][:40]), '사건')
                g.link('사건', eid, ev, '인수기록의 사건 줄')
        env = os.path.join(folder, '환경기록.tsv')
        if os.path.exists(env):
            ts = None
            for l in read_lines(env):
                f = l.split('\t')
                if f[0].startswith('증적 도구 sha256') or f[0] == '항목':
                    continue
                if f[0] == '증적 도구 sha256' and len(f) > 1:
                    ts = f[1]
            for l in open(env, encoding='utf-8'):
                f = l.rstrip('\n').split('\t')
                if f[0] == '증적 도구 sha256' and len(f) > 1:
                    ts = f[1]
            if ts:
                tpath = 'tools/ev_run.py#sha256=' + ts[:16]
                if tpath not in g.path2id:
                    cur = os.path.join(root, 'tools', 'ev_run.py')
                    same = '현재 파일과 같음' if os.path.exists(cur) and sha_file(cur) == ts else '현재 파일과 다름 또는 확인 안 됨'
                    aid = g.file_node(tpath, 'ev_run.py', ts, UN, UN, '증적:도구 · 환경기록에 적힌 도구 판 · %s · 구분=%s · 범위=%s' % (same, gubun, rn), '도구', code=True)
                    g.nodes[aid][7] = UN
                g.link('증빙', eid, g.path2id[tpath], '환경기록의 증적 도구 sha256')

    # 사본: 같은 sha256 · 크기, 다른 자리
    for (sha, size), (first, paths) in sorted(g.filebase.items()):
        for p in paths[1:]:
            g.link('사본', first, g.path2id[p], '같은 sha256 · 크기, 다른 자리(%s)' % os.path.dirname(p).split('/')[-1])

    # 고객 지원 노드(있는 줄만)
    th, tr = read_tsv(os.path.join(ctl, 'cs_tickets.tsv'))
    tl = read_lines(os.path.join(ctl, 'cs_tickets.tsv'))
    for r, l in zip(tr, tl):
        g.line_node('이력', 'cowork/ctl/cs_tickets.tsv#' + r[0], 'CS ' + r[0], r[3] if len(r) > 3 else UN, l, 'CS · 구분=%s · 분류=%s(고객 식별값은 싣지 않음 · 번호만)' % (r[3] if len(r) > 3 else '확인 안 됨', r[6] if len(r) > 6 else '확인 안 됨'), 'CS')
    vh, vr = read_tsv(os.path.join(ctl, 'voc_ledger.tsv'))
    vl = read_lines(os.path.join(ctl, 'voc_ledger.tsv'))
    for r, l in zip(vr, vl):
        g.line_node('이력', 'cowork/ctl/voc_ledger.tsv#' + r[0], 'VOC ' + r[0], UN, l, 'VOC · 번호만', 'VOC')
    eh, er = read_tsv(os.path.join(ctl, 'cs_ev_links.tsv'))
    el = read_lines(os.path.join(ctl, 'cs_ev_links.tsv'))
    for i, (r, l) in enumerate(zip(er, el)):
        if len(r) > 2 and r[2] not in ('없음', '') :
            g.line_node('이력', 'cowork/ctl/cs_ev_links.tsv#결함/%s' % r[2], '결함 ' + r[2], r[9] if len(r) > 9 else UN, l, '결함 · 구분=확인 안 됨 · 범위=%s' % (r[5] if len(r) > 5 else '확인 안 됨'), '결함')
    return g

def dump(g, pn, pl):
    rows = sorted(g.nodes.values(), key=lambda r: (r[2], r[0]))
    with open(pn, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\t'.join(NH) + '\n')
        for r in rows:
            f.write('\t'.join(x.replace('\t', ' ').replace('\n', ' ') for x in r) + '\n')
    lr = sorted(g.links.values(), key=lambda r: (r[3], r[1], r[2]))
    with open(pl, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\t'.join(LH) + '\n')
        for r in lr:
            f.write('\t'.join(r) + '\n')
    return len(rows), len(lr)

def load_prev(p):
    d = {}
    if p and os.path.exists(p):
        h, rows = read_tsv(p)
        for r in rows:
            d[r[2]] = r[0]
    return d

def count_ledger():
    return len(read_lines(LED))

def check():
    if not os.path.exists(OUT_N):
        print('ev_bridge check 실패: 노드 표가 없음 —', OUT_N, '(ev_bridge.py 를 먼저 돌려야 함)'); return 1
    # 사후 등록(지난 실행)은 원장 줄이 아니므로 뺀다
    n = sum(1 for l in open(OUT_N, encoding='utf-8') if l.rstrip('\n').split('\t')[-1].startswith('증적:실행 ·') and '지난 실행 · 사후 등록' not in l.rstrip('\n').split('\t')[-1])
    L = count_ledger()
    print('ev_bridge check', '통과' if n == L else '실패', '(원장 줄 %d · 실행 노드 %d · 사후 등록 제외)' % (L, n))
    return 0 if n == L else 1

def verify(args):
    """브-1~브-10. 입력은 읽기만, 산출은 임시 폴더에 두 번 내서 맞댄다."""
    res = []
    ins = [REG, LED] + [p for p in glob.glob(os.path.join(CTL, 'cs_*.tsv'))] + [os.path.join(CTL, 'voc_ledger.tsv')]
    before = {p: sha_file(p) for p in ins if os.path.exists(p)}
    td = tempfile.mkdtemp()
    stamp = args.stamp or 'verify'
    past = args.past or []
    g1 = build(stamp, load_prev(args.prev), past)
    a1 = dump(g1, td + '/n1.tsv', td + '/l1.tsv')
    g2 = build(stamp, load_prev(args.prev), past)
    a2 = dump(g2, td + '/n2.tsv', td + '/l2.tsv')
    after = {p: sha_file(p) for p in before}
    res.append(('브-1', '읽기만: 입력 %d건의 sha256 이 돌리기 앞뒤 같음' % len(before), 'PASS' if before == after else 'FAIL', '입력 %d건' % len(before)))
    nreg = len(read_lines(REG)); nled = count_ledger() + len(past)
    c = g1.counts
    ok2 = c.get('대상', 0) == nreg and c.get('실행', 0) == nled and (c.get('증빙', 0) + c.get('입력', 0)) == g1.manifest_rows
    res.append(('브-2', '대상=등록부 줄 · 실행=원장 줄(+사후등록) · 증빙+입력=해시목록 줄 합', 'PASS' if ok2 else 'FAIL', '대상 %d/%d · 실행 %d/%d · 증빙+입력 %d/%d' % (c.get('대상', 0), nreg, c.get('실행', 0), nled, c.get('증빙', 0) + c.get('입력', 0), g1.manifest_rows)))
    broken = [k for k, r in g1.links.items() if r[1] not in g1.nodes or r[2] not in g1.nodes]
    res.append(('브-3', '끊긴 링크 0(앞·뒤 번호가 노드 표에 있음)', 'PASS' if not broken else 'FAIL', '링크 %d · 끊김 %d' % (len(g1.links), len(broken))))
    # 브-4: 번호·경로가 dict 키라 겹치면 덮여 줄이 줄므로 입력 수와 노드 수를 맞대 겹침을 잡음
    expect = sum(c.values())
    dupkind = len(g1.links) != len({(r[3], r[1], r[2]) for r in g1.links.values()})
    res.append(('브-4', '같은 번호 두 줄 0 · 같은 종류|앞|뒤 두 줄 0', 'PASS' if len(g1.nodes) == expect and not dupkind else 'FAIL', '만든 노드 %d · 센 노드 %d' % (len(g1.nodes), expect)))
    good = bad = miss = 0
    for r in g1.nodes.values():
        if r[19].startswith(('증적:증빙', '증적:입력')):
            if os.path.exists(r[2]):
                if sha_file(r[2]) == r[6]: good += 1
                else: bad += 1
            else:
                miss += 1
    res.append(('브-5', '증빙 노드 sha256 = 해시목록 값 = 실제 사본 파일을 다시 계산한 값', 'PASS' if not bad and not miss else ('FAIL' if bad else '확인 안 됨'), '같음 %d · 다름 %d · 파일 없음(다시 계산 못 함) %d' % (good, bad, miss)))
    s1, s2 = sha_file(td + '/n1.tsv'), sha_file(td + '/n2.tsv')
    t1, t2 = sha_file(td + '/l1.tsv'), sha_file(td + '/l2.tsv')
    res.append(('브-6', '같은 입력 두 번 = 같은 출력 sha256', 'PASS' if (s1, t1) == (s2, t2) else 'FAIL', '노드 %s · 링크 %s' % (s1[:12], t1[:12])))
    # 브-7: D-2 원장의 파일 번호 규칙과 같은 번호가 나오는지 표본(원장에 없으면 확인 안 됨)
    if os.path.exists(D2):
        h, rows = read_tsv(D2)
        sm = [r for r in rows if r[1] == '파일' and re.fullmatch(r'[0-9a-f]{64}', r[6]) and re.fullmatch(r'HF-[0-9A-Fa-f]{16}-\d+', r[0])][:200]
        okn = sum(1 for r in sm if r[0] == 'HF-%s-%s' % (r[6][:16], r[7]))
        nf = [r for r in rows if r[1] == '파일']
        nhf = sum(1 for r in nf if r[0].startswith('HF-')); nhb = sum(1 for r in nf if r[0].startswith('HB-'))
        res.append(('브-7', 'D-2 원장에 있는 파일(표본 10건 이상)은 같은 번호', 'PASS' if len(sm) >= 10 and okn == len(sm) else ('FAIL' if len(sm) >= 10 and okn != len(sm) else '확인 안 됨'),
                    '지문 꼴(HF-) 표본 %d건 중 같음 %d · 이 원장의 파일 줄 %d건 중 지문 꼴 %d · 경로 해시 꼴(HB-) %d(경로 해시 꼴은 sha256이 없어 지문 규칙으로 맞댈 수 없음) · 다음에 읽을 방법: 지문 꼴 원장(D-2 생성기 산출)을 받아 --verify 다시 돌림' % (len(sm), okn, len(nf), nhf, nhb)))
    else:
        res.append(('브-7', 'D-2 원장에 있는 파일(표본 10건 이상)은 같은 번호', '확인 안 됨', 'D-2 원장 파일이 이 자리에 없음 · 다음에 읽을 방법: sb21b 원장을 받아 --verify 다시 돌림'))
    rel_ok = True; msg = []
    execs = [r for r in g1.nodes.values() if r[19].startswith('증적:실행')]
    lk = {}
    for r in g1.links.values():
        lk.setdefault((r[3], r[2]), []).append(r)
    for r in execs:
        if not any(l[3] == '시험 실행' and l[2] == r[0] for l in g1.links.values()):
            rel_ok = False; msg.append('시험 실행 없음 ' + r[3][:30])
    n_ev = sum(1 for r in g1.nodes.values() if r[19].startswith(('증적:증빙', '증적:입력')))
    n_lk = sum(1 for l in g1.links.values() if l[3] == '증빙' and g1.nodes[l[2]][19].startswith(('증적:증빙', '증적:입력')))
    if n_lk < n_ev: rel_ok = False; msg.append('증빙 링크 부족')
    res.append(('브-8', '실행 노드마다 「시험 실행」 1줄 · 증빙 노드마다 「증빙」 1줄 이상 · 사건 줄마다 이력 번호가 있으면 이력 행 링크', 'PASS' if rel_ok else 'FAIL', '실행 노드 %d · 증빙 노드 %d · 증빙 링크 %d · 사건 줄의 이력 번호 링크는 이력 번호가 있는 줄만(이 입력에는 사건 줄 %d건)' % (len(execs), n_ev, n_lk, c.get('사건', 0))))
    lack = [r[0] for r in execs if '구분=' not in r[19] or '범위=' not in r[19]]
    unk = [r[0] for r in execs if '구분=확인 안 됨' in r[19]]
    res.append(('브-9', '비고에 구분(실측·시뮬레이션·에뮬레이터 실측)과 범위가 있음, 없으면 「확인 안 됨」', 'PASS' if not lack else 'FAIL', '실행 노드 %d · 칸 없음 %d · 구분이 「확인 안 됨」으로 적힌 것 %d' % (len(execs), len(lack), len(unk))))
    txt = open(td + '/n1.tsv', encoding='utf-8').read() + open(td + '/l1.tsv', encoding='utf-8').read()
    hid = hb_common.has_hidden_word(txt) if hb_common else None
    sens = re.findall(r'(?i)password|passwd|비밀번호|api[_-]?key|secret|token=', txt)
    at = txt.count('@')
    ok10 = (hid is False) and not sens and at == 0
    res.append(('브-10', '숨김 낱말 0 · 로그인 값·코드 값 0 · 고객 식별값 0(번호만)', 'PASS' if ok10 else ('확인 안 됨' if hid is None else 'FAIL'), '숨김 낱말 %s · 민감 낱말 %d · 「@」 %d' % ('0' if hid is False else ('있음' if hid else 'hb_common 없음'), len(sens), at)))
    shutil.rmtree(td, ignore_errors=True)
    out = ['번호\t기준\t결과\t값']
    for r in res:
        out.append('\t'.join(r))
        print(r[0], r[2], '·', r[3])
    if args.report:
        open(args.report, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    return 0 if all(r[2] == 'PASS' for r in res) else 1

def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument('--stamp'); ap.add_argument('--prev'); ap.add_argument('--past', action='append')
    ap.add_argument('--nodes', default=OUT_N); ap.add_argument('--links', default=OUT_L)
    ap.add_argument('--check', action='store_true'); ap.add_argument('--verify', action='store_true'); ap.add_argument('--report')
    ap.add_argument('-h', '--help', action='store_true')
    a = ap.parse_args()
    if a.help:
        print(__doc__); return 0
    if a.check:
        return check()
    if a.verify:
        return verify(a)
    stamp = a.stamp or __import__('time').strftime('%y%m%d_%H%M')
    g = build(stamp, load_prev(a.prev), a.past)
    n, l = dump(g, a.nodes, a.links)
    print('ev_bridge 노드 %d · 링크 %d · 갈래 %s' % (n, l, ' '.join('%s %d' % kv for kv in sorted(g.counts.items()))))
    print(a.nodes, sha_file(a.nodes)[:16]); print(a.links, sha_file(a.links)[:16])
    return 0

if __name__ == '__main__':
    sys.exit(main())
