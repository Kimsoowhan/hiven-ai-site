#!/usr/bin/env python3
"""칭찬 자동 감지 장치 (praise_watch) — 대표님 11/06 20:21 예외 승인(칭찬 크레딧 작업, Sonnet 5.5 한정)

하는 일
  1) 대표님 메시지에서 칭찬 문구(한글·영어·음차·줄임말)를 판별한다. 인사(Good morning 등)·OK류 답변은 세지 않는다.
  2) 칭찬이면 직전 작업 모델(대화 원문의 마지막 답변 모델)에 귀속해 원장(cowork/ctl/praise_credit_ledger.tsv)에 한 줄 추가한다.
  3) 칭찬 문구를 정의·인용하는 지시(예: 「잘했어」를 센다는 지시)는 세지 않고 검토 대기(praise_watch_review.tsv)에 올린다.
  4) 상태(praise_watch_status.json)를 갱신하고, 원장·상태 변경분만 커밋·푸시한다(백그라운드, 실패해도 작업을 막지 않음).

쓰는 법
  감시 모드 : python3 praise_watch.py --watch   (이 작업 공간의 대화 원문을 15초마다 읽음 — 구동 방식)
  전수 검사 : python3 praise_watch.py --scan [--since 2026-11-01] [--dry]   (이미 센 것은 건너뜀)
  중지      : /tmp/claude-0/praise_watch.off 파일을 만들면 아무것도 하지 않는다 (삭제하면 재개)

안전 규칙: 항상 종료 코드 0, 입력을 막거나 거부하지 않음, 표준출력은 한 줄 이하, 대화 내용 외 데이터는 읽지 않음.
"""
import sys, os, re, json, csv, glob, hashlib, datetime, subprocess, fcntl

REPO = os.environ.get('PW_REPO', '/tmp/claude-0/hs')
CTL = os.path.join(REPO, 'cowork', 'ctl')
LEDGER = os.environ.get('PW_LEDGER', os.path.join(CTL, 'praise_credit_ledger.tsv'))
REVIEW = os.environ.get('PW_REVIEW', os.path.join(CTL, 'praise_watch_review.tsv'))
STATUS = os.environ.get('PW_STATUS', os.path.join(CTL, 'praise_watch_status.json'))
STATE = os.environ.get('PW_STATE', '/tmp/claude-0/praise_watch_state.json')
OFF = '/tmp/claude-0/praise_watch.off'
KST = datetime.timezone(datetime.timedelta(hours=9))

PRAISE = [r'잘했', r'잘 했', r'훌륭', r'고마워', r'고맙', r'감사', r'수고', r'최고', r'굿(?!모닝|나잇|이브닝|애프터눈)', r'땡큐', r'땡스',
          r'좋아', r'좋네', r'좋았', r'마음에 들', r'맘에 들', r'만족', r'멋져', r'멋지', r'대단', r'완벽',
          r'\bgood\b', r'\bgreat\b', r'\bnice\b', r'\bexcellent\b', r'\bawesome\b', r'\bperfect\b', r'\bwell done\b', r'\bbravo\b',
          r'\bthank(?:s| you| u)?\b', r'\bthx\b', r'\bthnx\b', r'\btnx\b', r'\bthanx\b', r'\bty\b']
GREET = [r'good\s+(?:morning|evening|night|afternoon|day)', r'굿\s*(?:모닝|나잇|이브닝|애프터눈)', r'좋은\s*(?:아침|저녁|밤|하루)', r'안녕', r'잘\s*자', r'굿밤']
OKW = [r'\bok(?:ay)?\b', r'오케이', r'오키', r'알겠어', r'승인']
META = [r'칭찬', r'카운트', r'크레딧', r'산정', r'사전', r'표현', r'문구', r'인용', r'포함시', r'센다', r'세는', r'표시', r'줄임말', r'영어', r'단어', r'반영', r'적용', r'삽입', r'분류', r'구분']  # 칭찬 문구를 정의·인용하는 지시의 표지
pr = re.compile('|'.join(PRAISE), re.I)
gr = re.compile('|'.join(GREET), re.I)
okr = re.compile('|'.join(OKW), re.I)
mr = re.compile('|'.join(META))
MODEL = [('fable', 'Fable'), ('opus', 'Opus'), ('sonnet', 'Sonnet'), ('haiku', 'Haiku')]


