#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""화면별 원천을 화면 코드에서 뽑는다 → cowork/ctl/sc_source_confirmed.tsv (2026-11-13 Fable 지시 · Opus 5.5)

왜: 페이지 전체가 미리 읽어 두는 원천(views9.js의 P.* 묶음 · views0.js의 hvMeta.*)은 화면을 열 때 요청이 생기지 않아
    tools/sc_fetch_measure.js(브라우저 실측)로는 어느 화면이 쓰는지 가를 수 없다. 그래서 코드를 읽어 화면 함수가 실제로 쓰는 변수로 가른다.

어떻게:
 1. index.html이 읽는 스크립트 순서대로 화면 함수(V['SC-xx']=…)를 모은다. 같은 파일 안에서 앞 정의를 잡아 두고(=V['SC-xx']) 다시 정의하면 감싼 것으로 보고
    겹을 잇고, 아니면 앞 겹을 버린다. 이름이 hvV10Late인 함수 안의 정의는 페이지를 다 읽은 뒤 붙으므로 맨 끝에 적용한다.
 2. 화면 함수 몸통에서 부르는 함수를 따라간다(같은 파일 정의 우선, 다른 파일에 하나만 있으면 그것, 여럿이면 따라가지 않음).
    미리 읽는 함수(P.x=r[i] · hvMeta.x=r[i]를 적는 함수)는 따라가지 않고, 화면 쪽에서 쓰는 변수(P.H · hvMeta.al …)를 그 함수가 읽는 파일로 바꾼다.
 3. 원천 종류: 저장소 파일(…tsv · …json) / 서버(ic.hiven.ai.kr의 /__… 주소) / 이 기기 브라우저 저장소(localStorage 열쇠) /
    코드 안 값(HVR · hvEM) / 코드에 구워 넣은 파일 값(hvMAN = manuals.json).

칸: 화면 · 원천 파일 · 근거 코드 파일·줄 · 서버 값 여부
쓰는 법: python3 tools/gen_sc_confirmed.py [저장소 맨 위(기본 지금 폴더)]
"""
import os, re, sys, collections

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
OUT = os.path.join(ROOT, 'cowork', 'ctl', 'sc_source_confirmed.tsv')
BAKED = {  # 코드 안 이름 → (원천 표기, 서버 값 여부)
    'hvMAN': ('cowork/ctl/manuals.json(tools/gen_views8.py가 views8.js에 구워 넣음)', '아님(코드에 구워 넣은 파일 값)'),
    'HVR': ('views0.js HVR(2026-11-04 옮겨 적은 옛 값)', '아님(코드 안 값)'),
    'hvEM': ('views7.js hvEM(체계 표)', '아님(코드 안 값)'),
}
LIT = re.compile(r"(['\"])((?:\.\./)?(?:[^\s'\"/+]+/)*[^\s'\"/+]+\.(?:tsv|json))\1")
KW = set('if for while switch return function typeof new catch try else do var let const in of this case default delete void instanceof throw'.split())


def scripts():
    s = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    out = []
    for m in re.finditer(r'<script\s+src="/?([^"?]+\.js)', s):
        f = m.group(1)
        if os.path.exists(os.path.join(ROOT, f)) and f not in out:
            out.append(f)
    return out


def blank(t):
    """글자열 · 주석 · 정규식 안을 빈칸으로 바꾼 사본(길이 같음). 괄호 짝 · 이름 찾기는 이 사본에서 한다."""
    o = list(t); n = len(t); i = 0; prev = ''
    def wipe(a, b):
        for k in range(a, min(b, n)):
            if o[k] != '\n': o[k] = ' '
    while i < n:
        c = t[i]
        if c in '"\'`':
            q = c; j = i + 1
            while j < n and t[j] != q:
                j += 2 if t[j] == '\\' else 1
            wipe(i + 1, j); i = j + 1; prev = 'x'; continue
        if c == '/' and i + 1 < n and t[i + 1] == '/':
            j = t.find('\n', i); j = n if j < 0 else j; wipe(i, j); i = j; continue
        if c == '/' and i + 1 < n and t[i + 1] == '*':
            j = t.find('*/', i + 2); j = n if j < 0 else j + 2; wipe(i, j); i = j; continue
        if c == '/' and prev in ('', '(', ',', '=', ':', '[', '!', '&', '|', '?', '{', '}', ';', '+', '-', '*', '%', '<', '>', '~', '^', 'r'):
            j = i + 1; cls = False
            while j < n and t[j] != '\n':
                if t[j] == '\\': j += 2; continue
                if t[j] == '[': cls = True
                elif t[j] == ']': cls = False
                elif t[j] == '/' and not cls: break
                j += 1
            if j < n and t[j] == '/':
                wipe(i + 1, j); i = j + 1; prev = 'x'; continue
        if not c.isspace():
            prev = c if not (c.isalnum() or c in '_$') else ('r' if t[max(0, i - 5):i + 1].endswith('return') else 'x')
        i += 1
    return ''.join(o)


def match_brace(b, i):
    d = 0
    for k in range(i, len(b)):
        if b[k] == '{': d += 1
        elif b[k] == '}':
            d -= 1
            if d == 0: return k
    return len(b) - 1


class Src:
    def __init__(self, f):
        self.f = f
        self.t = open(os.path.join(ROOT, f), encoding='utf-8').read()
        self.nl = [m.start() for m in re.finditer('\n', self.t)]
        self.b = blank(self.t)
        self.top = []  # 맨 위 괄호 구간(이 밖에서 정의한 함수 = 전역)
        k = 0
        while True:
            k = self.b.find('{', k)
            if k < 0: break
            e = match_brace(self.b, k); self.top.append((k, e)); k = e + 1

    def is_global(self, pos):
        return not any(a < pos < b for a, b in self.top)

    def line(self, pos):
        import bisect
        return bisect.bisect_left(self.nl, pos) + 1


def body_at(src, pos):
    i = src.b.find('{', pos)
    return (i, match_brace(src.b, i)) if i >= 0 else (pos, pos)


def collect():
    files = scripts()
    S = {f: Src(f) for f in files}
    funcs = collections.defaultdict(list)  # 이름 → [(파일, 시작, 끝)]
    for f, s in S.items():
        for m in re.finditer(r'\bfunction\s+([A-Za-z_$][\w$]*)\s*\(', s.b):
            a, b = body_at(s, m.end()); funcs[m.group(1)].append((f, m.start(), b, s.is_global(m.start())))
        for m in re.finditer(r'(window\.)?(?<![\w$.])([A-Za-z_$][\w$]*)\s*=\s*function\s*\(', s.b):
            a, b = body_at(s, m.end()); funcs[m.group(2)].append((f, m.start(), b, bool(m.group(1)) or s.is_global(m.start())))
    # 파일 맨 위 변수 중 원천 파일 이름을 담은 것(var F18=['a.tsv',…])
    fvars = collections.defaultdict(dict)
    for f, s in S.items():
        for m in re.finditer(r"(?<![\w$.])([A-Za-z_$][\w$]*)\s*=\s*\[\s*('[^'\n]+\.(?:tsv|json)'(?:\s*,\s*'[^'\n]+\.(?:tsv|json)')*)\s*\]", s.t):
            if s.b[m.start()] == ' ':
                continue
            fvars[f][m.group(1)] = (re.findall(r"'([^']+)'", m.group(2)), m.start())
    # 미리 읽는 함수(로더): P.x=r[i] / hvMeta.x=r[i]
    loaders = {}; fieldmap = {}  # (파일 범위, 객체, 필드) → (원천, 파일, 줄)
    for name, defs in funcs.items():
        for (f, a, b, _g) in defs:
            body = S[f].t[a:b]
            asg = re.findall(r'\b(P|hvMeta)\.(\w+)=r\[(\d+)\]', body)
            if not asg:
                continue
            loaders[(f, a)] = name
            lits = re.findall(r"['\"]((?:cowork/)?[\w/\-]*?[\w\-]+\.(?:tsv|json))['\"]", body)
            for obj, fld, i in asg:
                i = int(i)
                if i < len(lits):
                    scope = f if obj == 'P' else '*'
                    fieldmap[(scope, obj, fld)] = (lits[i], f, S[f].line(a))
    return files, S, funcs, fvars, loaders, fieldmap


def screens(files, S):
    chain = {}; late = []
    for f in files:
        s = S[f]
        lates = [(m.start(), body_at(s, m.end())[1]) for m in re.finditer(r'function\s+hvV10Late\s*\(', s.b)]
        for m in re.finditer(r"\bV\[['\"](SC-[\w]+)['\"]\]\s*=\s*(?!=)", s.t):
            sc = m.group(1); pos = m.start()
            if s.b[pos] != 'V':
                continue  # 주석 · 글자열 안
            rest = s.t[m.end():m.end() + 12]
            if rest.startswith('function'):
                a, b = body_at(s, m.end())
            else:  # V['SC-15']=hvTestOnly(…) · hv5(…) 같은 한 문장
                e = s.t.find(';', m.end()); b = e if e > 0 else m.end(); a = m.end()
            captured = re.search(r"=\s*V\[['\"]" + sc + r"['\"]\](?!\s*=)", s.t[:pos]) is not None
            d = (f, pos, a, b)
            if any(x <= pos <= y for x, y in lates):
                late.append((sc, d, captured)); continue
            chain[sc] = (chain.get(sc, []) + [d]) if captured else [d]
    for sc, d, captured in late:
        chain[sc] = (chain.get(sc, []) + [d]) if captured else [d]
    return chain


VDEF = {}


def refs(sc, defs, S, funcs, fvars, loaders, fieldmap):
    out = collections.OrderedDict()  # (원천, 종류) → [근거]

    def add(src, kind, f, pos, extra=''):
        k = (src, kind); ln = '%s:%d%s' % (f, S[f].line(pos), extra)
        out.setdefault(k, [])
        if ln not in out[k]:
            out[k].append(ln)

    seen = set(); todo = [(f, a, b) for (f, _, a, b) in defs]
    while todo:
        f, a, b = todo.pop(0)
        if (f, a) in seen:
            continue
        seen.add((f, a))
        s = S[f]; body = s.t[a:b + 1]
        for m in LIT.finditer(body):  # 글자열 하나가 통째로 파일 경로인 것만(안내 글 속 파일 이름은 원천으로 세지 않음)
            add(os.path.basename(m.group(2)), '아님(저장소 파일)', f, a + m.start())
        for m in re.finditer(r'\b(P|hvMeta)\.(\w+)\b(?!\s*=[^=])', body):
            k = (f if m.group(1) == 'P' else '*', m.group(1), m.group(2))
            if k in fieldmap:
                lit, lf, ll = fieldmap[k]
                add(os.path.basename(lit), '아님(저장소 파일 · 페이지가 미리 읽음)', f, a + m.start(), ' %s.%s ← %s:%d' % (m.group(1), m.group(2), lf, ll))
        for m in re.finditer(r"ic\.hiven\.ai\.kr(/__\w+(?:/\w+)?)|['\"](/__\w+(?:/\w+)?)", body):
            add('ic.hiven.ai.kr' + (m.group(1) or m.group(2)), '서버(ic.hiven.ai.kr)', f, a + m.start())
        for m in re.finditer(r"localStorage\.getItem\(\s*['\"]([\w\-]+)['\"]", body):
            add('브라우저 저장소 「%s」' % m.group(1), '아님(이 기기 브라우저 저장소)', f, a + m.start())
        for nm, (lab, kind) in BAKED.items():
            for m in re.finditer(r'\b' + nm + r'\b', body):
                add(lab, kind, f, a + m.start()); break
        for nm, (names, vpos) in fvars.get(f, {}).items():
            if re.search(r'(?<![\w$.])' + re.escape(nm) + r'\b', s.b[a:b + 1]) and not (a <= vpos <= b):
                for x in names:
                    add(x, '아님(저장소 파일)', f, vpos)
        bb = s.b[a:b + 1]
        local = set(re.findall(r'\b(?:var|let|const)\s+([A-Za-z_$][\w$]*)', bb)) | set(re.findall(r',\s*([A-Za-z_$][\w$]*)\s*=(?!=)', bb))
        for pm in re.finditer(r'function\s*[\w$]*\s*\(([^)]*)\)', bb):
            local |= set(x.strip() for x in pm.group(1).split(',') if x.strip())
        for m in re.finditer(r"V\[['\"](SC-[\w]+)['\"]\]\s*(?:\(|\.apply|\.call)", body):
            for (df, _p, da, db) in VDEF.get(m.group(1), [])[-1:]:
                if (df, da) not in seen:
                    todo.append((df, da, db))
        for m in re.finditer(r'(?<![\w$.])([A-Za-z_$][\w$]*)\b(?!\s*:[^:])', bb):
            nm = m.group(1)
            if nm in KW or nm not in funcs or nm in local:
                continue
            same = [d for d in funcs[nm] if d[0] == f]
            glob = [d for d in funcs[nm] if d[3]]
            ds = same or (glob if len(glob) == 1 else [])
            for (df, da, db, _g) in ds[:1]:
                if (df, da) in loaders or (df, da) in seen or (df == f and da <= a + m.start() <= db):
                    continue
                todo.append((df, da, db))
    return out


def main():
    files, S, funcs, fvars, loaders, fieldmap = collect()
    chain = screens(files, S)
    VDEF.update(chain)
    rows = []
    for sc in sorted(k for k in chain if re.match(r'SC-\d\d$', k)):
        r = refs(sc, chain[sc], S, funcs, fvars, loaders, fieldmap)
        if not r:
            rows.append([sc, '원천 없음(화면 코드 안의 값)', ' · '.join('%s:%d' % (f, S[f].line(p)) for f, p, _, _ in chain[sc]), '아님(코드 안 값)'])
        mg = collections.OrderedDict()
        for (src, kind), ev in r.items():
            k = mg.setdefault(src, [[], []])
            k[0] += [e for e in ev if e not in k[0]]
            if kind not in k[1]: k[1].append(kind)
        for src, (ev, kinds) in mg.items():
            if len(kinds) > 1 and '아님(저장소 파일)' in kinds: kinds.remove('아님(저장소 파일)')
            rows.append([sc, src, ' · '.join(ev[:3]) + (' 밖 %d곳' % (len(ev) - 3) if len(ev) > 3 else ''), ' · '.join(kinds)])
    with open(OUT, 'w', encoding='utf-8', newline='\n') as o:
        o.write('화면\t원천 파일\t근거 코드 파일·줄\t서버 값 여부\n')
        for r in rows:
            o.write('\t'.join(x.replace('\t', ' ') for x in r) + '\n')
    c = collections.Counter(r[0] for r in rows)
    print('화면 %d개 · %d줄 → %s' % (len(set(r[0] for r in rows)), len(rows), os.path.relpath(OUT, ROOT)))
    print(' '.join('%s:%d' % (k, c[k]) for k in sorted(c)))


if __name__ == '__main__':
    main()