def classify(text):
    """('praise'|'meta'|'none', 찾은 말 목록)"""
    t = okr.sub(' ', gr.sub(' ', text))
    hit = sorted(set(x.lower() for x in pr.findall(t)))
    if not hit:
        return 'none', []
    # 정의·인용 지시: 칭찬 문구를 따옴표 「」로 인용했거나 판정 규칙을 말하는 메시지
    quoted = re.findall(r'[「“"\'](.*?)[」”"\']', text)
    if mr.search(text) and (quoted or len(text) > 60):
        return 'meta', hit
    return 'praise', hit


def clean(c):
    if isinstance(c, list):
        c = ' '.join(x.get('text', '') for x in c if isinstance(x, dict) and x.get('type') == 'text')
    if not isinstance(c, str):
        return ''
    c = re.sub(r'<system-reminder>.*?</system-reminder>', '', c, flags=re.S)
    c = re.sub(r'<artifact-content-authored-by-others/>', '', c)
    return c.strip()


def human_msg(d):
    """대표님 메시지 한 건 → (본문, 고유값). 일반 user 줄과, 작업 도중 끼어든 메시지(queued_command 첨부)를 함께 읽는다. 아니면 (None, None)."""
    t = d.get('type')
    if d.get('isMeta') or d.get('isSidechain'):
        return None, None
    if t == 'user':
        return clean(d.get('message', {}).get('content')), d.get('uuid')
    if t == 'attachment':
        a = d.get('attachment') or {}
        if a.get('type') == 'queued_command' and (a.get('origin') or {}).get('kind', 'human') == 'human':
            return clean(a.get('prompt')), a.get('source_uuid') or d.get('uuid')
    return None, None


def model_label(raw):
    r = (raw or '').lower()
    for k, v in MODEL:
        if k in r:
            return v
    return '미상'


def last_assistant(tp, before=None):
    """transcript에서 before(시각) 이전 마지막 답변의 (모델, 요약). 못 찾으면 ('미상','')"""
    if not tp or not os.path.exists(tp):
        return '미상', ''
    mdl, txt = '미상', ''
    try:
        for ln in open(tp, encoding='utf-8', errors='ignore'):
            try:
                d = json.loads(ln)
            except Exception:
                continue
            if before and d.get('timestamp') and d['timestamp'] >= before:
                break
            if d.get('type') == 'assistant':
                m = d.get('message', {})
                if m.get('model') and not str(m['model']).startswith('<'):
                    mdl = model_label(m['model'])
                c = m.get('content')
                if isinstance(c, list):
                    t = ' '.join(x.get('text', '') for x in c if isinstance(x, dict) and x.get('type') == 'text').strip()
                    if t:
                        txt = t
    except Exception:
        pass
    return mdl, txt[:70].replace('\t', ' ').replace('\n', ' ')


def load_state():
    try:
        return json.load(open(STATE, encoding='utf-8'))
    except Exception:
        return {'seen': [], 'hits': 0, 'review': 0, 'runs': 0}


def save_state(s):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(s, open(STATE, 'w', encoding='utf-8'), ensure_ascii=False)


def read_ledger():
    if not os.path.exists(LEDGER):
        return None, []
    rows = list(csv.reader(open(LEDGER, encoding='utf-8-sig'), delimiter='\t'))
    return rows[0], rows[1:]


def append_ledger(ts, model, text, why, hit, src):
    """원장 한 줄 추가. 같은 시각·모델·문구는 건너뜀(중복 방지)."""
    hdr, rows = read_ledger()
    if hdr is None:
        return None
    key = ts.strftime('%m/%d %H:%M')
    for r in rows:
        if r[3] == key and text[:20] in r[6]:
            return None
    no = (max([int(r[0]) for r in rows if r[0].isdigit()] or [0])) + 1
    row = [str(no), ts.strftime('%Y-%m-%d'), str(ts.hour), key, model, '칭찬 크레딧',
           '대표님 「%s」 (%s, 자동 감지: %s)' % (text[:110].replace('\n', ' '), src, '·'.join(hit)),
           '자동 감지 — 직전 작업: ' + (why or '확인 안 됨'),
           '별도 누적(이력과 무관). 자동 감지 장치 기록', '부여', '대기']
    with open(LEDGER, 'a', encoding='utf-8', newline='') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        csv.writer(f, delimiter='\t', lineterminator='\n').writerow(row)
        fcntl.flock(f, fcntl.LOCK_UN)
    return no


def append_review(ts, text, hit, src):
    new = not os.path.exists(REVIEW)
    with open(REVIEW, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        if new:
            w.writerow(['시각', '출처', '찾은 말', '메시지 앞부분', '판정', '검토'])
        w.writerow([ts.strftime('%m/%d %H:%M'), src, '·'.join(hit), text[:100].replace('\n', ' '), '문맥 검토 대기(정의·인용 지시로 보여 세지 않음)', '대기'])


def write_status(st, last_hit=None, note=''):
    now = datetime.datetime.now(KST)
    hdr, rows = read_ledger()
    d = {'장치': '칭찬 자동 감지 장치(praise_watch)', '승인': '대표님 11/06 20:21 예외 승인(칭찬 크레딧 작업, Sonnet 5.5 한정)',
         '켜짐': not os.path.exists(OFF), '마지막 실행': now.strftime('%Y-%m-%d %H:%M:%S'), '실행 횟수': st.get('runs', 0),
         '자동 기록 건수': st.get('hits', 0), '문맥 검토 대기': st.get('review', 0), '원장 총건수': len(rows),
         '마지막 감지': last_hit or st.get('last_hit', ''), '비고': note}
    if last_hit:
        st['last_hit'] = last_hit
    json.dump(d, open(STATUS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def push(paths):
    """원장·상태만 커밋·푸시(백그라운드, 실패 무시)"""
    if os.environ.get('PW_NOPUSH'):
        return
    rel = [os.path.relpath(p, REPO) for p in paths if os.path.exists(p)]
    cmd = 'cd %s && git add %s && git commit -q -m "칭찬 자동 감지 장치 기록\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_012qSBL5TqsRWVrwA415UfBv" -- %s && (git push -q origin HEAD || (git pull -q --rebase origin HEAD && git push -q origin HEAD))' % (REPO, ' '.join(rel), ' '.join(rel))
    try:
        subprocess.Popen(['flock', '-n', '/tmp/claude-0/praise_push.lock', 'bash', '-c', cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    except Exception:
        pass


def handle(text, tp, ts, src, sid, uid, model=None):
    """반환: 한 줄 안내(칭찬 기록 시) 또는 None. 상태는 여기서 저장한다."""
    st = load_state()
    k = hashlib.sha1(('%s|%s|%s' % (sid, uid, text[:80])).encode('utf-8')).hexdigest()[:16]
    if k in st['seen']:
        return None
    kind, hit = classify(text)
    if kind == 'praise' and read_ledger()[0] is None:
        return None  # 원장을 못 읽으면 센 것으로 표시하지 않음(다음 처리 때 다시 시도)
    st['seen'] = (st['seen'] + [k])[-2000:]
    out, touched = None, []
    if kind == 'praise':
        mdl, why = (model_label(model), '') if model else last_assistant(tp, ts.astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S'))
        no = append_ledger(ts, mdl, text, why, hit, src)
        if no:
            st['hits'] = st.get('hits', 0) + 1
            out = '칭찬 크레딧 +1 → 원장 %d번, %s (%s). SC-13 칭찬 크레딧에 바로 반영됩니다.' % (no, mdl, '·'.join(hit))
            write_status(st, '%s %s 원장 %d번' % (ts.strftime('%m/%d %H:%M'), mdl, no))
            touched = [LEDGER, STATUS]
    elif kind == 'meta':
        append_review(ts, text, hit, src)
        st['review'] = st.get('review', 0) + 1
        write_status(st, note='문맥 검토 대기 +1')
        touched = [STATUS, REVIEW]
    save_state(st)
    if touched and not os.environ.get('PW_DEFER'):
        push(touched)
    return out


def main():
    if os.path.exists(OFF):
        return
    a = sys.argv[1:]
    if '--watch' in a:
        # 대화 원문을 15초마다 읽어 새 대표님 메시지를 판별(이미 센 것은 건너뜀). 작업 공간이 살아 있는 동안만 동작.
        import time
        since = datetime.datetime.now(KST) - datetime.timedelta(minutes=3)
        pos = {}
        while not os.path.exists(OFF):
            for f in glob.glob('/root/.claude/projects/*/*.jsonl'):
                sid = os.path.basename(f)[:-6]
                try:
                    sz = os.path.getsize(f)
                except Exception:
                    continue
                if f not in pos:
                    pos[f] = sz  # 시작 시점 이후 추가분만
                    continue
                if sz <= pos[f]:
                    continue
                with open(f, encoding='utf-8', errors='ignore') as fh:
                    fh.seek(pos[f]); chunk = fh.read(); pos[f] = sz
                for ln in chunk.splitlines():
                    try:
                        d = json.loads(ln)
                    except Exception:
                        continue
                    text, muid = human_msg(d)
                    if not text or 'This session is being continued' in text[:800]:
                        continue
                    try:
                        ts = datetime.datetime.fromisoformat(d['timestamp'].replace('Z', '+00:00')).astimezone(KST)
                    except Exception:
                        continue
                    handle(text, f, ts, '이 작업 공간 창(%s)' % sid[:8], sid, muid or ts.isoformat())
            st = load_state(); st['runs'] = st.get('runs', 0) + 1; save_state(st)
            time.sleep(15)
        return
    if '--scan' in a:
        since = datetime.datetime(2026, 11, 1, tzinfo=KST)
        if '--since' in a:
            y, m, dd = [int(x) for x in a[a.index('--since') + 1].split('-')]
            since = datetime.datetime(y, m, dd, tzinfo=KST)
        dry = '--dry' in a
        n = 0
        for f in glob.glob('/root/.claude/projects/*/*.jsonl'):
            sid = os.path.basename(f)[:-6]
            for ln in open(f, encoding='utf-8', errors='ignore'):
                try:
                    d = json.loads(ln)
                except Exception:
                    continue
                text, muid = human_msg(d)
                if not text or 'This session is being continued' in text[:800] or 'The summarized conversation included' in text[:200]:
                    continue
                try:
                    ts = datetime.datetime.fromisoformat(d['timestamp'].replace('Z', '+00:00')).astimezone(KST)
                except Exception:
                    continue
                if ts < since:
                    continue
                kind, hit = classify(text)
                if kind == 'none':
                    continue
                n += 1
                if dry:
                    print(ts.strftime('%m/%d %H:%M'), kind, hit, '|', text[:90].replace('\n', ' '))
                else:
                    handle(text, f, ts, '이 작업 공간 창(%s) 전수 검사' % sid[:8], sid, muid or ts.isoformat())
        if not dry:
            st = load_state(); write_status(st, note='전수 검사 실행'); save_state(st); push([LEDGER, STATUS, REVIEW])
        print('검사 결과 %d건 (%s)' % (n, '시험' if dry else '반영'))
        return
    print(__doc__)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
